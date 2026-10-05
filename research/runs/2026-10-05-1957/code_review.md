---
verdict: pass
---
# Code review (second pass): 2026-10-05-1957 shortcut reproduction veto

Reviewed `fc29dcb..2a002a8` (`experiments/chem_tape/evolve_shortcut_veto.py`, the `eligible`
mask in `chem_tape/evolve.py`, tests), plus proposal, critique, plan and queue. The first pass
failed on one issue, the runtime gate. That is fixed, and I found no new blocking issue.

## Blocking issues

None.

## The earlier blocking issue is resolved

`runtime_design` now estimates the main stage as 1.5 × n × mean pilot worker-seconds per
four-cell seed ÷ workers, plus one worst-case cap run and the 600 s analysis reserve. plan.md's
"Runtime gate" paragraph, the queue notes and a new regression test match the code.

I checked it on 16 full-size seeds (P1024, cap 262,144, 4 workers) drawn from the smoke
master, so no pilot or main seed was touched:

| | n = 600 | n = 800 |
|---|---|---|
| Mean cost per four-cell seed | 9.2 worker-s | 9.2 worker-s |
| Estimated main stage | 2,072 s | 2,763 s |
| Cap-run reserve | 133 s | 133 s |
| Total with 600 s reserve | 2,806 s | 3,496 s |
| Gate (about 9,500 s available) | admits | admits |

- **Actual cost:** the 16 seeds took 41 s of wall time, so the estimate's 1.5× margin is real
  headroom, not a tight fit.
- **Other stages:** the power simulation ran at about 0.08 s per trial at n = 600, so about a
  minute for 300 trials at both sizes. A 100,000-draw bootstrap at n = 800 took 2.5 s.
- **Tests:** `tests/test_evolve_shortcut_veto.py` has 35 passing.

## Re-checked on this commit

- **Veto wiring.** Both engine paths filter elites and the lexicase pool by the mask. The
  offspring count follows the actual number of elites. An all-true mask becomes `None`, so
  ordinary cells keep the unmodified RNG path. With `crossover_mate="selected"` the mate comes
  from the same filtered draw.
- **Identity on real trajectories.** All 32 pairs in my 16 seeds passed the pre-exposure digest
  check. 8 of 16 U pairs and 12 of 16 R pairs had a reproductive exposure and diverged after it.
- **Arms and seeds.** U is uniform 1/22 and R is 1814's frozen vector. Pilot, main and smoke
  masters are separate. Ordinary and veto share the training set and evolution seed within a
  vector and seed.
- **Statistics and routing.** Unchanged since the first pass: whole-seed resampling with shared
  indices, censored runs as infinity, 98.75% intervals, and `outcome()` in the registered order.
- **Critique.** Every point is implemented or answered in plan.md, including the runtime-fit
  requirement that was miscalibrated before.
- **Queue.** One entry, 10,800 s timeout, 10,500 s internal budget, outputs under `RUN_DIR`.

## Minor notes (not blocking)

- **The C1 gate may fail.** In my 16 seeds the U-ord median was about 23,700 evaluations and
  R-ord about 25,900. 1814 had 39,481 and 24,484 on natural sets. Sixteen seeds are far too few
  to conclude anything, but uniform may be faster on shortcut-admitting sets. That is a
  registered outcome ("gate failed"), and the analysis should be ready for it.
- **Joint route power can be near zero.** The power alternative injects P_R and P_U but not
  C1, so `complete_route` depends on the pilot's own C1. It was 0 of 20 in my check. It is
  descriptive and does not gate the main stage, as registered.
- **Power is lumpy.** It resamples 50 pilot records up to n = 600 or 800, so it is conditional
  on those 50. Read `power.json` with its Monte Carlo intervals and the exposure counts.
- **Injection can be infeasible.** If the pilot's R exposure fraction is low, P_R = 1.6 is
  unreachable and the run stops as `injection infeasible`. Report that as a statement about
  exposure, not about power.
- **Veto-cell exposure counts.** `cell_summary` counts `exposed_before_solve` and
  `reproductive_exposure` from each cell's own run. Only the ordinary-cell counts feed the
  power mask; label the veto-cell ones accordingly.
