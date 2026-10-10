---
verdict: pass
---
# Code review: 0024 restarted tree GP versus restarted and full-cap A8

Reviewed `git diff 604e424..1773d11` (restart_gp_run.py, restart_gp_report.py,
tests/test_restart_gp.py, frozen 2254 data under `data/restart_gp_0024/`),
proposal.md, critique.md, plan.md and queue.yaml. Beyond reading, I ran the
following checks against the worktree and the smoke-queue output:

- Native job tuple index 3 is the seed (`component_transfer_run.envelope`), so
  `with_seed` re-seeds both the search and the `BlockOperator` (which reads
  `meta["seed"]`); the tree tuple index 1 is likewise the seed. Build stays fixed
  across attempts because only `seed` is replaced.
- Freeze, seed audit, preparation hash and stage-0 hash all survive the JSON
  round-trip that `load_preparation` compares against: recomputed values equal
  the real smoke `preparation.json` (only `methods` differs, because
  `restart_gp_report.py` was edited after the smoke run at 604e424; in
  production all three stages run from the same checkout). This path was not
  exercised end to end by the smoke (smoke cannot admit), so this was the main
  untested risk and it holds.
- Real rows from both engines (the 2254 rows produced by the same
  `ordinary.execute`) carry every field the report and plots read (`curve`,
  `phenotype_diversity_curve`, `exact_check_seconds`,
  `compiled_tokens_evaluated`, `primitive_case_work`, `operator`);
  `initialization` is absent on A8 rows and is accessed with `.get`.
- `acquisition(saved, owner, b)` works for owner `"T"` as well as `"D"` (the
  test suite only covers `"D"`).
- Neither frozen engine has a wall-clock budget; `budget_seconds` is a
  measurement, so attempt-level determinism (pool worker versus main process)
  holds, as the smoke's equivalence and replay checks also showed.
- `run_queue.py` fixes the date folder once at queue start, so the
  `$RUN_DIR/../2026-10-11-0024-prepare` sibling path cannot break on a midnight
  crossing. `--validate` passes: three entries, 1800/5400/1800 s, 2.5 h summed.
- Seed formulas: within a cell the restarted offsets span 0..767 (< 1000), the
  F-A8, stage-0, validation and semantic bases are disjoint ranges, and the
  audit's computed overlaps with every historical set are empty (test passes).

Arm wiring, pairing, metrics and the decision rule match the proposal: R is the
ratio of arithmetic means with equal cell weight and failures charged the full
total cap (enforced by `validate_rows`), the paired 24-build bootstrap resamples
the same build draws for numerator and denominator, the reliability guard is the
lower paired bound of the solve-fraction difference above −0.03, TS is
summarised per family and never pooled, and the historical tree rows are
labelled as an unpaired 2254 reference.

Critique: notes 1–5 are addressed in plan.md (corrected counts, stage-0 and
validation seeds in the audit, build-heterogeneity sensitivity implemented and
the power claim qualified, noninferiority wording, both cost units, bounded
exit). Notes 6–9 concern digest/question wording outside the task folder and are
explicitly deferred to the steward; acceptable.

## Blocking issues

None.

## Minor notes

1. **Stage-0 projection is optimistic, not pessimistic.** It uses restart means
   from source/development cells, which solve faster than targets. It therefore
   cannot refuse the main stage for the wrong reason, but it is also a weak
   guard against DG overrunning. Worst case with zero restart benefit (per-job
   cost equal to 2254 full-cap means: tree 28.2 s, A8 11.8 s) is about 65 min
   at concurrency 9.1 against the 89.5 min internal deadline; at concurrency 7
   it approaches the limit. Expected wall is about 32 min. Run on an otherwise
   idle machine.
2. **Preparation's serial re-executions are not deadline-checked.** `validate()`
   re-runs each of the 8 validation jobs twice in the main process (first
   attempt, then the whole job). Worst case about 7.5 min if every attempt fails
   at the production cutoff; total preparation worst case about 20 min against
   the 29.5 min deadline. Fine, but note it if preparation times out.
3. **TS is coupled to DG completion.** The TS stage refuses to run without a
   complete, hash-matching DG result, so a DG timeout forfeits the descriptive
   TS data as well. Deliberate per plan.md; just be aware when reading a partial
   outcome.
4. **The real-row report path runs for the first time at the DG stage.** Tests
   use a synthetic grid. Field coverage is verified above, so the remaining risk
   is low; the report writes `result.json` and `report.md` before plotting, so a
   plot failure would still leave the numbers.
5. **Power is uncertain, as plan.md now says.** The build-pooled sensitivity
   gives about 59% joint resolution versus 99.6% for cell pooling.
   `unresolved_cost` is a realistic outcome and is pre-registered as
   INCONCLUSIVE with a resolution price, not a follow-up.
6. For the analysis: `classify` distinguishes `unresolved` from
   `demonstrated_inferiority_beyond_margin` on the reliability guard; report
   that distinction explicitly, per critique note 3.
