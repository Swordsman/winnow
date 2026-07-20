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
