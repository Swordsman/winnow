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
