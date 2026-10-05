---
status: closed
tags: [compositional-transfer, task-bank, feasibility, decoder, generic-grammar, headroom, alias-screen]
budget: {experiments: 1, used: 0}
---
# Is there a bank where a fixed generic grammar leaves room for a learned decoder?

Current summary: **Headroom yes at ten tokens; a same-primitive family pair, no — for the
screened design space** (run 2026-10-06-0001, commit `a65ded0`, outcome row 1; slot spent).

Background: in 11's reducer/combiner bank the hand-set previous-token grammar G
(INPUT → reducer; int → INPUT/ADD/DUP/IF_GT) solved every held-out cell in a median of
768–4 096 evaluations, so all four structural splits failed the 4 096-evaluation headroom rule.
G already solves those cells below the operational threshold; whether learning could improve
on its rows was not tested. Strategy 0001 kept G frozen as a bank-informed benchmark and asked
for two assembly families using the same primitives
([plan](../../../plans/compositional-family-headroom.md)).

What run 0001 found (exhaustive ≤ 9-token alias screen of 162 ten-token canonicals, three
domains; 50 paired seeds per cell × arm on D1331):
- **No eligible family pair.** Gate and branch-then keep 0 cells on every domain, branch-else at
  most 2 of 27, post-addition 4–8 of 54, each linear shape 3 of 18 by construction. Most
  failures are exact ≤ 9-token identities (ADD distributed out of an IF_GT branch via CONST_0;
  DUP reusing the condition); the rest are near-aliases from constant substitution and the sign
  correlation of S and S+X. Insensitive to the alias cutoff over 0.70–0.85 and to the domain.
- **Ten-token branch cells leave room above G.** G medians 8 192–41 728 on the ten
  post-addition/branch-else cells (2–10× the 4 096 line), solved in ≥ 42/50 seeds; F and G-marg
  above the line on all 16 retained cells. G/U 8.4–11.3× and G/G-marg 1.5–6.0× (paired
  capped-time ratios; 16/16 and 15/16 intervals exclude 1). Under U 13/16 cells reach ≥ 35/50;
  BE:S?M:(S+m) only 8/50.
- Post-addition alone has a valid split on D1331/D2401 (6 training, 2 holdout cells, both
  holdouts > 13k under G), but that is one family, not the two-family contrast asked for.

Scope: six shapes with conditions and operands from {S, M, m} on `v2_rmin`, three finite
domains, the frozen ≥ 80% alias and ≥ 4-cell/role-coverage rules. Not screened: families using
other tokens, longer canonicals, relaxed split rules. The run does not show that an alphabet
change is necessary, and no family grammar, learned decoder or transfer was measured.

Competing explanations as tested:
- "Any short bank on this alphabet is covered by a generic previous-token grammar": **not
  supported at length 10** — G leaves 2–10× headroom on branch cells. Still open whether a
  previous-token decoder can carry a family contrast (stage C never ran).
- "Banks deep enough to escape G are intractable under U": **mostly no** at 524k — 13/16 cells
  ≥ 35/50 under U, but one branch-else cell is hard for every arm except G.
- New, the binding obstacle: **semantic** — with ADD, IF_GT, CONST_0 and DUP over {S, M, m},
  most structural variants of a ten-token assembly have a shorter equivalent, so two families
  with enough distinct cells did not survive.

Related: [root 10](../question.md), [11](../11-composition-bank/question.md),
[run 2247 analysis](../../../runs/2026-10-05-2247/analysis.md),
[run 0001 analysis](../../../runs/2026-10-06-0001/analysis.md),
[run 0001 decision](../../../runs/2026-10-06-0001/decision.md),
[plan](../../../plans/compositional-family-headroom.md).

Reopen if: the strategist adopts a family design whose candidate shapes are not in the
screened 162 (other tokens, a fourth reducer, longer canonicals, or a non-sign-aligned
comparison) and a probe shows ≥ 4 retained cells per family; or root 10 accepts a one-family
post-addition split, in which case this run's stage A/B data (`a65ded0`) are reusable.
