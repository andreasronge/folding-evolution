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

## 2026-10-05: run 2026-10-05-2242, composition bank feasibility, second attempt (blocked, not run)

Experiment: [re-proposal](../../../runs/2026-10-05-2242/proposal.md), the 2039 study with the
critic's six notes folded in (stage 0 calibration, split rule for 7–9-cell banks, pooled top-ups,
censored medians, decoder validation against direct `v2_rmin`, frozen G/G-marg, total
experiment-2 cost). Critic: approve_with_notes ([critique](../../../runs/2026-10-05-2242/critique.md)):
no blanket underflow pruning in stage A; define the "no feasible inner budget" case; variance of
the capped cost min(T, B); marginal-matched controls in the transfer cost; headroom for all six
transversals; say which unresolved outcomes teach little. Auto-approved.

Result: none. The driver stopped at `prepare` on the same add/add conflict as 2039
(`research/runs/2026-10-05-1957/code_review.md`). No code, no `execution.md`, slot not charged.
The steward then resolved the conflict by hand: merge commit `823bc27` on `research/main`
takes `main`'s version (the second-pass review, verdict pass, which supersedes research/main's
first-pass review, kept in `8eea519`). `main` is now an ancestor of `research/main`; driver tests
pass (38/38). Not pushed.

Decision: continue 11 with the same study, the 2242 notes folded in
([run 2026-10-05-2247](../../../runs/2026-10-05-2247/proposal.md)), because nothing was measured,
the block was operational and is now removed, and this feasibility step is still the
prerequisite for everything under root 10.

## 2026-10-06: run 2026-10-05-2247, composition bank feasibility, third attempt (ran; row 2)

Experiment: [proposal](../../../runs/2026-10-05-2247/proposal.md), the 2242 design with its
notes folded in. Alphabet `v2_rmin`, latent-allele decoder (R = 23 000) with four arms
(U uniform, F fixed token bias, G hand-set previous-token grammar, G-marg = G's token
marginals with context removed). 3 reducer pairs ({S,M}, {S,m}, {M,m}) × 3 combiners (ADD,
DADD, SEL). Stage A exhaustive alias screen to depth 6; stage B 8 cells × 4 arms × 50 paired
seeds, cap 524 288, P 256, lexicase on 64 cases, exact check on 625; stage C 8 top-ups × 100
fresh seeds; 2·10⁸ sampled genotypes per arm. Critic approve_with_notes; code review passed
on the second pass. Commit `0995d33`, 19 min wall, no failures.

Result ([analysis](../../../runs/2026-10-05-2247/analysis.md)): **row 2**, with row 3 firing as
a diagnostic.
- Alias screen: 8 of 9 cells retained. SM-SEL is a real alias (a 6-token program solves it
  exactly; the other orientation has a 94.4% shorter near-alias).
- Tractability (U ≥ 35/50 or ≥ 105/150): 7 of 8 pass. Sm-SEL is 27/50 (54%, 95% 39–68%), curve
  still rising at the cap (17 → 21 → 27/50 at 131k/262k/524k); a reviewer probe on other seeds
  gave 26/50 at 524k and 36/50 at 2M. Because SM-SEL is aliased and Sm-SEL is not tractable,
  0 of 6 transversals are eligible: two need SM-SEL, two hold out Sm-SEL, two hold out Mm-SEL
  and then training has no SEL cell.
- Headroom (diagnostic, tractability waived): all 4 structurally possible transversals lack
  headroom, every time because of G. G medians: ADD 768–1 024, DADD 1 792–2 304, SEL 3 584 /
  4 096 evaluations (intervals of the SEL medians span the 4 096 line). Since every transversal
  holds out one ADD and one DADD cell, and G is below 4 096 on all of them, **no transversal of
  this bank can have headroom against this G**, whatever the cap. F alone leaves headroom.
- Map arms (paired seeds, median-speed ratio, 95% paired bootstrap): F/U 1.9–3.5× on the seven
  resolved cells; G/U 8.6–13.1× on ADD/DADD and 31× (18–44) on Mm-SEL; G/G-marg 2.6–4.5× on
  ADD/DADD, 9.9× (4.7–28) on Mm-SEL, 19.5× (4.6–36) on Sm-SEL, all intervals above 1. G raises
  exact-solver supply 120–1 650× over U; its speed-up is about ten times smaller. G mixes higher
  supply with a different mutation structure (1.65 vs 0.95 tokens changed per allele mutation),
  so G/G-marg names no mechanism.
- 67–100% of each cell's canonical bigrams occur in other cells' canonical programs: the
  bank is one shallow syntactic family (INPUT → reducer; int → INPUT/ADD/DUP/IF_GT), which is
  exactly what G's rows spell out.
- 43 of 2 400 runs met training-perfect but inexact programs; all caught by the exact check.

Decision: close 11 because it is answered for this candidate bank: no eligible split exists
at 524 288 evaluations (the pre-stated row 2), and, independently and more bindingly, no
transversal can have headroom against the hand-set grammar G, so a larger cap would not
rescue it. Return to strategy (as rows 2 and 3 prescribe) with two bottlenecks — a thin SEL
column and a family G already covers — and the redesign question opened as
[12-generic-grammar-headroom](../12-generic-grammar-headroom/question.md). This is a
limitation of this bank against this control, not a negative answer to root 10.
