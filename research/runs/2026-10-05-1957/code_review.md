---
verdict: fail
---
# Code review: 2026-10-05-1957 shortcut reproduction veto

Reviewed `fc29dcb..8681cb7` (`experiments/chem_tape/evolve_shortcut_veto.py`, the `eligible`
mask in `chem_tape/evolve.py`, tests), plus proposal, critique, plan and queue.

One blocking issue. The veto, pairing, statistics and outcome routing are correct as far as I
can find; the run as queued would nonetheless end as a pilot-only stop with near certainty,
for a reason that has nothing to do with power or the hypothesis.

## Blocking issues

1. **The runtime gate will refuse the main stage whatever the pilot shows.**
   `runtime_design` (`evolve_shortcut_veto.py:431-444`) prices every main run at the full cap,
   at 1.5 × the *largest* seconds-per-candidate seen in any pilot run of that cell. Real runs
   solve at a median of roughly 25–40k of 262,144 evaluations, and the largest
   seconds-per-candidate comes from short runs dominated by full-domain verification, so the
   estimate is about 30× too high.
   - **Measured in this harness:** I ran 8 full-size seeds (P1024, cap 262,144) on the smoke
     master, not pilot or main seeds. Actual cost was 2.7–14.0 worker-seconds per four-cell
     seed (mean 8.4), which puts n = 600 at about 21 min on 4 workers. The gate, given those
     same 8 records and n = 600, estimated **35,587 s against about 9,500 s available** and
     returned `main exceeds remaining deadline`.
   - **Cross-check on 1814's 500 sum>2 runs:** the largest seconds-per-candidate over 50
     seeds gives 137 s (U) and 208 s (R) per priced run, so about 100,000 s for n = 600. Even
     the *median* seconds-per-candidate with every run priced at cap gives about 11,300 s,
     which still fails. With 50 pilot seeds the maximum is larger than with my 8.
   - **Consequence:** root 01's last experiment would be spent on a `pilot-only feasibility
     stop` that the plan itself says is not evidence about G3, while the main stage would
     actually fit in well under an hour.
   - **Fix:** estimate from what the pilot runs actually cost, for example
     1.5 × n × (mean pilot worker-seconds per four-cell seed) ÷ workers, plus one worst-case
     cap run and the 600 s reserve. Pricing every run at cap is not needed for safety:
     deadline truncation is already handled as infrastructure missingness with a nonzero
     exit. Update plan.md's "Runtime gate" paragraph and the runtime-refusal test to match.
     No pilot or main data have been seen, so changing this now costs nothing statistically.

## Checked and found correct

- **Veto wiring.** `eligible = classes != 2` in veto cells only. Both engine paths filter
  elites and the lexicase pool by the mask; the offspring count is taken from the actual
  number of elites, so population size is kept when fewer than two are eligible. An all-true
  mask becomes `None`, so the ordinary RNG path is untouched. A per-generation lineage
  assertion checks no vetoed parent in either role.
- **Detection.** Every training-perfect row is classified on all 10,000 lists, exact sum>2
  first. The A sampler draws positives only where max>2 agrees, so every exact-max>2 program
  is training-perfect. The cache is keyed on full genome bytes.
- **Seeds and pairing.** Pilot, main and smoke use separate masters and offsets; none
  overlaps 1814. Ordinary and veto share training set, evolution seed and initial population
  within a vector and seed. Bootstrap and power streams are separate.
- **Identity check on real trajectories.** The committed smoke had no exposure, so it did not
  exercise divergence. In my 8 full-size seeds, 5 U and 6 R pairs were exposed, all pairs
  passed the pre-exposure digest check, the 5 unexposed pairs had identical endpoints, and
  exposed pairs diverged afterwards. So the veto does act on real runs.
- **Statistics.** Whole four-cell seed rows are resampled with the same indices for all four
  ratios. Censored runs enter as infinity; the lower median matches `km_curve`. Non-estimable
  draws widen the interval instead of being dropped, and a gate needs ≥ 99% finite draws.
  Intervals are 98.75%. `outcome()` follows the registered order exactly.
- **Power procedure.** Injection scales only exposed veto event times, keeps censored runs
  censored, censors at the cap, and stops if the target is unreachable. The three registered
  powers and the joint route probability are computed as planned.
- **Missingness.** Deadline-truncated or identity-failed runs make the stage incomplete: no
  `COMPLETE`, nonzero exit, no contrasts.
- **Critique.** Every point is implemented or stated in plan.md (whole-record resampling,
  censored-median safeguards, frozen injection, no assumed correlation, unexposed pairs
  untouched, joint probability, explicit eligibility filtering, identity invariant,
  interpretation limits). The runtime-fit requirement is implemented, but miscalibrated as
  in issue 1.
- **Tests and queue.** `tests/test_evolve_shortcut_veto.py`: 34 passed. One queue entry,
  10,800 s timeout, 10,500 s internal budget.

## Minor notes (not blocking)

- Power is estimated by resampling 50 pilot records up to n = 600 or 800. The result is
  conditional on those 50 and will be lumpy; read `power.json` with its Monte Carlo intervals
  and the exposure counts, not as a precise number.
- If the R exposure fraction in the pilot is low, the P_R = 1.6 target can be unreachable and
  the run stops as `injection infeasible`. That is as registered, but the analysis should
  report it as a statement about exposure, not about power.
- `cell_summary` counts `exposed_before_solve` and `reproductive_exposure` from each cell's
  own run. In veto cells these describe the veto trajectory; only the ordinary-cell counts
  feed the power mask. Label them accordingly in the analysis.
- In my 8 seeds the veto slowed R in 4 of 6 exposed pairs and sped it up in 2. This is far
  too few to mean anything; it shows only that the effect has either sign per seed.
