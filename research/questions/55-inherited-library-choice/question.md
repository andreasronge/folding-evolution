---
status: parked
tags: [map-bias, inheritance, self-adaptation, operator-choice, library-learning, linkage, fresh-start]
budget: {experiments: 3, used: 0}
---
# Can program selection favor an inherited choice of a useful structured variation law?

Opened by [strategy 1427](../../runs/2026-10-11-1427/strategy.md), with the
[inherited-library-choice plan](../../plans/inherited-library-choice.md).

Reopened by [strategy 1736](../../runs/2026-10-11-1736/strategy.md) (budget 1 → 2) for one redesigned usefulness test: recurrent bit mutation, f₀ = 1/16, per-population readout ([plan](../../plans/recurrent-inherited-library-choice.md), [proposal 1736](../../runs/2026-10-11-1736/proposal.md)).

Reopened by [strategy 0250](../../runs/2026-10-12-0250/strategy.md) (budget 2 → 3) for one content-choice test: the bit chooses between the saved order and signed-gate libraries at a fixed library rate, exposed on each family ([plan](../../plans/inherited-content-choice.md), [proposal 0250](../../runs/2026-10-12-0250/proposal.md)). Parked again after it.

Summary: **parked after experiment 0250 (commit `4ed0469`): inherited choice between two supplied libraries
moved toward the suited one on order, but its frozen mixtures gave fresh search no saving over the 50/50 start.**
The bit chose order-library or gate-library donors (each on half of mutations; redraw 1/32 toward 1/2, f₀ = 1/2),
exposed for twelve 64-generation episodes on six development cells of `x4-order-v1` or `x4-signed-gate-v1` (24
paired builds × 8 populations; P 256, lexicase, crossover 0.5). Final gate share: order L 0.377 [0.341, 0.413] vs
shuffled 0.485 (L − S −0.108 [−0.163, −0.056]); gate L 0.516 vs 0.484 (+0.032 [−0.029, +0.095], unresolved).
Frozen laws deployed alone: **R (geometric mean of L-matched / 50/50 mix over families) 0.991 [0.926, 1.060]**;
order 0.982 [0.882, 1.093], gate 0.999 [0.928, 1.075]. Pooled savings above about 7% are excluded (pre-set label: "20% pooled saving
excluded"); smaller savings, or a cost up to 6% higher, are not. Headroom was present (own pure library 0.73 and 0.78 of the mix, upper bounds 0.88 and 0.89), and the pure
matched library stays the cheapest law on each family. Endpoint costs follow a dose curve in f; L carried nothing
visible beyond its frequency, and was not resolved cheaper than shuffled or neutral endpoints. Descriptive
mechanism from this run's traces: selection on the bit acts mainly before each episode's first solve (order f fell
to about 0.24), then the redraw toward 1/2 relaxes it for the rest of the episode, and the readout froze the
relaxed value. One exposure rule, mutation rate, population size and pair of supplied libraries; development cells
only; no content learning or transfer. [Analysis](../../runs/2026-10-12-0250/analysis.md),
[decision](../../runs/2026-10-12-0250/decision.md).

Earlier, dose-only selector (1736, commit `3a18ef5`; six order development cells, 24 saved R-all
libraries; content and donor law supplied, never learned). With the child bit
redrawn from Bernoulli(1/16) at rate 1/32, the R-all carrier bit stayed polymorphic and rose from 1/16 to a mean
of 0.29 [0.23, 0.35] in linked populations, against 0.06 neutral-bit and 0.05 shuffled (L − N 0.23 [0.16, 0.30];
24/24 libraries). The rise is bimodal (46/144 above 0.5, 55/144 at or below the start): the observed pre-solve
selection differential was +0.0017 per generation at f ≤ 0.25 and about ten times larger in the high-frequency
stratum (suggesting frequency-dependent dynamics; not an intervention on frequency). Averaged over separate-population
deployments, each population's frozen law, deployed alone at q = f/2, cost **0.805 [0.704, 0.913]** of the starting law (pre-set useful bar: upper
< 0.90, so formally unresolved; the interval excludes 1), and beat the neutral (0.75 [0.64, 0.86]) and shuffled
(0.70 [0.61, 0.80]) endpoints. The law carries nothing beyond its dose: the three arm-average costs were within
about 6% of predictions averaged over their endpoint doses (endpoint-wise accuracy untested), 94/144 linked
endpoints were cheaper than their paired start, and the saving comes from the 43% of populations where the bit rose. Hand-set R-all
(q = 0.5) is 1.71× [1.45, 2.01] cheaper and needs no exposure; exposure repays against q₀ after about 16 searches.
Read: program selection can acquire a cost-lowering frequency of a supplied variation law when selector loss is
reversible, but the acquired dose falls well short of the obvious hand setting. Not shown: whether the saving exceeds 10%; other
mutation rates, population sizes or crossover rates; choice among contents; content learning; transfer.

Earlier probe (1427, commit `f8f4246`; observations only). Without bit mutation and from f₀ = 0.25, the bit
fixed in 46/96 linked trajectories against 27/96 shuffled, 29/96 size-matched random donors and 16/48 neutral
(L − S 0.20 [0.04, 0.35]), but absorbed rapidly (290/336 in the first episode), and the pooled frozen law was
unresolved from the start (0.91 [0.71, 1.20]). Corrections to its first wording are in the [log](log.md).

Root 10 established that the frozen externally acquired R-all donor law lowers
search cost on six order development cells. Root 23 did not establish useful
inherited token frequencies under its tested procedure. This root separates
two problems: discovering useful bias content, and selection propagating a
modifier that controls access to already available content. A global search
advantage need not benefit the modifier's carriers under lineage mixing.

The first candidate (probe 1427) is a binary, per-individual inherited choice between ordinary
mutation donors and the existing half-library R-all law. Start with both states;
no modifier mutation or library learning during the assay. Selection sees only
program performance. After equal fixed task exposure and program resets, freeze
the final modifier frequency as a donor mixture and test it in fresh searches.
Use linked, ancestry-shuffled and neutral-bit controls, plus fixed initial,
ordinary and R-all references. The plan leaves sizes and the formal comparison
to the steward.

This is selection from standing variation over externally acquired operators.
It is not evidence of invented library content, inherited token semantics,
fresh-family transfer or practical superiority to fixed R-all/R-order. The six
order development cells are the scope; protected rosters remain unsearched.

Competing explanations:

- A: The useful law improves descendants enough that persistent program–modifier
  association favors its carriers; its frozen final mixture improves fresh search
  over the starting mixture and the ancestry-shuffled readout.
- B: Useful program material spreads without sufficient advantage to the modifier
  that produced it; global usefulness does not yield useful inherited selection.
- C: Modifier movement reflects finite-population drift or incidental hitchhiking;
  linked dynamics do not distinguish themselves usefully from the controls.
- D: Selection favors a law for the resident population or the maintenance phase,
  but its frequency does not improve fresh search after programs are discarded.
- E: The initial mixture already captures the useful effect, leaving too little
  frozen-readout headroom; or this fixed exposure is too weak to resolve selection.

After 0250 (content choice; details in the [log](log.md)): A not supported; B consistent; C excluded for the
order shift, unresolved on gate; D partly (the readout froze a maintenance-phase balance); E's headroom half
excluded, its weak-exposure half supported for this rule.

Related: [root 10](../10-compositional-map-transfer/question.md),
[order result](../../runs/2026-10-11-1228/analysis.md),
[rectifier probe](../../runs/2026-10-11-1315/analysis.md),
[root 23](../23-heritable-variation-bias/question.md),
[root 01 lineage mixing](../01-map-bias/06-self-mate-establishment/question.md),
[probe 1427](../../runs/2026-10-11-1427/analysis.md), [decision 1427](../../runs/2026-10-11-1427/decision.md),
[experiment 1736](../../runs/2026-10-11-1736/analysis.md), [decision 1736](../../runs/2026-10-11-1736/decision.md),
[recurrent plan](../../plans/recurrent-inherited-library-choice.md),
[experiment 0250](../../runs/2026-10-12-0250/analysis.md), [decision 0250](../../runs/2026-10-12-0250/decision.md),
[content-choice plan](../../plans/inherited-content-choice.md), [root 10 signed-gate libraries](../10-compositional-map-transfer/58-signed-gate-acquisition/question.md), [log](log.md),
[owner note](../../plans/owner-heritable-map.md),
[Stephens et al.](https://pubmed.ncbi.nlm.nih.gov/9847423/),
[Serpell and Smith](https://uwe-repository.worktribe.com/output/975827).

Allocation: one probe (1427) and two experiments (1736, 0250), all used.

Reopen if: a strategist funds an inheritance design whose frozen law is taken where selection acts — e.g. exposure
that stops or freezes at each episode's first solve, exposure only on unsolved cells, or a redraw not aimed at the
starting mixture — with a stage-0 check that the frozen order-family gate share reaches ≤ 0.25 on average at
readout (0250's pre-solve minimum was about 0.24, its endpoint 0.38); or an inherited repertoire with changeable
content (owner note, root 23) needs this calibration of how a selected modifier relaxes under recurrent mutation.
More seeds, a redraw-rate sweep, or a top-up of the 0250 contrast is insufficient: its interval already excludes
savings above about 7%. Reuse the 1736 and 0250 harnesses and rows for descriptive follow-ups.
