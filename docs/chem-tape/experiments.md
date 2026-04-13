# Chemistry-Tape GP — Experiments

Ordered by the question each one answers. Every experiment is a YAML sweep under `experiments/chem_tape/sweeps/`; results live under `experiments/chem_tape/output/<sweep>/`.

See [architecture.md](architecture.md) for the v1 specification and the four-stage research ladder.

## The overall question

Does a separator-based decode with a neutral reserve, over a fixed 1D token tape, produce evolutionary dynamics qualitatively better than direct stack-GP — and ultimately competitive with folding-Lisp — on tasks where scaffold completion matters?

The architecture's research ladder gates this into four stages:

- **v1 — Substrate gate.** Does the separator+reserve mechanism help *at all*? Minimum-viable test. This document.
- **v2 — Expressivity parity.** Extended alphabet (quotations, structured records, conditionals). Does chem-tape match folding-Lisp on folding-Lisp's own benchmarks?
- **v3 — Chemistry ablation.** Which mechanisms within folding-style chemistry contribute evolvability, at matched alphabet?
- **v4 — Topology ablation.** 1D vs. 2D at matched chemistry.

v1 is deliberately the cheapest possible gate. Everything downstream earns its compute only if v1 passes.

---

## Methodology notes

- **Reproducibility.** Every sweep cell is a pure function of a frozen `ChemTapeConfig` + seed. Re-running a config produces bitwise-identical genotypes and fitness histories on both backends (covered by `tests/test_chem_tape_reproducibility.py`).
- **Backend equivalence.** NumPy and MLX engines produce bitwise-identical longest-run masks on fixed seeds (`tests/test_chem_tape_engine_parity.py`, 5 seeds × `(B=64, L=32)` random tapes). Backend choice is a performance knob, not a semantic one.
- **Resumable sweeps.** Output directories are keyed by `ChemTapeConfig.hash()`; re-running a sweep skips any hash with `result.json` present.
- **Arm equivalence.** Arm A (direct stack-GP) and Arm B (chem-tape v1) share every code path except Layers 4–5 (bond compute + longest-run decode). On a fully-active tape they produce identical programs (`tests/test_chem_tape_arm_equivalence.py`) — the representational difference is the *only* experimental variable.
- **Generalization guard.** For tasks whose input space exceeds `n_examples`, each run also scores the best genotype on a disjoint 256-example holdout (spec §Layer 10). This catches the overfitting-as-fitness artifact that caught out 8-bit parity in the CA module.

---

## 1. MVP: does the separator-based decode help on a short-scaffold task?

**Sweep:** `sweeps/mvp.yaml` — task=count-R, `arm ∈ {A, B}` × 10 seeds, fixed `L=32, pop=256, gens=200, E=64, mutation_rate=0.03, crossover_rate=0.7`.

**Hypothesis:** Arm B reaches fitness 1.0 at least as often as Arm A *and* within ≤ 2× generations on median (spec §Layer 11 gate).

**Purpose:** Substrate gate. Count-R has a 4-cell natural scaffold (`INPUT CHARS MAP_EQ_R SUM`) — short enough that direct stack-GP can find it by chance. If Arm B loses or only ties here, the chemistry-tape direction is falsified cheaply. If it wins, v2+ earns the right to extend expressivity and test richer chemistry.

### Status: PASS

Results from commit `2028e50`.

| Metric                           | Arm A (direct stack-GP) | Arm B (chem-tape v1) |
|---------------------------------|-------------------------|----------------------|
| Solved (train = 1.0)            | 10 / 10                 | 10 / 10              |
| Holdout fitness (256 unseen)    | 1.000 (all seeds)       | 1.000 (all seeds)    |
| Median gens-to-solve            | 39.5                    | **15.0**             |
| Mean gens-to-solve              | 46.7                    | 25.5                 |
| Range (gens-to-solve)           | 8 – 105                 | 1 – 141              |
| Median wall-clock per run       | ~33 s                   | ~15 s                |

**Gate criteria (§Layer 11):**

- **Solve count:** Arm B (10) ≥ Arm A (10). ✅
- **Speed:** Arm B median (15.0) ≤ 2 × Arm A median (79.0). Chem-tape is in fact **2.6× faster** in generations-to-solve than direct stack-GP — better than the gate requires. ✅
- **Generalization:** Every seed × arm achieves holdout=1.0 on a disjoint 256-example sample; no overfitting artifact. ✅

Three observations beyond the gate:

1. **Speed advantage is robust, but variance widens.** Arm B's distribution is `[1, 2, 10, 12, 15, 15, 15, 22, 22, 141]` — mostly very fast with one outlier. Arm A's distribution is tighter `[8, 12, 26, 30, 36, 43, 49, 68, 90, 105]` but slower throughout. Consistent with "neutral reserve lets the 4-cell motif appear and survive mutations easily, but occasional seeds get stuck in a local basin."
2. **Wall-clock advantage is larger than the generation-count advantage would suggest.** Arm B executes only the longest active run (~5–10 tokens on average); Arm A executes the full 32-token tape. Per-generation cost differs by ~2×, compounding with the ~2.6× generation-count advantage.
3. **The motif chem-tape finds is not always the canonical 4-cell scaffold.** Inspecting `best_genotype_hex` across solved runs, several seeds produce 10–14-cell active runs where the `INPUT CHARS MAP_*_* REDUCE_ADD` pattern is embedded among effectively-dead tokens (ops whose type-mismatched operands coerce to defaults). This is the "neutral reserve within the run" phenomenon — the active region tolerates passenger tokens as long as they don't alter the final top-of-stack.

**What this does NOT establish.** Count-R is the warm-up benchmark; both arms solve it. The real discriminator is sum-gt-10 (§3), whose ~14-cell scaffold is where Arm B's hypothesized advantage should dominate. The v1 gate is "chem-tape doesn't fail on easy problems"; the v1 *finding* awaits §3.

Plots: (to add when sweep-level analysis script lands).

---

## 2. has-upper: does the advantage hold on a second short-scaffold task?

**Sweep:** `sweeps/has_upper.yaml` — task=has_upper, `arm ∈ {A, B}` × 10 seeds, otherwise identical to MVP.

**Hypothesis:** Arm B matches or beats Arm A again. Has-upper also has a 4-cell scaffold (`INPUT CHARS MAP_IS_UPPER ANY`), so the quantitative gap should resemble §1.

**Purpose:** Confirm the count-R result isn't a count-R-specific artifact (e.g. an alphabet quirk) before spending compute on the load-bearing §3 benchmark.

### Status: queued.

---

## 3. sum-gt-10: the load-bearing benchmark

**Sweep:** `sweeps/sum_gt_10.yaml` — task=sum_gt_10, `arm ∈ {A, B}` × 10 seeds, otherwise identical to MVP.

**Hypothesis:** Arm B ≫ Arm A in both solve-count and median speed. The natural scaffold is ~14 cells (the literal 10 must be built from `CONST_1`, `DUP`, `ADD` primitives; minimum is `INPUT SUM C1 DUP ADD DUP ADD DUP ADD C1 ADD GT` or similar). A scaffold this long is where scaffold-preserving neutral reserve should pay off the most.

**Purpose:** The actual v1 research claim. If Arm B ≈ Arm A here, chem-tape's thesis — that neutral reserve helps scaffold completion — is not supported, even though the substrate gate (§1) passed. Conversely, if Arm B strongly beats A here, that's the first real evidence for the chemistry-tape direction and v2 is justified.

**Gate for v2:** Arm B solves strictly more seeds than Arm A and/or achieves a ≥ 3× advantage in median gens-to-solve. A tie or a narrow margin on sum-gt-10 would leave chem-tape as "mildly useful on easy problems" — not enough to justify v2's alphabet expansion.

### Status: queued. This is the next experiment to run.

---

## Next experiments (queued)

### 4. Scaffold-length sweep

**Sweep:** `sweeps/scaffold_length.yaml` — sweep synthetic tasks with known scaffold lengths 4, 8, 12, 16 cells. Measure Arm B's advantage as a function of scaffold length.

**Purpose:** Quantify the relationship between scaffold length and chem-tape's evolvability advantage. A smooth monotone increase would be the cleanest evidence for the mechanism. A threshold or plateau would refine the theory.

### 5. Population × generations tradeoff

**Sweep:** `sweeps/popsize_chem_tape.yaml` — `pop_size ∈ {64, 256, 1024}` × `generations ∈ {100, 400}`.

**Purpose:** Whether Arm B's advantage over Arm A is search-size-dependent or representation-intrinsic. If A catches up at pop=1024, the mechanism is "chem-tape is more sample-efficient" rather than "chem-tape finds solutions A can't." Both are interesting, but different claims.

### 6. Mutation rate

**Sweep:** `sweeps/mutation.yaml` — `mutation_rate ∈ {0.01, 0.03, 0.1, 0.3}` × both arms × 5 seeds on sum-gt-10.

**Purpose:** Test whether the neutral-reserve advantage depends on a mutation regime where the scaffold is fragile. High-rate regimes should hurt Arm A more than Arm B if the mechanism is "inactive cells buffer against drift." Mirrors the CA module's §4 mutation-rate cliff test.

---

## Planned v2 experiments (contingent on §3 passing)

### E. Expressivity parity vs folding-Lisp on structured-record benchmarks

**Representation change:** expand alphabet to ~30 tokens (quotations `[` `]`, typed data-source tokens, field access, conditionals), matching the folding-Lisp benchmark domain. See architecture.md §Expressivity vs folding-Lisp.

**Sweep:** `sweeps/v2_folding_parity.yaml` — matched against folding-Lisp's filter/map/reduce benchmarks.

**Gate:** chem-tape v2 reaches fitness 1.0 on ≥ 70% of folding-Lisp's benchmark ladder at pop=1024, gens=500. Below that, v3 chemistry ablation has no payload to attribute.

### F. Chemistry ablation (v3 kernel)

**Representation change:** at v2 alphabet, introduce folding-style chemistry mechanisms one at a time — single-pass → multi-pass staged → + bond priority → + irreversibility. Five-arm experiment producing a publishable-grade attribution claim about which folding-chemistry property matters for evolvability.

---

See [architecture.md](architecture.md) for the substrate specification, [findings.md](../findings.md) for prior Elixir-era folding results, and [coevolution.md](../coevolution.md) for the coevolution designs that motivated the scaffold-preservation framing.
