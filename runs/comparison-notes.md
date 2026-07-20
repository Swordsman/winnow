# Extraction quality: flash-baseline vs pro-re2 (first pass, 2026-07-20)

Both runs extract `transcripts/gemini-winnow-proto.txt` (24 turns, 12
batches). **Caveat: not a controlled model comparison** — the flash
baseline predates the prompt fixes, so model and prompt version are
conflated. A post-fix flash rerun would isolate the model variable.
`demo-deltas.wno` is a *different* corpus (spec §11 conversation), so it
anchors style/density expectations only, not a head-to-head.

## Headline numbers

|                | flash-baseline | pro-re2 | demo (hand, other corpus) |
|----------------|---------------|---------|---------------------------|
| nodes          | 37            | 48      | 37                        |
| edges          | 15            | 39      | 25                        |
| terms          | 102           | 59      | 7                         |
| edge types used| 3 of 8        | 8 of 8  | 7 of 8                    |
| edges/node     | 0.41          | 0.81    | 0.68                      |
| terms/node     | 2.76          | 1.23    | 0.19                      |

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

## Post-fix flash rerun (launched 2026-07-20, same session)

`runs/gemini-proto-flash-postfix-re2.wno` + log. Early observation:
flash's rejects differ in kind from pro's — flash invents frame types
(`unknown frame answer`), pro mis-targets edges at registry terms. Same
normalizer, different failure modes: flash breaks grammar, pro breaks
reference discipline. Analysis of the finished run is the open item.

## Next steps (remainder, per waiting-convention)

- [ ] Post-fix flash rerun (`--model flash`, same prompts) to isolate
      model from prompt version. Offline analysis then repeats verbatim.
- [ ] Decide the `about`-targets-a-term question (spec ruling or prompt
      nudge) before the next live run; it's 100% of pro rejects.
- [ ] Gloss-quality nudge in the normalizer prompt (finding 5).
- [ ] Per-delta yield curve (fold --upto N over both logs) if deeper
      granularity is wanted; not yet done.
