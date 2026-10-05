---
node: questions/01-map-bias/09-generic-bias-speedup
title: Does INPUT/GT mass or the rest of the fitted vector carry the no-lift speed-up? (2×2, fresh seeds, n 250)
---

## What changed since 1810

The experiment, arms, seeds, size and runtime are unchanged, as the
[critique](../2026-10-05-1810/critique.md) asked. Only the outcome rules changed:

1. **Labels no longer overlap.** Each component arm gets one label from two separate
   gates (below). "Carries" takes precedence. "Falls short" now needs C÷X's **lower**
   bound above 1.5. A lower bound above 1 is no longer enough.
2. **"No gain shown" and "only the combination helps" are gone.** If X improves and neither
   component is resolved either way, I report exactly that and park. I add no follow-up
   study to strengthen it.
3. **Both arms carrying means only "either intervention meets the 1.5× criterion".** I make
   no claim about additivity. The interaction is reported as a description.
4. **One scope rule covers every branch.** 09 closes only if the same verdict holds in both
   tasks and X replicated in both. Any single-task answer parks 09.

## Why this now

This follows [strategy.md](../2026-10-05-1759/strategy.md): one bounded test of 09 that
replicates the unregistered 1705 surprise on fresh seeds. In 1705, the other family's
fitted vector X added no exact solvers by sampling (1.02× / 1.33×), yet reached an exact
solve 3.3× (sum>2) and 1.9× (max>2) sooner than uniform, on 50 pairs
([1705 analysis](../2026-10-05-1705/analysis.md)). 1705 saved no shortcut genomes, and its
history is too coarse to time partial solutions. So the existing data cannot split X, and a
new run is needed.

## What would be run

**Arms.** Any 22-op vector splits into (a) p_INPUT and p_GT, and (b) the conditional
distribution over the other 20 ops.

| Arm | INPUT, GT | Other 20 ops (conditional) |
|---|---|---|
| U uniform | 1/22 each | uniform |
| IG | X's values | uniform, each (1 − p_INPUT − p_GT)/20 |
| R | 1/22 each | X's conditional, total mass 20/22 |
| X (replication) | X's values | X's conditional |

Each task uses its own X: the max-fit on sum>2 and the sum-fit on max>2. Both are frozen in
1705's `vectors.json` / `evolve_bias_vectors.json`.
- **U→IG** changes only (a). The other 20 ops all shrink by the same factor, about 0.82×.
- **U→R** changes only (b). This is not pure junk suppression: R also lowers the task's own
  aggregator and CONST_2, raises CONST_5, and on sum>2 raises REDUCE_MAX about 3.5×.
- **Initialization and mutation stay coupled**, as in 1705. Claims are about "the vector as
  used by this harness". They say which *intervention* suffices, not which mechanism
  (scaffold supply, junk suppression, shortcut ancestry) does the work.

**Fixed setup.** Identical to 1705: `experiments/chem_tape/evolve_bias.py` at `9abc25c`,
extended only with the new arms and the logging below. TAG, L 64, P1024, lexicase,
crossover v2 at 0.7 with a selected mate, mutation 0.015, 64 label-balanced training cases.
An exact solve means correct on all 10,000 lists. Cap of 262,144 evaluations. No pilot.

**Seeds.** A new master seed, disjoint from every 1705 stream. 250 paired seeds per cell, in
one look. Within a task, all four arms share each seed's training set. That makes
2 tasks × 4 arms × 250 = 2,000 runs.

**Sampling (descriptive).** 125M random tapes for each of IG and R on its task, as 1705 did
for the hand vector: 4 vectors at about 220 s each. This shows whether an arm that carries
also adds exact solvers. It cannot identify the evolutionary mechanism.

**Runtime.** At 1705's per-run CPU times, about 3.5 CPU-hours: about 1 h on 4 workers, plus
15 min of sampling and logging overhead. Estimate 1.5 h; queue timeout 3 h. This is a heavy
run, so it goes in the overnight window.

**Endpoint and statistics.** As in 1705: the paired ratio of median evaluations to the first
exact solve, with seed-bootstrap intervals. Five contrasts per task, ten in all: U÷X, U÷IG,
U÷R, IG÷X, R÷X. Each gets a Bonferroni 99.5% interval (α = 0.05/10). Ratios are time ÷ time,
so C÷X > 1 means C is slower than X.

**Precision check** (done for 1810, from 1705's saved times). I simulated an arm with X's
own time distribution, unpaired with X. Pairing should tighten this, but that is an
assumption, not a guarantee. The table shows the median 99.5% upper bound of arm÷X, and in
brackets the chance it falls below 1.5:

| n | sum>2 | max>2 |
|---|---|---|
| 100 | 1.52 (46%) | 1.54 (44%) |
| 200 | 1.35 (81%) | 1.38 (82%) |
| 250 | 1.33 (92%) | 1.34 (94%) |

This is the power for an arm that matches X *exactly*. It is not the power for every useful
intermediate. The plan reruns the check with its frozen bootstrap, on 1705 data only. It
also reports the chance that C÷X's lower bound exceeds 1.5 for an arm whose times are X's
times multiplied by 2.25. If either chance at 250 is under 80% on either task, the plan may
raise n to at most 350. It may not change the margin.

## Arm labels

The labels are frozen before running. They apply per task, and only where X replicated
(U÷X lower bound > 1). For each component arm C ∈ {IG, R}, two gates:
- **vs X (sufficiency, margin 1.5):** *within* if C÷X upper bound < 1.5; *short* if C÷X
  lower bound > 1.5; otherwise *open*.
- **vs U:** *faster* if U÷C lower bound > 1; otherwise *not resolved*.

Each arm gets exactly one label, in this order of precedence:
1. **carries** = within and faster.
2. **falls short** = short. The vs-U gate is reported beside it ("falls short, but faster
   than U" or "falls short; improvement over U not resolved").
3. **unresolved** = anything else, including "within" but not resolved faster than U. This
   is not evidence that C fails to carry, nor that it matches X.

On max>2, X's gain is only about 1.9×, so an arm within 1.5× of X may hold only about 1.3×
of it. There, "carries" means "within 1.5× of X", not "has most of the gain". The share of
the log gain, log(U÷C) ÷ log(U÷X), is reported in every cell as a description, not a gate.

## What each outcome would mean

**09 closes only when X replicated in both tasks and the verdict below is the same in both
tasks.** Every other case parks 09. The per-task labels are recorded either way, and a
one-task answer is stated as a one-task answer.

- **X not replicated in a task.** Report it as "not replicated at n = 250", not as "1705 was
  noise". If X fails in both tasks, park 09.
- **One arm carries** (in both tasks). Close 09: "raising INPUT and GT, with the rest thinned
  evenly, is enough to reproduce the speed-up within 1.5×" (IG), or "the shape of the rest
  is enough" (R). Report the arm's sampling lift beside it. The mechanism stays open, and so
  does the other arm's status if it is unresolved.
- **Both arms carry** (in both tasks). Close 09: "either intervention alone meets the 1.5×
  criterion". Nothing about additivity. The interaction is reported as a description.
- **Both fall short** (in both tasks). Park 09: "replicated; neither intervention alone comes
  within 1.5× of X". The vs-U gate says whether each one still helps.
- **X replicates, and no arm carries or falls short in a task.** Report it plainly, e.g. "X
  improves; neither component's improvement over U is resolved; IG and R are [resolved /
  not resolved] slower than X". Park 09 as unresolved at n = 250. No follow-up study is
  added to justify a stronger reading.
- **The tasks disagree**, or one task is unresolved. Record the per-task labels and park 09.
  The shortcut decode may hint at why, but it cannot decide.

The descriptive logs never upgrade a label. 08 follows 09: if 09 closes, close 08 with "yes,
about 4× over uniform; [component] carries the generic part; family-specific part small,
unresolved". If 09 parks, park the unfinished part of 08 with its 1705 result. Either way
the program returns to strategy. The last root slot is not an obligation.

**Descriptive additions** (no gates, no decisions):
1. Per-generation best training accuracy, and the first generation reaching ≥ 0.75 and 1.0.
2. Up to 20 distinct training-perfect shortcut genomes saved per run, each with its
   full-domain agreement with the other family's task.
3. Decoding of 1705's and the new solver genomes: are INPUT and GT on the executed output
   path, or only present on the tape?
4. The sampling lift of IG and R over uniform, and the pass-through for each arm.

## Alternatives considered

- **A 2× margin at n 100.** On max>2, X's whole gain is about 1.9×, so nearly any arm would
  pass. Rejected.
- **Two looks (125 + 125).** That adds a stopping rule to a run of about 1.5 h. Rejected.
- **A fifth junk-only arm, or an initialization vs mutation split.** These answer mechanism
  questions that this run no longer claims to settle. Deferred, and only if a component
  carries.
- **Spending 08's last slot on matched vs mismatched.** Rejected per the strategy: the best
  case is "real but about 1.7×".
- **Reusing 1705's X runs.** Rejected: fresh-seed replication is half the point, and the
  contrasts need X on the same training sets.
- **Parked questions.** No reopen condition is met, and both critiques agreed. 02 has no
  owner request. 07 has no testable B-helper copy or replay, and 04 depends on 07.

**Budget.** 09 has 2 experiments, 0 used; this uses 1, and 09's stop rule (one experiment)
ends it here. Root 01 has 2 left, so 1 would remain. 08 keeps its last slot unspent.
