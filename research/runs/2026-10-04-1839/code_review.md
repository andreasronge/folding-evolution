---
verdict: pass
---
# Code review — self-mate establishment contest and census

Reviewed `aed8aad..f2e4048` (new `experiments/chem_tape/self_mate_establishment.py`,
the sweep YAML, `tests/test_self_mate_establishment.py`, task-folder copies) against
proposal.md, plan.md and queue.yaml. No engine or Rust code changed.

## Blocking issues

None.

## What I checked

- **Arm wiring.** The committed YAML equals `make_spec()` output (loaded both and
  compared). `base` is `s31_dose.yaml`'s base plus `crossover_mate: self` only. The
  eight paired cells are the four L 64 / crossover 0.3 records of `s31_dose.yaml`
  (32-tape and 10-tape lists, each with exactly two distinct tapes: shared plus one
  competitor), each at rates 0.3 and 0.7. 240 distinct config hashes; the test
  confirms the cell × seed set is exactly duplicated/partly × 1/32, 1/10 × 0.3/0.7 ×
  seeds 0–29, and that the initial population holds 32 or 103 shared copies.
- **Self mate reaches the operator.** `evolve._mate` returns `population[i]` for
  `crossover_mate == "self"` in both breeding paths (evolve.py:604, :733), and
  `ChemTapeConfig.hash()` includes the field when it is not `selected`, so these runs
  cannot collide with the historical selected-mate runs.
- **Seeds.** Seed is the only grid axis, crossed with all eight cells, as in §31 D.
  Using the same seeds 0–29 as the historical rows is what the proposal asks for.
- **Final verdict.** `r31.classify_run` / `r31.outcome` are reused unchanged: non-elite
  final population, exhaustive exactness, ≥ 20 exact, > 90% shared = won, 0 = gone.
  Boundary tests pass.
- **Early readouts.** Taken straight from `shared_stats` (256-individual sample,
  shares conditional on full exactness, elites included). Undefined shares stay null
  and are excluded from the conditional mean with `n_defined` reported; the
  unconditional frequency `shared × n_fully_exact / n` is computed correctly and
  counts zero-exact samples as zero. Both are labelled as such.
- **Census.** Calls `tagged.crossover(parent, parent, rng, 'v2')`, the same function
  and variant the engine uses for TAG runs. Parents are taken from the sweep's seed
  tapes and checked to equal `sh.form_genome` and to classify as their own form.
  Exactness is tested per child before the semantic-key cache is consulted, so the
  cache cannot change counts; categories are mutually exclusive and sum to `events`.
- **Completeness guards.** `report` fails on any missing run, config mismatch, short
  run, missing census generation, bad denominator or extra run directory before
  writing anything. No silent exclusion path.
- **Queue.** Both commands write under `$RUN_DIR`; `expect_outputs` match what
  `sweep.py` and the report/census commands write. Run size matches the proposal.
- `tests/test_self_mate_establishment.py`: 8 passed locally.

## Minor notes (not blocking)

1. `exact_other` can never be non-zero: `sh.classify` gives every fully exact genome
   one of shared / partly / duplicated. The column is harmless but will always read 0;
   genomes with `other_output_helper` are counted as duplicated or partly, as in §31.
   The analysis should not read the zero as evidence that no unusual forms arose.
2. The historical comparison columns are hard-coded (`OFF_WINS`, `SELECTED_WINS`,
   default 0 for selected-mate cells not listed). The values match the proposal and
   plan, but they are not re-derived from the §30/§31 run folders, so the analysis
   should cite those sources rather than this table.
3. All three census parents use the same RNG seed 0 (as planned). The streams diverge
   as soon as the parents' run structures differ, but the three rows are not
   independent draws in the strict sense. At 10,000 events this does not matter.
4. The census test's direct classification maps "not fully exact" to `broken` via
   `classify(...)['form'] or 'broken'`, a slightly different route from the script's
   `Exactness` check. They agree by construction; just a different path, not a second
   independent oracle.
5. The trajectory plot and the "shared population frequency" column include elites
   and are sample-based; the final verdict excludes elites and is exhaustive. The
   report says this, and the analysis should keep the two apart.6. Census measures the hand-built seed layouts only, and with no mutation; in the
   evolution runs every non-elite child is also mutated (μ 0.015). Census "broken"
   rates are therefore a lower bound on per-generation loss, not an estimate of it.
