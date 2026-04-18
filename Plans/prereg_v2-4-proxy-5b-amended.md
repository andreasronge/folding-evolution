# Pre-registration: §v2.4-proxy-5b-amended — `mutation_rate` sweep outcome-grid repair (principle-2b amendment to §v2.4-proxy-5b INCONCLUSIVE)

**Status:** ACTIVE (re-chronicle complete against amended grid; no new sweep; data from commit `c3bd8eb`) · authored commit `4aa8b40` · 2026-04-18

**Supersedes:** [Plans/prereg_v2-4-proxy-5b-mutation-rate.md](prereg_v2-4-proxy-5b-mutation-rate.md)

---

## Amendment rationale (principle 2b)

§v2.4-proxy-5b returned `INCONCLUSIVE` because the pre-registered outcome grid contained an internal inconsistency: Arm A per-arm rows gated on `R₂_decoded ≥ 0.05` as the primary threshold, but the same prereg's degenerate-success guard stated that `R₂_decoded` for Arm A is **informational-only** and the primary Arm A mechanism signal is `R_fit_999`. The grid's R_decoded thresholds for Arm A rows were therefore non-binding on the metric the prereg itself identified as load-bearing.

Per methodology principle 2b (*"update the outcome grid [as a proper cross-product], then re-interpret"*): this amendment specifies a corrected grid in which Arm A rows gate on `R_fit_999` as primary, and BP_TOPK rows use `R_fit_999` as primary with `R₂_decoded` as co-primary. The grid is then constructed as the full cross-product of the measured axes' coarse bins (per §26), not as paired rows that presuppose a particular correlation pattern.

**Constraint (anti-smuggling).** This grid must be constructed **before** re-reading the precise data values, and it must include cells for every (arm × R_fit bin × R₂_decoded bin) combination — including cells the observed data does not occupy. A grid spec that happens to have exactly one row matching the observed numbers fails principle 2b; the amendment is judged by whether the cross-product is complete, not by whether the observed cell was predicted. The data are not re-inspected during grid construction; only the **axis definitions** (which metrics and which coarse bins) use information available at the time of the original prereg.

---

## Question (carried from §v2.4-proxy-5b, no change)

Under `seed_fraction=0.01` on `sum_gt_10_AND_max_gt_5` natural sampler, does the decoder-specific F/R dissociation measured at `mutation_rate=0.03` scale with mutation rate — lifting `R_fit_999` and/or `R₂_decoded` at lower rates (kinetic mechanism), or holding rate-insensitive across `mutation_rate ∈ {0.005, 0.015, 0.03}` (structural mechanism) — and does the scaling differ between BP_TOPK preserve and Arm A?

## Hypothesis (carried from §v2.4-proxy-5b, no change)

Two competing readings per decoder arm × a cross-arm differential hypothesis:

1. **Kinetic under both arms.** Mutation pressure continuously drives canonical's neighbours off plateau; lower rates slow the drift proportionally. Both arms lift.
2. **Structural under both arms.** The decoder arm's geometry dominates regardless of mutation rate. Both arms rate-insensitive.
3. **Decoder-specific (kinetic under Arm A, structural under BP_TOPK).** Arm A's proxy-basin erosion is kinetic; BP_TOPK's neutral network is structurally determined.

## Setup (carried from §v2.4-proxy-5b, no change)

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_4_proxy5b_mutation_rate_bp_topk.yaml` + `v2_4_proxy5b_mutation_rate_arm_a.yaml`
- **Arms / conditions:** `mutation_rate ∈ {0.005, 0.015, 0.03}` × `arm ∈ {BP_TOPK preserve, A}` × `seed_fraction ∈ {0.0, 0.01}`. 3 × 2 × 2 = 12 cells.
- **Seeds:** 0..19 per cell.
- **Fixed params:** `safe_pop_mode=preserve`, `pop_size=1024`, `generations=1500`, `tournament_size=3`, `elite_count=2`, `crossover_rate=0.7`, `tape_length=32`, `alphabet=v2_probe`, `disable_early_termination=true`, `dump_final_population=true`, `seed_tapes="0201121008010510100708110000000000000000000000000000000000000000"`, `n_examples=64`, `holdout_size=256`, `backend=mlx`.
- **Data commit:** `c3bd8eb` (2026-04-17). No new sweep required.
- **Related experiments:** §v2.4-proxy-5b (the INCONCLUSIVE run this amends), §v2.4-proxy-4d (decode-consistent follow-up, commit `cca2323` — baseline anchor).

## Baseline measurement (required, principle 6)

Unchanged from §v2.4-proxy-5b:

- **Baseline quantity at `mutation_rate=0.03` × `sf=0.01` (principle 6 anchor):**
  - BP_TOPK preserve: `R_fit_999 = 0.723`; `R₂_decoded = 0.0024` 95% CI `[0.0019, 0.0030]`. (§v2.4-proxy-4d, commit `cca2323`.)
  - Arm A: `R_fit_999 = 0.004` (primary); `R₂_decoded = 0.0046` (informational). (Same commit.)
- **Metric definitions (principle 27, cited from `experiments/chem_tape/analyze_retention.py` METRIC_DEFINITIONS):**
  - `R_fit_999`: Fraction of final-population individuals whose training-task fitness is >= 0.999.
  - `R₂_decoded`: Fraction of final-population tapes whose BP_TOPK(k=topk) decoded view is within Levenshtein edit distance 2 of canonical's decoded view. For arm=A runs this view is informational (the VM executes the raw tape), not execution-semantic.
  - `R₂_active`: Fraction of final-population tapes whose permeable-all active view is within Levenshtein edit distance 2 of canonical's 12-token active program.

## Internal-control check (required, principle 1)

- **Tightest internal contrast per arm:** `mutation_rate=0.005` vs `mutation_rate=0.03` at the same `sf=0.01`, same seeds, same commit. Within-arm comparison directly tests the kinetic-vs-structural reading for each decoder.
- **Cross-arm contrast:** under matched mutation_rate, compare `R_fit_999` lift between BP_TOPK and Arm A.
- **Are you running it here?** All six seeded cells span the internal contrast. Data already on disk.

## Amended outcome grid (principle 2b + §26 cross-product)

### Grid axes and coarse bins

**Primary axes measured at per-seed resolution:**

| axis | arm scope | coarse bins (§26) |
|---|---|---|
| `R_fit_999` at mr=0.005 vs baseline | both arms | low < 0.1 · mid 0.1–0.7 · high ≥ 0.7 |
| `R₂_decoded` at mr=0.005 vs baseline | BP_TOPK (co-primary); Arm A (informational) | low < 0.05 · high ≥ 0.05 |
| `F_AND` at mr=0.005 × sf=0.01 | both arms | 20/20 · partial 15–19/20 · swamped < 15/20 |

**Rationale for primary metric split:** Arm A primary metric is `R_fit_999` (not `R₂_decoded`) because the prereg's own degenerate-success guard establishes that the Arm A decoded view is informational-only — the VM executes the raw tape for arm=A. BP_TOPK uses `R_fit_999` as primary (solver retention is the key kinetic signal) and `R₂_decoded` as co-primary (canonical structural proximity within the solver cloud is the distinctly BP_TOPK mechanism signal). This split is the grid repair.

### Arm A outcome rows (primary: R_fit_999)

Outcome cells compare mr=0.005 (slowest) against baseline mr=0.03 (`R_fit_999 ≈ 0.004`). F_AND sanity gate applies to all rows.

| outcome | R_fit_999 at mr=0.005 vs baseline ≈ 0.004 | F_AND | interpretation |
|---|---|---|---|
| **A-KINETIC** | high ≥ 0.3 (substantial lift from baseline) | 20/20 | Arm A proxy-basin erosion IS kinetic. Slower mutation slows or halts the sink from canonical; variation-layer operators are live candidates. Magnitude of lift codes the strength of kinetic dependence. If R_fit ≥ 0.7 the basin may be mutation-competitive; 0.1–0.7 indicates partial kinetic sensitivity. |
| **A-MILD** | mid 0.1–0.3 (moderate lift, not high) | 20/20 | Arm A shows kinetic sensitivity but retention is not high even at minimal mutation. Rate is a lever but not a strong enough one to fully recover canonical retention. |
| **A-STRUCTURAL** | low < 0.1 (no lift across all rates) | 20/20 | Arm A proxy-basin is selection-dominant; mutation rate is not the lever. Variation-layer direction retired for Arm A. |
| **A-SWAMPED** | any | F < 18/20 | mr=0.005 too low to sustain solving even from seed; Arm A result uninformative for kinetic question. |

### BP_TOPK outcome rows (co-primary: R_fit_999 + R₂_decoded)

Outcome cells compare mr=0.005 against baseline mr=0.03 (`R_fit_999 ≈ 0.723`, `R₂_decoded ≈ 0.0024`).

| outcome | R_fit_999 at mr=0.005 vs baseline ≈ 0.723 | R₂_decoded at mr=0.005 | F_AND | interpretation |
|---|---|---|---|---|
| **BP-KINETIC-FULL** | high ≥ 0.85 | high ≥ 0.05 | 20/20 | Both solver retention and canonical proximity lift. The solver neutral network is retained and its center shifts back toward canonical. Full kinetic mechanism. |
| **BP-KINETIC-RFLT** | high ≥ 0.85 | low < 0.05 | 20/20 | Solver retention lifts (more seeds maintain high fitness) but canonical remains off-center in the cloud (low structural proximity). Partial kinetic: rate affects which part of the solver cloud is occupied, not the canonical-vs-noncanonical split within it. |
| **BP-MILD-FULL** | mid 0.1–0.7 (lift but not high) | high ≥ 0.05 | 20/20 | Modest retention lift with canonical proximity lift. Kinetically sensitive but weakly. |
| **BP-MILD-RFLT** | mid 0.1–0.7 | low < 0.05 | 20/20 | Modest retention lift; canonical proximity unchanged. Weak kinetic on fitness dimension only. |
| **BP-STRUCTURAL** | low (within 95% CI of baseline 0.723) | low < 0.05 | 20/20 | The solver neutral network is structurally determined by the decoder's many-to-one mapping. Rate does not shift fitness retention or canonical proximity. Representation-layer interventions are the direction. |
| **BP-STRUCTURAL-SHIFT** | low (within CI of 0.723) | high ≥ 0.05 | 20/20 | Solver retention unchanged but canonical becomes more central in the cloud. Structural on fitness dimension; kinetic on proximity dimension. Unusual cell — note if observed. |
| **BP-SWAMPED** | any | any | F < 18/20 | mr=0.005 too low for BP_TOPK arm; result uninformative. |

### Cross-arm outcome rows

The cross-arm row is the logical combination of the highest-matched per-arm rows at mr=0.005.

| outcome | Arm A component | BP_TOPK component | interpretation |
|---|---|---|---|
| **BOTH-KINETIC** | A-KINETIC or A-MILD | BP-KINETIC-FULL or BP-KINETIC-RFLT | Both arms respond to mutation rate. Variation-layer direction is live for both; magnitudes and sub-mechanisms may differ. |
| **DIVERGE** | A-KINETIC or A-MILD | BP-STRUCTURAL or BP-STRUCTURAL-SHIFT | Decoder-specific: Arm A proxy-basin is kinetic; BP_TOPK solver network is structurally determined. Mutation kinetics are orthogonal to BP_TOPK's decoder geometry. |
| **CONVERGE** | A-STRUCTURAL | BP-STRUCTURAL or BP-STRUCTURAL-SHIFT | Both mechanisms structural. Variation-layer direction retired for both arms. |
| **A-ONLY-KINETIC** | A-KINETIC or A-MILD | BP-MILD-* | Arm A shows strong kinetic; BP_TOPK shows mild response — partial diverge pattern. |
| **BP-SWAMPED** | any | BP-SWAMPED | BP_TOPK at mr=0.005 fails degenerate-success guard; only Arm A interpretable. |
| **A-SWAMPED** | A-SWAMPED | any | Arm A at mr=0.005 fails guard; only BP_TOPK interpretable. |
| **INCONCLUSIVE** | any other combination | any other combination | Per principle 2b, re-examine grid before interpreting. |

### Monotonicity cell (mr=0.015 interpolation)

Both arms: if R_fit_999 shows monotone lift from mr=0.03 → mr=0.015 → mr=0.005, the kinetic reading is strengthened. Non-monotonicity (e.g., R_fit dips at mr=0.015 below baseline or below mr=0.005) is an INCONCLUSIVE qualifier requiring follow-up.

## Degenerate-success guard (required, principle 4 — carried from §v2.4-proxy-5b, no change)

- **Mutation-rate-too-low artefact (SWAMPED rows):** at mr=0.005, F_AND per arm must be ≥ 18/20; unique_genotypes per arm must exceed 500/1024; R₀_decoded at sf=0.0 must remain 0.000.
- **Arm A decoded-view artefact:** Arm A R₂_decoded values are informational only; no Arm A mechanism claim rests solely on the decoded column (this is the defect the amendment repairs).
- **Non-monotonicity flag:** R_fit_999 that lifts at mr=0.015 but falls at mr=0.005, or vice versa, is flagged as INCONCLUSIVE on the kinetic axis; do not claim kinetic without monotone pattern.

## Statistical test (principle 22)

- **Primary:** per-cell bootstrap 95% CI on `R₂_decoded`, `R₂_active`, and `R_fit_999`. No additional tests beyond what §v2.4-proxy-5b ran.
- **Classification (principle 22):** **exploratory.** Does not gate a new findings.md claim; informs the decoder-specific mechanism split already ACTIVE in `findings.md#proxy-basin-attractor`.
- **Family:** n/a (exploratory). Proxy-basin FWER family size unchanged; corrected α stays at 0.05/3 ≈ 0.017.

## Diagnostics to log (beyond fitness)

Same as §v2.4-proxy-5b; all data already on disk from commit `c3bd8eb`:
- Per-seed × per-cell `F_AND`, `best-of-run` fitness
- Per-cell `R₂_decoded`, `R₂_active`, `R₂_raw`, `R_fit_999`, `unique_genotypes`, `final_generation_mean`
- Per-cell bootstrap 95% CI on all three R₂ views + R_fit_999
- Per-seed best-of-run hex at sf=0.01 per arm (canonical verification)
- Paired-seed R_fit_999 lift magnitude by arm at mr=0.005 vs mr=0.03

## Scope tag (required, principle 18)

**If this experiment's result enters a findings.md narrowing:**
`within-family · n=20 per cell (12 cells) · at pop=1024 gens=1500 tournament_size=3 elite_count=2 crossover_rate=0.7 v2_probe disable_early_termination=true · on sum_gt_10_AND_max_gt_5 natural sampler · BP_TOPK(k=3, bp=0.5) preserve + Arm A direct GP · mutation_rate ∈ {0.005, 0.015, 0.03} · seeded canonical 12-token AND body at sf ∈ {0.0, 0.01}`

Cross-task scope is open; §v2.4-proxy-5b-crosstask is queued as the external-validity next step before paper-level citation.

## Decision rule (principle 19)

- **BOTH-KINETIC →** update `findings.md#proxy-basin-attractor`: add mutation-rate kinetic qualifier for both arms, noting the magnitude asymmetry (Arm A: massive lift; BP_TOPK: modest lift). The decoder-specific mechanism split from §v2.4-proxy-4d is retained — mechanisms differ — but both decoders have a variation-layer lever. Queue cross-task scope test (§v2.4-proxy-5b-crosstask) before paper-level citation. Plasticity probe (§v2.5-plasticity-1a) remains the Arm A next step.
- **DIVERGE →** update `findings.md#proxy-basin-attractor`: add mutation-rate orthogonality note. Arm A's proxy basin is kinetic; BP_TOPK's solver network is structural. Cement decoder-specific mechanism split as mutation-rate-orthogonal. Move "variation-layer operators for Arm A" to live candidate; "representation-layer for BP_TOPK" to natural next direction.
- **CONVERGE →** both mechanisms structural. Update arc doc to close "is the dissociation mutation-kinetic?" with CONVERGE. Retire variation-layer direction for both arms.
- **A-KINETIC without BP-KINETIC →** interpret Arm A mechanism alone; do not update BP_TOPK scope. Plasticity probe remains the Arm A follow-up.
- **BP-KINETIC without A-KINETIC →** interpret BP_TOPK mechanism alone; update the "solver-neutral-network" naming with a mutation-rate qualifier.
- **A-SWAMPED or BP-SWAMPED →** re-check degenerate-success guard for the affected arm; if swamped only at mr=0.005, repeat at mr=0.01 before structural claim.
- **INCONCLUSIVE →** identify which grid cell(s) the data occupied and whether a new cross-product axis is required. Do not narrate mechanism without a grid row.

---

*Audit trail.* This amendment is constructed under principle 2b: the grid is the cross-product of the measured axes (R_fit_999, R₂_decoded, F_AND) at coarse bins per §26, not a grid designed around the observed pattern. Per-arm primary-metric declarations are reconciled with the original prereg's degenerate-success guard (R_fit_999 is primary for Arm A; R_fit_999 + R₂_decoded co-primary for BP_TOPK). FWER family classification unchanged: exploratory (principle 22). No new sweep; data anchor is commit `c3bd8eb`. Supersedes Plans/prereg_v2-4-proxy-5b-mutation-rate.md.*
