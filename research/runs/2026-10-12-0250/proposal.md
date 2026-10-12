---
node: questions/55-inherited-library-choice
title: Inherited content choice — does a program-linked order/gate bit learn which saved library suits the family it was exposed to?
bank: x4-order-v1 + x4-signed-gate-v1 (six development cells each; saved 1228 R-all and 1938 R-all libraries unchanged; protected rosters untouched)
---
**Question.** Per [strategy 0250](strategy.md) and its [plan](../../plans/inherited-content-choice.md). In 1736 the bit chose only *how often* a library was used. Here it chooses *which* library: state 0 draws order-library donors and state 1 gate-library donors, each on half of mutations. Is the gate fraction f a population ends with after exposure to one family cheaper on that family in fresh search than the 50/50 start, and than the f reached on the other family?

**Closest technique.** Self-adaptive operator choice by an inherited tag: Spears' one-bit choice of crossover type (described in [Harper & Blair 2006](https://cgi.cse.unsw.edu.au/~blair/pubs/2006HarperBlairSSCO.pdf)), [Angeline 1996](https://gpbib.cs.ucl.ac.uk/gp-html/angeline_1996_aigp2.html) in GP, inherited operator choice ([Serpell & Smith 2010](https://uwe-repository.worktribe.com/output/975827)) and indirect selection of variation parameters ([Stephens et al.](https://arxiv.org/abs/adap-org/9708002)). The map adapts by per-individual inheritance. **What this adds:** the options are two externally acquired content repertoires. The chosen mixture is frozen and deployed alone, in both family directions, against linkage and neutral controls. Content is supplied; a mechanism test.

**Feasibility probe (done, ≤10 min, observations; [log](../../questions/55-inherited-library-choice/log.md), [rows](headroom-probe/)).** I ran the unchanged engine on 24 paired builds × 6 cells × 1 seed, with all laws at library probability 0.5:

| family | O/M | G/M | worker-s per job (O, G, M) |
|---|---|---|---|
| order | 0.78 [0.51, 1.18] | 2.78 | 2.1, 7.4, 2.7 |
| gate | 1.56 | 0.69 [0.47, 1.05] | 0.57, 0.22, 0.35 |

Each library is much cheaper on its own family. Gate donors on order cells cost more than no library. The mixture leaves about 20–30% headroom both ways. (864 jobs, 176 s, 11 workers.)

**Design (plan values, no sweeps).** P 256, lexicase, crossover 0.5, two elites. The bit is inherited from the recipient and redrawn with probability 1/32 from Bernoulli(1/2). f₀ = 1/2. Exposure is twelve 64-generation episodes with balanced cell rotation, continuing after solves. Programs reset between episodes; bits persist. Pairs by build index (b ↔ b, performance-blind); mixtures normalized within library.
- Arms: L (linked), S (bits shuffled before selection), N (both states use the 50/50 mixture).
- Exposure: 3 arms × 2 families × 24 pairs × **8 populations** = 1,152 trajectories.
- Readout: discard the programs. Deploy each population's law alone: ordinary donors ½, order (1−f)/2, gate f/2.
  - Order family: L-matched (order-exposed L), L-swapped (gate-exposed L), S and N (own family), and M, all on 6 cells × 2 seeds per population or per (pair, population slot).
  - Pure O and G on 2 seeds per (pair, cell).
  - Gate family: the same laws. Jobs there are cheap, so it uses 4 seeds.

**Cost.**
- Exposure: about 14 worker-s per trajectory (1736): 16k worker-s, about 25 min.
- Readout: about 36k (order) + 12k (gate) worker-s, about 75 min.
- Timeouts: 50 + 160 min = 3.5 h, within the 4 h cap.
- Complete: critique 0.5 h, preparation ≤ 2 h (two-library path, the plan's validators, sustained timing), review 0.5 h, queue about 1.7 h (worst 3.5 h), analysis 1.5 h: about 7–8.5 h, ceiling 10 h, before 14:19 even at full timeouts.

**Primary comparison.** R = geometric mean over the two families of L-matched / M, in capped mean evaluations. Costs are averaged within populations, then pairs. The 95% interval is a nested bootstrap: pairs (one index used for both families), with populations within pairs.
- **Useful, reciprocal:** R upper < 0.90, and in *each* family L-matched/M upper < 1 and L-matched/L-swapped upper < 1.
- **One direction:** R upper < 0.90, only one family meeting both conditions (narrower answer).
- **No worthwhile saving:** R lower > 0.80. This ends the candidate.
- **Unresolved** otherwise. Return to strategy with a price.
- **Validity guard:** if the readout's own-pure/M pooled upper bound is ≥ 0.90, the test lacks headroom, and the result is reported as saturation, not as a failure of selection.

Precision: 1736 gave about ±12% at 6 populations with bimodal endpoints; with 8 populations, a mid-range start and two families pooled I expect ±8–9% on R. That separates 0.80 from 1.0, not 0.85 from 0.90.

Reported only: endpoint f by arm and family, S/M, N/M, pre-solve versus maintenance differentials, rejection by state, solves, worker seconds, per-cell results, and acquisition-plus-search cost.

**Expectation.** Order exposure drives f to about 0.15–0.3 (gate carriers are heavily penalized); gate exposure moves less, since gate tasks solve in 15–30 generations and episodes are mostly maintenance. I expect R ≈ 0.85–0.9, most likely *unresolved* or *one direction (order)*, with L-matched < L-swapped clear on order.
- **Surprises:** R < 0.80; gate exposure moving f as far as order; N or S matching L; L-matched worse than M anywhere.

**Next.** Return to strategy whatever the outcome. Reciprocal success would justify considering an inherited repertoire with changeable content; a negative bounds this selector and exposure rule (no top-up or rate sweep). Fresh-bank transfer stays unfunded.
