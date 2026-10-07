# Can selection learn useful context beyond token tuning?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md), selected
by [strategy 0803](../runs/2026-10-07-0803/strategy.md). This is not an experiment registration.
The steward chooses the proposal, sizes and outcome rules.

**Question.** Can a compact contextual learner improve fresh search beyond equally funded
token tuning, and does any improvement transfer with a preference for its training family?
The immediate question is training feasibility. Do not spend another full contextual run
without measuring whether selection can distinguish the proposed changes.

**Why this attempt differs.** [0132](../runs/2026-10-06-0132/analysis.md) changed three of
552 weights at a time; [0811](../runs/2026-10-06-0811/analysis.md) changed whole rows, but
neither established an increment over token learning on fresh training searches. In
[1723](../runs/2026-10-06-1723/analysis.md), 24-search scores ranked parents inconsistently,
while the larger final-selection scores better predicted fresh performance. These facts
motivate a compact parameterization and better measured selection, but do not establish
score noise as the cause of the earlier results. This is a new learning procedure, not a
causal test of that explanation.

**What to build.** Extend the reviewed decoder and adaptation code on `research/main`:
`composition_search.py`, `contextual_learning.py`, and `crossed_learning_run.py`. Those
files are not in the current `main` checkout; use their existing implementation rather
than recreating the harness. Keep G4, D1331, `v2_rmin_first`, exact verification, inner
search operators and the [1723 split](asymmetric-family-transfer.md) fixed. No new
alphabet, domain, screen or family grammar is needed.

Use G4 plus global token multipliers as the restricted control. The contextual arm adds
one compact interaction between previous-token row and next-token column. A concrete
candidate is a centered rank-one log-weight residual, with roughly 25 + 24 parameters
instead of 600 free table entries. Center the factors so a residual cannot simply become
another global token multiplier; initialize one factor randomly and the other at zero
so the initial table is exactly G4 while context mutations can move it. Fix bounds,
mutation scales and the representation before substantive scoring. This is a candidate
architecture, not a claim that rank one suffices.

Both arms start at the same G4 table, may tune token weights, and receive comparable
total inner-evaluation budgets and the same scoring procedure. Independent outer
trajectories supply learning replication. No canonical solution, hand-set BE/PA grammar,
previous solver, task identity or holdout score determines learned parameters. A compact
representation chosen from token-table structure is allowed; encoding the known winning
family grammars as its search directions would answer a different question.

**First experiment: selection and training feasibility.** On the ten training cells only,
measure paired candidate-minus-parent score repeatability for both token and context
mutations, including rescoring the selected candidates on independent search seeds.
Use a fixed, bounded comparison of scoring effort, not an open-ended optimizer sweep.
The useful observation is whether selected changes improve on fresh searches; acceptance
fractions or correlation among four nearly tied parents alone cannot decide feasibility.
Record actual evaluations and time, including slower perturbed maps and final evaluation.

Combine calibration with independently replicated contextual-versus-token learning on
BE and PA where the measured cost permits. Freeze the chosen procedure after calibration;
do not count calibration trajectories as independent confirmation of that choice. Compare
fresh-training search costs across paired learning trajectories, including a residual-off
readout of contextual maps if affordable. Beating G4 alone is insufficient: token learning
already does that. A result in only one family is useful partial evidence, not a reason
to erase that family or silently change the split.

Aim for at most four hours of queue time in this first slot. The old token learner took
10–14 minutes per trajectory; the new scoring effort and contextual mutations have no
measured runtime. Project the complete continuation from the calibration, including
independent trajectories and evaluation. Choose a practical increment and interval width
that can change the decision. If they cannot fit, report the measured limit to strategy;
a few noisy trajectories cannot exclude learnable context.

**Conditional second experiment.** If the first study produces a usable procedure and
credible fresh-training improvement beyond token tuning, freeze it and test transfer.
Add independent learning trajectories if required by the measured between-trajectory
spread, then score both training families' frozen maps on all three existing withheld
cells with fresh populations and seeds. Include the equally funded token controls and
G4. To attribute a gain to context, compare to residual removal and, where feasible, a
G4-based token-only map fitted to the learned map's emitted token marginals. Validate
the marginal match; residual removal alone can change those marginals too.

These targets have been examined repeatedly. They remain excluded from new adaptation
and tuning, but this is transfer on a reused screened bank, not a pristine benchmark.
One BE cell cannot establish generality across BE tasks. Preserve map-trajectory
uncertainty and the per-cell results; more inner-search seeds cannot replace learning
replication. Estimate contextual-over-token gain and matched-over-mismatched transfer
separately. The latter must not be inferred from the former.

Aim for at most five additional queue hours, leaving roughly five of the current fourteen
hours for implementation, review, analysis and contingency. Each queue remains at most
eight hours. Recompute against the actual deadline before admitting a later stage. If
the first result is promising but unresolved, a properly sized training resolution may
use the second slot instead, provided its measured cost fits and it could change the
decision. Return to strategy if neither continuation is informative and affordable.

**Answers.** A fresh-training increment establishes accessible improvement for this
procedure; transfer beyond the token and marginal controls supports newly learned context
on these compositions. A useful crossed preference supports dependence on the specified
training families; generic context gains would still answer part of root 10. A preference
created only by harming the other family is not useful improvement in both directions.
Training improvement without transfer limits generalization. Tight small-effect bounds
limit this procedure and budget; wide intervals remain unresolved. None of these outcomes
isolates supply from neighbourhood structure or generalizes to folding or CA development.
