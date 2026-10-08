---
outcome: adopt_feedback
---

# Analysis: partial-program feedback vs equal-allocation one-shot (2026-10-08-2116)

Reviewer analysis of `experiments/output/2026-10-08/2026-10-08-2116-partial-program-feedback/`
(code `393a4dc`, queue exit 0, wall 11 991 s = 200 min against a 227-min smoke projection and an
18 000 s timeout). Every number below was recomputed from `search.jsonl`, `corpora.json` and
`freeze.json`; all agree with the runner's `result.json` and `report.md` to the printed precision.
Plot: [analysis_contrasts.png](analysis_contrasts.png) (left: per-lineage primary; right: all
contrasts under the three cost conventions). The runner's own figure is
`diagnostics.png` in the output folder.

## 1. Data completeness

Complete. Nothing is missing, duplicated, errored or mis-wired.

| Check | Expected | Found |
|---|---:|---:|
| Rows in `search.jsonl` | 20 480 | 20 480 (2 048 round-1 + 3 × 2 048 round-2 + 3 × 2 048 round-3 + 6 × 1 024 scoring) |
| Collection (lineage, cell, round, arm) groups × sources | 448 × 32 | 448 × 32 |
| Scoring (lineage, cell, arm) groups × seeds | 384 × 16 | 384 × 16, no duplicate (seed, arm) |
| Lineages / BE–PA pairs | 16 / 8 | 16 / 8, `stop_kind` null, `completed_pairs` 8 |
| Round-1 replay vs 1831 manifest | 16 lineages bit-exact | 16 / 16 passed (sources, counts, C1 and T1 table hashes) |
| Scoring table hash per row vs `freeze.json` | all match | 0 mismatches in 6 144 rows; G4 rows all carry the one G4 hash |
| Collection table hash (F under C(r−1), TF under T(r−1), O under G4) | all match | 0 mismatches in 14 336 rows |
| Training cases identical across paired arms | yes | 1 024 scoring seeds, 0 with differing `training_indices`; 13 312 pairing checks passed |
| Archive verifications / holdout searches / re-encoded starts | all / 0 / 0 | 607 040 / 0 / 0 |
| Empty cell-rounds | 0 | 0; lowest contributing cell-round 24 / 32 (F, round 3) |
| Caps | 65 536 collection, 524 288 scoring | as expected on every row |

### Acquisition per round (16 lineages × 4 cells, 2 048 attempted sources per round-arm)

| Round | Arm (table searched under) | Solved sources | Contributing sources | Evaluations used / allocated | Mean tape D1331 acc. | Later-solved share of archive | Mean fitted row entropy |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | G4 (shared replay) | 351 (17.1%) | 2 001 | 0.925 | 0.678 | 0.093 | C1 2.707 / T1 2.678 |
| 2 | F under C1 | 560 (27.3%) | 1 946 | 0.872 | 0.738 | 0.150 | C2 2.664 |
| 2 | TF under T1 | 434 (21.2%) | 1 963 | 0.898 | 0.721 | 0.107 | T2 2.610 |
| 2 | O under G4 | 322 (15.7%) | 2 002 | 0.931 | 0.685 | 0.083 | (no fit) |
| 3 | F under C2 | 620 (30.3%) | 1 911 | 0.847 | 0.746 | 0.158 | C3 = F 2.645 |
| 3 | TF under T2 | 440 (21.5%) | 1 966 | 0.902 | 0.731 | 0.114 | T3 = TF 2.576 |
| 3 | O under G4 | 330 (16.1%) | 1 991 | 0.925 | 0.680 | 0.082 | O (96 sources) 2.712 |

Pooled contributing sources per cell at the final fit: F 82–96 (mean 91.5), TF 87–96 (92.7),
O 90–96 (93.7) of 96 allocated. Training-perfect non-exact tapes were ≤ 0.5% of any archive.
Starvation did not occur, but allocation and use diverge as the proposal anticipated: F's new
rounds consumed 230.7 M source evaluations against O's 249.2 M (7.4% fewer), because F sources
solve about twice as often before the cap.

## 2. Key numbers

Unit: lineage (n = 16; 8 BE + 8 PA). Lineage score = mean over its 4 own training cells of the
mean over 16 paired fresh seeds of log cost(denominator arm) − log cost(numerator arm); cost =
evaluations to an exact D1331 solve, else 2 × 524 288. Interval: 95% t over the 16 lineage
scores. "Solved" is exact on all 1 331 rows.

### Solves per arm (1 024 scoring searches each = 16 lineages × 4 cells × 16 seeds)

| Arm | Solved | Rate | BE / PA solved (of 512 each) | Median cost of solved (evals) | Searches with ≥ 1 training-perfect non-exact tape |
|---|---:|---:|---|---:|---:|
| C_exact (1246 ceiling) | 940 | 91.8% | 451 / 489 | 36 224 | 82 |
| **F** (C3, three context rounds) | **762** | **74.4%** | 389 / 373 | 87 040 | 119 |
| R (= C1, 1831's C_S) | 745 | 72.8% | 377 / 368 | 97 280 | 102 |
| **O** (one fit to 96 G4 sources) | **736** | **71.9%** | 364 / 372 | 94 720 | 94 |
| TF (T3, three token rounds) | 671 | 65.5% | 334 / 337 | 112 384 | 89 |
| G4 | 631 | 61.6% | 294 / 337 | 143 360 | 57 |

### Contrasts (cost ratio, 95% interval; > 1 means the first-named arm is cheaper)

| Contrast | 2 × cap (primary) | 1 × cap | Both-solved pairs only (n pairs) | Lineages > 1 (2 × cap) |
|---|---|---|---|---:|
| **F / O (primary)** | **1.18 [1.01, 1.37]**, SD 0.28 log | 1.16 [1.01, 1.33] | 1.09 [0.95, 1.26] (561) | 11 / 16 |
| F / R | 1.16 [0.99, 1.36] | 1.15 [0.99, 1.32] | 1.12 [0.95, 1.32] (576) | 9 / 16 |
| O / R | 0.99 [0.89, 1.10] | 0.99 [0.90, 1.10] | 1.06 [0.90, 1.26] (553) | 7 / 16 |
| F / TF | 1.46 [1.23, 1.75] | 1.38 [1.19, 1.60] | 1.27 [1.09, 1.47] (533) | 14 / 16 |
| TF / G4 | 1.28 [1.14, 1.45] | 1.25 [1.14, 1.37] | 1.30 [1.15, 1.48] (453) | 15 / 16 |
| F / G4 | 1.88 [1.56, 2.26] | 1.72 [1.48, 2.01] | 1.71 [1.43, 2.05] (489) | 16 / 16 |
| F / C_exact | 0.31 [0.25, 0.38] | 0.35 [0.29, 0.41] | 0.45 [0.38, 0.52] (709) | 0 / 16 |
| R / G4 (replication of 1831 C_S / G4 on fresh seeds) | 1.62 [1.41, 1.86] | 1.50 [1.34, 1.68] | 1.43 [1.25, 1.63] (482) | 16 / 16 |
| O / G4 | 1.60 [1.44, 1.78] | 1.49 [1.36, 1.62] | 1.40 [1.17, 1.67] (476) | 16 / 16 |

Paired F vs O searches (1 024): F cheaper in 485, O cheaper in 452, tied (both capped) in 87.
Both solved 561, F only 201, O only 175, neither 87. Wilcoxon over the 16 lineage scores for
F / O: p = 0.039; for F / R: p = 0.083; for O / R: p = 0.90.

### By family (n = 8 lineages each, 2 × cap)

| Contrast | BE | PA |
|---|---|---|
| **F / O** | **1.42 [1.17, 1.72]**, 8 / 8 lineages > 1 | **0.98 [0.83, 1.16]**, 3 / 8 lineages > 1 |
| F / R | 1.31 (6 / 8 > 1) | 1.03 (3 / 8 > 1) |
| O / R | 0.92 (3 / 8 > 1) | 1.05 (4 / 8 > 1) |

Per-lineage F / O (2 × cap): BE 1.09, 1.34, 1.24, 1.29, 1.47, 1.94, 2.06, 1.18;
PA 0.97, 0.94, 1.10, 0.94, 1.05, 0.82, 1.43, 0.72.

### By training cell (128 searches per arm per cell, 8 lineages pooled; descriptive)

| Cell | F / O | Solved F / O / R / TF / G4 of 128 |
|---|---:|---|
| BE:F>S?F:M+m | 1.60 [1.01, 2.53] | 82 / 65 / 78 / 50 / 54 |
| BE:F>m?S:F+M | 1.12 [0.89, 1.39] | 95 / 90 / 90 / 91 / 80 |
| BE:S>F?M:F+m | 1.43 [0.78, 2.63] | 103 / 98 / 93 / 90 / 66 |
| BE:S>F?m:M+S | 1.57 [0.94, 2.63] | 109 / 111 / 116 / 103 / 94 |
| PA:(F>S?F:m)+M | 1.17 [0.63, 2.15] | 72 / 63 / 66 / 48 / 58 |
| PA:(F>S?m:M)+F | 0.87 [0.64, 1.19] | 97 / 96 / 94 / 80 / 74 |
| PA:(M>F?m:S)+S | 1.12 [0.79, 1.58] | 105 / 107 / 104 / 101 / 106 |
| PA:(S>F?M:m)+m | 0.81 [0.60, 1.08] | 99 / 106 / 104 / 108 / 99 |

### Pricing (from the runner's `sizing` and `payback` blocks, checked)

- Lineages needed to put the F / O lower bound above 1.15 at the observed point estimate and SD:
  about 600 (584 more, ≈ 7 400 queue minutes). Not a practical follow-up.
- Payback: F's extra acquisition (230.7 M evaluations beyond round 1) saves a mean 18 680
  penalized evaluations per scored search over R, so about 12 350 future searches on these
  cells to repay. O's extra acquisition saves nothing (mean −11 050 vs R).

## 3. What the data shows

1. **Feedback beats equal-allocation one-shot on the primary endpoint, but only just.** F / O =
   1.18 [1.01, 1.37]; the lower bound clears 1 by 1%, and the 1 × cap convention gives the same
   picture (1.16 [1.01, 1.33]). Among pairs where both arms solved, F / O is 1.09 [0.95, 1.26]:
   as in 1831, the penalized gain is mostly a within-cap reliability gain (74.4% vs 71.9% solves,
   +26 solves) rather than a speed gain. The point estimate is at the 1.15 margin; a worthwhile
   gain is neither established nor excluded.

2. **The gain is entirely a BE result.** BE: F / O 1.42 [1.17, 1.72], all 8 lineages above 1.
   PA: 0.98 [0.83, 1.16], 3 of 8 lineages above 1, and PA solves are F 373 / O 372 / R 368 of
   512. On the PA family the three arms are indistinguishable at this n. This is the same
   family split 1831 reported for C_S / T_S (BE 1.42, PA 1.15), now sharper: the PA interval here
   is centred on 1.

3. **More G4 data does not help; whether feedback beats the first fit is unresolved.**
   O / R = 0.99 [0.89, 1.10]: tripling the G4 source allocation leaves the frozen decoder
   unchanged (an effect above 1.10× is excluded). F / R = 1.16 [0.99, 1.36] does not exclude 1.
   So the primary F / O result is "F > O" with O ≈ R; read together, the extra two rounds under
   feedback bought a gain that is resolved against the equal-allocation control and unresolved
   against doing nothing further. The two contrasts have nearly the same point estimate; the
   difference in resolution is interval width, not effect size.

4. **Token feedback is a poor substitute for context feedback.** F / TF = 1.46 [1.23, 1.75],
   14 / 16 lineages. TF / G4 = 1.28 [1.14, 1.45] matches 1831's one-shot T_S / G4 (1.27) and
   TF solves 671 / 1 024 against T_S's 674 in 1831 (different seeds; descriptive): three token
   rounds are no better than one. TF also trails R (745 solves).

5. **Feedback moves little toward the exact-corpus ceiling.** F / C_exact = 0.31 [0.25, 0.38]
   versus R / C_exact ≈ 0.26 here (1831: C_S / C_exact 0.27). Two feedback rounds close about
   one tenth of the log gap between the first partial fit and the exact fit. C_exact's acquisition
   cost is unmatched (per 1831's decision, ≈ 7.9× the per-cell source evaluations of one partial
   round), so this is a gap statement, not an efficiency comparison.

6. **The acquisition mechanics behaved as the feedback hypothesis predicts, in both families.**
   Sources run under C1 / C2 solve before the cap about twice as often as under G4 (27–30% vs
   16%), their archived tapes are more accurate (D1331 0.74–0.75 vs 0.68) and a larger share of
   archives come from sources that later solved (15–16% vs 8%). The fitted rows get slightly
   sharper (C3 entropy 2.645 vs O 2.712). None of this separates BE from PA (PA round-3 F tapes
   are the most accurate of all, 0.762), so the BE/PA split in the scored outcome is not a
   collection-yield difference.

7. **Shortcuts do not inflate the endpoint and did not grow out of hand.** Searches that hit at
   least one training-perfect non-exact tape: F 119, R 102, O 94, TF 89, C_exact 82, G4 57 of
   1 024. F is highest, consistent with a sharper prior, but exactness on D1331 is required for
   a solve, and F's solve count is also highest. Training-perfect tapes were ≤ 0.5% of any
   collected archive, so reinforced shortcuts in the corpus (explanation C) are not visible.

8. **Replication check passed.** R is bit-for-bit 1831's C_S table scored on 1 024 fresh seeds:
   745 solves vs 746, R / G4 1.62 [1.41, 1.86] vs 1.62 [1.37, 1.90]; G4 631 vs 624; C_exact
   940 vs 925. The 1831 result replicates on a second seed set.

9. **Capping caution does not apply.** Non-exact arms solve 62–74% of searches; the
   `almost_all_primary_capped` flag is false.

## 4. What the data does not show

- Not a worthwhile (≥ 1.15×) gain from feedback: the lower bound is 1.01, the runner's sizing
  says ≈ 600 lineages to establish the margin from this estimate, and the practical case is
  weaker than the label suggests (F / R unresolved, PA null, both-solved unresolved).
- Not a result on PA. Half the bank shows nothing; a decision that rests on the F / O lower bound
  rests on the BE family alone.
- Not a per-evaluation efficiency result: the allocation was equal but F used 7.4% fewer source
  evaluations than O, and C_exact's budget is far larger. F's modest payback (≈ 12 350 future
  searches) is penalized-cost accounting on these same cells.
- Not transfer, not order, not inheritance: development bank, own training cells, no holdout,
  no fresh bank, K unscored, external fitting only. F vs O compares collection procedures with
  yield and tape content bundled.
- Not a horizon or round-count result: one collection cap (65 536), three checkpoints, three
  rounds. Whether more rounds, different checkpoints or a per-round evaluation budget (to
  remove the use/allocation gap) would change F is untested.
- The both-solved and per-cell numbers are selection-conditioned or small-n and are
  decompositions, not tests.

## 5. Pre-stated routing (proposal rule, as implemented in `route`)

F / O upper bound 1.37 (not < 1, not < 1.15); lower bound 1.01 > 1; point estimate 1.18 ≥ 1.15.
This lands in the proposal's first branch, "feedback becomes the acquisition route, graded by
its point estimate against 1.15"; the plan's precedence labels it a resolved improvement with the
worthwhile gain not established. The grade is marginal on every secondary reading listed above,
and the steward should treat the label as "F > O on BE, at a point estimate near the margin",
not as an established route.

## Against the predictions

plan.md's precedence has five labels for F / O: degradation (UB < 1), small gain / prefer O
(UB < 1.15), resolved improvement with LB > 1 split into adopt-F-provisionally (point ≥ 1.15;
worthwhile only if LB > 1.15) and prefer-O-at-estimate (point < 1.15), else unresolved. The data
match **adopt_feedback, provisional**: UB 1.37, LB 1.01, point 1.18, LB not above 1.15, so the
worthwhile gain is not established. The runner's `route` returned the same label.

The plan's preconditions for reading the cost endpoint were met: all 16 lineages complete, every
round-1 lineage replayed bit-exactly, no empty cell-round, no restart or top-up, the 1 × cap and
both-solved sensitivities reported, and the near-universal-capping situation absent
(62–74% solved in the non-exact arms). The plan's secondary readings resolve as: F / R does not
separate retention from extra acquisition (interval spans 1); O / R says added G4 data adds nothing
(above 1.10× excluded); F / TF says the context update beats the token update clearly.

Against the proposal's stated expectations:

| Expectation | Observed | Verdict |
|---|---|---|
| O / R ≈ 1.05–1.15× (more G4 tapes add a little) | 0.99 [0.89, 1.10] | Below expectation: more G4 tapes add nothing measurable |
| F / O ≈ 1.1–1.3× | 1.18 [1.01, 1.37] | Point estimate inside the range; the interval reaches down to 1 |
| F / TF > 1 | 1.46 [1.23, 1.75], 14 / 16 lineages | As expected, larger than 1831's one-shot C / T gap (1.28) |
| Surprise: F < O (reinforced shortcuts) | F > O overall; PA alone 0.98 [0.83, 1.16] | Did not occur overall; on PA the arms are indistinguishable, which the proposal did not anticipate |
| Surprise: F ≥ C_exact / 2 | F / C_exact 0.31 [0.25, 0.38] | Did not occur; feedback closes about a tenth of the first fit's log gap to the exact fit |
| Surprise: TF ≈ F | F / TF 1.46 | Did not occur |
| Starvation low; ≥ 16 contributing sources per cell | 82–96 of 96 pooled per cell; F used 7.4% fewer evaluations than O | As expected; no starvation |

Two things the plan did not anticipate and the steward should weigh:

- **The provisional label rests on the BE family and on a 1% margin.** BE: 1.42 [1.17, 1.72],
  8 / 8 lineages; PA: 0.98 [0.83, 1.16], 3 / 8. The proposal's decision rule has no family
  clause, so the label stands as routed, but adopting feedback as "the acquisition route" would
  be adopting it for half the bank on current evidence. The collection diagnostics (source solve
  rate, tape accuracy, later-solved share) improve under feedback in PA as much as in BE, so the
  PA null is not explained by yield; it sits in what the PA tapes teach.
- **F / R is unresolved while F / O is resolved, with the same point estimate.** Because O ≈ R,
  the equal-allocation control and the retain-first-fit control are the same comparison in
  practice; the plan treated them as separating retention from extra acquisition. The honest
  summary is one effect of ≈ 1.16–1.18× with its lower bound on 1, not two findings.

The plan's "price needed lineages" clause applies to the unresolved label; the runner priced the
1.15 margin anyway at ≈ 600 lineages, which rules out resolving it by replication. A PA-only
follow-up would need a different design question (why PA tapes do not teach), not more of this one.
