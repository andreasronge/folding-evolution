# Log — 17 decoder initialization vs variation

- 2026-10-06 (2331): opened from strategy 2331. Proposal: 2×2 init-source × search-decoder on the three 2229 cells, all 20 maps, 400 fresh seeds. Probe (runtime only): mixed arms 0.37–1.43 s/search vs G/G about 2.0 s.

## 2026-10-07: run 2026-10-06-2331, frozen starting-program × ongoing-decoder 2×2 on the three 2229 cells — ran; row 3

Slot 1 of 2. Critic approve_with_notes, code review pass; commit `8f42f38`, complete data
(79 200 rows: 73 200 main + 6 000 MMr; 400 complete seeds 2331000–2331399; 3.0 h; no errors;
[analysis](../../../runs/2026-10-06-2331/analysis.md)). 20 frozen 1723 maps (M) and G4 (G) on
BE `S?m:(M+F)`, PA `(F?S:M)+m`, PA `(S?M:m)+F`; arms GG, MM, MG (MM's exact generation-0 tapes,
searched under G), GM (GG's exact tapes, searched under M), via conditional-uniform re-encoding at
generation 0. All validation passed: 400 000 round trips exact, chi-square p 0.83/0.66/0.68,
630/630 historical 2229 rows bit-identical, token hashes paired on all 24 000 triplets, MMr/MM
1.02× (99% [0.95, 1.09]; a non-rejection, not equivalence). GG solved 94.5–99.5% per cell.
Paired log2 cost ratios, crossed map-within-family / whole-seed bootstrap (map-level t agrees
within 0.01 log2):
- P1 = MG/MM (ongoing-decoder increment given M's start) **1.39× [1.31, 1.47]**, label P.
- P2 = GM/MM (start increment given ongoing M) **1.30× [1.24, 1.36]**, label P.
- Diagonal GG/MM 2.29× [2.05, 2.54] (reproduces 2229's 2.0–2.9×). Start effect under G
  (GG/MG) 1.65× [1.50, 1.81]; ongoing effect from G's start (GG/GM) 1.76× [1.61, 1.92].
- Interaction −0.34 log2 [−0.40, −0.29] (0.79×), negative in 20/20 maps: either component alone
  recovers 60–68% of the diagonal in log units; the second adds only 1.30–1.39×.
- Per cell (descriptive, map-level t): BE cell P1 1.11× [1.04, 1.19], P2 1.34×; PA cells P1
  1.46× and 1.65×, P2 1.22× and 1.35×. The larger component flips between the BE cell (start)
  and the PA cells (ongoing). One BE cell, so this is a hint, not a family result.
- Cap sensitivity (drop triplets with any cap hit, or winsorise at 65 536) moves P1 by ≤ 0.07
  log2 and P2 by ≤ 0.02; no label changes. 12/79 200 searches solved at generation 0.
- Effects are shifts, not sweeps: MG slower than MM in 57% of pairs, GM in 57%, GG in 69%.
Predicted row 1 at 45%, row 3 at 30%; row 1 was wrong on P2 (the probe's 25 seeds on three maps
under-read the start effect).

Decision: continue 17 with slot 2 (the same frozen 2×2 on the ten training cells), sharpened to
test whether the dominant component tracks cell family, because slot 1 gave a bounded answer
(row 3, both increments resolved above the margin, strongly sub-additive), which the plan's
decision rule names as the condition for slot 2, and the one new, unexplained pattern — start
dominant on the BE cell, ongoing decoder dominant on both PA cells — rests on a single BE cell and
can only be checked with more cells; the ten training cells (4 BE, 6 PA) are the only ones
available without new screening. This is root 10's last slot; 17 closes after it either way.

## 2026-10-07: run 2026-10-07-0315, the same frozen 2×2 on the ten training cells — ran; row 1

Slot 2 of 2 (root 10's slot 10). Critic approve_with_notes, code review pass; commit `5dae3a6`,
complete data (122 000 searches = 10 cells × 200 seeds 3150000–3150199 × (GG + 20 maps × MM, MG,
GM); 4.27 h; no errors; [analysis](../../../runs/2026-10-07-0315/analysis.md)). Same 20 frozen
1723 maps (M), G4 (G), arms and re-encoding as 2331, on the 4 BE and 6 PA training cells (each map
in-sample on its own family's cells). All validation passed: 40 round trips × 10 000 tapes exact,
786 historical rows (420 from 1723, 366 from 2331) bit-identical, generation-0 hashes paired on
all 80 000 MG/GM rows. Row-U gates cleared (GG 91–100% per cell; D lower bound 2.23×).
- P1 = MG/MM (ongoing-decoder increment given M's start) **1.28× [1.22, 1.34]**, label P.
- P2 = GM/MM (start increment given ongoing M) **1.33× [1.26, 1.40]**, label P.
- Diagonal GG/MM 2.44× [2.23, 2.66]; interaction −0.52 log2 [−0.62, −0.42] (0.70× [0.65, 0.75]),
  sub-additive, larger than 2331's −0.34.
- Family balance S_c = log2(T_MG/T_GM) per cell: BE −0.39, −0.21, −0.29, −0.23 (each resolved
  below 0); PA +0.05, +0.16, +0.04, +0.54, +0.31, −0.05 (three resolved above 0, none resolved
  below). Family means BE −0.28, PA +0.17; within-family spread s_w 0.18.
  **C = BE − PA = −0.45 log2, Welch 95% [−0.68, −0.22], df 6.7: label B.** By family, P1 is +0.20
  [0.11, 0.30] on BE and +0.51 [0.42, 0.59] on PA; P2 +0.48 [0.37, 0.59] on BE and +0.34 [0.26,
  0.41] on PA, so both components are resolved positive within each family.
- Robust: winsorising at 65 536 or dropping capped triplets changes no label (C −0.43, −0.48);
  leave-one-cell-out C −0.38 to −0.50, all upper bounds below −0.14; all 20/20 maps have lower S
  on BE cells than on PA cells. S is set by the cell family, not the map family (descriptive).
- Confound (post hoc, descriptive): across the ten cells S correlates with MM median cost
  (r 0.77) and GG cap rate (r −0.77); the two PA cells with S > 0.3 are the two hardest PA cells.
  At matched MM difficulty BE cells still sit at −0.21 to −0.39 and PA cells at +0.04 to +0.16.
  With four and six screened cells, "family", "branch-else versus plus-arg shape" and "difficulty
  tail" cannot be separated.
- Generation-0 solves 20/122 000.
Predicted row 1 at 35% (and row 4 at 35%); right. P1 is smaller here than in 2331 (1.28× vs
1.39×), P2 similar (1.33× vs 1.30×); different cells and seeds, descriptive comparison. Runtime
4.27 h against the 4.2 h probe projection and the 6.4 h conservative plan.

Decision: close 17, because both slots are spent and the question is answered at this design's
resolution: on the 13 cells tested (three withheld, ten training), the learned map helps both
through its starting programs and through its use during search, each about 1.3× given the other,
strongly sub-additive, and the balance between them differs by cell family on the training bank
(start relatively heavier on BE cells, C −0.45 [−0.68, −0.22]); what is left — why, and whether
family rather than shape or difficulty drives the balance — needs new cells or a finer
intervention, not another run of this design. Root 10's budget is spent, so the program returns
to strategy. Wording corrections to the 2331 entry and summary (critique 0315 notes 5–6; no
numbers change): "the start effect is about useful partial programs, not seeded solvers" should
read "generation-0 solves were rare (12/79 200), so direct solver seeding is unlikely to explain
the gain; which properties of the starting population carry it is unresolved".
