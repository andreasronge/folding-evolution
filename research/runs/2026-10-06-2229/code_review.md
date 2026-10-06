---
verdict: pass
---
# Code review — 2026-10-06-2229 (frozen crossed-family holdout evaluation)

Reviewer: Claude (Fable 5.1), independent of the researcher. Reviewed the diff
`2582aa6..33fcee2` in the worktree, proposal.md, critique.md, plan.md, queue.yaml,
smoke.md and verification.json. Every claim below was re-executed, not read off
the researcher's notes.

## What was checked

| Check | Result |
|---|---|
| Frozen stage-1 copies | SHA256 of `config.json`, `trajectories.json` and the decompressed `fresh_scores.json.gz` in `experiments/chem_tape/data/crossed_1723/` equal the originals in `experiments/output/2026-10-06/2026-10-06-1723-crossed-family-training/` (`f345d3e2…`, `94138e35…`, `bbca7320…`). The original run was complete (20 trajectories, `stop_reason` null, not gate-stopped). |
| Frozen maps | `frozen_source` requires exactly BE1–10 and PA1–10, checks id/family/outer seed, re-derives every table from its saved 24-vector with `table_for("M", …, {"G": G4})` and compares the hash. G4 hash `8a7b3091…` checked against `tables()["G4"]`. No map can be dropped, added or re-weighted; `make_report` independently re-checks the 20-map set. |
| Stage-1 rows through the new code | Running `gain_matrix` on the frozen 10 500 fresh rows and `estimate` on the own-training gains reproduces the 1723 analysis exactly: BE 2.179× [1.979, 2.400], PA 2.271× [1.946, 2.650]. So the descriptive transfer-loss baseline is the same quantity stage 1 reported. |
| Arm wiring | Job set is the full Cartesian product arms (21) × holdout cells (3) × seeds (400) = 25 200; `job()` rejects any training cell, unknown arm or seed outside the block. Search payload carries only `id` and `labels`. `load_bank`'s training-cell dictionary is discarded; holdout labels are checked against the D1331 roster inside `load_bank`. |
| Seeds | Block 2229000–2229399 is shared by all 21 maps (the design's pairing by seed) and disjoint from stage 1's 1723300–1723349 and from 1603's blocks. `gain_matrix` verifies that every row's 64 training-case indices equal `default_rng([seed, 0]).choice(1331, 64)`, which is what `search()` draws, so pairing across arms is enforced, not assumed. |
| Search settings | Unchanged `composition_search.search`: P 256, length 32, crossover 0.7, mutation 0.03, 64 sampled cases, exact check on all 1 331 inputs, cap 524 288; unsolved rows carry `evaluations == cap` and `gain_matrix` rejects anything else. Metric is seed-mean log2(T_G4/T_map), as proposed. |
| Inference | Trajectory is the unit; `interval()` gives one-sample t within arm and Welch between arms. C_BE, C_PA (on the per-map mean of the two PA holdouts), per-cell PA contrasts, the interaction (asserted equal to C_BE + C_PA in log2), six arm × cell generic gains, arm × family aggregate gains, damage/usefulness labels, transfer loss and future sizing are all computed. Outcome rules U/1/2/3/4/5(a,b) are applied in the proposal's order with W precedence over B. |
| Completeness and U | Any missing, duplicate or extra row, hash/phase/cap/pop mismatch, learning flag, smoke/probe mode or deadline stop returns `complete=False`, outcome U and empty inference dicts; partial rows are still persisted. The G4 ≥ 0.85 solve gate also forces U with data otherwise complete. Tests cover each path; 17/17 pass in the worktree, ruff clean. |
| Queue | Loads through `scripts.queue_lib.load_queue` and `run_queue.py --validate`; one entry, timeout 7 200 s, internal deadline 6 300 s with a 180 s reporting reserve, all 11 `expect_outputs` produced by the probe run. The runner pre-creates `metadata.json`/`stdout.log`/`stderr.log` in RUN_DIR; `Runner` only refuses a RUN_DIR that already has `config.json`, `search.jsonl` or `result.json`, so the launch will not trip on that. |
| Committed code = probed code | SHA256 of the three new source files at HEAD `33fcee2` equal those recorded in verification.json, so the probe and smoke ran on the committed implementation. Worktree is clean. |

## Gates and stop rules

There is no pilot-gated main stage: the queue is a single stage and the only
in-run gate is the G4 solve-fraction ≥ 0.85 per holdout, which decides U versus
a scientific row rather than whether anything runs. I recomputed its stability
from 1603's 150 G4 full-cap rows on these three cells (47/50, 49/50, 50/50):
drawing the 400-seed fraction from a resampled pilot rate, the gate fails with
probability about 0.013 on the BE cell and ≤ 0.0001 on the PA cells; at the
point estimates it never fails. The probe (5/5 on each cell) agrees. Stable.

The feasibility stop (write `infeasible.md`) was a researcher-time decision
and did not truncate any grid: the full 400-seed design is queued.

## Critique dispositions

All five substantive critic notes are implemented in code, not only in prose:
(1) deadline or incomplete rows → U with no subset inference, per-map/cell
solve counts recorded; (2) row 5b retained as the unresolved A-versus-B
reading; (3) row 3 and row 4 meanings rewritten to "improvement unresolved"
and "bounded matched advantage, not equality", with `reversed_preference`
reported; (4) matched/mismatched gains labelled improved/harmed/unresolved for
both directions, PA two-cell aggregate gains for both arms, interaction always
reported; (5) `future_sizing` separates expected half-width from approximate
80 % detection per direction and the interaction, with costs. Notes 6–8 concern
digest/question wording that the researcher role may not edit; plan.md says so
and leaves them to the steward. That is an acceptable answer.

## Blocking issues

None.

## Minor notes

1. **Two evaluation seeds were touched at reduced cap during the first smoke**
   (2229000–2229001, cap 8 192). Nothing could adapt to them since the maps are
   frozen and nothing was selected; the exposure is recorded in `config.json`
   and plan.md. The analysis should repeat the caveat in one line, no more.
2. **Runtime margin.** Probe mean 0.75 s/search projects 35 min; the internal
   work deadline (6 120 s) tolerates a mean of about 2.4 s/search. Unsolved
   full-cap searches cost about 20 s each, so an overrun needs roughly 8–9 %
   unsolved across all map × cell pairs; the probe saw 3/315 and stage 1 saw
   ≤ 4 % on training cells. One probe map (PA9 on the BE holdout) solved 3/5,
   so a weak map on one cell is possible but cannot alone exhaust the margin.
   An overrun yields U and a re-run, not a wrong result.
3. **Transfer loss mixes seed blocks.** Own-training gain uses stage 1's 50
   seeds; holdout gain uses 400 new seeds. It is descriptive, as the plan
   states; the analysis should not read its interval as a test.
4. **Stage-1 `early_stop`/`reservation` helpers are imported indirectly** via
   `crossed_learning_run` but never called; `test_job_set_all_frozen_maps_no_training_or_learning`
   patches `mutate` and `Runner.evolve` to fail if reached. Fine.
5. For the steward: the critic's notes 6–8 (digest and question 16 wording
   on "small", "tied" and "no harm") are still open and should be applied when
   the 2229 result is logged.
