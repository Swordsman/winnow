# claim: basis-view
- claimed: 2026-10-13T04:34Z
- session: Claude Code cloud session session_013ezpsWi4jSfkyQzeS687YL, at Joe's request ("you can build it now")
- based-on: 017f71e
- expected-duration: ~90min
- ttl: consider this claim dead after 6h

## before
- No view says which conclusions still hold when a premise is corrected.
  `depends` ("X needs Y") and `motivates` ("X is the reason for Y") are
  logged but nothing reads them as premises; `supports`/`contradicts` are
  evidence.
- 163 tests pass. `ds` maps `-m flash` to `deepseek-v4-flash`, which
  DeepSeek now serves with DeepSeek-V4.1-Flash; its pricing table is stale.

## intent
Joe's design (2026-10-13): no scores; "assuming X, we infer Y, so Y holds
so long as X holds", as traceable chains that cascade when an error is
found.
- `basis.py`: a view labeling nodes holds / pending / undermined, with the
  chain to each cause and what each rests on. `depends` premises are all
  needed (AND); `motivates` reasons need one survivor (OR). Evidence
  edges don't cascade. Hedged premises (`:modal may`), open or proposed
  items, and premises under a live `contradicts` are pending; corrected,
  retracted, superseded, abandoned, dropped, relaxed, retired and
  deprecated ones undermine. `--undermined`, `--node ID`, `--rests-on ID`
  (blast radius).
- fold records which turn each delta carried, so the view can say when a
  premise changed.
- `wno.py basis`, tests, spec glossary + Files + a §5 note, docs, TODO.
- `ds`: flash maps to `deepseek-flash`, `--think low`, current prices
  with peak hours (Joe: update ds here; ds-worker is being phased out).

## warnings
- Spec's `:modal` set is closed (must/should/may/can), so `assumed` isn't
  used; it goes to TODO as a spec question for Joe.
- A live littlewing recording calls `ds` per request in the background;
  keep `ds` working at every step.

## completion
- completed: 2026-10-13T04:42Z
- outcome: matched the intent. basis.py with holds / pending / undermined,
  chains, rests-on and blast radius; AND over depends, OR over motivates;
  fold records each delta's turn; ds on V4.1 Flash with --think low and
  current prices. `:modal assumed` went to TODO as Joe's call, as planned.
- hiccups: three ds test calls hung for 90 s each around 04:26 UTC; the old
  ds answered in 2 s right after and the new one did too on retry, so it
  was transient (API or proxy), not the edit. ds was restored to the old
  copy while that was checked, so the live littlewing run never used a
  suspect ds.
- checklist:
  - tests green: yes (python3 -m unittest discover -s tests, 177)
  - TODO.md flipped: yes (two Done items, three design items under Blocked on input)
  - handoff updated: not-needed separately; this session's handoff is the
    one pending on claims/fold-frontier-digest-split.md
  - pushed: yes
