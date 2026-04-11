# Folding Evolution

GP/ALife research project: protein-inspired genotype-phenotype mapping for genetic programming.

## Context

This project continues research started in Elixir/PTC-Lisp (`~/projects/ptc_runner/lib/ptc_runner/folding/`). The Python rewrite focuses on fast experimentation — batch evaluation, visualization, and access to the GP ecosystem (DEAP, NumPy, matplotlib).

## Documentation

- `docs/architecture.md` — The folding pipeline (alphabet, fold, chemistry, operators)
- `docs/findings.md` — All experimental results from the Elixir implementation
- `docs/experiments.md` — Planned experiments with hypotheses and setup
- `docs/coevolution.md` — Four coevolution designs tested, lessons learned
- `docs/theory.md` — Altenberg's constructional selection framework

## Key Findings (from prior work)

1. Folding loses on static metrics (neutrality, crossover) but wins on evolutionary dynamics
2. The regime shift experiment is the key result — folding adapts, direct encoding can't
3. Separated coevolution with data-dependence gate is the best design
4. Complexity ceiling at 3 bonds is the main limitation to address
5. Altenberg's framework explains the static/dynamic discrepancy

## Tech Stack

- **Language**: Python 3.12+ with Rust backend (PyO3)
- **Rust acceleration**: `_folding_rust` module provides `rust_develop`, `rust_develop_batch` (Rayon parallel), and `rust_develop_and_score_batch` (full VM scoring). The Python `develop()` function auto-detects and uses the Rust path.
- **Performance**: When writing experiment loops, use `develop_batch(genotypes)` for population evaluation (2-3x faster than per-individual `develop()`). The `dynamics.py` engine already uses batch and VM paths — prefer reusing it over writing custom eval loops.
- **Visualization**: matplotlib/seaborn
- **Notebooks**: Jupyter for experiments

## Design Principles

- Experiments should be reproducible (fixed seeds, logged parameters)
- Visualization of every experiment (fitness curves, population diversity, bond count distributions)
- The fold/chemistry pipeline should be decoupled from the evaluation language
- Compare against standard GP baselines (DEAP tree GP)
- When documenting findings in `docs/findings.md` or `docs/python-rewrite-results.md`, include the git commit hash that produced the results (e.g. `Results from commit abc1234`). This anchors data to a specific code state for reproducibility.
