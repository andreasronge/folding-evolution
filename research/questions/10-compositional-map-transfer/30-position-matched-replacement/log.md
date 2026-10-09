# Log: 30 position-matched replacement

## 2026-10-09: proposed in run 2026-10-09-0239 (score frozen Q and P on 1548 row F seeds)

## 2026-10-09: run 2026-10-09-0239 — stopped before scoring at the runtime admission gate

**Experiment.** Build frozen Q (G4 rows × per-position multipliers matched to C's emitted marginal
at each of 32 positions; C's start row at position 0) and P (independent draws from C's positional
marginals) from the 16 pinned 1246 C tables; pass intervention and replay gates; time 32 fixed
preparation searches; admit the 4 096-search scoring queue only if a conservative price fits the
3 h timeout ([plan](../../../runs/2026-10-09-0239/plan.md)).

**Result.** No efficacy result exists. All design gates passed
([infeasible](../../../runs/2026-10-09-0239/infeasible.md), [smoke/](../../../runs/2026-10-09-0239/smoke/)):
worst per-token marginal error Q 3.8e-5, P 2.7e-5 (limit 1e-3); worst positional total variation
Q 1.59e-4, P 1.61e-4 (limit 5e-3); Q's start rows equal C's; lookups match a scalar reference on
changing-table tapes; 32/32 C/T and 16/16 K historical rows replay bit-exactly. The runtime
admission price was 10 869.7 s (1.15 × the all-capped projection 9 304 s, plus fitting and
reporting) against a 10 800 s timeout: **69.7 s short**. Expected runtime is now 107–128 min,
above the proposal's 84–92 min. Nothing was adjusted after the gate failed.

Preparation observations (one search per corpus, rotating across cells, not paired with C; not
an efficacy estimate): exact solves at the cap Q 9/16 (95% CI 30–80%), P 6/16 (15–65%); mean
13.9 and 17.3 worker-seconds per search. For orientation only, the full 1548/0125 rosters solved
C 86.5% and K 72.5%; a 16-search rotating sample cannot be compared with them.

Decision: continue — re-propose the same frozen roster, method, gates and admission rule with an
11 700 s (3 h 15 min) scoring timeout in run 2026-10-09-0306, because the obstruction is a 70 s
shortfall on a deliberately conservative price after every validity gate passed; the revised
3 h 45 min summed timeout stays inside strategy 0239's 4 h ceiling; this question's and root 10's
slot is unused; and the decision the result feeds (whether an acquisition mechanism should target
positional supply or dependencies) is unchanged.

## 2026-10-09: run 2026-10-09-0306 — Q and P scored on 1548 row F; both replacements insufficient

**Experiment.** Same frozen roster, projections, gates and decision rule as 0239, with an 11 700 s
scoring timeout and, at the code reviewer's request, an admission rule that keeps the 15% safety
factor on the expected price and uses the all-capped projection as a separate hard bound
(rule `expected_safety_and_capped_bound_v1`; commit `2bab2c2`,
[plan](../../../runs/2026-10-09-0306/plan.md), [code review](../../../runs/2026-10-09-0306/code_review.md)).
16 corpora (8 BE, 8 PA) × 16 cells × 8 paired seeds per arm; 4 096 new Q/P searches, complete,
quintuple-paired with the 1548 C/T and 0125 K rows (2 048/2 048), replays bit-exact. Scoring took
96 min, so the original 3 h timeout would have sufficed; the 0239 stop came from the admission
price, not the workload.

**Result** ([analysis](../../../runs/2026-10-09-0306/analysis.md)). Corpus unit, n = 16, unsolved =
2 × cap, 95% t intervals:
- **C/Q 2.41× [2.11, 2.75]** (1 × cap 2.21× [1.97, 2.48]; both-solved pairs 1.95× [1.71, 2.23]);
  16/16 corpora (1.33–3.39×) and 16/16 cells above 1.20. Pre-stated rule: lower bound ≥ 1.20 →
  **this G4-based positional replacement is insufficient**.
- **C/P 5.47× [4.79, 6.25]** (1 × cap 4.26×; both-solved 3.30×, 7/256 corpus × cell groups empty);
  P insufficient on the same band.
- Q/K 1.03× [0.93, 1.13], 8/16 corpora each way, paired searches 931 vs 913: per-position matching
  gave no resolved gain over pooled matching; a gain above about 1.13× is excluded at this scope,
  a smaller one is not. log(C/Q)/log(C/K) = 0.97 (arithmetic, descriptive).
- Q/P 2.27× [2.10, 2.45]; T/Q 1.14× [1.04, 1.24] (the pooled token fit is slightly faster than Q).
- Solves: C 86.5%, T 75.5%, Q 73.9%, K 72.5%, G4 63.3% (unpaired), P 50.5%. P's geometric cost
  (370k) is above G4's (263k), unpaired and descriptive.
- Tokens changed per allele resample: C 2.97, T/K/Q 1.72–1.73, P 0.92; per crossover 14.7–14.9 for
  all arms.
- By fitting family (n = 8, descriptive): C/Q BE 2.68×, PA 2.17×; same ordering as C/K.

Matches the proposal's expectation ("both insufficient", C/Q 1.7–2.4×, P slower than Q); neither
surprise condition occurred. The inherited ×1.14 precision forecast held (sd log 0.246).

Scope: then-addition-v1 is a development bank (mechanism, not transfer); Q and P are external
projections of C matched under the uniform latent prior, not acquired and not matched to the
populations selection visits; the C advantage cannot be split into solver supply versus variation
neighbourhood (C's mutation changes about 3 tokens, Q's 1.7, P's 0.9). This rejects these two frozen
replacements under these operators, not every positional learner, and does not show that C's rows
are necessary.

Decision: close 30, because the pre-stated rule resolved on the primary comparison and on the
interpretation control in the same direction ("both fail"), with both lower bounds far above the
1.20 band under every censoring treatment, and Q/K 1.03× [0.93, 1.13] bounds what the position-specific supply strategy 0239 flagged adds over
pooled supply on this bank (no resolved gain; above about 1.13× excluded); another positional
control would not change the representation decision. Return to strategy (`next: strategy`), as
strategy 0239 and the plan require after this result. ([decision](../../../runs/2026-10-09-0306/decision.md))
