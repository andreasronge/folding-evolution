---
author: owner
written: 2026-10-06
---
# Owner note: how to let the map itself evolve

For the strategist and steward, when README part 2 ("let the map's bias evolve
across related tasks; does it transfer?") goes beyond externally fitted
`op_weights`. This is a direction and a set of design constraints, not an
approved experiment. Weigh it against the evidence like any other input.

## The problem

Changing what a token means changes every copy of it in the tape at once, so
a free table mutation is almost always harmful. Biology calls the genetic
code a "frozen accident" (Crick 1968) for this reason. Yet the code has
changed a few times, and frequency (codon usage) changes all the time. Use
nature's routes, cheapest first.

## Steps, in order

1. **Inherited op frequencies (codon usage).** Each individual carries its own
   op distribution; mutation and any fresh tokens in its offspring are drawn
   from the parent's distribution, which itself mutates slightly (e.g.
   log-normal noise on the weights, a floor so no op becomes unreachable).
   Meanings never change. Today `op_weights` / `ChemTapeConfig.op_probs`
   are one global vector used on the Python side for initialization and
   mutation, so this should be a modest change. Ask: does the population's
   distribution move towards what the fitted vectors in 08/09 found, and
   does an evolved distribution, frozen and given to fresh populations, help
   on held-out family members as much as the hand-set scaffold?
2. **Safe table changes: capture and synonyms.** Only if step 1 shows the map
   can learn something. Add an indirection, token → op, carried per
   individual (or per lineage). Allow only changes that cannot break the
   current program:
   - *Codon capture*: a token may be reassigned only when the individual's
     active (decoded) program does not use it. Mitochondria reassigned UGA
     this way.
   - *Synonyms*: a spare token takes on an existing meaning (a second ADD).
     Nothing breaks, and that op is written more often.
   The Rust batch decode assumes one shared table, so this is engine work:
   build and validate it as its own stage before using it in an experiment.
3. **Population-level maps (optional, costly).** One table or distribution
   per population; populations compete across a task family (an outer loop
   over maps, inner loops of evolution). This is the most literal "the map
   fits a family", at the price of many evolution runs per evaluation.
4. **Free table mutation** only as a contrast, to show it is harmful.

Skip the "ambiguous intermediate" route (a token read two ways for a while)
unless the steps above leave a specific gap.

## Controls that keep it honest

Uniform weights; the hand-set INPUT/GT/aggregator scaffold from 08/09 (it
matched the fitted vector, so an evolved map must beat it to be
interesting); and the cost of adapting the map, counted against the
speed-up it gives later.

## Sizing

The researcher's build step is limited (one prepare, 120 min). Step 1 should
fit. Step 2's engine work may not: split it into a build-and-validate cycle
(small queue that checks the new decode against the old one with an identity
table) before any experiment uses it.
