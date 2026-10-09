---
outcome: repertoire_earns_acquisition_review
---
# Analysis — 1036 frozen fragment reuse on excluded compositions (F/W/C on then-addition-v1, v1 holdouts as reference)

Reviewer: Claude Fable 5.1. Data: [`fragment-reuse-prepare`](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-1036-fragment-reuse-prepare) and [`fragment-reuse-score`](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-1036-fragment-reuse-score), both from commit `348f9e2`. Every number below was recomputed from `search.jsonl`; the primary ratios, intervals, sensitivities, per-cell and per-family values agree with `result.json` to three decimals. Plots: [per_corpus_contrasts.png](per_corpus_contrasts.png) (F/W, F/C, W/C per corpus, with the 0843 training-cell values for comparison) and [per_cell_then_addition.png](per_cell_then_addition.png).

## 1. Data completeness

Complete. Both queue entries exited 0; prepare took 57 s of 1800, scoring 9046 s (151 min) of 12 300, against a prepare projection of 9199 s. CPU efficiency 9.94 on 10 workers.

| check | result |
|---|---|
| scoring rows | 15 360 = 12 288 then-addition (3 arms × 16 corpora × 16 cells × 16 seeds) + 3 072 holdout (3 × 16 × 8 cells × 8 seeds) |
| rows per (phase, corpus, cell, arm) | 16 in all 768 then-addition groups; 8 in all 384 holdout groups; 0 duplicates |
| paired triples (phase, corpus, cell, seed) | 5 120, each with exactly one C, F and W row, one shared `initial_tokens_hash` and identical 64-case training draw |
| extra rows in the same file | 96 `smoke_*` replay rows (48 + 48); excluded here and by `report()` |
| table hashes | one per corpus (16), equal to the frozen 1548 C tables; `initial_reencoded` false on every row |
| cap / population | 524 288 / 256 everywhere; every unsolved row sits at the cap |
| admission | timing-only gate admitted 16 primary seeds (projection 153 min against the 195 min ceiling); no fallback to 12 |
| prepare validation | all 16 whole-corpus libraries at 32/32 and equal to the pinned 0843 records; 10 000-edit audit passed for F and W (2 678 tape-start, 2 668 tape-end edits each); 16 historical 1548 C rows replayed bit-exactly with the operator off; 12 288 NOP-padded evaluation-cell tests, 0 hits, nothing filtered; 96 smoke rows replayed before scoring |
| operator wiring (from per-row counters) | realized child fraction 0.2000 in F and W, 0 in C; tokens changed per edit 2.79 (F) and 2.89 (W), as in 0843; eligible children per generation ≈ 254, so elites were never edited |

"Solved" means exact on the full input domain; training-only programs are counted as shortcuts, not solves.

## 2. Key numbers

Per arm:

| bank | arm | solved | geometric cost (evals, unsolved = 2 × cap) | mean evals | mean worker s | total worker s |
|---|---|---:|---:|---:|---:|---:|
| then-addition (4 096 each) | C | 3 566 (87.1 %) | 67 289 | 144 583 | 7.20 | 29 492 |
| | F | 3 719 (90.8 %) | 45 888 | 112 027 | 5.69 | 23 325 |
| | W | 3 643 (88.9 %) | 54 845 | 124 769 | 6.20 | 25 377 |
| holdouts (1 024 each) | C | 950 (92.8 %) | 38 160 | 96 529 | 4.86 | 4 981 |
| | F | 992 (96.9 %) | 21 812 | 60 122 | 3.04 | 3 117 |
| | W | 986 (96.3 %) | 27 627 | 67 847 | 3.37 | 3 449 |

C's then-addition solve rate (87.1 %) matches 1548's 86.5 % on the same bank, so the C arm behaved as expected on fresh seeds.

Primary metric: exp(mean over 16 corpora of mean paired log cost_Y − log cost_X), unsolved = 2 × cap, 95 % t interval on 15 df. Pairs matched on (corpus, cell, seed) and share the initial population.

**Then-addition (primary, 4 096 pairs per contrast):**

| ratio | estimate | 95 % | 1 × cap | both solved (pairs) | BE corpora (8) | PA corpora (8) | paired wins / losses / ties | corpora > 1 |
|---|---:|---|---:|---:|---:|---:|---|---|
| F/W | **1.195** | 1.111–1.286 | 1.180 [1.103, 1.262] | 1.150 [1.085, 1.220] (3 338) | 1.154 [1.006, 1.325] | 1.238 [1.135, 1.349] | 2 173 / 1 835 / 88 | 14/16 (BE1 0.92, BE4 0.99) |
| F/C | **1.466** | 1.380–1.558 | 1.429 [1.349, 1.514] | 1.375 [1.291, 1.465] (3 282) | 1.456 [1.316, 1.612] | 1.476 [1.342, 1.624] | 2 361 / 1 625 / 110 | 16/16 |
| W/C | 1.227 | 1.148–1.311 | 1.211 [1.140, 1.286] | 1.188 [1.124, 1.256] (3 224) | 1.262 [1.113, 1.430] | 1.193 [1.101, 1.292] | 2 195 / 1 769 / 132 | 16/16 |

**Holdouts (reference, 1 024 pairs per contrast, no decision rule):**

| ratio | estimate | 95 % | 1 × cap | both solved (pairs) | BE (8) | PA (8) | wins / losses / ties | corpora > 1 |
|---|---:|---|---:|---:|---:|---:|---|---|
| F/W | 1.267 | 1.166–1.376 | 1.261 | 1.258 (956) | 1.309 [1.152, 1.488] | 1.225 [1.071, 1.403] | 574 / 441 / 9 | 16/16 |
| F/C | 1.749 | 1.570–1.949 | 1.700 | 1.569 (922) | 1.702 | 1.798 | 633 / 379 / 12 | 16/16 |
| W/C | 1.381 | 1.225–1.557 | 1.348 | 1.242 (920) | 1.300 | 1.467 | 573 / 427 / 24 | 15/16 (BE1 0.91) |

**Routing.** Rule 1 (harm) does not fire. Rule 2 fires: F/W lower bound 1.111 > 1 and point 1.195 ≥ 1.10; F/C lower bound 1.380 > 1. `result.json` says `repertoire_earns_acquisition_review`; I get the same from the raw rows. Note that the F/W lower bound (1.111) itself clears the 1.10 threshold under the primary metric, but not under the both-solved sensitivity (lower bound 1.085) or BE corpora alone (1.006).

**Precision.** Observed F/W half-width is ×1.076 on then-addition (corpus SD of log contrast 0.138) against the proposal's projection of ×1.072 at 256 pairs per corpus. The censoring concern (then-addition solves fewer) did not widen it materially.

**Comparison with 0843 training cells** (descriptive ratio of ratios, paired by corpus, 16 corpora; 0843 used leave-one-out libraries from 3 source cells, this run whole-corpus libraries from 4, so this is not a clean shape-attenuation estimate):

| contrast | 0843 training | then-addition here | ratio then-add / training | holdouts here | ratio holdout / training |
|---|---:|---:|---|---:|---|
| F/W | 1.234 [1.124, 1.355] | 1.195 | 0.968 [0.859, 1.092] | 1.267 | 1.026 [0.878, 1.199] |
| F/C | 1.574 [1.419, 1.746] | 1.466 | 0.932 [0.831, 1.045] | 1.749 | 1.112 [0.951, 1.299] |
| W/C | 1.275 [1.167, 1.393] | 1.227 | 0.962 [0.845, 1.096] | 1.381 | 1.083 [0.931, 1.260] |

None of the attenuation ratios is resolved from 1. For comparison, C/T lost a third across the same shape change in 1548 (0.68 [0.57, 0.81]).

**Per cell** (then-addition, 16 corpora × 16 seeds per cell, t on 15 df, descriptive):

| cell | F/W | F/C | W/C | solved C / F / W of 256 |
|---|---|---|---|---|
| F>m?F+M:S | 1.28 [1.01, 1.63] | 1.58 [1.15, 2.18] | 1.23 [0.97, 1.55] | 206 / 222 / 215 |
| F>m?F+S:M | 1.31 [1.02, 1.70] | 1.45 [1.11, 1.89] | 1.10 [0.89, 1.35] | 196 / 216 / 203 |
| F>m?M+M:S | 1.14 [0.88, 1.49] | 1.54 [1.13, 2.09] | 1.34 [1.03, 1.74] | 205 / 225 / 218 |
| F>m?M+S:F | 1.08 [0.89, 1.31] | 1.46 [1.25, 1.72] | 1.35 [1.17, 1.56] | 229 / 241 / 233 |
| F>m?M+S:M | 0.96 [0.80, 1.15] | 1.53 [1.24, 1.90] | 1.59 [1.35, 1.87] | 248 / 254 / 253 |
| F>m?M+S:S | 1.05 [0.78, 1.41] | 1.38 [0.99, 1.93] | 1.32 [1.05, 1.67] | 248 / 253 / 249 |
| F>m?M+m:S | 1.14 [0.85, 1.51] | 1.57 [1.26, 1.96] | 1.39 [1.11, 1.73] | 198 / 223 / 226 |
| F>m?S+S:M | 1.26 [1.00, 1.57] | 1.45 [1.23, 1.69] | 1.15 [0.95, 1.40] | 214 / 229 / 213 |
| F>m?S+m:M | 1.25 [0.98, 1.59] | 1.49 [1.15, 1.92] | 1.19 [1.00, 1.42] | 213 / 228 / 216 |
| M>F?F+S:m | 1.13 [0.86, 1.48] | 1.13 [0.91, 1.40] | 1.00 [0.77, 1.30] | 220 / 209 / 211 |
| M>F?F+m:S | 1.02 [0.77, 1.35] | 1.42 [1.19, 1.70] | 1.40 [1.08, 1.81] | 212 / 219 / 223 |
| M>F?M+S:m | 1.17 [0.94, 1.46] | 1.38 [1.09, 1.74] | 1.18 [1.00, 1.39] | 238 / 243 / 243 |
| M>F?M+m:S | 1.18 [0.94, 1.47] | 1.54 [1.13, 2.10] | 1.31 [1.05, 1.63] | 221 / 236 / 230 |
| M>F?S+S:m | 1.34 [1.00, 1.78] | 1.30 [0.98, 1.72] | 0.97 [0.74, 1.28] | 234 / 230 / 228 |
| M>F?S+m:F | 1.41 [1.03, 1.94] | 1.51 [1.13, 2.03] | 1.07 [0.75, 1.52] | 231 / 235 / 229 |
| M>F?S+m:m | 1.54 [1.36, 1.75] | 1.85 [1.54, 2.22] | 1.20 [1.00, 1.43] | 253 / 256 / 253 |

F/C point estimates are above 1 in 16/16 cells (lower bound > 1 in 13/16); F/W above 1 in 15/16 cells (lower bound > 1 in 5/16); W/C above 1 in 14/16 (lower bound > 1 in 9/16). The per-cell spread of log F/C (SD 0.10) is smaller than that of log F/W (0.12) or log W/C (0.13), and across cells log F/W and log W/C are negatively correlated (r = −0.67): cells where chain blocks already help most (`F>m?M+S:M`, W/C 1.59) are where fragments add least (F/W 0.96), and the reverse (`M>F?S+S:m`, W/C 0.97, F/W 1.34). Post-hoc, descriptive.

Holdout per cell (8 cells, 16 corpora × 8 seeds): F/W points 1.05–1.52, lower bound > 1 in 3/8; F/C 1.40–2.30, lower bound ≥ 1.00 in 8/8; W/C 1.09–1.69.

**Libraries and solver content.** The 16 whole-corpus libraries hold 113 distinct fragments in 512 slots (lengths 3/4/5 = 398/95/19 slots); 489/512 slots recur in all four source cells. Three fragments are in all 16 libraries (`input first gt`, `add input first`, `input reduce_min input`); BE and PA libraries share 46 fragments (82 and 77 distinct each). Among full-domain solvers, mean distinct library fragments per 32-token tape: then-addition C 7.43, F 9.10, W 7.35; solvers with at least one 4+-token library window: C 2 201/3 566 (61.7 %), F 2 756/3 719 (74.1 %), W 2 218/3 643 (60.9 %). Holdouts: C 65.9 → 69.1 %, F 81.4 %, W 69.3 %. The report's own `solver_library_share` is ≥ 0.999 for every arm because 3-token windows are ubiquitous and is uninformative. Occurrence, not ancestry.

**Shortcuts.** Searches that ever produced a training-only program: then-addition C 312, F 341, W 293 of 4 096; unsolved searches that produced one: 24, 22, 14. No arm reaches its solves through shortcuts. C encounters far more training-perfect-but-inexact individuals per search than W (6.96 M vs 2.84 M in total; F 5.41 M), repeating 1548's observation that C steers populations into near-alias neighbourhoods on this bank.

**Repayment** (result.json, descriptive): mean worker seconds saved per search, F against C 1.51 (then-addition) and 1.82 (holdout); F against W 0.50 and 0.32. Extraction of all 16 libraries cost 4.0 worker s, so the libraries repay after 3 (vs C) or 8 (vs W) then-addition searches. Corpus collection (48 039 worker s) is sunk and reported separately; counting it, F's saving against W repays after about 96 000 searches.

## 3. What the data shows

- **Frozen whole-corpus fragment libraries still beat C's chain blocks on the then-addition shape.** F/W 1.195 [1.111, 1.286], 14/16 corpora, 2 173 wins to 1 835 losses in 4 096 pairs; robust to the cap penalty and to both-solved pairs (1.150 [1.085, 1.220]), above 1 in both families. The increment is above the proposal's 1.10 threshold in point and (narrowly) in lower bound under the primary metric.
- **The practical gain over C survives the shape change almost intact.** F/C 1.466 [1.380, 1.558], 16/16 corpora, 13/16 cells individually resolved; attenuation from the 0843 training value is 0.93 [0.83, 1.05], not resolved from 1. This is a much smaller loss than C/T's 0.68 on the same shape change.
- **W itself still beats C across shape.** W/C 1.227 [1.148, 1.311], 16/16 corpora. The library-free block operator is a 1.15–1.31× gain on its own.
- **Holdouts within the v1 shape give the same ordering with larger values** (F/W 1.27, F/C 1.75, W/C 1.38), 16/16 corpora for F/W and F/C. No shrinkage from training is visible within shape.
- **F solvers carry more library content than C or W solvers** (9.1 vs 7.4 distinct fragments; 74 % vs 61 % with a 4+-token window), consistent with insertion but not proof of causal ancestry.

## 4. What the data does not show

- **No separation of fragment content from token supply.** There is no B arm here, so F/W confounds "intact solver fragments" with "a different token distribution"; 0843's B/C ≈ 0.98 on training cells argued against supply alone, but that was not re-tested on this shape.
- **Not transfer and not modularity.** then-addition-v1 was selected after v1 results and is a development bank (1548 §5). The libraries are the bank family's shared syntax (`input <reduce> input`, `input first gt if_gt`, `add input first`); then-addition cells need the same joins by construction. The result shows that one externally fitted literal-block procedure is reusable across one shape change, with a 1.10–1.29× margin over the library-free control.
- **Not acquisition.** Nothing evolutionary acquired the fragments; the library is fitted and frozen.
- **Not a uniform effect.** Per cell, F/W runs from 0.96 to 1.54; only 5/16 cells resolve F/W > 1 on their own, and in one cell (`F>m?M+S:M`, the easiest, 248/256 C solves) chain blocks are as good as fragments. The negative per-cell correlation between F/W and W/C suggests fragments and chain blocks partly substitute for each other, but this is a post-hoc reading on 16 points.
- **Not a clean attenuation estimate.** The 0843 libraries were leave-one-out from 3 source cells; these are whole-corpus from 4. The ratio-of-ratios table is descriptive only, and the proposal said so.
- **Marginal with respect to the 1.10 threshold.** The primary F/W lower bound (1.111) sits 1 % above the threshold; the both-solved and BE-only sensitivities fall below it. Rule 2 asks for point ≥ 1.10 and lower bound > 1, which is met with room; "increment resolved above 1.10" is not.

## 5. Minor notes

- The proposal's worry that then-addition censoring would widen F/W did not materialise (×1.076 observed vs ×1.072 projected). Holdout intervals are wider (×1.086 for F/W) because they have 64 pairs per corpus instead of 256.
- The W-cheaper flag is correctly false (rule 3 was not reached), though W/C's lower bound is > 1 on both banks.
- `resolution_price` in result.json (34 corpora, ~7.8 h) is a conditional price for the unresolved branch and is not needed since rule 2 fired.
- The prepare `search.jsonl` holds the 96 smoke rows and 16 operator-off historical replays; `report()` reads only the scoring file.

## Against the predictions

Read after the analysis above was written. plan.md restates the proposal's four ordered rules on then-addition only, adds solve scenarios, a precision scenario, a timing projection from a preselected 96-search smoke, and a scope sentence.

| prediction (plan.md / proposal) | observed | verdict |
|---|---|---|
| Steward's guess: F/W 1.05–1.15 (rule 2 or 4), F/C about 1.4, W/C about 1.25 | F/W 1.195 [1.111, 1.286], F/C 1.466, W/C 1.227; rule 2 | F/C and W/C as guessed; F/W a little above the guessed range and 0.005 under the proposal's "surprising" bar of 1.2 |
| Surprise conditions: F/W ≥ 1.2, or F/W < 1 with holdouts > 1.1 | F/W 1.195 on then-addition, 1.267 on holdouts | neither fired; the first is at the boundary |
| Rule 2 fires if F/W lower > 1 and point ≥ 1.10 and F/C lower > 1 | 1.111 > 1, 1.195 ≥ 1.10, 1.380 > 1 | rule 2, exactly as `result.json` routes |
| Conservative solve scenario: C rates carry over, 3 542/4 096 primary and 962/1 024 reference per arm | C 3 566 / 950; F 3 719 / 992; W 3 643 / 986 | C within 1 % on both banks; F and W above C |
| Improved scenario: F/W reach 94 % primary (3 850) and 96 % reference (983) | F 90.8 %, W 88.9 % primary; F 96.9 %, W 96.3 % reference | reference matched; primary rates stayed well under the hypothetical 94 % |
| Precision ×1.072 half-width at 16 seeds, "may be wider" from censoring | ×1.076 (F/W), ×1.063 (F/C), ×1.069 (W/C) | matched; censoring did not widen it |
| Timing: 9 205 s projection with 15 % margin; about 160 min expected queue | 9 046 s scoring wall, 57 s prepare; 152 min total | matched |
| Smoke worker s/search: then-addition C 6.56 / F 6.03 / W 4.74; holdout C 4.79 / F 2.13 / W 1.92 | 7.20 / 5.69 / 6.20; 4.86 / 3.04 / 3.37 | W under-projected on both banks (the 16-search smoke was too small per arm, as plan.md warned); the aggregate still fit |
| "Holdout win alone cannot resolve the primary decision" | primary resolved on its own; holdouts agree in direction and are larger | not needed |
| "W/C gain with small F/W favours W" | W/C 1.23 with F/W 1.20 above threshold | not the branch reached; W/C lower bound > 1 on both banks nonetheless |
| "Incomplete rosters never yield an efficacy decision" | 15 360/15 360 | not exercised |
| Four-source-cell whole libraries prevent a clean attenuation estimate | attenuation ratios reported as descriptive only (0.93–0.97, none resolved from 1) | caveat applied |

**Outcome label.** Rule 2, `repertoire_earns_acquisition_review`, fires as the plan defines it. Per the plan this earns a strategy review of acquiring a separate repertoire; it proves neither a true F/W increment above 1.10 (the primary lower bound clears it by 1 %, the both-solved and BE-only sensitivities do not) nor acquisition nor break-even on corpus collection. The scope sentence applies unchanged: an externally fitted literal-block procedure reuses across one shape change on two development banks, with no claim about modularity, fresh-bank transfer, acquisition or family specificity. Two things the plan did not anticipate deserve the strategist's attention: the practical F/C gain barely attenuated across shape (0.93 [0.83, 1.05]) where C/T lost a third, and the per-cell F/W and W/C gains are negatively correlated, so fragments and chain blocks may be partly substitutable rather than additive.
