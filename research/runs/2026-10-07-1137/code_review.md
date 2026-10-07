---
verdict: pass
---

# Code review: 2026-10-07-1137 selection-calibrated continuation

Reviewed `git diff b46cc98..86ef669` in the experiment worktree
(`continuation96_run.py`, `continuation96_report.py`, the pinned
`data/continuation_0821.json.gz`, `tests/test_continuation96.py`), plus
proposal.md, plan.md, queue.yaml, critique.md and smoke.md.

## Blocking issues

None.

## What was verified

1. **Arm wiring and seeds.** T and C share the in-loop learning blocks
   (`learning` seed = base + start_index·10000 + generation·100 + j) and the
   final-selection blocks within a start; each arm has its own mutation
   stream (`mutation` seed offset by arm index). The T arm forces token
   steps; C draws token or context steps with probability ½. Cells rotate
   per generation so BE gets 24 and PA 16 searches per cell. The new
   namespaces (1 861 000 000 to 1 866 000 000, plus the 10 M / 20 M smoke
   and probe offsets) are disjoint from 0821's (1 821 M to 1 847 M including
   offsets); only F1 (1 824 000 000 to 049) is reused, by design. A test
   asserts this disjointness.
2. **Budget.** Each trajectory is checked in code to spend exactly
   8·96·12 + 2·192 = 9 600 searches; F1 is 12 000 rows and full F2 is
   16 500. Smoke and the fake-jobs tests confirm the counts.
3. **Gate and outcome rows.** `gate()` is the F1 T/S point estimate ≥ 1.10;
   `outcome()` evaluates U → 1/2 → 3 → 4 → 5 → 6 → 7 in the proposal's
   order with the plan's thresholds. Boundary tests cover each row.
4. **Baseline identity check.** The pinned 0821 reference is SHA-verified
   on load. I hashed the three 0821 output files in
   `experiments/output/2026-10-07/2026-10-07-0821-rank-one-continuation/`:
   all match `source_files_sha256`. I recomputed all 4 000 S fingerprints
   from the original 0821 `fresh_scores.json` with the same 16 scientific
   fields: 0 mismatches; evaluations/solved agree on all 8 000 S and T24
   rows. The live replay in smoke.md matched 10/10 rows with this
   worktree's Rust build.
5. **Estimator reproduces 0821.** Running the new `contrasts()` on the
   reference T24/S rows gives 1.026 [0.904, 1.165], df 14, identical to the
   0821 analysis table, so the family-balanced estimator is unchanged.
6. **Tests.** `tests/test_continuation96.py` and
   `tests/test_rank_one_learning.py`: 21 passed. The runner imports from the
   worktree (`folding_evolution` and `_folding_rust` resolve under
   `2026-10-07-1137/`), `--help` runs, and the queue entry calls the module
   with `--workers 10 --deadline-seconds 19800` under `timeout_seconds`
   20 700 (5.75 h < 8 h cap).
7. **Runtime.** 0821's measured pair walls were 332–455 s for 8 080
   searches, so a 9 600-search trajectory is about 475 s and stage 1 about
   2.1 h plus 0.3 h F1. If the gate passes, 16 C trajectories plus F2 need
   about 2.5 h; with the 1.3× reserves all 16 starts fit the 5.5 h internal
   deadline at 0821 rates (the representative probe measured faster). The
   queue starts around 12:30, so the 22:00 clamp is inactive.
8. **Critique disposition.** Notes 1–5 are addressed in plan.md: fixed
   budget; survivor-only selected-change diagnostic with
   accepted/missing/covered counts and no substitution of the retained
   competitor (code and a test enforce this); row 1 restricted to "this
   procedure"; shortened stage 2 with ≥ 6 starts per family uses rows 4–7
   with T/S(F2) matched to the C starts (implemented and tested with
   df = n − 2); F2 S/T/G4 reserved even when no C fits; "bit-identical"
   defined as the 16 deterministic fields excluding timing and labels.
   Notes 6–9 concern wording in digest/question files outside the
   researcher's write scope; plan.md says so and does not propagate those
   claims. Acceptable.

## Gate stability (recomputed on the 0821 pilot)

Bootstrapping the pinned 0821 F1 rows (T24 vs S, 16 starts, 50 seeds),
resampling starts within family and seeds, 2 000 replicates:

| Resampled | sd of log2 T/S | gate passes (≥ 1.10) |
|---|---:|---:|
| starts + seeds | 0.085 | 14.5 % |
| seeds only | 0.039 | 0.6 % |
| starts only | 0.081 | 11.3 % |

Shifting the bootstrap distribution to a true effect of 1.15× gives a pass
rate of about 75 %; at 1.05× about 24 %. So the gate is a soft
point-estimate threshold whose error is dominated by which 16 starts were
drawn, exactly as the proposal states (half-width 0.18 log2). A false pass
costs 2.5 h of stage 2 that ends in row 5 or 7, not a false claim; a false
fail at a true 1.15× gain happens about one time in four. The size grid is
what the 22:25 run deadline allows (20 starts was considered and rejected
for time), not an arbitrary truncation. Not blocking, but the analysis
should report the gate's standard error (about 0.085 log2) with the verdict.

## Minor notes

- **F2 confirms seeds, not starts.** Seed-only resampling moves T/S by
  0.04 log2 while the between-start component (0.08) is shared between F1
  and F2, so T/S(F2) will track T/S(F1) closely. Row 5 versus 6 is in
  practice decided by the same 16 start-level values that passed the gate.
  plan.md already says F2 is not learning replication; the analysis should
  not call it independent confirmation of learning.
- **Selected-change coverage will be sparse.** In the smoke, 4 of 27
  accepted children had their source parent survive. At n = 96 coverage may
  stay low; treat the readout as descriptive with its denominators.
- **No fail-fast baseline check.** The S identity check runs after the 2.4 h
  token stage. A 20 s replay of two S rows (the `--probe` baseline check) at
  the start of the full run would catch a harness change early. Not needed
  today: the replay already matched in this worktree with the same build.
- **C reserve uses T timing.** Admission reserves 1.3× the slowest T
  trajectory; the probe shows C learn searches 6–15 % slower per search than
  T, within the margin. `slow_b` does scale the fresh reserve if C maps slow
  down.
- **Winner's-curse sign.** `acceptance_minus_rescore` is negative for a
  lucky child (acceptance score lower than its rescore); note the sign when
  reporting.
- **Internal deadline only checks > 180 s.** If a future run started after
  about 19:30 local, stage 1 would hit the deadline and yield U rather than
  refusing to start. Irrelevant for today's 12:30 start.
