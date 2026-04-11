# Planned Experiments

Ordered by expected impact. Each experiment has a clear hypothesis and measurable outcome.

## Priority 1: Break the Complexity Ceiling

The single most important problem. Most complex evolved program is 3 bonds. 4+ bond programs never emerge through evolution despite being abundant in random genotypes.

### Status: Building-Block Supply Problem — Motif Insertion Breakthrough

A comprehensive diagnostic series (see findings Section 6) progressively narrowed the bottleneck:

**What is NOT the bottleneck:**
- Representation expressivity (C1: 4+ bonds in 23-74% of random genotypes)
- Selection maintenance (seeded S4 swept to fixation at 0.832)
- Task design (filter tasks verified hard; staircase, lexicase, compositional credit all failed)
- Generic structural variation (substring duplication/transposition: no improvement)
- Archive preservation (nothing to archive — S3 too rare at 0.04%)

**What IS the bottleneck: building-block supply.**
- S3 carriers (fn+comparator+get_price) exist at only 0.04% of random genotypes
- The combination pipeline narrows exponentially: 42% → 12% → 0.8% → 0.04%
- Standard variation operators cannot generate useful motifs at sufficient frequency
- The S3→S4 transition IS achievable (0.32% per mutation) but fires too rarely because S3 is too rare

**The breakthrough: known-motif insertion raises S3 density 250x (0.04% → 10.3%)** and enables the full target program to evolve without direct seeding. Seed 13 produced `count(filter(fn x (> (get x :price) 200)) data/products)` at fitness 0.832 — the first unseeded discovery of the correct filter program. Generic substring operators (duplication, transposition) did not help.

### Completed Experiments

- **1.0: S3→S4 Transition Analysis** — DONE. S3→S4: 0.32%/mutation, S4→S5: 26.6%. Crossover: S3×random→S4 at 6.9%. The transitions are possible; S3 rarity is the bottleneck.
- **1.1: Module operators** — DONE. Motif insertion works (S3 5/20 seeds, S5 2/20 seeds). Generic dup/transpose doesn't help.
- **1.3: Archive reinjection** — DONE. Failed because S3 is too rare (0.04%) to archive. The mechanism is sound but needs motif supply upstream.

### Next Experiments (Priority 1)

**1.5: Learned motif library (NEXT)**

The central open question: can the system discover and accumulate useful motifs endogenously rather than having them hand-coded?

**Design:**
1. Discovery phase: run 50 short evolution runs on easy tasks. For each 2-4 char substring in evolved genotypes, test in 100 random fold contexts. Score by how often it produces S1/S2/S3 assemblies.
2. Application phase: run evolution on hard tasks with motif insertion drawing from the learned library.
3. Compare: no motifs, hand-coded motifs, learned motifs, random motifs (control).

**Hypothesis:** Motifs enriched by evolution on easy tasks produce useful building blocks for harder tasks. This is constructional selection: evolution shapes the GP map by enriching functional subsequences.

**1.6: Population-level motif ecology**

Keep a global motif pool updated from evolved populations. Motifs gain or lose frequency based on downstream success. This is a step toward open-ended motif accumulation.

**1.7: Hierarchical evolution**

Easy tasks evolve motifs, hard tasks consume and elaborate them. Two-level evolutionary process: outer loop evolves the motif library, inner loop evolves programs using it.

### Superseded/Completed Experiments

- **Scale Up**: C1 showed scaling doesn't help — more bonds but not better programs.
- **Complexity-Biased Selection**: Produces junk bonds, not useful structure.
- **Generic fitness shaping**: Staircase, lexicase, compositional credit all failed.
- **Evolvable chemistry alone**: d2 increases bond counts but not useful structure.
- **Generic substring operators**: Duplication/transposition don't increase scaffold frequency.

## Priority 2: The Central Experiment — Representation x Selection Regime

The strongest claim this project can make: **the usefulness of a GP map depends on the selection regime**. Canalized maps favor stability; pleiotropic developmental maps favor adaptation under environmental change. This is Altenberg's prediction, tested directly.

The existing regime shift data (pop=50, len=30, 3 runs) is preliminary. Direct encoding scored 0.10 even before the shift — it may never solve these tasks at all. If direct encoding can't compete under stable conditions, there is no crossover interaction to measure and the comparison is invalid.

This priority has three phases: calibrate, then the 2x2 experiment, then mechanism.

### Phase 1: Calibration (run first)

**Goal**: Determine whether direct encoding can solve any tasks in this system, and at what difficulty level.

**Setup**:
- Direct encoding, stable target, 500 gens, pop=50, 10 seeds
- Task sweep across complexity levels:
  - 1-bond: single data source (trivial baseline)
  - 2-bond: `count(data)`, `first(data)`
  - 3-bond: `count(filter(fn [...] data))`
- Also run DEAP tree GP (same function/terminal set) as reference
- Genotype length: 30 and 50

**Measure**: Generation of first solution, final fitness, convergence curve. Find the task complexity where direct encoding reliably reaches >0.5 fitness.

**Decision gate**:
- If direct encoding succeeds on some tasks: use those tasks for the 2x2
- If direct encoding never succeeds: replace it with tree GP baseline (Option A) or redesign the direct encoding as stack-based assembly (Option B)
- Option B (stack-and-bond): read left-to-right, maintain a stack, push fragments, pop and bond when a valid combination appears. Same alphabet and operators as folding. Cleaner isolation of the spatial-topology variable.

**Why this phase matters**: The 2x2 is only as strong as its weaker arm. Skip calibration and you risk 30-seed runs that produce "folding wins everything" — a result that looks like a rigged comparison.

### Phase 2: The 2x2 Experiment

**Status**: Partially completed in Python. The original crossover hypothesis was not supported by the first large sweep.

**Updated finding**:
- Folding beats direct under both stable and shifting conditions on the current task family.
- The dynamic advantage is still real, but it appears as higher mean fitness over time, more fitness jumps, and better recovery under repeated shifts, not as a clean stable-vs-shifting crossover.
- The clearest separation so far is at genotype length 80 with shifts every 20 generations.

**Current best result**:
- Stable, length 50: folding `0.588`, direct `0.547`
- Stable, length 80: folding `0.588`, direct `0.469`
- Shift every 20, length 80: folding final `0.531`, direct `0.397`
- Shift every 50, length 80: folding final `0.515`, direct `0.436`

**Design**:
```
              Stable target    Shifting target
Folding       (F+S)            (F+Sh)
Baseline*     (B+S)            (B+Sh)

* Baseline = whichever canalized encoding survived Phase 1
  (direct encoding, tree GP, or stack-based assembly)
```

**Updated setup to prioritize next**:
- Genotype length: 80 primary, 50 as control
- Population: 100 now; 300 next if wall-clock allows
- Generations: 200 now; extend to 500 only after 50-seed confirmation
- Seeds: 50 for the next confirmatory run
- Task pool: products-focused and employees-focused multi-target fitness
- Stable condition: one target fixed for 200 gens
- Shifting condition: repeated alternation every N gens
- Shift frequency sweep: prioritize `N = 20` and `N = 50`

**Matched controls**:
- Same alphabet, same mutation/crossover operators, same population size, same evaluation budget
- Stable and shifting use the same task pool — stable just fixes one target from the pool
- Task difficulty matched to what both representations can solve (from Phase 1)

**Primary measures**:
- Mean fitness over time
- Final fitness
- Mean drop and recovery after each shift
- Number of fitness jumps (>0.1 improvement in one generation)
- Bond-count distribution at termination

**Statistical analysis**:
- Two-way ANOVA: representation x regime, testing for interaction effect
- Wilcoxon rank-sum on final fitness per condition
- Effect sizes and 95% confidence intervals
- The shift frequency sweep is reported as a curve: folding advantage vs shift frequency

**The figure**: One plot with stable controls and periodic-shift conditions for both encodings. A second plot showing mean post-shift recovery aggregated over all shifts. The main expected pattern now is not a crossover but a widening dynamic gap as shift frequency increases and genotype length grows.

**Convergence check**: Run both representations for 500 gens on stable target (10 seeds) to confirm whether direct is still improving at 200 gens. If so, report the current 200-gen results as a lower bound on the stable baseline.

### Phase 3: Mechanism (explains the 2x2)

Run after Phase 2 confirms the interaction effect. These explain *why* the interaction exists.

**3a. Pleiotropy per mutation on evolved populations**

For each individual (evolved and random), apply 100 point mutations. Count phenotypic traits changed per mutation (bonds, program output, active sites). Compare distributions between representations and between stable-evolved vs shift-evolved populations.

Altenberg predicts: evolved < random. We additionally predict: shift-evolved folding populations may show *higher* pleiotropy than stable-evolved folding populations (selection maintained exploratory capacity).

**3b. Phenotype frequency distribution**

Generate 100,000 random genotypes per length (30, 50, 80). Map each through folding and direct encoding. Plot the phenotype frequency distribution.

Prediction: folding produces a more skewed distribution (few high-frequency simple phenotypes, many rare complex phenotypes). This reframes the complexity ceiling as a phenotype accessibility problem, connecting to Dingle et al.'s RNA GP-map work.

**3c. Motif enrichment in evolved genotypes**

Extract all 3-character and 4-character subsequences from evolved genotypes (post-experiment). Compare frequencies to random genotypes. Compute enrichment ratios.

If enriched motifs correspond to functional fold patterns (e.g., "DaK" = get+price+>), this is evidence of constructional selection — evolution shaping the GP map, not just the programs the map produces.

## Priority 3: Altenberg-Inspired Measurements

### Experiment 3.1: Motif Enrichment

**Hypothesis**: Evolved genotypes contain enriched functional motifs — evidence of constructional selection.

**Setup**:
- Extract all 3-character and 4-character subsequences from evolved genotypes (post-coevolution)
- Compare frequencies to random genotypes of same length
- Compute enrichment ratios

**Measure**: Top enriched motifs. Do they correspond to functional fold patterns (e.g., "DaK" = get+price+>)?

### Experiment 3.2: Pleiotropy Per Mutation

**Hypothesis**: Evolved genotypes have lower pleiotropy than random genotypes — evolution has shaped the G-P map.

**Setup**:
- For each individual (evolved and random), apply 100 point mutations
- Count phenotypic traits changed per mutation: bonds formed, program output, active sites
- Compare distributions

**Measure**: Mean pleiotropy (traits changed per mutation) in evolved vs random. Altenberg predicts evolved < random.

### Experiment 3.3: Historical Contingency

**Hypothesis**: Folding produces more divergent evolutionary histories than direct encoding.

**Setup**:
- 50 independent runs per encoding, same parameters
- Measure: variance in final fitness, number of unique phenotypes at termination, Hamming distance between best genotypes across runs

**Analysis**: Higher variance in folding indicates the development process creates more contingent evolutionary paths.

## Priority 4: Coevolution Improvements

### Experiment 4.1: Context Variation Count

**Hypothesis**: More evaluation contexts create more diverse niches (up to a point).

**Setup**:
- 2, 3, 5, 10, 20 contexts
- Separated coevolution, 200 gens

**Measure**: Final niche count (unique phenotypes), average fitness, evaluation time. Find the sweet spot.

### Experiment 4.2: Novelty-Rewarded Testing

**Hypothesis**: Rewarding testers for unique output profiles (not just difficulty frontier) increases phenotype diversity.

**Setup**:
```python
test_score = 0.5 * frontier_score(pass_rate) + 0.5 * novelty_score
novelty_score = 1.0 - (fraction of other testers with same pass-rate profile)
```

**Measure**: Phenotype diversity vs generations. Compare to frontier-only scoring.

## Priority 5: Alternative Development Processes

### Experiment 5.1: Codon Table

**Hypothesis**: A codon table (3-character sequences map to program tokens) creates a different pleiotropy profile than 2D folding.

**Setup**:
- Same genotype strings, same alphabet, same genetic operators
- Instead of folding: read genotype in 3-char codons, map each to a program token
- Compare all metrics (neutrality, crossover, pleiotropy, regime shift adaptation)

### Experiment 5.2: Stack Machine

**Hypothesis**: A stack-based development process creates yet another dynamic profile.

**Setup**:
- Characters push/pop from a stack, building the program bottom-up
- Same comparison as above

### Experiment 5.3: GP Tree Representation (Baseline)

**Hypothesis**: Standard GP tree-based representation (as in DEAP) provides a well-understood baseline.

**Setup**:
- Use DEAP's standard GP tree representation with the same function/terminal set
- Run the same experiments (regime shift, coevolution, etc.)
- Compare: does the folding representation offer anything beyond standard GP?
