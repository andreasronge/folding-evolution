---
verdict: pass
---
# Code review — 2026-10-10-0145 complementary-source A8 replication

Reviewed `51148fe..b6d1974` in the worktree (`source_replication_run.py`,
`source_replication_report.py`, roster plumbing in `comparison_gate_bank.py`,
`fragment_library.py`, `small_source_run.py`, tests, pinned reference snapshot),
plus proposal.md, critique.md, plan.md, queue.yaml and the smoke artifacts.

## Blocking issues

None.

## What was checked

1. **Arm wiring.** Collection phases: first/static attempts run as `G4` (off, no
   operator, G4 table); adaptive attempts run as `F` under the corpus's own
   seed build (C4 table + F4 library from the 16 first-batch rows); A8′ refits on
   first + adaptive, S8′ on first + static. Confirmation and timing rows resolve
   `builds["<corpus>|<arm>"]`, so each new build is one artifact used for all four
   ordinals, as the plan states. Historical G4 replay rows resolve the target
   cells; collection rows resolve the replacement source cells. No cross-wiring.
2. **Seeds.** Collection seeds are unique (768), disjoint from the 5 376
   historical source seeds in the snapshot, from the timing seeds and from the
   confirmation seeds; the runner asserts all three. Confirmation seeds use 2303's
   formula unchanged, and the test asserts every A8 key maps to a historical
   corpus-j/block-s row with `block == seed_ordinal`. A8′/S8′ share seeds per
   (corpus, cell, ordinal), as in 2303.
3. **Metrics match the proposal.** `bootstrap()` from 2303 is reused: per-build
   mean of four block means (each 16 cells), builds resampled within family
   (columns 0–7 BE, 8–15 PA, matching the per-family slicing in the report),
   one shared G4 baseline per draw stratified within cell, 8 192 fixed draws,
   failures = 2×cap via `cost()`. The one-cap sensitivity halves `cap` on
   unsolved rows, which gives exactly 1×cap. δ uses `contrast()` grouped by
   historical (corpus, block) on identical keys, 16 units, t on 15 df. I ran the
   report on the historical 1 024 A8 rows as if they were new rows: it returns
   u = 2.730 [2.360, 3.156], the 2303 figure, so the estimator is the same one.
4. **Legacy exactness.** `build_source`/`extract_windows` with the default roster
   reproduce the archived 2033 `BE1|0|A8` table, library, attempt keys, yields and
   hashes (test passes; also re-run in the smoke gate). The search executor and
   F operator are untouched by the diff.
5. **Handoff.** The score stage's equality check (`method_freeze`, builds,
   seed_builds, validation, admission and timing hashes) was only exercised on the
   refusal path by the researcher. I recomputed every hash from the smoke
   `preparation.json`/`builds.json`/`seed_builds.json`/`validation.json` after the
   JSON round trip: all match, so a legitimate prepare will be accepted.
6. **A8-only fallback path.** `report()` with `arms=["A8"]` was not covered by the
   tests; I ran it on synthetic rows and it completes (sigma = None, all four
   outputs written). A crash here would have cost the automated analysis after
   two hours of scoring.
7. **Gates and stop rules.** Admission is timing-only and never reads solve
   rates. Stop (cost obstacle) fires only if even A8′ alone exceeds 7 080 s with
   reserves or prepare exceeds 2 280 s. Smoke projects A8′-alone at about
   3 800 s with reserve, and full prepare at roughly 15–20 min (5.8 k worker-s
   of collection, 32 timing searches, fast fits), so neither trigger is
   plausible. Internal deadlines (2 280 s, 7 080 s) sit below the queue
   timeouts (2 400 s, 7 200 s), so a timeout is raised by the runner rather than a
   kill. Finish-by 07:12 is rechecked at score start. No risk of stopping the
   main stage for the wrong reason.
8. **Critique.** Notes 1–6 are implemented in plan.md and the report text
   (explicit counts, timing-only admission, single-build uncertainty units with
   precision scenarios, pairing manifest, usefulness/attribution/economics kept
   separate, uninformative outcome defined). Notes 7–8 are digest/question-log
   wording outside the researcher's write scope; plan.md says so and defers them
   to the steward. Acceptable.
9. Tests: `tests/test_source_replication.py` 9 passed in the worktree.

## Minor notes (non-blocking)

- **Projection bias toward dropping S8′.** Effective workers are estimated from a
  32-job timing batch on 10 workers, so tail idling biases them low (7.1 in the
  16-row smoke) and the both-arm projection high: the smoke's 6 876 s with
  reserve sits just under the 7 080 s ceiling. S8′ may therefore be dropped even
  though 2 048 searches at ~20 worker-s each would run in ~70 min at full
  throughput. This is the approved fallback and loses only the secondary
  diagnostic; the analysis should state which candidate was selected and the
  measured effective workers.
- **No F-arm historical scientific replay.** Only two 2303 G4 rows are replayed
  against stored references; no historical A8/S8 search row is. The operator and
  search code are unchanged in this diff and are hashed in the freeze, and the
  score stage replays all 32 of its own timing rows, so determinism is covered;
  cross-commit equivalence of the F path rests on the hash, not a replay.
- **`block` field on new rows.** New A8′/S8′ rows carry `block = seed_ordinal`
  purely as the pairing label to historical corpus-j/block-s; every new build has
  one artifact. The analysis must not read `block` as a separate artifact or
  treat the four ordinals as 64 units; `historical_pairing.json` makes the
  mapping explicit.
- **G4 worker-time calibration** comes from two replay rows (0.556 in the smoke,
  i.e. this machine is ~1.8× faster than the 2303 run); only the worker-seconds
  economics depend on it, and the report labels it approximate.
- Build inputs are deterministic because `jobs()` returns rows sorted by key, so a
  rebuild from `first.jsonl`/`continuation.jsonl` would reproduce the artifacts.
