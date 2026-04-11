# GPU-Friendly Redesign: Dataflow Experiment and Next Steps

Design notes for GPU-parallel folding. Direction A (broadcast dataflow) was
implemented and tested — it answered the key question but is not viable as
the main path. Direction B (layered immutable chemistry) is the recommended
next step.

Target hardware: Apple M1 (unified memory, Metal compute shaders).

## Problem: Why the Current Pipeline is GPU-Hostile

Three blockers, in order of severity:

### 1. Chemistry is sequential and self-modifying (the killer)

The 5-pass `assemble()` mutates the graph as it runs. `bond()` in `engine.rs`:
- Consumes child positions → changes what later bonds can see
- Merges child adjacencies into parent → creates new neighbor edges
- Each bond depends on all previous bonds

This is fundamentally serial *within one individual*. Rayon parallelizes across
individuals, but GPU needs parallelism within each individual too.

### 2. Variable-size hash maps everywhere

`Grid = IndexMap<Pos, u8>`, `FragmentMap = IndexMap<Pos, Fragment>`,
`Adjacency = FxHashMap<Pos, Vec<Pos>>`. GPU needs fixed-size, contiguous memory.

### 3. Variable-size ASTs + stack VM

Programs have different sizes, instruction counts, and data flow patterns.
GPU threads that diverge (different branch paths) lose all parallelism.

### Performance context

Profiling (commit `82f74c0`) shows 91% of develop time is in chemistry
`assemble()`, not fold. Rust is only 5-6x faster than Python here because
both are dominated by hash map operations (Python dicts are C-backed).
The Rayon batch path gives ~10x total over per-individual Python, but
the fundamental bottleneck is architectural, not language-level.

## What Must Be Preserved

From experimental findings:
- **Folding creates pleiotropy** — mutations rearrange 2D topology
- **Self-avoidance creates junk DNA** — neutral mutation absorption
- **Bond accumulation creates gradual complexification**
- **Regime shift adaptation** — folding adapts to new targets, direct encoding can't
- **Scarcity and exclusion** — bonds consume positions, creating competition
- **Developmental cascade** — pass ordering constrains what later passes can build

## Direction A: Broadcast Dataflow — TESTED, NOT VIABLE

Implemented in `rust/src/dataflow/`, tested, and dropped as main direction.

### What it was

Eliminated AST construction. The folded grid was the program. Values
propagated via K rounds of broadcast message passing: `get` operated
element-wise on lists-of-dicts, comparators produced bool-lists, `filter`
used boolean masks, wildcards acted as relay cells.

### Experimental results

| Metric | Chemistry | Dataflow |
|--------|-----------|----------|
| Speed (200 ind × 300 gens) | 8.2ms/gen | 12.7ms/gen |
| Random nonzero fitness | 3/200 (1.5%) | 152/200 (76%) |
| Evolution (100 gens, 3 seeds) | improves | stuck at 0.7688 |

### Why it failed

**Broadcasting removed scarcity, and without scarcity there is no selection
pressure toward composition.**

- 76% random nonzero fitness means the representation is far less selective
  than chemistry. The landscape is smooth and dense.
- Evolution immediately found `count(data/products)` (a raw data source
  shortcut) scoring 0.7688, and could not escape — no gradient toward the
  harder compositional target `count(filter(price>200, products))`.
- Slower on CPU (12.7ms vs 8.2ms) due to `Vec<Value>` cloning per round,
  removing the practical justification for an intermediate architecture.

### What this tells us about evolutionary dynamics

1. **Scarcity (exclusive consumption) is load-bearing.** It forces evolution
   to compete for bonding partners, which is what drives composition.
2. **Developmental cascades (pass ordering) create structure.** Without them,
   the system rewards shallow reusable signals too early.
3. **Smooth ≠ evolvable.** A smoother landscape with more nonzero fitness
   does not produce better evolution — it produces easier shortcuts.
4. **The old system's punctuated dynamics (24% catastrophic breaks) are a
   feature, not a bug.** They prevent exploitation of shallow correlates.

### What to keep from Direction A

- **Fixed array-backed fold** (`rust/src/dataflow/grid.rs`): the 32×32
  `[u8; GRID_SIZE]` fold and `NeighborTable` are reusable for Direction B.
- **Tests** (`tests/test_dataflow.py`): validates the fixed-grid fold.
- **The lesson**: broadcast dataflow smooths the landscape and induces
  shortcut traps. Any GPU acceleration must preserve exclusion and bond
  competition.

### Code location (can be removed)

```
rust/src/dataflow/         — Rust dataflow module (grid.rs, evaluate.rs)
src/folding_evolution/phenotype_dataflow.py — Python wrapper
tests/test_dataflow.py     — Tests
```

To remove: delete the above, remove `mod dataflow;` from `lib.rs`, remove
the two PyO3 function registrations and their `#[pyfunction]` blocks.

## Direction B: Layered Immutable Chemistry (Recommended Next Step)

Keep the 5-pass chemistry semantics — including exclusion and pass ordering —
but make each pass a pure function on fixed-size arrays.

```
Current:  mutate fmap + adj + consumed in place across all passes
Proposed: pass_N reads layer_{N-1} → writes layer_N (immutable input, new output)
```

### Why this preserves dynamics

- **Exclusion**: two-phase propose/accept within each pass. Each cell
  proposes which neighbors it wants to bond with. Conflicts resolved by
  position priority (lower grid index wins). Only one bond per consumed
  position.
- **Pass ordering**: passes still run sequentially (pass 1 output feeds
  pass 2 input). The developmental cascade is preserved.
- **Same language**: produces the same AST structures as the current
  chemistry, with minor determinism differences from conflict resolution.

### How to parallelize

Each pass becomes a GPU kernel (or a parallel CPU loop on fixed arrays):

```rust
// Phase 1: Propose — each cell independently identifies its bond candidates
fn propose_leaf_bonds(grid: &FixedGrid, layer: &[Fragment; N*N]) -> [BondProposal; N*N]

// Phase 2: Accept — resolve conflicts (position priority), apply bonds
fn accept_bonds(proposals: &[BondProposal; N*N], layer: &mut [Fragment; N*N])
```

The propose phase is embarrassingly parallel. The accept phase needs
conflict resolution but is still parallelizable with priority rules.

### Reusable components from Direction A

- `FixedGrid` type and `fold_fixed()` from `dataflow/grid.rs`
- `NeighborTable` for O(1) neighbor lookup
- The 32×32 grid size (validated: handles genotype_length=100 without
  clipping)

### Implementation plan

1. Port `FixedGrid` + `NeighborTable` to a shared `grid` module (out of
   `dataflow/`)
2. Implement layered chemistry: `[Fragment; GRID_SIZE]` per pass layer,
   propose/accept bond resolution
3. Compile resulting AST fragments to bytecode (reuse existing VM)
4. Benchmark against current IndexMap chemistry
5. If faster: wire into `develop_and_score_batch` as the default path

### Conflict resolution detail

When two adjacent `get` cells both want to bond with the same `:price`:

```
Cell A at index 100 proposes: bond with :price at index 101
Cell B at index 115 proposes: bond with :price at index 101

Resolution: Cell A wins (lower index). Cell B gets no bond this pass.
```

This is deterministic and matches the spirit of the current IndexMap
iteration order (which processes positions in insertion order).

Two-phase parallel resolution:

```
Phase 1 (parallel): each cell writes its proposal to a proposals array
Phase 2 (parallel): each "consumed" cell checks all proposals that claim it,
         accepts the one with lowest proposer index, rejects others
Phase 3 (parallel): accepted proposers write their assembled fragment
```

## Validation Plan

### Phase 0: Isolate what sequential chemistry contributes

Before building layered chemistry, test what exclusive bonding and pass
ordering contribute separately. Modify the existing chemistry:

- **Condition X**: Current chemistry (sequential, exclusive) — baseline
- **Condition Y**: Same 5 passes, but broadcasting (no consumption) —
  isolates exclusivity
- **Condition Z**: Full dataflow (K rounds, no pass ordering) — already
  tested (Direction A result above)

If Y ≈ X → exclusivity alone doesn't matter, pass ordering is the key.
If Y ≠ X → exclusivity is essential (likely, given Direction A results).

### Phase 1: Implement Direction B on CPU

- Fixed-size grid fold (reuse from Direction A)
- Layered immutable chemistry with propose/accept
- Same bytecode VM for evaluation
- Rayon parallelism across individuals

### Phase 2: Equivalence testing

- Compare Direction B outputs against current chemistry on 1000+ genotypes
- Measure determinism differences from conflict resolution
- Run regime shift experiment: must match current dynamics within noise

### Phase 3: GPU port (only if Phase 2 confirms equivalence)

Target: Apple M1 Metal compute shaders via `wgpu`.
- Fixed-grid fold on CPU (sequential per-individual, fast)
- M1 unified memory: grid arrays directly GPU-visible, zero copy
- 5 chemistry passes → 5 × 2 GPU kernels (propose + accept)
- Bytecode VM evaluation → GPU kernel per individual
- Scale to 10K+ populations

## GPU Technology: Apple M1 Metal

Target hardware: M1 with unified memory (8-16 GB shared between CPU and GPU).

| Option | Fit for M1 | Notes |
|--------|------------|-------|
| **wgpu** (Rust) | Cross-platform, Metal backend on macOS | Recommended |
| **metal-rs** (Rust) | Native, best M1 performance | Fallback if wgpu is too slow |

### M1 unified memory advantage

No CPU↔GPU memory transfer. A grid array allocated in Rust is directly
readable by Metal compute shaders — zero copy. Threadgroup shared memory
(32 KB) fits a 32×32 grid + fragment layers easily.

M1 GPU: 128 execution units, ~2.6 TFLOPS.

### Estimated performance (Direction B)

Current (CPU, Rayon, pop=200):
- develop_batch: ~8ms/generation
- Total per seed (300 gens): ~5s

Projected (M1 GPU, pop=10,000, Direction B):
- Fold: CPU, ~8ms for 10K individuals (Rayon)
- 5 chemistry passes × 2 kernels: ~5-10ms (with fixed arrays, no hash maps)
- VM evaluation: ~2-5ms (one thread per individual)
- Total per seed (300 gens): ~5-8s at 50x population size

The GPU win is population scale, not per-individual speed.
