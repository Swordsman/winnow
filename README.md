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
```

Tests: `python3 -m unittest discover tests`

`demo-deltas.wno` is a real extraction of an 8-turn filesystem-design conversation, walked through in spec §11: a design superseded mid-stream, hard requirements delivered inside doomsday jokes, a convention stated two contradictory ways, and a wrong user premise entering the graph faithfully and getting corrected structurally.

## Repository

| Path | What |
|---|---|
| `winnow-spec-v0.2.md` | the specification |
| `fold.py` | reference implementation (parse, fold, validate, snapshot, frontier, digest, query, hashes) |
| `winnow.py` | streaming extraction orchestrator (spec §9 loop; live via the Anthropic SDK, or deterministic `--replay` mode) |
| `demo-deltas.wno` | runnable demo log (spec §11) |
| `tests/` | unit tests for the fold and the orchestrator (`python3 -m unittest discover tests`) |
| `docs/hash-ids.md` | content-hash id design note (v0.3) + rationale for the `--hashes` prototype |
| `sessions/` | winnow self-extractions of winnow's own design sessions — the protocol taking notes on its own development, kept as provenance for v0.2 design decisions |
| `TODO.md` | open items and deferred questions |

## Status

v0.2 — spec, reference fold, and a working orchestrator loop (validated in replay mode; live-run evaluation pending). Reach handling, promotion TTLs, and profile learning are orchestrator future work; cross-session merge is designed (`docs/hash-ids.md`) with hash ids prototyped in `fold.py`; the global knowledge base stays deferred (spec §12).
