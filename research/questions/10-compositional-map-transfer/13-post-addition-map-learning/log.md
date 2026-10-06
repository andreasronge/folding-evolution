# Log

## 2026-10-06: opened (run 2026-10-06-0132)

Opened under root 10 on strategy 0132's direction (one-family transfer on the post-addition
split from run 0001). Steward probes on the six training cells, 65 536 cap, 20 seeds per cell
(`a65ded0`, unreviewed): G 13.75 / 13.94 mean log2 cost on two seed sets (SE 0.14); hand-set PA
grammar 14.10; U 16.57; G with all log-weights + N(0, 0.5) 14.12–14.86; one row + N(0, 0.7)
−0.26 to +0.54 versus G (SE ≈ 0.17, paired correlation 0.16–0.49). Inner-run cost 0.65–1.2 s
at 10 workers. ([results](../../../runs/2026-10-06-0132/steward_probes/results.md))

Decision: propose a gated outer-loop adaptation study with three learners (contextual, G-based
token multipliers, token-only), six independent trajectories each, evaluated on fresh training
seeds and both holdouts ([proposal](../../../runs/2026-10-06-0132/proposal.md)), because the
probes show the training signal is measurable but small against noise, and only real
trajectories can tell learning from no learning.

## 2026-10-06: run 2026-10-06-0132, result

Experiment: three outer-loop learners from fixed starts — C (all 552 contextual log-weights,
from G), M (23 global token multipliers on G's rows, from G), T (23 tied weights, from G-marg) —
6 matched trajectories each, (4 + 12) with re-scored parents, 3-coordinate N(0, 0.5) mutations,
25 generations on the six training cells at the 65k cap; every final map then scored on the same
fresh seeds (6 training cells × 50, 2 holdouts × 100, cap 524 288)
([proposal](../../../runs/2026-10-06-0132/proposal.md), [plan](../../../runs/2026-10-06-0132/plan.md)).

Result: outcome **row 1** on complete data (commit `02cf76f`, 197 528 searches, all 18
trajectories; [analysis](../../../runs/2026-10-06-0132/analysis.md)). Ratios are speed (> 1 =
faster), 95% two-level bootstrap, 524k cap:
- C / G: training 0.92 [0.78, 1.09] (no practical gain; 65k: 0.94 [0.81, 1.09]); holdouts 1.16
  [0.86, 1.54] and 0.80 [0.60, 1.07]. Learning curves flat in all six; L1 drift from G 1.1–1.5;
  C-marg / G-marg 1.01–1.10. C stayed at G plus noise.
- M / G: training 2.23 [1.82, 2.75]; holdouts (S?M:S)+M 2.01 [1.47, 2.81], (S?M:S)+m 1.71
  [1.26, 2.32]; all 6 trajectories faster on all three sets; curves still falling at gen 25.
  M's holdout cost sits 0.38 log2 above its training cost (G +0.12): about a third of the
  training gain does not reach the holdouts.
- T / G-marg 1.69–2.12× faster on all sets, but T / G 0.41–0.57.
- What M and T learned, consistent across trajectories: INPUT up (M ×3.4, 6/6), DUP down
  (M ×0.5, 6/6; T 6/6), IF_GT up (M 6/6), reducers up.
- Stage 0: G repeatability 13.86 vs 13.81 (gate 0.6). The gate dropped stage-3 sampling
  (projection 427 min vs 420); the run took 346 min. No sampled solver rates for learned maps.

Decision: keep 13 open (1 of 2 slots left) and return to strategy (`next: strategy`), because
row 1 and strategy 0132 both send the first adaptive result there before slots 2–3 are spent.
The run answers the procedure question, not A1: three-coordinate steps in 552 dimensions never
lifted C above the score noise (sd ≈ 1.6 log2 per run), so contextual learning is untested
rather than rejected. The restricted learner M gives the root its first held-out gain from a
learned decoder change (1.7–2.0× over frozen G, lower bounds 1.26/1.47); whether that gain is
specific to the PA family or a generic improvement of G on this alphabet is unmeasured.
