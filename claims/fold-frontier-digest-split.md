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
