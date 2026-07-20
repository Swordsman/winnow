# Arc-split corpus: merge findings (2026-07-20)

Corpus: `transcripts/arc-split/` — the 24-turn Gemini proto transcript
cut at graph-derived arc boundaries (cuts after original turns 10 and
16; method + audit trail in `cbtdag/arc-split/design-spec.md` and
`boundaries.json`). Each part renumbered from t1 and extracted
independently (pro `--re2`, fresh registry each):
part1 37n/15e/43t, part2 10n/5e/21t, part3 21n/13e/10t. Merges:
`merged-p1p2.wno` (pairwise), `merged-3way.wno` (68n/33e/74t, both
validate OK).

## 1. The q5 evidence: `:src` unions verbatim and provenance dies

merge.py already namespaces the **id axis** correctly — colliding node
ids are renumbered into one space (each part had its own c1/q1/a1; the
merged log has exactly one of each, with part2/part3 nodes pushed to
high ids like q12/c28). But the **provenance axis** unions verbatim:
`:src t1` in the merged log names three different original turns —

- `(constraint k1 (same-as compression-method used-for-olfactory-conversation) ... :src t1)` — part2's t1 = **original turn 11**
- `(claim c28 (must-standalone this-form) ... :src t1)` — part3's t1 = **original turn 17**
- part1's own t1 nodes — original turn 1

Nothing in the merged log can tell these apart; the
`transcripts/arc-split/README.md` mapping is the only surviving ground
truth. This is the concrete case for the TODO merge-UX item's options:
session-namespaced provenance (`:src (part2 t1)`) or a per-log id in
the meta header that merge rewrites into `:src`. Evidence only — the
ruling is Joe's.

## 2. Bounded q6 signal: total registry disjunction

The three registries share **zero** term ids (43+21+10 = 74 = merged
union). Same conversation, same model, same prompts — and not one
shared vocabulary entry. The full-conversation run with a single
shared registry minted 59 terms; the split extraction needs 74 for
the same content (+25% from drift alone), with same-concept/
different-id pairs across parts (part1 `compressed-transcript` /
`archival-compression` vs part2 `compressed-meta-log` /
`current-conversation`). Bounded signal per TODO: one author, one
conversation — real alias drift still needs two independent corpora.
But it makes the join problem concrete: without canon anchors or
alias-layer merging, cross-session vocabulary never reconverges.

## 3. Content-hash join axis: untested by this corpus (by design)

Zero node joins across parts (68 = 37+10+21) — the parts have no
overlapping content, so the hash-join path never fired. A future
variant with overlapping splits (shared turns in adjacent parts) would
exercise dedup-on-merge; this corpus exercises collision, not join.

## 4. Bycatch: supersede-vs-§2 tension, surfaced by the status warnings

part1's extraction superseded an action; the `supersede` op sets
`:status superseded` on its target regardless of frame, but §2 lists
`superseded` only for claim/decision — so fold's new status warnings
flag `off-spec status 'superseded' for action a1` (part1 and both
merged logs). Either §2 grows `superseded` where supersede is legal,
or supersede gets frame-restricted. Spec question for Joe; recorded
here, not ruled.

## Next steps

- [ ] Joe: `:src` namespacing ruling (item 1) — spec change, then
      merge.py implementation.
- [ ] Joe: supersede/§2 tension ruling (item 4).
- [ ] Optional: overlapping-split variant to exercise the hash-join
      axis (item 3).
- [ ] Alias-drift proper (q6) still wants two independently-authored
      corpora (item 2 stays bounded until then).
