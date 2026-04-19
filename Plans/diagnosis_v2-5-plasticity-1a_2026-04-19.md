# Diagnosis · §v2.5-plasticity-1a — failure-class classification per methodology §29

**Experiment:** §v2.5-plasticity-1a — rank-1 operator-threshold plasticity on Arm A + BP_TOPK seeded cells (`sum_gt_10_AND_max_gt_5` natural sampler, pop=512, budget ∈ {1,2,3,5}). Data commit `4ceb22b` (run 2026-04-19), 240/240 runs.

**Diagnosis:** `selection-deception` / "deception of learning-to-learn" (Risi & Stanley 2010, class 4 per methodology §29). **Dated pre-escalation-prereg per §29's "pre-commit rule" extension of §2b.**

---

## Observed pattern that triggered the diagnosis

1. **PASS-Baldwin row fails.** Arm A Baldwin_slope is positive at every tested budget ∈ {1, 2, 3, 5} with seed-level bootstrap 95% CI excluding 0 on the *positive* side (wrong sign vs the pre-registered Baldwin hypothesis). Magnitude scales monotone with budget: +0.014 → +0.018 → +0.047 → +0.069.
2. **PARTIAL-universal-adapter row fails.** δ_std grows monotone with budget (0.69 → 0.98 → 1.67 → 2.67) — the opposite of the universal-adapter signature (δ collapse). Genotypes at different Hamming distances from canonical find different δ values; near-canonical keeps δ ≈ 0, distant tail pushes |δ| toward 3-5.
3. **FAIL-weak-plasticity row fails.** F_AND_train saturates at 20/20 in every seeded cell (frozen and plastic alike); F_AND_test = 20/20; Baldwin_gap concentrated in h≥4 tail (+0.046 → +0.260 monotone with budget) — capacity IS being exercised, not absent.
4. **GT_bypass fraction < 0.01** across every Arm A plastic cell — regression input is the full population, not a minority.
5. **Population-level δ saturation at budget=5 sf=0.01 is substantial (73.6% mean, max 0.94, 16/20 seeds >50%)** but **top-1 best-of-run winners at sf=0.01 have 0/20 |δ|≥5** (winners are near-canonical, don't use δ). At sf=0.0 drift, 14/20 top-1 winners saturate. Saturation concentrates in the tail the selection layer ignores because canonical-elite dominates best-of-run.
6. **Frozen-control anchor check passes.** Arm A frozen control at pop=512 gens=1500 mr=0.03 reproduces the per-tape mutation budget match to §v2.4-proxy-4c (gens × mr = 45 matched exactly); absolute R_fit magnitudes differ from §4c (pop=512 vs pop=1024 is acknowledged per prereg). F_AND_train = 20/20 on seeded cells establishes infrastructure correctness.

## Classification — walk through the §29 decision tree

### Class 1: `measurement-artifact` (methodology-local)

**Check:** Does the infrastructure gate (§25) fail? Does F_train fall below ceiling on seeded cells? Does the frozen-control anchor diverge from baseline?

**Rejected.** `F_AND_train = 20/20` on every seeded Arm A cell (plastic and frozen alike). `final_population.npz` contains all eight pre-registered per-individual columns (`delta_final`, `test_fitness_frozen`, `test_fitness_plastic`, `train_fitness_frozen`, `train_fitness_plastic`, `has_gt`, `genotypes`, `fitnesses`) per `analyze_plasticity.py`'s pytest-validated ingest (commit `feae431`). METRIC_DEFINITIONS in `analyze_plasticity.py` match the prereg's definitions verbatim. The frozen-control anchor reproduces the per-tape mutation budget of §v2.4-proxy-4c (gens × mr = 45 matched); absolute R_fit difference (0.192 vs 0.004) is attributable to the pop reduction from 1024 to 512 and is acknowledged in the prereg's principle-23 audit clause. **No measurement-artifact failure.**

### Class 2: `mechanism-weak` (capacity-insufficient plasticity; Soltoggio-Stanley-Risi 2018 EPANN review)

**Check:** Is the mechanism's capacity being exercised? Does latent state (δ) spread widen with adaptation budget? Do tail cells show measurable latent activity?

**Rejected.** δ_std grows monotone with budget (0.69 → 0.98 → 1.67 → 2.67). Per-Hamming-bin δ_std broadens across budgets. At budget=5 sf=0.01, 73.6% of the non-GT-bypass population reaches |δ|≥5 — the mechanism is hitting the *edge* of its operative range for the `max > 5` conjunct threshold. Baldwin_gap in the h≥4 tail grows monotone with budget (+0.046 → +0.260) — plasticity IS doing measurable work on distant genotypes. The rank-1 mechanism is not capacity-starved. **No mechanism-weak failure.**

**Specifically:** escalating to rank-2 memory (the §29 escalation for `mechanism-weak`) under the current selection regime would reproduce the same pattern at higher capacity — more δ-space to saturate in the tail while selection continues to prefer canonical-elite. Rank-2 is NOT the correct next step.

### Class 3: `grid-miss` (methodology-local, §2b)

**Check:** Does the observed pattern fit no pre-registered row? (Methodology-local class — applies only when the pattern is novel enough that no literature-term mapping is obvious.)

**Partially applicable, but subsumed by Class 4.** The observed pattern matches none of the prereg's 9 formally-enumerated rows (PASS-Baldwin / PARTIAL-universal-adapter / PARTIAL-δ-convergence / FAIL-weak-plasticity / INCONCLUSIVE-frozen-wins / INCONCLUSIVE-mid-F_test / INCONCLUSIVE-GT-bypass-majority / SWAMPED / INCONCLUSIVE-grid-miss-catchall). The pre-committed scratch candidate INVERSE-BALDWIN from `Plans/scratch_plasticity_1a_grid_extension_2026-04-19.md` (committed at `cecfb58` pre-n=20 analysis on n=13 partial data) matches the observed signatures — but a scratch-doc pre-commitment is not a prereg row, and the scratch doc itself says "do not reference it in the chronicle when the sweep lands" (a self-instruction to prevent silent promotion). So §29's grid-miss class *is* formally satisfied (pattern fits no prereg row), but selecting grid-miss as the sole diagnosis would obscure the literature-term mapping below. The more informative classification is Class 4.

### Class 4: `selection-deception` (Risi & Stanley 2010 "deception of learning-to-learn"; Lehman & Stanley 2011 "objective deception")

**Check:** Is mechanism capacity exercised (yes, per Class 2 rejection), but selection does not *need* the mechanism? Is there a static shortcut that satisfies the fitness criterion before plasticity can contribute?

**Accepted.** Three confirming signatures:

(a) **Static shortcut is structurally present.** Seeded canonical 12-token AND body at sf=0.01 + elite preservation + tournament_size=3 selection: canonical is retained at best-of-run in 20/20 seeds under every tested budget (F_AND_test = F_AND_train = 20/20 saturates). Best-of-run fitness never depends on plasticity because canonical-via-static-decoder already clears the fitness ceiling on training.

(b) **Mechanism-capacity-at-wrong-target.** Plasticity's measurable work (positive Baldwin_gap at h≥4 tail; δ_std growth with budget) happens on the population tail — distant-from-canonical individuals where plasticity compensates for off-canonical thresholds. Selection does not need or reward that compensation because canonical-elite already wins. The population-level δ saturation at budget=5 (73.6% |δ|≥5) with 0/20 top-1 winners |δ|≥5 is the clearest signature: plasticity is exhausting its operative range in the part of the population selection ignores.

(c) **Seed-removal asymmetry.** Drift cells at sf=0.0: Arm A budget=5 gives F_AND_test = 7/20 plastic vs 3/20 frozen-best; BP_TOPK budget=5 gives F_AND_test = 8/20 plastic vs 1/20 frozen-best. Without the static shortcut, plastic discovery from noise becomes measurable. This is consistent with the selection-deception reading: remove the shortcut, plasticity has room to contribute; keep the shortcut, plasticity is a mechanistic side-show that selection cannot distinguish from adaptation-absent behaviour.

**Literature anchor.** Risi & Stanley 2010 ("Evolving Plastic Neural Networks with Novelty Search," *Adaptive Behavior* 18(6), 470-491) identifies this pattern as canonical under objective-driven evolution: static domain-specific heuristics are easier evolutionary targets than plastic learning rules; selection finds static first and never commits to plasticity. The escape route Risi & Stanley propose is novelty search on a plasticity-sensitive behavioral characterization (BC) — but BC power determines search power, and a poorly chosen BC trades one deception for meaningless exploration. The escalation ladder below reflects this.

**`docs/theory.md` currency.** Risi & Stanley 2010 entry added to `docs/theory.md` "References to Obtain" at methodology-improvements commit `cecfb58` (2026-04-18) alongside the §29 addition itself. Lehman & Stanley 2011 (novelty-search foundational paper) also referenced there. No new theory.md additions required from this diagnosis commit beyond confirming the entries exist.

---

## Rejected-diagnoses record (for §29 principle-29 pre-commit rule)

| class | rejected on the evidence of | one-line reason |
|---|---|---|
| `measurement-artifact` | F_AND_train saturation + METRIC_DEFINITIONS verification + frozen-control anchor discharge | infrastructure passes every §25 gate |
| `mechanism-weak` | δ_std monotone growth + h≥4 Baldwin_gap monotone growth + population saturation at budget=5 | capacity is being exercised; rank-2 would reproduce the pattern |
| `grid-miss (§2b only)` | pattern fits §29 Class 4 signature | grid-miss is formally correct but literature-term mapping adds more information; Class 4 takes priority |

---

## Escalation path (pre-committed, per §29 prereg-reference-pattern)

Per §29 class-4 `selection-deception` escalation: change the **selection regime**, not the mechanism. Ladder ordered cheapest → most engineering:

### Rung 1 — Strip the canonical seed (§v2.5-plasticity-2a candidate)

Sweep identical to §v2.5-plasticity-1a except `seed_fraction=0.0` across all budget cells. No engineering beyond a sweep YAML edit. Disjoint-seed replication (seeds 20..39) preferred to avoid same-seed re-use.

**Decision rule at sf=0.0:**
- If INVERSE-BALDWIN replicates (slope positive, CI excludes 0 on positive side, δ_std grows with budget): selection-deception is **partially refuted** — the static-canonical shortcut is not the sole driver; rank-1 plasticity may have an intrinsic "help-concentrates-in-distant-tail" property. Diagnosis narrows to a mechanism-structural reading; escalation pivots toward rank-2 memory or deeper architecture (not novelty search first).
- If slope flips to negative (Baldwin-direction) at any budget with CI excluding 0: selection-deception is **strongly supported** — removing the shortcut allowed plasticity to do its intended work. Escalation: novelty-search / MAP-Elites with a pre-registered plastic-adaptation BC (Rung 3) to confirm the finding under a fully BC-driven selection regime; rank-2 memory deferred until this confirmatory leg lands.
- If slope is flat (CI includes 0) with F_AND_test ≥ 15/20 on drift: universal-adapter reading fires on the no-shortcut regime; report as NULL-at-rank-1 and escalate to rank-2 under sf=0.0 as the next mechanism probe.

**Status:** prereg NOT yet drafted. To be registered as §v2.5-plasticity-2a after this diagnosis doc lands and before any sweep launches. The prereg's Setup section must contain the §29 reference clause (see "Prereg-reference-pattern clause" below).

**Estimated compute:** ≈ 2-4 hours wall at 10 workers (same order as §v2.5-plasticity-1a's Arm A + BP_TOPK plastic cells, minus the seeded cells).

### Rung 2 — Evolvability-ES under rank-1 plasticity (§v2.5-plasticity-2b candidate)

EES rewards offspring-variance diversity directly (no BC commitment needed). Under §29's class-4 escalation ladder this is the cheapest BC-free selection-regime change. Engineering: ~1 week to land an EES selection primitive in the chem-tape executor.

**Decision rule:** If EES produces a Baldwin-direction slope at ≥ 1 budget or a collapse of δ_std's budget-scaling (mechanism-state stops diverging under EES), selection-deception survives and the next rung becomes the BC-driven confirmatory. If EES reproduces the positive-slope + δ_std-growth INVERSE-BALDWIN pattern, selection-deception is ruled out and the mechanism is read as an intrinsic rank-1 structural property.

**Status:** prereg NOT drafted; blocked on EES primitive implementation. §v2.5-plasticity-2b is the candidate ID.

### Rung 3 — Novelty search / MAP-Elites with pre-registered plastic-adaptation BC (§v2.5-plasticity-2c candidate)

Candidate BCs (each requires pre-registration with METRIC_DEFINITIONS per principle 27 before any sweep launches):

- `adaptation_delta_BC`: per-individual `test_fitness_plastic − test_fitness_frozen` across a parametric `THRESHOLD(k)` task family (k ∈ {3, 5, 7, 10, 12}). Rewards genotypes where plasticity does measurable work; collapses inverse-Baldwin by construction (tail-only uplift won't survive a BC that asks "which genotypes use plasticity across multiple thresholds").
- `parametric_output_vector_BC`: 5-element binary output vector on `THRESHOLD(k)`. Rewards genotypes that respond differently to k. More expressive but noisier.
- `operator_frequency_histogram_BC`: structural histogram of decoded program tokens. Cheap but likely underpowered — doesn't distinguish static-wins-with-different-ops from plastic-wins.

**Mouret-Clune 2015** (MAP-Elites) and **Pugh-Soros-Stanley 2016** (BC design discipline) are the methodology-local references for BC design; both cited in `docs/theory.md` "References to Obtain" at `cecfb58`.

**Status:** BC-prereg blocker. §v2.5-plasticity-2c is the candidate ID. No sweep launches until the BC prereg lands.

### Rung 4 (deferred): rank-2 memory (§v2.5-plasticity-1b — the plasticity-direction doc's original fallback)

**Rank-2 is deferred, not the next step.** Per §29 and per the scratch-doc diagnostic tree: rank-2 memory targets `mechanism-weak` (class 2), not `selection-deception` (class 4). Queuing rank-2 under the current selection regime would reproduce the INVERSE-BALDWIN pattern at higher capacity. Rank-2 is revisited only after either (a) P-1 (Rung-1 sf=0.0 check) violates the selection-deception diagnosis by reproducing INVERSE-BALDWIN on the no-shortcut regime, or (b) a separate `mechanism-weak` signal appears in a task where selection-deception is structurally absent.

---

## Prereg-reference-pattern clause (for §v2.5-plasticity-2* escalation preregs)

Any §v2.5-plasticity-2{a,b,c} escalation prereg MUST include in its Setup section:

> *This prereg follows from diagnosis `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md` (class: `selection-deception` / "deception of learning-to-learn" — Risi & Stanley 2010). Escalation path is pre-committed; scope is restricted to the path identified there.*

The research-rigor `prereg` mode should refuse to finish drafting the escalation prereg without this clause when this diagnosis doc exists in the preceding commit history.

---

## References cited

- **Risi, S. & Stanley, K. O. (2010).** "Evolving Plastic Neural Networks with Novelty Search." *Adaptive Behavior* 18(6), 470-491. Canonical reference for "deception of learning-to-learn" — static domain heuristics are easier evolutionary targets than plastic learning rules; objective-driven evolution finds static first and never commits to plasticity. Escape route: novelty search on a plasticity-sensitive BC. Caveat: BC power = search power. (In `docs/theory.md` "References to Obtain"; full read pending.)
- **Lehman, J. & Stanley, K. O. (2011).** "Abandoning Objectives: Evolution Through the Search for Novelty Alone." *Evolutionary Computation* 19(2), 189-223. Foundational "objective deception" paper in the novelty-search lineage; underwrites the BC-driven escape-hatch pattern above. (In `docs/theory.md` "References to Obtain".)
- **Soltoggio, A., Stanley, K. O., & Risi, S. (2018).** "Born to learn: the inspiration, progress, and future of evolved plastic artificial neural networks." *Neural Networks* 108, 48-67. EPANN review; definitional anchor for `mechanism-weak` (capacity-insufficient plasticity). (In `docs/theory.md` "References to Obtain".)
- **Mouret, J.-B. & Clune, J. (2015).** "Illuminating search spaces by mapping elites." arXiv:1504.04909. MAP-Elites mechanism reference for Rung 3. (In `docs/theory.md` "References to Obtain".)
- **Pugh, J., Soros, L., & Stanley, K. O. (2016).** "Quality Diversity: A new frontier for evolutionary computation." *Frontiers in Robotics and AI*. BC design discipline reference for Rung 3. (In `docs/theory.md` "References to Obtain".)
- **Hinton, G. & Nowlan, S. (1987).** "How learning can guide evolution." *Complex Systems* 1, 495-502. The classical Baldwin effect reference; the PASS-Baldwin row's theoretical anchor. (Already in `docs/theory.md`.)

## Source data

- **Prereg:** `Plans/prereg_v2-5-plasticity-1a.md`
- **Raw data directory:** `experiments/output/2026-04-19/v2_5_plasticity_1a/` (240 run dirs; `plasticity.csv`, `plasticity_summary.json`, per-run `result.json` + `final_population.npz`)
- **Analysis module:** `experiments/chem_tape/analyze_plasticity.py` (commit `feae431`; METRIC_DEFINITIONS dict therein)
- **Scratch pre-commitment:** `Plans/scratch_plasticity_1a_grid_extension_2026-04-19.md` (`cecfb58`, pre-n=20 analysis)
- **Chronicle (this diagnosis is referenced from):** `docs/chem-tape/experiments-v2.md` §v2.5-plasticity-1a
- **Direction doc:** `docs/chem-tape/runtime-plasticity-direction.md` (rank-1 → rank-2 fallback ladder; this diagnosis modifies the ladder per §29)
