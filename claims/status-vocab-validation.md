# claim: status-vocab-validation
- claimed: 2026-07-20T08:02Z
- session: Claude (fable 5), remote container, branch claude/fable-wno-files-review-3y82sh
- based-on: 6c5e751
- expected-duration: ~30min (design here; implementation delegated to a
  subagent per Joe's 2026-07-20 process instruction)
- ttl: consider this claim dead after 2h

## before
- Spec §2 defines a closed status vocabulary per frame; neither fold.py
  nor the winnow.py normalizer enforces it. Live-run artifacts contain
  off-spec values (question `partially-answered` in flash-postfix,
  `resolved` in pro-re2, claim `open` in baseline) and validate OK.
- fold.py validates edge types (ETYPES, errors list, line ~251) but has
  no per-frame status table; winnow.py normalizer rejects unknown
  frames/edges/dangling refs but not off-spec statuses.
- Status drives Resolver rank class + mass gating, so off-spec values
  silently land in the wrong rank class (comparison-notes finding 12).
- 100 tests green.

## intent (design — implementation contract for the subagent)
1. fold.py: `STATUSES` per-frame dict mirroring §2 exactly
   (claim: live/corrected/retracted/superseded; def: live/deprecated;
   question: open/answered/dropped; decision: proposed/frozen/
   superseded/abandoned; constraint: live/relaxed/retired; action:
   todo/doing/done/blocked/dropped; artifact: live/deprecated).
2. fold.py: off-spec status (on add AND on update ops) is a **warning,
   not an error** — committed logs are records; existing runs/*.wno and
   sessions/*.wno must keep validating OK. Warnings get their own list
   and are printed in the stats block (count + items); validation line
   stays OK when only warnings exist.
3. winnow.py normalizer: off-spec status on an emitted op → reject with
   reason `off-spec status S for FRAME` — consistent with its existing
   grammar-enforcement posture; extractor re-pass is the recovery path.
   Reuse fold's STATUSES (winnow already imports from fold) — one
   source of truth, no duplicated table.
4. Normalizer prompt: one added line stating the legal statuses per
   frame (keep it compact, mirror §2).
5. Tests (~5): fold warns on off-spec add / off-spec update; fold
   silent on legal statuses; normalizer rejects off-spec; full suite +
   all repo .wno files still validate OK.
6. No spec change — §2 already states the vocabulary; this closes a
   code gap. Done = tests green (100 + new), all 14 repo .wno files
   still OK, TODO note updated, pushed.

## warnings
- Do NOT make fold hard-fail on off-spec statuses — that would flip
  committed run artifacts from OK to failing and rewrite the meaning of
  recorded results.
- The rank-class map in winnow.py (~line 250) contains "rejected",
  which is also outside §2's claim vocab — it is a tolerant rank map,
  deliberately out of scope here; don't "fix" it.
- The `about`-targets-a-term ruling and gloss nudge stay open (Joe);
  not part of this claim.
