# Log: 29 frequency-matched transfer control

## 2026-10-09: proposed in run 2026-10-09-0125 (score frozen K on 1548 row F seeds)

## 2026-10-09: run 2026-10-09-0125, frozen K vs C on then-addition — ran; pooled frequencies insufficient

Experiment ([proposal](../../../runs/2026-10-09-0125/proposal.md), [plan](../../../runs/2026-10-09-0125/plan.md), commit `8e62831`, [analysis](../../../runs/2026-10-09-0125/analysis.md)): the 16 frozen 1246 K tables (8 BE-, 8 PA-fitted; G4 × 24 multipliers matched to C's pooled emitted marginals, max error 2.90e-5) scored on 1548 row F's 16 then-addition cells with the same 8 paired seeds and 64-case draws as C and T: 2 048 new searches, 41.5 min, complete. Preparation passed: 48 table hashes, bank SHA, 32/32 C/T rows replayed bit-exactly on the current build, 16 timing rows replayed identically inside the full roster. C, T and G4 rows reused from 1548.

Result (2 × cap, 95% t over 16 corpora; > 1 = first arm cheaper).
- Primary **C/K 2.48× [2.17, 2.83]** (sd log 0.25); 1 × cap 2.25× [1.98, 2.54]; both-solved pairs 1.92× [1.68, 2.21] (selection-conditioned, 16/16 corpora occupied).
- All 16 corpora (1.44–3.67×) and all 16 cells (1.42–3.67×) above 1.20. BE-fitted 2.77× [2.36, 3.25], PA-fitted 2.21× [1.77, 2.76] (secondary, not contrasted).
- **K/T 0.86× [0.77, 0.96]**: K slower than T in 14/16 corpora; descriptive share log(K/T)/log(C/T) = −0.21. T and K are the same model class (G4 × 24 multipliers); the ML choice beats the pooled-marginal choice.
- K/G4 1.57× [1.45, 1.70] (unpaired G4, descriptive). C/T reproduced 2.12× [1.86, 2.41].
- Solves C 1 771, T 1 547, K 1 484 of 2 048; G4 162/256. Paired per search: K slower 1 322, tie 103, faster 623. Shortcut runs (training-perfect, not exact; never counted) C 174, T 156, K 126.

Pre-stated rule: LB 2.17 ≥ 1.20 → **this G4-based pooled-frequency replacement is insufficient within 20% on these cells**. Against expectations: C/K at the top of the expected 1.5–2.5×; K/T inside the expected 0.8–1.1; neither named surprise occurred. Not anticipated by the plan: K/T's interval excludes 1, replicating question 20's 0.83× on a second bank.

Where the explanations stand: A (more than pooled frequency) supported at this scope; B (pooled frequency suffices) not supported; C (partial recovery of C/T) not supported, since K recovers none of C/T. Which structure carries C − K (context dependencies, positional frequencies, or both) is not separated.

Decision: close 29 as answered and return to strategy (`next: strategy`), because the pre-stated rule routed to "insufficient", root 10's 20 slots are now used, and [strategy 0125](../../../runs/2026-10-09-0125/strategy.md) asked for a review after this comparison with the fragment plan's full price. ([decision](../../../runs/2026-10-09-0125/decision.md))
