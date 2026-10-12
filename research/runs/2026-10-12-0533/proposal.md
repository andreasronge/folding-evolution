---
node: questions/62-inherited-contextual-development
title: Inherited decoder under rotating comparison-gate goals, map-only readout
bank: comparison-gate-v1 (development: 8 training cells for exposure, 8 former holdouts for readout)
---
**Question.** Can program selection improve a per-individual decoder so that its frozen map helps fresh populations on unseen goals? Stage one of the [plan](../../plans/inherited-contextual-development.md).

**Mechanism.** Each individual carries a previous-token map, initialised to G4 and stored as labelled allele segments per row. Rows hold at most 64 segments; every token keeps at least 250 alleles. Mutation: each non-elite child, with p 0.1 on its own stream, picks a tape position j. In the row for the token before j, it overwrites a block of 240–1 200 alleles containing j's allele with a random token. Only alleles in the block change, including j's, so selection acts on the map directly. The child inherits the map of its prefix parent.

Exposure uses P 256 and [1246's loop](../2026-10-08-1246/analysis.md): 64 episodes × 128 generations (2.1M evaluations). The 8 training cells rotate in shuffled blocks; residents are kept.

**Closest technique.** Per-individual inherited genetic codes ([Keller & Banzhaf 1999](https://gpbib.cs.ucl.ac.uk/gp-html/keller_1999_TEGCGP.html); [O'Neill & Ryan 2004](https://gpbib.cs.ucl.ac.uk/gp-html/oneill_2004_eurogp.html)) were judged within the run. Changing goals follow [Kashtan et al. 2007](https://pmc.ncbi.nlm.nih.gov/articles/PMC1948871). New here: map-only readout on unseen goals, residents discarded, acquisition charged, drift and fixed-goal controls.

**Arms.** 24 independent acquisitions per arm (the unit of evidence). The readout map is one preassigned, fitness-blind final-population member.
- **L:** as above.
- **N:** each child copies a uniformly random member's map, then mutates it. This is the drift control.
- **F:** one fixed training cell throughout, 3 acquisitions per cell.
- **L-marg:** each L map projected to its token marginals.
- **G4:** the reference.

Readout: fresh uniform genomes under existing `search()` with a frozen-map decoder, cap 524k. Each acquisition index gets 8 holdouts × 4 seeds, shared across arms. Training cells × 2 seeds are descriptive only.

**Feasibility.** 1246 measured G4 at 49 µs per evaluation per worker (10 workers), 15.5 s per search, solving 59% of training and 77% of holdout searches. Projected: 2.5 min exposure per acquisition, about 2.3 h queue for roughly 3 000 readout searches. Smoke times the new decoder; over 7 h projected, drop the training readout. Checks:
- the segment decoder matches `Decoder` for G4 on 10⁵ tapes;
- with p = 0, exposure replays G4 exactly;
- floors, map/tape alignment under crossover and non-aliased elites hold.

**Cost.** About 6 h (2 h prepare, 2.5 h queue, 1.5 h review) of the 20–28 h block.

**Primary comparison.** Per acquisition, take the geometric mean of cost(L)/cost(G4) over its 32 paired holdout searches, charging unsolved runs at 2 × cap. Average over the 24 acquisitions with a 95% t interval.
- Upper bound < 0.80: worthwhile. Next, freeze the method with a fresh bank for protected transfer.
- Lower bound > 0.80: park 62 for this law.
- Otherwise: replicate only if the point estimate is below 0.85.

L/N, L/F and L/L-marg: secondary, intervals only.

**Expectation.** L within ±15% of G4: drift at neutral positions erodes G4. A surprise would be L beating G4, N and F on holdouts.
