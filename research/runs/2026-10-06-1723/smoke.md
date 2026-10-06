# Implementation and feasibility checks

The approved training-only design is feasible at the measured scale. No full
learning queue was launched by the researcher. No holdout was searched.

## Checks

- `pytest -q tests/test_crossed_learning.py tests/test_four_reducer.py tests/test_map_learning.py`:
  25 passed. After the final precision readout was added, the seven crossed-learning
  tests were rerun and passed, including its numerical sample-size check.
- Ruff passes on both new modules and their tests.
- `scripts/run_queue.py --queue <task>/queue.yaml --validate`: one entry, OK;
  timeout sum 28,800 seconds, meeting the eight-hour cap.
- Full learner accounting with stub searches verifies 9,696 inner searches plus
  600 selection searches per trajectory, BE 30/cell and PA 20/cell for each
  selection candidate including G4, with disjoint inner/selection seed blocks.
- Tests cover frozen hashes, holdout payload rejection, operational early-stop
  routing to all saved maps' fresh scoring, runtime admission, independent Welch
  intervals, overlapping-label precedence, missing/duplicate/mismatched fresh
  rows, and both-arm variability in sizing.

## Reduced end-to-end smoke

Command from the worktree, with RUN_DIR set to
`experiments/output/1723-smoke-final`:

```sh
.venv/bin/python -m experiments.chem_tape.crossed_learning_run --smoke --workers 10 --deadline-seconds 600
```

One generation, inner cap 4,096, selection 12 seeds/candidate, fresh cap 8,192
and two fresh seeds/cell. Completed two independent trajectories per family in
30.14 seconds, with eight initial/generation records, 2,260 raw searches,
100/100 fresh rows, no missing/duplicate/hash/case-pairing errors and zero
holdout searches. Candidate histories, selected maps, schedules and two plots
were written and inspected. This run is explicitly smoke-only and outcome U
under the six-map minimum; it is not scientific evidence about learning.
Reports were regenerated from the same fresh rows after readout refinements;
the search engine and adaptation procedure did not change.

## Real-cap runtime diagnostic

The first diagnostic overlapped other checks and is not used for cost sizing.
An isolated five-seed/cell repeat indicated modestly higher costs; an isolated
20-seed/cell batch then reduced sensitivity to the particular seed block.
The latter command, with RUN_DIR `experiments/output/1723-probe-20`, was:

```sh
.venv/bin/python -m experiments.chem_tape.crossed_learning_run --probe --probe-seeds 20 --workers 10 --deadline-seconds 600
```

G4 and one sparse mutation from G4, every training cell, seeds
1723601..1723620, cap 65,536, population 256. Mutation RNG 1723600;
coordinates [10,18,5], deltas [0.277571,-0.459725,-0.209298].
400 searches completed in 36.77 seconds on ten workers total.

| Family / map | Searches | Mean loaded search seconds | Solves within 65k |
|---|---:|---:|---:|
| BE / G4 | 80 | 1.0383 | 57/80 |
| PA / G4 | 120 | 0.7636 | 110/120 |
| BE / perturbation | 80 | 0.9069 | 64/80 |
| PA / perturbation | 120 | 0.8840 | 103/120 |

G4 solves per cell (20 seeds each): BE 15,14,13,15; PA 15,18,19,19,19,20,
in the frozen training roster's order. All targets remain reachable. The
calibration comparison is 0.928/0.764 seconds for BE/PA in 1603; current BE
cost is about 12% higher, PA unchanged. The sparse perturbation changes both
rates and solve fractions; it does not establish late-trajectory costs.

Without assuming faster learned maps, these G4 costs project to 17.8 and
13.1 minutes per trajectory, 309 minutes for twenty trajectories, plus about
33 minutes for fresh scoring from the prior measured 1.88 seconds/search,
and reporting/overhead: approximately 345 minutes. The first admission uses a
rounded 31-minute pair cost; subsequent admissions use 1.3 times the slowest
observed pair including selection. The fresh reserve uses the larger of 1.88
seconds/search and an equal-cell average of observed costs, with capped inner
searches extrapolated to the full cap, and a 1.3 allowance. The retained
7.5-hour internal deadline and eight-hour timeout therefore remain appropriate.
Achieved balanced n can still be a runtime outcome, as approved.

## Reproduction and saved evidence

The branch contains a byte-identical bank snapshot (SHA256
`b2b856cb6d051e65599b22409cf49f654ba8d87539f073d2e9b7d061079aceb9`), checked
against current D1331 labels. G4 SHA256 is
`8a7b3091f411e659f553981b8680dc5db4bd5f3f34b6eca9c8ab3ee3e728dc10`.
The source is the main repository's 1603 output bank, unchanged.

Small review artifacts are preserved in this task's `smoke/` folder. Complete
raw smoke and diagnostic `search.jsonl` files remain under the worktree's
`experiments/output/1723-smoke-final/` and `experiments/output/1723-probe-20/`.
They were produced before the implementation commit; config.json's git hash
identifies the prior base HEAD, not the new uncommitted implementation. Final
code checksums and artifact checksums are recorded in `smoke/checksums.json`.
Full queued execution will record its actual committed HEAD in config.json.

The required plan and queue live in the shared task folder. Identical copies
of researcher-authored task artifacts are committed in this worktree's task
folder so they are reviewable with the implementation commit.
