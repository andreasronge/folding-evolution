# Log: 16-crossed-family-adaptation

- 2026-10-06 (run 2026-10-06-1723, proposal): opened from strategy 1723 (root 10 slots 7–9,
  root budget 7 → 9). Stage 1 proposed: 10 independent G4-based token-multiplier trajectories
  per family (BE 4 training cells, PA 6), 0132's learner unchanged, fresh training scores on all
  ten training cells, holdouts not scored. Cost measured from 1603's G4 rows and 0132's M
  trajectories: ≈ 12–14 min per trajectory on 10 workers, not the 35–70 min first projected.
- 2026-10-06 (run 2026-10-06-1723, ran; row 4). Approved with notes by the critic; commit
  `db96645`, complete data, 4.28 h, 216 420 searches, zero holdout searches
  ([analysis](../../../runs/2026-10-06-1723/analysis.md)). 10 BE + 10 PA independent
  trajectories from G4, all admitted, early gate never fired; 9.5–13.7 min per trajectory.
  Fresh training scores (50 shared seeds per cell, 524k cap, trajectory as unit, 95% t):
  own-family gain over G4 BE **2.18× [1.98, 2.40]**, PA **2.27× [1.95, 2.65]** (both L; 20/20
  maps above 1). Off-family training cells: BE-trained maps on PA cells 2.07× [1.94, 2.21],
  PA-trained on BE cells 1.93× [1.61, 2.30]; no map hurt the other family. In-sample crossed
  contrasts (Welch): BE-trained over PA-trained on BE cells **1.13× [0.93, 1.37]**, PA over BE
  on PA cells **1.10× [0.93, 1.29]**, both X; matched arm ahead on 8 of 10 cells, 2 tied. Post hoc
  within-map interaction (sum of both contrasts) 1.24× [1.09, 1.41], exploratory. Mean
  log-multiplier vectors differ by 0.53 of the within-family spread (permutation p 0.20); both
  families make the same big moves (INPUT up, IF_GT up, REDUCE_ADD up, DUP down). Sizing rule:
  s_off 0.355 log2 (BE cells 0.447), so n = 10 per family meets the 0.50 half-width target; no
  extension. Steward check of the fresh rows: at 50 seeds about half the per-cell between-map
  variance is seed noise (seed-noise sd 0.15–0.33, remaining between-map sd 0–0.46 log2).
  Decision: continue 16 with stage 2 (holdout evaluation of the 20 frozen maps plus G4, no new
  trajectories), because row 4 routes there and the pre-stated size rule gives n = 10; the
  learner works on both training sets, mostly generically, and only the withheld cells can say
  whether the small in-sample family preference transfers. Competing explanation D is out for
  this learner and budget; C (damage) does not apply on training cells.
