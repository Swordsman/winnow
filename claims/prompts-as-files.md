# claim: prompts-as-files
- claimed: 2026-10-13T05:30Z
- session: Claude Code cloud session session_013ezpsWi4jSfkyQzeS687YL, at Joe's request ("why would you pass in the RAW text via commandline ... shoving crap in as an argument is insane")
- based-on: 2a808a7
- expected-duration: ~60min
- ttl: consider this claim dead after 6h

## before
- winnow.py's deepseek client passes the system prompt and the whole user
  message (digest plus new turns) to `ds` as arguments. Linux refuses one
  argument over 128 KiB (checked: a 300 KB task dies with "Argument list
  too long"), and argv shows in `ps`. The child also inherits the
  caller's stdin, which `ds` reads whenever it isn't a terminal.
- `ds` reads a system prompt from a file (`--system-file`) but the user
  message only from argv, or wrapped in tags from `--context` / stdin.
- ds-guide.md's recommended winnow commands put both prompts in argv.
- The claude-code backend already uses a file and stdin.

## intent
- `ds --task-file FILE`: the user message from a file, verbatim (dry-run
  request identical to the argument form).
- winnow's deepseek client writes both prompts to a private temp dir,
  passes `--system-file` / `--task-file`, closes stdin. Test with a
  300 KB prompt.
- ds-guide: prompts go in files, never on the command line.
- A read-only sweep (workflow wq9669pkx) of winnow, the plugin and
  provider-api-library for every other place content goes into argv,
  code and docs; fix what it confirms, here and in the plugin.

## warnings
- The live littlewing recording in the background runs the plugin's copy
  of winnow; it loaded the old code before this change, so it keeps
  passing argv until it finishes. Don't restart it for this.
- provider-api-library/skills/deepseek-api/ is being edited by the design
  workflow's docs agent; don't edit it until that agent finishes.

## progress (2026-10-15)
- The sweep (workflow wq9669pkx) finished on 2026-10-13 apart from its
  final completeness critic, which the account's session limit stopped.
  Confirmed instances in winnow: ds's self-calls (`--help-me-out`,
  `_quick_inference`); fixed with `_call_self` and tests/test_ds.py.
- Confirmed elsewhere, not fixed here: term_capture broker.py and ai-coop
  (tmux send-keys), shellcrawl explore.py, taskdagger
  washing_machine.py, token-counter SKILL.md, term-capture
  PEER_MESH_ARCHITECTURE.md (all copies of upstream repos inside the
  plugin), and deepseek-api SKILL.md + scripts/deepseek.sh
  (provider-api-library, then the plugin copy).
- Open question for Joe: fix the upstream repos (then re-copy) or only
  the plugin copies, which the next sync would overwrite.
