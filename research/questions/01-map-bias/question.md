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
What is left is why shared forms rarely appear in random-start runs: arrival or fixation of a
single new copy (07). The
README's second part, letting the map's bias itself evolve across a task family, is untested.

Competing explanations:
- A: The map mainly decides what arrives often; selection then keeps whatever form arrived
  first (arrival of the frequent, first-form persistence).
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
[findings](../../../docs/map-bias/findings.md), [notebook](../../../docs/map-bias/notebook.md),
[shared-helper plan](../../../Plans/shared-helper-reuse.md),
[digest](../../digest.md), [README core question](../../../README.md)
