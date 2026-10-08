# Comparison-gate-v1 bank (1246)

Built in this worktree from `comparison_gate_bank.py`, implementing the approved
2026-10-08-1246 proposal. `comparison_gate_1246_bank.json` is pinned by an
independent SHA-256 constant in that module. It includes the exact D1331 manifest,
all 220 distinct nonconstant behaviours and their role-assignment aliases,
canonical programs, independently checked best ≤9-token witnesses, screen rules,
and the frozen four-training/four-holdout split per family.

Reproduce the semantic build (does not perform evolutionary searches):

```sh
RUN_DIR=/absolute/empty/output RAYON_NUM_THREADS=1 .venv/bin/python -m experiments.chem_tape.comparison_gate_bank
```

The roster has 240 programs per family; 162 per family have nonconstant gates.
The exact typed-stack screen through nine tokens retains 37 BE and 56 PA
behaviours after rejecting exact/≥80% aliases and collapsing equivalent role
assignments to their lexicographically first id. Canonicals are checked in
Python and Rust on all 1331 inputs. The screen does **not** prove minimality of
13-token canonical programs. Bank identity contains no timing measurements;
`screen_timing.json` records those separately.

Training ids are the approved eight development behaviours. All twelve
steward-probed behaviours and every equivalent spelling are excluded from
holdout selection. Holdouts use the lowest SHA-256 of id + "1246" among retained,
unprobed role-covered candidates, one per repeated reducer and family. The
candidate lists and token totals are in `split`. All eight selected holdouts,
and all other nontraining cells, remain unsearched in stage 1246.

`load_training()` checks the pinned artifact and the deterministic split and
returns only training ids/labels as search payloads. Canonicals and witnesses
never enter collection or scoring. `comparison_gate_run.py` writes the full
future holdout seed roster and fitted-table hashes under its RUN_DIR; its
execution interface refuses holdout searches.
