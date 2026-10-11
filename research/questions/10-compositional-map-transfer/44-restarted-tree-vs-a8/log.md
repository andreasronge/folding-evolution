# Log: 44 restarted tree GP versus A8

2026-10-11 (steward, run 2026-10-11-0024): opened from strategy 0024. Read-only probe of 2254 saved DG
rows (an attempt of cutoff t is an ordinary search truncated at t): at t = 65,536 with up to 8 attempts,
projected mean evaluations / solve fraction are tree 87k / 0.990 and A8 111k / 0.987 (full-cap observed:
tree 263k / 0.526, A8 178k / 0.818). Shorter cutoffs favour tree more (16,384: tree 32k, A8 103k), so
65,536 is not a tree-favouring choice. TS: tree 7.6k, A8 37k. A8 per-build solves within 65,536 range
2–13 of 16 (over-dispersed versus binomial). Simulated 384 jobs per arm (24 builds × 2, pooled-cell resampling, build heterogeneity not modelled): restarted
tree / restarted A8 ratio about 0.78, 95% upper end below 1 in about 90% of simulations; hence 4 repeats (768 jobs) proposed.

Decision: propose symmetric restarts (both arms at the same cutoff) as the primary, keeping the strategy's
restarted-tree versus full-cap A8 contrast as secondary, because restart alone is projected to cut A8's
cost by about 40%.

2026-10-11 (steward, run 2026-10-11-0024): ran at commit `1773d11` (code review pass; prepare 186 s, DG
1626 s, TS 377 s; all 1920 rows per family complete, seeds disjoint from 2254, 16/16 A8 replays and 8/8
first-attempt equivalences matched; first-attempt solve rates reproduced 2254's cutoff-truncated rates).
DG (primary, 768 jobs per restarted arm, 8 × 65,536 cap 524,288, failures at full cap, paired 24-build
bootstrap): R = mean evaluations R-tree ÷ R-A8 **0.792 [0.682, 0.915]**; solved 765/768 vs 754/768,
difference **+0.014 [0.000, 0.034]** (3-point noninferiority guard met, equality not shown). Pre-registered
PASS cell. Tree cheaper in all 8 cells (0.64–0.98) and 20/24 builds; leave-one-build-out 0.77–0.83; build 16
holds 7 of A8's 14 failures. Worker seconds go the other way: **1.388 [1.196, 1.604]** (tree 98 µs/eval vs A8
56), so per search R-A8 saves 2.48 s [1.39, 3.52] and repays its historical acquisition after about 312 [211,
579] searches per build (never on 6 builds); in evaluations it never repays (saving −23.7k [−41.1k, −8.6k]).
Restarting also helped A8: R-A8 ÷ F-A8 0.727 [0.647, 0.814] in evaluations, solved 0.982 vs 0.836 (F-A8
321/384); R-tree ÷ F-A8 0.576 [0.501, 0.668]. Tree attempts look independent (per-attempt success flat about
0.45, projection 0.992 vs observed 0.996); A8's later attempts are enriched for weak builds (fixed-build
heterogeneity, not attempt dependence). Shortcut note: 9.6% of R-tree DG evaluations went to programs perfect
on the 64 training cases but not D625-exact (A8 0.18%); since each attempt redraws cases, part of tree's
restart gain may be escaping an overfitted case sample — not separated from population reset. TS
(descriptive): R 0.181 [0.159, 0.202], worker seconds 0.265 [0.225, 0.305], both 768/768
([analysis](../../../runs/2026-10-11-0024/analysis.md)).

Explanations: (a) not supported in evaluations at this schedule; (b) supported in evaluations, with the
case-resampling vs reset share unidentified; (c) not supported for tree (attempts behave independently).

Decision: close 44 and return to strategy (`next: strategy`) because the pre-registered PASS cell was reached
(A8 keeps no evaluation saving over restarted tree GP on these development rosters at this schedule), the
residual A8 value is now a worker-time saving whose purchase depends on the owner's cost unit, and root 10's
36-slot budget is spent; whether to fund the tree-native fragment plan against R-tree is the strategist's call.

2026-10-11 (steward, run 2026-10-11-0150): wording corrections from critique 0150's digest check (notes 6–8),
applied to question.md; the entry above stands as written. "Reliability within three points" → noninferior
within the prespecified three-point margin, equal reliability not established (solve-difference interval
[0.000, 0.034] is not inside ±0.03). "(b) supported" → the restarted comparison favours tree GP in evaluations;
the stagnation/shortcut mechanisms in (b) remain hypotheses. "Attempts behave independently" / "fixed-build
heterogeneity" → tree hazards are consistent with the independence projection; A8's shortfall is consistent
with build heterogeneity. No decision changes.
