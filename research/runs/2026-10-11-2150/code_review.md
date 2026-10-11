---
verdict: pass
---

# Code review — 2026-10-11-2150 protected signed-chain reuse confirmation

Reviewed commit `83c7c5b` against `92a458f` (driver `signed_chain_run.py`, tests
`tests/test_signed_chain.py`, archived 2044 freeze `method_2044.json.gz`; no engine,
extractor, bank or Rust change), plus proposal.md, critique.md, plan.md, queue.yaml and
smoke.md. Re-ran `tests/test_signed_chain.py` in the worktree (10 passed, 41 s) and
`run_queue.py --validate` on queue.yaml (OK, 2 entries, 12,420 s summed).

## Blocking issues

None.

## What was checked and holds

1. **Arm wiring unchanged.** `envelopes` still gives R-tree no donors, R-all the `semantic`
   entries of saved 1938 library `build`, R-gate the 24 supplied p/n helpers; jobs carry only
   `id` and `labels`. The confirm freeze re-verifies every reviewed source and binary hash
   from 2044 except the driver itself, plus grammar, cutoff, attempts, population, crossover,
   library probability, gates, archive SHA, acquisition identities and donors. Only the
   driver's own diff (this review) is new.
2. **Protected release is explicit and one-directional.** Protected cells are allowed only
   when `confirm=True` and `smoke=False`; a confirm smoke or a development phase hitting a
   protected cell fails closed (tested). A confirmation freeze cannot be consumed by the
   development phase and vice versa (`load_prepared` re-derives the freeze with the phase's
   own `confirm` flag; tested). `--confirm` is rejected on scoring phases; `confirm` phase
   requires `--prepared`.
3. **Seeds.** 18 cells × 24 builds × 4 repeats × 8 attempts = 13,824 seeds, 20461000–20474823
   (arithmetic checked: last = 20461000 + ((17·24+23)·4+3)·8+7). Each unit's tuple is shared
   only across its three arms (`len({tuple(seeds)}) == 1` over the paired triple). The audit's
   historic set now also includes the full 2044 development and 2044 smoke schedules
   (20460000–20460407 lies inside the proposal's "20460000 onward" namespace; the plan's
   move to 20461000 is correct and the collision test proves the audit would catch it).
   Confirm smoke seeds start at 20480000 and are audited as disjoint.
4. **Grid and completeness.** `schedules(confirm=True)` yields 5,184 metas; `validate_rows`
   (order_run → order_protected_run → signed_gate_run) rejects missing or duplicate units,
   schedule disagreement, restart accounting errors, unsolved jobs not at 8 × 65,536, and
   re-executes every claimed solver against the labels. `summarize` on 5,183 rows raises
   (tested).
5. **Primary statistic matches the proposal.** Pooled capped arithmetic mean ratio
   R-all/R-tree on evaluations; `bootstrap_mean` averages the four repeats inside each
   build × cell unit, then resamples builds and cells with the same index draws for all
   arms (paired two-way, repeats kept). Decision rule `upper < 1.00` saving, `lower > 1.00`
   harm, else unresolved; 0.80 bar labelled only. Boundary cases tested (upper exactly 1.00
   is unresolved). Confirmation uses its own bootstrap seed.
6. **Validity flags.** Computed from actual arm job counts (not a hard-coded 288):
   first-attempt ≤ 0.85 passes, caps > 0.25 flags cap-dominated, R-gate solves ≥ 0.95
   required. They are interpretation flags only; nothing stops, resamples or tops up on
   them, so there is no stop-for-the-wrong-reason risk. `validity_checks.json` is written
   separately and is in `expect_outputs`.
7. **Economics.** A = per-build historical acquisition (bootstrapped with the same build
   draws), Delta = C_tree − C_all, totals at N ∈ {0, 1, 10, 100, 1000} with 10 and 100
   pre-stated; repayment A/Delta only for Delta > 0; interval marked unbounded whenever the
   saving interval includes zero (both via the inverted ratio quantile and the saving
   interval). The measured R-all/R-gate and R-gate/R-all contrasts replace the forecast
   "2.6×" wording. Already-owned curve `N·C_all` reported separately.
8. **Admission replay portability.** `admission_identity` compares historical-bank
   references by repository-relative path while still requiring identical old-bank hashes,
   full cell evidence, split and pairwise agreement; a changed agreement count or hash is
   rejected (tested). The frozen manifest and `BANK_HASH` are untouched. The queue runs with
   this worktree as cwd (`research.py` line 463), so the rust-extension and source hashes
   that passed in the smoke preparation apply at run time.
9. **Critique.** Notes 1–5 are addressed in plan.md and in code (full seed-range audit,
   fixed grid, "within the development chain bank" scope string in the freeze and report,
   unresolved/no-top-up wording, 85%/25%/95% definitions, capped costs reported regardless
   of flags, distinct economics symbols, measured supplied-prior gap). Notes 6–9 concern
   digest/question wording outside the researcher's write scope and are deferred to the
   steward with that reason, as in 2044. Acceptable.
10. **Timeouts.** 900 + 11,520 s = 207 min, under the 240-min ceiling; internal deadlines
    30 s inside each entry. Smoke measured 7.58 worker-s/job, central 86 min and doubled-tail
    172 min for scoring; both fit the 11,490 s deadline.

## Minor notes

- **Deadline margin on an unseen tier.** At the measured 7.6 effective concurrency the
  confirm deadline tolerates a pooled mean of about 16.8 worker-s/job, roughly 2.2× the smoke
  mean. At the 25% R-tree cap-dominance threshold the expected mean is around 10–11 s, so a
  cap-dominated but otherwise normal run still fits. Only a pathological tier (most jobs
  capping across all arms at ~30–35 s) would hit `TimeoutError`; `score.jsonl` keeps the
  completed rows (cell-major order, arms innermost, so the loss is whole trailing cells) and
  no `report.json` is written. If that happens, label the analysis `pilot_only`/unresolved
  on the completed cells rather than pooling; heavy capping would itself be the finding.
- **Prepared-directory lookup.** `"$(dirname "$RUN_DIR")/…-prepare"` assumes both entries run
  in one `run_queue` invocation (the date directory is fixed at queue start). Same construct
  as 1938 and 2044.
- **Legacy test failures are pre-existing.** The two `tests/test_signed_gate.py` failures
  reproduce at baseline `92a458f` (`baseline-legacy-tests.log`): 1938's presearch freeze
  compares the entire method inventory and absolute executable path. This run's provenance
  goes through the hash-verified 1938 archive and the archived 2044 freeze instead, both of
  which verify. Not a concern for this experiment.
- **Repayment interval encoding.** `repayment_interval95` uses `None` both for "no finite
  lower bound" (saving upper ≤ 0) and "unbounded upper". The analysis should read
  `repayment_unbounded` and `nonpositive_saving_bootstrap_fraction` alongside the list.
- **Smoke throughput.** The smoke's 3.9 effective concurrency is a 12-job straggler artefact;
  smoke.md correctly uses 2044's full-batch 7.6 for the timing projection.
