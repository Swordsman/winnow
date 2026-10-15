# claim: fold-frontier-digest-split
- claimed: 2026-10-13T04:08Z
- session: Claude Code cloud session session_013ezpsWi4jSfkyQzeS687YL (started in sync_swords_plugin on the littlewing rework), at Joe's request
- based-on: 5f0778b
- expected-duration: ~2h
- ttl: consider this claim dead after 6h

## before
- `fold.py` (676 lines) holds the s-expression reader, the Graph replay, and
  every view: snapshot, frontier (open items plus the last 6 live
  claims/defs), tiers and digest, query, concepts, stale, hashes, yield
  curve. One CLI, one flag per view.
- The docs use "fold" for three things: the replay (spec §7), the frontier
  (`--frontier`) and the tiered window (`--digest`). winnow.py hands the
  extractor `g.digest()`, while spec §1 and §9 and the extractor prompt say
  it gets the frontier.
- 144 tests pass: `python3 -m unittest discover -s tests`.
- Import from fold: winnow.py, merge.py, split.py, mega-fold.py,
  term-table.py, every test file.

## intent
Joe's ask (2026-10-13): three needs, three implementations, each named for
what it does; separate scripts with `wno.py` as the primary interface; the
recency tail goes wherever makes sense.
- `sexpr.py`: the reader/printer (tokenize, parse, sx, anns, Lit,
  _symbols). fold.py re-exports them, so existing imports keep working.
- `fold.py`: log to graph only: replay, validate, snapshot, stats, yield
  curve, and the mass and hash-id metrics other code ranks and joins by.
- `frontier.py`: graph to open items: live constraints, proposed
  decisions, open questions, todo/doing/blocked actions. The recency tail
  leaves the frontier.
- `digest.py`: graph plus profile to fire/hot/warm/cold. Hot is the
  frontier plus the recency tail. Owns P3 promotions, made expiry-based so
  fold no longer ages them.
- `query.py`: query, concepts, stale, hashes.
- `wno.py`: one front door dispatching to every script.
- `fold.py --frontier/--digest/--query/--concepts/--stale/--hashes` keep
  working for one release, forwarding with a note on stderr.
- Callers and tests updated, a test file per new module, a spec glossary
  plus §1, §9, §10, §11, Files and Appendix, the extractor prompt wording,
  a CLAUDE.md vocabulary rule, README, TODO.md.
- Done means: all tests green; the digest of existing logs unchanged
  except its hot-tier label; the spec §11 frontier demo regenerated.

## warnings
- Rewording the extractor prompt touches model behavior; flagged for Joe.
- The plugin copy (Swordsman/sync_swords_plugin `scripts/winnow/`) needs a
  re-copy after this lands. littlewing's recorder there loads fold.py's
  reader by path.
- Never commit .wno records.

## progress (2026-10-13, before completion)
- Work pushed: a3cfb0e (the split) and a65e557 (normalizer rejects a
  dangling annotation key; found by the live run below). PR #15. 163 tests.
- Plugin copy done: Swordsman/sync_swords_plugin PR #5, same branch name.
- Remaining: the session handoff. littlewing's new wno mode is recording
  this session live (DeepSeek flash, scratch storage only). When it
  finishes: review it with `fold.py --snapshot`, add the `; id:` /
  `; receives:` header and `:log-id`, upload to Session Records as
  `.wno.txt`, index it, then write the completion section.

## progress (2026-10-15T05:37Z)
- The live recording hit its 7000 s limit on 2026-10-13 06:49Z and kept
  turns 1-28 (266 nodes, 141 edges, validation OK). littlewing now drops
  background-task notifications from transcripts (plugin f707b00), which
  merges old t26-t28 into t26; the record was remapped to match
  (12 `:src t28` -> t26) and still folds clean.
- Interim handoff uploaded to Session Records:
  wno-20261013-littlewing-fold-split-2ca4.wno.txt, asset
  6abac979dc385f4ebc326c4c36dd3185, index row marked INTERIM (turns 1-26).
  Receives wno-20261012-tree-code-goal-7c1e.
- Running: winnow over turns 27-54 (deepseek flash, think max), seeded
  with that record. When it lands: review with `fold.py --snapshot`
  (drop the spurious `(locate ...)` questions the old reach bug made,
  add what's missing, including turns 55+ by hand), upload again,
  repoint the index row, then write the completion section here.
