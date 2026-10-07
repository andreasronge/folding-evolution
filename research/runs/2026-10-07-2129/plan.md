---
estimated_minutes: 30
---

Implement the approved saved-map four-arm crossing, adding only T1/T2 searches.
No collection, fitting, table selection, C3 or bank changes. This extends 1924;
it is not independent confirmation of its already-inspected C2/C1 contrast.
The engine and fitter from 5565d54 remain unchanged.

Training is 16 BE lineages × 4 cells × 32 seeds and 16 PA lineages × 6 cells
× 32 seeds: 5,120 searches per new arm. Holdout is all 32 lineages × all three
withheld cells × 32 seeds: 3,072 per new arm, admitted as a complete stage or
not at all. Ten spawned workers, RAYON_NUM_THREADS=1, cap 524,288, population
256, length 32, 64 training cases, exact D1331 verification stay fixed.
Seeds are exactly 1924 seed_for phases 11/12, BASE, lineage/cell/seed indices;
training_indices must match across all four arms. Smoke uses the first lineage
of each family, two seeds per cell at the full scientific cap and has no claims.

Before any T row counts: freeze and pin source config/corpora and C1/C2 search
rows, validate all four tables against stored hashes and validate the full
row-key, seed and training-index roster. Replay the first own-training cell,
seed zero, for C1 and C2 on every lineage (64 rows). Compare every scientific
field exactly, excluding wall/CPU timing and administrative arm aliases only.
The entire saved training and holdout rosters must correspond before scoring.

The fixed timing block is T2 seed index 0 on every own-training cell
of each of the 32 lineages (160 searches: 64 BE, 96 PA; all 16 lineages per
family, all cells). This covers unequal family cell rosters instead of timing
only one possibly unrepresentative cell. Retain these rows in
the fixed training roster. Gate solely on elapsed/worker time, never solve rate
or effect. Project remaining T2 cost by family, combine with historical T1
worker costs (1.042 training; 0.946 holdout), divide by observed effective
workers, and require remaining work time > 1.25 × projection. After training,
use observed T2 family training worker costs with a historical holdout/training
inflation of at least one and the same 1.25 allowance for whole-stage holdout
admission. Stage 1 may not shrink. An unaffordable primary is row 0.

Full queue timeout is 45 minutes; internal work budget is at most 40 minutes,
with 120 seconds for reporting. Absolute work cutoff is 22:20:38 Stockholm
(20:20:38 UTC) on 2026-10-07, reserving five minutes to the autonomous deadline
22:25:38 for reporting and downstream review/analysis. A launch after that
cutoff performs no searches. A timeout does not authorize extending the owner
deadline. Smoke may use a short relative deadline solely for implementation QA.
If smoke measurements show primary runtime cannot fit, write infeasible.md and
stop for the steward rather than silently changing sample size or cutoff.

Measurements: seeds, indices, table/source hashes, evaluations, solved flags,
wall/worker time, effective workers, complete-stage checks and timing admissions.
Unsolved cost is 2×cap. Per-cell mean log2 cost is averaged equally over own
training cells (or three holdouts), then lineage D=(C2−T2)−(C1−T1).
I=2^(−D). Training equally weights family means, SE=0.5√(SE_BE²+SE_PA²), t15;
holdout uses all 32 lineage Ds and t31. Report descriptive T2/T1, C2/T2,
C1/T1 and family I with intervals. The proposal's precision estimates are
provisional heuristics: they omit T2 and unknown covariance and are not
conservative bounds. Calculate final intervals directly from lineage Ds;
retain every approved lineage irrespective of precision.

Apply ordered rules separately to complete training and complete holdout:
0. Hash/validation/replay failure or incomplete primary: no comparison claim.
1. I lower >1: feedback increased the advantage of additionally fitted context.
   If token improvement's lower bound >1, both fits improved; otherwise report
   its interval and leave the token increment unresolved, without 'mostly contextual'.
2. I upper <1: token fitting gained relatively more; C2/T2 measures whether
   additionally fitted context still helps after feedback.
3. 1/1.10 < lower ≤1≤ upper <1.10: relative increment bounded within ±10%
   for these two procedures on this bank. No equality or shared-mechanism claim;
   call both fits improved only if their own intervals support improvement.
4. Otherwise unresolved, especially an interval spanning 1 and worthwhile
   I>1.10, or appreciable effects on both sides. Report observed lineage SDs,
   conditional sizing and paired within-cell seed noise versus between-lineage
   variation; observed variance alone cannot identify its mechanism.
Training-only, skipped holdout or unresolved holdout leaves transfer unresolved.
T fits global token multipliers over fixed G4 context; this comparison concerns
additional fitted context, not elimination of all decoder context. All outcomes
return to strategy and authorize no C3.

Critique notes 1–5 are implemented above. Notes 6–9 concern digest/question
wording outside the researcher's permitted write scope; defer those edits to
the steward. This run isolates the previously untested contextual increment.

Implementation QA also runs a preflight: all 64 replays then this 160-row
T2 block, without inference or primary-stage execution. Full queue repeats
these deterministic rows and retains them once within its primary roster.
