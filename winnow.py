#!/usr/bin/env python3
"""winnow v0.2 streaming extraction orchestrator (spec section 9).

Drives the core loop over a turn-tagged transcript:

    turns -> extractor (loose, LLM) -> normalizer (strict) -> delta -> log

The extractor sees only the tiered digest (fold.py, spec section 10) plus
the new turns. Stage B is split per the spec: an optional LLM pass for the
semantic rules (R1/R3/R5/R6/R9/R10), then a procedural pass that enforces
the mechanical ones (R7 ann order, R8 serial ids, R11 dedup, reference
validation) regardless of what any model emitted.

Transcript format: turns are introduced by a header line `[tN speaker]`
(e.g. `[t1 user]`); everything until the next header is that turn's text.

Usage:
    python3 winnow.py transcript.txt --out log.wno
    python3 winnow.py transcript.txt --out log.wno --replay fixtures.txt
    python3 winnow.py transcript.txt --out log.wno --per-turn

Live mode needs the `anthropic` package and an API credential; --replay
mode (canned responses separated by lines containing only %%%) needs
neither and exists for tests and offline development.
"""
import argparse
import re
import sys

from fold import Graph, parse, tokenize, sx, anns, ETYPES, FRAMES

ID_PREFIX = {"claim": "c", "decision": "d", "question": "q",
             "constraint": "k", "def": "f", "action": "a", "artifact": "r"}
ANN_ORDER = ["status", "conf", "status-conf", "strength", "by",
             "src", "time", "modal", "neg"]
DEFAULT_MODEL = "claude-opus-4-8"

EXTRACTOR_SYSTEM = """\
You're taking working notes on a live conversation, for a future reader \
with zero patience for transcript archaeology -- probably us, later. You \
get two things: the note graph so far (just the live frontier), and the \
newest turns.

Jot what changed, as winnow delta ops -- new claims, decisions, \
constraints, questions, definitions, actions, and links between them. \
Loose syntax is fine; a normalizer cleans up after you. What matters:

- capture every commitment, correction, requirement, and open thread
- when someone's joking, keep the payload, drop the joke
- when someone takes a position on material they read or were given, \
note the stance -- the verdict outranks the summary
- if something restates what's already in the graph, skip it
- if a new statement kills or changes an old node, say so (update / supersede)
- attribute everything: who said it (:by), which turn (:src)
- unsure? include it with low :conf rather than dropping it

Never note: greetings, filler, vibes, meta-chatter about the conversation \
itself.

Emit ops as s-expressions, one per line, e.g.:
(term some-term :gloss "...")
(add (claim x1 (relation subj obj) :by user :src t3))
(add (edge (supports x1 x2)))
(update q2 :status answered)
Use any placeholder ids you like; the normalizer assigns real ones."""

NORMALIZER_SYSTEM = """\
You are the winnow normalizer. Input: a candidate delta plus the current \
term registry. Output: the canonical ops, one s-expression per line, \
nothing else.

Apply R1-R12: canonical kebab-case term ids (nearest registry match beats \
minting; minted terms get a (term ...) entry), one proposition per node, \
fixed slot order per the relation's direction gloss, tense/modality/\
polarity as annotations, active voice, no synonym relations. Keep the \
extractor's placeholder node ids -- serial ids are assigned after you. \
Drop ops that restate existing graph content unless the status changed."""


# ------------------------------------------------------------ transcript

def parse_transcript(text):
    """Yield (turn_index, speaker, text) from `[tN speaker]` blocks."""
    turns = []
    cur = None
    for line in text.splitlines():
        m = re.match(r"^\[t(\d+)\s+(\S+)\]\s*$", line)
        if m:
            cur = [int(m.group(1)), m.group(2), []]
            turns.append(cur)
        elif cur is not None:
            cur[2].append(line)
    return [(n, who, "\n".join(body).strip()) for n, who, body in turns]


# ------------------------------------------------------------ llm clients

def anthropic_client(model):
    import anthropic
    client = anthropic.Anthropic()

    def call(system, user):
        resp = client.messages.create(
            model=model,
            max_tokens=16000,
            thinking={"type": "adaptive"},
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in resp.content if b.type == "text")

    return call


def replay_client(path):
    """Canned responses split on lines containing only %%% -- consumed in
    call order. For tests and offline runs."""
    with open(path) as f:
        chunks = re.split(r"(?m)^%%%$", f.read())
    queue = [c.strip() for c in chunks if c.strip()]

    def call(system, user):
        if not queue:
            raise RuntimeError("replay fixture exhausted")
        return queue.pop(0)

    return call


# ------------------------------------------------------------ normalizer

def extract_forms(text):
    """Pull balanced top-level s-expressions out of LLM prose."""
    forms, depth, start = [], 0, None
    in_str = False
    for i, ch in enumerate(text):
        if ch == '"':
            in_str = not in_str
        if in_str:
            continue
        if ch == "(":
            if depth == 0:
                start = i
            depth += 1
        elif ch == ")" and depth > 0:
            depth -= 1
            if depth == 0:
                forms.append(text[start:i + 1])
    parsed = []
    for f in forms:
        try:
            got = parse(tokenize(f))
            parsed.extend(x for x in got if isinstance(x, list) and x)
        except (IndexError, AssertionError):
            continue
    # unwrap any (delta :turn N op...) wrappers the model emitted
    flat = []
    for form in parsed:
        if form[0] == "delta":
            flat.extend(x for x in form[1:] if isinstance(x, list))
        else:
            flat.append(form)
    known = {"term", "add", "update", "supersede", "merge", "del"}
    return [f for f in flat if f[0] in known]


class Normalizer:
    """Procedural stage-B enforcement: serial ids (R8), dedup (R11),
    annotation order (R7), reference validation. Semantic normalization
    (R1-R6, R9-R12) is the upstream LLM pass's job; everything here holds
    even if that pass is skipped or misbehaves."""

    def __init__(self, graph):
        self.g = graph
        self.serial = {f: 0 for f in ID_PREFIX}
        for nid, n in graph.nodes.items():
            num = int(re.sub(r"\D", "", nid) or 0)
            f = n["frame"]
            if f in self.serial:
                self.serial[f] = max(self.serial[f], num)
        self.payload_index = {
            (n["frame"], sx(n["payload"])): nid
            for nid, n in graph.nodes.items()}

    def _next_id(self, frame):
        self.serial[frame] += 1
        return f"{ID_PREFIX[frame]}{self.serial[frame]}"

    def _map(self, ref, idmap):
        return idmap.get(ref, ref)

    def _node_form(self, frame, nid, payload, ann_dict):
        parts = [frame, nid]
        parts += payload if frame == "def" else [payload]
        for k in ANN_ORDER:
            if k in ann_dict:
                parts += [":" + k, ann_dict[k]]
        return parts

    def normalize(self, forms):
        """Return (canonical_ops, rejects). canonical_ops are parsed
        forms ready to serialize into one delta."""
        out, rejects, idmap = [], [], {}
        for op in forms:
            head = op[0]
            if head == "term":
                if op[1] not in self.g.terms:
                    out.append(op)
                continue
            if head == "add":
                item = op[1]
                if item[0] == "edge":
                    et, a, b = item[1]
                    a, b = self._map(a, idmap), self._map(b, idmap)
                    if et not in ETYPES:
                        rejects.append(f"unknown edge type {et}")
                        continue
                    assigned = set(idmap.values())
                    if (a not in self.g.nodes and a not in assigned) or \
                       (b not in self.g.nodes and b not in assigned):
                        rejects.append(f"dangling edge ({et} {a} {b})")
                        continue
                    if ("edge", et, a, b) in {("edge", t, s, d)
                                              for t, s, d in self.g.edges}:
                        continue  # R11 for edges
                    out.append(["add", ["edge", [et, a, b]]])
                    continue
                frame, xid = item[0], item[1]
                if frame not in FRAMES:
                    rejects.append(f"unknown frame {frame}")
                    continue
                if frame == "def":
                    payload, tail = [item[2], item[3]], item[4:]
                else:
                    payload, tail = item[2], item[3:]
                a = anns(tail)
                key = (frame, sx(payload))
                if key in self.payload_index:      # R11
                    existing = self.payload_index[key]
                    idmap[xid] = existing
                    old_status = self.g.nodes[existing]["status"]
                    if "status" in a and a["status"] != old_status:
                        out.append(["update", existing,
                                    ":status", a["status"]])
                    continue
                nid = self._next_id(frame)
                idmap[xid] = nid
                self.payload_index[key] = nid
                out.append(["add", self._node_form(frame, nid, payload, a)])
                continue
            if head in ("update", "supersede", "merge", "del"):
                mapped = [head] + [self._map(x, idmap) if isinstance(x, str)
                                   else x for x in op[1:]]
                refs = [x for x in mapped[1:2 if head in ("update", "del")
                                          else 3]
                        if isinstance(x, str) and not x.startswith(":")]
                if head == "del" and isinstance(op[1], list):
                    out.append(op)
                    continue
                bad = [r for r in refs if r not in self.g.nodes
                       and r not in set(idmap.values())]
                if bad:
                    rejects.append(f"{head} of unknown id {' '.join(bad)}")
                    continue
                if head == "update":
                    a = anns(mapped[2:])
                    mapped = ["update", mapped[1]]
                    for k in ANN_ORDER:
                        if k in a:
                            mapped += [":" + k, a[k]]
                out.append(mapped)
                continue
            rejects.append(f"unknown op {head}")
        return out, rejects


# ------------------------------------------------------------ orchestrator

def render_delta(turn, ops):
    lines = [f"(delta :turn {turn}"]
    for op in ops:
        lines.append("  " + sx(op) + ("" if op is not ops[-1] else ")"))
    if len(ops) == 0:
        return None
    return "\n".join(lines)


def run(transcript_path, out_path, llm, llm_normalize=True,
        per_turn=False, verbose=True):
    turns = parse_transcript(open(transcript_path).read())
    if not turns:
        sys.exit("no [tN speaker] turns found in transcript")
    g = Graph()
    log_parts = ['(meta :winnow-version "0.2" :semantic-rep "registry-v0.1")']

    # group turns into triggers
    batches, cur = [], []
    for t in turns:
        cur.append(t)
        if per_turn or t[1] != "user":
            batches.append(cur)
            cur = []
    if cur:
        batches.append(cur)

    for batch in batches:
        turn_no = batch[-1][0]
        new_text = "\n\n".join(f"[t{n} {who}]\n{txt}"
                               for n, who, txt in batch)
        digest = g.digest() if g.nodes else "; graph is empty"
        registry = "\n".join(sx(["term", tid] + list(tail))
                             for tid, tail in sorted(g.terms.items())) \
                   or "; registry is empty"

        loose = llm(EXTRACTOR_SYSTEM,
                    f"NOTE GRAPH SO FAR (digest):\n{digest}\n\n"
                    f"NEW TURNS:\n{new_text}")
        if llm_normalize:
            loose = llm(NORMALIZER_SYSTEM,
                        f"TERM REGISTRY:\n{registry}\n\n"
                        f"CANDIDATE DELTA:\n{loose}")

        norm = Normalizer(g)
        ops, rejects = norm.normalize(extract_forms(loose))
        for r in rejects:
            print(f"  (reject \"{r}\")", file=sys.stderr)
        if not ops:
            if verbose:
                print(f"turn {turn_no}: no signal", file=sys.stderr)
            continue
        delta_text = render_delta(turn_no, ops)
        g.apply(parse(tokenize(delta_text))[0])
        log_parts.append(delta_text)
        if verbose:
            print(f"turn {turn_no}: {len(ops)} ops "
                  f"({len(g.nodes)} nodes, {len(g.edges)} edges)",
                  file=sys.stderr)

    with open(out_path, "w") as f:
        f.write("\n\n".join(log_parts) + "\n")
    errs = g.validate()
    if verbose:
        print(f"wrote {out_path}: {len(g.nodes)} nodes, "
              f"{len(g.edges)} edges, {len(g.terms)} terms; "
              f"validation {'OK' if not errs else errs}", file=sys.stderr)
    return g


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("transcript")
    ap.add_argument("--out", required=True, help="output .wno log path")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--replay", help="canned-response fixture (offline)")
    ap.add_argument("--per-turn", action="store_true",
                    help="one delta per turn instead of per exchange")
    ap.add_argument("--no-llm-normalizer", action="store_true",
                    help="skip stage-B LLM; procedural enforcement only")
    args = ap.parse_args()

    llm = (replay_client(args.replay) if args.replay
           else anthropic_client(args.model))
    run(args.transcript, args.out, llm,
        llm_normalize=not args.no_llm_normalizer,
        per_turn=args.per_turn)


if __name__ == "__main__":
    main()
