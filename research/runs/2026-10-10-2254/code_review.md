---
verdict: pass
---

# Code review: 2026-10-10-2254 (round 2, after repair)

Round 1 (commits `eedcdcf..3f60bd9`) failed on one blocking issue: scoring
stages could refuse an admitted preparation because `load_preparation`
re-read forced full-cap tail rows in completion order and fed them to
`project()`, whose `np.mean` is summation-order dependent, so the stored
projection would not reproduce and both `-dg` and `-ts` would stop with
"timing/solve gate changed" before any target search. Round 1's full text is
summarised under "Round 1 disposition"; its "checked and sound" list still
holds since the repair touched nothing else.

This round reviewed the repair commit `c32ff04` (`git diff 3f60bd9..c32ff04`,
`tree_gp_run.py` and `tests/test_tree_gp_report.py` only) against the full
range `eedcdcf..c32ff04`, plus plan.md, queue.yaml, implementation.md and
the committed smoke outputs. Worktree is clean at `c32ff04`.

## Blocking issues

None.

## Verification of the repair

- **Fix is correct and minimal.** `load_preparation` (`tree_gp_run.py:706`)
  now sorts the reloaded tails by `str(row_key(r))` once and uses that list
  for both the digest and `project()`. In `prepare`, tails are built as
  per-family `validate_rows` output (each sorted by the same key) concatenated
  DG then TS; because `row_key` puts `family` first and `"('DG'" < "('TS'"`,
  the combined sort equals that concatenation, so `tails_hash` and the
  per-family relative order given to `np.mean` are identical on both sides.
  Calibration rows and replay rows were already order-stable (both sides pass
  through `validate_rows`, and the replay list is hashed in write order).
- **Regression test exposes the bug and exercises the admitted path.**
  `test_admitted_tail_preparation_reaches_scoring[DG|TS]` builds a synthetic
  admitted preparation with ten unequal tail timings per family, searches for
  a permutation that actually changes `project()` output (asserts one is
  found), writes the tails in that completion order, and then drives
  `require_admission` → `load_preparation` → `score()` up to the point where
  target jobs would start, with the job runner replaced by a sentinel. It also
  checks that an altered tail timing is rejected. Running the same test against
  the pre-repair reload function fails both parametrisations with
  "timing/solve gate changed" ([regression-original-code.log](regression-original-code.log)).
- **Tests pass here.** `pytest tests/test_tree_gp.py tests/test_tree_gp_report.py`:
  13 passed on `c32ff04`.
- **Real-data round trip.** I reloaded the committed smoke preparations
  (`smoke-review-repair/`, `smoke-committed/`) through `validate_rows`,
  `choose_mix` and `digest`: calibration rows hash, chosen mix, replay hash,
  empty tails hash, preparation hash and method freeze all reproduce exactly
  from the JSON files. So real tree rows and native rows (not only the test's
  synthetic rows) survive the JSON round trip that the gates depend on.
- **TS dependency check is order-safe.** `report()` sorts rows by the same
  key as `row_key` before computing `search_rows_hash`; the TS stage validates
  the DG `search.jsonl` through `validate_rows` (same sort) before hashing, so
  the "DG result hash mismatch" gate reproduces. `preparation.json` written by
  the DG stage is the JSON-loaded `p`, so the TS equality check against the
  prepare folder holds.
- **No design change.** Seeds (calibration 22140000, scoring 22180000, smoke
  22160000, tails 22160200–209/22161200–209), arms, mix freeze, 80% timing
  admission, DG <25% stop, 1770 s preparation bound, bootstrap and decision
  classes are untouched. The `.get("DG", {})` change in `require_admission`
  only turns a `KeyError` into the intended `ValueError` for smoke
  preparations; a production projection always carries DG, and a missing DG
  still fails admission.
- **Queue unchanged.** Three sequential entries, timeouts 1800/7200/5400 s
  (sum 14 400 s, under the 8 h cap), `expect_outputs` match the runner's
  writes, deadlines equal the approved timeouts and the runner refuses larger
  ones. Seed audit replayed on the repair commit: zero overlaps, pairing
  intact ([audit-review-repair.log](audit-review-repair.log)).

## Critique disposition

Unchanged from round 1: all five substantive critique notes are implemented in
plan.md and code (gates and replays retained; old scoring base explicitly
replaced and its regression kept; both rosters with development-bank scope;
technique naming; resolution price, unbounded repayment and "within margin is
not equality" in the report). Note 6 needed no change. The repair plan and
repair verification sections appended to plan.md describe exactly what was
committed.

## Minor notes (not blocking, carried from round 1)

- **Preparation timeout margin is thin but pre-registered.** Worst case (all
  256 calibration searches cap) is about 1 391 s at the measured 9.2 effective
  workers plus about 30 s of replay and audits, against the 1 770 s internal
  deadline. A sustained throughput loss above roughly 20 percent would end the
  run with a `TimeoutError` before targets; such a failure says nothing about
  either method and the steward should treat it as a cost obstacle, not a
  result.
- **The DG <25% solve gate is a hard stop, not a reviewer clearance.** Plan
  retains it deliberately. If it fires, read the operator rejection,
  initialization and diversity diagnostics in `preparation.json`: rejection-
  heavy operators suggest a broken arm; otherwise a low solve rate is the
  proposal's own listed surprise (tree GP weaker than G4) and a legitimate
  observation.
- **Sibling-folder dependency assumes one `run_queue` invocation.** `-dg` and
  `-ts` reference `$RUN_DIR/../2026-10-10-2254-prepare`; a crash-resume on a
  later calendar day would not find it. Same pattern as earlier runs.
- `project()` for TS uses the historical A8 rate (3.6 s) because measured
  replays are faster; the `max()` is conservative as intended.

## Round 1 disposition

Round 1 blocking issue 1 (tail order dependence in `load_preparation`): fixed
in `c32ff04`, verified above. Round 1 "checked and sound" items (seed
schedules and pairing, arm wiring, tree search operators and interpreter
agreement, paired block bootstrap and decision classes, queue structure) were
re-read for this round and are unaffected by the repair.
