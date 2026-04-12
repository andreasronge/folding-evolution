# Architecture: CA-Development GP

A parallel research track to the folding pipeline. Instead of a linear genotype that folds onto a 2D grid, the genotype here *is* the update rule of a 2D cellular automaton. The phenotype is the grid configuration after T update steps — reading a designated output cell gives a prediction, which is scored against a task.

Source: `src/folding_evolution/ca/`. Drivers: `experiments/ca/`.

## Overview

```
Genotype (100 bytes — the rule table)
    | decode to (K, max_sum+1) lookup table
    v
CA update rule: next_state = table[self_state, sum_of_neighbors]
    | initialize grid, clamp input bits on row 0
    v
Apply rule for T steps (Moore neighborhood, zero padding, row 0 clamped)
    | read designated output cell
    v
State -> predicted bit
    | compare across all task examples
    v
Fitness = fraction correct
```

## Layer 1: Rule family

**Outer-totalistic, K-state, 8-neighbor (Moore).**

The update rule depends only on (a) a cell's own current state and (b) the *sum* of its 8 neighbors' states — not on the individual neighbor positions. This is the classical Game-of-Life style abstraction.

For K states and 8 neighbors, the max neighbor sum is `8·(K-1)`, so the rule table has shape `(K, 8·(K-1)+1)`:

| K | Table shape | Entries | Genotype length |
|---|-------------|---------|-----------------|
| 2 | (2, 9)      | 18      | 18 bytes        |
| 4 | (4, 25)     | 100     | 100 bytes       |
| 8 | (8, 57)     | 456     | 456 bytes       |

Each table entry is itself a state in `[0, K)`. The genotype is the flat table laid out row-major; one byte per entry.

Other rule families (symbolic, neural, asymmetric) plug in via the `rule_family` config field. Only outer-totalistic is implemented so far.

## Layer 2: Genotype and operators

The genotype is a flat `uint8` array. Nothing more. No grammar, no trees, no variable-length structure.

- **Initialization**: each byte sampled uniformly from `[0, K)`.
- **Mutation**: per-byte random-reset. Each byte is independently replaced with a uniform draw at probability `mutation_rate` (default 0.03).
- **Crossover**: single-point splice on the flat array.

Mutation rate and crossover rate are sweep axes.

## Layer 3: Grid, I/O, and the task interface

A task is a dataclass with `inputs`, `labels`, and two callables:

- `encode(inputs, cfg) → (B, N) clamp row` — how input examples get placed onto the CA grid.
- `decode(output_states, cfg) → labels` — how an output cell's final state becomes a predicted label.

### Parity task (current default)

- Grid: `N × N`, each cell in `{0, …, K-1}`. Default `N = 16`.
- Input: `n_bits` bits placed in the **center of row 0**. Cell state 0 = bit 0; cell state 1 = bit 1. States `≥ 2` unused by the encoding.
- Boundary: **row 0 is clamped** to the input each step. The input is not a one-shot initial condition — it is continuously re-asserted.
- Workspace: rows 1..N-1 start at zero.
- Steps: `T` applications of the rule. Default `T = N`.
- Output: the final state of a designated cell (`output_row`, `output_col`; defaults to last row, center column). Predicted bit: `state > K/2`.
- Fitness: fraction of `n_examples` parity questions answered correctly. If `n_examples ≥ 2^n_bits`, the full truth table is used.

The encoding/decoding choice is deliberately minimal — discrete in, discrete out, no hand-tuned readout. The CA has to *compute* the answer, not just carry the input to the output cell.

## Layer 4: Evaluation batching

This is the performance-critical choice. Given population size `P` and `E` task examples, naively we'd run `P·E` separate simulations. Instead:

- Rule tables stack into `(P, K, S)`.
- Broadcast to `(P·E, K, S)` — every rule paired with every example along one flat batch axis.
- Input clamp rows broadcast to `(P·E, N)`.
- Initial grid `(P·E, N, N)` of zeros.

One call to the step kernel advances *every rule × every example* by one step. For `P=256, E=64, N=16, T=16` that's `≈4M` cells per step, 16 dispatches per generation.

The batch is flattened, not nested — no MLX/NumPy loop over populations. This is what makes sweep-scale experiments affordable on M1.

## Layer 5: Backends

Two interchangeable step kernels behind a one-line dispatcher:

| Backend | File                | When to use                                   |
|---------|---------------------|-----------------------------------------------|
| NumPy   | `engine_numpy.py`   | Reference / correctness baseline / CI         |
| MLX     | `engine_mlx.py`     | M1 Metal acceleration for sweeps              |

Both produce bitwise-identical results on fixed seeds (verified by `tests/test_ca_engine_parity.py`). The `backend` config field selects at runtime. Downstream code is backend-agnostic — MLX outputs are converted back to NumPy `uint8` before evaluation.

## Layer 6: Evolution loop

Standard generational GA:

1. Initialize population of `pop_size` random genotypes.
2. Evaluate (batched as above).
3. Each generation:
   - Copy top `elite_count` individuals unchanged.
   - Fill remaining slots: with probability `crossover_rate`, draw two parents by tournament (size `tournament_size`) and splice; else copy a single tournament winner. Always mutate the child.
4. Record per-generation stats: best/mean/std fitness, count of unique genotypes, hex of the best.
5. Return best genotype and full history.

Tournament selection, elitism, and per-byte mutation are the entire GA — no niching, no island model, no adaptive rates. The question this module asks is *whether the representation is evolvable at all*; exotic GA machinery would confound the answer.

## Layer 7: Experiment driver

Everything above is a pure function of one frozen `CAConfig` dataclass. The config's SHA-1 hash names its output directory. This gives:

- **Reproducibility**: same config → same hash → results live at the same path.
- **Resumability**: sweeps skip any config whose `result.json` already exists.
- **Sweep-first design**: a sweep is a YAML file declaring `base` fields and a `grid` (or `paired`) of override axes. `experiments/ca/sweep.py` expands the Cartesian product, runs each, and writes an index.

Outputs per run:

```
output/<sweep>/<hash>/
    config.yaml      # the exact config used
    result.json      # best_fitness, best_genotype_hex, elapsed_sec, ...
    history.csv      # per-generation stats (human-readable)
    history.npz      # per-generation stats (fast reload for analysis)
```

## Scope boundary

This module does **not** touch the folding pipeline, the Rust backend, or existing experiment scripts. The only shared dependency is the Python environment (`pyproject.toml` gains `mlx` and `pyyaml`). CA-GP lives in parallel — it's a second representation under test, not a refactor of the first.

See [experiments.md](experiments.md) for sweep-level hypotheses and results.
