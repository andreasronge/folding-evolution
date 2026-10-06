# Crossed learning: training only

Fresh training cells only; no held-out transfer is measured.

Outcome: U — Unresolved: incomplete/invalid data or fewer than six maps per family.
Maps per family: {'BE': 2, 'PA': 2}. Smoke: True.

own BE: 1.016x, 95% interval [0.8337323585233677, 1.2372740484553173]; N.
own PA: 1.000x, 95% interval [1.0, 1.0]; N.
off BE: 0.916x, 95% interval [0.29995245571235524, 2.796658423335374]; descriptive.
off PA: 1.000x, 95% interval [1.0, 1.0]; descriptive.
crossed BE: 1.016x, 95% interval [0.8337323585233677, 1.2372740484553173]; B.
crossed PA: 1.092x, 95% interval [0.357569587925354, 3.3338616869300375]; X.

L/W takes precedence over N/B; retain both flags. N/B bounds gains below 1.25x, not absence of improvement.
Crossed estimates use independent trajectory Welch intervals; shared search seeds are paired within map/cell only.
No result from this stage establishes held-out family specificity.

Sizing (training-only proxy): {"s_off": 0.19106194363276607, "definition": "median over ten cells of sqrt((s_BE^2+s_PA^2)/2)", "family_cell_medians": {"BE": 0.20229122767759367, "PA": 0.0816656553471191}, "candidates": [{"n_per_family": 2, "half_width_log2": 0.8220731933227587, "reaches_target": false}, {"n_per_family": 14, "half_width_log2": 0.1484392913646328, "reaches_target": true}, {"n_per_family": 18, "half_width_log2": 0.12942819529575342, "reaches_target": true}], "selected_n_per_family": 14, "no_candidate_reaches_target": false, "achieved_half_width_log2": 0.8220731933227587, "ratio_whose_point_estimate_would_clear_one": 1.7679447543109932, "caveat": "Training-only precision proxy; neither power nor conservative coverage is guaranteed for any holdout."}

Stop reason: None
