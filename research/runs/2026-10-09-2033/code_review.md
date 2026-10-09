---
verdict: pass
---

Reviewed commit `e12edbf` (diff from `1db5444`): `experiments/chem_tape/sparse_feedback_run.py`,
`sparse_feedback_report.py`, `tests/test_sparse_feedback.py`, and the pinned
`data/sparse_feedback_2033/` snapshot of 1743's outputs; plus proposal.md, plan.md,
queue.yaml, critique.md and the smoke4/handoff artefacts in this folder.

## Blocking issues

None.

## What was checked and found correct

- **Arm wiring.** Both arms run the unchanged F operator (`operator_arm` is always `"F"`
  except for G4 replays); the policy label is bookkeeping only. Scoring rows look up
  `builds["corpus|block|arm"]`, so A8 and S8 use their own rebuilt table and library.
  Collection rows look up `seed_builds["corpus|block"]`, the pinned 1743 C4+F4 build,
  which `historical_gates` first proves bit-exact against a fresh rebuild of the first
  batch (table, table hash, library digest, attempt keys and attempts hash for all 64).
- **Source allocation.** `source_allocations` selects by 1246 schedule order, positions
  `4b:4b+4` (first) and `16+4b:20+4b` (static), validates all 3072 rows, requires 48 per
  cell, and asserts first and static keys are disjoint before hashing them. Failures are
  retained (the "not eight attempts per cell" gate counts attempts, not solvers).
- **Seeds.** Collection seeds `BASE + ci*10000 + b*1000 + ti*100 + a` are unique (1024)
  and checked against source, both candidate scoring rosters, and timing seeds; the
  implementation-smoke collection adds 2 000 000 so it never reuses full-collection
  draws. Scoring seeds are 1743's historical seeds; I verified by script that the
  12-seed roster is a subset of the 16-seed roster and that `block = seed_ordinal % 4`
  matches the retained reference rows for all 4096 F rows (0 mismatches).
- **Pooling and fitting.** `transition_counts` normalises every non-empty cell to mass
  1600 and empty cells receive 1600 of G4 expected transitions, so eight attempts do not
  weaken the α 50 prior relative to four, as the proposal claims. Library extraction
  sorts eligible fragments with a full tie-break (cells, count, length, tokens), so the
  different row orders of A8 and S8 sources cannot change the library.
- **Primary estimator.** `contrast(rows, "S8", "A8")` is cost(S8)/cost(A8) with unsolved
  = 2 × cap, cell/seed means within block, equal block weights within corpus, t interval
  on the 16 corpus log means (df 15); it raises unless all 16 corpora are complete.
  Decision labels and thresholds (lower > 1.10, upper < 1.10, else unresolved) match the
  proposal. Reference rows (retained C4F4, full F, full C) are attached to the A8 row
  with the same (corpus, cell, seed) and the pairing check compares training indices and
  block; they are never rescored.
- **Pairing check.** The parent's `initial_tokens_hash` equality was dropped on purpose
  (different decoders decode different initial tapes); training indices and arm
  presence are still enforced per (corpus, cell, seed).
- **Admission gate.** Timing uses 128 searches on the actual final A8/S8 builds, 15 %
  margin, replay and 240 s reserve, against 10 800 s. Smoke4 projected 6 683 s for 16
  seeds, so the gate falls to 12 only at ~1.6× slowdown and fails only above ~2.1×.
  Neither branch looks at yields or fitness. Prepare took 191 s with an eighth of the
  collection; the full prepare should need roughly 15 min against a 2580 s deadline.
  No wrong-reason stop risk of substance.
- **Handoff.** `score` refuses implementation-smoke preparations, re-verifies every
  frozen hash (admission, builds, code, source schedules, rosters, timing payload,
  accounting) and replays the 128 timing rows exactly before any efficacy search. The
  two negative checks in `reject_smoke/` and `reject_admission_change/` ran zero
  efficacy searches.
- **Queue.** Commands point at this worktree, outputs go under `RUN_DIR`, the score
  entry reads `preparation.json` from the sibling prepare directory (same pattern as
  1743), `expect_outputs` for both entries match the files smoke4/handoff actually
  wrote, and the 13 500 s timeout sum is under `max_queue_hours = 8`.
- **Critique disposition.** Notes 1–4 are addressed in plan.md and the code (explicit
  8192/6144 roster, timing-only admission before efficacy, pilot archive with
  reconstructed manifest, separate economics with horizon-indexed difference intervals,
  precision scenarios, scope statement). Note 5 is a digest/log wording correction that
  plan.md correctly defers to the steward, since the researcher edits no research files.

## Minor notes (non-blocking)

1. **S8 is charged the intermediate C4+F4 build** (`intermediate=True` for both arms in
   `economics`). The proposal says so, but a pure static policy would not need that
   build. The amount is ~0.2 worker-s against ~285 s of source time per build, so it
   cannot change any curve; the analysis should just say it is charged.
2. **Resolution-price target.** `balanced_target_n` uses a 1.05 half-width factor
   (log 0.0488), while plan.md's resolution-at-1.15 needs log half-width < 0.0445.
   Report-only; the analysis should use the plan's number when quoting a price.
3. **External verification seconds** are added to A8/S8 search seconds but not to the
   calibrated reference rows. Millisecond scale; negligible but asymmetric.
4. **Steward follow-up from critique note 5:** the root-10 log entry for 1743 and the
   archived digest passage still say blockwise exclusion of 0.833; blocks 0 and 1
   (upper bounds 0.858, 0.912) remain unresolved. Carry this into the next decide step.
5. Timing-smoke seeds are shared between the A8 and S8 rows of each corpus/block. Fine
   for timing; just do not read those 128 rows as a paired efficacy sample.
