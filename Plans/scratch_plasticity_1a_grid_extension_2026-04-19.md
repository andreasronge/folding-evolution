# Scratch · candidate grid-miss row for §v2.5-plasticity-1a (dated pre-n=20)

**Status:** PROVISIONAL / NOT A PREREG AMENDMENT. Drafted 2026-04-19, during the §v2.5-plasticity-1a relaunch (157/240 runs completed on first pass → relaunch to finish the remaining 83). Partial data at n=13 per cell motivates this row; the extension must not be merged into the prereg until n=20 lands and the pattern replicates. Principle 2b: update the grid *before* interpreting — this doc is the pre-commitment.

**Source data:** `/tmp/plasticity_1a_partial_n13/plasticity.csv`, `/tmp/plasticity_1a_partial_n13/interim_report.txt` (2026-04-19).

---

## Observation (n=13 partial, Arm A plastic cells, sf=0.01)

| budget | n  | R_fit_frozen | R_fit_plastic | ΔR     | Baldwin_slope | CI95               | δ_mean | δ_std |
|-------:|---:|-------------:|--------------:|-------:|--------------:|:-------------------|-------:|------:|
| 1      | 14 | 0.201        | 0.201         | +0.000 | +0.0147       | [+0.003, +0.040]   | −0.25  | 0.70  |
| 2      | 14 | 0.075        | 0.091         | +0.016 | +0.0241       | [+0.019, +0.036]   | −0.33  | 1.01  |
| 3      | 14 | 0.065        | 0.066         | +0.001 | +0.0466       | [+0.032, +0.085]   | −1.34  | 1.68  |
| 5      | 14 | 0.091        | 0.092         | +0.002 | +0.0756       | [+0.060, +0.145]   | −2.72  | 2.69  |

Three simultaneous signals:

1. **Baldwin slope sign-inverted.** Positive, monotone in budget, CI excludes 0 at every budget ≥ 1.
2. **No population-layer uplift.** ΔR ≈ 0 (max +0.016 at budget=2). Far below the prereg's +0.1 "large uplift" bin.
3. **δ_std grows with budget.** Counter to universal-adapter (which would have δ collapsing to a point). Genotypes find *different* δs, and the diversity expands as adaptation budget grows.

Additional:
* `GT_bypass_fraction` = 0.00–0.01 across all cells → Baldwin regression runs on essentially the full population; the `INCONCLUSIVE — GT-bypass majority` row is retired for this sweep.
* Mean δ drifts negative and grows in magnitude with budget (−0.25 → −2.72).

## Why this doesn't fit the existing grid

| existing row                          | why this pattern fails it                             |
|--------------------------------------|-------------------------------------------------------|
| **PASS — Baldwin**                   | slope wrong sign (positive)                           |
| **PARTIAL — universal adapter**      | CI excludes 0 (not flat); δ_std grows with budget (counter-signature) |
| **FAIL — weak plasticity**           | CI excludes 0 with nonzero magnitude (plasticity *is* doing something) |
| **INCONCLUSIVE — frozen wins**       | needs ΔR < −0.1; observed ΔR ≈ 0                      |
| **INCONCLUSIVE — mid F_test**        | F_AND_train = 14/14 at sf=0.01 (strong)               |
| **INCONCLUSIVE — GT-bypass majority**| GT_bypass_fraction = 0.01                             |

Classified as **INCONCLUSIVE (grid-miss)** per principle 2b. Candidate new row below.

## Candidate new row — **INVERSE-BALDWIN (tail-adapter)**

**Definition.** Positive Baldwin_slope with 95% CI excluding 0, AND ΔR (R_fit_plastic − R_fit_frozen) within [−0.05, +0.05], AND δ_std increasing monotone with budget.

**Mechanistic hypothesis.** Selection drives the population toward near-canonical genotypes (small Hamming to canonical), which already solve train near-perfectly at δ=0. Plasticity cannot help these individuals — their frozen test fitness is already at the top of their capacity. The *uplift* is realised only in the distant tail of the population, where δ compensates for off-canonical thresholds. Because most of the population is near-canonical (gap ≈ 0) and only the tail gets gap > 0, the regression of gap on Hamming distance produces a **positive** slope. The population-mean R_fit does not move because the tail is a small fraction.

**Contrast with Baldwin.** Classical Baldwin: evolved genotype is already *close* to the learnable solution; plasticity refines a real circuit. Slope negative because closer-to-canonical ⇒ more learnable. Here: evolved genotype is *already the solution*; plasticity is stuck helping the stragglers, not refining the winners. No mechanism-level support for the "genotype encodes learnable circuit" claim.

**Contrast with universal adapter.** Universal adapter: δ does all the work, genotype irrelevant, δ_std collapses. Here: δ does *some* work only for the tail, genotype matters (near-canonical ignores δ), δ_std *grows* as budget permits per-genotype optimal δ to diverge. Opposite in δ-space.

**Reading.** Plasticity is a **load-bearing adaptation for distant genotypes only**. The evolutionary signal (selection on train_plastic fitness) is preserved but weakened: near-canonical already wins pre-plasticity, so plasticity adds no selection edge. Does NOT support the `plasticity-narrow-plateau` candidate finding — it shows plasticity helps where it was least needed (the tail), not where the prereg hypothesised (the near-canonical majority that should have been on a ramp to canonical).

## Promotion / demotion decision at n=20

**If n=20 confirms the pattern** (positive slope, CI still excludes 0, ΔR still ≈ 0, δ_std still grows with budget):

* Do NOT promote `plasticity-narrow-plateau` to findings.md as a Baldwin claim.
* Record as a **NEGATIVE finding against the classical Baldwin hypothesis on this task**, with the inverse-Baldwin pattern as a secondary descriptive observation.
* The FWER family `plasticity-narrow-plateau` opens at size 1 with corrected α=0.05 and the confirmatory test *fails* (slope sign wrong). Family remains open; future plasticity probes (rank-2 memory, different tasks) continue to draw from it.
* **Diagnosis check before escalation (Risi & Stanley 2010).** Inverse-Baldwin with δ_std growing + F_AND_train pinned at ceiling is the structural signature of **selection-deception** ("deception of learning-to-learn"): static-canonical shortcuts satisfy selection before plasticity has any work to do, so the learning-rule gradient dries up regardless of mechanism capacity. Rank-2 memory is the fix for *mechanism-weakness*, not *selection-deception*. Distinguishing test:
  - If δ_std scales with budget AND F_AND_train saturates AND GT_bypass_fraction < 0.10 → **selection-deception diagnosis**, rank-2 likely wasted compute.
  - If δ_std *does not* scale with budget AND tail-bins show no uplift → **mechanism-weak diagnosis**, rank-2 is the right escalation.
  - Apply this diagnostic at n=20 before queuing any follow-up sweep.
* **Escalation branches by diagnosis:**
  - **Mechanism-weak branch.** Try rank-2 memory per the plasticity-direction doc's fallback ladder (§v2.5-plasticity-1b).
  - **Selection-deception branch.** Break the static-canonical attractor by changing the *selection regime*, not the plasticity mechanism. Ladder of escalation:
    1. **Evolvability-ES variant first** (no BC commitment needed). Rewards offspring-variance diversity; cheapest to try; surfaces committed-plastic lineages without pre-registration-grade BC design.
    2. **Novelty search or MAP-Elites with a plastic-adaptation BC** if EES's diffuse signal is insufficient. Candidate BCs (must pre-register per methodology §25 / §27 before any sweep):
       - `adaptation_delta_BC`: `test_fitness_plastic − test_fitness_frozen` across a parametric task family (`THRESHOLD(k)` for k ∈ {3, 5, 7, 10, 12}). Directly rewards genotypes where plasticity does measurable work; collapses inverse-Baldwin by construction.
       - `parametric_output_vector_BC`: 5-element binary output on `THRESHOLD(k)` above. Rewards genotypes that respond differently to k. More expressive but noisier.
       - `operator_frequency_histogram_BC`: structural; cheap but likely underpowered (doesn't distinguish static-wins-with-different-ops from plastic-wins).
    3. **Remove the seed (sf=0.0 confirmatory)** as a minimal-engineering check. If plasticity signal emerges without the canonical seed blocking it, the selection-deception diagnosis is corroborated.
  - **BC pre-registration is load-bearing.** Risi & Stanley flag explicitly: "novelty search's power is entirely determined by the BC — a poorly chosen characteristic trades one deception for meaningless exploration." The BC itself must live in code with a METRIC_DEFINITIONS entry and parity tests before the sweep runs (same discipline as the current Baldwin_slope machinery). No novelty-search sweep launches until the BC prereg lands.

**If n=20 narrows the pattern** (slope drops toward 0, CI widens to include 0):

* Reclassify as `PARTIAL — universal adapter` *if* δ_std stops growing with budget (or shrinks). The extra seeds may have diluted a small-n artifact.
* If δ_std keeps growing while slope flattens, the pattern is `FAIL — weak plasticity` on the population layer with no clear Baldwin or universal-adapter signature.

**If n=20 flips the pattern** (slope negative, CI excludes 0):

* Original PASS — Baldwin row fires. The positive-slope signal at n=13 was a small-n artifact. This is the low-probability branch but possible; n=13 bootstrap CIs can be misleading on per-individual regressions.

## What this scratch doc is NOT

* NOT a prereg amendment. Do not cite it in findings.md. Do not reference it in the chronicle when the sweep lands.
* NOT a claim. The inverse-Baldwin pattern is a partial-N observation with no CI discipline applied at the sweep level yet.
* NOT an escape hatch from the principle-22 family commitment. The original confirmatory test (Baldwin_slope negative, CI excludes 0) is what was pre-registered and is what the n=20 result is judged against. A grid-miss means "none of the pre-registered rows fire cleanly" — it does not grant license to retroactively define a row that fits the data.

## What to do after n=20 lands (checklist)

1. Re-run `analyze_plasticity.py` on the complete sweep.
2. Check whether the partial-N pattern replicates (sign, magnitude, CI, δ_std growth).
3. IF it replicates:
   - File a prereg amendment note adding INVERSE-BALDWIN as a formally enumerated grid row, *dated as provisional on 2026-04-19*, with this scratch doc as the source.
   - Classify the cell outcome per the rules above (likely NEGATIVE finding, no findings.md promotion).
4. IF it does not replicate:
   - Delete/archive this scratch doc (with a note recording what the n=13 signal turned out to be).
   - Proceed with whichever pre-registered row fires at n=20.

## Files

* Interim report: `/tmp/plasticity_1a_partial_n13/interim_report.txt`
* Partial CSV: `/tmp/plasticity_1a_partial_n13/plasticity.csv`
* Partial summary JSON: `/tmp/plasticity_1a_partial_n13/plasticity_summary.json`
* Source prereg: `Plans/prereg_v2-5-plasticity-1a.md`
* Direction doc: `docs/chem-tape/runtime-plasticity-direction.md`

## References cited in the diagnosis / escalation logic

* **Risi, S. & Stanley, K.O. (2010).** "Evolving Plastic Neural Networks with Novelty Search." *Adaptive Behavior* 18(6), 470–491. Identifies *deception of learning-to-learn*: static domain-specific heuristics are easier evolutionary targets than plastic learning rules; objective-driven evolution finds static first and never commits to plasticity. This is structurally the pattern the n=13 partial data exhibits under the inverse-Baldwin reading. Escape route: novelty search on a plasticity-sensitive BC. Caveat: BC power determines search power; a poorly chosen BC trades one deception for meaningless exploration.
* **Evolvability ES** (general framework): alternative instantiation of the same anti-deception principle; selects for offspring-variance diversity rather than behavioral diversity. BC-free — cheaper first rung on the selection-deception escalation ladder.
