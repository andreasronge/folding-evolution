---
verdict: pass
---

# Code review — 2001 table × library component crossing

Reviewed `git diff 9a15cc9..6dabda8` (`component_transfer_run.py`,
`component_transfer_report.py`, `tests/test_component_transfer.py`, frozen
1717 artifacts under `data/component_transfer_2001/`), proposal.md, plan.md,
queue.yaml, critique.md and `smoke_measurements.json`.

## Blocking issues

None.

## What was verified

1. **Arm wiring.** `schedules()` sets table_build = pair for D tables and
   permutation[pair] for T tables, and library_build by the same rule from the
   library owner, so T/D is T table π(i) + D library i and D/T is the
   reverse. `envelope()` reads table and library from the declared owners;
   the `arm` string passed into `search()` is only stored. Bare arms pass
   `child_transform=None`, the same path the G4 arm used in 1717, with the
   fitted table; the test checks this equals plain `search()` on the same job.
2. **RNG separation and shared initialisation.** Search uses
   `default_rng([seed, 0/1/2])` for cases, initial population and variation;
   `BlockOperator` uses `[seed, 4]`. Same table + seed therefore gives the same
   initial population across library choices, and `validate_rows` enforces
   this by `initial_tokens_hash`. Proposal's "arms with the same table share
   initial programs" holds.
3. **Seeds.** Target seeds 2100000–2115047, calibration 2200000+…; disjoint
   from each other (tested) and from the 1717 target seeds (1200000–1215047,
   checked: zero overlap), so D/D and T/T are fresh references. Calibration
   cells (development split) are disjoint from target cells (tested).
4. **Replay.** 16 native 1717 target rows (4 per family × cohort, builds 0
   and 12) replayed bit-exact excluding timing fields. Both banks share the
   identical 625-input list, so drawing the diagnostic inputs from the
   family bank instead of the DG bank (as 1717 did) changes nothing.
5. **Provenance checks.** Artifact hashes, 1717 preparation hash, D cohort
   identity against the audited original, TS source rows and fit membership,
   method hashes, table/library digests, and operator-off ⇒ zero block
   events are all checked before any search; each scoring stage re-checks
   the frozen preparation and recomputes the admission from the saved
   calibration rows. TS joins DG only after `search_rows_hash` matches.
6. **Statistics.** Log cost with failures at 2×cap, geometric mean over the
   fixed cells; R = cost(T/T)/cost(T/D) with the numerator/denominator in
   the right order; bootstrap resamples the 24 pairs once per draw shared
   across both families, and the two repeats jointly across arms within
   pair × cell. `classify` applies the plan's labels on DG only; the
   critique's non-exclusive contrasts (T/∅ vs T/D, D/T vs D/D, bare B) are
   reported as separate flags, not folded into the primary label. 1×cap
   sensitivity, economics (hybrids charged two acquisitions, tested) and
   resolution price are descriptive.
7. **Gate.** Admission requires both family projections
   (1.3 × max(worker, wall) + 120 s) under timeout − 30 s and prepare
   < 1770 s. Measured: DG 5374 s vs 8970, TS 1699 s vs 3570, prepare 142 s.
   The projection is recomputed deterministically in each scoring stage
   from the saved calibration rows, so it cannot flip between prepare and
   score. There is no stop rule that could abort the DG primary stage for a
   reason unrelated to runtime.
8. **Queue.** Three sequential entries, 14 400 s ≤ 8 h cap; `${RUN_DIR%/*}`
   resolves to the per-run date directory (`run_queue.py` computes it once
   and sets RUN_DIR without a trailing slash, shell=True). The 10-worker
   requirement matches `--workers 10`; `LIMITS` match the entry timeouts.
9. **Critique.** Notes 1–5 are addressed in plan.md (costing scenario
   wording, calibration spec, replacement-vs-portability labels, unresolved
   outcome named, Keijzer et al. added). Notes 6–9 are digest/question edits
   outside the researcher's write scope and are explicitly deferred to the
   steward; that is a reasonable disposition.

## Minor notes (non-blocking)

- **TS calibration under-predicts TS target runtime.** The TS development
  cells are much easier than the protected targets: T/T averaged 0.69 s on
  the dev cells vs 3.40 s on the 1717 TS targets (D: 3.6 vs 4.4 s). Scaling
  the four unknown arms by the dev-cell ratio gives roughly 1 750 s; if they
  ran like G4 on targets (14 s) the raw total is about 2 900 s, inside the
  3 570 s limit but without the 30 % reserve. A TS timeout would lose only
  the secondary retention result (DG writes a complete `result.json` first),
  so this is not blocking. The analyst should check `progress.json` if TS
  fails, and a future design should calibrate on target-like cells.
- Because admission is `all(...)` over both families, a TS over-projection
  would also skip the DG primary stage. With TS at 48 % of its limit this is
  not a realistic risk tonight, but the coupling is worth removing later.
- **Resume caveats.** `Runner` refuses a RUN_DIR that already has
  `config.json`, so an interrupted entry re-run into the same folder fails
  immediately; and a resume on a later calendar day points
  `${RUN_DIR%/*}` at a new date directory, so DG/TS would not find
  `preparation.json`. Only matters if the queue crashes.
- The bootstrap resamples both pairs and seeds, which is slightly
  conservative relative to a pure pair bootstrap; fine for the plan's
  intervals.
- `resolution_price` pools per-arm seconds across both families when
  pricing added pairs; it is descriptive only.
- `progress.json` and `timing.json` are produced by the scoring entries but
  not listed in their `expect_outputs`; harmless.
