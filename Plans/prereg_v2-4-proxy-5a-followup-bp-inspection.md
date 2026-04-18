# Pre-registration: §v2.4-proxy-5a-followup-bp-inspection — zero-compute population inspection of the bp=0.9 R_fit collapse

**Status:** QUEUED · zero-compute diagnostic · data at `experiments/output/2026-04-17/v2_4_proxy5a_bp_sweep/` (sweep from commit `c3bd8eb`) · prereg at commit `4aa8b40` · 2026-04-18

## Upstream context

§v2.4-proxy-5a ran a `bond_protection_ratio` sweep (bp ∈ {0.5, 0.7, 0.9}) on BP_TOPK preserve and returned **INCONCLUSIVE (matched DISSOLVE row)**: `R_fit_999` dropped monotonically from 0.723 at bp=0.5 to 0.177 at bp=0.9, while `R₂_decoded` stayed flat at ~0.002–0.005 across all three bp values. The DISSOLVE decision rule is explicit: *"stop and inspect; do not apply any findings-layer update until genotype inspection confirms the mechanism."*

Specifically open from the §v2.4-proxy-5a chronicle: *"is the collapsed mass at bp=0.9 (R_fit=0.177) one alternative attractor, many attractors, or dispersed noise?"* This inspection pre-registers the answer-seeking procedure.

**Data on disk (no new compute required):** `experiments/output/2026-04-17/v2_4_proxy5a_bp_sweep/<hash>/` — 6 cells × 20 seeds = 120 runs. Each hash dir contains `config.yaml`, `result.json`, and `final_population.npz` (keys: `genotypes` (1024, 32) uint8, `fitnesses` (1024,) float32). The 20 target runs (bp=0.9 × sf=0.01) have been confirmed on disk.

## Question (one sentence)

Is the R_fit collapse at bp=0.9 (R_fit_999 = 0.177, down from 0.723 at bp=0.5) caused by convergence to a **single alternative attractor**, **fragmentation across multiple attractors**, or **dispersed proxy-basin noise with no coherent attractor**?

## Hypothesis

§v2.4-proxy-5a confirmed that all 60 best-of-run genotypes at sf=0.01 are byte-for-byte canonical — so the population-level collapse in `R_fit_999` is not visible at the best-of-run layer. The collapse lives in the mass of the final population *below* canonical. Three structural readings are plausible:

1. **Single-attractor reading.** Raising bp from 0.5 → 0.9 destabilises canonical's basin and pulls the majority of the population toward a specific alternative high-fitness attractor (a non-canonical program that solves or nearly-solves the task). The drift-check at bp=0.9 produced one non-canonical solver (`0d15010d...`), which is circumstantial evidence for a specific alternative basin.

2. **Multi-attractor reading.** bp disrupts canonical's basin but the population fragments across several competing local basins, none dominant. Multiple distinct best-of-run attractor hexes appear across seeds with no one hex holding ≥80% of seeds.

3. **Dispersed-noise reading.** bp simply destabilises the search dynamic without channeling it; the population spreads into the proxy basin without coherent clustering. The R_fit collapse is diffuse. This would be consistent with the decoder-structural reading (the neutral network is bp-insensitive at the decoded level, but bp reduces the *frequency* of near-canonical genotypes by preventing short-distance exploration from bonded cells).

A fourth reading is a mixed signal:

4. **CLIFF-PARTIAL reading.** Some seeds show near-canonical clustering (Hamming distance to canonical ≤ 2 in the raw tape) despite low per-population R_fit, while others do not — partial cliff-flattening in a subset of seeds. Would appear as a shoulder in the Hamming-to-canonical distribution at bp=0.9 that is absent at bp=0.5.

## Setup

- **Sweep file:** none — zero-compute analysis of `experiments/output/2026-04-17/v2_4_proxy5a_bp_sweep/`
- **Analysis script to create:** `experiments/chem_tape/inspect_bp9_population.py`
- **Target runs:** bond_protection_ratio=0.9 × seed_fraction=0.01 (20 runs confirmed on disk)
- **Comparison runs for baseline:** bond_protection_ratio=0.5 × seed_fraction=0.01 (20 runs, same sweep dir)
- **Seeds:** 0..19 (same seed set as §v2.4-proxy-5a per-cell)
- **Fixed params:** all inherited from §v2.4-proxy-5a sweep; arm=BP_TOPK, topk=3, pop_size=1024, tape_length=32, alphabet=v2_probe
- **Est. compute:** zero — file I/O + Hamming/token counting on existing npz. Expected < 2 min wall.
- **Related experiments:** §v2.4-proxy-5a (commit `c3bd8eb`, the source data), §v2.4-proxy-5a-followup-mid-bp (pending — mid-bp localisation sweep; decision rule of this inspection determines whether and how that sweep should track attractor identity)

## Baseline measurement (required)

- **Baseline quantity:** best-of-run genotype hex distribution and R_fit_999 at bp=0.5 × sf=0.01 (the DISSOLVE anchor). Per §v2.4-proxy-5a chronicle: R_fit_999 = 0.723, 60/60 best-of-run canonical. Token histogram at bp=0.5 provides the "undisturbed cloud" reference for the active-view histogram comparison.
- **Measurement:** `inspect_bp9_population.py` loads bp=0.5 × sf=0.01 populations alongside bp=0.9 × sf=0.01, and reports active-view token histograms and Hamming distributions for both. No external number is imported — both conditions are in the same sweep dir.
- **Value (if known):** 20/20 best-of-run canonical at bp=0.5 × sf=0.01 (from §v2.4-proxy-5a; commit `c3bd8eb`).

**Principle 20 audit:** no training distribution change. No new compute. Principle 20 not triggered.

## Internal-control check (required)

- **Tightest internal contrast:** bp=0.5 vs bp=0.9 populations in the *same* run directory on the *same* seeds. Best-of-run hex clustering at bp=0.5 should be 20/20 canonical (known), providing the null baseline for the attractor-category classification at bp=0.9.
- **Are you running it here?** Yes. The script loads both bp conditions side by side; the bp=0.5 distribution is the within-sweep control.

## Pre-registered outcomes (required — principle 2 + 2b grid)

This inspection measures **two independent axes** per methodology §26:
- **Axis A (attractor coherence):** how many distinct best-of-run hexes appear at bp=0.9 across 20 seeds?
- **Axis B (Hamming-to-canonical shoulder):** does the raw-tape Hamming distribution at bp=0.9 show a shoulder within edit distance 2 compared to bp=0.5?

Grid (Axis A × Axis B):

| outcome | Axis A: distinct hexes at bp=0.9 | Axis B: Hamming ≤ 2 shoulder vs bp=0.5 | interpretation | decision rule |
|---|---|---|---|---|
| **SINGLE-ATTRACTOR** | ≤ 2 distinct hexes with ≥ 80% of seeds (≥ 16/20) at one hex | No shoulder (bp=0.9 Hamming-≤-2 fraction ≤ 1.05 × bp=0.5 fraction) | bp destabilises canonical's basin and pulls the population toward a specific alternative attractor; mid-bp localisation (§-followup-mid-bp) should track this attractor's R_fit as a function of bp. Alternative attractor is a mechanism candidate pending localisation. | Queue mid-bp sweep tracking this hex's R_fit; report alternative-attractor hex in findings arc doc. |
| **SINGLE-ATTRACTOR + CLIFF-PARTIAL** | ≤ 2 distinct hexes with ≥ 80% of seeds at one hex | Shoulder present (bp=0.9 Hamming-≤-2 fraction > 1.5 × bp=0.5 fraction) | Single dominant attractor AND some cliff-flattening; the canonical basin has partial partial-flattening signal alongside attractor migration. | Mid-bp sweep tracks both the alternative-attractor R_fit and the Hamming-shoulder fraction as a function of bp. Both signals must be reported. |
| **MULTI-ATTRACTOR** | 3–10 distinct hexes with each having ≥ 2 seed occurrences, and no single hex at ≥ 80% of seeds | Either (no outcome constraint) | bp creates multiple competing attractors; canonical's basin is disrupted but no single alternative dominates. The decoded-structural hypothesis is consistent: many-to-one decode supports multiple stable encodings. Mid-bp sweep still required; mechanism is more complex than simple cliff-flatten or dissolve. | Queue mid-bp sweep; include attractor-category tagging per seed so the sweep can track which attractors persist at which bp. |
| **DISPERSED** | > 10 distinct hexes OR no hex with ≥ 2 occurrences | No shoulder | bp simply destabilises the search dynamic; R_fit collapse is diffuse noise, not an attractor shift. Supports the decoder-structural reading: the cloud dissolves because mutation protection changes the landscape, not because it channels toward a new attractor. | Mid-bp sweep confirms where the instability threshold is; no attractor tracking required. The decoded-structural hypothesis gains support. |
| **CLIFF-PARTIAL-ONLY** | > 10 distinct hexes (dispersed) | Shoulder present (bp=0.9 Hamming-≤-2 fraction > 1.5 × bp=0.5 fraction) | Dispersed population but with more mass near canonical than at bp=0.5 despite low R_fit. Mixed mechanism: some cliff-flattening partial signal plus general dissolution. | Mid-bp sweep tracks the shoulder fraction as a function of bp; does not track any specific alternative attractor. |
| **IMPOSSIBLE** | ≤ 2 hexes (single attractor) AND > 10% Hamming ≤ 2 fraction AND R_fit_999 = 0.177 | Both conditions simultaneously | Ruled out by physics: if a dominant attractor accounts for ≥ 80% of seeds but R_fit_999 is only 0.177, the attractor itself is a non-solver. This outcome can occur — it would mean bp channels the population toward a specific non-canonical low-fitness program. | Not impossible in principle; if observed, reclassify as SINGLE-ATTRACTOR but note the attractor is a proxy-basin non-solver (most interesting scenario). |
| **INCONCLUSIVE** | Any pattern not fitting above rows | Any | Outcome grid missing a cell. Per principle 2b, update the grid then re-interpret. Do not narrate the missing cell as a result. | Update this prereg's grid, then re-run inspection. |

**Threshold justification:** the ≥ 80% (≥ 16/20) threshold for SINGLE-ATTRACTOR is taken from the §v2.4-proxy-5a-followup context specification verbatim. The Hamming shoulder threshold (1.5× baseline fraction) is set conservatively relative to bootstrap CI noise at n=20; bp=0.5 Hamming-≤-2 fraction is expected to be near R₂_decoded ≈ 0.0024 (< 3 / 1024), so any shoulder > ~0.0036 in the bp=0.9 pool would be a 1.5× lift.

## Degenerate-success guard (required)

- **Too-clean result would be:** 20/20 seeds at a single non-canonical hex that is the same as the bp=0.9 drift-check discoverer (`0d15010d...`). This would be striking but is a genuinely interesting mechanistic finding, not a statistical artefact — it would mean bp channels the majority-population toward the same alternative basin that a random init converges to. Not a degenerate success; the drift-check was pre-logged in §v2.4-proxy-5a.
- **Candidate degenerate mechanisms:**
  - *All 20 seeds produce canonical best-of-run (already known true), so "hex clustering" at the best-of-run layer cannot distinguish the reading.* This is not a degenerate success — it correctly means the attractor classification must be done on population-level clustering, not on best-of-run hex.
  - *The Hamming distance is computed on the raw 32-token tape (including 20-NOP tail), not on the 12-token active program.* NOP inflation means many genotypes will cluster near edit-distance 0 of *each other* in raw-tape space regardless of their decoded program. The script must compute Hamming on the full tape AND separately on the active-view tokens; the report must distinguish the two.
  - *The "distinct hex" count is over the best-of-run genotype (from result.json), not over the population.* Since all best-of-run are canonical (known), the attractor-category question must be re-cast to the *second-best* or to the population centroid — or, better, to the modal non-canonical genotype within the final population's R_fit ≥ 0.9 slice.

- **How to detect:** the script (i) counts unique best-of-run hexes across seeds (expected all canonical — null clustering result), (ii) identifies the modal non-canonical genotype hex within each seed's population filtered to fitnesses ≥ 0.9, (iii) clusters these modal hexes across seeds to form the attractor-category table. The "attractor hex" for SINGLE-ATTRACTOR / MULTI-ATTRACTOR classification is the modal non-canonical high-fitness genotype, not the best-of-run (which is canonical by construction).

**Infrastructure note (principle 25):** the key degenerate-success guard is that the script operates on population-level genotype clustering, not on the best-of-run hex. The script must be written before this analysis runs; it does not yet exist. Creating it IS the compute step for this zero-compute prereg. Writing the script is low-cost (~1hr); classifying attractor categories from it is zero-cost (file I/O only).

## Statistical test (if comparing conditions)

- **Test:** no statistical test with a p-value gate. This is a zero-compute inspection; all quantities are descriptive (counts, histograms, modal hexes, Hamming distributions).
- **Classification (principle 22):** **exploratory** — effect-size only, no p-value gate, used for hypothesis generation and decision-rule routing. Does not enter the proxy-basin FWER family. Does not grow the confirmatory test count; corrected α for the family stays at 0.05 / 3 ≈ 0.017.
- **Family:** n/a (exploratory).

## Diagnostics to log (beyond fitness)

Per the analysis script `experiments/chem_tape/inspect_bp9_population.py`:

1. **Best-of-run hex table** — all 20 seeds at bp=0.9 × sf=0.01, confirming all are canonical (should match §v2.4-proxy-5a `check_canonical.py` output). If any are non-canonical, this is a new finding.
2. **Fitness distribution statistics per seed** — mean, std, fraction ≥ 0.999, fraction ≥ 0.9, fraction ≥ 0.5 for the 1024-individual final population at each seed. Report aggregate (mean across 20 seeds) and per-seed table.
3. **Modal non-canonical high-fitness hex per seed** — for each seed, the most common genotype hex in the population slice filtered to fitness ≥ 0.9, excluding canonical. Used for attractor-category classification (see degenerate-success guard above).
4. **Unique-hex count in the fitness ≥ 0.9 slice** per seed and pooled across 20 seeds. Determines SINGLE / MULTI / DISPERSED outcome axis.
5. **Active-view token histogram** — aggregated across all 20 × 1024 = 20 480 genotypes at bp=0.9 × sf=0.01, and separately at bp=0.5 × sf=0.01. Token frequency delta (bp=0.9 − bp=0.5) identifies which tokens dominate the displaced solver cloud.
6. **Raw-tape Hamming distance distribution from canonical** — histogram of `hamming(genotype, canonical_tape)` for each individual in each population, reported as a fraction-of-population distribution at each Hamming-distance level d ∈ {0, 1, 2, 3, 4, 5, ≥6}. Reported separately for bp=0.5 and bp=0.9; the delta detects the Axis B shoulder.
7. **Active-view Hamming distance distribution from canonical** — same as (6) but on the active-program token sequence (non-NOP, non-separator tokens). Complementary to raw-tape Hamming; avoids NOP-inflation artefact (see degenerate-success guard).

**Metric infrastructure (principle 25):**

| Metric | State | Source |
|---|---|---|
| Best-of-run hex per seed | (i) produced directly | `result.json:best_genotype_hex` — same file `check_canonical.py` reads |
| Fitness distribution per seed | (i) produced directly | `final_population.npz:fitnesses` (1024,) float32 |
| Modal non-canonical hex (fitness ≥ 0.9 slice) | (i) produced directly | `final_population.npz:genotypes` + `fitnesses` — script computes mode |
| Active-view token histogram | (i) produced directly | `final_population.npz:genotypes` → `analyze_retention.extract_active()` applied per-individual |
| Raw-tape Hamming to canonical | (i) produced directly | `final_population.npz:genotypes` vs `CANONICAL_AND_BODY_HEX` — per-individual Hamming sum |
| Active-view Hamming to canonical | (i) produced directly | Active-view token sequences from `extract_active()` vs canonical active-view — Levenshtein capped at 8 |

All six metrics are directly computable from files confirmed on disk. No new sweep required; no metric is a labeled bound or proxy.

## Scope tag (required for any summary-level claim)

**If this inspection yields an attractor-category classification that enters a finding:**
`within-family · n=20 seeds · at BP_TOPK(k=3) preserve v2_probe pop=1024 gens=1500 bp=0.9 mutation_rate=0.03 · on sum_gt_10_AND_max_gt_5 natural sampler seeded canonical · zero-compute inspection of §v2.4-proxy-5a final populations`

This inspection is a **mechanism-reading gate**, not a findings-promotion step. Its output routes the mid-bp localisation sweep (§-followup-mid-bp) and determines whether any findings.md entry can be updated per the §v2.4-proxy-5a DISSOLVE decision rule.

## Decision rule

- **SINGLE-ATTRACTOR →** the mid-bp localisation sweep (§v2.4-proxy-5a-followup-mid-bp) should track the identified alternative attractor's R_fit as a function of bp; `findings.md` arc doc notes "alternative attractor" as a mechanism candidate pending localisation confirmation. Promote a narrow claim only after localisation confirms the attractor is stable across the bp transition.
- **SINGLE-ATTRACTOR + CLIFF-PARTIAL →** mid-bp sweep tracks both the alternative-attractor R_fit AND the Hamming-shoulder fraction as a function of bp. Both signals must converge on the same mechanism reading before any findings.md update.
- **MULTI-ATTRACTOR →** mid-bp sweep required; include per-seed attractor-category tagging. Mechanism is more complex than a simple cliff-flatten or dissolve; no findings.md update until localisation clarifies which attractor dominates at which bp.
- **DISPERSED →** bp is simply destabilising the search dynamic; mid-bp sweep confirms where the instability threshold is; the decoded-structural hypothesis gains support (the cloud dissolves because the mutation protection changes the search landscape, not because it channels toward a new attractor). `findings.md#proxy-basin-attractor` mechanism-reading section can note "bp-destabilisable solver cloud at bp≥0.7" as a scope boundary, not a new claim.
- **CLIFF-PARTIAL-ONLY →** partial support for cliff-flattening in some seeds; mid-bp sweep should track the shoulder fraction. No findings.md update until shoulder is replicated on mid-bp values.
- **INCONCLUSIVE →** update the outcome grid above, then re-run inspection. Do not narrate the missing cell.

---

*Audit trail.*
- **Principle 1 (internal control):** bp=0.5 vs bp=0.9 on identical seeds within the same sweep dir is the tightest possible internal contrast.
- **Principle 2 (≥ 3 outcomes):** six outcome rows including SINGLE-ATTRACTOR, MULTI-ATTRACTOR, DISPERSED, CLIFF-PARTIAL-ONLY, SINGLE-ATTRACTOR + CLIFF-PARTIAL, and INCONCLUSIVE.
- **Principle 2b (grid over ≥ 2 axes):** Axis A (attractor coherence) × Axis B (Hamming shoulder) forms the grid. Every cell is assigned an outcome token.
- **Principle 4 (degenerate-success guard):** three candidate mechanisms named; the "best-of-run is canonical by construction" guard is explicitly addressed by redirecting attractor classification to the population-level high-fitness modal hex.
- **Principle 6 (baseline-relative thresholds):** SINGLE-ATTRACTOR threshold (≥ 80%, ≥ 16/20 seeds) is the context-specified bar; Hamming shoulder threshold (1.5× bp=0.5 fraction) is calibrated against the known bp=0.5 R₂_decoded ≈ 0.0024 baseline.
- **Principle 20:** not triggered — no training distribution change, no new sweep.
- **Principle 22:** exploratory; does not grow the FWER family; corrected α stays at 0.05/3 ≈ 0.017.
- **Principle 25:** all six metrics are in state (i) produced directly; source files named. The one infra gap (the script does not yet exist) is explicitly noted — creating the script IS the work step, and it is low-cost.
- **Principle 26:** both axes are gridded at coarse bins in the outcome table; no axis is demoted to diagnostic-only without an explicit reason.
- **Principle 27:** metric definitions cite `analyze_retention.METRIC_DEFINITIONS` entries where applicable (`extract_active` for active-view computation); Hamming distance is defined in the script via simple XOR-count on uint8 arrays (raw tape) and Levenshtein capped at 8 (active view).
