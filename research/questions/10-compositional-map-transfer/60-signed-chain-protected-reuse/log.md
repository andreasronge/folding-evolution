# Log: 60 signed-chain protected reuse

- 2026-10-11 (steward, 2150): opened on strategy 2150 (root 10 budget 49 → 50, this sub-question 1).
  Proposal: [run 2150](../../../runs/2026-10-11-2150/proposal.md).
- 2026-10-11 (steward, 2150): experiment [run 2150](../../../runs/2026-10-11-2150/analysis.md), commit `83c7c5b`.
  Bank `x4-signed-chain-v1`, 18 protected cells released for the first time (no other output folder contains
  them); 24 saved 1938 R-all libraries (hash-verified), R-tree, R-gate; 24 builds × 18 cells × 4 repeats = 1,728
  paired jobs per arm, 5,184 jobs, fresh audited seeds, complete grid (0 missing, 0 duplicates); 85 min scoring.
  - Validity: R-tree first attempt 467/1,728 = 27.0% (≤ 85%: hard tier), capped 118 = 6.8% (≤ 25%: not
    cap-dominated; capped jobs 20% of R-tree evaluations), R-gate 1,728/1,728 solved (≥ 95%).
  - **Primary R-all/R-tree 0.778× [0.696, 0.870]** (pooled capped mean evaluations, two-way build × cell bootstrap,
    repeats within units, paired): **saving**. 0.80 bar unresolved. Worker seconds 0.761× [0.680, 0.848]. Cells
    only [0.745, 0.812], builds only [0.717, 0.844]. Ratio of medians 0.61; both-solved 0.81.
  - Below 1 in 18/18 cells (0.67–0.94; 8 cell intervals below 1, none above) and 20/24 builds (0.56–1.09); R-all
    cheaper in 997/1,728 paired jobs and 291/432 units. Solves +2.7 points [+0.5, +5.0]; first attempt +8.5 points
    [+2.9, +14.1].
  - R-gate/R-tree 0.263× [0.233, 0.296]; R-gate/R-all 0.338× [0.298, 0.383]; R-gate needed ≥ 4 attempts in 78
    jobs, R-tree in 659.
  - Coverage strata (descriptive, confounded): 0 / 1 / 2 / 3 needed helpers in 114 / 198 / 109 / 11 of 432 build ×
    cell pairs; R-all/paired R-tree 0.98 / 0.78 / 0.59 / 0.42 (cell-matched 0.99 / 0.79 / 0.57 / 0.37).
  - Economics: saving per search 39.6 k [22.2 k, 57.1 k]; acquisition 216 k [207 k, 226 k] per build; repayment
    **5.4 [3.8, 9.7] searches**; at N = 10 acquire-and-reuse is cheaper by 181 k [7 k, 353 k] (just resolved), at
    N = 100 by 3.75 M [2.00 M, 5.49 M].
  - Against the forecast: resolved, and narrower than both forecast scenarios (bound ratio 1.25 vs 1.35 / 1.53).
  Against the competing explanations: development seed luck or cell selection is not supported; a saving under 20%
  is not excluded. The coverage gradient is now well measured but still an association.
  Decision: close 60 as answered (resolved saving on this bank's held-out cells), because the pre-stated rule
  resolved with all validity checks passed, and strategy 2150 committed no top-up; whether 13–30% is "material"
  is settled for the economics (repaid within about 10 searches) without a larger run. Next: return to strategy
  ([decision 2150](../../../runs/2026-10-11-2150/decision.md)).
