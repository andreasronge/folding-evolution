---
author: owner
written: 2026-10-12
---
# Owner note: next direction after run 2026-10-10-1419

For the strategist and steward. An area to explore, not a design.

**Area: can evolution make its own map better at finding new solutions?**
Evolvability of the genotype→program map, learned by evolution itself,
without outside fitting. This is the project's own question; the tree-GP
library line answered a neighbouring one.

**What we know.** In 55, an inherited preference faded once the task was
solved: with one fixed goal, being good at search stops paying. Outside
fitting works but is known ground (EDA, PIPE, run-transferable libraries).

**Leads, not orders.** Pick, combine or replace them:
- Goals that change between related tasks (modularity and facilitated
  variation in biology, e.g. Kashtan & Alon).
- How the genetic code and developmental bias evolve; neutral networks;
  duplication and divergence.
- Give evolution more freedom over the map itself: make parts of the
  chemistry inherited and mutable (bond rules and reach, as in the folding
  track's `dev_genome.py`; token meanings through synonyms or duplication then
  divergence, see [owner-heritable-map](owner-heritable-map.md)). Use safe
  routes: a free change of a token's meaning breaks every copy at once.
  Earlier, extra reach (d2 bonds) made bigger programs but no fitter ones on
  easy tasks, so pair freedom with pressure that rewards it (changing or harder
  goals).
- Something the data or literature suggests that is not on this list.

**Must-haves.**
- Use the project's own map (chemistry, decoder, inherited weights); tree GP
  is the outside baseline.
- Separate what the map learned from saved programs carried along.
- Test on goals never seen while the map evolved, and count the cost of
  evolving it.
- Probes are welcome while the area is new. Name the closest prior work and
  what we add.

**Deferred.** The [abstraction plan](corpus-abstraction-transfer.md) (useful
but crowded) and PSB2 (waits for a method worth a broader test).
