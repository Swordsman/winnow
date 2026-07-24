# Winnow Front-End — Unified Design & Plan

**Status:** v0.2 DRAFT — supersedes both `winnow-harness-design-spec.md` (v0.1,
integrated-agent architecture) and `winnow-frontend-proposal.md` (the
proposal) upon acceptance of the decision items in §1. Until then this is
the unified record of the design discussion: architecture, contracts,
evaluation, risks, roadmap.
**Date:** 2026-07-25
**Baselines:** `Swordsman/winnow @ 1cdbf24` · cbtdag concepts per
`cbtdag/arc-split/` artifacts · harness research per the coding-agent-harnesses
skill (July 2026 snapshot) · side-session research conclusions (seven-axes
taxonomy, MiMo source audit).

---

## 1. Decision items (answer in one line: "1 yes, 2 yes, 3 yes, 4 yes, 5 yes, 6 yes")

1. **Adopt the front-end topology** (winnow as interface between conversation
   and code harnesses), superseding v0.1's integrated-agent architecture.
   *Recommend: yes.*
2. **First step is a zero-build validation run** — one real design
   conversation → existing winnow tooling → hand-rendered work order → real
   backend → hand-scored constraint adherence — before any new code.
   *Recommend: yes.*
3. **The human dispatch gate is normative.** No auto-dispatch, ever.
   Pre-flight = open questions + proposed decisions + actions lacking
   acceptance criteria. *Recommend: confirm.*
4. **Scope guardrail: the front-end never grows execution tools** (no bash,
   no writes beyond its own state files). Without this, it becomes a
   mediocre harness in six months. *Recommend: confirm.*
5. **Reconciliation v1 is manual** — results reported back in conversation
   and extracted as deltas; automation deferred until manual proves
   annoying. *Recommend: confirm.*
6. **Handoff artifacts are emitted in cbtdag format** (dag.json +
   work-order.md) when the slice contains ≥2 actions joined by a `depends`
   edge; plain work order otherwise (granularity floor). *Recommend: yes.*

## 2. Thesis

Winnow's competence is taking conversation and producing code-like structure
— a typed, queryable, provenance-carrying graph. That makes it an *interface
layer* between humans and machines, not a component inside one machine. The
bet: **a graph-rendered, human-reviewed work order dispatched to an
unmodified code harness beats raw-transcript or summary dispatch on
constraint adherence and cross-session continuity** — and the graph
compounds intent and rationale across dispatch cycles, which no surveyed
harness does.

Antecedents: winnow spec §12's USG bridge note ("conversational front end,
computational back end"); arc-split (three arcs, independent extractions,
merged) as the pipeline in prototype.

## 3. Architecture — three layers, three concerns

```
conversation ──► WINNOW FRONT-END        fidelity of intent
                    │  distillation: typed semantic graph (.wno)
                    ▼
                 CBDAG TRANSLATION        verifiability of work
                    │  graph slice → dag.json + work-order.md
                    │  (frozen contracts, fixtures, acceptance)
                    ▼
                 CODE HARNESS BACKEND     competence of execution
                    │  Claude Code / Codex / MiMo / next month's best
                    ▼
              results ──► back as new deltas (loop closes)
```

- **Front-end (winnow session companion).** Long design/planning
  conversations distilled as they happen — tiers, resolution ladder, honest
  miss all earn their keep *within* the session (a four-hour design
  conversation is itself a long-horizon memory problem). Output: a
  version-controlled `.wno` graph per project.
- **cbtdag translation layer.** Renders graph slices into cbtdag's native
  form: `dag.json` (conventions, frozen contracts with fixtures, tasks with
  readiness) + `work-order.md` (permissions, acceptance criteria, honest-
  report mandate). Backend adapters are thin format shims.
- **Backend (unmodified code harness).** Swappable; the contract is the
  artifact, not the harness. Keeps its own context strategy — that is what
  it is good at, and tool-output-dense turns never enter winnow's pipeline.
- **The loop closes:** execution results return as deltas (action `done`,
  constraint violated, claim corrected by reality). The graph becomes
  persistent *project* memory: conversation shapes it, execution updates it,
  the next conversation opens from its digest.

State model (normative, unchanged from v0.1):

- **L0 raw archive** — append-only JSONL per session; redaction of
  credential-shaped strings on intake (lossy by design); the only complete
  record.
- **L1 winnow log** — semantic truth; `fold(empty, log)`; any prefix valid;
  write-after-batch atomic rename; a delta failing `validate()` is
  quarantined, never appended.
- **L2 derived** — digest/views, ephemeral; `.reach` sidecar is telemetry,
  not memory.

## 4. The handoff contract (normative mappings)

Graph → DAG is a homomorphism with one single-sourced, versioned mapping
table. Anything readable two ways is stated here, once:

| winnow graph | cbtdag artifact |
|---|---|
| `decision :status frozen` | `dag.json metadata.conventions[]` entry |
| `decision :status proposed` | **dispatch blocker** (pre-flight item) |
| `constraint :strength hard :status live` | acceptance-criteria seed in work order |
| `question :status open` | **dispatch blocker** (honest misses answered first) |
| `action :status todo`, deps met | task, `readiness: parallel_ready` |
| `action :status blocked` | task, `requires_done` on the blocker |
| `action :status doing` | in-flight task (never re-dispatched) |
| `depends` edges | task `requires` / `provides` topology |
| node `:src` | provenance field on the generated task |
| content-hash tip of the slice | `graph_commit` stamped into dag.json |

- **Drift detection:** a dag.json whose `graph_commit` ≠ the current slice
  hash is stale — mechanically detectable, semantically meaningful (unlike a
  git SHA). Dispatch refuses stale DAGs.
- **Fixture gap:** graphs capture intent, not verification. cbtdag's
  happy-path + error fixture requirement is satisfied at the dispatch gate:
  the human reviewer confirms or authors fixtures per boundary contract.
  The pre-flight checklist's third query (`action` nodes without acceptance
  criteria) exists precisely to surface this.
- **Granularity floor (item 6):** cbtdag form only when ≥2 actions with a
  `depends` edge; otherwise a plain work order. Single-task dispatches never
  pay DAG overhead.
- **Vocabulary discipline:** the status mapping table above is the only
  place either system's lifecycle vocabulary is defined relative to the
  other. Version it with the table's own changelog section; never let
  `blocked` drift to two meanings.

## 5. The dispatch gate (normative)

Pre-flight, always human, three queries against the folded graph:

1. `frame=question status=open` — honest misses and unresolved threads
2. `frame=decision status=proposed` — things never actually frozen
3. `frame=action` lacking acceptance criteria — unverifiable work

Dispatch is a human act emitting the artifact; results are reported back
(reconciliation, §6). **No auto-dispatch. No auto-merge. No execution tools
in the front-end.** (Items 3 and 4.)

## 6. Reconciliation (closing the loop)

- **v1 (manual):** backend outcomes reported to the front-end in ordinary
  conversation; the extraction pipeline turns them into deltas — action
  status flips, constraint violations as `contradicts` edges, reality-
  corrections with `:by backend-report`.
- **Deferred (v2):** result-intake pass drafting deltas from structured
  backend reports. Built only when manual reconciliation is *measured*
  annoying (telemetry: reconciliation events per week, lag between execution
  and graph update).

## 7. Evaluation & measurement

- **WO-0 recall corpus — permanent canary, not a phase gate that dies.**
  Transcripts with planted commitments/corrections/constraints + gold
  node/edge manifests; recall/precision scorer. Re-run on every model swap,
  prompt tweak, upstream pin bump. Extraction quality changes silently;
  the corpus is the only thing that notices. (Seed: arc-split fixtures;
  the known arc-split finding — batch cadence dropped four design
  commitments — is the failure class to build around.)
- **Zero-build validation run (decision item 2):** one real design
  conversation → existing tooling → hand-rendered work order → real backend
  → hand-scored constraint adherence. Tests the thesis at near-zero cost
  before any new code.
- **Intent-fidelity A/B (the head experiment):** same backend, same task,
  dispatched via graph-handoff vs. raw transcript vs. summary; measured on
  constraint adherence in the output. Same-model control, per the harness
  research's own methodology standard — the skepticism that was applied to
  MiMo's self-run numbers applies inward.
- **Telemetry (dogfood):** handoff sizes, pre-flight findings per dispatch,
  reconciliation lag, digest growth, ladder rung distribution, honest-miss
  rate. Feeds upstream §10.4 profile learning eventually.

## 8. Engineering specifics surviving from v0.1

- **Conventions:** env prefix `WNOH_`; session ids `wnoh-YYYYMMDD-<slug>-<4hex>`;
  keys referenced by indirection (`WNOH_API_KEY_ENV` names the env var);
  UTC ISO-8601; `:src` per-session integer turns; cadence one delta per
  exchange.
- **Trust boundaries:** LLM output is untrusted input to L1 (procedural
  stage-B + quarantine are the gates); `.wno` logs are data, never executed;
  config is trusted input; write access to the session directory is control
  authority (lockfile with holder pid).
- **Failure matrix (front-end form):** extractor down → exchange proceeds,
  gap comment, telemetry, gap grep-able; reject flood (>50% of ops) →
  bounce-back repair once, then quarantine + alert; `validate()` failure →
  quarantine, L1 never holds invalid state; crash mid-batch → last complete
  batch stands, resume via `--seed`; redaction false positive → accepted,
  counted, tuned in dogfood; concurrent processes → lockfile `SessionLocked`
  carrying pid; stale `graph_commit` at dispatch → refuse.
- **Upstream sharp edges that constrain this design** (winnow @ 1cdbf24,
  fixes land upstream, never patched locally): the `merge` op leaves
  dangling payload refs invisible to `validate()` — hand-check after manual
  merges; `split.py` always cuts `about`→term-id edges — handoff slices lose
  topic links, so the renderer must re-attach term context explicitly;
  tokenizer has no string escapes — no `"` in glosses; hot tier unbounded
  in unresolved commitments — digest budgets apply within long front-end
  sessions.

## 9. Repo topology (decided)

- **New repo** (working name `Swordsman/winnow-front`; rename freely) —
  the front-end is its own project. Winnow has utility beyond this layer,
  but its full potential is realized when *foundational*: zero front-end-
  coupled features land upstream.
- **Consumption: git submodule pinned to a commit** (initial `1cdbf24`),
  imported in-process; no copy-fork. Bump procedure: update pin → run
  upstream 129-test suite → re-review sharp-edges list → commit.
- The winnow skill tracks upstream independently; skill pin and repo pin may
  diverge deliberately (latest-reviewed vs. last-integration-tested).
- cbtdag artifacts/conventions are referenced from the winnow repo; if
  cbtdag graduates to its own repo, the translation layer consumes it the
  same way (pinned, no fork).

## 10. Honest risk assessment

**Would it work?** Mechanically, yes — no scary engineering anywhere; the
hard pieces (fold, ladder, merge, split, cbtdag formats) exist and are
tested. The real question is whether the graph handoff *wins*, and that is
now a cheap experiment instead of an expensive one.

Calibrated expectations (provenance: derived from the repo evidence, the
harness survey base rates, and the arc-split findings — not measured yet):

- **~70%** the graph handoff beats raw-transcript and summary dispatch on
  constraint adherence for multi-session, decision-dense projects. The 45%
  scenario from the integrated design (winnow vs. BM25 on code turns) is
  dissolved by the topology, not answered.
- **~85%** the build produces a keeper regardless: queryable provenance
  over your own design history is more observability than any surveyed
  harness offers.

Sticking points, ranked by expected pain:

1. **Ritual overhead.** Every dispatch is render → review → handoff →
   report-back. The gate is the point, but friction is the cost; if the
   ritual is heavier than the value, usage decays silently. Telemetry on
   dispatch frequency is the early-warning signal.
2. **Reconciliation compliance.** The closing of the loop depends on
   humans (or the operator agent) reporting results back. If it doesn't
   happen, the graph drifts from reality while looking authoritative —
   worse than no graph. Mitigation: reconciliation lag in telemetry;
   stale-action `--stale` review in the pre-flight.
3. **Registry drift over long projects.** The term registry grows
   monotonically; alias maintenance is human work; cross-session merges
   inherit the §12 caveat (canonical-form invariance holds *given a shared
   registry*).
4. **Silent recognition failure (unchanged, inherited).** Rung 5's honest
   miss only fires when the extractor *notices* a reference it can't place;
   confident wrong-referent answers are invisible by construction. No
   mechanical fix exists; mitigations are low-`:conf` discipline and
   telemetry review. Named because it looks like success when it fails.
5. **Backend drift.** Backends reshuffle prompt conventions weekly; the
   handoff contract must tolerate it (adapters are the shock absorber).

## 11. Decomposition & roadmap

Additive, independently shippable chunks; a mid-build failure leaves a
coherent system. Every boundary frozen with happy + error fixtures before
its wave dispatches.

| WO | Chunk | Depends on |
|---|---|---|
| WO-0 | **Zero-build validation run** (manual pipeline, real conversation, real backend, hand-scored) — decision item 2 | — |
| WO-1 | **Recall corpus + scorer** (permanent canary, §7) | — |
| WO-2 | `fold.py --handoff` view: slice → work-order.md + dag.json emission, mapping table (§4) single-sourced | WO-0 (thesis validated) |
| WO-3 | Dispatch-gate tooling: packaged pre-flight queries + `graph_commit` staleness check | WO-2 |
| WO-4 | Backend adapters (thin format shims; Claude Code + Codex first) | WO-2 |
| WO-5 | Dogfood + telemetry harness (§7 metrics, live project use) | WO-3, WO-4 |
| WO-6 | Reconciliation intake assistance (draft deltas from result reports) — only if WO-5 telemetry says manual hurts | WO-5 |
| WO-7 | Intent-fidelity A/B, formal (§7) | WO-5 data |
| WO-8 | Docs reconciliation (terminal): operator guide, mapping-table changelog policy | WO-7 |

Waves: **W0** = WO-0 ∥ WO-1 (gate: thesis validated at near-zero cost; an
ugly answer re-plans before any renderer code). **W1** = WO-2. **W2** =
WO-3 ∥ WO-4. **W3** = WO-5 (integration + dogfood, first-class).
**W4** = WO-6 (conditional), WO-7, WO-8.

## 12. Load-bearing unknowns

- **U1 — Extraction recall on real planning conversations.** Confidence:
  medium-high (demo + arc-split evidence stands). Contingency: registry
  seed-work, cadence tightening; last resort, winnow as query layer over
  raw archive. **Resolved by WO-1.**
- **U2 — Work-order sufficiency.** Does a graph-rendered work order carry
  enough for faithful backend execution? Confidence: medium — this is the
  new risk concentration. Contingency: thicker handoffs (more slice hops,
  transcript appendix); the renderer's hop count is the tuning knob.
  **Resolved by WO-0 (zero-build run) before WO-2 exists.**
- **U3 — Reconciliation compliance.** Behavioral unknown (§10.2).
  Contingency: WO-6 intake assistance. **Resolved by WO-5 telemetry.**

## 13. Exclusions (deliberate, each with reason)

| Exclusion | Reason |
|---|---|
| Execution tools in the front-end | Decision item 4 — separation of concerns is the design |
| Auto-dispatch / auto-merge | Decision item 3 — the gate is the point |
| Integrated agent loop (v0.1 architecture) | Superseded; seamlessness partially relocatable later via watch-mode + headless backend pipes |
| Multi-agent orchestration beyond cbtdag's own dispatch | Worktree-isolation + gate evidence; cbtdag owns DAG execution |
| Global KB (winnow §10.5 rung 4) | Upstream hash-id era |
| Profile learning update rule | Needs this system's telemetry first |
| Automated reconciliation (v1) | Decision item 5 — measured annoyance precedes automation |
| FTS5 index for rung 3 | Trigger-based: cross-session node count > ~5k |
| TUI/GUI beyond plain CLI | Surface is not the differentiator |
| UEL/embedding term-identity mode | Upstream v2; registry-v0.1 only |

---

*Supersedes on acceptance: `winnow-harness-design-spec.md` (v0.1),
`winnow-frontend-proposal.md`. Preserved regardless of answer: WO-1 canary,
three-layer truth ranking, redaction, quarantine, skill sync — load-bearing
under both architectures.*
