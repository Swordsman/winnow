# winnow — open items

## Blocked on input
- [ ] **DeepSeek doc audit (q4 from d10 handoff).** Joe is denoising the
  docs that fed the d9/d10 design sessions; audit them against the merged
  spec for dropped commitments when they arrive. Salvage-only — the spec
  is authoritative.
- [ ] **Quality comparison (successor to a9).** First pass done:
  `runs/comparison-notes.md` (2026-07-20) — flash-baseline shows
  edge-type collapse + term explosion; pro-re2 uses the full edge
  palette with supersede chains; registry discipline is both runs' gap
  to hand-authored. **Post-fix flash rerun analysis done 2026-07-20**
  (notes findings 7–13): prompt version, not model, caused the
  baseline's term explosion and edge collapse; flash's residual gaps
  are node/edge yield, frame grammar (question+claim only survived),
  and status discipline. New finding 12: off-spec status values
  (`partially-answered`, `resolved`, claim `open`) pass normalizer and
  fold unvalidated — fold checks ETYPES but not §2 status vocab, and
  status drives Resolver rank class + mass gating; small code-level
  fix candidate — **fixed 2026-07-20** (STATUSES table, fold warns /
  normalizer rejects, 9 tests; sweep also surfaced two grandfathered
  off-spec decision statuses in the live-run handoff). Remaining, per
  the notes' next-steps list: the `about`-targets-a-term ruling (100%
  of pro rejects), gloss-quality prompt nudge, optional per-delta
  yield curves.
- [ ] **aimpack packaging.** Needs the aimpack format spec / an example
  pack — not in this repo. Ship spec + fold.py + registry as a part once
  available.
- [ ] **Questions for Hermes (wno review 2026-07-20, needs Joe to
  relay).** From the review of the 801da04 ENI-handoff expansion:
  (a) Δ20/turn-39 hole in `eni-winnow-design-20260719.wno` — delta
  labels jump Δ19 (turn 38b) → Δ21 (turn 40), no turn 39 anywhere; did
  a delta get lost from ENI's draft, or is it a labeling skip?
  (b) 801da04's commit message claims the c2 attribution fix, but
  `(update c2 :by assistant)` already existed in fabc99c — confirm the
  fix is ENI's, and that c2 ("hard-ceiling context-window") really was
  assistant articulation. (c) FYI: the review restored the
  `(supports c99 c97)` edge dropped by the Δ21 rewrite (new c99
  restates old c99's content; the renumbered sibling edge was carried
  over, so the drop read as accidental) — veto welcome. (d) the
  `; id:`/`; receives:` header convention should travel to Hermes
  (already noted in resolver-batch handoff); meta file header also
  says "companion to eni-winnow-design.wno", missing the date suffix.

## Next up
- [ ] **ENI proposals: inclusion decision (Joe 2026-07-20, "relates to
  the ultimate goal").** Design session with Joe to rule on the three
  proposed decisions in `sessions/eni-winnow-design-20260719.wno`
  (surfaced by `--stale`): d1 canonical-form reduction, d2/d3
  universal-foundation-beneath-linguistic-foundation. Plus the polysemy
  finding (c33/c37/c96): the collapse contract preserves synonyms but
  erases polysemes — collapse synonyms *within* a sense, preserve
  polysemes *across* senses. Directly load-bearing for the Gau merge
  (cross-conversation vocabulary drift) and JITCW. Cheapest first step
  if adopted: sense-qualified term ids (tap/faucet vs tap/strike) +
  registry split into alias-layer and concept-layer jobs (c48), which
  also positions canon anchors as the universal-layer join. **First
  mechanical step landed 2026-07-20:** sense-qualified tids
  (`tap/faucet`) supported in the Resolver — bare word reaches all
  parked senses ranked, qualified reference hits one; plus a latent
  kebab-comparison bug fixed in `_matches`. Executive decision (Joe
  delegated): wire-format convention is `word/sense`, no spec change
  yet — spec §-note rides with the registry-split design session. Bigger
  pieces (utterances-as-nodes, retroactive disambiguation, multi-word
  spans) are v2-scale — sequence after the registry split proves out. (Joe's proposal, fresh session).** Claude in
  haiku mode forwards messages between Joe and DeepSeek (via ds);
  DeepSeek and/or haiku generate .wno updates live during the
  conversation. Measures extraction on a real live conversation instead
  of a replayed transcript, and iterates toward JIT context window
  compilation: the relay's context becomes folded digest + live tail
  (fold.py tier rendering), and the test is whether references to
  scrolled-out material resolve from the digest alone (resolution
  ladder on live traffic). Variant worth testing: side-payload — the
  responding frontier model emits .wno ops alongside its reply (one
  call); manager-side decomposition is the weak link per flash-baseline
  evidence, so keep the lightweight model's role recognition-only (c29).
- [ ] **Multi-session corpus (arc-split, Joe 2026-07-17).** Produce the
  corpus ourselves instead of waiting: split an existing transcript at
  conversational-arc boundaries (arcs ≈ split.py dense components;
  session boundaries are arbitrary under managed context). Exercises
  `:src` namespacing (q5). Note: a single-conversation split shares one
  registry, so alias drift (q6) needs two independently-extracted
  corpora instead.
- [ ] **Merge UX hardening** (post-first-real-use): `:src` values collide
  across logs (t1 in log A ≠ t1 in log B); currently unioned verbatim.
  Needs session-namespaced provenance (e.g. `:src (sess-a t1)`) or a
  log-id in the meta header — spec change; test corpus now planned via
  arc-split item above.
- [ ] **Alias-aware hashing.** `hash_id` hashes canonical term ids; two
  logs whose registries alias the same surface form to different ids
  won't join. Upgraded mechanism (2026-07-17): **canon anchors** —
  optional `:canon` key on term entries attaching a Wikipedia-title
  canonical form, attach-don't-replace; organic ids stay the wire
  format, anchors are cross-lineage join keys (same pattern as hash
  ids). fold.py already tolerates the key; needs §8 grammar note +
  merge/Resolver consumption. Anchoring happens in idle time (pairs
  with `--stale` maintenance pass).

## Minor / notes
- [ ] **Transfer-file ids + receives: lines (spec patch).** Orphaned
  ancestor references bit us live: the d10 handoff used terms (gam,
  rampart, mandol, cuhk-critique) declared only in its ancestor file,
  which the boot instructions never listed. Convention proposed by the
  d10 session: `; id: wno-YYYYMMDD-slug-4hex` plus one `; receives:`
  line per ancestor in the header comment, so a fresh session can detect
  a missing ancestor immediately. Wants a small spec section alongside
  the transfer conventions.
- [ ] **Tier/graph visualizer for Joe.** Interactive model of tiers,
  fold, push/pull for design intuition (Joe: needed before evaluating
  ranking/profile-learning items). Options: Kimi swarm / AI Studio
  (ground them with the spec file + real `--digest` output, not a
  paraphrase) or a Claude-built artifact from real fold data.
- [ ] §10.4 profile learning loop: update rule deliberately unspecified;
  reach telemetry now exists in the orchestrator (rung numbers per reach)
  but isn't yet persisted to a sidecar — add when there's a live run to
  measure.
- [ ] Global KB construction (§12) — deferred to hash-id era; rung 4
  interface reserved in `Resolver`. Construction sketch now exists:
  merge.py + term-usage index + mass ranking + canon anchors.
- [ ] UEL / embedding-anchor representation mode (§12) — v2 identity engine.

## Done
- [x] **Resolver-layer batch (2026-07-20).** fold.py: `term_usage()` /
      `term_mass()` (status-gated, superseded/rejected/retracted gated
      out), `node_mass()`, `last_touch` tracking, `--concepts` sorted
      view, `--stale N` view. winnow.py Resolver: `_rank()` by (status
      class, mass, recency) applied to all multi-hit rungs, rung-2
      ranked truncation, constituent matching (auth → auth-system),
      KIMI_ALIASES (sniping/echo/concept-space). 12 new tests (97
      total). Mass is map-side only — never logged, never residency.
- [x] Kimi doc assessment + salvage ledger (2026-07-17): usage-mass /
      ranking / constituent matching / stale view / canon anchors /
      side-payload variant adopted; logged importance scalars and scalar
      salience fields rejected with receipts. Full rulings in
      `sessions/kimi-salvage-session-transfer.wno`.
- [x] Check whether "GAM" (latency objection, d10 session) and
  "seventh-block cliff" were load-bearing terms or session shorthand —
  resolved: they're published research systems (GAM, RAMPART, Mandol,
  CUHK critique), ingested from the DeepSeek survey material. Term
  declarations + claims c42–c50 live in the 77-node ancestor file, now
  in-repo as `sessions/d9-d10-session-transfer.wno`.
- [x] **Live orchestrator run.** Done via Joe's ds harness +
  DEEPSEEK_API_KEY. Backend flag: `--backend deepseek --model pro|flash`.
  First corpus was the Gemini proto-winnow transcript (not §11 demo —
  still worth doing for the hand-authored comparison).
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
