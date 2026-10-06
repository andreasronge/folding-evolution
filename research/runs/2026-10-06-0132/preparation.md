# Researcher preparation and smoke validation

The approved experiment is implemented in `experiments/chem_tape/map_learning_run.py`,
with frozen parameterization/support allocation in `map_learning.py` and paired
inference/plots in `map_learning_report.py`. The existing composition search and
Rust executor are unchanged. Versioned data contains the exact eight PA cells,
original bank SHA256, recovered split, and reused G/G-marg sampling measurements
with source SHA256. All runtime artifacts are under RUN_DIR.

Validation:

- `python -m pytest tests/test_map_learning.py tests/test_composition_bank.py tests/test_assembly_family.py -q`: 32 passed. The nine new tests cover starts,
  parameter bounds/support, sparse mutations, censoring, paired trajectory
  inference, joint seed resampling with four T trajectories, unresolved outcomes,
  runtime reduction order, and refusal to start when evaluation cannot be reserved.
- Ruff check and format pass on all three modules and the new tests; staged
  whitespace checks pass. Python package and Rust extension resolve in this worktree.
- Two end-to-end `--smoke --workers 10 --deadline-seconds 1800` launches with
  RUN_DIR set to `experiments/output/2026-10-06/2026-10-06-0132-researcher-smoke`
  and the corresponding `...-smoke-final` directory. Each completed 848 searches,
  including 104 fresh tests, one trajectory/generation per learner, final-parent
  selection, independent 312500-genotype marginal measurement/check, optional
  sampling and 20 reported contrasts. The final launch completed in 192.7 s.
  Both launches exactly match on all 848 searches' solves, evaluation counts,
  table hashes, training cases and search curves. No map is missing; sampling
  and both marginal checks pass. Smoke outcome classification is suppressed.
- Recomputed the final smoke report/plot with the final reporting code and
  visually checked the plot. Learning/drift points appear at the single smoke
  generation; pooled curves compare the same two holdouts across all arms.

Final smoke calibration used the true caps (65536 training, 524288 tests) but
only one training seed per cell and one generation. Training seconds/search
were C=.754, M=.544, T=1.540. All 12 sparse mutations per arm changed integer
tables; paired score-difference SDs were about 1.38, 1.56 and 1.67 log2 in the
first launch (small smoke diagnostic, not a selection-response estimate).
Sampling was timed in a one-Rayon-thread spawn worker and projected to 653 CPU-s
per 1e8 genotypes, consistent with the proposal's 680 CPU-s. Arm-specific PA
stage-2 tests were included. The final smoke's schedule projections were:

| Schedule | Projected minutes (15% headroom, short smoke calibration) |
|---|---:|
| C6/M6/T6, 25 generations, sampling | 395.0 |
| C6/M6/T6, 25 generations, no sampling | 380.0 |
| C6/M6/T4, 25 generations, no sampling | 315.6 |
| C6/M6/T4, 20 generations, no sampling | 264.3 |

These measurements reveal no infeasibility. They do not replace the full
stage-0 gate: the queue times two complete generations with four seeds/cell
per arm and two independent 120-search G repeatability sets. No smoke score
was used to change the optimizer, split, caps, seeds or outcome rules.
The estimated 405-minute queue wall time includes the longer full calibration.
The internal deadline is 27600 s; the sole queue entry timeout is 28800 s.
Queue parsing, the task ID prefix and eight-hour timeout sum were checked.

Stage 0 freezes the approved fallback schedule using timings and G training
repeatability only. Interrupted or shortened fixed schedules retain raw search
observations, checkpoints and missing-map IDs and cannot receive a planned-study
outcome. A hard kill leaves an explicit incomplete-study marker written before
learning. No holdout score enters selection, runtime reductions or stopping.

No code_review.md or driver_feedback.md was present. Critique 1-5 are addressed
in plan.md and code; critique 6-9 concern belief files outside researcher scope.
Full learning and transfer measurements have not been run by the researcher;
the committed queue is ready for code review and driver execution.
