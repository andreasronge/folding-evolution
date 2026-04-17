# Pre-registration: §v2.4-proxy-5a — `bond_protection_ratio` sweep on the BP_TOPK seeded cell (decoder-specific mechanism probe)

**Status:** QUEUED · target commit `TBD` · 2026-04-17 evening

## Supersession / upstream context

§v2.4-proxy-4d decode-consistent follow-up (commit `cca2323`) confirmed the decoder-specific mechanism split under the F/R dissociation. **BP_TOPK cells:** canonical off-center in a wide solver neutral network (R_fit ≈ 0.72 solvers; R₂_decoded ≈ 0.002 — decoded programs across the majority-solver cloud are structurally distinct from canonical). **Arm A:** classical proxy-basin population dynamics (R_fit ≈ 0.004; canonical elite-preserved only). Tournament selection is the common ingredient but is no longer a sufficient mechanism description per decoder. This prereg tests a **variation-layer** intervention under the BP_TOPK mechanism specifically: does raising `bond_protection_ratio` (bp) compress the decoded-solver cloud toward canonical, or is the cloud structurally stable under bp variation because the BP_TOPK decoder's many-to-one mapping creates the neutral network regardless of mutation pressure on bonded cells?

## Question (one sentence)

Under BP_TOPK(k=3) preserve on `sum_gt_10_AND_max_gt_5` natural sampler with `seed_fraction=0.01`, does raising `bond_protection_ratio` from the project default (0.5) toward strong protection (0.9) compress the post-1500-gen final population's decoded-view retention (`R₂_decoded`) toward canonical, maintain the current wide-solver-cloud structure with canonical off-center, or dissolve the cloud without compression?

## Hypothesis

§v2.4-proxy-4d's decode-consistent finding is that the BP_TOPK solver cloud is genuinely a wide neutral network of structurally distinct decoded programs, not an "ineffective code" variation around canonical. Two competing mechanism readings predict different bp sensitivities:

1. **Cliff-flattening reading.** Canonical's off-center position arises because canonical's 1-bit mutation neighbours in bonded cells fall off fitness plateau (cliff at fitness ≈ 0.87 proxy). Raising bp from 0.5 → 0.9 flattens that cliff by suppressing mutation in bonded cells; selection then pulls more of the decoded-solver cloud toward canonical's decoded form as that region becomes mutation-stable. **Prediction:** R₂_decoded lifts monotonically with bp.

2. **Decoder-structural reading.** The wide neutral network is a property of the BP_TOPK(k=3) many-to-one decode mapping itself — many genotypes concatenate top-3 runs into decoded programs that all solve the task. Canonical is one point; the network has structural genotype-space volume. Raising bp doesn't change the decoder's mapping structure; it only slows lateral drift *within* the network. **Prediction:** R₂_decoded insensitive to bp.

A third scenario is degenerate:

3. **Freezing artefact at bp=0.9.** At bp=0.9, mutation in bonded cells is nearly suppressed; the population freezes near initial conditions rather than exploring the neutral network. R₂_decoded may look lifted simply because 1% of init was canonical and the elite slots never drift — not because the cliff flattened. Ruled in by the degenerate-success guard (unique_genotypes collapse, extreme F dependence on sf).

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_4_proxy5a_bp_sweep.yaml`
- **Arms / conditions:** `bond_protection_ratio ∈ {0.5, 0.7, 0.9}` × `seed_fraction ∈ {0.0, 0.01}`. 3 × 2 = 6 cells. sf=0.0 is the drift-check per cell (anchored to §v2.4-proxy-4b/4c/4d Arm-0 pattern).
- **Seeds:** 0..19 per cell (disjoint ordering unchanged from 4b/4c/4d so paired-seed comparability is preserved).
- **Fixed params:** `arm=BP_TOPK`, `topk=3`, `safe_pop_mode=preserve`, `pop_size=1024`, `generations=1500`, `tournament_size=3`, `elite_count=2`, `mutation_rate=0.03`, `crossover_rate=0.7`, `tape_length=32`, `alphabet=v2_probe`, `disable_early_termination=true`, `dump_final_population=true`, `seed_tapes="0201121008010510100708110000000000000000000000000000000000000000"`, `n_examples=64`, `holdout_size=256`, `backend=mlx`. Only `bond_protection_ratio` and `seed_fraction` vary.
- **Est. compute:** 6 cells × 20 seeds × ~15 min/run ÷ 10 workers ≈ 30-45 min wall. Matches the §v2.4-proxy-4d sweep wall per cell within workers×rate.
- **Related experiments:** §v2.4-proxy-4b (bp=0.5 preserve baseline, commit `f10b066`), §v2.4-proxy-4c (bp=0.5 preserve replication, commit `9135345`), §v2.4-proxy-4d direct-active-view measurement (commit `a8a1e6d`), §v2.4-proxy-4d decode-consistent follow-up (commit `cca2323` — the per-cell R₂_decoded baseline this prereg is anchored against).

**Principle 20 audit:** label function, input distribution, and sampler unchanged from §v2.4-proxy-4b/4c/4d. Only `bond_protection_ratio` and `seed_fraction` vary across cells. Principle 20 not triggered.

**Principle 23 audit:** Arm 0 cells (`sf=0.0`) at each bp serve as drift checks. Principle 23 gate is straightforward — no mid-run changes planned; the bp=0.5 cells reproduce §v2.4-proxy-4d numbers exactly (baseline comparability check).

## Baseline measurement (required)

- **Baseline quantity at sf=0.01:** `R₂_decoded` (per §27 METRIC_DEFINITIONS in `experiments/chem_tape/analyze_retention.py`):
  > Fraction of final-population tapes whose BP_TOPK(k=topk) decoded view — the exact token sequence passed to the VM under arm=BP_TOPK, computed as the top-K longest non-separator runs concatenated in tape order via engine.compute_topk_runnable_mask — is within Levenshtein edit distance 2 of canonical's decoded view. For arm=A runs this view is informational (the VM executes the raw tape), not execution-semantic.
- **Value at bp=0.5 preserve (§v2.4-proxy-4d decode-consistent follow-up, commit `cca2323`):** `R₂_decoded = 0.0024` 95% CI `[0.0019, 0.0030]` at `seed_fraction=0.01` across n=20 seeds. This is the measured baseline this prereg lifts thresholds against, not an imported historical number.
- **Secondary anchor:** `R_fit_999` at bp=0.5 preserve = 0.723 (§v2.4-proxy-4d decode-consistent follow-up, commit `cca2323`). R_fit is a co-primary outcome axis per §26 below.
- **Drift-check expectation at sf=0.0 × bp=0.5:** F=0/20 (from §v2.4-proxy-4b/4c/4d; no solving without seed).

## Internal-control check (required)

- **Tightest internal contrast:** bp=0.5 vs bp=0.9 on the same seeds, same commit, same task. This is within the tested task family; no alphabet or sampler change.
- **Are you running it here?** Yes. bp=0.7 is the interpolation point testing monotonicity.

## Pre-registered outcomes (required — §26-compliant outcome grid across two primary axes + F sanity)

<!--
Per methodology §26: grid every measured axis at coarse bins. Axes measured per-seed at per-cell resolution:
  - R₂_decoded (primary; mechanism-level)
  - R_fit_999 (co-primary; decoder-level)
  - F_AND (solve rate; expected 20/20 under seeded init, sanity check)

Grid: (R₂_decoded coarse × R_fit coarse) with F as sanity; F drops trigger SWAMPED.
R₂_decoded coarse bins: {low < 0.05 | mid 0.05-0.3 | high ≥ 0.3}
R_fit coarse bins:      {below-baseline < 0.5 | baseline 0.5-0.8 | above-baseline > 0.8}

Baseline cell at bp=0.5 is (low, baseline) per §v2.4-proxy-4d numbers.
-->

Measured at `seed_fraction=0.01` per bp cell, n=20 seeds each, comparing to bp=0.5 baseline numbers above.

| outcome | R₂_decoded (cell vs bp=0.5) | R_fit_999 (cell vs bp=0.5 ≈ 0.72) | F_AND | interpretation |
|---|---|---|---|---|
| **PASS — cliff-flattening confirmed** | ≥ 0.3 at bp ∈ {0.7, 0.9} | any | 20/20 | Mechanism reading (1) confirmed: raising bp compresses the cloud toward canonical. Variation-layer intervention is the right lever; canonical's 1-bit mutation cliff is the load-bearing structural feature. |
| **PARTIAL — modest compression** | 0.05-0.3 at bp ∈ {0.7, 0.9} | any (drop to <0.8 or hold) | 20/20 | Some compression but cloud structure dominates; bp is informative but not sufficient. Suggests mixed mechanism (cliff + structural neutrality). |
| **FAIL — decoder-structural** | < 0.05 at bp ∈ {0.5, 0.7, 0.9} | 0.5-0.8 held across bp cells | 20/20 | Mechanism reading (2) confirmed: the BP_TOPK wide solver cloud is a property of the decoder's many-to-one mapping. Variation-layer intervention is the wrong lever. Points toward representation-level (e.g., evolvable chemistry / AutoMap) or selection-level (non-tournament) probes as the better directions. |
| **DISSOLVE — cloud collapse without canonical gain** | < 0.05 | R_fit drops to < 0.3 at high bp | 20/20 | Unusual outcome: bp disrupts the solver cloud without compressing it toward canonical (solvers disappear instead of concentrating). Mechanism reading: high bp destabilises the decoder's neutrality but canonical's basin is too narrow to capture the displaced mass. Implies a non-monotone relationship between mutation protection and solver retention. |
| **SWAMPED — bp pathological** | any | any | F < 18/20 at bp=0.9 | bp=0.9 suppresses mutation enough to break the search dynamic; F drops below the seeded-init expectation. Result uninformative for the mechanism question. Degenerate-success guard below specifies the unique_genotypes collapse condition that flags this prospectively. |
| **INCONCLUSIVE** | any pattern not fitting above | any pattern not fitting above | any | Outcome does not match a pre-registered row. Per principle 2b, adding the row (rather than post-hoc interpreting) is the correction. |

**Threshold justification:** the 0.05 floor matches the §v2.4-proxy-4b PARTIAL floor; the 0.3 PASS threshold matches 4b's PASS threshold. Both are preserved from the prior outcome grid so cross-sweep comparability is clean. R_fit bin boundaries (0.5, 0.8) bracket the measured bp=0.5 baseline (0.72) with enough margin to detect cell-level shifts without single-bootstrap-CI-width sensitivity.

## Degenerate-success guard (required)

- **Freezing artefact at bp=0.9 (mechanism reading 3):** at very high bp, mutation in bonded cells is nearly suppressed; population sits near initial conditions. R₂_decoded could lift trivially because 1% of init is canonical and elite slots freeze — not because any cliff-flattening happens.
- **Detection conditions (all three must pass to avoid SWAMPED):**
  1. `unique_genotypes` at bp=0.9 must exceed 800/1024 (baseline 987/1024 at bp=0.5); drop below this signals population freezing.
  2. `F_AND` at bp=0.9 × sf=0.01 must be ≥ 18/20; drops signal the GA is no longer converging productively.
  3. `R₀_decoded` at bp=0.9 × sf=0.0 (drift check) must be < 0.05; a drift-check spike signals canonical-like genotypes are arising randomly rather than via the mechanism, invalidating the sf=0.01 comparison.
- **Zero-retention artefact (`R₂_decoded = 0` while best-of-run canonical is preserved):** per §v2.4-proxy-4d's analogous check, R₀_decoded > 0 (≈ 0.002 for 2 elite slots) is the sanity condition indicating the `final_population.npz` dump captured at least the elite — a value of 0.000 would flag an infrastructure bug.
- **Off-plateau canonical shell artefact:** if R₂_decoded lifts specifically at bp=0.7 but falls at bp=0.9, that is a non-monotone signature. Interpretation is `DISSOLVE` (above), not PASS — the cliff-flattening reading would predict monotonic lift with bp.

## Statistical test

- **Primary:** per-cell bootstrap 95% CI on `R₂_decoded` (per §27 METRIC_DEFINITIONS `bootstrap_ci_spec`):
  > Nonparametric bootstrap over per-seed values: 10 000 resamples with replacement via numpy.random.default_rng(seed=42); 95% CI is the [2.5%, 97.5%] empirical quantile of the resampled means.
  95% CIs on `R_fit_999` and `R₂_active` reported alongside.
- **Secondary:** paired McNemar on solve count `F_AND` across bp values on shared seeds — gates the SWAMPED row if any bp cell differs from bp=0.5 at α=0.05 raw.
- **Classification (principle 22):** **exploratory.** This prereg does not gate a new findings.md claim; it informs the mechanism reading already ACTIVE in `findings.md#proxy-basin-attractor` under the decoder-specific narrowing. The confirmatory test for the proxy-basin family is §v2.4-proxy-4b's McNemar (p<0.0001), unchanged by this sweep.
- **Family:** n/a (exploratory). Does not grow the proxy-basin FWER family; corrected α for the family stays at 0.05 / 3 ≈ 0.017.

## Diagnostics to log (beyond fitness)

- Per-seed × per-cell `F_AND`, `best-of-run` fitness (expected 20/20 and 1.0 respectively at sf=0.01)
- Per-cell `R₂_decoded`, `R₂_active`, `R₂_raw`, `R_fit_999`, `unique_genotypes`, `final_generation_mean` (via `analyze_retention.py`)
- Edit-distance histogram `{0, 1, 2, 3, ≥4}` active-view per cell (existing output format)
- Per-cell bootstrap 95% CI on all three R₂ views (via existing `analyze_retention.py` path with `--out` redirection for per-sweep output)
- Per-seed best-of-run hex at sf=0.01 — confirm byte-for-byte canonical across all 60 seeded runs (matches §v2.4-proxy-4b/4c/4d attractor-category pattern; deviation flags degenerate-success guard)

## Scope tag (required for any summary-level claim)

**If this experiment's result enters a findings.md narrowing:**
`within-family · n=20 per cell (6 cells) · at BP_TOPK(k=3) preserve v2_probe pop=1024 gens=1500 tournament_size=3 elite_count=2 mutation_rate=0.03 disable_early_termination=true · on sum_gt_10_AND_max_gt_5 natural sampler seeded canonical 12-token AND body · bond_protection_ratio ∈ {0.5, 0.7, 0.9}`.

Not expected to broaden the top-line `proxy-basin-attractor` claim — this probe narrows the mechanism reading within the already-tested family.

## Decision rule

- **PASS — cliff-flattening →** update `findings.md#proxy-basin-attractor` mechanism-reading naming history to note that the BP_TOPK wide-solver-cloud compression under bp=0.9 supports a mutation-cliff component of the mechanism. Add scope boundary "bp-dependent compression" and queue a fresh confirmatory test on an independent seed block (20-39) before paper-level citation. Tier-2 "repair operator" becomes lower-priority (bp already does the work).
- **PARTIAL →** note modest compression in the arc doc + findings.md narrowing entry, but do NOT broaden scope. Keep the decoder-structural reading as co-active. Queue the non-tournament-selection probe and mutation_rate sweep (§v2.4-proxy-5b) in parallel; either could complete the mechanism.
- **FAIL — decoder-structural →** update arc doc's Open Q #2 to closed; move "variation-layer interventions for BP_TOPK" to the known-failure-modes list in the arc. The decoded-solver network is structurally determined; Part-1 meta-learning direction should prioritise representation-level (decoder-evolution) over operator-level interventions for BP_TOPK. Mutation_rate sweep (§v2.4-proxy-5b) retains informational value only on Arm A.
- **DISSOLVE →** unexpected; stop and inspect. Do not apply any findings-layer update until genotype inspection confirms the mechanism. Likely requires a follow-up mid-bp sweep (e.g., bp ∈ {0.6, 0.65, 0.75, 0.85}) to localise the non-monotonicity.
- **SWAMPED →** degenerate measurement; no mechanism claim. Note the bp ceiling in the chronicle. Repeat at `bond_protection_ratio=0.8` if the bp=0.9 cell was uniquely pathological.
- **INCONCLUSIVE →** the outcome grid missed a cell. Per principle 2b, update the grid *then* re-interpret. Do not narrate the missing cell as a result.

---

*Audit trail.* Six outcome rows (principle 2 + 2b). §v2.4-proxy-4d decode-consistent follow-up numbers are the measured baseline (principle 6). Internal control is bp=0.5 vs bp=0.9 on the same seeds (principle 1). Degenerate-success guard includes the freezing artefact explicitly (principle 4). Principle 20 not triggered. Principle 22 classified as exploratory; does not grow the proxy-basin FWER family. Principle 23 gate preserved — sf=0.0 drift checks in each cell and paired-seed comparability with prior 4b/4c/4d runs. Principle 25 satisfied — all three R₂ columns + R_fit_999 are produced by `experiments/chem_tape/analyze_retention.py` (entries cited verbatim from the module's `METRIC_DEFINITIONS` dict per principle 27). Principle 26 satisfied — R_fit_999 is gridded at 3 coarse bins alongside R₂_decoded rather than demoted to diagnostic-only. Decision rule commits to specific arc-doc / findings-layer edits per outcome (principle 19).
