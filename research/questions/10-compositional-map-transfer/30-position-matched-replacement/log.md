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
