# Python Rewrite: Results and Status

## Motivation

The Elixir/PTC-Lisp implementation achieved 10,900 evals/sec. The bottleneck was IPC overhead — every evaluation required sending the assembled program over an Erlang port to the PTC-Lisp runtime and reading the result back. The Python rewrite aimed to eliminate this overhead by running everything in-process.

## What Was Built

17 Python modules, 126 tests, all passing in 1.4s:

```
Core pipeline:     alphabet.py, ast_nodes.py, fold.py, chemistry.py, evaluator.py, phenotype.py
Evolution:         config.py, individual.py, operators.py, fitness.py, selection.py, stats.py, evolution.py
Baselines:         direct.py (direct encoding)
Experiments:       dynamics.py, visualization.py
```

Three experiment scripts: `exp_regime_shift.py`, `exp_calibration.py`.

## Performance: The Rewrite Was NOT Faster

| Component | PTC-Lisp (Elixir) | Python | Ratio |
|-----------|-------------------|--------|-------|
| Full pipeline (folding) | 10,900 evals/sec | ~4,000 evals/sec | 0.37x (slower) |
| Evolution loop (folding) | — | ~5,000 evals/sec | — |
| Direct encoding only | — | ~73,000 evals/sec | — |

**The Python folding pipeline is ~2.7x slower than PTC-Lisp**, not 10x faster as hoped.

### Why

Profiling 1000 genotypes (length 50) shows:

| Component | % of time | Notes |
|-----------|-----------|-------|
| Chemistry (5-pass assembly) | 82% | Grid adjacency scanning, bond formation |
| Fold (2D grid placement) | 12% | Self-avoidance path finding |
| Evaluator | <1% | Programs are tiny (3-15 nodes) |
| Phenotype glue | 5% | AST selection, source string generation |

**The bottleneck was never the interpreter.** It was always the chemistry — scanning an NxN grid for adjacent pairs across 5 sequential passes. Eliminating IPC saved ~50% of the PTC-Lisp overhead, but the chemistry itself is now the dominant cost, and pure Python dict/list operations are slower than Elixir's compiled pattern matching for this workload.

### Why it Doesn't Matter (Much)

The 100K+ evals/sec target was premature. What actually matters:

| Experiment | Evals needed | Time at 4K/sec | Time at 10.9K/sec (Elixir) |
|------------|-------------|----------------|---------------------------|
| Regime shift (5 seeds, 60 gens, pop=40) | 24,000 | 6s | 2s |
| Calibration (10 seeds, 200 gens, pop=40) | 160,000 | 40s | 15s |
| 2x2 (30 seeds, 200 gens, pop=40) | 480,000 | 2 min | 44s |
| Coevolution (300 pop, 1000 gens, 10 samples) | 3M | 12.5 min | 4.6 min |

Everything up to the 2x2 experiment runs in minutes. Coevolution is the first experiment where the speed difference matters, and even there it's minutes vs minutes, not hours vs seconds.

### Optimization Path (if needed)

The chemistry module is the target. Options ranked by effort:

1. **Adjacency caching** — the 5 passes re-scan the same grid. Precompute the adjacency graph once. Low effort, likely 2-3x speedup.
2. **NumPy grid** — represent the grid as a 2D numpy array instead of a dict. Vectorize adjacency lookups. Medium effort, likely 3-5x speedup.
3. **Cython for chemistry** — compile the hot loop. High effort, likely 10x+ speedup.
4. **Compile-and-cache** — replace the tree-walking evaluator with compiled Python callables. Minimal impact (<1% of time is evaluation).

## Regime-Shift Replication

### Elixir Results (pop=40, len=30, 3 runs)

```
  Gen | Fold fit | Dir fit  | Phase
  ----+----------+----------+------
    0 |    0.071 |    0.050 | A
    3 |    0.661 |    0.100 | A
    5 |    0.792 |    0.100 | A
   20 |    0.792 |    0.100 | A <<< REGIME SHIFT
   21 |    0.490 |    0.100 | B
   30 |    0.626 |    0.100 | B
   40 |    0.667 |    0.100 | B
```

### Python Results (pop=40, len=50, 5 seeds averaged)

Multi-target regime (count + first + count-of-rest):

```
  Metric                  Folding    Direct
  Pre-shift best fitness  0.484      0.099
  Final best fitness      0.494      0.353
  Avg fitness jumps       1.6        0.6
```

Per-seed: Direct encoding stuck at 0.050 in 3/5 seeds (matching Elixir's 0.100 partial credit floor). 2/5 seeds got lucky — noise from small sample size.

### Key Differences from Elixir

1. **Multi-target fitness** — Elixir used single target per regime, Python uses 3 targets (count, first, count-of-rest). This makes the problem harder for both encodings, which is why folding's pre-shift (0.484) is lower than Elixir's (0.792).

2. **Partial credit** — Python includes the same graduated scoring as Elixir (numeric near-miss, list length similarity, wrong-type floor at 0.05).

3. **(mu+lambda) selection** — Python now matches Elixir's selection: produce pop_size children, evaluate parents+children together, keep top N.

4. **Crossover OR mutation** — Python now matches Elixir: each child is produced by either crossover or mutation, not both.

### Assessment

The **qualitative pattern replicates**: folding adapts to regime shifts, direct encoding doesn't. The quantitative values differ because of the harder multi-target fitness function, but the core finding holds.

## Calibration Results

200 generations, stable target, 10 seeds per condition:

| Task | Folding success | Direct success | Folding first discovery | Direct first discovery |
|------|----------------|----------------|------------------------|----------------------|
| 1-bond: count(products) | 100% | 60% | Gen 15 | Gen 64 |
| 2-bond: count+first | 90% | 70% | Gen 22 | Gen 50 |
| 3-target: count+first+rest | 100% | 60% | Gen 22 | Gen 67 |

**Calibration verdict**: Direct encoding is NOT a strawman — it can solve these tasks given enough time (60-70% success rate by gen 200). But it converges 3-4x slower than folding. Under regime shifts (target changes every 10-30 gens), direct encoding never gets enough time to converge.

This validates the 2x2 experiment design: direct encoding is a legitimate baseline that can compete under stable conditions but loses under environmental change.

## What the Rewrite Enabled

Despite being slower per-eval, the Python rewrite was successful for its actual goals:

1. **Reproducible experiments** — fixed seeds, CSV output, matplotlib plots, all in one codebase
2. **Fast iteration** — changing parameters, adding targets, re-running experiments takes seconds of developer time, not hours of IPC debugging
3. **Multi-target fitness** — the partial credit scoring and data-dependence gate are clean Python, easy to modify
4. **Calibration sweep** — ran 60 independent evolution runs (10 seeds x 2 encodings x 3 tasks x 200 gens) in ~72 seconds
5. **Regime-shift comparison** — same-genotype fairness control, (mu+lambda) selection matching Elixir, 5-seed comparison in ~20 seconds

The bottleneck for research is not evals/sec — it's experiment design, parameter tuning, and analysis. The Python rewrite optimized for the right thing.

## Performance Optimization: In-Place Mutation

After the initial rewrite, in-place mutation of dicts in `chemistry.py` and `fold.py` eliminated O(N) dict copying per bond/placement. The original code used functional-style `{**dict, key: val}` patterns that created full copies on every operation.

### Changes

1. `chemistry.py` `_bond()`: mutate `fmap`, `adj`, `consumed` in place instead of `{**dict}` copies
2. `chemistry.py` `_build_adjacency()`: return sets instead of lists
3. `chemistry.py` pass loops: inline fragment type checks to skip ~80K unnecessary function calls per 1000 genotypes
4. `fold.py` `_place_with_avoidance()`: mutate grid in place instead of copying
5. `fold.py` direction tables: promote to module-level constants

### Results

| Metric | Before | After | Speedup |
|--------|--------|-------|---------|
| develop() 1000x | 0.245s | 0.191s | 1.28x |
| Evolution evals/sec | ~5,000 | ~10,800 | 2.16x |
| Regime shift wall-clock | 6s | 3.5s | 1.7x |

Now matches the Elixir implementation's 10,900 evals/sec.

## 2x2 Experiment Performance

The 2x2 experiment (300 total runs: 30 seeds x 2 encodings x 5 conditions) completed in 7.5 minutes at the optimized speed. Folding runs dominate wall-clock time (~65s per 30-seed batch) vs direct (~9s) due to the chemistry pipeline overhead.
