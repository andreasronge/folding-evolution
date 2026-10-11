---
node: questions/10-compositional-map-transfer/53-order-library-cap-release
title: Uncapped semantic library (R-all) on order development cells
bank: x4-order-v1 (development roster only; 24 protected cells stay unsearched)
---
**Question and mechanism.** Per [strategy 1228](strategy.md) and the [cap-release plan](../../plans/order-library-cap-release.md).
In the 1129 probe the behaviour-keyed extractor (R-S) had an admissible recurrent order helper in 49/96 helper × build
cases, and the 16-entry cap dropped 44 of them. **R-all** is R-S with one change: `ranked[:16]` becomes `ranked`, so the
library keeps every eligible class (≥ 2 source cells, 3–9 nodes, one minimum representative each) and donors are drawn
uniformly. Everything else is unchanged from `db30b15`; no helper recognition, filtering or reweighting.

Read-only check on the saved 1129 libraries: uncapped pools hold 22–32 classes (median 28.5), with
3–9 helpers per build. At least one destination-needed helper appears in **31/48** development cell × build pairs
(both helpers in 10/48), against 3/48 under the cap. The rest of each pool is 3-node sums, comparators and a constant
class, content that raised cost in 1129 (R-L 1.55×, R-sum 2.12× of R-tree). Does the coverage pay for the dilution?

**Closest known technique.** Run Transferable Libraries ([Keijzer, Ryan & Cattolico 2004](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf)):
subtrees are pooled from earlier runs and frozen for new runs. Libraries keyed by semantics appear in
[Pawlak, Wieloch & Krawiec 2015](https://gpbib.cs.ucl.ac.uk/gp-html/Pawlak_2014_ieeeEC.html) (a procedure library
used by semantic backpropagation operators). Here the map adapts by **external fitting**, not inheritance. A boundary
test of a known technique; it adds: can a recurrence-only library acquire content the alphabet lacks
(min/max built from GT/IF_GT) and turn it into a search saving once its dilution is charged?

**Arms, unit, seeds.** 24 **new, independent acquisitions** from the frozen 1129 roster and effort. Each build is
24 sources × 2 R-tree jobs = 48 jobs (1,152 total, failures charged). Build seeds come from a namespace disjoint from
1129 builds 0–7. The bank is reloaded from `bank.json` and checked against its hash, with no re-screen. Capped R-S and
R-all are built from the **same** corpus. Scoring has 4 arms (R-tree, R-order, R-S, R-all) on 6 development cells,
24 builds and 4 repeats: 576 seed-paired units, 2,304 jobs. The build is the learning unit. Validation checks that
R-all's first 16 entries equal R-S, that every entry traces to its own corpus, and that no helper census or
destination identity enters extraction.

**Feasibility.** These rates are measured at 1129 (`db30b15`). Source jobs were 384/384 solved, with about 11 worker-s
and 0.20 M evaluations per build. Destination worker-s per job: R-tree 5.4, R-S 7.6, R-order 0.4, R-sum 10.6. If
R-all costs no more than R-sum, scoring takes about 13.8 k worker-s, roughly 25 min wall on 10 workers. If every
R-all job ran to the cap (about 38 s each), scoring would take about 51 min. Rows are saved as they finish.
Timeouts: prepare 20 min, score 90 min, 110 min in total (≤ 2 h).

**Full cost.** Researcher 1–1.5 h, review 0.5 h, queue 0.5–1 h, analysis and decision 1.5 h: about 4–5 h, under
the 6 h ceiling.

**Primary comparison and decision rule.** The primary measure is the R-all / R-tree ratio of capped arithmetic mean
evaluations (failures charged 524,288). Its 95% interval comes from a bootstrap over the 24 builds, with pairs kept
on identical seeds. The worthwhile saving is set at **0.67×** (a third). At R-tree's 75.7 k mean, that saving repays
the ≈ 0.2 M acquisition in about 8 searches.
- **Useful acquisition:** upper bound < 0.80. Return to strategy with a case for the separately priced protected
  stage, judged against the R-order gap.
- **End this recipe on order content:** lower bound > 0.67, which excludes a worthwhile saving and covers harm.
- **Otherwise unresolved:** price the resolution and return to strategy. This is not equality and not an automatic
  top-up.

Expected precision: 1129's per-build log arithmetic R-S/R-tree SD was about 0.47 at 12 pairs; 24 pairs × 24 builds
give an interval of about ×/÷ 1.15–1.2.

Reported but outside the rule: R-all/R-S (paired), geometric ratios, solves and worker seconds, and the share of the
R-tree → R-order log gap recovered. Also cost split by needed-helper coverage (0/1/2, descriptive), donor
insertion and rejection, and break-even searches against R-tree. If R-order stays cheaper, no repayment against it is
claimed.

**Expectation.** I expect the trivia dilution to cancel much of the coverage gain. My guess is R-all/R-tree around
0.8–1.0×, which would land unresolved or end the recipe. In 1129, the builds that held a needed helper gave 0.67×
(geometric, post hoc, 24 pairs); that supports "some gain", not usefulness. Two results would surprise me: R-all
≤ 0.5× (about a quarter of the 3-nat gap to R-order), or R-all clearly costlier than R-S.

**Next action.** Researcher implements the R-all flag and the prepare/score entries; then return to strategy
whatever the outcome. No protected scoring and no cap, ranking, size or rate variants follow automatically.
