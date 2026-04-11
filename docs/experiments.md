# Planned Experiments

Ordered by expected impact. Each experiment has a clear hypothesis and measurable outcome.

## Priority 1: Break the Complexity Ceiling

The single most important problem. Most complex evolved program is 3 bonds. 4+ bond programs never emerge.

### Experiment 1.1: Scale Up

**Hypothesis**: Longer genotypes + larger populations + more generations produce 4+ bond programs.

**Setup**:
- Genotype length: 80, 100, 150
- Population: 100 per role (300 total for separated coevolution)
- Generations: 500, 1000
- 3 context variations
- Data-dependence gate on

**Measure**: Max bond count, average bond count, distribution of bond counts over generations. Target: first 4+ bond program observed, generation of first appearance.

**Rationale**: Length 50 already showed max 11 bonds in random genotypes (avg 3.2). Evolution at length 50 achieved max 4.2 avg. Longer genotypes should provide more bonding opportunities, and larger populations + more generations should find them.

**This is the experiment the Elixir implementation couldn't run** due to eval speed (10,900 evals/sec). At 300 individuals x 10 samples x 3 contexts x 1000 gens = 9M evals. PTC-Lisp: ~14 minutes. Python with NumPy batch eval should be seconds-to-minutes.

### Experiment 1.2: Seeded Complexity

**Hypothesis**: Seeding populations with known 4-bond genotypes allows evolution to maintain and improve complex programs.

**Setup**:
- Find/construct genotypes that fold into 4+ bond programs (e.g., filter+fn+predicate+data)
- Seed 10% of each population with these genotypes
- Run separated coevolution, measure whether complexity is maintained or decays

**Measure**: Average bond count over generations. Does it stay at 4+ or decay to 2-3?

### Experiment 1.3: Complexity-Biased Selection

**Hypothesis**: Adding a complexity bonus to fitness rewards more complex programs without destroying coevolution dynamics.

**Setup**:
```python
fitness = base_fitness + lambda_complexity * bond_count
```

**Measure**: Average bond count vs lambda_complexity. Find the sweet spot where complexity increases without selection pressure collapsing to "build the longest program regardless of correctness."

## Priority 2: Validate Dynamic Findings at Scale

The regime shift result (folding wins on dynamics) was measured at small scale (pop=50, len=30, 3 runs). Need statistical confidence.

### Experiment 2.1: Regime Shift with Statistical Power

**Hypothesis**: Folding's dynamic advantage holds across many seeds and larger populations.

**Setup**:
- 30 independent runs per encoding (folding vs direct)
- pop=100, genotype_length=50
- Regime A: 30 gens, Regime B: 50 gens
- Measure: pre-shift fitness, post-shift drop, recovery rate, final fitness, fitness jumps

**Analysis**: Wilcoxon rank-sum test on final fitness. Report effect size and confidence intervals.

### Experiment 2.2: Continuous Regime Shifts (Red Queen)

**Hypothesis**: Folding's advantage grows under repeated environmental changes.

**Setup**:
- Shift target problems every N generations (N = 5, 10, 20, 50)
- 500 total generations
- Compare folding vs direct encoding: average fitness, adaptation lag after each shift

**Measure**: Time to recover 80% of pre-shift fitness after each shift. Does adaptation lag decrease over time (learning to adapt)?

### Experiment 2.3: Stabilizing vs Directional Selection

**Hypothesis**: Direct encoding wins under stable targets; folding wins under shifting targets. (Altenberg's prediction.)

**Setup**:
- Condition A: Fixed target for 200 gens (stabilizing)
- Condition B: Target shifts every 10 gens (directional)
- 20 runs per condition per encoding

**Measure**: Final fitness in both conditions. Interaction effect (encoding x condition).

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
