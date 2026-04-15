# Folding Evolution

Protein-inspired genotype-phenotype mapping for genetic programming research.

A linear genotype string folds onto a 2D grid. Characters that land adjacent bond according to fixed chemistry rules, assembling into executable program ASTs. The folding is the development process — it creates a non-linear mapping between sequence position and program structure.

## Research Question

**Does a developmental encoding (folding) enable qualitatively different evolutionary dynamics than direct encoding?**

Prior work (in Elixir/PTC-Lisp) established:
- Folding loses on static metrics (lower neutrality, more catastrophic mutations, worse crossover preservation)
- Folding wins on dynamic metrics (discovers solutions direct encoding cannot reach, adapts to regime shifts, exhibits punctuated fitness dynamics)
- Coevolution finds equilibria quickly but hits a complexity ceiling at 3-bond programs

This project continues the research in Python for faster experimentation and access to the GP/ALife ecosystem.

## Running Overnight Experiments

The nightly queue runner (`scripts/run_queue.py`) runs every entry in `queue.yaml` whose id isn't already terminal in `queue.status.json`. Per-run output lands in `experiments/output/YYYY-MM-DD/<id>/` with stdout/stderr logs, rusage profile, and metadata. Experiments must write their outputs under `$RUN_DIR` (exported to the child environment) for `expect_outputs` checks to pass.

```
# before bed: lint your queue, then kick off
uv run python scripts/run_queue.py --validate
caffeinate -s uv run python scripts/run_queue.py

# morning: Claude-CLI summaries
uv run python scripts/summarize_runs.py
```

For a pre-bed smoke test, maintain a `smoke.yaml` with short-budget variants of tonight's runs (e.g. 2 seeds, 10 generations) and run it against disposable state:

```
uv run python scripts/run_queue.py \
  --queue smoke.yaml \
  --status /tmp/smoke.status.json \
  --lock /tmp/smoke.lock \
  --output-root /tmp/smoke_out
```

Full design: [Plans/overnight-queue-runner.md](Plans/overnight-queue-runner.md).

## Direction

An upcoming probe evaluates whether the project should reframe around **inductive program synthesis from input-output examples** (PBE) using [PSB2](https://arxiv.org/abs/2106.06086) as an external benchmark. The hypothesis is that the chem-tape + folding representation, combined with Pareto scaffold preservation (see [Findings §1.11/§1.13](docs/folding/findings.md)), produces a smaller train→held-out generalization gap than direct-encoding GP at matched compute. Plan: [Plans/psb2-sanity-probe.md](Plans/psb2-sanity-probe.md). This is a scoped probe, not yet a committed pivot — the decision rule is in the plan.

## Documentation

- **Research Tracks** — Each track has its own architecture + experiments:
  - [Folding](docs/folding/architecture.md) — original 2D-grid folding chemistry ([experiments](docs/folding/experiments.md), [findings](docs/folding/findings.md))
  - [Chem-tape](docs/chem-tape/architecture.md) — 1D token tape with bond bits ([experiments](docs/chem-tape/experiments.md))
  - [CA](docs/ca/architecture.md) — cellular-automata development ([experiments](docs/ca/experiments.md))
- **[Coevolution Designs](docs/coevolution.md)** — Four coevolution frameworks tested, what worked and what didn't
- **[Theory](docs/theory.md)** — Altenberg's constructional selection and how it connects

## Research Workflow (`/research-rigor`)

The `research-rigor` skill (`.claude/skills/research-rigor/`) enforces [methodology.md](docs/methodology.md) at the three checkpoints where overreach silently accumulates. Invoke it by intent, not a literal command.

Lifecycle for a new experiment:

```
  (1) prereg  →  [run sweep]  →  (2) log-result  →  [replicate/inspect]  →  (3) promote-finding
                                        │
                                        ↓
                                 scope-check (inline)
                                 supersession (when a later experiment narrows)
```

| mode | when | produces |
|---|---|---|
| **prereg** | *before* running — "pre-register X", "design experiment for Y" | `Plans/prereg_<slug>.md` with outcome table, decision rule, degenerate-success guards, sampler diagnostics |
| **log-result** | *after* running — "log result of §X", "write up X" | section in `docs/<track>/experiments.md` matching a pre-registered outcome row |
| **promote-finding** | only after replication + mechanism inspection — "promote §X to findings" | scope-tagged entry in `docs/<track>/findings.md` |
| **scope-check** | any draft text — "review this claim", "is this overreaching" | diff of overreach phrases → scope-qualified rewrites |
| **supersession** | when a later experiment narrows/falsifies an earlier one — "supersede §X", "retract §X" | explicit retraction block; original reasoning preserved |

Not every run needs a new prereg. If a prior prereg already covers the work (e.g., its promised baseline sweep was skipped), skip straight to running the YAML and then **log-result** to discharge the outstanding promises. Genuinely new outcome tables / decision rules need their own prereg first.

Templates that back the skill live in [docs/_templates/](docs/_templates/).

## Key References

- Altenberg, L. (1995/2023). "Genome Growth and the Evolution of the Genotype-Phenotype Map." — Constructional selection, pleiotropy, genome-as-population
- Hillis, W.D. (1990). "Co-evolving parasites improve simulated evolution as an optimization procedure."
- Bonner, J.T. (1974). *On Development*. — Low pleiotropy principle
- Kauffman, S.A. (1989). "Adaptation on rugged fitness landscapes." — NK model
