---
verdict: pass
---

# Code review: 1723 crossed BE/PA training-only learning

Reviewed `git diff 1ae6eb7..db96645` (new `crossed_learning_run.py`,
`crossed_learning_report.py`, frozen bank snapshot, tests), proposal.md,
critique.md, plan.md, queue.yaml and the smoke/probe artifacts. Ran the
crossed-learning and map-learning tests (16 passed) and the queue validator
(OK, one entry, 28 800 s = the 8 h cap).

## Blocking issues

None.

## What was checked

**Arm wiring and seeds.** Both families start from the same G4 (hash asserted),
use the same learner (`initial/mutate/table_for/log_cost` from `map_learning`),
the same (4+12), 25 generations, 24 inner searches at cap 65 536, same cell
cycling `train[(j+gen) % len]` as the reviewed 1603 stage-C code. Outer seeds
BE `1723200+2k`, PA `1723201+2k`; inner seeds `seed*10000+gen*100+j` (max
offset 2523) and selection seeds `+5000+j` (j<120) never collide within or
across trajectories. Fresh seeds 1723300–1723349 are new (1603 used
1603100–1603149 and 1603300–1603349). Within a generation all 16 candidates
share the same 24 (cell, seed) pairs; G4 is scored on the same 120 selection
seeds as the four final parents. Fresh scoring runs every saved map plus G4
on all ten training cells × 50 shared seeds. Search payloads carry only
`id` and `labels`; holdout IDs are rejected at job construction and again in
`jobs()`. The frozen bank's SHA256, D1331 labels and label disjointness are
verified at load.

**One procedural change from 1603, an improvement.** Selection uses 120
distinct seeds cycled over cells (BE 30/cell, PA 20/cell); 1603 reused the
same 20 seeds on every cell. Plan.md states this. G4 is added to the selection
block for the gate. Both are documented.

**Metrics.** Per map/cell gain = seed mean of log2(T_G4/T_map), unsolved
T = cap; cells averaged equally within each training set; trajectories are
the unit (one-sample t for own/off, Welch for crossed). The crossed contrast
for family F is own-trained maps minus other-trained maps on F's cells, which
equals log2 of the matched-over-mismatched speed as the proposal defines.
Flags keep `resolved_gain` and `upper_below_1_25` separately with L/W over
N/B precedence (critique note 3). s_off is the median over ten cells of
sqrt((s_BE²+s_PA²)/2) with per-family medians retained (note 4). Outcome rows
match the proposal, with row 1 relabelled "early low-yield stop; learning
remains unresolved" (note 3). Fresh cross-product completeness, duplicates,
cap, hash and case-pairing are all validated before inference; any error
yields U.

**Early gate stability (recomputed).** Using the probe-20 rows (G4 vs one
perturbation, 65k cap) and 1603's G4 calibration rows truncated to 65k: the
per-search log2-cost sd is 1.9–2.0 (BE) and 1.5–1.7 (PA); common-seed
correlation between maps is 0.1–0.3, so a 120-search paired gain has
SE ≈ 0.19–0.22 log2 against a threshold of log2(1.1) = 0.14. Simulating four
trajectories with best-of-4 selection:

| true gain (log2) | 0 | 0.1 | 0.2 | 0.3 |
|---|---|---|---|---|
| P(gate stops), BE-like noise | 0.05 | 0.003 | 0.001 | 0 |
| P(gate stops), PA-like noise | 0.08 | 0.007 | 0 | 0 |

The gate essentially never stops real learning; it is weak at stopping under
the null, as the proposal says. Stable, not a risk to the main stage.

**Runtime admission.** Default first-pair estimate 31 min; afterwards
1.3 × slowest pair + fresh reserve + 180 s must fit the 27 000 s internal
deadline. The fresh reserve uses max(1.88 s, observed projected rate) × 1.3
over (saved maps + prospective pair + G4) × 500 searches. Projected per
trajectory at G4 speed: BE 17.8 min, PA 13.1 min; 10 pairs ≈ 5.2 h, fresh
≈ 33 min; total ≈ 5.7 h within 7.5 h. Stage-2 size grid {n, 14, 18}: 18 per
family means 8 more pairs (≈ 4.1 h) plus holdout and fresh scoring (≈ 2.2 h),
which fits one 8 h queue, so the grid is not truncated below what the queue
allows.

**Critique dispositions.** Notes 1–4 are implemented as described above.
Notes 5–7 concern wording in existing belief files; plan.md says the
researcher may not edit those and leaves them to the steward. That is the
right disposition.

## Minor notes (not blocking)

1. **Fresh reserve is about 2× conservative.** The admission rate extrapolates
   unsolved 65k inner searches by 524288/65536 = 8×. On the probe rows this
   gives 3.7 s/search versus the measured 1.88 s full-cap mean. With 31-min
   pairs n = 10 still fits; if pairs run ≥ 35 min the tenth pair is refused
   and n = 9. This is the approved "runtime outcome" and the critic asked for
   conservative reserves, so acceptable; the analysis should read
   `schedule.json` before calling an achieved n < 10 a cost problem.
2. **A deadline hit during learning skips all fresh scoring.** `TimeoutError`
   from `evolve()` propagates past the fresh loop, so completed maps get no
   fresh rows and the outcome is U even though `trajectories.json` holds the
   maps. The 1.3× pair reserve makes this unlikely. If it happens, the saved
   maps can be scored in a follow-up without re-learning.
3. **Partial fresh block.** If the deadline hits inside a fresh block, that
   block's rows are in `search.jsonl` (phase `fresh_training`) but not in
   `fresh_scores.json`. The reviewer can reconstruct from `search.jsonl`.
4. **Generation 0 scores four identical G4 copies** (72 redundant searches
   per trajectory, under 1% of cost). Same as 1603; Spearman at generation 1
   is correctly undefined and recorded as such.
5. **Weak null stopping power** (5–8%) means continuation past the gate is
   not evidence of learning; only the fresh intervals are.
6. `RAYON_NUM_THREADS=1` is set in-process before the spawn pool rather than
   in the queue `cmd` as 1603 did; with the spawn context children inherit it,
   so this is fine.
