---
verdict: pass
---

# Code review: 2026-10-11-1628 helper-arrangement intervention

Reviewed `git diff 7ce5911..46e05cb` in the task worktree (three new files:
`experiments/chem_tape/order_helper_arrangement.py`, `experiments/chem_tape/order_helper_run.py`,
`tests/test_order_helper_arrangement.py`; engine, extractor and 1530 wrapper untouched), plus
proposal.md, critique.md, plan.md, queue.yaml and the smoke outputs under
`experiments/output/2026-10-11/2026-10-11-1628-{initial-,}smoke-{prepare,score}/`.

## Blocking issues

None.

## What I checked

1. **Arm wiring.** `envelopes()` passes no donors for R-tree, the unchanged `semantic_all` prefixes
   for R-all (same as 1530's R-all), and `constructions[repeat % 4]` for R-hx. The realization index
   is part of the frozen schedule and is re-validated row by row (`validate_partial` compares every
   meta key). Test `test_grid_pairing_realizations_and_protected_exclusion` covers this and the
   protected-cell exclusion.
2. **Replacement law matches the proposal.** `replace()` calls the existing `tree_permutation.permute`
   on a single entry, so pools are (arity, token-width) within that entry; the first draw whose
   complete subtree census (including the root) matches no helper on D625 is accepted; failure after
   256 draws raises. `build()` re-checks per-entry `signature`, byte-identity of every non-helper slot,
   and absence of any helper-valued subtree on every slot of every construction. Duplicate slots are
   drawn independently (tested). All 96 constructions in the smoke are distinct, 177/177 helper entries
   replaced, max 16 draws, 613/708 replacements projection-valued, matching the planning audit.
3. **Seeds.** Search seeds come from a new `1628-search` namespace keyed by (build, cell, repeat,
   attempt) and are shared by all three arms for a given unit (seed-paired as proposed); the smoke
   grid uses a separate `1628-smoke-search` namespace, so smoke evidence cannot enter the primary
   estimate. Construction and bootstrap seeds are separate namespaces. `seed_audit` checks all
   groups against each other and against the 1129/1228/1427/1530 historical sets (311,595 values).
   `validate_partial` additionally requires identical initial-population hashes and training indices
   across arms per unit, which the smoke passed, confirming donors do not touch initialization.
4. **Primary metric.** Q is the ratio of pooled capped arithmetic means (equal cell×repeat counts per
   build, so the per-build block means give the same pooled ratio), with an 8,192-draw bootstrap that
   resamples whole builds and applies the same build indices to numerator and denominator. Matches the
   registered comparison; checked by `test_pooled_whole_build_bootstrap_and_no_partial_verdict`.
   `classify()` thresholds match plan.md at the boundaries (tested, including 1.25 and 0.80 exactly).
5. **Completeness.** `summarize()` returns `incomplete_no_efficacy_verdict` with no contrasts unless all
   3,456 rows are present; duplicates or unknown keys raise. Rows are fsynced per job. There is no
   balanced-partial fallback, as plan.md states.
6. **Gates and stop rules.** Two gates decide whether scoring runs: (a) a deterministic static gate
   (24 libraries reconstructed, 177 helper entries, all invariants) that reproduced identically in both
   smoke runs; (b) a runtime projection gate that aborts preparation if the projected full scoring time
   exceeds 3,300 s. The projection comes from build 0 alone. From 1228's rows, build 0's summed per-arm
   worker time is 11.7 s against a 24-build mean of 13.8 s and a maximum of 19.6 s; scaling the smoke's
   1,341 s projection by the worst build gives about 2,240 s, still under the gate, and the expected
   full run is about 1,600 s against a 3,510 s batch deadline. The gate therefore has low risk of
   stopping the main stage for the wrong reason, and a wrong stop would be visible (failure.json with
   the number) rather than silent.
7. **Provenance.** `SOURCE_PREPARATION_HASH` equals the 1530 preparation hash on disk; `load_source`
   re-verifies all 1530 artifacts and reconstructs the 1228 libraries through `archive.load_saved`;
   `previous.freeze` pins the engine/extractor hashes. `load_prepared` recomputes every frozen artifact
   and compares it to the files written by prepare (tampering test passes).
8. **Queue.** `run_queue.py --validate` passes: two sequential entries, 600 + 3,600 s = 70 min, well
   under `max_queue_hours = 8`. The driver runs the queue with the worktree as cwd and the main repo's
   `experiments/output` as output root, so `$RUN_DIR/../2026-10-11-1628-prepare` resolves to the
   prepare entry's directory (same pattern 1530 used). The worktree's `.venv` imports
   `_folding_rust` and the new module from the worktree. All expected outputs are written in both the
   complete and the incomplete paths.
9. **Tests.** 32 passed in `test_order_helper_arrangement.py`, `test_tree_permutation.py`,
   `test_order_protected.py` in the worktree venv.
10. **Critique.** Notes 1–4 are incorporated in plan.md (explicit 1228 counts and the "R-S is
    pessimistic, not a bound" caveat; frozen construction details with independent seed namespaces;
    narrowed retention/loss wording; precedent). Notes 5–7 concern digest and question wording outside
    the researcher's folder; plan.md says so and defers them to the steward. That is an adequate answer
    for a code review, but the steward should act on them at decision time.

## Minor notes (not blocking)

- **Rediscovery census lacks a baseline.** `summarize()` censuses helper-valued subtrees only in R-hx
  solvers, and the smoke shows 24/24. Because the development cells' targets are themselves built from
  min/max, solvers in every arm will probably contain helper-valued subtrees, so this number cannot
  separate "search reconstructed the helper" from "any solver must contain it". The analysis should
  compute the same census for R-all and R-tree solvers from the stored `solver_tree` fields (post hoc,
  no rerun needed) before reading the R-hx fraction as rediscovery.
- **Smoke stratum Q's are from one build** (stratum 2: Q ≈ 2.6 on 8 units; stratum 0: 0.57 on 4 units)
  and must not be quoted as evidence; the full-run strata are descriptive only, as plan.md says.
- **Re-run after a crash.** `main()` refuses a `RUN_DIR` that already contains `source/` or
  `method_freeze.json`. If the driver re-runs an interrupted entry into the same directory, the entry
  will fail immediately; the directory must be cleared first. Same behaviour as 1530.
- `preparation.json` records the git commit of the smoke runs (7ce5911, pre-commit); the queue run will
  record 46e05cb. The score phase does not compare commits, only artifact hashes, which is sufficient.
