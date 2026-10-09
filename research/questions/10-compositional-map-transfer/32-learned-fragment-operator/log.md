# Log: 32 learned fragment operator

## 2026-10-09: steward probe (run 2026-10-09-0826), read-only

Knockout (NOP substitution, 96 fixed inputs) of all 1 808 1246 G4 exact-solver tapes with
research/main's Python executor: 0 label mismatches; median 20 knockout-active tokens per tape
(IQR 17–23). Per corpus, 255–386 distinct contiguous all-active 3–6-token windows occur in
≥ 2 of the corpus's 4 source cells (3-token ~150, 4-token ~100, 5-token ~45, 6-token ~15).
29 s. Observation only: recurrence is not evidence of reusable computation.

## 2026-10-09: steward probe (run 2026-10-09-0843), read-only

Leave-one-cell-out libraries (same knockout rule; windows recurring in ≥ 2 of the other 3 cells):
138–307 per held-out cell (median 208) across 64 corpus × cell sets. The top 32 (rank: source
cells, count, length, tokens) are ~75% length 3 and ~22% length 4; none solves any of the
corpus's 4 cells when NOP-padded. Null pseudo-arm splits of 1246 C rows give a corpus-level
log-ratio SD of 0.27 at 16 seeds/cell and 0.19 at 32 (95% half-width ×1.155 / ×1.107).
[Probe](../../../runs/2026-10-09-0843/steward_probe/loo_probe.py). 30 s. Proposal revised
after [critique 0826](../../../runs/2026-10-09-0826/critique.md).

## 2026-10-09: run 2026-10-09-0843 (slot 23), fragment block edits on training cells — ran

Commit `e347793`, [analysis](../../../runs/2026-10-09-0843/analysis.md),
[proposal](../../../runs/2026-10-09-0843/proposal.md). C's 16 frozen comparison-gate tables and
search unchanged (P 256, lexicase, 524k cap); arms C (no operator), F (intact fragment from the
cell's leave-one-cell-out library of 32), B (library per-position marginals, same length law),
W (C's own chain from the preceding token); each non-elite child gets one 3–6-token block with
p 0.2, window + next allele re-encoded, decoded suffix kept. 16 corpora × 4 training cells × 32
paired seeds = 2 048 searches per arm; complete roster (8 192 rows), all prepare checks passed
(10k edit audit/arm, 16 historical C replays exact, 128 smoke replays), 74 min queue.

Solved C 90.6%, F 93.8%, B 90.8%, W 94.1%. Primary metric (unsolved = 2 × cap, t over 16
corpora): F/C **1.57× [1.42, 1.75]** (16/16 corpora > 1; BE 1.47×, PA 1.68×; 1 × cap 1.54×;
both-solved 1.47×), F/B **1.60× [1.45, 1.77]**, F/W **1.23× [1.12, 1.36]** (13/16 corpora),
W/C 1.28× [1.17, 1.39], B/C 0.98× [0.93, 1.04]. Tokens changed per edit F 2.79, B 2.80, W 2.92.
Per cell (descriptive, df 7) F/C 0.99–2.17×; on `BE:F>S?F:M+m` F/C 0.99× [0.70, 1.41] and F/W
0.79× [0.65, 0.96]. The libraries are mostly the bank's shared 3-token syntax (lengths 3/4/5/6 =
1554/409/80/5 of 2 048 slots; 16–23 of each corpus's 32 fragments shared by all four LOO
libraries). F solvers carry more library windows (9.4 vs 7.8 distinct; 81% vs 70% with a 4+-token
fragment), occurrence not ancestry. Precision scenario matched (observed half-width ×1.10–1.11).

Rule 1 fired (`earns_review_of_reuse`). Steward's guess (F/C 1.0–1.15) was wrong; the result is
in the proposal's "surprising" region. Interpretation limits: training cells of a development
bank (no transfer; LOO libraries barely differ); W/C mixes block locality with chain content
(C's point mutation re-decodes the suffix, block arms keep it), and B is not a clean locality
control; nothing about evolutionary acquisition.

Decision: keep 32 open and return to strategy (`next: strategy`), because the pre-registered
rule 1 sends the reuse stage to strategy review, root 10 has no slot left, and the result raises
a competing question (why a library-free block edit, W, beats C by 1.28×) that the strategist
should weigh against reuse. ([decision](../../../runs/2026-10-09-0843/decision.md))
