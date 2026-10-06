# Learn on the surviving post-addition family

Concept-plan addendum for [root 10](../questions/10-compositional-map-transfer/question.md),
chosen by [strategy 0132](../runs/2026-10-06-0132/strategy.md). This is not an experiment
registration. It replaces the immediate two-family requirement in the
[assembly-family plan](compositional-family-headroom.md); the broader
[transfer plan](compositional-map-transfer.md) remains the longer-term question.

The first question is whether evolving decoder parameters on several related tasks
improves fresh search on withheld operation combinations beyond the supplied grammar and
token-frequency tuning. A positive would establish transfer within this screened family.
It would not distinguish family-specific learning from improved generic syntax.

## Reuse the measured bank

Use the eight retained post-addition (PA) tasks on D1331: length-three lists over integers
−5 through 5, all 1,331 inputs. S, M and m denote sum, maximum and minimum; `S?X:Y`
means `S > 0 ? X : Y`. Use the split already identified by
[0001](../runs/2026-10-06-0001/analysis.md): six training tasks, with
`PA:(S?M:S)+M` and `PA:(S?M:S)+m` withheld. Recover the exact roster, split and frozen maps
from that run's artifacts, not by reconstructing them from prose.

All eight passed the frozen ≤9-token, 80%-agreement alias screen on D1331. The holdouts
had G medians of 13,568 and 18,688 evaluations at the 524,288 cap, compared with uniform
medians 83,968 and 148,480. Uniform solved 46/50 and 43/50; G solved 49/50 and 48/50.
G-start searches reached at least 25/50 solves by 65,536 evaluations on every retained
cell in the wider bank. Those observations justify measuring outer learning. They do not
prove that nearby decoder mutations improve training or that learning will transfer.

These tasks were selected after baseline screening. Describe subsequent evaluation as
fresh-seed transfer on a screened bank, not a wholly untouched benchmark. Freeze the split
before adaptation. No holdout scores may select maps, hyperparameters, checkpoints or
stopping times. Keep canonical programs solely as evaluator checks; never seed searches
or derive learned parameters from them. Verify claimed solvers on the complete domain.

## What to build

Reuse `assembly_bank.py`, `composition_search.py` and the frozen U/F/G/G-marg maps on
`research/main` (completed study at `a65ded0`). Keep `v2_rmin`, executor semantics, latent
genome length and variation fixed. Do not port the TAG harness or alter the alphabet.

Add a small outer population of heritable decoder tables, selected and mutated using
capped costs of freshly initialized searches across the six training tasks. Start from
G to exploit measured tractability. Preserve token support and regularize table changes;
the steward chooses the small parameterization and optimization budget. Score candidates
on comparable training-search seeds and check selected maps on fresh training seeds so
selection cannot merely memorize one noisy search. Save each independent trajectory and
its complete evaluation cost. No program genome, task identity or prior solver transfers
to the held-out search. This tests evolution of map parameters in an outer population,
not simultaneous coevolution of maps and programs.

Keep comparisons interpretable:

- Frozen G is the primary supplied-prior benchmark; U and F retain baseline context.
- Adapt an independent-token map with a comparable training budget. Also include a
  restricted G-based control that can tune global token multipliers while retaining G's
  contextual template. This shares the starting grammar advantage and asks whether
  learning new contextual preferences adds anything beyond retuning token weights on G.
  The restricted control is not itself a context-free map; label it accurately.
- Remove context from each learned map using its empirically measured emitted token
  marginals. Check marginal agreement under the actual genotype prior. This addresses
  final token composition, but does not by itself separate sampling from mutation effects.

The proposal should prioritize these contrasts rather than expand into an operator sweep.
Do not substitute linear-task training for a matched other-family control: those tasks
lack IF_GT. Do not claim specificity from beating frozen G or its marginals. Starting at G
and ending near it is not evidence of learned improvement simply because G beats U.

## First experiment and follow-up

Calibrate the outer objective on training tasks only: cost of evaluating candidate maps,
variation in training performance, fresh-seed repeatability and end-to-end runtime.
Use the measured G search curves as a starting estimate, not a guarantee for perturbed
maps. Project the whole study, including independent adaptation trajectories, restricted
and token-only adaptation, marginal estimation and held-out searches. A short calibration
should gate the main study within the same approved queue when feasible; avoid a separate
tiny experiment merely to reconfirm known PA solve rates. Queues remain ≤8 hours.

If affordable, freeze the training procedure and evaluate independently adapted maps on
both holdouts with fresh program populations. Include fresh-training-task evaluation to
distinguish failure to learn from failure to transfer. Choose one practical speed effect,
a fixed size supported by measured variability, a 95% interval and a consistent treatment
of unsolved searches. Map trajectories are the independent evidence about learning;
inner-search seeds estimate each map's performance. Do not replace trajectory replication
with thousands of seeds for one selected map.

Measure held-out random-genotype behaviour frequencies as supporting evidence, with a
bounded sampling budget. Sparse counts yield bounds and need not veto an interpretable
search comparison. Record adaptation evaluations and wall time separately from transfer
cost; estimate amortization across future tasks only when there is a measured saving.

Return to strategy after this result. A second slot can replicate adaptation on new seeds
or resolve an informative interval. There are no additional reserved PA cells under the
six/two split: a rotated split would be a separately frozen replication within the same
screened bank, not new task-family evidence. A genuinely new-family replication requires
its own plan and feasibility evidence.

## What would count as an answer

An advantage on both held-out compositions across independent map trajectories, beyond G,
frequency-only adaptation and the G-based restricted control, would support transferable
learned contextual preferences in this family. Beating learned marginals would show that
final token frequencies alone do not reproduce performance. Neither result would identify
the causal contribution of supply versus mutational neighbourhoods, or establish family
specificity, or generalize to folding and CA maps.

Training improvement without held-out improvement supports overfitting at this budget.
G-based token tuning matching the full learner would leave new contextual preferences
unnecessary here, within the interval's resolution. A learner that fails to improve even
on fresh training searches diagnoses the tested adaptation procedure, not transfer.
Broad intervals remain unresolved. A bounded failure should return its measured obstacle
to strategy; it should not trigger an automatic alphabet expansion or program stop.
