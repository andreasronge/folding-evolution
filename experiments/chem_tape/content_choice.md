# Inherited content choice (0250)

`content_choice_run.py` deploys unchanged 1228 order and 1938 signed-gate libraries
paired by build index on the original six development cells per bank. Protected
cells never enter job construction. It replays acquisition provenance and source
extraction, independently validates donor semantics, and freezes code, Rust
extension, libraries, rosters, seeds and the complete job schedule before exposure.
The saved order preparation is `inherited_library_run.DEFAULT_SAVED`; the gate
acquisition is the checked-in hash-pinned `signed_chain_2044/saved_1938.json.gz`.

Run from the worktree root with its venv, `PYTHONPATH=.` and
`RAYON_NUM_THREADS=1`. Each stage requires a fresh `RUN_DIR`:

```
.venv/bin/python -m experiments.chem_tape.content_choice_run exposure --workers 11
.venv/bin/python -m experiments.chem_tape.content_choice_run readout --workers 11 --exposure <exposure-dir>
```

Add `--smoke` to both for four builds, one population slot, all six cells, one
readout seed block, and the unchanged 12 × 64 generation exposure and full
restarted-search budgets. Smoke results are descriptive and labelled `smoke_only`.
Full stages use internal deadlines 2,970 and 9,570 seconds; the approved queue
has external timeouts of 3,000 and 9,600 seconds. Partial rows survive a failure,
but a failed or incomplete phase cannot be admitted or used in a later stage.

The engine's opt-in `donor_libraries=(order, gate)` interface samples a library
with probability 1/2 on each mutation, then samples uniformly within that source.
Without `gate_fraction`, the recipient's post-redraw bit selects the source;
with a fraction it samples the source independently. N uses fraction 1/2 in both
states. `donor_library` retains the legacy dose-selector behavior and random
stream. Simultaneous interfaces, empty repertoires and invalid fractions fail.

Full exposure is 1,152 trajectories; readout is 12,096 order plus 24,192 gate
searches. Pure references are one block per pair/cell/scoring repeat. The five
population laws use shared fresh program seeds per slot; pure references use a
separate namespace. The nested bootstrap uses shared build and slot indices
across both families and all laws. Pure-reference arrays are constant across
slots, so slot resampling never adds pure-reference observations.

`exposure.jsonl` preserves all per-generation selection, redraw, elite, donor
and solve-phase accounting and all episode witnesses. `score.jsonl` preserves
all restarted attempts and their exact witnesses. The readout rejects changed
code, saved libraries, schedules, audits, manifest hashes or incomplete grids.
`report.json` provides primary and directional intervals, independent 20% saving
exclusion labels, pure-reference headroom, control-qualified linkage language,
endpoint frequencies, per-state attempted/accepted/rejected donors, episode and
readout solves separately, cell costs, and acquisition/exposure/search pricing.
`dynamics.png` shows frequency, correctness diversity and readout costs. The
approved outcome precedence and conservative precision scenarios are in the
main checkout's `research/runs/2026-10-12-0250/plan.md`.
