---
verdict: pass
---

# Code review: 2026-10-07-1924 (diff 1909a66..5565d54)

Reviewed `solver_feedback_run.py`, `solver_feedback_report.py`, the committed
`data/solver_feedback_1924/` artifacts, `tests/test_solver_feedback.py`,
proposal.md, critique.md, plan.md and queue.yaml. The search engine, bank,
`transition_counts`, `fit`, `seed_for` and the streaming `jobs` runner are the
unchanged 1707 code, reused by subclassing.

## Blocking issues

None.

## What was checked

1. **Provenance of frozen inputs (recomputed, not trusted).** The three 1707
   source files hash to the values in `provenance.json`. All 32 tables in
   `parents.json` are byte-equal to 1707's `corpora[tid]["tables"]["C"]`, their
   `table_hash` equals the fit's recorded C hash, and every 1707 training row
   with arm C for that lineage carries the same hash. `solvers.json` is the
   exact multiset of the 7,408 solved 1707 collection rows (corpus, cell,
   tape). `replay.json` is identical to the 40 phase-`replay` rows in 1707's
   search log. The pinned provenance SHA and artifact SHAs match the files.
2. **Arm wiring.** C = parent table; C2 = `fit(counts from C-collected tapes)["C"]`;
   C' = `fit(counts from G4-collected tapes)["C"]`. Collection under C uses
   `parent["table"]`, under G4 uses the hash-checked G4. T and K are saved and
   never evaluated. Shrinkage target stays G4; the first-round corpus is not
   pooled. Matches the proposal's frozen rule.
3. **Seeds and pairing.** Phases 10 (A), 11 (B), 12 (C), 13 (D collection) with
   the unchanged BASE; within-phase offsets stay below 1e6, so they are disjoint
   from 1707's phases 0–5. The probe used absolute seeds 19,240,000+, which do
   not intersect the ~2.03e9 BASE-derived blocks. C2, C and C' share seeds and
   case indices per lineage × cell (same `seed_for` arguments; `contrast()`
   additionally rejects unpaired `training_indices`). The runner's roster-key
   check rejects duplicate (phase, family, corpus, cell, arm, seed) jobs.
   Expected job counts (10,240 / 6,144 / 5,120 / 3,072 / 2,560 at half) are
   asserted by the test and I re-ran the test file: 5 passed, ruff clean.
4. **Holdout leakage.** `load_bank` returns only training cells; `envelope`
   switches to the three holdout cells only for phase `holdout`, and the test
   confirms a holdout cell in a collection phase raises.
5. **Estimator and outcome rows.** Per-cell mean log2 (unsolved = 2 × cap), then
   equal cell weight per lineage, equal family weight pooled, df = min family
   df (15 full, 7 half-control); holdout one-sample over 32 (or 16) lineages.
   Rows 0/1/2/4/3/5 in `outcome()` are disjoint and in the plan's order; row 1
   requires a complete, valid C' contrast, otherwise row 2. Holdout labels and
   `source_attributed_transfer` (row 1 + both holdout contrasts > 1) match the
   plan. Both sides of every C' contrast use the fixed admitted roster; an
   incomplete roster raises rather than shrinking.
6. **Yield floor (the only gate before the primary stage).** 24/48 per cell
   under C. In 1707 the worst C cell over 32 seeds solved 28/32 (0.875); at
   that rate P(< 24/48) ≈ 4e-11. The probe's 20 cells gave ≥ 46/48. The floor is
   a safety net, not a live gate.
7. **Stage D admission (timing only, no result enters).** Recomputed with
   1707's measured costs (G4 collection 2.075 worker-s, C training 0.777,
   holdout 0.766): D is 22,306 worker-s. 1707's large phases ran at 9.9
   effective workers and per-lineage collection at 8.6, so the projection is
   about 38–40 min and the full gate about 48–50 min. A–C is about 32–35 min
   including validation. With the 100-min work window that leaves about 65 min
   at the gate: full D with ~15 min margin. Even if C2 were 2× slower than C
   in B and C (about +10 min), full D is still admitted. The grid
   (full/half/none) fills the time the queue allows; half is admitted down to a
   ~25-min remainder. The whole run (~75–80 min) fits inside the 6,000-s
   deadline and 6,660-s timeout.
8. **Failure handling.** Timeout in B → row 0 (validation false). Timeout in C
   → training rows stand, holdout unresolved. Any exception in D: timeout keeps
   completed control phases, a scientific error (yield floor, hash, pairing)
   sets `control_valid=False` and drops both C' contrasts while keeping C2/C.
   `search.jsonl` is streamed, `corpora.json`/`stages.json` are checkpointed.
9. **Critique disposition.** Notes 1–5 are implemented (solve expectations in
   config, absolute-cutoff repricing, source-procedure scope in config and
   limitations, fixed half roster with df 7/15 and abort-on-control-failure,
   conditional `required_n`, distinct harm/bounded/unresolved labels). Notes
   6–11 concern existing digest/question text; plan.md says the researcher role
   forbids editing those files and leaves them to the steward. That is a valid
   reason; the steward should apply them at `decide`.

## Minor notes (not blocking)

- **Hard-coded absolute cutoff.** `OWNER_WORK_CUTOFF` is 22:05 Stockholm today
  and the parser refuses any other value for a non-smoke run. The work window
  is min(100 min, time to cutoff). Full D needs a queue start before about
  20:45 Stockholm, half D before about 21:05, and B+C before about 21:30; a
  start after 22:05 fails at validation and would still consume root 10's last
  slot. The driver should start the queue immediately after this review (it is
  20:12 now). Re-running later needs a one-line edit of the constant.
- The seed-disjointness assertion against `range(19240000, 19350000)` is
  vacuous (BASE-derived seeds are ~2e9), but the conclusion holds because the
  probe really did use absolute seeds.
- `validation["parent_table_checks"]` and `table_checks` start at 32 as
  constants rather than counters; cosmetic.
- `make_report`/`save_report` are not wrapped in try/except; a reporting bug
  would lose `result.json` while raw rows survive in `search.jsonl`. The smoke
  exercised every stage and report branch, so the risk is low.
- The smoke's `effective_workers` of 2.5 reflects tiny stages and pool startup,
  not the full-scale throughput used above; the full run's A–C timings will set
  it.
