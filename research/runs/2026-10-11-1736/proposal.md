---
node: questions/55-inherited-library-choice
title: Recurrent-mutation selector — does one population's evolved R-all frequency make fresh search cheaper than its starting law?
bank: x4-order-v1 (six original development cells; saved 1228 R-all libraries; rectifier protected cells untouched)
---
**Question.** Follows [strategy 1736](strategy.md) and its [plan](../../plans/recurrent-inherited-library-choice.md) as written. Unlike [probe 1427](../2026-10-11-1427/analysis.md) it has bit mutation (no absorption), a low starting dose and a separate readout per population. A carrier bit switches a program's mutation donors to the half-library R-all law, and only program selection acts on it. Does the law one population ends with make fresh search cheaper than its starting law, beyond what mutation and broken linkage produce?

**Closest technique.** Self-adaptation: inherited, mutated variation parameters selected indirectly ([Stephens et al. 1998](https://pubmed.ncbi.nlm.nih.gov/9847423/); inherited operator choice, [Serpell & Smith 2010](https://uwe-repository.worktribe.com/output/975827)). The map adapts by per-individual inheritance. GP rate control ([Kim et al. 2011](https://gpbib.cs.ucl.ac.uk/gp-html/Kim_2011_EuroGP.html)) uses outer-loop credit instead. **Adds:** the selected law is deployed alone in fresh search, against linkage and neutral controls. Content stays external; a mechanism test.

**Design (plan values).** P 256, lexicase, crossover 0.5, two elites, R-all content and donor law unchanged.
- Each population starts with 16 random carriers (f₀ = 1/16).
- At each nonelite birth the child inherits the recipient's bit, then redraws it from Bernoulli(1/16) with probability 1/32. Elites keep their bits.
- Exposure is twelve 64-generation episodes with balanced cell rotation. Programs reset between episodes; bits persist.

| Arm | Bit-1 law | Trajectories |
|---|---|---|
| L linked | R-all | 24 libraries × 6 |
| S shuffled before selection | R-all | 24 × 6 |
| N neutral | ordinary | 24 × 6 |

**Readout.** Each of the 432 populations is deployed alone at q = 0.5 · final f, using its own library. It is scored on 6 cells × 2 fresh seeds, at 8 × 65,536 evaluations. The references are q₀ = 1/32 and R-all (q = 0.5), scored on the same 12 seeds per (library, cell) as that library's populations. That makes 8,640 jobs. Costs average over populations, then libraries; the bootstrap resamples libraries, populations nested.

**Forecast ([forecast_model.py](forecast_model.py), read-only).** The model uses the plan's rates and the 1427 measurements:
- carrier advantage s ≈ 0.036 per pre-solve generation, about 100 distinct parents, about 50% of episodes solved;
- cost(q) ≈ 32 k + 42 k·e^(−q/0.104), fitted to the pooled 1427 dose points. This gives q₀ ≈ 63 k, about 1.9× R-all, but that point is unmeasured.

It predicts mean final f of L ≈ 0.13 and N ≈ 0.065, with 17–23% of populations ending at zero carriers. **Predicted L-final/q₀ is ≈ 0.95** (0.93–1.01 for Ne from 60 to 150). A 20% saving would need s ≈ 0.1, about three times the measured value. At the measured s, u = 1/128 forecasts 0.88, so the rate is not the lever. The model is crude (s was measured at f ≥ 0.25 under absorption), so the experiment tests whether low-frequency selection is much stronger than assumed.

**Feasibility.**
- **Exposure:** 1427 ran 336 trajectories in 480 s on 10 workers; 432 take about 11 min.
- **Readout:** low-dose jobs take about 4.3 s and R-all jobs 2.5 s, about 34,000 worker-s or 57 min in all.
- **Timeouts:** 30 + 120 min.
- **Precision:** the job CV is about 1.5. With 1,728 jobs per law, the ratio's 95% half-width is about ±10% before seed pairing helps.

**Prepare (≤ 120 min) validates** bit alignment after mutation, elites and rejected edits. It also checks N's transitions against 1/512 off→on and 15/512 on→off, that zero mutation replays 1427 exactly, the separate modifier stream, equal exposure, and the readout paths at q₀ and 0.5. No efficacy pilot.

**Cost.** About 7–8 h (ceiling 10 h; 20.5 h left): proposal/critique 1 h, prepare 2 h, review 0.5 h, queue 70 min, analysis/decision 1.5 h.

**Primary comparison.** L-final / q₀ in capped mean evaluations, with a 95% library bootstrap.
- **Useful:** upper bound < 0.90. Inheritance is supported only if L-final/N-final and L-final/S-final also have upper bounds below 1. A gain N shares is a mutation/endpoint effect.
- **No worthwhile saving:** lower bound > 0.80 and upper bound ≥ 0.90. This ends the candidate.
- **Unresolved** otherwise. Back to strategy with a price for resolving it.

Reported, deciding nothing: solve counts, worker seconds, q₀/R-all (headroom; below 1.25 the test is uninformative), L-final/R-all with supplied R-order visible, the low-f selection differential, mean final f by arm, polymorphic and zero-carrier time, rejection by state, cell heterogeneity, and acquisition-plus-search cost.

**Expectation.** The second outcome: about 0.95, a resolved L > N in mean final f, and headroom present. That ends the candidate with a quantitative reason: ~4% carrier advantage against ~100 effective parents cannot set a useful law. It also tells root 23 how strong a heritable learner's advantage must be. **Surprises:** L-final/q₀ ≤ 0.85; a low-f differential of at least 0.08; L's mean final f no higher than N's; or q₀ ≤ 1.25× R-all.

**Next.** Return to strategy whatever the outcome. Transfer or content learning stays unfunded.
