# Work order A — arc detector (arc-split-corpus)

Operating mode: spec-only (contracts honored by convention).
Repo: /home/user/winnow. You may create ONLY:
`cbtdag/arc-split/detect_arcs.py` and `runs/arc-split/boundaries.json`
(create the `runs/arc-split/` directory if needed). Do not commit or
touch git. Do not modify any existing file.

## Task

Write `cbtdag/arc-split/detect_arcs.py` (zero-dependency python3,
style-matched to the repo's fold.py/split.py: argparse, small
functions, terse comments) that detects conversational-arc boundaries
in a winnow log by turn-axis minimum-crossing cut, then run it to
produce the real `runs/arc-split/boundaries.json`.

Algorithm:
- Parse the log with `from fold import Graph, parse, tokenize` (see
  how split.py loads a log — reuse that pattern; run from the repo
  root so the import works).
- A node's turn = int in its `:src` (t7 → 7). Nodes without `:src`
  are ignored. Edges between two `:src`-bearing nodes are the only
  crossings counted.
- Candidate boundary b (integer) sits between turns b and b+1;
  crossing(b) = count of edges with one endpoint turn ≤ b and the
  other > b.
- Choose K cuts minimizing total crossings subject to every resulting
  part having ≥ min-part turns (turn span, based on the declared
  turn-count axis 1..T). Tie-break: the partition minimizing the
  largest part (more balanced wins); if still tied, lower cut indices.
- Exhaustive search is fine (T ≤ 24, K ≤ 2 → trivial).

CLI:
```
python3 cbtdag/arc-split/detect_arcs.py LOG --transcript T.txt \
    [--k 2] [--min-part 5] --out boundaries.json
```
Turn count comes from the transcript's max `[tN ...]` header.

## Provides-contract: boundaries-json (FROZEN)

Output JSON schema — exactly these keys:
`source_log`, `source_transcript`, `turn_count`, `cuts` (ascending
ints), `parts` (inclusive 1-indexed [start, end] pairs covering
1..turn_count with no gaps), `crossings_at_cuts` (parallel to cuts),
`all_candidates` (map of every legal candidate boundary → crossing
count; keys are strings because JSON), `rationale` (one line).

## Fixture (must pass before the real run)

```
python3 cbtdag/arc-split/detect_arcs.py \
    cbtdag/arc-split/fixtures/fixture-log.wno \
    --transcript cbtdag/arc-split/fixtures/fixture-transcript.txt \
    --k 1 --min-part 2 --out /tmp/fixture-out.json
```
must produce JSON whose `cuts`, `parts`, `crossings_at_cuts`, and
`all_candidates` match `cbtdag/arc-split/fixtures/expected-boundaries.json`
(field-by-field; `rationale` may differ; source paths must point at the
fixture files).

## Real run (the deliverable)

```
python3 cbtdag/arc-split/detect_arcs.py runs/gemini-proto-pro-re2.wno \
    --transcript transcripts/gemini-winnow-proto.txt \
    --k 2 --min-part 5 --out runs/arc-split/boundaries.json
```

Also run `python3 split.py runs/gemini-proto-pro-re2.wno --component
--seed <a-node-id> --out /tmp/comp.wno` style probes ONLY if useful as
a sanity cross-check; do not write anything outside your two permitted
paths.

## Acceptance

1. Fixture passes exactly.
2. `runs/arc-split/boundaries.json` schema-valid, parts cover 1..24,
   every part ≥ 5 turns, cuts' crossing counts consistent with
   `all_candidates`, and `all_candidates` is honest (recomputable).
3. Report in your final message: the chosen cuts, their crossing
   counts, the full candidate table, and a 2-3 sentence read of
   whether the cuts land on plausible topic shifts (peek at the
   transcript text around the cut turns).
