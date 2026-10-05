---
node: questions/01-map-bias/09-generic-bias-speedup
title: Does INPUT/GT mass or the rest of the fitted vector carry the no-lift speed-up? (2×2, fresh seeds, n 250)
---

## What changed since 1759

The design is the same four-arm factorial the critic asked to keep ([critique](../2026-10-05-1759/critique.md)).
I made four changes:
1. **The carry gate now points the right way.** An arm C carries the gain only if the
   **upper** bound of C÷X (C's median time ÷ X's) is below 1.5. That means C is at most
   1.5× slower than X.
2. **Decisions name components, not mechanisms.** "IG suffices" means that raising INPUT
   and GT, and thinning every other op evenly, reproduces the speed-up. It does not show
   that partial scaffolds are supplied, that junk is suppressed, or that shortcuts act as
   stepping stones. Shortcut and milestone logs stay descriptive and drive no decision.
3. **Unresolved outcomes are spelled out.** This includes "X replicates but IG and R stay
   unresolved", which ends as *unresolved*, not as "diffuse".
4. **n is set from a precision check on 1705's saved times** (below): 250 pairs instead of
   100. I also measure the sampling lift of the two new vectors, which takes about 15 min.
   Without it, an IG win cannot be read against the "no-lift" puzzle: IG keeps the
   aggregator and CONST_2 close to uniform, so it probably *does* add exact solvers.

## Why this now

I follow [strategy.md](../2026-10-05-1759/strategy.md): one bounded test of 09, replicating
the unregistered 1705 surprise on fresh seeds. In 1705 the other family's fitted vector X
added no exact solvers by sampling (1.02× / 1.33×). Even so, X reached an exact solve 3.3×
(sum>2) and 1.9× (max>2) sooner than uniform, on 50 pairs
([1705 analysis](../2026-10-05-1705/analysis.md)).

X raises INPUT (2.6–2.9×), GT (3.0–3.2×), CONST_5 and CONST_1. It lowers the holdout's own
aggregator (0.38–0.45×), CONST_2 (0.37×) and about ten other ops. 1705 saved no shortcut
genomes. Generation-0 best training accuracy is 0.50–0.54 in every arm, and the history is
too coarse to time partial solutions. So the existing data cannot split X, and a new run is
needed.

## What would be run

**Arms.** Any 22-op vector splits into two parts: (a) p_INPUT and p_GT, and (b) the
conditional distribution over the other 20 ops.

| Arm | INPUT, GT | Other 20 ops (conditional) |
|---|---|---|
| U uniform | 1/22 each | uniform |
| IG | X's values | uniform, each (1 − p_INPUT − p_GT)/20 |
| R | 1/22 each | X's conditional, total mass 20/22 |
| X (replication) | X's values | X's conditional |

Each task uses its own X: the max-fit on sum>2, the sum-fit on max>2. Both are frozen in
1705's `vectors.json` / `evolve_bias_vectors.json`. Here is what each contrast holds fixed:
- **U→IG** changes only (a). The other 20 ops all shrink by the same factor, about 0.82×.
- **U→R** changes only (b). That is not pure junk suppression. R also lowers the task's
  aggregator and CONST_2 and raises CONST_5. On sum>2 it raises REDUCE_MAX about 3.5×.
- **Initialization and mutation stay coupled.** The vector feeds both, as in 1705. Claims
  are about "the vector as used by this harness".

**Fixed setup.** Identical to 1705: `experiments/chem_tape/evolve_bias.py` at `9abc25c`,
extended only with the new arms and the logging below. The setup is TAG, L 64, P1024,
lexicase, crossover v2 at 0.7 with a selected mate, mutation 0.015 and 64 label-balanced
training cases. An exact solve means correct on all 10,000 lists. The cap is 262,144
evaluations, and there is no pilot.

**Seeds.** A new master seed, disjoint from every 1705 stream. There are 250 paired seeds per
cell, in one look. Within a task, all four arms share each seed's training set. That makes
2 tasks × 4 arms × 250 = 2,000 runs.

**Sampling (descriptive).** 125M random tapes for each of IG and R on its task, as 1705 did
for the hand vector. That is 4 vectors at about 220 s each.

**Runtime.** At 1705's per-run CPU times (U 1.9 / 7.3 s, X 3.5 / 13.2 s on sum2 / max2), and
assuming IG and R fall between U and X, the runs need about 3.5 CPU-hours. That is about
1 h on 4 workers, plus 15 min of sampling, plus logging overhead. Estimate 1.5 h; queue
timeout 3 h. This is a heavy run, so it goes in the overnight window.

**Endpoint and statistics.** As in 1705: the paired ratio of median evaluations to the first
exact solve, with seed-bootstrap intervals. There are five registered contrasts per task,
ten in all: U÷X, U÷IG, U÷R, IG÷X and R÷X. Each gets a Bonferroni 99.5% interval
(α = 0.05/10).

**Precision check (done for this proposal, from 1705's saved run times).** I simulated an arm
whose times are drawn from X's own 1705 distribution. I paired it *unpaired* with X, which is
conservative because shared training sets add positive correlation. Then I computed the
99.5% upper bound of arm÷X. The table shows the median upper bound, and in brackets the
chance it falls below 1.5:

| n | sum>2 | max>2 |
|---|---|---|
| 100 | 1.52 (46%) | 1.54 (44%) |
| 200 | 1.35 (81%) | 1.38 (82%) |
| 250 | 1.33 (92%) | 1.34 (94%) |

So at 100 pairs, an arm exactly as fast as X fails the gate about half the time. That is
the critic's "least informative" outcome, so I chose 250. The plan should rerun this check
with its frozen bootstrap. If the chance at 250 is under 80% on either task, the plan
raises n to at most 350. It may not loosen the margin.

**Arm labels**, per task and per component arm C ∈ {IG, R}, frozen before running:
- **carries**: U÷C lower bound > 1 and C÷X upper bound < 1.5. C is resolved faster than
  uniform and at most 1.5× slower than X.
- **partial**: U÷C lower bound > 1 and C÷X lower bound > 1. C is resolved faster than
  uniform and resolved slower than X.
- **no gain shown**: C÷X lower bound > 1 and U÷C lower bound ≤ 1.
- **unresolved**: anything else. This label is not evidence that C fails to carry, or that
  C matches X.

On max>2, X's gain is only about 1.9×, so an arm that is within 1.5× of X may have only
about 1.3× of the gain. There, "carries" means "within 1.5× of X", not "has most of the
gain". The share of the log gain, log(U/C) ÷ log(U/X), is reported for every cell as a
description, not a gate.

**Descriptive additions** (no gates, no decisions):
1. Per generation, best training accuracy, and the first generation reaching ≥ 0.75 and
   1.0 training accuracy.
2. Up to 20 distinct training-perfect shortcut genomes saved per run, each with its
   full-domain agreement with the other family's task.
3. Decoding of 1705's and the new solver genomes: are INPUT and GT on the executed output
   path, or only present on the tape?
4. Sampling lift of IG and R over uniform, and pass-through for each arm.

## What each outcome would mean

First, X has to replicate in a task: the U÷X lower bound must be > 1. Component verdicts
count only in tasks where it does.

- **X not replicated in a task.** Report it as "not replicated at n = 250", not as
  "1705 was noise". If X fails in both tasks, park 09. Close 08 with "≈ 4× over uniform;
  the generic share is unconfirmed".
- **The same single arm carries in every task where X replicated, and the other does not
  carry.** If IG carries: INPUT/GT mass, with even thinning of the other ops, is enough to
  reproduce the speed-up. If R carries: the shape of the rest is enough. Close 09 with that
  component answer. Whether partial scaffolds, junk suppression or shortcuts do the work
  stays open, and IG's or R's measured sampling lift is reported next to it. Close 08: "yes
  over uniform; generic part = [component]; family-specific part small, unresolved". If X
  replicated in only one task, the claim is single-task and 09 is parked, not closed.
- **Both arms carry.** Either component alone is enough, and the effects do not add up.
  Close 09 with that, mechanism open.
- **Both partial.** Each arm is resolved faster than U and resolved slower than X: neither
  component alone reproduces the gain. Park 09 as "replicated; neither part alone
  suffices". The interaction is reported as a description.
- **No gain shown for both, with X replicated.** Only the combination helps. Park 09 with
  that.
- **The tasks disagree** (e.g. IG carries on max>2, R on sum>2). Record the per-task labels
  and park 09. The shortcut decode may hint at why, but it cannot decide.
- **Any label that would change the outcome is unresolved.** Examples: X replicates while
  IG and R straddle the gate, or one arm carries and the other is unresolved where that
  matters. The answer is "unresolved at n = 250". Park 09 and say so plainly. No reading
  of the descriptive logs upgrades it.

09 stops after this run in every case, and the program returns to strategy. The last root
slot is not an obligation.

## Alternatives considered

- **Keep n at 100 with margin 2×.** On max>2, X's whole gain is about 1.9×, so a 2× margin
  would pass nearly any arm that beats uniform. Rejected.
- **Two looks (125 + 125) to save time.** That adds a stopping rule for a run of about
  1.5 h. Rejected.
- **Spend 08's last slot on matched vs mismatched.** Rejected per the strategy: the best
  case is "real but about 1.7×".
- **A fifth "junk-only" arm, or an initialization vs mutation split.** These answer
  mechanism questions that this run's decisions no longer claim. Deferred until a
  component carries.
- **Reuse 1705's X runs.** Rejected: replication on fresh seeds is half the point, and the
  contrasts need X on the same training sets.
- **Parked questions.** No reopen condition is met, and the critic agreed. 02 has no owner
  request. 07 and 04 have no testable B-helper arrival or replay.

**Budget.** 09 has 2 experiments, 0 used; this uses 1. Root 01 has 2 left, so 1 would
remain. 08 keeps its last slot unspent.
