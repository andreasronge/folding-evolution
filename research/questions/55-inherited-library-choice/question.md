---
status: parked
tags: [map-bias, inheritance, self-adaptation, operator-choice, library-learning, linkage, fresh-start]
budget: {experiments: 2, used: 0}
---
# Can program selection favor an inherited choice of a useful structured variation law?

Opened by [strategy 1427](../../runs/2026-10-11-1427/strategy.md), with the
[inherited-library-choice plan](../../plans/inherited-library-choice.md).

Reopened by [strategy 1736](../../runs/2026-10-11-1736/strategy.md) (budget 1 → 2) for one redesigned usefulness test: recurrent bit mutation, f₀ = 1/16, per-population readout ([plan](../../plans/recurrent-inherited-library-choice.md), [proposal 1736](../../runs/2026-10-11-1736/proposal.md)).

Summary: **parked after experiment 1736 (commit `3a18ef5`; six order development cells, 24 saved R-all
libraries, P 256, lexicase, crossover 0.5; content and donor law supplied, never learned).** With the child bit
redrawn from Bernoulli(1/16) at rate 1/32, the R-all carrier bit stayed polymorphic and rose from 1/16 to a mean
of 0.29 [0.23, 0.35] in linked populations, against 0.06 neutral-bit and 0.05 shuffled (L − N 0.23 [0.16, 0.30];
24/24 libraries). The rise is bimodal (46/144 above 0.5, 55/144 at or below the start): selection is weak while the
bit is rare (+0.0017 per generation at f ≤ 0.25) and about ten times stronger once it is common. Each population's
frozen law, deployed alone at q = f/2, cost **0.805 [0.704, 0.913]** of the starting law (pre-set useful bar: upper
< 0.90, so formally unresolved; the interval excludes 1), and beat the neutral (0.75 [0.64, 0.86]) and shuffled
(0.70 [0.61, 0.80]) endpoints. The law carries nothing beyond its dose: every endpoint's cost sits within 6% of the
dose curve at its own q, and the saving comes from the 43% of populations where the bit rose. Hand-set R-all
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

Related: [root 10](../10-compositional-map-transfer/question.md),
[order result](../../runs/2026-10-11-1228/analysis.md),
[rectifier probe](../../runs/2026-10-11-1315/analysis.md),
[root 23](../23-heritable-variation-bias/question.md),
[root 01 lineage mixing](../01-map-bias/06-self-mate-establishment/question.md),
[probe 1427](../../runs/2026-10-11-1427/analysis.md), [decision 1427](../../runs/2026-10-11-1427/decision.md),
[experiment 1736](../../runs/2026-10-11-1736/analysis.md), [decision 1736](../../runs/2026-10-11-1736/decision.md),
[recurrent plan](../../plans/recurrent-inherited-library-choice.md), [log](log.md),
[owner note](../../plans/owner-heritable-map.md),
[Stephens et al.](https://pubmed.ncbi.nlm.nih.gov/9847423/),
[Serpell and Smith](https://uwe-repository.worktribe.com/output/975827).

Allocation: one probe (1427) and one experiment (1736), both used.

Reopen if: a strategist decision needs to know whether this procedure clears a 10% saving (price: a second batch of
six populations per library, about 432 trajectories + 8,640 readout jobs, ~70 min queue, ~4 h complete; resampling
the 1736 rows suggests that only just reaches an upper bound of 0.90 if the point holds); an inherited-choice
design where the chosen law carries more than a dose (e.g. choice between intact R-all and helper-scrambled R-hx at
equal mix, or among several libraries) is funded, which can reuse the 1736 harness and its controls; or a later
inherited-content study (root 23 or the owner's heritable-map note) needs this calibration of low-frequency
selection under crossover. More seeds of the same dose-only selector, a mutation-rate sweep or available compute
is insufficient.
