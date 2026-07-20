# Extraction quality: flash-baseline vs pro-re2 (first pass, 2026-07-20)

Both runs extract `transcripts/gemini-winnow-proto.txt` (24 turns, 12
batches). **Caveat: not a controlled model comparison** — the flash
baseline predates the prompt fixes, so model and prompt version are
conflated. A post-fix flash rerun would isolate the model variable.
`demo-deltas.wno` is a *different* corpus (spec §11 conversation), so it
anchors style/density expectations only, not a head-to-head.

## Headline numbers

|                | flash-baseline | flash-postfix | pro-re2 | demo (hand, other corpus) |
|----------------|---------------|---------------|---------|---------------------------|
| nodes          | 37            | 37            | 48      | 37                        |
| edges          | 15            | 21            | 39      | 25                        |
| terms          | 102           | 26            | 59      | 7                         |
| edge types used| 3 of 8        | 7 of 8        | 8 of 8  | 7 of 8                    |
| edges/node     | 0.41          | 0.57          | 0.81    | 0.68                      |
| terms/node     | 2.76          | 0.70          | 1.23    | 0.19                      |

## Findings

1. **Edge-type collapse (flash).** 13 of flash's 15 edges are
   `supports`; pro-re2 uses the full eight-type palette with a
   distribution close to the hand-authored profile (about/refines/
   supersedes-heavy). Edge typing looks like the clearest
   model-capability separator in this pair.
2. **Term explosion (flash).** 102 terms for 37 nodes, many generic
   junk ("decision", "architecture", "benefit", "component") and many
   with empty glosses. Pro-re2's 59 is still ~8x the hand-authored
   density but the terms are specific (R1..R5 rule names,
   choice-B-injection-decision). Registry discipline is the biggest
   gap between both live runs and hand-authored.
3. **`--concepts` doubles as a registry QA tool.** Flash's top concept
   by mass is the junk term "decision" (mass 4) — mass ranking surfaces
   registry pollution instantly. Worth adding to a maintenance pass
   alongside `--stale`.
4. **Revision tracking (pro only).** Pro-re2 produced 6 supersedes
   edges / 3 superseded claims and resolved or answered 4 questions;
   flash answered 1 and superseded nothing. Pro is tracking the
   conversation's self-corrections; flash mostly appended.
5. **Gloss quality (pro).** Pro glosses are frequently just the
   de-kebabed id ("choice B injection decision") — low information.
   Possible normalizer prompt nudge: require glosses to add content
   beyond the id or omit the term.
6. **Rejects (pro): 4, all one shape** — edges targeting registry terms
   instead of nodes (e.g. `(about q5 archival-compression)`). The
   extractor keeps wanting topic-edges into the registry. Options:
   prompt nudge ("edge endpoints must be node ids"), or a spec question:
   should `about` legally target a term? (Terms as topics is arguably
   the natural reading of `about`.)

## Post-fix flash rerun: analysis (2026-07-20)

`runs/gemini-proto-flash-postfix-re2.wno` + log. Same corpus, same
prompts as pro-re2 — the model variable is isolated now. Headline:
**most of the baseline's pathology was the prompt version, not the
model.**

7. **Term explosion was a prompt artifact.** 102 → 26 terms (now below
   pro's 59); terms/node 2.76 → 0.70. Junk changed shape rather than
   vanishing: the generic-word terms ("decision", "architecture") are
   gone; clause-terms appeared instead
   (`look-ahead-dependency-check-failed-to-apply-to-turn-1`,
   `and-contract-questions`; several ids 50–68 chars), and 12/26
   glosses are empty. `--concepts` top-of-mass is clean now
   (compressed-format 5, background-ai 4, dual-payload-json 2) where
   baseline's top was junk — mass ranking keeps working as registry QA.
8. **Edge-type collapse was mostly a prompt artifact.** 3 → 7 of 8
   types (missing: `depends`); supports share 13/15 → 3/21; refines=8
   leads. The distribution is within sight of the hand-authored
   profile. The remaining model gap vs pro is yield and density: 37 vs
   48 nodes, 0.57 vs 0.81 edges/node.
9. **Frame diversity is the new flash failure.** Only question+claim
   frames survived. Flash *attempted* constraint and def frames but
   emitted them malformed — all correctly rejected (`node missing
   payload (def d1)` / `(constraint c7)` / `(constraint c8)`);
   baseline at least landed singleton constraint/decision/action
   frames. The normalizer is doing its job: grammar breakage now costs
   flash whole frames instead of polluting the graph.
10. **Reject shapes confirmed with prompts controlled.** Flash's 5
    rejects are all grammar (2 invented frame `answer`, 3 malformed
    payloads); pro's 4 were all reference discipline (term-targeted
    edges). Different failure modes, same normalizer.
11. **Revision tracking:** flash now attempts supersession (1
    supersedes edge, 2 superseded claims; baseline had none) but pro
    still leads (6 edges / 3 superseded claims).
12. **New finding — off-spec status values pass through unvalidated.**
    flash-postfix has a question at `partially-answered`, pro-re2 a
    question at `resolved`, flash-baseline a claim at `open`; §2
    vocabularies allow none of these. fold.py validates edge types
    (ETYPES) but not statuses, and status drives Resolver rank class
    and mass gating, so an off-spec value silently lands in the wrong
    rank class. Candidate small fix: per-frame status table in fold.py
    validation + one normalizer prompt line.
13. **Status discipline generally:** flash-postfix emits 5 `answers`
    edges yet leaves 10/11 questions open — answers edges land without
    the question status flip. Pro shows the same gap more softly (9
    answers edges, 4 questions non-open). Candidate ruling: should an
    `answers` edge auto-flip its target question (mirroring the
    `supersede` op's status side effect)? Spec question, not a bug.

**Verdict:** with prompts fixed, flash is usable for
recognition-shaped extraction (clean high-mass registry head, sane
edge palette) but under-yields nodes/edges and can't hold frame
grammar or status discipline; pro remains the extraction model. This
supports the live-relay plan's posture (c29: keep the lightweight
model's role recognition-only).

## Next steps (remainder, per waiting-convention)

- [x] Post-fix flash rerun (`--model flash`, same prompts) to isolate
      model from prompt version — done, findings 7–13 above.
- [ ] Decide the `about`-targets-a-term question (spec ruling or prompt
      nudge) before the next live run; it's 100% of pro rejects.
- [ ] Gloss-quality nudge in the normalizer prompt (finding 5).
- [ ] Status-vocabulary validation (finding 12): per-frame status table
      in fold.py + normalizer prompt line. Small, code-level.
- [ ] Per-delta yield curve (fold --upto N over both logs) if deeper
      granularity is wanted; not yet done.
