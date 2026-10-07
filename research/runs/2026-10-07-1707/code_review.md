---
verdict: pass
---

# Code review: 2026-10-07-1707 solver-corpus context fit

Reviewed `git diff a791565..627336d` in the experiment worktree, plus proposal.md, critique.md,
plan.md, queue.yaml and the smoke artifacts. Independent checks run by the reviewer:

- `tests/test_solver_corpus.py`: 7 passed in the worktree `.venv`.
- Vendored data hashes: `replay.json` and `provenance.json` SHA256 match the constants in
  `solver_corpus_run.py`. Replay rows are 40 GG rows at `table_hash` = `G4_HASH`, cap 524288,
  P 256, no re-encoding, so the replay exercises the unchanged search path.
- Re-ran `--smoke` from the committed code (RUN_DIR under /tmp): 480/480 search rows identical to
  `smoke-final/search.jsonl` on every field except timing, all 12 fitted-table hashes identical,
  identical pooled C/T and holdout C/T readouts, all 11 `expect_outputs` present. The researcher's
  smoke-final was produced from a dirty tree at `a791565`; the commit reproduces it bit for bit.
- Gate stability (resampled pilot): 200 bootstrap corpora per family drawn with replacement from
  the 48/cell probe's collection rows (`smoke-probe/search.jsonl`). T optimizer converged 200/200
  per family; K validated 200/200 per family, max K error 3.7e-5 against the 1e-3 tolerance;
  minimum resampled cell yield 32 (BE) and 40 (PA) against the 24/48 floor. Binomial P(yield < 24)
  at the lowest observed cell rate (42/48) is 4e-11. Row-0 gates are not near any boundary.
- Seeds: roster test confirms 7,680 / 17,920 / 9,600 searches with disjoint collection, training,
  holdout, reference and M blocks; T/C/K share seeds within corpus × cell; corpus stride 2,000 >
  6 cells × 200; cell stride 200 > 128 G4 holdout seeds; phase stride 1e6 > the largest
  within-phase offset (~1.3e5). Main base 2,026,100,717 is disjoint from the steward probe
  (17,07x,xxx / 17,17x,xxx) and from the smoke/probe bases (+1e8, +2e8).

## Blocking issues

None.

## Correctness checks that passed

1. **Search change is inert for RNG and existing fields.** `return_solver` only records
   `programs[i].tolist()` at the break and appends a `solver` key; no RNG stream is touched.
   The test compares all scientific fields between the two call forms, and the 40-row 0315
   replay passed in the probe. The tape saved is the decoded 32-token program, which is what
   `transition_counts` and the independent 1,331-input re-verification consume.
2. **Fits implement the frozen rule.** Transition counts use start row 24 and (previous → token)
   with per-cell rescaling to 1,600. T is a bounded (±ln 16) L-BFGS-B weighted likelihood with an
   analytically correct gradient; C is `(n + 50·g4)/(N + 50)`; K matches quantized C's exact
   32-position uniform-latent emitted marginal via 400 fixed-point steps of 0.7. All tables go
   through `normalize(…, R=24000)` and `validate_table` (shape 25×24, range 24,000, min 250).
   Nothing from the evaluation phases enters fitting.
3. **Arm wiring and leakage.** Evaluation jobs pass each corpus's own `tables[arm]`; the
   `save` callback verifies every returned row's `table_hash` against the roster, the case
   indices against the seed, and arm pairing of cases. `envelope` rejects holdout cells outside
   the holdout phase and payloads with anything but `{id, labels}`. No holdout is searched before
   stage 2.
4. **Stage-2 gate is a time gate only.** Admission = remaining work time > 1.5 × projection,
   projection from actual stage-1 per-arm seconds, measured effective workers, and a ≥ 1
   difficulty factor from the worst historical holdout/training G4 ratio. It never reads a
   result. Rough reviewer projection from probe costs (G4 2.1 s, T 0.3, C 0.3, K 1.2 s): ≈ 33 min
   collection + ≈ 27 min stage 1 + ≈ 16 min stage 2 on ~8 effective workers, inside the 7,800 s
   work window with margin for tails. A skip is recorded with the projection in `admission.json`.
5. **Estimator matches the proposal.** Per-corpus contrast = mean over cells of per-cell mean
   log2 cost (unsolved 2×cap; 1×cap sensitivity reported); family means weighted equally; pooled
   se = ½√(se_BE² + se_PA²), t on min family df (15); holdout contrast is one-sample over 32
   corpora. Row 1 requires all-corpus C/T, K-valid-subset C/T and C/K all with lower bound > 1;
   row 2/3/4 thresholds (1 and 1.10) match. K-invalid corpora drop out of C/K and the subset C/T
   only. Failure paths (yield floor, > 4 K failures per family, replay mismatch, deadline) raise
   before `stage1_complete` and force row 0; an interrupted stage 2 yields no transfer readout.
6. **Critique points.** Notes 1–5 are addressed in plan.md and in code (deterministic replay
   field set with explicit exclusions; per-cell yields, convergence and K errors logged; disjoint
   evaluation blocks per corpus; K-exclusion scoping with all-corpus C/T preserved; C/G4 and T/G4
   alongside the outcome; arithmetic break-even with collection failures and fitting charged, no
   finite break-even on nonpositive savings; 1× vs 2× cap sensitivity; projection updated from
   measured throughput). Notes 6–7 concern digest/question wording the researcher may not edit;
   plan.md carries the corrected numbers to the steward. Acceptable.

## Minor notes (non-blocking)

- `smoke-probe/result.json` reports `outcome.row = 0` and its config shows the earlier seed
  strides (1,000/100). It was produced by a pre-final version of the code; the committed code
  labels probe/smoke outcomes `diagnostic` (verified in my smoke re-run) and uses strides
  2,000/200. The probe remains valid for yields and timing only, which is all it is used for.
- The researcher's smoke-final `config.json` records `git_commit = a791565` (dirty tree). The
  queue run will record `627336d`, which I verified reproduces the smoke exactly.
- The `> 4 K failures` check runs after a family's full collection, so an infeasible family
  would be detected only after its ~16 min of collection. Given 200/200 bootstrap K validity
  this is immaterial.
- G4 (phase 3/5) and M (phase 4) references use their own seed blocks, so C/G4, T/G4 and T vs M
  are unpaired comparisons; the report and plan already label them descriptive.
- Stage-2 admission is likely but not guaranteed under slow tails; if skipped, stage 1 still
  decides the row and the holdouts are simply absent, as the plan allows.
