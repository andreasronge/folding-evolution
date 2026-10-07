---
estimated_minutes: 35
---

Implement the approved saved-map four-arm comparison by importing only the
context-increment harness, tests and pinned inputs from ec742da. Keep the
search/fitting engine at 5565d54 unchanged. This extends the inspected 1924
comparison; it is not independent confirmation. No collection, refitting,
lineage selection, bank changes or C3 are authorized.

Conditions and seeds: T1 is 1707 tables.T, T2 is 1924 C2.tables.T; reuse
1924's saved C1/C2 rows. Training retains all 16 BE lineages × four cells and
16 PA × six cells, each with 32 seeds (5,120 searches per new arm).
Holdout retains all 32 lineages × three withheld cells × 32 seeds (3,072
per new arm), as a whole stage or none. Seeds are precisely phase 11/12
seed_for(BASE, family, lineage index, cell index, seed index) from 1924;
all four arms share training indices. Ten spawned workers, Rayon one thread
each, cap 524,288, population 256, length 32, 64 cases and exact D1331
verification remain fixed. Unsolved searches cost 2×cap.

Before counting T rows, validate all 128 table hashes, provenance/artifact
hashes, all 16,384 saved C rows, their complete key/seed/index rosters and
budgets. Replay C1/C2 on every lineage's first training cell at seed index
zero (64 rows), requiring exact scientific-field matches. Replay timings
and administrative aliases are excluded. Retain the fixed T2 seed-zero
timing block across every own-training cell (160 rows) exactly once in the
primary roster. Stage 1 runs unconditionally after validation/replay; the
small-block throughput must not gate its admission.

Replace BOTH the old absolute cutoff and the old relative work limit.
Queue timeout is 4,500 seconds (75 minutes), with a 300-second reporting
reserve. Count elapsed time from the beginning of the queued process,
including imports, validation, replay, timing block and primary work. No
calendar deadline remains in this harness. Before considering holdout,
write a complete primary report (JSON, Markdown and plots) and checkpoint
its validation/stages/timing. That saved report must survive a holdout
overrun or interrupted process.

Holdout timing gate: combine the timing block and remaining primary
execution to measure full-roster worker seconds and full-roster wall time.
Effective workers = min(10, full primary worker seconds / full primary
wall seconds). Measure T1 and family-specific T2 mean worker cost from all
primary rows; do not use the 160-row block as the throughput estimate.
Project each holdout arm's worker cost using these means and the explicitly
assumed historical holdout/training inflation max(1, 0.946/1.042) = 1.
For T1, use its observed primary mean; for T2, use the appropriate family's
observed primary mean. This assumption does not measure T2 holdout difficulty.
Projected holdout wall time is projected worker cost / effective workers.
Admit the complete holdout iff 1.25×projected wall time is strictly less
than 4,500 − elapsed since queue start − 300 seconds. The gate uses time
only, never solve rates or effects. Save inputs, inflation, projection,
elapsed and remaining time in admission.json. A skipped holdout leaves
transfer unresolved.

Implementation QA: run targeted harness and reused engine invariant tests,
then smoke the first BE/PA lineage with two seeds per cell at the full cap.
Smoke covers replay, both stages, reporting and preserves row 0 (no claims).
Run the fixed full 64-row replay/160-row timing preflight as feasibility QA;
these deterministic rows are recomputed once in the full queue, not appended
from smoke. Record wall/worker costs and solves as feasibility observations.
If measured rates/runtime or validation show this approved design cannot
work, stop, write infeasible.md with numbers and an alternative, commit and
leave replanning to the steward. Do not shrink the scientific roster.

Measurements and estimator: record fixed seeds/indices, source/table hashes,
evaluations, solved flags, wall and worker seconds, complete-stage checks,
pairing checks and timing admission. Average log2 costs over seeds per cell,
then over each lineage's own cells. D=(C2−T2)−(C1−T1), I=2^(−D).
Training weights families equally: SE=0.5√(SE_BE²+SE_PA²), t with 15 df.
Holdout uses all 32 lineage Ds, t with 31 df. Report T2/T1, C2/T2, C1/T1,
C2/C1 and per-family I with 95% intervals; split paired within-cell seed
noise from between-lineage variation and report conditional sizing.
The previous ×/÷1.075/1.10 precision figures are heuristics; final intervals
come from observed lineage Ds, with every approved lineage retained.

Apply the ordered outcome rules separately to complete training (primary)
and complete holdout, using I's 95% lower and upper bounds:

0. Hash/roster/replay failure or incomplete primary: no comparison claim;
   report measured cost.
1. Lower >1: feedback increased the advantage of this additionally fitted
   context procedure over this restricted token procedure. If T2/T1 also
   has lower >1, both fits improved; otherwise token improvement remains
   unresolved. This establishes neither token-map impossibility nor a
   sharpening mechanism, and does not justify saying mostly contextual.
2. Upper <1: the token fit gained relatively more from feedback; C2/T2
   indicates whether additional fitted context still helps afterward.
3. 1/1.10 < lower ≤1≤ upper <1.10: this interaction is bounded within ±10%
   on this bank for these procedures. No equality/shared-mechanism claim;
   call either fit improved only if its own interval supports it.
4. Otherwise unresolved, including an interval spanning 1 and worthwhile
   I>1.10. Report lineage SDs, seed-versus-lineage variance and conditional
   sizing; more seeds alone need not settle it.

Training-only, skipped or unresolved holdout leaves transfer unresolved.
T fits global token multipliers over G4's fixed context; the contrast is
about additional fitted context. Yield, diversity, tape content and fitting
behavior remain bundled. Every outcome returns to strategy; none authorizes
C3. Row 1 can inform allocation to a later contextual-fit investigation;
rows 2/3 can inform corpus-yield/diversity or transfer-bank allocation without
claiming that the gain is mostly a better corpus. Row 4 informs a sized rerun
or parking with a concrete reopen condition.

Critique notes 1–4 are addressed above. Runtime projects to about 22–53
minutes under the stated assumptions, before allowance and overhead; it is
not a bound (note 5). Only the fixed 160-row T2 timing block was evaluated
in 2129; the remaining primary roster was not launched and no four-arm
interaction was computed (note 6). Digest/question corrections are outside
the researcher's permitted task-folder write scope and remain for the
steward. The likely sub-30-minute runtime is justified by the full matched
roster and whole-stage holdout; no extra unmatched seeds are added.

Implementation QA completed: 18 targeted tests and Ruff passed. Smoke
completed both stages in 34.82 seconds, with four exact replays and its
primary snapshot preserved; outcome remains row 0. Full preflight took
24.50 seconds: 128 tables and 16,384 saved rows validated, all 64 replays
matched exactly, and 160/160 T2 timing searches solved. BE/PA T2 costs were
0.6713/0.3436 worker-seconds/search; the timing block achieved 4.317 effective
workers. Historical T1 plus these measured T2 training costs project about
47.2 minutes for training plus holdout at this small-block throughput under
the stated holdout inflation assumption. This is a feasibility projection,
not a runtime bound or a primary gate. T2 holdout cost remains unmeasured;
the full queue measures primary throughput before admitting holdout.
See smoke_checks.json for the complete QA snapshots and ignored raw-output
paths. The validated queue has one 4,500-second entry, within the eight-hour
cap. The full scientific run has not been executed during implementation.
