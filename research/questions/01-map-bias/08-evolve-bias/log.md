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

## 2026-10-05 — run 2026-10-05-1558: sum vs max family bias on constant thresholds, sampling only

Experiment: [proposal](../../../runs/2026-10-05-1558/proposal.md),
[plan](../../../runs/2026-10-05-1558/plan.md). Same design and code as 1510 with a feasible
task set (commit `cd69bce`, branch `research/2026-10-05-1558`, master seed 202610051558, one
run). TAG alphabet, L 64. Fit `op_weights` on sum>1, sum>5 (Σ) and max>1, max>5 (M); hold out
sum>2 and max>2. 200M uniform calibration; three starts × six iterations of 10M per fit;
decisive transfer arms uniform, Σ-fit, M-fit and prune at 125M each (look 1 of 4); exact =
correct on all 10,000 lists; bounds at α = 0.05/64. 2309 s wall, no runtime cut.

Result: **verdict A** as pre-registered
([analysis](../../../runs/2026-10-05-1558/analysis.md)). Holdout hits per 125M:

| Arm | sum>2 | max>2 |
|---|---:|---:|
| uniform | 173 | 69 |
| Σ-fit | 852 | 92 |
| M-fit | 176 | 612 |
| prune | 161 | 86 |

Specificity (matched / mismatched) 4.84× (adj. 3.36–7.08) for Σ, 6.65× (4.13–11.08) for M;
gain (matched / uniform) 4.92× (3.42–7.22) and 8.87× (5.24–15.73). All lower bounds above 3.
Fit tasks gained 18–34×; the holdouts about a quarter of that. Mismatched fits did nothing for
the other family's holdout (1.02×, 1.33×), though they raised its fit thresholds 3.9–6.1×.
Pruning alone did nothing (0.93×, 1.25×). Both fits pushed CONST_2 down to 0.36–0.37× (CONST_5
up 1.6–1.7×): the constant overfitting the proposal feared, costing about 2.7× of holdout
gain, but not enough to reach D. Reviewer's post-hoc reading: every rate in the run (30
vector×task cells, swaps included) is reproduced within 1.5× by the product of four op folds
(INPUT, GT, the aggregator, the threshold constant); the aggregator-swap pools turn the Σ
vector into a 13.9× max>2 sampler. So what transferred is the aggregator weight (plus INPUT
and GT), not richer family structure. The Σ holdout gain repeats across 3 starts; the M fit is
one trajectory (cold starts 1–2 never reached 10 elites). This also refutes the 1510 hint that
mismatched fits help held-out members about as much (C).

Decision: continue 08 with the pre-registered next step, an evolution test on the two holdouts
(uniform, matched fit, mismatched fit, and a hand-set vector with only INPUT, GT and the
aggregator raised), because sampling A leaves A vs B (supply vs success) open, and item 12
predicts B. The hand-set arm is needed so a win for the fitted vector is not just "knowing the
aggregator helps". Fairly sure of the sampling numbers; narrow in meaning (one seed, one
holdout per family, thresholds that differ only in the constant).

## 2026-10-05 — run 2026-10-05-1705: does the fitted bias speed evolution on sum>2 / max>2?

Experiment: [proposal](../../../runs/2026-10-05-1705/proposal.md) (revision of 1700),
[plan](../../../runs/2026-10-05-1705/plan.md), code `experiments/chem_tape/evolve_bias.py` at
commit `9abc25c` (branch `research/2026-10-05-1705`). Four frozen `op_weights` arms per task
(uniform, matched fit, mismatched fit, hand-set scaffold: INPUT, GT and the family aggregator at
the fit's probabilities, CONST_0/1/2/5 at 1/22). Tagged harness: lexicase, crossover v2 0.7 with
a selected mate, mutation 0.015, L 64, P1024, 64 training cases, no early stop on training
fitness; every training-perfect candidate checked on all 10,000 lists. Endpoint: evaluations
to first exact solve, cap 262,144; paired KM median ratio, bootstrap, α = 0.05/12; two looks
(50 then up to 100 seeds per cell). 650 runs, 1,197 s wall of an 8 h budget, complete.

Result: **Partial** as pre-registered ([analysis](../../../runs/2026-10-05-1705/analysis.md)).

| Comparison (ratio of medians) | sum>2 | max>2 | Verdict |
|---|---|---|---|
| uniform ÷ matched (50 pairs) | 4.33 (2.60–6.92) | 3.58 (1.91–6.00) | faster, both |
| mismatched ÷ matched (100 pairs) | 1.66 (0.96–2.34) | 1.80 (1.23–2.80) | unresolved, both |
| matched ÷ hand-set | 0.93 (0.61–1.57) | 1.08 (0.71–1.56) | no difference, both |

So B is out for these tasks: the bias speeds evolution about 4× over uniform. The hand-set
scaffold matches the fit. Family specificity is probably real but small (point 1.7–1.8×,
below the 2× bar; the max>2 interval excludes 1, the sum>2 one does not). Unregistered and the
main surprise: the **mismatched vector, with no sampling lift on these holdouts (1.02×, 1.33×),
is itself 3.3× (sum>2) and 1.9× (max>2) faster than uniform** (95% intervals 2.18–3.93,
1.30–2.79; 50 pairs). Most of the matched speed-up is therefore generic and not predicted by
exact-solver supply; sampling lift does not predict evolution speed-up (pass-through
0.35–3.2). The four-op product model failed out of sample: it predicted hand-set sampling
lifts of 17× / 22×, measured 5.45× / 11.07× (hand-set still samples 1.11× / 1.25× better than
the fit). Evolution reached its median solve 9–40× sooner than computed random search with
the same vector, in every arm. Shortcuts (training-perfect, not exact) were common and never
counted; mismatched met them most and holds 5 of the 8 censored runs. All 642 solvers
re-verified exact; 2 of 650 solved in generation 0.

Decision: keep 08 open with its last slot unspent and send the program to strategy
(`next: strategy`), because that is the plan's frozen route for Partial, and the one thing 08
could still buy (more seeds on matched vs mismatched) can at best show a specific gain near
1.7×, under the 2× the proposal called worthwhile. The new question the run raised, why a
vector with no sampling lift speeds evolution 2–3×, is opened as
[09-generic-bias-speedup](../09-generic-bias-speedup/question.md) rather than buried here.
Fairly sure of "≈ 4× over uniform" and "hand-set ≈ fit"; the generic/specific split is
unregistered and rough.
