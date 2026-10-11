---
node: questions/55-inherited-library-choice
title: Standing-variation probe — can program selection carry a bit that switches on R-all?
bank: x4-order-v1 (development roster only; saved 1228 R-all libraries; protected cells untouched)
kind: probe
---
**Question.** This follows [strategy 1427](strategy.md) and the [plan](../../plans/inherited-library-choice.md). R-all cut cost on the six order development cells to 0.40× R-tree ([1228](../2026-10-11-1228/analysis.md)). Here an inherited per-program bit chooses between ordinary donors and R-all, and only program selection acts on it. Does selection raise its frequency, and does the final frequency make fresh search cheaper once programs are discarded? Content is held fixed; no transfer claim.

**Closest technique.** Self-adaptation, meaning indirect selection on inherited variation parameters ([Stephens et al. 1998](https://pubmed.ncbi.nlm.nih.gov/9847423/); inherited operator choice in GAs, [Serpell & Smith 2010](https://uwe-repository.worktribe.com/output/975827)). GP operator-rate adaptation ([Kim et al. 2011](https://gpbib.cs.ucl.ac.uk/gp-html/Kim_2011_EuroGP.html)) uses external credit assignment, an outer-loop update. In biology, mutators hitchhike in asexual populations, but recombination erodes the association ([yeast, 2011](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3141426/)); root 01's mixing result predicts the same risk. **Adds:** a law with measured fresh-search benefit, and a rejection-matched null separating content from robustness selection.

**A confound, measured now.** An oversize insertion reverts to a copy of the parent. In 1228, library draws were rejected 0.547 of the time against 0.363 for ordinary donors. Carriers therefore produce about 5 points more clones, which near an optimum can favour the bit alone ("survival of the flattest", [Wilke et al. 2001](https://dx.doi.org/10.1038/35085569)). A neutral bit cannot detect this. So I add a **size-matched null**, built with the existing `tree_library.controls`: random donors matched in (nodes, compiled length) to each build's R-all entries. It builds for all 24 libraries (read-only check).

**Exposure.** The 1228 tree engine is unchanged: P 256, crossover 0.5, lexicase, two elites.
- Carriers' mutation children use the carrier's law; the bit follows the recipient (p1), reverts and elites included.
- The starting frequency is f₀ = 0.25: 64 random carriers, assigned independently of programs, with no bit mutation. Fixed before any efficacy data, for readout headroom (library probability 0.125 vs 0.5).
- Each trajectory runs 12 episodes: the six development cells twice, 64 generations each. Order is fixed, with the start rotated so every cell leads equally often.
- Episodes run past the first solve, which is recorded. Between episodes, programs are reinitialized independently of the bit; bits keep their slots.

| Arm | Bit-1 law | Trajectories |
|---|---|---|
| L linked | R-all | 24 libraries × 4 |
| S shuffled | R-all, bits permuted before each selection | 24 × 4 |
| Z size-null | size-matched random donors | 24 × 4 |
| N neutral | ordinary (bookkeeping check) | 24 × 2 |

The unit is the library (trajectories under one library are not independent). Logged: census and recipient f per generation; draws, insertions and reverts per state; Δf before and after each episode's solve.

**Frozen readout.** For each library, discard all programs and score five global laws, given as library probability: R-tree (0), initial (0.125), L-final (0.5 × the mean final f of its four L trajectories), S-final, and R-all (0.5). Scoring follows 1228: 6 cells × 2 repeats × 8 attempts × 65,536, seeds paired across laws in a new namespace, 1,440 searches.

**Feasibility.**
- **Speed:** 0.0186 worker-s per generation under load (1228); 0.007 s single-thread today.
- **Drift:** about 115–125 distinct recipients per generation, so drift is strong and many trajectories may fix.
- **Exposure:** 336 × 768 generations ≈ 4,900 worker-s, about 9 min on 10 workers.
- **Readout:** about 5,100 worker-s (9 min), mixed laws assumed between R-tree (5.3 s/job) and R-all (2.1).
- **Timeouts:** 1,500 s + 1,800 s = 55 min.

**Cost.** Preparation ≤ 120 min, queue about 20 min, plus agent cycles: about 4.5–5 h.

**Primary comparison.** Descriptive probe; continuation rule fixed now. The comparison is mean final f, L − S, with a bootstrap over the 24 libraries. I would propose the 6–8 h confirmation only if all three hold:
- (a) L − S ≥ 0.15, with lower bound > 0;
- (b) L − Z ≥ 0.10, i.e. selection beyond revert rate and size;
- (c) the initial law costs ≥ 1.25× R-all.

If N's mean departs from 0.25 beyond its interval, bookkeeping is broken: no conclusion. Otherwise:
- **(a) fails:** explanations B or C; the procedure ends.
- **Only (b) fails:** robustness selection; record it and end.
- **(c) fails:** explanation E; park.

Readout ratios (L-final/initial, L-final/S-final) are reported per cell and decide nothing.

**Expectation.** The bit touches a quarter of a carrier's children, crossover hands helpers to non-carriers, and the benefit is mostly pre-solve, so I expect L − S of about 0.05–0.10, with Z rising after the solve. Surprises: L fixing in ≥ 60% of trajectories, L below S, or Z matching L.

**Next.** To the strategist. If the rule passes, a confirmation priced from this variance (fresh seeds; L-final/initial primary); otherwise end or park root 55.
