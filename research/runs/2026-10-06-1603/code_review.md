---
verdict: pass
---
# Code review — 2026-10-06-1603 (four-reducer FIRST bank)

Reviewed `git diff e5b133d..92ba7c5` in the worktree, plus proposal.md, critique.md,
plan.md, queue.yaml and smoke.md with its JSON evidence. I re-ran
`tests/test_four_reducer.py` (9 passed), recomputed the G4 table from the proposal's
numbers, re-read the full D1331 screen result, and recomputed the stage-C cost
projection from the full-cap benchmark rows.

## Blocking issues

None.

## What was verified

- **FIRST semantics.** Rust `op_first` and Python `_op_first` both return the first
  element, 0 on empty or wrong-type input, through the same `safe_pop` path as the other
  reducers. `v2_rmin_first` is wired into dispatch, masks, `is_active`, `_token_max` and
  `parse_alphabet`; `v2_rmin` is unchanged (FIRST is NOP there, tested). The validation
  stage (depth-4 brute force vs. semantic machine, 100k random programs Python vs. Rust,
  all 36 canonicals per domain) runs before any screen and a failure routes to U.
- **Decoders.** `four_reducer_maps.tables()` reproduces the proposal's G4 exactly
  (independently rebuilt from the proposal text: start row INPUT 12 500, after-INPUT
  reducers 1 813/1 812/3 625×3, after-integer 3 500×4, floor 500, all rows sum to
  24 000). F4 adds FIRST = 3 to F. G4-BE / G4-PA replace the two rows the proposal
  specifies. Marginals are exact expected emitted-token frequencies over 32 positions
  including the start row (0001 used a Monte Carlo estimate of the same quantity; the
  plan documents the change and a test checks emitted frequencies within 0.002).
  `Decoder` handles the 25×24 table with start row index 24.
- **Roster, retention, split.** 12 BE + 24 PA cells, all 10-token canonicals, so the
  ≤ 9-token exact screen compares strictly shorter programs. Retention uses the unchanged
  `screen_domain` rule (≥ 80 % agreement or identical labels drops the cell). The split
  treats BE summands as one unordered role, requires every holdout (role, reducer) in
  training, no label sharing with holdouts, and takes the first lexicographic pair, per
  the proposal.
- **Arm wiring and pairing.** Stage B jobs iterate seeds × cells × arms with the same seed
  on every arm of a cell; `search()` derives every RNG from the seed only, so arms are
  paired. 13 cells × 8 arms × 10 seeds per block, 5 blocks → 5 200 runs. Calibration
  seeds 1603100–1603149; learner, selection and fresh-scoring seed namespaces are
  disjoint.
- **Metrics.** `contrast()` is the proposal's speed ratio: mean over seeds of
  log₂ min(T,cap) differences, geometric mean over fixed cells, bootstrap of seed
  indices within each cell carrying all arms. Table B uses G4-PA/G4-BE on BE cells and
  G4-BE/G4-PA on PA cells; the marginal pair and the directly paired ratio of ratios are
  computed. Readings follow W → C (> 25 % capped in either arm) → B (upper < 1.25) → X.
  KM medians return `None` when unobserved and are labelled `> cap`. Headroom counts an
  unobserved median as ≥ 4 096; tractability requires an observed median ≤ 65 536 and
  ≥ 35/50 solves.
- **Outcome routing.** Completeness requires exactly the 50 seed IDs per cell × arm and
  three complete screens; otherwise U. Order: U (incl. C started but unfinished) → 1 →
  2 → 3 → 4/5. Deadline interruptions keep completed rows via `search.jsonl` and route
  to U. Tests cover each route.
- **Critique disposition.** Notes 1–4 are implemented (full C cost including
  initialisation, selection and final scoring with a 2× candidate allowance; paired
  context-minus-marginal contrast; crossed-preference and "frozen 4 096 rule" wording in
  the report interpretation; within-generation Spearman of re-scored parents with a
  distinct-score rule). Notes 5–8 are digest wording the critic marked as not affecting
  the recommendation; plan.md says the researcher may not edit belief files and leaves
  them to the steward. Acceptable.

## Gate stability

- **Split gate (a)** is deterministic: exact typed-state enumeration. The smoke's full
  depth-9 D1331 screen (108 s, 5.07 GiB) gives 13 retained cells (BE 5, PA 8), BE has no
  role-covered pair, PA's first pair is `(F?S:M)+m`, `(S?M:m)+F`. The run will reproduce
  this, so Table A row 1 is the certain outcome barring a validation or screen failure.
  Stage B (the always-run calibration and Table B) is unaffected.
- **Headroom (b) and tractability (c)** are unreachable in this run. For the record, the
  2-seed benchmark shows G4 capping 1/2 on both benchmarked BE cells, so (c) would be in
  doubt on this bank; a future design should not assume G4 tractability on BE cells.
- **Cost gate (d)** is deterministic given the first-block timings, but see note 1.

## Notes (non-blocking)

1. **Stage C cannot fit this queue even if every gate passed.** Recomputing `projection()`
   on the benchmark's G4 rows gives inner ≈ 2.4 s per 65k-cap search on the worst BE cell
   and ≈ 12 s per full-cap search, so projected C ≈ 8.3–10.4 h against a 3.5 h deadline.
   Even an optimistic estimate (cyclic mean over training cells, no 2× allowance) is
   about 2.4 h, which still exceeds the ~2.3 h left after A + B. Inner searches on this
   bank cost 2–4× 0132's ~0.6 s, so the proposal's 10–20 min per trajectory does not
   carry over. Moot here because (a) fails deterministically, but the analysis should say
   that rows 4/5 were unreachable by construction, and any slot-7 proposal must size the
   learner from this run's measured per-search seconds, not from 0132.
2. The projection uses the worst training cell's mean inner time, while learner searches
   are spread cyclically over all training cells. Deliberately conservative; consistent
   with plan.md.
3. Generation 0 scores four identical copies of the start vector (96 searches where 24
   would do) per trajectory. Only matters if C runs.
4. `search()`'s shared `budgets` tuple gained 4 096. Additive: it only adds a
   `budget_seconds` key and does not change search behaviour. Older runs' rows lack the
   key, harmless for this run.
5. `gates.json` is written only when stage B completes, so a deadline interruption will
   fail `expect_outputs`; that is the U outcome anyway, and `interruption.json` records
   the cause.
6. Every `contrast()` call re-seeds its bootstrap RNG with 1603002, so all contrasts
   share the same resampling indices. Deterministic and fine; just not independent
   draws across contrasts.
7. Expected wall time: validation 4 s, three screens ≈ 6 min serial at ≤ 5.2 GiB each,
   stage B ≈ 57 min from the benchmark's 5.5 s mean per search on 10 workers, report
   seconds. Well inside the 12 600 s internal deadline and 14 400 s timeout; the queue sum
   is under `max_queue_hours`.
