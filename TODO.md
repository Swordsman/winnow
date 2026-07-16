# winnow — open items

## Blocked on input
- [ ] **DeepSeek doc audit (q4 from d10 handoff).** Joe is denoising the
  docs that fed the d9/d10 design sessions; audit them against the merged
  spec for dropped commitments when they arrive. Salvage-only — the spec
  is authoritative.
- [ ] **Pro post-fix live run (a9).** Flash baseline is done
  (`runs/gemini-proto-flash-baseline.wno`, pre-prompt-fix). The pro run
  with fixed prompts showed zero rejects through turn 6 but crawled
  (default thinking mode + degraded connection, retries invisible in
  the pre-patch process). Rerun with retry logging now in place;
  consider `--re2` (implies --think off) for speed. Then compare
  flash-baseline vs pro vs hand-authored quality.
- [x] **Live orchestrator run.** Done via Joe's ds harness +
  DEEPSEEK_API_KEY. Backend flag: `--backend deepseek --model pro|flash`.
  First corpus was the Gemini proto-winnow transcript (not §11 demo —
  still worth doing for the hand-authored comparison).
- [ ] **aimpack packaging.** Needs the aimpack format spec / an example
  pack — not in this repo. Ship spec + fold.py + registry as a part once
  available.

## Next up
- [ ] **Live relay experiment (Joe's proposal, fresh session).** Claude in
  haiku mode forwards messages between Joe and DeepSeek (via ds);
  DeepSeek and/or haiku generate .wno updates live during the
  conversation. Measures extraction on a real live conversation instead
  of a replayed transcript, and iterates toward JIT context window
  compilation: the relay's context becomes folded digest + live tail
  (fold.py tier rendering), and the test is whether references to
  scrolled-out material resolve from the digest alone (resolution
  ladder on live traffic).
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
- [ ] **Transfer-file ids + receives: lines (spec patch).** Orphaned
  ancestor references bit us live: the d10 handoff used terms (gam,
  rampart, mandol, cuhk-critique) declared only in its ancestor file,
  which the boot instructions never listed. Convention proposed by the
  d10 session: `; id: wno-YYYYMMDD-slug-4hex` plus one `; receives:`
  line per ancestor in the header comment, so a fresh session can detect
  a missing ancestor immediately. Wants a small spec section alongside
  the transfer conventions.
- [x] Check whether "GAM" (latency objection, d10 session) and
  "seventh-block cliff" were load-bearing terms or session shorthand —
  resolved: they're published research systems (GAM, RAMPART, Mandol,
  CUHK critique), ingested from the DeepSeek survey material. Term
  declarations + claims c42–c50 live in the 77-node ancestor file, now
  in-repo as `sessions/d9-d10-session-transfer.wno`.
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
