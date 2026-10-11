The implementation passes the approved semantic, reconstruction, replay and
90-minute runtime gates. Full protected scoring remains queued.

- `smoke-bank/bank.json`: 144/144 candidates admitted; fixed first-four
  development roster includes both probe cells and all three predicate splits;
  six protected cells per split. Exact executable screen through nine tokens
  took 106.7 seconds. All 144 canonical and witness checks passed.
- `smoke-small/smoke.json`: 12 restarted development jobs at 2,048 evaluations
  per attempt; deterministic replay and four ordinary-engine equivalence checks.
- `smoke-stage/reconstruction.json`: all 24 complete 0150 builds reproduced
  exactly from 768 source jobs, retaining four failed source jobs and original
  per-build acquisition/extraction/validation costs. Matched random donors
  regenerated from original control seeds.
- `smoke-stage/replay.json`: eight saved off-path jobs matched in every
  deterministic field.
- `smoke-stage/stage_gate.json`: 288 production-budget development jobs,
  actual eight-attempt wrapper and all builds. Solves R-tree 96/96, R-lib
  96/96, R-size 94/96. Means 80,920 / 16,309 / 75,528 evaluations;
  worker means 6.972 / 1.327 / 6.504 seconds. Sustained wall 153.81 seconds,
  effective concurrency 9.239; protected projection 3,689.15 seconds including
  30% reserve plus 90 seconds, below the 5,400-second gate.
- `smoke-admission/admission_check.json`: real admitted production evidence
  passes the complete score loader. Submission intercepted before any protected
  job; intended count 5,184, actual protected submissions zero.

Tests: 36 distinct tests passed across `tests/test_gate_sum.py`,
`tests/test_tree_library.py`, `tests/test_tree_gp.py`, and
`tests/test_tree_gp_report.py`. The generic 0150 report retains its defaults;
new tests exercise bank semantics/probe exclusion, deficient split refusal,
paired/disjoint schedules, missing grid and changed-seed refusal, original
source reconstruction, runtime gates, decision overlap/reliability precedence,
joint acquisition accounting and unbounded repayment, 18-cell/4-repeat report
and PNG generation, and smoke-preparation refusal before submission. Ruff and
`git diff --check` passed. The shared queue loader accepts both entries;
summed timeouts are 7,800 seconds and shell syntax is valid. All preparation
`expect_outputs` were produced by the full stage smoke.

Commands (from the worktree):

```sh
RAYON_NUM_THREADS=1 .venv/bin/python -m pytest -q tests/test_tree_library.py tests/test_tree_gp.py tests/test_tree_gp_report.py
RAYON_NUM_THREADS=1 .venv/bin/python -m pytest -q tests/test_gate_sum.py
RUN_DIR=/Users/andreas/developer/folding-evolution/research/runs/2026-10-11-0348/smoke-stage RAYON_NUM_THREADS=1 .venv/bin/python -m experiments.chem_tape.gate_sum_run --prepare --workers 10 --deadline-seconds 2400
RUN_DIR=/Users/andreas/developer/folding-evolution/research/runs/2026-10-11-0348/smoke-admission RAYON_NUM_THREADS=1 PYTHONPATH=. .venv/bin/python /Users/andreas/developer/folding-evolution/research/runs/2026-10-11-0348/check_score_admission.py
```

Development measurements are feasibility observations. Their projected solves
are descriptive, not protected-cell reliability evidence. The actual full run
will repeat unchanged preparation and independently validate its admission.

Implementation commit: `1f02bb7` on `research/2026-10-11-0348`. Worktree is
clean; no `research/` files were committed on that branch. Plan, queue and
smoke evidence are stored only in this main-checkout task folder.
