# Steward probes, run 2026-10-06-0811 (unreviewed, one run each)

## Probe A: re-read of run 0132's learning data (no new searches)

From `generations.jsonl` (commit `02cf76f`): each child's paired score difference from its parent
on the generation's 24 training searches (65k cap, unsolved = 17). "True-effect sd" = sd of the
child means minus the average within-child sampling variance (paired SE²), i.e. the spread of
real child effects that selection can act on.

| learner | generations | children | mean diff | observed sd | noise sd | true-effect sd |
|---|---|---:|---:|---:|---:|---:|
| C (3 of 552 cells, N(0, 0.5)) | 1–8 / 9–17 / 18–25 | 576 / 648 / 576 | +0.01 / +0.03 / +0.01 | 0.36–0.39 | 0.37–0.38 | 0.00 / 0.00 / 0.09 |
| M (3 of 23 multipliers, N(0, 0.5)) | same | same | +0.06 / +0.08 / +0.11 | 0.47–0.51 | 0.40–0.42 | 0.28 / 0.25 / 0.25 |
| T (3 of 23 tied weights) | same | same | +0.01 / +0.03 / +0.06 | 0.39–0.47 | 0.37–0.41 | 0.12 / 0.25 / 0.19 |

C's operator produced no child variation selection could see; M's did throughout, and was not
shrinking by generation 25.

## Probe B: one-step children at the six saved M maps (`probe.py`)

Detached worktree at `02cf76f`, 10 spawn workers. For each of M1–M6 (final maps from 0132,
table checked against `table_for('M', vector)`): 10 children per operator, each scored on 24
training searches (4 seeds × 6 cells, cap 65 536) paired with the parent on the same seeds.
Seeds 811100000 + k·100 + s (disjoint from 0001/0132 namespaces). 4 464 searches, 192 s wall,
23.3 searches/s; mean 0.39–0.46 s per search per worker for every operator.

| operator | children | mean child − parent | observed sd | noise sd | true-effect sd | share < −0.5 |
|---|---:|---:|---:|---:|---:|---:|
| M move: 3 multipliers + N(0, 0.5) | 60 | +0.04 | 0.52 | 0.41 | 0.32 | 0.15 |
| row move: one row, all 23 log-weights + N(0, 0.5) | 60 | −0.12 | 0.38 | 0.34 | 0.18 | 0.15 |
| row move: one row, all 23 log-weights + N(0, 1.0) | 60 | +0.09 | 0.48 | 0.34 | 0.34 | 0.03 |

Parent means on these seeds: 13.50, 12.51, 12.64, 13.19, 12.42, 12.77 (G ≈ 13.8 in 0132).

Reading: whole-row contextual steps at the M maps give 2–4× the true-effect spread of 0132's
three-cell C steps, comparable to M's own token steps; σ 1.0 is mostly harmful on average, σ 0.5
roughly neutral. The variance estimates rest on 60 children each (SE of a variance of this size
≈ ±0.02–0.03, so true-effect sd 0.18 could be 0.1–0.24). The mean differences share each start's
parent noise (SE ≈ 0.13 across six starts), so −0.12 is not evidence that row steps improve M.
