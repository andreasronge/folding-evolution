---
status: open
tags: [map-bias, arrival-of-the-frequent, chem-tape, tagged-runs, shared-helper, crossover]
budget: {experiments: 6, used: 0}
---
# How does the genotype→program map bias what evolution finds and keeps?

Current summary: Random-genotype frequency predicts easy tasks but not which hard ones get
solved, and folding's advantage over direct encoding on fixed targets looks like a sampling
advantage (findings items 1, 17). The line has moved to building blocks: can the chemistry
discover, preserve and reuse a shared helper? Retention is easy. Establishment from rare is
blocked by crossover v2 with a selected mate (§29–§31), but the barrier is mixing between
lineages: with self as the mate, crossover still discovers (§32 J, about three times slower)
and a seeded shared form establishes at the crossover-off rate (06, run 2026-10-04-1839).
Why shared forms rarely appear in random-start runs was the last shared-helper question (07,
parked): established partly populations produce exact shared children about twice per run, all
A-only or other, and a natural single copy never established (0/100); the B-helper form that
won in both shared-ending runs never arrived in 30M partly-parent children. The shared-helper
line stops there (03–07 closed or parked). The README's second part, letting the map's bias
itself fit a task family, is [08](08-evolve-bias/question.md): by sampling, a fitted
`op_weights` vector transfers to a held-out threshold (4.9× and 8.9× over uniform, run
2026-10-05-1558), mainly through the aggregator's weight. In evolution (run 2026-10-05-1705)
it speeds the exact solve about 4× over uniform and a hand-set INPUT/GT/aggregator scaffold
does as well, but the other family's fit, with no resolved sampling lift, is already 3.3× / 1.9×
faster: both fits helped and family specificity is unresolved, and sampling lift does not predict evolution speed.
[09](09-generic-bias-speedup/question.md) (run 2026-10-05-1814) replicated that speed-up on
fresh seeds (2.73× / 2.02×) and split the vector: on max>2 raising INPUT and GT alone carries
it, on sum>2 neither part is resolved; the vector's flat sampling rate is INPUT/GT's 3–4× lift
cancelled by the rest's 3–4× loss. Run 2026-10-05-1957 reopened 09 for root 01's last
experiment, a direct test of the max>2 shortcut behind the rest-of-vector arm's sum>2 gain
(veto exact max>2 from reproduction). It stopped at its 50-seed pilot on the power gate, so
there is no registered result; at pilot strength the shortcut is the usual last step to the
solve but blocking it only delays the solve, as near-max programs take over. 08 and 09 are
parked, root 01's budget is spent, and the program is with the strategist.

Competing explanations:
- A: The map mainly decides what arrives often; selection then keeps whatever form arrived
  first (arrival of the frequent, first-form persistence). At the level of program forms
  (07) this is mixed: A-only shared children arrive about twice per run and drift out; the
  B-helper form was never seen arriving. Unresolved.
- B: The variation operators (crossover v2 in particular) decide what is kept, independent
  of how often a form arrives. True for selected-mate crossover vs a rare seeded form (03);
  removed by self-mating (06).
- C: The task and training sample decide it: shortcuts that fit 64 cases, and no pressure
  for sharing at the tape lengths tried.

Related: [02-fixed-target-sampling](02-fixed-target-sampling/question.md),
[03-rare-shared-establishment](03-rare-shared-establishment/question.md),
[04-random-start-discovery](04-random-start-discovery/question.md),
[05-latent-helper](05-latent-helper/question.md),
[06-self-mate-establishment](06-self-mate-establishment/question.md),
[07-shared-arrival](07-shared-arrival/question.md),
[08-evolve-bias](08-evolve-bias/question.md),
[09-generic-bias-speedup](09-generic-bias-speedup/question.md),
[findings](../../../docs/map-bias/findings.md), [notebook](../../../docs/map-bias/notebook.md),
[shared-helper plan](../../../Plans/shared-helper-reuse.md),
[digest](../../digest.md), [README core question](../../../README.md)
