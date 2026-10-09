# Log: 33 pre-solve fragment source

## 2026-10-09: steward probe (run 2026-10-09-1350), read-only

[Script](../../../runs/2026-10-09-1350/steward_probe/partial_library_probe.py), 2 s. One S tape
per 1831 source search and checkpoint (lowest archive slot, performance-blind): 331–359 tapes per
corpus. The 0843 rule (all-active 3–6 windows, ≥ 2 source cells, top 32) fills 32/32 in all 16
corpora; every fragment recurs in all 4 source cells and ≥ 11 distinct source searches; 9–18
(about 14) of 32 fragments are shared with the 1036 exact library. Pre-solve libraries lack the
`gt` comparison joins and hold `input <reducer> if_gt` windows instead. Observation only.

## 2026-10-09: run 2026-10-09-1350 (33), pre-solve fragments vs C-chain blocks on then-addition — ran

Slot 25 (strategy 1350 raised root 10's budget 24 → 25). Commit `e9a04f8`,
[analysis](../../../runs/2026-10-09-1350/analysis.md), code review pass. 1036's harness unchanged
(C tables from 1548, P 256, lexicase, 524k cap, block edit on non-elite children at p 0.2, decoded
suffix kept). E: fragment from the corpus's pre-solve library (frozen probe rule; ranking by cell
count then raw occurrence, as plan.md fixed). W_E: C-chain blocks with E's length and start laws.
then-addition-v1 (development bank), 16 corpora × 16 cells × 16 seeds = 4 096 paired searches per
arm, same seeds as 1036; the 1036 F/W/C rows replayed bit-exactly (48/48), so all five arms are
paired. 84 min scoring, 16 seeds admitted, no fallback library, 0 padded hits on 8 192 checks.
Source tapes all before their search's first exact solve (generations 64/128/256).

Primary E/W_E **0.981× [0.911, 1.057]** (7/16 corpora > 1; pairs 2 000 vs 1 985, 111 ties; 1 × cap
0.981 [0.918, 1.049]; both-solved 0.989 [0.931, 1.051]; BE 0.977 [0.875, 1.090], PA 0.986 [0.866,
1.122]). Half-width ×1.077 (corpus SD 0.139), as projected. Secondary, paired: E/F **0.843× [0.795,
0.892]** (0/16 corpora, 16/16 cells below 1, 5 resolved; largest deficit on `M>F?S+m:m`, 0.62);
E/C 1.235× [1.163, 1.313] (≈ 1036's W/C 1.227); W_E/W 1.026× [0.942, 1.117]; E/W 1.007× [0.948,
1.070]. Solves E 90.1%, W_E 90.2% (F 90.8%, W 88.9%, C 87.1%). E costs 0.39 worker-s more per search
than W_E. Pre-solve collection 5 058 worker-s (sunk; about a tenth of the 48 039 exact corpus),
extraction 8.6 worker-s.

Descriptive: no pre-solve library contains `gt`; every exact library carries `input first gt`.
Shared half is reducer/add syntax; E-only windows are reducer→`if_gt` (`input first if_gt`,
`input reduce_max if_gt` in 16/16). E solvers carry more E-library windows than other arms' solvers
(occurrence, not ancestry) but exact-library `gt` joins no more often than W_E/W/C solvers (64% vs
62–65%; F solvers 78%). Training-perfect inexact individuals: E 5.25 M, F 5.41 M, C 6.96 M vs W_E
1.82 M, W 2.84 M (library insertion steers into near-alias regions; F pays it and still wins).

Rule 3 fired (`no_worthwhile_increment_ends_source`): upper bound 1.057 < 1.10, also under every
sensitivity. Steward's guess (E/W_E 1.0–1.10, E/F 0.85–0.95) right on routing, slightly high on
both points. Interpretation limits: bounds this source + extractor at this scope, not pre-solve
learning in general (other checkpoints, performance-aware selection, other extractors untested);
not a harm finding (interval includes 1); E/W_E ≈ 1 with E/F < 1 is consistent with "gate joins
carry F's increment" and against "shared reducer/add syntax carries it", but E differs from F in
source, content and length law together, so no mechanism is identified.

Decision: close 33 and return to strategy (`next: strategy`), because the pre-registered rule 3
fired with margin under every sensitivity, ending this source/extractor at this scope; its one slot
and root 10's 25 slots are used; every rule was pre-set to return to strategy.
([decision](../../../runs/2026-10-09-1350/decision.md))
