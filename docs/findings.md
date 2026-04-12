# Research Findings

All data from the Elixir/PTC-Lisp implementation (pop=40-50, genotype_length=10-50, 20-200 generations, 3 context variations).

## 1. Validity Rate is Near 100%

Random genotypes of any length almost always produce some valid program fragment. Even a single data source character or literal counts. The interesting metric is not validity but *complexity* — how many bonds form and whether the resulting program uses higher-order functions.

## 2. Static Metrics: Folding vs Direct Encoding

Matched comparison using identical genotypes, same alphabet, same operators. Only difference: genotype-to-phenotype mapping.

### Neutral Mutation Rate

| Length | Folding (phenotype) | Direct (phenotype) | Folding (behavioral) | Direct (behavioral) |
|--------|--------------------|--------------------|---------------------|---------------------|
| 10     | 60%                | 69%                | 61%                 | 84%                 |
| 20     | 66%                | 83%                | 69%                 | 89%                 |
| 30     | 69%                | 85%                | 76%                 | 92%                 |
| 50     | 70%                | 87%                | 76%                 | 97%                 |

**Direct encoding has substantially higher neutrality.** At length 50: 87% vs 70% phenotype, 97% vs 76% behavioral. This is the *opposite* of the original hypothesis.

**Why?** In direct encoding, mutations to late-genotype characters only affect the expression tail. In folding, a mutation anywhere can rearrange the entire 2D grid topology, breaking or creating bonds far from the mutation site. Folding creates **pleiotropy**, not neutrality.

### Mutation Effect Spectrum

| Length | Metric       | Folding | Direct |
|--------|-------------|---------|--------|
| 10     | Neutral      | 62%     | 78%    |
| 10     | Large break  | 37%     | 17%    |
| 10     | Beneficial   | 1%      | 5%     |
| 50     | Neutral      | 73%     | 94%    |
| 50     | Large break  | 24%     | 2%     |
| 50     | Beneficial   | 3%      | 4%     |

Folding has **5-12x more large breaks**. When a folding mutation is non-neutral, it's almost always catastrophic. The landscape is cliff-like: most mutations absorbed, but the non-neutral ones are destructive.

### Crossover Preservation

| Length | Folding (behavioral) | Direct (behavioral) |
|--------|---------------------|---------------------|
| 10     | 51%                 | 85%                 |
| 20     | 60%                 | 94%                 |
| 30     | 55%                 | 92%                 |
| 50     | 43%                 | 97%                 |

Direct encoding preserves crossover behavior 2x better. Gap widens with length.

### Complexity

| Length | Folding (avg program size) | Direct (avg program size) |
|--------|---------------------------|---------------------------|
| 10     | 7.8                       | 17.0                      |
| 20     | 11.1                      | 18.6                      |
| 30     | 15.7                      | 26.7                      |
| 50     | 16.8                      | 34.4                      |

Direct encoding produces 2x more complex phenotypes because it consumes characters sequentially.

### Bond Count (Folding Only)

| Length | Avg bonds (random) | Avg bonds (evolved) | Max bonds (random) | Max bonds (evolved) |
|--------|-------------------|--------------------|--------------------|---------------------|
| 10     | 0.35              | 1.05               | 5                  | 2                   |
| 20     | 1.02              | 1.77               | 4                  | 4                   |
| 30     | 1.40              | 1.43               | 4                  | 4                   |
| 50     | 3.23              | 4.22               | 8                  | 11                  |

**Length 50 is the sweet spot**: avg 3.2 bonds random, 4.2 evolved, max 11.

## 3. Dynamic Metrics: Regime Shift Experiment

The decisive test. Train both representations on target problems (Regime A), shift to different targets (Regime B), measure adaptation. pop=50, genotype_length=30, 3 runs averaged.

```
  Gen | Fold fit | Dir fit  | Phase
  ----+----------+----------+------
    0 |    0.071 |    0.050 | A
    3 |    0.661 |    0.100 | A       <- folding finds solutions
    5 |    0.792 |    0.100 | A       <- folding converged; direct stuck
   20 |    0.792 |    0.100 | A <<< REGIME SHIFT
   21 |    0.490 |    0.100 | B       <- folding drops, starts recovering
   30 |    0.626 |    0.100 | B       <- folding recovering
   40 |    0.667 |    0.100 | B       <- folding adapted; direct unchanged

  Pre-shift fitness:   Folding 0.792   Direct 0.100
  Post-shift drop:     Folding 0.302   Direct 0.000
  Final fitness:       Folding 0.667   Direct 0.100
  Recovery:            Folding 0.177   Direct 0.000
  Fitness jumps:       Folding 5       Direct 0
```

**Folding dramatically outperforms on evolutionary dynamics.** Direct encoding never gets above 0.1 — it cannot discover target programs. Folding discovers them by gen 3 and recovers from regime shifts.

**Why direct encoding fails**: It reads left-to-right, so the root expression is locked by position 0. Most mutations change the deeply nested tail with no output effect. The high neutrality is actually **evolutionary inertia** — the representation is too canalized.

**Why folding succeeds**: Characters need spatial adjacency, not sequential position. A mutation anywhere can shift the fold topology, bringing functional characters together. The 5 fitness jumps are punctuated reorganizations — the pleiotropy that looked bad in static metrics enables structural innovation.

## 4. Revised Assessment

| Metric | Static winner | Dynamic winner | Resolution |
|--------|--------------|---------------|------------|
| Neutrality | Direct (87%) | Folding | Direct's neutrality is inertia, not robustness |
| Crossover preservation | Direct (97%) | Folding | Direct preserves behavior that was never fit |
| Mutation break rate | Direct (2%) | Folding | Folding's breaks include beneficial reorganizations |
| Task performance | — | Folding (0.79) | Direct never discovers solutions (0.10) |
| Adaptation speed | — | Folding | Recovers from regime shift; direct doesn't |

**The original hypothesis (folding increases neutrality) was wrong. The reframed finding: folding's pleiotropy enables qualitatively different evolutionary dynamics — punctuated equilibrium, structural reorganization, and regime-shift adaptation.**

## 5. The 2x2 Experiment: Representation x Selection Regime

Updated Python sweep using the Rust-accelerated backend. Design: `(folding vs direct) x (stable vs shifting)` with repeated regime shifts rather than a single one-shot change.

**Setup**:
- Population: 100
- Generations: 200
- Seeds: 20 per condition
- Stable target: products-focused multi-target fitness
- Shifting target: alternate between products-focused and employees-focused target sets
- Genotype lengths: 50 and 80
- Shift frequencies: every 20 or 50 generations

### Stable Controls

| Length | Folding avg final | Direct avg final | Folding avg bonds | Direct avg bonds |
|--------|-------------------|------------------|-------------------|------------------|
| 50     | 0.588             | 0.547            | 1.45              | 1.85             |
| 80     | 0.588             | 0.469            | 1.80              | 1.40             |

The stable control does not show a crossover where direct wins. Folding is modestly ahead at length 50 and clearly ahead at length 80.

### Periodic Shift Results

| Shift every | Length | Folding final | Direct final | Folding avg best | Direct avg best |
|-------------|--------|---------------|--------------|------------------|-----------------|
| 20          | 50     | 0.519         | 0.467        | 0.515            | 0.350           |
| 20          | 80     | 0.531         | 0.397        | 0.510            | 0.304           |
| 50          | 50     | 0.531         | 0.490        | 0.530            | 0.379           |
| 50          | 80     | 0.515         | 0.436        | 0.515            | 0.311           |

The clearest separation is **length 80 with shifts every 20 generations**.

### Drop and Recovery

| Shift every | Length | Encoding | Avg drop after shift | Avg recovery before next shift |
|-------------|--------|----------|----------------------|--------------------------------|
| 20          | 50     | Folding  | 0.247                | 0.242                          |
| 20          | 50     | Direct   | 0.151                | 0.178                          |
| 20          | 80     | Folding  | 0.251                | 0.247                          |
| 20          | 80     | Direct   | 0.103                | 0.124                          |
| 50          | 50     | Folding  | 0.276                | 0.257                          |
| 50          | 50     | Direct   | 0.195                | 0.241                          |
| 50          | 80     | Folding  | 0.260                | 0.239                          |
| 50          | 80     | Direct   | 0.154                | 0.214                          |

Folding takes larger fitness drops because it reaches stronger pre-shift solutions, but it also recovers more of that loss within each regime window. Direct is more inert: smaller drops, weaker recovery, lower mean fitness over time.

### Fitness Jumps and Complexity

| Shift every | Length | Folding jumps | Direct jumps | Folding avg bonds | Direct avg bonds |
|-------------|--------|---------------|--------------|-------------------|------------------|
| 20          | 50     | 9.3           | 7.5          | 1.90              | 1.75             |
| 20          | 80     | 9.5           | 5.5          | 2.55              | 1.95             |
| 50          | 50     | 3.85          | 3.60         | 2.10              | 1.95             |
| 50          | 80     | 3.70          | 2.90         | 2.25              | 1.65             |

At length 80, folding evolves both more punctuated dynamics and higher bond counts than direct encoding.

### Interpretation

This sweep updates the earlier, stronger “folding adapts while direct does not” claim.

1. **The interaction is present, but weaker than the original Elixir result suggested.** Direct does adapt under repeated shifts; it is not flatlined at a 0.1 floor.
2. **Folding still has the better dynamic profile.** It maintains higher mean fitness over time, especially under frequent shifts, and this gap widens at length 80.
3. **Longer genotypes help folding more than direct.** The length-80 runs increased folding bond counts and improved the separation under shifting regimes.
4. **The best current condition is length 80, shift every 20 generations.** This is the right default for larger follow-up sweeps (50+ seeds, larger populations).

## 6. Complexity Ceiling Diagnostics

A series of experiments investigating why evolution plateaus at 3 bonds and what interventions could break through to 4+ bond programs like `(count (filter (fn [x] (> (get x :price) 200)) data/products))`.

### C1: Random Bond-Count Survey

100,000 random genotypes per length. The representation CAN produce high-bond programs abundantly.

| Length | Avg bonds | 4+ bonds % | Max bonds |
|--------|-----------|------------|-----------|
| 50     | 2.64      | 22.9%      | 35        |
| 80     | 3.41      | 37.6%      | 34        |
| 100    | 3.82      | 46.0%      | 33        |
| 150    | 4.62      | 62.4%      | 38        |
| 200    | 5.23      | 74.0%      | 45        |

**The ceiling is not a representation problem.** Random genotypes produce 4+ bond programs at high rates. Evolution doesn't find/keep them because current tasks don't require them.

### C2: Reverse-Engineering 4-Bond Genotypes

The known 4-bond genotype `QDaK5XASBw` → `(filter (fn x (> (get x :price) 500)) data/products)` is robust: 44% of single mutations maintain 4 bonds, 5% improve to 5 bonds. Extending by 5 random characters keeps 99.2% at 4+. Hand-crafted `BASQDaK5CeTb` produces a 5-bond `(count (filter ...))`.

### Task Difficulty Verification (Exact Match)

Tested whether candidate tasks genuinely require high bond counts. Used 8 discriminating contexts with exact-match scoring on 100K random genotypes at length 100.

| Task | Intended bonds | Min bonds for 75% exact | Min bonds for 100% exact |
|------|---------------|------------------------|-------------------------|
| count(products) | 2 | 1 | 1 |
| count(rest(products)) | 3 | 2 | 2 |
| count(filter(price>200, products)) | 5 | NONE | NONE |
| count(filter(price>500, products)) | 5 | NONE | NONE |
| count(filter(amount>300, orders)) | 5 | 4 (accidental) | NONE |

**Filter tasks are verified hard.** No random genotype at any length achieved even 75% exact match. The best accidental match is 5/8 via `count(rest(rest(products)))` which happens to correlate on some contexts. The gap from 5/8 to 8/8 requires the actual filter expression — a structural leap, not an incremental improvement.

### Distance-2 Bond Diagnostic

Tested whether allowing bonds between characters at Chebyshev distance 2 (16 additional neighbors beyond the standard 8) increases bond counts.

| Length | Avg bonds (d1→d2) | 4+ % (d1→d2) | Max bonds (d1→d2) |
|--------|-------------------|---------------|-------------------|
| 50     | 2.64 → 4.58 (+73%) | 22.9% → 52.8% | 35 → 40 |
| 80     | 3.41 → 5.77 (+69%) | 37.4% → 63.9% | 30 → 54 |
| 100    | 3.82 → 6.40 (+68%) | 45.9% → 68.9% | 33 → 58 |
| 150    | 4.63 → 7.57 (+64%) | 62.5% → 77.7% | 38 → 70 |

Distance-2 bonds increase avg bond count by ~70% and dramatically increase the 4+ bond rate. The golden 4-bond genotype is unchanged (already compact). Mutation robustness improves: 5+ bond mutants double (30→61).

### Evolvable Chemistry (Stage 1)

Built a DevGenome system: evolvable chemistry parameters (distance weights, bond affinities, stability) that control the assembly process. Population-level evolution: one shared DevGenome mutated every N generations.

**Result on easy tasks** (count, rest, first): Evolvable chemistry matched baseline fitness. d2 weight did not evolve from 0.0 (initialization bug — gaussian sigma too small from zero). Forced d2=1.0 increased bond counts (avg 1.5→3.8) but not fitness — extra bonds were structural noise, not useful programs.

### Staged Curriculum Experiment

Three-phase curriculum: easy tasks (gen 0-50) → easy+hard (50-150) → hard only (150-200). Three conditions: fixed d1, fixed d2=0.3, evolvable d2.

| Condition | Best fit | Avg bonds | 4+ bonds % | Hard exact avg |
|-----------|----------|-----------|------------|----------------|
| Fixed d1-only | 0.574 | 3.1 | 38% | 0.438 |
| Fixed d2=0.3 | 0.487 | 4.2 | 60% | 0.325 |
| Evolvable d2 | 0.549 | 4.3 | 65% | 0.400 |

d2 increased bond counts but not fitness. The evolvable condition DID evolve d2 upward (seeds reaching 0.76 and 0.86), confirming the chemistry can evolve. But best programs were still rest-chain shortcuts (`count(rest(rest(...)))`) scoring via accidental numeric correlation, not filter expressions.

**Key finding:** the curriculum creates pressure, and the chemistry can evolve, but the objective cannot distinguish "structurally correct" from "numerically lucky" well enough. Evolution finds shortcuts instead of compositional solutions.

### Structural Staircase + Lexicase Selection

Tested whether a structurally informed fitness function (rewarding numeric type, plausible range, numeric closeness, exact match) combined with lexicase selection (preserving specialists on anti-alias contexts) could guide evolution past shortcuts.

| Condition | Avg fit | Avg bonds | Hard exact | Filter programs |
|-----------|---------|-----------|------------|-----------------|
| Baseline (partial + tournament) | 0.573 | 2.9 | 0.425 | 1/10 (trivial) |
| Staircase + tournament | 0.568 | 2.5 | 0.425 | 0/10 |
| Partial + lexicase | 0.504 | 2.5 | 0.344 | 0/10 |
| Staircase + lexicase | 0.502 | 4.1 | 0.356 | 0/10 |

**None of the selection/objective interventions helped.** Lexicase actually reduced fitness by preserving specialists that solve individual contexts accidentally. The structural staircase rewarded the same intermediates as partial credit because both rest-chains and filter programs are numeric, in-range, and close to target.

**The gap between rest-chains and filter programs is structural, not selective.** No smooth path exists in the current representation from `count(rest(rest(products)))` to `count(filter(fn [x] (> (get x :price) 200)) data/products)`. These are qualitatively different program structures requiring different spatial arrangements on the 2D grid. No amount of selection refinement bridges this gap — it requires a qualitative structural leap in the genotype.

### Substructure Frequency Analysis

Scanned random genotypes and evolved populations for components of the target filter program. Individual building blocks are common in random genotypes at length 100:

| Substructure | Random freq | Description |
|---|---|---|
| `(get x :KEY)` | 41.5% | Accessor + field bond |
| `(> EXPR VALUE)` | 71.9% | Comparator expression |
| `(> (get x :KEY) VALUE)` | 11.9% | Comparator with get operand |
| `(fn x EXPR)` | 50.5% | Fn wrapper |
| `(fn x (> (get x :KEY) VALUE))` | 0.8% | Full predicate |
| `(filter (fn ...) DATA)` | 6.7% | Higher-order with fn |
| `filter(fn(comparator(get)))` | 0.1% | Complete filter chain minus count |

**The pipeline narrows exponentially at each combination step**: 42% → 12% → 0.8% → 0.1%.

**Selection destroys the useful intermediates.** In evolved populations, comparator-based predicates (`fn(comparator)`) drop from 8.2% to 0.2% over 200 generations. Meanwhile, trivially-true filters (`filter(fn x 400)`) are selected FOR (1.8% → 29.4%). Selection replaces useful predicates with trivial constants because trivial filters produce the same output as `count(products)`.

The full chain `filter(fn(>(get x :price) VALUE))` was **never observed** in any evolved individual across any seed at any generation.

### Seeded Module Elaboration

Tested whether evolution can grow partial filter substructures into complete programs when seeded into 20% of the population. Four progressive stages:

| Stage | Core genotype | Program | Bonds |
|---|---|---|---|
| S1 | `Da` | `(get x :price)` | 1 |
| S2 | `DaK5` | `(> (get x :price) 500)` | 2 |
| S3 | `QDaK5` | `(fn x (> (get x :price) 500))` | 3 |
| S4 | `QDaK5XAS` | `(filter (fn x (> (get x :price) 500)) data/products)` | 4 |

**Results: seeded modules degrade.** Every substructure was eliminated within 10-25 generations. Even the complete S4 filter program was replaced by `count(products)` in all but one seed. The seeded `(get x :price)` dropped from 5.0 to 0.0 individuals. `(fn x (> (get x :KEY) VALUE))` dropped from 1.0 to 0.0.

### Breakthrough: Seeded S4 Can Sweep Under Right Conditions

One critical exception: **Original fitness, S4 seeded, seed 7** — the complete `count(filter(fn x (> (get x :price) 200)) data/products)` program evolved from the seeded S4 genotype and swept the entire population (100/100 individuals by gen 16). Best fitness 0.832, the highest ever observed.

What happened: the seeded S4 genotype `QDaK5XAS` (threshold 500) mutated to threshold 200, producing the exact target program. This scored 0.832 as a numeric output, beating all rest-chain shortcuts (0.769), and swept via selection.

**Key comparisons:**

| Condition | Full filter chain ever found? | Peak count |
|---|---|---|
| Original fitness, S4 seeded | YES — seed 7 gen 16 | 100/100 individuals |
| Aligned fitness, S4 seeded | YES — seed 6 gen 8 | 44/100 individuals |
| Aligned fitness, S3 seeded | NEVER | 0 |
| Aligned fitness, no seeding | NEVER | 0 |
| Any unseeded condition ever | NEVER | 0 |

**The S3→S4 gap is the critical structural bottleneck.** S3 (fn+predicate) never elaborates into S4 (filter+fn+data) because the filter character must appear adjacent to both the fn-expression and a data source on the 2D grid — a spatial conjunction that requires coordinated multi-character changes, not incremental mutation.

**Once the complete filter program exists and produces the correct numeric output, selection maintains it enthusiastically.** The problem is not maintenance but discovery of the required spatial arrangement.

### Aligned Compositional Fitness

Tested whether rewarding list-valued filter intermediates (via `count(output)` fallback when output is list and target is numeric) would prevent anti-selection of filter programs.

The filter program `(filter (fn x (> (get x :price) 500)) data/products)` scored 0.050 under original fitness (wrong-type floor for list output vs numeric target) but 0.428 under aligned fitness. However, this also rewarded trivially-true filters at high scores, creating a new deceptive attractor. The aligned fitness did not break through on its own — the critical factor was having the correctly-thresholded `count(filter(...))` which already returns a number.

### S3→S4 Transition Analysis

Systematic mutation and crossover probing to map the exact probability of each structural step. Results from commit 38f4a90.

**Core genotype transitions (short, no padding):**

| Transition | Point mutation rate | Insertion rate | Key mechanism |
|---|---|---|---|
| S1→S2 | 0.00% | — | Impossible: can't add comparator by changing 2 chars |
| S2→S3 | 0.00% | 1.61% | Insert `Q` at pos 0 |
| S3→S4 | **0.00%** | — | Impossible: need filter+data, can't grow by mutation |
| S4→S5 | **0.41%** | 0.72% | pos 5: X→B gives `(count (filter ...))` |

**S3→S4 via genotype extension:** appending just 2 characters `AS` (filter + data/products) to the S3 core `QDaK5` produces the full S4 at **0.83%** (32/3844 extensions). The fold topology naturally places the fn-expression where filter can bind it.

**Padded genotype transitions (length 100, realistic):**

| Transition | Mutation rate | Interpretation |
|---|---|---|
| S3 maintained | 80.2% | S3 is robust in padded context |
| S3→S4 (full chain) | **0.32%** (~1 in 310) | Achievable per mutation |
| S4 maintained | 53.4% | S4 is moderately robust |
| S4→S5 (count wrapper) | **26.6%** (~1 in 4) | Nearly automatic |

**Crossover combinations:**

| Pairing | → S4 (full) | → S5 (full target) |
|---|---|---|
| S3 × random | **6.9%** | 0.06% |
| S4 × random | 13.9% | **24.5%** |
| S3 × S4 | 12.2% | 0.55% |

**Key finding:** S3→S4 is NOT structurally impossible — it occurs at 0.32% per point mutation on padded genotypes. S4→S5 is nearly automatic at 26.6%. **The real bottleneck is that S3 carriers are too rare to begin with.** S3 frequency in random genotypes: **0.04%** (4/10,000). In pop=100, expected S3 carriers: ~0.04 per generation.

### Archive Reinjection

Tested whether preserving and reinjecting scaffold carriers from an archive would allow the S3→S4 transition to fire. 20 seeds, 300 generations.

**Result: no improvement.** S4 was NEVER found in either condition (0/20 seeds each). The archive had nothing to archive because S3 carriers barely exist in random populations (0.04%). The archive mechanism is sound in principle but requires scaffold carriers to exist first.

### Module-Generating Operators

Tested whether new variation operators could increase scaffold assembly frequency. Three conditions: standard operators, +substring duplication/transposition, +known-motif insertion.

**Random walk results (50 operator steps on random genotypes):**

| Operator | S3 freq at step 0 | S3 freq at step 49 | S4 at step 49 | S5 at step 49 |
|---|---|---|---|---|
| Standard | 0.1% | 0.1% | 0.0% | 0.0% |
| + Dup/transpose | 0.1% | 0.0% | 0.0% | 0.0% |
| **+ Motif insertion** | **0.6%** | **10.3%** | **1.2%** | **0.7%** |

Motif insertion raises S3 density by **250x** (0.04% → 10.3%). The known-useful motifs (`Da`, `DaK`, `QDa`, `AS`, `BS`) create the spatial density of useful characters needed for the chemistry to assemble higher-level scaffolds.

**Evolutionary results (pop=100, 300 gens, 20 seeds, with archive):**

| Condition | S3 found | S4 found | S5 found |
|---|---|---|---|
| Standard operators | 2/20 | 0/20 | 1/20 |
| + Dup/transpose | 2/20 | 0/20 | 0/20 |
| **+ Motif insertion** | **5/20** | **1/20** | **2/20** |

**Motif insertion seed 13: the first unseeded breakthrough.** `count(filter(fn x (> (get x :price) 200)) data/products)` evolved at gen 200 and scored 0.832 — the correct target program, discovered without seeding the S4 genotype. The motif insertion operator supplied the building blocks; the folding chemistry assembled them; selection amplified the result.

Generic substring duplication/transposition did NOT help (same as baseline). The system is not bottlenecked on "more rearrangement" — it is bottlenecked on specific reusable motifs.

### Revised Complexity Ceiling Assessment

The complexity ceiling is a **building-block supply problem**:

1. **The representation can express complex programs** — 4+ bond programs are abundant in random genotypes (23-74%).
2. **Selection maintains them once found** — the S4 filter program swept to fixation when it appeared.
3. **Individual building blocks are discoverable** — S1 at 1.2%, S2 at 0.8% of random genotypes.
4. **The S3→S4 transition is achievable** — 0.32% per mutation on verified S3 carriers. S4→S5 is nearly automatic (26.6%).
5. **But S3 carriers are too rare (0.04%) for the transition chain to fire.** Standard variation operators do not generate useful motifs at sufficient frequency. The combination pipeline narrows exponentially: 42% → 12% → 0.8% → 0.1% at each assembly level.
6. **Supplying known-useful motifs raises scaffold density dramatically** (S3: 250x increase) and enables the full target program to evolve without direct seeding (2/20 seeds, including fitness 0.832 breakthrough).

The analogy to biology: innovations arise from reuse of conserved, historically selected building blocks (domains, motifs, regulatory elements), not from random sequence variation. Generic duplication doesn't help; biased, functional duplication does.

### Endogenous Motif Discovery (Experiment 1.5)

Three approaches were tested to make motif supply endogenous rather than hand-coded.

**Chemistry-aware duplication (option D): FAILED.** Bonded runs in random genotypes are abundant (6.5 per genotype, avg length 3.0) but lack the critical motifs: `Da` appears in only 0.096% of bonded runs, `DaK` in 0.001%. Even the refined approach (duplicating contiguous bonded runs rather than arbitrary substrings) showed no improvement over baseline. Cross-individual bonded-run transfer also failed. The fundamental issue: bonding is context-dependent — a substring bonds at position X because of the fold topology at X. Copying it elsewhere changes the fold context entirely. The motif insertion approach works because sequences like `Da` encode fold instructions that CREATE the needed adjacency regardless of position.

**Evolution-mined motifs (option A): FAILED.** Short evolution runs on easy tasks (count, first, rest) produced genotypes dominated by `BS` → `(count data/products)`. All enriched substrings were hitchhikers from the dominant genotype, not functional motifs. Zero overlap with hand-coded motifs. Root cause: easy tasks don't require `Da`, `DaK`, or comparator building blocks, so those motifs are never selected for. The critical building blocks for the filter program are compositionally useful but individually invisible to selection — `(get x :price)` fails the data-dependence gate unless wrapped in `(filter (fn [x] ...) data)`.

**Chemistry screening (option B): SUCCEEDED at discovery.** Exhaustive screening of all 242,172 substrings of length 2-3 by bond production in random fold contexts. Each substring was placed in 50-200 random genotype backgrounds and scored by scaffold stage frequency (S1+ rate).

Results — the hand-coded motifs rank in the **top 0.08%** endogenously:

| Motif | Rank | out of | S1+ rate | S2+ rate | Program |
|---|---|---|---|---|---|
| `QDa` | #42 | 242K | 24.0% | 4.0% | `(fn x (get x :price))` |
| `Da` | #135 | 242K | 16.0% | 8.0% | `(get x :price)` |
| `DaK` | #186 | 242K | 14.0% | 10.0% | `(get x :price)` |

The top screened motifs are `Da`/`aD` variants with flanking characters that improve fold topology: `aDl` at 40% S1+, `KaD` at 20% S2+, `DaL` at 22% S2+.

This is a clean positive finding: the chemistry's own bonding rules, when systematically screened, identify the same building blocks that were hand-coded — plus superior variants. No evolution, no human domain knowledge. The fold/chemistry IS the motif discovery mechanism.

### Application Phase: Intermediate Preservation Bottleneck

Screened motifs were tested on the hard task (filter programs) alongside hand-coded and random motif controls. Pop=100, len=100, 300 gens, 20 seeds.

| Condition | Avg bonds | S3 | S4 | S5 |
|---|---|---|---|---|
| No motifs (baseline) | 1.4 | 2/20 | 0/20 | 1/20 |
| Chemistry-screened | 2.4 | 3/20 | 0/20 | 0/20 |
| Hand-coded motifs | 2.1 | 3/20 | 1/20 | 1/20 |
| Random motifs | 2.2 | 2/20 | 1/20 | 0/20 |

**All conditions are statistically indistinguishable at 20 seeds.** The screened motifs raise average bond count (2.4 vs 1.4 baseline) and sustain S2 carriers early (4.6% at gen 10), but S1/S2 carriers are erased by gen 25. The motifs create raw material, but selection acts as a scrubber, not a ratchet.

Three critical observations:

1. **Hand-coded motifs underperforming the original module-operator result** (S5 1/20 vs 2/20) means the earlier breakthrough was a rare-event regime, not a robust operator effect.
2. **Random motifs getting S4 1/20** is a warning against over-reading any single rare breakthrough at this sample size.
3. **Higher bonds without better S4/S5** confirms that more local chemistry is not enough — the problem is coordinated multi-motif co-localization and survival under selection.

### Neutral Drift Phases (Experiment 1.8)

Tested whether selection is prematurely purging low-fitness intermediates needed for S3/S4 assembly. Four conditions, same screened motifs, same seeds, same insertion rate (75% of mutations). Pop=100, len=100, 300 gens, 20 seeds.

| Condition | S3 | S4 | S5 | S1 lifetime | S2 lifetime | S1 co-occur | S2 co-occur |
|---|---|---|---|---|---|---|---|
| A. Continuous selection | 3/20 | 0/20 | 0/20 | 17.4 | 4.7 | 18.4 | 1.9 |
| **B. Drift 10/20** | **18/20** | **15/20** | **11/20** | **48.7** | **29.6** | **206.3** | **166.2** |
| **C. Drift 25/50** | **19/20** | **14/20** | **9/20** | **52.6** | **40.1** | **194.2** | **152.7** |
| D. Weak selection 10/20 | 3/20 | 0/20 | 2/20 | 32.9 | 21.6 | 84.9 | 33.4 |

**This is the strongest result in the project.** Drift phases transform the system from 0/20 S4 to 15/20 S4 and from 0/20 S5 to 11/20 S5.

**Mechanistic explanation — the carrier lifetime and co-occurrence data:**

- S1 carrier lifetime: 17→49 gens (2.8x under drift 10/20)
- S2 carrier lifetime: 5→30 gens (6.3x)
- S1 co-occurrence (gens with 2+ carriers): 18→206 (11x)
- S2 co-occurrence: 2→166 (83x)

Under continuous selection, S2+ carriers drop to 0 by gen 20 and stay there for the remaining 280 generations. Under drift 10/20, S2+ rises to 15.1 at gen 299 with S3+ at 1.3. Intermediates persist and accumulate during drift windows; the transition chain S3→S4→S5 fires because carriers overlap long enough for crossover and mutation to combine them.

**Density during drift vs selection windows (condition B):**
- S1 during drift: 26.2 individuals, during selection: 15.9
- S2 during drift: 9.4, during selection: 4.7

Drift accumulates carriers; selection doesn't fully purge them before the next drift window. The cycle ratchets upward.

**Weak selection does NOT work.** Condition D (tournament_size=1 with mu+lambda) is essentially identical to continuous selection (S3 3/20, S4 0/20). This is especially important: it rules out the softer claim that "a bit less selection pressure helps" and supports the stronger claim that these intermediates are below the viability threshold under any ordinary fitness-based retention. The preservation mechanism requires pure drift — this is a threshold phenomenon, not a smooth selection-strength tradeoff.

**Both drift schedules work comparably:** 10/20 slightly better on S5 (11 vs 9), 25/50 slightly better on S3 persistence (4.3 avg S3+ carriers at gen 299 vs 1.3). The similar success of both schedules means the effect is robust and not overfit to one cadence.

### Interpretation: Mechanism, Not Just Performance

This result does more than improve performance — it identifies the mechanism. The earlier motif results (1.5) said "discovery is possible, application fails." Experiment 1.8 now pins down *why* application fails under standard evolution: selection is actively destroying the intermediate scaffold population before composition can occur. Drift removes that pressure, intermediates accumulate, overlap rises, and the S2→S3→S4→S5 chain starts firing at high rates.

The strongest part of the result is the **causal alignment between outcome and mechanism**:

- Final outcomes jump sharply: 0/20 → 15/20 for S4, 0/20 → 11/20 for S5.
- The exact precursor signals predicted also jump: carrier lifetime (2.8-6.3x), co-occurrence (11-83x), and late-stage occupancy (S3+ from 0 to 1.3-4.3 carriers).
- Weak selection failing confirms these intermediates are below the viability threshold, not marginal.

### Revised Complexity Ceiling Assessment

The complexity ceiling is not just a motif-supply problem and not just a search problem. It is a **two-constraint problem**:

1. **Useful motifs must exist or be supplied.** Chemistry screening identifies `Da`, `QDa`, `DaK` in the top 0.08% of 242K substrings. The GP map contains endogenous information about useful building blocks. No evolution or human knowledge required.

2. **Intermediate carriers must be preserved long enough to compose.** Periodic neutral drift windows (fitness = constant) allow S1/S2 carriers to persist and co-occur. This enables the S3→S4→S5 transition chain to fire. The effect is dramatic: 0/20 → 15/20 S4, 0/20 → 11/20 S5.

Experiments 1.5b and 1.8 fit together cleanly: chemistry screening solves endogenous discovery, drift solves preservation. The combined system breaks through the complexity ceiling that has been the central limitation since the Elixir implementation.

This is a much better result than "motif insertion sometimes helps," because it gives a mechanistic explanation for *when and why* higher-order structure emerges. The claim: **folding can generate endogenous building blocks, but immediate fitness selection suppresses the developmental intermediates required for compositional elaboration; periodic neutral phases restore that pathway and reliably break the complexity ceiling.**

This connects directly to Altenberg's constructional selection framework: the GP map exposes useful building blocks (constraint 1), but the evolutionary regime must permit their accumulation (constraint 2). Pure fitness-based selection, even with the right building blocks, acts as a scrubber that destroys precursors before they can compose. Drift phases provide the temporal slack for compositional innovation — analogous to neutral evolution enabling exploration of genotype space in biological systems (Kimura, Huynen).

This is probably the strongest result in the project because it connects representation, evolutionary regime, and mechanism in one experiment. The natural next move: test whether explicit scaffold protection or motif ecology can recover the same benefit without full drift, which would make the result both more biologically plausible and more generally useful.

### Consolidation at Scale (Experiment 1.9)

Confirmed the 1.8 result at 50 seeds, pop=200, 500 generations. Two conditions: continuous selection vs drift 10/20.

| Condition | S3 | S4 | S5 | Filter programs |
|---|---|---|---|---|
| A. Continuous selection | 13/50 (26%) | 2/50 (4%) | 1/50 (2%) | 0/50 (0%) |
| **B. Drift 10/20** | **50/50 (100%)** | **46/50 (92%)** | **39/50 (78%)** | **36/50 (72%)** |

The result is robust. Every seed finds S3 under drift. S5 appears in 78% of seeds. 72% of seeds evolve actual filter programs containing `(get x :price)`.

**Stage accumulation at pop=200:** S1+ carriers rise from 4.6 at gen 0 to 101.0 at gen 499 — half the population carrying S1+ scaffolds. S2+ reaches 37.6, S3+ reaches 2.2. The drift-selection cycle ratchets scaffold density upward over 500 generations.

**Evolved filter programs** (endogenous, no seeding):
- `(count (filter (fn x (< (get x :price) 600)) data/products))` — fitness 0.633
- `(count (filter (fn x (< (get x :price) 700)) data/products))` — fitness 0.616
- `(filter (fn x (> (get x :price) 700)) data/products)` — fitness 0.644 (wrapped with count)

These are genuine compositional programs with the correct structure: higher-order function + anonymous predicate + field accessor + comparator + data source. They use different thresholds and comparison operators than the hand-designed target, but are structurally correct filter expressions assembled endogenously by the fold/chemistry. None reached the exact target `count(filter(fn x (> (get x :price) 200)) data/products)` at fitness 0.832 — the evolved programs use thresholds (600, 700) that are close but not optimal.

**Timing:** Continuous selection: 471s (9.4s/seed). Drift: 1479s (29.6s/seed). Drift is ~3x slower due to population diversity reducing cache hits and more unique genotypes to develop.

**Average time to first appearance** (drift condition, among seeds where found):
- S3: gen 36 (avg)
- S4: gen 123
- S5: gen 153

The transition chain takes roughly 120 generations from first S3 to first S5, consistent with the transition probabilities measured in experiment 1.0 (S3→S4: 0.32%/mutation, S4→S5: 26.6%).

### Scaffold Protection Without Drift (Experiment 1.11)

Tested whether Pareto selection on (fitness, scaffold_stage) can recover the drift benefit without turning off selection. Three conditions, same motifs, same seeds. Pop=100, len=100, 300 gens, 20 seeds.

| Condition | S3 | S4 | S5 | Filter programs | S1 lifetime | S2 lifetime |
|---|---|---|---|---|---|---|
| A. Continuous selection | 3/20 | 0/20 | 0/20 | 0/20 | 21 | 5 |
| B. Drift 10/20 | 19/20 | 13/20 | 8/20 | 5/20 | 52 | 34 |
| **C. Pareto(fitness, scaffold)** | **20/20** | **19/20** | **18/20** | **14/20** | **305** | **302** |

**Pareto surpasses drift on every metric.** S5 rises from 8/20 (drift) to 18/20 (Pareto). Filter programs from 5/20 to 14/20. Carrier lifetimes increase from 34 gens (drift) to 302 gens (Pareto) — carriers essentially never die under scaffold protection.

**The stage trace is the most striking result.** Under Pareto, scaffolds monotonically accumulate without the oscillations seen in drift:
- Gen 25: S3+=7.5, S5+=1.4 (already present)
- Gen 100: S5+=31.2 — 31% of the population carrying S5 scaffolds
- Gen 200: S5+=51.6
- Gen 299: S5+=55.9 — 56% of the population

Under drift, S5 never exceeds 0.3 average occupancy and oscillates with each drift/selection cycle. Pareto provides continuous, directional scaffold accumulation.

**This answers the mechanistic question definitively:** drift worked because it preserved scaffold carriers, not because of random exploration or diversification. Pareto provides targeted preservation while maintaining fitness selection at all times — no wasted generations. The result is both stronger (90% vs 40% S5 rate) and more biologically plausible (analogous to gene duplication or niche structure protecting developmental intermediates).

**Minor tradeoff:** Pareto avg fitness is 0.757 vs 0.769 for continuous selection and drift. The scaffold protection slightly dilutes fitness pressure. But the tradeoff is massively favorable — a 1.5% fitness cost for 90% S5 rates vs 0%.

**Implications:**

1. The preservation mechanism is specifically about protecting scaffold-bearing lineages, not about the broader effects of neutral drift. This makes the mechanistic claim from 1.8 more precise.
2. Pareto selection is a practical approach — no need for artificial drift windows, no wasted generations, continuous adaptive improvement.
3. The monotonic scaffold accumulation under Pareto suggests that once the preservation constraint is properly addressed, the fold/chemistry's compositional assembly is reliable and directional, not stochastic.

### Generalization Test (Experiment 1.12)

Tested whether the scaffold protection mechanism is general or task-specific. Two levels:

**Level 1: Same target (filter-price), generic vs task-specific metric.**
Does Pareto(fitness, bond_count) — a generic structural metric with no target knowledge — work as well as Pareto(fitness, scaffold_stage)?

| Condition | Avg fitness | Avg bonds | S3 | S4 | S5 | Filter programs |
|---|---|---|---|---|---|---|
| A. Continuous selection | 0.769 | 2.2 | 3/20 | 0/20 | 0/20 | 0/20 |
| B. Pareto(scaffold_stage) | 0.754 | 8.5 | 20/20 | 20/20 | **20/20** | **16/20** |
| C. Pareto(bond_count) | 0.754 | 12.3 | 14/20 | 6/20 | **4/20** | 1/20 |

**Level 2: Different target (filter-amount on orders), generic metric only.**
The `scaffold_stage` classifier is hardcoded to `:price` and returns 0 for `:amount` programs. Screened motifs regenerated for `:amount` (`Df`, `fD`, `KU`, etc.) using the same chemistry-screening procedure.

| Condition | Avg fitness | Avg bonds | S3 (incidental) | S4 (incidental) | S5 (incidental) |
|---|---|---|---|---|---|
| D. Continuous selection | 0.728 | 2.2 | 3/20 | 1/20 | 1/20 |
| E. Pareto(bond_count) | 0.711 | 12.3 | 6/20 | 1/20 | 0/20 |

S3/S4/S5 counts at Level 2 detect only incidental `:price` subexpressions, not the actual `:amount`-based scaffolds we care about. Bond counts inflate from 2.2 to 12.3 but this is mostly junk accumulation, not useful structure.

**Interpretation — the generic mechanism is weaker, which sharpens the claim.**

Pareto(bond_count) shows real signal on Level 1 (14/20 S3, 4/20 S5 vs 0/20 baseline), confirming that generic structural preservation helps. But it is substantially weaker than Pareto(scaffold_stage) (4/20 vs 20/20 S5). At Level 2, Pareto(bond_count) mostly inflates bonds without producing useful structure.

**Three findings:**

1. **The preservation mechanism is real and general in principle.** Any second objective rewarding structure provides some benefit over pure fitness selection.
2. **But targeted protection vastly outperforms generic protection.** Knowing what kind of intermediate to preserve matters — not all bonds are useful scaffolds. Generic complexity inflation includes noise.
3. **The 1.11 success was built on target-specific knowledge.** The `scaffold_stage` classifier encodes what filter-price scaffolds look like. Without that knowledge, Pareto(bond_count) produces ~5x fewer S5 breakthroughs.

**What this means for the Altenberg story:**

The GP map can expose useful building blocks (chemistry screening), and multi-objective preservation can protect them (Pareto selection), **but the protection must be informed about what compositional structure matters.** Unprotected generic complexity becomes junk accumulation. This is consistent with biological intuition: gene duplication and niche protection in nature target specific functional categories, not arbitrary sequence complexity.

**The new open question — can scaffold identification itself be made endogenous?**

Three plausible directions:
1. **Motif-presence objective**: Pareto(fitness, count of screened motifs present in genotype). Uses chemistry screening (endogenous) rather than AST classification (hand-coded) as the scaffold signal.
2. **Structural type detection**: Generic AST patterns like "higher-order function + predicate lambda + data source" without specifying `:price`. Recognizes compositional structure regardless of which field it operates on.
3. **Co-evolved scaffold classifier**: A second evolving system learns which AST substructures predict fitness improvement, providing an adaptive Pareto objective.

### Endogenous Scaffold Identification (Experiment 1.13)

Tested three Pareto objectives on both price and amount targets.

**Level 1: Price target**

| Condition | Avg fitness | S3 | S4 | S5 | G5 | Filter programs |
|---|---|---|---|---|---|---|
| A. Continuous selection | 0.769 | 3/20 | 0/20 | 0/20 | 3/20 | 0/20 |
| B. Pareto(motif_presence) | 0.723 | 17/20 | 10/20 | 5/20 | 12/20 | 3/20 |
| **C. Pareto(structural_pattern) — generic** | **0.739** | **20/20** | **19/20** | **18/20** | **20/20** | **12/20** |
| D. Pareto(scaffold_stage) — task-specific | 0.754 | 20/20 | 20/20 | 20/20 | 20/20 | 16/20 |

**Level 2: Amount target** (`scaffold_stage` returns 0 here, use G levels)

| Condition | Avg fitness | G3 | G4 | G5 | Filter programs |
|---|---|---|---|---|---|
| E. Continuous selection | 0.728 | 10/20 | 2/20 | 2/20 | 0/20 |
| F. Pareto(motif_presence) | 0.731 | 20/20 | 13/20 | 12/20 | 6/20 |
| **G. Pareto(structural_pattern) — generic** | **0.714** | **20/20** | **20/20** | **20/20** | **17/20** |

**The generalization claim is defended.** Pareto(structural_pattern) — a field-agnostic, target-family-general preservation objective — nearly matches the hand-coded scaffold_stage on the price target (18/20 vs 20/20 S5) AND transfers cleanly to the amount target (20/20 G5, 17/20 filter programs). The mechanism works across target families without any target-specific classifier.

**Motif-presence is weaker**, and this is informative: local motif counts are too crude an abstraction for preservation. A genotype with many screened motifs scattered as inert substrings scores the same as one with motifs in productive spatial arrangement. You need arrangement-sensitive structure, not just substring inventory. Motif supply alone is not the right abstraction level for preservation.

**Definitional precision on "generic":** The `structural_pattern` objective is **field-agnostic and target-family-general within the symbolic program domain**, not fully domain-free. It is typed around compositional program structure: higher-order function + predicate lambda + data source. That is the right level of abstraction for this domain — not a limitation. Any preservation scheme must commit to what kind of compositional form it protects; `structural_pattern` commits at a level that transfers across field names, data sources, and target programs within the filter/map/reduce family.

**Revised project claim (upgraded from "targeted" to "semigeneric"):**

1. The chemistry can discover useful building blocks endogenously (1.5b).
2. Standard fitness selection destroys intermediate scaffold carriers (1.5 application).
3. Multi-objective preservation rescues those carriers (1.8, 1.11).
4. The preservation objective does not need target-specific field names or hand-coded final programs (1.13).
5. A generic compositional template (higher-order + predicate + data) is enough to reliably break the ceiling across target families.

Selection on developmental potential — not just immediate task fitness — is what unlocks compositional complexity in the folding GP map. That potential can be detected at a level general enough to transfer across related target families without hand-coding.

**Interpretive reads:**
- `Pareto(structural_pattern)` is the key winner — not because it beats `scaffold_stage`, but because it nearly matches it while being generic.
- `Pareto(motif_presence)` underperforming tells us motif supply alone is not sufficient as a preservation signal; arrangement matters, not just inventory.
- The amount-target result being at least as strong as price (17/20 vs 12/20 filter programs) suggests the mechanism is not narrowly overfit to one target family.

**Next: cryptic-variation assay.** If populations evolved under `Pareto(structural_pattern)` adapt faster to novel but related targets than continuous-selection populations, the preservation mechanism is accumulating reusable variation — stored evolvability — not just boosting current-task innovation. This ties the preservation story to the evolvability literature tightly.

### Cryptic Variation Assay (Experiment 1.15)

Tested whether Pareto-preserved populations adapt faster to novel but related targets than continuous-selection populations. 15 seeds, pop=100, train 300 gens on filter-price-200, snapshot at gens 200 and 300, assay 80 gens of continuous selection only (no Pareto, no motif insertion) on two novel targets.

**Results (snapshot gen 300):**

| Task | Condition | final_best (mean) | first≥0.6 | first≥0.8 | start S5+ | start G5+ |
|---|---|---|---|---|---|---|
| T_near: filter-price-600 | A. Continuous | 0.454 | 34 gens (1/15) | — (0/15) | 0 | 0 |
| T_near: filter-price-600 | B. Pareto(scaffold_stage) | 0.512 | 29 gens (2/15) | 14 gens (1/15) | 74 | 68 |
| T_near: filter-price-600 | C. Pareto(structural_pattern) | 0.519 | 28.5 gens **(4/15)** | — (0/15) | 16 | 87 |
| T_far: filter-amount-300 | A. Continuous | 0.628 | 23.1 gens (7/15) | — (0/15) | 0 | 0 |
| T_far: filter-amount-300 | B. Pareto(scaffold_stage) | 0.642 | **11.5 gens (8/15)** | 19 gens (2/15) | 74 | 68 |
| T_far: filter-amount-300 | C. Pareto(structural_pattern) | 0.630 | 21.1 gens (7/15) | 43 gens (2/15) | 16 | 87 |

**What the raw data supports (from per-seed distributions):**

1. **Ceiling access is the cleanest signal.** Continuous selection reached fitness ≥0.8 in 0/30 seed-task combinations at snap 300; Pareto conditions reached ≥0.8 in 4/60. Preservation unlocks fitness regions that re-evolution from unstructured populations cannot reach in 80 assay generations.

2. **B_scaffold reaches ≥0.6 at earlier gens on T_far.** Time-to-≥0.6 sequence: B_scaffold `[1, 1, 4, 6, 14, 15, 18, 33]`, A_continuous `[4, 10, 19, 24, 26, 30, 49]`. This looked like a ~2x speed advantage in the original summary. The trajectory reanalysis (below) showed this is confounded by elevated Pareto starting fitness: B_scaffold populations begin the assay already close to 0.6 because their inherited scaffolds score partial credit. Keep this metric descriptive but do not read it as "faster adaptation."

3. **Endpoint fitness distributions are bimodal/modal.** A_continuous on T_far clusters at `0.55, 0.713, 0.731` — discrete partial-credit modes matching specific program shapes. Pareto conditions add tail outliers at `0.825–0.844`. The "higher ceiling access" claim is a tail-distribution claim, not a mean-shift claim.

4. **Plateau dynamics under both conditions.** Median ~2 best-fitness changes across the 80-gen assay. For C_structural on T_far, 8/15 runs have ≤1 change after the initial jump. The assay is often "found a scaffold, sat there" — not sustained adaptive search. This is mechanistically informative: preservation stocks *discrete compositional assets*, not continuous latent variation.

**What the data does NOT strongly support:**

- **A large average-case transfer advantage.** Means differ by 5–15%; medians are similar. 80 gens of continuous selection partially closes the gap.
- **Generic > task-specific preservation for transfer.** The C > B ordering on T_near (4/15 vs 2/15 for ≥0.6) is *consistent with* this prediction but too small to claim statistically. On T_far, B slightly edges C.
- **Near/far distinction separating mechanisms.** I'd expected C_structural to dominate T_far transfer specifically. The two preservation methods produce similar transfer quality with different distribution shapes.

**Starting-structure confound (disclosed):**

At snapshot 300, A_continuous starts the assay with S5+=0 / G5+=0; B_scaffold with S5+=74 / G5+=68; C_structural with S5+=16 / G5+=87. This is a genuine confound: the result is a *transfer-of-preserved-structure* assay, not a clean test of hidden latent variation independent of scaffold occupancy. Both claims are interesting, but they are different claims.

**Mechanistic interpretation — distinct from continuous cryptic variation:**

The bimodal endpoint distributions and plateau dynamics together argue that this mechanism is **not** Wagner/Kimura-style continuous standing variation that becomes visible under selection. Continuous latent variation would produce smooth fitness improvement distributions and sustained adaptive search. What the data shows instead is **discrete inventory transfer of compositional scaffolds**: preserved populations either inherit a scaffold that solves the novel target or they don't, and when they do, they converge quickly and plateau. This is closer to constructional selection (Altenberg) than to standing-variation population genetics.

**Honest claim for paper writeup (superseded — see Revised Headline after trajectory analysis, below):**

> *Populations evolved under Pareto preservation carry a transferable inventory of discrete compositional scaffolds. When exposed to novel but related targets under continuous selection with no preservation machinery, they reach fitness ceilings that continuous-selection controls do not reach within the assay window (≥0.8 in 4/60 Pareto seed-trials vs 0/30 controls). Time-to-threshold metrics initially looked like faster adaptation; the trajectory reanalysis below shows the effect is dominated by inherited elevated starting fitness, not steeper climb. The surviving mechanism claim: scaffolds function as discrete adaptive assets, not as a gradient of hidden diversity.*

**Caveats and limitations:**

- n=15 per condition; should scale to 30+ for statistical claims
- 80-gen assay long enough that controls partially catch up on T_far (not on T_near); shorter checkpoints (10/20/40) are sufficient for the surviving claims
- T_far is still within the filter compositional family; a true far-transfer (reduce, nested filter) would stress-test the structural-reuse claim
- No motif insertion in assay is the cleanest mechanism test but understates production-setting transfer
- **Starting fitness is elevated for Pareto conditions** (partial credit from inherited scaffolds). Matched-starting-fitness subpopulation analysis is required before any claim that the transfer effect is structural rather than baseline-inherited.

**Trajectory analysis (post-hoc, same data):**

AUC of the best-fitness trajectory, fitness at checkpoints (10, 20, 40, 80 gens), and early slope were computed from the saved trajectories. Three findings refine the summary interpretation:

1. **Endpoint clustering is extreme.** A_continuous on T_near snap 300: 11/15 seeds end at exactly 0.425, 2/15 at 0.488, 2/15 at 0.550–0.600. On T_far: 11/15 at exactly 0.550, rest at 0.713 or 0.731. Pareto conditions show the same modes plus tail outliers at 0.812–0.844. These are partial-credit-scoring fingerprints of specific program shapes. The Pareto advantage is exclusively about unlocking the tail, not shifting the mode.

2. **Pareto advantage grows with assay time on T_near, not shrinks.** Mean-at-checkpoint deltas (Pareto − Continuous) at gens 10/20/40/80 for T_near snap 300:
   - B_scaffold: −0.003, +0.033, +0.043, +0.057
   - C_structural: −0.013, +0.017, +0.029, +0.065

   On T_far the gap is largest at gen 20 and partially closes by gen 80 — but on T_near the gap keeps widening. The "80 gens lets controls catch up" concern applies to T_far but not to T_near.

3. **Early slope is *lower* for Pareto, not higher.** T_far snap 300 slope×20: A 0.285, B 0.250, C 0.161. This contradicts my earlier "2x faster adaptation" framing. The reason: Pareto populations start the assay with higher baseline fitness (inherited partial-credit from scaffolds), so they have less headroom for a steep early climb. The "faster to reach ≥0.6" metric reflects *starting closer to the threshold*, not steeper improvement. This is an honest recharacterization: Pareto populations don't adapt faster — they *start ahead and occasionally climb into regions controls cannot access*.

**Revised headline claim after trajectory analysis:**

> *Pareto-preserved populations inherit an elevated starting fitness on novel related targets plus occasional access to high-fitness regions (≥0.8) that continuous-selection controls cannot reach within 80 assay generations. The mechanism is not steeper adaptation; it is inherited inventory plus rare ceiling unlock. Mean advantages at endpoint are small and driven by 2–4 tail outliers per condition; median endpoints are identical across conditions on T_far.*

That is a weaker and more specific claim than "cryptic variation demonstrated" or "faster adaptation." It is also the claim the data actually supports.

**Follow-up priorities (now better-informed):**

1. **30+ seed rerun with shorter checkpoints (10, 20, 40).** Emphasize mid-range differences where the Pareto signal is clearest. 80-gen window is not required.
2. **Add a genuine compositional-family far-transfer** (e.g., `(reduce (fn a b (+ a (get b :price))) 0 data/products)` or `(count (map (fn x (get x :price)) data/products))`). Current T_far stays within filter family.
3. **Matched-starting-fitness subpopulation analysis.** The elevated-baseline finding makes this more important, not less: comparing Pareto subpopulations at equivalent starting fitness against continuous-selection individuals tests whether ceiling access survives the baseline confound. *Run as Experiment 1.15b; see below.*
4. **Count unique endpoint values per condition.** If Pareto populations produce more distinct programs at termination, that is additional evidence of inventory transfer (diverse scaffolds → diverse solutions).

### Matched-Starting-Fitness Transfer (Experiment 1.15b)

Follow-up to 1.15. The trajectory reanalysis showed Pareto populations inherit elevated T_far starting fitness via partial-credit scoring of preserved scaffolds. To disambiguate "inherited scaffold inventory" from "starting-position advantage," we pooled the 15-seed gen-300 snapshots per condition (1500 individuals each), scored every individual on T_far in the unadapted state, and attempted to build matched-starting-fitness subpopulations across conditions.

**The matching was impossible to construct — the distribution non-overlap is the headline result.**

| Starting-fitness band on T_far | A_continuous | B_scaffold | C_structural |
|---|---|---|---|
| [0.20, 0.30) | 1500 | 1388 | 1296 |
| [0.30, 0.55) | 0 | 0 | 0 |
| [0.55, 0.60) | 0 | 104 | 102 |
| [0.60, 0.65) | 0 | 0 | 100 |

All 1500 A_continuous individuals score exactly 0.213 on T_far — the partial-credit floor for a data-dependent program that passes the gate but matches nothing specific. A_continuous has no natural variation above this floor; every seed converges on `count(products)` and nothing else. Pareto populations span 0.213 upward, with 100–200 individuals per condition in the 0.55–0.65 range. There is no starting-fitness band where all three conditions have individuals; matched comparison is undefined.

**What this establishes:**

- **The two optimization regimes produce qualitatively different phenotype distributions on related tasks, not just different means.** A_continuous collapses onto a single narrow specialist basin. Pareto populations maintain structural programs that score partial credit on the novel target *by construction*, because their preserved form matches `(higher_order (fn x (CMP (get x :ANY) VAL)) data/ANY)` — the template generalizes to different field/data slots automatically.
- **The 1.15 transfer advantage is explained by structural generality, not by stored cryptic variation.** Pareto populations start the assay already at 0.55–0.65 on T_far because their programs structurally generalize to the novel target. From this elevated start, ordinary mutation/crossover can sometimes reach the 0.8+ tail. From A's 0.213 floor, it cannot in 60–80 gens.
- **The ≥0.8 ceiling hits (4/60 Pareto vs 0/30 control) reframe as second-stage elaboration from a structurally advantaged start, not as evidence of latent adaptive capacity.** The climb from 0.55 to 0.8 is ordinary mutation/crossover work; what matters is being at 0.55 in the first place.
- **Matched comparison cannot be run in this system** because the distributions do not overlap. That is a constraint on what future experiments can test, not an oversight. Any future attempt would need a different control — e.g., training A_continuous under a multi-target regime that forces some structural breadth before transfer.

**Revised headline claim (supersedes the 1.15 first-pass and trajectory-analysis framings):**

> *Pareto preservation changes what evolution stores. Instead of converging on narrow shortcuts, it maintains compositional scaffolds that generalize by construction to related targets. The observed transfer advantage in 1.15 is fully consistent with this inherited structural generality; the data do not support an additional cryptic-variation claim beyond the baseline effect. Continuous selection, by contrast, collapses onto a single specialist basin (`count(products)` in 15/15 seeds) with no natural variation across the 1500-individual pool on the related T_far target.*

**Why this is the right story, not a downgrade:**

1. It is specific and falsifiable. "Preservation selects for reusable compositional structure; reusable compositional structure generalizes across related tasks; pure fitness optimization selects brittle specialists" — each piece can be independently checked.
2. It fits the Altenberg / constructional-selection framework directly and avoids borrowing the looser Wagner/Kimura "hidden variation" vocabulary.
3. It explains *why* Pareto transfer works without invoking a reservoir of hidden capacity that the data cannot support.
4. The distribution non-overlap itself is a headline result — it says the optimization regimes produce different phenotype classes, not different points on the same distribution.

**What the matched-fitness failure does NOT do:**

- It does not rule out some residual extra capacity beyond baseline. It only says the current assay cannot test for it. "Fully consistent with structural generalization alone" is the honest claim; "entirely explained by baseline" would overclaim.
- It does not weaken the ceiling-access finding. ≥0.8 hits in Pareto but not control remain clean — they just reframe as downstream consequences of the baseline difference, not as a separable effect.

**Follow-up priorities (updated after 1.15b):**

1. **Pooled-genotype AST analysis** — confirm A_continuous pool is essentially all `count(products)` while B/C pools contain diverse compositional forms. Lightweight supporting measurement for the "specialist basin" claim.
2. **Far-transfer scale-up** — see reachability check below; in practice blocked for cross-family targets.
3. **A2 ablation** (folding × preservation × motifs on hard problems) — now ready to run; answers "what is the paper about" with a clean separation of contributions.
4. **Multi-target continuous-selection control.** The matched-fitness failure motivates this: train A_continuous on a diverse 3-target set that exposes it to filter structure, then compare transfer. Tests whether continuous selection *can* produce structural breadth given the right pressure, or whether pure fitness always collapses to specialism.

### Cross-Family Far-Transfer Reachability (Representation Scope Statement)

Before scaling the 1.15 series to a genuinely cross-family far-transfer (reduce-sum or first-of-filter-equals-string), we checked whether the targets are reachable in the natural phenotype distribution of the current alphabet/chemistry. 10,000 random length-100 genotypes were developed and scanned for the full target signatures.

| Target | Full signature | Partial: top-level op | Partial: load-bearing substructure |
|---|---|---|---|
| `(reduce (fn a b (+ a (get b :price))) 0 data/products)` | **0 / 10,000** | reduce present: 110 (1.10%) | reduce + 2-arg fn: **0** |
| `(first (filter (fn x (= (get x :KEY) STR)) data/DS))` | **0 / 10,000** | first: 2268 (22.68%); filter: 103 (1.03%) | first+filter+=: **0** |

**What is blocked:**

- `reduce` occurs as a top-level operator at ~1% of random genotypes, but `reduce` combined with a 2-argument lambda appears zero times in 10,000 samples. The fn-bonding chemistry produces 1-argument predicate lambdas by default; 2-argument lambdas require an adjacency pattern that random genotypes almost never hit.
- `first`, `filter`, and `=` are each individually abundant (22%, 1%, 16%), but the conjunction `first(filter(fn x (= (get x :K) "str")))` with a string literal is zero. Even within the filter family, specific predicate shapes outside `(CMP (get x :K) NUM)` are unreachable.

**Scope statement for the paper:**

*The current folding alphabet and chemistry naturally generate one compositional family: 1-argument predicate/accessor lambdas wrapped in higher-order operators over data sources. Cross-family transfer (reduce with accumulator, filter with string equality, nested compound predicates) cannot be tested fairly because those targets lie outside the natural phenotype distribution of the representation. The 1.15 structural-generalization claim therefore applies **within the representation's natural compositional family**, not across arbitrary compositional families. Extending to other families would require alphabet or chemistry extension — a separate research step, not a test of the current mechanism.*

This is not a disaster; it is a precise boundary. It reframes the 1.15 / 1.15b claim as: *Pareto preservation produces structurally general programs within the representation's natural family (1-arg predicate/data pipelines). Pure fitness optimization collapses even within that family to a single specialist point.*

**Decision:** skip the 30-seed cross-family rerun. Run one cheap within-family robustness check (1.15c, comparator and wrapper variations) to confirm the within-family claim is not resting on a single transfer pair, then move to A2 ablation.

### Within-Family Robustness (Experiment 1.15c)

Cheap sanity check (10 seeds) testing two additional within-family transfer targets — comparator swap and wrapper swap — under the 1.15b design. Same Phase 1 training (filter-price-200, 300 gens, pop=100), snapshot at gen 300, 40-gen assay with continuous selection only, no motif insertion, single-target novel assays.

**T_comp (comparator swap, `>` → `<`):**

`(count (filter (fn x (< (get x :price) 500)) data/products))`

| Cond | T_comp starting-fitness pool (1000 indiv.) | endpoint ≥0.7 |
|---|---|---|
| A_continuous | 1000 / 1000 at 0.413 (single value) | 8/10 |
| B_scaffold | 896 at 0.413, **101 at 0.594** | 7/10 |
| C_structural | 896 at 0.413, **102 at 0.594** | 10/10 |

Non-overlap persists at the tail: Pareto conditions carry ~10% of the pool at 0.594, A carries 0. The *bulk* distribution is now overlapping (both A and Pareto at 0.413), not separate as in 1.15b. After 40 assay gens, A matches B on ≥0.7 hits (8/10 vs 7/10). C_structural is the cleanest with 10/10 at ≥0.7, no variance. Ceiling access (≥0.8) is absent for all conditions on this target — `count(rest(products))` and similar shortcuts get to 0.731 easily, so there's no tail only Pareto can reach.

**T_wrap (wrapper swap, `count` → `first`):**

`(first (filter (fn x (> (get x :price) 300)) data/products))`

| Cond | T_wrap starting-fitness pool | endpoint ≥0.6 |
|---|---|---|
| A_continuous | 1000 / 1000 at 0.050 | 0/10 |
| B_scaffold | 998 at 0.050, 2 at 0 | 0/10 |
| C_structural | 1000 / 1000 at 0.050 | 0/10 |

**All three conditions collapse to the same floor.** No non-overlap. Evolution also fails for all conditions — no seed reaches ≥0.6 in 40 gens. The reason is mechanistic: `first(filter(...))` returns a product *object*, not a number. Partial-credit scoring cannot credit numerical outputs from any condition when the target expects an object. **The elevated-baseline mechanism that drove the 1.15b non-overlap disappears when output type changes.**

**The three-way interaction — what actually makes transfer work:**

The 1.15 series, interpreted together, shows that transfer benefit from Pareto preservation depends on an interaction of three factors, not one:

1. **Reachable compositional structure in the representation.** The reachability check showed cross-family targets (reduce with accumulator, first-filter-equals-string) are outside the natural phenotype distribution. Transfer can only be tested within the family the representation naturally generates.

2. **Preserved scaffold inventory from Pareto.** The matched-fitness non-overlap (1.15b) and the T_comp tail (1.15c) show Pareto populations carry structurally distinct individuals that continuous selection does not. Continuous selection collapses to a single specialist basin; Pareto does not.

3. **Scoring function's partial-credit geometry.** T_wrap's null result shows that even when preserved structure is present, transfer advantage disappears if the scoring function cannot partially reward inherited outputs against the new target. Partial credit on numeric outputs vs numeric targets works; partial credit on numeric outputs vs object targets does not.

**Bounded claim for the paper (final version):**

> *Pareto preservation biases evolution toward scaffold-rich numeric programs whose outputs remain partially aligned with related targets. This creates an inherited baseline advantage and occasional access to higher-fitness regions under related target changes. The effect is bounded by the representation's reachable compositional family and by the scoring function's type compatibility. Continuous selection, by contrast, converges to narrower specialist solutions with less transferable structure.*

**What is safe to claim:**
- Pareto preservation yields inherited structural inventory that transfers to related numeric targets when that inventory lands in a compatible scoring basin.
- Continuous selection converges to narrower specialist solutions with less transferable structure.
- The transfer effect is real but highly conditional on representation reachability and scoring-function compatibility.

**What is NOT safe to claim:**
- Broad within-family structural generalization (T_wrap disproves this).
- Generic transfer across related program variants (bounded by output-type compatibility).
- Stored cryptic variation in the Wagner/Kimura sense (matched-fitness non-overlap rules this out).
- Faster adaptation dynamics (trajectory reanalysis rules this out — Pareto slopes are lower, not higher).

**Why the narrowing improves the paper:**

The result is now mechanistically specific rather than vaguely general. The three-way interaction decomposition makes each claim independently falsifiable. The T_wrap null is not a weakness — it is evidence that the mechanism is not a general "stored capacity" phenomenon, and it isolates *which* factor (scoring geometry) is necessary for the effect. Reviewers cannot puncture an overbroad generalization because we have not made one.

The headline becomes about **what preservation changes in the phenotype distribution** (reusable scoring-compatible structures) rather than about **where preserved variation can go** (which turns out to be bounded in two orthogonal ways).

## 7. Coevolution Findings (Elixir)

### Single-Context Collusion
With one evaluation context, populations converge on a single phenotype (e.g., literal `500`). Everyone produces the same output, so everyone "passes" everyone else's test. Solve scores hit 1.0 with zero diversity.

### Multi-Context Profiles Fix Collusion
Evaluating across 3+ context variations (different list sizes, different data) forces diversity. A hardcoded `500` produces profile `[500, 500, 500]`; a computing `(count data/products)` produces `[2, 3, 5]`. Populations maintain ~15 unique phenotype niches.

### Triad Coevolution: Role Conflict is Fundamental
Single population with `fitness = w_solve * solve + w_test * test + w_oracle * oracle`. A tester-specialist (test=1.0, solve=0.0) gets fitness 0.3 while a solver-specialist (solve=0.9) gets 0.36. Testers can never compete on overall fitness. Per-role elitism keeps one alive but can't create a lineage.

### Separated Coevolution: Role Activation Solved
Three independent populations with unambiguous selection pressure. 30/30 testers producing valid data transformations by gen 3 (vs 1 protected singleton in triad).

### Degenerate Equilibrium (Constant-Output Collapse)
Despite role activation, all populations collapsed to trivial constant-expression agreement. Solver pass rate: 100%. All solvers: `(= 800 0)` -> `false`. All oracles: `(not 400)` -> `false`. Testers can't break solvers that ignore data.

### Data-Dependence Gate: The Fix That Worked
Fitness = 0 if output is identical on all base contexts. One line of logic blocks constant collapse. Results (200 generations):
- Solver avg fitness: 0.66-0.69
- Discriminating testers: 30/30 at 66.7% pass rate
- All solvers: `(count (rest (rest data/employees)))` — genuinely data-dependent
- Plateau: delta 0.022 between gen 11-100 and gen 101-200

## 8. The Complexity Ceiling (Revised)

See Section 6 for the full diagnostic series. The framing evolved through multiple revisions as evidence accumulated.

**Original claim:** "representation/search issue — scale up, seed, or bias selection."

**Revision 1 (after staircase+lexicase):** The ceiling is a reachability problem — selection-side interventions cannot bridge the structural gap.

**Revision 2 (after seeded elaboration):** The ceiling is a developmental accessibility bottleneck. The representation can express complex programs, selection maintains them once found, but the S3→S4 spatial conjunction is unreachable by incremental mutation.

**Revision 3 (after transition analysis):** The S3→S4 transition IS achievable (0.32% per mutation) but S3 carriers are too rare (0.04% of random genotypes) for the transition to fire. Not structural impossibility, but structural accessibility under selection.

**Revision 4 (after module operators):** The complexity ceiling is a building-block supply problem. Supplying known-useful motifs raises scaffold density 250x and enables the full target program to evolve (2/20 seeds, including a fitness 0.832 breakthrough). The central open question: can motif discovery become endogenous?

**Revision 5 (after endogenous motif experiments):** The complexity ceiling decomposes into two separate constraints: motif discovery (solved via chemistry screening) and intermediate preservation (unsolved — selection destroys S1/S2 carriers by gen 25).

**Revision 6 (after drift phases):** Both constraints resolved. Drift phases transform S4 from 0/20 to 15/20, S5 from 0/20 to 11/20. Weak selection does not work — pure drift required.

**Revision 7 (after consolidation):** Confirmed at 50 seeds, pop=200, 500 gens. S3: 100%, S4: 92%, S5: 78%, filter programs: 72%. Ceiling broken and robust.

**Revision 8 (after scaffold protection):** Pareto(fitness, scaffold_stage) surpasses drift: S5 90% vs 40%, filter programs 70% vs 25%. Mechanism confirmed as targeted preservation, not random drift.

**Revision 9 (after generalization):** Pareto(bond_count) helps but much weaker than scaffold_stage. Preservation needs a targeted objective; generic complexity alone is not a substitute.

**Revision 10 (after endogenous scaffold identification):** Pareto(structural_pattern) — a field-agnostic, target-family-general AST objective — nearly matches scaffold_stage on price target (18/20 vs 20/20 S5) and transfers cleanly to amount target (17/20 filter programs, 20/20 G5). The generalization claim is defended. Motif-presence is weaker (arrangement matters, not just inventory). Claim upgraded from "targeted preservation works" to "semigeneric preservation of compositional intermediates works."

**Revision 11 (after cryptic variation assay, first pass):** Preserved populations transfer discrete compositional scaffolds to novel but related targets. Pareto-preserved populations reach fitness ceilings that continuous-selection controls never reach in the assay window (≥0.8 in 4/60 Pareto seed-trials vs 0/30 controls). Bimodal endpoint distributions and plateau dynamics indicate the mechanism is *discrete inventory transfer* of compositional scaffolds, mechanistically distinct from continuous standing variation (Wagner/Kimura). Starting-structure confound disclosed.

**Revision 12 (after trajectory-analysis reanalysis of 1.15):** The initial "2x faster adaptation" framing was wrong. Post-hoc trajectory analysis showed Pareto populations have *lower* early slopes than continuous-selection — they inherit higher starting fitness (partial credit from inherited scaffolds), which looks like fast adaptation in time-to-threshold metrics but is actually an initial-condition advantage. Intermediate framing: "preserved populations inherit an elevated baseline plus occasional access to high-fitness regions unreachable to controls in the assay window."

**Revision 13 (after matched-fitness follow-up, 1.15b):** The two optimization regimes produce qualitatively different phenotype distributions on related tasks. A_continuous collapses to a single specialist basin (all 1500 pooled individuals at 0.213 on T_far); Pareto populations span 0.213–0.613 with elevated tails. Starting-fitness distributions do not overlap; matched comparison is undefined. Intermediate framing: "Pareto preservation maintains compositional scaffolds that generalize by construction to related targets."

**Current (after reachability check and within-family robustness, 1.15c):** The "structural generalization" framing was directionally right but too broad. Reachability check showed cross-family targets (reduce, first-filter-equals) are outside the natural phenotype distribution — the representation generates one compositional family, not arbitrary programs. Within-family check showed the non-overlap effect is target-dependent: strong on T_far (field+data shift), weak-and-tail-only on T_comp (comparator swap), and absent on T_wrap (wrapper swap). T_wrap's null is mechanistically informative: `first(filter(...))` returns an object, not a number, so partial-credit scoring cannot credit inherited numerical outputs. The actual mechanism is a three-way interaction: (1) reachable compositional structure, (2) preserved scaffold inventory from Pareto, (3) scoring function's partial-credit geometry. Final bounded claim for the paper: *Pareto preservation biases evolution toward scaffold-rich numeric programs whose outputs remain partially aligned with related targets. This creates an inherited baseline advantage and occasional access to higher-fitness regions under related target changes. The effect is bounded by the representation's reachable compositional family and by the scoring function's type compatibility.* Continuous selection, by contrast, converges to narrower specialist solutions with less transferable structure. What the result is NOT: broad within-family generalization, generic transfer, stored cryptic variation, or faster adaptation dynamics.

## 9. Eval Performance

PTC-Lisp: **10,900 evals/sec**. Scaling to pop=300x3, len=100, 1000 gens is hours. This is the primary motivation for the Python rewrite — NumPy batch evaluation, no IPC overhead.

## 10. CA-Development GP (parallel research track)

A second genotype-phenotype mapping where the CA rule **is** the program: inputs clamped on row 0 of an N×N grid, rule iterated T steps, output read from a designated cell. MLX-backed (M1 Metal) batch evaluation; NumPy reference backend is bitwise-identical on fixed seeds. Full details in `docs/ca/architecture.md` and `docs/ca/experiments.md`.

Six sweeps (178 runs total) on outer-totalistic rules over a 3×3 Moore neighborhood; `K` state counts ∈ {2, 4, 8}; `N ∈ {8, 16, 32}`.

**a) K=2 is a representational cliff, task-invariant.** Every K=2 run on every tested n_bits, on both parity AND majority, is stuck at exactly 0.50 (random). Rules out mutation-pressure artifact (30-run sweep with `mutation_rate ∈ {0.01 … 0.8}`, K=2 stays flat at 0.50). K=2 outer-totalistic rules with the row-0-clamp / center-readout geometry cannot produce non-constant output at the readout cell.

**b) K=4 saturates expressiveness for these tasks.** K=4 and K=8 are indistinguishable on parity and on majority, across all tested n_bits. Doubling state count buys nothing measurable. Claim is task-conditional — richer tasks may still benefit.

**c) Spatial budget is not the bottleneck.** Grid size N ∈ {8, 16, 32} with step count scaled to match produces similar results at every K ≥ 4. At N=8 the CA has room; at N=32 it doesn't use the extra.

**d) Difficulty is task-structural, not representation-structural.** Parity degrades steeply with n_bits (1.00 at 4-bit → **0.70 at 8-bit under full-space training**); majority degrades gently (1.00 at 3-bit → ~0.95 at 7-bit on half-space training, likely similar on full). Matches the classical Mitchell/Crutchfield result — CAs are naturally good at density/majority tasks and bad at parity. The 8-bit parity ceiling survived both mutation-rate (0.01-0.8) and population-size (256→4096) sweeps without climbing, so the ceiling is not search-bound.

**e) Pipeline reproducibility.** Same config + seed twice produces bitwise-identical genotypes and fitness histories on both backends; sweeps are resumable; all 178 runs logged with config hash + history for post-hoc analysis.

**f) Rule-family symmetry is *not* the 8-bit parity bottleneck.** A decision-tree rule family (depth 5, 94-byte genotype, breaks rotation + permutation symmetry of OT) performs *worse* than outer-totalistic at matched budget on both parity (0.72 vs 0.81 median on overfit-training) and majority (0.88 vs 0.94). Diagnosis: OT's symmetries are a correct inductive bias for these symmetric tasks — removing them forces evolution to re-discover the prior from byte-level mutations, which evidently doesn't happen within 150 generations.

**g) Methodology correction and 8-bit ceiling restatement.** Mechanistic inspection of the best 8-bit OT rule revealed **severe overfitting**: training fitness 0.92 on 64 examples, but only 0.57 on the 192 unseen inputs (0.66 full-space accuracy). The previous "0.80 ceiling" across sweeps 3–8 was training-subset memorization at `n_examples=64` on a 256-input space, not a true parity competence measure. A confirmatory sweep (`parity_full_train.yaml`) trained on all 256 inputs — median true accuracy falls to **0.70 (max 0.82)**, confirming the qualitative ceiling but correcting its level downward by ~10 points. The CA at K=4 / N=16 / T=16 genuinely cannot compute 8-bit parity. Sweeps with `n_examples ≥ 2^n_bits` (4-bit, 6-bit parity; 3-bit, 5-bit majority) were always clean and remain valid. Going forward: prefer full-space training, or log holdout accuracy as a secondary metric.

**h) Cross-task comparison on clean data — paper-worthy claim supported.** `majority_full_train.yaml` (90 runs) re-ran majority under full-space training for `n_bits ∈ {3, 5, 7}`. 7-bit majority corrected from 0.938 (half-coverage) to **0.898 (full-space)** — a small 0.04 drop compared to parity's 0.10 drop. The resulting full-space-training table makes the cross-task claim unambiguous:

  | n_bits (par/maj) | parity | majority | gap    |
  |------------------|--------|----------|--------|
  | 4 / 3            | 1.000  | 1.000    | 0.00   |
  | 6 / 5            | 0.875  | 0.938    | +0.06  |
  | 8 / 7            | 0.703  | 0.898    | +0.20  |

The majority-vs-parity gap widens with n_bits — classical Mitchell/Crutchfield result confirmed without any memorization confound. K=2 cliff holds a third time (0.500 on all n_bits on both tasks). K=4 / K=8 remain indistinguishable on clean data.

**i) Readout geometry does not matter — 0.70 ceiling is the CA dynamic itself.** `readout_geometry.yaml` (30 runs) varied `output_mode` on the clean 8-bit parity setup: single cell (baseline), 3-cell horizontal pool with bit-majority-voting, full 16-cell bottom-row vote. All three medians agree within 0.01 (0.69 / 0.69 / 0.70). Pooling 16× more output cells does not lift the 0.70 ceiling. Four independent mechanisms for the 8-bit parity ceiling are now ruled out: rule expressiveness (K=4 = K=8), search pressure (mutation and pop sweeps null), rule-family symmetry (DT < OT), and readout geometry (all three modes equal). The remaining diagnosis: the CA at N=16 / T=16 genuinely cannot bring 8-bit parity information to the readout — a property of the dynamic, not of rule flexibility, search, or aggregation.

**j) Scaling CA compute budget is not the missing ingredient.** `ca_dynamic_budget.yaml` (killed at 10/15 after the signal stabilized) scaled `(grid_n, steps)` relative to the (16, 16) baseline. More time alone at fixed N (0.70 → 0.70) was null; more space + matched time (32, 32) gave +0.04 median; more time and space together (32, 64) gave no further gain and possibly slightly worse. Adds a fifth ruled-out mechanism: raw compute budget. Consistent with the §8-b + §8-b-readout diagnosis — the CA's *state* doesn't carry 8-bit parity information no matter how much lattice and how many steps you give the same uniform dynamics. Round-2 sweeps (§11 in docs/ca/experiments.md) target state-carrying machinery directly: non-uniform rules (banded/per-row), rule schedules (phases), neighborhood radius, second-order memory.

**k) Langton's λ is not a useful summary statistic for this CA-GP setup.** Zero-new-compute reanalysis (`experiments/ca/analyze_lambda.py`) over all 374 evolved rules across 11 sweeps: evolved-λ distribution is **indistinguishable from random-rule λ at the same (family, K) shape**. Δ(evolved median, random mean) is ≤ 0.011 in every cell with n ≥ 9. Within each K band, fitness ranges from 0.5 to 1.0 at essentially the same λ — λ is orthogonal to fitness. Evolution finds task-solving rules without tuning λ toward any critical edge-of-chaos value; the K=2 stuck cliff sits at random K=2 λ (no gradient); none of the five already-ruled-out mechanisms for the 8-bit parity ceiling are λ-related. Whatever distinguishes evolved working rules from random rules is finer-grained than a single-scalar λ summary.

**l) 🎯 Spatial specialization breaks the 8-bit parity ceiling.** `nonuniform_bands.yaml` (§11.a, 40 runs) compared uniform outer-totalistic against a banded variant in which 3 horizontal bands (N=16 → rows 0–4 / 5–10 / 11–15) each carry their own K=4 OT rule table. On 8-bit parity full-space training:

  | rule family       | median | min   | max   | mean  |
  |-------------------|--------|-------|-------|-------|
  | outer_totalistic  | 0.693  | 0.621 | 0.816 | 0.711 |
  | banded_ot (3 bands) | **0.805** | 0.637 | **0.969** | **0.794** |

  Δmedian +0.11, Δmax +0.15. Best banded seed reached 0.969 = 248/256 correct; 15 percentage points above anything uniform OT ever produced across 6 prior sweeps (ceiling 0.816). Error inspection of the best banded rule shows all 8 errors concentrated at bit-count=5, with every other bit-count exactly solved — qualitatively different from uniform OT's spread-across-odd-weights failure mode (§9). The banded rule approximates true parity with one structural residual class, not a bit-count heuristic.

  Also lifts 7-bit majority modestly (Δmedian +0.03 on an already-high 0.90 baseline). **First ceiling-break in 11 sweeps**: every prior intervention was null or negative, consistent with §8-b's state-carrying-machinery framing — partial structures that carry parity needed different rules in different rows to exist at all. Matched-byte control is not formally run but §3's K=4 vs K=8 null (100 vs 456 bytes same fitness) argues against "more bytes" as the alternative explanation. Natural next step: `per_row` specialization (16 independent row-rules) to see if the gain keeps scaling.

**m) Per-row specialization is *worse* than uniform — 3 bands is a sweet spot, not a monotone effect.** `per_row.yaml` (§11.a-b, 20 runs) ran banded_ot with `n_bands=16` (every row its own K=4 rule, 1600-byte genotype) on the same two tasks. 8-bit parity: median 0.641 (worse than uniform 0.693), narrow 0.621–0.656 band; 7-bit majority: 0.797 (also worse than uniform 0.898). Diagnosis: at `mutation_rate=0.03` per byte, expected flips per generation scale linearly with genome length — per_row gets 48 flips/gen vs banded_3's 9 and uniform's 3. Evolution's effective step size is too large relative to the fitness landscape; search never consolidates. Two important corollaries: (1) banded_3's win in (l) is NOT a "more bytes = better" story — per_row has 5× the bytes and does 0.16 worse; (2) matched-byte controls for all subsequent §11 sweeps must normalize mutation rate to genome length (hold expected flips per generation fixed across variants) to avoid confounding genome length with evolvability.

**n) 🎯 Neighborhood radius fully solves majority but does nothing for parity.** `radius.yaml` (§11.c, 60 runs) swept Moore radius ∈ {1, 2, 3} (genotype bytes 100 / 292 / 580 at K=4) with length-normalized mutation rate (~3 flips/gen across all radii), 10 seeds × 2 tasks. **7-bit majority at r=3: 9/9 runs at exactly 1.000 in median 111 generations — first 100%-solved non-trivial task across the entire CA-GP track.** r=2 modestly lifts majority (0.910 vs 0.898 baseline); r=3 closes the remaining 0.10 gap cleanly. **8-bit parity: null or slightly negative at every radius** — r=2 and r=3 both at 0.66 median vs r=1's 0.69. At r=3 with T=16, per-step causal cone extends 3 cells, so the readout cell can see any input cell within distance 48 — far beyond N=16. **Information-reach is not the parity bottleneck.** The CA literally sees the entire input and still can't XOR it. Betel-Oliveira-Flocchini's 1D propagation-speed argument does not transfer to this 2D row-0-clamp geometry.

Across twelve completed sweeps, only one intervention moves 8-bit parity's ceiling: spatial role-specialization (banded_3 from §11.a). Not bigger windows, not richer rules, not more search budget, not varied readouts, not richer families, not edge-of-chaos regimes. **Different rules in different rows** is the unique parity-mover; everything else is null. Mitchell/Crutchfield strengthened: CAs do density tasks well when given sufficient local integration, and parity is structurally resistant in ways that bigger local context cannot overcome. **Total runs across CA track: 478.**

Sweeps reproducible from `experiments/ca/sweeps/*.yaml`; per-run history under `experiments/ca/output/<sweep>/<config_hash>/`.
