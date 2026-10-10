---
node: questions/10-compositional-map-transfer/38-cheap-bias-source-replication
title: Rebuild A8 from the complementary source roster; score on two-sum-v1
bank: two-sum-v1
---
**Question and mechanism.** Per [strategy 0145](strategy.md) and its [plan](../../plans/cheap-bias-source-replication.md):
A8 has only ever been built from the comparison-gate training cells, the roster on which its
source size and feedback policy were developed. Does the unchanged recipe acquire a useful
frozen bias when rebuilt from **fresh searches on the other four cells per family** (the former
holdouts), or did its 2.73× lead over G4 on two-sum-v1 ([2303](../2026-10-09-2303/analysis.md))
depend on favourable sources? Both sides are development data.

**Closest technique.** Model-building GP updating a program distribution from search results
([PIPE](https://pubmed.ncbi.nlm.nih.gov/10021756/)) and run-to-run library reuse
([Keijzer, Ryan & Cattolico 2004](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf)).
The map adapts by **external fitting**, then is frozen. Not new in kind; a **replication
across source sets**.

**Arms** (code from research/main `74196a8`, laws unchanged; only an explicit source roster is
threaded through `small_source_counts`, extraction and the loader, old default replays exactly).
- **A8′**: per build, 4 fresh G4 attempts per source cell → C4+F4 → 4 attempts under that
  build's own C4+F4 → refit. Failures, empty-cell fallbacks and all costs kept.
- **S8′** (secondary): same first batch plus 4 more fresh G4 attempts, same refit.
- **G4**: the 256 two-sum rows from 2303, reused with replay of a sample (identical keys).
- **Historical A8** (2033 builds, 2303 rows): contextual, not a replicate.

**Unit and roster.** 16 independent builds, 8 per family (BE builds learn from the four BE
cells, PA from PA, as before); new collection seeds disjoint from all 1246/2033 seeds. Score
on all 16 two-sum-v1 confirmation cells × 4 seeds, using 2303's seed and training-case formula
with build index = corpus index, so A8′ build *j* shares keys with historical corpus *j*.
A8′ and S8′: 2 048 searches.

**Feasibility** (from the [audit](source-replication-cost-audit.json), not new runs). Collection:
512 G4 attempts × 12.0 worker-s + 256 adaptive × ~5 s (2033: 4.9) ≈ 7.4 k worker-s ≈ 13 min at
~9.6 effective workers; 2033's prepare, which ran 1 024 adaptive attempts, took 11 min. Scoring at
2303's measured 1.88 s wall per two-sum search: 2 048 searches ≈ 64 min. Expected queue ≈ 1.5 h.

**Admission (prepare stage).** After collection and fitting, time A8′ and S8′ from 4 builds on
the 4 disjoint two-sum timing cells (32 searches). First rule that fits, projection × 1.15
ending by 07:12: (a) A8′+S8′ at 4 seeds; (b) A8′ alone at 4 seeds (1 024 searches); else stop and
report a cost obstacle. Solve rates never enter admission.

**Full cost.** Researcher ≤ 100 min (roster plumbing, loader with membership checks, tests,
smoke). Queue timeouts: prepare 40 min + score 2 h = 2.67 h; ~1.5 h expected. Critic, review,
analysis, decision ≈ 1.5 h. Total ≈ 4.5 h, inside the 6.2 h left.

**Primary comparison.** u = cost(G4)/cost(A8′) on two-sum-v1: 2303's estimator (log capped
evaluations, unsolved = 2 × cap, cell/seed means per build, 16 builds), G4 seeds resampled within
each fixed cell and shared across builds, builds resampled within family; 95% interval.
Margin **1.5×**: about 40% of historical A8's log-gain, and at that speed A8′'s ~6.5 M
acquisition still repays within ~100 searches.
- **LB > 1.5: useful replication.** Carry the *recipe*, not only the 2033 artifacts, to a later
  genuinely new family.
- **UB < 1.5: source-dependent.** Keep A8 as a verified source-specific artifact set; a later
  family needs its own source check.
- **Otherwise unresolved**; report the resolution price in builds. No automatic top-up.

**Reported, no rule.** δ = cost(A8′)/cost(historical A8), paired by corpus index on identical
keys, t interval on 15 df: the direct measure of roster dependence (expected half-width factor
≈ 1.25 at an assumed difference log-SD 0.40); σ′ = S8′/A8′ against 1.17; per-family and per-cell
results; solve counts; 1 × cap; source yield, empty cells and library size per build; between-build
spread; A + N·S in evaluations and worker-seconds with break-even against G4. Low S8′ and A8′ together
point to the source set; low A8′ alone to the adaptive step.

**Expectations.** G4 solved 77% of attempts on these cells against 68% on the original roster, so
first-batch yield should be similar or higher. I expect u ≈ 2.2–2.8 with LB above 1.5 (about 80%),
δ ≈ 0.9–1.2, σ′ > 1. With single builds instead of 4-block means, the build log-SD may reach 0.35
(2303 corpus: 0.27), so a true u near 1.8 would come out unresolved. **Surprises:** u UB < 1.5;
δ LB > 1.25; a PA/BE split where one family's sources fail; σ′ < 1.

**Scope.** One alternative roster within the two families, one target bank (development),
D1331, external fitting. Decoder, library, yield and content stay bundled; no new-family,
family-specificity or inherited-evolution claim.

**Next action.** Researcher adds the roster argument and replacement-source loader, verifies exact
replay of a 2033 build under the old default, smokes collection on two builds, queues prepare
and score. Return to strategy whatever the outcome.
