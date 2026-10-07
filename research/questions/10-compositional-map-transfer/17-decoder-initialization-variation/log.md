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
