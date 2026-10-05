# Research tree

Working notebook for the autonomous research loop (`scripts/research.py`).
Agents: read this first, then your role file in `roles/`.

## Layout

- `digest.md` — what we currently believe and why. Start here; every claim
  links to its evidence.
- `questions/NN-slug/` — one folder per research question; sub-questions are
  sub-folders. Each has `question.md` (frontmatter `status`, `tags`,
  `budget`; summary, competing explanations, `Related:` links, `Reopen if:`)
  and `log.md` (append-only: experiment → result → `Decision: … because …`).
- `runs/<task>/` — one folder per experiment cycle: `proposal.md`,
  `critique.md`, `plan.md`, `queue.yaml`, `code_review.md`, `execution.md`, `analysis.md`,
  `decision.md`. Raw data lives in `experiments/output/` (linked from
  `execution.md`).
- `briefs/` — the owner's morning briefs, and `<run>-auto-summary.md` after
  an autonomous run.
- `plans/` — plans for root questions, written by the strategist.
- `roles/`, `agents.toml`, `config.toml` — who plays which role, how agents
  are launched, loop settings.

## Conventions

- **Find prior work by exploring.** `grep -r` the tree for tags, terms and
  `Decision:` lines; follow `Related:` links. There is no other index.
- Folders never move or get renamed; status lives in frontmatter. Number new
  question folders after the highest existing number anywhere in the tree.
- Parked questions keep a concrete `Reopen if:` condition. New evidence that
  meets it is a reason to reopen.
- Link, don't copy: point to `docs/`, notebooks and run folders.
- `findings.md` files in `docs/` hold claims the owner has promoted. This
  folder is the working layer and may be wrong; say how sure you are.

## Budgets and stopping

`budget: {experiments: N, used: M}` in `question.md`. Experiments the loop
runs are counted automatically from `runs/*/execution.md` (by the proposal's
`node`); `used` is only for experiments counted by hand, normally 0.
Sub-questions draw from their ancestors' budgets: an experiment counts
against every ancestor, and cannot run when any ancestor has none left.
Budgets are allocations, not verdicts: the owner sets them, and in an
autonomous run the strategist may raise a root's budget (the run itself is
capped at `auto_max_experiments`). `research.py status` shows what is left.

Park a question when further experiments would not change a decision, not to
save budget; an unresolved result that a larger or better-sized run could
settle is a reason to propose that run, unless another question is worth
more. Close a question when it is answered.

## Proposal format

`runs/<task>/proposal.md`:

```markdown
---
node: questions/01-map-bias/04-random-start-discovery   # relative to research/
title: Short name of the experiment
---
Why this now · what would be run (arms, seeds, rough runtime) · feasibility
(measured hit or solve rates and runtime the design depends on, or a stage 0
probe that measures them) · what each outcome would mean, as outcome rules
that do not overlap, with an `unresolved` row · alternatives considered.
```

Every proposal is approved by the owner before it runs, or in autonomous
mode (`research.py run --auto`) by the critic: `approve` and
`approve_with_notes` run it; `revise` or `reject` sends it back to the
steward (with critique.md). After two revisions the strategist redesigns or
redirects instead; five turned-down proposals in a row need the owner. If the
researcher finds an approved design infeasible, it writes `infeasible.md` and
the steward re-plans.

## Statistics

This is a lab notebook, not a paper. Prefer simple pre-stated comparisons:
one effect size with a 95% interval, a fixed n chosen so the interval can
change a decision. Use multiplicity corrections, sequential looks, power
gates and equivalence margins only when the decision really depends on them;
a design whose gates are longer than its question is too heavy. A finite
sample with no hits is an upper bound, not absence; an unresolved difference
is not equality.

## Experiment size

Size an experiment by what the question needs, up to 8 h of queue time when
that is justified. Each cycle costs about an hour of agent work, so prefer one
well-sized experiment over several tiny ones: a queue under 30 min usually
should have done more, or had a later stage gated in code. The driver refuses queues whose entry
`timeout_seconds` sum to more than `max_queue_hours`, because nothing may run
longer than that without an agent reviewing the results. Split longer studies
into stages, each analysed and decided before the next.

## Autonomous mode

The strategist (`roles/strategist.md`) reviews the whole program every few
cycles, when a proposal moves to another root question, and when the steward
ends `decide` with `next: strategy` in decision.md's frontmatter instead of a
proposal, when the next proposal has no budget left, and after two critic
revisions. It writes `runs/<task>/strategy.md`, which the next proposal reads,
may raise root budgets, write plans in `plans/`, and open up to two new root
questions per autonomous run. Only the strategist opens root questions
(top-level folders); the steward adds sub-questions. A run ends after
`auto_max_experiments` experiments, at its deadline (a finished queue is
still analysed), on `research/STOP`, or when the strategist writes
`next: stop`. The driver keeps a one-row-per-cycle table in
`briefs/<run>-ledger.md`.
