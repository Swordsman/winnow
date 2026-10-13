# winnow — open items

## Blocked on input
- [ ] **`:modal assumed` (Joe to decide, 2026-10-13).** basis.py treats a
  `:modal may` premise as a hedge, so whatever rests on it is pending. A
  stated assumption ("assuming X...") is a different stance from "X may
  be so", but spec §3 closes `:modal` at must/should/may/can. Add
  `assumed` there, add an epistemic key beside `:modal`, or keep `may`?
- [ ] **Failure frame (design, Joe 2026-10-13).** A ninth frame, `failure`,
  for something that went wrong: what happened is the node (provenance
  via `:src`), its kind is a `:mode` term from the registry
  (miscommunication, wrong-assumption, instruction-violation,
  tool-failure, regression, omission, stale-state), its statuses run open
  → diagnosed → repaired → prevented (plus dismissed, superseded). The
  cause is an ordinary claim, a hypothesis until shown: `(motivates CAUSE
  F)`; repair `(answers FIX F)` (answers widens from questions to open
  items); prevention `(motivates F GUARD)`. No blame in payloads: name the
  faulty assumption or action, and `:by` records who spotted it. basis.py
  already cascades through those edges, so a retracted cause reopens the
  failure's explanation. Cheap first step, no spec change: a trouble view
  listing the failure signals logs already hold (corrected/retracted
  claims, abandoned decisions, blocked/dropped actions, live contradicts,
  honest misses) with their `:src` turns. Test cases from this session:
  the false "uploads can't be compressed" claim (wrong-assumption), the
  normalizer crash on a dangling key (tool-failure), "fold" meaning three
  things (miscommunication).
- [ ] **Extractor guidance for premises.** basis.py is only as good as the
  `depends`/`motivates` edges the extractor writes. Candidate prompt line:
  when someone reasons from a premise ("since X", "assuming X", "if X
  then"), record the conclusion and a `depends` edge to the premise. A
  prompt change, so measure on a live run before adopting.
- [ ] **Extractor prompt rewording (Joe to confirm, 2026-10-13).** The
  fold/frontier/digest split reworded one phrase in the extractor prompt
  (winnow.py and spec §9): "the note graph so far (just the live
  frontier)" became "(a digest of what's live, not the whole graph)",
  because the extractor gets the digest. Prompt wording has moved
  extraction quality before (see the quality comparison below), so the
  next live run should watch for drift; revert the phrase if it hurts.
- [ ] **Further neutral-wording changes (Joe to decide, 2026-10-13).**
  The plugin's winnow, wash and sync skills were reworded in
  sync_swords_plugin#4. These candidates are still open:
  - Rename the wash skill: its name is `context-window-washing`.
    Renaming changes how the skill is invoked.
  - Taskdagger: about 200 "wash" hits in the plugin, 102 of them in
    `skills/taskdagger/references/washing_machine.py`, plus
    `references/wash.md`. The upstream is Swordsman/cbtdag, so change it
    there and then re-copy it to the plugin.
  - The winnow spec: line 3 of `winnow-spec-v0.2.md` says "Streaming
    semantic distillation". Change it here, the source, then re-copy it
    to the plugin's `skills/winnow/references/`. The same tagline is
    in README.md and CLAUDE.md here.
  - Other "distill" uses: the plugin's delegate-fileread and
    delegate-research skills say "distilled returns". This is probably
    benign. Check with a grep before changing anything.
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
  off-spec decision statuses in the live-run handoff). **`about`-targets
  -a-term ruling resolved 2026-07-24:** `about` now legally targets term
  ids (spec §5 note, fold + normalizer updated, 6 tests). **Gloss-quality
  prompt nudge done 2026-07-24:** extractor hint + normalizer R1 rule
  require glosses to define the concept, not restate the label. **Per-delta
  yield curves done 2026-07-24:** `--yield-curve` flag on fold.py,
  `stats_dict()` method, TSV output per delta (3 tests).
- [x] **aimpack packaging (2026-07-24).** `dist/winnow-v0.2.aimpack`
  ships spec + fold.py + demo-deltas.wno (3 files, sha256 checksummed).
  Built with the aimpack skill tool.
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
- [x] **Rung 4 / global KB wiring (2026-07-24, done 2026-07-25).**
  `Resolver` now takes an optional `global_kb` graph; queries that miss
  all session rungs (0–3) check the KB graph at rung 4 before declaring
  an honest miss at rung 5. CLI: `--global-kb runs/mega-all.wno`. KB
  terms are indexed with the same surface/canon/constituent/sense
  machinery as session terms. KB hits are ranked by (status class, mass,
  recency) against the KB graph. Reach handling renders KB hits from the
  KB graph (not the session graph) and skips P3 promotion (KB nodes
  aren't session-resident). 5 new tests (144 total). Trust weighting +
  staleness policy remain open design questions — the mechanism landed
  first, as planned.
- [ ] **Polysemy ruling on two canon-map entries (2026-07-24).** Our own
  canon map may erase specializations rather than collapse synonyms,
  against the polysemy finding (collapse within a sense, preserve across
  senses): `vector-db-chromadb` → "Vector database" folds a technology
  choice into the generic component, and
  `background-ai-as-intent-gatekeeper` → "Intent gatekeeper" folds a
  role-attribution into the role. Both are still in `canon-map.json` as
  committed — revert was proposed, not executed, pending Joe's ruling.
- [ ] **Mega-fold follow-ons (2026-07-24, updated 2026-07-25).** **(a)
  Junk-term exclusion done 2026-07-25:** `junk-terms.json` (90 terms in 5
  categories: edge types, bare words, sentence fragments, combination
  artifacts, placeholders) + `--exclude-terms` flag on mega-fold.py.
  All junk was in `runs/`, zero in `sessions/`. **(b) Semantic dedup pass
  done 2026-07-25:** 30 new canon-map entries across 15 clusters (push/pull
  interfaces, DbC-conversation, compression-prompt family, Vibrational
  Olfaction transcript variants, R1 restatement, etc.). Canon map now 63
  entries. mega-all terms: 362 → 259. 8 new tests (137 total). **(c)
  Remaining MEDIUM clusters and judgment calls:** `etch-scale` vs
  `degree-annotation` (versioned pair?), `resolution-cascade` vs
  `resolution-ladder` (evolution?). **(d)** Procedural normalization
  pre-pass still open — the HIGH tier was entirely mechanical drift, so
  cheap code may catch most of it before an LLM is involved. **(e)**
  Node-level semantic dedup via the same subagent pattern; no `:canon`
  equivalent for nodes. **(f)** No tests yet for `term-table.py`.
- [ ] **Winnow front-end: WO-0 zero-build validation (2026-07-24).**
  Kimi K3 design reviewed; thesis adopted (winnow as compiler from NL
  instructions to structured work orders); compiler framing over
  translation metaphor. WO-0 pipeline: this conversation as corpus →
  extract .wno (done: `sessions/wno-20260724-compiler-framing-93a3.wno`)
  → fold → hand-render work order from graph slice → dispatch to real
  backend → score constraint adherence. Open questions for WO-2:
  reconciliation report format, adapter I/O contract, work-order
  rendering spec. K3 design doc:
  `sessions/kimi-k3-frontend-design.md`.
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
- [x] **Merge `:src` qualification (2026-07-24).** merge.py reads
  `:log-id` from the meta header (not `; id:` comments — comments
  aren't part of the graph). Qualified `:src` values group turns by
  log-id: `(wno-xxx t1 t3)`. Logs without `:log-id` produce bare
  `:src` as before. Spec §7 (meta keys), §8 (grammar), §12 (limits)
  updated; 5 new tests (120 total).
  (Supersede/§2 ruling also 2026-07-24: `superseded` added to all
  frame types — spec §2 + fold.py STATUSES + normalizer prompt updated.)
- [x] **Canon anchors (2026-07-24).** `:canon` key on term entries
  documented in spec §4 + §8 grammar. merge.py joins terms across logs
  by canon anchor (different organic ids, same `:canon` value → one
  merged term, payloads rewritten). Resolver indexes canon values as
  surface forms for resolution. Anchoring happens in idle time (pairs
  with `--stale` maintenance pass); no terms are anchored yet.

## Minor / notes
- [x] **winnow copied into the plugin (2026-10-13).** Code, data files,
  `ds`, `demo-deltas.wno` and `tests/` went to
  Swordsman/sync_swords_plugin `scripts/winnow/`. The spec,
  `docs/hash-ids.md` and `ds-guide.md` went to
  `skills/winnow/references/`. Its SKILL.md was updated, and all 144
  tests pass there. The PR is
  https://github.com/Swordsman/sync_swords_plugin/pull/4, and Joe
  merges it. This repo stays the source, so when copied files change
  here, re-copy them to the plugin. Joe expects winnow to move into
  the plugin eventually.
- [x] **Plugin skill descriptions reworded (2026-10-13).** The plugin's
  README had already swapped classifier-trigger terms for neutral
  wording, but three skill descriptions kept them. Joe asked to reword
  those descriptions, which ride the same PR (sync_swords_plugin#4).
  - winnow: "semantic distillation" became "semantic extraction".
  - wash: "context window washing" became "context review".
  - sync: "self-syncing" became "auto-updating".

  The skill bodies were reworded the same way, on Joe's word that the
  classifier reads whole files. The only old term left in those three
  files is the wash skill's name, `context-window-washing`.

  Other plugin files still use "wash", mostly under taskdagger: about
  200 hits, 102 of them in `washing_machine.py`. The winnow spec copy
  in `references/` still says "semantic distillation", because it
  stays a byte-identical copy of the upstream file.
- [x] **.wno records moved to Session Records (2026-10-13).** The 17
  handoffs and 10 run outputs now live in the Session Records doc
  (https://claude.ai/code/artifact/f57faba9-75c5-418f-9b5f-c21516af9b1f):
  handoffs in its index, runs in its Runs tab, uploaded as `.wno.txt`
  and SHA-256 checked. They're out of git; `sessions/*.wno` and
  `runs/**/*.wno` are gitignored. Boot step 4 downloads the newest
  handoff; download runs under `runs/` before mega-fold.py or
  term-table.py. `demo-deltas.wno` and the cbtdag fixture stay in the
  repo because tests and the spec use them. Older `sessions/` and
  `runs/` paths in this file and in `claims/` are history.
- [x] **Transfer-file ids + receives (2026-07-24).** Moved from comment
  conventions (`; id:`, `; receives:`) into proper graph structure:
  `:log-id` and `:receives` meta keys (§7 table, §8 grammar). fold.py
  stats displays log identity and ancestor list. Comments remain as
  human-readable hints but are not functional graph components.
- [x] **Tier/graph visualizer for Joe (2026-07-24).** Claude-built
  artifact from real fold data (gemini-proto-pro-re2.wno). Interactive
  HTML: stat tiles (48n/39e/59t/~3.5k tokens), four-band tier map
  (fire/hot/warm/cold swim lanes with node pills, frame-type dots,
  status badges), click-to-inspect detail panel (tier reason, mass,
  edges, digest rendering preview), toggleable edge overlay with hover
  tooltips, yield curve (nodes/terms/edges over 12 deltas), table view
  toggle. Both light and dark themes.
- [ ] §10.4 profile learning loop: update rule deliberately unspecified.
  **Reach telemetry sidecar done 2026-07-24:** orchestrator accumulates
  reach events (query, rung, hits, turn) and writes a `.reach` JSON
  sidecar alongside the `.wno` log (2 tests). The update rule (how
  telemetry tunes profile knobs) remains deferred per spec §12 — needs
  a live run to measure.
- [ ] Global KB construction (§12) — **sketch now built (2026-07-24)**:
  `mega-fold.py` realizes merge.py + mass ranking + canon anchors as a
  working cross-log graph. Promoted to a Next-up item (rung 4 wiring);
  see there. Rung 4 remains interface-reserved in `Resolver`.
- [ ] UEL / embedding-anchor representation mode (§12) — v2 identity engine.

## Done
- [x] **Prompts reach ds as files (2026-10-13).** Joe: shoving content in
      as an argument is insane. winnow's deepseek client passed the system
      prompt and the whole user message as argv; one argument over 128 KiB
      fails exec (a 300 KB task: "Argument list too long"), and argv shows
      in `ps`. Now both go in files: `ds --system-file` and the new
      `ds --task-file` (verbatim; dry-run request identical to the argument
      form), stdin closed so ds can't read the caller's. ds-guide's winnow
      commands use files. 1 test (187 total).
- [x] **Claude subagent backend and checker (2026-10-13).** Joe: a
      subagent instead of DeepSeek is fine; Haiku only if Sonnet or better
      double-checks it, Sonnet solo or with Opus checking, Opus solo.
      `--backend claude-code` runs a tool-less `claude -p` from an empty
      scratch directory (project settings only, no MCP, no skills, so no
      hooks, plugins or CLAUDE.md reach it), at `--effort` from `--think`,
      prompt on stdin. `--checker MODEL` runs a second model on the same
      backend over each delta (digest, registry, pulls, new turns,
      candidate) before the procedural normalizer; `claude_policy_error`
      enforces the pairing on both Claude backends. `--model` now defaults
      per backend (deepseek-anthropic no longer gets a Claude model id),
      and `--global-kb` no longer dies on an undefined `verbose`. 5 tests
      (186 total).
- [x] **Max thinking effort by default (2026-10-13).** Joe: running winnow
      below max effort is a bad idea. winnow.py `--think` (default `max`)
      now reaches every backend: `ds --think max` for deepseek, and
      `output_config.effort` with streaming (each model's full output
      capacity as max_tokens) for the
      anthropic and deepseek-anthropic backends. CLAUDE.md's live-run
      convention says so. 2 tests.
- [x] **basis view (2026-10-13).** `basis.py` (`wno.py basis`) labels every
      node with grounds holds / pending / undermined, with the chain to
      each cause, what it rests on, and `--rests-on ID` for a premise's
      blast radius. Joe's design: logic chains, no scores ("Y holds so long
      as X holds"). `depends` premises are all needed, `motivates` reasons
      need one survivor; evidence edges don't cascade except that a live
      `contradicts` leaves the target pending. fold now records each
      delta's turn (`Graph.delta_turns`, `touched_at_turn`). Spec: glossary
      row, §5 note, Files. 14 tests (177 total).
- [x] **ds on DeepSeek-V4.1-Flash (2026-10-13).** `-m flash` asks for
      `deepseek-flash` (the retired `deepseek-v4-flash` is redirected to it
      anyway), `--think low` added, cost estimates use current off-peak and
      peak prices. Flash output went from $0.28 to $0.60/M off-peak, $1.20
      peak. Joe: update ds here, ds-worker is being phased out.
- [x] **fold / frontier / digest split (2026-10-13).** "Fold" had come to
      mean three things in the docs: the replay, the open-items view, and
      the tiered window. Now one script per job behind `wno.py`:
      `sexpr.py` (reader), `fold.py` (log → graph only), `frontier.py`
      (what's still open), `digest.py` (tiers + the window the extractor
      sees; owns P3 promotions as expiry indices the fold never ages),
      `query.py` (query, concepts, stale, hashes). The recency tail moved
      from the frontier into the digest's hot tier, so the frontier is
      strictly open items; digest output is unchanged apart from the hot
      tier's label (checked against the old code on every prefix of both
      repo logs: 81 outputs identical or exactly as intended). Spec gained
      a glossary and §1/§7/§9/§10/§11/Files/Appendix rewrites; §11 now
      shows the real digest entering turn 8 (~460 tokens, not the v0.1
      frontier's 175). CLAUDE.md has a vocabulary rule. 162 tests (144
      kept, 18 new; a test file per script).
      Follow-up: `fold.py --frontier/--digest/--query/--hashes/--concepts/
      --stale` still forward to the new scripts with a deprecation note;
      remove them next release.
- [x] **Mega-fold (2026-07-24).** `mega-fold.py` merges every source
      `.wno` into one graph via content-hash dedup and folds it;
      `--scope sessions|runs|all`, `--overlap`, `--canon-map`,
      `--digest`, `--concepts`, `--out`. All 21 source files validate
      clean — the predicted dangling-ref problem never materialized, no
      validation softening needed. Outputs: `runs/mega-sessions.wno`
      (579n/272e/130t, ~23k tokens), `runs/mega-all.wno`
      (805n/405e/362t, ~35k tokens). Node dedup only 1.2% (exact-hash
      join can't see paraphrase); term dedup 25 → 42 with the canon map.
      `term-table.py` extracts the registry with provenance for subagent
      consumption. `canon-map.json` holds 33 ids → 16 anchors from an
      LLM clustering pass over all 379 terms (29 clusters found, 66
      terms, 17.4%). Drift is concentrated in `runs/`, not `sessions/` —
      repeated extraction of one transcript drifts far worse than
      independent design sessions. Merge-hygiene note: the `super-root`
      undeclared-term gap in mega-all is inherited from
      `demo-deltas.wno`, not merge-caused; mega-fold doubles as a
      repo-wide lint. PR #12. Handoff:
      `sessions/wno-20260724-mega-fold-e1da.wno`.
- [x] **Multi-session corpus (arc-split, 2026-07-20).** First
      cbtdag-structured task (`cbtdag/arc-split/`): graph-derived arc
      boundaries (cuts after t10/t16, min-crossing audit committed),
      3-part corpus renumbered from t1 with ground-truth mapping,
      three independent pro-re2 extractions, pairwise + 3-way merges.
      Findings in `runs/arc-split/notes.md`: id axis namespaced but
      `:src` unions verbatim (q5 evidence); zero term-id overlap
      across parts, 74 vs 59 terms (+25% drift, bounded q6 signal);
      hash-join axis untested (no overlap, by design); supersede/§2
      tension surfaced by the new status warnings.
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
- [x] tests: 129 across fold/orchestrator/merge/reach/split/resolver/status
