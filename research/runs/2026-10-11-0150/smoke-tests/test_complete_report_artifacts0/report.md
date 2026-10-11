# Restarted tree versus A8 (0024)

fixed DG/TS development rosters; no transfer or optimal-policy claim

historical acquisition worker seconds plus contemporary search seconds; hardware/load limits; point-estimates are not resolved repayment

## DG (primary)

{'verdict': 'tree_evaluation_win_with_noninferiority', 'reliability_noninferiority': True, 'reliability_status': 'within_three_percentage_points'}

| Contrast | Evaluation ratio (95%) | Worker-time ratio (95%) | Solve difference (95%) |
|---|---|---|---|
| R-tree/R-A8 | 0.5 [0.5, 0.5] | 1 [1.0, 1.0] | 0 [0.0, 0.0] |
| R-tree/F-A8 | 0.5 [0.5, 0.5] | 1 [1.0, 1.0] | 0 [0.0, 0.0] |
| R-A8/F-A8 | 1 [1.0, 1.0] | 1 [1.0, 1.0] | 0 [0.0, 0.0] |

Means and solve fractions: `{'evaluations': {'R-tree': 3200.0, 'R-A8': 6400.0, 'F-A8': 6400.0}, 'worker_seconds': {'R-tree': 1.0, 'R-A8': 1.0, 'F-A8': 1.0}}`; `{'R-tree': 1.0, 'R-A8': 1.0, 'F-A8': 1.0}`.

Historical tree reference: `{'label': '2254 historical unpaired reference, development data', 'jobs': 1, 'solves': 1, 'mean_evaluations': 1024.0, 'mean_worker_seconds': 1.0, 'restarted_to_historical_evaluation_ratio': 3.125}`.

Full per-cell metrics, attempts, geometric sensitivity, acquisition-plus-search curves in both units, repayment bounds and resolution prices are in result.json.

evaluations, R-A8: saving {'point': -3200.0, 'interval95': [-3904.0, -2474.6666666666665]}; repayment None, 95% [None, None], unbounded=True.
evaluations, F-A8: saving {'point': -3200.0, 'interval95': [-3904.0, -2474.6666666666665]}; repayment None, 95% [None, None], unbounded=True.
worker_seconds, R-A8: saving {'point': 0.0, 'interval95': [0.0, 0.0]}; repayment None, 95% [None, None], unbounded=True.
worker_seconds, F-A8: saving {'point': 0.0, 'interval95': [0.0, 0.0]}; repayment None, 95% [None, None], unbounded=True.

| Cell | Arm | Solves / jobs | Mean evaluations | Mean worker seconds |
|---|---|---|---|---|
| 0 | R-tree | 96/96 | 3200.0 | 1.000 |
| 0 | R-A8 | 96/96 | 6400.0 | 1.000 |
| 0 | F-A8 | 48/48 | 6400.0 | 1.000 |
| 1 | R-tree | 96/96 | 3200.0 | 1.000 |
| 1 | R-A8 | 96/96 | 6400.0 | 1.000 |
| 1 | F-A8 | 48/48 | 6400.0 | 1.000 |
| 2 | R-tree | 96/96 | 3200.0 | 1.000 |
| 2 | R-A8 | 96/96 | 6400.0 | 1.000 |
| 2 | F-A8 | 48/48 | 6400.0 | 1.000 |
| 3 | R-tree | 96/96 | 3200.0 | 1.000 |
| 3 | R-A8 | 96/96 | 6400.0 | 1.000 |
| 3 | F-A8 | 48/48 | 6400.0 | 1.000 |
| 4 | R-tree | 96/96 | 3200.0 | 1.000 |
| 4 | R-A8 | 96/96 | 6400.0 | 1.000 |
| 4 | F-A8 | 48/48 | 6400.0 | 1.000 |
| 5 | R-tree | 96/96 | 3200.0 | 1.000 |
| 5 | R-A8 | 96/96 | 6400.0 | 1.000 |
| 5 | F-A8 | 48/48 | 6400.0 | 1.000 |
| 6 | R-tree | 96/96 | 3200.0 | 1.000 |
| 6 | R-A8 | 96/96 | 6400.0 | 1.000 |
| 6 | F-A8 | 48/48 | 6400.0 | 1.000 |
| 7 | R-tree | 96/96 | 3200.0 | 1.000 |
| 7 | R-A8 | 96/96 | 6400.0 | 1.000 |
| 7 | F-A8 | 48/48 | 6400.0 | 1.000 |

Noninferiority is within three percentage points, not equal reliability. An unresolved guard does not establish inferiority. Lower capped expenditure does not imply unlimited time-to-solution or practical superiority. Return to strategy; no automatic top-up.
