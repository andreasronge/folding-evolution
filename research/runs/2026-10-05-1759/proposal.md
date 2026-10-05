---
node: questions/01-map-bias/09-generic-bias-speedup
title: Split the no-lift speed-up into INPUT/GT and the rest of the fitted vector (2×2, fresh seeds)
---

## Why this now

I follow the strategy ([strategy.md](strategy.md)): one bounded test of 09. It also replicates
1705's unregistered surprise on fresh seeds. In 1705, the other family's fitted vector
("mismatched", X) added no exact solvers by sampling on sum>2 / max>2 (1.02× / 1.33×). Yet it
reached an exact solve 3.3× / 1.9× sooner than uniform (50 pairs, 95% intervals 2.18–3.93 and
1.30–2.79). We do not know whether that effect is real, or which part of X causes it.

The data also make one thing sharper. On each holdout, X *lowers* the ops that task needs.
- On sum>2, X is the max-fit. It sets SUM to 0.38× and REDUCE_ADD to 0.40× of uniform.
- On max>2, X is the sum-fit. It sets REDUCE_MAX to 0.45×.
- On both, CONST_2, the holdout's threshold constant, is 0.37×.

X raises INPUT (2.6–2.9×), GT (3.0–3.2×), CONST_5 (1.6–1.7×) and CONST_1, and pushes about
ten other ops below 0.6×. So the gain comes from something other than the task's own parts.

**What 1705 saved (checked before proposing).** Each run file has: the solver genome, the
*count* of training-perfect shortcut candidates, the 64 training indices, and a coarse history
(generation 0, every 25 generations and the end; best and mean training accuracy, number of
training-perfect individuals, run census).
- **No shortcut genomes were saved.** So the "free decode" of shortcuts that 09 suggested (G3)
  is impossible. Only the 642 solver genomes can be decoded. That would show what the
  solutions contain, but not what came before them.
- Generation-0 best training accuracy is about 0.50–0.54 in every arm. So the speed-up does
  not show as better starting fitness at this resolution.
- The history is too coarse to time when partial solutions appear.

## What would be run

**The arms** form a 2×2 factorial that splits X exactly. Write any 22-op vector as two
parts:
- (a) the probabilities of INPUT and GT;
- (b) how the remaining mass is split among the other 20 ops (their conditional
  distribution).

Then:

| Arm | INPUT, GT | The other 20 ops (conditional) |
|---|---|---|
| U uniform | 1/22 each | uniform |
| IG | X's values | uniform (each = (1 − p_INPUT − p_GT)/20) |
| R ("fitted remainder") | 1/22 each | X's conditional, rescaled to 20/22 |
| X mismatched (replication) | X's values | X's conditional |

Each task uses its own X: the max-fit on sum>2 and the sum-fit on max>2, frozen in 1705's
`evolve_bias_vectors.json`. Here is what is held fixed, and the limits of each contrast:
- **U → IG** raises INPUT and GT and shrinks all 20 other ops by the same factor (about
  0.82×). It changes nothing *between* the other ops. Equal dilution is the unavoidable
  cost of raising INPUT and GT.
- **U → R** keeps INPUT and GT at uniform and changes only the shape of the rest. **R is not
  a junk-suppression control.** It also lowers the task's aggregator and CONST_2 and raises
  CONST_5. On sum>2 it also raises REDUCE_MAX (about 3.5×), so it carries the max>2
  shortcut route (G3). On sum>2, an effect of R can therefore be G2 (junk suppression) or
  G3. **max>2 is the cleaner test of G1 vs G2.** There, sum>2 is training-perfect on
  0 of 100 training sets, so G3 cannot act.
- **IG and R vs X** asks whether either factor alone reaches the full effect. The
  interaction (whether the two factors add on the log-time scale) is reported but is not a
  decision input.
- **Initialization and mutation stay coupled.** Every vector is used for both, as in 1705.
  Claims are about "the vector as used by this harness". There will be no claim about
  initial supply versus mutational supply. Concentrated vectors also make a few more op
  mutations redraw the same op. This is reported, not controlled.

**Fixed setup:** identical to 1705, using `experiments/chem_tape/evolve_bias.py` on branch
`research/2026-10-05-1705` (commit `9abc25c`), extended only with the new arms and logging.
TAG alphabet, L 64, P1024, lexicase, crossover v2 at 0.7 with a selected mate, mutation
0.015, 64 label-balanced training cases. An exact solve means correct on all 10,000 lists.
The cap is 262,144 evaluations. There is no pilot: 1705's pilot already set the size and cap.

**Seeds:** a new master seed, disjoint from all 1705 streams. 100 paired seeds per cell.
Within a task, all arms share a seed's training set. 2 tasks × 4 arms × 100 = 800 runs, in a
single look. For scale, 1705 ran 650 runs (half of them slower uniform or mismatched runs) in
20 min on 4 workers. Expect under 1 h; queue timeout 2 h.

**Endpoint and statistics:** as in 1705. The endpoint is the paired ratio of median
evaluations to the first exact solve, with a seed-bootstrap interval. Per task, there are
five registered contrasts: U÷X, U÷IG, U÷R, X÷IG and X÷R. That makes ten in all, corrected
for multiplicity (the plan fixes α and the method). The plan freezes the "matches X" margin.
I suggest that an arm *carries* the gain when U÷arm is resolved faster (lower bound > 1) and
X÷arm has its upper bound < 1.5. In words: the arm is clearly faster than uniform, and not
much slower than X. Point estimates and solve curves go in the report for every cell.

**Cheap descriptive additions** (no gates). These serve the strategist's priority: partial
programs rather than counts of complete solvers.
1. **Per-generation logging** of best training accuracy, the first generation reaching
   ≥ 0.75 and the first reaching 1.0 training accuracy. This splits time-to-exact into
   "reaching a good partial" and "turning a training-perfect into an exact solver". It shows
   which phase each factor shortens.
2. **Save up to 20 distinct shortcut genomes per run.** For each, record its full-domain
   agreement with the other family's task (max>2 on sum>2 runs, sum>2 on max>2 runs). This
   is what tests G3. The data only describe which shortcuts occur and cannot show they cause
   the speed-up.
3. **Decode the 1705 solver genomes and the new ones.** Count whether INPUT and GT are on
   the executed output path, versus merely present on the tape.

## What each outcome would mean

All outcomes are judged per task. max>2 decides G1 vs G2; sum>2 adds G3.

- **No replication** (U÷X not resolved faster in a task): the 1705 effect was noise or
  seed-specific in that task. If both tasks fail, park 09 ("did not replicate"). Close 08
  with "≈ 4× over uniform; generic share unconfirmed". If one task fails, judge only the
  other; the generic claim becomes single-task.
- **IG carries the gain, R does not** (G1, shared scaffold): raising the two ops every
  threshold task reads is the transferable part. This would be the first piece of a bias
  that evolution uses without supplying whole solvers. That is what a heritable-bias design
  would need to carry. Close 09. Close 08 with "yes over uniform; the generic part is
  INPUT/GT; the family-specific part is small and unresolved". Hand to strategy.
- **R carries the gain, IG does not**: the shape of the rest matters, not INPUT/GT. On
  max>2, that points to G2, junk suppression, broadly read: R also shifts constants. On
  sum>2 alone, G2 and G3 cannot be told apart; the shortcut decode is then the only hint.
  Close 09 with that bounded answer. Do not chase which ops in R matter; the stop rule is
  one experiment.
- **Both partly** (each faster than uniform, neither reaching X): the gain is spread out,
  with no single interpretable component. Park 09 as "replicated, mechanism diffuse". Close
  08 with its bounded answer.
- **The tasks disagree** (e.g., IG carries on max>2, R on sum>2): this would fit G1 plus a
  sum>2-only stepping stone (G3). It counts as a mechanism only if the shortcut decode shows
  max>2-like shortcuts in sum>2 runs. Otherwise treat it as ambiguous and park.

In every case 09 stops after this run. The program returns to strategy, and the last root
slot is not committed.

## Alternatives considered

- **Spend 08's last slot on more matched-vs-mismatched seeds.** Rejected, as the strategy
  says: the best case is "real but about 1.7×".
- **A suppression-only arm built by resetting INPUT and GT in X and renormalizing.** This is
  my R, renamed. I named it for what it actually changes, because it is not pure junk
  suppression.
- **A cleaner junk-only arm** (lower only ops that never appear on solver paths). It needs a
  definition of "junk" taken from solver decodes that do not exist yet. That would add a
  fifth arm and a second mechanism question, so I rejected it.
- **Separate initialization from mutation** (X at initialization only, or in mutation only).
  This adds 4 more cells per task. It is the next question only if IG or R carries the gain,
  so I deferred it.
- **Drop the X arm and reuse 1705's data for it.** Rejected: replication on fresh seeds is
  half the point, and paired contrasts need X on the same training sets.
- **Run CA robustness or 02 instead.** Rejected per the strategy: they are less direct, and
  02 has no owner request.

**Budget:** 09 has 2 experiments, 0 used; this uses 1. Root 01 has 2 left, so 1 would remain
afterward. 08 keeps its last slot unspent.
