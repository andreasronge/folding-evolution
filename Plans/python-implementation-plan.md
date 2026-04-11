# Plan: Python Implementation for Folding Evolution

## Context

Migrating the folding evolution GP/ALife research from Elixir/PTC-Lisp to Python. The Elixir implementation is 22 files / 5,279 lines. We do not need the full PTC-Lisp interpreter (2,980 lines) — evolved programs are small (max 3-5 bonds, ~15 operation types) and the chemistry produces ASTs directly.

**Goal of this plan**: Reproduce the regime-shift result (folding outperforms direct encoding under shifting targets) in Python. Everything else is follow-on work.

Currently: zero Python code, Python 3.13.1 available.

---

## Milestone 1: Core Phenotype Engine

Build the genotype → phenotype pipeline and verify it against the golden test.

### Files

```
folding-evolution/
├── pyproject.toml
├── src/folding_evolution/
│   ├── __init__.py
│   ├── alphabet.py        # char → (fragment_type, fold_instruction)
│   ├── ast_nodes.py       # frozen dataclass AST node types
│   ├── fold.py            # genotype → 2D grid with self-avoidance
│   ├── chemistry.py       # 5-pass bond assembly → AST
│   ├── evaluator.py       # AST → value (tiny tree-walk, ~15 node types)
│   └── phenotype.py       # full pipeline: genotype → (program, source_str, bond_count)
└── tests/
    ├── test_alphabet.py
    ├── test_fold.py
    ├── test_chemistry.py
    ├── test_evaluator.py
    └── test_phenotype.py
```

### Dependencies (minimal)

```toml
[project]
name = "folding-evolution"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "numpy>=1.26,<3.0",
    "matplotlib>=3.8,<4.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov>=5.0", "ruff>=0.5"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.setuptools.packages.find]
where = ["src"]
```

Add `pandas`, `scipy`, `seaborn`, `hypothesis`, DEAP, Jupyter only when the milestone that needs them arrives.

### AST Nodes (`ast_nodes.py`)

```python
@dataclass(frozen=True, slots=True)
class Literal:
    value: int | float

@dataclass(frozen=True, slots=True)
class Symbol:
    name: str

@dataclass(frozen=True, slots=True)
class Keyword:
    name: str

@dataclass(frozen=True, slots=True)
class NsSymbol:
    ns: str
    name: str

@dataclass(frozen=True, slots=True)
class ListExpr:
    items: tuple  # (operator, *operands)

ASTNode = Literal | Symbol | Keyword | NsSymbol | ListExpr
```

### Evaluator (`evaluator.py`)

A simple tree-walking evaluator over ~15 node types. Not a compiler — just `match/case` dispatch.

```python
def evaluate(node: ASTNode, ctx: dict) -> Any:
    """Evaluate an AST node against a data context. Returns None on error."""
    match node:
        case Literal(v):       return v
        case Keyword(k):       return k
        case NsSymbol("data", name):  return ctx.get(name)
        case ListExpr(items):  return _eval_list(items, ctx)
        case _:                return None
```

**Operations to implement** (only these, nothing more):

| Operation | Semantics | Notes |
|-----------|-----------|-------|
| `count(coll)` | `len(coll)` | Most common evolved program |
| `first(coll)` | `coll[0]` | Common |
| `rest(coll)` | `coll[1:]` | Common |
| `get(record, key)` | `record[key]` | Field access |
| `filter(fn, data)` | `[x for x in data if fn(x)]` | Target 4-bond |
| `map(fn, data)` | `[fn(x) for x in data]` | Target 4-bond |
| `fn [x] body` | Closure over ctx | Required for filter/map |
| `> < = + -` | Standard Python | Comparators, arithmetic |
| `and or not` | Short-circuit | Logic |
| `if p t e` | `t if p else e` | Conditional |

All error paths return `None`. No step-count timeout — programs have no recursion construct and always terminate.

If profiling later shows the evaluator is a bottleneck, switch to compile-and-cache (AST → Python callable, cached by genotype string). Treat this as an optimization hypothesis, not a design assumption.

### Acceptance Criteria

1. `pytest tests/` passes
2. `develop("QDaK5XASBw")` with context `{"products": [{"price": 600}, {"price": 400}]}` returns `[{"price": 600}]`
3. `develop("QDaK5XASBw")` produces source string `(filter (fn [x] (> (get x :price) 500)) data/products)` and bond_count = 4
4. 1000 random genotypes of length 30: all complete `develop()` without exception
5. Benchmark: `develop()` on 1000 random genotypes of length 50, report time (no target yet — just measure)

### Implementation Order

1. `pyproject.toml` + venv
2. `ast_nodes.py`
3. `alphabet.py` + tests
4. `fold.py` + tests
5. `chemistry.ex` → `chemistry.py` + tests (most complex, ~300-400 lines)
6. `evaluator.py` + tests
7. `phenotype.py` + golden test
8. Benchmark

### Elixir Reference

- `~/projects/ptc_runner/lib/ptc_runner/folding/alphabet.ex` (125 lines)
- `~/projects/ptc_runner/lib/ptc_runner/folding/fold.ex` (136 lines)
- `~/projects/ptc_runner/lib/ptc_runner/folding/chemistry.ex` (609 lines)
- `~/projects/ptc_runner/lib/ptc_runner/lisp/eval.ex` (1,271 lines) — reference for operation semantics only

---

## Milestone 2: Minimal Evolution Loop

Add genetic operators, fitness evaluation, selection, and one baseline encoding. Run the first evolution.

### Files (added)

```
src/folding_evolution/
    ├── operators.py       # point mutation, insertion, deletion, crossover
    ├── individual.py      # Individual dataclass
    ├── direct.py          # direct encoding baseline
    ├── fitness.py         # target-based fitness, data-dependence gate
    ├── selection.py       # tournament + elitism
    ├── evolution.py       # generational loop with callbacks
    ├── data_contexts.py   # base context generation (3+ variations)
    ├── config.py          # EvolutionConfig dataclass
    └── stats.py           # per-generation stats → CSV
tests/
    ├── test_operators.py
    ├── test_fitness.py
    └── test_evolution.py
```

### Fitness

Target-based: evolve a program that produces a specific output given a data context.

```python
def evaluate_fitness(individual, target_fn, contexts):
    """Fraction of contexts where individual's output matches target."""
    matches = 0
    for ctx in contexts:
        output = individual.evaluate(ctx)
        expected = target_fn(ctx)
        if output == expected:
            matches += 1
    return matches / len(contexts)
```

The data-dependence gate: fitness = 0 if output is identical across all contexts.

### Direct Encoding (`direct.py`)

Same alphabet, read left-to-right, sequential assembly. Same `Individual` interface — `develop(genotype) → (ast, source, bond_count)`.

### Config

```python
@dataclass
class EvolutionConfig:
    pop_size: int = 50
    genotype_length: int = 50
    generations: int = 200
    seed: int = 42
    encoding: str = "folding"  # "folding" | "direct"
    mutation_rate: float = 0.1
    crossover_rate: float = 0.3
    tournament_size: int = 3
    elitism: int = 2
```

### Acceptance Criteria

1. Folding encoding, target `count(data/products)`, pop=50, len=30, 100 gens, seed=42: best fitness reaches 1.0 within 50 generations
2. Direct encoding, same setup: record what fitness it achieves (may be 0.0 — that's data, not a failure)
3. Stats CSV written with columns: `generation, best_fitness, mean_fitness, best_source, best_bond_count`
4. 3 different seeds produce different trajectories but all reach fitness > 0.5 for folding
5. Benchmark: full 50-pop × 100-gen run, report wall-clock time and evals/sec

### Implementation Order

1. `operators.py` + tests
2. `individual.py`
3. `direct.py` + tests
4. `fitness.py` + `data_contexts.py` + tests
5. `selection.py`
6. `config.py` + `stats.py`
7. `evolution.py`
8. Run acceptance tests
9. Profile: `cProfile` on the full run, identify where time goes

### Elixir Reference

- `~/projects/ptc_runner/lib/ptc_runner/folding/operators.ex` (85 lines)
- `~/projects/ptc_runner/lib/ptc_runner/folding/direct.ex` (221 lines)

---

## Milestone 3: Regime-Shift Experiment

The minimal decisive experiment: reproduce the finding that folding adapts to regime shifts while direct encoding doesn't.

### Files (added)

```
src/folding_evolution/
    ├── dynamics.py        # regime shift protocol
    └── visualization.py   # fitness curve plotting
experiments/
    └── exp_regime_shift.py
```

### Experiment Design

```python
# Regime A: target = count(data/products) for N generations
# Regime B: target = count(data/employees) for M generations
# Run both encodings, multiple seeds, compare
```

Parameters matching Elixir findings: pop=50, len=30, regime_a=20 gens, regime_b=20 gens.

### Acceptance Criteria

1. Folding encoding: best fitness > 0.5 in regime A (replicates Elixir's 0.792)
2. Folding encoding: fitness drops after regime shift, then recovers to > 0.4 (replicates Elixir's 0.667)
3. Direct encoding: best fitness < 0.2 throughout (replicates Elixir's 0.100)
4. At least 1 fitness jump > 0.1 in a single generation for folding (replicates Elixir's 5 jumps)
5. Results hold across 5 seeds (not 30 yet — that's the follow-on 2×2 experiment)
6. Fitness curve plot saved as PNG showing both encodings across the regime shift

If criteria 1-4 fail to replicate, **stop and investigate** before proceeding. The entire research program depends on this result.

### Implementation Order

1. `dynamics.py` — regime shift protocol
2. `visualization.py` — fitness curve plot (matplotlib only, no seaborn yet)
3. `exp_regime_shift.py`
4. Run with 5 seeds, verify against Elixir findings
5. Save plots and CSV results

### Elixir Reference

- `~/projects/ptc_runner/lib/ptc_runner/folding/dynamics.ex` (371 lines)

---

## Follow-On Work (separate plans, after Milestone 3)

These are scoped but not planned in detail. Each becomes its own plan when the previous milestone is done.

### A. The 2×2 Experiment

The central paper experiment: `{folding, baseline} × {stable, shifting}`.

Requires:
- Calibration: verify baseline encoding can solve stable tasks (if direct can't, add `stack_assembly.py` or DEAP tree GP)
- Batch runner for 120+ runs (4 conditions × 30 seeds)
- Statistical analysis: two-way ANOVA, Wilcoxon, effect sizes (add `scipy`, `pandas`)
- Shift frequency sweep: N = 5, 10, 20, 50

### B. Coevolution

Separated 3-population coevolution with solver/tester/oracle roles.

Requires: `output_interpreter.py`, `coevolution.py`, frontier scoring, multi-context evaluation.

### C. Scale-Up Experiments

Break the complexity ceiling: longer genotypes (80-150), larger populations (100+), more generations (500-1000). Complexity-biased selection.

### D. Mechanism Studies

Motif enrichment, pleiotropy measurement, phenotype frequency distribution. Connects results to Altenberg's constructional selection framework.

### E. Alternative Representations

Stack-based assembly, codon table, DEAP tree GP baseline. For the 2×2 experiment or independent comparison.

---

## What We're NOT Building (in this plan)

- No CLI (`cli.py`) — run experiments directly
- No batch runner — single-seed runs are enough for Milestone 3
- No statistical analysis module — 5 seeds with visual inspection suffices to replicate
- No coevolution — not needed for the regime-shift result
- No notebooks — plots from experiment scripts
- No DEAP integration — follow-on if needed
- No compile-and-cache optimization — profile first, optimize if needed
- No `reduce`, `group-by`, `assoc`, `let`, `match` operations — add when evolved programs need them

## Performance

No target number. Instead, staged measurement:

1. **Milestone 1**: Benchmark `develop()` on 1000 genotypes, report time
2. **Milestone 2**: Benchmark full 50-pop × 100-gen evolution run, report evals/sec
3. **Milestone 3**: Benchmark 5-seed regime shift experiment, report wall-clock time

If any milestone takes more than 10 minutes wall-clock, profile and optimize before proceeding.

## Key Reference Files (Elixir)

Port what's needed per milestone, don't replicate line-for-line:

- `~/projects/ptc_runner/lib/ptc_runner/folding/alphabet.ex` (125 lines)
- `~/projects/ptc_runner/lib/ptc_runner/folding/fold.ex` (136 lines)
- `~/projects/ptc_runner/lib/ptc_runner/folding/chemistry.ex` (609 lines) — most complex
- `~/projects/ptc_runner/lib/ptc_runner/folding/operators.ex` (85 lines)
- `~/projects/ptc_runner/lib/ptc_runner/folding/direct.ex` (221 lines)
- `~/projects/ptc_runner/lib/ptc_runner/folding/dynamics.ex` (371 lines)
- `~/projects/ptc_runner/lib/ptc_runner/lisp/eval.ex` (1,271 lines) — operation semantics reference only
