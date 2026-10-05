# Log

## 2026-10-06: opened from 11 (run 2026-10-05-2247)

Opened with budget 1 after 11's bank failed headroom against G. Sent to the strategist first.
Strategy 0001 chose the [assembly-family plan](../../../plans/compositional-family-headroom.md)
(two same-primitive families, addition in different structural positions, frozen G kept as a
bank-informed benchmark). The steward's probes and proposal are logged in the
[root log](../log.md).

## 2026-10-06: run 2026-10-06-0001, assembly-family alias screen + 10-token search calibration

Experiment: exhaustive alias screen (depth 8 stored + depth 9 output-only, typed-stack dedup)
of 162 frozen ten-token canonicals in six shapes — gate `(A+B)>0 ? C : D`, branch-then
`S>0 ? (X+Y) : Z`, branch-else `S>0 ? Z : (X+Y)`, post-addition `(S>0 ? X : Y) + Z`, linear
`2X+Y+Z` and `2(X+Y)+Z`, reducers {S, M, m} — on three domains (625, 1 331, 2 401 inputs);
frozen pair rule (≥ 4 retained cells per shape, shared token multiset, role-covering holdout
pair). Then stage B: U/F/G/G-marg (frozen 2247 tables) × 50 paired seeds on every cell retained
on D1331, cap 524 288, plus 10⁸ sampled genotypes per arm. Stages C (family grammars) and D
(cost projection) were gated on a pair. ([proposal](../../../runs/2026-10-06-0001/proposal.md),
[plan](../../../runs/2026-10-06-0001/plan.md),
[analysis](../../../runs/2026-10-06-0001/analysis.md); commit `a65ded0`, 35 min wall, clean.)

Result: **outcome row 1** (complete data).
- Retained cells (D625 / D1331 / D2401): gate 0/0/0 of 18, branch-then 0/0/0 of 27,
  branch-else 1/2/2 of 27, post-addition 4/8/8 of 54, each linear shape 3/3/3 of 18.
  0 of 45 shape-pair × domain rows eligible. Branch-else/post-addition share a token multiset
  and post-addition has a valid split on the two wider domains; the pair fails only because
  branch-else has 2 < 4 cells. The linear pair has 3 cells by construction (split-rule failure,
  not aliasing). The verdict does not move for any alias cutoff in 0.70–0.85; a pair first
  appears at 0.90 (D1331, BT/PA).
- The witnesses name the identities: ADD distributes out of an IF_GT branch through the
  executor's CONST_0 default, DUP reuses the condition when it is also a branch value, and
  near-aliases come from constant substitution (`M ≈ 5` given S>0) and the sign correlation of
  S and S+X. Every retained branch cell has condition S.
- Stage B (D1331, 16 cells × 4 arms × 50 seeds, all complete, no top-up owed): G medians
  8 192–41 728 on the ten branch cells (2–10× the 4 096 line), 2 304–5 120 on the six linear
  cells (3 below the line, 1 on it). F and G-marg medians above the line on all 16
  (minima 9 216 and 8 704). Paired capped-time ratios: G/U 8.4–11.3× (16/16 intervals exclude
  1), G/G-marg 1.5–6.0× (15/16), F/U 1.0–3.6× (4 intervals include 1). Hard cell
  BE:S?M:(S+m): U 8/50, F 22/50, G-marg 34/50, G 42/50; two G seeds there sat on
  training-perfect wrong programs.
- Sampling: U 0 hits in 10⁸ on every cell (≤ 3.0×10⁻⁸ each); G 13–180 per 10⁸; F and G-marg
  0–2 per cell. Supply ratios against U are lower bounds only.
- Cost: mean 1.1 s (G) to 4.3 s (U) per run including capped runs; 3 200 runs in 19 min on 8
  workers; the screen is ~90 s and 4.9 GB per domain.

Decision: close 12 because the frozen design space is answered: none of the six enumerated
same-primitive shapes on `v2_rmin` over {S, M, m} yields an eligible family pair on any of the
three domains (row 1), and the obstacle is named (ADD/IF_GT/CONST_0/DUP identities and S-sign
correlation), not a threshold or domain artefact. This does not show every length-≤ 10 family
aliases or that an alphabet change is required. The question's other half has a positive,
operational answer: ten-token post-addition and branch-else cells sit 2–10× above the 4 096
line under the frozen G and are tractable under G, F and G-marg, so headroom against G is
available at this length. Return to strategy (row 1, and strategy 0001's "review after another
bank failure"): whether root 10 continues with a one-family post-addition split, a different
contrast, or an alphabet change is a program-level choice.
