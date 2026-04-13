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

## Direction

An upcoming probe evaluates whether the project should reframe around **inductive program synthesis from input-output examples** (PBE) using [PSB2](https://arxiv.org/abs/2106.06086) as an external benchmark. The hypothesis is that the chem-tape + folding representation, combined with Pareto scaffold preservation (see [Findings §1.11/§1.13](docs/findings.md)), produces a smaller train→held-out generalization gap than direct-encoding GP at matched compute. Plan: [Plans/psb2-sanity-probe.md](Plans/psb2-sanity-probe.md). This is a scoped probe, not yet a committed pivot — the decision rule is in the plan.

## Documentation

- **[Research Findings](docs/findings.md)** — What we know so far, with data
- **[Architecture](docs/architecture.md)** — The folding pipeline: genotype -> fold -> chemistry -> phenotype
- **[Experiments](docs/experiments.md)** — Planned experiments and their rationale
- **[Coevolution Designs](docs/coevolution.md)** — Four coevolution frameworks tested, what worked and what didn't
- **[Theory](docs/theory.md)** — Altenberg's constructional selection and how it connects

## Key References

- Altenberg, L. (1995/2023). "Genome Growth and the Evolution of the Genotype-Phenotype Map." — Constructional selection, pleiotropy, genome-as-population
- Hillis, W.D. (1990). "Co-evolving parasites improve simulated evolution as an optimization procedure."
- Bonner, J.T. (1974). *On Development*. — Low pleiotropy principle
- Kauffman, S.A. (1989). "Adaptation on rugged fitness landscapes." — NK model
