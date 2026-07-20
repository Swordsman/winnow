#!/usr/bin/env python3
"""arc-split — conversational-arc boundary detector.

Detects K arc boundaries in a winnow log by turn-axis minimum-crossing
cut: a node's turn is the integer in its `:src` (t7 -> 7); an edge
"crosses" candidate boundary b if one endpoint's turn is <= b and the
other's is > b. We choose K cuts that minimize total crossings subject
to every resulting part spanning >= --min-part turns, tie-breaking on
balance (smaller max part) then on lower cut indices.

Design: cbtdag/arc-split/design-spec.md D2/D3. Contract: boundaries-json
(frozen), schema in the design spec and cbtdag/arc-split/work-order-A.md.

Usage:
    python3 cbtdag/arc-split/detect_arcs.py LOG.wno --transcript T.txt \\
        [--k 2] [--min-part 5] --out boundaries.json
"""
import argparse
import itertools
import json
import os
import re
import sys

# repo root is two levels up (cbtdag/arc-split/detect_arcs.py); put it on
# sys.path so `from fold import ...` resolves regardless of invocation cwd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from fold import Graph, parse, tokenize


def load(path):
    """Same load pattern as split.py: parse, fold, refuse if invalid."""
    g = Graph()
    for form in parse(tokenize(open(path).read())):
        if form and form[0] == "meta":
            g.set_meta(form)
        else:
            g.apply(form)
    errs = g.validate()
    if errs:
        sys.exit(f"{path}: refusing to detect arcs on an invalid log: {errs}")
    return g


def node_turn(src):
    """Int turn from a :src value (t7 -> 7); None if absent/unparseable."""
    if src is None or isinstance(src, list):
        return None
    m = re.search(r"\d+", str(src))
    return int(m.group()) if m else None


def transcript_turn_count(path):
    """Max N from `[tN role]` headers (winnow.py parse_transcript format)."""
    n = 0
    with open(path) as f:
        for line in f:
            m = re.match(r"^\[t(\d+)\s+(\S+)\]\s*$", line)
            if m:
                n = max(n, int(m.group(1)))
    if n == 0:
        sys.exit(f"{path}: no [tN role] headers found")
    return n


def edge_turn_pairs(g):
    """(turn_a, turn_b) for every edge with both endpoints :src-bearing."""
    turns = {nid: node_turn(n.get("src")) for nid, n in g.nodes.items()}
    pairs = []
    for _, a, b in g.edges:
        ta, tb = turns.get(a), turns.get(b)
        if ta is not None and tb is not None:
            pairs.append((ta, tb))
    return pairs


def crossing_counts(edge_pairs, turn_count):
    """b (1..turn_count-1) -> count of edges straddling boundary b."""
    return {b: sum(1 for ta, tb in edge_pairs if (ta <= b) != (tb <= b))
            for b in range(1, turn_count)}


def valid_combos(turn_count, k, min_part):
    """All ascending K-tuples of cuts s.t. every resulting part spans
    >= min_part turns (turn span, inclusive)."""
    out = []
    for combo in itertools.combinations(range(1, turn_count), k):
        bounds = [0] + list(combo) + [turn_count]
        spans = [bounds[i + 1] - bounds[i] for i in range(len(bounds) - 1)]
        if all(s >= min_part for s in spans):
            out.append(combo)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("log")
    ap.add_argument("--transcript", required=True,
                    help="source transcript for turn count")
    ap.add_argument("--k", type=int, default=2, help="number of cuts")
    ap.add_argument("--min-part", type=int, default=5,
                    help="minimum turn span per part")
    ap.add_argument("--out", required=True, help="boundaries.json output")
    ns = ap.parse_args()

    g = load(ns.log)
    turn_count = transcript_turn_count(ns.transcript)

    edge_pairs = edge_turn_pairs(g)
    cross = crossing_counts(edge_pairs, turn_count)

    combos = valid_combos(turn_count, ns.k, ns.min_part)
    if not combos:
        sys.exit(f"no valid {ns.k}-cut partition of {turn_count} turns "
                  f"with min-part {ns.min_part}")

    def rank(combo):
        bounds = [0] + list(combo) + [turn_count]
        spans = [bounds[i + 1] - bounds[i] for i in range(len(bounds) - 1)]
        total = sum(cross[b] for b in combo)
        return (total, max(spans), combo)

    best = min(combos, key=rank)
    legal = sorted({b for combo in combos for b in combo})
    all_candidates = {str(b): cross[b] for b in legal}

    cuts = list(best)
    bounds = [0] + cuts + [turn_count]
    parts = [[bounds[i] + 1, bounds[i + 1]] for i in range(len(bounds) - 1)]
    crossings_at_cuts = [cross[b] for b in cuts]

    out = {
        "source_log": ns.log,
        "source_transcript": ns.transcript,
        "turn_count": turn_count,
        "cuts": cuts,
        "parts": parts,
        "crossings_at_cuts": crossings_at_cuts,
        "all_candidates": all_candidates,
        "rationale": (
            f"exhaustive search over {len(combos)} valid {ns.k}-cut "
            f"partitions (min-part {ns.min_part}); picked minimum total "
            f"crossings ({sum(crossings_at_cuts)}), tie-broken by balance "
            f"then lowest cut indices"),
    }

    with open(ns.out, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print(f"wrote {ns.out}: turn_count={turn_count} cuts={cuts} "
          f"crossings_at_cuts={crossings_at_cuts}", file=sys.stderr)


if __name__ == "__main__":
    main()
