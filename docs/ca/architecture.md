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

## A concrete run, end to end

Everything below is grounded in one real run: `experiments/ca/output/mvp/117db496acd2` — seed 5 of the MVP sweep, 4-bit parity at `K=4, N=16, T=16`, final fitness `1.000`. Numbers and grid states are copied verbatim from replaying the evolved rule.

### The grid, drawn

A `16×16` board. Each cell holds a single integer in `{0, 1, 2, 3}` — that's what `K=4` means: every cell is in one of 4 discrete states at every timestep. You can read the states as "colors" or "cell types"; they carry no intrinsic meaning, evolution decides what each state does.

For 4-bit parity, the 4 input bits go into the **center of row 0** (columns 6–9). State `0` encodes bit 0; state `1` encodes bit 1. States `2` and `3` never appear on row 0 at `t=0` — they're workspace the rule is free to use internally.

Initial grid for input bits `[1, 0, 0, 0]`:

```
col:    0         1
        0123456789012345
row 0:  0000001000000000   <- clamped input: bits at cols 6..9
row 1:  0000000000000000
row 2:  0000000000000000
  ...   (all zero)
row 15: 0000000000000000   <- row 15, col 8 is the readout cell
```

Row 0 is **clamped** — re-asserted at every step, so it stays `0000001000000000` for the entire run. The CA can't overwrite its own input. Everything below row 0 evolves.

### One update step, worked by hand

The rule for this run is a `(K, 8·(K-1)+1) = (4, 25)` table. Seed 5's evolved table starts:

```
         neighbor_sum: 0  1  2  3  4  5  6  7  8  ...  24
self=0:                1  3  0  2  1  1  2  1  3  ...   0
self=1:                0  3  3  2  1  1  2  2  0  ...   1
self=2:                0  0  1  3  1  0  2  3  3  ...   0
self=3:                3  2  3  0  0  3  2  3  3  ...   3
```

A cell's next state = `table[self_state, sum_of_its_8_Moore_neighbors]`. Two worked examples from row 1 at `t=0 → t=1`:

- **Cell (1, 0)** — far from the input. `self=0`, all 8 neighbors are 0, `neighbor_sum=0`. Look up `table[0, 0] = 1`. Next state: `1`.
- **Cell (1, 6)** — directly under the lone input bit. `self=0`. Neighbors: row 0 cols 5,6,7 = `0,1,0` and row 1 cols 5,7 = `0,0` and row 2 cols 5,6,7 = `0,0,0`. `neighbor_sum=1`. Look up `table[0, 1] = 3`. Next state: `3`.

So at `t=1` the whole of row 1 becomes `1`s, except a small `333` bump under the active input bit. Evolution has discovered: *use state 3 to mark "an input bit was 1 in my neighborhood."* That marker is what propagates down the grid.

### Four snapshots of a successful run

Input `[1, 0, 0, 0]` → true parity `1`. The readout cell is `(15, 8)`; the prediction rule is `state > K/2`, i.e., state `3` → predicted bit `1`, states `0/1/2` → predicted bit `0`.

```
t=0 (initial, only row 0 set):        t=1 (after one step, row 0 re-clamped):
0000001000000000                      0000001000000000
0000000000000000                      1111133311111111   <- "333" marks the active bit
0000000000000000                      1111111111111111
... (all zero) ...                    1111111111111111
                                      ... (rows 3..15 all 1s) ...

t=4 (structure has reached row 12):   t=16 (final):
0000001000000000                      0000001000000000
1032302032322301                      2303200332323323
0000333330133100                      3021220302233033
3132321232222313                      1330310023030003
2320303030000232                      1132212130333300
2320000000000232                      2030320333101002
... 2320000000000232 ...              ... mixed 0/1/2/3 ...
3132222222222313                      3102003022023212
0013333333333100                      0110222300101123
1032222222222301                      3033131333101332   <- row 15
                                                ^ col 8 = state 3
```

At `t=16` the readout cell `(15, 8)` is in state `3` → `3 > 2` → prediction `1`. Correct.

Running the same evolved rule on input `[0, 0, 0, 0]` (parity `0`) ends with cell `(15, 8)` in state `2` → `2 > 2` is false → prediction `0`. Also correct. The rule generalizes across all 16 inputs in this run's training set — that's what "fitness = 1.000" means here.

### What the evolved rule is actually doing

From the snapshots, informally:

1. **Amplify: a fast fill.** In one step the 0-background promotes itself to state 1 everywhere (`table[0,0]=1`), except where an input bit sat above it. So `t=1` is a near-uniform sea of 1s with a thin trace of 3s marking input-1 positions.
2. **Propagate: state 3 as a carrier.** Column regions under input-1 bits stay 3-dominated in rows 2–4; the rule routes this pattern downward and outward.
3. **Mix: interference at depth.** By `t=8` the grid is a jumble of all four states. But it's not random — replaying with a *different* input (e.g. flipping one bit) produces a visibly different jumble, and the evolved rule arranges for the readout cell specifically to carry the parity answer.
4. **Readout: one cell, one threshold.** Only cell `(15, 8)`'s final state matters. Everything else is scratch space the rule uses to get the right bit to that one location.

This is what "evolving a CA to compute parity" looks like concretely — not a clean circuit, not an interpretable algorithm. Just a rule table of 100 numbers that pushes the grid into states whose readout cell happens to carry the parity bit after 16 steps. Whether this counts as "computing" parity or "memorizing" parity on a specific training set is exactly the question sweep §9 in [experiments.md](experiments.md) runs into at 8 bits.

You can reproduce the snapshots above with:

```
python experiments/ca/inspect_best.py experiments/ca/output/mvp/117db496acd2 --show-grid
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
