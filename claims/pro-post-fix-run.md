# claim: pro-post-fix-run
- claimed: 2026-07-20T07:05Z
- session: Claude (fable 5), same session as resolver-batch claim
- based-on: HEAD after resolver-batch push (PR #6 branch)
- expected-duration: ~12min (hard stop: fable window closes ~07:18Z)
- ttl: consider this claim dead after 1h

## before
- runs/ has only gemini-proto-flash-baseline.wno (pre-prompt-fix).
- winnow.py deepseek_client has no --re2 passthrough; default thinking
  mode is what made the last pro attempt crawl.
- TODO a9: rerun pro with retry logging in place, consider --re2.

## intent
1. Wire a --re2 flag through winnow.py into the ds invocation
   (--re2 paper, implies --think off per ds-guide).
2. Run: python3 winnow.py transcripts/gemini-winnow-proto.txt
   --out runs/gemini-proto-pro-re2.wno --backend deepseek --model pro
   --re2. First live run exercising ranked reach resolution.
3. Commit whatever completes: the out file even if partial (note turn
   reached), the --re2 patch, TODO note.

## warnings
- DEEPSEEK_API_KEY is env-only, provided by Joe in-chat this session;
  never commit it; treat as rotate-after-session.
- Hard cutoff likely mid-run: a partial out file is expected, not
  breakage. The run log (runs/*.log if present) shows where it stopped.

## completion
- completed: 2026-07-20T07:16Z
- outcome: matched intent. --re2 wired through (committed separately),
  full 24-turn pro run completed at ~7s/turn (the old thinking-mode run
  crawled to turn 6). Output runs/gemini-proto-pro-re2.wno + run log
  runs/pro-re2-run.log committed. Bonus patch: run() now writes the
  delta log incrementally so interrupted runs strand nothing.
- hiccups: fresh container lacked the openai module (ds dependency) —
  first launch burned one retry cycle before pip install fixed it.
  Rejects this run were all dangling edges whose target was a registry
  term rather than a node (e.g. (about q5 archival-compression)) —
  extractor keeps proposing term-targeted edges; normalizer correctly
  rejects, but the pattern is systematic enough to consider either a
  prompt nudge or spec ruling. Logged in TODO successor item.
- checklist:
  - tests green: yes (97, unchanged by run)
  - TODO.md flipped: yes (a9 replaced by quality-comparison successor)
  - handoff updated: yes (amended in same commit)
  - pushed: yes
