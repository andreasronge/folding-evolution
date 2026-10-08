# Log: 24-comparison-gate-bank

- 2026-10-08 steward probe (run 1246, read-only, research/main a804f4f): roster 2x240 -> 162+162 non-constant gates -> 220 distinct behaviours (0 cross-family, 0 equal to the 1603 bank); exact <=9-token screen (104 s): BE 82 distinct, 45 near-alias, 0 exact, 37 retained; PA 138 distinct, 76 near, 6 exact, 56 retained; retained agreement 0.61-0.80. G4 on 6+6 sampled retained cells, 8 seeds each (12460000+), cap 524288: 57/96 solved, per-cell 2/8-7/8, medians 48k to above the cap, 141.6 s wall on 10 workers. Those 12 cells are development/training only. Files: runs/2026-10-08-1246/steward_probe/.

## 2026-10-08 — run 2026-10-08-1246 (slot 16 of 16 in root 10): bank frozen, C/T on training cells — recommend stage 2

Experiment: built the comparison-gate bank in-repo (commit `5dd86bd`, bank SHA-256 `df3476d0…`,
split hash `b0cc4ae0…`; 37 BE / 56 PA behaviours retained by the exact ≤ 9-token screen, which
does not certify 13-token minimality). Froze 4 training + 4 untouched holdouts per family
(holdouts chosen performance-blind by lowest sha256(id+"1246"), one per repeated reducer).
16 independent G4 solver corpora (8 per family, 48 collection searches per own training cell),
frozen 1707 fitting rule (C: previous-token table, α 50; T: 24 token multipliers on G4; K fitted,
not scored), then C and T on 16 paired fresh seeds per own training cell, plus 32 G4 seeds per
training cell. 5 376 searches, 119 min, complete, all validation passed, 0 holdout searches;
stage-2 roster frozen in `freeze.json` ([analysis](../../../runs/2026-10-08-1246/analysis.md)).

Result: C/T (speed, unsolved = 2 × cap) **3.11× [2.78, 3.48]** over 16 corpora (BE 2.86×
[2.56, 3.20], PA 3.37× [2.74, 4.16]); 1 × cap 2.82× [2.52, 3.14]. C beat T in 16/16 corpora and
64/64 corpus × cells; solve rates C 91.4%, T 77.2%, G4 68.0% (G4 unpaired); among the 731 pairs
both solved, median T/C evaluations 2.21×. Descriptive: C/G4 5.8×, T/G4 1.9×, so T is not a
damaged control. Collection yield 58.9% pooled (BE 56.0%, PA 61.7%; weakest corpus-cell 14/48;
no empty cell). Per-corpus sd 0.21 log. Fitted C tables are diffuse (row entropy 3.80 bits vs
3.82 for T), not copies of tapes. Expected 1.2–1.4×; the observed effect is over twice that.
Explanation B (old-bank gain tied to its short shapes) is ruled out on these training cells;
A consistent; E not supported at this cap. Why the effect is larger than on the old bank (longer
programs, harder base task, weaker T) is not identified. Training-cell result only: every cell
was both source and test of its fit; no transfer is shown. C/T compares fitting procedures;
token order is not isolated (K unscored).

Decision: close 24 and open [25-comparison-gate-transfer](../25-comparison-gate-transfer/question.md)
for the frozen stage 2, because both parts of this question are answered (the bank gives a
role-covered 4 + 4 protected split with tractable G4 search, and C/T resolves far above 1 with
yield above the 40% floor, so the pre-stated rule routes to stage 2), and the holdout
comparison is a separate question that needs its own allocation (root 10 has 16 of 16 used).
