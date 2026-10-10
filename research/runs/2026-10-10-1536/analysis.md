---
outcome: "useful protected-cell replication on x4-double-gate-v1, relative to G4 at this cap"
---
# Analysis: fresh A8 builds on the independent-input double-gate family, scored on the 8 protected cells (stage 2)

Code commit `7244fa1` on `research/2026-10-10-1536`. Data: `experiments/output/2026-10-10/2026-10-10-1536-independent-input-prepare/` (24 fresh builds, 768 source searches, fits) and `.../2026-10-10-1536-independent-input-score/` (896 protected searches, `result.json`, `report.md`). Every number below was recomputed from `first.jsonl`, `adaptive.jsonl`, `source_summary.json` and `search.jsonl`; all agree with the runner's `result.json` to the printed precision, including an independent re-implementation of the build-resampled bootstrap (2 000 draws: 7.56–13.29 against the runner's 7.60–13.15).

## 1. Data completeness

Both entries finished with exit 0 inside their timeouts; `search.jsonl`, `timing.json` and `diagnostics.png` (the outputs the code review asked me to check explicitly) are all present.

| Entry | Wall | Timeout | Effective workers (of 10) |
|---|---:|---:|---:|
| prepare (validation + 768 source searches + fits) | 1 902 s | 3 000 s | 9.7 / 9.8 |
| score (896 protected searches + bootstrap + plot) | 1 893 s | 4 200 s | 9.8 |

- **Freeze and provenance.** Preparation passed Python/Rust/semantic validation (492 canonicals and witnesses, 7 240 depth-3 programs, 10 000 random tapes) and froze bank, O artifacts, source and scoring schedules, method hashes, builds and the admission record before any protected search (`frozen_before_search: true`). Admission was runtime-only (projected 3 109 s ≤ 4 170 s); the discovery-obstacle reading was recorded but did not gate. The scoring entry re-verified the hashes and ran at the same commit. `protected_performance_scored` flipped to true only after the batch.
- **Protected cells were unsearched.** None of the eight protected cell labels appears in any 0311 jsonl (prepare or score). This run's own source phase targets only the four source cells.
- **Acquisition.** 384 first-batch rows and 384 adaptive rows: exactly 24 builds × 4 source cells × 4 attempts per phase, no duplicates. Seeds 500000–523033 and 600000–623033 as specified, disjoint from each other, from scoring and from 0311's blocks. All 24 builds completed with a final context table and a non-empty library; no build was replaced.
- **Scoring.** 896 rows = 8 cells × (48 G4 + 48 A8 + 16 O), no duplicates, no missing or extra rows against the frozen `schedule.json`. Seeds follow 700000 + 1000·cell + ordinal; G4 and A8 share every (cell, ordinal) seed and O uses the first 16 of them. A8 build = ordinal // 2 (24 builds × 2 seeds per cell); O artifacts 0–7 × 2 seeds per cell. One G4 table hash across all 384 G4 rows (fixed prior); 24 distinct A8 table/library hashes; 8 distinct O table/library hashes. No `empty_library_fallback`, no `initial_reencoded` in scoring.
- **Solved semantics.** `solved` requires the exact check on all 625 inputs and the runner re-verifies every solver (raises on mismatch). Every unsolved row sits at exactly 524 288 evaluations; no solved row reached the cap. Zero rows with errors.
- **Shortcut tails.** Training-perfect-but-wrong programs occurred in 16/384 G4, 25/384 A8 and 9/128 O searches; three searches had very long exact-check tails (G4 122 384 checks, 23 s; O 66 893; A8 57 679). Total exact-check time was 107 s of 18 522 worker-s; the per-check maximum stayed at 4.8 ms. No shortcut passed the 625-input check.

Nothing is missing, duplicated or silently substituted.

## 2. Acquisition (24 fresh builds)

| Phase | Solved / attempts | Fraction | Per-cell solved of 96 |
|---|---:|---:|---|
| First batch (G4, 4 attempts per source cell per build) | 64 / 384 | 16.7 % | 15, 19, 14, 16 |
| Adaptive batch (4 more under each build's intermediate C4+F4) | 218 / 384 | 56.8 % | 61, 51, 58, 48 |

- Per-build first-batch yield: median 2 of 16 (range 1–6); 10 of 24 builds yielded exactly 1. The pre-stated 4/16 reading was met by 7 builds, so the run again reports a discovery obstacle (recorded, non-gating).
- **Eight builds (0, 2, 3, 4, 5, 9, 16, 23) had an empty intermediate library** and ran their adaptive batch on the context table alone through the unchanged fallback (128 of 384 adaptive attempts). These eight builds solved 3–10 adaptive attempts of 16 against 7–15 for the other sixteen.
- Final libraries: 18 builds hold the 32-fragment maximum; builds 0, 3, 4, 9, 16 and 23 ended with 22, 13, 31, 27, 17 and 7 fragments. Six builds ended with 1–2 source cells never solved (`final_empty_cells`), differently from the pilot where none did. Fragments are 3–6 tokens (387 / 192 / 84 / 30 by length); the tape is 32 tokens, so no fragment is a whole solution.
- Cost: 8.5–15.8 M evaluations per build, mean 12.5 M; 529–992 worker-s per build, mean 772 (the proposal planned on 694). Fits and extraction ≤ 0.2 s.

## 3. Protected scoring (8 cells)

Pooled over all 8 protected cells (failures charged 2 × cap unless stated):

| Arm | Solved / attempts | Fraction (descriptive Wilson 95 %) | Capped / attempts | Solved-only geometric cost | Mean worker-s per search |
|---|---:|---:|---:|---:|---:|
| G4 | 63 / 384 | 16.4 % (13.0–20.4) | 321 / 384 | 192 823 | 29.4 |
| A8 | 317 / 384 | 82.6 % (78.4–86.0) | 67 / 384 | 45 589 | 10.8 |
| O | 58 / 128 | 45.3 % (37.0–53.9) | 70 / 128 | 86 721 | 24.0 |

Primary comparison and the two descriptive contrasts (geometric mean of per-cell geometric capped cost; build-resampled bootstrap, 8 192 draws, builds resampled with replacement, 2 seeds resampled within build and cell, one shared cell-stratified G4 seed draw per replicate, O resampled within BE/PA strata):

| Contrast | Point (2 × cap) | 95 % interval | Point (1 × cap) | 95 % interval (1 × cap) | Same-seed pairs: A8 cheaper / G4 cheaper / both capped |
|---|---:|---:|---:|---:|---|
| **G4 / A8″** | **10.08** | **7.60 – 13.15** | 6.37 | 5.02 – 8.03 | 307 / 23 / 54 of 384 |
| G4 / O | 2.34 | 1.64 – 3.48 | 1.92 | 1.45 – 2.63 | – |
| O / A8″ | 4.30 | 2.68 – 6.61 | 3.32 | 2.25 – 4.74 | – |

The lower bound of the primary interval is above the pre-set 1.5 margin under both failure charges, so the label is not penalty-sensitive. Per-cell detail (solved count; geometric capped cost in thousands of evaluations):

| Protected cell | Pairing | G4 (of 48) | A8″ (of 48) | O (of 16) | G4/A8″ 2 × cap | 1 × cap |
|---|---|---|---|---|---:|---:|
| (X0+X1)>(X2+X3) ? X2:X1 | seen {01\|23} | 5 · 929 k | 34 · 89 k | 7 · 322 k | 10.4 | 6.8 |
| (X0+X1)>(X2+X3) ? X2:X3 | seen {01\|23} | 5 · 859 k | 44 · 61 k | 5 · 587 k | 14.2 | 8.1 |
| (X0+X2)>(X1+X3) ? X3:X0 | **unseen {02\|13}** | 11 · 676 k | 39 · 107 k | 7 · 421 k | 6.3 | 4.2 |
| (X0+X3)>(X1+X2) ? X0:X3 | seen {03\|12} | 9 · 736 k | 41 · 67 k | 8 · 350 k | 10.9 | 6.9 |
| (X0+X3)>(X1+X2) ? X2:X1 | seen {03\|12} | 11 · 751 k | 42 · 72 k | 6 · 278 k | 10.4 | 6.7 |
| (X1+X3)>(X0+X2) ? X0:X1 | **unseen {02\|13}** | 8 · 810 k | 38 · 121 k | 6 · 285 k | 6.7 | 4.3 |
| (X1+X3)>(X0+X2) ? X1:X3 | **unseen {02\|13}** | 9 · 740 k | 38 · 101 k | 7 · 355 k | 7.3 | 4.8 |
| (X2+X3)>(X0+X1) ? X0:X1 | seen {01\|23} | 5 · 886 k | 41 · 43 k | 12 · 222 k | 20.6 | 12.2 |

Subgroups (descriptive, no decision rule):

| Subgroup | G4 solved | A8″ solved | O solved | G4/A8″ (95 %) | O/A8″ (95 %) |
|---|---:|---:|---:|---:|---:|
| 3 unseen-pairing cells | 28 / 144 (19.4 %) | 115 / 144 (79.9 %) | 20 / 48 (41.7 %) | 6.76 (4.94–9.24) | 3.19 (1.76–5.44) |
| 5 seen-pairing cells | 35 / 240 (14.6 %) | 202 / 240 (84.2 %) | 38 / 80 (47.5 %) | 12.81 (8.99–17.76) | 5.15 (2.90–9.02) |

The three unseen-pairing cells are the three cells with the smallest ratios, but A8″ still solved about four in five searches there and the subgroup interval sits well above 1.5. G4 happens to solve the unseen cells slightly more often than the seen ones, so part of the subgroup gap is a baseline difference, not only a weaker A8″.

**Between-build variation.** A8″ build mean log cost SD 0.62 (natural log; factor 1.85), compared with 0.79 in the pilot. Per-build geometric capped cost on the protected cells ranges from 24 k (build 8) to 427 k (build 16), a factor 18. Per-build solved counts are 8–16 of 16; build 16 at 8/16 is the only build below 9. Against the pooled G4 baseline every one of the 24 builds has a ratio above 1.5 at 2 × cap (range 1.9–33.6, median 11.3); at 1 × cap 23 of 24 do and build 16 sits at 1.5 exactly. The eight builds with an empty intermediate library have a pooled geometric cost of 119 k against 64 k for the other sixteen (solved 96/128 vs 221/256); Spearman of first-batch yield against build log cost is −0.44 (24 builds, descriptive). Builds 0, 3 and 5 contradict the simple yield story: each solved 1 of 16 first-batch attempts and had an empty intermediate library, yet their protected costs (60–73 k) are at the pooled A8″ level. O artifacts are uniformly weak: 4–12 of 16 per artifact, build log SD 0.52.

**Economics (arithmetic evaluations, failures at cap).** Mean search cost G4 479 k, A8″ 167 k, O 350 k evaluations; mean acquisition 12.5 M evaluations per build. The saving per search is 313 k evaluations, so one build repays its acquisition after about 40 protected searches (per-build range 26–144; build 16 is the 144). The 16 protected searches scored per build in this design do not repay acquisition; this is an accounting statement about a 24-build design, not a claim about deployment.

**Diagnostics** (`diagnostics.png` in the score folder): best-correct-lexicase-case curves order A8 > O > G4 at every budget; distinct correctness patterns are similar after 30 k evaluations. Consistent with the cost table.

**Resolution price:** not needed (`needed: false`).

## 4. Comparison with the stage-1 pilot (development cells, 8 builds)

| Quantity | Pilot (0311, 4 development cells) | This run (8 protected cells) |
|---|---:|---:|
| G4/A8 point, 2 × cap | 12.2 (6.7–20.7) | 10.1 (7.6–13.1) |
| G4/A8 point, 1 × cap | 7.3 | 6.4 |
| A8 solved | 55/64 = 85.9 % | 317/384 = 82.6 % |
| G4 solved | 7/64 = 10.9 % | 63/384 = 16.4 % |
| O solved | 22/64 = 34.4 % | 58/128 = 45.3 % |
| First-batch source yield | 22/128 = 17.2 % | 64/384 = 16.7 % |
| Empty intermediate libraries | 4 of 8 | 8 of 24 |

The protected result is slightly smaller than, and consistent with, the development pilot. Nothing in stage 1 was tuned on the protected cells (never searched before this run), and the 24 builds are new.

## 5. What the data shows

1. **Fresh A8 builds on the independent-input family are clearly cheaper than the fixed G4 prior on all eight protected cells**, on shared seeds, with the primary interval 7.6–13.1 at 2 × cap and 5.0–8.0 at 1 × cap, both above the pre-set 1.5 margin. The label is not penalty-sensitive, although the magnitude is: 321/384 G4 searches are censored at the cap, so the point estimates are capped-cost ratios, not time-to-solution ratios.
2. **The gain holds on the three cells whose predicate pairing no source cell contains**, at a smaller size (6.8, 4.9–9.2) than on the five seen-pairing cells (12.8, 9.0–17.8). The surprising outcome the proposal named (unseen cells no better than G4) did not happen.
3. **Every one of 24 independent builds beats the pooled G4 baseline by more than 1.5× at 2 × cap**, despite median first-batch yield of 2/16 and eight empty intermediate libraries. Build quality still varies by a factor 18 in geometric cost, and the sparse-discovery builds are costlier on average, but even the weakest build (16) clears the margin at 2 × cap and sits at it at 1 × cap.
4. **The eight reinterpreted old-family artifacts (O) are between the two**: better than G4 (2.3, 1.6–3.5) and clearly worse than fresh builds (O/A8″ 4.3, 2.7–6.6). As in the pilot, these specific old libraries do not carry the double-sum help.
5. **Discovery on this alphabet stays sparse and the recipe tolerates it.** First-batch yield 64/384 matches the pilot's 22/128; all 24 builds still produced usable artifacts.

## 6. What the data does not show

- Not fresh-bank transfer or general recipe portability. `x4-double-gate-v1` is a development bank (the critic's note 2); this is a within-bank confirmation on cells that had not been scored, relative to G4 at this cap, on one family and one alphabet.
- Not an attribution to context table versus fragments versus token supply: all are bundled in A8; O's token reinterpretation prevents a family-specificity reading.
- Not an isolated effect of predicate placement: alphabet, domain and family changed together relative to the output-addition banks.
- Not that G4 is a competitive baseline on `v2_x4`: it is the supplied prior with 84 % of searches capped; a stronger uninformed baseline would shrink every ratio by an unknown amount.
- Not a causal yield-to-quality relation: 24 builds, Spearman −0.44, with three low-yield builds performing at the pooled level.
- Not a wall-time saving: A8″ searches took 10.8 worker-s against G4's 29.4, but acquisition cost 772 worker-s per build and the repayment number above is arithmetic evaluations only.
- The subgroup and per-build numbers are descriptive; no decision rule was pre-set for them.

## 7. Figure

`analysis-figure.png` in this folder. Left: evaluations to exact solution per protected cell and arm on the shared seeds, unsolved counts as squares at 2 × cap (unseen-pairing cells starred). Middle: per-build A8″ geometric capped cost against first-batch yield, empty-intermediate builds in red, pooled G4 and O as dashed lines. Right: per-build G4/A8″ ratio at both failure charges against the 1.5 margin.

## Against the predictions

plan.md fixed one decision rule and several interpretations. Taken in order:

| Plan statement | Data | Match |
|---|---|---|
| Primary: lower 95 % bound of R = G4/A8″ > 1.5 → **useful protected-cell replication on x4-double-gate-v1, relative to G4 at this cap** | R = 10.08, interval 7.60–13.15 | **Yes.** This is the label. |
| Repeat at 1 × cap; flag a label change as penalty-sensitive | R = 6.37, interval 5.02–8.03; same label | Not penalty-sensitive. The magnitude is still censoring-inflated (321/384 G4 at cap) and must be read as a capped-cost ratio, not time to solution, as the plan says. |
| Unresolved / not worthwhile branches, conditional resolution price | Neither branch triggered; `needed: false` | Not applicable. |
| "Failure specifically on the three unseen-pairing cells leaves new-pairing assembly unresolved even if the pooled result is useful" | Unseen cells: A8″ 115/144 solved, G4/A8″ 6.76 (4.94–9.24), descriptive | The condition did not occur. The unseen cells are the three weakest for A8″, but the recipe helped them clearly; no subgroup decision was pre-set, so this stays a descriptive observation that the surprise named in the proposal (unseen cells no better than G4) did not happen. |
| "Mostly capped arms and a ratio near one say little about uncapped difficulty" | A8″ capped 67/384 (17 %); G4 capped 321/384 | A8″ is far from mostly capped, so the comparison is informative on the A8″ side; the G4 side is a censored baseline, which is why the 1 × cap repeat matters. |
| Sparse acquisition is a mechanism risk, not a gate; retain all fallbacks | First yield 64/384, median 2/16; 8/24 empty intermediate libraries kept; admission was runtime-only | Followed. The weakest build (16, empty intermediate, 17 fragments) still clears 1.5 at 2 × cap and sits at 1.5 at 1 × cap, so sparse discovery degraded but did not defeat any build. |
| Repayment: arithmetic evaluations once per build, no wall-time claim | 40 searches per build (range 26–144) | Reported as such; no wall-time saving claimed. |
| Scope: within-bank confirmation only, no fresh-bank transfer, portability, inheritance or context/fragment/supply isolation; O/A8 cannot isolate family specificity | – | Respected throughout §5–6. The question's `fresh-transfer` tag is still wrong (critique note 7, flagged for the steward). |
| Proposal's expectation: R clearly above 1.5, point 4–10×, A8 solving most, G4 under 20 %, unseen cells helped but less, O between | R 10.1 (6.4 at 1 × cap), A8″ 82.6 %, G4 16.4 %, unseen 6.8 vs seen 12.8, O 2.3× over G4 and 4.3× under A8″ | Every expectation met; the 2 × cap point is at the top edge of the expected 4–10 range. |

Frozen-artifact check: the plan's source-schedule, scoring-schedule, bank and O SHA-256 values are byte-identical to those in `preparation.json`, and `protected_performance_scored` was false in every pre-run artifact (smokes and the plan) and true only in the scoring result. The outcome label is the plan's positive label. One critique item for the steward remains open outside this folder: question 40's tag `fresh-transfer` should become `protected-replication`, and 39's log should not attribute O/A8 to G4 censoring.
