---
node: questions/10-compositional-map-transfer/41-same-alphabet-family-preference
title: Crossed family preference on one alphabet — double-gate vs branch-sum A8 builds
bank: x4-double-gate-v1 (8 spare cells) + x4-branch-sum-v1 (new, built performance-blind)
---
**Question.** Following [strategy 1717](strategy.md) and its [plan](../../plans/same-alphabet-family-preference.md):
does the unchanged A8 recipe learn a *useful preference for its own family*, or one correction that helps
both? The alphabet `v2_x4`, D625, executor and recipe stay the same; only the source family changes. DG is
`(Xa+Xb)>(Xc+Xd) ? Xe:Xf` and TS is `Xa>Xb ? Xc+Xd : Xe+Xf`. Both canonicals: six readouts, two ADD, GT, IF_GT.
Earlier tests (16, 20, 25) crossed close families and stayed near 1.0–1.1×.

**Closest technique.** [PIPE (Salustowicz & Schmidhuber 1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/)
updates a program distribution from search outcomes. A8 is **external fitting** (a context table plus
literal fragments, then frozen), not selection or inheritance. Crossed source/target tests are standard
transfer practice, and mismatched sources can hurt ([Zhang et al., negative-transfer survey](https://arxiv.org/pdf/2009.00909)).
This is a **mechanism/boundary test** of a known recipe: family-level information, or repair of a
weak prior?

**Feasibility (read-only probe, [41 log](../../questions/10-compositional-map-transfer/41-same-alphabet-family-preference/log.md)).**
TS has 1020 distinct behaviours, 216 of them using all four readouts; a greedy 80%-separated set has 540
cells. No TS behaviour agrees with any DG clique cell on more than 26% of inputs. The 8 spare DG clique
cells were never searched. The ≤9-token alias screen did not finish within 10 min;
it moves to preparation (216 cells only). 1536 rates: acquisition 772 worker-s/build; per search, G4 29 s, matched A8 10.8 s, a weak bias (O) 24 s; 9.8 workers. TS rates are **unmeasured**.

**Design (unit = acquisition build).** Runner from research/main `7244fa1`, extended to a second bank and
multi-roster scoring.
- *Prepare:* (1) build the TS bank the way DG's was built: ≤9-token screen, 80% rule, exact maximum clique,
  deterministic 4 source / 4 development / 8 target split (sources span ≥2 GT pairings and all four
  readouts; targets ≥3 pairings); (2) check the hashes and provenance of the 24 frozen DG builds;
  (3) 24 fresh TS builds with new seed blocks; (4) time ≥64 searches across all arms on the development
  cells; (5) hash-freeze both target rosters, builds, seeds and method before any target search.
- *Score:* 16 target cells (8 spare DG, 8 TS) × 48 shared seeds × {G4, D-builds, T-builds}, with 2 seeds
  per build per cell: **2304 searches**. Cap 524 288, P 256, 64 lexicase cases, exact check on 625 inputs;
  failures and fallbacks are kept.

**Stops (validity and price, not outcome):** fewer than 16 separated TS cells or no covered split; any
target already solved by a source behaviour; a hash mismatch; projected scoring time over the timeout.
Each returns to strategy; poor TS acquisition is a result, not a stop.

**Primary comparison.** Capped cost is the geometric mean over a roster's 8 cells, with failures charged
at 2 × cap. P_DG = cost(T on DG)/cost(D on DG); P_TS = cost(D on TS)/cost(T on TS).
**I = √(P_DG · P_TS)**: a bias that wins everywhere cancels out of I. The 95% bootstrap resamples builds
within each cohort (each build keeps its rows on both rosters) and seeds within build × cell; cells are
fixed. Margin **1.5×**:
- lower bound > 1.5 → **material family preference**: *reciprocal* if both P lower bounds exceed 1,
  otherwise *one-directional* (name the direction);
- upper bound < 1.5 → **no material reciprocal preference**. If both cohorts beat G4 by 1.5× on both
  rosters → *shared-bias candidate*; if one cohort is better on both rosters → *one bias dominates*;
- otherwise **unresolved**, with a resolution price.

Also reported: 1 × cap repeat (penalty-sensitive if the label changes), arm/G4 ratios, solve fractions,
per-cell and per-build costs, acquisition-plus-search evaluations.
**Precision (planning only):** with DG's build log-SD of 0.62 in both cohorts, I's interval spans about ×/÷ 1.3–1.45. A true I ≈ 2 should clear 1.5; a point estimate ≤ 1.1 bounds it below 1.5.

**Full cost.** Preparation ≤ 120 min. Prepare entry: screen 5–15 min, acquisition ≈ 32 min (more if TS
sources are harder), timing 5 min → **80 min timeout**. Score: 2304 × 22–30 worker-s ≈ 87–118 min →
**140 min timeout** (or two 70-min entries). Sum **220 ≤ 240 min**. With ≈ 4 h agent time, total
**≈ 7–8.5 h** of the 44.9 h left.

**Expect.** Both matched arms beat G4. P_DG ≈ 2–4, because TS libraries lack `(a+b)>(c+d)` joins.
P_TS ≈ 1–2, because DG fragments contain the `push push ADD` pairs TS needs. I ≈ 1.5–2.5.
**Surprises:** I ≤ 1.1 with cross arms as good as matched; or a mismatched cohort worse than G4.

**Cannot show:** context vs fragments vs supply; inheritance; competitive-baseline superiority; fresh-bank
generality. Output ranges differ (TS −4..4, DG −2..2), so any preference is family-level, not pure ADD placement.

**Next.** Exit to strategy in every case. Reciprocal → PSB2 planning uses family-specific acquisitions.
Shared or dominant → acquire one bias and test it on a third family. Unresolved → price the resolution.
