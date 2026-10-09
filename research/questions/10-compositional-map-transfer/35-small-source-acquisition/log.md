# Log — 35 small-source acquisition

## 2026-10-09: opened (strategy 1743, slot 27 of root 10)

Steward probe, read-only, research/main build: first four 1246 collection attempts per corpus ×
cell; full C reproduced bit-exactly from all 48 (16/16 hashes), so the fitter is wired as in 1246.
150 solvers, empty cells BE2/BE7/BE8/PA6 (G4 expected-transition fallback). F4 sizes 4 (BE2) to 28.
64 searches per arm, 16 corpora × 4 then-addition cells, new seeds: C4 51/64, geo 112k, 7.9 worker-s;
C4+F4 61/64, geo 42k, 3.8 worker-s. Observation only. Proposal: [1743](../../../runs/2026-10-09-1743/proposal.md).

## 2026-10-09: run 2026-10-09-1743, four-attempt C4+F4 / C4+W4 against the full pipeline — ran

Slot 27 of root 10 (strategy 1743 raised the budget 26 → 27). Commit `652fde5`,
[analysis](../../../runs/2026-10-09-1743/analysis.md), [execution](../../../runs/2026-10-09-1743/execution.md).
Each 1246 corpus got four disjoint acquisitions (block b = attempts 4b+1…4b+4 of each training
cell, failures kept): 1 024 of 3 072 attempts, 615 solvers, 14 empty source cells (G4 fallback;
51/64 acquisitions had none), libraries 4–32 fragments, no empty library. C4+F4 and C4+W4 on 1036's
then-addition roster, 16 corpora × 16 cells × 16 seeds (block = seed ordinal mod 4), 8 192 searches,
104 min; paired with 1036's full F/W/C rows (same cases, different initial programs). All gates
passed: 16/16 full-C hashes, all-empty → G4, edit audits, 34 historical and 128 smoke replays
bit-exact; 16 seeds admitted on timing.

Primary ρ = cost(full F)/cost(C4+F4) **0.679 [0.614, 0.752]** (unsolved = 2 × cap, t on 15 df):
the four-attempt pipeline needs about 1.47× the search (1.33–1.63×). Upper bound below 0.833 under
1 × cap (0.771), BE (0.827), PA (0.773) and every block (0.81–0.91); both-solved 0.767 [0.707,
0.832]. 16/16 corpus means < 1. Solves C4+F4 85.9%, C4+W4 86.3%, full F 90.8%, W 88.9%, C 87.1%.
Secondary (cost ratios, > 1 = numerator costlier): C4+W4/C4+F4 1.119 [1.030, 1.216] (F4 beats W4,
unresolved against 1.10); full C/C4+F4 0.996 [0.919, 1.080] (not resolved from full C alone);
full C/C4+W4 0.890 [0.837, 0.947]; C4+W4/full W 1.378 [1.298, 1.463]; C4+F4 geometric cost 0.26×
G4's (unpaired). Economics A + N·S in evaluations: acquisition 4.97 M vs 61.3 M (8.1%), per capped
search 148.9 k vs 112.0 k; C4+F4 is the cheaper deployment up to N ≈ 1 530 [1 247, 2 016] fresh
searches (≈ 780 in qualified worker-s), repays against G4 after ≈ 31 [27, 38].
Post hoc, 64 acquisitions: ρ 0.21–1.34 (14 ≥ 1); Spearman with library size 0.36, empty source
cells −0.35, solver count 0.19, `gt` fragments 0.25 (steward recomputation; confounded with size).
Acquisitions with any empty cell average 0.52, none 0.735; full 32-fragment libraries still 0.77.

Against expectation: proposal expected ρ ≈ 0.95 [0.85, 1.06]; observed is the named surprise
direction (ρ < 0.7 at the point estimate). The 64-search probe (unpaired, block 0) misled:
C4+F4 42k vs F 46k there, 67.5k vs 45.9k paired here.

Decision: close 35 and return to strategy (`next: strategy`), because rule 2 (tight loss) fired
with margin under every sensitivity, block and family, so the four-attempt policy fails the
pre-set 20% retention target; the plan routes every outcome to strategy, root 10's 27 slots are
used, and whether an intermediate source budget is worth pricing is an allocation question, not a
continuation of this one. ([decision](../../../runs/2026-10-09-1743/decision.md))
