---
status: closed
tags: [compositional-transfer, task-bank, feasibility, decoder, stack-tape, reduce-min]
budget: {experiments: 1, used: 0}
---
# Is there a tractable bank of held-out reducer/combiner compositions with room for a learned decoder?

Current summary: **Not this bank** (run 2026-10-05-2247, commit `0995d33`, row 2; slot spent).
The 3 reducer-pair ({S,M}, {S,m}, {M,m}) × 3 combiner (X+Y, 2X+Y, S>0 ? X : Y) bank on
`v2_rmin`, length-4 lists in {-2..2}, fails for two independent reasons:
- **Tractability at 524 288 evaluations.** Exhaustive screening to depth 6 kept 8 of 9 cells
  (SM-SEL is an exact alias). Uniform search solved 7 of the 8 in ≥ 35/50 runs, but Sm-SEL only
  27/50 (95% 39–68%, still rising at the cap; a reviewer probe reached 36/50 at 2M). With one
  SEL cell aliased and the other slow, 0 of 6 transversals are eligible. A 2–4× larger cap might
  fix this; untested.
- **Headroom against the hand-set grammar G (binding).** G solved every retained cell in every
  seed, with medians 768–1 024 (ADD), 1 792–2 304 (DADD) and 3 584–4 096 (SEL) evaluations.
  Every transversal holds out an ADD and a DADD cell, both below the 4 096 line under G, so all
  four structural splits fail the 4 096-evaluation headroom rule under G; raising the search
  cap alone does not remedy this (whether another decoder could improve on G here was not
  tested). G's rows (INPUT → reducer; int →
  INPUT/ADD/DUP/IF_GT) are the syntax of every canonical program here; 67–100% of each cell's
  canonical bigrams occur in other cells.

Descriptive map-bias numbers from the same run (paired seeds, 95% paired bootstrap): F/U
1.9–3.5×; G/U 8.6–13× (ADD/DADD), 31× (18–44) on Mm-SEL; G/G-marg 2.6–4.5× (ADD/DADD), 9.9×
and 19.5× on the SEL cells, all intervals above 1. G raised exact-solver supply 120–1 650× over
U; the search speed-up was about ten times smaller. G/G-marg mixes supply with mutation
structure (1.65 vs 0.95 tokens changed per allele mutation), so it is not a mechanism. Nothing
here tests a learned decoder.

Competing explanations as tested (about this design, not root 10's answer):
- Bank (too few non-aliased cells): **no** — 8 of 9 survive exhaustive screening.
- Tractability: **yes, at 524k, for one cell** (Sm-SEL), which is enough to block every split.
- Headroom: **yes, and it alone blocks every split** — the generic grammar already covers this
  family's syntax.
- Cost: not reached; no split was selected, so no experiment-2 cost was computed.

Related: [root 10](../question.md), [plan](../../../plans/compositional-map-transfer.md),
[run 2247 proposal](../../../runs/2026-10-05-2247/proposal.md),
[analysis](../../../runs/2026-10-05-2247/analysis.md),
[decision](../../../runs/2026-10-05-2247/decision.md); blocked earlier attempts
[2039](../../../runs/2026-10-05-2039/proposal.md), [2242](../../../runs/2026-10-05-2242/proposal.md);
follow-up [12-generic-grammar-headroom](../12-generic-grammar-headroom/question.md) (closed, run 2026-10-06-0001).

Reopen if: the strategist decides that G was an oracle rather than a fair control for this
bank (for example, root 10 adopts a weaker, type-valid generic grammar as its fixed control)
**and** a larger cap (≥ 1M) makes Sm-SEL tractable; then only the new control arm and a
larger-cap Sm-SEL top-up need running; stage A and the U/F data stand.
