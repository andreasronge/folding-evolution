---
node: questions/23-heritable-variation-bias
title: Inherited op frequencies vs ancestry-broken control — frozen-vector search speed on the training thresholds (acquisition test, slot 1 of 2)
bank: tag-threshold-v1   # sum/max > 1, 5 on length-4 lists over 0..9; threshold 2 untouched (development bank)
---
**Question.** Per [strategy 2243](strategy.md) and the [plan](../../plans/heritable-variation-bias.md): can program selection alone put useful information into a token-frequency vector that each individual carries and passes on? Does that vector, frozen and given to fresh populations, beat a control in which the program–vector link is broken? Channel: each individual's fresh tokens come from its own vector. That covers its tape at each reset and its offspring's mutated or inserted ops; token meanings and the decoder stay fixed.

**Closest technique.** Per-individual self-adaptation by inheritance:
- [Angeline 1996](https://gpbib.cs.ucl.ac.uk/gp-html/angeline_1996_aigp2.html) gives each GP tree inherited crossover-point probabilities.
- [Stephens et al. 1997](https://arxiv.org/abs/adap-org/9708002) and [Serpell & Smith 2010](https://doi.org/10.1162/EVCO_a_00006) study encoded operator parameters.
- [Kim et al. 2011](https://gpbib.cs.ucl.ac.uk/gp-html/Kim_2011_EuroGP.html) adapt operator rates at population level, which is not inheritance.

New here: the inherited parameter is the token distribution, frozen and tested on fresh populations, against broken ancestry and the scaffold, with no external fit or outer loop (unlike root 10).

**Procedure (fixed now; no calibration sweep).** The 1705 TAG harness: P1024, L64, lexicase, crossover v2 0.7 with a selected mate, mutation 0.015, 2 elites, exact check on all 10,000 lists.
- Modifier: θ ∈ [−3, 3]^22, starting at 0, with p = 0.9·softmax(θ) + 0.1/22. A child copies its recipient's θ and adds N(0, 0.03²) per component. Elites copy θ exactly. The modifier has its own RNG stream.
  - Why σ = 0.03: neutral drift over ≈2,000 generations is about 1 log-unit, the size of the fitted INPUT/GT raises.
- Exposure: 48 episodes per run, alternating thresholds 1 and 5, with 64 fresh label-balanced cases each. An episode ends at the first exact solve or after 128 generations. At each reset every individual redraws its tape from its own p.
- Arms: **inherited** vs **broken**. Broken permutes θ across the whole population, elites included, before every parent selection, including generation 0. That cuts both channels.
- Unit: one independent acquisition run; 16 per family per arm, 64 in total. Extraction: the mean of the final population's p. Every individual's θ is saved.
- Frozen scoring: one global vector, cap 262,144 evaluations, on the family's two training targets. Each target has 16 search seeds shared by all vectors. References on the same seeds plus 48 more: uniform, the hand-set scaffold and the 1558 matched fit.

**Feasibility (1705 per-run files).**
- Speed: about 30k evaluations/s per worker. Mean uniform search took 1.9 s (sum2) and 7.3 s (max2). Shortcut-stuck runs push the tail to 150 s.
- Code on `research/main`: `evolve_bias.py`, `family_bias.py` (it already defines sum1/5 and max1/5) and the lineage record in `evolve.py` (recipient, mate, elite). Per-child rows need only a per-row `_draw_ops`; no Rust change.
- Stage 0 (in the queue, not gated on outcomes):
  - unit checks: normalisation, the floor, bookkeeping, and that a θ change alone leaves execution unchanged;
  - with σ = 0 and identical rows, the legacy search is reproduced on 20 seeds;
  - one timed acquisition run per arm.

**Cost.**
- Acquisition: 64 runs × ~4 min on 10 workers ≈ 0.5 h (worst case 1.1 h).
- Scoring: about 2,600 searches ≈ 0.3 h (worst case 1 h).
- Queue timeouts: ≤ 3.5 h in total.
- Agent time: about 4–5 h, so 6–8 h overall, inside the 10–14 h block.

**Primary comparison.** Each run's score is the geometric mean of evaluations to exact over its 32 frozen searches, with censored searches counted at the cap. Effect: broken ÷ inherited, with families pooled equally. The 95% bootstrap resamples runs within family. The expected interval is about ×/÷1.2, assuming a between-run SD of about 0.3 log (stage 0 reports the actual value).
- **Acquired**: lower bound > 1 and point ≥ 1.5× → slot 2 runs the plan's frozen threshold-2 transfer test (matched/mismatched, scaffold, uniform, fresh seeds).
- **Limited**: upper bound < 1.5× → record a bound on this procedure (B or E), park 23 and go to strategy.
- **Otherwise**: unresolved → go to strategy with a priced extension. This is not a null.

**Secondary (descriptive).**
- Inherited ÷ uniform, ÷ scaffold and ÷ the fit.
- The Price covariance of θ with offspring count in each arm.
- θ trajectories, especially CONST_2 (explanation D).
- Episode solve times.

Beating the scaffold here is partly expected (a learned vector can raise CONST_1/5); the practical claim belongs to slot 2.

**Expectation.** About 45% acquired, with INPUT, GT and the family aggregator rising; 30% limited; 25% unresolved. What would surprise me:
- broken ≈ inherited while both beat uniform, meaning drift or the floor shaped the vector;
- inherited beating the fit by more than 1.5×.

**Next action.** The researcher builds the modifier path and runs stage 0, acquisition and scoring in one queue. Scope: one rule, σ and schedule, on a development bank, training targets only.
