---
estimated_minutes: 30
---

# Approved helper-arrangement intervention

Implement proposal 1628 without acquiring or fitting new libraries. Use the 24 saved 1228 R-all libraries reconstructed from 1530 evidence, verify recorded file and semantic hashes, and score only the six development cells in the frozen x4-order-v1 bank. Protected cells remain unscored. Preparation and validation precede all scoring.

## Conditions and seeds

- R-all: original ordered uncapped donor slots, unchanged.
- R-hx: replace only entries whose whole-tree D625 output matches one of the twelve pairwise min/max helpers. Independently shuffle labels within each entry's (arity, compiled token-width) pools; take the first draw for which no subtree matches any helper on D625. Limit: 256 draws per entry per realization; failure aborts construction, with no dropped entries or relaxed matching. Four realizations per build, assigned to repeat modulo four. Preserve every slot, duplicates, primitive counts, skeleton, nodes, compiled length and uniform draw probabilities; do not re-deduplicate by semantics. Non-helper entries remain byte-identical.
- R-tree: no donor library. All arms use the existing restarted tree-GP wrapper, half library mutation donors where applicable, up to eight attempts of 65,536 evaluations.
- Full size: 24 builds × six development cells × eight repeats × three arms = 3,456 jobs, 1,152 per arm. Experimental unit: build × cell × repeat; pair search seeds across all three arms.
- Use deterministic hash-derived seeds in new, separate `1628-construction`, `1628-search`, and `1628-bootstrap` namespaces. Construction keys include build, realization and slot; search keys include build, cell and repeat. Log all seeds and audit them against saved acquisition and scoring seeds. Never choose a realization by performance.

## Validation and measurements

Before any search, reconstruct all saved R-all libraries from the immutable acquisition rows, check saved hashes and the complete source grid, and validate original and replacement entries by independent interpreter versus VM on D625. Census every subtree, including roots, for all twelve helpers; validate unchanged non-helper entries and all material/shape/length invariants. Record accepted draw counts, per-slot semantic hashes, projection outputs, duplicate slots, and four realization hashes. Freeze bank, method, libraries and seed schedules to disk and hash-check them before scoring.

Smoke-test a small balanced grid at unchanged search caps after static validation; measure worker and wall time, solves, capped evaluation costs and output completeness. Add focused construction and completeness tests. Smoke evidence is feasibility evidence only and never enters the primary estimate. Write smoke outputs beneath an explicit RUN_DIR, record their location here, and do not run the full queue during implementation.

Full scoring records every attempt, solver tree, evaluations, solve status and worker seconds. Report pooled capped arithmetic means, solves per arm, Q = R-hx/R-all and R-hx/R-tree with 95% paired whole-build bootstrap intervals (resample all realizations, cells and repeats with each build). Report descriptive Q by saved needed-helper coverage stratum, and the share of solved R-hx jobs whose solver contains any helper-valued subtree (rediscovery). Write fitness/evaluation-cost and node/compiled-length visualizations appropriate to this tree-GP harness. No new inferential coverage comparisons.

## Feasibility and stopping

Prior 1228 solves: R-all 576/576, R-tree 574/576, R-S 572/576; worker seconds per job 2.14, 5.31, 6.39 respectively. Planning audit supported 177/177 helper entries in 465 draws, maximum 16. Using R-S as a pessimistic R-hx scenario gives about 15,944 worker seconds, or 27.4 minutes at 9.7 effective workers; it is not a worst-case bound. Expect about 22–30 queue minutes. Allocate 600 seconds preparation plus 3,600 seconds scoring (70 minutes summed timeouts; below the proposal's 90-minute ceiling). Reserve time inside each entry for complete/incomplete reporting.

Construction failure, unreachable required validation, or smoke runtime far beyond the approved assumptions triggers infeasible.md with measured numbers and a suggested redesign, then stop and commit. Queue timeout or missing jobs makes the experiment incomplete: no verdict from fastest-finished jobs, no partial balanced fallback, no automatic top-up. All 3,456 jobs are required for the primary decision.

The same-library split check in the proposal estimates search noise only. Twenty-four independent build clusters retain between-build uncertainty in the intervention effect; do not promise an upper interval near 1.15–1.20.

## What outcomes mean

- Lower(Q) > 1.25: material loss. Intact helper-valued entries benefit search relative to this mostly projection-valued, same-material replacement law, conditional on the remaining R-all content and this search regime. This supports preserving the intact entries in a comparable acquisition design. It does not show unique min/max necessity, superiority over other nontrivial computations, or a universal requirement for future acquisition.
- Upper(Q) < 1.25 and upper(R-hx/R-tree) < 0.80: useful retention. Preassembled helper-valued donor entries are unnecessary for this saving at the registered resolution. Search may reconstruct exact helpers; the solver census describes that possibility. Other content or primitive/subtree supply remain competing carriers.
- Otherwise: unresolved, including intervals crossing 1.25 or retained Q without useful performance relative to R-tree. Price a resolving design during later analysis, without running it automatically.

Return to strategy for every outcome. This is a mechanism comparison of external GP donor libraries, not a new learning algorithm or target-directed semantic inversion. No fresh-bank transfer claim follows. A projection-valued replacement is computationally trivial as a whole expression but may supply useful subtrees through variation; do not label it evolutionarily inert.

## Critic notes

Notes 1–4 are incorporated above: explicit counts and runtime caveat, closed construction/completion gates, independent seed namespaces, fixed four realizations, narrower interpretation, and correct precedent. Notes 5–7 concern digest/question wording outside the researcher's authorized task folder. They are deferred to the steward: report observed failure counts rather than population-level zero loss, keep non-helper carriers unidentified, and scope capped-library evidence to development cells. No changes to questions, digest or briefs are made here.

## Implementation and smoke evidence

Implemented in `experiments/chem_tape/order_helper_arrangement.py` and `order_helper_run.py`; the existing tree-GP engine and donor law are unchanged. The construction wrapper calls `tree_permutation.permute` with a single entry at a time, validates each unique subtree by scalar interpreter against VM on D625, and accepts only the first helper-free draw. The scorer replays reconstruction and all four constructions, compares all frozen artifacts and method hashes, checks attempt accounting and common initialization/training cases, and requires the complete fixed grid before emitting contrasts or a decision.

Final smoke outputs (raw data outside the notebook):

- [Preparation and construction audit](../../../experiments/output/2026-10-11/2026-10-11-1628-smoke-prepare/preparation.json), [per-construction audit](../../../experiments/output/2026-10-11/2026-10-11-1628-smoke-prepare/construction_audit.json), and [smoke report](../../../experiments/output/2026-10-11/2026-10-11-1628-smoke-prepare/smoke_report.json).
- [Scoring replay report](../../../experiments/output/2026-10-11/2026-10-11-1628-smoke-score/report.json) and [dynamics plot](../../../experiments/output/2026-10-11/2026-10-11-1628-smoke-score/dynamics.png).

The static phase took 8.92 seconds; preparation including smoke and plotting took 37.23 seconds. All 177 original helper entries were replaced in all four realizations: 96 constructions, 708 replacement slots, 1,762 total draws, maximum 16 draws, and 635 unique subtree interpreter/VM checks. All construction invariants passed. Of 708 replacements, 613 were projection-valued; their potential evolutionary subtree supply remains part of the interpretation.

Smoke grid: one build × six development cells × four repeats × three arms = 72 jobs, with all four realizations represented. All arms solved 24/24. Mean worker seconds/job: R-tree 4.05, R-all 2.70, R-hx 3.01; 27.93 seconds batch wall time, about 8.39 effective workers. The projection is 1,341 seconds (22.35 minutes) full scoring, comfortably inside the 60-minute scoring timeout; this is a feasibility estimate from one build, not a bound. Eight-repeat full scoring remains unchanged. The separate scoring-path smoke replays all source/construction validation, reproduces seed-paired evaluations, solves and solver programs, and exercises report/plot output. No protected searches and no efficacy verdict were made.

Validation: 32 tests passed in `tests/test_order_helper_arrangement.py`, `test_order_protected.py` and `test_tree_permutation.py`; Ruff passed for all three added files. Tests cover per-entry matching, duplicate slots, unchanged non-helpers, rejection exhaustion, embedded-helper and hash gates, protected-cell exclusion, four-realization assignment, search pairing, pooled whole-build bootstrap, threshold boundaries, incomplete-grid refusal and frozen-artifact tampering. Python and the Rust extension both import from this worktree's own source/venv. Rust source was unchanged.

An earlier broader check also ran `tests/test_order_cap.py`: 38 passed and two legacy tests failed (`test_frozen_bank_schedules_seed_audit_and_protected_guard`, `test_preparation_roundtrip_and_tampering_fail_closed`). Both reject the pre-existing tree-GP extension against the older 1129 pilot hash `bf953038…`. The current file and branch HEAD both hash to `61598ff0…`, exactly the approved extension pinned by the 1530 wrapper reused here. This task does not modify that engine or relax the old historical tests. The actual 1628 preparation and scoring method gates passed.

`queue.yaml` parses with `scripts/queue_lib.load_queue`: two sequential entries, correct task-prefixed IDs, 600 + 3,600 = 4,200 seconds (70 minutes) summed timeouts. The driver runs commands with this reviewed worktree as cwd; each phase writes beneath its exported RUN_DIR. Full scoring has not been run.

Implementation committed on `research/2026-10-11-1628` as `46e05cb`. Smoke evidence was generated before this commit and is anchored by the source hashes in its method freeze; the committed source matches those hashes. No research notebook files were committed on the task branch.
