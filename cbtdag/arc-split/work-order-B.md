# Work order B — corpus cutter (arc-split-corpus)

Operating mode: spec-only (contracts honored by convention).
Repo: /home/user/winnow. You may create ONLY:
`cbtdag/arc-split/cut_corpus.py`, files under `transcripts/arc-split/`
(create the directory). Do not commit or touch git. Do not modify any
existing file. Do NOT read or wait for `runs/arc-split/boundaries.json`
— build and verify against the fixture contract below; the real
boundaries file may not exist yet (a sibling worker produces it in
parallel).

## Task

Write `cbtdag/arc-split/cut_corpus.py` (zero-dependency python3,
style-matched to the repo's fold.py/split.py) that cuts a
`[tN role]`-format transcript into per-part session files according to
a boundaries JSON, renumbering each part's turn headers to start at t1.

Transcript format: header line `^\[t(\d+)\s+(\S+)\]\s*$` starts a
turn; everything until the next header is that turn's body (see
winnow.py `parse_transcript`). Preserve each turn's body byte-for-byte,
including interior blank lines. Emit parts with exactly one blank line
between turns and a trailing newline (match the source file's layout).

CLI:
```
python3 cbtdag/arc-split/cut_corpus.py BOUNDARIES.json --out-dir DIR
```
Reads `source_transcript` and `parts` from the JSON. Writes
`DIR/part1.txt ... partN.txt` (parts in order) and `DIR/README.md`.

README.md must contain: what the corpus is (one paragraph, mention it
was cut at arc boundaries for the multi-session `:src`-collision
exercise), the boundaries JSON it was cut from, and a mapping table —
one row per original turn: original tN → (part file, part-local tM,
role). This mapping is ground truth for later merge-provenance
verification; it must be complete and correct.

Renumbering: within each part, turns are relabeled t1..tk in order,
roles preserved, bodies untouched.

Round-trip invariant (verify it in code or a self-check block): the
concatenation of all parts' turns, with headers restored to original
numbering via the mapping, reproduces the source transcript exactly.

## Requires-contract: boundaries-json (FROZEN)

Schema per `cbtdag/arc-split/fixtures/expected-boundaries.json`:
`source_transcript`, `parts` (inclusive 1-indexed [start,end] pairs,
gap-free cover of 1..turn_count) are the fields you consume. Trust the
schema, validate the cover property, error loudly on violation.

## Fixture (must pass — this is your verification gate)

```
python3 cbtdag/arc-split/cut_corpus.py \
    cbtdag/arc-split/fixtures/expected-boundaries.json \
    --out-dir /tmp/fixture-parts
```
must produce part1.txt and part2.txt byte-identical to
`cbtdag/arc-split/fixtures/expected-part1.txt` / `expected-part2.txt`,
plus a README.md with a complete 6-row mapping.

## Real run (the deliverable — ONLY if the real boundaries file exists)

If `runs/arc-split/boundaries.json` exists when your fixture passes,
run the cutter on it with `--out-dir transcripts/arc-split`. If it
does not exist, stop after the fixture — the executor runs the real
cut later; say clearly in your report which case happened.

## Acceptance

1. Fixture outputs byte-identical to expected files.
2. Round-trip invariant demonstrated (show the check).
3. README mapping complete (every original turn appears exactly once).
4. Report: files created, whether the real cut ran, any format
   surprises in the source transcript.
