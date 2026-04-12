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

### 8-b. I/O geometry (queued, not yet run)

**Next cheap probe:** vary the readout. Candidates:
- Read from multiple cells + vote (reduce readout noise).
- Read at a different position (top-right, bottom-right, opposite side from input).
- Multi-row output band (read full bottom row, majority-vote for the bit).

If any of these breaks the 8-bit parity ceiling under OT, the ceiling was a readout-geometry artifact. If none do, the 8-bit ceiling is fundamentally tied to the CA dynamic at this grid size — a stronger, more negative result about this representation.

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
- **Visualization of evolved rules** — `experiments/ca/inspect_best.py` can reload the best genotype, but interpretive analysis of *what* the winning rule is doing is out of scope for the sweep layer.
