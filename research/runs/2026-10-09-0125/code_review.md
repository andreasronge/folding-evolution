---
verdict: pass
---

# Code review: frozen frequency-matched K on 1548 row F

Reviewed `git diff 516448f..8e62831` in the worktree (new runner, report
wrapper, tests, vendored 1548 row F data), plus proposal.md, critique.md,
plan.md and queue.yaml. Worktree HEAD is `8e62831`, status clean.

## Blocking issues

None.

## What was verified

1. **Arm wiring.** The K roster is the 1548 row F C roster with `arm='C'`
   replaced by `'K'`; the envelope selects `corpora[corpus]['tables']['K']`,
   the same table-by-arm path C and T used. `search()` uses the arm name only
   as a label. All 16 K tables are hash-checked against the 1246 freeze and
   the per-corpus fit record in `frozen_source`, and K's definition in
   `solver_corpus_fit.fit` is G4 reweighted by per-token multipliers, as the
   proposal states. Pooled marginal error recomputed at 2.897e-5 (< 0.001).
2. **Seeds and pairing.** Each K row shares its seed and 64-case draw with
   the saved C and T rows (`check_pairs` compares training indices against
   both); seeds are unique within K (test asserts 2048 distinct). No seed is
   reused across corpora or cells.
3. **Metric and direction.** `contrast('C','K')` computes
   log cost_K − log cost_C averaged over cells×seeds then over 16 corpora,
   t interval on 15 df; unsolved = 2×cap with 1×cap sensitivity. C/K > 1
   means K is slower, matching the proposal. Routing thresholds (LB ≥ 1.20
   insufficient, UB ≤ 1.20 adequate, else unresolved) match plan.md.
   Reproduction test recovers C 1771, T 1547, G4 162 solves from the
   vendored data.
4. **Admission hashes.** I recomputed `implementation_hashes()` with the
   worktree's `.venv` python (including the Rust binary) and it equals
   `preparation.json` exactly, so the full run's "implementation changed"
   check will not fire. `preparation.json` has `admitted: true`, replay
   32/32 bit-exact with zero errors, workers 10 (queue passes `--workers 10`).
5. **Runtime and deadline.** Queue timeout 9000 s, `--deadline-seconds 8880`,
   internal work deadline 8760 s. Sample projection 72 min; all-capped
   projection 110 min (127 min with 15 % margin); worst case per-search
   ~23 s × 2048 / 9.8 workers ≈ 80 min. 1548 ran at 10 workers on this
   12-core machine with ~9.8 effective. Comfortable margin. Timeout or error
   writes partial rows and an `incomplete` report and exits nonzero; no
   partial-roster efficacy decision is possible.
6. **Gates / stop rules.** The only pre-main gate (preparation admission) has
   already passed on this exact build. Remaining in-run stops are the
   deadline, hash identity, pairing checks and deterministic re-check of the
   16 timed K rows; C/T replay was bit-exact across builds, so same-build K
   determinism is not at risk. No gate can stop the main stage for a
   statistical reason.
7. **Queue.** `run_queue.py --validate` accepts the one-entry queue; 2.5 h
   is within `max_queue_hours = 8`. All `expect_outputs` are written by the
   runner (`timing.json` by `jobs`, `progress.json` per corpus pair,
   `result.json`/`report.md`/`diagnostics.png` by `save_report` even on error).
8. **Tests.** `tests/test_frequency_matched.py`: 6 passed (29.8 s).
9. **Critique.** Notes 1–4 are incorporated in plan.md (solve counts stated,
   replay on the actual build, decision wording restricted to "this G4-based
   frequency map", C/T reported beside C/K, SD labelled a planning
   assumption). Notes 5–8 concern wording in questions/ and the digest; the
   researcher cannot edit those and plan.md defers them to the steward with
   the suggested wording. That is an adequate "why not"; the steward should
   action them at `decide`.

## Minor notes (non-blocking)

- The 16 timing searches were all on the first selected cell
  (`TA:F>m?F+M:S`) and solved 9/16; plan.md correctly says this is not a
  bank-wide solve-rate estimate. Analysis should not quote it as one.
- K/G4 is computed against the unpaired 16-seed G4 rows per cell and the
  corpus interval ignores G4 sampling uncertainty; the report labels this.
  Keep it descriptive in the analysis.
- The row-F envelope passes `save_solver=False`, so K gets the same in-search
  exact-D1331 criterion as C/T in 1548, not an additional independent solver
  replay. Consistent with the reused rows; just noting that "exact D1331
  verification" means the search-internal check here.
- `envelope` does `row not in self.schedule` (linear scan over 2048 dicts per
  job); negligible cost at this size.
- Both-solved contrasts drop corpora with no solved pairs, so their `n` can be
  below 16; occupancy is reported. Treat them as selection-conditioned only.
