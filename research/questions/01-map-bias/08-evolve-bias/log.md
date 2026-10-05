# Log: 08-evolve-bias

## Opened 2026-10-05 by the steward

Opened when [07](../07-shared-arrival/log.md) was parked and the shared-helper line stopped
(run 2026-10-04-2135). Part 2 of the README's core question is the root's only untested half;
[02](../02-fixed-target-sampling/question.md)'s reopen condition still needs an owner wish to
settle fixed-target bias, which is not recorded. First experiment proposed in
[runs/2026-10-05-0040](../../../runs/2026-10-05-0040/proposal.md).

## 2026-10-05 — run 2026-10-05-1510: sum vs max family bias, sampling only (not executed)

Experiment: [proposal](../../../runs/2026-10-05-1510/proposal.md) (third version, after
critiques in runs 0040 and 1505). Fit `op_weights` on sum>5/10/15 and max>2/5/7, hold out
sum>7/12 and max>3/6, compare uniform, matched and mismatched fits on held-out P(exact), with
CI gates. The researcher built it (commit `3803bca` on branch `research/2026-10-05-1510`:
`experiments/chem_tape/family_bias.py`, Rust TAG sampler); the code passed review on
correctness but the run was blocked after one repair.

Result: not run; no budget used. The reviewer's own uniform probes (60M + 35M tapes, reviewer
seeds, not run data; [code_review.md](../../../runs/2026-10-05-1510/code_review.md)) show the
frozen task set cannot pass calibration: thresholds equal to an alphabet constant are hit at
~1e-6 (60M: sum>5 75, max>1 47, max>2 42, max>5 30), thresholds one ADD away at ~1e-8
(max>3 2 in 60M, sum>7 1 in 95M), and sum>10, sum>15, max>7, sum>12, max>6, sum>8, sum>11,
max>4 had 0 hits in 95M. The Σ family would keep one fitting task and no holdout, so the run
would stop at "infeasible task set". Side observations from the reviewer's emulation of the
fit on the probe pool (descriptive): the Σ-fit raised sum>5 ≈ 6.9× and the M-fit raised
max>2/max>5 ≈ 7.7×/8.4×, but the *mismatched* fits also raised them (M-fit on sum>5 ≈ 2.9×,
Σ-fit on max>5 ≈ 5×), so much of the gain may be generic (explanation C). The fit's
per-iteration pool (~833k tapes) is too small to iterate past the first update.

Decision: continue 08 with an amended task set built from the constant thresholds (fit on
1 and 5, hold out 2, in both families) and a larger fit pool, reusing the reviewed code,
because the blocker is the task set, not the design or the code, and a corrected run costs
about an hour of queue. Lesson: probe uniform hit rates before freezing a task set.
