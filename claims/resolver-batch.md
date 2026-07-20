# claim: resolver-batch
- claimed: 2026-07-20T06:45Z
- session: Claude (fable 5), remote container, branch claude/claude-md-handoffs-wno-a48tl5
- based-on: fcc2294
- expected-duration: ~20min (hard stop: fable access window closes)
- ttl: consider this claim dead after 2h

## before
- fold.py: no term-usage index, no --concepts, no --stale views. 85 tests green.
- winnow.py Resolver: rung-2 multi-hit resolution truncated arbitrarily; no
  constituent matching (reach for "auth" cannot find "auth-system").
- Registry: no Kimi vocabulary aliases.
- TODO.md: resolver-layer batch is first item under "Next up".

## intent
Execute a1 from kimi-salvage handoff (approved 2026-07-17):
1. fold.py: term-usage index (term -> referencing node ids), status-gated
   mass; --concepts sorted view; --stale view (open/proposed/doing
   untouched N deltas).
2. winnow.py Resolver: rank multi-hit resolutions by (status class, mass,
   recency) replacing rung-2 truncation; constituent-aware matching
   (hyphen-split term ids).
3. Kimi vocabulary as registry aliases: sniping->reach/ladder,
   echo->promotion+mass, concept-space->term-registry.
4. Tests for all of it. TODO.md flip rides with the work.
Done = tests green (85 + new), views produce sane output on real session
files, TODO flipped, pushed.

## warnings
- Rulings NOT to relitigate: no logged importance scalars (d1), mass never
  drives window residency (d3), no scalar salience fields (d4). Mass is
  derived, map-side, excluded from equivalence.
- Fable access window closes ~07:08Z; if this claim has no completion,
  assume hard cutoff mid-work — check git diff fcc2294..HEAD.
