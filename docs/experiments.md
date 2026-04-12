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

**1.13: Endogenous scaffold identification** — DONE. **Pareto(structural_pattern) works.** The field-agnostic, target-family-general AST objective nearly matches hand-coded scaffold_stage on price (18/20 vs 20/20 S5) AND transfers cleanly to amount target (17/20 filter programs). Motif-presence is weaker — arrangement matters, not just inventory. Claim upgraded to "semigeneric preservation of compositional intermediates works." See `exp_endogenous_scaffold.py`.

**1.11: Scaffold protection** — DONE. **Pareto surpasses drift.** Pareto(fitness, scaffold_stage) achieves S5 18/20 (90%) vs drift 8/20 (40%) vs baseline 0/20. Carrier lifetimes reach 302 gens (vs 34 drift, 5 baseline). Scaffolds accumulate monotonically to 56% of population at gen 299. Confirms the mechanism is specifically about preserving scaffold carriers. See `exp_scaffold_protection.py`.

**1.12: Generalization test** — DONE. Mixed result that sharpens the claim. Pareto(bond_count) generic metric helps (4/20 S5 vs 0/20 baseline) but much weaker than Pareto(scaffold_stage) (20/20 S5). On different target family (filter-amount), generic metric mostly inflates bonds without useful structure. The preservation mechanism needs a targeted objective — generic complexity alone is not a substitute. See `exp_generalization.py`.

### Priority Order for Next Experiments

After 1.13, the story is: discovery solved (chemistry screening), preservation solved semigenerically (structural_pattern Pareto). The remaining questions are (a) does preservation buy stored evolvability, and (b) can the preservation objective itself be learned from data? The recommended sequence:

1. **1.15 (DONE, needs scale-up)** — cryptic variation assay. First pass (15 seeds) supports transfer of preserved adaptive structure: Pareto reaches fitness ceilings continuous selection doesn't (≥0.8 in 4/60 vs 0/30) and adapts ~2x faster to mid-thresholds on T_far. Bimodal endpoints and plateau dynamics argue for *discrete inventory transfer*, not continuous latent variation. Follow-up: AUC reanalysis on existing data, then 30+ seed rerun with shorter checkpoints and a true far-transfer (reduce / nested filter).
2. **1.14 (next)** — lineage analysis. Mechanistic confirmation at individual level; also produces the dataset needed for 1.19.
3. **1.19** — learned preservation objective. Closes the last hand-coding loop.
4. **A2 ablation (external benchmark)** — folding × preservation × motifs ablation on hard problems. Answers "what is the paper actually about."
5. **1.16 / 1.17** — epistasis and modularity assays to sharpen existing findings.

---

**1.15: Cryptic variation assay — DONE (first pass; scale-up planned)**

First-pass result (15 seeds, snapshots at gens 200 and 300, 80-gen assay on T_near=filter-price-600 and T_far=filter-amount-300): Pareto-preserved populations reach fitness ceilings (≥0.8) in 4/60 seed-trials vs 0/30 for continuous selection; B_scaffold adapts ~2x faster to ≥0.6 on T_far than continuous (first-hit sequence B `[1,1,4,6,14,15,18,33]` vs A `[4,10,19,24,26,30,49]`). Endpoint distributions are bimodal; plateau dynamics dominate. Interpretation: discrete inventory transfer of compositional scaffolds, mechanistically distinct from Wagner/Kimura continuous standing variation. See findings Section 6 "Cryptic Variation Assay" and `exp_cryptic_variation.py`.

**Confound disclosed**: starting-structure imbalance (A: 0 scaffolds, B: 74 S5+/68 G5+, C: 16 S5+/87 G5+) means the result is a *transfer-of-preserved-structure* assay, not a clean latent-variation test. Average-case final-fitness advantage is modest (5–15%); ceiling access is clean.

**Follow-up plan (1.15b)**:
- AUC / recovery-slope reanalysis on existing trajectories (no new compute). Report fitness at checkpoints 10/20/40 to emphasize early adaptation.
- Rerun at 30+ seeds with 40-gen assay (not 80), shorter checkpoint schedule, and a genuine compositional-family far-transfer: `(reduce (fn a b (+ a (get b :price))) 0 data/products)` or nested filter-of-map.
- Optional matched-starting-fitness subpopulation analysis to partially disentangle preserved-scaffold-inventory from starting-fitness advantage.

**1.14: Lineage analysis of preservation breakthroughs**

Reconstruct the ancestry of successful S5 / filter-program individuals from 1.9, 1.11, and 1.13 runs. Also produces the training data for 1.19.

**Hypothesis**: Under Pareto preservation, breakthrough individuals have ancestors carrying S1 / S2 / S3 scaffolds for many generations before S4 / S5 appears. Under continuous selection, scaffold ancestors are absent or short-lived.

**Setup**:
- Add parent-pointer tracking to the evolution engine (one ID per individual, parent ID per child)
- Rerun selected conditions from 1.11 / 1.13 with lineage tracking enabled
- For each breakthrough individual at termination, trace parent pointers back to gen 0
- For each ancestor, classify scaffold stage
- Compute: generation of first S1/S2/S3 ancestor, dwell time per stage, number of independent S1 lineages feeding into the final genotype

**Measure**: Lineage depth of each scaffold stage, dwell time distributions, whether multiple independent S1/S2 lineages converge via crossover into the breakthrough individual.

**Why this matters**: Mechanistic confirmation at the individual / lineage level, not just population statistics. Also produces the dataset for 1.19 (substructure extraction from ancestry).

**1.19: Learned preservation objective (fully endogenous pipeline)**

The final endogenous step. The `structural_pattern` objective in 1.13 was a human-engineered hypothesis about what "compositional form" means. This experiment *learns* the preservation objective from lineage data, closing the last hand-coding loop.

**Hypothesis**: AST substructures that repeatedly appear in ancestors of breakthrough individuals across *multiple* target families can be extracted and clustered into a preservation template that matches or exceeds hand-coded `structural_pattern` on a *held-out* target family.

**Setup**:

1. **Discovery runs** (uses 1.14 lineage data):
   - Pareto(structural_pattern) on three training target families: filter-price, filter-amount, filter-department
   - For each seed with a breakthrough, trace ancestors of the breakthrough individual

2. **Substructure extraction**:
   - Extract all AST subtrees of depth 2–3 from ancestor programs
   - Normalize: replace specific symbols with type placeholders (`:price` → `:FIELD`, `data/products` → `data/ANY`, specific literals → `NUM`)

3. **Precedence scoring**:
   - For each normalized substructure S: score = P(S appears in ancestor | breakthrough) vs P(S appears in random ancestor from same run)
   - High precedence = S is predictive of future breakthrough
   - **Critical**: hold out at least one target family entirely during discovery to prevent circularity

4. **Cross-family filtering**:
   - Keep templates that score high in multiple target families (cross-generalizing)
   - Drop templates that only appear in one family (task-specific artifacts)

5. **Application on held-out target** (e.g., filter-category, reducer, or map variant):
   - A. Continuous selection (baseline)
   - B. Pareto(structural_pattern) — 1.13 hand-coded baseline
   - C. Pareto(learned_templates) — fully endogenous

**Measure**: Filter programs / S5-equivalent rate per condition on held-out target. If C matches or exceeds B, the pipeline is fully endogenous end-to-end.

**Why this matters**: Closes the last piece of human scaffold engineering. Chemistry screening is endogenous; motif insertion is endogenous; this makes the preservation objective endogenous. Also tests whether "higher-order + predicate + data" is the only template that matters, or whether learning surfaces additional compositional patterns that hand-coding missed.

**Failure modes to watch**:
- *Circularity*: if "precedence" is measured against current-task success, we re-encode target knowledge. Mitigation: held-out target family is not in discovery set.
- *Granularity*: depth-2 substructures may be too specific (many near-duplicates), depth-4 too sparse. Normalize aggressively and evaluate both.
- *Too few breakthroughs*: if training data is insufficient, relax "breakthrough" threshold from "full filter program" to "S3+ emergence."
- *Scale mismatch in Pareto sort*: learned templates might produce a wider objective range than structural_pattern (5 levels). Normalize to comparable ranges.

**What this might reveal** beyond matching structural_pattern: unexpected templates like "predicate with two accessors," "nested higher-order," or "fn-wrapped constant" that matter for some tasks but weren't in the hand-coded hypothesis.

**1.10: Endogenous motif screening during evolution**

Replace the offline chemistry screening with online motif scoring: every N generations, screen the most common 2-3 char substrings in the population, promote high-scoring ones to the motif insertion operator. This closes the loop — no pre-computed motif library needed. Combine with preservation for the full endogenous pipeline.

**1.20: Generalization to different target program families**

(Separate from 1.12, which tested filter-amount within the filter family.) Does Pareto preservation break through on structurally different target programs — `(reduce (fn x (+ x ...)) 0 data)`, `(map (fn x (assoc x :key value)) data)`, or nested structures? If yes, the mechanism is general. If no, the chemistry screening and/or structural_pattern template is specific to the filter family.

**1.6: Population-level motif ecology**

Keep a global motif pool updated from evolved populations. Now unblocked — preservation provides the persistence layer.

**1.7: Hierarchical evolution**

Easy tasks evolve motifs, hard tasks consume and elaborate them. Now unblocked.

**1.16: Motif-pair and motif-triple epistasis**

Measure whether useful motifs contribute additively, synergistically, or context-dependently to scaffold formation.

**Hypothesis**: The fitness / bond contribution of any single motif (e.g., `Da`) depends strongly on whether other motifs (`QDa`, `DaK`, `AS`, `BS`) are nearby on the genotype. Motif effects are non-additive; composition requires co-localization.

**Setup**:
- Use the chemistry-screened motif set from 1.5 plus hand-coded motifs (`Da`, `QDa`, `DaK`, `AS`, `BS`, `K5`)
- For each motif pair (A, B) and a subset of triples:
  - Insert A alone, B alone, and A+B into 1000 random genotype backgrounds at length 100
  - Score each background for: bond count, scaffold stage (S1–S5), program fitness
- Compute: expected effect under additivity (effect(A) + effect(B)), observed effect (effect(A+B)), epistasis = observed − expected

**Measure**: Epistasis distribution across motif pairs. Per-pair synergy score. Identify "compositional partners" (large positive epistasis) vs "interchangeable" vs "antagonistic."

**Why this matters**: 1.4 showed bonding is context-dependent — this quantifies it at the motif level. Tests the compositional claim that breaks from "motifs help" into "which motifs help *together*." Informs whether the motif-presence Pareto proposed in 1.13 should count motifs independently or score co-presence.

**1.17: Trait dissociation assay**

Lightweight modularity proxy: can one phenotypic subtree be mutated independently of another?

**Hypothesis**: In scaffold-carrying genotypes, comparator threshold, field accessor, and wrapper structure can be mutated independently — the folding representation produces module-like dissociability even without explicit modular structure.

**Setup**:
- Start from S4 / S5 carrier genotypes (seeded and evolved)
- Define three target traits:
  - Threshold value (e.g., 500 in `(> ... 500)`)
  - Field accessor (`:price` vs `:amount` vs other keys)
  - Wrapper (filter vs filter+count; fn wrapper present or absent)
- For each genotype, apply 500 point mutations and classify each mutation by which traits changed (possibly multiple)
- Compute: pairwise co-change frequency between traits, conditional probabilities (P(trait_b changed | trait_a changed))

**Measure**: Trait dissociation index = fraction of mutations changing exactly one trait. Compare evolved scaffold carriers vs random genotypes with matched bond counts. Low co-change = modular; high co-change = pleiotropic tangles.

**Why this matters**: Gives a principled modularity statement without full biological network machinery. If evolved scaffolds show higher dissociation than matched random controls, that is constructional selection reshaping the GP map. If not, the "modular scaffold" framing needs softening.

**1.18: Direct pleiotropy-per-mutation on evolved populations**

Promote the existing 3a / 3.2 plan to Priority 1.

**Hypothesis**: Evolved folding populations have lower mutational pleiotropy than random genotypes (Altenberg's prediction). Shift-evolved populations may show *higher* pleiotropy than stable-evolved populations (selection maintained exploratory capacity).

**Setup**:
- For each individual in four populations (random, stable-evolved folding, shift-evolved folding, continuous-selection filter-evolved), apply 100 point mutations
- Count phenotypic traits changed per mutation: bond count, program AST depth, program output on fixed context set, active program sites (positions that contribute to output)
- Compute distributions per condition

**Measure**: Mean and variance of pleiotropy per mutation per condition. Compare with Wilcoxon rank-sum. Report distribution shape, not just the mean.

**Why this matters**: Right now pleiotropy is inferred from neutrality and large-break rates. A direct assay tightens the Altenberg claim. Supporting, not central, to the preservation story — but needed if the paper frame retains the evolvability connection.

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
