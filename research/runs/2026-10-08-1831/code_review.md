---
verdict: pass
---

# Code review: 2026-10-08-1831 partial-program context

Reviewed `0a8ade7..998a9fe` (search instrumentation, collector, partial-count
estimator, runner, report, tests), `proposal.md`, `critique.md`, `plan.md`,
`queue.yaml`, `smoke.md` and the smoke-final outputs. I re-ran
`tests/test_partial_program.py` (7 passed, real executor replay included),
re-derived the frozen schedule (`roster(BASE)` digest equals
`confirmation_schedule.json`'s `bf362b4b…`, 7 168 rows), parsed `queue.yaml`
with `queue_lib`, and checked the smoke `search.jsonl` for archive provenance
(no archive row at or after a solve, terminal flag only at checkpoint 256,
all 16 fresh seeds carry exactly the five arms).

## Blocking issues

None.

## What was checked and holds

- **Replay.** With `collector=None` the search loop is byte-for-byte the old
  behaviour (the early `break` is kept). With a collector, the terminal
  lexicase draw uses a copied `FastRandom` (Python state via `setstate`,
  numpy bit-generator state deep-copied), and the search breaks right after;
  the result dict is identical to the uninstrumented run (test and smoke).
- **Checkpoint semantics (critique note 2).** Checkpoints are evaluated
  population counts (`generation + 1`), evaluations `= 64/128/256 × 256`. The
  exact check and `break` precede the collector call, so a solve generation
  never archives and nothing descends from a solver. S (8 of 508 parent slots)
  and P (8 of 256 indices) are drawn with replacement from the same evaluated
  population by a separate `default_rng([seed, 1831])`. Every archived tape is
  independently re-executed on D1331 in the worker; an exact tape or a
  post-solve row raises rather than being dropped.
- **Arm wiring and pairing.** Five arms share each fresh seed; collection
  seeds are offset by 1e6 from scoring seeds; corpora and families have
  distinct strides; smoke base is +1e8 and disjoint. `jobs()` verifies the
  returned `table_hash` against the expected table for every row, the
  training-case indices against the seed, and pairing across arms. C_exact is
  1246's frozen C for the same family/index, hash-checked by `frozen_source`.
  Holdout cells cannot enter a payload (`envelope` raises).
- **Estimators.** `partial_transition_counts` gives equal weight to archive
  rows within a source, then to contributing sources within a cell, then
  rescales each cell to 1 600, as plan.md states; it refuses solver-style rows,
  foreign cells, exact rows, post-solve rows and duplicate sources, and fails
  on an empty cell. C_S and T_S come from one `fit(n)` call on identical S
  counts; C_P from P counts; the α 50 C estimator and bounded T estimator are
  the frozen 1707 code. K is computed, not scored.
- **Endpoint and routing.** `log cost_T − log cost_C`, cell mean, corpus
  mean, t interval over corpora; balanced prefix guarantees equal BE/PA
  weight. `route` applies the pre-stated precedence (UB < 1.20 first). The
  1×-cap and both-solved sensitivities and the near-universal-cap flag are
  computed and shown before interpretation.
- **Stop rules.** Only completed BE_i/PA_i pairs are inferential, ≥ 6 pairs
  required, errors never count as a timeout prefix. Internal cutoff is
  14 100 s with a 300 s reserve under the 14 400 s queue timeout. Smoke
  projection is 144 min (8.9 effective workers); the all-partial-arms-capped
  sensitivity is 210 min, still under the cutoff, and the 6-pair minimum would
  be reached at about 108 min (expected) or 158 min (capped). I see no
  realistic path to stopping before six pairs for a non-scientific reason.
- **Critique disposition.** Notes 1–5 are addressed in plan.md and the code
  (corrected collection arithmetic, measured smoke rates with verification
  and serialization included, frozen schedule, terminal draw spec, weighting
  and replacement stated, routing language narrowed, uninformative outcomes
  named and priced). Notes 6–7 concern digest/question wording outside the
  researcher's folder; plan.md says so and hands them to the steward. Accepted.

## Minor notes (not blocking)

1. **Error after six complete pairs.** An execution error in a later block
   (e.g. a verification `ValueError`) makes `efficacy_eligible` false even
   though earlier pairs are complete and valid. This is the pre-stated
   conservative rule; if it triggers, the analyst should still report the
   completed prefix descriptively and name the error cause, since the data
   is intact in `search.jsonl`.
2. **Fresh-RUN_DIR guard vs crash resume.** `Runner.__init__` refuses a
   directory that already holds `config.json`. `research.py` re-runs
   interrupted entries into the same run dir, so a driver crash mid-run would
   make the retry fail at startup instead of rerunning. Not a data-integrity
   risk; worth knowing when reading a failed retry.
3. **Seed-range overlap with 1246.** The base differs from 1246's by 585, so
   seeds for (cell 0, index ≥ 15) coincide with 1246's (cell 3, index − 15).
   Different cells mean different labels, so trajectories diverge from
   generation 1; only case indices and the initial allele population are
   shared. No effect on the within-1831 paired contrasts, but future tasks
   should pick bases with a stride larger than the roster span.
4. **`effective_sources` equals `contributing_sources`** by construction
   under equal weights. Descriptive only; the name should not be read as an
   effective-n.
5. **Capped sensitivity 210.3 min** nominally exceeds the 210-minute gate.
   plan.md correctly treats it as a sensitivity, not the measured projection;
   it remains within the 235-minute internal cutoff.
6. `archive_diagnostics` and the report's projection are descriptive; nothing
   in them feeds the decision rule.
