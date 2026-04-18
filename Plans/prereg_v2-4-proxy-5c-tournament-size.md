# Pre-registration: §v2.4-proxy-5c-tournament-size — tournament_size selection-pressure probe on BP_TOPK preserve (precursor to §v2.4-proxy-5c-nontournament)

**Status:** QUEUED · target commit TBD · 2026-04-18 · precursor to [§v2.4-proxy-5c-nontournament](./prereg_v2-4-proxy-5c-nontournament.md)

**Engineering prerequisite:** NONE. `tournament_size` is already a `ChemTapeConfig` field (default 3); no new code path. This is the cheapest possible selection-pressure probe.

## Upstream context

§v2.4-proxy-4d established the decoder-specific F/R dissociation: under BP_TOPK(k=3, bp=0.5) preserve, canonical sits off-center in a wide solver neutral network (R_fit_999 ≈ 0.72, R₂_decoded ≈ 0.002). Every cell across §v2.4-proxy-4b/4c/4d/5a/5b used `tournament_size=3, elite_count=2`. §v2.4-proxy-5c-nontournament introduced new `selection_mode` infrastructure (ranking / truncation) but tested only a single `selection_top_fraction=0.5` — one point on the selection-pressure axis. A "DECODER-INTRINSIC" verdict from 5c would leave open whether `top_fraction=0.5` is simply indistinguishable from `tournament_size=3`'s pressure level.

This prereg runs the cheapest selection-pressure probe available in existing code: varying `tournament_size` ∈ {2, 3, 5, 8} on the BP_TOPK preserve seeded cell. If tournament_size already shows R_fit_999 shifts, selection pressure is load-bearing for the wide solver neutral network — and the §v2.4-proxy-5c-nontournament result must be interpreted in that light. If tournament_size shows no shift, the decoder-intrinsic reading has a stronger base rate before ranking/truncation is layered on.

## Question (one sentence)

Under `seed_fraction=0.01` on `sum_gt_10_AND_max_gt_5` natural sampler with BP_TOPK preserve, does varying `tournament_size` ∈ {2, 3, 5, 8} (selection pressure from weakest to strongest) shift `R_fit_999` or `R₂_decoded` beyond bootstrap CI?

## Hypothesis

Two competing readings:

1. **SELECTION-PRESSURE-SENSITIVE.** Stronger tournaments (tournament_size=5 or 8) should preferentially propagate high-fitness individuals, narrowing the solver cloud and potentially lifting R₂_decoded (canonical becomes relatively more prevalent). Weaker tournaments (tournament_size=2) would widen the cloud further. **Prediction:** R_fit_999 or R₂_decoded shifts by ≥ 0.1 absolute between tournament_size=2 and tournament_size=8 at sf=0.01.

2. **SELECTION-PRESSURE-INSENSITIVE (within tournament regime).** The many-to-one BP_TOPK decoder produces so many decoded-equivalent tapes that varying tournament pressure within the tournament-selection regime just doesn't matter — the population equilibrium is decoder-determined. **Prediction:** R_fit_999 and R₂_decoded stay within bootstrap CI across all four tournament sizes.

Reading (2) strengthens the DECODER-INTRINSIC interpretation of §v2.4-proxy-5c-nontournament if it lands there. Reading (1) requires re-interpreting 5c's `top_fraction=0.5` result against a richer selection-pressure baseline — the 5c verdict would need a selection-pressure axis, not a selection-mode axis, before findings-layer citation.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_4_proxy5c_tournament_size.yaml` (to be created)
- **Arms / conditions:** `tournament_size ∈ {2, 3, 5, 8}` × `seed_fraction ∈ {0.0, 0.01}`. 4 × 2 = 8 cells.
- **Seeds:** 0..19 per cell (shared with §v2.4-proxy-4b/4c/4d for paired comparability).
- **Fixed params:** `arm=BP_TOPK`, `topk=3`, `safe_pop_mode=preserve`, `bond_protection_ratio=0.5`, `pop_size=1024`, `generations=1500`, `elite_count=2`, `mutation_rate=0.03`, `crossover_rate=0.7`, `tape_length=32`, `alphabet=v2_probe`, `task=sum_gt_10_AND_max_gt_5`, `disable_early_termination=true`, `dump_final_population=true`, `seed_tapes="0201121008010510100708110000000000000000000000000000000000000000"`, `n_examples=64`, `holdout_size=256`, `backend=mlx`. Only `tournament_size` and `seed_fraction` vary.
- **Est. compute:** 8 cells × 20 seeds = 160 runs at ~2 min/run ÷ 10 workers ≈ 35 min wall. tournament_size=8 may be slightly slower (more fitness comparisons per parent selection), but the cost is negligible.
- **Related experiments:** §v2.4-proxy-4d decode-consistent follow-up (commit `cca2323` — baseline at tournament_size=3), §v2.4-proxy-5c-nontournament (selection_mode probe; this prereg provides the tournament-pressure axis that 5c lacks).

**Principle 20 audit:** Label function, input distribution, sampler unchanged. Only `tournament_size` and `seed_fraction` vary. Principle 20 not triggered.

**Principle 23 audit:** `tournament_size=3 × sf=0.01` must reproduce §v2.4-proxy-4d decode-consistent numbers at the same commit — baseline comparability gate. The only difference from §v2.4-proxy-4d at that cell is the addition of `tournament_size=3` to the config (unchanged from default). Config hashes should match byte-for-byte with §v2.4-proxy-4d's preserve cell if the sweep runs at a commit where no other fields were added.

## Baseline measurement (required)

- **Baseline anchor (principle 6):** BP_TOPK preserve × tournament_size=3 × sf=0.01 → `R_fit_999 = 0.723`, `R₂_decoded = 0.0024 95% CI [0.0019, 0.0030]`, `R₂_active = 0.0025 95% CI [0.0020, 0.0031]`. Source: §v2.4-proxy-4d decode-consistent follow-up (commit `cca2323`).
- **Drift-check anchor at sf=0.0:** expected R_fit_999 ≈ 0, solve_count = 0/20 across all tournament sizes.
- **Metric definitions (principle 27, cited verbatim from `experiments/chem_tape/analyze_retention.py` METRIC_DEFINITIONS):**
  - `R_fit_999`: *"Fraction of final-population individuals whose training-task fitness is >= 0.999 (near-canonical fitness proxy, independent of structural distance from canonical)."*
  - `R2_decoded`: *"Fraction of final-population tapes whose BP_TOPK(k=topk) decoded view — the exact token sequence passed to the VM under arm=BP_TOPK, computed as the top-K longest non-separator runs concatenated in tape order via engine.compute_topk_runnable_mask — is within Levenshtein edit distance 2 of canonical's decoded view."*
  - `R2_active`: *"Fraction of final-population tapes whose permeable-all active view (non-NOP, non-separator tokens in tape order) is within Levenshtein edit distance 2 of canonical's 12-token active program."*
  - `R_fit_holdout_999`: *"Fraction of final-population individuals whose HOLDOUT-task fitness is >= 0.999 (holdout generalization analogue of R_fit_999)."* (produced via `analyze_retention.py --include-holdout` per 2026-04-18 engineering.)
  - `bootstrap_ci_spec`: *"Nonparametric bootstrap over per-seed values: 10 000 resamples with replacement via numpy.random.default_rng(seed=42); 95% CI is the [2.5%, 97.5%] empirical quantile of the resampled means."*

## Internal-control check (required)

- **Tightest internal contrast:** tournament_size=2 vs tournament_size=8 at sf=0.01, shared seeds 0..19. This brackets the selection-pressure range within-sweep.
- **Are you running it here?** Yes. All four tournament sizes share seeds for direct paired contrast.

## Pre-registered outcomes (required — §26-compliant grid)

<!--
Axes per-seed at sf=0.01:
  - R_fit_999 (primary — solver neutral network width proxy)
  - R₂_decoded (primary — canonical structural retention)
  - R_fit_holdout_999 (secondary — generalization axis; added post-E1 engineering)
  - F_AND (solve rate; SWAMPED gate)

Grid bins (R_fit_999 bin × R₂_decoded bin × F_AND bin × tournament-profile shape):
  R_fit_999: stable within ±0.05 | shifted >0.1
  R₂_decoded: stable within bootstrap CI | lifted ≥ 0.05
  F_AND: ≥18/20 | SWAMPED <18/20
  Tournament-profile: monotone vs non-monotone shape
-->

Outcome cells compare per-tournament-size R_fit_999 and R₂_decoded against the baseline (tournament_size=3) at sf=0.01, on seeds 0..19.

| outcome | R_fit_999 profile across ts ∈ {2, 3, 5, 8} | R₂_decoded profile | F_AND | interpretation |
|---|---|---|---|---|
| **SELECTION-INSENSITIVE** | All four cells within ±0.05 of baseline (ts=3 at 0.723) | All four cells within bootstrap CI of baseline (0.0024) | ≥18/20 | Tournament pressure at {2,3,5,8} does not change R_fit or canonical retention. Strengthens the DECODER-INTRINSIC reading of §v2.4-proxy-5c-nontournament. The wide solver neutral network is a decoder-geometry property, not a tournament-pressure-coupling. |
| **PRESSURE-MONOTONE-R_FIT** | R_fit_999 monotone across ts (increasing or decreasing); ts=2 vs ts=8 differs by >0.1 | Any profile | ≥18/20 | Tournament pressure has a monotone effect on R_fit: either stronger tournaments narrow the cloud (R_fit drops with ts↑) or paradoxically widen it. Re-interpret §v2.4-proxy-5c-nontournament's single-point result as one value on a selection-pressure curve; the DECODER-INTRINSIC verdict from 5c requires replication at matched-pressure ranking/truncation before citation. |
| **PRESSURE-MONOTONE-R₂** | Any R_fit profile | R₂_decoded monotone across ts; ts=2 vs ts=8 differs by ≥ 0.05 | ≥18/20 | Selection pressure directly affects canonical retention (sharper tournaments pull population closer to canonical). Two-component mechanism: decoder determines cloud width; selection determines canonical position within the cloud. This is the decision-rule branch for a mechanism-expanding narrowing of `findings.md#proxy-basin-attractor`. |
| **PRESSURE-NONMONOTONE** | R_fit_999 non-monotone (dip or spike) across ts values | Any | ≥18/20 | Non-monotone selection-pressure response — analogous to the bp non-monotone result in §v2.4-proxy-5a-followup-mid-bp. Unexpected; stop and inspect plateau-edge populations before interpreting. Likely warrants its own follow-up prereg. |
| **SWAMPED** | Any | Any | F_AND < 18/20 under any tournament size | At least one tournament setting breaks convergence. Most likely ts=2 (weakest pressure fails to propagate solvers at budget). Affected cell demoted from the grid; remaining cells interpreted at their subset scope. |
| **BASELINE-DRIFT** | ts=3 cell does not reproduce §v2.4-proxy-4d (commit `cca2323`) within CI | Any | Any | Commit-level drift between `cca2323` and this sweep's commit. Investigate before interpreting any other tournament cell; no claim update until baseline reproduces. |
| **INCONCLUSIVE** | Any pattern not matching rows above | Any | Any | Per principle 2b, update the grid before interpreting. |

**Threshold justification:** R_fit_999 ±0.05 tolerance matches §v2.4-proxy-5c-nontournament's threshold (same measurement, same scale). 0.1 "substantial shift" is 14× the ≤0.03 run-to-run variability observed at equivalent configs across 5a/5b. R₂_decoded ≥ 0.05 floor matches §v2.4-proxy-4b PARTIAL floor for cross-sweep comparability. F_AND ≥ 18/20 SWAMPED gate matches §v2.4-proxy-5b.

## Degenerate-success guard (required)

- **tournament_size=8 freeze artefact.** At tournament_size=8 the selection pressure is strong enough that the population may converge fast to a single attractor and freeze. Detection: `unique_genotypes` at ts=8 × sf=0.01 must remain above 800/1024 (baseline ~987 at ts=3). Drop below 800 flags freeze; demote that cell to SWAMPED.
- **tournament_size=2 exploration starvation.** At tournament_size=2 the selection pressure is so weak that solvers may never propagate above the random-init baseline. Detection: F_AND at ts=2 × sf=0.01 must remain ≥ 18/20 (same baseline as the other cells). Below that: SWAMPED at the weak-pressure end.
- **Spurious PRESSURE-MONOTONE with R_fit_holdout divergence.** If PRESSURE-MONOTONE-R_FIT fires but R_fit_holdout_999 does NOT track R_fit_999, the monotone R_fit shift is on train-proxy overfitting, not real solver retention. Use `analyze_retention.py --include-holdout` to compute R_fit_holdout_999 per cell. Divergence is a mechanism narrowing, not an artefact — but requires naming in the chronicle.

## Statistical test (principle 22)

- **Primary:** per-cell bootstrap 95% CI on `R_fit_999`, `R₂_decoded`, `R_fit_holdout_999`. Paired within-sweep differences (ts=2 − ts=3, ts=5 − ts=3, ts=8 − ts=3) reported with bootstrap CI on shared seeds.
- **Classification (principle 22): exploratory.** Does not gate a new findings.md claim. Informs `findings.md#proxy-basin-attractor` scope and the interpretation of §v2.4-proxy-5c-nontournament. Proxy-basin FWER family size unchanged at 3; corrected α stays at 0.05/3 ≈ 0.017.
- **Family:** n/a (exploratory).

## Diagnostics to log (beyond fitness)

- Per-seed × per-cell `F_AND`, `best-of-run` fitness (expected 20/20 and 1.0 at sf=0.01 across all tournament sizes)
- Per-cell `R_fit_999`, `R₂_decoded`, `R₂_active`, `R_fit_holdout_999`, `R_fit_holdout_mean`, `unique_genotypes`, `final_generation_mean` (via `analyze_retention.py --include-holdout`)
- Per-cell bootstrap 95% CI on R_fit_999 and R₂_decoded
- Per-seed best-of-run hex at sf=0.01 per tournament size — canonical convergence check (attractor-category inspection per principle 21)
- Paired within-sweep R_fit_999 differences (ts=2 − ts=3, ts=5 − ts=3, ts=8 − ts=3) per seed; bootstrap CI on the paired differences

## Measurement-infrastructure gate (principle 25)

| metric | state | producing code |
|---|---|---|
| `R_fit_999` | produced directly | `analyze_retention.py:R_fit_999` |
| `R₂_decoded`, `R₂_active`, `R₂_raw` | produced directly | `analyze_retention.py` |
| `R_fit_holdout_999`, `R_fit_holdout_mean` | produced directly | `analyze_retention.py --include-holdout` (2026-04-18 engineering) |
| `unique_genotypes` | produced directly | `analyze_retention.py` |
| Paired R_fit_999 differences | derived directly from per-run CSV | post-hoc Python on `retention.csv` |
| best-of-run hex per seed | produced directly | `sweep_index.json:best_genotype_hex` |

All metrics are in state (i) (produced directly). No proxy substitutions. Principle 25 gate discharged.

## Scope tag (required for any summary-level claim)

**If SELECTION-INSENSITIVE:** `within-family · n=20 per cell (8 cells) · at pop=1024 gens=1500 mr=0.03 elite_count=2 crossover_rate=0.7 v2_probe disable_early_termination=true · on sum_gt_10_AND_max_gt_5 natural sampler · BP_TOPK(k=3, bp=0.5) preserve · tournament_size ∈ {2, 3, 5, 8} · seeded canonical 12-token AND body at sf ∈ {0.0, 0.01}`. Conclusion: tournament-pressure axis does not vary wide-solver-neutral-network metrics within this range.

**If PRESSURE-MONOTONE-R_FIT or R₂:** scope tag adds the specific pressure-sensitivity direction and the cell-pair differential magnitude.

**Not expected to broaden the top-line `proxy-basin-attractor` claim.** This probe adds either a "tournament-pressure-insensitive" qualifier (SELECTION-INSENSITIVE) or a "selection-pressure-component" narrowing (PRESSURE-MONOTONE-*) to the already-promoted claim. It is a precursor / baseline for the §v2.4-proxy-5c-nontournament verdict, not a standalone claim.

## Decision rule

- **SELECTION-INSENSITIVE →** run (or retry) §v2.4-proxy-5c-nontournament to get the ranking/truncation data. Their verdict joined with this prereg's null makes the DECODER-INTRINSIC reading defensible: neither within-tournament pressure variation nor across-selection-mode variation shifts the cloud. Strengthens the already-promoted wide-solver-neutral-network claim with a "selection-regime-insensitive" qualifier.
- **PRESSURE-MONOTONE-R_FIT →** §v2.4-proxy-5c-nontournament's result must be re-interpreted at a specific selection-pressure level matched to tournament_size=3. If 5c's ranking/truncation verdicts fall on the tournament-pressure curve produced here, they are single points on a continuous response, not evidence for DECODER-INTRINSIC vs SELECTION-COUPLED. Queue a unified selection-pressure follow-up prereg before any findings-layer update.
- **PRESSURE-MONOTONE-R₂ →** update `findings.md#proxy-basin-attractor` with a two-component qualifier: cloud width = decoder geometry; canonical position within cloud = selection-pressure-modulated. Queue a narrowing sweep with `tournament_size ∈ {2, 4, 6, 8, 10}` + `elite_count ∈ {0, 2, 4}` to characterise the selection-pressure → canonical-position curve. Paired-seed analysis across this sweep's data and §v2.4-proxy-5c-nontournament.
- **PRESSURE-NONMONOTONE →** STOP and inspect plateau-edge populations (analogous to §v2.4-proxy-5a-followup-mid-bp). Do not update findings.md. Draft a narrowed follow-up prereg based on inspection findings.
- **SWAMPED →** drop the affected cell; interpret the remaining cells at their subset scope. If only ts=2 SWAMPed, the conclusion becomes "selection pressure matters at weak-tournament regime" — queue a narrower weak-pressure probe with ts ∈ {2, 3} and varied elite_count.
- **BASELINE-DRIFT →** investigate the commit delta before interpreting; no findings-layer update until ts=3 baseline reproduces `cca2323`.
- **INCONCLUSIVE →** update the grid per principle 2b before interpreting.

## Status-transition checklist (from QUEUED → RUNNING)

- [ ] Sweep YAML created: `experiments/chem_tape/sweeps/v2/v2_4_proxy5c_tournament_size.yaml`.
- [ ] Queue entry added to `queue.yaml` with timeout=3600 (tournament selection is fast; this is the existing code path).
- [ ] Commit hash captured at run time (principle 12).
- [ ] Baseline comparability check discharged at ts=3 × sf=0.01 against §v2.4-proxy-4d.

---

*Audit trail.* Seven outcome rows (principle 2 + 2b; SELECTION-INSENSITIVE, PRESSURE-MONOTONE-R_FIT, PRESSURE-MONOTONE-R₂, PRESSURE-NONMONOTONE, SWAMPED, BASELINE-DRIFT, INCONCLUSIVE). §v2.4-proxy-4d numbers are the baseline (principle 6). Internal control is the within-sweep tournament_size contrast on shared seeds 0..19 (principle 1). Degenerate-success guard covers freeze at ts=8, exploration-starvation at ts=2, and spurious PRESSURE-MONOTONE via train-proxy overfitting (principle 4). Principle 20 not triggered. Principle 22: exploratory; does not grow the proxy-basin FWER family. Principle 23 gate preserved — ts=3 cell must reproduce §v2.4-proxy-4d baseline. Principle 25 satisfied: all metrics produced directly by `analyze_retention.py --include-holdout` (2026-04-18 engineering). Principle 26: R_fit_999, R₂_decoded, R_fit_holdout_999 all gridded as primary axes; F_AND as gating axis. Principle 27: metric definitions cited verbatim from `METRIC_DEFINITIONS`. Decision rule commits to specific findings.md or follow-up-experiment actions per outcome (principle 19). **No new engineering required — this probe uses only existing `ChemTapeConfig.tournament_size` field, which has been load-bearing since v1.** The cheapest possible selection-pressure probe, to be run BEFORE interpreting §v2.4-proxy-5c-nontournament's ranking/truncation verdict.
