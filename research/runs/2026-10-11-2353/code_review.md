---
verdict: pass
---

# Code review: 2026-10-11-2353 (R-bind vs R-all on the 24 signed-chain cells)

Reviewed commit `465f2fa` against `997ccdb` (three new files: `rebound_library.py`,
`input_rebound_run.py`, `tests/test_input_rebound.py`; no engine, bank or Rust change),
plus proposal.md, critique.md, plan.md, queue.yaml, smoke.md and the smoke/prepare artifacts.
Independently re-ran `tests/test_input_rebound.py` and `tests/test_signed_chain.py` in the
worktree: 16 passed in 51 s. The signed-chain driver hash in the worktree matches the pinned
`CHAIN_DRIVER_SHA`.

## Blocking issues

None.

## What was checked

1. **Arm wiring.** `envelopes()` passes `None` donors for R-tree, the 24 supplied gates for
   R-gate, the original semantic entries for R-all and the expanded list for R-bind, all
   through the unchanged `order_run.execute` (P 256, mix 0.5, 8 × 65,536, half-library
   donors). Donor draws in `tree_gp_search.search` are uniform over the list, so retained
   duplicate slots carry original-entry mass as the proposal requires.
2. **Rebinding is correct.** Prefix opcodes 0–3 are X0–X3 (`TERMINALS` order), so `rename`
   maps exactly the indexed inputs and leaves ANY, constants and operators alone. Validation
   checks every one of 21,528 slots against the production VM and against column permutation
   of D625, including fixtures with repeated inputs, ANY and IF_GT operand order. Primitive
   sizes and identity-permutation slots are checked. Roster-averaged needed-helper draw mass
   is asserted equal per build; the smoke prepare confirms it (R-all strata 144/275/138/19
   units at 0–3 present; R-bind 552 units with all three present).
3. **Seeds.** Full grid uses 20481000–20508647, cell-major, build, repeat, attempt. Seeds are
   shared only within a unit across arms (library arms at every repeat; references at
   repeat 0), so the 576 R-tree and 576 R-gate jobs are independent seed groups as the
   critique asked. Disjointness from every historical range (1938 source/presearch, 2044,
   2150 and their smokes) and from the smoke/identity seeds is audited and tested.
4. **Primary estimand and decision rule.** Pooled capped mean R-bind/R-all over 24 × 24
   units with repeats averaged inside units before the paired crossed build × cell
   bootstrap (8,192 draws, seed 202610112353). `classify` implements the approved precedence
   (upper < 0.90 → material; else lower > 1.00 → harm; else lower > 0.85 → small/none;
   else unresolved) and both threshold facts are reported. Reference contrasts use
   repeat-zero pairing and are labelled so. Validity flags are computed first and do not
   alter rows.
5. **Gates and stop rules.** The only pre-stage rule is the timing-only r selection; it was
   applied in the smoke (ratio 0.479 ≤ 1.3) and r = 6 is now fixed in queue.yaml, so it
   cannot stop the main stage. The prepare entry is deterministic provenance replay that
   already passed (113 s against a 870 s limit). No efficacy gate exists.
6. **Timeouts.** Scoring timeout 12,900 s against an estimate of 160 min that prices both
   library arms at the smoke R-all cost (9.86 s/job) rather than the measured 7.70 (2044,
   development cells) or 8.80 (2150, protected cells). Even an R-bind price of 15 s/job
   would finish in about 190 min. Summed timeouts 230 min are inside `max_queue_hours`.
   The output date directory is fixed at queue launch, so the `$(dirname "$RUN_DIR")`
   sibling lookup for the prepared folder is safe across midnight.
7. **Critique notes.** Notes 1–4 are addressed in plan.md and in code (explicit reference
   grid, fixed smoke size and r rule, inclusive timeouts, narrowed attribution wording,
   decision precedence, archived sizing script). Note 5 (prior question/digest wording) is
   deferred to the steward with a stated reason (the researcher may only write in the task
   folder); that is acceptable and the steward should pick it up at decide.

## Minor notes

- **Precision forecast is optimistic.** `precision_audit.json` reproduces the shifted-build
  half-width (0.112) but not the proposal's repeat-split claim: a straightforward repeat
  split gives 0.153. The 0.08–0.09 forecast therefore rests on one of two sizing views. The
  2150 R-all/R-tree interval at 18 cells × 4 repeats had log half-width about 0.107; with
  24 cells × 6 repeats and seed-paired library arms, 0.09–0.11 is a more honest expectation.
  This does not change whether the grid should run, but the analyst should expect
  `unresolved` to be likelier for true ratios in 0.85–0.92 than the proposal states.
- **Post-deadline failure after success.** `main()` raises `TimeoutError` and writes
  `failure.json` if the report finishes after the internal deadline, even though
  `report.json` and `score.jsonl` were already written. With 30 s of slack this is
  unlikely; if it happens, the written report is still complete and usable.
- **Legacy signed-gate tests** (`test_frozen_bank_complete_split_and_fresh_paired_grid`,
  `test_source_replay_and_tampering_fail_closed`) fail on this branch as they did on
  `997ccdb` and in 2150; `baseline_legacy_check.json` reproduces that. Not caused by this
  change and not on the experiment's path.
- Smoke rows (16 jobs, 15 solves, 1 R-all cap) are timing-only and carry no validity or
  efficacy information; the analysis must not cite them.
