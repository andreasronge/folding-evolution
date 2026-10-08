---
node: questions/23-heritable-variation-bias
title: Inherited token frequencies at equal exposure — approved 0843 design, contrast seeds only (slot 1, re-admitted)
bank: tag-threshold-v1   # sum/max > 1, 5 on length-4 lists over 0..9; threshold 2 untouched (development bank)
---
**What this is.** The approved [0843 proposal](../2026-10-08-0843/proposal.md)
([plan](../2026-10-08-0843/plan.md)) with one roster change, because the queue missed the 3 h
timeout ceiling by 68 s ([infeasible](../2026-10-08-0843/infeasible.md)). Question: at equal
exposure, does a token-frequency vector inherited with each program become useful through
program selection, and stay useful frozen on fresh populations? Why this skips a strategy pass is in
[decision 0843](../2026-10-08-0843/decision.md). The strategist reviews immediately after this
result.

**Closest technique.** Self-adaptation by per-individual inheritance
([Stephens et al. 1998](https://pubmed.ncbi.nlm.nih.gov/9847423/),
[Angeline 1996](https://doi.org/10.7551/mitpress/1109.003.0009)). The parameters are selected
only through their carriers, and they may come to protect resident fitness rather than help search
([Glickman & Sycara 2000](https://www.ri.cmu.edu/pub_files/pub2/glickman_matthew_2000_1/glickman_matthew_2000_1.pdf);
explanation D). New here (a mechanism test): an inherited token distribution scored frozen on fresh
populations against uniform, broken-ancestry and hand-scaffold controls.

**Design (unchanged unless marked).**
- **Code.** `c01f16d` on `research/2026-10-08-0843`, which is not on `research/main`.
  Merge it; re-run tests and smoke only as a post-merge check.
- **Acquisition.** 48 episodes alternating thresholds 1 and 5, P 1024, exactly 128 generations
  each (6 144 per run). The first solve is recorded, verification is skipped after it, and
  selection continues. Master seed `202610080843`. The four timing vectors stay excluded.
- **Arms and unit.** Inherited and broken (θ shuffled after every census), sum and max; one
  acquisition run is the unit, 20 per family × arm (80). Acquisition is never cut.
- **Frozen scoring.** Each learned vector gets shared seed indices 0–15 on its family's two
  training targets, 2 560 searches with a cap of 262 144.
- **Changed: references.** Uniform, scaffold and the 1558 fit get **only indices 0–15** on all
  four targets (192 searches, down from 768). Contrasts already used only these 16 shared
  seeds, so no comparison changes. If exact repricing still exceeds 10 800 s, drop the 1558 fit
  (descriptive only). If it still exceeds 10 800 s, stop and go to strategy.
- **Queue entries.** Acquisition, sum scoring, max scoring and analysis run as separate entries.

**Feasibility and cost** (measured in [0843 timing](../2026-10-08-0843/cost/projection.json)).
- Acquisition: 175–181 s per sum run and 396–433 s per max run. That is 46 min on 10 workers,
  including a final-worker allowance, with a timeout of 5 824 s.
- Scoring from 2243 timing means: sum ≈ 9.7 min, max ≈ 25 min.
- Expected queue ≈ **81 min**, and the timeout sum is ≈ **10 600 s** against the 10 800 s ceiling
  (linear extrapolation from the two priced rosters; the researcher reprices exactly).
- Agent time ≈ 2 h: a short preparation (merge, reprice, queue), then review and analysis.
- **Full cost ≈ 5 h**, inside the strategy's 5–7 h for this slot. The max verifier tail is the
  main runtime risk. Each timeout allows about 2× its mean estimate.

**Primary comparison** (per family, never pooled): **R_u = uniform cost ÷ inherited cost**.
- **Score.** Geometric-mean evaluations to the first exact solve over both training targets.
  Censored searches count at the cap, and solve counts are reported.
- **Interval.** 95% crossed bootstrap over acquisition runs and shared seed indices, as planned.
- **Precision.** ×/÷1.33–1.48 if the between-run SD is 0.5–0.8 log (assumed; measured here).

| Outcome | Rule |
|---|---|
| **Acquired** | lower bound > 1 and point ≥ 1.5× |
| **Bounded** | upper bound < 1.5× |
| **Unresolved** | otherwise |

**Interpretation controls** (pre-stated, not gates):
- **Linkage.** L = broken ÷ inherited, shown beside broken ÷ uniform so that a degraded control
  is visible.
- **Practical value.** S = inherited ÷ scaffold. S lower bound < 2 only means a twofold
  disadvantage is not established; S upper bound < 2 means inherited is within 2×.
- **Descriptive.** As in the 0843 plan (solves, depth, Price covariances, θ trajectories).

**Next action.**
- **Acquired, L lower bound > 1 and S lower bound < 2:** suggest slot 2 (frozen transfer to
  threshold 2) to the strategist; do not consume it automatically.
- **Acquired, but linkage unresolved or the scaffold clearly better:** record the acquisition
  and end expansion of this procedure.
- **Bounded in both families:** park 23 with a bound on this procedure (B/E), not on
  self-adaptation.
- **Unresolved:** report the measured SD and the price of an extension.

All four outcomes go to the strategist.

**Expectation.**
- **Sum:** acquired ≈ 45%, unresolved 30%, bounded 25%.
- **Max:** acquired ≈ 25%, unresolved 30%, bounded 45%. Timing runs solved 26/48 max episodes
  against 6–7 under early stopping (n = 1, different rule): perhaps more selection signal than feared.
- **Most likely overall:** a modest sum gain that the scaffold beats clearly, which ends expansion.

**Surprises:** broken ≈ inherited, both beating uniform; max inherited beating uniform;
inherited within 2× of the scaffold.

**Scope.** One modifier rule, σ = 0.03 and one fixed-duration schedule, which includes maintenance
selection after solving. Development bank, training targets only, fixed token meanings.
