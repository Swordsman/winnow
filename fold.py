#!/usr/bin/env python3
"""winnow v0.2 reference implementation.

Parse an s-expression delta log (.wno), fold it into a materialized
semantic graph, validate references, print stats, and render views:
the canonical snapshot, the v0.1 frontier digest, or the v0.2 tiered
immediate context window (spec section 10).

Usage:
    python3 fold.py LOG.wno            # stats + validation
    python3 fold.py LOG.wno --snapshot # also print canonical snapshot
    python3 fold.py LOG.wno --frontier # v0.1 frontier digest
    python3 fold.py LOG.wno --digest   # v0.2 tiered window
    python3 fold.py LOG.wno --upto N   # fold only the first N deltas
"""
import sys
import re
from collections import Counter


class Lit(str):
    """Quoted string literal (as opposed to a bare symbol)."""


FRAME_ORDER = ["constraint", "decision", "question", "def",
               "claim", "action", "artifact"]
DEFAULT_STATUS = {
    "claim": "live", "question": "open", "decision": "proposed",
    "constraint": "live", "action": "todo", "def": "live",
    "artifact": "live",
}
FRAMES = set(DEFAULT_STATUS)
ETYPES = {"supports", "contradicts", "supersedes", "refines",
          "answers", "motivates", "depends", "about"}
ANN_ORDER = ["status", "conf", "status-conf", "strength", "by",
             "src", "time", "modal", "neg"]

# Cooling-profile defaults = the human default profile (spec 10.4).
# promotion-ttl and widening-base are declared knobs consumed by an
# orchestrator; the static fold records but does not act on them.
PROFILE_DEFAULTS = {
    "tail": 6,            # recent live claims/defs kept hot
    "fire-hops": 1,       # forward-projection radius from touched nodes
    "protect": ETYPES,    # edge types the demotion invariant counts
    "promotion-ttl": 2,   # deltas a reach-promotion survives untouched
    "widening-base": 3,   # rung-2 widening: base, base^2, base^3
}


# ---------------------------------------------------------------- parsing

def tokenize(src):
    toks, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if c == ";":                            # comment to end of line
            while i < n and src[i] != "\n":
                i += 1
        elif c.isspace():
            i += 1
        elif c in "()":
            toks.append(c)
            i += 1
        elif c == '"':
            j = i + 1
            while j < n and src[j] != '"':
                j += 1
            toks.append(Lit(src[i + 1:j]))
            i = j + 1
        else:
            j = i
            while j < n and not src[j].isspace() and src[j] not in '()"':
                j += 1
            toks.append(src[i:j])
            i = j
    return toks


def parse(toks):
    pos = 0

    def rd():
        nonlocal pos
        t = toks[pos]
        pos += 1
        if t == "(":
            out = []
            while toks[pos] != ")":
                out.append(rd())
            pos += 1
            return out
        return t

    forms = []
    while pos < len(toks):
        forms.append(rd())
    return forms


def sx(v):
    """Serialize a parsed value back to canonical s-expr text."""
    if isinstance(v, list):
        return "(" + " ".join(sx(x) for x in v) + ")"
    if isinstance(v, Lit):
        return '"' + str(v) + '"'
    return str(v)


def anns(rest):
    """Collect :key value pairs from a tail; ignore anything else."""
    d, i = {}, 0
    while i < len(rest):
        k = rest[i]
        if isinstance(k, str) and not isinstance(k, Lit) and k.startswith(":"):
            d[k[1:]] = rest[i + 1]
            i += 2
        else:
            i += 1
    return d


# ---------------------------------------------------------------- graph

class Graph:
    def __init__(self):
        self.nodes = {}     # id -> dict
        self.edges = []     # (etype, src, dst)
        self.terms = {}     # termid -> tail
        self.errors = []
        self.deltas = 0
        self.turn = 0
        self.meta = {}
        self.profile = dict(PROFILE_DEFAULTS)
        self.touched = set()   # node ids touched by the most recent delta

    # -- header ------------------------------------------------------
    def set_meta(self, form):
        self.meta = anns(form[1:])
        prof = self.meta.get("profile")
        if isinstance(prof, list):
            for k, v in anns(prof).items():
                if k == "protect":
                    self.profile[k] = set(v) if isinstance(v, list) else {v}
                else:
                    self.profile[k] = int(v)

    # -- ops ---------------------------------------------------------
    def apply(self, delta):
        assert delta[0] == "delta", "top-level form must be (delta ...)"
        self.deltas += 1
        head_anns = anns(delta[1:3])
        if "turn" in head_anns:
            self.turn = head_anns["turn"]
        self.touched = set()
        for op in (x for x in delta[1:] if isinstance(x, list)):
            head = op[0]
            if head == "term":
                self.terms[op[1]] = op[2:]
            elif head == "add":
                self._add(op[1])
            elif head == "update":
                nid = op[1]
                if nid not in self.nodes:
                    self.errors.append(f"update of unknown id {nid}")
                    continue
                self.nodes[nid].update(anns(op[2:]))
                self.touched.add(nid)
            elif head == "supersede":            # (supersede NEW OLD ...)
                new, old = op[1], op[2]
                a = anns(op[3:])
                if old not in self.nodes:
                    self.errors.append(f"supersede of unknown id {old}")
                    continue
                self.nodes[old]["status"] = "superseded"
                if "conf" in a:
                    self.nodes[old]["status-conf"] = a["conf"]
                self._edge("supersedes", new, old)
            elif head == "merge":                # (merge LOSER WINNER)
                loser, winner = op[1], op[2]
                self.edges = [
                    (t,
                     winner if s == loser else s,
                     winner if d == loser else d)
                    for t, s, d in self.edges]
                self.nodes.pop(loser, None)
                self.touched.discard(loser)
                self.touched.add(winner)
            elif head == "del":
                tgt = op[1]
                if isinstance(tgt, list):        # (del (edge (t a b)))
                    t, a, b = tgt[1]
                    try:
                        self.edges.remove((t, a, b))
                    except ValueError:
                        self.errors.append(f"del of missing edge {sx(tgt)}")
                else:
                    self.nodes.pop(tgt, None)
                    self.edges = [e for e in self.edges
                                  if tgt not in (e[1], e[2])]
                    self.touched.discard(tgt)
            else:
                self.errors.append(f"unknown op {head}")

    def _add(self, item):
        if item[0] == "edge":
            et, a, b = item[1]
            self._edge(et, a, b)
            return
        frame, nid = item[0], item[1]
        if frame not in FRAMES:
            self.errors.append(f"unknown frame {frame}")
        if nid in self.nodes:
            self.errors.append(f"duplicate add {nid}")
        if frame == "def":                       # (def id termid "gloss" ...)
            payload = [item[2], item[3]]
            tail = item[4:]
        else:
            payload = item[2]
            tail = item[3:]
        node = {"frame": frame, "payload": payload,
                "status": DEFAULT_STATUS.get(frame, "live")}
        node.update(anns(tail))
        self.nodes[nid] = node
        self.touched.add(nid)

    def _edge(self, et, a, b):
        if et not in ETYPES:
            self.errors.append(f"unknown edge type {et}")
        self.edges.append((et, a, b))
        self.touched.update((a, b))              # promotion trigger P2

    # -- checks ------------------------------------------------------
    def validate(self):
        for t, a, b in self.edges:
            for x in (a, b):
                if x not in self.nodes:
                    self.errors.append(f"dangling ref {x} in ({t} {a} {b})")
        return self.errors

    # -- shared rendering --------------------------------------------
    def _node_key(self, nid):
        f = self.nodes[nid]["frame"]
        num = int(re.sub(r"\D", "", nid) or 0)
        return (FRAME_ORDER.index(f) if f in FRAME_ORDER else 99, num)

    def _payload_line(self, nid):
        n = self.nodes[nid]
        parts = ([n["frame"], nid] + list(n["payload"])
                 if n["frame"] == "def" else [n["frame"], nid, n["payload"]])
        return sx(parts)

    def _full_line(self, nid):
        n = self.nodes[nid]
        parts = [n["frame"], nid]
        pl = n["payload"]
        parts += pl if n["frame"] == "def" else [pl]
        for k in ANN_ORDER:
            if k in n:
                parts += [":" + k, n[k]]
        return sx(parts)

    # -- views -------------------------------------------------------
    def snapshot(self):
        lines = []
        for tid in sorted(self.terms):
            lines.append(sx(["term", tid] + list(self.terms[tid])))
        for nid in sorted(self.nodes, key=self._node_key):
            lines.append(self._full_line(nid))
        for e in sorted(self.edges):
            lines.append(sx(["edge", list(e)]))
        return "\n".join(lines)

    def _frontier_ids(self):
        keep_status = {"constraint": {"live"}, "decision": {"proposed"},
                       "question": {"open"}, "action": {"todo", "doing",
                                                        "blocked"}}
        ids = [nid for nid, n in self.nodes.items()
               if n["status"] in keep_status.get(n["frame"], set())]
        claims = [nid for nid, n in self.nodes.items()
                  if n["frame"] in ("claim", "def") and n["status"] == "live"]
        ids += claims[-int(self.profile["tail"]):]
        return list(dict.fromkeys(ids))

    def frontier(self):
        """The v0.1 digest: everything actionable + recent tail."""
        ids = self._frontier_ids()
        dormant = len(self.nodes) - len(ids)
        lines = [self._payload_line(i) for i in ids]
        lines.append(f"; +{dormant} dormant nodes (resolved/superseded), "
                     f"full graph on request")
        return "\n".join(lines)

    def tiers(self):
        """fire/hot/warm/cold per spec section 10; pure function of
        (log, profile). Never logged, excluded from equivalence."""
        protect = self.profile["protect"]
        adj = {}
        for t, a, b in self.edges:
            if t in protect:
                adj.setdefault(a, set()).add(b)
                adj.setdefault(b, set()).add(a)
        fire = {i for i in self.touched if i in self.nodes}
        for _ in range(int(self.profile["fire-hops"])):
            fire |= {nb for i in fire for nb in adj.get(i, ())
                     if nb in self.nodes}
        hot = [i for i in self._frontier_ids() if i not in fire]
        resident = fire | set(hot)
        warm = [nid for nid in self.nodes if nid not in resident
                and any(nb in resident for nb in adj.get(nid, ()))]
        cold = [nid for nid in self.nodes
                if nid not in resident and nid not in warm]
        return fire, hot, warm, cold

    def _holding_edge(self, nid, resident):
        for t, a, b in self.edges:
            if a == nid and b in resident or b == nid and a in resident:
                return t, a, b
        return None

    def digest(self):
        """The v0.2 immediate context window (push side): side-effect
        state, fire in full, hot as payloads, warm as stubs, cold count.
        Pull results and promotion TTLs belong to an orchestrator."""
        fire, hot, warm, cold = self.tiers()
        p = self.profile
        prot = ("all" if p["protect"] == ETYPES
                else ",".join(sorted(p["protect"])))
        lines = [
            f"; digest @ turn {self.turn} -- derived, ephemeral, never logged",
            f"; profile: tail={p['tail']} fire-hops={p['fire-hops']} "
            f"promotion-ttl={p['promotion-ttl']} "
            f"widening-base={p['widening-base']} protect={prot}",
            f"; side-effect state: {len(self.terms)} terms (registry travels "
            f"with log); live hard constraints render hot",
            "; --- fire: last exchange + projection ---",
        ]
        lines += [self._full_line(i) for i in sorted(fire, key=self._node_key)]
        lines.append("; --- hot: frontier ---")
        lines += [self._payload_line(i) for i in sorted(hot,
                                                        key=self._node_key)]
        lines.append("; --- warm: dormant, edge-held by residents ---")
        resident = fire | set(hot)
        for nid in sorted(warm, key=self._node_key):
            n = self.nodes[nid]
            held = self._holding_edge(nid, resident)
            via = f" held-by ({held[0]} {held[1]} {held[2]})" if held else ""
            lines.append(f"; {self._payload_line(nid)} "
                         f":status {n['status']}{via}")
        lines.append(f"; --- cold: {len(cold)} nodes, log-resident; "
                     f"(reach QUERY) to promote ---")
        return "\n".join(lines)

    def stats(self):
        out = [f"deltas applied : {self.deltas}",
               f"nodes          : {len(self.nodes)}",
               f"edges          : {len(self.edges)}",
               f"terms          : {len(self.terms)}"]
        by_frame = Counter(n["frame"] for n in self.nodes.values())
        for f in FRAME_ORDER:
            if by_frame[f]:
                st = Counter(n["status"] for n in self.nodes.values()
                             if n["frame"] == f)
                st_txt = " ".join(f"{k}={v}" for k, v in sorted(st.items()))
                out.append(f"  {f:<10} {by_frame[f]:>3}   ({st_txt})")
        by_et = Counter(t for t, _, _ in self.edges)
        out.append("  edge types     " +
                   " ".join(f"{k}={v}" for k, v in sorted(by_et.items())))
        snap = self.snapshot()
        out.append(f"snapshot size  : {len(snap)} chars "
                   f"(~{len(snap) // 4} tokens)")
        return "\n".join(out)


# ---------------------------------------------------------------- main

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    with open(sys.argv[1]) as f:
        forms = parse(tokenize(f.read()))
    upto = (int(sys.argv[sys.argv.index("--upto") + 1])
            if "--upto" in sys.argv else None)
    g = Graph()
    applied = 0
    for form in forms:
        if form and form[0] == "meta":
            g.set_meta(form)
            continue
        if upto is not None and applied >= upto:
            break
        g.apply(form)
        applied += 1
    errs = g.validate()
    if "--frontier" in sys.argv:
        print(g.frontier())
        return
    if "--digest" in sys.argv:
        print(g.digest())
        return
    print(g.stats())
    print("validation     :",
          "OK" if not errs else f"{len(errs)} problem(s)")
    for e in errs:
        print("  !", e)
    if "--snapshot" in sys.argv:
        print("\n; --- canonical snapshot ---")
        print(g.snapshot())


if __name__ == "__main__":
    main()
