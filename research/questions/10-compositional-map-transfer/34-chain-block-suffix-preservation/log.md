# Log: 34 chain-block suffix preservation

## 2026-10-09: steward probe (run 2026-10-09-1606), read-only

[Script](../../../runs/2026-10-09-1606/steward_probe/suffix_probe.py), < 1 s. 16 1246 C tables,
1036 length laws, uniform starts, C-chain block tokens; 2 000 random-allele tapes and 2 000
re-encoded 1036 W then-addition solver tapes per corpus. Without boundary repair the boundary
token changes in 64.8% (solvers) / 66.8% (random) of edits; suffix tokens changed per edit 1.95 /
2.22 (3.0 / 3.3 given any); blocks ending at the tape end 3.4%, no-op blocks 0.4%. Observation only.

## 2026-10-09: run 2026-10-09-1606 (34), C-chain blocks with (W) versus without (R) suffix preservation on then-addition — ran

Slot 26 (strategy 1606 raised root 10's budget 25 → 26). Commit `af8a7e5`,
[analysis](../../../runs/2026-10-09-1606/analysis.md), code review pass. R: same operator stream,
block draws and block encoding as W; at the boundary it redraws the allele uniformly within the
interval of the token that the *unchanged* allele decodes to under the new final block token, so
its decode equals the unrepaired decode; no later allele is written. W and C are 1036's rows, all
15 360 re-matched and 32 replayed bit-exactly, so the paired main path ran (no fallback).
then-addition-v1 (development bank), 16 corpora × 16 cells × 16 seeds = 4 096 R searches, plus
1 024 descriptive holdout searches (8 comparison-gate holdouts × 8 seeds). 10 000-edit forced audit
passed, including tape-end, no-op and unchanged-final-token cases. Scoring 47 min.

Primary W/R **0.954× [0.903, 1.007]** (W/R > 1 would favour the repair; 5/16 corpora > 1; 1 × cap
0.961 [0.916, 1.008]; both-solved 0.984 [0.940, 1.031], 3 320 pairs; BE 0.981 [0.907, 1.061], PA
0.927 [0.846, 1.016]). Half-width ×1.056, tighter than the projected ×1.07 (corpus SD 0.103).
R/C **1.286× [1.208, 1.370]**, 16/16 corpora, 11/16 cells resolved; W/C in the same pairs 1.227×
[1.148, 1.311]. Solves R 3 685, W 3 643, C 3 566 of 4 096; most of the W/R gap is censoring (R-only
solves 365, W-only 323). Holdouts (descriptive): W/R 0.963 [0.850, 1.092], R/C 1.434 [1.250, 1.645].
Realized ripple in scored R: 63.8% of block edits change the decoded suffix, 1.82 suffix tokens per
edit (2.86 given any), so 4.71 tokens changed per edit against W's 2.89; near-geometric tail to 29.
This confirms the steward probe and corrects 32's "re-decodes the whole suffix".

Rule 3 fired (`not_needed_at_this_resolution`): upper bound 1.007 < 1.10, and R/C's lower bound
1.208 > 1, so chain proposals help without containment. Rule 1 (ripple helps, upper < 1) missed by
0.7%. Steward's guess (W/R 1.03–1.10) was on the wrong side of 1; neither surprise threshold fired
(0.954 vs < 0.95). Interpretation limits: not equality (W at most 0.7% better, at most 9.7% worse);
not that ripple helps; not that chain proposals are W's sole cause (length law and token supply
untested); one externally fitted previous-token decoder, ripple confined to ~3 tokens; ordinary
mutation and crossover unchanged in both arms; development bank, nothing acquired.

Decision: close 34 and return to strategy (`next: strategy`), because the pre-registered rule 3
fired with a clear margin under every sensitivity and family split (upper bounds 1.008–1.061, all
below 1.10): suffix preservation is not needed in later acquisition baselines at this resolution,
so the next acquired-decoder test may use either policy; the one slot and root 10's 26 slots are
used, and every rule was pre-set to return to strategy.
([decision](../../../runs/2026-10-09-1606/decision.md))

## 2026-10-09: corrections from critique 1743 (digest check, notes 7–9)

- "Same bound under 1 × cap, both-solved, BE and PA" overstated: the 0.7% repair-gain bound is the
  pooled primary's only (upper 1.007); the sensitivities' upper bounds are 1.008, 1.031, 1.061 and
  1.016, so what holds under each is that the worthwhile 1.10× repair gain is excluded.
- "Later acquisition baselines need not keep the repair" widened scope: run 1606 tested full C and
  its block law only. Dropping repair is a supported implementation choice under the tested full-C
  setup; its effect under changed decoders remains unmeasured (1743 kept the repair).
- "Corrects 32's 're-decodes the whole suffix'" conflated re-decoding with token change. Run 1606
  measured changed suffix tokens after block edits: under these edits downstream changes are
  typically local despite suffix re-decoding. Ordinary point-mutation ripple was not measured.
Corrected in [question.md](question.md), the root log and the digest.
