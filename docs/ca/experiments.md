# CA-Development GP — Experiments

Ordered by the question each one answers. Every experiment is a YAML sweep under `experiments/ca/sweeps/`; results live under `experiments/ca/output/<sweep>/`.

See [architecture.md](architecture.md) for the representation itself.

## The overall question

Can a 2D cellular automaton rule be *evolved* to compute a non-trivial function? The CA is a candidate developmental representation — if evolution can find rules that compute parity (a notoriously GP-hard function under most encodings), the module earns its place as an alternative to folding for the cross-representation study in `docs/future-directions.md`.

The sweeps below are ordered from *does it work at all* → *where does it break* → *what axes matter*.

---

## Methodology notes

- **Reproducibility.** Every sweep cell is a pure function of a frozen `CAConfig` + seed. Re-running a config produces bitwise-identical genotypes and fitness histories on both backends (covered by `tests/test_ca_reproducibility.py`).
- **Backend equivalence.** NumPy and MLX kernels are bitwise identical on fixed seeds (`tests/test_ca_engine_parity.py`). Backend choice is a performance knob, not a semantic one.
- **Resumable sweeps.** Output directories are keyed by `CAConfig.hash()`; re-running a sweep skips any hash that already has `result.json`.
- **Secondary metric.** `analyze_sweep.py` reports `solved` (count of seeds reaching fitness 1.0) and `med_gens` (median generation at first 1.0) alongside best-fitness stats. Keeps the easy region (where final fitness saturates) informative.

---

## 1. MVP: does evolution beat random?

**Sweep:** `sweeps/mvp.yaml` — one `CAConfig` × 10 seeds.
**Hypothesis:** With `K=4`, `N=16`, `T=16`, `pop=256`, `gens=200`, on 4-bit parity, median final best-fitness is ≥ 0.65 across seeds (random baseline = 0.5).
**Purpose:** Pipeline validation, not a representation claim. A weak bar — we're checking that mutation / crossover / selection / evaluation all line up correctly, not that the representation is good.

### Status: PASS

Sweep complete. All 10 seeds solve 4-bit parity well above the 0.65 threshold; the task is easy at this size. The pipeline is sound — batched MLX evaluation, tournament selection, byte-array operators, and config-hash output layout all behave as intended. Fitness curves in `output/mvp/fitness_curves.png`.

The MVP gate being easy is informative: it means 4-bit parity at `N=16, K=4` is near the floor of the task's difficulty envelope. The next sweeps push on that envelope deliberately.

---

## 2. Difficulty: where does the task become hard?

**Sweep:** `sweeps/difficulty.yaml` — `n_bits ∈ {4, 6, 8}` × 10 seeds, holding `K=4, N=16, T=16`.
**Hypothesis:** Final best-fitness decreases monotonically with `n_bits`. 4-bit is solvable; 6-bit is partial; 8-bit may be at or near the representation's limit for this grid size.
**Purpose:** Locate the difficulty cliff along one axis, so later sweeps can place their probes around it rather than on either side of a trivial/impossible boundary.

### Status: complete, feeds into sweep 3.

The difficulty axis was folded into the capacity sweep (below) with a richer cross, so its findings are reported there.

---

## 3. Capacity: rule expressiveness vs spatial budget vs task difficulty

**Sweep:** `sweeps/capacity.yaml` — 3 × 3 × 3 × 3 = 81 configs.

- Paired: `(grid_n, steps) ∈ {(8,8), (16,16), (32,32)}` — grid and step count scale together.
- Grid: `n_bits ∈ {4, 6, 8}` × `n_states ∈ {2, 4, 8}` × `seed ∈ {0, 1, 2}`.

**Hypothesis (pre-sweep):** Larger grids and more states both buy capacity. Expectation was a smooth gradient — bigger/wider rules should solve harder parity tasks, with some diminishing return.

**Purpose:** Separate two capacity sources: *rule-table expressiveness* (`K`) from *spatial-temporal budget* (`N`, `T`). If they traded off, we'd see a diagonal; if one dominated, a cliff along one axis.

### Status: 81/81 complete. Clean three-way boundary.

Final best-fitness, median across 3 seeds, pooled over `grid_n ∈ {8, 16, 32}` (grid size barely moves results — see below):

| n_bits \ n_states | 2    | 4    | 8    |
|-------------------|------|------|------|
| **4**             | 0.50 | 1.00 | 1.00 |
| **6**             | 0.50 | 0.89 | 0.88 |
| **8**             | 0.50 | 0.80 | 0.81 |

Three findings, all sharper than the pre-sweep hypothesis predicted:

1. **K=2 is stuck at 0.50 — cause not yet isolated.** For every `n_bits` and every grid size, K=2 runs never depart from random-chance fitness. Flat curves, zero improvement across 150 generations. Two causes are confounded in this sweep and must be separated before the cliff can be called *representational*:
   - The 18-byte rule table may genuinely lack the capacity to express parity via 16-step propagation.
   - At `mutation_rate=0.03` per byte, expected flips/genome scale as `length × rate`: K=2 → 0.54/gen, K=4 → 3.0, K=8 → 13.7. K=2 is simultaneously the smallest rule table *and* the most mutation-starved. A rate sweep at fixed K=2 is the cleanest test (see §4 below).
2. **K=4 is sufficient for parity; K=8 is indistinguishable on this task.** Doubling to K=8 buys nothing measurable (+0.01 on 8-bit, within seed noise). Claim is task-specific — whether K>4 is ever useful is a task-diversity question, not settled by parity alone. Richer output structures (symbolic regression, majority-with-ties) may still benefit from more states.
3. **Grid size is not the bottleneck in the tested range.** `N ∈ {8, 16, 32}` with step counts scaled to match produce similar results at every `K ≥ 4` and every `n_bits`. At N=8 the CA still has room; at N=32 it's not using the extra budget. Whether N>32 unlocks anything — or N<8 breaks things — is untested.

**Reframing:** the two hypothesized capacity sources are not symmetric. Rule expressiveness is a sharp gate (K=2 impossible, K=4 sufficient, K=8 redundant); spatial budget is a near-flat axis in this regime. Any future experiments that vary `N` in isolation should treat it as a secondary axis, not a primary one.

**Difficulty cliff holds across all grids:** 4-bit solved everywhere with K≥4; 6-bit drops to ~0.88 median; 8-bit to ~0.80. The cliff is in the task, not the representation — same shape whether N=8 or N=32.

Plots: `output/capacity/{fitness_curves.png, box_*.png, heatmap_*.png}`. The clearest single figure is `heatmap_n_bits_vs_n_states.png` — the K=2 row is uniformly flat-at-0.5; the K=4 and K=8 columns are indistinguishable; the difficulty gradient runs top-to-bottom.

---

## Next experiments (queued)

The capacity sweep settles the "how much representation do you need" question for parity, but leaves two load-bearing hyperparameter questions open. Order below reflects information-per-unit-cost, not just thematic grouping.

### 4. Mutation rate on K=2 — cliff or artifact?

**Sweep:** `sweeps/mutation_k2.yaml` — `mutation_rate ∈ {0.01, 0.03, 0.1, 0.3, 0.5, 0.8}` × 5 seeds, fixed at `K=2, n_bits=4, N=16, T=16, pop=256, gens=300`.
**Hypothesis:** If the K=2 flat-0.50 result is a mutation-pressure artifact (0.54 expected flips/genome), higher rates (0.3–0.8) should climb above 0.5. If it's a representational limit, all rates stay flat.

### Status: complete. K=2 cliff is representational, not mutation-bound.

All 30 runs finished at exactly 0.500 — stronger than expected:

| mutation_rate | 0.01 | 0.03 | 0.10 | 0.30 | 0.50 | 0.80 |
|---------------|------|------|------|------|------|------|
| median best   | 0.500 | 0.500 | 0.500 | 0.500 | 0.500 | 0.500 |
| min / max     | 0.500 / 0.500 | same | same | same | same | same |

Every seed at every rate is a flat line at 0.5. Even at `mutation_rate=0.8` — effectively resetting the 18-byte genome every generation (~14 flips/gen) — no run ever exceeds 0.5. More telling: the *population mean* fitness is also exactly 0.500 everywhere. **Every individual in every generation of every run is behaviorally identical at the readout cell** — they all produce a constant prediction (8/16 correct on balanced 4-bit parity gives exactly 0.5).

This rules out mutation pressure as an explanation and sharpens the §3 finding: K=2 outer-totalistic rules with the row-0-clamp I/O convention cannot produce a non-constant output at the central readout cell after 16 steps. The 18-entry rule table is genuinely too small to represent a non-trivial input-to-output mapping at this grid/step/readout geometry.

**Residual question for future work:** is the bottleneck rule-table size (2×9=18 entries) or state count (K=2)? A follow-up with K=2 but a larger neighborhood (e.g., 5×5 = 24 neighbors → rule table 2×25=50 entries) would separate these.

### 5. Population size on the 8-bit ceiling

**Sweep:** `sweeps/popsize_8bit.yaml` — `pop_size ∈ {256, 1024, 4096}` × 5 seeds, fixed at `K=4, n_bits=8, N=16, T=16, gens=150`.
**Hypothesis:** 16× more population should push through the 8-bit 0.80 ceiling if the plateau is premature-convergence bound.

### Status: complete. 8-bit ceiling is not search-size bound either.

| pop_size | median best | min   | max   | mean  | solved |
|----------|-------------|-------|-------|-------|--------|
| 256      | 0.812       | 0.719 | 0.906 | 0.819 | 0/5    |
| 1024     | 0.844       | 0.766 | 0.906 | 0.831 | 0/5    |
| 4096     | 0.812       | 0.812 | 0.922 | 0.840 | 0/5    |

Median moves within 0.03 across a 16× population increase; the best seed at pop=4096 (0.922) is only marginally better than the best at pop=256 (0.906). No run at any pop_size reaches fitness 1.0. The upward drift in mean (+0.02) is real but inside seed noise.

Combined with §4, this narrows the diagnosis: the 8-bit parity plateau at K=4 is representational, not search-bound by either mutation or population size. Outer-totalistic K=4 on N=16/T=16 appears to lack the expressive headroom to fully compute 8-bit parity — the same structural story as the K=2 cliff, one layer up.

**Known crash:** pop=4096/seed=4 OOMed on MLX; re-run on NumPy backend (identical semantics). Does not affect the conclusion — the other 4 seeds at pop=4096 are already distributed in the same 0.81–0.92 range as the smaller pops.

Plots: `output/popsize_8bit/box_pop_size.png`, `fitness_curves.png`.

### 6. Task beyond parity — majority

**Sweep:** `sweeps/majority.yaml` — `n_bits ∈ {3, 5, 7}` × `n_states ∈ {2, 4, 8}` × 3 seeds = 27 runs. Fixed `N=16, T=16, pop=256, gens=150`. Odd `n_bits` chosen so strict-majority labels are balanced 50/50 (even `n_bits` with ties→0 gives an imbalanced task, which would break the random=0.5 baseline).
**Hypothesis:** Parity is classically hard for spatial computers — every input bit must be integrated. Majority is classically easy — partial local counts already approximate it. If the K=2 cliff is parity-specific, K=2 should break through on majority; if it survives, K=2 is representationally dead.

### Status: complete. K=2 cliff is task-invariant; parity is specifically hard.

| n_bits \ n_states | 2    | 4    | 8    |
|-------------------|------|------|------|
| **3**             | 0.50 | 1.00 | 1.00 |
| **5**             | 0.50 | 0.94 | 0.94 |
| **7**             | 0.48 | 0.94 | 0.95 |

Two findings:

1. **K=2 cliff generalizes.** Every K=2 run on every n_bits is stuck at 0.50 (the 7-bit K=2 median is 0.484, a single pathological rule doing slightly *worse* than random — still inside the no-signal regime). The K=2 outer-totalistic representation is structurally incapable of expressing non-constant output at the readout cell, regardless of task. This confirms the §3/§4 conclusion was not parity-specific.
2. **Majority is much easier than parity at matched difficulty.** Compare the same table shape across tasks:

   | task     | n_bits=small | n_bits=mid   | n_bits=large |
   |----------|--------------|--------------|--------------|
   | parity   | 1.00 (4-bit) | 0.89 (6-bit) | 0.80 (8-bit) |
   | majority | 1.00 (3-bit) | 0.94 (5-bit) | 0.95 (7-bit) |

   Majority degrades gently with n_bits (plateau ~0.94-0.95); parity degrades steeply (0.80 at 8-bit, below the majority 7-bit score). This matches the classical Mitchell/Crutchfield result that CAs are naturally good at density-class tasks and naturally bad at parity — the CA's local-propagation dynamic integrates well with "how many" but badly with "how many mod 2."

**Taken together (§3, §4, §5, §6):** the ceilings we measured on parity at K=4 are not about the CA being expressively weak in general — majority at the same K=4/N=16 hits 0.94+ on tasks of comparable bit-width. The ceiling is the interaction of *this rule family* with *this task structure*. Parity remains a useful hard task for future rule-family experiments; majority now serves as the "can this at least do something easy" baseline for any new representation variant.

Plots: `output/majority/heatmap_n_bits_vs_n_states.png` is the cleanest companion to the parity heatmap — same row structure, same K=2 cliff, much warmer K≥4 cells.

### 7. Selection regime

**Hypothesis:** Higher tournament sizes will collapse diversity faster on easy tasks but may help on 8-bit parity. Current sweeps use `tournament_size=3, elite_count=2`.
**Why it's lower priority:** tournament size is a second-order knob compared to mutation rate and pop size on these tasks; likely worth visiting only if §4–§5 don't crack the 8-bit ceiling.

### 8. Rule family beyond outer-totalistic — decision tree

**Sweep:** `sweeps/rule_family_compare.yaml` — `rule_family ∈ {outer_totalistic, decision_tree}` × `(task, n_bits) ∈ {(parity, 8), (majority, 7)}` × 5 seeds = 20 runs. Matched budget: `grid_n=16, steps=16, K=4, pop=256, gens=150`, genotype length 100 bytes (OT) vs 94 bytes (DT depth-5).

**Decision-tree family:** fixed-shape complete binary tree of depth 5 over the 3×3 Moore window. Each internal node tests `window[position] == value`; leaves emit next-state. Breaks both rotation and permutation symmetry of the outer-totalistic family. Implementation in `src/folding_evolution/ca/rule_decision_tree.py`; MLX kernel bitwise-identical to NumPy reference (8 parity tests).

**Hypothesis:** if the 8-bit parity 0.80 ceiling was caused by OT's maximally-symmetric rule structure (rotation- and permutation-invariant over neighbors), a less-symmetric rule family should break through. If the ceiling is actually geometric (clamped-row input, central-cell readout) or intrinsic to the CA dynamic, DT should not clearly win.

### Status: complete. DT is *worse* than OT on both tasks.

| task          | rule family       | median | min   | max   | mean  | n |
|---------------|-------------------|--------|-------|-------|-------|---|
| 7-bit majority | outer_totalistic | 0.938  | 0.922 | 0.938 | 0.931 | 5 |
| 7-bit majority | decision_tree    | 0.875  | 0.797 | 0.922 | 0.866 | 5 |
| 8-bit parity   | outer_totalistic | 0.812  | 0.719 | 0.906 | 0.819 | 5 |
| 8-bit parity   | decision_tree    | 0.719  | 0.641 | 0.750 | 0.706 | 5 |

DT is consistently below OT: **-0.06 median on majority, -0.09 median on parity**. Well outside seed noise.

**Interpretation — corrects the working hypothesis.**

The original framing was that OT is "strictly more symmetric" and DT is "strictly more expressive." Both halves are wrong at matched budget:

1. **DT depth-5 is not strictly more expressive than OT K=4.** OT K=4 has 100 entries, each a distinct behavior over the (self, sum) input space. DT with 32 leaves can only express 32 distinguishable behaviors total. They are *incomparable* expressive classes, not nested.
2. **OT's symmetries are inductive biases, not just compression.** Rotation and permutation invariance over neighbors are exactly correct priors for parity and majority — both tasks are symmetric under permutation of input bits. OT encodes that prior for free; DT must *learn* it from byte-level mutations, and evidently cannot within 150 generations.
3. **The mutation landscape degrades under DT.** A byte flip in OT shifts one output value in the table. A byte flip in DT's `pos` bytes qualitatively changes which window position a test consumes — much larger effect. Consistent with the slightly wider best-fitness spread in DT (min 0.641 vs OT min 0.719 on parity).

**What this rules out.** The 8-bit parity 0.80 ceiling is *not* caused by OT's symmetry constraint. A less-symmetric rule family with similar expressive budget does worse, not better. The ceiling must live somewhere other than rule-family symmetry — most likely the **I/O geometry** (row-0 clamp for inputs, single-cell readout for output). That makes §8-b (below) the scientifically next move, not a deeper or less-symmetric rule family.

Plots: `output/rule_family_compare/heatmap_rule_family_vs_task.png` is the clearest single figure — DT is the darker row in both task columns.

### 8-b. I/O geometry — readout variants

**Sweep:** `sweeps/readout_geometry.yaml` — `output_mode ∈ {center_cell, horizontal_3, row_full}` × 10 seeds on 8-bit parity full-space training (`n_examples=256`). `center_cell` reproduces the §9 baseline (one cell at (N-1, N/2)); `horizontal_3` majority-votes bits over 3 cells on the bottom row; `row_full` majority-votes over the full 16-cell bottom row.

**Hypothesis:** if the 0.70 ceiling was a readout-geometry artifact, pooling more cells before voting should reduce noise and lift fitness. If it's the CA dynamic itself that can't compute parity, pooling the same inadequate information over more cells shouldn't help.

### Status: complete. Null result — readout geometry does not matter.

| output_mode  | n  | median | min   | max   | mean  |
|--------------|----|--------|-------|-------|-------|
| center_cell  | 10 | 0.693  | 0.621 | 0.816 | 0.711 |
| horizontal_3 | 10 | 0.693  | 0.637 | 0.820 | 0.703 |
| row_full     | 9  | 0.703  | 0.637 | 0.805 | 0.710 |

Medians and means agree within 0.01 across modes. Max across all modes is ~0.82 — the same seed-lucky ceiling the center-cell baseline produces. Pooling the full bottom row (16 cells majority-voted) gives the same result as reading a single cell.

(One `row_full` run crashed on MLX mid-sweep — `n=9`. Result is already unambiguous; no re-run needed.)

**Interpretation.** The 0.70 ceiling is not a readout-noise or readout-position artifact. Aggregating bit-decisions over 16× as many cells doesn't recover information that the CA state doesn't carry. At N=16 / T=16 under K=4 outer-totalistic, the CA cannot encode the parity bit reliably in any contiguous portion of the bottom row.

### What's now ruled out for the 8-bit parity ceiling

Four independent mechanisms, each tested:
1. Rule-table expressiveness — K=4 equals K=8 everywhere (§3, §10).
2. Search pressure — mutation rate 0.01…0.8 (§4) and pop size 256…4096 (§5) both null.
3. Rule-family symmetry — decision tree at matched budget is *worse* than outer-totalistic (§8).
4. Readout geometry — single cell, 3-cell pool, and full-row majority vote all 0.70 (§8-b above).

The ceiling is a property of the CA dynamic itself. With this input encoding (row-0 clamp, 8 input bits laid out over the row) under this time budget (16 steps), the CA cannot reliably bring 8 bits' worth of parity information to the bottom of a 16×16 grid. Remaining candidates, from cheapest to most radical: more time steps (T); larger grid (N); different input encoding (e.g., unary or spread input); different developmental process (not CA at all).

Plot: `output/readout_geometry/box_output_mode.png` — three near-identical boxplots, visually confirming the null.

---

## 9. Mechanistic error inspection — the 8-bit "ceiling" was an overfitting artifact

**Motivation.** Six sweeps converged on an ~0.80 training-fitness plateau for 8-bit parity under K=4 outer-totalistic. Before running a seventh sweep, reload the best-of-all-runs rule (`popsize_8bit/7ea2b8d7974c`, training fitness 0.922) and evaluate it on the **full 256-input space**, not just its 64 trained examples.

### Finding: the rule overfits hard.

| cut of the input space | accuracy | n correct / n total |
|------------------------|----------|---------------------|
| trained 64 examples    | 0.922    | 59 / 64             |
| holdout 192 examples   | 0.568    | 109 / 192           |
| full 256-input space   | 0.656    | 168 / 256           |

Error rate by bit-count (how many 1s in the input) is far from random:

| bit-count | should output | err rate | notes                           |
|-----------|---------------|----------|---------------------------------|
| 0         | 0             | 0.00     | trivially correct               |
| 1         | 1             | **0.75** | mostly predicts 0               |
| 2         | 0             | 0.07     | well-fit                        |
| 3         | 1             | 0.41     |                                 |
| 4         | 0             | 0.20     |                                 |
| 5         | 1             | 0.52     | worse than random               |
| 6         | 0             | 0.21     |                                 |
| 7         | 1             | **1.00** | predicts 0 for every input      |
| 8         | 0             | 0.00     |                                 |

The rule is biased toward emitting 0, with additional structure that makes it 93% correct at bit-count=2 but 100% wrong at bit-count=7. It has not learned parity — it has learned a local heuristic that happens to match parity on 59 of the 64 specific bit patterns in its training subset.

### What this retrospectively invalidates

The "cliff from 6-bit to 8-bit" reported in §3 was an artifact of holding `n_examples=64` fixed while `2^n_bits` grew:

| n_bits | n_examples | trained-on-full-space? | previous reading                | correct reading                 |
|--------|------------|------------------------|---------------------------------|---------------------------------|
| 4      | 16         | yes (all 16)           | 1.00 = true parity              | **true parity learned**         |
| 6      | 64         | yes (all 64)           | 0.88 median, 0.98 best          | **near-true parity (0.98)**     |
| 8      | 64         | **no** (25% of 256)    | 0.80 median = representation ceiling | **fitness on training subset; generalization ~0.57** |

The 8-bit conclusions from sweeps 3–5 (difficulty, capacity, popsize_8bit) and the §8 OT-vs-DT comparison are all affected: "fitness" meant "training accuracy on 64 examples," and at 8 bits that's a memorization score, not a parity score.

**What remains valid:**
- The K=2 cliff (§3, §4, §6) — K=2 runs were stuck at exactly 0.50 even on tasks where `n_examples` covered the full input space (3-bit majority, 4-bit parity). Representational cliff intact.
- The 6-bit parity and 3-bit/5-bit majority results — those trained on full input spaces already.
- The decision-tree vs outer-totalistic ordering at matched conditions — DT is worse even on 7-bit majority (which at `n_examples=64` covers half the space) and on 6-bit parity-like regimes.

### §9-b. Confirmatory sweep — retrain with full input space

**Sweep:** `sweeps/parity_full_train.yaml` — `(n_bits, n_examples)` paired at `(4, 16), (6, 64), (8, 256)` × 10 seeds. All configs train on every possible input; fitness IS generalization accuracy.

**Hypotheses:**
- If 8-bit climbs near 1.0 (like 6-bit did): the CA can compute 8-bit parity; prior sweeps measured memorization. The "8-bit ceiling" disappears.
- If 8-bit still plateaus near 0.80: there's a real expressive / geometric ceiling around 7–8 input bits for K=4/N=16/T=16. Reinstate §8-b as the next probe.

Either outcome is high-information. Running now.

### Status: complete. Both things are true — ceiling is real, and was previously overestimated.

With full-space training (fitness = true accuracy, memorization impossible):

| n_bits | n_examples | median | min   | max   | mean  | solved | prior (overfit-reading) |
|--------|-----------|--------|-------|-------|-------|--------|-------------------------|
| 4      | 16         | 1.000  | 1.000 | 1.000 | 1.000 | 10/10  | 1.00 (matches)          |
| 6      | 64         | 0.875  | 0.734 | 0.984 | 0.869 | 0/10   | 0.88–0.98 (matches)     |
| 8      | 256        | **0.703** | 0.621 | 0.816 | 0.716 | 0/9    | 0.80 (inflated by ~0.10) |

(One 8-bit run crashed on MLX under the 4× batch size — `n=9` not 10. Re-running on NumPy in the background; it won't move the median meaningfully. Pattern is already unambiguous.)

**Headline:** the CA at K=4, N=16, T=16 genuinely *cannot* compute 8-bit parity — its true full-space accuracy maxes out around 0.82 (best seed), medians at 0.70. The earlier "0.80 ceiling" result overstated the CA's competence by ~10 percentage points, because training on 64 of 256 inputs let evolution discover rules that memorize the training subset while generalizing poorly.

**What survives with only numeric adjustments:**
- 8-bit parity under OT K=4 has a real expressive ceiling — neither mutation rate, pop size, nor rule family fixed it (§4, §5, §8). The ceiling is just ~0.70 full-space, not ~0.80 training.
- The qualitative gap between parity and majority (§6) still holds: 7-bit majority at 64/128 coverage reached ~0.94, suggesting majority at full coverage should do similar or better. Worth running `majority_full_train` for confirmation, but the ordering (parity >> majority difficulty for this CA) does not depend on overfitting.

**What changes interpretation:**
- The rule-family comparison (§8) was run with `n_examples=64` on 8-bit parity — so both DT and OT were measuring overfit training accuracy, not true parity. The *relative* ordering (DT < OT) is preserved because both families had the same opportunity to overfit, but the absolute numbers should not be cited as "parity-solving ability." Re-running under `n_examples=256` would give the clean comparison.

### Recommended next sweep

**`majority_full_train.yaml`** — same structure as this one but for majority: `(n_bits, n_examples) ∈ {(3,8), (5,32), (7,128)}` × seeds. Confirms the majority-vs-parity gap on clean data. Cheap (all input spaces are ≤ 128). If 7-bit majority is still ~0.94 at full training, then the cross-task gap (parity 0.70 vs majority 0.94 at comparable bit-widths) is unambiguous and the paper-worthy claim stands.

---

## 10. Majority under full-space training (clean cross-task comparison)

**Sweep:** `sweeps/majority_full_train.yaml` — paired `(n_bits, n_examples) ∈ {(3,8), (5,32), (7,128)}` × `n_states ∈ {2, 4, 8}` × 10 seeds = 90 runs (89 completed; one 7-bit K=8 run crashed on MLX, pattern unambiguous).

### Status: complete. Paper-worthy cross-task claim now supported on clean data.

**Majority fitness by n_bits × n_states (medians):**

| n_bits \ n_states | 2     | 4     | 8     |
|-------------------|-------|-------|-------|
| 3                 | 0.500 | 1.000 | 1.000 |
| 5                 | 0.500 | 0.938 | 0.938 |
| 7                 | 0.500 | 0.898 | 0.891 |

**Three findings:**

1. **K=2 cliff holds a third time — third independent confirmation on clean data.** Every K=2 run at every tested n_bits stuck at exactly 0.500. Combined with the parity (§3) and mutation-rate (§4) sweeps, the K=2 cliff is now one of the most firmly established results in this module: three sweeps, two tasks, six `n_bits` values, hundreds of runs, *zero* K=2 runs above 0.500.
2. **The majority-vs-parity gap is real and widens with n_bits.** Side-by-side on full-space training:

   | n_bits (parity / majority) | parity median | majority median | gap (maj − par) |
   |----------------------------|---------------|-----------------|-----------------|
   | 4 / 3 (small)              | 1.000         | 1.000           | 0.00            |
   | 6 / 5 (mid)                | 0.875         | 0.938           | +0.06           |
   | 8 / 7 (large)              | 0.703         | 0.898           | **+0.20**       |

   The gap essentially doesn't exist at small n_bits (both tasks trivially solvable), appears at mid (~0.06), and is large at high n_bits (~0.20). Classical Mitchell/Crutchfield prediction: CAs integrate "how many" easily and "how many mod 2" badly, with the gap growing as more bits must be integrated.
3. **The previous half-coverage majority result slightly overstated performance.** 7-bit majority was 0.938 at `n_examples=64` (half the 128-input space); full coverage gives 0.898. A ~0.04 drop, much smaller than parity's ~0.10 drop — majority is both easier *and* more robust to training-subset sampling, consistent with its local-count structure (most input variation is reflected in bit-count, which majority depends on).

Also confirmed on clean data: K=4 and K=8 remain indistinguishable (0.898 vs 0.891 at 7-bit; within seed noise).

### Current consolidated claims (after clean re-evaluation)

1. **K=2 outer-totalistic with row-0-clamp / center-readout geometry cannot express non-constant input-dependent output.** Structural, task-invariant, robust to mutation-rate (§4) and input-coverage (§3, §6, §10).
2. **K=4 is sufficient; K=8 is redundant.** Rule-table expressiveness saturates at K=4 for both parity and majority at all tested n_bits.
3. **Grid size (N ∈ {8, 16, 32}) is not a binding constraint** at K≥4 on either task.
4. **Parity is hard, majority is easy, and the gap widens with n_bits.** Full-space training: parity 0.70 @ 8-bit vs majority 0.90 @ 7-bit. Confirms the task-structure hypothesis — spatial CAs integrate density easily and parity badly.
5. **Breaking CA symmetry (DT vs OT) doesn't help on these tasks.** DT is worse than OT on both under matched budget; OT's symmetries are useful priors for symmetric tasks.

Plots: `output/majority_full_train/heatmap_n_bits_vs_n_states.png` is the cleanest single figure — matches the parity heatmap's K=2 column exactly, but warmer K≥4 cells. Side-by-side with `output/capacity/heatmap_n_bits_vs_n_states.png` (parity) is the paper-worthy figure for this module.

---

## 10-b. CA-dynamic budget scaling (killed early)

**Sweep:** `sweeps/ca_dynamic_budget.yaml` — paired `(grid_n, steps) ∈ {(16,32), (32,32), (32,64)}` × 5 seeds on 8-bit parity full-space. Intended as a brute-force probe of "is the ceiling compute-bound or structure-bound?" by scaling time alone, space + matched time, and both together relative to the (16, 16) baseline.

**Killed at 10/15 runs.** Partial-data signal was already conclusive and this framing was superseded by the §11 plan before the sweep finished.

### Partial result

| (N, T)       | n | median | max   | vs (16,16) baseline 0.703 |
|--------------|---|--------|-------|---------------------------|
| (16, 16) ref | 10 | 0.703 | 0.816 | —                         |
| (16, 32)     | 4 | 0.699 | 0.707 | null                      |
| (32, 32)     | 3 | 0.742 | 0.801 | +0.04 median              |
| (32, 64)     | 3 | 0.680 | 0.715 | null / slightly worse     |

**Three observations, all consistent with §8-b's diagnosis:**

1. **More time alone does nothing.** Doubling `steps` at fixed `grid_n` produces a null. The CA is not time-starved — it is state-starved.
2. **More space + matched time gives a modest, inconsistent lift.** (32, 32) lifts median by +0.04 and max by nothing — the best seed there (0.80) is within the range the baseline already produced. Not a ceiling break.
3. **More time AND space does not compound.** (32, 64) is at or slightly below baseline. If compute budget were the bottleneck the gain would scale with total cells × steps; it does not.

**Interpretation.** Raw CA compute budget is not the missing ingredient. Scaling (N, T) moves the ceiling by at most ~0.04, consistent with having a little more lattice for the same dynamic to spread into rather than unlocking new computational modes. This matches the §8-b reframing: partial structures that could carry parity information are not failing to be *selected* (§5, §8-b) or to be *aggregated* (§8-b readouts), and now also not failing to have *enough spacetime* — they are failing to *exist* in the CA's state dynamics at all, regardless of grid size. Round-2 experiments (§11) target the state-carrying machinery directly.

Plot: `output/ca_dynamic_budget/heatmap_grid_n_vs_steps.png` — visibly flat across the grid with a mild warm spot at (32, 32).

---

## 11. Next experiments (round 2) — constructional expressivity

§3–§10 bound the current rule family's ceiling on 8-bit parity at ~0.70 full-space. Four distinct mechanisms have been ruled out: rule-table expressiveness (§3), search pressure (§4, §5), rule-family symmetry (§8), readout geometry (§8-b). The remaining move is to change *what kind of thing the CA is* — add structure that lets partial solutions persist and combine, or lets information propagate further per step, rather than enlarge the flat rule table. The four sweeps below are ordered by predicted information-per-cost. All use 8-bit parity full-space training (`n_examples=256`) as the primary task; 7-bit majority full-space is cheap to re-run as a cross-task control under each variant.

### 11.a Non-uniform CA — banded rule assignment

**Sweep:** `sweeps/nonuniform_bands.yaml` — `rule_family ∈ {outer_totalistic, banded_ot}` × `(task, n_bits, n_examples) ∈ {(parity, 8, 256), (majority, 7, 128)}` × 10 seeds = 40 runs. Banded: 3 bands at N=16 (rows 0–4, 5–10, 11–15), each with its own K=4 OT rule table. Total banded genotype = 300 bytes; baseline uniform is 100 bytes.

**Hypothesis:** if the 0.70 ceiling is caused by uniform rules forcing every row to play the same role, banding should break it. Sipper's non-uniform result predicts parity becomes tractable once cells can specialize. Expected direction: banded > uniform by ≥ 0.05 on median, or null.

### Status: complete. First ceiling-break in 11 sweeps.

| task           | rule family       | n  | median | min   | max   | mean  |
|----------------|-------------------|----|--------|-------|-------|-------|
| 7-bit majority | outer_totalistic  | 10 | 0.898  | 0.875 | 0.930 | 0.904 |
| 7-bit majority | banded_ot         | 9  | 0.930  | 0.797 | 0.938 | 0.913 |
| **8-bit parity** | outer_totalistic | 10 | 0.693  | 0.621 | 0.816 | 0.711 |
| **8-bit parity** | **banded_ot**     | 10 | **0.805** | 0.637 | **0.969** | **0.794** |

(One 7-bit majority banded_ot run crashed on MLX — n=9; doesn't affect the direction.)

**8-bit parity: Δmedian +0.11, Δmax +0.15, Δmean +0.08.** Best banded run reached **0.969 = 248/256 correct** on the full 256-input space. That's 15 percentage points above anything uniform OT ever produced across six prior sweeps (max 0.816).

**7-bit majority: Δmedian +0.03, Δmax +0.008.** Modest lift on top of an already-high baseline; majority was already close to solved.

**Mechanistic inspection of the best banded parity rule (seed=2, fitness 0.9688):**

| bit-count | n   | correct | err rate |
|-----------|-----|---------|----------|
| 0         | 1   | 1       | 0.000    |
| 1         | 8   | 8       | 0.000    |
| 2         | 28  | 28      | 0.000    |
| 3         | 56  | 56      | 0.000    |
| 4         | 70  | 70      | 0.000    |
| 5         | 56  | 48      | **0.143** |
| 6         | 28  | 28      | 0.000    |
| 7         | 8   | 8       | 0.000    |
| 8         | 1   | 1       | 0.000    |

**All 8 errors concentrate at bit-count=5.** Every other bit count is exactly solved. This is qualitatively different from the uniform OT failure mode (§9), which had bias-by-bit-count spread across multiple odd-weight inputs and a strong bias toward predicting 0. The banded rule is approximately computing true parity, with a single structural failure mode on one residue class. Bit-position asymmetries are also much smaller (max +0.062 vs uniform OT's +0.156 at position 0).

**Interpretation.** Spatial specialization is the first intervention in 11 sweeps that actually works. Rule-table expressiveness (§3), search pressure (§4, §5), rule-family symmetry (§8), readout geometry (§8-b), compute budget (§10-b), and λ-class (§13) all failed to move the ceiling; banding moves it by 0.11 median and nearly solves the task on best seed. The §8-b reframing is vindicated: partial structures carrying parity information needed different rules in different rows to exist at all, not more aggregation or more time.

**Matched-byte control caveat.** Banded (300 bytes) vs uniform K=4 (100 bytes) is not byte-matched. However, the §3 capacity result showed K=4 vs K=8 OT (100 vs 456 bytes) is a null — raw byte count at fixed family doesn't move fitness. That makes "more bytes" a weak alternative explanation here, though not ruled out formally. A future matched-byte control could run banded K=2 (54 bytes) and compare to uniform K=2 (18 bytes) — predicts banded K=2 still stuck at 0.5 if the K=2 cliff is band-invariant.

**Next move per the §11 plan.** The `per_row` ablation is now warranted: extend specialization from 3 bands to 16 rows (16 × 100 = 1600 bytes, K=4) and ask whether the ceiling keeps moving up. If per_row pushes parity accuracy > 0.95 median, spatial specialization is *the* story. If per_row plateaus at 0.80-ish like banded_3, 3 bands is capturing the available structural advantage.

Plot: `output/nonuniform_bands/heatmap_n_bits_vs_rule_family.png`; error map of best run at `nonuniform_bands/8ae27e2c29a7/error_analysis.png`.

### 11.a-b Per-row specialization ablation — over-parameterization

**Sweep:** `sweeps/per_row.yaml` — `rule_family=banded_ot, n_bands=16` (every row gets its own rule table), × `(task, n_bits, n_examples) ∈ {(parity, 8, 256), (majority, 7, 128)}` × 10 seeds = 20 runs (one majority run crashed on MLX; n=9 for that cell). Genotype length = 1600 bytes at K=4.

**Hypothesis (pre-sweep):** if specialization granularity keeps paying off, per_row (16 bands) should push 8-bit parity above banded_3's 0.80 median, possibly past 0.95. If 3 bands was a sweet spot, per_row matches or modestly exceeds banded_3.

### Status: complete. Per_row is *worse* than uniform — sweet spot is not monotone.

Cross-family comparison (8-bit parity full-space, 7-bit majority full-space):

| task           | family       | bytes | n  | median | min   | max   | mean  |
|----------------|--------------|-------|----|--------|-------|-------|-------|
| 8-bit parity   | uniform OT   | 100   | 10 | 0.693  | 0.621 | 0.816 | 0.711 |
| 8-bit parity   | banded_3     | 300   | 10 | **0.805** | 0.637 | **0.969** | **0.794** |
| 8-bit parity   | per_row (16) | 1600  | 10 | 0.641  | 0.621 | 0.656 | 0.639 |
| 7-bit majority | uniform OT   | 100   | 10 | 0.898  | 0.875 | 0.930 | 0.904 |
| 7-bit majority | banded_3     | 300   | 9  | **0.930** | 0.797 | **0.938** | 0.913 |
| 7-bit majority | per_row (16) | 1600  | 9  | 0.797  | 0.789 | 0.852 | 0.817 |

**Per_row is worse than plain uniform OT** on both tasks — counterintuitive but clean: −0.05 median vs uniform on parity, −0.10 on majority. The parity per_row runs cluster tightly at 0.621–0.656 (Δmax−Δmin = 0.035 across 10 seeds) — evolution has essentially no traction.

**Diagnosis — over-parameterization by mutation-rate schedule.** At `mutation_rate=0.03` per byte, expected flips per genome per generation scale linearly with length:

| family       | bytes | expected flips / gen |
|--------------|-------|-----------------------|
| uniform OT   | 100   | 3.0                   |
| banded_3     | 300   | 9.0                   |
| per_row (16) | 1600  | 48.0                  |

Per_row at 48 flips per generation is re-initializing a substantial fraction of the rule table every step. Evolution's effective step size is far too large relative to the fitness landscape's useful features. The narrow 0.621–0.656 band is what you get when search is stuck in the "random with high churn" regime — never consolidating gains, always bouncing around roughly similar-fitness random-ish rules.

**Two implications, both important:**

1. **§11.a's banded_3 win is NOT a "more bytes = better" story.** Per_row has 5× the bytes of banded_3 and does 0.16 worse. Whatever makes banded_3 work is specifically a 3-band structural advantage at a search-space size evolution can still navigate with this mutation schedule. The matched-byte worry from §11.a is partially resolved — more capacity alone hurts, not helps.

2. **Matched-byte controls for §11.b, §11.c, §11.d must normalize mutation rate to genome length.** Otherwise longer genomes are inherently disadvantaged under the current schedule. A clean normalization: hold expected flips per genome fixed (e.g., 3 for everyone) by setting `mutation_rate = 3 / genotype_len`. Flag this upstream in the §11 methodology.

**Follow-up worth flagging.** Per_row at `mutation_rate = 3/1600 ≈ 0.002` would test whether per_row has fundamental expressive *value* once evolvability is fixed. Prediction: it'll land between uniform (100 bytes, 0.69 median) and banded_3 (300 bytes, 0.80 median) — having more capacity than banded_3 but also a much larger search space to navigate in the same 200 generations. But the direction of that comparison is scientifically interesting either way.

Plot: `output/per_row/box_task.png` — per_row parity is a visibly tight cluster just above 0.5 random baseline.

### 11.b Rule schedules — multi-phase CA

**Sweep:** `sweeps/phase_schedule.yaml` — `n_phases ∈ {1, 2, 3}` × 10 seeds on 8-bit parity full-space. Genotype: `n_phases` separate rule tables plus a 16-entry schedule vector assigning each time step to a phase. `n_phases=1` reproduces the current baseline. Matched-byte uniform control as in §11.a.

**Hypothesis:** Lee-Xu-Chau proved parity is exactly solvable by a *sequence* of radius-1 rules even when no single one suffices. If the ceiling is rooted in "one stationary local rule is a very restrictive language," phases should lift it. Expected direction: `n_phases=3` > `n_phases=1` by ≥ 0.05, or null.

**Why second:** strong theoretical grounding, independent of §11.a (results don't overlap). If §11.a already breaks the ceiling, §11.b becomes an ablation rather than the primary bet.

### 11.c Neighborhood radius — information propagation speed

**Sweep:** `sweeps/radius.yaml` — `radius ∈ {1, 2, 3}` × 10 seeds on 8-bit parity full-space. Rule table scales with neighborhood count: r=1 → 3×3 = 9 neighbors (current baseline), r=2 → 5×5 = 25, r=3 → 7×7 = 49. At K=4 outer-totalistic the tables are 36 / 100 / 196 bytes respectively. Matched-byte control for r=1: K=4 with a wider sum range or additional state bit, sized to r=2's 100-byte budget.

**Hypothesis:** Betel-Oliveira-Flocchini (2012) proved radius-2 1D CA cannot solve parity and radius-4 can — a sharp theoretical transition in information propagation. In 2D at N=16 / T=16, the ceiling identified in §8-b is precisely "information does not reach the bottom fast enough." Propagation speed per step equals the radius, so doubling it doubles the causal cone reaching the readout. Expected direction: r=2 > r=1 by ≥ 0.05 on 8-bit parity, with a possible further step at r=3.

**Why third (but arguably first — see sequencing note):** strongest theoretical grounding on the list. Betel/Oliveira/Flocchini is a proof, not an empirical trend. The mechanism (propagation speed) maps most directly onto the §8-b diagnosis that state at the bottom of the grid doesn't carry enough input information. The sweep is placed third rather than first only because the kernel delta is largest (rule-table size scales quadratically with radius) and there is some risk of confounding "more propagation" with "more rule capacity" — hence the matched-byte control.

**Sequencing note:** if §11.a and §11.b both null, escalate §11.c (radius) ahead of §11.d (memory) — radius has a theoretical prediction of effect *direction and location*, memory only predicts direction.

### 11.d Second-order CA — cell memory depth

**Sweep:** `sweeps/memory_depth.yaml` — `memory_depth ∈ {0, 1, 2}` × 10 seeds on 8-bit parity full-space. `memory_depth=0` reproduces the current baseline. `memory_depth=k` extends the rule-table input to `(self, prev_self_1, …, prev_self_k, neighbor_sum) → next_state`, multiplying the table by K^k at K=4 (100, 400, 1600 entries). Matched-byte control at each depth: K=4 no-memory at the same byte budget via extended neighborhood or wider sum range.

**Hypothesis:** Stone & Bull (2009) showed memory improves CA evolvability on density classification. The folding-scaffold analogy predicts memory gives partial information somewhere to persist rather than being rewritten every step. Expected direction: `memory_depth ≥ 1` > 0 by ≥ 0.03, with diminishing or null returns from depth=1 → depth=2 (memory effect likely saturates shallow).

**Why fourth:** smallest predicted effect, and the mechanism is the least clear of the four (see caveat 3 below). If §11.a, §11.b, and §11.c all null out, §11.d becomes the load-bearing test; if any succeeds, §11.d becomes a follow-up ablation. If budget is tight, run only `memory_depth ∈ {0, 1}` first and add depth=2 only if depth=1 is positive.

### Concerns / open caveats for round 2

1. **§8-b reframes the bottleneck upstream of readout.** Pooling 16× more cells on the bottom row gave the same 0.70 as a single cell. Partial structures are not failing to be *selected* — they are failing to *exist* in the CA state at T=16. Round-2 interventions must change state-carrying machinery (propagation, specialization, memory). Further readout-side fitness shaping is not expected to help and is out of scope for this round.
2. **Keep representation changes and fitness shaping separate.** Intermediate-row supervision (auxiliary losses on rows 8, 12, etc.) is a training-signal intervention, not a representation one. Bundling it into §11 would conflate two effects and make diagnosis harder. Defer to a future §12 if round-2 motivates it.
3. **The folding → CA scaffold analogy is suggestive, not mechanistic.** In folding, partial structures persist because the mapping physically preserves them across mutations. In CA, every cell is rewritten each step — memory adds a hidden bit but does not create a persistent lattice of carriers. Non-uniformity (role specialization) is arguably closer in spirit to folding's motif arrangement than memory is. Budget expectations for §11.d accordingly.
4. **Matched-byte controls are mandatory.** Each round-2 sweep adds parameters. Without a byte-matched uniform baseline, any gain could be attributed to "more capacity" rather than "more *constructional* capacity" — the confound §8 (DT vs OT) exposed. Every sweep in this round must publish both absolute fitness and a matched-byte control.
5. **Cross-task control on majority.** 7-bit majority full-space (§10) is cheap to re-run under each new representation. If round-2 lifts parity but not majority, or lifts both equally, that discriminates task-specific bottlenecks from general evolvability gains — informative either way.

---

## 12. Mechanism diagnostic — particles and space-time structure of evolved rules

**Not a sweep — a post-hoc analysis pass over §11 outputs.**

Crutchfield / Mitchell / Das (1998) frame evolved CA computation as *particles* (propagating boundaries between homogeneous domains) and *collisions* (particle interactions that implement logical operations). §11.a–d all propose mechanisms for letting partial structure persist or travel — but none of the sweeps alone verify that a successful variant is actually computing via particle-like carriers, versus some other mechanism that happens to lift fitness.

**Procedure:**
- For the best-of-run genotype from each §11 variant (and the matched-byte control), render full space-time diagrams: `N × T` grid coloured by state, one diagram per input.
- Overlay input-bit identity: mark which output cells are causally downstream of each input bit (precompute via a causal-cone traversal under the evolved rule).
- Identify (manually, then script) candidate particles: thin diagonal or vertical strips of state change that persist across ≥ 3 time steps.
- For rules that solve or nearly solve parity: count collisions on the readout row and check whether the final readout cell's state is consistent with a particle-parity interpretation.

**What the analysis buys:**
- If §11.a (banded) lifts fitness, particle diagrams should show role-stratified dynamics across bands (e.g., the middle band transporting particles from transducer to reducer). If the diagrams look identical to uniform dynamics, the gain came from somewhere else — capacity, not specialization — and the interpretation changes.
- If §11.c (radius) lifts fitness, particle speeds in the diagram should scale with r. A null here would be a red flag even with positive fitness numbers.
- If §11.b (phases) lifts fitness, particle geometry should change at phase boundaries. Absent that, the phase schedule is acting as mere extra capacity, consistent with Lee-Xu-Chau at a more superficial level than their result suggests.

**Caveat.** This is interpretive, not automated fitness — conclusions should be reported as qualitative observations with concrete diagram references, not as numerical metrics. Keep the sweep-level claims separate from the diagnostic claims.

---

## 13. Edge-of-chaos retrospective — Langton's λ on all evolved rules

**Zero-new-compute reanalysis of existing sweep outputs.** Implementation: `experiments/ca/analyze_lambda.py` — walks every `result.json` in `experiments/ca/output/*/`, decodes the best genotype, computes λ (fraction of rule-table entries mapping to non-quiescent state), compares against 10,000 random-rule samples of the same shape.

### Status: complete. Evolved λ is indistinguishable from random λ.

**Coverage:** 374 evolved rules across all 11 completed sweeps, 3 rule families × state counts (OT K=2, OT K=4, OT K=8, DT K=4).

**λ medians per (family, K, task, n_bits):**

| family | K | task | n_bits | n   | evolved λ med | random λ | Δ       |
|--------|---|------|--------|-----|---------------|----------|---------|
| OT     | 2 | parity   | 4 | 39  | 0.500 | 0.499 | +0.001 |
| OT     | 2 | parity   | 6 | 9   | 0.556 | 0.499 | +0.057 |
| OT     | 2 | parity   | 8 | 9   | 0.556 | 0.499 | +0.057 |
| OT     | 2 | majority | 3 | 13  | 0.500 | 0.499 | +0.001 |
| OT     | 2 | majority | 5 | 13  | 0.500 | 0.499 | +0.001 |
| OT     | 2 | majority | 7 | 13  | 0.500 | 0.499 | +0.001 |
| OT     | 4 | parity   | 4 | 39  | 0.760 | 0.749 | +0.011 |
| OT     | 4 | parity   | 6 | 29  | 0.760 | 0.749 | +0.011 |
| OT     | 4 | parity   | 8 | 90  | 0.750 | 0.749 | +0.001 |
| OT     | 4 | majority | 3 | 13  | 0.750 | 0.749 | +0.001 |
| OT     | 4 | majority | 5 | 13  | 0.750 | 0.749 | +0.001 |
| OT     | 4 | majority | 7 | 18  | 0.760 | 0.749 | +0.011 |
| OT     | 8 | parity   | 4 | 9   | 0.884 | 0.874 | +0.010 |
| OT     | 8 | parity   | 6 | 9   | 0.882 | 0.874 | +0.008 |
| OT     | 8 | parity   | 8 | 9   | 0.877 | 0.874 | +0.003 |
| OT     | 8 | majority | 3 | 13  | 0.879 | 0.874 | +0.005 |
| OT     | 8 | majority | 5 | 13  | 0.877 | 0.874 | +0.003 |
| OT     | 8 | majority | 7 | 13  | 0.875 | 0.874 | +0.001 |
| DT     | 4 | parity   | 8 | 5   | 0.781 | 0.748 | +0.033 |
| DT     | 4 | majority | 7 | 5   | 0.750 | 0.748 | +0.002 |

**Main finding: evolution does not move λ.** Across every cell with n ≥ 9, Δ(evolved, random) is ≤ 0.011. The outlier cells (K=2 at 6-bit / 8-bit parity, DT at 8-bit parity) are tiny subsets (n=9, n=9, n=5) with large variance. Across the 334-rule OT-K=4 population overall, evolved λ distribution is **centered exactly on the random-rule distribution**, with no statistical separation.

**Fitness is not predicted by λ.** Within each K band, fitness ranges from 0.5 (K=2 stuck) to 1.0 (solvable cells) at essentially the same λ. The `lambda_all.png` scatter shows each K cluster as a vertical band at its random-rule λ; fitness varies orthogonally to λ. Rules that compute parity/majority sit in the *same* λ regime as random rules that do nothing.

**Interpretation.** Langton's edge-of-chaos hypothesis does not apply to this CA-GP setup as a useful summary statistic:

1. **Evolution finds task-solving rules without tuning λ.** When a task is solvable (K ≥ 4 on small bit-widths), evolution discovers rules with fitness 1.0 at λ indistinguishable from the random distribution. Whatever makes an evolved rule work is much finer-grained than its λ.
2. **K=2 confirms the null gradient.** The K=2 cliff (§3, §4, §6, §10) is consistent with a flat fitness-λ relationship: if λ gradient were the mechanism, K=2 evolution would at least move λ even if it couldn't break 0.5. It doesn't — evolved K=2 λ matches random K=2 λ nearly perfectly. No signal, no search pressure, no movement on any summary statistic.
3. **The bottleneck isn't λ-class.** None of the five already-ruled-out mechanisms for the 8-bit parity ceiling (§3, §4, §5, §8, §8-b, §10-b) are λ-related either. λ is not on the list of candidate causes; the reanalysis merely confirms this explicitly.

**Implication for §11.** Round-2 interventions (non-uniform, rule schedules, radius, memory) can be evaluated without λ as a correlate. The λ readout for §11 rules will be reported in the per-sweep summary but should not be expected to differ from random — the analog of this section's finding. If §11 variants *do* show displaced λ, that would itself be notable.

Plots: `experiments/ca/output/analysis/lambda_all.png` (consolidated), per-sweep `lambda_<sweep>.png`. Raw CSV: `experiments/ca/output/analysis/lambda_summary.csv` (374 rows).

---

## Methodological correction (applies to all future CA sweeps)

The `n_examples` field in CAConfig historically defaulted to 64. For tasks whose input space is ≤ 64 (e.g., 6-bit parity), that trains on the full space. For larger spaces (8-bit parity has 256 inputs) it silently becomes a train/holdout split without a holdout evaluation — allowing memorization to register as fitness.

**Going forward:**
- Prefer `n_examples = 2^n_bits` when feasible (full-space training — fitness = generalization).
- When `n_examples < 2^n_bits` is necessary (e.g., larger n_bits), report both training and held-out accuracy. Add `holdout_fitness` as a secondary metric in CAGenerationStats.
- Re-run any 8-bit (or larger) conclusions from §3–§8 under the new convention before citing them.

---

## What these experiments do not address

- **Comparison against folding** — that is a separate study (see `docs/future-directions.md` Direction 3.1). CA-GP must first stand up on its own.
- **Symbolic regression** — deferred until a second discrete task is in place.
- **Visualization of evolved rules as a sweep concern** — `experiments/ca/inspect_best.py` can reload the best genotype, and §12 specifies a post-hoc particle/space-time analysis pass for §11 variants. Interpretive analysis is out of scope for the sweep layer itself, but is explicitly in scope for §12.
