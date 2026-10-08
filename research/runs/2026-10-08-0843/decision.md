---
next: proposal
---
# Decision: run 2026-10-08-0843 (root 23, slot 1 corrected) — stopped 68 s over the cost gate

**Continue root 23 and re-propose the same design with the descriptive reference seeds removed.**
Budget unchanged: 2 experiments, 0 used (nothing executed). No belief changed; the digest's
root-23 paragraph was updated to say that a second design stopped, and critique notes 6–9 were fixed.

## What happened

The researcher implemented the equal-exposure design (commit `c01f16d`, on
`research/2026-10-08-0843`, not yet merged to `research/main`). It passed 111 tests and a
four-cell smoke run, and the analysis was rewritten as the critic asked (20 runs per arm, uniform
primary, per-family verdicts, S = inherited/scaffold). Four full-size timing acquisitions then
priced the queue ([infeasible.md](infeasible.md)):

| Roster | Expected queue | Timeout sum | Ceiling |
|---|---:|---:|---:|
| Full (64 reference seeds/target) | 87.5 min | 11 397 s | 10 800 s |
| Approved fallback (32) | 83.1 min | 10 868 s | 10 800 s |

The fallback failed by 68 s (0.6%). The cause is the max acquisition. It took 396–433 s against
the 260 s the proposal assumed, and 236–276 s of that was exact verification of
training-fitting shortcuts before the first witness. Continuing selection after solving changes
the trajectory, so 2243's verifier time was not an upper bound. The researcher correctly applied
the pre-stated stop rule rather than shaving the margin.

Timing observations (n = 1 per cell, no frozen scoring, logged only): first exact solves were
35/48 in sum inherited, 25 in sum broken, 26 in max inherited and 19 in max broken, with mean
lineage depth 5 995–6 132 of 6 144. The max count is higher than 2243's 6–7/48 under early
stopping. With different rules and seeds and one run per cell, this does not show that the
max under-exposure problem is solved.

## Why re-propose rather than return to strategy

[Strategy 0843](strategy.md) asks for review "immediately after the first result, a
feasibility-only outcome, or another build/cost obstacle". This is literally a cost obstacle, so I
am departing from that instruction on purpose. The critic can send the proposal back if it disagrees.

- **Nothing the strategist decided has changed.** The design, primary contrast, controls and
  decision rules stay the same. The expected queue rises from about 74 to about 81 minutes, which
  is still inside the strategy's ≤ 3 h queue / 5–7 h total envelope. A strategy pass would
  have nothing to decide about root 23 that the result will not decide better.
- **The fix costs no information.** Every contrast already used only the 16 shared seeds. The
  extra reference seeds were described as descriptive in the plan, and infeasible.md lists
  dropping them as an option. Removing them prices the queue at about 10 600 s (linear in the
  measured per-search cost: max scoring −117 s, sum −15 s, each doubled). If the exact
  repricing still exceeds 10 800 s, the 1558 fit is also dropped (descriptive only, ≈ −90 s).
- **The strategist reviews right after this result anyway.** Another pass now would add an
  agent cycle without a decision to make. A third cost or build stop on this design goes to
  the strategist (now written into the question's allocation).

I rejected raising the ceiling to 190 min. It would also work, but it moves a pre-stated gate
after seeing the price, whereas removing descriptive seeds changes nothing that is inferred.

## Tree and digest

- Root 23: log entry appended (with a correction to 2243's "cost itself is not the obstacle",
  critique note 9). The question summary and allocation were updated. Status open.
- Digest: notes 6–8 fixed. The withheld-cell family advantage is now "not resolved" rather than
  absent. The selection-based context claim is now "not demonstrated" rather than "did not
  reach". The INPUT/GT and scaffold comparisons are stated as within their registered margins,
  not as equality. The root-23 paragraph was rewritten. No belief was added or removed.
- Parked questions re-checked: 02, 04, 07, 08 and 09 under root 01. Nothing new was observed
  scientifically, so no reopen condition is met. 09(b), "a heritable-bias design needs to know
  whether INPUT/GT supply alone is what evolution uses", is not triggered: this design compares
  against the hand scaffold directly and does not depend on that answer.
