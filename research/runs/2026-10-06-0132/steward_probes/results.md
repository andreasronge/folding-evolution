# Steward probes, run 2026-10-06-0132 (unreviewed, one run each)

Code: `research/main` at `a65ded0`, detached worktree, 10 spawn workers on the 12-core host.
Six PA training cells on D1331, cap 65 536, population 256, score = log2(evaluations to an
exact solve), unsolved = log2(131 072) = 17.

Probe 1 (`probe.py`; 840 runs, 90 s wall; 20 seeds × 6 cells per map):

| map | solved ≤ 65k | mean log2 cost (SE) | sd per run | s/run (10 workers) |
|---|---|---|---|---|
| G | 0.93 | 13.75 (0.14) | 1.56 | 0.65 |
| hand-set PA grammar (IF_GT→INPUT/ADD, ADD→DUP) | 0.88 | 14.10 (0.15) | 1.64 | 0.80 |
| U | 0.23 | 16.57 (0.08) | 0.87 | 1.75 |
| G, all 552 log-weights + N(0, 0.5), four draws | 0.73–0.88 | 14.12–14.86 | 1.41–1.68 | 0.76–1.20 |

Probe 2 (`probe2.py`; 1 560 runs, 124 s wall; same 120 paired runs per map): G 13.94. One row of
G perturbed (all 23 log-weights + N(0, 0.7)), difference from G (SE), paired correlation:
start row 23 +0.07 (0.10, r 0.80); INPUT +0.16 (0.18); SUM −0.26 (0.17); REDUCE_ADD +0.01;
REDUCE_MAX +0.02; REDUCE_MIN(22) −0.18 (0.18); ADD +0.25 (0.17); DUP −0.04; IF_GT +0.54 (0.19);
CONST_0 −0.02; CONST_1 −0.20 (0.15); CONST_2 −0.04. Paired correlation 0.16–0.49 except the
start row (0.80).
