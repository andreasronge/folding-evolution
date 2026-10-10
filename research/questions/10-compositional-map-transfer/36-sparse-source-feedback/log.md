# Log — 36 sparse-source feedback

## 2026-10-09: opened (strategy 2033, slot 28 of root 10)

Steward probe, read-only, at 652fde5 in a temporary worktree. A stale Rust build in the main venv
gave 0/16 G4 solves; the probe was rerun after rebuilding. G4 sanity check: 11/16 training-cell
searches solved. Then 1743's frozen C4+F4 builds for blocks 0 and 2 (32 builds), one search per
training cell, new seeds: 117/128 solved, 4/6 in cells that were empty in the source. Mean ≈ 100k
evaluations and 4.5 worker-s per search (10 workers, 35–50 s wall per 64), against 310k
evaluations per first-batch G4 attempt, which solves 9.6 of 16. Observation only.
Proposal: [2033](../../../runs/2026-10-09-2033/proposal.md).

## 2026-10-09: run 2026-10-09-2033, one feedback batch under C4+F4 (A8) versus four more G4 attempts (S8) — ran

Commit `e12edbf`, [analysis](../../../runs/2026-10-09-2033/analysis.md), code review pass. Each of
1743's 64 builds (16 corpora × 4 source blocks) kept its first four G4 attempts per training cell
and added four more, either under its own frozen C4+F4 (A8, new seeds) or as G4 attempts later in
the 1246 schedule (S8); both pooled eight and refitted C and F with 35's code unchanged. Scoring on
1743's then-addition roster, 16 corpora × 16 cells × 16 seeds × 2 arms = 8 192 searches; 16-seed
roster admitted on timing only; all hash, replay and pairing gates passed; queue 94 min.

- Collection: A8 solved 947/1 024 (92.5%) at 96.6 k evaluations per attempt; S8's G4 batch 590/1 024
  (57.6%) at ~306 k. Solvers per build 24.4 vs 18.8 (A8 ≥ S8 in 64/64); empty cells 0 vs 1; both
  libraries at or near the 32-fragment cap. Second batch 0.30× S8's evaluations. The stage-0 probe
  (117/128) predicted this.
- Primary σ = cost(S8)/cost(A8) **1.126 [1.039, 1.220]**, 14/16 corpora > 1: resolved above 1,
  **unresolved against the 1.10 bar**. Same under 1 × cap (1.124 [1.042, 1.212]), both-solved
  (1.138 [1.057, 1.225]), BE (1.130 [1.058, 1.208]); PA 1.122 [0.944, 1.333]; blocks 1.075–1.186.
  Solves 90.0% vs 89.7%; the gain is a cost shift among solved searches. No lock-in.
- No rule: C4+F4/A8 1.52 [1.37, 1.68], C4+F4/S8 1.35 [1.23, 1.48] (16/16 each); full F/A8
  **1.031 [0.951, 1.117]** (A8 slower than full F by more than about 5% excluded; a gain not
  excluded either), full F/S8 0.915 [0.839, 0.998]. 1743's primary replicated exactly (0.679).
- Economics (evaluations, A + N·S): A8 6.51 M acquisition vs S8 10.20 M vs full F 61.3 M. A8 is
  cheaper than S8 at every horizon, interval excluding zero up to N = 1 024 (worker-s: up to 256).
  A8 repays its extra 1.54 M over the seed after ≈ 44 [35, 57] searches. A8 vs full F crossover in
  evaluations ≈ 42 k searches [6 k, 275 k], 35% of bootstraps never; in calibrated worker-seconds
  full F overtakes after ≈ 1 360 [1 020, 1 970] (16-row calibration; scoring ran 27% slower per
  search than the admission sample, so worker-s comparisons across runs are rough).
- Resolution price: at the observed point 1.126 and corpus SD 0.151, putting the lower bound above
  1.10 needs about 163 corpora, each with fresh G4 sources and a full-F reference.

Decision: close 36, answered at its scope, because the sparse first batch did not lock in: the
adaptive batch searched resolved faster than equal-attempt static collection (1.13× [1.04, 1.22])
and level with the 48-attempt pipeline within about 5%, at 0.30× the second batch's evaluations, so
on cost and speed together adaptive collection is the better of the two policies whether or not
σ clears 1.10; resolving that bar would take about ten times the corpora and would change no policy
choice. Root 10's 28 slots are used and the strategy routed every outcome back to review, so the
next step is `next: strategy`. ([decision](../../../runs/2026-10-09-2033/decision.md))

2026-10-10 (steward, run 2303 decide; wording correction from [critique 2303](../../../runs/2026-10-09-2303/critique.md) notes 7–9, no new data): the decision above says A8 is "level with the 48-attempt pipeline within about 5%". The interval cost(full F)/cost(A8) 1.031× [0.951, 1.117] is one-sided evidence: A8 is not resolved from full F, an A8 slowdown above about 5% is excluded, and an A8 gain of about 10% remains possible. "Every horizon" means lower estimated total evaluation cost at every reported horizon, resolved through 1 024 searches (worker-seconds through 256). "No lock-in" means none observed on this one update and development roster. The summary in question.md now uses these readings. Fresh-bank follow-up: [37](../37-cheap-bias-fresh-transfer/log.md).
Decision: keep 36 closed because the correction narrows wording only and changes no decision.
