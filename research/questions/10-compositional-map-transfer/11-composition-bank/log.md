# Log


## 2026-10-05: run 2026-10-05-2039, composition bank feasibility (blocked, not run)

Experiment: [proposal](../../../runs/2026-10-05-2039/proposal.md). Alphabet `v2_rmin` (v2_probe +
REDUCE_MIN), a latent-allele decoder, a 3 reducer-pair × 3 combiner bank screened
exhaustively for aliases (stage A), then 50 paired seeds per cell under four decoder arms
U/F/G/G-marg plus 2·10⁸-sample sampling (stage B), a gated top-up (stage C), and a pre-stated
transversal split rule. Critic: approve_with_notes (6 notes: calibrate throughput first; make
the split rule executable for 7–8-cell banks and per canonical length; pooled top-up counts
and unestimated medians; validate uniform decoding against `v2_rmin`, not old `v2_probe`
rates; freeze G and its marginal measurement; report total experiment-2 cost, not per-queue).

Result: none. The driver stopped at `prepare` before any code was written: merging `main`
(research-loop v2, commits c67c112, 3512f3b, b912e90) into `research/main` conflicts on one
file, `research/runs/2026-10-05-1957/code_review.md` (add/add). Nothing was measured; no
`execution.md`, so the budget slot is not charged. The steward's read-only probes in the
proposal (ANY constant on 624/625 inputs; GT cells ≥ 96% single-reducer thresholds;
integer-valued X+Y, 2X+Y, S>0?X:Y cells ≤ 69% best-simpler agreement; MIN-free cells solved in
roughly 5k–524k evaluations) stand as unreviewed probes, one run each.

Decision: continue 11 and re-propose the same experiment with the critic's six notes folded in
([run 2026-10-05-2242](../../../runs/2026-10-05-2242/proposal.md)), because the block was
operational, the question is unchanged, its slot is unspent, and the strategy names this
feasibility step as the prerequisite for everything else under root 10. The owner must resolve
the merge conflict first or the next cycle will block again.
