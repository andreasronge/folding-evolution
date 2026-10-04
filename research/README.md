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
  `plan.md`, `queue.yaml`, `code_review.md`, `execution.md`, `analysis.md`,
  `decision.md`. Raw data lives in `experiments/output/` (linked from
  `execution.md`).
- `briefs/` — the owner's morning briefs.
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
against every ancestor, and cannot run when any ancestor has none left. Only
the owner raises `experiments`. `research.py status` shows what is left.

Stopping is the default. Park a question after two valid results that
changed no decision and separated no explanations. Close it when answered.

## Proposal format

`runs/<task>/proposal.md`:

```markdown
---
node: questions/01-map-bias/04-random-start-discovery   # relative to research/
title: Short name of the experiment
---
Why this now · what would be run (arms, seeds, rough runtime) · what each
outcome would mean · alternatives considered.
```

Every proposal is approved by the owner before it runs.
