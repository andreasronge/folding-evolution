Implemented on research/2026-10-10-2001, commit 6dabda8.

- New `experiments/chem_tape/component_transfer_run.py` reuses the unchanged
  production search, decoder, literal operator, verifier, worker pool helper,
  bank validators and original provenance loader. Explicit component owners,
  build identities and operator mode replace the old cohort-bound arm dispatch.
- `data/component_transfer_2001/` freezes all 48 final/intermediate builds,
  complete source rows/schedule, banks, original admitted preparation and 16
  identity-selected historical native rows. Raw hashes, method freeze, source
  membership and table/library digests are checked before work. No fitting.
- `component_transfer_report.py` implements fixed-cell capped geometric cost,
  joint donor-pair bootstrap, funded attribution contrasts, secondary retention,
  one-cap sensitivity, per-cell/pair costs and solves, arithmetic deployment
  costs (hybrids pay both acquisitions), resolution pricing and dynamics plots.
- Full-cap development calibration ran 96 searches at ten workers on both
  families plus 16 exact native replays. It admitted both full scoring entries;
  measured numbers are in `smoke_measurements.json`. These searches are solely
  feasibility/validation, not new confirmation rows.
- Preparation freezes all 4,608 jobs, calibration jobs, donor permutation,
  artifacts and code before search. Each scoring stage reloads the preparation,
  validates its hash/freeze, validates calibration rows and recomputes both cost
  admissions. Failed admission produces a feasibility-stop report and no new
  target search. TS reporting checks the DG row hash and frozen preparation
  before joining both rosters. A scoring exception/timeout preserves partial
  JSONL/progress but never emits a complete comparison result.
- Queue is three sequential entries: preparation 1,800 seconds, DG 9,000 and
  TS 3,600; 14,400 seconds total. All ids have the required prefix, cwd is the
  task worktree, and generated outputs use RUN_DIR. Full target scoring has
  not been launched by the researcher.

Validation: `RAYON_NUM_THREADS=1 .venv/bin/python -m pytest
 tests/test_component_transfer.py tests/test_family_preference.py -q`:
13 passed. Ruff check passed on the three new Python files. The new tests cover
explicit off-mode equivalence to ordinary learned-table search, enabled empty
fallback, component/hash/init isolation, complete seed/arm grid, paired build
uncertainty without cell pseudoreplication, replacement versus portable activity,
native identity attribution, slow-arm admission refusal and deployment charges.

Critic notes are addressed in plan.md, including deferral of out-of-scope belief
file edits to the steward. Closest-technique citations are reused from the
approved proposal/critique; this turn implements their existing design, rather
than proposing a new mechanism or adding a new literature claim.

Final end-to-end smoke: verified-prepare, verified-DG and verified-TS
all exited zero. Each scoring stage ran 24 reduced-cap development searches;
TS emitted a complete combined 48-row smoke result, with target_performance_scored
false. Report, arithmetic economics, 8192-draw paired bootstrap, 1-cap sensitivity,
row-hash checks and plot generation completed. Combined plot visually inspected.
Queue parsed through scripts.queue_lib.load_queue; all three commands passed
bash syntax validation, ids matched and timeouts summed to 14,400 seconds.
Git worktree is clean; no research/ files were committed on the task branch.
