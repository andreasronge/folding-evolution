---
verdict: pass
---

Reviewed `git diff 5663d9a..4ed0469` (new `content_choice_run.py`, opt-in two-library path in `tree_gp_search.py`, `tests/test_content_choice.py`, `content_choice.md`), proposal.md, critique.md, plan.md, queue.yaml, and the final smoke artifacts (`smoke-final-exposure/`, `smoke-final-readout/`, `smoke-timing.json`, `negative-validation.json`, `queue-validation.json`).

## Blocking issues

None.

## What was checked

- **Arm wiring.** Exposure: state 0 draws order donors, state 1 gate donors, each only when the per-mutation library draw (p = 1/2) fires; L keeps recipient inheritance, S shuffles bits before selection so elites inherit shuffled bits, N passes `gate_fraction=0.5` so the bit carries no donor information while both states still receive the half/half mixture. Redraw 1/32 toward Bernoulli(1/2), initial exactly 128 ones, twelve 64-generation episodes with `continue_after_solve`, programs reset per episode and bits carried over. All match plan.md.
- **Readout law.** `fraction()` maps L-matched to the own-family L endpoint, L-swapped to the other family's L endpoint of the same build and slot, S/N to own-family endpoints, M to 0.5, O/G to 0/1. In the engine the frozen law gives ordinary 1/2, order (1−f)/2, gate f/2 with uniform sampling within the chosen library, so unequal list sizes do not shift mass. Eight attempts × 65,536 cap, capped evaluations as the cost metric.
- **Seeds.** Exposure arms share program/modifier seeds within family/build/slot; the five population laws share readout seeds within destination/build/slot/cell/repeat; pure references have their own namespace. The audit counts (384 / 4,608 / 4,608 / 55,296 / 6,912) and grid counts (1,152 exposures; 12,096 order + 24,192 gate readouts) are exact and the test suite confirms them. Rotations depend only on build and slot.
- **Primary comparison and precedence.** `classify()` implements the plan's precedence (reciprocal → one direction → pooled with direction unresolved; "20% pooled saving excluded" attached independently; [0.82, 0.88] gives useful + excluded) and is unit tested. Headroom is reported pooled and per family with "unresolved" as the default label, as the critique asked. Bootstrap draws common build and slot indices across both families and all laws; pure-reference arrays are constant across slots so they are counted once per build.
- **Legacy path.** The committed `test_legacy_replay` compares `HEAD:tree_gp_search.py` with itself now that the change is committed, so I re-ran the same comparison against the parent commit 5663d9a: plain and linked single-library searches are bit-identical (results, modifier trace, final bits). The new path is opt-in and consumes no extra RNG unless `donor_libraries` is set.
- **Gates that decide whether the main stage runs.** There is no pilot or power gate; the only pre-run gates are fail-closed correctness validations (grid completeness, episode continuity, per-state donor accounting, exact witnesses, method/library/schedule/seed freezes). They passed on the final smoke and rejected five intentional corruptions. I timed the non-batch overhead at full scale: load/replay/audit about 14 s before the batch, exposure validation about 11 s for 1,152 rows, score validation about 5 s for 36,288 rows, summarize and plots seconds. The internal deadlines (2,970 s / 9,570 s) therefore cannot be tripped by validation after a complete batch.
- **Timing.** Exposure is fixed-length (196,608 evaluations per trajectory): 18.1k projected worker-s, about 30 min against a 50 min timeout. Readout projects 54k worker-s (about 90 min at ten effective workers); pricing every order law at the slowest observed per-job mean gives 132 min against 160 min. `run_queue.py --validate` admits the queue (210 min summed, under the 8 h cap); entries run sequentially so `$RUN_DIR/../2026-10-12-0250-exposure` resolves as in 1736.
- **Critique.** Notes 1–5 are addressed in plan.md and in the code (separate episode vs readout solves, per-family headroom, control-qualified linkage text, explicit precedence, conservative precision scenario). Notes 6–7 concern digest/question wording outside the researcher's write scope and plan.md says so; that is an acceptable reason.
- **Tests.** `tests/test_content_choice.py`: 17 passed at HEAD (29 s).

## Minor notes

1. `test_legacy_replay` should pin the pre-change commit (5663d9a) instead of `HEAD`; as committed it is tautological. Verified manually this time (see above).
2. Readout deadline margin is roughly 30 min under the conservative scenario. Each unsolved row costs about 41 worker-s, so a few hundred extra unsolved crossed rows (L-swapped, G or N on order) would consume it. If that happens the stage fails closed with partial rows; the exposure stays admitted and only the readout needs re-running. The analysis should check for `failure.json` before reading `report.json`.
3. Own-pure/M headroom is build-paired but not search-seed-paired (pure references use a separate seed namespace), so expect that interval to be wider than L/M. Interpretation only; the plan already says the guard cannot override a direct L/M result.
4. `freeze()` keys nine files by path relative to `Path.cwd()`, so both stages must run from the same working directory for the readout's freeze comparison to pass. True under `run_queue.py`; worth remembering for any manual re-run.
5. Full-size `exposure.jsonl` will be about 0.9 GB and is loaded whole in both stages; fine on this 32 GB machine.
6. The smoke exposure manifest records `git_commit` 5663d9a (run before the commit) while its method hashes match 4ed0469; the full run will record the right commit.
