# Coevolution Designs

Four coevolution frameworks were tested in the Elixir implementation. Each addressed limitations of the previous.

## 1. Single-Population Coevolution

**Design**: One population, dual roles. Every individual can be solver and tester depending on interaction context.

- **Solver**: run phenotype against context -> output
- **Tester**: run phenotype against base context -> output IS the expected answer for peers

```
fitness = w_solve * solve_score
        + w_test * test_effectiveness
        + w_robust * static_baseline_score

solve_score = fraction of peer tests I pass
test_score  = frontier_score(solver_pass_rate)  # peaks at 50%
robust_score = performance on external baseline problems
```

**Selection**: (mu+lambda) with elitism (top 3 always survive), tournament selection (best of 3 random), crossover rate 30%.

**Result**: Works with multi-context profiles (3+ contexts prevent collusion). Maintains ~15 phenotype niches. But limited to simple solver/tester dynamics.

## 2. Interactive Coevolution

**Design**: Population + archive (hall of fame) with staged information exposure.

**Archive**: Maintains best solver and best tester from history. Deduplicates by phenotype. Provides stable selection pressure, prevents coevolution cycling.

**Staged info exposure**:
- Phase 1: Testers see only solver profile (aggregate fitness stats)
- Phase 2: Add solver phenotype source code
- Phase 3: Add solver genotype string

**Match tool**: Testers can structurally pattern-match solver code:
```
(tool/match {:pattern "(count *)"})  # wildcard * matches any subexpression
```

**Challenge system (original, replaced)**: Hash-based ChallengeDecoder mapped tester output to ChallengeSpec via modular arithmetic. Created arbitrary mapping with no semantic relationship. Small mutations -> completely different challenge types.

**OutputInterpreter (replacement)**: Tester's phenotype output IS the data transformation. If tester produces a list of maps, it directly replaces the relevant data source. Small genotype mutations -> small transformation changes -> smooth fitness gradient.

**Evaluation flow**:
```
For each tester:
  For each base_context:
    1. Build tester_context with solver info (phase-dependent)
    2. Run tester phenotype -> raw_output
    3. Interpret raw_output as context modification (OutputInterpreter)
    4. For each solver:
       a. Run solver on modified_context -> solver_answer
       b. Oracle evaluates modified_context -> expected
       c. Score solver_answer vs expected
```

## 3. Triad Coevolution

**Design**: One population, three simultaneous roles. Every individual can be solver, tester, AND oracle. No external task definitions — population self-generates tasks.

**Protocol for each triple (solver S, tester T, oracle O)**:
1. T runs against base context -> T_output
2. OutputInterpreter(T.source, T_output, base_ctx) -> modified_ctx
3. O runs against modified_ctx -> expected_answer (oracle defines "correct")
4. S runs against modified_ctx -> solver_answer
5. S passes if solver_answer == expected_answer

```
fitness = w_solve * solve_score
        + w_test  * test_effectiveness
        + w_oracle * oracle_frontier_score
```

**Per-role elitism**: Preserve best solver-specialist, best tester-specialist, best oracle-specialist even if overall fitness is lower.

**Tester potential gradient**: Since evolving programs that produce list-of-maps is hard, a gradient rewards output type: nil -> 0.0, scalar -> 0.02, list -> 0.08, list-of-maps -> 0.15.

**Result (pop=50, len=30, 30 gens)**: Solver and oracle roles activate immediately. Test role has gradient (0.02) but testers haven't produced list-of-maps. The fundamental problem is **role conflict**: a tester-specialist (test=1.0, solve=0.0, oracle=0.0) gets fitness 0.3 while a solver-specialist (solve=0.9) gets 0.36. Testers can never compete on overall fitness.

**Conclusion**: Role conflict is fundamental in single-population multi-role design. Per-role elitism keeps one tester alive but can't create a lineage.

## 4. Separated Coevolution (Best Design)

**Design**: Three independent populations, each with unambiguous selection pressure.

**Solvers** (pop=30):
- Fitness = fraction of (tester, oracle) pairs where solver matches oracle
- Gate: must be data-dependent (different output on different contexts)

**Testers** (pop=30):
- Phenotype output becomes modified context (via OutputInterpreter)
- Fitness = frontier_score(solver_fail_rate under my modification)
- Gate: must produce valid data transformation (list of maps)

**Oracles** (pop=30):
- Phenotype output is the expected answer
- Fitness = frontier_score(solver_match_rate)
- Gate: must produce non-nil output and be data-dependent

**Key parameters**:
```
generations: 20-200
solver_pop/tester_pop/oracle_pop: 20-30
genotype_length: 25-50
elitism: 2
tournament_size: 3
crossover_rate: 0.3
samples: 10  # matchups per individual per generation
```

### Evolution of the Design

**v1 — Basic three-population**: Role activation solved (30/30 valid testers by gen 3). But all populations collapsed to constant-expression agreement. Solver pass rate: 100%.

**v2 — Hybrid oracle anchor**: Anchored oracle fitness to external ground truth. Oracle correctness = 0.0 for all 100 gens — target phenotype too hard to reach from random init. Dropped.

**v3 — Data-dependence gate**: Fitness = 0 if output identical on all base contexts. One line of logic. Results:
- Solver avg fitness: 0.66-0.69
- 30/30 discriminating testers at 66.7% pass rate
- No collapse across 200 generations
- Stable equilibrium around `count + rest + reverse` (3-bond programs)

## Frontier Score Function

Used for tester and oracle fitness. Rewards the difficulty frontier — programs that are neither trivial (everyone passes) nor degenerate (no one passes).

```python
def frontier_score(pass_rate):
    # Peaks at 0.5, declines symmetrically
    return 1.0 - abs(2.0 * pass_rate - 1.0)
```

A tester where 50% of solvers fail gets max score. A tester where 0% or 100% fail gets 0.

## OutputInterpreter

Converts tester phenotype output into a modified data context:
- If output is list of maps -> replaces the detected data source in context
- If output is non-list or empty -> identity (no modification)
- Detects which data source by scanning tester source for `data/X` references

This is the key innovation over hash-based challenge decoders: small genotype mutations -> small transformation changes -> smooth fitness gradient. The tester's program IS the transformation.

## Lessons Learned

1. **Role conflict kills single-population multi-role designs.** Even with per-role elitism.
2. **Separate populations with focused selection pressure work best.** No compromise fitness functions.
3. **Constants are the degenerate attractor.** Block them structurally (data-dependence gate).
4. **Multi-context evaluation is essential.** 3+ contexts prevent collusion.
5. **Frontier scoring at 50% works well** for tester/oracle selection pressure.
6. **Direct output interpretation > hash-based challenge decoding.** Smooth gradient matters.
7. **The complexity ceiling is the fundamental limitation**, not the coevolution design.
