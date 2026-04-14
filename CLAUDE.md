# Folding Evolution

GP/ALife research project: protein-inspired genotype-phenotype mapping for genetic programming.

## Context

This project continues research started in Elixir/PTC-Lisp (`~/projects/ptc_runner/lib/ptc_runner/folding/`). The Python rewrite focuses on fast experimentation — batch evaluation, visualization, and access to the GP ecosystem (DEAP, NumPy, matplotlib).

## Documentation

- `docs/folding/architecture.md` — The folding pipeline (alphabet, fold, chemistry, operators) — original folding track
- `docs/folding/findings.md` — Folding-track experimental results (authoritative; includes commit hashes)
- `docs/folding/experiments.md` — Folding-track planned experiments with hypotheses and status
- `docs/chem-tape/` and `docs/ca/` — Active research tracks (each has own architecture.md + experiments.md)
- `docs/coevolution.md` — Four coevolution designs tested, lessons learned
- `docs/theory.md` — Altenberg's constructional selection framework
- `Plans/` — Scoped plans for new directions (current: `psb2-sanity-probe.md`)

## Key Findings (current)

1. Folding loses on static metrics (neutrality, crossover) but wins on evolutionary dynamics
2. The regime shift experiment is the key result — folding adapts, direct encoding can't
3. **3-bond ceiling is broken** via Pareto scaffold preservation (§1.11/§1.13): S5 reached in 78–92% of seeds. Both discovery (chemistry screening) and preservation (Pareto on structural pattern) are required — neither alone is sufficient.
4. Altenberg's constructional selection framework explains the static/dynamic discrepancy

For full completed-experiment list and open questions, see `docs/folding/experiments.md` (original track), `docs/chem-tape/experiments.md`, and `docs/ca/experiments.md`.

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
- When documenting findings in any track's `findings.md`/`experiments.md` (or `docs/python-rewrite-results.md`), include the git commit hash that produced the results (e.g. `Results from commit abc1234`). This anchors data to a specific code state for reproducibility.

## Overnight Runs

Nightly experiment queue runner. User authors `queue.yaml`, `scripts/run_queue.py` executes every entry not marked done in `queue.status.json`, writes per-run output to `experiments/output/YYYY-MM-DD/<id>/` including rusage profile. Experiments must write outputs under `$RUN_DIR` (exported to child env) for `expect_outputs` to match. Claude CLI summarization (`scripts/summarize_runs.py`) is a separate morning phase — phase 1 never depends on it. Launch: `caffeinate -s uv run python scripts/run_queue.py`. Design: [Plans/overnight-queue-runner.md](Plans/overnight-queue-runner.md).
