---
verdict: pass
---
# Code review: 2026-10-09-0306 position-matched Q/P rerun (re-review after fix)

Re-review of commit `2bab2c2` (worktree HEAD, clean) against the previous
`verdict: fail` review of `0faced8`. Reviewed `git diff a4aabfa..2bab2c2` with
emphasis on `git diff 0faced8..2bab2c2` (the fix), plus `proposal.md`,
`critique.md`, `plan.md`, `queue.yaml`, `implementation.md` and the
`smoke-review/` outputs. Checks run in the worktree:

- `pytest -q tests/test_position_matched.py tests/test_frequency_matched.py`: 18 passed in 63 s.
- `scripts/run_queue.py --validate` on the task's `queue.yaml`: OK, 2 pending sequential entries, 1 800 + 11 700 s.
- `smoke-review/preparation.json`: `admitted: true`; expected 9 061 s and all-capped bound 9 511 s against 11 700 s (margins 22.6 % and 18.7 %); preparation wall 197 s against 1 800 s. Both prices recompute exactly from the recorded sample, batch, capped and fit fields. The published diagnostic price (10 912.5 s) is unchanged in definition.
- `smoke-review` implementation hashes for the three `position_matched*.py` files equal SHA-256 of the committed files, and `config.json` records `git_commit 2bab2c2`, `task 2026-10-09-0306`, so the queue's preparation entry will reproduce these hashes and the scoring entry will accept it.
- 32/32 C/T and 16/16 K replays bit-exact, Q/P timing rows deterministic (9/16, 6/16 solves, identical to both earlier runs).

## Blocking

None.

The single blocking issue from the previous review is fixed. `runtime_admission()`
in `position_matched_run.py` now implements exactly the required predicate:
`elapsed <= 1800 and expected < 11700 and bound < 11700`, with
`expected = 1.15 × max(sample, batch) + fit + 120` and
`bound = all-capped (with tail) + fit + 120`. The all-capped zero-solve worst case
is kept as a hard refusal, the 15 % multiplier applies only to the realistic
projection, and the margin (about 2 200–2 600 s) is roughly ten times the 1.9 %
run-to-run drift observed between the two earlier smokes, so a few percent of
background load during the queue's timing searches cannot stop the cycle. The
rule is recorded in `preparation.json` as `admission_rule` (versioned, with the
formulas) alongside the retained `safety_multiplier` and diagnostic price. The new
tests cover 1.9 % and 6 % drift (the latter would have flipped the old predicate),
independent refusal by each of the three conditions, and the inclusive/strict
boundaries. `plan.md` and the queue notes state the predicate change explicitly,
replacing the earlier "no reduced safety factor" wording.

Science path: `git diff 37c78c1 2bab2c2 -- . ':!research'` touches only the
admission function, the task label, the timeout constants and the data README. Arms,
schedules, pairing, decoders, projections, metric, provenance and hash refusals are
as verified in the previous review and unchanged.

Critique: notes 1–4 are reflected in plan.md (preparation solves stated as
observations only, joint Q/P reading, limits, no top-up). Notes 5–6 concern
question/digest wording; plan.md says they are deferred to the steward, which is
acceptable since they do not affect this design.

## Minor

- `preparation.json` still carries `safety_multiplier: 1.15`; with `admission_rule`
  present this is unambiguous, but the analysis should quote `admission_rule.version`
  rather than `safety_multiplier` when stating which rule admitted the run.
- The scoring command's `${RUN_DIR%/*}` sibling path assumes both entries run in one
  `run_queue.py` invocation on the same calendar day (as before). Fine for this
  sequential queue; a cross-day resume would need the path edited.
- The data folder name `position_matched_0239` is retained by design (frozen
  paths); the analysis should identify this cycle by run folder and commit `2bab2c2`.
