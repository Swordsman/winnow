# Changelog

Version log, newest first. Each user-visible change gets a line in the
same commit (see CLAUDE.md's Commits convention). Keep entries in plain
language so a problem can be traced to the change that caused it.

## 2026-11-01

- Failure records: something that went wrong is a claim
  `(fails THING KIND)`. Why it happened is a diagnosis claim
  `(causes CAUSE FAILURE)`. A fix links with `answers` and a guard put in
  place so it can't happen again links with `motivates`. A trouble view
  lists the failure signals the graph already holds.
- Assumptions: a supposition is a claim with `:status assumed`; a
  conditional used as a reason is a claim `(implies A C)`; basis
  discharges the consequent's dependence on the antecedent.
- Typed relations: relation terms can carry `:sig` slots; the normalizer
  checks argument count and order and swaps a reversed binary
  proposition.
- Model policy simplified: on the Claude backends a haiku extractor
  needs a `--checker` that isn't haiku; everything else is allowed;
  unknown model families are still refused.

## 2026-10-13

- Reach queries drop `:key value` annotations before resolution, so
  `(reach the-export :by user :src t1)` stops searching for the tags
  themselves.
- Prompts reach ds as files: winnow's DeepSeek client sends the system
  prompt and task through `--system-file` and `--task-file` instead of
  argv, and closes stdin.
- Claude subagent backend and checker: `--backend claude-code` runs a
  tool-less `claude -p` subagent from an empty scratch directory;
  `--checker MODEL` reviews each delta before the procedural normalizer;
  default models are per-backend.
- Max thinking effort by default: `--think` defaults to `max` on every
  backend, and the SDK backends stream with each model's full output
  capacity as `max_tokens`.
- basis view: `wno.py basis` labels each node held / pending /
  undermined, with the chain to causes and `--rests-on ID` for a
  premise's blast radius; no scores.
- ds on DeepSeek-V4.1-Flash: `-m flash` uses `deepseek-flash`, `--think
  low` was added, and cost estimates use current prices.
- fold / frontier / digest split: one script per job behind `wno.py`;
  fold means log-to-graph only, frontier means open items, digest means
  tiers plus the window the extractor sees; the spec gained a glossary
  and matching section rewrites.