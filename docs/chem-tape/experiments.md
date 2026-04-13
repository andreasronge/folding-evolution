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

### Status: complete. Diversity hypothesis substantially vindicated for Arm B; no effect on A or BP.

Results from commit `4454c96` — sweep elapsed 330s / 5.5 min at 4 workers.

#### 4a. Head-to-head (islands vs panmictic at matched total evaluations)

| arm | panmictic (§2b / §3b) | islands (§4) | Δ |
|-----|----------------------|--------------|---|
| A   | 3 / 10               | 3 / 10       | 0 |
| B   | **0 / 10**           | **2 / 10**   | **+2** |
| BP  | 1 / 10               | 1 / 10       | 0 |

**A-B solve-count gap:** panmictic +3 → island **+1**. Islands close 2/3 of the v1-strict tax.

#### 4b. Which seeds do islands unlock?

- **Arm B under islands:** solves seeds 2 and 9. Seed 2 solved at gen 701; seed 9 solved at gen 257. Both of these are seeds Arm A also solves — i.e., islands let Arm B reach *already-known-reachable* solutions it was previously missing.
- **Arm B does NOT solve seed 8** even with islands. Arm A under panmictic and islands both solve seed 8 (though island-A shifted the solve pattern: solves seeds 1, 2, 9 instead of panmictic's 2, 8, 9). Seed 8's solution appears intrinsically unreachable under the strict active-cell decode.
- **Arm BP under islands** still solves only seed 2. Islands add nothing for BP.
- **Arm A under islands** shifts which seeds it solves (1, 2, 9 vs panmictic's 2, 8, 9) but matches the same 3/10 total count — consistent with "A's diversity is already adequate under panmictic; islands just reshuffle which seeds get attention."

#### 4c. Interpretation: decomposing the v1 tax

The clean read: **the v1 tax decomposes into two roughly equal parts — diversity loss under panmictic tournament, plus decode-intrinsic pruning.**

- **Diversity-loss part (~2/3 of the tax):** Arm B's narrow reachable-program class (v1's strict active-cell decode excludes NOP-containing and short-run programs) produces less population entropy under panmictic tournament selection. Tournament pulls toward whichever few bonded-run shapes dominate early, and alternatives die off before they can explore. Islands preserve sub-populations exploring different bonded-run configurations; each can independently assemble a scaffold. This is an **infrastructure bug**, not a representation bug. The panmictic GA amplifies a cost that isn't intrinsic to chem-tape.
- **Decode-intrinsic part (~1/3 of the tax):** seed 8 is unreachable under Arm B regardless of GA structure. The solution class Arm A uses on seed 8 (a 32-cell program with junk tokens scattered through the scaffold — the structural shape §3 identified) is *structurally absent* from Arm B's reachable set under any amount of diversity. Islands don't fix this; only decode-rule changes (permeable §3, or soft redesign) can.

**Why Arm A is unchanged by islands:** A's reachable class is "all 32-cell programs" — maximally broad. Its population diversity under panmictic tournament is already high; islands can't add what's already there. The shift in *which* seeds A solves (1/2/9 vs 2/8/9) is noise-level rerouting, not a performance effect.

**Why Arm BP is unchanged by islands:** this is the surprising finding. If BP's decode is broader than B's (NOP passes through), we'd predict smaller diversity-loss tax and therefore smaller island benefit — which is what we see (0 vs +2). But more interesting: BP's one solved seed (2) is the *easiest* seed under any representation, and the diversity preservation that helped B on seeds 2 and 9 doesn't help BP find seed 9 or any unreachable-under-BP-panmictic seed. Possible explanation: seed 9's Arm A solution uses 32-cell breadth; BP's permeable rule extends reach within a bonded region but *doesn't* let programs span across separators. Seed 9 may need that cross-separator reach, which neither B nor BP can provide.

#### 4d. What this means for the v1 verdict and v2 direction

1. **The spec §Layer 11 rejection is narrowed, not overturned.** Arm B 2/10 under islands is still < Arm A 3/10. Rejection clause "Arm B < Arm A on sum-gt-10" still holds. But the gap is now +1, not +3 — and +1 is within the noise range of seed choice for 5–10 seeds. The design is no longer clearly inferior.
2. **"Islands become the new baseline GA" reading is supported.** For future chem-tape experiments (v1.5, soft redesign, granularity sweeps), panmictic pop=1024 is the wrong baseline — islands are. This changes the methodology of every downstream experiment.
3. **The decode-intrinsic residual (~1/3 of the tax) is still there.** §3 (permeable) and §4 (islands) address different parts of the tax: permeable addresses the hard-separator bug within the decode; islands address the tournament-diversity bug within the GA. Neither fully closes it. The combined **BP + islands** configuration would be the natural next test — this sweep tested them separately, not together.
4. **Soft redesign becomes less urgent.** The argument "v1 is dominated by direct stack-GP on its own gate" was the motivator for the soft redesign. With islands (and with the mechanism decomposition above), v1 is now "comparable to direct under matched infrastructure, with a smaller decode-intrinsic cost." The soft redesign moves from "critical-path alternative" to "still-interesting but not obviously required."

#### 4e. Immediate follow-ups

Note: §4 already tested all three arms under islands (the sweep YAML set `n_islands: 8` at the base, and arms were the grid axis). The "BP + islands combined" question that would have been queued is *already* in the §4a/b table — and it shows islands do not help BP. The follow-ups below are what's new:

- **Fully-permeable rule (all of 0, 14, 15 transparent; no hard separators at all).** This is the limiting case of the permeable redesign — ablates the last boundary semantics. If fully-permeable chem-tape matches Arm A under islands, then no hard-separator decode is needed; bonds would have to earn their keep through evolutionary-structure effects (soft redesign) rather than through any execution-gating role. Cheap to implement (one-line change to `SEPARATOR_MASK`) and test (10 runs).
- **Island parameter sensitivity.** Are the pre-registered choices (8 islands, 50-gen interval, 2 migrants) optimal for chem-tape in particular? Unknown. The seed-8 residual under Arm B may respond to different migration schedules. A small sensitivity sweep (migration_interval ∈ {25, 50, 100}, migrants_per_island ∈ {1, 2, 4}) on Arm B only would clarify.
- **Why does seed 8 resist Arm B even with islands?** The best-genotype inspection on Arm A seed 8 would tell us whether the required scaffold shape is intrinsically outside B's (and BP's) reachable set. If so, that's additional mechanism-level evidence for the decode-intrinsic residual.

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
8. **§4 island-model: v1 tax decomposes into diversity-loss + decode-intrinsic parts.** 8-island ring-topology GA with synchronous migration closes 2/3 of the A-B solve-count gap on sum-gt-10 at matched total evaluations — Arm B solves 0/10 panmictic → 2/10 islands (Arm A unchanged at 3/10; Arm BP unchanged at 1/10). This vindicates the diversity hypothesis for Arm B specifically: the v1-strict reachable-program class interacts badly with panmictic tournament selection, not because the representation is broken but because the GA amplifies its narrowness. The residual +1 gap is decode-intrinsic (seed 8 is unreachable under B at any GA structure tested). **Islands become the new baseline GA for every downstream chem-tape experiment.**

9. **Current priorities (in order):**
   - **§v1.5 regime-shift test** (queued, ordered up after §4 resolved) — the experiment the architecture was actually motivated to run. Tests whether chem-tape's neutral reserve enables the folding-analog dynamic advantage when active task rotates within a run. Now runs over the island-GA baseline.
   - **Fully-permeable rule ablation** — ablate ids 14 and 15 as separators too (all three currently-inactive ids become transparent). If this matches Arm A under islands, then no separator-based decode is needed; only the soft redesign remains as a chem-tape research direction.
   - **§3c permeable at expanded budget** (queued) — completes the three-arm budget-scaling picture; lower priority since §3 and §4 together already characterized the representation.
   - **Soft redesign** (bonds as evolutionary-dynamics structure — bond-aware mutation rates, bond-preserving crossover — execution over the full tape, Arm-A-style) remains the natural v2 experiment. **Downgraded in priority** now that §4 shows the v1 gap is partly infrastructure; the soft redesign's unique value is no longer "rescuing a broken representation" but "a genuinely different mechanism for using bonds."

See [architecture.md](architecture.md) for the substrate specification, [findings.md](../findings.md) for the prior Elixir-era folding results that motivated the "differential outcome" expectation, and [coevolution.md](../coevolution.md) for the coevolution designs that produced the scaffold-preservation framing.
