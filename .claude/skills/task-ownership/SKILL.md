---
name: task-ownership
description: Claim/complete protocol for multi-session development. Use at session boot (check for active claims before touching anything), before starting any nontrivial task (write a claim declaration), and at task completion (write the completion declaration). Prevents parallel double-development and makes interrupted or botched sessions detectable and recoverable.
---

# Task ownership protocol

Sessions are ephemeral and parallel sessions are possible. This protocol
makes ownership explicit, so a fresh session can always tell: is anyone
working on this? did a previous attempt finish, die midway, or wrap up
badly? Each of those needs different handling, and guessing wrong wastes
work or corrupts state.

**The git remote is the only shared channel.** Sessions run in isolated
containers with fresh clones — another session's uncommitted files are
invisible to you, and local file mtimes tell you nothing about remote
activity. Every declaration in this protocol is only real once pushed.

## Claims live in `claims/`

One file per task, deterministic name: `claims/<task-slug>.md`. Two
sessions claiming the same task produce the same path — the second push
gets rejected, and the race is caught by git itself. That rejection is
the protocol working; if your claim push fails, fetch, read the claim
that beat you, and stand down.

## Claiming a task

Before nontrivial work, write the claim, commit it alone, push
immediately:

```markdown
# claim: <task-slug>
- claimed: 2026-07-16T09:10Z          <- datetime, UTC
- session: <who/what is doing the work>
- based-on: <git SHA of HEAD at claim time>
- expected-duration: ~90min           <- honest guess; liveness baseline
- ttl: consider this claim dead after 4h

## before
What the things you're about to touch look like right now. Brief but
concrete: files, node counts, test counts, behaviors. This is the
baseline an assessor will diff against.

## intent
What you're going to alter and roughly what the end state should look
like. Files you expect to touch, changes you expect to make, what
"done" means.

## warnings
Sharp edges for anyone who has to pick this up mid-flight: ordering
constraints, things that look broken but aren't, state that must not
be committed (keys, scratch files), irreversible steps.
```

Commit message: `claim: <task-slug>`. Push before starting the work.
If you can't push the claim, you don't own the task.

## Completing a task

Append to the same file, in the same commit as the final work and its
TODO.md flip:

```markdown
## completion
- completed: <datetime UTC>
- outcome: <final state relative to the intent — matched / deviated how>
- hiccups: <surprises, workarounds, anything a future session should know>
- checklist:
  - tests green: yes/no (which suite, count)
  - TODO.md flipped: yes/no
  - handoff updated: yes/no/not-needed
  - pushed: yes  <- by definition, if this is visible
```

The checklist is deliberately explicit. A completion section with
missing or wrong checklist entries is the scenario-3 detector: attention
depletion can't both skip the wrap-up and fill out the form correctly.

Completed claims stay in place; any later session may sweep completed
claims older than a week into `claims/done/` (or delete them — git
history keeps the record).

## At session boot: read the claims before touching anything

For every claim file without a `## completion` section, check
`- claimed:` against now, and `git fetch` to see remote activity since:

| Claim age | Posture |
|---|---|
| > 1 day | Claimant is dead. Handle as scenario 2 or 3 below. |
| hours | Almost certainly dead; verify no pushes since claim, then proceed as scenario 2/3. |
| < 1 hour | Take a closer look: fetch, check for recent pushes on the claim's branch. |
| < 20 min | Cautious: assume live unless evidence otherwise. Work elsewhere. |
| < 5 min | Hit the brakes. A session is likely mid-flight *right now*. Fetch every few minutes and watch for pushes; do not touch anything the claim's intent section names. |

(Local file mtimes are only meaningful for same-machine sessions —
don't trust their absence as evidence across containers.)

## Scenario handling

**Scenario 1 — active parallel session** (fresh claim, no completion):
don't touch anything named in the claim's intent. Work on something
else or wait. Never "help" an active claim without coordination
through the user.

**Scenario 2 — interrupted session** (stale claim, no completion, work
cuts off partway): assess before acting. `git diff <based-on>..HEAD`
shows exactly what the claimant changed; compare against the claim's
`before`/`intent` to locate the cutoff point. Read the `warnings`
section before touching anything. Then **alert the user with findings
and check for constraints you can't see** (instructions or context the
dead session had that you don't) before wrapping up on its behalf.

**Scenario 3 — botched wrap-up** (work spans the full intent, but the
completion section is missing, incomplete, or contradicts reality):
this is the dangerous one. The wrap-up failing is symptomatic —
attention depletion at the end means details are likely missed
*throughout*. Don't just finish the checklist: audit the whole span of
the work against the intent (run the tests yourself, verify the TODO
flips, fold/validate any generated artifacts, spot-check the diffs)
expecting scattered gaps rather than a clean cutoff. Report what you
find to the user before building on top of it.

## Interaction with the rest of the protocol

- `TODO.md` = what needs doing. `claims/` = who is doing what right
  now. `git log` = what actually happened. CLAUDE.md's staleness rule
  still applies: the repo beats every prose declaration, including
  claims.
- Small fixes (typo, one-line bug) don't need claims — the commit
  itself is claim and completion in one. The threshold: if being
  interrupted midway would leave the repo in a state someone else
  might misread, claim it first.
