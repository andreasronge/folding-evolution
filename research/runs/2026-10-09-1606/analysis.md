---
outcome: not_needed_at_this_resolution
---
# Analysis — 1606 chain blocks with versus without suffix preservation (W vs R on then-addition, C as reference)

Reviewer: Claude Fable 5.1. Data: [`suffix-preservation-prepare`](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-1606-suffix-preservation-prepare) and [`suffix-preservation-score`](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-1606-suffix-preservation-score), both from commit `af8a7e5` (the queued `config.json` of both entries records that commit, which settles code-review minor note 2). Every number below was recomputed from `search.jsonl` plus `historical_references.json`; the primary ratios, intervals, sensitivities, family splits and per-cell values agree with `result.json` to three decimals. Plot: [per_corpus_contrasts.png](per_corpus_contrasts.png) (W/R and R/C per corpus on both banks). The run's own plots are in the score folder (`then_addition_diagnostics.png`, `then_addition_ripple.png`, holdout equivalents).

## 1. Data completeness

Complete. Both queue entries exited 0. Prepare took 74 s of 1 800; scoring 2 796 s (47 min) of 6 600, against the prepare projection of 4 170 s (the projection was conservative, as the code review anticipated). CPU efficiency 9.88 on 10 workers.

| check | result |
|---|---|
| new R rows | 5 152 = 4 096 then-addition (16 corpora × 16 cells × 16 seeds) + 1 024 holdout (16 × 8 cells × 8 seeds) + 32 smoke replays (excluded from the report) |
| historical W and C rows | 10 240 = 2 arms × (4 096 + 1 024), read from 1036's pinned output; I re-matched all 10 240 by (phase, corpus, cell, arm, seed) against 1036's own `search.jsonl` and found 0 missing, 0 differing in solved / evaluations / solver / hashes / training draw / seconds |
| rows per (phase, corpus, cell, arm) | 16 in all 768 then-addition groups, 8 in all 384 holdout groups, across all three arms; 0 duplicate keys |
| paired triples (phase, corpus, cell, seed) | 5 120, each with exactly one R, W and C row, one shared `initial_tokens_hash`, identical 64-case training draw, one table hash |
| table hashes | one per corpus (16), `initial_reencoded` false on all 15 360 rows |
| cap / population | 524 288 / 256 everywhere; all 1 539 unsolved rows (three arms, both banks) sit exactly at the cap |
| prepare validation | full 1036 roster metadata check passed (15 360 rows); 32 historical W/C rows replayed with no field differences; 10 000-edit forced audit passed (2 670 tape-start, 2 652 tape-end, 2 064 no-op-block, 4 525 unchanged-final-token cases) |
| score validation | 32 smoke payloads replayed before scoring; `historical_paired` true, so the main path ran, not the fallback |
| operator wiring (per-row counters) | realized child fraction 0.2000 in W and R, 0 in C; inside-block tokens changed per edit 2.888 (W) and 2.886 (R); span per edit 3.259 in both. R's inside histogram tracks W's shape, so the block proposals are the same distribution |

Arm wiring (from `git diff a3a254d..af8a7e5`): R and W share the operator stream, length, start and token draws; R diverges only at position `start + length`, where it looks up the token the *unchanged* allele decodes to under the new final block token and redraws uniformly within that token's interval. The boundary allele is read before it is written in the same loop iteration, and no later position is touched. R's change counters re-decode the actual child, so suffix changes are measured, not assumed.

"Solved" means exact on the full input domain; training-only programs are counted as shortcuts, not solves.

## 2. Key numbers

Per arm (W and C are the historical 1036 rows; worker-seconds for them are 1036 hardware and descriptive only):

| bank | arm | solved | geometric cost (evals, unsolved = 2 × cap) | mean evals | solved-only median evals | mean worker s |
|---|---|---:|---:|---:|---:|---:|
| then-addition (4 096 each) | W | 3 643 (88.9 %) | 54 845 | 124 769 | 36 864 | 6.20 |
| | R | 3 685 (90.0 %) | 52 314 | 119 177 | 36 864 | 5.93 |
| | C | 3 566 (87.1 %) | 67 289 | 144 583 | 45 312 | 7.20 |
| holdouts (1 024 each) | W | 986 (96.3 %) | 27 627 | 67 847 | 23 040 | 3.37 |
| | R | 991 (96.8 %) | 26 612 | 64 029 | 22 016 | 3.17 |
| | C | 950 (92.8 %) | 38 160 | 96 529 | 26 624 | 4.86 |

Primary metric: exp(mean over 16 corpora of mean paired log cost_Y − log cost_X), unsolved = 2 × cap, 95 % t interval on 15 df. W/R > 1 would favour the repair.

**Then-addition (primary, 4 096 pairs per contrast):**

| ratio | estimate | 95 % | 1 × cap | both solved (pairs) | BE corpora (8) | PA corpora (8) | paired wins / losses / ties (Y costlier / cheaper / equal) | corpora > 1 |
|---|---:|---|---:|---:|---:|---:|---|---|
| **W/R** | **0.954** | **0.903–1.007** | 0.961 [0.916, 1.008] | 0.984 [0.940, 1.031] (3 320) | 0.981 [0.907, 1.061] | 0.927 [0.846, 1.016] | 1 939 / 2 042 / 115 | 5/16 |
| R/C | 1.286 | 1.208–1.370 | 1.261 [1.193, 1.332] | 1.198 [1.139, 1.260] (3 267) | 1.286 [1.178, 1.403] | 1.287 [1.147, 1.444] | 2 213 / 1 757 / 126 | 16/16 |
| W/C (1036, for reference) | 1.227 | 1.148–1.311 | 1.211 [1.140, 1.286] | 1.188 [1.124, 1.256] (3 224) | 1.262 [1.113, 1.430] | 1.193 [1.101, 1.292] | 2 195 / 1 769 / 132 | 16/16 |

**Holdouts (descriptive, 1 024 pairs per contrast):**

| ratio | estimate | 95 % | 1 × cap | both solved (pairs) | BE (8) | PA (8) | wins / losses / ties | corpora > 1 |
|---|---:|---|---:|---:|---:|---:|---|---|
| W/R | 0.963 | 0.850–1.092 | 0.967 [0.858, 1.089] | 0.975 [0.873, 1.089] (961) | 0.924 [0.787, 1.085] | 1.004 [0.795, 1.269] | 492 / 512 / 20 | 9/16 |
| R/C | 1.434 | 1.250–1.645 | 1.395 [1.234, 1.577] | 1.309 [1.192, 1.437] (926) | 1.407 [1.091, 1.816] | 1.461 [1.215, 1.757] | 582 / 424 / 18 | 15/16 |
| W/C (1036) | 1.381 | 1.225–1.557 | 1.348 | 1.242 (920) | 1.300 | 1.467 | 573 / 427 / 24 | 15/16 |

**Routing.** Rule 1 (ripple helps: upper bound < 1) does not fire, by 0.7 %: the W/R upper bound is 1.007. Rule 2 (lower bound > 1 and point ≥ 1.10) does not fire. Rule 3 fires: the upper bound 1.007 < 1.10. R/C's lower bound 1.208 > 1, so `chain_proposals_help_without_containment` is true. `result.json` says `not_needed_at_this_resolution`; I get the same from the raw rows.

**Precision.** Observed W/R half-width is ×1.056 on then-addition (corpus SD of log contrast 0.103), tighter than the proposal's ×1.07 projection, because the W/R contrast is less heterogeneous across corpora than W/C was (SD 0.139 in 1036). Holdout W/R half-width ×1.134 (SD 0.236, 64 pairs per corpus).

**Where the W/R difference comes from.** The both-solved sensitivity (0.984 [0.940, 1.031], 3 320 pairs) is closer to 1 than the primary (0.954): among pairs where both arms solve, R is only about 1.6 % cheaper, and solved-only median evaluations are identical (36 864). Most of the primary gap is censoring: R solves 42 more then-addition searches than W (365 R-only vs 323 W-only solves, 88 neither, of 4 096), and each unsolved search costs 2 × cap. On holdouts R-only 30 vs W-only 25, neither 8.

**Per cell** (then-addition, 16 corpora × 16 seeds per cell, t on 15 df, descriptive):

| cell | W/R | R/C | solved W / R / C of 256 |
|---|---|---|---|
| F>m?F+M:S | 0.81 [0.63, 1.05] | 1.51 [1.19, 1.92] | 215 / 229 / 206 |
| F>m?F+S:M | 0.79 [0.62, 1.00] | 1.39 [1.13, 1.72] | 203 / 208 / 196 |
| F>m?M+M:S | 0.96 [0.76, 1.22] | 1.39 [1.11, 1.76] | 218 / 222 / 205 |
| F>m?M+S:F | 1.04 [0.88, 1.23] | 1.30 [1.08, 1.57] | 233 / 238 / 229 |
| F>m?M+S:M | 1.12 [0.95, 1.31] | 1.43 [1.15, 1.77] | 253 / 251 / 248 |
| F>m?M+S:S | 1.06 [0.86, 1.31] | 1.24 [0.93, 1.66] | 249 / 250 / 248 |
| F>m?M+m:S | 1.08 [0.91, 1.28] | 1.29 [1.06, 1.56] | 226 / 213 / 198 |
| F>m?S+S:M | 0.93 [0.77, 1.13] | 1.24 [0.98, 1.57] | 213 / 222 / 214 |
| F>m?S+m:M | 0.86 [0.71, 1.05] | 1.39 [1.11, 1.73] | 216 / 229 / 213 |
| M>F?F+S:m | 0.96 [0.69, 1.33] | 1.04 [0.78, 1.40] | 211 / 216 / 220 |
| M>F?F+m:S | 1.10 [0.85, 1.41] | 1.27 [0.99, 1.64] | 223 / 212 / 212 |
| M>F?M+S:m | 0.94 [0.81, 1.09] | 1.25 [1.05, 1.50] | 243 / 239 / 238 |
| M>F?M+m:S | 0.83 [0.70, 0.99] | 1.57 [1.21, 2.04] | 230 / 238 / 221 |
| M>F?S+S:m | 0.92 [0.72, 1.18] | 1.06 [0.82, 1.35] | 228 / 233 / 234 |
| M>F?S+m:F | 0.95 [0.74, 1.24] | 1.12 [0.82, 1.52] | 229 / 229 / 231 |
| M>F?S+m:m | 0.99 [0.83, 1.17] | 1.22 [1.06, 1.40] | 253 / 256 / 253 |

W/R point estimates are below 1 in 11/16 cells; only one cell (`M>F?M+m:S`, 0.83 [0.70, 0.99]) resolves below 1 on its own and none resolves above 1. R/C is above 1 in 16/16 cells, lower bound > 1 in 11/16, the same pattern 1036 reported for W/C (14/16 and 9/16). Holdout per cell (8 cells, 128 pairs): W/R 0.79–1.07, none resolved either way; R/C 1.15–1.61, lower bound > 1 in 7/8.

**Realized ripple (natural, from scored R rows, 96.7 M edited children on then-addition).** The suffix (boundary and beyond) changes in 63.8 % of block edits; given a change, mean 2.86 tokens change. Per edit, R changes 2.89 tokens inside the block plus 1.82 beyond it, 4.71 in all, against W's 2.89. The suffix-change histogram is close to geometric (fractions 0.36, 0.22, 0.14, 0.10, 0.06, 0.04 for 0–5 changed tokens) with a thin tail out to 29. This matches the steward's read-only probe (65–67 % of edits, about 2 extra tokens) and confirms that the natural rate is far higher than the 30.4 % in the prepare audit, which deliberately included 40 % constructed neutral controls. Holdout figures are the same (63.7 %, 1.83 suffix tokens per edit).

**Shortcuts and search behaviour.** Searches that ever produced a training-only program: then-addition W 293, R 310, C 312 of 4 096; unsolved ones with a shortcut 14, 18, 24. No arm reaches its solves through shortcuts. Training-perfect-but-inexact individuals encountered per bank: W 2.84 M, R 4.01 M, C 6.96 M; R sits between W and C on this near-alias measure, which is consistent with its wider edits but is descriptive only. Mean generations per search: W 487, R 466, C 565.

## 3. What the data shows

- **The boundary repair does not help on then-addition at this resolution.** W/R 0.954 [0.903, 1.007], 4 096 pairs, 16 corpora; R is cheaper in 11/16 corpora and 2 042 of 3 981 non-tied pairs. The upper bound excludes a 1.10 gain, and indeed any gain above 0.7 %. The same holds under 1 × cap (upper 1.008), both-solved (1.031), within BE (1.061) and PA (1.016), and on holdouts (1.092).
- **The point estimate is on the side of ripple helping.** The W/R upper bound misses rule 1 by 0.7 %, and PA alone (0.927 [0.846, 1.016]) and the holdout BE split (0.924) lean the same way. This is a direction, not a finding: no split resolves below 1, the both-solved estimate is 0.984, and the primary gap is mostly 42 extra R solves in 4 096.
- **Chain proposals without containment beat C by the same margin W did.** R/C 1.286 [1.208, 1.370], 16/16 corpora, 11/16 cells individually resolved; W/C in the same pairs was 1.227 [1.148, 1.311]. R/C is robust to the cap penalty (1.261) and to both-solved pairs (1.198), in both families. Holdouts give the same ordering with larger values (1.434).
- **The ripple is as the probe described it: frequent and local.** 64 % of edits change the decoded suffix, by about 3 tokens when they do; the edit grows from 2.9 to 4.7 changed tokens on average. The data do not show the whole-suffix re-decode that question 32 assumed.
- **R solves slightly more** (3 685 vs 3 643 then-addition; 991 vs 986 holdout) at the same solved-only median cost. Small, but in the same direction on both banks.

## 4. What the data does not show

- **Not that ripple helps.** Rule 1 did not fire. 0.954 with upper bound 1.007 is compatible with no effect; a replication at the current size would be expected to land either side of 1.
- **Not equality of W and R.** Rule 3 is a resolution statement: W is at most 0.7 % better and at least 9.7 % worse than R, and most of that range is "about the same".
- **Not that coordinated chain proposals are the sole cause of W's gain over C.** R/C > 1 shows the proposals help *without* containment, as the proposal's rule 3 wording says. Whether anything else in W matters (its length law, its token supply) is untested here; 1036 had no B arm on this shape either.
- **Not a locality or GE-ripple result in general.** This is one externally fitted previous-token decoder, 32-token tapes, block length 3–5 (mean 3.26), ripple limited to about 3 tokens. The GE literature's crossover/mutation distinction is not addressed: ripple here rides on the block operator only; ordinary mutation and crossover are unchanged in both arms.
- **Not transfer.** then-addition-v1 and the v1 holdouts are development banks. C remains an external fit; nothing is acquired or inherited.
- **Mechanism of R's small edge, if real, is open.** Candidates the data cannot separate: the wider 4.7-token edit explores more per child (31 found undirected width hurts, but this width is *coupled* to the chain proposal, not undirected); the boundary refresh in R is a free neutral mutation of one allele; or censoring noise. The near-alias counts (R between W and C) hint at wider effective moves, descriptively.

## 5. Minor notes

- The fallback branch (fresh W/R, 8 192 searches) was never exercised; the replay gate passed 32/32 at `af8a7e5`, as it did at `e9a04f8` in 1350.
- The admission projection (4 170 s with margin) over-estimated scoring wall (2 796 s) by about 50 %, because measured concurrency in the 32-job smoke was tail-dominated; harmless here.
- `resolution_price` in `result.json` (20 corpora, about 3.9 h to reach ×1.05) is computed for the unresolved branch and is not needed since rule 3 fired. The reported `chain_proposals_help_without_containment: true` is correctly gated on rule 3 plus R/C lower bound > 1.
- W/C recomputed from the historical references (1.227 [1.148, 1.311]) matches 1036's analysis exactly, confirming the paired C rows are the same 4 096 the earlier decision rested on.
- R's `changed_histogram` has 33 bins versus W's 7; the report module pads W to zero suffix changes, which is correct because W's repair is audited to leave the suffix decode unchanged.

## Against the predictions

Read after the analysis above was written. plan.md restates the proposal's four ordered rules on then-addition, adds the critic's solve and precision scenarios, a 32-search timing admission, and the audit and pairing gates.

| prediction (plan.md / proposal) | observed | verdict |
|---|---|---|
| Steward's guess: W/R 1.03–1.10 (rule 3 or 4), R/C above 1 | W/R 0.954 [0.903, 1.007]; R/C 1.286 [1.208, 1.370] | R/C as guessed; W/R below the guessed range, on the other side of 1 |
| Surprise conditions: W/R ≥ 1.15 or < 0.95 | 0.954 | neither fired; the "ripple helps" side is missed by 0.004 in the point and 0.007 in the upper bound |
| Rule 3 fires if upper < 1.10; "most expected points 1.03–1.10 remain unresolved" | upper 1.007; rule 3 fires with room, rule 4 was not reached | the critic's worry that the result would be unresolved did not materialise, because the point landed below 1 and the interval was tighter than projected |
| Rule 1 (upper < 1) drops the repair | upper 1.007 | not fired, narrowly |
| R/C lower > 1 supports chain proposals without containment | 1.208 | fired; `chain_proposals_help_without_containment` true |
| Precision: scenario half-width ×1.07 from W/C; "not measured W/R variance" | ×1.056 (corpus SD 0.103 vs W/C's 0.139) | tighter than the scenario; the caveat was right in direction, wrong in sign |
| Solve scenarios: W 3 643 / 986 and C 3 566 / 950 as anchors; adverse 80 % R primary (about 3 277) | R 3 685 (90.0 %) / 991 (96.8 %) | R above both anchors; the adverse scenario was far from exercised |
| Timing: about 75 queue minutes (73.6 scoring with margin and reserve, 1.2 prepare), adverse 88.5 | scoring 46.6 min, prepare 1.2 min | within budget; the projection was about 50 % conservative, as the code review expected from the tail-dominated smoke |
| Replay gate 32/32 bit-exact or fallback to fresh W/R | 32/32 in prepare, 32 smoke replays in score | main paired path ran; fallback never exercised |
| Audit: W/R identical in prefix and block, R decode equals unrepaired decode, later alleles unchanged, equal RNG state | passed on 10 000 edits with the stated edge-case coverage | as planned |
| Diagnostics must decode the actual child and count suffix changes (critique note 2) | 63.8 % of natural edits ripple, 1.82 suffix tokens per edit | done; the natural rate matches the steward's 65–67 % probe and not the audit's control-diluted 30.4 % |
| "Identical proposals on identical inputs; trajectories may diverge" | inside-block change and span histograms are near-identical between W and R (2.888 vs 2.886 tokens per edit, 3.259 span) | proposals matched in distribution; divergence of trajectories is not measurable from these counters and was not claimed |
| Scope: development bank, externally fitted decoder, boundary policy and its downstream effects only | applied unchanged | no transfer, acquisition, modules, C/T or sole-cause claim is supported |
| All outcomes return to strategy; no top-up | rule 3 reached; `resolution_price` computed but not needed | per plan, next step is strategy |

**Outcome label.** Rule 3, `not_needed_at_this_resolution`, fires as the plan defines it: the W/R upper bound (1.007) excludes the 1.10 worthwhile gain, and R/C's lower bound (1.208) shows chain proposals help without containment. Two things the plan did not anticipate deserve the strategist's attention. First, the point estimate is below 1 and the rule-1 boundary was missed by under 1 %: the repair may be slightly harmful rather than merely unnecessary, which, if it held up, would say that a coupled 2-token widening of a chain edit is not the "undirected width" that 31 found costly. The data here cannot resolve that, and the both-solved estimate (0.984) says most of the gap is 42 extra R solves. Second, R/C (1.286) is numerically a little above W/C (1.227) in the same 4 096 pairs, so dropping the repair would simplify the operator at no measured cost; whether to do so in the next acquisition baseline is the strategist's call, with the explicit caveat that "no measured cost" is bounded at 0.7 % only on this development bank.
