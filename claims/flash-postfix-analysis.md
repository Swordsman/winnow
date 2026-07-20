# claim: flash-postfix-analysis
- claimed: 2026-07-20T07:39Z
- session: Claude (fable 5), remote container, branch claude/fable-wno-files-review-3y82sh
- based-on: 76df2f9
- expected-duration: ~25min
- ttl: consider this claim dead after 2h

## before
- runs/gemini-proto-flash-postfix-re2.wno exists (run completed per
  924f455) but the analysis section in runs/comparison-notes.md still
  says "Analysis of the finished run is the open item".
- comparison-notes.md next-steps list has the post-fix flash rerun
  analysis as its first unchecked box; TODO.md quality-comparison item
  mirrors it.
- Headline table covers flash-baseline / pro-re2 / demo only.

## intent
Repeat the first-pass offline analysis verbatim on the post-fix flash
run to isolate the model variable from the prompt version:
1. fold.py stats (nodes/edges/terms/edge-types/ratios) added to the
   headline table as a fourth column.
2. Findings re-checked against the postfix run: edge-type collapse,
   term explosion / registry junk (--concepts), revision tracking
   (supersedes/answers), gloss quality, reject shapes from the run log.
3. comparison-notes.md updated (postfix section replaces the "open
   item" text; next-steps box checked); TODO.md quality-comparison item
   updated in the same commit.
Done = notes updated, TODO flipped, tests still green, pushed.

## warnings
- Analysis only — no code changes intended. If a fold.py bug surfaces
  mid-analysis, it becomes a separate claim/commit.
- The `about`-targets-a-term ruling and gloss-quality prompt nudge stay
  open (need Joe / a next live run); do not fold them into this claim.

## completion
- completed: 2026-07-20T07:52Z
- outcome: matched intent. Headline table gained the flash-postfix
  column; findings 7–13 added (analysis replaces the "open item"
  text); next-steps box checked; TODO.md updated same commit. Headline
  result: baseline's term explosion and edge-type collapse were prompt
  artifacts, not model capability — flash-postfix lands 26 terms / 7
  of 8 edge types; residual model gaps are yield (37 vs 48 nodes,
  0.57 vs 0.81 edges/node), frame grammar, status discipline.
- hiccups: analysis surfaced a normalizer/fold validation gap rather
  than a fold bug — off-spec status values (question
  `partially-answered` in flash-postfix, `resolved` in pro-re2, claim
  `open` in baseline) pass through; fold validates ETYPES but not §2
  status vocab. Recorded as finding 12 + next-steps item + TODO note,
  NOT fixed here per this claim's warnings. Also corrected mid-analysis:
  flash's `(def d1)` reject is a malformed legal frame, not an invented
  one — only `answer` was invented.
- checklist:
  - tests green: yes (tests/, 100 passed — analysis only, no code)
  - TODO.md flipped: yes (same commit)
  - handoff updated: yes — session handoff committed next in same push
  - pushed: yes
