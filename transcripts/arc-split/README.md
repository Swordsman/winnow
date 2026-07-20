# arc-split corpus

Per-part transcripts cut from `transcripts/gemini-winnow-proto.txt` at arc boundaries, for the multi-session `:src`-collision exercise (cbtdag/arc-split/design-spec.md): each part is extracted independently into its own winnow log with a fresh id/turn space, so every part's nodes carry `t1..`-style `:src` values by construction -- the collision evidence the merge-UX hardening work needs. Turn headers are renumbered per part to start at `t1` (roles preserved, bodies untouched); the mapping table below is the ground truth for translating a part-local `tM` back to the original corpus's `tN` during later merge-provenance verification. Cut with `cbtdag/arc-split/cut_corpus.py` from the boundaries JSON below.

## Boundaries JSON (`runs/arc-split/boundaries.json`)

```json
{
  "source_log": "runs/gemini-proto-pro-re2.wno",
  "source_transcript": "transcripts/gemini-winnow-proto.txt",
  "turn_count": 24,
  "cuts": [
    10,
    16
  ],
  "parts": [
    [
      1,
      10
    ],
    [
      11,
      16
    ],
    [
      17,
      24
    ]
  ],
  "crossings_at_cuts": [
    4,
    2
  ],
  "all_candidates": {
    "5": 7,
    "6": 6,
    "7": 9,
    "8": 10,
    "9": 10,
    "10": 4,
    "11": 5,
    "12": 5,
    "13": 5,
    "14": 4,
    "15": 4,
    "16": 2,
    "17": 2,
    "18": 2,
    "19": 5
  },
  "rationale": "exhaustive search over 55 valid 2-cut partitions (min-part 5); picked minimum total crossings (6), tie-broken by balance then lowest cut indices"
}
```

## Turn mapping

original -> part file, part-local turn, role

| original | part file | part-local | role |
|---|---|---|---|
| t1 | part1.txt | t1 | user |
| t2 | part1.txt | t2 | assistant |
| t3 | part1.txt | t3 | user |
| t4 | part1.txt | t4 | assistant |
| t5 | part1.txt | t5 | user |
| t6 | part1.txt | t6 | assistant |
| t7 | part1.txt | t7 | user |
| t8 | part1.txt | t8 | assistant |
| t9 | part1.txt | t9 | user |
| t10 | part1.txt | t10 | assistant |
| t11 | part2.txt | t1 | user |
| t12 | part2.txt | t2 | assistant |
| t13 | part2.txt | t3 | user |
| t14 | part2.txt | t4 | assistant |
| t15 | part2.txt | t5 | user |
| t16 | part2.txt | t6 | assistant |
| t17 | part3.txt | t1 | user |
| t18 | part3.txt | t2 | assistant |
| t19 | part3.txt | t3 | user |
| t20 | part3.txt | t4 | assistant |
| t21 | part3.txt | t5 | user |
| t22 | part3.txt | t6 | assistant |
| t23 | part3.txt | t7 | user |
| t24 | part3.txt | t8 | assistant |
