# Crossed adaptation on the screened four-reducer bank

Concept-plan addendum for [root 10](../questions/10-compositional-map-transfer/question.md),
chosen by [strategy 1723](../runs/2026-10-06-1723/strategy.md). The steward supplies the
experiment design, sizes and outcome rules. This is not an experiment registration.

The immediate question is whether the training family changes transfer under the successful
token-multiplier learner. It precedes another attempt to learn contextual structure.
[Run 1603](../runs/2026-10-06-1603/analysis.md) rejected the symmetric split, but established
usable search rates and a smaller covered split. Use that evidence without reclassifying
the failed study as successful.

**Bank and changed scope.** Retain D1331, `v2_rmin_first`, the reviewed executor, G4 and
the exact screened roster from 1603's artifacts. S/M/m/F mean SUM/MAX/MIN/FIRST. BE is
`A>0 ? B : (C+D)`; PA is `(A>0 ? B : C)+D`.

- BE: hold out `S?m:(M+F)`; train on the other four retained cells.
- PA: hold out `(F?S:M)+m` and `(S?M:m)+F`; train on the other six retained cells.

Only the number of BE holdouts changes from the earlier plan. Preserve the ≤9-token,
80%-agreement alias screen, role coverage, full-domain exact checks and 4,096-evaluation
headroom reference. Recover exact cell IDs and table hashes from the artifacts. No new
screen or domain sweep is needed. Verify that no training target is identical to any
holdout in either family, and exclude all three holdout scores from adaptation.

This split was chosen after seeing baseline and hand-set grammar results. Freeze it before
learning and describe it as transfer on a screened bank. Repeated learning can strengthen
the evidence about these three tasks; it cannot create additional BE task replication.
Training sets also differ in size and role distribution. The eventual claim concerns these
specified training sets, not an isolated causal effect of expression shape alone.

**What to build.** Reuse the reviewed four-reducer search and decoder-adaptation code on
`research/main`. Run separate outer populations of G4-based token multipliers for BE and
PA, with identical initial G4, token support, parameterization and learning procedure.
Use independent random learning trajectories, paired across families where useful; extra
continuations of one evolved map do not count as new starts. No family grammar seeds,
canonical programs, old solvers or task identity enter the learned decoder.

Equalize total inner-search evaluation allocation per candidate and total outer effort
between families; balance task exposure within each family despite four versus six tasks.
Report actual evaluated-program counts and wall time as well. Transfer only frozen decoder
parameters, initializing each program population afresh. Save all final maps by a rule
fixed from training data, without holdout-based checkpoint or trajectory selection.

**First experiment and continuation.** The first balanced learning stage should measure
candidate-scoring repeatability on training tasks, fresh-training improvement and actual
cost for perturbed maps. Aggregate operator acceptance near 25% is not a ranking test.
Use independent rescoring on training tasks to assess whether selected candidates improve.
Combine calibration with substantive learning where affordable; avoid a tiny standalone
pilot that only reconfirms G4's known solve rates.

A useful scheduling candidate is three balanced batches, each with two trajectories per
family, giving six per family. This is a runtime sketch, not a justified final sample size.
1603 estimates 35–70 minutes per 25-generation trajectory on ten workers: each batch's
learning is about 2.3–4.7 hours, and all twelve about 7–14 hours. Measure scoring and reporting
overhead too. Keep queues ≤8 hours and project the complete study within about 18 compute
hours, leaving the remaining autonomous time for agent work.

After the first batch, use training-only variance and runtime to fix an affordable final
size and a decision-relevant effect before examining learned-map holdout results. Return
to strategy if training feasibility or precision is inadequate. A noisy small pilot is
not evidence that no affordable learning study exists. If the procedure changes, treat
old maps as pilot data rather than pooling different learners as one replicate set.
Reserved follow-up slots are an allocation, not a requirement to run an uninformative stage.

**Evaluation and answers.** Score every frozen map from both training families on the same
fresh search seeds for all three holdouts, plus fresh training evaluations and frozen G4.
Use adaptation trajectories as the independent unit for learning uncertainty; retain each
holdout's result rather than hiding opposite effects in a pooled average. The steward
should choose one capped-search-cost effect, a practical magnitude and 95% intervals with
an explicit unresolved outcome. Fix the final evaluation rule before holdout inspection.

A useful matched-over-mismatched advantage in both directions, with improvement over G4,
supports training-family-dependent transfer on these compositions. An advantage confined
to one direction is partial evidence. A crossed preference caused only by degradation
still shows dependence on training history, but does not establish useful improvement in
both families. Similar gains under both training sets support a generic component only
to the intervals' resolution; wide intervals do not establish equality. Fresh training
gains without holdout gains limit transfer. No fresh training gain limits this learner
and budget, not the existence of learnable family structure.

No outcome establishes learned contextual preferences: G4's context remains supplied.
The hand-set family grammars are already a capacity witness, not learned baselines that
need another full sweep. Solver-frequency measurements are optional supporting evidence;
they must not displace independent trajectories or be mistaken for a supply/variation
mechanism test. Report adaptation cost separately from search savings. Return to strategy
after the crossed result before funding context, a new bank or a mechanism study.
