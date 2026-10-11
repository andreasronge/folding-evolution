- 2026-10-11 (steward, 1427): opened by [strategy 1427](../../runs/2026-10-11-1427/strategy.md); probe proposed
  ([proposal](../../runs/2026-10-11-1427/proposal.md)), critic approve_with_notes
  ([critique](../../runs/2026-10-11-1427/critique.md): size-matched null is not an exact robustness control;
  thresholds advisory; aggregate-law readout), [plan](../../runs/2026-10-11-1427/plan.md) took notes 1–4, code
  review pass ([review](../../runs/2026-10-11-1427/code_review.md)).

- 2026-10-11 (steward, 1427): **probe run** (commit `f8f4246`; queue 480 s + 533 s of 3,300 s;
  [analysis](../../runs/2026-10-11-1427/analysis.md), [execution](../../runs/2026-10-11-1427/execution.md)).
  `x4-order-v1` development cells only, 24 saved 1228 R-all libraries, P 256, lexicase, crossover 0.5; a per-program
  bit (recipient-inherited, no bit mutation, f₀ = 0.25) switches mutation donors to R-all. Arms L linked, S bits
  shuffled before each selection, Z linked bits with size-matched random donors, N neutral. Grids complete
  (336/336 trajectories, 1,440/1,440 readout jobs), no protected cells scored, no bookkeeping alarm. Observations:
  - **Absorption is fast.** Every trajectory ended fixed or lost; 328/336 by the end of episode 0, median absorbing
    generation 12 (L) to 18 (S), latest 136. Episodes 2–12 measured nothing about the bit.
  - **Fixation:** L 46/96 (0.48), S 27/96 (0.28), Z 29/96 (0.30), N 16/48 (0.33). Library-level bootstrap:
    L − S **0.20 [0.04, 0.35]**, L − Z **0.18 [0.05, 0.30]**; S, Z and N all compatible with the neutral 0.25.
    Per build L > S in 14/24, tie 4, L < S 6.
  - **Per-generation selection differential** (selected-parent minus census carrier share, pre-solve polymorphic
    generations): L +0.016 [0.009, 0.023] (library bootstrap; relative carrier advantage ≈ 4%), S, Z, N within
    ±0.005 of zero. L's rise sits in the pre-solve phase of episodes that go on to solve.
  - **Revert confound present and matched:** pre-solve library-draw rejection L 0.39, S 0.40, Z 0.42 against
    ordinary 0.30–0.32; Z still fixed at the neutral rate, so extra clones alone did not raise the bit here (Z
    content is not neutral, so content versus robustness is not fully separated).
  - **Frozen readout** (capped mean evaluations, library bootstrap): initial / R-all 1.33 [1.03, 1.72];
    **L-final / initial 0.91 [0.71, 1.20], unresolved**; L-final / R-all 1.21 [0.98, 1.46]; L-final / S-final 0.70
    [0.57, 0.82], which the convex dose curve (cost by probability 0: 74 k, 0.125: 45 k, 0.25: 37 k, 0.5: 32 k)
    explains as S losing the bit in more builds, not as separate usefulness evidence. Ceiling if every L trajectory
    fixed: about 0.73× of initial.
  - Steward read-only checks on the saved rows (descriptive, no interval): (i) in episode 0, where selection
    acted, L and S solved equally often within 64 generations (55/96 each; discordant pairs 20 vs 20); Z 34/96,
    N 15/48. Linkage moved the bit without a visible within-run solve gain. (ii) Deploying one evolved population's
    law (0 or 0.5, at L's fixation rate 0.48) would cost about 0.48 × 32 k + 0.52 × 74 k ≈ 54 k on the pooled dose
    curve, about 1.2× the initial mixture: under drift-dominated absorption, selection turns the starting mixture
    into a lottery that the convex dose curve punishes.
  Against the explanations (observations only): A gets its selection half (L above S and Z, about 4% relative
  carrier advantage) but not its usefulness half; B in its strong form (no carrier advantage) is not supported, but in its weak form (an advantage
  too small to fix the bit reliably against drift) it fits; C (drift) dominates the outcome: the bit is decided in about 15 generations and fixed in only half the L runs;
  D and E are both live: the readout cannot separate them, and the dose curve leaves little headroom above
  f₀ = 0.25 (headroom against R-all was present at the point, interval to 1.03). All three advisory thresholds
  held; the usefulness inspection the plan required is unresolved.

  Decision: park 55 because the probe answered what this procedure can answer cheaply: program selection gave the
  R-all carriers a small, resolved advantage over shuffled and size-matched controls (observation), but drift
  absorbed the bit within about 15 generations, so the extracted law's usefulness over the starting mixture is
  unresolved with a ceiling of about 0.73×, it is not better than fixed R-all, and a single population's law is a
  lottery that the dose curve makes worse in expectation. Confirming the allele movement alone would not change a
  decision (strategy 1427: "more inherited allele movement alone is not a useful answer"), and the 1-experiment
  budget is spent. A usefulness test needs a redesigned instrument (polymorphism kept by bit mutation or weaker
  drift, a starting frequency where the dose curve is steep), which strategy 1427 said is not automatically
  funded. Back to the strategist, as the proposal stated.
