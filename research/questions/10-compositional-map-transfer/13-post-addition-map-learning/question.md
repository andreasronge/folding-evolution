---
status: closed
tags: [compositional-transfer, decoder, evolve-the-bias, outer-loop, post-addition, fresh-start, transfer]
budget: {experiments: 2, used: 0}
---
# Does selecting a decoder on six post-addition tasks speed fresh search on the two withheld compositions?

Current summary: **closed (2 of 2 slots used). Yes for learned token weights on G, about 2×;
whether contextual moves add to that is bounded on training and unresolved on the holdouts.**
Two runs, both on complete data; speed ratios (> 1 = faster) with 95% two-level bootstrap,
fresh seeds, 524k cap.

Run 2026-10-06-0132 (commit `02cf76f`, outcome row 1), 6 trajectories × 25 generations per learner:
- M (23 token multipliers on G's rows, from G) vs frozen G: training 2.23× [1.82, 2.75],
  holdouts 2.01× [1.47, 2.81] and 1.71× [1.26, 2.32]; 6/6 trajectories faster everywhere.
  Re-scored in run 0811 on 200 new seeds per holdout: 2.25× [1.81, 2.81] and 2.06× [1.60, 2.63].
- C (all 552 contextual weights, from G, three-coordinate steps): no resolved training gain,
  0.92× [0.78, 1.09]; it drifted modestly (L1 1.1–1.5 vs M's 11–14). A result about that operator
  and budget, not about whether context can be learned.
- T (23 tied weights, from G-marg): 1.7–2.1× faster than its start, still 0.41–0.57× of G.
- Agreement across trajectories: INPUT up and DUP down (M and T), IF_GT up (6/6 M); reducer
  changes with exceptions. About a quarter of M's training log-gain was lost on the holdouts
  (≈ 22% pooled; 14% and 33%).

Run 2026-10-06-0811 (commit `0709104`, outcome row 4), 12 matched pairs × 35 generations from the
six M maps: R (M's multipliers plus 24 × 23 row residuals; half token steps, half whole-row steps)
vs M+ (token steps only):
- R / M+: training 1.00× [0.90, 1.11], so a gain above 1.11× is excluded; holdouts 1.16×
  [0.91, 1.48] and 1.06× [0.83, 1.31], unresolved. The between-start spread (0.41–0.45 log2) is
  what keeps them open; more seeds would not help.
- Continuing token learning still pays: M+ / M 1.45× [1.26, 1.69] on training, 1.43× and 1.21×
  (unresolved) on the holdouts. R / M 1.41–1.51× everywhere.
- Residual ablation R / R_abl: 1.15× [0.97, 1.41], 1.10× [0.97, 1.25], 1.17× [0.88, 1.53]; no
  resolved advantage on the three PA sets, appreciable gains still possible.
- Operator acceptance fractions were near 25% (23.7–25.8%) for every operator; these counts do
  not establish how well selection ranks individual steps. Slow cumulative improvement is a
  proposed explanation, not an isolated mechanism.
- Off-family: frozen M / G 2.23× [1.66, 3.06] on the two branch-else cells, 1.08× [0.72, 1.57] on
  the six linear cells (G near the floor). So M's benefit is not confined to post-addition on
  the tested cells; a PA preference remains unmeasured. Unregistered, six maps: R / M+ 1.33× [1.05, 1.66] on branch-else and
  0.65× [0.44, 0.88] on linear; R doubled PA solver supply over M+ in 5/6 starts without a
  resolved PA search gain.
([0132 analysis](../../../runs/2026-10-06-0132/analysis.md),
[0811 analysis](../../../runs/2026-10-06-0811/analysis.md))

Setup: the eight post-addition cells `(S>0 ? X : Y) + Z` retained on D1331 by run 0001's alias
screen. Training: `(S?M:m)+M`, `(S?M:m)+S`, `(S?m:M)+S`, `(S?m:M)+m`, `(S?m:S)+M`, `(S?m:S)+m`.
Holdouts: `(S?M:S)+M`, `(S?M:S)+m` (the then/else pair M/S never occurs in training). Only decoder
tables transfer; every held-out search starts from fresh random genotypes. The bank was screened,
so this is fresh-seed transfer on a screened bank, not an untouched benchmark.

Competing explanations (root 10's A–E, narrowed to one family):
- A1: selection learns contextual preferences that speed held-out search beyond retuning token
  weights on G. **Not supported on training** (R / M+ ≤ 1.11×); **unresolved on the holdouts**
  (points 1.06–1.16×, upper bounds 1.31–1.48×). R / R_abl does not attribute anything to the
  residuals.
- B1: any gain is token-weight retuning. **Consistent with the planned PA comparisons**:
  token-only adaptation (M, M+) has demonstrated gains; an additional contribution from learned
  residuals has not been established (R / M gains are resolved, R / M+ and R / R_abl are not).
  Not shown to be the whole story: the holdout R / M+ is open, and an exploratory R / M+
  branch-else advantage (1.33×) is under test in [14](../14-saved-map-shape-shift/question.md).
- C1: the learned map improves training more than the withheld compositions. **Partly**: M lost
  about a quarter of its log-gain; M+ lost 48% / 5% of its increment, R 8% / none (descriptive).
- E1: the outer loop does not improve fresh training search. **Does not hold** for M, M+, R or T;
  for C under three-coordinate steps there was no resolved improvement (a gain above 1.09× is
  excluded). Operator acceptance near 25% does not establish how well selection ranks steps.
- G1: M's change is generic on this alphabet, not a PA preference. **Partly supported**: the
  frozen M maps are also faster than G on branch-else (2.23× [1.66, 3.06]; point estimate similar
  to the PA holdouts, not an equivalence test, so a PA preference is not ruled out); linear is
  unresolved near the floor. Branch-else is not an independently trained family.

Not answerable here: family specificity proper (no second trained family), supply versus
mutational-neighbourhood mechanism (they move together), other optimizers.

Related: [root 10](../question.md), [12](../12-generic-grammar-headroom/question.md),
[plan](../../../plans/post-addition-map-adaptation.md),
[strategy 0132](../../../runs/2026-10-06-0132/strategy.md),
[strategy 0811](../../../runs/2026-10-06-0811/strategy.md),
[run 0001 analysis](../../../runs/2026-10-06-0001/analysis.md),
[08-evolve-bias](../../01-map-bias/08-evolve-bias/question.md),
[09-generic-bias-speedup](../../01-map-bias/09-generic-bias-speedup/question.md) (INPUT/GT raise as the generic part),
[run 0132 decision](../../../runs/2026-10-06-0132/decision.md),
[run 0811 decision](../../../runs/2026-10-06-0811/decision.md).

Reopen if: (a) a design with about 20 independent M starts (or an equivalent variance reduction)
is funded to settle the holdout R / M+ increment; (b) an outer objective whose per-generation
selection beats the chance acceptance rate becomes available, so R and M+ can be compared
under a loop that discriminates; or (c) a pre-registered off-family test confirms that R's
residuals shift search toward branch shapes (faster on branch-else, slower on linear), which
would make the contextual learner worth a second look on this split.
