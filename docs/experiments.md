# Planned Experiments

Ordered by expected impact. Each experiment has a clear hypothesis and measurable outcome.

## Priority 1: Break the Complexity Ceiling

The single most important problem. Most complex evolved program is 3 bonds. 4+ bond programs never emerge through evolution despite being abundant in random genotypes.

### Status: Two-Constraint Decomposition

The complexity ceiling has been decomposed into two separate constraints through a comprehensive diagnostic series (see findings Section 6):

**Constraint 1 — Motif discovery: SOLVED.**
Chemistry screening (exhaustive bond-production scoring of all 242K length-2+3 substrings) identifies the critical building blocks endogenously: `QDa` rank #42, `Da` rank #135, `DaK` rank #186 — all in the top 0.08%. No evolution, no human domain knowledge needed. The fold/chemistry contains endogenous information about useful building blocks.

**Constraint 2 — Intermediate preservation: UNSOLVED.**
Even with the right motifs (screened or hand-coded), selection destroys S1/S2 carriers by generation 25 before they can combine into S3+ structures. Motif insertion creates raw material, but selection acts as a scrubber, not a ratchet. Higher average bonds (2.4 vs 1.4 baseline) without better S4/S5 confirms that more local chemistry is not enough — the problem is coordinated multi-motif co-localization and survival under selection.

### Completed Experiments

- **1.0: S3→S4 Transition Analysis** — DONE. S3→S4: 0.32%/mutation, S4→S5: 26.6%. Crossover: S3×random→S4 at 6.9%. The transitions are possible; S3 rarity is the bottleneck.
- **1.1: Module operators** — DONE. Motif insertion works (S3 5/20 seeds, S5 2/20 seeds). Generic dup/transpose doesn't help. Note: the S5 2/20 result was likely a rare-event regime, not a robust operator effect — later runs with identical hand-coded motifs yielded S5 0-1/20.
- **1.3: Archive reinjection** — DONE. Failed because S3 is too rare (0.04%) to archive.
- **1.4: Chemistry-aware duplication** — DONE. Failed. Bonded runs lack critical motifs (Da at 0.096% of runs, DaK at 0.001%). Cross-individual transfer also failed. Bonding is context-dependent — duplicating bonded substrings to new positions changes the fold context. See `exp_chemistry_aware_dup.py`.
- **1.5: Endogenous motif discovery** — DONE. Three approaches tested:
  - *Evolution-mined motifs*: FAILED. Easy tasks select for `BS` → `(count data/products)`, not for `Da`/`DaK`. Enriched substrings are hitchhikers, not functional motifs.
  - *Chemistry screening*: SUCCEEDED at discovery. Da/QDa/DaK in top 0.08% of 242K screened substrings. See `exp_learned_motifs.py`.
  - *Application phase*: All conditions (screened, hand-coded, random, baseline) statistically indistinguishable at 20 seeds. S1/S2 carriers erased by gen 25. The bottleneck shifted from motif supply to intermediate preservation.
- **1.8: Neutral drift phases** — DONE. **The strongest result in the project.** Pure drift phases (fitness = constant) transform the system from 0/20 S4 to 15/20 S4 and 0/20 S5 to 11/20 S5. Carrier lifetimes increase 3-6x, co-occurrence increases 11-83x. Weak selection (tournament_size=1) does NOT work — pure drift is required. See `exp_drift_preservation.py` and findings Section 6.

### Next Experiments (Priority 1)

With both constraints addressed (motif discovery + drift preservation), the ceiling is broken. Next experiments should consolidate the result and explore what it enables.

**1.9: Consolidation** — DONE. 50 seeds, pop=200, 500 gens. S3: 100%, S4: 92%, S5: 78%, filter programs: 72% of seeds. Result is robust. Genuine filter programs with `(get x :price)` evolve endogenously. See `exp_consolidation.py`.

With the ceiling broken and confirmed, the next experiments shift from "can we break through?" to "what does the breakthrough enable and how can the mechanism be refined?"

**1.11: Scaffold protection** — DONE. **Pareto surpasses drift.** Pareto(fitness, scaffold_stage) achieves S5 18/20 (90%) vs drift 8/20 (40%) vs baseline 0/20. Carrier lifetimes reach 302 gens (vs 34 drift, 5 baseline). Scaffolds accumulate monotonically to 56% of population at gen 299. Confirms the mechanism is specifically about preserving scaffold carriers. See `exp_scaffold_protection.py`.

**1.10: Endogenous motif screening during evolution**

Replace the offline chemistry screening with online motif scoring: every N generations, screen the most common 2-3 char substrings in the population, promote high-scoring ones to the motif insertion operator. This closes the loop — no pre-computed motif library needed. Combine with drift for the full endogenous pipeline.

**1.12: Generalization to different target programs**

Does drift+motifs break through on a DIFFERENT hard task (not just the filter chain)? Test with `(reduce (fn x (+ x ...)) 0 data)`, `(map (fn x (assoc x :key value)) data)`, or nested structures. If yes, the mechanism is general. If no, the chemistry screening is task-specific.

**1.6: Population-level motif ecology**

Keep a global motif pool updated from evolved populations. Now unblocked — drift provides the preservation layer.

**1.7: Hierarchical evolution**

Easy tasks evolve motifs, hard tasks consume and elaborate them. Now unblocked.

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
