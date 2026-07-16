# winnow

**Streaming semantic distillation for AI conversations.**

An s-expression delta protocol over a typed semantic graph. Extraction happens *while* the conversation happens; the knowledge graph is a fold over the delta log. Named for what it does: separate grain from chaff — signal becomes nodes, noise never gets extracted.

## The idea in four lines

```
turns ──► extractor (loose) ──► normalizer (strict) ──► delta ──► log
                ▲                                                 │
                └────────── context window ◄────── fold ◄────────┘
```

The extractor never sees the whole transcript or the whole graph — only a bounded digest plus the newest turns. Batch extraction degrades as input grows; winnow's per-step input is constant-ish, no matter how long the conversation runs.

## Spec

[`winnow-spec-v0.2.md`](winnow-spec-v0.2.md) — the full specification. Highlights:

- **8 frames** (claim, def, question, decision, constraint, action, artifact, edge) and **8 edge types**. Closed sets.
- **Normalization rules R1–R12**: one meaning → one form, enforced. Two extractions of the same text fold to isomorphic graphs.
- **Delta protocol**: `add` / `update` / `supersede` / `merge` / `del` / `term` — the graph is `fold(empty, log)`; any prefix of the log is a valid earlier state.
- **Tiers (§10, new in v0.2)**: no traditional context window. An *immediate context window* is JIT-compiled per message boundary from four temperature tiers (fire/hot/warm/cold), governed by a declared cooling profile, backed by a resolution ladder that terminates in an honest miss instead of a fabricated referent.
- **Meta header (new in v0.2)**: `.wno` files declare their version, term-representation mode, and cooling profile. Headerless v0.1 files remain valid and default cleanly.

## Quickstart

Zero dependencies, one file:

```sh
python3 fold.py demo-deltas.wno              # stats + validation
python3 fold.py demo-deltas.wno --snapshot   # canonical folded graph
python3 fold.py demo-deltas.wno --frontier   # v0.1 frontier digest
python3 fold.py demo-deltas.wno --digest     # v0.2 tiered window
python3 fold.py demo-deltas.wno --upto 4 --frontier   # any prefix is a valid state
python3 fold.py demo-deltas.wno --query "frame=constraint strength=hard"
python3 fold.py demo-deltas.wno --hashes     # content-hash id table (v0.3 prototype)
```

Run the extraction loop itself over a turn-tagged transcript (`[t1 user]` /
`[t2 assistant]` headers) with `winnow.py` — extractor and normalizer prompts
from spec §9, procedural stage-B enforcement, one `.wno` log out:

```sh
python3 winnow.py transcript.txt --out log.wno          # live (needs anthropic + API key)
python3 winnow.py transcript.txt --out log.wno --replay fixtures.txt   # offline/deterministic
python3 winnow.py transcript.txt --out log.wno --seed prior.wno        # continue a session
```

When the extractor can't place a reference it emits `(reach QUERY)`; the orchestrator walks the §10.5 resolution ladder (resident hit → warm widening → cold scan → honest miss), promotes what it finds into the fire tier with a TTL, re-passes the extractor with the pull results, and turns unresolvable references into open questions addressed to the human — never a fabricated referent.

Merge logs from different sessions on content-hash join keys (`docs/hash-ids.md`) — identical propositions collapse with unioned provenance, status conflicts surface as open questions:

```sh
python3 merge.py a.wno b.wno --out merged.wno
```

Split is the procedural inverse-ish: slice a valid sub-log out of a folded log — topic handoffs, live/dormant archival partition, KB ingestion filtering. Seeds come from a query or explicit ids; expansion walks edges *and* payload node-refs; payload references are always closure-pulled (validity); live hard constraints ride along (§10.6); cut edges become comments; parent ids are preserved:

```sh
python3 split.py log.wno --seed d3 --component --out cluster.wno --rest remainder.wno
python3 split.py log.wno --query "status=superseded" --hops 0 --out dormant.wno
```

Tests: `python3 -m unittest discover tests`

`demo-deltas.wno` is a real extraction of an 8-turn filesystem-design conversation, walked through in spec §11: a design superseded mid-stream, hard requirements delivered inside doomsday jokes, a convention stated two contradictory ways, and a wrong user premise entering the graph faithfully and getting corrected structurally.

## Repository

| Path | What |
|---|---|
| `winnow-spec-v0.2.md` | the specification |
| `fold.py` | reference implementation (parse, fold, validate, snapshot, frontier, digest, query, hashes) |
| `winnow.py` | streaming extraction orchestrator (spec §9 loop + §10.5 resolution ladder; live via the Anthropic SDK, or deterministic `--replay` mode) |
| `merge.py` | cross-log merge on content-hash join keys (v0.3 feature, shipped early) |
| `split.py` | procedural log slicing — topic slices, archival partition, component extraction |
| `demo-deltas.wno` | runnable demo log (spec §11) |
| `tests/` | unit tests for the fold, orchestrator, ladder, and merge (`python3 -m unittest discover tests`) |
| `docs/hash-ids.md` | content-hash id design note + the merge design `merge.py` implements |
| `sessions/` | winnow self-extractions of winnow's own design sessions — the protocol taking notes on its own development, kept as provenance for v0.2 design decisions |
| `TODO.md` | open items and deferred questions |

## Status

v0.2 complete, plus the two headline v0.3 features shipped early: cross-log merge (`merge.py`) and the resolution ladder with reach handling and P3 promotion TTLs (`winnow.py` + `fold.py`). Validated offline/replay; live-run evaluation pending an API credential or the DeepSeek harness. Still deferred: profile learning (§10.4 — wants live reach telemetry first), global KB construction (§12, rung 4 interface reserved), session-namespaced provenance for merged logs (`TODO.md`).
