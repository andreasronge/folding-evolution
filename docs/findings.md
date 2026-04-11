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

## 5. Coevolution Findings

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

## 6. The Complexity Ceiling

The fundamental limitation across all coevolution designs:

- Most complex evolved program: `(count (rest (rest data/X)))` — 3 bonds
- 4+ bond programs (`filter + fn + predicate + data`) never emerge through evolution
- The chemistry's phenotype space is too shallow for sustained arms races
- When max complexity is 3 bonds, there aren't enough strategies for an arms race

This is a representation/search issue, not a coevolution design issue. Potential fixes:
- Genotype length 80-100 with populations 100+ and 500+ generations
- Seed genotypes with known 4-bond programs
- Complexity-biased selection (bonus for more bonds)

## 7. Eval Performance

PTC-Lisp: **10,900 evals/sec**. Scaling to pop=300x3, len=100, 1000 gens is hours. This is the primary motivation for the Python rewrite — NumPy batch evaluation, no IPC overhead.
