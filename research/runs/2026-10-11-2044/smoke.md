# Implementation and smoke verification

The approved design is runnable. No engine, extractor or Rust code changed,
and no new acquisitions or protected searches ran. The bank, method and seed
freeze precede all new development search. `plan.md` was written before the
screen/execution checks; it addresses critique notes 1–4 and defers notes 5–8
outside this role's write scope.

Bank admission: all 24 destinations survive. Six development cells comprise
all four stage-0 cells plus `C:p20+n03+p31` and `C:p23+n30+p01`; the eighteen
others remain protected. Independent labels, recursive interpreter, Python
stack interpreter and production worktree VM agree on D625, including zero
conditions. Existing helper/random-tree executor checks pass. Exhaustive
through-nine-token screening visits 17,807 distinct outputs: maximum short
agreement 335/625, old-bank agreement 305/625, pairwise agreement 335/625.
No exclusions/replacements or exact short aliases. Longer aliases are not
ruled out. Bank digest:
`e3873e170b71ffcb69bea99b0d2cf4afd7062a5b6ab28ef2a9e59608f6c6d175`.

The saved 1938 archive contains all 24 actual experimental libraries and
2,304 acquisition rows, with original bank, schedules, methods and preparation
hashes. Archive SHA-256:
`2e6b84e2b1c74a39005eb17fa7b273bc2249bbbdec80ce62224d88b8059b81ca`.
Acquisition replay and source-only reconstruction match exactly. R-all donors
are the saved semantic entries unchanged; source rows are replayed for
verification, never searched again. All original method hashes match this
worktree, including its Rust extension. The two stage-0 libraries are unused.

The first smoke attempt (`smoke-development/`) failed closed before any
search because of tuple/list equality across JSON serialization of the
frozen grammar. Canonical hash comparison fixes that implementation error;
a new regression verifies a valid preparation round-trip and rejects library
tampering. Successful fresh preparation is in `smoke-prepare-v2/` (111.406 s;
104.472 s exhaustive screen), and its method/schedule/seed envelope was copied
to `experiments/chem_tape/data/signed_chain_2044/presearch.json.gz` before search.
Its preparation hash is
`f41970d44a5bee793a4d69ac61d73a3ad1cf2457a9c871041a1f96ee77121d0e`.
Earlier failed and successful preparation artifacts remain for traceability.

Successful search smoke is `smoke-development-v2/`: two seen development
cells x two saved builds x one repeat x three arms = 12 jobs, full population
and restart limits, separate fixed seeds beginning 20460000. Raw attempts,
curves, costs and rejection counters are in `score.jsonl`; descriptive
summaries in `report.json`; the rendered `dynamics.png` was inspected.

| Arm | Solves / jobs | First attempt | Mean evaluations | Mean worker s | Max attempts |
|---|---:|---:|---:|---:|---:|
| R-tree | 4 / 4 | 1 / 4 | 101,184 | 5.059 | 4 |
| R-all | 4 / 4 | 1 / 4 | 70,080 | 3.543 | 2 |
| R-gate | 4 / 4 | 4 / 4 | 5,888 | 0.291 | 1 |

These are feasibility observations on a tiny fixed fixture, not an efficacy
verdict or an early look at the full probe. The smoke did not generate a
confirmation forecast or strategy recommendation. There is no evidence of
an unreachable target or unexpected cap ceiling in this fixture.

Batch scoring wall time was 10.559 s, worker time 35.574 s, max worker time
10.005 s, and effective concurrency 3.369 with eight workers. Small-batch
startup/straggler effects make that concurrency a poor sustained estimate;
full-run forecasts will use the complete probe's measured throughput.
Naive 864-job scaling gives 760.3 s (12.7 min); adding preparation/replay/report
overhead gives about 15 min expected queue wall time. Replacing 10% of jobs
at the smoke mean cost (2.965 worker-s) with estimated 30-worker-s caps adds
693.3 s (11.6 min) at this small-batch concurrency: about 24.2 min scoring,
within the 40-minute reserve. Extrapolating individual smoke worker/evaluation
rates to 524,288 evaluations gives roughly 19.5–28.6 worker-s per cap, consistent
with the proposal's 30-s estimate; this is not a measured cap or an upper bound.
The proposal's stage-0 estimate (7.6 effective workers) remains a separate
scenario, where 10% cap replacement adds 4.6 min. Unexpected widespread caps
or much slower throughput are not covered by these expectations.

Verification: the original four probe tests plus existing tree-GP/library
checks passed (20 tests); after the serialization fix, all five probe tests
passed, including the new round-trip/tampering regression. Ruff passes for
all new Python files; no existing engine files changed. Tests check complete
paired grids, protected isolation, exact solvers/cap accounting, helper-only
metadata isolation, saved acquisition identities, crossed variance components,
actual protected roster size, conservative variance sensitivity and unresolved
hypothetical effects at 0.80. No broad efficacy inference is made from these
fixtures.

The full queue is exactly the approved probe: 900-s prepare plus 2,400-s
score/report reservations, sum 3,300 s = 55 minutes. Commands use this
worktree's interpreter/cwd and write under RUN_DIR. No protected scoring or
confirmation entry is present. The report's confirmation forecast is a
conditional planning approximation with normal delta-method sampling errors
and a doubled-variance sensitivity, using only six development cells/two
repeats; it cannot establish actual protected precision, decisiveness or
permission to confirm. Return the complete probe to strategy after execution.

Final validation on the completed implementation: all 21 targeted tests passed
in 31.93 s (`test_signed_chain.py`, `test_tree_gp.py`, `test_tree_library.py`).
The queue parsed through `scripts/queue_lib.py`, both command strings passed
`bash -n`, ids match the required task prefix, and summed timeouts are 3,300 s.
No code_review.md or driver_feedback.md was present on the final recheck.

Implementation committed on `research/2026-10-11-2044` as `8a621df`.
The task worktree is clean; no research/ files are included in the commit.
The pre-commit smoke preparation records the parent HEAD while its exact
method/source hashes identify the committed implementation. The full queue
will record the implementation commit in its preparation and runner metadata.
