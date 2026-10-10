---
outcome: "material geometric family interaction (2 × cap; one resolved direction, DG-built cohort preferred on DG; TS direction unresolved; not reciprocal; no dominant bias; penalty-sensitive, unresolved at 1 × cap)"
---
# Analysis: crossed family preference on one alphabet (DG-built vs TS-built A8, 8 spare DG cells + 8 TS target cells)

Code commit `b5697a1` on `research/2026-10-10-1717` (clean tree). Data: `experiments/output/2026-10-10/2026-10-10-1717-family-preference-prepare/` (TS bank, 24 fresh TS builds, 768 source searches, 96 calibration searches, freeze) and `.../2026-10-10-1717-family-preference-score/` (2 304 target searches, `result.json`, `report.md`, `dynamics.png`). Every number below was recomputed from `first.jsonl`, `adaptive.jsonl`, `calibration.jsonl`, `source_summary.json`, `banks.json` and `search.jsonl`; all agree with the runner's `result.json` to the printed precision, including an independent re-implementation of the hierarchical bootstrap (2 000 draws: I 1.62–2.38 against the runner's 1.58–2.44 at 8 192 draws; P_DG 2.12–4.19 vs 2.07–4.33; P_TS 0.96–1.73 vs 0.94–1.78).

Figures in this folder: `per_cell_costs.png` (per-cell geometric capped cost, three arms, both rosters) and `per_build_cross_roster.png` (each build's cost on the DG roster against its cost on the TS roster).

## 1. Data completeness

Both queue entries finished with exit 0 well inside their timeouts, and every `expect_outputs` file is present.

| Entry | Wall | Timeout | Effective workers (of 10) |
|---|---:|---:|---:|
| prepare (screens + 768 TS source searches + fits + 96 calibration searches) | 1 065 s | 4 800 s | 9.0–9.4 |
| score (2 304 target searches + bootstrap + plot) | 3 426 s | 8 400 s | 9.8 |

- **Banks.** The TS screen (`x4-branch-sum-v1`) completed exhaustively at ≤ 9 tokens on D625 (216 role-assignment cells, 106 s), the 80 % rule gave a maximum clique of 108, and the deterministic split is 4 source / 4 development / 8 target. The DG bank was regenerated in-run (492 cells, clique 24) and its hash matched the frozen artifact. Python/Rust/semantic validation passed (7 240 depth-3 programs, 10 000 random tapes, 708 canonical and witness cells). The alias check (no target label equal to any source label or to the output of any acquired source solver, both before and after TS acquisition) raises on failure and did not; preparation recorded `admitted: true` with an empty reasons list.
- **DG provenance.** The 24 D builds are the 1536 builds (commit `7244fa1`), loaded with hash verification against the 1536 prepare output; the code review confirmed the files byte-identical. The 8 DG targets are the clique cells outside the 1536 source/development/protected split and appear in no earlier jsonl.
- **TS acquisition.** 384 first-batch rows (seeds 900000–923033) and 384 adaptive rows (1000000–1023033): exactly 24 builds × 4 source cells × 4 attempts per phase, no duplicates, no `empty_library_fallback`. All 24 T builds reached the 32-fragment maximum library; none had an empty intermediate library; one build (19) ended with one source cell never solved.
- **Calibration and admission.** 96 development-cell searches cycling all 24 builds of each cohort (16 per family × arm). Measured rates: DG G4 30.4 s, D 7.9 s, T 26.9 s; TS G4 14.9 s, D 3.0 s, T 2.6 s. Projected scoring 4 839 s ≤ 8 370 s. The gate was price-only, as planned.
- **Scoring.** 2 304 rows = 16 cells × 48 ordinals × 3 arms, no duplicates, no missing or extra rows against the frozen `schedule.json`. Seeds 1200000–1215047, 768 distinct, shared across G4/D/T for each (cell, ordinal); build = ordinal // 2 (2 seeds per build per cell). One G4 table hash in all 768 G4 rows; 24 distinct D and 24 distinct T table/library hashes. No `initial_reencoded`, no errors. All 749 unsolved rows sit at exactly 524 288 evaluations; no solved row reached the cap. `solved` requires the exact check on all 625 inputs.
- **Shortcut tails.** Training-perfect-but-wrong programs occurred in 14/384 G4, 36/384 D and 50/384 T searches on DG and 32/384, 17/384 and 28/384 on TS; none passed the 625-input check. Total exact-check time was 212 s of 33 584 worker-s; one D search on DG spent 40 s verifying. Nothing is distorted by verification cost.

Nothing is missing, duplicated or silently substituted.

## 2. Acquisition: the two cohorts are not equally hard to build

| Cohort | First batch solved / 384 (G4 on 4 sources) | Adaptive solved / 384 | Median first yield of 16 per build | Empty intermediate libraries | Final library 32/32 | Evaluations per build (M) | Worker-s per build |
|---|---:|---:|---:|---:|---:|---:|---:|
| D (DG sources, 1536) | 64 (16.7 %) | 218 (56.8 %) | 2 | 8 of 24 | 18 of 24 | 12.5 (8.5–15.8) | 771 |
| T (TS sources, this run) | 242 (63.0 %) | 343 (89.3 %) | 10 | 0 of 24 | 24 of 24 | 6.1 (3.9–7.8) | 307 |

G4 solves TS sources almost four times as often as DG sources. The TS cohort was therefore built from a far richer solver corpus at half the evaluation cost, and the runner correctly recorded no discovery obstacle for T (obstacle for D, as in 1536). Per source cell the T first batch solved 75, 70, 28 and 69 of 96; `X2>X3?(X0+X2):(X1+X3)` is the hard TS source (28, then 60 adaptive).

## 3. Target scoring (16 cells, 48 common seeds, three arms)

Solve fractions (denominator 384 = 8 cells × 48 seeds):

| Roster | G4 | D (DG-built) | T (TS-built) |
|---|---:|---:|---:|
| 8 DG spare cells | 59 / 384 (15.4 %) | **307 / 384 (79.9 %)** | 187 / 384 (48.7 %) |
| 8 TS target cells | 266 / 384 (69.3 %) | 364 / 384 (94.8 %) | **372 / 384 (96.9 %)** |

Geometric capped cost over the 8 fixed cells (failures at 2 × cap; thousands of evaluations) and the mean search time:

| Roster | G4 | D | T |
|---|---:|---:|---:|
| DG | 806 k (29.4 s) | 98 k (12.4 s) | 293 k (23.6 s) |
| TS | 184 k (14.2 s) | 29 k (4.4 s) | 23 k (3.4 s) |

Pre-stated contrasts (hierarchical bootstrap, 8 192 draws: builds resampled independently within each cohort with each build keeping its rows on both rosters, two seeds resampled jointly within build × cell, one shared cell-stratified G4 draw):

| Contrast | 2 × cap point | 95 % | 1 × cap point | 95 % (1 × cap) |
|---|---:|---:|---:|---:|
| P_DG = cost(T on DG) / cost(D on DG) | **2.98** | **2.07 – 4.33** | 2.40 | 1.76 – 3.30 |
| P_TS = cost(D on TS) / cost(T on TS) | 1.29 | 0.94 – 1.78 | 1.27 | 0.94 – 1.72 |
| I = √(P_DG · P_TS) | **1.96** | **1.58 – 2.44** | 1.75 | **1.45** – 2.12 |
| G4 / D on DG | 8.21 | 5.98 – 11.13 | 5.25 | 3.99 – 6.85 |
| G4 / T on DG | 2.75 | 2.20 – 3.47 | 2.18 | 1.83 – 2.63 |
| G4 / D on TS | 6.31 | 4.69 – 8.45 | 5.29 | 4.02 – 6.94 |
| G4 / T on TS | 8.13 | 6.39 – 10.28 | 6.71 | 5.41 – 8.32 |

The runner's classification: interaction `material geometric family interaction` at 2 × cap but `unresolved interaction` at 1 × cap (penalty-sensitive); P_DG `matched preference`, P_TS `unresolved direction`; not reciprocal; no dominant bias; own-family useful; not a family-specific-acquisition candidate; not a shared-bias candidate.

### Per cell

Solved of 48 and geometric capped cost (2 × cap, thousands of evaluations); T/D is the within-cell ratio, > 1 means the DG-built cohort is cheaper.

| Cell | G4 | D | T | T/D (2 × cap) | T/D (1 × cap) |
|---|---:|---:|---:|---:|---:|
| DG (X0+X1)>(X2+X3) ? X3:X2 | 7 · 802 k | 37 · 96 k | 20 · 384 k | 4.01 | 3.13 |
| DG (X0+X2)>(X1+X3) ? X3:X2 | 6 · 883 k | 43 · 76 k | 25 · 257 k | 3.40 | 2.62 |
| DG (X0+X3)>(X1+X2) ? X3:X0 | 9 · 795 k | 37 · 76 k | 32 · 175 k | 2.32 | 2.15 |
| DG (X1+X2)>(X0+X3) ? X0:X2 | 6 · 877 k | 36 · 167 k | 23 · 303 k | 1.82 | 1.50 |
| DG (X1+X2)>(X0+X3) ? X3:X1 | 4 · 971 k | 36 · 111 k | 27 · 236 k | 2.13 | 1.87 |
| DG (X1+X3)>(X0+X2) ? X0:X2 | 8 · 755 k | 40 · 89 k | 13 · 557 k | 6.28 | 4.25 |
| DG (X1+X3)>(X0+X2) ? X2:X0 | 10 · 701 k | 41 · 85 k | 25 · 310 k | 3.65 | 2.89 |
| DG (X1+X3)>(X0+X2) ? X3:X1 | 9 · 700 k | 37 · 112 k | 22 · 252 k | 2.26 | 1.82 |
| TS X0>X1 ? (X2+X3):(X1+X2) | 36 · 166 k | 45 · 25 k | 48 · 12 k | 0.48 | 0.50 |
| TS X0>X1 ? (X2+X3):(X1+X3) | 34 · 185 k | 47 · 37 k | 46 · 16 k | 0.44 | 0.43 |
| TS X0>X2 ? (X1+X3):(X2+X3) | 34 · 170 k | 45 · 34 k | 48 · 33 k | 0.98 | 1.02 |
| TS X2>X0 ? (X1+X3):(X0+X1) | 36 · 148 k | 46 · 26 k | 47 · 23 k | 0.90 | 0.92 |
| TS X2>X1 ? (X0+X3):(X1+X3) | 26 · 287 k | 42 · 37 k | 47 · 14 k | 0.39 | 0.42 |
| TS X3>X0 ? (X1+X2):(X0+X2) | 34 · 196 k | 48 · 28 k | 46 · 24 k | 0.85 | 0.82 |
| TS X3>X2 ? (X0+X1):(X0+X2) | 35 · 153 k | 46 · 24 k | 44 · 39 k | 1.62 | 1.57 |
| TS X3>X2 ? (X0+X2):(X0+X1) | 31 · 197 k | 45 · 27 k | 46 · 35 k | 1.34 | 1.35 |

On the DG roster the DG-built cohort is cheaper on all 8 cells, by 1.8× to 6.3×. On the TS roster the TS-built cohort is cheaper on 5 of 8 cells (three of them by 2× or more), about equal on 2, and dearer on 1 (and the 1.34 cell is close to equal); the TS per-cell ratios straddle 1 both ways.

Same-seed pairs (each cell × ordinal runs both fitted arms from the same seed):

| Roster | D cheaper | T cheaper | Both capped | Tie | of |
|---|---:|---:|---:|---:|---:|
| DG | 236 | 107 | 41 | 0 | 384 |
| TS | 171 | 211 | 0 | 2 | 384 |

Against G4 on the same seed: D cheaper 299 / G4 cheaper 20 / both capped 65 on DG; T cheaper 176 / 38 / 170 on DG; D cheaper 303 / 73 / 8 on TS; T cheaper 320 / 61 / 3 on TS.

### Per build

Per-build geometric capped cost (16 searches per build per roster) and the build-level log-cost SD (natural log):

| Cohort | On DG: range, solved of 16 | SD (DG) | On TS: range, solved of 16 | SD (TS) | log(cost DG / cost TS) mean ± SD |
|---|---|---:|---|---:|---|
| D (24 builds) | 26 k – 370 k, 7–16 | 0.66 | 9 k – 107 k, 13–16 | 0.55 | 1.21 ± 0.70 |
| T (24 builds) | 110 k – 711 k, 3–12 | 0.42 | 11 k – 41 k, 14–16 | 0.34 | 2.56 ± 0.46 |

On the DG roster 21 of 24 D builds are cheaper than the cheapest-but-two T build; only D builds 3, 16 and 23 (the weak builds already noted in 1536: empty intermediate library, 7–11 of 16 solved) overlap the T range. On the TS roster the two clouds overlap almost completely (`per_build_cross_roster.png`). D build 16 is the weakest build on both rosters (8/16 and 13/16); no T build is weak on TS.

The D cohort's build SD on DG (0.66) matches the 0.62 the proposal planned on; the T cohort is more homogeneous (0.42 / 0.34), which is consistent with every T build reaching a full library from a rich solver corpus.

### Economics (arithmetic, failures at actual cap, acquisition charged once per build)

Arithmetic mean evaluations per search: DG roster G4 480 k, D 186 k, T 332 k; TS roster G4 256 k, D 78 k, T 59 k. Per build, the number of target searches that repays acquisition (median over 24 builds, range):

| Cohort | Acquisition (M evals) | Repay on DG | Repay on TS | Repay on both rosters |
|---|---:|---|---|---|
| D | 12.5 | 38 (24–121) | 70 (41–353) | 49 (34–180) |
| T | 6.1 | 40 (20–165), one build never | 30 (16–62) | 33 (21–101) |

The 32 target searches per build in this design do not repay D acquisition and only just repay T acquisition at the median; this is an accounting statement about the design, not a deployment claim. One T build has no saving on DG at all.

## 4. What the data shows

1. **DG-built A8 is clearly better than TS-built A8 on the never-searched DG cells.** P_DG ≈ 3.0 with a 2.1–4.3 interval at 2 × cap and 1.8–3.3 at 1 × cap; all 8 cells agree; same-seed pairs favour D 236 to 107. This direction is robust to the failure charge. Both cohorts still beat G4 there (8.2× and 2.8×).
2. **On the TS cells the two cohorts are close, with a lean towards the TS-built cohort that is not resolved.** P_TS ≈ 1.3 with an interval spanning 0.94–1.78; 5 of 8 cells favour T, same-seed pairs 211 to 171. The DG-built cohort transfers to TS almost as well as the matched one (6.3× vs 8.1× over G4).
3. **The geometric interaction I ≈ 2.0 clears the 1.5 margin at 2 × cap (lower bound 1.58) but not at 1 × cap (lower bound 1.45).** The label is penalty-sensitive, and the excess over 1.5 comes almost entirely from P_DG; I is a geometric mean of one large and one small effect.
4. **No dominating bias.** D is not better on both rosters (its TS interval includes 1 both ways), and T is not better on both (it loses clearly on DG). The asymmetry is therefore a genuine family × cohort interaction rather than one cohort simply being stronger.
5. **Not reciprocal, so not a family-specific-acquisition candidate under the pre-stated rule.** Own-family usefulness holds (both matched arms beat G4 with lower bounds well above 1.5), and all four G4 ratios' lower bounds exceed 1.5, but the shared-bias label is excluded by the material interaction at 2 × cap.
6. **Replication of the DG result on 8 new cells.** The same 24 D builds give G4/D 8.2 (6.0–11.1) with 307/384 solved on the spare cells, against 10.1 (7.6–13.2) and 317/384 on the 1536 protected cells (G4 59 vs 63 of 384). This is a new-cell, same-build replication, not a new-build one.

## 5. What the data does not show, and the main confound

- **The two rosters differ greatly in difficulty, which compresses P_TS.** G4 solves 69 % of TS target searches but 15 % of DG ones; both fitted cohorts solve 95–97 % of TS searches. With almost nothing left to fail, the TS roster can only separate the cohorts by solved-search cost, and the differences there (29 k vs 23 k) are within build-to-build variation. The TS roster cannot resolve a T preference even if one exists, and the branch-sum family turns out not to be a demanding test. "Unresolved direction" on TS is a statement about this roster's resolving power as much as about the cohorts.
- **Family information or source difficulty?** The D cohort was fitted on sources G4 rarely solves and contains the `(a+b)>(c+d)` join (the proposal's own mechanism), while the T cohort came from an easy family. That P_DG ≈ 3 is consistent with "TS libraries lack the join", but the data cannot separate the content of the fragments from the fact that the D cohort learned from a harder, more informative corpus. A context-only versus context-plus-fragments comparison on the saved builds would address this and was listed as the nearest cheaper alternative.
- **The interaction label depends on charging failures twice.** At 1 × cap I's lower bound is 1.45. A reader who prefers the 1 × cap charge should read the result as "one clear direction, interaction unresolved at the margin", not as a material interaction.
- **Scope.** External fitting plus literal fragments on fixed rosters; the DG bank is a development bank (its spare cells were never searched, but the bank's method and split were tuned on it); the TS bank is new and performance-blind but built on the same alphabet by the same screen; G4 is a supplied weak prior; the cap is 524 288. No claim about inheritance, a competitive baseline, pure ADD placement or fresh-bank generality is supported. Output ranges differ between families (TS −4..4, DG −2..2), so the preference is at family level.
- **Seen/unseen GT pairings on DG.** Four DG targets use the {02|13} pairing absent from the D sources; their T/D ratios (3.4, 6.3, 3.7, 2.3) are not systematically different from the seen-pairing cells (4.0, 2.3, 1.8, 2.1). Descriptive only.

## Against the predictions

Plan read after the analysis above was written. The plan's primary rule is the 2 × cap interaction with a 1 × cap repeat that flags changes.

| Pre-stated item | Prediction / rule | Observed | Verdict |
|---|---|---|---|
| Both matched arms beat G4 | expected | G4/D on DG 8.2 (6.0–11.1); G4/T on TS 8.1 (6.4–10.3) | met |
| P_DG ≈ 2–4 ("TS libraries lack the `(a+b)>(c+d)` join") | expected | 2.98 (2.07–4.33); 2.40 (1.76–3.30) at 1 × cap | met, both charges |
| P_TS ≈ 1–2 ("DG fragments contain the `push push ADD` pairs TS needs") | expected | 1.29 (0.94–1.78) | point inside the expected range; direction unresolved by the plan's rule |
| I ≈ 1.5–2.5, lower bound > 1.5 → material interaction | expected | 1.96 (1.58–2.44) at 2 × cap; 1.75 (1.45–2.12) at 1 × cap | met at 2 × cap only; penalty-sensitive, as the plan asked to flag |
| Reciprocal only if both directional lower bounds > 1 | rule | P_DG lower 2.07; P_TS lower 0.94 | not reciprocal |
| Dominant bias if one directional upper < 1 | rule | P_TS upper 1.78, P_DG upper 4.33 | no dominant bias; the interaction is genuine |
| Family-specific acquisition candidate only if reciprocal and own-family useful | rule | own-family useful; not reciprocal | not a candidate |
| Shared-bias candidate only if I upper < 1.5 and all four G4 ratios' lower bounds > 1.5 | rule | all four lower bounds > 1.5 (2.20–6.39) but I upper 2.44 | not a candidate |
| Surprises: I ≤ 1.1 with cross arms as good as matched; a mismatched cohort worse than G4 | named surprises | neither occurred; the weakest cross arm (T on DG) still beats G4 2.75× (2.20–3.47) | no surprise fired |
| Precision scenario: interval factor 1.30–1.45, lower 1.38–1.54 at I = 2 | planning | observed factor ≈ 1.24 below and 1.24 above the point (1.58 / 1.96, 2.44 / 1.96); the T cohort's smaller build SD (0.42 / 0.34) tightened it | slightly better than the scenario; the plan was right not to assume resolution at I = 2, since the 1 × cap repeat sits at 1.45 |
| TS feasibility unmeasured; poor TS acquisition would be a boundary, not a stop | caveat | TS acquisition was easy (63 % first-batch, 89 % adaptive, all libraries full); the opposite of the feared boundary | caveat moot; the easy family is instead the resolving-power problem for P_TS |
| Price: preparation ≤ 80 min, scoring ≤ 140 min, ≈ 110 min expected | plan | 17.8 min + 57.1 min = 74.9 min | under the estimate; calibration rates (DG D 7.9 s, T 26.9 s; TS D 3.0 s, T 2.6 s) were close to the scored means (12.4, 23.6; 4.4, 3.4) |
| Validity stops: < 16 separated TS cells, no covered split, target solved by a source behaviour, hash mismatch, projected time over the timeout | gates | 108-cell clique, 4/4/8 split, alias check passed, hashes verified, 4 839 s ≤ 8 370 s | none fired; all were price/validity gates, no outcome gate |

**Outcome label.** The data match the plan's `material geometric family interaction` branch at the primary 2 × cap charge, with the plan's own qualifiers: one direction resolved (the DG-built cohort is preferred on DG), the TS direction unresolved, not reciprocal, no dominant bias. The plan explicitly says an unresolved direction is not proven one-directionality, and that is the right reading here: the TS roster is too easy for both fitted cohorts (95–97 % solved) to separate them. The 1 × cap repeat falls to the plan's `unresolved` branch (lower bound 1.45), so the interaction label is penalty-sensitive and should be reported as such.

**What the plan's branches imply for the next step.** All branches return to strategy. The family-specific-acquisition action is not triggered. The shared-bias action is not triggered either, even though every cohort beats G4 by more than 1.5× on every roster, because the interaction is material on the DG side. The steward should weigh three things the pre-stated rules did not anticipate: (i) the one resolved direction is robust to the failure charge (P_DG 1.76–3.30 at 1 × cap) and is the actionable finding; (ii) the TS roster has no headroom, so resolving P_TS would need a harder branch-sum roster or a lower cap rather than more builds (the runner's resolution price of 131 min for 512 builds examined assumes the present roster and would mostly buy precision on a compressed contrast); (iii) the cheaper context-only versus context-plus-fragments comparison on the saved builds is now the direct test of the proposal's mechanism for P_DG, since the D cohort's advantage on DG could be the join fragments or simply a more informative (harder) source corpus.
