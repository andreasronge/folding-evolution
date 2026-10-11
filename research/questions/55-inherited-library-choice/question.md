---
status: parked
tags: [map-bias, inheritance, self-adaptation, operator-choice, library-learning, linkage, fresh-start]
budget: {experiments: 1, used: 0}
---
# Can program selection favor an inherited choice of a useful structured variation law?

Opened by [strategy 1427](../../runs/2026-10-11-1427/strategy.md), with the
[inherited-library-choice plan](../../plans/inherited-library-choice.md).

Current summary: **parked after probe 1427 (commit `f8f4246`; observations only, six order development
cells, 24 saved R-all libraries, protected cells unsearched).** A recipient-inherited bit switching
mutation donors to R-all, starting at f₀ = 0.25 with no bit mutation, fixed in 46/96 linked trajectories
against 27/96 shuffled, 29/96 with size-matched random donors and 16/48 neutral: L − S 0.20 [0.04, 0.35],
L − Z 0.18 [0.05, 0.30] (library bootstrap). The carriers' per-generation advantage among selected parents
was small (about 4% relative, pre-solve, L only), and drift decided every trajectory, almost all within
about 15 generations of the first episode, so 11 of 12 planned episodes measured nothing. The frozen
mean law was not resolved from the starting mixture (L-final / initial 0.91 [0.71, 1.20]; ceiling about
0.73× if every run had fixed) and is not better than fixed R-all (1.21× [0.98, 1.46]). In the episode where
selection acted, linked and shuffled populations solved equally often (55/96 each). Because each population
ends at 0 or 0.5 and the dose curve is convex, deploying one population's law would be expected, on the
pooled curve, to cost about 1.2× the starting mixture (steward arithmetic, no interval). Read: selection
can favour carriers of a useful donor law here, but too weakly against drift for the inherited choice to show a
resolved fresh-search gain at this population size and exposure (unresolved, not shown absent). Not shown: anything under bit mutation, other population
sizes or crossover rates, other libraries or banks, or on protected cells.

Root 10 established that the frozen externally acquired R-all donor law lowers
search cost on six order development cells. Root 23 did not establish useful
inherited token frequencies under its tested procedure. This root separates
two problems: discovering useful bias content, and selection propagating a
modifier that controls access to already available content. A global search
advantage need not benefit the modifier's carriers under lineage mixing.

The first candidate is a binary, per-individual inherited choice between ordinary
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
[probe 1427](../../runs/2026-10-11-1427/analysis.md), [decision 1427](../../runs/2026-10-11-1427/decision.md), [log](log.md),
[owner note](../../plans/owner-heritable-map.md),
[Stephens et al.](https://pubmed.ncbi.nlm.nih.gov/9847423/),
[Serpell and Smith](https://uwe-repository.worktribe.com/output/975827).

Allocation: one probe, used (1427). The conditional 6–8 h confirmation in the plan was not proposed:
it would confirm allele movement, which strategy 1427 said is not a useful answer by itself.

Reopen if: the strategist funds a redesigned usefulness test whose instrument keeps the modifier
polymorphic long enough to matter (e.g. bit mutation with a measured mutation–selection balance, or a
population/selection regime where a pilot shows absorption well beyond one episode) and starts where a
measured dose curve shows headroom (in 1427 most of the saving came between probability 0 and 0.125); a
different already validated variation law offers a selective advantage well above the ~4% seen here; or a
later inherited-content study (root 23 or the owner's heritable-map note) needs this standing-variation
calibration — then a cheap single-episode confirmation of L > S and L > Z with fresh seeds can reuse the
1427 harness. Mere library improvement, more seeds of the same design, or available compute is insufficient.
