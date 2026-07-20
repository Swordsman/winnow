# claim: arc-split-corpus
- claimed: 2026-07-20T08:45Z
- session: Claude (fable 5), remote container, branch claude/fable-wno-files-review-3y82sh
- based-on: 51f1c65
- expected-duration: ~60min (two parallel subagent workers + executor
  extraction/merge phases)
- ttl: consider this claim dead after 3h

## before
- TODO "Multi-session corpus (arc-split)" open; no corpus exists.
- transcripts/ has only gemini-winnow-proto.txt (24 turns);
  runs/gemini-proto-pro-re2.wno is its best extraction (48n/39e).
- winnow.py takes :src turn numbers from [tN] headers, so a naive
  slice would NOT produce colliding :src values.
- No cbtdag/ directory; first cbtdag-structured task in this repo.

## intent
Execute cbtdag project `cbtdag/arc-split/` (design-spec.md is the
authority; dag.json + two work orders + frozen-contract fixtures are
committed alongside this claim):
- A (subagent): detect_arcs.py — turn-axis min-crossing cut on the
  pro-re2 graph → runs/arc-split/boundaries.json (K=2 → 3 parts,
  min part 5 turns).
- B (subagent, parallel against the frozen boundaries contract):
  cut_corpus.py — part1..3.txt renumbered from t1 + mapping README
  under transcripts/arc-split/.
- C (executor): three live pro --re2 extractions → runs/arc-split/
  partN-pro-re2.wno (DEEPSEEK_API_KEY persistent env var per Joe).
- D (executor): merge.py over the part logs; runs/arc-split/notes.md
  documents :src-collision evidence (q5), bounded q6 signal,
  content-hash join behavior.
Done = acceptance list in design-spec.md; TODO flipped; pushed.

## warnings
- Never commit DEEPSEEK_API_KEY or write it to any file.
- Merge/spec changes are OUT of scope (D7): the corpus produces
  evidence for Joe's :src-namespacing ruling, it must not preempt it.
- If cut off mid-flight: the design spec + dag.json + work orders are
  the full remainder; boundaries.json (if present) is contract-valid;
  any completed part logs fold standalone (incremental writes).
- Live-run cost rides on Joe's key (~24 pro --re2 turns total, same
  volume as the committed a9 run). If that inference spend was NOT
  meant to be autonomous, veto applies to C/D only — A/B artifacts
  stand alone.
