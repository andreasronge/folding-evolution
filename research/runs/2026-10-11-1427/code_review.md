---
verdict: pass
---

Reviewed `git diff 6284a17..f8f4246` (engine extension in `tree_gp_search.py`,
runner `inherited_library_run.py`, pinned-hash change in `tree_hand_run.py`,
`tests/test_inherited_library.py`), proposal.md, critique.md, plan.md,
queue.yaml and the smoke artifacts in `smoke/final-exposure` and
`smoke/final-readout`. I re-ran `tests/test_inherited_library.py` in the
worktree: 8 passed.

## Blocking issues

None.

## What I checked (and found correct)

- **Arm wiring.** L: saved R-all library, carriers draw at 0.5. S: same, bits
  permuted by an independent RNG before every selection (elites included, as
  the freeze states). Z: per-build size-matched random donors from
  `tree_library.controls`, rebuilt and compared in the readout. N:
  `donor_library=None`, so both states use ordinary donors; `validate_exposure`
  rejects any library draw by state 0 or by N.
- **Bit inheritance.** Child bit = recipient (p1) bit, including reverts;
  elites keep their own bits; `next_bits` is aligned with `pop = elites +
  children`. No bit mutation. Bits persist across episodes, programs are
  reinitialised from the episode's program seed only.
- **RNG separation.** The modifier RNG is only used for the S shuffle;
  non-carriers never call `variation.random()` for a library draw, and with
  `bits=None`, p=0.5 the engine consumes the stream exactly as the 1228 engine
  (replay test against commit 60ab766 passes). N with bits present replays the
  ordinary search exactly (tested).
- **Seeds.** Program, assignment and shuffle seeds depend on (build, repeat,
  episode) only, so they pair across arms and differ across builds and
  trajectories (1152 distinct program seeds asserted). Readout seeds depend on
  (build, cell, repeat, attempt) and pair across the five laws. All namespaces
  are checked against 1228 and earlier published seed sets. 63-bit seeds are
  fine for both `default_rng` and `FastRandom` (`random.Random`).
- **Rotation.** `(b + r) % 6` gives each development cell the lead 16 times
  per arm in L/S/Z and 8 in N; each cell appears twice per trajectory. Only
  development cells reach the workers; readout `metas` are development cells
  only, so no protected scoring.
- **First solve.** `continue_after_solve` records the first exact witness and
  continues to the cap; validated against the training labels in
  `validate_exposure`. Pre/post deltas index the trace at the solve generation
  correctly (`first // 256 - 1`).
- **Frozen readout.** Laws 0, 0.125, 0.5·mean f_L(4 trajectories), 0.5·mean
  f_S, 0.5; p=0 takes the historical ordinary path. Eight restarted attempts of
  65,536; failure rows must total 524,288. Bootstrap resamples whole builds with
  paired per-build differences. Thresholds (a)–(c) match the proposal and are
  reported as advisory only; nothing gates the readout on exposure values.
- **Fail-closed stages.** Deadline overrun or any validation failure writes
  `failure.json`, which the readout refuses; the readout also revalidates
  artifact hashes, the method freeze, the seed audit, the size-null
  reconstruction and the probability extraction.
- **Critique disposition.** Notes 1–4 are implemented (full-trajectory timing,
  preserved first hit, size-matched naming with rejection counters by state and
  phase, advisory thresholds, aggregate-law wording). Notes 5–6 concern digest
  and question wording outside the researcher's write scope; plan.md says so.
- **Timing.** Smoke: ~10.3 worker-s per 768-generation trajectory → 336 × 10.3
  ≈ 3,460 worker-s, ~350 s on 10 workers, against a 1,470 s deadline. Readout
  smoke 3.4 worker-s/job → 1,440 × 3.4 ≈ 4,900 worker-s, ~490 s against 1,770 s
  (1228 anchors give 2.1–5.3 s/job). Queue sum 3,300 s ≤ 60 min probe cap; the
  queue runs with the worktree as cwd, as `methods()` requires.

## Minor notes (not blocking)

1. Drift is fast: in the smoke, Z and N carriers were lost within the first
   episode and L fixed. With four trajectories per build the per-build mean
   f_L will often be a multiple of 0.25, so L−S and the L-final law will be
   coarse. The analysis should report fixation/loss counts (already in
   `report.json`) alongside the point contrasts before reading (a)/(b).
2. `pre_solve_delta_mean` pools solved episodes (delta to the solve
   generation) with unsolved ones (whole-episode delta). The analysis should
   split these by `solved` when interpreting pre- vs post-solve movement.
3. The 'post' phase for counters begins with the transition after the solve
   generation; the solve generation's own transition is counted as post.
   Consistent, just worth stating in the analysis.
4. Post-batch validation and reporting run after the batch deadline check; if
   the batch ends within a few seconds of `--seconds`, a complete report can be
   followed by `failure.json`. That is the right direction (fail closed) and
   the projections leave >2× slack.
5. `main()` refuses a RUN_DIR that already holds artifacts, so a retry of a
   failed entry into the same directory errors out rather than overwriting.
   Harmless unless the runner reuses directories.
6. The smoke manifest's `git_commit` is 6284a17 (smoke ran before the commit);
   the full run will record f8f4246.
