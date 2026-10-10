# Log: 38 cheap-bias source replication

2026-10-10 (steward, run 2026-10-10-0145): opened under strategy 0145. No new searches; the
strategist's [read-only audit](../../../runs/2026-10-10-0145/source-replication-cost-audit.json)
gives G4 196/256 solved on the replacement cells (12.0 worker-s per search) and two-sum target
rates (A8 17.0, G4 22.6 worker-s). research/main `small_source_run.py` passes the hardcoded
`TRAINING[family]` roster to `small_source_counts` and extraction; corpora are family-specific
(8 BE, 8 PA), so a roster argument is the needed change.
Decision: propose 16 fresh A8 builds (8 per family) from the holdout roster, primary G4/A8′ on
two-sum-v1 against 1.5×, because that is the cheapest complete test of source dependence the plan allows.

2026-10-10 (run 2026-10-10-0145, commit `b6d1974`; [analysis](../../../runs/2026-10-10-0145/analysis.md)):
16 fresh A8′ builds (8 BE, 8 PA), each from 4 G4 attempts on each of its family's four complementary
cells (the former comparison-gate holdouts) → C4+F4 → 4 attempts under it → refit; 768 new collection
seeds disjoint from 1246/2033; legacy 2033 build replayed exactly under the old default roster. Sources:
first batch 193/256 solved (75%), adaptive 255/256, no empty cells, library 32 in every build;
acquisition 4.51 M evaluations per build (historical A8 6.51 M). Admission rejected both arms (projected
7 188 s with reserves, ceiling 7 080 s) and admitted A8′ alone; the projection came from a 32-job timing
batch at 6.1 effective workers while scoring achieved ≥ 9.4, so S8′ was built but **not scored** (σ′ lost
to a biased estimator, not a real cost obstacle). Score: 1 024 searches, 1 892 s, complete, 32/32 timing
rows replayed. Primary u = cost(G4)/cost(A8′) on two-sum-v1 **2.50× [2.17, 2.85]** (1× cap 2.06×
[1.84, 2.28]; BE 3.14× [2.61, 3.71], PA 1.99× [1.66, 2.32]; 16/16 builds below G4's geometric cost;
build log-SD 0.23). Historical A8 on the same G4 rows: 2.73× [2.36, 3.17]. Solves A8′ 489/1 024, historical
A8 521, G4 51/256; the 32-solve deficit is all PA (217 vs 249; BE 272 both). δ = cost(A8′)/cost(historical A8)
on identical keys **1.093× [0.905, 1.321]** (16 builds, t on 15 df; BE 0.96×, PA 1.25× [0.87, 1.79]);
PA1, PA6, PA7 each about twice their historical counterpart, not explained by first-batch yield (yield vs
log cost r = 0.13). Repays acquisition against G4 after 35 [30, 43] searches in evaluations; the runner's
worker-second "never repays" rests on a two-row, uncontended G4 calibration (0.558) contradicted by
equal evaluation throughputs, so worker-second economics are unestablished.
Decision: close 38, answered at its scope, because the pre-registered rule fired with margin (LB 2.17 > 1.5,
also per family and at 1× cap): the unchanged recipe rebuilt from the complementary roster produced a
clearly useful frozen bias, so the *recipe*, not only the 2033 artifacts, is what to carry to a later
genuinely new family. Not shown: equality with historical A8 (δ allows 10% cheaper to 32% costlier),
robustness to arbitrary source sets or other families, or where the weaker PA builds come from (S8′ unscored);
both rosters are development data. Scoring the already-built S8′ would place the PA deficit but would not
change the carry-the-recipe choice, so no top-up.
