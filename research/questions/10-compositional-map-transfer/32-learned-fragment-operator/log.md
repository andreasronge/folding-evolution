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

## 2026-10-09: steward probe (run 2026-10-09-1036), read-only

Variance components of 0843's paired log-cost contrasts (16 corpora × 128 pairs): pair SD
1.85–1.88; between-corpus SD F/W 0.06, F/C 0.10, W/C ≈ 0. Projected F/W 95% half-width
×1.136 / ×1.098 / ×1.082 / ×1.072 at 64 / 128 / 192 / 256 pairs per corpus (training-noise
scenario). Whole-corpus libraries (0843 prepare): 32/32 in all 16 corpora, 113 distinct
fragments, lengths 3/4/5 = 398/95/19 slots, none dropped as padded solvers.
[Probe](../../../runs/2026-10-09-1036/steward_probe/variance_probe.py). Budget raised 1 → 2
for the reuse stage allocated by [strategy 1036](../../../runs/2026-10-09-1036/strategy.md).

## 2026-10-09: run 2026-10-09-1036 (slot 24), frozen fragment reuse on excluded compositions — ran

Commit `348f9e2`, [analysis](../../../runs/2026-10-09-1036/analysis.md),
[proposal](../../../runs/2026-10-09-1036/proposal.md), [plan](../../../runs/2026-10-09-1036/plan.md).
C's 16 frozen comparison-gate tables and search unchanged (P 256, lexicase, 524k cap). Arms C (no
operator), F (one intact fragment, p 0.2 per non-elite child, from the corpus's whole-corpus
library of 32 fragments from all four training cells, rebuilt to the pinned 0843 hashes) and W
(C's own chain from the preceding token, F's length and start laws). No B arm. Primary:
then-addition-v1, 16 corpora × 16 cells × 16 seeds (4 096 paired searches per arm); reference:
the 8 comparison-gate holdouts, 16 × 8 × 8 (1 024 per arm). Complete roster (15 360 rows), every
prepare check passed (libraries 32/32 and equal to 0843; 10k-edit audits; 16 historical C replays
bit-exact; 12 288 NOP-padded fragment/cell tests with 0 solvers; 96 smoke replays). 152 min queue.

Solved, then-addition: C 87.1%, F 90.8%, W 88.9% (C matches 1548's 86.5%); holdouts C 92.8%,
F 96.9%, W 96.3%. Primary metric (unsolved = 2 × cap, t over 16 corpora, 15 df), then-addition:
F/W **1.195× [1.111, 1.286]** (14/16 corpora; BE 1.15× [1.01, 1.33], PA 1.24× [1.14, 1.35];
1 × cap 1.18× [1.10, 1.26]; both-solved 1.15× [1.09, 1.22]); F/C **1.466× [1.380, 1.558]**
(16/16 corpora); W/C 1.227× [1.148, 1.311] (16/16). Holdouts (reference, no rule): F/W 1.27×
[1.17, 1.38], F/C 1.75× [1.57, 1.95], W/C 1.38× [1.23, 1.56]. Observed F/W half-width ×1.076
against the projected ×1.072. Descriptive ratio of then-addition to 0843 training values (not a
clean attenuation estimate: LOO 3-cell libraries there, whole 4-cell libraries here): F/C 0.93×
[0.83, 1.05], F/W 0.97× [0.86, 1.09], W/C 0.96× [0.85, 1.10]; C/T lost a third across the same
shape change (0.68×). Per cell (descriptive): F/C above 1 in 16/16 (13 resolved), F/W 0.96–1.54
(15/16 above 1, 5 resolved), W/C 0.97–1.59; across cells log F/W and log W/C correlate −0.67
(post hoc): where chain blocks help most, fragments add least. Libraries: 113 distinct fragments
in 512 slots (lengths 3/4/5 = 398/95/19), mostly shared syntax (`input first gt`, `add input
first`, `input reduce_min input` in all 16). F solvers carry more library windows (9.1 vs 7.4
distinct; 74% vs 62% with a 4+-token window), occurrence not ancestry. Repayment (descriptive):
F saves 1.51 worker-s per then-addition search against C and 0.50 against W; extraction costs 4 s,
but the shared solver corpus cost 48 039 worker-s, about 96 000 searches of F-over-W saving.

Rule 2 fired (`repertoire_earns_acquisition_review`): F/W lower bound > 1 with point ≥ 1.10, and
F/C lower bound > 1. This does not establish a true F/W increment above 1.10 (the lower bound
clears it by 1%; both-solved and BE-only lower bounds do not). Steward's guess (F/W 1.05–1.15,
F/C ~1.4, W/C ~1.25) was right on F/C and W/C, slightly low on F/W. Interpretation limits: both
banks are development banks and then-addition needs the libraries' shared joins by construction,
so this is reuse of one literal-block procedure across one shape change, not modularity,
fresh-bank transfer, family specificity or acquisition; without B on this shape, F/W does not
separate intact content from changed token supply.

Decision: close 32 and return to strategy (`next: strategy`), because the question is answered
at its tested scope (training cells, protected holdouts and one excluded shape all favour F over
C and W), both its slots are used, and pre-registered rule 2 routes to a strategy review of
whether to acquire a repertoire, which is a different question with an unpriced design.
([decision](../../../runs/2026-10-09-1036/decision.md))
