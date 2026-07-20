# Arc-split corpus — design spec (cbtdag phase 0)

2026-07-20. Author: Claude (fable 5), from Joe's declared intent in
TODO.md ("Multi-session corpus (arc-split, Joe 2026-07-17)") — the goal,
method sketch, and q5/q6 framing are Joe's; the concrete decisions below
are this session's resolutions of the open choices, revisable on veto.

## Goal

Produce a multi-session test corpus by splitting an existing transcript
at conversational-arc boundaries, then independently extract each part
and merge the results — generating the concrete `:src`-collision
evidence the merge-UX-hardening spec change needs (TODO q5). Session
boundaries are arbitrary under managed context, so arc boundaries are
the honest cut points.

## Inputs

- `transcripts/gemini-winnow-proto.txt` — 24 turns, `[tN role]` header
  per turn (role ∈ user/assistant), the only transcript in-repo.
- `runs/gemini-proto-pro-re2.wno` — best extraction of that transcript
  (48 nodes, 39 edges, full edge palette); arc detection runs on this
  graph, not on raw text.
- `winnow.py parse_transcript` takes turn numbers from the `[tN]`
  headers (winnow.py:152), NOT from an internal counter — so `:src`
  values in an extraction mirror the part file's own labels.

## Decisions

- **D1 detection source.** Arcs are detected on the pro-re2 graph.
  `split.py --component` output is a sanity cross-check only (TODO:
  "arcs ≈ split.py dense components").
- **D2 detection method.** Turn-axis minimum-crossing cut. A node's
  turn is the numeric part of its `:src` (t7 → 7; nodes without `:src`
  are ignored). For each candidate boundary b (between turns b and
  b+1), the crossing count is the number of edges whose endpoint turns
  straddle b. Choose K=2 cuts (→ 3 parts), minimizing total crossings,
  subject to: each part ≥ 5 turns. Tie-break: prefer the more balanced
  partition (minimize the largest part). Report per-candidate crossing
  counts so the choice is auditable.
- **D3 boundary artifact (the frozen A→B contract).**
  `runs/arc-split/boundaries.json`:
  ```json
  {"source_log": "runs/gemini-proto-pro-re2.wno",
   "source_transcript": "transcripts/gemini-winnow-proto.txt",
   "turn_count": 24,
   "cuts": [8, 17],
   "parts": [[1, 8], [9, 17], [18, 24]],
   "crossings_at_cuts": [2, 3],
   "all_candidates": {"5": 7, "6": 4, "...": 0},
   "rationale": "one line"}
  ```
  (`cuts` values are illustrative.) `parts` are inclusive
  1-indexed turn ranges; `cuts`[i] is the last turn of part i+1.
- **D4 corpus format.** `transcripts/arc-split/part{1,2,3}.txt`:
  verbatim text slices EXCEPT the `[tN role]` headers are renumbered
  so every part starts at t1 (roles preserved) — required so each
  independent extraction emits colliding `:src` values (t1... in every
  log), which is the q5 exercise. The original↔part-local turn mapping
  goes into `transcripts/arc-split/README.md` as ground truth for
  later provenance verification.
- **D5 extraction.** Executor-run (not a worker): three live runs,
  `python3 winnow.py transcripts/arc-split/partN.txt --out
  runs/arc-split/partN-pro-re2.wno --backend deepseek --model pro
  --re2` — the established best config; DEEPSEEK_API_KEY is a
  persistent env var (Joe, 2026-07-20). Each run has a fresh registry
  and fresh id/turn space by construction.
- **D6 merge + analysis.** Executor-run: `merge.py` over the three
  part logs (pairwise then three-way, in file order), output under
  `runs/arc-split/`. The analysis notes (`runs/arc-split/notes.md`)
  document: `:src` collisions unioned verbatim (q5 evidence),
  cross-part registry/alias drift (bounded q6 signal only — same
  conversation, one author, so real alias drift needs two independent
  corpora; say so), content-hash join behavior, and anything merge
  surfaces as open questions.
- **D7 non-goals.** No merge.py changes, no spec changes (`:src`
  namespacing design is Joe's ruling, this corpus is its evidence), no
  registry-split work, no fold/winnow changes.
- **D8 layout.** cbtdag artifacts in `cbtdag/arc-split/` (this spec,
  dag.json, work orders); corpus in `transcripts/arc-split/`; run
  outputs + analysis in `runs/arc-split/`.

## Semantic conventions

- Turns are 1-indexed everywhere; `tN` labels and JSON integers refer
  to the same axis. Part ranges are inclusive on both ends.
- "Crossing" counts edges only (both endpoints are nodes with `:src`);
  term references don't cross.
- Part files must round-trip: concatenating the parts' bodies in order
  and restoring original numbering reproduces the source transcript
  byte-for-byte (modulo the renumbered header lines themselves).

## Chunks and contracts (spec-only mode)

- **Chunk A — arc detector** (worker): reads D1 inputs, implements D2,
  writes D3 artifact. Provides: boundaries.json (contract above, with
  fixture). Requires: nothing beyond repo files. Tool lands at
  `cbtdag/arc-split/detect_arcs.py` (project tooling, not shipped code;
  zero-dependency python3, repo style).
- **Chunk B — corpus cutter** (worker): reads D3 artifact + source
  transcript, implements D4, writes part files + README. Provides:
  part files + mapping README. Requires: boundaries.json (may be built
  against the fixture; A and B run in parallel against the frozen
  contract). Tool lands at `cbtdag/arc-split/cut_corpus.py`.
  Verification includes the D4 round-trip property.
- **Chunk C — extraction** (executor): D5. Gated on B verified.
- **Chunk D — merge + notes** (executor): D6. Gated on C.

Contract A→B fixture (freeze-gate): a synthetic 6-turn transcript +
boundaries {"cuts":[3],"parts":[[1,3],[4,6]]} pair checked into
`cbtdag/arc-split/fixtures/`; B must cut the fixture transcript
correctly before touching the real one; A must emit fixture-shaped
JSON.

## Acceptance

1. boundaries.json exists, schema-valid, cuts satisfy D2 constraints,
   crossing table auditable against the pro-re2 graph.
2. Part files: 3, renumbered from t1, round-trip property holds,
   README mapping complete.
3. Three part logs fold + validate OK (status warnings acceptable).
4. Merged log folds; notes.md states the q5 evidence with concrete
   node examples (which t1 is whose).
5. TODO.md arc-split item flipped with pointers; claim completed;
   nothing outside D8 paths touched except TODO/claims/sessions.
