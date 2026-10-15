# claim: failures-assumptions-types
- claimed: 2026-10-13T05:12Z
- session: Claude Code cloud session session_013ezpsWi4jSfkyQzeS687YL, at Joe's request ("implement everything now")
- based-on: b5e8d0e
- expected-duration: ~4h (design workflow, implementation, review workflow)
- ttl: consider this claim dead after 10h

## before
- 8 frames (7 node frames + edge), 8 edges, closed `:modal` (must/should/may/can).
- No way to record that something went wrong, why, or what was done.
- basis.py reads depends (AND) and motivates (OR); a hedge is `:modal may`;
  no assumptions with scope, no conditional claims.
- Relation terms are untyped: nothing checks a payload's arity or argument sorts.
- 181 tests pass.

## intent
The TODO design items, built (Joe: implement everything now):
1. `failure` frame: what went wrong, `:mode` from a failure-mode vocabulary,
   lifecycle statuses, cause/repair/prevention via existing edges; a
   trouble view over failure nodes and the failure signals logs already hold.
2. Assumptions and discharge (Lambek / natural-deduction inspired): an
   explicit assumption marker; conclusions resting on an assumption are
   pending; a discharged conditional ("if X then Y") holds without X.
   Settles the `:modal assumed` question.
3. Typed relations: relation terms declare a type in the registry; fold
   warns and the normalizer rejects payloads that don't fit.
4. Extractor and normalizer prompt guidance for premises, assumptions and
   failures.
Spec, code, tests, docs. Designs chosen by a judge panel; review by an
adversarial workflow before pushing.

## warnings
- Prompt changes move extraction quality; TODO records that the next live
  run should check for drift.
- Plugin copy needs a re-copy afterwards. A live littlewing recording runs
  in the background against the plugin's copy; don't break ds.

## progress (2026-10-15T05:37Z)
- Still live: the same session, resumed after the account's session
  limit stopped its design workflow on 2026-10-13 (9 of 11 agents failed).
  Liveness extended: consider this claim dead after 2026-10-16T06:00Z.
- Design workflow resumed from its run id (workflow wxer71gv3): finished
  agents replay from cache; the failure, assumptions and types designs,
  their judges, and the deepseek-api docs review run again.
- Nothing implemented yet; spec, code and prompts unchanged by this claim.
