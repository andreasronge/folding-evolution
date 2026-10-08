# Research tree

Working notebook for the autonomous research loop (`scripts/research.py`).
Agents: read this first, then your role file in `roles/`.

## Layout

- `digest.md` — what we currently believe and why. Start here; every claim
  links to its evidence. Current beliefs only, one short section per root,
  under about 3000 words: history and superseded numbers live in the
  questions' `log.md`.
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
- `plans/` — plans for root questions, written by the strategist, and the
  owner's notes (`owner-*.md`): directions and constraints to weigh, not
  approved experiments.
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
bank: four-reducer-v1   # the task set the decision rests on, or `none`
kind: probe             # only for a probe (see Probes); omit otherwise
---
Question and mechanism · closest known technique (name it; say whether the
map adapts by external fitting, outer-loop selection or per-individual
inheritance) and what this adds beyond it · arms, experimental unit, seeds ·
feasibility (measured rates and runtime the design depends on, or a stage 0
probe) · full cost (agent and queue time) · the primary comparison and its
decision rule · what you expect and what would surprise you · next action.
```

At most 800 words; link harness details instead of repeating them. Only the
primary comparison needs a formal decision rule. A replication, mechanism or
boundary test is worth running even when the technique is known; say which.

## Prior work

Name the closest known technique (GP, EDA, grammar-guided GP, EvoDevo,
evolvability, biology). Search the literature when a mechanism is new to this
tree, and cite only papers you actually found, with links. Ideas from biology
are welcome as hypotheses, never as evidence.

Every proposal is approved by the owner before it runs, or in autonomous
mode (`research.py run --auto`) by the critic: `approve` and
`approve_with_notes` run it; `revise` or `reject` sends it back to the
steward (with critique.md). The critic judges value as well as validity: a
valid experiment that changes little may be sent back. After two revisions
the strategist redesigns or redirects instead; five turned-down proposals in a row need the owner. If the
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

Choose the cheapest experiment that could change the decision, counting agent
time (about an hour per cycle) as well as queue time. Do not enlarge a queue
just to fill the time available. The driver refuses queues whose entry
`timeout_seconds` sum to more than `max_queue_hours`, because nothing may run
longer than that without an agent reviewing the results. Split longer studies
into stages, each analysed and decided before the next.

## Probes

A probe (`kind: probe`) is a cheap, open look at something unexplained: at
most 60 min of queue timeouts, fixed seeds, descriptive output, no outcome
table. Its results are observations: they go in the question's `log.md`, may
motivate a proposal, and enter the digest as beliefs only after a later
experiment confirms them. An autonomous run allows one probe plus one per four
full experiments; it is an allowance, not a quota.

## Task banks

Name the task set an experiment rests on in `bank:`. A bank that earlier
decisions were based on is a development bank: fine for mechanism studies,
but a transfer claim needs a fresh bank, frozen together with the method
before it is scored. More seeds or one extra task do not make a bank fresh.

## Autonomous mode

The strategist (`roles/strategist.md`) reviews the whole program every few
cycles, when a proposal moves to another root question, and when the steward
ends `decide` with `next: strategy` in decision.md's frontmatter instead of a
proposal, and after two critic revisions. When the next proposal only lacks
budget, the strategist makes a short allocation decision instead
(`allocation.md`: grant a block of experiments, or ask for a full review). It writes `runs/<task>/strategy.md`, which the next proposal reads, answers
each new or changed owner note (pursued, deferred or declined), may raise root
budgets, write plans in `plans/`, and open up to two new root
questions per autonomous run. Only the strategist opens root questions
(top-level folders); the steward adds sub-questions. A run ends after
`auto_max_experiments` experiments, at its deadline (a finished queue is
still analysed), on `research/STOP`, or when the strategist writes
`next: stop`. The driver keeps a one-row-per-cycle table in
`briefs/<run>-ledger.md`.
