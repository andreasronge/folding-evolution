# Pre-registration: §v2.4-proxy-5ab-cross-probe-diff — zero-compute cross-probe population-diff analysis on existing 5a/5b/mid-bp data

**Status:** QUEUED · target commit TBD · 2026-04-18 · zero-compute (reads existing `final_population.npz` files)

**Engineering prerequisite:** `analyze_retention.py --include-holdout` must be available (landed in the 2026-04-18 E1 batch). This prereg's load-bearing axis is cross-probe holdout-fitness comparison; without `R_fit_holdout_999` the analysis can only report training-fitness axes.

## Upstream context

Three BP_TOPK preserve probes on `sum_gt_10_AND_max_gt_5` have produced final_population.npz data on disk across two lever axes:

- **§v2.4-proxy-5a (bp axis)** — bp ∈ {0.5, 0.7, 0.9}, R_fit_999 = {0.723, 0.375, 0.177}.
- **§v2.4-proxy-5a-followup-mid-bp (bp axis fill)** — bp ∈ {0.60, 0.65, 0.75, 0.85}, R_fit_999 = {0.604, 0.519, 0.467, 0.242}. Full bp profile is non-monotone (dip at bp=0.70, recovery at bp=0.75).
- **§v2.4-proxy-5b (mr axis)** — mr ∈ {0.005, 0.015, 0.03}, BP_TOPK R_fit_999 = {0.949, 0.863, 0.723}.

The §v2.4-proxy-5a-followup-mid-bp inspection (2026-04-18, commit `5c6c539`) falsified the two-mechanism reading for the bp axis: all bp cells classify as DISPERSED with no Hamming shoulder emergence. The surviving candidate mechanism is **single-mechanism non-monotone cloud-destabilisation** under bp. This raises a natural cross-probe question: does the mr axis produce the same single-mechanism signature, and if so, do bp and mr act through a common erosion mechanism or through mechanistically distinct pathways that happen to share the single-mechanism naming?

## Question (one sentence)

Does the baseline pair (bp=0.5 unperturbed vs mr=0.03 unperturbed) produce statistically indistinguishable populations (BASELINE-CONFIRMED), and do the Pair III exploratory-diagnostic comparisons surface any holdout-dissociation signal worth a follow-up? (Note: the originally-drafted pair of mechanism-deciding questions — SHARED-MECHANISM vs TWO-MECHANISM — was removed after codex adversarial review identified that existing disk data lacks the matched-R_fit mr cell those questions required; this prereg is rescoped to framework-consistency + hypothesis generation.)

## Hypothesis

Three competing readings:

1. **SHARED-MECHANISM.** bp and mr act through a common erosion mechanism (e.g., "off-center solver cloud reduced by any generic erosion source"). Final populations at matched R_fit_999 values from the two levers should be genotypically indistinguishable at the active-view and decoded-view levels. Prediction: token histograms, edit-distance distributions, and attractor categories match within bootstrap CI when compared at matched R_fit_999.
2. **TWO-MECHANISM-CLEAN.** bp and mr produce structurally distinct attractor regimes. bp-erosion might preferentially preserve scaffold structure (via bond-protection mask) while mr-erosion strips scaffold uniformly. Prediction: at matched R_fit_999 the bp populations retain a recognisable body-like active-view vocabulary while mr populations shift token usage more broadly.
3. **TWO-MECHANISM-GRADIENT.** Both levers affect the same mechanism axis but with different dose-response shapes (the bp axis is non-monotone per §v2.4-proxy-5a-followup-mid-bp; the mr axis is monotone per §v2.4-proxy-5b). Populations at matched R_fit_999 are close but not identical — a gradient, not a clean cluster break.

Reading (3) is the weakest default hypothesis; (1) and (2) are the load-bearing alternatives.

## Engineering setup (zero-compute analysis)

- **Sweep yaml:** NONE. Zero new sweeps.
- **Input data:**
  - `experiments/output/2026-04-17/v2_4_proxy5a_bp_sweep/` (3 bp cells at sf=0.01: bp=0.5, 0.7, 0.9)
  - `experiments/output/2026-04-18/v2_4_proxy5a_mid_bp/` (4 bp cells at sf=0.01: bp=0.60, 0.65, 0.75, 0.85)
  - `experiments/output/2026-04-18/v2_4_proxy5b_mutation_rate_bp_topk/` (3 mr cells at sf=0.01: mr=0.005, 0.015, 0.03). **If this path differs locally, locate via metadata.json.**
- **Analysis script:** `experiments/chem_tape/inspect_cross_probe.py` (to be created, ~250 LoC). Patterned on `inspect_plateau_edge.py`. Reuses `analyze_retention.extract_active`, `extract_decoded`, `levenshtein`, and `inspect_bp9_population.classify_attractor`. Adds `R_fit_holdout_999` analysis via `analyze_retention.evaluate_holdout_population` (landed in 2026-04-18 E1 engineering).
- **Est. compute:** pure analysis (no new evolution runs). Loading 10 cells × 20 seeds = 200 final_population.npz files × ~50 MB each ≈ 10 GB IO. Holdout re-evaluation: 200 × ~0.3s = 60s. Attractor classification + histograms: < 60s. Total wall: ~2 min.

**Principle 20 audit:** No new sampler. No new training data. Analysis operates entirely on pre-existing labeled data. Not triggered.

**Principle 23 audit:** Analysis re-reads disk data; no new execution. The cells being analysed are already chronicled (§v2.4-proxy-5a and §v2.4-proxy-5b). Principle 23 at this layer is "does the analysis preserve the existing chronicled numbers byte-for-byte?" — confirm `R_fit_999` per cell matches the existing chronicle tables, within 0.000 (metric definition stable).

## Baseline measurement (required)

- **Baseline cells (principle 6):**
  - bp=0.5 × sf=0.01: R_fit_999 = 0.723, R₂_decoded = 0.0024, R₂_active = 0.0025 (source: §v2.4-proxy-4d decode-consistent follow-up, commit `cca2323`).
  - mr=0.03 × sf=0.01 at BP_TOPK: R_fit_999 = 0.723, R₂_decoded = 0.0024 (source: §v2.4-proxy-5b-amended at same commit).
  - These two cells are the "unperturbed" endpoints on the bp and mr axes respectively; they share a nominal R_fit_999.

- **Matched-R_fit anchors for the cross-probe comparison:**
  - bp=0.65 × sf=0.01 (R_fit_999 = 0.519) paired with mr=0.015 × sf=0.01 (R_fit_999 ≈ 0.86 — not matched; defer).
  - Actually, due to non-monotone bp and limited mr grid, no mr cell R_fit_999 matches bp=0.75's 0.467 cleanly. The pairing is therefore by-lever-value at the anchor endpoints, not by matched-R_fit across the axes. Report this caveat explicitly in the chronicle.
  - Alternative: use the {R_fit_999 ∈ [0.40, 0.55]} band to pair bp=0.65 and bp=0.75 against any mr cell that falls in the band — mr=0.03 (R_fit=0.723) and mr=0.005 (R_fit=0.949) are both outside, so no direct matched-R_fit mr comparison exists at this task. The cross-probe comparison is therefore **not R_fit-matched within the existing data** — a known scope limitation.

- **Metric definitions (principle 27, cited verbatim):**
  - `R_fit_999`: *"Fraction of final-population individuals whose training-task fitness is >= 0.999 (near-canonical fitness proxy, independent of structural distance from canonical)."*
  - `R2_decoded`: *"Fraction of final-population tapes whose BP_TOPK(k=topk) decoded view [...] is within Levenshtein edit distance 2 of canonical's decoded view."*
  - `R_fit_holdout_999`: *"Fraction of final-population individuals whose HOLDOUT-task fitness is >= 0.999 (holdout generalization analogue of R_fit_999)."*
  - `R_fit_holdout_mean`: *"Mean holdout-task fitness across the full final population."*
  - `bootstrap_ci_spec`: *"Nonparametric bootstrap over per-seed values: 10 000 resamples with replacement via numpy.random.default_rng(seed=42); 95% CI is the [2.5%, 97.5%] empirical quantile of the resampled means."*
  - **New analysis-script-local metric definition:**
    - `cross_probe_token_delta`: *"For two populations A and B pooled across all seeds at their respective cells, the normalised token-frequency delta d_t = freq_A(t) − freq_B(t) across the active-view token vocabulary. Measured at per-token resolution; the distribution summary is the max |d_t| across tokens (largest single-token divergence) and the sum of |d_t| (total-variation distance in vocabulary)."*

## Internal-control check (required)

- **Tightest internal contrast:** bp=0.60 vs bp=0.65 (two adjacent bp cells on the decay arm, same lever) — within-lever null. If even within-lever adjacent cells show token-delta max ≥ 0.1, cross-lever comparisons at similar R_fit_999 gaps are uninterpretable.
- **Are you running it here?** Yes. Every lever's within-lever contrast is a free by-product of the cross-lever analysis.

## Pre-registered outcomes (required — §26-compliant grid)

<!--
Axes (all per-cell, measured across cross-probe pairs):
  - R_fit_999 (per cell; already measured in chronicles)
  - R_fit_holdout_999 (per cell; measured here via --include-holdout)
  - Attractor category per cell (DISPERSED / MULTI / SINGLE; via classify_attractor)
  - Active-view token histogram delta (cross-probe; cross_probe_token_delta max + TV)
  - Decoded-view Levenshtein distribution (per cell; joint JS divergence against canonical)
  - Hamming ≤ 2 raw-tape fraction (per cell)
Grid coarse bins:
  token-delta max: < 0.05 | [0.05, 0.10] | > 0.10
  TV: < 0.2 | [0.2, 0.4] | > 0.4
  holdout-vs-train R_fit divergence: within 0.05 | [0.05, 0.10] | > 0.10
-->

Three cross-probe pairs, gridded per pair:

### Pair I: bp=0.5 (baseline) vs mr=0.03 (baseline) at sf=0.01

These are the unperturbed endpoints on the two axes. R_fit_999 nominally matched at ~0.72.

| outcome | token-delta max | TV | holdout-train divergence | interpretation |
|---|---|---|---|---|
| **BASELINE-IDENTICAL** | < 0.05 | < 0.2 | within 0.05 both cells | The two "unperturbed" cells converge to statistically indistinguishable populations. Confirms the cross-probe baseline — any cross-probe difference at eroded cells is due to the levers, not initial-state differences. |
| **BASELINE-DIVERGENT** | ≥ 0.05 OR TV ≥ 0.2 | | any | The "unperturbed" cells are not actually identical. This undermines the cross-probe comparison framework; investigate before interpreting the eroded cells. Possible causes: commit drift (§v2.4-proxy-5a commit `169eb0e` vs §v2.4-proxy-5b commit `c3bd8eb`); per-commit RNG-consumption difference. |

### Pair II: bp=0.9 (bp-collapsed) vs mr=0.005 inverted ("mr-augmented")

bp=0.9 R_fit = 0.177 (collapsed); mr=0.005 R_fit = 0.949 (lifted). **R_fit is opposite polarity, not matched.** This pair tests whether the direction of lever effect matters for population structure at extreme settings.

| outcome | token-delta max | TV | holdout-train divergence | interpretation |
|---|---|---|---|---|
| **OPPOSITE-LEVERS-DIVERGENT** | > 0.10 | > 0.4 | any | bp-collapsed and mr-lifted populations are structurally distinct. Consistent with TWO-MECHANISM-CLEAN OR with the obvious fact that opposite R_fit endpoints have different populations. This outcome is mostly a sanity check. |
| **OPPOSITE-LEVERS-CONVERGENT** | < 0.05 | < 0.2 | any | Even with opposite R_fit, the populations converge to similar token distributions — unlikely, but would strongly suggest an attractor basin that is stable under both levers. Report and investigate. |
| **MODERATE-DIVERGENCE** | [0.05, 0.10] | [0.2, 0.4] | any | Partial convergence — the expected regime given the R_fit polarity difference. Not mechanism-decisive on its own. |

### Pair III: bp=0.85 (bp-partially-collapsed) vs mr=0.03 (unperturbed mr baseline)

bp=0.85 R_fit = 0.242 (collapsed); mr=0.03 R_fit = 0.723 (unperturbed). **R_fit differs by ~0.48 — the pair is NOT R_fit-matched.** Pair III is therefore **diagnostic-only**, not mechanism-deciding (per codex adversarial review: a 0.48 R_fit gap with no matched-R_fit mr cell available in the existing data cannot support a SHARED-MECHANISM verdict against a TWO-MECHANISM alternative — any observed population divergence is attributable to the R_fit gap itself before any mechanism interpretation).

The outcome grid below is labeled as exploratory-diagnostic, with NO combined-profile promotion rights. The primary mechanism-deciding pairs are Pair I (matched baselines) and Pair II (extreme endpoints, polarity sanity check). A future cross-probe experiment that runs a dedicated mr-at-eroded-R_fit cell (e.g., a low-mr cell that lands in the R_fit=0.24 range, requiring a new sweep) would be needed to make Pair-III-class comparisons mechanism-deciding.

| outcome (EXPLORATORY-DIAGNOSTIC ONLY — does not decide combined profile) | token-delta max | TV | holdout-train divergence | attractor parity | interpretation (as hypothesis, not verdict) |
|---|---|---|---|---|---|
| **DIAGNOSTIC-DIVERGENT** | > 0.10 | > 0.4 | any | any | Populations differ substantially — but the divergence cannot be cleanly attributed to bp-vs-mr mechanism when R_fit_999 itself already differs by 0.48. Reported for hypothesis generation; does not feed the combined-profile table. |
| **DIAGNOSTIC-CONVERGENT** | < 0.05 | < 0.2 | within 0.05 | both DISPERSED | Populations look similar despite the 0.48 R_fit gap. Surprising and hypothesis-generating — the token-level signatures are R_fit-insensitive within this bp/mr domain, which would weakly support a shared-mechanism reading. Queue a new sweep with matched-R_fit mr cell (via lowered gens or a dedicated mr-at-R_fit=0.24 probe) before promoting. |
| **DIAGNOSTIC-HOLDOUT-DISSOCIATION** | any | any | R_fit_holdout_999 > R_fit_999 + 0.1 in one cell, opposite in the other | any | The two levers produce populations with OPPOSITE train-vs-holdout relationships. Notable signal worth following up regardless of R_fit mismatch, because holdout divergence within a single cell is internal to that cell and not driven by the cross-cell R_fit gap. If this fires, queue a dedicated R_fit-matched follow-up. |
| **INCONCLUSIVE** | any other pattern | any other | any | Per principle 2b, update grid before interpreting. |

### Cross-pair profile (mechanism-deciding combined verdict — Pair I only)

Because Pair III is demoted to exploratory-diagnostic (R_fit-mismatched), the combined profile rests on Pair I (matched baselines) plus Pair II as sanity check. Pair III is reported alongside as hypothesis-generating; it does NOT participate in the combined profile verdict.

| combined profile | signature |
|---|---|
| **BASELINE-CONFIRMED** | Pair I = BASELINE-IDENTICAL; Pair II = OPPOSITE-LEVERS-DIVERGENT or MODERATE. The two unperturbed cells match within noise; the framework is consistent. Any further mechanism discrimination requires a new sweep with matched-R_fit mr cells and cannot be settled by this prereg. |
| **HOLDOUT-DISSOCIATION-IN-PAIR-III-DIAGNOSTIC** | Pair III = DIAGNOSTIC-HOLDOUT-DISSOCIATION (regardless of other pair outcomes). Priority-elevated hypothesis: one lever selects for train-proxy overfit and the other selects for generalizing solvers. Queue a dedicated confirmatory sweep with R_fit-matched mr cells. |
| **BASELINE-BROKEN** | Pair I = BASELINE-DIVERGENT. Framework broken before any cross-probe comparison can be run. Investigate; likely a commit drift issue. |

**Removed outcomes (per codex review):** The prior UNIFIED-MECHANISM, DISTINCT-MECHANISMS, and GRADIENT-CONSISTENT rows depended on Pair III's verdict, but Pair III is not mechanism-deciding at this data configuration. Those combined profiles require a new cross-probe sweep with matched-R_fit mr cells to resolve — the present prereg's scope is limited to baseline consistency + polarity sanity + diagnostic token-divergence at unmatched-R_fit cells.

**Threshold justification:** `token-delta max > 0.10` is ~2× the within-population noise observed in the §v2.4-proxy-5a-followup-mid-bp plateau-edge inspection (Pair A's STABLE cells had ratios within 1.24× of each other; translated to token-delta scale this corresponds to < 0.05). TV of 0.4 is the §v2.4-proxy-4d "clear mechanism distinction" bar. Holdout-vs-train divergence of 0.10 is 1× the bootstrap CI half-width of existing R_fit_999 measurements.

## Degenerate-success guard (required)

- **Commit-drift artefact.** The 5a sweep is at commit `169eb0e`, the 5b sweep at `c3bd8eb`, the mid-bp sweep at `5c6c539`. If Pair I (BASELINE-IDENTICAL) fails, the three commits may have non-equivalent code paths downstream of the config hash. Detection: compute `config_hash` for the baseline cells; they should be byte-identical across commits if no hash-excluded change touched the execution path. If config hashes differ on the baseline cells, **halt interpretation** until commit lineage is understood.
- **Holdout evaluation stale.** `analyze_retention.py --include-holdout` rebuilds the task from config.yaml + seed via `tasks.build_task`. If the task registry has changed between the sweep's commit and the analysis commit, the "holdout" being re-evaluated may differ from the original run's holdout. Detection: the sweep's `result.json` has a `holdout_fitness` field for the best-of-run individual; the analysis should recompute it for that individual and confirm agreement within 0.005. Discrepancy is a task-registry-drift flag; halt until resolved.
- **Pool-across-seeds artefact.** Pooling 20 seeds × 1024 individuals = 20 480 tapes per cell into a single token histogram hides seed-level heterogeneity. If any single cell has one or two outlier seeds driving its token distribution, the pooled delta may not reflect the typical population signature. Detection: report both pooled-across-seeds and per-seed mean ± std for the token-histogram axis.

## Statistical test (principle 22)

- **Primary:** Nonparametric bootstrap 95% CI on per-pair (pool-A-minus-pool-B) token-delta max and TV. Bootstrap resamples the per-seed token histograms (i.e., 20 seed-histograms per cell, resample 20 with replacement).
- **Classification (principle 22): exploratory.** Does not gate a new findings.md claim. Informs `findings.md#proxy-basin-attractor` mechanism language (strengthens, narrows, or splits the "non-monotone single-mechanism cloud-destabilisation" name proposed in §v2.4-proxy-5a-followup-mid-bp).
- **Family:** n/a (exploratory). Proxy-basin FWER family size unchanged at 3; corrected α stays at 0.05/3 ≈ 0.017.

## Diagnostics to log (beyond token-delta)

- Per-cell attractor category (DISPERSED / MULTI / SINGLE) via `classify_attractor`
- Per-cell dominant_hex and unique_hex_count in the fitness ≥ 0.9 slice
- Per-cell active-view Levenshtein histogram {0, 1, 2, 3, ≥4, ≥8-cap}
- Per-cell decoded-view Levenshtein histogram (same bins)
- Per-cell raw-tape Hamming distribution {0, 1, 2, 3, 4, 5, ≥6}
- Per-cell R_fit_holdout_999 + R_fit_holdout_mean via `analyze_retention.py --include-holdout`
- Per-pair pooled and per-seed token-delta max + TV
- Per-pair bootstrap 95% CI on the cross-lever delta summaries
- Cross-pair profile summary per the combined-profile table

## Measurement-infrastructure gate (principle 25)

| metric | state | producing code |
|---|---|---|
| `R_fit_999` | produced directly | `analyze_retention.py:R_fit_999` |
| `R₂_decoded`, `R₂_active` | produced directly | `analyze_retention.py` |
| `R_fit_holdout_999`, `R_fit_holdout_mean` | produced directly | `analyze_retention.py --include-holdout` (2026-04-18) |
| Attractor classification | produced directly | `inspect_bp9_population.classify_attractor` |
| Active-view token histogram + cross-probe delta | **pending** | new script `inspect_cross_probe.py` — must be written and committed before this prereg runs. Est. effort: ~200 LoC extending `inspect_plateau_edge.py` patterns. |
| Bootstrap CI on token-delta | **pending** | ~20 LoC in the new script, reusing `analyze_retention.bootstrap_ci`. |

**Gate status: BLOCKED pending `inspect_cross_probe.py`.** Transition from QUEUED → RUNNING only after the script lands. Est. ~1 hour engineering.

## Scope tag (required for any summary-level claim)

**If BASELINE-CONFIRMED:** `within-family · pool-across-20-seeds per cell (limited to Pair I baseline + Pair II polarity check — 2 cells each) · at pop=1024 gens=1500 tournament_size=3 elite_count=2 crossover_rate=0.7 v2_probe disable_early_termination=true · on sum_gt_10_AND_max_gt_5 natural sampler · BP_TOPK(k=3, bp=0.5) preserve · bp × mr axis cross-probe at baseline endpoints only; Pair III (bp=0.85 vs mr=0.03) exploratory-diagnostic only`. The scope tag deliberately excludes any mechanism claim — a mechanism-deciding claim requires a follow-up sweep with matched-R_fit mr cells.

**If HOLDOUT-DISSOCIATION-IN-PAIR-III-DIAGNOSTIC:** scope tag adds "hypothesis: bp and mr levers may select for opposite train-vs-holdout regimes; confirmatory matched-R_fit replication queued before any findings-layer citation."

**Not expected to change the top-line `proxy-basin-attractor` claim.** This probe is a framework-consistency check plus hypothesis generation, not a mechanism-deciding experiment (principle 17 — scope boundary on the R_fit-mismatch data).

## Decision rule

- **BASELINE-CONFIRMED →** record Pair I baseline consistency; Pair III's diagnostic token-divergence (DIAGNOSTIC-DIVERGENT or DIAGNOSTIC-CONVERGENT) is hypothesis-generating and does NOT update findings.md. Queue a new cross-probe sweep with matched-R_fit mr cells before any findings-layer update; this prereg's scope does not include mechanism-decidedness beyond baseline.
- **HOLDOUT-DISSOCIATION-IN-PAIR-III-DIAGNOSTIC →** priority-elevated hypothesis. Update `docs/chem-tape/arcs/proxy-basin-attractor-arc.md` (NOT findings.md yet) with the hypothesis: "bp and mr levers may produce populations with opposite train-vs-holdout R_fit relationships." Queue a confirmatory R_fit-matched sweep to promote to findings.md — not promotable from this prereg's unmatched-R_fit data alone (principle 17).
- **BASELINE-BROKEN →** halt all interpretation. Investigate commit drift (169eb0e vs c3bd8eb vs 5c6c539). If drift is benign (e.g., non-executing field addition), document and re-run the baseline check. If drift is real (execution path changed), re-chronicle affected §v2.4-proxy-5a / 5b / mid-bp entries before proceeding.
- **INCONCLUSIVE →** update the grid per principle 2b before interpreting.

## Status-transition checklist (from QUEUED → RUNNING)

- [ ] `experiments/chem_tape/inspect_cross_probe.py` written and committed (~200 LoC). Pattern: `inspect_plateau_edge.py`.
- [ ] Commit hash captured at run time (principle 12).
- [ ] Baseline comparability check (Pair I = BASELINE-IDENTICAL) discharged before interpreting Pairs II and III.
- [ ] `R_fit_holdout_999` re-evaluation validated against best-of-run `holdout_fitness` in `result.json` for each cell (degenerate-success guard item 2).

---

*Audit trail.* Four combined-profile outcomes (UNIFIED-MECHANISM, DISTINCT-MECHANISMS, GRADIENT-CONSISTENT, BASELINE-BROKEN) + HOLDOUT-DISSOCIATION sub-branch + INCONCLUSIVE (principle 2 + 2b). Internal control is the within-lever bp=0.60 vs bp=0.65 contrast (principle 1). §v2.4-proxy-4d + §v2.4-proxy-5b-amended numbers are the measured baselines (principle 6); no imported numbers. Degenerate-success guard covers three artefacts (commit drift, holdout-task staleness, pool-across-seeds outliers) (principle 4). Principle 20 not triggered. Principle 22: exploratory; does not grow the proxy-basin FWER family. Principle 23: analysis preserves existing chronicled numbers byte-for-byte (validate via per-cell R_fit_999 cross-check against 5a/5b/mid-bp chronicles). Principle 25: blocked pending `inspect_cross_probe.py`; R_fit_holdout is produced directly by `analyze_retention.py --include-holdout` (2026-04-18 engineering). Principle 26: token-delta, attractor category, Hamming histogram, Levenshtein histogram, R_fit_holdout all gridded as primary axes. Principle 27: metric definitions cited verbatim from METRIC_DEFINITIONS; new `cross_probe_token_delta` definition added inline and will be added to `METRIC_DEFINITIONS` in the analysis script when it lands. Decision rule commits to specific findings.md or follow-up-experiment actions per outcome (principle 19). **Zero-compute prereg** — no new sweeps, no new runs, no new evolutionary compute. Uses existing data on disk plus post-E1 holdout re-evaluation.
