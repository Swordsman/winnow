# claim: claude-code-backend
- claimed: 2026-10-13T05:24Z (written after the work began at ~05:15Z; the claim step was missed at the start)
- session: Claude Code cloud session session_013ezpsWi4jSfkyQzeS687YL, at Joe's request ("using a subagent instead of deepseek would be fine as an option as well")
- based-on: 6809ed7
- expected-duration: ~45min
- ttl: consider this claim dead after 6h

## before
- winnow.py's backends: anthropic (SDK), deepseek (`ds`), deepseek-anthropic.
  None runs Claude without an API key, and nothing checks a delta before
  the procedural normalizer commits it.
- `--model` defaults to a Claude model id on every backend, so
  deepseek-anthropic without `--model` sends a Claude id to DeepSeek.
- `--global-kb` reads an undefined `verbose` in main() and dies.
- 181 tests pass.

## intent
Joe's model policy (2026-10-13): "make sure that haiku isn't used unless
sonnet or better double check haiku's output. sonnet can be used solo or
with opus as a quality checker, opus can be used solo".
- `--backend claude-code`: a tool-less `claude -p` subagent on the local
  login, isolated from hooks, plugins, MCP, skills and CLAUDE.md, at
  `--effort` from `--think` (max by default), prompt on stdin.
- `--checker MODEL`: a second model on the same backend checks each delta
  (digest, registry, pull results, new turns, candidate) before the
  procedural pass.
- `claude_policy_error` enforces the pairing on both Claude backends:
  haiku+sonnet, haiku+opus, sonnet, sonnet+opus, opus. Anything else, and
  any model that isn't haiku/sonnet/opus, is refused.
- Per-backend `--model` defaults; the `verbose` fix.
- Tests, spec §9 + Files, README, CLAUDE.md, TODO. Littlewing (plugin)
  gets a `checker` option on its wno mode.

## warnings
- Overlaps claims/failures-assumptions-types.md (same session): that work
  will change the extractor and normalizer prompts. CHECKER_SYSTEM lists
  the seven node frames and eight edges literally; if the failure frame
  lands, CHECKER_SYSTEM needs the new frame too.
- Pairings Joe didn't name (sonnet+sonnet, opus+any checker) are refused
  rather than guessed at; Fable models are refused too. Joe may widen it.
- A live littlewing recording is running in the background on deepseek;
  don't break the deepseek path.
