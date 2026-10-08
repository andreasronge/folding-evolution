# Log: 28 partial-program feedback

## 2026-10-09: run 2026-10-08-2116, feedback vs equal-allocation one-shot on training cells — ran; small resolved gain, BE only

Experiment ([proposal](../../../runs/2026-10-08-2116/proposal.md), [plan](../../../runs/2026-10-08-2116/plan.md), commit `393a4dc`, [analysis](../../../runs/2026-10-08-2116/analysis.md)): comparison-gate-v1 own training cells, 16 lineages (8 BE, 8 PA), each one 1831 corpus. Round 1 = 1831's 32 G4 sources per cell, replayed bit-exactly in 16/16 lineages. Each acquisition arm then got two more rounds of 32 sources per cell (96 in total; 1831's collector: first solve or 65 536 evals, 8 parent tapes at generations 64/128/256, only pre-solve tapes). F: collect under C1, refit, collect under C2, freeze C3. TF: the same with token-only fits. O: both new rounds under G4, one fit to all 96. R = C1 (1831's C_S). References G4 and 1246's C_exact. 6 arms × 16 lineages × 4 cells × 16 paired fresh seeds = 6 144 scoring searches; 20 480 rows, 200 min, complete, every table hash, pairing and archive check passed, no empty cell-round.

Result (2 × cap, 95% t over 16 lineages; > 1 = first arm cheaper).
- Acquisition: sources under C1/C2 solved before the cap 27–30% of the time against 16% under G4, with more accurate tapes (D1331 0.74–0.75 vs 0.68), in both families. F used 7.4% fewer source evaluations than O (equal allocation, not equal use). Pooled contributing sources per cell 82–96 of 96: no starvation.
- Primary **F/O 1.18× [1.01, 1.37]**, SD 0.28 log, 11/16 lineages; 1 × cap 1.16× [1.01, 1.33]; both-solved pairs 1.09× [0.95, 1.26] (selection-conditioned). Solves F 74.4%, O 71.9%, R 72.8%, TF 65.5%, G4 61.6%, C_exact 91.8%.
- By family (secondary, n = 8 each): **BE 1.42× [1.17, 1.72]** (8/8 lineages), **PA 0.98× [0.83, 1.16]** (3/8). The BE–PA difference was not tested as a contrast.
- O/R 0.99× [0.89, 1.10]: tripling the G4 allocation did not change the fit's value (a gain above 1.10× excluded; a loss down to 0.89× not). F/R 1.16× [0.99, 1.36], unresolved. Because O ≈ R, these are practically one effect of about 1.16–1.18× whose lower bound sits at 1.
- F/TF 1.46× [1.23, 1.75] (14/16). TF/G4 1.28× [1.14, 1.45], close to 1831's one-shot T_S/G4 1.27× (different runs; three token rounds did not visibly beat one).
- F/C_exact 0.31× [0.25, 0.38] (R/C_exact about 0.26 here): feedback closed roughly a tenth of the first partial fit's log gap to the exact-solver fit; C_exact's acquisition cost is unmatched.
- Replication: R/G4 1.62× [1.41, 1.86] on fresh seeds, against 1831's 1.62× [1.37, 1.90].
- Shortcut searches (≥ 1 training-perfect non-exact tape): F 119, R 102, O 94 of 1 024; training-perfect tapes ≤ 0.5% of any archive.
- Price: about 600 lineages to put F/O's lower bound above 1.15; F's extra acquisition repays over R after about 12 350 future searches on these cells.

Pre-stated rule (plan precedence): UB 1.37 not below 1.15, LB 1.01 > 1, point 1.18 ≥ 1.15 → **adopt feedback provisionally; worthwhile (≥ 1.15×) gain not established**. Against expectations: F/O inside the expected 1.1–1.3×; O/R below the expected 1.05–1.15×; F/TF > 1 as expected; none of the listed surprises occurred. Not anticipated: no resolved PA gain (0.98×), with PA collection improving as much as BE.

Where the explanations stand: A (feedback) supported at this scope for BE only, at a margin just above 1 overall; B (data quantity only) not supported, since more G4 data added nothing (O/R) while feedback collection did; C (reinforcement/starvation) not supported overall (no starvation, no degradation; PA alone is unresolved around 1, admitting a loss down to 0.83× or a gain up to 1.16×). The win identifies the collection procedure, with yield and tape content bundled.

Decision: close 28 as answered at this scope, and return to strategy (`next: strategy`), because the pre-stated rule routed to provisional adoption with the worthwhile margin unresolved, resolving that margin by replication is priced at about 600 lineages, and [strategy 2116](../../../runs/2026-10-08-2116/strategy.md) allocated this one experiment and asked for a review after it ("no result automatically earns more feedback rounds"). Root 10 has 1 of 20 slots left. ([decision](../../../runs/2026-10-08-2116/decision.md))
