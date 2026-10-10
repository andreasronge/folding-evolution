---
outcome: observations
---
# Analysis: independent-input double-gate bank, source discovery and pilot acquisition (stage 1)

Probe (`kind: probe`), descriptive only. Code commit `09c850d`. Data: `experiments/output/2026-10-10/2026-10-10-0311-independent-input-prepare/` (bank, sources, builds) and `.../2026-10-10-0311-independent-input-score/` (development scoring). Everything below was recomputed from `first.jsonl`, `adaptive.jsonl` and `search.jsonl`; all numbers agree with the runner's `report.md` and `result.json`.

## 1. Data completeness

Both queue entries finished with exit 0, well inside their timeouts.

| Entry | Wall | Timeout | Effective workers (of 10) |
|---|---:|---:|---:|
| prepare (bank + 256 source searches + fits) | 599 s | 1500 s | 9.4 / 9.2 |
| score (192 development searches) | 444 s | 1800 s | 9.5 |

- **Bank.** `x4-double-gate-v1` under alphabet `v2_x4`, SHA-frozen before any search. Real-token exhaustive screen to depth 9 completed (`complete: true`, 121 s). Maximum pairwise-separated set: **24 cells**, matching the semantic pre-audit. Split: 4 source, 4 development, 8 protected (16 used, 8 spare). Protected cells were never searched (`protected_performance_scored: false`; no protected cell label appears in any jsonl). Validation passed in Python, Rust and the semantic machine: 492 canonicals and witnesses, depth-3 typed-state enumeration (7 240 programs), 10 000 random tapes.
- **Split coverage.** Sources cover pairings {01|23} (three cells) and {03|12} (one cell) and use every Xi as an output. Development covers {03|12} (two), {01|23} (one) and **{02|13} (one), a pairing no source has**. Protected covers all three pairings. So one development cell tests transfer to an unseen predicate pairing; the other three share their predicate (or its flip) with a source cell.
- **Sources.** 128 first-batch G4 rows and 128 adaptive rows, exactly 4 per build × cell, no duplicates, matching the frozen `source_schedule.json`. Seeds 310000–317033 (first) and 320000–327033 (adaptive), disjoint from each other and from development.
- **Development.** 192 rows = 4 cells × 3 arms × 16 seeds, no duplicates, no missing or extra rows against `schedule.json`. Seeds (330000–333015) are identical across the three arms within each cell, as planned. A8 and O each map 8 builds × 2 seeds per cell. All rows at cap 524 288, pop 256, `v2_x4`. No `initial_reencoded`, no `empty_library_fallback` in the development phase.
- **Solved semantics.** `solved` requires the exact check on all 625 inputs; the runner re-verifies every solver and raises on mismatch (`execute()` in `independent_input_run.py`). Every unsolved row sits at exactly 524 288 evaluations. No solved row reached the cap.
- **O artifacts.** Eight A8′ builds from run 2026-10-10-0145 (BE1–4, PA1–4, original alphabet `v2_rmin_first`), SHA-frozen, with `declared_token_reinterpretation: true`. Their fragment names still read `_op_first`, `_op_reduce_max`, etc.; under `v2_x4` those token ids are the X0–X3 readouts.
- **Freeze.** Score entry verified bank, O, schedule, method-file and build hashes and the recorded admission before searching. Admission was runtime-only (projected 754 s ≤ 1770 s, prepare 599 s ≤ 1470 s); the discovery reading was recorded but did not gate, as the code review required.

Nothing is missing, duplicated or silently substituted.

## 2. Source discovery and acquisition

**First-batch G4 discovery (4 attempts per source cell per build):** 22/128 solved = 17.2 % (Wilson 95 % 11.6–24.7 %). Per-cell: 9, 5, 5, 3 of 32. Per-build yields 1, 1, 2, 2, 3, 3, 4, 6 of 16; **median 2.5/16, below the pre-stated 4/16 reading**, so the run reports a *discovery obstacle*. Only 2 of 8 builds reached 4/16.

**Adaptive batch (4 more attempts per cell under each build's own intermediate C4+F4):** 81/128 = 63.3 % (Wilson 54.7–71.1 %). Per-build 7–13 of 16.

| Build | First yield /16 | Intermediate empty cells | Intermediate library empty | Adaptive yield /16 | Final library |
|---|---:|---:|---|---:|---|
| 0 | 2 | 3 | yes | 8 | 32 fragments |
| 1 | 4 | 1 | no | 12 | 32 |
| 2 | 1 | 3 | yes | 9 | 32 |
| 3 | 2 | 3 | yes | 8 | 32 |
| 4 | 3 | 1 | no | 11 | 32 |
| 5 | 1 | 3 | yes | 7 | 32 |
| 6 | 3 | 1 | no | 13 | 32 |
| 7 | 6 | 1 | no | 13 | 32 |

- Four builds (0, 2, 3, 5) had an **empty intermediate fragment library** (corpus of 1–2 solvers, nothing recurring), so their 64 adaptive attempts ran with the C4 context table only, through the unchanged empty-library fallback. Those 64 attempts solved 32/64 (50 %); the 64 attempts with a non-empty library solved 49/64 (77 %).
- Adaptive attempts in cells with **no intermediate solution of their own** solved 35/64 (55 %), against 46/64 (72 %) in cells that had one. Both are far above the 17 % first-batch rate, so the intermediate refit helps even cells it had not solved; the four source cells share predicates, so this is within-family transfer, not evidence about new predicates.
- No build ended with an empty cell, corpus or library; all 8 final libraries hold 32 fragments of length 3–6 (for example `INPUT X3 INPUT`, `INPUT X1 ADD`, `ADD GT IF_GT`). The canonical solver is 16 tokens, so no fragment is a whole solution; A8 is not copying source programs.
- Acquisition cost per build: 8.7–14.2 M evaluations, 461–815 worker-s for the final source batch, mean 694 worker-s all-in. Fit and extraction are negligible (≤ 0.15 s). Exact-check tails in the source phases: ≤ 2.5 s per search, 2.8 s in total for the adaptive batch.

## 3. Development scoring (4 cells × 16 shared seeds per arm)

| Arm | Solved | Fraction (Wilson 95 %) | Geometric capped cost (failures 2 × cap) | Solved-only geometric cost | Mean worker-s per search |
|---|---:|---:|---:|---:|---:|
| G4 | 7/64 | 10.9 % (5.4–20.9) | 879 385 | 209 844 | 30.0 |
| A8 | 55/64 | 85.9 % (75.4–92.4) | 71 818 | 46 313 | 9.2 |
| O | 22/64 | 34.4 % (23.9–46.6) | 484 653 | 111 062 | 26.9 |

Per cell (solved of 16; geometric capped cost):

| Development cell | Pairing seen in sources? | G4 | A8 | O |
|---|---|---|---|---|
| (X0+X3)>(X1+X2) ? X1:X2 | yes (same predicate as a source) | 1 · 940 k | 16 · 35 k | 5 · 534 k |
| (X1+X2)>(X0+X3) ? X0:X1 | yes (flipped source predicate) | 2 · 928 k | 12 · 111 k | 8 · 368 k |
| (X1+X3)>(X0+X2) ? X2:X1 | **no** ({02|13} unseen) | 3 · 801 k | 13 · 133 k | 5 · 464 k |
| (X2+X3)>(X0+X1) ? X1:X3 | yes (same predicate as two sources) | 1 · 856 k | 14 · 52 k | 4 · 604 k |

Ratios of geometric capped cost, build-resampled bootstrap (8 192 draws; builds/artifacts as the unit, seeds resampled within build and cell, one shared cell-stratified G4 seed draw per replicate):

| Contrast | Point | 95 % interval | Same-seed pairs cheaper / dearer / both capped (n = 64) |
|---|---:|---:|---|
| G4/A8 | 12.2 | 6.7–20.7 | A8 cheaper in 55, dearer in 2, tie 7 |
| G4/O | 1.8 | 1.3–2.5 | O cheaper in 21, dearer in 5, tie 38 |
| O/A8 | 6.7 | 3.5–12.5 | A8 cheaper in 49, dearer in 11, tie 4 |

Sensitivity: with failures charged 1 × cap instead of 2 × cap the points are G4/A8 7.3, G4/O 1.5, O/A8 4.7. The ordering is not penalty-driven; the magnitudes are, since 57/64 G4 and 42/64 O rows are censored at the cap.

**Between-build variation.** A8 build mean log costs span 10.2–12.5 (SD 0.79 in natural log, a factor 2.2). Builds 3 and 5 solved 4/8 and 5/8; the other six solved 7–8/8. O artifacts are tighter (SD 0.35) and uniformly poor (1–5 of 8). Across the 8 builds, Spearman of adaptive source yield against development mean log cost is −0.52 and of first-batch yield against it is −0.05; with 8 points this is an observation only.

**Shortcut and verification tails.** G4 produced no training-perfect-but-wrong programs. A8 produced them in 3/64 searches (at most 40 distinct). O produced them in 10/64, one search with 78 764 distinct training-perfect failures and 16.6 s of exact checking. Total exact-check time in the score batch was 20 s of 4 227 worker-s, almost all from that one O row. The per-check maximum stayed at 2.2 ms.

**Diversity panels** (runner's `diagnostics.png`): best-correct-lexicase-case curves order A8 > O > G4 at every budget; distinct correctness patterns are similar across arms after 30 k evaluations. Nothing there contradicts the cost table.

## 4. Stage-2 price (conditional scenario, from `result.json`)

Inputs: A8 between-build log variance 0.63, G4 within-cell seed log variance 0.33, measured 9.2 effective workers, measured mean costs (acquisition 694 worker-s per build; G4 30, A8 9.2, O 26.9 worker-s per search). The target half-width factor is 1.25 on the protected G4/A8 ratio with 2 A8 seeds per build per protected cell and 8 protected cells.

| Scenario | Fresh builds | G4 seeds per protected cell | Half-width | Jobs (acq / G4 / A8) | Worker-s | Compute wall at 9.2 workers | Optional O extra |
|---|---:|---:|---:|---|---:|---:|---:|
| baseline grows with builds | 53 | 106 | 1.249 | 1 696 / 848 / 848 | 70 009 | 2.1 h | 22 809 worker-s (0.7 h) |
| baseline fixed 16 per cell | 64 | 16 | 1.249 | 2 048 / 128 / 1 024 | 57 695 | 1.7 h | 27 543 worker-s (0.8 h) |

With a fixed 16-seed G4 baseline the baseline alone contributes a floor factor of 1.105, so builds cannot be traded for baseline seeds indefinitely. Caveats as stated by the runner: development build variance is held constant and not divided over protected cells, pilot builds are not reusable as confirmation builds, and the scenario assumes protected cells behave like development cells, which 4 cells and 8 builds cannot establish. Either scenario fits well inside one `max_queue_hours` night but would need a sequential split (acquisition entry, then scoring entry) because acquisition must finish before scoring.

The pilot's own cost for reference: 448 searches, 9 780 worker-s of search (3 473 first, 2 080 adaptive, 4 227 development), 17.4 min of wall.

## 5. What the data shows

1. **The bank is buildable and the split is protected.** 24 separated cells under the real tokens, three executors agree on all 492 canonicals, and 8 protected cells with all three pairings exist unscored. The proposal's bank-obstacle condition (fewer than 12) is far from met.
2. **Discovery under `v2_x4` is sparse.** First-batch G4 solves one attempt in six (22/128); the per-build median of 2.5/16 is below the 4/16 reading the proposal fixed in advance. Four of eight builds could not form an intermediate fragment library. The recipe nonetheless completed every build with a full 32-fragment final library, because the intermediate context refit lifted the second batch to 63 %.
3. **G4 development headroom is at the bottom of the pre-stated 10–80 % band.** 7/64 = 10.9 %, interval 5.4–20.9 %. Per cell it is 1–3 of 16. The headroom condition is met by the point estimate only.
4. **A8 is far cheaper than G4 on development cells**, on the same seeds, in every cell, including the cell whose predicate pairing no source contains. The interval excludes the proposal's expected 1.5–3× range on the high side, but the magnitude is a censored-cost artefact: 57/64 G4 searches hit the cap.
5. **The eight reinterpreted 0145 artifacts are clearly costlier than fresh A8 builds** (O/A8 6.7, interval 3.5–12.5; A8 cheaper on 49 of 64 shared seeds) and only modestly better than G4 (G4/O 1.8, interval 1.3–2.5; 38 of 64 pairs both capped). Of the proposal's two O/A8 readings, the data matches *O clearly costlier*, not *old syntax already carries the help*.
6. **Build-to-build variation in A8 is large** (factor 2.2 SD on geometric cost; two of eight builds solve about half the development searches). This, not the G4 baseline, dominates the stage-2 price.

## 6. What the data does not show

- Nothing about protected cells. All contrasts are on 4 development cells chosen by hash, not sampled from the family, so the ratios are not a transfer estimate and must not enter the digest as one.
- Not that fresh acquisition is necessary in general. O was eight specific artifacts under a declared reinterpretation of their token ids; it says that *these* old libraries do not carry the double-sum help, not that no old library could.
- Not an isolated test of predicate placement. Alphabet, domain and family changed together, as the critic noted.
- Not a confirmed discovery rate. 22/128 with interval 11.6–24.7 % lies inside the proposal's expected 15–35 %; the per-build median reading (2.5/16) and the pooled rate (17 %) describe the same data, the reading is just the stricter of the two.
- Not a measurement of whether G4's unchanged prior is a fair baseline on this alphabet; G4's solved-only cost (210 k evaluations) is similar to the 0145 two-sum regime, but only 7 solves support it.
- The stage-2 price is a planning number conditional on development variance. 53–64 fresh builds and about 2 hours of compute is the central scenario, not a budget.

## 7. Figure

`analysis-figure.png` in this folder. Left: evaluations to exact solution per development cell and arm on the shared 16 seeds, unsolved counts as squares at 2 × cap. Right: per-build first-batch yield, adaptive yield and A8 development solves.

## Against the predictions

plan.md fixed interpretations in advance without an outcome table (probe). Taken in its order:

| Pre-stated reading (plan.md / proposal) | Observed | Match |
|---|---|---|
| Bank obstacle: fewer than 12 separated cells after the real screen or Rust validation; require a feasible 16-cell split | 24 separated cells, 16-cell split with the promised coverage, three executors agree on all 492 cells; SHAs in the data match the plan's frozen values | not met; bank clears the semantic precondition |
| Discovery obstacle: median first-batch G4 yield below 4/16 per build; report, do not raise attempts | median 2.5/16 (per-build 1–6); 22/128 pooled; attempts unchanged | **met**: discovery obstacle reported |
| Sparse discovery or empty fits identify limitations of the fixed recipe/prior | 4/8 builds had an empty intermediate library (C4-only adaptive batch); 0/8 had an empty final cell, corpus or library | partly: intermediate fits were thin, final fits were complete |
| Headroom: G4 development solve fraction in 10–80 % | 7/64 = 10.9 % (interval 5.4–20.9 %) | met by the point only; at the band's lower edge |
| Clear G4/A8 improvement motivates separately approved confirmation on protected cells; ambiguity needs a resolution price | G4/A8 12.2, interval 6.7–20.7; A8 cheaper on 55/64 shared seeds, every cell | clear on development cells |
| O/A8: unresolved from 1 with point ≥ 0.9 means old syntax carries the help; O clearly costlier means fresh acquisition is needed; G4/O needed to judge whether either fitted arm helps | O/A8 6.7 (3.5–12.5); G4/O 1.8 (1.3–2.5) | *O clearly costlier*; with the critic's narrowing this bounds only these eight reinterpreted artifacts |
| Stage-2 price: builds needed for a half-width factor ≤ 1.25 at measured log-SD, costed under measured load | 53 builds (growing baseline) or 64 builds (fixed 16-seed baseline); 58–70 k worker-s, about 2 h of compute, O optional at +0.7–0.8 h | reported as a conditional scenario |
| Expected: first-batch discovery 15–35 % | 17.2 % pooled | inside the expectation, yet below the 4/16 median reading |
| Expected: G4/A8 of 1.5–3× | 12.2×, 1 × cap sensitivity 7.3× | above expectation; the excess is censoring at the cap (57/64 G4 failures) |
| Expected: O between G4 and A8 | yes | as expected |
| Surprises named: A8 no better than G4, or O as good as A8 | neither occurred | none |
| Runtime: about 35 min of queue wall, 55 min of timeouts | 17.4 min wall, both entries admitted on runtime | under budget |

Two of the plan's readings pull in opposite directions and should be reported together to the steward: source discovery is below the fixed 4/16 reading (an acquisition limitation of the unchanged G4 prior on `v2_x4`), yet every build completed its library and the completed libraries made the development cells cheap. The plan's own rule applies: this is a development observation that returns to strategy, not a digest belief, and the protected cells remain unscored. Stage 2, if pursued, needs fresh builds and should expect the between-build spread seen here (two of eight builds about half as effective) rather than the 0145 regime.
