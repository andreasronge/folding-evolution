# Log: 41 same-alphabet family preference

2026-10-10 (steward, run 2026-10-10-1717): opened. Read-only probe at proposal time (research/main
`7244fa1`, Python semantic executor; the installed Rust module predates `v2_x4`): the TS shape gives 1020
distinct behaviours on D625 (216 role assignments use all four readouts with distinct addition pairs); a
greedy ≥ 80%-disagreement set has 540 cells; the maximum agreement of any TS behaviour with any of the 24
DG clique cells is 0.26, so the two rosters cannot alias each other. The exhaustive ≤ 9-token alias screen
did not finish within the 10-minute probe limit (depth 8: 14 M states, 3.8 GB, 20 s; depth 9 over 1020
cells > 10 min), so it moves to preparation. The 8 spare DG clique cells appear in no 0145/0311/1536 jsonl.

Decision: propose the crossed comparison ([proposal](../../../runs/2026-10-10-1717/proposal.md)) because
it is the strategy's allocated question and the bank looks admissible; the alias screen is a preparation gate.

## 2026-10-10: run 2026-10-10-1717, crossed DG/TS A8 cohorts on one alphabet — ran

Slot 33 of root 10. Commit `b5697a1`, code review pass, [analysis](../../../runs/2026-10-10-1717/analysis.md),
[execution](../../../runs/2026-10-10-1717/execution.md). Preparation 17.8 min, scoring 57.1 min (timeouts 80 + 140).
New performance-blind TS bank `x4-branch-sum-v1`: exhaustive ≤ 9-token screen (216 cells), 80 % rule, maximum
clique 108, 4/4/8 split; alias checks passed; all admission gates passed. The 24 DG builds of 1536 reused
(hash-verified); 24 fresh TS builds. Scored 16 never-searched target cells (8 spare DG, 8 TS) × 48 shared seeds ×
{G4, D, T} = 2 304 searches, complete, no errors.

- Acquisition is very unequal: G4 first batch solved TS sources 242/384 (63 %) against DG's 64/384 (17 %);
  all 24 T builds reached a full 32-fragment library (D: 18/24; 8 D builds had an empty intermediate library);
  T acquisition 6.1 M evaluations per build, D 12.5 M.
- Solved of 384: DG roster G4 59, D 307, T 187; TS roster G4 266, D 364, T 372.
- P_DG = cost(T on DG)/cost(D on DG) **2.98× [2.07, 4.33]** at 2 × cap, 2.40× [1.76, 3.30] at 1 × cap; 8/8 DG
  cells favour D (1.8–6.3×); same-seed pairs 236 D-cheaper vs 107.
- P_TS = cost(D on TS)/cost(T on TS) **1.29× [0.94, 1.78]**, 1.27× [0.94, 1.72] at 1 × cap; 5/8 cells favour T,
  per-cell ratios 0.39–1.62; same-seed pairs 211 T-cheaper vs 171. Direction unresolved.
- I = √(P_DG·P_TS) **1.96× [1.58, 2.44]** at 2 × cap (margin 1.5× cleared), 1.75× [1.45, 2.12] at 1 × cap
  (not cleared): penalty-sensitive. Almost all of I's excess comes from P_DG.
- Every arm beat G4 on both rosters: G4/D on DG 8.21× [5.98, 11.13] (replicates 1536's 10.1× on 8 new cells
  with the same builds), G4/T on DG 2.75× [2.20, 3.47], G4/D on TS 6.31× [4.69, 8.45], G4/T on TS 8.13× [6.39, 10.28].
- Pre-stated labels: material geometric interaction (2 × cap only); one resolved direction (D preferred on DG);
  not reciprocal; no dominant bias; own-family useful; neither the family-specific-acquisition nor the
  shared-bias candidate fired.
- Limits: the TS roster is near ceiling for fitted arms (95–97 % solved), so it had little power to separate
  the cohorts; the D cohort learned from harder sources that contain the `(a+b)>(c+d)` join, so family content
  and source difficulty are not separated; context, fragments and supply bundled; DG is a development bank.
- Economics (descriptive): median searches to repay acquisition on both rosters D 49, T 33.

Decision: close 41 at this scope because the crossed comparison ran cleanly and gave its answer for the
direction that could be measured: acquisition on the double-gate family carries a large, charge-robust
preference for its own unseen cells (≈ 3× over a TS-built bias), while a TS-built bias is not resolved
better than a DG-built one on TS cells, and that roster lacks the headroom to resolve it. More builds on the
same roster would mostly buy precision on a compressed contrast. Whether the DG advantage is the join content
or a harder, richer-in-structure source corpus is a new mechanism question, left to the strategist with the
saved-build attribution option; root 10's 33 slots are used, so `next: strategy`.
([decision](../../../runs/2026-10-10-1717/decision.md))
