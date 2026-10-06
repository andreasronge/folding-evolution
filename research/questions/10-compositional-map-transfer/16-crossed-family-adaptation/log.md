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
- 2026-10-06 (run 2026-10-06-2229, stage 2, ran; row 4). Approved with notes by the critic;
  code review pass; commit `33fcee2`, complete data (25 200/25 200 rows, 35 min, no errors,
  no learning or training rows; [analysis](../../../runs/2026-10-06-2229/analysis.md)). The 20
  frozen stage-1 maps and G4 (hashes verified) on the three holdouts, 400 shared fresh seeds
  per cell (2229000–2229399), 524k cap; per-map seed-mean log2(T_G4/T_map), trajectory as the
  unit, n = 10 per family, 95% t / Welch. G4 gate passed (385, 377, 398 of 400 solved).
  Generic gain over G4: L on all six arm × cell estimates, 1.97×–2.93×, lowest lower bound
  1.63× (PA maps on the BE cell); BE maps on the BE cell 2.01× [1.86, 2.18]; PA maps on the
  two PA cells 2.48× [2.07, 2.96], BE maps on them 2.59× [2.41, 2.77]. Crossed contrasts:
  C_BE (BE over PA maps on `S?m:(M+F)`) **1.02× [0.835, 1.2485]**, C_PA (PA over BE maps on
  the two PA holdouts) **0.96× [0.79, 1.15]**; both not W and B (matched advantage bounded
  below 1.25×), neither reversed. Per PA cell: 0.91× [0.75, 1.11] and 1.00× [0.82, 1.23].
  Pre-stated interaction I 0.98× [0.83, 1.15], not W. C_BE's B label holds by 0.0015 on the
  upper bound; dropping any one of 14 of the 20 maps lifts it to 1.25–1.30 (row 5b), so rows 4
  and 5b read the same here. PA9 (weakest stage-1 map) carries most of the PA arm's spread.
  Holdout gains match or exceed the stage-1 training gains (BE 2.18× → 2.01×, PA 2.27× → 2.48×;
  cross-block, descriptive). Predicted row 5b; generic gains were larger than the predicted
  1.6–2.0×, and the in-sample 1.13×/1.10× point estimates did not reappear. Detecting a true
  1.1× at 80% would need about 75 (BE) / 64 (PA) trajectories per family, 14–30 h of learning.
  Decision: close 16, because it is answered at its design's resolution: on these three
  screened cells the token maps transfer generically (about 2–3× over G4, all resolved) and the
  matched-family advantage is bounded below about 1.25× in both directions with point estimates
  near 1 (explanation B fits; A is not supported at this resolution but a preference up to
  1.25×, including the stage-1 1.1×, is not excluded; C does not apply because the mismatched
  arms improve G4; D was out after stage 1). A detection-sized rerun would most likely buy a
  tighter bound around 1, so slot 9 goes back to strategy. Corrections to the 1723 entry above
  (critique 2229 notes 7–8): "2 tied" should read "the other two within 0.02 log2 of zero",
  and "no map hurt the other family" should read "all 20 maps had positive estimated gains
  averaged over the other family's training cells; both arm-level gains were resolved".
