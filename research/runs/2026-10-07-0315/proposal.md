---
node: questions/10-compositional-map-transfer/17-decoder-initialization-variation
title: Starting programs versus ongoing decoder on the ten training cells — does the balance track family?
---
**Why this now.** Run [2331](../2026-10-06-2331/analysis.md) split the frozen 1723 maps' gain
(M over G4 = G) on the three 2229 cells into two parts. With identical generation-0 tapes,
searching under M saves 1.39× [1.31, 1.47] (P1). With the search decoder held at M, starting from
M's programs saves 1.30× [1.24, 1.36] (P2). The two overlap: interaction −0.34 log2 [−0.40,
−0.29]. Row 3 is the bounded answer that [17](../../questions/10-compositional-map-transfer/17-decoder-initialization-variation/question.md)'s
slot plan and [strategy 2331](../2026-10-06-2331/strategy.md) require before slot 2. Slot 2 is
root 10's last slot. 2331 also showed a pattern nobody predicted. On the one BE cell the start
carries more (P1 1.11× [1.04, 1.19], P2 1.34×). On both PA cells the ongoing decoder carries
more (P1 1.46× and 1.65×, P2 1.22× and 1.35×). If this follows family, the pooled "both,
overlapping" statement averages over tasks whose mechanisms differ. If it does not, the BE
holdout was an odd cell. The ten training cells (4 BE, 6 PA) are the only cells that can tell
these apart without new screening. So this run does two things: it replicates the pooled
increments across the bank, and it tests the family difference.

**Design.** The 2331 runner (`initialization_run`, commit `8f42f38`) is unchanged except for the
cell list, the seed range, the dropped MMr arm, and dispatch of two seed blocks at a time
(the code review's barrier note). Same 20 frozen maps (BE1–10, PA1–10, equal weight, none
dropped), G4, D1331, `v2_rmin_first`, 32-token tapes, pop 256, lexicase, crossover 0.7, mutation
0.03, cap 524 288, exact 1 331-input verification. Same four arms: GG (one per cell and seed,
shared by maps), MM, MG (MM's exact tapes, searched under G) and GM (GG's exact tapes, searched
under M). Conditional-uniform re-encoding at generation 0 only, stream `[seed, 3]`.
- **Cells:** the ten 1723 training cells. BE `F?S:(M+m)`, `F?m:(S+M)`, `S?F:(M+m)`, `S?M:(m+F)`;
  PA `(F?S:m)+M`, `(F?m:M)+S`, `(F?m:S)+M`, `(S?M:F)+m`, `(S?m:F)+M`, `(S?m:M)+F`. Each map is
  in-sample on its own family's cells and off-family on the other family's. This is a reused,
  screened set, not a holdout.
- **Seeds:** fresh 3150000–3150199 (200), shared by every arm. Ordered seed-major, so a deadline
  leaves a balanced set of complete seeds. The minimum for analysis is 120.
- **Count:** 10 × 200 × 61 = 122 000 searches.
- **Validation (in the queue, before the grid; failure stops the run):** round trips G↔M for
  all 20 maps (10 000 tapes per pair); MG = MM and GM = GG generation-0 token hashes on every
  (map, cell, seed); bit-exact reproduction of 1723's fresh-score rows for all 21 tables × 10
  cells × seeds 1723300–1723301 (420 searches), and of 2331's rows for all arms × 3 cells × seeds
  2331000–2331001 (366 searches). The MMr law check is dropped. The encoding law does not depend
  on the cell, and it passed at 99% on this code (1.02× [0.95, 1.09]).

**Feasibility (measured).** Per-search seconds from 2331 on 10 single-threaded workers: MM 0.70,
MG 1.20, GM 0.85 and GG 1.83 (means over the three cells). So a mixed-arm block costs 3.92× an
MM search. 1723's fresh scoring on these ten cells (50 seeds, same harness) measured map searches
at 0.22–2.21 s (mean 0.95 s) and G4 at 0.40–4.87 s. Cap hits are 0–4.4% for maps and 0–14% for
G4; three BE cells have the heaviest tails. Projection: 20 × 3.92 × 9.54 s + 22 s for G4 ≈ 770
CPU-s per seed over all ten cells, so 154 000 CPU-s for 200 seeds. At 2331's measured efficiency
(0.67 of 10 workers) that is **6.4 h**; with two-block dispatch it is about 5.3 h. Internal
deadline 7.0 h, queue timeout 7.5 h (≤ 8 h cap). 120 seeds take about 3.8 h even at the
slower rate. G4 solved 43–50/50 on every one of these cells in 1723, and the maps solved
956–1 000/1 000.

**Analysis.** T = evaluations to the first exact solve, or the cap if unsolved. Contrasts are
paired log2 ratios per (map, cell, seed), as in 2331.
- *Pooled (replication):* P1 = log2(T_MG/T_MM) and P2 = log2(T_GM/T_MM). Also D, I_G, O_G and
  the interaction. Cells get equal weight within family, families equal weight, maps equal
  weight within family. Intervals use 2331's crossed bootstrap (maps resampled within family,
  whole seed blocks shared across arms, maps and cells; 20 000 replicates). Labels as in 2331,
  δ = 0.25 log2: **N** upper < δ; **P** lower > 0 and upper ≥ δ; **X** otherwise. A resolved
  negative value is flagged as antagonism.
- *Family balance (co-primary):* per cell, S_c = mean over maps and seeds of log2(T_MG/T_GM),
  which equals P1 − P2. Positive S_c means losing the learned decoder during search costs more
  than losing the learned start. In 2331, S_c was −0.27 on the BE cell and +0.27 and +0.29 on the
  PA cells. **C = mean S over the BE cells − mean S over the PA cells.** The cell is the unit:
  Welch 95% t over 4 vs 6 cells. Labels: **B** (BE start-heavier) upper < 0; **E** (no family
  difference at the margin) interval inside (−0.25, +0.25); **R** (reversed) lower > 0;
  **X** otherwise.
- *Sensitivity:* winsorise at 65 536 and drop capped triplets, as in 2331. If a label changes,
  say so; the row still uses the planned analysis. *Descriptive:* per-cell P1, P2 and S; map
  family × cell family (in-sample versus off-family); solve fractions and cap counts per arm.
  The 13-cell view that adds 2331's cells is descriptive only, because it uses different seeds.
- *Precision:* the pooled half-widths should be about 0.08–0.12 log2 (2331 gave 0.08 on 3 cells
  at 400 seeds). C's half-width is about 1.55 × s_w, where s_w is the between-cell spread of S
  within a family (unmeasured). s_w = 0.2 gives ±0.31 and s_w = 0.3 gives ±0.46. A
  difference the size of 2331's (−0.55) resolves when s_w ≲ 0.35. Label E needs s_w ≲ 0.15 and a
  point near 0, so it is unlikely to be reachable. More seeds would not fix this: the number of
  cells limits C.

**Outcome rules (first match).**

| Row | Condition | Meaning |
|---|---|---|
| U | a validation check fails; < 120 complete seeds; GG solves < 75% on any cell; or pooled D's lower bound ≤ log2 1.25 | Intervention or coverage problem; no mechanism reading. |
| 1 | P1 = P, P2 = P, C = B | Both components help across the bank, and the learned start matters relatively more on BE cells than on PA cells. This is the 2331 flip at family level, on screened cells. |
| 2 | P1 = P, P2 = P, C = E | Both help; the start/ongoing balance does not differ by family at this margin. The 2331 BE cell was cell-specific. |
| 3 | P1 = P, P2 = P, C = R | Both help; on training cells the BE cells lean *more* on the ongoing decoder. The BE holdout was atypical. |
| 4 | P1 = P, P2 = P, C = X | Both help across the bank; family dependence unresolved. Report s_w and per-cell S. |
| 5 | one of P1, P2 = N, the other = P | On the training cells one component carries the gain at this margin, so the 2331 pooled pattern does not carry over. The conditional reading applies, as in 2331's plan. |
| 6 | otherwise (any X, or both N) | Attribution unresolved, or redundant at the margin (both N). Report widths. |

Per-cell, per-map-family and 13-cell views cannot change the row.

**Prediction.** Row 1 35%, row 4 35%, row 5 10%, row 2 10%, row 3 5%, row 6 5%. The pooled
increments should replicate, because 2331's lower bounds sit well above δ and both map families
agreed. The family test is a near coin flip between "resolved" and "unresolved", depending on
s_w. In-sample cells may raise P2, since a matched map's start was tuned on that cell. I
report that split, but it is not a primary readout.

**What it cannot show.** As in 2331: "ongoing" bundles mutation, crossover, inherited latent
alleles and continued program supply. A family difference in S would describe which component
matters more on which composition shape. It would not explain why, and it would not concern
whether the maps are family-specific. Ten screened cells from one bank, G4's hand-supplied
context, one regime.

**Next by outcome.** Every row closes 17. Root 10's budget is then spent, so the program
returns to strategy. Row 1 would give the strategist a concrete mechanism lead: what M's
starting programs supply on branch-else shapes, for example a census of generation-0 partial
programs, or an initialization-only map for BE tasks. Rows 2–4 leave the pooled "both,
overlapping" result as root 10's mechanism statement. Rows 5–6 limit 2331 to its three cells.

**Alternatives considered.**
- *Return to strategy now:* the strategist allocated slot 10 to this test, and the new per-cell
  pattern can only be tested with more cells.
- *Split mutation from crossover under M:* this refines "ongoing" but would leave unknown whether
  the pooled split is one mechanism or an average. It is a later question.
- *400 seeds:* about 12 h, over the cap. C is limited by the number of cells, not by seeds.
- *10 maps at more seeds:* this would thin the map-family × cell-family split to 5 maps per
  family and save little that matters.
- *Keep MMr:* this repeats a cell-independent law check that already passed on this code.
