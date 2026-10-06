---
status: open
tags: [compositional-transfer, decoder, evolve-the-bias, outer-loop, post-addition, fresh-start, transfer]
budget: {experiments: 2, used: 0}
---
# Does selecting a decoder on six post-addition tasks speed fresh search on the two withheld compositions?

Current summary: **one learner transferred, the contextual one never moved** (run
2026-10-06-0132, commit `02cf76f`, outcome row 1; 1 of 2 slots used). Six matched outer-loop
trajectories per learner, 25 generations, scored on fresh seeds at the 524k cap:
- C (all 552 contextual weights, from G): no practical training gain, C/G 0.92 [0.78, 1.09];
  flat learning curves, L1 drift 1.1–1.5. With three-coordinate N(0, 0.5) steps the change per
  child is far below the per-run score noise (sd ≈ 1.6 log2), so this is a result about the
  operator and budget (E1 for C), not about whether contextual preferences can be learned.
- M (23 token multipliers on G's rows, from G): faster than frozen G on fresh training (2.23×,
  [1.82, 2.75]) and on both withheld compositions (2.01× [1.47, 2.81], 1.71× [1.26, 2.32]); 6/6
  trajectories in every set; still improving at generation 25. A ≥ 1.5× holdout gain is not
  established on either cell (lower bounds 1.47, 1.26). About a third of M's training gain is lost on the holdouts.
- T (23 tied weights, from G-marg): 1.7–2.1× faster than its start, still 1.8–2.4× slower than G.
- Learned direction, consistent across trajectories: INPUT up, DUP down, IF_GT and reducers up.
  The probe's hand-set PA grammar (IF_GT→INPUT/ADD, ADD→DUP) pushed DUP the other way.
([analysis](../../../runs/2026-10-06-0132/analysis.md),
[probes](../../../runs/2026-10-06-0132/steward_probes/results.md))

Setup: the eight post-addition cells `(S>0 ? X : Y) + Z` retained on D1331 by run 0001's alias
screen. Training: `(S?M:m)+M`, `(S?M:m)+S`, `(S?m:M)+S`, `(S?m:M)+m`, `(S?m:S)+M`, `(S?m:S)+m`.
Holdouts: `(S?M:S)+M`, `(S?M:S)+m` (the then/else pair M/S never occurs in training). Frozen G
holdout KM medians 13 568 and 18 688 evaluations (49/50, 48/50), against U 83 968 and 148 480
(run 0001's reviewed analysis; on run 0132's seeds G's were 10.9k and 16.1k, 97/100 each).
Only decoder tables transfer; every held-out search starts from fresh random genotypes.

Competing explanations (root 10's A–E, narrowed to one family), as tested in run 0132:
- A1: selection on training tasks learns contextual preferences that speed held-out search beyond
  G and beyond retuning token weights on G's template. **Untested**: C never left G's
  neighbourhood, so the C-vs-M contrast that decides A1 was not reached.
- B1: any gain is token-weight retuning. **The only gain observed is token-weight retuning** (M);
  whether a learner that can move contextual weights adds anything is open.
- C1: the learned map improves training search but not the withheld compositions. **Partly**: M
  transfers, with shrinkage (holdout cost +0.38 log2 above training vs G's +0.12).
- E1: the outer loop does not improve even fresh training search at this budget. **Holds for C
  under three-coordinate mutations**; does not hold for M or T with the same operator.
- New, G1: M's change (INPUT up, DUP down) is a generic improvement of G on this alphabet, not a
  PA-family preference. Untested; nothing outside PA was scored.

Not answerable here: family specificity (no second family survived run 0001's screen), and supply
versus mutational-neighbourhood mechanisms.

Related: [root 10](../question.md), [12](../12-generic-grammar-headroom/question.md),
[plan](../../../plans/post-addition-map-adaptation.md),
[strategy 0132](../../../runs/2026-10-06-0132/strategy.md),
[run 0001 analysis](../../../runs/2026-10-06-0001/analysis.md),
[08-evolve-bias](../../01-map-bias/08-evolve-bias/question.md),
[09-generic-bias-speedup](../../01-map-bias/09-generic-bias-speedup/question.md) (INPUT/GT raise as the generic part),
[run 0132 decision](../../../runs/2026-10-06-0132/decision.md).

Reopen if parked: a cheaper or less noisy outer objective becomes available, a contextual
operator (row-wise or larger steps, or residuals on top of M) shows a training trend in a probe,
or a second family gives a specificity contrast worth a learned map.
