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

### Revised Complexity Ceiling Assessment

The original framing ("representation/search issue, potential fixes: scale up, seed, complexity-biased selection") was wrong. The diagnostics show:

1. **The representation can produce 4+ bond programs** — they're abundant in random genotypes.
2. **The tasks can require 4+ bonds** — filter tasks are verified hard under exact match.
3. **The chemistry can be evolved** — d2 weights move upward under selection.
4. **But there is no incremental path from simple to complex programs.** The fitness landscape has a structural gap. Rest-chain programs and filter programs occupy disconnected regions of genotype space. Selection pressure, curriculum design, and chemistry variation all fail to bridge this gap.

The ceiling is a **reachability problem within the developmental map**, not a search problem or a selection problem. The chemistry produces either simple programs (count, rest chains) or syntactically complex but semantically useless programs (deeply nested contains?, match). It does not produce the intermediate forms that would serve as stepping stones toward useful complex programs like filter expressions.

Potential directions:
- Chemistry quality: affinity-based bonding that preferentially forms useful bonds (Stage 2)
- Softer chemistry: graded/probabilistic bonds, provisional assemblies
- Hierarchical assembly: stable submodules that compose into larger programs
- Alternative developmental processes: codon tables, stack machines

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

See Section 6 for the full diagnostic series. The original framing is superseded.

**Original claim:** "representation/search issue — scale up, seed, or bias selection."

**Revised:** The ceiling is a **reachability problem in the developmental map**. The representation can express 4+ bond programs (C1 diagnostic: 23-74% of random genotypes). The tasks can require them (verified hard under exact match). Selection can be refined (staircase, lexicase). Chemistry can evolve (d2 moves upward). But evolution cannot incrementally reach filter programs from rest-chain programs because they occupy disconnected regions of genotype space. No intervention on the selection or task side alone bridges this structural gap.

## 9. Eval Performance

PTC-Lisp: **10,900 evals/sec**. Scaling to pop=300x3, len=100, 1000 gens is hours. This is the primary motivation for the Python rewrite — NumPy batch evaluation, no IPC overhead.
