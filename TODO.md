# winnow — open items

## Blocked on input
- [ ] **DeepSeek doc audit (q4 from d10 handoff).** Joe is denoising the
  docs that fed the d9/d10 design sessions; audit them against the merged
  spec for dropped commitments when they arrive. Salvage-only — the spec
  is authoritative.
- [ ] **Live orchestrator run.** `winnow.py` is tested in replay mode only.
  Plan: Joe's DeepSeek mini-harness (deferred — code needs retrieving), or
  an `ANTHROPIC_API_KEY` in this environment, whichever lands first.
  First corpus: the §11 demo conversation, to compare the live loop's
  output against the hand-authored demo log.
- [ ] **aimpack packaging.** Needs the aimpack format spec / an example
  pack — not in this repo. Ship spec + fold.py + registry as a part once
  available.

## Next up
- [ ] **Merge UX hardening** (post-first-real-use): `:src` values collide
  across logs (t1 in log A ≠ t1 in log B); currently unioned verbatim.
  Needs session-namespaced provenance (e.g. `:src (sess-a t1)`) or a
  log-id in the meta header — spec change, so wants a real multi-session
  corpus first.
- [ ] **Alias-aware hashing.** `hash_id` hashes canonical term ids; two
  logs whose registries alias the same surface form to different ids
  won't join. Registry reconciliation pass before merge (cheap version:
  alias-table intersection warning; real version: UEL).

## Minor / notes
- [ ] Check whether "GAM" (latency objection, d10 session) and
  "seventh-block cliff" were load-bearing terms or session shorthand —
  ask the session they came from if it still exists. Spec currently
  paraphrases both generically (§10.1, §10.5); probably fine.
- [ ] §10.4 profile learning loop: update rule deliberately unspecified;
  reach telemetry now exists in the orchestrator (rung numbers per reach)
  but isn't yet persisted to a sidecar — add when there's a live run to
  measure.
- [ ] Global KB construction (§12) — deferred to hash-id era; rung 4
  interface reserved in `Resolver`.
- [ ] UEL / embedding-anchor representation mode (§12) — v2 identity engine.

## Done
- [x] v0.2 spec: §10 tiers, meta header, §3/§7/§9 patches, renumbering (PR #1)
- [x] fold.py: digest/tiers, query layer, hash-id prototype, P3 promotion TTL
- [x] winnow.py: §9 orchestrator loop; §10.5 resolution ladder (rungs 0–3,
      honest miss, optional cheap-inference escalation), reach handling
      with extractor re-pass, `--seed` session continuation
- [x] merge.py: cross-log merge on content-hash join keys; conflicts
      surface as open questions; self-merge is a fixed point
- [x] split.py: procedural slicing (query/seed + hops/component expansion,
      validity closure, constraint carry, cut-edge comments, --rest cover)
- [x] tests: 85 across fold/orchestrator/merge/reach/split
