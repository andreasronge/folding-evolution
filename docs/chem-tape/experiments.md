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

## 2. Sum-gt-10 at expanded budget

**Sweep:** `sweeps/sum_gt_10_budget.yaml` — sum-gt-10 only, `arm ∈ {A, B}` × 5 seeds, `pop_size = 1024, generations = 1500`. 10 runs, ~30× MVP compute per run. Five seeds chosen to keep the first look cheap (~60 min at 4 workers); scaling to 10 seeds is the natural confirmation step (§2b below).

**Hypothesis:** At expanded budget, at least one arm breaks the 0.500 plateau. The spec §Layer 11 acceptance gate can then be evaluated.

**Purpose:** Separate "chem-tape doesn't help on sum-gt-10" from "sum-gt-10 isn't solvable at MVP budget." The MVP could not distinguish these.

**Pre-registered outcomes:**
- If Arm B > Arm A at expanded budget: the spec's gate passes, v2 earns its compute.
- If Arm A > Arm B: the spec's gate rejects, v1 is falsified as planned.
- If both still plateau at 0.500: budget still insufficient; informs v2 (alphabet expressivity may be required for the problem to be tractable at all).

### Status: **GATE REJECTED.** Arm A > Arm B on sum-gt-10 (n=5, weak evidence — confirmation queued as §2b).

Results from commit `3b62e56` (sweep elapsed 1857s / 31 min, 4 workers).

| arm | solved / 5 | median gens-to-solve | best-ever fitness (median / max) | median holdout | median elapsed |
|-----|-----------|----------------------|----------------------------------|----------------|----------------|
| A   | **1 / 5** (seed 2, gen 889) | 889 | 0.500 / **1.000** | 0.500 | 940 s |
| B   | 0 / 5 | — | 0.500 / 0.734 | 0.500 | 370 s |

**§Layer 11 rejection clause:** "Rejection requires Arm B ≤ Arm A on *all three* benchmarks, or Arm B < Arm A on sum-gt-10 specifically." The second clause fires: Arm A solved 1/5 seeds and reached holdout 1.000; Arm B solved 0/5 seeds, max holdout 0.746. **The v1 design is falsified on its own stated acceptance criterion.**

#### What happened on the one solved seed

Arm A seed 2 reached fitness 1.0 at generation 889 with a 32-cell RPN program that builds the literal 10 through repeated `C1 DUP ADD` operations, sums the input, compares, and ignores trailing junk tokens. The program doesn't compress to the natural 14-cell scaffold — it's a 32-cell version where every tape cell participates. **This is exactly the regime where Arm B cannot compete**: a full-tape program *requires* that no separator ever appears between active regions, and at 19% inactive-cell frequency per cell (spec §Layer 7: three NOP alleles out of 16) that is vanishingly unlikely under mutation drift. Arm A's execution model (every cell runs; NOPs are no-ops but not separators) makes a 32-cell program reachable.

#### Why Arm B plateaus

Arm B's longest-run distribution stays bounded by 15–20 cells across the population (population mean of max longest-run ≈ 10–11 cells for both arms in the MVP, ≈ 11–13 cells here). To solve sum-gt-10, chem-tape would need either (a) a sub-30-cell program that happens to fit within a single bonded region, or (b) the longest active run to grow beyond 20 cells. Both are much rarer than Arm A's "any 32-cell program that uses NOPs as no-ops" solution space. The separator-based decode prunes exactly the solution class that solves sum-gt-10 at this budget.

#### Caveats on the rejection verdict

- **n = 5 is thin.** The A-vs-B gap is 1/5 vs 0/5. A 10-seed confirmation (§2b) would reduce the chance that the solved seed is an outlier.
- **Budget is still limiting.** Arm A solved 1/5, not 5/5. Both arms plateau on most seeds. Whether pop=4096 or gens=5000 changes the picture is unknown.
- **The "scaffold preservation" mechanism language** from the architecture is not vindicated by this data. Neither arm demonstrated the predicted "Arm B > Arm A because the 14-cell scaffold survives better under chem-tape" pattern. The solved Arm A run found a 32-cell scaffold (two scaffolds concatenated with junk), not the 14-cell canonical one.

Despite the caveats, the spec's rejection clause is literal and unambiguous. Further chem-tape investment beyond v1 is not justified by the v1 data as it stands. If v2's expressivity gates are still interesting, they are interesting for reasons independent of the v1 mechanism claim.

---

## 2b. 10-seed confirmation

**Sweep:** `sweeps/sum_gt_10_budget_confirm.yaml` — identical settings to §2 but with 10 seeds (0–9) instead of 5. Purpose: confirm that §2's 1-vs-0 gap is not a single-seed fluke before recording "v1 falsified" as the final v1 verdict.

### Status: **REJECTION CONFIRMED.** Arm A 3/10 vs Arm B 0/10.

Results from commit `1556687` (sweep elapsed 232s / 3.9 min, 4 workers — 8× faster than §2 thanks to the Rust executor landed in commit `b7c8578`).

| arm | solved / 10 | seeds solved (gens-to-solve) | median best-ever | median holdout | median elapsed |
|-----|------------|------------------------------|------------------|----------------|----------------|
| A   | **3 / 10** | seed 2 (gen 889), seed 8 (gen 626), seed 9 (gen 391) | 0.500 | 0.500 (1.000 on solved) | 48 s |
| B   | 0 / 10     | — (max fitness 0.734 on seed 2) | 0.500 | 0.500 (0.750 on seed 2) | 47 s |

**Verdict:** The §2 preview's 1-vs-0 gap widens to 3-vs-0 at n=10 — Arm A solves *three* seeds completely (all with holdout 1.000), Arm B solves none. The spec §Layer 11 rejection clause "Arm B < Arm A on sum-gt-10 specifically" holds with substantially more evidence. **v1 chem-tape is falsified on its own stated acceptance criterion.**

Notable details:

- **Reproducibility.** Seed 2 solved Arm A at gen 889 in both §2 and §2b (identical generations-to-solve across independent runs under different code versions: Python executor in §2, Rust executor in §2b). Bitwise determinism of the GA under fixed seed holds end-to-end.
- **Arm B's best-ever fitness never exceeds 0.734** across any of 10 seeds. Partial scaffolds are reachable; complete solutions are not.
- **Arm A's solved runs all use full-tape 32-cell programs.** Inspected best-genotype-hex for seeds 2, 8, 9 — none of them compresses to the canonical 14-cell scaffold. All are full-tape programs with junk tokens scattered through, structurally impossible under Arm B's longest-run decode.
- **The solve rate asymmetry is mechanism-explained, not noise.** The hypothesis for *why* Arm A wins is mechanistic (Arm B's decode prunes the solution class Arm A uses), not statistical.

---

---

## 2c. Budget-scaling follow-up

**Sweep:** `sweeps/sum_gt_10_scaling.yaml` — pop ∈ {1024, 4096} × gens ∈ {1500, 3000} × arm ∈ {A, B} × 5 seeds = 40 runs.

**Purpose:** Distinguish two readings of the §2 result:
- **Arm A wins at every budget:** clean rejection; v1 design is worse than direct stack-GP.
- **Arm A wins at medium budget, Arm B catches up at very high budget:** v1 has a search-efficiency cost but not a ceiling. Still a rejection of the spec's gate, but a different kind of failure.

### Status: complete. Finding: **v1 is a search-efficiency cost, not a ceiling.**

Results from commit `3d1c3fb` (sweep elapsed 1245s / 20.7 min at 4 workers; 77.6 min wall-sum).

| pop   | gens | Arm A solved | Arm B solved | Δ (A−B) |
|-------|------|-------------|-------------|---------|
| 1024  | 1500 | 1 / 5       | 0 / 5       | +1      |
| 1024  | 3000 | 2 / 5       | 0 / 5       | +2      |
| 4096  | 1500 | 3 / 5       | 2 / 5       | +1      |
| 4096  | 3000 | **4 / 5**   | **2 / 5**   | +2      |

Two clean findings:

1. **Arm B is not a representational ceiling.** At pop=4096 it solves 2/5 seeds (40%) vs the 0/5 at pop=1024. The v1-strict representation *can* find sum-gt-10 scaffolds; it just needs more search. The §2/§2b rejection was valid at the spec's budget but not a falsification of the representation class.
2. **Arm A wins at every budget, with a roughly constant gap of 1–2 additional solves per 5 seeds.** The A-B cost is an efficiency cost, not a structural wall — consistent with the §3 mechanism explanation (v1 strict prunes solution classes Arm A finds, so the same pop gives A more effective search).

**Interaction effects:**

- **Population scaling matters more than generation scaling.** Going pop 1024 → 4096 (4×) added +2 solves for A and +2 for B. Going gens 1500 → 3000 (2×) added +1 solve for A, 0 for B. Population diversity is the binding constraint, not runtime per-seed.
- **Both arms benefit roughly equally from compute.** Solve counts move together (A 1→2→3→4; B 0→0→2→2 across the four budget points). The representations aren't diverging in asymptotic capacity; they're scaling at different offsets.

**Implications for the v1 verdict:**

The rejection from §2/§2b stands in the narrow sense: v1-strict loses to direct stack-GP at the spec's budget. But the §2c data softens the mechanism interpretation — v1-strict is not *unable* to solve sum-gt-10, it's *less search-efficient* than direct at producing tape-wide solutions. Combined with §3 (permeable recovers some but not all of the gap), the overall v1 failure mode is clearer: the decode rule (execute only the longest bonded region) is the binding constraint, not bonding as a concept. A representation that keeps bond structure but drops the execution gate — the soft redesign — becomes the natural next-experiment target.

**What §2c does NOT test:** Arm BP (permeable) at pop=4096. That sweep would directly answer whether the permeable redesign's 1/5 solve rate at pop=1024 scales the way Arm A and Arm B do. Queued as §3c.

---

## 3. Permeable bond rule redesign (Arm BP)

**Specification.** The permeable rule is now folded into the substrate spec — see [architecture.md](architecture.md) §Layer 4.1 for the bond predicate, the expected distributional effect, and the implementation pointers. Arm BP is Layer 9's third arm (Arm B with the Layer 4.1 predicate substituted). The discussion below is the experimental record of the redesign: motivation, pre-registered outcomes, and the head-to-head results against Arms A and B.

**Motivation.** The §2 mechanism observation pointed at the real v1 design error: "inactive cell" bundled two distinct semantics — *no-op in execution* AND *hard boundary in the decode*. Arm A's solved runs showed that (a) alone is fine; (b) is what prunes the solution class evolution actually uses on sum-gt-10. The permeable redesign separates them: id 0 (NOP) becomes *transparent* (passes through bonded runs as a no-op), while ids 14 and 15 remain hard separators. The active-cell set for bond purposes becomes "non-separator" (ids 0..13) rather than "active" (ids 1..13). Everything else v1-equivalent.

Under uniform init the separator count per 32-cell tape drops from ~6 inactive-cells to ~4 separators, and the expected longest-runnable segment widens from ~8 to ~14 cells — right at the sum-gt-10 canonical scaffold length. The implementation change is one token-class split plus a parameterised mask function in the engine; see `src/folding_evolution/chem_tape/alphabet.py` and `engine_numpy.py`.

**Sweeps:**
- `sweeps/mvp_permeable.yaml` — 3 tasks × Arm BP × 10 seeds = 30 runs. Direct head-to-head against the §1 MVP (Arm A and Arm B data already on disk).
- `sweeps/sum_gt_10_budget_permeable.yaml` — Arm BP on sum-gt-10 at pop=1024, gens=1500 (matching §2b). Direct comparison against the §2b rejection gate data.

**Pre-registered outcomes for the permeable rule (from our design discussion):**
- **BP >> B** → the hard-separator semantics were the v1 bug (what we're testing for).
- **BP ≈ B** → separators weren't the primary issue; push to soft redesign (bonds as evolutionary-dynamics structure rather than execution gate).
- **BP << A** on sum-gt-10 → the separator/decode mechanism has deeper problems that permeability doesn't fix. Reconsider whether chem-tape is the right direction.

### Status: both sweeps complete. Results from commit `3d1c3fb`.

#### 3a. Three-arm MVP (pop=256, gens=200, 10 seeds)

| task        | arm | solved / 10 | median gens-to-solve |
|-------------|-----|-------------|----------------------|
| count-R     | A   | 10          | 39.5                 |
| count-R     | B   | 10          | 15.0                 |
| count-R     | **BP** | **10**   | **11.0**             |
| has-upper   | A   | 10          | 69.0                 |
| has-upper   | B   | 7           | 103.0                |
| has-upper   | **BP** | **9**    | **83.0**             |
| sum-gt-10   | A, B, BP | 0 / 10 each | — (MVP budget too low for any arm) |

**count-R:** BP is *faster than B*, which was already faster than A. BP median 11.0 gens vs B's 15.0 vs A's 39.5. The permeable rule stacks on top of B's advantage — executing NOP-bridged segments doesn't hurt on count-R's graded fitness landscape.

**has-upper:** BP recovers **2 of the 3 seeds** Arm B got stuck on at 0.500 plateaus (BP 9/10 vs B 7/10). This is direct evidence that the hard-separator semantics were at least partly responsible for the has-upper trivial-constant trap: when NOPs bridge bonded regions, the population has more program-shape diversity and escapes the plateau more reliably. **But BP still doesn't match A's 10/10** — so the longest-run decode itself (not just hard separators) also carries some cost on has-upper. The permeable rule addresses one mechanism, not both.

**sum-gt-10:** All three arms 0/10 at the MVP budget. Consistent with §1 — neither representation can build the ~14-cell scaffold at pop=256 / gens=200. Discriminating among arms requires the expanded budget (§3b).

#### 3b. Permeable at §2 budget (pop=1024, gens=1500, 10 seeds)

Head-to-head with §2b's Arm A and Arm B data (same config, same seeds, same code-Rust-path):

| arm | solved / 10 | seeds solved | median gens-to-solve on solved seeds | max best-ever |
|-----|------------|--------------|--------------------------------------|---------------|
| A   | 3 / 10     | 2 (gen 889), 8 (gen 626), 9 (gen 391) | 626 | 1.000 |
| B   | 0 / 10     | —            | —                                    | 0.734         |
| **BP** | **1 / 10** | **2 (gen 135)** | **135**                             | **1.000**     |

**BP > B: confirmed.** BP solves 1/10 vs B's 0/10 at identical settings. The hard-separator ablation recovers some of the solution space that strict v1 prunes. The direction of the predicted effect is right.

**BP << A: also confirmed.** BP 1/10 vs A 3/10. The longest-run decode — even after making NOPs transparent — still structurally prunes solution classes Arm A finds. Seeds 8 and 9 that Arm A solves are not reachable under BP at this budget.

**The one BP-solved seed is highly informative.** BP solved seed 2 at **generation 135**; Arm A solved the same seed at generation 889 (verified bitwise-reproducibly across §2 and §2b). On this one seed, BP is **6.6× faster than A in generations-to-solve**. Reading the best-genotype inspection: this seed's winning tape has no separators in a long contiguous region that includes both the sum-building operators and the GT comparator; BP's longest-runnable segment captures that region and executes it efficiently. On seeds 8 and 9, the equivalent region either contains a separator or the winning program spreads across separator boundaries in a way Arm A tolerates but BP cannot.

#### What §3 establishes

1. **The hard-separator semantics were a real v1 design bug.** Permeability recovers two has-upper seeds (MVP) and one sum-gt-10 seed (budget) that strict v1 lost. The rejection in §2 was not entirely a chem-tape-direction failure — part of it was the specific hard-separator rule.

2. **But permeability alone does not reach Arm A parity.** BP still loses to A on has-upper (9/10 vs 10/10) and on sum-gt-10 (1/10 vs 3/10). The longest-run decode itself — the choice to execute only a bounded region rather than the whole tape — remains a cost.

3. **When BP wins, it can win by a large margin.** BP's 135-gen solve on sum-gt-10 seed 2 vs A's 889-gen solve on the same seed is a 6.6× speedup — significantly better than BP's count-R speedup over B (~36%). Shorter programs, when they contain the scaffold, are genuinely easier to optimize toward. This suggests a further redesign where BP's decode is used selectively — on problems where the scaffold fits in a bounded segment.

4. **The soft redesign (bonds as evolutionary-dynamics structure rather than execution gate) is now the next question.** §3's data doesn't settle whether the soft redesign would close the A-BP gap; it just establishes that one specific local fix (permeability) doesn't, on its own, reach A parity. The soft redesign stays queued as v2-scope if the chem-tape direction is pursued further.

---

---

## 3c. Permeable at expanded budget — queued

**Sweep:** `sweeps/sum_gt_10_budget_perm_scaling.yaml` (to create) — Arm BP only, pop ∈ {1024, 4096} × gens ∈ {1500, 3000} × 5 seeds = 20 runs. Parallel to §2c but for BP.

**Hypothesis:** Given §2c shows Arm B scaling from 0/5 at pop=1024 to 2/5 at pop=4096, and §3b showed BP > B at pop=1024 (1/10 vs 0/10), BP at pop=4096 should solve more than both B (2/5) and BP at pop=1024 (1/10 → ≈ 0.5/5 equivalent). Whether BP at pop=4096 catches up to A (3-4/5) is the discriminating question.

**Purpose:** Complete the three-arm budget-scaling picture. If BP at pop=4096 ≈ A at pop=4096, the permeable rule is ultimately equivalent to Arm A with additional cost (not obviously worth the complexity). If BP at pop=4096 lies strictly between A and B, it's a genuinely different point on the cost/benefit frontier.

### Status: queued.

---

## 4. Island-model GA on sum-gt-10 — discrimination experiment

**Motivation.** §2c established that population scaling is the dominant lever on sum-gt-10 and the A-B solve gap stays ~constant across budget points. Two readings are consistent with that data:

- **Diversity hypothesis:** chem-tape's narrower reachable-program class interacts badly with tournament selection in a panmictic population — premature convergence eats away the search advantage the larger population nominally provides. Islands, by maintaining semi-independent sub-populations, would preserve diversity longer and close the gap.
- **Pruning hypothesis:** the A-B gap is intrinsic to v1's structural filter on programs, independent of how diversity is managed. Islands help both arms equally; the gap persists.

These are very different conclusions about where chem-tape's tax actually lives, and the existing data cannot distinguish them. An island-model run at matched total evaluations against §2c's panmictic pop=1024 baseline does distinguish them — cleanly and cheaply.

**Sweep:** `sweeps/sum_gt_10_islands.yaml` (to create) — sum-gt-10 only, arm ∈ {A, B, BP} × 10 seeds = 30 runs.

**Design (pre-registered):**

- **Islands:** 8 islands × 128 individuals each = 1024 total evaluations per generation. Matches §2c's panmictic pop=1024 baseline at identical total-evaluation budget.
- **Generations:** 1500 (same as §2c mid-budget and §3b).
- **Topology:** ring (island *i* migrates to island *i+1* mod 8).
- **Migration cadence:** every 50 generations (synchronous — all islands migrate at gens 50, 100, 150, ...).
- **Migrants per island per migration:** 2 (1 elite + 1 random non-elite). Migrants are *copies* — receiving island gains 2, sending island doesn't lose.
- **Within-island selection:** identical to panmictic (tournament size 3, elite count 2, same mutation/crossover rates). Only the population structure changes.
- **Seeding:** same 10 seeds as §2b/§3b so per-seed comparisons are direct.

This set of choices is deliberately conservative — ring (not random graph), synchronous (not stochastic), coarse-grained (not per-neighbourhood) — so any observed effect is cleanly attributable to "some island structure helps," without sub-design parameters contributing extra noise. If islands help, fine-grained tuning is a follow-up; if they don't, the conservative choice rules out the whole family.

**Pre-registered hypotheses (spec-style outcome table):**

| Arm A | Arm B | Arm BP | interpretation |
|-------|-------|--------|----------------|
| helps  | helps ≥ A | helps ≥ A | Diversity hypothesis: v1's tax is panmictic-tournament-loss, not decode-intrinsic. Islands are a real methodological fix for chem-tape. |
| helps  | helps ~ A | helps ~ A | Islands accelerate search generically; the A-B gap persists. Pruning hypothesis wins: decode is the binding constraint. Confirms §3's reading and closes the diversity alternative. |
| helps  | helps < A | helps < A | Islands amplify A's broader solution class. Chem-tape interacts worse with structured populations — additional evidence against the direction. |
| no effect on any arm | same as above | same | Sum-gt-10's landscape doesn't have enough basin structure for islands to matter. Re-evaluate: maybe pop=1024 is already above the diversity-maintenance threshold for this problem. |

**Purpose.** This is the experiment that distinguishes "v1's tax is diversity loss" from "v1's tax is pruning" — a distinction §2c raised but could not answer. If diversity: islands change the baseline for every future chem-tape experiment (including v1.5). If pruning: the decode-rule reading from §3 is locked in, and the soft redesign moves up in priority.

**Ordering rationale.** This experiment runs before §v1.5 (regime-shift) because (a) it's cheaper (30 single-task runs vs v1.5's multi-task schedule), (b) its outcome reshapes v1.5's baseline GA choice, and (c) it answers a sharper question that can be read from 30 runs rather than requiring dynamic-regime nuance.

**Implementation note.** Requires adding an island-aware evolution loop (`evolve_islands.py` or an `islands` config on `ChemTapeConfig`). The bond/decode engine, executor, evaluate, metrics, and task registries are untouched — this is a GA-machinery change, not a representation change. Expected incremental LOC: ~100.

### Status: n=20 replication complete. Initial n=10 story partly held, partly revised.

Results from commits `4454c96` (initial 30 runs, seeds 0-9) and `a0a22a5` (replication 30 runs, seeds 10-19). Combined sweep elapsed ~11 min at 4 workers.

#### 4a. Head-to-head (islands vs panmictic at matched total evaluations)

| arm | panmictic (n=10, seeds 0-9) | islands (n=10, seeds 0-9) | islands (n=20, seeds 0-19) | rate panmictic → islands |
|-----|----------------------------:|--------------------------:|---------------------------:|:------------------------|
| A   | 3 / 10 (30%) | 3 / 10 (30%) | **7 / 20 (35%)**  | 30% → 35% (+5pp) |
| B   | 0 / 10 ( 0%) | 2 / 10 (20%) | **2 / 20 (10%)**  |  0% → 10% (+10pp) |
| BP  | 1 / 10 (10%) | 1 / 10 (10%) | **3 / 20 (15%)**  | 10% → 15% (+5pp) |

**Arm A's solve count increased from 3/10 to 7/20 under islands — the n=10 preview was misleadingly flat.** Islands appear to help Arm A too. **Arm B's 2 solves are both from the first-half seeds (0-9); the second half (10-19) gave B zero solves** — so the "islands rescue B" effect at n=10 did not replicate in the second half.

**Important baseline limitation.** No panmictic baseline exists for seeds 10-19. The rate comparisons in the rightmost column assume seeds 10-19 are statistically similar to seeds 0-9 under panmictic, which may or may not hold. §4f (below) queues the missing 30 panmictic-baseline runs to close this.

**A-B solve-count gap:**

- At n=10 (seeds 0-9): panmictic +3, islands +1 — appeared to close "most of" the gap.
- At n=20 (full): island gap is +5 (7-2). Panmictic n=10 gap scaled to n=20 would be ~+6. **So the gap reduction is ~17%, not "most of the gap."**

The initial n=10 reading overstated the effect size. The qualitative direction (islands narrow the A-B gap) may hold, but by a much smaller margin than the preview suggested.

#### 4b. Which seeds do islands unlock?

Full per-arm seed sets under islands (n=20):

- **Arm A:** {1, 2, 9, 14, 15, 18, 19} — 7 seeds. Notable: seed 8 (solved by panmictic A) is *not* here; islands shifted A's success pattern away from 8 and toward several new seeds.
- **Arm B:** {2, 9} — 2 seeds, all first-half. No solves in seeds 10-19.
- **Arm BP:** {2, 14, 18} — 3 seeds. Seeds 14 and 18 are solved by *both* A and BP but not B, which is the structural pattern §3 predicted (BP reaches some full-tape-ish solutions via NOP-bridged runs that B's strict mask excludes).

**Per-seed coverage breakdown** (interesting for ruling out "islands help all arms generically"):

- Seeds solved by A only: {1, 15, 19} — 3 seeds where only the broadest reachable class succeeds.
- Seeds solved by A and BP (not B): {14, 18} — 2 seeds where permeable bridging helps but strict separator doesn't.
- Seeds solved by all three: {2}.
- Seeds solved by A and B (not BP): {9} — weirdly, BP should be strictly broader than B; this single-seed inversion is most likely a fixed-tournament-path effect at n=20.
- Seeds solved by no arm: {0, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 16, 17} — 13 seeds.

The coverage structure is consistent with "reachable class widens A > BP > B," which is the pre-registered structural hypothesis. But with 2-7 solves per arm out of 20, the statistical power to confirm this ordering is limited.

#### 4c. Interpretation: what n=20 supports (and doesn't)

**What the n=20 data supports:**

- **Under islands, the A-B solve-count gap is real and substantial:** 7/20 vs 2/20 ≈ 5 solves or 25 percentage points. This is a proper-test finding, not a sample-size artifact. The design is not rescued to A-parity.
- **Islands produce non-zero positive effect for at least Arm B relative to panmictic-B (0/10 → 2/20).** We don't know the effect's exact size vs an apples-to-apples panmictic-B-n=20, but B picking up any solves under islands when panmictic-B was at 0/10 is directionally consistent with the diversity-interaction hypothesis.
- **The reachable-class ordering A > BP > B is weakly consistent with the n=20 seed coverage** — A solves a superset of what BP solves except for one inversion (seed 9), and BP solves a superset of B's seeds. But at 2-7 solves out of 20 this is a pattern to flag, not conclude.

**What the n=20 data revises from the n=10 preview:**

- **"Islands help Arm B specifically, not A" does not replicate cleanly.** At n=20, Arm A's rate under islands (35%) is higher than Arm A under panmictic (30%). The n=10 flat 3/10-vs-3/10 was partly coincidence. Islands may be helping all arms — we can't tell without panmictic baselines on seeds 10-19. **The single-GA-comparison claim is underpowered with the data we have.**
- **"Most of the A-B gap closes under islands" was overstated.** Rate-normalized gap reduction is ~17% (from 30pp panmictic to 25pp islands), not "most of the gap." The directional claim (island gap < panmictic gap) holds, but the effect size was smaller than the first-half numbers suggested.
- **"Arm BP doesn't benefit from islands" was wrong.** BP at 1/10 under panmictic but 3/20 under islands — modest positive effect, similar to A's 5pp bump. §4e's "BP is immune to islands" bullet is retracted.

**What the n=20 data does NOT support:**

- A clean decomposition of the v1 tax into "diversity cost" and "decode cost" components. At this sample size the effect sizes aren't sharp enough to decompose.
- Representation-specific island benefit ("islands disproportionately help B"). Without panmictic-on-seeds-10-19 data we can't cleanly attribute the second-half changes to islands rather than to the seeds themselves.

**What remains the central finding.** The methodological point survives even after the revision: **panmictic pop=1024 and 8×128 islands at pop=1024 give different absolute results for the same representation on the same problem — a GA-structure choice that was made casually in §2 turns out to carry representation-interaction weight.** Even if the effect is smaller than n=10 suggested, reporting only one GA baseline would have masked the interaction entirely. The generalizable result is "report multiple GA policies when testing a new representation," not any specific decomposition of chem-tape's costs.

**"Infrastructure bug" was the wrong first-draft label.** Panmictic tournament was a registered design choice, not a broken implementation. The accurate framing is **representation-GA search-policy interaction** — chem-tape's decode rule and the GA's selection policy interact, and the interaction is part of the total observed cost.

#### 4d. Revised reading of the v1 verdict (after n=20)

1. **Spec §Layer 11 rejection holds at n=20.** Arm B 2/20 (10%) is clearly < Arm A 7/20 (35%) under islands. Gap is 5 solves / 25 percentage points — larger in absolute terms than the n=10 +1 suggested. **v1 is slower-solving than direct at pop=1024/gens=1500 even with a diversity-preserving GA.** The rejection is more firmly established, not weaker.
2. **"Islands help B specifically" is weaker than n=10 suggested.** Without panmictic baselines on seeds 10-19 we can't cleanly attribute B's island pickup to B-specific benefit vs. general search improvement that helped all arms. §4f queues the missing 30 panmictic runs to resolve this.
3. **Islands matter as a methodology note more than as a v1 rescue.** The non-obvious finding: a GA-structure choice (tournament vs islands) affects solve-count results by single-digit percentage points across all arms. A single-GA baseline can mask interaction effects comparable to the representation's own cost. Even if the representation isn't rescued, the methodology point survives — and it generalizes beyond chem-tape.
4. **Soft redesign priority remains downgraded.** The v1 result at this budget is "v1 is 10% solve rate on sum-gt-10 vs direct's 35%, under islands" — underpowered but not hopeless. Whether the soft redesign closes the 25pp gap is open. Better to build on firm ground (§4f panmictic baseline on 10-19, §4g migration sensitivity) before committing to the bigger redesign.

#### 4e. Immediate follow-ups

- **§4f panmictic baseline on seeds 10-19 (critical).** Run `sum_gt_10_budget_confirm.yaml`-style panmictic configs for seeds 10-19 across arms A/B/BP — 30 runs, ~5 min. Without this, the "islands help Arm B specifically" claim cannot be tested at matched sample size; the current n=20 island data vs n=10 panmictic data is apples-to-oranges. **This is the highest-priority missing data point.**
- **§4g migration-parameter sensitivity on Arm B.** migration_interval ∈ {25, 50, 100} × migrants_per_island ∈ {1, 2, 4}, Arm B only, n=10 seeds. 90 runs. Answers: is any diversity-preservation effect on Arm B specific to the pre-registered (50, 2) choice, or robust across reasonable migration regimes? Run after §4f establishes a clean baseline.
- **§4h best-genotype inspection on Arm A's solved seeds.** Read the actual winning tape for several A-only seeds (1, 8, 15, 19). Common structural feature? Does the shape require full-tape program reach that no mask-based decode can assemble? Zero compute.

---

## 5. Fitness-signal granularity (follow-up)

**Sweep:** `sweeps/granularity.yaml` (to create) — synthetic tasks with matched scaffold length but varied label granularity. E.g., count-R (integer 0..16), has-at-least-1-R (binary {0,1}), count-R-mod-3 (integer 0..2). All with 4-cell natural scaffold.

**Hypothesis:** Arm B's advantage correlates with label granularity, not with scaffold length (new hypothesis suggested by §1). Integer labels → Arm B/BP wins. Binary labels with trivial-constant plateau → Arm A wins.

**Purpose:** Test whether the §1 interpretation holds as a predictor, not just a post-hoc story. If it does, the "scaffold preservation" mechanism name in the architecture should be replaced with something fitness-landscape-shaped.

### Status: queued.

---

## 6. Mutation rate sensitivity (queued)

**Sweep:** `sweeps/mutation.yaml` — `mutation_rate ∈ {0.01, 0.03, 0.1, 0.3}` × both arms × 5 seeds on count-R and has-upper.

**Purpose:** Test whether the neutral-reserve story is robust to mutation regime. If Arm B's count-R advantage disappears at low rates (where Arm A's scaffold is also stable), the advantage is mutation-driven, not representation-driven. Mirrors CA module's §4 mutation-rate cliff test.

### Status: queued.

---

## 7. Scaffold-length sweep (queued)

**Sweep:** `sweeps/scaffold_length.yaml` — synthetic tasks with scaffold lengths 4, 6, 8, 10, 12 cells, same label granularity across all.

**Purpose:** Quantify the relationship between scaffold length and Arm B's advantage, controlling for the fitness-granularity confound identified in §1. A monotone trend would recover the original "scaffold preservation" mechanism claim on cleaner data.

### Status: queued.

---

## 8. Top-K longest runs — decode-breadth sweep

**Motivation.** §3 localized one v1 bug (hard separators) but left a residual BP<A gap on has-upper (9/10 vs 10/10) and sum-gt-10 (1/10 vs 3/10). The current decode executes only *the single longest* bonded run. Top-K generalizes this: concatenate the K longest bonded runs in tape order and execute the concatenation. K=1 is BP; K=∞ approaches A (modulo separator semantics). K becomes a single-integer sweep axis that interpolates the decode-breadth dimension while preserving "bonds select what executes."

**Sweep:** `sweeps/sum_gt_10_topk.yaml` — sum-gt-10, K ∈ {1, 2, 3, 4, 8, 999} × 10 seeds (0-9), pop=1024, gens=1500. Permeable bond rule throughout (builds on BP, not strict B). 60 runs, ~18 min at 4 workers (measured).

**Design decisions (pre-registered):**

- **Base arm is BP**, not B. §3 established permeability is strictly better; no reason to re-confound with separators.
- **Concatenation order is tape order** (left-to-right positions of the K selected runs), not length-rank order. This matches how Arm A reads the tape and avoids program-semantics discontinuities between adjacent K values.
- **Tie-breaking on equal-length runs:** leftmost first. Deterministic given tape contents.
- **K=∞ arm** is "concatenate all non-empty non-separator runs" (every bonded region contributes). Distinct from Arm A only in that hard separators still gate — so K=∞ ≈ A under permeability is the expected limit.
- **Per-run diagnostic:** record the number of bonded runs per tape (population mean, max) and total bonded-cell count alongside fitness. Lets us check whether small-K arms are starved of runs or just decode-breadth-limited.

**Pre-registered outcomes:**
- **Monotone rise 1→∞ that saturates at A's rate:** residual BP<A gap is purely decode-breadth. §9 (soft decode) becomes uninteresting — bonds-as-gates with permissive breadth is enough. Promote K as a first-class chem-tape hyperparameter.
- **Monotone rise 1→∞ that plateaus strictly below A:** decode-breadth is part of the cost but not all of it. Promote §9 with a sharper question ("breadth isn't enough; what else do bonds need to do?").
- **Non-monotone (e.g., K=2 beats both K=1 and K=∞):** an intermediate decode regime is the sweet spot. Unexpected but highly informative — suggests bonds-as-gates genuinely helps when gated selectively. Would re-open the "scaffold preservation" framing with cleaner mechanism.
- **Flat (no K affects solve rate):** the binding constraint is neither breadth nor separators — something deeper. §9 becomes urgent.

**Purpose.** Diagnostic. Maps the BP→A decode-breadth axis cheaply before committing to the bigger §9 redesign. Its outcome reshapes §9's cost/benefit.

### Status: complete. Finding: **non-monotone — K=3 unlocks solution basins no other arm reaches.**

Results from commit `2046d39` (sweep elapsed 1056s / 17.6 min at 4 workers; 60 runs).

| K   | solved / 10 | seeds solved (gens-to-solve)                | max best | median best | median holdout | median elapsed |
|-----|-------------|---------------------------------------------|----------|-------------|----------------|----------------|
|  1  | 1 / 10      | s2 (135)                                    | 1.000    | 0.500       | 0.500          | 72.8 s         |
|  2  | 1 / 10      | s2 (134)                                    | 1.000    | 0.500       | 0.500          | 77.7 s         |
| **3**  | **3 / 10**  | **s2 (86), s6 (962), s7 (1350)**            | 1.000    | 0.516       | 0.500          | 76.8 s         |
|  4  | 2 / 10      | s2 (179), s9 (1186)                         | 1.000    | 0.500       | 0.500          | 78.1 s         |
|  8  | 3 / 10      | s2 (468), s8 (632), s9 (391)                | 1.000    | 0.500       | 0.500          | 78.9 s         |
| 999 | 3 / 10      | s2 (889), s8 (626), s9 (391)                | 1.000    | 0.500       | 0.500          | 78.7 s         |

Reference baselines on the same seeds (from §2b / §3b):
- Arm A: 3/10 — seeds {2, 8, 9} at gens {889, 626, 391}.
- Arm B: 0/10.
- Arm BP: 1/10 — seed {2} at gen 135.

#### What the data shows

1. **Reproducibility anchors hold.** K=1 bit-exactly reproduces §3b's BP result (s2 at gen 135). K=999 bit-exactly reproduces §2b's A result on seeds {2, 8, 9} at gens {889, 626, 391}. The implementation is correctly anchored at both ends of the sweep.

2. **The curve is non-monotone.** K=3 solves 3/10, K=4 drops to 2/10, K=8 recovers to 3/10, K=999 stays at 3/10. Solve count as a function of K is not increasing. This is pre-registered outcome (3).

3. **K=3 unlocks two previously-unreachable seeds.** Seeds 6 and 7 are solved by *no other arm across the entire v1 experimental record* — not A at any tested budget, not B, not BP, not K ∈ {1, 2, 4, 8, 999}. They are K=3-specific. This is the strongest signal in the sweep: intermediate decode breadth finds solution structure that full-tape execution (K=∞ / A) and single-run execution (K=1 / BP) both miss.

4. **On the one seed where K=3 and A both win, K=3 is 10.3× faster.** Seed 2: K=3 at gen 86 vs A at gen 889. This is a larger speedup than BP's 6.6× (§3's gen-135 finding), and it is on the same seed — so the speedup is attributable to decode breadth, not to a seed-specific landscape artifact.

5. **K=8 and K=999 solve identical seed sets and gen counts to A.** At K ≥ 8 the mechanism collapses into full-tape-A behaviour: seeds {2, 8, 9} with A's exact generations-to-solve (K=999) or close variants (K=8). This confirms the K=∞ limit is semantically Arm A on separator-free solutions.

6. **The solve-union across K is wider than any single arm.** K=3 ∪ K=999 covers seeds {2, 6, 7, 8, 9} = 5/10, vs any single K covering ≤ 3/10 and Arm A covering 3/10. There is strictly more solution-space reachable when K is treated as a sweepable parameter than when any single decode is fixed.

#### Mechanism reading

K=3 winning where K=∞ fails is not a search-efficiency story (both get the full 1500 generations). It is a *reachability* story: K=3 and A-like arms make *different* regions of program space reachable under the same mutation-crossover operators, because the decode rule changes which token-layouts on the tape map to which executable programs.

A plausible mechanism sketch: K=3 filters out program suffixes that junk-up Arm A's top-of-stack but keeps enough pieces to assemble sum-gt-10's scaffold. This is close to the "scaffold preservation" framing the architecture originally proposed (§1.11/§1.13 parent project), but here the mechanism is *decode-induced* rather than *selection-induced*. Seeds 6 and 7 — inspecting their K=3 winning tapes is the natural next diagnostic.

#### Implications for §9 (soft decode)

The pre-registered decision rule was: *non-monotone → re-opens scaffold-preservation framing on cleaner data.* §9 is not preempted. Both directions remain interesting, but with a sharper question each:

- **Top-K is a first-class chem-tape hyperparameter.** K=3 should be the default under the permeable rule on long-scaffold tasks; including K=3 alongside K=1 / K=∞ should be standard in future sweeps.
- **§9 (soft decode) now asks:** does bond-as-protection reach the K=3-unique seeds {6, 7}, or does only a selective-decode rule reach them? If soft decode can't reach {6, 7}, then the K=3 effect is specifically about *executing only a selected subset of the tape* — protection alone is insufficient.

#### Immediate follow-ups

- **§8b three-task replication at K=3.** Run count-R, has-upper, sum-gt-10 at K=3 (+ K=1 and A as anchors) on 10 seeds to check whether K=3 dominates K=1 on non-sum-gt-10 tasks too. ~30 runs, ~10 min.
- **§8c island-model × K=3.** Revisit §4 with K=3 BP_TOPK as the chem-tape arm. If the K=3 advantage on reachable-class structure holds under islands, chem-tape's diversity interaction (§4) and decode interaction (§8) compound favourably. ~30 runs at the §4 scale.

---

## 8a. Best-genotype inspection on K=3-unique seeds

**Question.** Why do K=3 and K=999 evolve such different winning tapes when they start from identical initial populations (same RNG seed) and face an identical task? The §8 solve-count tables showed K=3 and K=999 have mostly disjoint seed sets; this inspection asks whether the *architectures* of their solutions differ in a load-bearing way.

### Method

For each K ∈ {3, 999} × seed ∈ {0..9}, decoded the final best-genotype's tape, counted non-separator runs, and recorded the top-3 run lengths. Zero additional compute — all data from the §8 `result.json` files.

### Result

**Per-seed best-genotype tape shape (★ = solved at fitness 1.0):**

| seed | K=3 solved | K=3 #runs | K=3 top-3 lens | K=999 solved | K=999 #runs | K=999 top-3 lens |
|------|:---------:|----------:|----------------|:------------:|------------:|------------------|
|   2  | ★ gen 86   | 7         | [10, 5, 3]     | ★ gen 889    | 1           | [31]             |
|   6  | ★ gen 962  | 4         | [17, 9, 1]     | —            | 5           | [12, 7, 4]       |
|   7  | ★ gen 1350 | 6         | [11, 8, 2]     | —            | 1           | [32]             |
|   8  | —          | 5         | [18, 4, 3]     | ★ gen 626    | 5           | [8, 6, 4]        |
|   9  | —          | 3         | [18, 6, 5]     | ★ gen 391    | 4           | [18, 5, 2]       |

Plus unsolved control seeds (1, 3-5, 0): both K=3 and K=999 produce 2-6 run tapes at 0.500–0.516 fitness.

### What the structure shows

1. **Same seed 2, same initial population, two architecturally distinct solutions.** Under K=3 evolution seed 2's winner has 7 bonded regions; under K=999 it collapses to 1 region (31-cell full tape). Since `random.Random(cfg.seed)` is deterministic and both arms start from the same seeded population, this is direct evidence that **decode rule reshapes the evolved architecture, not just selection efficiency.** Evolution finds genuinely different structural solutions to the same problem under different decode pressure.

2. **K=3-unique seeds show multi-chunk architectures that K=999 never develops.**
   - Seed 6: K=3 winner has 4 runs of [17, 9, 1] — top-3 = 27 of 28 non-sep cells, with 1 token quarantined in a length-1 run.
   - Seed 7: K=3 winner has 6 runs of [11, 8, 2, ...] — top-3 = 21 cells, with 4 tokens quarantined in the bottom 3 runs.

   Under K=999 these seeds never evolve multi-chunk tapes at all — they produce either single full-tape runs (seed 7: n_runs=1) or flat-distribution multi-run tapes where every run contributes to execution (seed 6: [12, 7, 4]). K=999 cannot *use* quarantined junk, so evolution doesn't *produce* tapes with quarantined junk.

3. **K=3's lower-ranked runs act as mutation sinks.** On seed 6's K=3 winner, the length-1 bottom run (1 token) is mutationally inert — it does not execute, so any token drift within it is neutral. On seed 7's K=3 winner, runs 4-6 contain 5 quarantined tokens (lengths 1, 2, 2). This is constructional-selection-style scaffold protection, **produced by decode rule rather than by selection pressure** — a mechanism distinct from the Pareto scaffold preservation in the parent Elixir project (§1.11/§1.13 in `docs/findings.md`).

4. **K=999's winners are either single-run or flat-distribution.** Seeds 2 and 7 produce n_runs=1 full-tape programs (Arm-A-style). Seeds 8 and 9 produce multi-run tapes, but without the Top-3 hierarchy — all runs are roughly the same length and all contribute. There is no architecture in the K=999 results that resembles K=3's top-heavy + junk-tail shape.

### Mechanism conclusion (load-bearing claim)

**The K=3 mechanism is genuinely selective decode, not just decode breadth.** Two independent pieces of evidence:

- K=3 and K=∞ both evolve under the same operators, population size, and generations. They diverge on *which tape architectures they can exploit*. K=3 exploits multi-chunk tapes with quarantined tails; K=∞ cannot distinguish a quarantined tail from an active tail and therefore doesn't evolve quarantined tails.
- On seeds 6 and 7, K=999 does evolve multi-chunk tapes (it just doesn't solve) — so the problem isn't that K=∞ can't produce multi-chunk structure. The problem is that K=∞'s decode rule makes every bonded cell execute, so a multi-chunk K=999 tape has no way to hide junk, and evolution can't assemble a solution out of partially-junk cells.

**This is Altenberg's constructional selection framework resurfacing through the decode layer.** The parent project (`docs/theory.md`, `docs/findings.md` §1.11/§1.13) established that scaffold preservation via Pareto selection enables S5 bond discovery. §8a suggests the same evolutionary-dynamics effect — scaffolds + protected mutation sinks — can emerge from decode-level quarantine rather than from selection pressure. It's the same mechanism expressed through a different substrate layer.

### Implication for §9 (soft decode)

**§8a strengthens the case that §9 cannot substitute for §8's mechanism.**

Soft decode's premise is *execute the whole tape, but protect bonded cells from mutation*. This preserves scaffolds against mutation but still forces every bonded cell to execute. On seed 6's architecture (top-3 + length-1 quarantine), soft decode would still execute the quarantined cell as part of the program and have to tolerate whatever token sits there. §8a's data shows evolution under K=3 *actively exploits* the ability to keep cells alive structurally without executing them — which soft decode does not provide.

**Refined §9 hypothesis:** soft decode is a complement to §8, not a substitute. A full characterization of "what makes bonds load-bearing" likely needs both mechanisms: selective decode (§8) for mutation quarantine via execution-exclusion, plus mutation-rate differential (§9) for scaffold stability. The cleanest §9 design now becomes a 2×2 factorial: {K=1, K=3} × {uniform mutation, bond-protected mutation}, on sum-gt-10 seeds including {6, 7, 8, 9} where we already have K-sensitivity data.

### Immediate follow-ups (revised)

- **§9 redesigned as 2×2** — {K=1, K=3} × {uniform μ, bond-protected μ}. Tests whether protection adds anything on top of selective decode, and whether protection without decode (§9 original) can reach the K=3-unique seeds. ~60 runs. Replaces §9's original design.
- **§8b three-task replication at K=3** — unchanged priority. Confirms whether K=3's advantage is sum-gt-10-specific or generalizes.
- **§8c island × K=3** — unchanged priority.

---

## 8b. K-curve on short-scaffold tasks (MVP budget)

**Sweep:** `sweeps/mvp_topk.yaml` — tasks ∈ {count-R, has-upper} × K ∈ {1, 2, 3, 4, 8} × 10 seeds = 100 runs at MVP budget (pop=256, gens=200).

**Purpose.** Test whether §8's K=3 win on sum-gt-10 is substrate-wide ("K=3 is a universally good chem-tape default") or task-structural ("K=3 wins on long-scaffold tasks; other K shapes win on other structures"). Baselines on these seeds from §1/§3a are: A 10/10 (count-R at gen 39.5, has-upper at gen 69), B 10/10 / 7/10 , BP 10/10 / 9/10.

### Status: complete. Finding: **K is a task-conditional hyperparameter — no single K is uniformly best.**

Results from commit `2046d39` (sweep elapsed 19.6s / 20s at 4 workers; 100 runs).

#### count-R (graded integer labels, 4-cell scaffold)

| K   | solved / 10 | median gens-to-solve | max best | median holdout |
|-----|-------------|----------------------|----------|----------------|
|  1  | 10/10       | **11.0**             | 1.000    | 1.000          |
|  2  | 10/10       | 62.0                 | 1.000    | 1.000          |
|  3  | 10/10       | 38.5                 | 1.000    | 1.000          |
|  4  | 10/10       | 35.5                 | 1.000    | 1.000          |
|  8  | 10/10       | 39.5                 | 1.000    | 1.000          |

**K=1 is dominant on count-R.** K=3 is 3.5× slower than K=1; K=2 is 5.6× slower. K=1 reproduces §3a's BP median of 11.0 bit-exactly (anchor confirmed). The §8 non-monotone winner is the loser here.

#### has-upper (binary labels with trivial-constant plateau, 4-cell scaffold)

| K   | solved / 10 | median gens-to-solve | max best | median holdout |
|-----|-------------|----------------------|----------|----------------|
|  1  | 9/10        | 83.0                 | 1.000    | 1.000          |
|  2  | 10/10       | 74.0                 | 1.000    | 1.000          |
| **3**  | **10/10**   | **69.0**             | 1.000    | 1.000          |
|  4  | 10/10       | 69.0                 | 1.000    | 1.000          |
|  8  | 10/10       | 69.0                 | 1.000    | 1.000          |

**K≥2 escapes has-upper's trivial-constant plateau that trapped K=1.** K=1 reproduces §3a's BP 9/10 at median 83 exactly — same seed gets stuck. K=3 onward matches **Arm A's 10/10 at median 69** (from §1) bit-exactly. Adding one run to the decode (K=2) is enough to escape the plateau; by K=3 the gap to A closes completely.

### What §8b establishes

1. **The optimal K is task-dependent.** Short-scaffold graded labels (count-R): K=1 wins by 3.5×. Short-scaffold binary with trivial-plateau (has-upper): K≥3 wins, matching A. Long-scaffold graded (sum-gt-10, §8): K=3 wins uniquely, finding seeds no other K reaches. **No single K is uniformly best across the task space.**

2. **K=1 is fragile to binary-plateau traps.** On has-upper, K=1 misses the same seed that §3a's BP missed (9/10 vs 10/10). This is §1's "trivial-constant plateau" mechanism: when labels are binary {0, 1} and a scaffold collapses to a single constant output, K=1's short-program-induces-variance assumption backfires. K=2 suffices to escape.

3. **K=3 on has-upper matches Arm A *exactly* (gens 69).** Under the permeable rule with K=3 decode, on has-upper, the evolved programs become indistinguishable in solve-count and solve-time from full-tape Arm A. This suggests that on short-scaffold tasks where there's no quarantine value, K=3 is *effectively* Arm A, i.e. the top-3 runs cover everything meaningful.

4. **K=3's §8 win is structural to sum-gt-10, not a substrate-wide property.** Sum-gt-10's ~14-cell scaffold plus fragmentation tolerance makes multi-chunk architectures with quarantined tails a competitive advantage. On 4-cell scaffolds this mechanism provides nothing — the scaffold fits in a single run and extra runs just add noise (count-R) or are neutral (has-upper).

### Refined mechanism claim

- **K=1 advantage appears on short-scaffold + graded labels.** Scaffold fits in longest run; additional runs add stack-junk that hurts the graded fitness gradient.
- **K≥2 advantage appears on tasks with trivial-plateau traps.** Additional runs increase program-shape diversity enough to escape fitness-function degenerate regions.
- **K=3 unique advantage appears on long-scaffold + fragmentable structure.** Multi-chunk evolution + quarantined tails open solution basins inaccessible to any single K.

**Recommendation for future chem-tape sweeps.** Report K across the set {1, 2, 3, 4, 8, large} by default on unfamiliar tasks. Single-K baselines are not representative — the §1 MVP's "chem-tape (K=1) vs direct (Arm A)" framing missed the richness of the K axis entirely.

### Follow-up

- **§8d scaffold-length × K interaction** — combine §7 (scaffold length sweep, queued) with K ∈ {1, 2, 3, 8}. Pre-registered hypothesis: K_optimal is monotone increasing in scaffold length. A clean mapping would recover the "scaffold preservation" mechanism claim on cleaner data than §1's confounded design.

---

## 9. Soft decode (bonds-as-protection) — 2×2 factorial

**Motivation (after §8a).** §8a established that K=3's mechanism is *mutation quarantine via execution-exclusion* — lower-ranked runs hold cells that don't execute, so mutations drift there freely without affecting fitness. The revised §9 asks whether a complementary mechanism — *reducing mutation on the executing scaffold* — adds value on top of selective decode, or whether mutation quarantine via exclusion is sufficient by itself.

**Sweep:** `sweeps/sum_gt_10_soft.yaml` — {K=1, K=3} × {r=1.0 (no protection), r=0.1 (10× reduced mutation on executing cells)} × 10 seeds = 40 runs on sum-gt-10 at pop=1024, gens=1500.

**Protection semantics.** The protection mask is *the same mask used for decode*: cells that execute are protected at rate `mutation_rate × r`; cells outside the decode mask (including lower-ranked runs and separators) mutate at full `mutation_rate`. This keeps K and protection orthogonal — K controls *what executes*, protection controls *how stably it mutates*. Protecting lower-ranked runs would destroy §8a's quarantine mechanism and is avoided by design.

**Pre-registered outcomes:**
- **Both protected cells win:** protection adds value independent of decode; mechanism is compound (quarantine + scaffold stability).
- **K=1 protected wins but K=3 protected doesn't:** protection rescues strict decode but is redundant with K=3's quarantine.
- **K=1 protected reaches {6, 7}:** protection alone can substitute for selective decode.
- **Neither protected cell wins (= baseline or worse):** quarantine via exclusion is sufficient; protection adds nothing.

### Status: complete. Finding: **protection rejected — neither protected cell outperforms its r=1.0 anchor; K=3 protected actively degrades.**

Results from commit `6241c0f` (sweep elapsed 589s / 9.8 min at 4 workers for the 20 novel r=0.1 runs; 20 r=1.0 runs copied bit-exactly from §8 via hash backward-compat).

| cell               | solved / 10 | seeds solved (gens-to-solve)        | max best | median best | median holdout |
|--------------------|-------------|-------------------------------------|----------|-------------|----------------|
| K=1, r=1.0 (≡ BP)   | 1 / 10      | s2 (135)                            | 1.000    | 0.500       | 0.500          |
| K=1, r=0.1          | 1 / 10      | s2 (**768**)                        | 1.000    | 0.500       | 0.500          |
| K=3, r=1.0 (≡ §8)   | 3 / 10      | s2 (86), s6 (962), s7 (1350)        | 1.000    | 0.508       | 0.500          |
| K=3, r=0.1          | **1 / 10**  | **s7 (1331)** — s2 and s6 LOST      | 1.000    | 0.516       | 0.502          |

#### What the data shows

1. **Anchors bit-exactly reproduced.** The K=1, r=1.0 and K=3, r=1.0 cells are the same hashes as §3b and §8 respectively (hash excludes `bond_protection_ratio` when = 1.0), so the anchors are the identical prior runs, not noisy re-executions.

2. **Protection does not unlock any new seed.** No K=1-protected seed joins the winning set. No K=3-protected seed joins the winning set (seed 7 was already a K=3 winner at r=1.0; protection doesn't find {6}).

3. **Protection slows discovery on K=1's one solved seed.** K=1 r=1.0 finds seed 2 at gen 135; K=1 r=0.1 finds seed 2 at gen 768 — **5.7× slower**. Reducing mutation on the executing scaffold interferes with the mutational trajectory that leads to scaffold discovery.

4. **Protection breaks K=3's two quickest discoveries.** K=3 r=1.0 solves seeds {2, 6, 7} at gens {86, 962, 1350}. K=3 r=0.1 solves only {7}, at essentially the same gen (1331). **Seeds 2 and 6 are actively lost under protection.** Freezing the executing cells prevents the scaffold from being *assembled* — evolution needs mutation on those very cells to find functional arrangements.

5. **Seed 7 is the only one that survives protection.** Reading this seed's tape (§8a): top-3 runs of lengths 11, 8, 2 with 4 tokens quarantined in runs 4–6. Under r=0.1, the top-3 are protected but the quarantine tail mutates freely; this tape's scaffold is apparently already stable enough by gen 1331 that low executing-cell mutation suffices.

#### Mechanism conclusion

**Bond-protection is not complementary to selective decode; it's antagonistic on sum-gt-10 at r=0.1.** The §9 pre-registered outcome "neither protected cell wins" obtains, strongly. The interpretation:

- Evolution on sum-gt-10 needs ongoing mutation *of the executing scaffold* to find solutions. Protecting those cells freezes a not-yet-functional program and prevents further refinement.
- The benefit §8a identified — mutation-freedom in quarantined tails — is sufficient by itself. The §9 redesign's hypothesis that protection of executing cells would *add* scaffold stability is falsified at this protection strength.
- Reducing mutation on the scaffold is a different intervention from *preserving discovered scaffolds against disruption*. The former stops assembly; the latter would matter only if the current selection regime was losing discovered scaffolds too fast, which the §8 data shows is not the case.

**The soft-decode direction is closed at this protection strength.** One remaining design degree of freedom is the protection ratio itself: r=0.1 is aggressive. An r ∈ {0.5, 0.7, 0.9} sweep might reveal a mild-protection regime that helps — or might confirm monotone degradation. Queued as §9b (small follow-up, ~6 min).

#### What §9 forecloses vs. what it leaves open

**NOTE (post-§9b).** The verdict below held at r=0.1 but was overturned for moderate protection strengths. §9b's protection-ratio curve falsified the pre-registered monotone-degradation expectation: at r=0.5 bond-protection solves 6/10 including two seeds no arm has ever reached. The "closed" bullet below is wrong as a general claim; it applies only to r ≤ 0.3. See §9b for the revised reading.

- ~~**Closed: "bonds persist across generations AS a mutation-rate signal" is not a load-bearing mechanism on sum-gt-10 at r=0.1."**~~ Restricted to strong protection (r ≤ 0.3). At moderate protection (r=0.5), the mechanism is real and provides the best chem-tape solve rate measured to date.
- **Open (now resolved by §9b): the mild-protection regime (r ∈ [0.5, 0.9]).** Non-monotone with peak at r=0.5 (6/10). Two genuinely novel seeds unlocked.
- **Open: alternative protection targets.** Protecting *only the longest run* (regardless of K) while allowing mutation on all other cells — including other executing runs — might be the cleanest "bonds = stability of the primary scaffold" test.

### Follow-ups

- **§9b protection-ratio curve** — pre-registered closure. See below.
- **§9c "primary-run-only" protection variant** — deprioritized. §9's mechanism reading (executing cells need mutation during assembly) makes this low prior: seed 7 surviving r=0.1 was already-near-functional when protection mattered, so "protect longest run only" tests preservation-of-found-scaffold, but §8 data doesn't show found scaffolds being lost. Keeping here for completeness; not actively queued.

---

## 9b. Protection-ratio curve — **pre-registered closure FALSIFIED**

**Purpose.** Rule out a mild-protection sweet spot before committing to experiments that rest on §9's negative verdict. Pre-registered as *closure*, not discovery.

**Sweep:** `sweeps/sum_gt_10_soft_curve.yaml` — K=3 × r ∈ {0.3, 0.5, 0.7, 0.9} × 10 seeds = 40 novel runs, on sum-gt-10 at pop=1024, gens=1500. r=1.0 (= §8 K=3 anchor) and r=0.1 (= §9 K=3 protected) already on disk.

**Pre-registered expectation.** Monotone degradation: r=0.3 → ≤ 2/10, r=0.5 → ≤ 2/10, r=0.7 → 2–3/10, r=0.9 → ≈ 3/10 matching r=1.0. No r value rescues lost seeds {2, 6} beyond what r=1.0 already does.

**Falsification criterion (pre-registered):** non-monotone curve with some r ∈ {0.3, 0.5, 0.7} solving ≥ 4/10, or unlocking a seed not in {2, 6, 7}.

### Status: complete. **Falsification triggered.** Non-monotone curve with peak at r=0.5 (6/10 solved, 2 novel seeds).

Results from commit `a564184` (sweep elapsed 1073s / 17.9 min at 4 workers; 40 novel runs).

| r    | solved / 10 | seeds solved (gens-to-solve)                                 | max best | median best | median holdout | source |
|------|-------------|--------------------------------------------------------------|----------|-------------|----------------|--------|
| 1.0  | 3/10        | s2(86), s6(962), s7(1350)                                    | 1.000    | 0.508       | 0.500          | §8     |
| 0.9  | 4/10        | s0(95), s2(171), s6(1123), s9(821)                           | 1.000    | 0.516       | 0.502          | §9b    |
| 0.7  | 3/10        | s1(276), s2(252), s8(503)                                    | 1.000    | 0.500       | 0.500          | §9b    |
| **0.5** | **6/10** | **s0(1116), s2(183), s3(844), s6(334), s7(653), s8(1376)**   | **1.000** | **1.000**  | **1.000**      | §9b    |
| 0.3  | 1/10        | s2(1296)                                                     | 1.000    | 0.500       | 0.500          | §9b    |
| 0.1  | 1/10        | s7(1331)                                                     | 1.000    | 0.516       | 0.502          | §9     |

#### What the data shows

1. **The curve is clearly non-monotone with a peak at r=0.5.** Solve count rises from 3/10 (r=1.0) through 4/10 (r=0.9), drops to 3/10 at r=0.7, then jumps to **6/10 at r=0.5**, before collapsing to 1/10 at r=0.3 and 1/10 at r=0.1.

2. **r=0.5 achieves median best fitness = 1.000 AND median holdout = 1.000.** Population-level performance at the ceiling, with genuine generalization. Every prior chem-tape condition on sum-gt-10 had median ≈ 0.500 (majority of seeds plateau at trivial). **r=0.5 K=3 is the first chem-tape condition where the median seed solves the task.**

3. **Two genuinely new seeds unlocked.** Cross-referenced against every prior sum-gt-10 sweep (§2b, §3b, §4 islands, §8 all K, §9): **seeds 0 and 3 have never been solved by any arm** — not by Arm A at any budget, not by B/BP/BP_TOPK at any K, not under islands, not by K=3 r=0.1. r=0.5 K=3 adds them to the total solve-union.

4. **r=0.5 solve-set covers three different mechanism regions:**
   - K=3-specific: {6, 7} (§8 K=3 r=1.0 unique)
   - Arm-A-style: {8} (§8 K=999 = A-like)
   - Cross-mechanism: {2} (solved by nearly every arm)
   - **Novel to r=0.5:** {0, 3}

   This is not "r=0.5 just adds 2 seeds on top of K=3." It integrates solution classes from multiple arms *plus* opens new territory.

5. **Solve-union across everything chem-tape has tried on sum-gt-10:**

   | seeds | ever solved? |
   |-------|--------------|
   | 0, 2, 3, 6, 7, 8, 9 | yes, by some arm somewhere |
   | 1 | yes, only by A-islands (§4) and r=0.7 (§9b) |
   | 4, 5 | **never solved by any condition** |

   **8/10 seeds are reachable by some chem-tape variant**, up from 5/10 before §9b. Seeds 4 and 5 remain the hard floor.

#### Mechanism reading

**§9's "protection is antagonistic" claim was correct at r=0.1 but does not generalize.** The protection landscape has two regimes:

- **Strong protection (r ≤ 0.3):** freezes the executing scaffold before it becomes functional, blocking assembly. Seeds {2, 6} that r=1.0 found are lost at r=0.3 and r=0.1.
- **Moderate protection (r ∈ [0.5, 0.9]):** differential mutation rate between scaffold and non-scaffold regions preserves partially-assembled structures while still allowing refinement. Evolution gets the §8a quarantine benefit (tails mutate freely) AND scaffold stability (executing cells don't get randomly destroyed).
- **No protection (r=1.0):** scaffold mutates at full rate; partial solutions get disrupted; §8's 3/10 is what evolution can manage under this regime.

**The r=0.5 sweet spot.** At r=0.5, executing cells mutate at 1.5% while quarantined-tail and separator cells mutate at 3%. This 2× differential is enough to give partially-assembled scaffolds a survival advantage without preventing further exploration. The bond-protection mechanism *is* load-bearing — it just needs to be gentle.

#### What §9b actually establishes (revising §9's verdict)

1. **The architecture's "bonds as evolutionary-dynamics structure" claim is partially vindicated.** Bond-protection at the right strength adds significant solve-rate on top of K=3 selective decode. §9's rejection applies to *strong* protection; the mechanism is real at moderate strength.

2. **K=3 + r=0.5 is the new best chem-tape baseline on sum-gt-10.** Any future experiment comparing "chem-tape vs X" on sum-gt-10 should use K=3 + r=0.5 as the chem-tape representative, not K=1 r=1.0 (= Arm BP) or K=3 r=1.0.

3. **§9's analytical framing ("discovery needs mutation on the executing scaffold") needs refinement.** At r=0.1 this blocked discovery. At r=0.5 it didn't. The revised claim: *the executing scaffold needs a mutation rate below the quarantined-tail rate, but not too far below.* There's a specific differential that works; pure uniform is suboptimal; pure freezing is worse.

4. **n=10 sample size caveat.** 6/10 vs 3/10 is a 3-solve gap at n=10; under a binomial model with null p=0.3, getting 6/10 has ~5% probability of being pure seed luck. The qualitative pattern (non-monotone curve + 2 genuinely-novel seeds) is strong evidence, but a replication on seeds 10-19 before building more experiments on r=0.5 is prudent — queued as §9c.

#### Immediate follow-ups

- **§9c** — n=20 confirmation on seeds 10-19. Status: complete, see next section.
- **§9d best-genotype inspection on r=0.5-unique seeds {0, 3}** — zero-compute. Queued alongside §9c.
- **Revise §9 summary.** The §9 result ("protection antagonistic") applies only to r ≤ 0.3. Main-summary entries need updating after §9c.

---

## 9c. n=20 confirmation of the protection curve

**Sweep:** `sweeps/sum_gt_10_soft_confirm.yaml` — K=3 × r ∈ {1.0, 0.9, 0.5, 0.3} × seeds 10-19 = 40 novel runs, matching §9b's settings. Purpose: confirm both §9b's r=0.5 peak and the r=0.3 collapse on an independent seed set before adopting r=0.5 as the chem-tape baseline.

### Status: complete. Finding: **peak confirmed as a plateau r ∈ [0.5, 0.9]; r=0.3 "collapse" did NOT replicate.**

Results from commit `25c17a9` (sweep elapsed 805s / 13.4 min at 4 workers; 40 novel runs).

#### Per-half results

| r   | seeds 0-9 (§9b) | seeds 10-19 (§9c) | combined n=20 | vs historical 30% baseline |
|-----|-----------------|-------------------|---------------|----------------------------|
| 1.0 | 3/10            | 4/10              | 7/20 (35%)    | consistent with baseline   |
| 0.9 | 4/10            | 6/10              | 10/20 (50%)   | convincingly above         |
| **0.5** | **6/10**    | 5/10              | **11/20 (55%)** | **convincingly above**   |
| 0.3 | 1/10            | 4/10              | 5/20 (25%)    | consistent with baseline   |

**Statistical framing note.** The p-values in an earlier draft of this table tested against a fixed null p=0.3 (the historical chem-tape baseline expectation), not the observed r=1.0 sample of 7/20. For the direct pairwise comparison r=0.5 vs r=1.0 on paired seeds: 5 seeds where r=0.5 wins and r=1.0 loses, 1 seed the other way — one-sided McNemar p ≈ 0.11. So r=0.5 (and r=0.9) are convincingly above baseline expectations at ~50% vs the historical ~30%, but the direct pairwise advantage over r=1.0 is directional rather than sharply estimated at n=20.

Seeds solved in the combined sample:
- r=1.0: {2, 6, 7, 13, 14, 18, 19}
- r=0.9: {0, 2, 6, 9, 10, 12, 14, 15, 16, 18}
- **r=0.5:** {0, 2, 3, 6, 7, 8, 10, 13, 14, 15, 18}
- r=0.3: {2, 14, 15, 18, 19}

#### What §9c confirms

1. **Moderate protection (r ∈ [0.5, 0.9]) is a real effect at n=20.** Both r=0.5 (11/20) and r=0.9 (10/20) are convincingly above the 30% historical baseline expectation. The direct pairwise advantage over r=1.0 (7/20) is directional — McNemar p ≈ 0.11 — so "real but not sharply estimated at n=20." This is not a seed-luck artifact on §9b's half.

2. **r=0.5 and r=0.9 are nearly tied.** On seeds 0-9, r=0.5 dominated (6 vs 4). On seeds 10-19, r=0.9 dominated (6 vs 5). Combined, r=0.5 at 11/20 vs r=0.9 at 10/20 — statistically indistinguishable. **§9b's "peak at r=0.5" was a single-point seed-sampling artifact; the actual structure is a plateau across r ∈ [0.5, 0.9]**, not a single peak.

3. **r=0.3 is noisy, not consistently antagonistic.** On seeds 0-9, r=0.3 solved 1/10 (strong collapse). On seeds 10-19, r=0.3 solved 4/10 (matches baseline). Combined 5/20 is not significantly different from null p=0.3. The §9b "collapse at r=0.3" story did not replicate; it was seeds-0-9-specific variance. The real antagonistic regime starts below r=0.3 (r=0.1 from §9 is 1/10 on seeds 0-9, not tested on 10-19).

#### What §9c reveals about the seed populations

Seeds 10-19 are **collectively slightly easier** than seeds 0-9:
- r=1.0 on seeds 10-19: 4/10 vs seeds 0-9: 3/10.
- r=0.3 on seeds 10-19: 4/10 vs seeds 0-9: 1/10.

This has implications for all past findings that used only seeds 0-9 as baselines (most of §1–§9b). The §2b "Arm A solves 3/10" and §8 "K=3 solves 3/10" numbers may understate A and K=3's true solve rates; seeds 10-19 would likely reveal slightly higher values for these arms too. §4f (panmictic baseline on seeds 10-19, queued) becomes more important as a general methodological step, not just for the islands attribution.

#### Combined reachable-seed picture (n=20)

Seeds ever solved by some chem-tape condition or Arm A on sum-gt-10:

| seed set | solved by |
|----------|-----------|
| 0, 3, 7, 8, 10, 12, 13, 14, 15, 16, 19 | some protected-K=3 condition |
| 1 | only A-islands (§4) and r=0.7 (§9b) |
| 2, 6, 9, 18 | widely solved across arms |
| **4, 5, 11, 17** | **never solved by any condition (n=20 hard floor)** |

**16/20 = 80% of seeds are reachable by some chem-tape variant.** Up from §9b's 8/10 preliminary figure. Hard floor remains at ~20% (seeds {4, 5, 11, 17}).

#### Revised mechanism reading (after §9c)

- Protection landscape is a **plateau** across r ∈ [0.5, 0.9], not a single peak. Both give ~50% solve rate at n=20.
- Below r=0.3, protection becomes antagonistic (§9's original r=0.1 result at 1/10 still stands).
- Above r=1.0 (no protection) the 35% baseline holds.
- The **2×–5× differential between scaffold and tail mutation rates** is the active mechanism range. The specific sweet-spot ratio is not sharp — anywhere from 1.1× (r=0.9) to 2× (r=0.5) provides significant benefit.

#### Recommendation

**Adopt K=3 + r=0.5 (or r=0.9) as the chem-tape baseline going forward.** At n=20 both outperform r=1.0 by ~15 percentage points. The choice between 0.5 and 0.9 is arbitrary given their near-equivalent performance; default to **r=0.5** for simplicity (larger differential, cleaner mechanism interpretation) unless a downstream experiment motivates otherwise.

---

## 9d. Best-genotype inspection on protection-specific winners

**Question.** §9b and §9c showed moderate protection solves seeds that r=1.0 K=3 cannot. Does this correspond to a distinct structural pattern in the evolved tapes, or does protection just "do the same thing better"?

### Method

Zero-compute. Decoded the best-genotype tapes for:
- **r=0.5-unique on seeds 0-9:** {0, 3} — failed at r=1.0, solved at r=0.5.
- **r=0.5 novel on seeds 10-19:** {10, 15} — failed at r=1.0, solved at r=0.5.
- **r=0.9 novel on seeds 10-19:** {16} — failed at r=1.0, solved at r=0.9.

All at K=3; top-3 decode mask extracted.

### Result

Per-seed tape architecture (★ = protection-specific solve):

| seed | r    | gens | #runs | top-3 lens          | architecture          |
|------|------|------|-------|---------------------|-----------------------|
| ★ 0  | 0.5  | 1116 | 4     | [13, 11, 4]         | Multi-chunk with tail quarantine (§8a-style) |
| ★ 3  | 0.5  | 844  | 1     | [32]                | A-like single run                      |
| ★ 10 | 0.5  | 1087 | 1     | [32]                | A-like single run                      |
| ★ 15 | 0.5  | 508  | 2     | [26, 5]             | Near-A-like with small tail           |
| ★ 16 | 0.9  | 1263 | 2     | [17, 14]            | Bimodal — two roughly equal runs      |

Note on "A-like": the decode *behaviour* on a 1-run tape under K=3 is identical to Arm A's decode — the whole non-separator span executes. But the tape was evolved under different selection pressure (top-3 decode + differential mutation), so its program content may differ systematically from tapes Arm A evolves. "A-like architecture" describes the decode shape, not necessarily the program semantics.

### Interpretation

**Moderate protection's five inspected winners span multiple tape architectures.** K=3 r=1.0's winners (§8a: seeds 2, 6, 7) were uniformly multi-chunk with quarantine tails (4, 6, 7 non-separator runs). Arm A / K=999 winners were uniformly 1-run or flat multi-run. The five inspected r=0.5/0.9 winners include multi-chunk (seed 0), A-like (seeds 3, 10), near-A-like (seed 15), and bimodal (seed 16).

This is **suggestive but not established evidence** that §8a's quarantine-via-exclusion story is incomplete for the moderate-protection regime. Seeds 3 and 10 have no tail to quarantine, yet they solve under K=3 r=0.5 while failing at K=3 r=1.0. So whatever advantage r=0.5 provides on those seeds, it is not the §8a mechanism.

**Working hypothesis (not yet established):** differential mutation creates a more stable fitness signal that lets evolution commit to whichever architecture fits the seed's specific landscape — multi-chunk when that's the path, A-like when that's the path, bimodal when that works. Call it **architecture-agnostic scaffold stability** as a provisional label. Five seeds is too small to establish this; it needs either (a) a larger structural-inspection sample across all 11 r=0.5 solved seeds, or (b) a direct experimental test that discriminates this hypothesis from alternatives (e.g., "protection merely raises success rate uniformly across whatever architectures evolution would have found").

### Implications

1. **§8a's mechanism description is partial.** It correctly describes K=3 r=1.0's winners (three inspected, all multi-chunk) but at least two of the five r=0.5 inspected winners (seeds 3, 10) are A-like single-run architectures that §8a's quarantine story does not explain. Working picture:
   - K=3 + r=1.0: quarantine-via-exclusion mechanism; all three inspected winners multi-chunk.
   - K=3 + r ∈ [0.5, 0.9]: five inspected winners span multi-chunk, A-like, and bimodal. Working hypothesis: architecture-agnostic scaffold stability. **Not yet established** — requires larger sample or mechanistic experiment.
   - K=3 + r ≤ 0.3: scaffold freezing; blocks assembly. Replicated at r=0.1; r=0.3 is noisy (see §9c).

2. **§10 K-alternating's premise needs revisiting.** The plasticity hypothesis in §10 — "cryptic variation in K=3's quarantined tail becomes primary scaffold when K flips to ∞" — is a specific mechanism that may not apply to r=0.5 winners that are A-like (seeds 3, 10 have no tail). The K-alternating test at K=3 r=0.5 may produce outcome 3 (canalized generalist) for A-like winners and outcome 1 (smooth switching) only for multi-chunk winners — a per-seed effect to pre-register, and a reason to run §10 with an architecturally-uniform baseline (K=3 r=1.0, whose winners are consistently multi-chunk) rather than r=0.5 if the clean plasticity test is the goal.

3. **Seed 16's bimodal architecture is a novel observation, n=1.** Two nearly-equal runs (lengths 17 and 14) is a structure neither K=3 r=1.0 nor K=999 nor Arm A produced in any inspected winner. Worth flagging but not over-weighting — a single instance isn't a pattern.

### Updated working summary (post-§8a + §9d)

| regime                    | inspected winning architectures      | status                          |
|---------------------------|--------------------------------------|---------------------------------|
| K=3 r=1.0                 | Multi-chunk with quarantined tail (n=3) | Quarantine mechanism (§8a), uniform evidence |
| K=3 r ∈ [0.5, 0.9]        | Multi-chunk, A-like, bimodal (n=5)   | Mixed architectures; broader mechanism suggested but not established |
| K=3 r ≤ 0.3               | None successful                      | Scaffold freezing; antagonistic |
| K=999 / Arm A             | A-like single run or flat multi-run  | Full-breadth execution          |

---

## 10. K-alternating regime shift — plasticity test

**Motivation (after §8+§8a+§9).** §8/§8a/§9 converge on the claim that decode rule is the load-bearing evolvability axis and decode-induced quarantine (K=3's lower-ranked runs as mutation sinks) is the specific mechanism. Two distinct plasticity claims remain untested, and §10 is the sharpest single-task test available for them:

- **Latent-phenotype plasticity:** does the cryptic variation accumulated in K=3's quarantined tail become functional primary scaffold when the decode forces those cells to execute? This is the central prediction that would vindicate chem-tape as a many-to-many genotype-phenotype substrate.
- **Canalized generalist body:** can evolution find a single tape that performs adequately under multiple K values — even without true latent-phenotype switching — trading peak per-K fitness for cross-K robustness?

K-alternating holds the task fixed and alternates the decode every N generations. It does not require multi-task infrastructure, isolates the K-plasticity mechanism cleanly, and its outcome reshapes the priority of both evolve-K-per-individual and the original §v1.5 task-alternating design.

### Design

**Base condition.** sum-gt-10, pop=1024, gens=1500, seeds 0-9, backend=mlx (same as §8/§9 for comparability).

**Regime-shift schedule.** K alternates between K=3 (quarantine present) and K=∞ (all non-separator cells execute). The K=3 ↔ K=∞ pairing is chosen because §8a established that K=3 quarantines tails while K=∞ forces every non-separator cell to execute — this is the most direct test of whether cryptic variation becomes primary scaffold.

**Flip interval (grid):** every 100 gens, every 300 gens. Rationale: 100 gens is short enough that mid-flip recovery dynamics are visible; 300 gens allows partial specialization before each flip. Both are explored.

**Controls (fixed-K reference runs, already on disk):**
- K=3 fixed for 1500 gens (§8 anchor): 3/10 on seeds {2, 6, 7}.
- K=∞ / K=999 fixed for 1500 gens (§8 anchor): 3/10 on seeds {2, 8, 9}.

**Metrics (per seed, per regime flip):**
- Post-flip fitness drop: `best_fitness(gen = flip_t - 1) − best_fitness(gen = flip_t)`.
- Recovery time: generations until post-flip fitness returns to within 5% of pre-flip peak.
- Cross-K ratio: `min(best_fitness_under_K=3, best_fitness_under_K=∞) / max(...)`. Flatness of this ratio across a run diagnoses the canalized generalist outcome.
- Solve-count under the alternating schedule (vs fixed-K controls).

### Pre-registered outcomes

| outcome | signature | interpretation |
|---------|-----------|----------------|
| **(1) Smooth switching** | Post-flip fitness drop small; recovery < 30 gens; solve-count ≥ better-fixed-K control | Latent-phenotype plasticity vindicated. Quarantined-tail variation does become primary scaffold when K flips. Evolve-K-per-individual becomes high-prior next experiment. |
| **(2) Abrupt collapse** | Post-flip fitness drop large; recovery > 300 gens or never; solve-count strictly worse than better-fixed-K control | Latent-phenotype plasticity fails on chem-tape. K-committed bodies cannot re-route. Evolve-K-per-individual inherits this ceiling — de-prioritize in favor of multi-task evolve-K-islands as the §v1.5 convergence. |
| **(3) Canalized generalist** | Cross-K ratio stays high (> 0.7) throughout the run; per-K peak fitness is below fixed-K controls; solve-count comparable but slower | Evolution finds bodies that are adequate under both K values without true latent switching. Theoretically the most interesting outcome: partial plasticity without cryptic variation as primary mechanism. Pre-register this explicitly — it's easy to miss by only coding (1) vs (2). |
| **(4) Monotone degradation** | Each flip strictly worsens fitness; no recovery between flips | Alternation itself is harmful regardless of K-switching semantics. Would suggest selection horizon is too short vs flip interval — retry at longer intervals or abandon. |

### Decision tree (asymmetric)

Positive K-alternating (outcomes 1 or 3) → **evolve-K-per-individual with islands** becomes the clear next experiment, with outcome-3 adding a generalist-body hypothesis to pre-register.

Negative K-alternating (outcome 2) → does **not** kill evolve-K by itself, because a panmictic evolve-K on sum-gt-10 can simply fix K=3 and do fine (single-task optimization doesn't require plasticity to be adaptive). The sharper follow-up in this branch is **multi-task evolve-K-islands** where fix-K is suboptimal by construction — which is where the §v1.5 reframe and evolve-K converge into the same experiment.

### Design notes pre-registered for follow-ups

**Within-individual vs between-population plasticity (if §10 runs).** A body that performs well under both K=1 and K=3 needs its longest run to be functional on its own AND its top-3 concatenation to be functional. That's a much narrower search target than either optimum alone — possibly too narrow to evolve under panmictic selection on a single task. §10 tests within-individual plasticity directly. Evolve-K-islands (follow-up) tests between-population plasticity. These may have different answers; chem-tape may support the second but not the first. Name the distinction explicitly when reporting results.

**Migration design for future evolve-K-islands.** Different-K islands will have incompatible body structures. Naive ring-migration lands migrants in foreign basins where they underperform and get outselected before contributing. Design options to evaluate before running:
- Very low migration rate (rare-novelty injection).
- Asymmetric migration (one-way; e.g., K=3 → K=1 only, testing whether cryptic content from K=3's tails helps K=1 populations).
- **"Migrate body, adopt host K"** — decouples body from its evolved decode context; a meaningful design decision in itself.

The naive default (standard ring-migration with identical bodies flowing across K priors) is likely to produce a null result that doesn't actually test the plasticity claim. Worth a pre-implementation discussion.

**§v1.5 reframe adopted.** Replace the original "neutral reserve enables regime recovery" with "quarantined-tail cryptic variation becomes primary scaffold after regime change." Sharper and more falsifiable. Applies to both §10 (K-alternating, single-task) and future §v1.5 (task-alternating, multi-task).

### Status: queued. To run after §9b completes.

---

## 4f. Arm A panmictic baseline on seeds 10-19

**Sweep:** `sweeps/sum_gt_10_arm_a_confirm.yaml` — 10 runs, Arm A panmictic on seeds 10-19. Closes the methodological hole that every prior "A vs chem-tape" comparison on sum-gt-10 used only seeds 0-9.

### Status: complete.

Results from commit `e86aba4` (141s / 2.4 min at 4 workers).

| seed half | solved | seeds solved (gens) |
|-----------|--------|---------------------|
| 0-9 (§2b) | 3/10   | 2 (889), 8 (626), 9 (391) |
| 10-19 (§4f) | 2/10 | 14 (711), 18 (190)  |
| **n=20**  | **5/20 (25%)** | {2, 8, 9, 14, 18} |

**Revises §9c's "seeds 10-19 are slightly easier" claim.** The claim was arm-specific: K=3 r=1.0 finds 4/10 on 10-19 vs 3/10 on 0-9, but Arm A finds *fewer* on 10-19 (2/10 vs 3/10). Different arms have different seed-difficulty profiles. The right framing is "seed-difficulty varies by arm," not "seed difficulty varies uniformly."

---

## 11. Compact K × r × islands comparison

**Motivation.** §8, §9, §4 independently established that decode breadth, moderate protection, and island-model diversity each help vs Arm A on sum-gt-10. The open question: do these three factors add, substitute, or interact? A 3 × 2 grid isolates the answer.

**Sweep:** `sweeps/sum_gt_10_krs_islands.yaml` — K=3 × r ∈ {1.0, 0.5} × n_islands=8 × seeds 0-19 = 40 novel runs. Fills the missing island cells; other cells already on disk.

### Status: complete. Finding: **factors are non-additive; r=0.5 + islands actively destroys the r=0.5 advantage.**

Results from commit `e86aba4` for §4f, this commit for §11 (sweep elapsed 875s / 14.6 min at 4 workers, 40 novel runs).

#### The full 3 × 2 grid at n=20

| condition                 | solved/20 | seeds solved |
|---------------------------|-----------|--------------|
| Arm A panmictic           | 5/20      | 2, 8, 9, 14, 18 |
| Arm A islands             | 7/20      | 1, 2, 9, 14, 15, 18, 19 |
| K=3 r=1.0 panmictic       | 7/20      | 2, 6, 7, 13, 14, 18, 19 |
| K=3 r=1.0 islands         | 8/20      | 1, 2, 7, 8, 14, 15, 16, 18 |
| **K=3 r=0.5 panmictic**   | **11/20** | **0, 2, 3, 6, 7, 8, 10, 13, 14, 15, 18** |
| K=3 r=0.5 islands         | 5/20      | 0, 1, 2, 14, 18 |

#### Pairwise McNemar tests (one-sided, paired seeds 0-19)

| comparison                                          | wins/losses | p-value |
|-----------------------------------------------------|-------------|---------|
| **K=3 r=0.5 panmictic > A panmictic**               | **7/1**     | **0.035 ★** |
| K=3 r=0.5 panmictic > A islands                     | 7/3         | 0.172   |
| **K=3 r=0.5 panmictic > K=3 r=0.5 islands**         | **7/1**     | **0.035 ★** |
| K=3 r=1.0 panmictic > A panmictic                   | 4/2         | 0.344   |
| K=3 r=1.0 islands > A panmictic                     | 4/1         | 0.188   |
| A islands > A panmictic                             | 3/1         | 0.312   |
| K=3 r=1.0 islands > K=3 r=1.0 panmictic             | 4/3         | 0.500   |

Only two comparisons clear the p<0.05 threshold at n=20: **K=3 r=0.5 panmictic beats Arm A panmictic, and K=3 r=0.5 panmictic beats K=3 r=0.5 islands.** Every other comparison is directional or ambiguous.

#### Three findings

1. **The three factors are not additive.** Naive additivity would predict K=3 r=0.5 islands ≈ 13–15/20 (if islands add ~2 solves to every panmictic cell, as they do for Arm A: 5 → 7). Actual: **5/20, same as Arm A panmictic's baseline.** Adding islands to the best-performing cell destroys its 11-solve advantage entirely.

2. **r=0.5 and islands are substitutes, not complements.** Both mechanisms make evolution "gentler" — protection by reducing scaffold mutation rate; islands by preserving diversity via subpopulations. Applied together, evolution is too gentle to assemble scaffolds — not enough exploration pressure. Lost under K=3 r=0.5 islands: seeds {3, 6, 7, 8, 10, 13, 15} — specifically, seven of the "novel r=0.5" seeds from §9b/§9c. Islands keep the Arm-A-findable seeds {1, 2, 14, 18} but lose the protection-findable ones.

3. **K=3 r=0.5 panmictic remains the single best cell**, and its advantage over Arm A panmictic (11 vs 5, p=0.035) is the only statistically significant arm-vs-arm comparison at n=20. K=3 r=1.0 vs A panmictic (7 vs 5) and A islands vs A panmictic (7 vs 5) are directional but not significant.

#### Mechanism reading

The non-additivity points at **interaction between exploration pressure and selection pressure**. Each factor reduces one or the other:

- Arm A → K=3 decode: reduces *selection noise* (top-K decode filters out irrelevant tape regions from fitness evaluation).
- r=1.0 → r=0.5: reduces *mutation pressure on scaffold cells* (preserves partially-assembled structure).
- panmictic → islands: reduces *selection homogenization* (each island explores independently).

Applied together, all three simultaneously dial down the forces that drive evolution to find solutions. K=3 + r=0.5 gives panmictic pop=1024 just enough exploration to assemble novel scaffolds. Add islands (pop per island = 128) and the same protection/decode settings are operating in a population that's already diversity-preserved — the combination starves the search of pressure to move.

This is a provisional mechanism reading from the solve-count pattern; the fitness-trajectory data per seed (which I haven't inspected) would test whether the K=3 r=0.5 islands cell plateaus earlier than panmictic, or just crawls slower. That's a zero-compute follow-up worth doing.

#### Implications for upstream experiments

**§4's "islands help" story was arm-specific.** §4 tested A, B, BP under islands; all three gave small positive shifts. §11 shows this does NOT generalize to K=3 r=0.5 — the shift is strongly negative. The §4 methodological finding ("a GA-structure choice affects solve counts across arms") is correct, but the specific claim "islands help" needs qualification to "islands help under low-exploration-pressure regimes but hurt under low-exploration-pressure × high-protection combinations."

**§10's plasticity test should use K=3 r=1.0 as the baseline, not r=0.5.** §11 shows r=0.5 is already fragile to additional GA-structure changes (islands hurt it dramatically). A K-alternating schedule is also a GA-dynamics perturbation; there's no reason to expect r=0.5 to tolerate it better than it tolerates islands. Use the architecturally-uniform K=3 r=1.0 baseline for cleaner interpretation.

#### Combined reachable-seed picture

Union across every condition tried on sum-gt-10 at n=20 (§1–§11):
- **Ever solved:** {0, 1, 2, 3, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 18, 19} = 16/20 (80%)
- **Never solved by any condition:** {4, 5, 11, 17} = 4/20 (20%)

The hard floor hasn't moved since §9c. Four seeds (20% of the seed space) appear to be outside the reachable set for any chem-tape variant tested so far, including Arm A. Whether these are "impossible at this compute budget" or "impossible regardless of compute" is an open question for later.

---

## Planned v2 experiments (contingent on §2 passing)

### E. Expressivity parity vs folding-Lisp on structured-record benchmarks

**Representation change:** expand alphabet to ~30 tokens (quotations `[` `]`, typed data-source tokens, field access, conditionals), matching the folding-Lisp benchmark domain. See architecture.md §Expressivity vs folding-Lisp.

**Gate:** chem-tape v2 reaches fitness 1.0 on ≥ 70% of folding-Lisp's benchmark ladder at pop=1024, gens=500. Below that, v3 chemistry ablation has no payload to attribute.

### F. Chemistry ablation (v3 kernel)

**Representation change:** at v2 alphabet, introduce folding-style chemistry mechanisms one at a time — single-pass → multi-pass staged → + bond priority → + irreversibility. Five-arm experiment producing a publishable-grade attribution claim about which folding-chemistry property matters for evolvability.

---

## Summary of v1 findings

1. **MVP gate on sum-gt-10: REJECTED (confirmed, n=10).** At pop=1024, gens=1500, Arm A solved 3/10 seeds with holdout 1.000; Arm B solved 0/10 (max best-ever 0.734). Spec §Layer 11's rejection clause "Arm B < Arm A on sum-gt-10 specifically" holds with solid evidence. v1-strict chem-tape is falsified on its own stated acceptance criterion.
2. **But the v1 design error was localized: hard-separator semantics, not the bonding/decode concept itself.** §3's permeable-rule redesign (id 0 passes through bonded runs; ids 14, 15 remain separators) recovers 2 of Arm B's 3 has-upper failures at MVP budget, and 1 of the 3 sum-gt-10 solves at expanded budget (vs B's 0). **Arm BP > Arm B** across all tested benchmarks. The bundling of "no-op" with "hard boundary" into a single "inactive cell" class was the v1 mechanism-level bug.
3. **But Arm BP < Arm A on the hard benchmarks.** Permeability alone does not close the gap: BP 9/10 vs A 10/10 on has-upper, BP 1/10 vs A 3/10 on sum-gt-10. The longest-run decode itself (executing only a bounded region rather than the whole tape) also carries a cost that permeability doesn't address.
4. **When BP wins, it wins efficiently.** On the one sum-gt-10 seed where both BP and A succeed, BP solves at gen 135 vs A at gen 889 — a 6.6× speedup. Shorter programs are genuinely easier to optimize *when they contain the scaffold*. This hints at a selective-decode redesign where BP's mechanism is preserved on bounded-scaffold problems.
5. **Arm B ≠ Arm A on short-scaffold tasks, and the difference is task-specific and opposite in sign.** Count-R: B/BP win (BP fastest at 11.0 median gens). Has-upper: A wins. The best current explanation is fitness-signal granularity, not scaffold length per se — graded integer labels favor shorter-program arms; binary labels with trivial-constant plateaus favor longer-program arms. §4 granularity sweep (queued) would test this as a predictor.
6. **Mechanism claim partially vindicated (not in the predicted form).** The architecture's "scaffold preservation" framing doesn't describe the v1 data, but **§3's "decode matters and hard-separators hurt" finding vindicates a weaker claim**: the bond/decode structure does change search in ways that matter — just not necessarily in the direction or for the reason the architecture anticipated. This is the correct v1 → v2 handoff framing: what v2 should try next is *different decode rules*, not *richer chemistry* (per the original research ladder).
7. **§2c resolved: v1 is a search-efficiency cost, not a ceiling.** Arm B solves 2/5 at pop=4096 (40%) vs 0/5 at pop=1024. Arm A keeps a roughly constant +1–2 solve advantage across the four tested budget points. Population scaling (1024→4096) helps more than generation scaling (1500→3000). The v1 rejection stands in the narrow "at the spec's budget" sense, but v1-strict is not an unworkable representation — it's a less search-efficient one than direct stack-GP, with the decode rule (not bonding as a concept) as the binding constraint.
8. **§4 island-model: n=20 shows effects are real but smaller than n=10 suggested.** Under 8×128 islands with ring-topology synchronous migration: Arm A 7/20 (35%), Arm B 2/20 (10%), Arm BP 3/20 (15%). The A-B rejection holds firmly at n=20 (gap: 25 percentage points). The n=10 preview's "islands specifically help B" claim is underpowered — without panmictic baselines on seeds 10-19 we can't cleanly separate representation-specific benefits from general island benefits that affect all arms. The *methodological finding* is firm: a GA-structure choice affects solve counts by single-digit percentage points across arms, so a single-GA baseline is not a neutral test of a new representation. **Panmictic pop=1024 should no longer be the default baseline for chem-tape experiments.** §4f panmictic-on-10-19 baseline is the critical missing data to resolve effect-size attribution.

9. **§8 Top-K result: non-monotone, K=3 unlocks unreachable seeds.** K=3 on sum-gt-10 solves 3/10 including seeds {6, 7} that no other arm (A, B, BP, K=1,2,4,8,999) has ever solved — a K-specific reachability effect, not a search-efficiency one. K=1 reproduces BP (§3b) and K=999 reproduces A (§2b) bit-exactly. Union of solves across K covers 5/10 seeds vs any single arm's ≤ 3/10. Pre-registered outcome (3) — intermediate decode-breadth wins. Top-K becomes a first-class chem-tape hyperparameter; §9 (soft decode) re-promoted with a sharper question ("can protection alone reach K=3's unique seeds, or is selective decode necessary?").

10. **§8a inspection result: mechanism is mutation quarantine via execution-exclusion.** Seeds 6 and 7 (K=3-unique) evolve multi-chunk tapes whose top-3 bonded runs carry the functional program while lower-ranked runs hold non-executing "junk" cells. On seed 2, same initial RNG population, K=3 evolves a 7-run tape and K=999 evolves a 1-run tape — direct evidence that decode rule reshapes evolved architecture. The mechanism is Altenberg's constructional selection surfacing through the decode layer rather than through selection pressure. §9 redesigned as 2×2 factorial — protection and selective-decode are complements, not substitutes.

11. **§8b K-curve on short-scaffold tasks: optimal K is task-dependent.** count-R (graded, 4-cell scaffold): K=1 dominant at median 11 gens, K=3 3.5× slower. has-upper (binary-plateau, 4-cell): K=1 falls into trivial-constant trap (9/10), K≥3 matches Arm A exactly (10/10 at median 69). Combined with §8 on sum-gt-10 (graded, 14-cell) where K=3 wins uniquely: no single K is uniformly best. K_optimal appears to increase with scaffold length and in the presence of binary-plateau traps. Chem-tape reports should include multiple K values by default — a single-K framing misses the structure entirely. The §1 MVP's "chem-tape vs direct" gate rejection was partially an artifact of fixing K=1 (= Arm B).

12. **§9 / §9b / §9c soft decode — moderate protection is a real and confirmed win.** The sequence of findings: (a) §9 rejected r=0.1 as antagonistic (K=3: 3/10 → 1/10); (b) §9b's pre-registered closure was falsified, revealing a non-monotone curve with peak at r=0.5 (6/10) including two genuinely novel seeds; (c) §9c confirmed on fresh seeds 10-19 that the peak is real but is actually a **plateau across r ∈ [0.5, 0.9]**, not a single peak — combined n=20: r=0.5 → 11/20 (55%, p=0.017 vs null), r=0.9 → 10/20 (50%, p=0.048), r=1.0 baseline → 7/20 (35%). The §9b "collapse at r=0.3" did NOT replicate: seeds 10-19 gave 4/10 at r=0.3 (= baseline), confirming the antagonistic regime starts *below* r=0.3, not at it. **K=3 + r=0.5 is the new chem-tape baseline on sum-gt-10** — ~15 percentage points above r=1.0 at n=20. Combined reachable-seed union at n=20 is 16/20 (80%); hard floor is {4, 5, 11, 17}. The architecture's "bonds as evolutionary-dynamics structure" claim is partially vindicated at moderate protection strengths.

13. **Seeds 10-19 reveal that seeds 0-9 are slightly harder.** r=1.0 on seeds 10-19 solves 4/10 vs 3/10 on seeds 0-9; r=0.3 shows a larger gap (4/10 vs 1/10). All findings reported only on seeds 0-9 (§1-§9b, §2b, §4 panmictic) likely understate arm performance by a small but consistent amount. §4f (panmictic baseline on seeds 10-19) now more important as a general methodological correction, not just for the islands attribution question.

14. **§4f + §11 static-picture baseline: K=3 r=0.5 panmictic is the only statistically significant improvement on Arm A panmictic at n=20 (11/20 vs 5/20, McNemar p=0.035).** Every other arm-vs-arm comparison (K=3 r=1.0 vs A, A islands vs A panmictic, K=3 r=1.0 islands vs K=3 r=1.0 panmictic) is directional but not significant at n=20. The three factors decode + protection + islands are **non-additive**: K=3 r=0.5 islands collapses to 5/20 (= Arm A panmictic's baseline), losing 7 of the "novel r=0.5" seeds from §9b/§9c. Mechanism reading: r=0.5 and islands are substitutes, not complements — both reduce exploration pressure, and together they starve the search. Combined reachable-seed union across §1-§11 is 16/20 (80%); hard floor {4, 5, 11, 17}.

15. **Current priorities (reordered after §11):**
    - **§10 K-alternating regime shift** — use K=3 r=1.0 baseline (architecturally uniform, stable under GA-structure perturbations) rather than r=0.5 (§11 showed r=0.5 is fragile to GA changes). Tests within-individual plasticity under a cleaner initial condition.
    - **§8d scaffold-length × K × r** — generalization test; synthetic task design required.
    - **Evolve-K-per-individual (panmictic)** — gated on §10 outcome.
    - **§11 fitness-trajectory inspection (zero-compute)** — does K=3 r=0.5 islands plateau early, or crawl slower? Discriminates between "starved of exploration" and "too slow to converge." ~15 min analysis work.
    - **§v1.5 regime-shift test (task-alternating)** — after §10.
    - **Type-closed top-K decode criterion** — cheap side experiment; low prior.

See [architecture.md](architecture.md) for the substrate specification, [findings.md](../findings.md) for the prior Elixir-era folding results that motivated the "differential outcome" expectation, and [coevolution.md](../coevolution.md) for the coevolution designs that produced the scaffold-preservation framing.
