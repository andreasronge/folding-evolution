---
status: open
tags: [map-bias, arrival-of-the-frequent, chem-tape, tagged-runs, shared-helper, crossover]
budget: {experiments: 6, used: 0}
---
# How does the genotype→program map bias what evolution finds and keeps?

Current summary: Random-genotype frequency predicts easy tasks but not which hard ones get
solved, and folding's advantage over direct encoding on fixed targets looks like a sampling
advantage (findings items 1, 17). The line has moved to building blocks: can the chemistry
discover, preserve and reuse a shared helper? Retention is easy; establishment from rare is
blocked by the same crossover v2 that drives discovery from random starts (§29–§31). The
README's second part, letting the map's bias itself evolve across a task family, is untested.

Competing explanations:
- A: The map mainly decides what arrives often; selection then keeps whatever form arrived
  first (arrival of the frequent, first-form persistence).
- B: The variation operators (crossover v2 in particular) decide what is kept, independent
  of how often a form arrives.
- C: The task and training sample decide it: shortcuts that fit 64 cases, and no pressure
  for sharing at the tape lengths tried.

Related: [02-fixed-target-sampling](02-fixed-target-sampling/question.md),
[03-rare-shared-establishment](03-rare-shared-establishment/question.md),
[04-random-start-discovery](04-random-start-discovery/question.md),
[05-latent-helper](05-latent-helper/question.md),
[findings](../../../docs/map-bias/findings.md), [notebook](../../../docs/map-bias/notebook.md),
[shared-helper plan](../../../Plans/shared-helper-reuse.md),
[digest](../../digest.md), [README core question](../../../README.md)
