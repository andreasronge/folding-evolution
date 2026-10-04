# Plan: autonomous research tree (v2 of the nightly coordinator)

Status: implemented 2026-10-04 (`scripts/research.py`, `research/`). Not yet
scheduled; first nights are owner-supervised. Builds on
[nightly-research-coordinator.md](nightly-research-coordinator.md) (v1: flat
approved backlog); v2 replaces the backlog with a tree of questions and keeps
v1's execution, validation and briefing requirements.

Advice incorporated from Codex (gpt-6.1-sol) consult, 2026-10-04.

## Goal

Research runs overnight with only high-level control from the owner. Agents
pick up a question, run an experiment, interpret it, and propose what next —
including going deeper, parking a direction, or reopening an old one. The owner
sees a short morning brief: what was tested, what we learned, why we go where
we go next.

Principles:

- **Files are the memory.** Any fresh agent can continue from the repo alone.
- **Minimal code and instructions.** Agents explore the folder themselves; we
  only fix the few conventions that make that work.
- **The driver enforces limits, agents supply judgment.** Budgets and stop rules
  live in code, not in prompts an agent might forget.
- **Stopping is the default.** Continuing a direction needs a written reason.

## The research folder

```
research/
  README.md            how the tree works; the only standing instructions (~1 page)
  digest.md            what we currently believe and why, 1–2 pages, every claim linked
  agents.toml          agent kind → headless command template
  roles/
    steward.md
    researcher.md
    reviewer.md
  questions/
    01-map-bias/
      question.md
      log.md
      02-crossover-dose/
        question.md
        log.md
    03-.../
  runs/                one folder per task (driver-owned, see below)
  state.json           driver bookkeeping (phase, task id, budget used)
  briefs/2026-10-05.md
```

### question.md

```markdown
---
status: open            # open | parked | closed
tags: [crossover, map-bias, persistence]
budget: {experiments: 3, used: 1}   # children draw from the parent's remainder
---
# Does crossover dose explain first-form persistence?

Current summary: two or three sentences, kept current by the steward.

Competing explanations:
- A: map bias makes the form frequent on arrival
- B: crossover preserves it once present

Related: ../../05-latent-helper/ (negative result), docs/chem-tape/experiments.md §31

Reopen if: (only for parked) a concrete condition, e.g. "a map where B is
testable without stage-4 confound".
```

### log.md

Append-only, steward-written. Each entry: experiment → result (with link to
`experiments/output/...`) → a line starting with `Decision:` and its reason.
The `Decision:` prefix is the one convention that makes decision history
greppable.

### Conventions that make "just explore the folder" work

- Folders never move; status lives in frontmatter.
- Folder nesting is history; `Related:` links express real relationships
  (grep finds words, not the same mechanism under another name).
- Parked questions carry a reopen condition. Part of the steward's routine is
  `grep -l "status: parked"` and asking whether new findings meet it.
- `digest.md` is the index. If scanning gets slow, *generate* a flat listing
  (path, title, status, tags) from frontmatter — never a hand-kept catalog.
- Raw data stays in `experiments/output/`; `findings.md` stays the home for
  claims the owner promotes. `research/` is the working notebook and links to
  historical track docs instead of copying them.

## Roles (three to start)

| Role | Does | Writes |
|---|---|---|
| **Steward** | Reads digest + tree. Chooses the question, decides continue / park / close / propose new. Updates question state, logs, digest. Writes the brief. | `questions/**`, `digest.md`, `briefs/` (only role that edits shared state) |
| **Researcher** | Designs the experiment and states what each outcome would mean *before* running. Implements in a worktree, smoke-tests, prepares the queue entry. | its `runs/<task>/` folder, worktree code |
| **Reviewer** | Different model. Before execution: reviews changed code (skipped if harness unchanged). After: analyses results independently, then challenges the researcher's interpretation. | its `runs/<task>/` folder |

"Different opinions" come from the reviewer being a different model and from
questions listing competing explanations — the researcher must say which
explanation each outcome hurts. Blind analysis is enforced by input: the
reviewer first gets question, config, measurements and code, and only then the
researcher's predictions.

More roles (separate analyst, curator, advocates for rival explanations) can be
split out later if a role's prompt gets overloaded. Not before.

### Role file

```markdown
---
agent: codex
model: gpt-6.1-sol
effort: high
timeout_min: 60
---
You are the reviewer. ...
```

Changing which model plays a role is a one-line edit.

## Running agents: headless, inside herdr panes

Codex pointed out that herdr's interactive `agent wait` / `agent prompt` can't
prove a specific assignment finished (waits can match an earlier turn, timeouts
don't stop the agent). So agents run **headless**, but **in a herdr pane** so
the owner can watch or attach:

```
herdr pane run <pane> 'cd <worktree> && <headless cmd> ; echo $? > research/runs/<task>/exit'
```

`agents.toml` maps each kind to its headless form; adding an agent is one line:

```toml
[claude]
cmd = "claude -p {prompt} --model {model} --permission-mode acceptEdits"
[codex]
cmd = "codex exec {prompt} -m {model} -c model_reasoning_effort={effort} --sandbox workspace-write"
[gemini]
cmd = "gemini -p {prompt} -m {model}"
[opencode]
cmd = "opencode run {prompt} -m {model}"
```

The driver polls for `exit` plus the expected output file, enforces
`timeout_min`, and closes the pane (killing the process) on timeout. Success
means "the expected artifact exists and parses", not "the agent went idle".

Prompts stay short: *"You are the reviewer. Read research/roles/reviewer.md and
research/README.md. Task: research/runs/<task>/task.md. Write
research/runs/<task>/review.md."*

## The nightly cycle (fixed phases)

```
select → prepare → code review → execute → analyse/review → decide & brief → stop
steward   researcher  reviewer     run_queue   reviewer         steward
```

- **One cycle per night** to start. The steward proposes the next one in the
  brief; same-night adaptive cycles come after recovery is proven.
- The driver enforces the phase order; an agent can't skip review or dispatch
  arbitrary roles.
- One critique round, one bounded repair; unresolved blockers → park and report.
- `state.json` holds task id, phase, launch identity, expected artifact and
  budget used, written atomically. On restart the driver reconciles with the
  pane/queue state before re-dispatching anything.
- Every task and every queue retry gets a unique id (status is keyed by id;
  reused ids skip runs or mix outputs).

The driver is a small Python script; its size should follow from these
failure cases, not from a line target.

## Stopping and budgets

- Each question has an experiment budget; **children draw from the parent's
  remainder** (subdividing creates no new allowance). An "experiment" is a
  bounded campaign with fixed arms, seeds and runtime.
- Prep, review, repair and failed launches count against the night's
  time / model-call limits.
- **Park after two valid results that changed no decision and distinguished no
  explanations.** Close when answered or deliberately abandoned.
- Continuing past budget requires the steward to write why the next experiment
  beats the best other open question; that goes to the owner, not auto-run.

## Owner control

- Owner sets root questions, global budget, and which agents/models fill roles.
- **Before bed:** approve the night's experiment and limits (edit/OK the
  steward's proposal). **Morning:** read the brief, approve or redirect the next
  proposal.
- Sub-questions within an approved root can be proposed freely; a pivot to a new
  root or reopening a parked one without approval produces a brief and stops.
- Brief format: what was tested and why · what happened (key numbers, 1–3 plots)
  · what we learned (1–3 sentences) · tree change · next proposal and why ·
  failures/uncertainty.

## Prerequisites: queue runner fixes

Unattended launches need these fixed first (confirmed in code):

1. `run_queue.py:351` reclassifies and saves status *before* taking the lock — a
   second invocation can mark a live run interrupted. Lock first.
2. `queue_lib.py:153` lock is check-then-write; use `fcntl.flock`.
3. `run_queue.py:207` `shell=True` child is killed alone; workers can survive.
   Start a new session/process group and kill the group with escalation.
4. Parallel groups share one `state.current_child` (`run_queue.py:435`). Track
   all children or disable parallel groups for coordinator runs.
5. The runner exits 0 even if entries failed — the driver reads per-entry status
   and runs v1's validation (arms, seed coverage, duplicates, config, outputs).

Also from v1: freeze the execution checkout/config, and check the Rust extension
was built from that checkout.

## Rollout

1. Fix the runner defects.
2. Seed `research/`: README, roles, `agents.toml`, `digest.md` from current
   map-bias findings, one root question (current map-bias line) with 2–3
   children reconstructed from §31–§32.
3. Run one cycle manually with the driver phase by phase, owner watching in herdr.
4. Test failure handling: kill an agent mid-run, timeout, blocked permission
   prompt, driver restart mid-phase.
5. Run nightly for a week with bedtime/morning approval. Note which steward
   decisions the owner overrides — that's what to tune or automate next.
6. Only then: multiple cycles per night, more roles, automatic sub-question
   execution.

## Implementation notes

- Every proposal needs owner approval in this version (`research.py approve`),
  including sub-questions. Loosen once the owner's override rate is known.
- Code chains through `research/main`: each experiment branches from it and it
  fast-forwards to the experiment's commit after the run. The owner merges
  `research/main` into `main` when wanted; the driver merges `main` into each
  new experiment branch so the owner's work is picked up.
- Daytime runs: `research.py run --now` (same cycle, deadline `day_max_hours`).
- If herdr is not reachable the driver falls back to plain local processes.

## Open decisions

- Which models fill steward / researcher / reviewer?
- Nightly time and model-usage budgets.
- Brief destination: repo Markdown first; HTML later?
- Does the steward run on the laptop session or the Mini?
