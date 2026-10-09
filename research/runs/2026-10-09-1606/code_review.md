---
verdict: pass
---

# Code review: 2026-10-09-1606 chain-block suffix preservation (W vs R)

Reviewed `git diff a3a254d..af8a7e5` in the task worktree (7 files, +647/−5),
`proposal.md`, `critique.md`, `plan.md`, `queue.yaml`, and the researcher's smoke
outputs under `smoke/final-verification-prepare/`. Ran
`tests/test_suffix_preservation.py` (9 passed) and `scripts/run_queue.py --validate`
on the task queue (OK, 2 entries, 1800 + 6600 s = 140 min ≤ `max_queue_hours` 8).

## Blocking issues

None.

## What was checked

**Arm wiring (fragment_operator.py).** R shares every draw with W up to the
boundary: same `[search_seed, 4]` operator stream, same fragment-length draw, same
start draw, same C-chain token proposals, same conditional-uniform re-encoding of
the block positions. The only divergence is at `j == lengths` where R replaces the
target token with `decoder.lookup[new_final_token, original_boundary_allele]` and
draws uniformly inside that interval, so the decoded output equals the unrepaired
decode. Positions beyond the boundary are never written. `Decoder.lookup` is
`searchsorted(..., side='right')`, so the interval `[lower, table[prev, token])`
used by the operator is exactly the decoder's preimage. R's diagnostics re-decode
the actual child and split Hamming changes into inside/suffix masks, which answers
critique note 2 (the old `desired`-based counter would have under-counted). W's
code path is unchanged; `minlength=len(self.stats[key])` equals the old constant 7
for W/F/B, so historical W stats are reproduced, which the 32/32 replay confirms.

**Forced-edit audit (suffix_preservation_audit.py).** 10,000 edits over 16 C
tables, with constructed no-op blocks (every 5th row) and unchanged-final-token
controls (every 5th+1 row), plus the operator's own `boundary=True` tape-start and
tape-end forcing. It asserts: W/R identical in prefix and block (alleles and
tokens), R decode == unrepaired decode, boundary allele in its preimage, alleles
beyond the boundary untouched, W suffix unchanged, and that the R stats equal the
independently measured inside/suffix counts. Passed in the final smoke
(coverage: 2,670 tape-start, 2,652 tape-end, 2,064 no-op, 4,525 unchanged-final).

**Pairing with 1036 (suffix_preservation_run.py).** Historical files are
SHA-pinned (1036's output dir via the 1350 provenance fixture plus three added
hashes). At init the full 1036 roster (15,360 rows) is checked for duplicates,
schedule equality, table hash, training-index draw, shared initial tokens with the
C mate, cap, pop size and evaluation accounting. The paired roster is 1036's C
rows re-labelled `R`, so corpus/cell/seed are bit-identical; `score()` additionally
checks each R row's `initial_tokens_hash`, `training_indices`, `table_hash`, cap
and pop size against the historical W mate. Smoke and fallback seeds are checked
for non-overlap with both 1036 and the G4 source seeds. Replay compares
`REPLAY_FIELDS + ('solver', 'operator')`; 32/32 matched.

**Metric and rules (suffix_preservation_report.py).** `comparison(rows, 'W', 'R')`
yields `log cost_R − log cost_W` per pair, equal-weight corpus means, 95% t
interval on 15 df, unsolved = 2 × cap (`solver_corpus_report.cost`). Direction
matches the proposal (W/R > 1 favors repair). `route()` applies the four rules in
the proposal's order; the parametrized test includes the critique's worked
example 1.05 [0.981, 1.124] → unresolved. `chain_proposals_help_without_containment`
is gated on rule 3 and R/C lower > 1, as written. `resolution_cost` keys the report
needs are present in 1036's `preparation.json` (verified), so the post-scoring
report will not crash on a missing key; the end-to-end report test covers both
paired and fallback modes.

**Gates and stop rules.**
- Replay failure selects the approved fresh-W/R fallback (8,192 searches, no
  holdouts, no paired C); it does not stop the run. The 1350 cycle and this cycle's
  smoke both replayed cleanly at the same decoder code, so a spurious fallback is
  unlikely.
- Admission projects 73.6 min (with 15% margin, handoff replay and 180 s report
  reserve) against a 108 min job deadline; the adverse 80%-solve scenario is 88.5 min.
  The projection is conservative in two ways that make a false "infeasible" stop
  unlikely: measured concurrency (6.54 of 10) comes from a 32-job smoke dominated by
  its tail, and holdouts are costed at the primary mean rather than 1036's 3.37 s.
  A wrong stop would need the queue machine to be roughly 45% slower than during
  the smoke. No outcome-dependent resizing exists; the roster is fixed.
- `score()` refuses on any freeze/schedule/hash mismatch and on an incomplete
  roster, so a partial run cannot yield an efficacy table.

**Queue.** `${RUN_DIR%/*}/…-prepare/preparation.json` works because
`run_queue.py` fixes `date_dir` once per invocation (same precedent as 1350).
Both entries use `.venv/bin/python` in the worktree, which imports `_folding_rust`.
`expect_outputs` match what `prepare()`/`score()` actually write in both modes
(holdout plots are only written in paired mode and are not listed).

**Critique.** Notes 1–5 are addressed in `plan.md` and the code (solve scenarios
and admission at 10 workers; edge-case audit and actual-suffix diagnostics; the
resolution statement and retain-incumbent-on-unresolved; one-run exit; revised
prior-work wording and Byrne et al. 2010). Notes 6–7 concern wording in files
outside the researcher's task folder; the plan explicitly leaves them for the
steward, which is the right call.

## Minor notes

1. The audit asserts equal W/R RNG *state* on identical input. NumPy's bounded
   integer sampler (Lemire) can in principle consume different randomness for
   different interval widths, so this is a stronger property than "same number of
   draws". It is deterministic under the fixed audit seed and passed, so there is
   no run risk; just read the proposal's "same number of RNG draws" as integer
   draws, not bit-identical consumption.
2. `smoke/final-verification-prepare/config.json` records `git_commit a3a254d`:
   the smoke ran on the uncommitted tree before `af8a7e5`. The queue's own prepare
   step re-runs every gate, so nothing depends on it; the analysis should confirm
   the queued `config.json` shows `af8a7e5`.
3. The audit's 30.4% suffix-ripple fraction includes the 40% constructed controls
   and must not be compared to the steward probe's 65–67%; the code's note says so.
   The analysis should use the scored R diagnostics for the natural rate.
4. In paired mode, W and C `seconds` come from 1036 hardware while R is timed now;
   the report marks worker-seconds descriptive, which is sufficient.
5. `admit()`'s `cap_scenario_seconds` fallback (slowest s/eval × cap when no capped
   smoke row exists) is descriptive only; in the actual smoke 4/32 were capped so
   the measured value was used.
