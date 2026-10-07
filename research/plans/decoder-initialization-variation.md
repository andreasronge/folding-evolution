# Where the learned decoder's transferable gain enters search

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md), selected
by [strategy 2331](../runs/2026-10-06-2331/strategy.md). This is not an experiment
registration. The steward chooses sizes, primary contrasts and outcome rules.

The token maps from [1723](../runs/2026-10-06-1723/analysis.md) improve search on the three
targets in [2229](../runs/2026-10-06-2229/analysis.md) about 2–3× regardless of training
family. Each map changes both the distribution of initial programs and what ordinary
allele mutation and crossover produce thereafter. Separate those two uses before trying
to explain the gain with exact-solver frequency or newly learned assembly rules.

**What to build.** Extend the reviewed `composition_search.py` harness on `research/main`
to accept an initial decoded population independently of the decoder retained during
search. Reuse the 20 saved tables, provenance and hash checks in
`experiments/chem_tape/data/crossed_1723/` and the 2229 evaluation code. Keep G4, D1331,
`v2_rmin_first`, program length, selection, mutation, crossover and exact verification
unchanged. No task identities, canonical solutions or old evolved programs enter search.

Let G denote G4 and M one frozen learned map. The concept is a crossed comparison:

| Initial program source | Decoder during search | Interpretation |
|---|---|---|
| G | G | Original fixed baseline |
| M | G | Learned initial distribution only |
| G | M | Learned ongoing decoder only |
| M | M | Original learned-map treatment |

For a fixed source and search seed, both ongoing-decoder arms must start with exactly the
same ordered token tapes, including inactive tokens, and hence the same outputs and
training scores. Decode uniformly sampled source alleles once, then represent those
token tapes under the destination decoder. Its integer cumulative table gives an interval
of alleles for each next token conditional on the previous token (or start row). Draw
uniformly within that interval, independently by position and individual. Every interval
must have positive width. This preserves the token sequence exactly; a midpoint encoding
would change the latent distribution and is not an adequate control.

The inspected decoder requires strictly positive token counts in every row. Thus inverse
encoding is structurally available for these tables, subject to artifact validation.
With identical source and destination, conditional-uniform re-encoding has the same law
as original uniform initialization: the probability of each token sequence times its
conditional allele probabilities recovers the uniform allele prior. Preserve that law,
including correlations induced by sequential decoding. Keep encoding randomness separate
from cases, selection and variation streams. Do not repeatedly re-encode elites or
offspring: only initialization changes; later generations use the original search code.

Changing the table on unchanged alleles is unsuitable because it changes the starting
programs. Rewriting only active tokens is also unsuitable because inactive tokens can
matter after crossover or mutation. These are the critical validity checks, not a new
search algorithm.

**First experiment.** Validate exact decode/encode round trips for all source/destination
tables, initial-population equality between the relevant paired arms, and recovery of
the original G/G and M/M baseline laws and search behaviour. A source=destination path
using original alleles can provide an implementation reference. Measure inverse-encoding
overhead and mixed-arm search cost on a small, explicitly designated calibration batch.
Keep pilot handling separate from the main fixed comparison as appropriate; do not use
the most favourable pilot effect to choose maps or targets.

Then run the substantive comparison on all three 2229 targets, retaining all 20 maps.
The old holdout results motivated this experiment, so this is a mechanistic follow-up
with fresh search seeds, not a new untouched transfer test. The two training families
remain labelled; do not select one winning trajectory or average their tables into a
single supposed representative map. Learning trajectories are the unit for uncertainty
across adapted maps. Shared G/G rows and common search seeds create dependence that the
analysis must retain rather than count as independent baseline replications.

Use a consistent capped-search-cost measure, exact full-domain solving, and 95% intervals.
Choose a practical effect and sample size from the saved search variability plus measured
mixed-arm runtime. Show the ongoing-decoder effect at each initialization and the
initialization effect under each ongoing decoder; an interaction can make a pooled main
effect misleading. Also show each target. Select a small primary set of comparisons and
include an unresolved outcome rather than building a large gate system.

2229's 25,200 searches took 35 min on the existing setup. That supports feasibility of
scoring frozen maps, but is not a runtime measurement for the mixed arms. A calibration
can gate the larger stage in one queue. No new outer learning or rare-solver sampling is
required. Keep queues ≤8 h, aim to complete this study and its conditional follow-up in
≤12 h of compute, and reserve the rest of the autonomous window for reviews and analysis.

**What would count as an answer.** If M/G retains most of the M/M benefit with a suitably
tight bound on the increment from ongoing M, the learned initial distribution suffices
at this resolution. If G/M improves on G/G while M/G contributes little at useful bounds,
ongoing decoder use carries the benefit. Benefits in both interventions or a resolved
interaction support a combined account. Wide intervals leave the corresponding question
unresolved. Failure to reproduce the diagonal benefit or preserve initial populations
requires resolving that discrepancy before assigning a mechanism.

An ongoing effect includes mutation, crossover, inherited latent alleles and continuing
program supply under selection. It does not isolate mutation alone, match exact-solver
frequencies, or prove a neighbourhood advantage beyond sampling. An initialization effect
includes useful partial programs, not just initial exact solvers. Nothing here shows new
context was learned or that the gain is family-specific.

**Follow-up allocation.** Root slot 10 is for the same frozen intervention on the ten
already scored training cells, testing whether the initial/ongoing pattern extends beyond
the three transfer targets. It is coverage within this screened bank, not new task-family
or map-learning replication. If the first result is infeasible or leaves no useful bounded
comparison, return to strategy with measured costs and uncertainty before spending that
slot. Do not substitute an operator sweep, another token-learning run or a new bank.
