# Log: 06-self-mate-establishment

## Opened 2026-10-04 by the steward

Split from [04](../04-random-start-discovery/log.md): the self-mate establishment test is a
seeded contest (§31 D setup), not a random-start run, so it gets its own question.
Proposed in [runs/2026-10-04-1839](../../../runs/2026-10-04-1839/proposal.md).

## 2026-10-04, run 2026-10-04-1839 (commit f2e4048)

- Self-mate contest: §31 D cells (L 64, pop 1024, shared vs duplicated / partly shared,
  1/32 and 1/10 shared, seeds 0–29) with `crossover_mate: self` at crossover 0.3 and 0.7,
  240 runs, plus a one-step self-crossover census (10,000 children per hand-built form).
  [proposal](../../../runs/2026-10-04-1839/proposal.md),
  [analysis](../../../runs/2026-10-04-1839/analysis.md), raw data
  `experiments/output/2026-10-04/2026-10-04-1839-self-mate-contest/` and `…-self-crossover-census/`.
- Result: shared wins 183/240 under self-mate vs 34/240 with a selected mate in the same
  cells and seeds, and 75/120 with crossover off. Per cell (1/32, 1/10; self 0.3 / 0.7):
  vs duplicated 27/27, 30/30 (off 19, 29); vs partly 12/13, 26/18 (off 8, 19). Every cell
  clears the pre-registered two-thirds-of-off threshold; no cell is more than one win below
  crossover off. No early loss: shared share rises from generation 0, as with crossover off
  (selected mate halves it by generation 5). Census: no self-crossover child changes form
  (0 of 120,000 over four RNG seeds); shared breaks in 20.0% vs 19.0% / 18.7%, a one-point
  excess from having one more run (fewer clones).
- Soft spot: self 0.7 vs partly from 1/10 has 6 "in between" runs, 5 of which had reached
  ≥ 95% shared and then fell back as partly shared returned (the partly seed tape sits in an
  elite slot). So "majority wins" is not fully clean at 0.7 against partly.
- Side observation: in every arm (off, self, selected), runs where shared is lost against
  duplicated end **partly shared**, never duplicated. Partly shared arises in the run; shared
  is replaced by a third form, not beaten by duplicated.
- Not shown: "self-mating helps shared beyond crossover off" (7 of 8 cells higher, but same
  seeds across rates; seed-paired 10 vs 2, p ≈ 0.04; unclear). Nothing here is about arrival
  or about a single new copy.

Decision: close 06 with explanation A (the barrier is mixing between lineages; a shared form
already present at 3–10% establishes under self-mate crossover at about the crossover-off
rate) because all 8 cells met the strong-rescue row of the plan, far from any boundary, and
the census rules out rearrangement damage as a material cost (B). Discovery (§32 J) and
seeded establishment can therefore coexist under one operator. The arrival claim the
proposal hoped to close with is **not** shown by this run; it moves to
[07-shared-arrival](../07-shared-arrival/question.md).
