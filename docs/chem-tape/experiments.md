# Chemistry-Tape GP — Experiments

Ordered by the question each one answers. Every experiment is a YAML sweep under `experiments/chem_tape/sweeps/`; results live under `experiments/chem_tape/output/<sweep>/`.

See [architecture.md](architecture.md) for the v1 specification and the four-stage research ladder.

## The overall question

Does a separator-based decode with a neutral reserve, over a fixed 1D token tape, produce evolutionary dynamics qualitatively better than direct stack-GP — and ultimately competitive with folding-Lisp — on tasks where scaffold completion matters?

The architecture's research ladder gates this into four stages:

- **v1 — Substrate gate.** Does the separator+reserve mechanism help *at all*, and on which tasks? Minimum-viable test. This document.
- **v1.5 — Regime-shift test (optional, gated on v1).** Same benchmarks, active task alternates every N generations. Tests for the folding-analog dynamic advantage.
- **v2 — Expressivity parity.** Extended alphabet. Does chem-tape match folding-Lisp on folding-Lisp's own benchmarks?
- **v3 — Chemistry ablation.** Which mechanisms within folding-style chemistry contribute evolvability?
- **v4 — Topology ablation.** 1D vs. 2D at matched chemistry.

**Methodological note (from architecture.md).** The expected positive signal is *differential across tasks*, not uniform. Arm B is predicted to lose on short-scaffold tasks (count-R, has-upper) where the longest-run decode costs cells without compensating benefit, and win on long-scaffold tasks (sum-gt-10, ~14-cell scaffold) where neutral reserve protects partial scaffolds. The "scaffold preservation" mechanism language is deliberately loose enough that v1 data can rename it if needed.

---

## Methodology notes

- **Reproducibility.** Every sweep cell is a pure function of a frozen `ChemTapeConfig` + seed. Re-running a config produces bitwise-identical genotypes and fitness histories on both backends (covered by `tests/test_chem_tape_reproducibility.py`).
- **Backend equivalence.** NumPy and MLX engines produce bitwise-identical longest-run masks on fixed seeds (`tests/test_chem_tape_engine_parity.py`, 5 seeds × `(B=64, L=32)` random tapes). Backend choice is a performance knob, not a semantic one.
- **Resumable sweeps.** Output directories are keyed by `ChemTapeConfig.hash()`; re-running a sweep skips any hash with `result.json` present.
- **Arm equivalence.** Arm A (direct stack-GP) and Arm B (chem-tape v1) share every code path except Layers 4–5 (bond compute + longest-run decode). On a fully-active tape they produce identical programs (`tests/test_chem_tape_arm_equivalence.py`) — the representational difference is the *only* experimental variable.
- **Diagnostics (spec §Layer 11).** Each run records per-generation mean/max/best-individual longest-active-run length alongside fitness. This is intrinsic to the tape distribution (arm-independent), and under the hypothesis it is the mechanism-level quantity expected to differ between the two arms during training.
- **Generalization guard.** For tasks whose input space exceeds `n_examples`, each run scores the best genotype on a disjoint 256-example holdout (spec §Layer 10). Catches the overfitting-as-fitness artifact that caught out 8-bit parity in the CA module.

---

## 1. MVP: three-task differential test

**Sweep:** `sweeps/mvp.yaml` — `task ∈ {count-R, has-upper, sum-gt-10}` × `arm ∈ {A, B}` × 10 seeds = 60 configs, fixed `L=32, pop=256, gens=200, E=64, mutation_rate=0.03, crossover_rate=0.7`.

**Hypothesis (spec §Layer 9 prediction, "predicted pattern" row):**

| count-R | has-upper | sum-gt-10 | interpretation |
|---------|-----------|-----------|----------------|
| B < A | B < A | **B > A** | scaffold-completion pressure localizes the benefit to long scaffolds |

**Acceptance criterion:** Arm B > Arm A on sum-gt-10 (the load-bearing benchmark). count-R and has-upper characterize the mechanism but do not gate it. Rejection requires Arm B ≤ Arm A on all three, or Arm B < Arm A on sum-gt-10 specifically.

### Status: **INCONCLUSIVE**. Gate untestable at this budget.

Results from commit `4409af8` (MVP sweep elapsed 604s / 10 min, 4 workers).

#### Per-task table (median across 10 seeds, 200 gens)

| task        | arm | solved / 10 | median gens-to-solve | holdout fitness (median) | final mean longest-run |
|-------------|-----|-------------|----------------------|--------------------------|------------------------|
| count-R     | A   | **10**      | 39.5                 | 1.000                    | 10.22                  |
| count-R     | B   | **10**      | **15.0**             | 1.000                    | 11.15                  |
| has-upper   | A   | **10**      | **69.0**             | 1.000                    | 10.71                  |
| has-upper   | B   | 7           | 103.0                | 1.000 (0.500 on the 3 unsolved) | 10.73             |
| sum-gt-10   | A   | 0           | —                    | 0.500                    | 11.31                  |
| sum-gt-10   | B   | 0           | —                    | 0.500                    | 10.85                  |

#### Differential pattern observed (vs. spec §Layer 9 prediction)

| task | observed | predicted | match |
|------|----------|-----------|-------|
| count-R | **B > A** (2.6× faster, median 15 vs 39.5 gens) | B < A | ✗ contradicts |
| has-upper | **B < A** (7/10 solved vs 10/10; slower when solved) | B < A | ✓ matches |
| sum-gt-10 | **B ≈ A** (both at baseline 0.500, max best-ever 0.516) | B > A | ✗ untested |

#### Interpretation

**The count-R result contradicts the short-scaffold prediction.** The spec predicted Arm B would lose on count-R because its longest-run decode costs cells without compensating benefit. Instead, Arm B won by a factor of 2.6× in generations-to-solve. The likely mechanism: count-R's **integer-valued labels (0..16)** produce a rich fitness gradient even for near-scaffolds, and Arm B's shorter programs mean less stack clutter to push the final top-of-stack away from the correct count. Arm A's 32-cell programs trail enough junk operations past the scaffold to frequently lose the count at the final pop. This is a fitness-landscape effect, not a scaffold-preservation effect — consistent with the spec's warning that "scaffold preservation" as a mechanism name may need renaming under v1 data.

**The has-upper result partially matches the prediction.** Both arms have a 4-cell natural scaffold (`INPUT CHARS MAP_IS_UPPER ANY`), but has-upper's **binary labels {0, 1}** give rise to a trivial-constant plateau at fitness 0.500: any program that always outputs 0 or always outputs 1 scores 50% on a balanced dataset. Three Arm B seeds (0, 4, 5) never escape this plateau — their longest-run shrinks to a single `CONST_0` or `CONST_1` cell and selection can't disentangle it. Arm A's full-tape execution keeps program outputs more varied, making the plateau easier to escape. **This is the opposite side of the count-R story**: binary labels hurt Arm B when the fitness gradient is discrete, while graded integer labels help Arm B. Scaffold length is not the governing variable — fitness-signal granularity is.

**The sum-gt-10 result is uninformative, not falsifying.** Neither arm exceeds 0.516 best-ever fitness across any of 10 seeds × 200 gens. The ~14-cell scaffold (`INPUT SUM C1 DUP ADD DUP ADD DUP ADD C1 ADD GT`) is outside the search envelope at pop=256, gens=200. This mirrors the CA module's 8-bit parity ceiling (`docs/ca/experiments.md` §5–§6): the representation cannot be evaluated on a task the *combined* budget can't solve in either arm. Technically the gate clause "Arm B ≤ Arm A on sum-gt-10" is satisfied (both equal at baseline), but reading that as a rejection would be a category error — we have no signal either way.

**Final longest-run diagnostic** (population-mean, arm-independent): Both arms converge to mean longest-run ≈ 10–11 cells across all three tasks. The active-run length does not meaningfully diverge between arms — so whatever difference the representations produce is not visible at this coarse diagnostic. The per-arm differences above come from *which* cells make the active run and the program's stack behaviour, not from active-run length alone.

#### What v1 actually shows

1. **Chem-tape is not uniformly better or uniformly worse than direct stack-GP.** The representation's value is task-dependent, and the dependence is more subtle than "scaffold length."
2. **Fitness-signal granularity interacts with representation.** Graded labels (count-R) favour Arm B; binary labels with trivial-constant plateaus (has-upper) favour Arm A. This is a new hypothesis, not in the spec's outcome table.
3. **The load-bearing benchmark (sum-gt-10) is out of reach at the MVP budget.** Expanding search to test the spec's actual gate is the next experiment (§2).
4. **The "scaffold preservation" mechanism language is under-specified** — as the spec anticipated. Different mechanism candidates fit the count-R and has-upper results, and discriminating between them needs §4 (mutation rate) and §5 (scaffold-length sweep).

Plots: (to add — per-task fitness curves, longest-run evolution, holdout gap).

---

## 2. Sum-gt-10 at expanded budget (next experiment)

**Sweep:** `sweeps/sum_gt_10_budget.yaml` (to create) — sum-gt-10 only, `arm ∈ {A, B}` × 10 seeds, `pop_size ∈ {1024, 4096}` × `generations ∈ {500, 1500}`. Four budget points, 80 runs.

**Hypothesis:** At pop=4096, gens=1500 (≈60× the MVP compute for this task), at least one arm breaks the 0.500 plateau. The acceptance-criterion gate from the architecture can then be evaluated.

**Purpose:** Separate "chem-tape doesn't help on sum-gt-10" from "sum-gt-10 isn't solvable at MVP budget." These are very different conclusions and the MVP cannot distinguish them.

**Pre-registered outcomes:**
- If Arm B > Arm A at expanded budget: the spec's gate passes, v2 earns its compute.
- If Arm A > Arm B: the spec's gate rejects, the whole direction is falsified as planned.
- If both still plateau at 0.500 at 4096×1500: the ~14-cell scaffold is out of reach for 14-token alphabets regardless of representation. Falsifies v1 *and* informs v2 (the extra alphabet expressivity is necessary to make the problem tractable at all).

### Status: queued.

---

## 3. Fitness-signal granularity (follow-up)

**Sweep:** `sweeps/granularity.yaml` (to create) — synthetic tasks with matched scaffold length but varied label granularity. E.g., count-R (integer 0..16), has-at-least-1-R (binary {0,1}), count-R-mod-3 (integer 0..2). All with 4-cell natural scaffold.

**Hypothesis:** Arm B's advantage correlates with label granularity, not with scaffold length (new hypothesis suggested by §1). Integer labels → Arm B wins. Binary labels with trivial-constant plateau → Arm A wins.

**Purpose:** Test whether the §1 interpretation holds as a predictor, not just a post-hoc story. If it does, the "scaffold preservation" mechanism name in the architecture should be replaced with something fitness-landscape-shaped.

### Status: queued. Runs only if §2 doesn't render v1 falsified.

---

## 4. Mutation rate sensitivity (queued)

**Sweep:** `sweeps/mutation.yaml` — `mutation_rate ∈ {0.01, 0.03, 0.1, 0.3}` × both arms × 5 seeds on count-R and has-upper.

**Purpose:** Test whether the neutral-reserve story is robust to mutation regime. If Arm B's count-R advantage disappears at low rates (where Arm A's scaffold is also stable), the advantage is mutation-driven, not representation-driven. Mirrors CA module's §4 mutation-rate cliff test.

### Status: queued.

---

## 5. Scaffold-length sweep (queued)

**Sweep:** `sweeps/scaffold_length.yaml` — synthetic tasks with scaffold lengths 4, 6, 8, 10, 12 cells, same label granularity across all.

**Purpose:** Quantify the relationship between scaffold length and Arm B's advantage, controlling for the fitness-granularity confound identified in §1. A monotone trend would recover the original "scaffold preservation" mechanism claim on cleaner data.

### Status: queued.

---

## Planned v2 experiments (contingent on §2 passing)

### E. Expressivity parity vs folding-Lisp on structured-record benchmarks

**Representation change:** expand alphabet to ~30 tokens (quotations `[` `]`, typed data-source tokens, field access, conditionals), matching the folding-Lisp benchmark domain. See architecture.md §Expressivity vs folding-Lisp.

**Gate:** chem-tape v2 reaches fitness 1.0 on ≥ 70% of folding-Lisp's benchmark ladder at pop=1024, gens=500. Below that, v3 chemistry ablation has no payload to attribute.

### F. Chemistry ablation (v3 kernel)

**Representation change:** at v2 alphabet, introduce folding-style chemistry mechanisms one at a time — single-pass → multi-pass staged → + bond priority → + irreversibility. Five-arm experiment producing a publishable-grade attribution claim about which folding-chemistry property matters for evolvability.

---

## Summary of v1 findings

1. **MVP gate: INCONCLUSIVE** at the specified budget. Neither arm solves the load-bearing sum-gt-10 benchmark at pop=256 / gens=200, so the decisive comparison cannot be read.
2. **Arm B ≠ Arm A on short-scaffold tasks, but the difference is task-specific and opposite in sign.** Count-R: Arm B wins 2.6× on generations-to-solve. Has-upper: Arm A wins in solve count and speed. This contradicts the spec's "uniformly B < A on short scaffolds" prediction.
3. **Fitness-signal granularity emerges as a candidate explanatory variable** not present in the original architecture's outcome table. The §3 granularity sweep would test this.
4. **Longest-run-length diagnostic does not differ between arms.** The representation difference must live at the fitness-gradient or program-semantics level, not at active-run length alone.
5. **Next action: §2 budget sweep on sum-gt-10.** Cannot interpret v1 until the load-bearing gate is evaluable.

See [architecture.md](architecture.md) for the substrate specification, [findings.md](../findings.md) for the prior Elixir-era folding results that motivated the "differential outcome" expectation, and [coevolution.md](../coevolution.md) for the coevolution designs that produced the scaffold-preservation framing.
