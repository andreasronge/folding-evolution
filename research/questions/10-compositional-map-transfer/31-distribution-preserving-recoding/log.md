# Log: 31 distribution-preserving recoding


## 2026-10-09: run 2026-10-09-0537, recoded Q (R30, R100) at an exactly fixed random-program distribution — ran

Experiment ([proposal](../../../runs/2026-10-09-0537/proposal.md),
[plan](../../../runs/2026-10-09-0537/plan.md), code `fe196c1`,
[analysis](../../../runs/2026-10-09-0537/analysis.md)). Root-10 slot 22, granted by strategy 0537.
Each of the 16 then-addition Q tables (from 0306) recoded by context-dependent allele permutations
inside every body row (positions 1–31, previous tokens 0–23): R30 permutes a random 30% of each
row's 24 000 entries among themselves, R100 the whole row; position 0 unchanged. Row token counts
exact, so the uniform-prior distribution of complete tapes is Q's. Two construction realizations
per corpus and dose, nested in corpora (4 seeds each). Generation-0 alleles mapped through the
inverse permutation, so starting token tapes equal Q's. 4 096 new searches on Q's 2 048 (corpus,
cell, seed) triples, case draws and streams; Q (0306) and C (1548) rows reused. Primary
G = cost_Q/cost_R30, corpus unit n = 16, unsolved = 2 × cap, 95% t interval; useful gain needs a
lower bound ≥ 1.20, no useful gain an upper bound ≤ 1.20.

Result. Gates all passed: 32/32 identity replays (16 Q, 16 C) bit-exact, 936/936 C solver tapes
recovered, 64/64 maps validated and hashed, 4 096/4 096 initial-token hashes equal to Q's, 4 096
rows paired with Q, no duplicates. Scoring 5 972 s. The queue marked scoring `failed` because of a
missing `import json` in the last plotting step, after `result.json`, `report.md` and validation
were written; the reviewer recomputed all ratios from `search.jsonl` and regenerated the missing
figure. The data are complete.

Variation audit (uniform tapes): tokens changed per single allele resample C 2.95, Q 1.71,
R30 3.00, R100 7.71; P(≥ 4) C 0.31, Q 0.09, R30 0.31, R100 0.64; crossover changes about 10.3
tokens in every arm. On 936 C-solver tapes, C 2.52, Q 1.68, R30 2.90, R100 6.81. R30 did get
C's mutation width, on uniform and solver tapes.

| Contrast (cost ratio, > 1 = second arm cheaper) | 2 × cap | 1 × cap | both-solved | corpora < 1 |
|---|---|---|---|---|
| G = Q/R30 (primary) | 0.855 [0.801, 0.914] | 0.857 [0.806, 0.910] | 0.810 [0.733, 0.895] | 14/16 |
| Q/R100 | 0.409 [0.386, 0.434] | 0.475 | 0.473 | 16/16 |
| R30/R100 | 0.479 [0.455, 0.504] | 0.555 | 0.595 | 16/16 |
| H = R30/C | 2.819 [2.488, 3.193] | 2.580 | 2.272 | 0/16 |
| Q/C (reference, recomputed) | 2.411 [2.114, 2.749] | 2.210 | 1.954 | 0/16 |

Solves: C 86.5%, Q 73.9%, R30 73.7%, R100 52.4%. In the digest's speed convention R30 is 1.17×
slower than Q [1.09, 1.25], and R100 2.4× slower [2.3, 2.6]. Both realizations (k0 0.83
[0.75, 0.92], k1 0.88 [0.81, 0.96]) and both families (BE 0.84, PA 0.88) are below 1. Per corpus G
ranges 0.71–1.09; no cell's interval lies above 1. R30 solves as often as Q (both 1 159, Q only
355, R30 only 350) but more slowly when both solve. Descriptive gap share log(G)/log(Q/C) = −0.18
(arithmetic, not mediation). Shortcut programs per search: C 210, R30 67, Q 59, R100 15; they do
not explain the ordering.

Pre-stated label: **no useful gain at either dose** (both upper bounds ≤ 1.20); R30 does not
approach C (H upper bound 3.19 > 1.5). This is the expected branch; G 0.855 sits at the bottom of
the expected 0.85–1.10 band, and R100 was slower than expected (0.41 against 0.6–0.9). Neither
surprise condition occurred.

Scope: one development bank, frozen external maps, one operator set, two random within-row
recodings. The recoding changes allele–token correlations and what crossover does as well as
mutation width, so width is not isolated. A structured, locality-preserving recoding was not
tested. This does not show that C's conditional rows are necessary.

Decision: close 31, because the primary comparison resolved well below the 1.20 band at both
doses, under every cost convention, in both realizations and both families, so no larger run
would change the label. At C's width, at Q's exact random-program distribution, undirected
coupling made search slower. Return to strategy (`next: strategy`), because strategy 0537 granted
one slot and required a review after this result; the fragment plan is the competing investment.
([decision](../../../runs/2026-10-09-0537/decision.md))
