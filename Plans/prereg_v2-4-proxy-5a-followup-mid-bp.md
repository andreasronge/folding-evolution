# Pre-registration: §v2.4-proxy-5a-followup-mid-bp — mid-range bond_protection_ratio localisation sweep

**Status:** QUEUED · target commit `4aa8b40` · 2026-04-18

## Question (one sentence)

Does R_fit_999 drop monotonically across the full bp range (0.5, 0.9), or does it threshold at a specific bp value in {0.60, 0.65, 0.75, 0.85}?

## Hypothesis

§v2.4-proxy-5a (commit `c3bd8eb`) found R_fit_999 collapsed monotonically from 0.723 → 0.375 → 0.177 as bp rose from 0.5 → 0.7 → 0.9, but the three anchor points were too coarse to distinguish a smooth continuous decay from a threshold transition. The DISSOLVE decision rule for §v2.4-proxy-5a explicitly required a mid-bp localisation sweep. Two competing hypotheses are:

1. **MONOTONE reading.** Cloud destabilisation is a smooth function of bp — each additional unit of bond protection erodes solver-cloud occupancy proportionally. No cliff or plateau. The 5a coarse grid happened to sample three points on a smooth decay curve.

2. **THRESHOLD reading.** There is a structural threshold somewhere in (0.5, 0.9) at which the decoder's many-to-one neutral network destabilises. Below the threshold R_fit holds near the 5a bp=0.5 baseline (0.72); above it R_fit collapses. The 5a grid sampled below-threshold (bp=0.5) and above-threshold (bp=0.7, 0.9) without localising the threshold. The threshold-low and threshold-high sub-hypotheses differ in where the cliff sits.

Additionally, §v2.4-proxy-5a found unseeded discovery (1/20 non-canonical solver at sf=0.0) at bp=0.7 and bp=0.9 but 0/20 at bp=0.5. This discovery axis may also threshold or rise smoothly with bp.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_4_proxy5a_mid_bp.yaml`
- **Arms / conditions:** `bond_protection_ratio ∈ {0.60, 0.65, 0.75, 0.85}` × `seed_fraction ∈ {0.0, 0.01}`. 4 × 2 = 8 cells. sf=0.0 is the drift/discovery check; sf=0.01 is the seeded-init arm that produced the 5a R_fit numbers.
- **Seeds:** 0..19 (identical seed block as §v2.4-proxy-5a for paired-seed comparability).
- **Fixed params:** `arm=BP_TOPK`, `topk=3`, `safe_pop_mode=preserve`, `pop_size=1024`, `generations=1500`, `tournament_size=3`, `elite_count=2`, `mutation_rate=0.03`, `crossover_rate=0.7`, `tape_length=32`, `alphabet=v2_probe`, `task=sum_gt_10_AND_max_gt_5`, `disable_early_termination=true`, `dump_final_population=true`, `seed_tapes="0201121008010510100708110000000000000000000000000000000000000000"`, `n_examples=64`, `holdout_size=256`, `backend=mlx`. Only `bond_protection_ratio` and `seed_fraction` vary.
- **Decoder arm:** BP_TOPK(k=3) preserve only (same as §v2.4-proxy-5a).
- **Est. compute:** 8 cells × 20 seeds = 160 runs ÷ 10 workers ≈ 45 min wall.
- **Related experiments:** §v2.4-proxy-5a (DISSOLVE result, commit `c3bd8eb`) — this sweep fills the mid-bp gap mandated by the 5a decision rule.

**Principle 20 audit:** label function, input distribution, and sampler unchanged from §v2.4-proxy-5a. Only `bond_protection_ratio` and `seed_fraction` vary. Principle 20 not triggered.

## Baseline measurement (required)

- **Baseline quantity:** `R_fit_999` — fraction of final population with fitness ≥ 0.999, per `analyze_5ab.py` (`R_fit_999_mean` column), which aggregates `analyze_retention.py`'s per-run R_fit field.
- **Measurement:** same analysis pipeline as §v2.4-proxy-5a; `analyze_5ab.py <sweep_dir> bp` grouped by `(bond_protection_ratio, seed_fraction)`.
- **Anchors from §v2.4-proxy-5a (commit `c3bd8eb`):**

  | bp | R_fit_999 | R₂_decoded | unseeded discoveries |
  |---|---|---|---|
  | 0.5 | 0.723 | 0.0024 | 0/20 |
  | 0.7 | 0.375 | 0.0046 | 1/20 |
  | 0.9 | 0.177 | 0.0045 | 1/20 |

  The bp=0.5 cell R_fit_999=0.723 is the baseline that new cells are read against. Thresholds below reference this value, not absolute numbers from other experiments.

- **Secondary:** R₂_decoded per cell (expected to remain near 0.004 across the mid-bp range per §v2.4-proxy-5a's flat pattern).

## Internal-control check (required)

- **Tightest internal contrast:** bp=0.60 vs bp=0.85 on the same seeds, same task, same commit. These bracket the range while being within-family.
- **Are you running it here?** Yes — all four bp cells share seeds 0..19 and run in a single sweep, enabling pairwise within-sweep contrast.

## Pre-registered outcomes (required — §26-compliant grid)

<!--
Axes measured per-seed at per-cell resolution:
  - R_fit_999 (primary; collapse-profile axis) — coarse bins: {near-baseline ≥ 0.6 | mid 0.3-0.6 | collapsed < 0.3}
  - Unseeded discovery rate at sf=0.0 (secondary; monotone vs step) — coarse bins: {none 0/20 | low 1/20 | elevated ≥ 2/20}

Grid: R_fit_999 monotonicity pattern (shape across the 4 bp cells, not per-cell bin) × discovery trend.
Because the primary question is about the shape of the R_fit_999 profile across bp cells (monotone vs threshold), the grid rows encode the profile shape, with discovery trend as a secondary annotation.

Per §26: the discovery rate axis is measured at per-seed resolution and must be gridded or explicitly demoted. It is demoted here to effect-size-only (no p-value gate) with the explicit reason: n=20 per cell gives expected counts of 0-2 events; binomial CIs on discovery rate would be too wide (0/20 CI [0, 0.17]) to classify a within-sweep step vs monotone trend at the required resolution. The primary mechanism question is on R_fit_999 shape; discovery rate is logged for hypothesis generation. Demotion is explicit per principle 26 — this is not silent diagnostic demotion.
-->

Measured at `seed_fraction=0.01` per bp cell, n=20 seeds each, comparing to 5a anchors above.

| outcome | R_fit_999 profile across bp ∈ {0.60, 0.65, 0.75, 0.85} | interpretation | decision rule |
|---|---|---|---|
| **MONOTONE** | R_fit_999 decreases monotonically at every step from 0.60 → 0.65 → 0.75 → 0.85; no plateau (no two adjacent cells within 0.05 of each other), all cells below 0.6 | Cloud destabilisation is a smooth function of bp; no structural threshold. The 5a three-point coarse grid correctly characterised the trend. | findings.md #proxy-basin-attractor: add "smooth collapse" qualifier to the bp destabilisation note. No attractor-mechanism threshold to localise. |
| **THRESHOLD-LOW** | R_fit_999 ≥ 0.60 at bp ∈ {0.60, 0.65}, then drops below 0.4 at bp ∈ {0.75, 0.85} | A structural threshold near bp ≈ 0.70; below it the solver cloud is stable, above it it destabilises. §v2.4-proxy-5a's bp=0.7 result (0.375) was already post-threshold. | findings.md: record threshold near bp=0.70. Queue targeted n=40 replication at bp=0.70 on independent seeds 20-59. |
| **THRESHOLD-HIGH** | R_fit_999 ≥ 0.60 at bp ∈ {0.60, 0.65, 0.75}, then drops below 0.4 at bp=0.85 only | Threshold near bp=0.85; §v2.4-proxy-5a's bp=0.9 was just over the edge. bp=0.7 was a degraded-but-not-collapsed regime. | findings.md: record threshold near bp=0.85. Queue targeted n=40 replication at bp=0.85 on independent seeds 20-59. |
| **PLATEAU-MID** | R_fit_999 stabilises in the range [0.3, 0.6] across two or more adjacent bp cells (adjacent-cell difference < 0.05 within the plateau band) | Non-monotone staircase: two regimes or two competing mechanisms. Expected two mechanisms: (a) structural neutrality compression dominant at low bp, (b) freeze artefact dominant at high bp. | Unexpected. Stop and inspect. Genotype inspection of the two plateau-edge populations required before any findings-layer update. Queue a winner-tape decode across the plateau cells to identify attractor-category shifts. |
| **INCONCLUSIVE** | Profile does not match any row above (e.g., non-monotone oscillation, single-cell outlier that breaks the pattern) | Outcome grid missed a cell; per principle 2b, update the grid then re-interpret. | Per principle 2b: characterise the unexpected cell, draft the missing row, re-interpret. Do not narrate the missing cell as a result. |

**Threshold justification:** the 0.60 near-baseline floor is 5a baseline (0.723) minus a 0.12 margin — tight enough to distinguish stable from degraded. The 0.4 collapse ceiling is midway between §v2.4-proxy-5a's bp=0.7 result (0.375) and the baseline; below it signals the cloud is operating in the 5a-DISSOLVE regime. The 0.3–0.6 plateau band for PLATEAU-MID is the same range as the 5a observed values (0.177 low, 0.375 mid, 0.723 baseline), bounded to avoid overlap with MONOTONE (where cells continue falling) and INCONCLUSIVE (where the pattern is non-structured).

**Discovery-rate secondary axis (effect-size-only, no outcome-table row, explicitly demoted per §26):** log the sf=0.0 solve count per bp cell. If any cell produces ≥2/20 unseeded discoveries, flag for attractor-category inspection. Trend direction (monotone vs step) is hypothesis-generating only; n=20 gives binomial CIs too wide to classify reliably. Report as a table alongside the primary grid output.

## Degenerate-success guard (required)

- **Freeze artefact at high bp (inherited from §v2.4-proxy-5a):** at bp=0.85, mutation in bonded cells is heavily suppressed. R_fit may appear stable relative to bp=0.75 not because there is a plateau but because the population freezes near the seeded canonical body. Detection: `unique_genotypes` at bp=0.85 × sf=0.01 must remain above 800/1024 (baseline ~987 at bp=0.5). Drop below 800 flags freeze; that cell is demoted to SWAMPED and excluded from the profile.
- **Spontaneous solver at sf=0.0 inflating discovery count:** the 1/20 unseeded discoveries at 5a's bp=0.7 and bp=0.9 were non-canonical bodies. At the mid-bp range, any sf=0.0 "discovery" must be inspected with `decode_winner.py` to confirm it is a genuine non-canonical solver and not a canonical-equivalent body that scores ≥0.999 only on the holdout distribution. Discovery count reported only after inspection.
- **MONOTONE-trivial artefact:** if all four mid-bp cells show R_fit < 0.3 (all collapsed), the profile is technically monotone but the cells contain no information beyond "bp ≥ 0.60 collapses the cloud." This signals §v2.4-proxy-5a's threshold was below bp=0.60, not within the mid-bp sweep range. Report as INCONCLUSIVE-BELOW-SWEEP-RANGE.

## Statistical test (if comparing conditions)

- **Primary:** per-cell bootstrap 95% CI on `R_fit_999` via `analyze_5ab.py` (same bootstrap_ci routine as §v2.4-proxy-5a, 10 000 resamples, numpy.random.default_rng(seed=42)). CIs reported for each of the 4 mid-bp cells plus the 3 anchored 5a cells for visual comparison.
- **Profile shape classification:** Monotone is declared when adjacent-cell R_fit differences are all in the same direction and no plateau (adjacent-cell difference < 0.05) exists. Threshold is declared when ≥2 consecutive cells at low bp are within 0.12 of the baseline and the remaining cells are below 0.4. These are decision rules, not formal statistical tests.
- **Classification (principle 22):** **exploratory.** This sweep localises the collapse profile to inform findings.md wording and follow-up targeting; it does not gate a new findings.md claim nor add a confirmatory test to the proxy-basin FWER family. The corrected α for the proxy-basin family stays at 0.05 / 3 ≈ 0.017, unchanged.
- **Family (if confirmatory):** n/a — exploratory.

## Diagnostics to log (beyond fitness)

- Per-cell `R_fit_999_mean` and 95% CI (primary outcome axis, from `analyze_5ab.py bp`)
- Per-cell `R₂_decoded_mean` and 95% CI (expected flat ~0.004; deviation flags mechanism shift)
- Per-cell `unique_genotypes_mean` (freeze-artefact guard; must remain >800 at high bp)
- Per-cell `solve_count` at sf=0.0 (unseeded discovery tally, effect-size-only)
- Per-cell `final_mean_fitness_mean` (sanity; expected near 0.999 at sf=0.01 under seeded init)
- Winner-tape decode at sf=0.0 for any cell with solve_count ≥ 1 (via `decode_winner.py`), to confirm non-canonical and rule out holdout-only solver
- Analysis command: `python experiments/chem_tape/analyze_5ab.py <sweep_dir> bp`

## Measurement-infrastructure gate (principle 25)

| metric | state | producing code |
|---|---|---|
| R_fit_999 | produced directly | `analyze_5ab.py` → `analyze_retention.py:R_fit_999` (fraction of final-pop tapes with VM fitness ≥ 0.999, via `dump_final_population=true` in sweep config) |
| R₂_decoded | produced directly | `analyze_5ab.py` → `analyze_retention.py:R2_decoded` (fraction of final-pop tapes with BP_TOPK decoded view within edit-distance 2 of canonical, per `METRIC_DEFINITIONS["R2_decoded"]`) |
| unique_genotypes | produced directly | `analyze_5ab.py` → `analyze_retention.py:unique_genotypes` |
| unseeded discovery rate | produced as labeled proxy | `analyze_5ab.py:solve_count` at `seed_fraction=0.0` counts seeds where `best_fitness ≥ 0.999`. This is an **upper bound** on genuine non-canonical discoveries — some may be canonical-equivalent. The actual non-canonical count requires `decode_winner.py` inspection per detected solver. The proxy is informative as a screen; the actual rate is confirmed by inspection. |

## Scope tag (required for any summary-level claim)

**If this experiment's result enters a findings.md update:**
`within-family · n=20 per cell (4 mid-bp cells + 3 anchored 5a cells) · at BP_TOPK(k=3) preserve v2_probe pop=1024 gens=1500 tournament_size=3 elite_count=2 mutation_rate=0.03 disable_early_termination=true · on sum_gt_10_AND_max_gt_5 natural sampler seeded canonical 12-token AND body · bond_protection_ratio ∈ {0.60, 0.65, 0.75, 0.85}`

This sweep narrows the §v2.4-proxy-5a DISSOLVE finding to a profile shape (smooth vs threshold). It does not broaden the proxy-basin-attractor claim.

## Decision rule

- **MONOTONE →** update `findings.md#proxy-basin-attractor` bp-destabilisation note: "collapse is smooth and continuous across bp, not threshold-mediated." No threshold follow-up needed. Close the localisation question.
- **THRESHOLD-LOW →** findings.md: record threshold near bp=0.70. Queue n=40 targeted replication at bp=0.70 on seeds 20-59. This is a genuine structural threshold localisation — a narrowing of the DISSOLVE finding.
- **THRESHOLD-HIGH →** findings.md: record threshold near bp=0.85. Queue n=40 targeted replication at bp=0.85 on seeds 20-59.
- **PLATEAU-MID →** unexpected. Do not write any findings-layer update. Inspect plateau-edge populations genotype-by-genotype (zero-compute per principle 3) to identify mechanism shift. Draft a narrowed follow-up prereg based on inspection findings.
- **INCONCLUSIVE →** characterise the unexpected cell. Update the outcome grid in a new prereg commit. Do not interpret the missing cell post-hoc.

---

*Audit trail.* Five outcome rows (principle 2 + 2b). §v2.4-proxy-5a measured numbers are the baseline (principle 6). Internal control is bp=0.60 vs bp=0.85 on the same seeds (principle 1). Degenerate-success guard names three specific artefacts with detection conditions (principle 4). Principle 20 not triggered. Principle 22: classified as exploratory; does not grow the proxy-basin FWER family (corrected α unchanged at 0.05/3 ≈ 0.017). Principle 25: all four metrics have infrastructure state labels; unseeded discovery rate is explicitly labeled as upper-bound proxy requiring inspection confirmation (not silent). Principle 26: discovery-rate secondary axis explicitly demoted to effect-size-only with cited reason (n=20 binomial CIs too wide for profile classification) — not silent demotion. Decision rule commits to specific follow-up per outcome (principle 19).
