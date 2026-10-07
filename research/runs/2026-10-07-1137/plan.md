---
estimated_minutes: 297
---

# Implementation plan, fixed before experiment execution

Implement the approved [proposal](proposal.md) using the reviewed rank-one
runner and learning engine. Expected queue wall-clock is about 145 minutes
if the token gate fails and 297 minutes if all context starts fit. The queue
timeout is 20,700 seconds (5.75 hours); the internal admission deadline is
the earlier of queue start + 5.5 hours and 22:00 Europe/Stockholm. Smoke tests
exercise small runs only; they do not decide the scientific gate.

## Conditions and seeds

Use all sixteen saved 1723 maps BE1–8 and PA1–8, without success filtering;
exclude the four calibration starts. Preserve D1331, v2_rmin_first, population
256, length 32, 64 lexicase cases, crossover 0.7, mutation 0.03, exact checks
on 1,331 inputs, bounds, normalization, and mutation operators from 0821.
For T and C use two parents, six children, twelve generations, 96 shared
searches per candidate at cap 65,536 (BE: 24 per own cell; PA: 16), then 192
fresh final-selection searches per parent. Each trajectory uses 9,600 searches.
T mutates three token coordinates with N(0, 0.5). C uses a token step or a
rank-one context step with probability one half, and its own mutation stream.

Allocate deterministic namespaces 1,861,000,000 for generation searches,
1,862,000,000 for final selection, 1,863,000,000 for F2, and 1,864,000,000
for mutation streams, and 1,865,000,000 for row directions, with disjoint
per-start/block offsets. The initial 1,837 namespace would overlap 0821's
smoke bootstrap namespace; this pre-execution correction avoids it. T and C share
generation/final search blocks within a start. Verify these namespaces against
earlier runner configurations before smoke execution; log the resolved seed
schedule. F1 intentionally reuses 1,824,000,000–049, 50 shared seeds per own
cell, cap 524,288. F2 uses 1,863,000,000–049, the same allocation and cap.
Neither fresh block selects maps; F1 only controls the stage-2 admission gate.

Stage 1 always runs all T trajectories and F1 evaluations of S, generation-6
T_mid, and final T (12,000 fresh searches). Compare all S scientific fields
against 0821 F1 rows: cell, seed, budget, evaluations, success, and every
other deterministic scientific payload field present in the prior schema.
Exclude arm/label bookkeeping and elapsed/runtime fields. Require exactly
the expected unique rows and verify source hashes and train/holdout separation.
Prior T24 maps are compared descriptively using their existing F1 rows.

Stage 2 runs iff the family-balanced paired T/S(F1) point estimate is >=1.10.
Admit C in BE1, PA1, ..., BE8, PA8 order, stopping at the first that cannot fit.
Use 1.3 times the slowest completed T trajectory plus reserved F2 scoring
for all admitted starts and the prospective start. Always reserve independent
S/T confirmation and G4 scoring even if no C start fits. F2 scores S/T for
all sixteen starts, C/C0 for admitted starts, and G4 on all ten cells; full
F2 is 16,500 searches. Report T/S(F2) on the same complete starts as C/T when
a context comparison exists; also provide the all-start confirmation as a
descriptive readout. C0 removes only the learned residual.

## Measurements and diagnostic accounting

Primary estimates average paired log2 cost improvements within own cells and
seeds, then within start, and give each family equal weight. Use a 95% t
interval with n_BE+n_PA-2 degrees of freedom (14 for all sixteen). Preserve
the reviewed family-balanced standard-error calculation. Report solve counts,
failures charged at twice cap, actual inner evaluations spent, search counts,
elapsed time, parameters, seeds, map/source hashes, admission decisions, and
infrastructure checks. Emit the learning-curve figure and machine-readable
summary plus raw maps, searches, and trajectory histories.

Selected-change diagnostics use only accepted child/source-parent pairs for
which BOTH actual source parent and child survive into the next generation.
Their next-block independent rescores are already in the 9,600-search budget.
Record the child's actual parent ID, accepted-child count, eligible count,
missing-source-parent count, final-generation count without a next block, and
covered pair count per arm/start/generation. This is a selected subset, not
complete coverage. Never substitute the retained competitor for the source
parent. No diagnostic scores enter selection and no extra searches are added.
Winner's curse compares an accepted child's acceptance score with its own
next-generation rescore whenever the child survives. Other descriptive
readouts: T_mid/S, T/T_mid, T96/T24 (different procedures and effort), mean
parent-score slope, per-family gains versus starting S, C operator survival,
clipping, and residual cosine alignment with the hand-set BE–PA direction.

## Outcome meanings, evaluated in this order

U: hash or leakage failure, baseline mismatch, missing/duplicate required rows,
or fewer than six complete T trajectories in either family: infrastructure
result, no scientific claim. Any invalid required fresh rows also yield U.

1: gate fails and T/S(F1) upper <1.10: this twelve-generation, 96-search
procedure's mean gain is bounded below 1.10 on these saved starts. It does
not establish an operator plateau at every budget. Keep question 18 parked
and return to strategy; joint learning from G4 remains untested.

2: gate fails and upper >=1.10: unresolved token progress; report the bound
and return to strategy without automatically allocating another experiment.

3: gate passes but fewer than six complete C trajectories in either family:
report token F1/F2 estimates; context comparison is unresolved because of
runtime. A shortened stage with >=6 starts in each family uses rows 4–7,
reports admitted identities and larger intervals, and conditions the token
confirmation on exactly those starts. This resolves the proposal's conflicting
runtime prose in favor of its explicit outcome-table minimum.

4: gate passes and C/T lower >1: C outperforms T on training cells for this
procedure. Claim beneficial adaptation above S only if C/S resolves it.
Resolved C/C0 >1 supports residual contribution, while acknowledging removal
changes token marginals. Transfer remains untested in this queue.

5: gate passes, C/T lower <=1 and T/S(F2) lower <=1: token progress lacks
fresh-search confirmation. Report the C/T interval as a constraint on relative
context performance, without treating this as the informative positive-control
null. F2 replicates scoring on fixed learned maps, not learning trajectories.

6: gate passes, T/S(F2) lower >1 and C/T upper <1.15: in a procedure with
confirmed token gain, the mean context addition is bounded below 1.15 on
training cells. Restrict interpretation to these starts, representation and
loop; joint learning from G4 remains untested.

7: otherwise: unresolved C/T with a confirmed token control. Any follow-up
requires observed pair variance and a decision it could change.

The larger evidence block, shorter trajectory, and greater total effort are
a procedure comparison, not causal identification of scoring noise. Failure
does not distinguish plateau from insufficient depth. The 45% gate-pass
estimate is a planning judgment; the proposed intervals may leave small
effects unresolved. Midpoint and selected-subset diagnostics characterize
these ambiguities without changing outcome rows.

## Critique disposition and verification

Address critique notes 1–5 through the fixed budget, survivor-only accounting,
restricted interpretations, subset semantics, baseline comparison, and F2
reserve above. Notes 6–9 concern existing belief files outside this role's
write scope: do not edit them. Do not propagate equality/no-learning claims;
prior estimates were unresolved, operator survival proportions were observed
0.22–0.27, and final residuals had measured |cos| <=0.105.

Inspect existing schemas and queue format, implement minimal extensions, and
test counts, seed separation, midpoint retention, diagnostic parent identity,
baseline equality excluding timing, gate boundaries, outcome ordering,
deadline admission, and fresh reserve. Run a real small-scale Rust-backed
smoke against saved maps and compare a small prior baseline subset. Measure
learn/fresh throughput using representative full-cap searches. If measured
runtime/rates or infrastructure make the approved design infeasible, write
infeasible.md with measured numbers and alternatives, commit, and stop.
Otherwise write the full queue with ten workers, task-prefixed entry IDs,
RUN_DIR outputs and realistic timeout; validate the queue without running
the full experiment. Commit implementation and task artifacts on the task
branch and leave the worktree clean.

## Post-smoke feasibility record

The representative full-cap probe supports the approved design: 3,072 learn
searches at 96.03% solves, 300 fresh at 99.67%, 121.49/20.77 seconds wall,
projecting 235.4 minutes for the full queue. An earlier calibration-start
probe was slower; both measurements and their sampling difference are
recorded in [smoke.md](smoke.md). Keep the original 297-minute planning
estimate and the approved admission reserves, since later learned maps can
change runtime. The final reduced smoke and 21 targeted tests passed; the
full queue was validated and not run. Scientific conditions and outcomes
above were fixed before execution and remain unchanged.
