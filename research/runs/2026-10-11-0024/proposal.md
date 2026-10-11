---
node: questions/10-compositional-map-transfer/44-restarted-tree-vs-a8
title: Restarted tree GP versus restarted and full-cap A8 on the DG and TS rosters
bank: x4-double-gate-v1 (8 spare cells) + x4-branch-sum-v1 (8 targets), saved 1717 builds; development data
---
**Question.** In [43](../../questions/10-compositional-map-transfer/43-acquired-bias-vs-tree-gp/question.md), A8 kept two DG advantages over tree GP: reliability (314 vs 202 of 384 solved) and about 86k evaluations saved per search. Tree GP either solved fast or stalled (179 solves by 65,536 evaluations, 23 more by the cap). **Under the same restart schedule, does acquisition-free tree GP remove A8's arithmetic saving at equal reliability?** This follows [strategy 0024](strategy.md) and its [plan](../../plans/restarted-tree-acquisition-value.md), with one change.

**Closest technique.** Fixed-cutoff restarts of a randomized search ([Luby, Sinclair & Zuckerman 1993](https://www.cs.utexas.edu/~diz/pubs/speedup.pdf)); in GP, short versus long runs ([Luke, GECCO 2001](https://gpbib.cs.ucl.ac.uk/gp-html/luke2_2001_gecco.html)). A8's map adapts by external fitting. This is a baseline test of a known technique.

**Change: restart both arms.** The strategy keeps A8 at full cap. My read-only probe of 2254's rows (an attempt is an ordinary search truncated at the cutoff) projects that restarting at 65,536 also helps A8: **111k** evaluations and **98.7%** solved, against 178k and 81.8% at full cap. Restarted tree GP projects to **87k and 99.0%**. An asymmetric primary would credit the schedule to the representation, giving a projected ratio of 0.49 instead of 0.78. The strategy's contrast remains secondary. Shorter cutoffs favour tree GP more (16,384: 32k vs 103k), so 65,536 does not favour tree GP. No sweep ([log](../../questions/10-compositional-map-transfer/44-restarted-tree-vs-a8/log.md)).

**Arms** (per family: 8 target cells, all 24 native builds).
- **R-tree**: frozen 2254 tree GP (mix 0.5, 32-token limit, P 256, lexicase on 64 cases). Up to 8 attempts of 65,536 evaluations each (total 524,288). Each attempt resets the population and draws new training cases from its own seed. The job stops at the first D625-exact solve.
- **R-A8**: same schedule; the build is fixed and each attempt gets a new search seed.
- **F-A8**: unchanged full-cap A8 (secondary).

The unit is the complete scheduled job. Per cell: 24 builds × 4 repeats = 768 jobs for R-tree and R-A8, and 2 repeats = 384 for F-A8. Attempt seeds are `22300000 + 1000·(8f+c) + 8·(4b+r) + k`, shared by both restarted arms. F-A8 seeds are `22320000 + 1000·(8f+c) + 2b + r`. Before scoring, the auditor publishes both sets and checks them for overlap with each other and with every 2214/2239/2254 calibration, smoke, scoring, acquisition and replay seed.

**Validation.** For both arms, attempt 1 must reproduce the ordinary capped search on every non-timing field. Also test a later solve, a full failure, evaluation accounting (≤ 524,288) and deterministic replay, and rerun the 16 A8 build replays. Reuse `tree_gp_search.py`/`tree_gp_run.py` at `c32ff04` and add only a scheduling wrapper.

**Feasibility.** Rates measured in 2254: tree 107 µs/eval on DG (84 on TS), A8 66 (55), concurrency 9.1. DG projection: 768 × 9.3 s + 768 × 7.3 s + 384 × 11.8 s ≈ 17k worker-s, about 32 min. TS about 6 min. Restart overhead is unmeasured: Stage 0 times 64 sustained DG jobs per restarted arm and refuses a projected DG wall above 75 min.

**Cost.** Queue: preparation ≤ 20 min, DG about 50 min, TS about 10 min (timeouts 30/90/30, 2.5 h summed). Agents about 3.5 h. Total about 4.5 h, well before the deadline.

**Primary comparison (DG).** R = arithmetic mean actual evaluations, R-tree ÷ R-A8. Cells are weighted equally, and a failed job counts the cap. The interval is a paired block bootstrap over 24 builds (8,192 draws, 95%). Reliability holds if the lower bound of the solve-fraction difference (R-tree − R-A8) is above −0.03.
- **Upper < 1 and reliability holds**: A8 saves nothing over restarted generic search on these rosters, so its acquisition never repays. Stop buying A8 here. R-tree becomes the comparator for the [tree-native learning plan](../../plans/tree-native-fragment-learning.md).
- **Lower > 1**: A8 keeps a saving. Report the `A + N·S` repayment horizon against R-tree.
- **Upper < 1 but reliability fails**: cheaper but less reliable, which is not an efficiency win. Report both.
- **Otherwise unresolved**: state the price of resolving it; no automatic follow-up.

Simulation from saved rows: R ≈ 0.78, upper bound below 1 in about 90% of 384-job runs, hence 768. A8's build heterogeneity (2–13 of 16 per-build solves) will widen the interval.

**Secondary (descriptive).**
- R-tree ÷ F-A8 (the strategy's contrast, projected about 0.49) and R-A8 ÷ F-A8.
- R-tree against the 2254 full-cap tree rows (a labelled historical reference).
- Per-cell solves and cost curves, geometric 2×cap, attempts per job.
- Worker seconds: tree GP is 1.6× slower per evaluation, so an evaluation win may be a seconds loss.
- TS: the same contrasts, reported separately and never pooled.

**Expectations.** R between 0.65 and 0.9; both restarted arms solve about 98–99%; TS R about 0.2. **Surprises**: R > 1; a restarted arm below 95% solved (dependent attempts); restart overhead above 30% of wall time.

**Next action.** After the result or any measured obstacle, close 44 and exit to strategy. Development data only: no transfer claim.
