# claim: plugin-copy
- claimed: 2026-10-13T02:19Z
- session: cloud session on branch ccr-05e66749-jwb4ko (tree-code review session, PR #14)
- based-on: c05de32
- expected-duration: ~60min
- ttl: consider this claim dead after 4h

## before
- Swordsman/sync_swords_plugin main a52ece8, plugin v0.6.0: winnow is
  only `skills/winnow/SKILL.md` (distilled from the spec). No winnow
  code, spec copy or tests. Its CLAUDE.md sources row reads
  "winnow-spec-v0.2.md (distilled into SKILL.md)".
- winnow c05de32: `.wno` records live in the Session Records doc;
  `python3 -m unittest discover -s tests` passes 144 tests.
- Session Records index row for wno-20261012-tree-code-goal-7c1e
  points at an older snapshot (asset 39b39a96ff7d9a04738ac07bb6fae475).
  The local handoff has deltas through :turn 43.
- Cloud Session Anchor, Repos > winnow tab: Repo facts and the handoff
  log still link GitHub `sessions/*.wno` URLs, which stop resolving once
  PR #14 merges.

## intent
Joe's call (t44): copy code, spec and tests into the plugin now; winnow
stays the source, and will probably move into the plugin later.
1. Plugin branch ccr-05e66749-jwb4ko:
   - `scripts/winnow/`: fold.py, winnow.py, merge.py, split.py,
     mega-fold.py, term-table.py, `ds` (winnow.py calls it from its own
     dir), canon-map.json, junk-terms.json, demo-deltas.wno (test_fold
     reads it), and `tests/`.
   - `skills/winnow/references/`: winnow-spec-v0.2.md, hash-ids.md,
     ds-guide.md.
   - Update the SKILL.md file list to `${CLAUDE_PLUGIN_ROOT}` paths.
     Update the CLAUDE.md and README sources and layout rows. Bump
     plugin.json to 0.7.0.
   - Open a PR. Joe merges, as with plugin PRs #1-#3.
2. winnow TODO.md: a done item for the plugin copy, linking the PR.
3. Handoff: a delta for t44/t45 (move answered, plugin decision, plugin
   PR). Upload the new version as `.wno.txt` and repoint the index row
   (Record + Asset id cells).
4. Anchor: point the winnow tab's Repo facts and handoff log at Session
   Records. Update the pipeline brief (Verified so far, Open questions).
5. PR #14 body: add the move commit c05de32 and this work.

## warnings
- Never commit `.wno` records: `sessions/*.wno` and `runs/**/*.wno` are
  gitignored, and the local copies are working copies.
- Uploads refuse `.wno`, so upload as `<name>.wno.txt`.
- The plugin repo uses neutral wording on purpose. Its README and
  CLAUDE.md were rewritten to drop classifier trigger terms
  ("self-syncing", "semantic distillation" and others). Keep new text
  neutral.
- The plugin has no root .gitignore. Run its tests with `python3 -B`
  so no `__pycache__` gets committed.
- The plugin has no CI. Its CLAUDE.md says not to watch its PRs.
