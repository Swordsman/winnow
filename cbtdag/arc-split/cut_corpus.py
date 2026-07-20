#!/usr/bin/env python3
"""arc-split corpus cutter (cbtdag/arc-split, chunk B).

Cuts a `[tN role]`-format transcript into per-part session files
according to a boundaries JSON (frozen contract, produced by a sibling
worker's arc detector), renumbering each part's turn headers to start
at t1. Built for the multi-session `:src`-collision exercise
(cbtdag/arc-split/design-spec.md D4): each part gets extracted
independently, so every part log emits colliding `t1..` src values by
construction; the README.md this tool writes alongside the parts is
the ground-truth original<->part-local turn mapping later
merge-provenance verification needs.

Transcript format: header line `[tN role]` starts a turn; everything
until the next header is that turn's body (see winnow.py
parse_transcript, which this mirrors exactly, including its
leading/trailing-whitespace strip -- interior blank lines inside a
body are untouched).

Boundaries JSON (frozen contract; schema per
cbtdag/arc-split/fixtures/expected-boundaries.json): this tool consumes
`source_transcript` (path to the transcript to cut) and `parts`
(inclusive 1-indexed [start, end] pairs that must gap-free cover
1..turn_count). Other fields (cuts, crossings_at_cuts, all_candidates,
rationale, ...) are the arc detector's provenance and are carried into
README.md verbatim but not otherwise consumed.

Usage:
    python3 cut_corpus.py BOUNDARIES.json --out-dir DIR

Writes DIR/part1.txt .. partN.txt (one per entry in `parts`, in order)
and DIR/README.md (corpus description, the boundaries JSON, and the
full original-turn -> (part file, part-local turn, role) mapping
table).
"""
import argparse
import json
import os
import re
import sys

TURN_RE = re.compile(r"^\[t(\d+)\s+(\S+)\]\s*$")


# ------------------------------------------------------------ transcript

def parse_transcript(text):
    """Yield (turn_index, role, body) from `[tN role]` blocks -- same
    contract as winnow.py's parse_transcript (winnow.py:147)."""
    turns = []
    cur = None
    for line in text.splitlines():
        m = TURN_RE.match(line)
        if m:
            cur = [int(m.group(1)), m.group(2), []]
            turns.append(cur)
        elif cur is not None:
            cur[2].append(line)
    return [(n, who, "\n".join(body).strip()) for n, who, body in turns]


def render_turns(turns):
    """turns: iterable of (n, role, body) -> canonical transcript text:
    exactly one blank line between turns, a trailing newline, bodies
    untouched."""
    return "\n\n".join(f"[t{n} {role}]\n{body}" for n, role, body in turns) + "\n"


# ------------------------------------------------------------ boundaries

def load_boundaries(path):
    with open(path) as f:
        raw = f.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.exit(f"{path}: not valid JSON ({e})")
    for key in ("source_transcript", "parts"):
        if key not in data:
            sys.exit(f"{path}: missing required field {key!r}")
    return data, raw


def validate_cover(parts, total_turns):
    """parts: list of [start, end] inclusive 1-indexed pairs. Must be a
    sorted, gap-free, non-overlapping cover of 1..total_turns. Returns
    the same pairs as a list of (start, end) tuples."""
    if not isinstance(parts, list) or not parts:
        sys.exit(f"parts must be a non-empty list, got {parts!r}")
    norm = []
    for i, p in enumerate(parts):
        if not (isinstance(p, list) and len(p) == 2 and
                all(isinstance(x, int) and not isinstance(x, bool) for x in p)):
            sys.exit(f"parts[{i}] is not a [start, end] integer pair: {p!r}")
        start, end = p
        if start > end:
            sys.exit(f"parts[{i}] = [{start}, {end}]: start > end")
        norm.append((start, end))
    expect = 1
    for i, (start, end) in enumerate(norm):
        if start != expect:
            sys.exit(f"parts[{i}] = [{start}, {end}]: expected start "
                      f"{expect} (gap or overlap in the 1..{total_turns} "
                      f"cover)")
        expect = end + 1
    if expect - 1 != total_turns:
        sys.exit(f"parts cover 1..{expect - 1} but the transcript has "
                  f"{total_turns} turns -- not a complete cover")
    return norm


# ------------------------------------------------------------ cutting

def cut(turns, parts):
    """turns: list of (n, role, body) in original order. parts:
    validated [(start, end), ...]. Returns (part_turns, mapping):
    part_turns is a list (one per part) of [(local_n, role, body), ...]
    with local_n renumbered from 1; mapping is a list of
    (orig_n, part_index, local_n, role) rows, one per original turn, in
    original-turn order (part_index and local_n are both 1-indexed)."""
    by_n = {n: (role, body) for n, role, body in turns}
    part_turns = []
    mapping = []
    for part_idx, (start, end) in enumerate(parts, start=1):
        local = []
        for local_n, orig_n in enumerate(range(start, end + 1), start=1):
            if orig_n not in by_n:
                sys.exit(f"part {part_idx} [{start}, {end}] references "
                          f"t{orig_n}, which is not in the transcript")
            role, body = by_n[orig_n]
            local.append((local_n, role, body))
            mapping.append((orig_n, part_idx, local_n, role))
        part_turns.append(local)
    return part_turns, mapping


def round_trip_check(source_text, turns, part_turns, mapping):
    """Reconstruct the source transcript from the cut parts, restoring
    original tN numbering via the mapping (design-spec.md D4's
    round-trip property), and diff against the original source text.
    Returns (ok, message)."""
    restore = {(part_idx, local_n): orig_n
               for orig_n, part_idx, local_n, _ in mapping}
    reconstructed_turns = []
    for part_idx, local in enumerate(part_turns, start=1):
        for local_n, role, body in local:
            reconstructed_turns.append(
                (restore[(part_idx, local_n)], role, body))
    reconstructed_turns.sort(key=lambda t: t[0])
    reconstructed = render_turns(reconstructed_turns)
    if reconstructed == source_text:
        return True, "reconstructed source matches the original byte-for-byte"
    # Isolate "we mis-cut" from "the source file wasn't already in
    # canonical [tN role]-header / single-blank-line-separator form".
    canonical_source = render_turns(turns)
    if reconstructed == canonical_source:
        return False, ("reconstruction matches a canonical re-render of "
                        "the source but NOT the raw source bytes -- the "
                        "source transcript has non-canonical spacing "
                        "and/or line endings around its turn headers")
    return False, "reconstructed parts do not reproduce the source transcript"


# ------------------------------------------------------------ output

def write_parts(out_dir, part_turns):
    paths = []
    for i, local in enumerate(part_turns, start=1):
        path = os.path.join(out_dir, f"part{i}.txt")
        with open(path, "w") as f:
            f.write(render_turns(local))
        paths.append(path)
    return paths


def write_readme(out_dir, boundaries_path, boundaries_raw, source_transcript,
                  mapping):
    lines = [
        "# arc-split corpus",
        "",
        f"Per-part transcripts cut from `{source_transcript}` at arc "
        f"boundaries, for the multi-session `:src`-collision exercise "
        f"(cbtdag/arc-split/design-spec.md): each part is extracted "
        f"independently into its own winnow log with a fresh id/turn "
        f"space, so every part's nodes carry `t1..`-style `:src` values "
        f"by construction -- the collision evidence the merge-UX "
        f"hardening work needs. Turn headers are renumbered per part to "
        f"start at `t1` (roles preserved, bodies untouched); the "
        f"mapping table below is the ground truth for translating a "
        f"part-local `tM` back to the original corpus's `tN` during "
        f"later merge-provenance verification. Cut with "
        f"`cbtdag/arc-split/cut_corpus.py` from the boundaries JSON "
        f"below.",
        "",
        f"## Boundaries JSON (`{boundaries_path}`)",
        "",
        "```json",
        boundaries_raw.rstrip("\n"),
        "```",
        "",
        "## Turn mapping",
        "",
        "original -> part file, part-local turn, role",
        "",
        "| original | part file | part-local | role |",
        "|---|---|---|---|",
    ]
    for orig_n, part_idx, local_n, role in mapping:
        lines.append(f"| t{orig_n} | part{part_idx}.txt | t{local_n} | {role} |")
    lines.append("")
    text = "\n".join(lines)
    path = os.path.join(out_dir, "README.md")
    with open(path, "w") as f:
        f.write(text)
    return path


# ------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("boundaries", help="boundaries JSON path")
    ap.add_argument("--out-dir", required=True, help="output directory")
    ns = ap.parse_args()

    data, raw = load_boundaries(ns.boundaries)
    source_transcript = data["source_transcript"]
    parts_field = data["parts"]

    if not os.path.exists(source_transcript):
        sys.exit(f"source_transcript not found: {source_transcript}")
    source_text = open(source_transcript).read()
    turns = parse_transcript(source_text)
    if not turns:
        sys.exit(f"{source_transcript}: no [tN role] turns found")

    total_turns = len(turns)
    orig_ns = [n for n, _, _ in turns]
    if orig_ns != list(range(1, total_turns + 1)):
        sys.exit(f"{source_transcript}: turn numbers are not a dense "
                  f"1..{total_turns} sequence in order: {orig_ns}")

    if "turn_count" in data and data["turn_count"] != total_turns:
        sys.exit(f"{ns.boundaries}: turn_count={data['turn_count']} does "
                  f"not match {total_turns} turns parsed from "
                  f"{source_transcript}")

    parts = validate_cover(parts_field, total_turns)
    part_turns, mapping = cut(turns, parts)

    ok, msg = round_trip_check(source_text, turns, part_turns, mapping)
    print(("round-trip OK: " if ok else "round-trip FAILED: ") + msg,
          file=sys.stderr)
    if not ok:
        sys.exit("refusing to write parts: round-trip invariant failed")

    os.makedirs(ns.out_dir, exist_ok=True)
    paths = write_parts(ns.out_dir, part_turns)
    readme = write_readme(ns.out_dir, ns.boundaries, raw, source_transcript,
                           mapping)
    print(f"wrote {len(paths)} part file(s) + {readme}", file=sys.stderr)
    for p in paths:
        print(f"  {p}", file=sys.stderr)


if __name__ == "__main__":
    main()
