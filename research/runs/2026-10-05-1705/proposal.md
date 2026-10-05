---
node: questions/01-map-bias/08-evolve-bias
title: Does a fitted op-frequency bias speed evolution on held-out sum>2 / max>2? (uniform vs matched vs mismatched vs hand-set scaffold; time-to-exact-solve, two looks)
---

**Why this now.** Run [2026-10-05-1558](../2026-10-05-1558/analysis.md) returned sampling
verdict A. A fitted vector raised held-out sum>2 (max>2) P(exact) 4.9× (8.9×) over uniform
and 4.8× (6.7×) over the other family's fit. Its plan pre-registered the next step for A: test
evolution on the holdouts, which separates A (the bias helps search) from B (it changes supply,
not success; item 12 predicts B). This is a revision of
[1700](../2026-10-05-1700/proposal.md). It takes all three of the critic's points: the
hand-set vector is rebuilt so its constants really are uniform, the endpoint and the
"no difference" margin are fixed before any data, and the harness keeps going after shortcuts.
08 has 2 experiments left; this uses 1.

**Arms.** Four vectors per task, with sum>2 and max>2 on length-4 lists over [0,9]. All are
frozen from 1558's `result.json` (`vectors`), and the researcher writes them into the plan as
22 numbers each.

| Arm | Vector |
|---|---|
| uniform | 1/22 each |
| matched | the selected fit for the task's family |
| mismatched | the other family's selected fit |
| hand-set scaffold | INPUT, GT and the family aggregators (SUM + REDUCE_ADD, or REDUCE_MAX) at the matched fit's *probabilities*; CONST_0/1/2/5 fixed at 1/22; the remaining mass spread over the other ops in proportion to uniform |

I checked that the hand-set vectors are feasible. For Σ, INPUT is 2.86× uniform, GT 3.23×,
SUM 1.96× and REDUCE_ADD 1.73×; the 13 other ops drop to 0.59× uniform. For M, INPUT is
2.60×, GT 2.97× and REDUCE_MAX 2.84×; the others drop to 0.64×. A hand-set win shows only
that a simple manual scaffold bias is enough. It does not isolate any one op's effect on
evolution, and I will word it that way.

**Sampling check (descriptive, does not gate anything).** 125M tapes per hand-set vector with
the 1558 sampler, about 10 minutes in total. The four-op product model, applied to the
vector actually specified, predicts about **17×** over uniform on sum>2
(2.86 × 3.23 × mean(1.96, 1.73) × 1.0) and about **22×** on max>2 (2.60 × 2.97 × 2.84 × 1.0).
The model ignores the 0.6× dilution of the other ops, so this is a real out-of-sample test of
it. These hit rates also feed the random-search baseline below.

**Evolution harness.** Use the standard tagged setup: lexicase, crossover v2, mutation 0.015,
L 64, and 64 label-balanced training cases. Initial genomes and mutations are drawn from the
arm's `op_probs`. Every training-perfect candidate is checked against all 10,000 lists, from
generation 0 on. Early termination on training fitness 1 is disabled
(`disable_early_termination` or equivalent), so shortcut populations keep running. A run
stops only on the first exact solve or at the cap.

**Primary endpoint, fixed now.** *Evaluations to first exact solve*: the candidates evaluated
up to and including the solver, counted at candidate level, so generation 0 and the position
within a generation count. It is right-censored at the cap. The effect is the time ratio
between two arms (uniform ÷ matched etc.). The plan fixes the estimator before data: the
Kaplan–Meier median ratio with bootstrap CI, or a log-normal AFT fit. Solve rate at the cap is
secondary. I fix this now and will not switch it after seeing a ceiling.

- **Smallest worthwhile effect: 2× in evaluations to solve.** The sampling lift is 5–9×, so a
  speed-up below 2× would mean evolution passes on little of the supply gain.
- **Six comparisons**, three per family: matched vs uniform, matched vs mismatched, and
  hand-set vs matched. They use family-wise α = 0.05, split Bonferroni across the 6 and across
  2 looks (two-sided z ≈ 2.87).
- **"Faster"** = lower bound > 1 and point ≥ 2. **"No difference that matters"** = the whole
  CI inside (0.5, 2). Anything else is unresolved.

**Pilot (disjoint seeds, not analysed).** Uniform and hand-set (the predicted fastest), 10
seeds each per task, at two or three population sizes. The rule, frozen now: per task, choose
one population size and one cap, shared by all arms, so that uniform solves ≥ 80% of pilot
runs by the cap. Among the sizes that pass, take the one where hand-set's median solve is
latest (time resolution). If none reaches 80%, take the largest size that fits the time
budget, and expect more censoring. The pilot also measures seconds per run, which sets the
timeouts.

**Sample size, two looks (frozen rule).**
- Look 1: 50 seeds per cell (8 cells, 400 runs). Comparisons that are resolved at look 1
  stop there.
- Look 2: if any of the six is unresolved, add 50 more seeds to the cells involved, up to
  100 per cell.
- Rough power: with about 100 solves per arm, SE(log ratio) ≈ 0.14. A true ratio near 1 then
  resolves as "no difference" (CI inside 0.5–2), and a true 5× resolves as "faster" at look 1.
- If the pilot timing says look 2 cannot fit, the queue runs look 1 only and the experiment
  becomes a large-effect screen. The plan must say so before the queue.
- Pilot + sampling + both looks must fit within the 8 h `max_queue_hours`. My guess is 2–4 h,
  since the uniform random-search horizon is about 1M evaluations (≈ 1000 generations at pop
  1024), and evolution should be faster.

**Free baseline.** Random search on the same evaluation axis: P(solved by N) = 1 − (1 − p)^N,
for each arm's p from sampling (1558 counts; the new 125M for hand-set). The CI on p is
carried through, and the full curve is drawn over the KM curves. Two descriptive numbers per
arm: evolution's speed-up over random search, and its *pass-through*, i.e. its speed-up over
uniform divided by the sampling lift. Neither identifies a search mechanism. Both link to §28
("evolution is mostly a worse sampler").

**What each outcome means.**
- **A**: matched is faster than both uniform and mismatched, in both families. The fitted bias
  speeds evolution on unseen members, beyond a generic speed-up. That answers 08's practical
  question, even if supply explains all of it; pass-through says how much. Close 08.
  - If, in addition, hand-set vs matched is "no difference" or hand-set is faster, record
    **A'**: "yes, and a hand-set INPUT/GT/aggregator scaffold does as well".
  - A heritable-bias follow-up goes to the strategist.
- **B**: matched vs uniform is "no difference" in both families, despite the 5–9× supply.
  Frequency bias matters to sampling but not to evolution's speed on these tasks. Park the
  frequency-only version of 08 (its stop rule).
- **Partial**: one family only, or faster than uniform but not than mismatched. Report it as
  such. Most likely it is a generic speed-up, not family transfer; 08 then goes to strategy
  with its last slot unspent.
- **Unresolved after the last look**, or a large-effect screen that saw no large effect: this
  says nothing about A vs B. Go to `next: strategy`. Do **not** park frequencies as
  ineffective on this evidence.

**Prior.** A on speed, probably with low pass-through (2–4× of a 5–9× lift). A' is likely,
because the fits suppress CONST_2. I put about 30% on B.

**Scope.** Two holdouts that differ from their fit members only in a constant. One fitted
vector per family (M from one trajectory). TAG alphabet, L 64, one evolution setup. Nothing
about heritable or co-evolving bias.

**Alternatives considered.**
- *Keep 50 seeds and solve rate at the cap as primary* (1700's design). This was rejected:
  half-widths of about 20 points cannot support B or equivalence, and choosing the endpoint
  after the pilot invites post-hoc switching.
- *Drop the mismatched arm.* Without it, a win could not be told apart from a generic
  speed-up. The 1558 specificity result is about sampling only.
- *A second M fit trajectory, or a harder fit.* Either refines the sampling result and decides
  nothing for 08.
- *`next: strategy` now.* Premature: this is the pre-registered next step, and the critic
  agreed it is the right experiment.
- **Parked questions:** none reopens. 02 still needs the owner's wish; 07 still has no
  B-helper copy or replay; 04 depends on 07.
