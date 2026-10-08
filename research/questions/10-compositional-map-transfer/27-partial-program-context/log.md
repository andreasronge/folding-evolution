# Log: 27 partial-program context

## 2026-10-08: run 2026-10-08-1831, partial-program context vs token fit on training cells — ran; useful

Experiment ([proposal](../../../runs/2026-10-08-1831/proposal.md), [plan](../../../runs/2026-10-08-1831/plan.md), commit `998a9fe`, [analysis](../../../runs/2026-10-08-1831/analysis.md)): comparison-gate-v1 training cells, D1331, P 256, G4. 16 corpora (8 BE, 8 PA), each from 32 G4 source searches per own training cell, stopped at first exact solve or 65 536 evals; at evaluated populations 64/128/256 each unsolved source archived 8 lexicase-parent tapes (S) and 8 uniform population tapes (P). Fits with the frozen 1707 rule: C_S and T_S on identical S counts, C_P on P counts; C_exact = 1246's frozen exact-solver C (hash-checked). 5 120 paired fresh searches (5 arms × 16 corpora × 4 cells × 16 seeds), 7 168 rows, 120 min, complete, no errors; 89 536 archived tapes, all verified non-exact on D1331; 0 holdout searches.

Result. Collection: 2.3/7.3/17.1% of sources solved by the three checkpoints; 29–32 contributing sources per cell; mean 1.94M source evaluations per cell, against 15.3M for 1246's exact corpora (7.9×, steward computed from both `search.jsonl`). S tapes are more accurate than P (D1331 0.68 vs 0.49). Solved: C_exact 90%, C_S 73%, C_P 73%, T_S 66%, G4 61%.
- Primary C_S/T_S **1.28× [1.12, 1.45]** (2 × cap, 95% t over 16 corpora; SD 0.24 log), 13/16 corpora; 1 × cap 1.22× [1.09, 1.36]; both-solved pairs 1.05× [0.88, 1.24]. BE 1.42× [1.17, 1.72], PA 1.15× [0.96, 1.38] (unresolved). Two of 8 cells below 1 (0.80, 0.83), the ones where T_S solves most.
- C_S/G4 **1.62× [1.37, 1.90]**, 16/16 corpora; both-solved 1.41× [1.21, 1.64]. T_S/G4 1.27× [1.10, 1.45].
- C_S/C_P 1.04× [0.92, 1.16]: no resolved parent enrichment; >1.16× excluded.
- C_S/C_exact 0.27× [0.24, 0.30]; C_exact/G4 5.97×. At unequal acquisition effort (≈ 7.9× fewer source evaluations for C_S).
- Fitted arms hit training-perfect non-exact tapes about 3× as often as G4 (107/110/101 vs 34 of 1 024 searches); they do not count as solves.
Pre-stated rule: upper bound 1.45 ≥ 1.20 (no "bounded" branch); C_S/T_S and C_S/G4 lower bounds > 1 → **useful partial-program context**, worthwhile 1.20× plausible but not established. Against expectations: C_S/T_S at the low edge of 1.3–2×; C_P ≈ C_S as expected; C_S/C_exact far below the expected 0.5–0.8. Not anticipated: the C_S-over-T_S gain is mainly a within-cap reliability gain (more solves), not faster solving when both solve; and it is BE-carried.

Where the explanations stand: A supported at this scope (training cells, development bank, one horizon); B not supported in its strong form (C_S over T_S resolved), but the both-solved decomposition and the 0.27× gap to C_exact leave room for much of the useful structure appearing only with complete assembly; C consistent at the measured resolution (parent enrichment above 1.16× excluded; a small enrichment or a loss up to about 8% is not).

Decision: close 27 as answered at this scope, and return to strategy (`next: strategy`), because the pre-stated rule routed to "useful partial-program context" with both lower bounds above 1, which by the proposal and [strategy 1831](../../../runs/2026-10-08-1831/strategy.md) is the condition for the strategist to consider the bounded feedback stage, a continuation that strategy explicitly left unallocated. Resolving the 1.20× margin alone (≈ 64 corpora, ≈ 6 h queue) would not change that choice. Further work belongs in a new sub-question once the strategist funds it. ([decision](../../../runs/2026-10-08-1831/decision.md))

## 2026-10-09 — wording correction (steward, from critique 2116 digest check, notes 7–8)

Corrections to the 1831 entry above; no new data.
- "not faster solving when both solve" overstates an unresolved, success-conditioned estimate (1.05× [0.88, 1.24]). Read: "more within-cap solves; no resolved speed difference among both-solved pairs". Run 2116 found the same pattern for F/O (both-solved 1.09× [0.95, 1.26]).
- "A supported at this scope" endorsed A's mechanism ("order/assembly information") more broadly than the run tested. C_S/T_S compares fitting procedures; K was unscored, so order is not isolated. Read: "A's predictive claim is supported on the training cells: the context-fitting procedure beats T and G4; the carrying structure is unidentified." question.md is corrected to match.
- Reopen check: 2116 used this collector's frozen C_S/T_S rows as its first-round reference (bit-exact replay) under the new question [28](../28-partial-program-feedback/question.md); nothing here needs reopening.
