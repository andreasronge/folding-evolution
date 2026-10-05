# Plan: autonomous mode and a strategist role (v3 of the research loop)

Status: implemented 2026-10-04, after a Codex (gpt-6.1-sol) plan review. Builds on [research-tree.md](research-tree.md) (v2: one
cycle per owner approval). Goal: the loop runs for one or two days without the
owner, then the owner reviews what it did and changes how it works.

## What changes

1. **`research.py run --auto --hours 48`**: cycles run back to back until the
   hours are used, the `research/STOP` file appears, or the loop needs the owner.
   No night window. The owner's approval is replaced by the critic's.
2. **A strategist role** (Codex `gpt-6-astra`, high effort): steps back from the
   current line, chooses where the program goes next, and may open at most one
   new root question per autonomous run, with a plan.
3. **A cap on unreviewed compute**: one experiment's queue may run at most
   `max_queue_hours = 8`. Agents size experiments to the question; anything
   longer is split into stages, each analysed and decided before the next.

Everything else stays: fixed phases, reviewer on code and results, budgets,
commit + push after every cycle, owner-only `findings.md`.

## Approval in autonomous mode

At `awaiting_approval`, `--auto` reads `critique.md`'s `recommend:`:

| critic says | first proposal | after one re-proposal | after two |
|---|---|---|---|
| approve / approve_with_notes | run it | run it | run it |
| revise or reject | steward re-proposes | steward re-proposes | strategist redesigns or redirects, then up to two more proposals; then owner needed |
| (no verdict) | agent failure, retried | | |

A proposal at a node with no budget left goes to the strategist, who may
raise the root's budget or redirect (v2). `approval.md` records how it was approved. The
researcher always reads `critique.md`, in both modes, and the code reviewer
checks that its points are answered in plan.md.

Re-proposals start a new task folder (as `reject` does now), so every proposal
and critique is kept for the owner's review.

## Strategist

Role file `research/roles/strategist.md`: `agent: codex`, `model: gpt-6-astra`,
`effort: high`. It writes `runs/<task>/strategy.md`: what the program has
learned, which root questions matter and why, which to work on next, and what
the steward should propose. It may:

- create **one** new root question (`questions/NN-slug/` with `question.md`,
  `log.md`, a budget proportional to its plan) and its plan in
  `research/plans/<slug>.md`;
- not edit existing questions, `digest.md`, briefs or `findings.md` (the steward
  integrates the strategy in its next proposal and decide step).

When it runs (autonomous mode only), after `decide`:

- every `strategy_every = 4` cycles (the decide prompt then asks for no
  proposal);
- when the steward's next proposal moves to a different root question (the
  proposal is kept as `steward_proposal.md` for the strategist to weigh);
- when the steward writes `next: strategy` in decision.md's frontmatter
  because no open question deserves another experiment. A decide step with
  neither a proposal nor `next: strategy` is an agent failure.

The strategist's `strategy.md` starts with `next: proposal` or `next: stop`;
stop ends the run (owner needed). Then `propose` (the steward reads
strategy.md), critique and approval as usual.

**One new root per run**: the driver records the top-level question folders
when the run starts (in `auto_run.json`) and checks after every phase that
writes the tree (proposal, decide, strategy). More than `max_new_roots = 1`
new ones → stop, owner needed. Only the strategist is told it may open roots.

**End-of-run summary**: when an autonomous run ends (except Ctrl-C), the
strategist writes `briefs/<run-id>-auto-summary.md` (a plain list of the run's
briefs if that agent fails), then it is committed and pushed: every cycle of the run in a
line or two, how the tree and digest changed, what it would do next, where it
was least sure, and what the owner should check first. This is the owner's
starting point for the review.

## Compute cap

- `max_queue_hours = 8` (config). `check_prepared` rejects a queue whose entry
  timeouts sum to more, or any non-positive timeout (driver feedback to the
  researcher: set realistic `timeout_seconds`, or split into stages). The
  default entry timeout is 4 h.
- The cap is cumulative: queue time is recorded in state, and a resumed queue
  gets only what is left. After a driver crash the attempt is charged
  conservatively (all time since it started). Used up → the experiment is blocked and goes to `decide`.
- The run's deadline is a cutoff for *starting* work: a queue started before
  it may finish after it (by at most the cap). Code review now always runs,
  also when only queue.yaml changed.
- README and role files say: size experiments by what the question needs;
  short is fine; up to 8 h of queue when justified; longer work is staged.

## Robustness for unattended runs

- **Durable run state** in `research/auto_run.json` (id, deadline, roots at
  start, cycle counters). `run --auto` resumes an unfinished run with its
  original deadline; delete the file to start a new one.
- **Only agent failures are retried** (non-zero exit, timeout, missing or
  incomplete output): after 10 minutes, at most 3 in a row per task+phase.
  Every other stop (changed code after review, queue failure, git error, owner
  needed, deadline) ends the run with the summary. A critique counts only if the
  critic finished successfully (recorded in state); otherwise it is redone; the decide prompt asks the steward not to
  log twice when retried. Git calls are time-bounded.
- **STOP file**: checked between phases in every mode. The running phase
  finishes (a queue may take up to 8 h); Ctrl-C stops at once.
- `max_agent_calls` stays per cycle; re-proposals start a new task, so they
  get a fresh count.

## Owner review after 1–2 days

Read the auto summary, then `git log -p research/digest.md`, the briefs, and
the critic's recommendations against what ran. Questions to answer: did the
critic gate well; did the strategist's root make sense; were experiment sizes
sensible; did beliefs drift without evidence? Then tune roles, caps and the
approval table.

## Not in this version

Parallel experiments, the owner being notified (push notifications), raising
budgets automatically, merging `research/main` into `main`.

## v2, after the first autonomous run (2026-10-05)

The first run (2026-10-05-1503) stopped after 5.5 of 48 h: root 01's budget
ran out and the strategist chose `next: stop`. A Claude and a Codex review of
the run's record led to these changes:

- **Run pool.** A run executes at most `auto_max_experiments = 40`
  experiments (charged when a queue first starts; revised, set-aside and
  infeasible proposals cost nothing). Question budgets become allocations:
  the strategist may raise a root's budget in steps of 1–4, the driver
  refuses raises by anyone else, and a proposal with no budget goes to the
  strategist instead of being rejected. Up to two new roots per run.
- **Stopping.** The strategist stops only after comparing at least two
  directions and saying why none deserves a feasibility probe; it may write
  plans instead. "Stopping is the default" is gone from the README.
- **Feasibility first.** Proposals state the rates and runtime they depend
  on, or start with a probe. The researcher can write `infeasible.md`; the
  driver then skips the build and review and goes to `decide`, uncharged.
- **Critic.** New `approve_with_notes`; `revise` only for a blocking point;
  a revision is checked against the previous critique first; after two
  revisions the strategist steps in instead of running a contested proposal.
- **Reviewer.** Gates and stop rules that decide whether the main stage runs
  must be stable and sized to the queue time, or the review fails.
- **Statistics.** README "Statistics": simple pre-stated comparisons, one
  95% interval, heavier machinery only when a decision depends on it.
- **Digest check.** The critic checks the previous cycle's belief updates
  against its analysis (`## Digest check` in critique.md); the steward fixes
  them in its next decide.
- **Deadline drain.** A queue that finished is still analysed and decided
  after the deadline.
- **Ledger.** The driver writes `briefs/<run>-ledger.md`, one row per cycle
  (critic verdict, code review, queue minutes against the estimate, charged,
  outcome, decision), the owner's first table to read.
