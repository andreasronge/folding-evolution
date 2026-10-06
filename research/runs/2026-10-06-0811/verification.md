# Preparation and verification

Implemented the approved M-start comparison in `experiments/chem_tape/contextual_learning_run.py`, reusing the production composition search and 0132 normalization. Sources are vendored in `data/contextual_0811_sources.json` with original paths and SHA-256 hashes, so the full queue needs no external prior-output files.

[Plan](plan.md) was written before experimental execution. The implementation addresses critique notes 1–5: exact zero-residual reconstruction; actual residual-row calibration and signed effects; R/ablation timings; whole-pair admission with immediate tests; six-start/shared-seed inference and sensitivity; bounded interpretations. Notes 6–11 are for steward updates to evidence files outside this task's write scope.

## Measured feasibility

The approved Stage-0 workload ran on separate verification namespaces (+20,000,000), with no holdout/off-family search or adaptation: 222.2 seconds, 5,016 training searches. The full queue uses its original unused namespaces and repeats Stage 0 before freezing its schedule.

- G training mean log2 capped cost: 13.743 versus 13.84, difference 0.097, within .6; 108/120 solved by 65k.
- Actual R row moves: estimated true-effect SD 0.164 log2, above .15. Approximate diagnostic interval 0.000–0.341. Signed mean child-minus-parent effect +0.199; 25.0% of child means were beneficial. Spread alone does not establish beneficial signal.
- M token moves: true-effect SD 0.170, signed mean +0.259. Approximate subtraction retains shared-parent uncertainty and fixed task strata; these diagnostics are not optimization outcomes.
- Calibration solves: M+ 2258/2304, R 2244/2304. Effective worker-seconds/search: M+ 0.407, R 0.402; approximately 24.7 searches/second across ten workers.
- Representative 524k training timings: M+, mixed R and R_abl each solved 36/36; G 35/36. No score selected these timing maps. Conservative reference allowance 2.513 worker-seconds/search; PA test allowance for each learned map 0.833.
- Sampling extrapolation on all sixteen cells: 123.3 wall-seconds per map per 10^8 genotypes at ten workers; slower than the proposal's 68 seconds but affordable.
- Uncut projection: 379.4 minutes (6.32 hours), including elapsed Stage 0, 10% headroom once and report reserve. It retains twelve pairs, 35 generations, learned off-family tests, and sampling. No design reduction or infeasible declaration is required. The full queue recomputes the timing-only decision on its own Stage 0.

Raw observations and diagnostics: [feasibility/search.jsonl](feasibility/search.jsonl), [feasibility/stage0.json](feasibility/stage0.json), [feasibility/config.json](feasibility/config.json). Calibration-only result is deliberately incomplete and does not classify the study.

## Smoke and checks

The final complete smoke ran in 49.6 seconds at ten workers: 712 searches, including both learning arms, final selection, all frozen references, PA testing, exact residual ablation, off-family tests, and bounded sampling. It completed one reduced pair, 2-seed tests, one generation, and 10,000 samples per map. All 80 PA map/cell coverage checks passed; both arms shared generation/selection seeds; R_abl exactly matched the selected R multiplier vector without residuals. Smoke produces no outcome claim.

Artifacts: [smoke-final/result.json](smoke-final/result.json), [smoke-final/search.jsonl](smoke-final/search.jsonl), [smoke-final/generations.jsonl](smoke-final/generations.jsonl), [smoke-final/curves.png](smoke-final/curves.png). The final completeness helper was also checked directly against these real observations after the completeness guard was tightened.

Validation: 39 tests passed across `test_contextual_learning.py`, `test_map_learning.py`, `test_assembly_family.py`, and `test_composition_bank.py`; Ruff formatting/lint and git whitespace checks pass. Tests cover inherited reconstruction, bounded operators, whole-row changes, clustered/shared-seed bootstrap, priority cuts, gate routing, pairing/reservation, ablation, and missing-seed completeness. Python and the Rust extension load from this worktree/venv. No Rust source changed.

[Queue](queue.yaml) loads with `scripts.queue_lib.load_queue`: one entry with required task prefix and timeout 28,800 seconds, at the eight-hour cap. Internal deadline is 27,600 seconds with a 180-second reporting reserve. Commands run from the worktree and every output is under RUN_DIR. The full queue has not been launched.
