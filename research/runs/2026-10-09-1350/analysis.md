---
outcome: no_worthwhile_increment_ends_source
---
# Analysis — 1350 pre-solve fragment source on then-addition (E / W_E, with the 1036 F / W / C rows replayed as paired references)

Reviewer: Claude Fable 5.1. Data: [`pre-solve-fragments-prepare`](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-1350-pre-solve-fragments-prepare) and [`pre-solve-fragments-score`](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-1350-pre-solve-fragments-score), both from commit `e9a04f8`. Every number below was recomputed from `search.jsonl` and `historical_references.json`; the four primary and secondary ratios, their intervals, the cap and both-solved sensitivities and the family splits agree with `result.json` to three decimals. Plot: [contrasts.png](contrasts.png) (per-corpus points for E/W_E, E/F, E/W, W_E/W on the left; per-cell E/W_E and E/F with intervals on the right). The run's own `then_addition_diagnostics.png` shows the two arms as near-identical cost, fitness and diversity curves.

## 1. Data completeness

Complete. Both queue entries exited 0; prepare took 116 s of 1800, scoring 5 044 s (84 min) of 9 000, against a prepare projection of 6 335 s. CPU efficiency 9.92 on 10 workers.

| check | result |
|---|---|
| scoring rows | 8 256 = 8 192 then-addition (2 arms × 16 corpora × 16 cells × 16 seeds) + 64 smoke replay rows (excluded here and by `report()`) |
| rows per (corpus, cell, arm) | 16 in all 512 groups; 0 duplicates; 256 seeds per corpus |
| paired (corpus, cell, seed) | 4 096, each with exactly one E and one W_E row, one shared `initial_tokens_hash` and identical 64-case training draw |
| historical references | 12 288 rows (C, F, W × 4 096) from 1036, SHA-pinned; every one of the 4 096 groups has all five arms with matching `initial_tokens_hash`, `training_indices`, table hash, cap and population. 48 rows (one per arm per corpus) replayed bit-exactly on the full field list including `solver` and `operator`, so `historical_paired` is true and E/F, E/C, W_E/W are paired contrasts |
| cap / population | 524 288 / 256 everywhere; all 807 unsolved rows sit at the cap |
| libraries | 16 × 32/32 from 331–359 selected pre-solve tapes per corpus (2 048 source attempts, 5 596 tapes, 50 empty attempts); no fallback corpus; every selected tape re-checked non-exact on the full domain; 0 NOP-padded hits on then-addition cells (8 192 tests) |
| admission | timing-only gate admitted 16 seeds (projection 106 min against the 135 min bound); no fallback to 12 |
| operator wiring (per-row counters) | realized child fraction 0.2000 in both arms; tokens changed per edit 2.66 (E) and 2.78 (W_E); `fallback` false on all 8 192 rows |
| source checkpoints | 2 001 tapes at generation 64, 1 898 at 128, 1 697 at 256, all before the source search's first exact solve |

"Solved" means exact on the full input domain; training-only programs are counted as shortcuts, not solves.

## 2. Key numbers

Per arm on then-addition (4 096 searches each; the F, W, C rows are 1036's, paired by seed):

| arm | solved | geometric cost (unsolved = 2 × cap) | mean evals | mean worker s | searches with a shortcut | training-perfect inexact individuals (total) |
|---|---:|---:|---:|---:|---:|---:|
| E (pre-solve fragments) | 3 692 (90.1 %) | 54 466 | 122 619 | 6.28 | 345 | 5.25 M |
| W_E (C-chain blocks, E's length law) | 3 693 (90.2 %) | 53 443 | 119 948 | 5.89 | 293 | 1.82 M |
| F (1036, exact-solver fragments) | 3 719 (90.8 %) | 45 888 | 112 027 | 5.69 | 341 | 5.41 M |
| W (1036, C-chain blocks, F's length law) | 3 643 (88.9 %) | 54 845 | 124 769 | 6.20 | 293 | 2.84 M |
| C (1036, no block operator) | 3 566 (87.1 %) | 67 289 | 144 583 | 7.20 | 312 | 6.96 M |

Metric: exp(mean over 16 corpora of the mean paired log cost_Y − log cost_X), unsolved = 2 × cap, 95 % t interval on 15 df. Ratio > 1 favours the first-named arm. All contrasts use the same 4 096 (corpus, cell, seed) groups.

| ratio | estimate | 95 % | 1 × cap | both solved (pairs) | BE corpora (8) | PA corpora (8) | corpora > 1 |
|---|---:|---|---:|---:|---:|---:|---|
| **E/W_E (primary)** | **0.981** | **0.911–1.057** | 0.981 [0.918, 1.049] | 0.989 [0.931, 1.051] (3 419) | 0.977 [0.875, 1.090] | 0.986 [0.866, 1.122] | 7/16 |
| E/F | 0.843 | 0.795–0.892 | 0.846 [0.803, 0.893] | 0.856 [0.812, 0.902] | 0.810 [0.730, 0.898] | 0.877 [0.821, 0.935] | 0/16 |
| E/C | 1.235 | 1.163–1.313 | 1.209 [1.141, 1.282] | 1.162 [1.095, 1.234] | | | 16/16 |
| W_E/W | 1.026 | 0.942–1.117 | 1.018 [0.942, 1.099] | 0.988 [0.930, 1.049] | | | 10/16 |
| E/W (descriptive) | 1.007 | 0.948–1.070 | 0.999 [0.944, 1.056] | 0.973 [0.914, 1.036] | 0.935 [0.878, 0.995] | 1.085 [0.999, 1.178] | |
| F/W (1036 check) | 1.195 | 1.111–1.286 | | | | | 14/16 |
| W/C (1036 check) | 1.227 | 1.148–1.311 | | | | | 16/16 |

Paired E vs W_E: E cheaper in 2 000 pairs, W_E cheaper in 1 985, ties 111.

**Routing.** Rule 1 (harm) does not fire: the upper bound is 1.057. Rule 2 does not fire: the lower bound is 0.911. Rule 3 fires: upper bound 1.057 < 1.10. `result.json` says `no_worthwhile_increment_ends_source`; I get the same from the raw rows, and also under the 1 × cap and both-solved sensitivities (upper bounds 1.049 and 1.051) and within each family alone (1.090 BE, 1.122 PA; the family intervals are not part of the rule).

**Precision.** E/W_E half-width ×1.077 (corpus SD of log contrast 0.139), essentially the ×1.08 the proposal projected from 1036's F/W. E/F is tighter (×1.059) and E/C tighter still (×1.062).

**Per cell** (16 corpora × 16 seeds per cell, t on 15 df, descriptive; see the right panel of [contrasts.png](contrasts.png)):

| cell | E/W_E | E/F | E/W | solved E / W_E / F of 256 |
|---|---|---|---|---|
| F>m?F+M:S | 0.89 [0.67, 1.19] | 0.82 [0.64, 1.06] | 1.05 [0.85, 1.31] | 221 / 218 / 222 |
| F>m?F+S:M | 0.88 [0.67, 1.15] | 0.71 [0.54, 0.93] | 0.93 [0.74, 1.18] | 195 / 201 / 216 |
| F>m?M+M:S | 0.89 [0.73, 1.09] | 0.88 [0.70, 1.10] | 1.00 [0.79, 1.27] | 227 / 224 / 225 |
| F>m?M+S:F | 1.03 [0.84, 1.27] | 0.89 [0.71, 1.11] | 0.96 [0.80, 1.16] | 232 / 235 / 241 |
| F>m?M+S:M | 0.83 [0.66, 1.06] | 0.80 [0.65, 0.97] | 0.77 [0.66, 0.90] | 251 / 251 / 254 |
| F>m?M+S:S | 1.00 [0.85, 1.17] | 0.97 [0.77, 1.24] | 1.02 [0.87, 1.20] | 251 / 253 / 253 |
| F>m?M+m:S | 1.03 [0.82, 1.29] | 0.83 [0.68, 1.00] | 0.94 [0.72, 1.23] | 222 / 218 / 223 |
| F>m?S+S:M | 1.02 [0.80, 1.30] | 0.90 [0.71, 1.13] | 1.12 [0.86, 1.48] | 227 / 229 / 229 |
| F>m?S+m:M | 1.02 [0.80, 1.31] | 0.94 [0.74, 1.18] | 1.17 [0.97, 1.41] | 231 / 231 / 228 |
| M>F?F+S:m | 1.03 [0.76, 1.40] | 0.92 [0.72, 1.17] | 1.03 [0.76, 1.41] | 218 / 219 / 209 |
| M>F?F+m:S | 1.01 [0.79, 1.29] | 0.92 [0.70, 1.21] | 0.93 [0.74, 1.18] | 224 / 228 / 219 |
| M>F?M+S:m | 1.04 [0.83, 1.32] | 0.89 [0.71, 1.13] | 1.04 [0.86, 1.27] | 244 / 242 / 243 |
| M>F?M+m:S | 0.95 [0.72, 1.26] | 0.88 [0.70, 1.10] | 1.03 [0.91, 1.17] | 232 / 235 / 236 |
| M>F?S+S:m | 0.91 [0.73, 1.12] | 0.77 [0.60, 0.99] | 1.03 [0.85, 1.26] | 227 / 231 / 230 |
| M>F?S+m:F | 1.29 [0.90, 1.85] | 0.84 [0.61, 1.16] | 1.19 [0.87, 1.62] | 235 / 226 / 235 |
| M>F?S+m:m | 0.95 [0.80, 1.13] | 0.62 [0.54, 0.72] | 0.96 [0.81, 1.13] | 255 / 252 / 256 |

No cell resolves E/W_E on either side of 1 (points 0.83–1.29). E/F is below 1 in 16/16 cells and resolved below 1 in 5/16; the largest deficit is the easiest cell (`M>F?S+m:m`, 0.62 [0.54, 0.72]), where 1036 found F's largest gain over W (1.54).

**Libraries.** The 16 pre-solve libraries fill 32/32 and share 9–18 fragments (median 14) with the corresponding 1036 exact-solver library. Lengths are 3/4/5 = 445/66/3 slots, shorter than F's 398/95/19, which is why W_E's length law differs from W's. Every fragment recurs in all four source cells and in at least 11 distinct source searches (minimum raw count 17). The decisive difference is lexical: **no pre-solve library contains the token `gt`** (vocabulary over all 512 slots: `input` 97 distinct-fragment uses, `add` 38, `reduce_min` 36, `reduce_max` 26, `if_gt` 25, `first` 17, `sum` 10, `reduce_add` 8, `dup` 3), while every exact library carries `input first gt` and 15/16 carry `input first gt if_gt`, `first gt if_gt` and `add input first gt`. In their place the pre-solve libraries hold `input first if_gt` (16/16 corpora), `input reduce_max if_gt` (16/16), `input sum if_gt` (15/16), `input reduce_add if_gt` (15/16) and `input reduce_min if_gt` (14/16), none of which appears in any exact library: a reducer feeding the gate directly, with no comparison in between. The shared half of the libraries is the reducer/add syntax (`input reduce_min input`, `input reduce_min add`, `input reduce_max add`, `input first input`, `add input first`).

**Solver content** (occurrence in full-domain solver tapes, not ancestry). The report's `solver_library_share` is ≥ 0.999 for both arms because 3-token windows are ubiquitous, exactly as in 1036, and is uninformative. More discriminating counts:

| solvers of arm | distinct E-library fragments per tape | share with a 4+-token E window | distinct F-library fragments | share with a 4+-token F window | share containing an F-library `gt` join |
|---|---:|---:|---:|---:|---:|
| E | 7.58 | 52.5 % | 7.86 | 62.1 % | 64.0 % |
| W_E | 6.27 | 40.4 % | 7.30 | 60.1 % | 64.4 % |
| F | 6.88 | 45.5 % | 9.10 | 74.1 % | 77.9 % |
| W | 6.36 | 42.8 % | 7.35 | 60.9 % | 65.3 % |
| C | 6.32 | 40.9 % | 7.43 | 61.7 % | 61.7 % |

E's insertions leave a trace (E solvers carry more E-library content than W_E, W or C solvers) without buying speed, and E solvers contain exact-library `gt` joins no more often than the C-chain arms do, whereas F solvers contain them 14 points more often.

**Shortcuts and near-aliases.** No arm reaches its solves through shortcuts (unsolved searches that produced a training-only program: E 26, W_E 8, F 22, W 14, C 24). The arms differ sharply in how many training-perfect-but-inexact individuals they encounter: E 5.25 M, F 5.41 M and C 6.96 M against W_E 1.82 M and W 2.84 M. Library insertion (from either source) steers populations into near-alias neighbourhoods at about three times W_E's rate; F pays this and still wins, E pays it and does not.

**Cost** (descriptive, from `result.json`). E used 0.39 more worker seconds and 2 670 more evaluations per search than W_E, so there is no break-even. The pre-solve collection (5 058 worker s for 2 048 attempts, sunk) is about a tenth of the exact-solver collection shared by all arms (48 039 worker s); extraction cost 8.6 worker s. The conditional ×1.05 resolution price is 34 corpora, about 7.1 h; it is not needed under rule 3.

## 3. What the data shows

- **Pre-solve fragments do not beat length-matched C-chain blocks on then-addition.** E/W_E 0.981 [0.911, 1.057], 7/16 corpora above 1, 2 000 wins to 1 985 losses in 4 096 pairs, under every sensitivity and in both families. The upper bound excludes the 1.10 worthwhile increment, so rule 3 fires as pre-stated. This is a bound on the increment, not equality: a true E/W_E anywhere in 0.91–1.06 is compatible with the data.
- **E is resolved below F.** E/F 0.843 [0.795, 0.892], 0/16 corpora above 1, 16/16 cells below 1. The same extractor on pre-solve parents gives a library that costs about 16 % more evaluations than the exact-solver library does, with everything else in the harness equal.
- **E is indistinguishable from W, and W_E from W.** E/W 1.007 [0.948, 1.070]; W_E/W 1.026 [0.942, 1.117]. The pre-solve length law (more 3-token blocks) changes nothing measurable, and the pre-solve content performs like C-chain content. E/C 1.235 [1.163, 1.313] is the same gain W/C showed in 1036 (1.227): it is the block operator's gain, not the library's.
- **The 1036 references replay bit-exactly and reproduce F/W 1.195 and W/C 1.227** from the same rows, so the historical arms are genuinely paired with E and W_E, and the comparison rests on one shared roster of initial populations and case draws.
- **The pre-solve libraries differ from the exact libraries in one systematic way.** The 14/32 shared fragments are the reducer/add syntax; the missing ones are the `gt` comparison joins; the extras are reducer-to-gate windows. The only candidate increment over W that is present in F and absent in E is therefore the comparison join. That is a description of the two libraries, not a mechanism test.

## 4. What the data does not show

- **Not a mechanism.** E/W_E ≈ 1 with E/F < 1 is consistent with "gate joins carry F's increment" and inconsistent with "shared reducer/add syntax carries it," but E differs from F in source, content and length law at once, and neither comparison has a marginal-content control. The join explanation is a hypothesis the libraries make natural, not a result. A direct test would insert the exact library's `gt` fragments alone, or the exact library with them removed, against W.
- **Not "pre-solve material is useless."** One extractor (all-active 3–6-token windows ranked by cell recurrence and raw occurrence, top 32) on one source selection (minimum-slot archived parents at generations 64/128/256) on one development bank. A different extractor, later checkpoints, performance-aware parent selection or a larger library could behave differently. The data bounds this source-and-extractor combination at this scope.
- **Not a solver-free or inherited system.** C is still fitted from exact solvers in both arms; the library is fitted and frozen; nothing is inherited.
- **Not transfer.** then-addition-v1 is a development bank, and the libraries are the bank family's shared syntax.
- **Not a harm finding.** The E/W_E interval includes 1; "pre-solve windows mislead" (the third competing explanation in question 33) is not supported, though E does drive populations into near-alias regions at F's and C's rate rather than W_E's.
- **Per-cell values are descriptive.** No cell resolves E/W_E; the one point at 1.29 (`M>F?S+m:F`) has an interval of 0.90–1.85.

## 5. Minor notes

- The code reviewer's note that W_E ran faster than E in the smoke persisted in the full run (5.89 vs 6.28 worker s per search) and the arithmetic savings are negative as predicted; the `break_even` fields are null.
- The prepare `search.jsonl` holds the 64 smoke rows and the 48 operator-on historical replays; the score file holds the 64 smoke replays plus the 8 192 efficacy rows. `report()` reads only the then-addition phase.
- E's mean generations (479) are slightly above W_E's (469) and both are far below C's (565); the fitness and diversity curves in the run's diagnostics plot overlap throughout.
- The score's historical references are copies of 1036 rows (SHA-pinned), not new searches, so the F, W and C numbers here are 1036's by construction, and their agreement with the 1036 analysis is a consistency check on the pairing, not new evidence.

## Against the predictions

Read after the analysis above was written. plan.md restates the proposal's four ordered rules on then-addition only, freezes the probe's occurrence-ranking extractor, adds solve-count and precision scenarios, a timing projection from a 64-search smoke, and a scope paragraph.

| prediction (plan.md / proposal) | observed | verdict |
|---|---|---|
| Steward's expectation: E/W_E between 1.0 and 1.10 (rule 3 or 4); E/F about 0.85–0.95 | E/W_E 0.981 [0.911, 1.057], rule 3; E/F 0.843 [0.795, 0.892] | E/W_E just below the expected range but routed as expected; E/F slightly below the guessed range |
| Surprise conditions: E/W_E ≥ 1.2 (shared syntax enough) or E resolved below W_E | 0.981, upper 1.057, lower 0.911 | neither fired |
| Rule 3 fires if upper bound < 1.10 (plan: needs point below about 1.019 at ×1.08 width) | upper 1.057, point 0.981, width ×1.077 | fires, with margin; also under 1 × cap, both-solved and each family alone |
| "Missing gate joins should cost most of F's increment" | E/W 1.007, E/F 0.843, F/W 1.195: E recovers none of F's increment over W | consistent with the guess, but untested as a mechanism (plan's own caveat: E/W_E ≈ 1 does not establish missing-gate causality) |
| Precision scenario ×1.08 half-width, E variance unmeasured | ×1.077 (corpus SD 0.139, the same as 1036's F/W) | matched |
| Solve-count scenarios: about 3 643–3 719 of 4 096 per arm from W/F rates; harmful E at 80 % gives 3 277 | E 3 692, W_E 3 693 | both within the W–F scenario band; no harmful-rate signal |
| Timing: 106 min projected scoring at 16 seeds with margin, 112 min queue wall; slower-E scenario up to 144 min | 84 min scoring, 2 min prepare; efficiency 9.92 vs smoke 7.39 | faster than projected because the smoke under-measured concurrency; 16 seeds admitted, no fallback |
| Smoke worker s per search E 6.03 / W_E 3.98 | 6.28 / 5.89 | E matched; W_E under-projected by the 32-search smoke, as the code review warned |
| 48 historical replays match, else all C/F/W demoted | 48/48 bit-exact; pairing metadata equal on all 4 096 groups | paired references available; E/F, E/C, W_E/W inferential as designed |
| Empty libraries fall back to W_E laws and are reported | 16/16 libraries at 32/32; 0 fallback rows | not exercised |
| Then-addition NOP-padded hits reported, never filtered | 0 of 8 192 | nothing to report |
| "Before stage 2 inspect E/C and W_E/W for practical value" | E/C 1.235 [1.163, 1.313] equals W/C 1.227; W_E/W 1.026 [0.942, 1.117] | the practical gain is the block operator's, not the library's; no stage 2 is reached |
| "E near F does not establish shared reducer/add causality; E near W_E does not establish missing-gate causality" | E is not near F; E is near W_E and W | the second caveat applies; the libraries' lexical difference (no `gt` in any pre-solve library) makes the join hypothesis the natural next test, but this run did not test it |

**Outcome label.** Rule 3, `no_worthwhile_increment_ends_source`, fires as the plan defines it: the E/W_E upper bound (1.057) is below 1.10 under the primary metric and every pre-stated sensitivity. Per the plan this ends expansion of this source-and-extractor combination at this scope and returns to strategy; it does not reject pre-solve learning in general, and it is not a harm finding (the interval includes 1). Two things the plan treated as secondary deserve the strategist's attention: E/F is resolved well below 1 (0.843, 0/16 corpora above 1), so the exact-solver source is strictly the better input to this extractor, and E/W and W_E/W are both about 1, so pre-solve content and the shorter length law each add nothing over C-chain blocks. The one systematic content difference between the two library families is the absent `gt` comparison join, which is a hypothesis for a cheap knock-in or knock-out test on the exact library, not a conclusion from this run.
