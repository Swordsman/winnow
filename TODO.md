# winnow — open items

## Blocked on input
- [ ] **DeepSeek doc audit (q4 from d10 handoff).** Joe is denoising the
  docs that fed the d9/d10 design sessions; audit them against the merged
  spec for dropped commitments when they arrive. Salvage-only — the spec
  is authoritative.

## Next up
- [ ] **Live orchestrator run.** `winnow.py` is tested in replay mode only;
  run it against a real conversation with a real API key and evaluate
  extraction quality (needs `ANTHROPIC_API_KEY` in the environment).
  First corpus candidate: the §11 demo conversation, to compare the live
  loop's output against the hand-authored demo log.
- [ ] **Cross-log merge tool** (v0.3): implement the merge sketch in
  `docs/hash-ids.md` on top of `Graph.hash_id`.

## Minor / notes
- [ ] Check whether "GAM" (latency objection, d10 session) and
  "seventh-block cliff" were load-bearing terms or session shorthand —
  ask the session they came from if it still exists. Spec currently
  paraphrases both generically (§10.1, §10.5); probably fine.
- [ ] §10.4 profile learning loop: update rule deliberately unspecified;
  revisit after reach telemetry exists in a real orchestrator.
- [ ] Global KB construction (§12) — deferred to hash-id era.
- [ ] UEL / embedding-anchor representation mode (§12) — v2 identity engine.
- [ ] aimpack packaging: ship spec + fold.py + registry as an aimpack part.
