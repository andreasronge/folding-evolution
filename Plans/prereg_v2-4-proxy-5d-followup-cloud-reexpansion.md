# Pre-registration: §v2.4-proxy-5d-followup-cloud-reexpansion (v1) — independent-seed replication of non-monotone R_fit recovery + holdout axis

**Status:** QUEUED · target commit TBD · 2026-04-18 · follow-up to [§v2.4-proxy-5a-followup-mid-bp](./prereg_v2-4-proxy-5a-followup-mid-bp.md) (chronicle, commit `5c6c539`)

**Engineering prerequisite:** `analyze_retention.py --include-holdout` (landed 2026-04-18 E1). **The per-generation trajectory axis is removed from this v1 prereg** (codex review identified it as principle-25 underdischarged given the infra hasn't landed); a separate v2 follow-up prereg will cover trajectory after the sweep.py snapshot infra is built. This prereg's scope is endpoint-replication + holdout axis only.

## Upstream context

§v2.4-proxy-5a-followup-mid-bp (2026-04-18, data commit `5c6c539`) found R_fit_999 is non-monotone across bp ∈ {0.50, 0.60, 0.65, 0.70, 0.75, 0.85, 0.90} at sf=0.01 on BP_TOPK preserve: values {0.723, 0.604, 0.519, 0.375, 0.467, 0.242, 0.177}. A local minimum at bp=0.70 is followed by a partial recovery at bp=0.75 (0.375 → 0.467, a 0.092 absolute gap at the edge of per-cell bootstrap CI half-widths ≈ 0.10). Plateau-edge inspection falsified the two-mechanism (cliff-flattening vs cloud-destabilisation) reading: no Hamming shoulder emerges at any bp; all cells are DISPERSED. The surviving tentative mechanism is "non-monotone single-mechanism cloud-destabilisation on the BP_TOPK wide solver neutral network" — but the non-monotonicity is at the edge of statistical significance on n=20 seeds 0..19.

The PLATEAU-MID decision rule explicitly forbade findings-layer update from the upstream chronicle and committed to drafting this narrowed follow-up prereg. Three axes were specifically called out in that chronicle; this v1 prereg covers axes (1) and (2) only, with (3) deferred to a v2 follow-up gated on trajectory-snapshot infrastructure:
1. independent-seed replication (seeds 20..39) at bp ∈ {0.65, 0.70, 0.75} to test whether the dip-recovery survives paired replication — **covered by this v1 prereg;**
2. `R_fit_holdout_999` alongside `R_fit_999` to test whether the bp=0.75 off-center recovery is a train-only overfit — **covered by this v1 prereg;**
3. per-generation R_fit_999 trajectory at {gen=500, 1000, 1500} to test whether bp=0.75 is converging slower or equilibrating at a different point — **DEFERRED to v2 (§v2.4-proxy-5d-v2-trajectory), blocked on `sweep.py` snapshot infrastructure. Shipping (3) under this v1 prereg would violate principle 25 (metric-infra gate) because the trajectory-producing code does not exist yet.**

Additionally, R₂_decoded was flagged as principle-26 axis-demotion in the upstream chronicle (bp=0.85 cell showed 0.0054, a 1.5× lift over the mid-bp mean not captured by the prior grid). This prereg grids R₂_decoded explicitly.

## Question (one sentence)

Does the R_fit_999 non-monotone dip (bp=0.70) followed by recovery (bp=0.75) observed on seeds 0..19 replicate on independent seeds 20..39, and does the bp=0.75 recovery correspond to `R_fit_holdout_999` lift (generalizing) or not (train-only proxy overfit)? (v2 prereg to follow on trajectory-shape question, gated on infra.)

## Hypothesis

Four competing readings:

1. **REPLICATE-AND-GENERALIZING.** The dip-recovery profile reproduces on seeds 20..39, and `R_fit_holdout_999` tracks `R_fit_999` within 0.05 at bp=0.75 (≥ 0.4 holdout fitness). The recovery is a genuine off-center generalizing solver cloud re-expansion.
2. **REPLICATE-AND-TRAIN-ONLY.** The dip-recovery reproduces, but `R_fit_holdout_999` stays at the bp=0.70 level (≈ 0.35) while `R_fit_999` lifts to ≈ 0.47. The recovery is in train-only proxy-fitting individuals; the generalizing solver cloud continues to erode monotonically. **Mechanism rename:** "bp destabilises generalizing solvers monotonically; train-only proxy overfitting partially recovers at high-bp due to decoder-path masking." Narrows findings.md.
3. **FAIL-TO-REPLICATE.** On seeds 20..39 the R_fit_999 profile is monotone; the 0..19 non-monotonicity was within-CI noise. Principle 8 applies: n=20 was hypothesis-generating, not load-bearing. The surviving claim is "bp destabilises R_fit_999 monotonically within single-mechanism cloud-destabilisation."
4. **PARTIAL-REPLICATE.** The dip is present at bp=0.70 but no recovery at bp=0.75 (or vice versa — recovery without a dip). Mixed signal; principle 2b grid-revision before interpretation.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_4_proxy5d_replication.yaml` (to be created)
- **Arms / conditions:** `bond_protection_ratio ∈ {0.65, 0.70, 0.75}` × `seed_fraction ∈ {0.01}` × `seed ∈ {20, 21, ..., 39}`. 3 × 1 × 20 = 60 runs.
  - Drift-cell at sf=0.0 is NOT included — drift behaviour was well-characterised by §v2.4-proxy-5a-followup-mid-bp; this sweep is purely the replication test.
- **Fixed params:** `arm=BP_TOPK`, `topk=3`, `safe_pop_mode=preserve`, `pop_size=1024`, `generations=1500`, `tournament_size=3`, `elite_count=2`, `mutation_rate=0.03`, `crossover_rate=0.7`, `tape_length=32`, `alphabet=v2_probe`, `task=sum_gt_10_AND_max_gt_5`, `disable_early_termination=true`, `dump_final_population=true`, `seed_tapes="0201121008010510100708110000000000000000000000000000000000000000"`, `n_examples=64`, `holdout_size=256`, `backend=mlx`. Only `bond_protection_ratio` and `seed` vary.
- **Est. compute:** 60 runs × ~2 min/run ÷ 10 workers ≈ 15 min wall.
- **Related experiments:** §v2.4-proxy-5a-followup-mid-bp (the upstream non-monotone observation, commit `5c6c539`); §v2.4-proxy-5a (3-point bp baseline, commit `169eb0e`); §v2.4-proxy-4d decode-consistent follow-up (R_fit_999 baseline at bp=0.5, commit `cca2323`).

**Principle 20 audit:** Sampler and label function unchanged. Only bp and seed block vary. Not triggered.

**Principle 23 audit:** This sweep does NOT reproduce the seeds 0..19 data — the purpose is independent replication on a disjoint seed block. The principle-23 gate applies at the analysis layer: the joined 0..19 ∪ 20..39 result must be compared within the upstream chronicle's framework, and if 20..39 disagrees with 0..19 (FAIL-TO-REPLICATE), the upstream's non-monotonicity claim is falsified per principle 8.

## Baseline measurement (required)

- **Baseline quantities (seeds 0..19, from §v2.4-proxy-5a-followup-mid-bp, principle 6 anchor):**

  | bp | R_fit_999 [95% CI] | R₂_decoded [95% CI] | R_fit_holdout_999 |
  |---|---|---|---|
  | 0.65 | 0.519 [0.392, 0.618] | 0.0036 [0.0026, 0.0046] | **not measured** (pre-E1) — re-evaluate via `--include-holdout` |
  | 0.70 | 0.375 (from §v2.4-proxy-5a commit `169eb0e`) | 0.0046 | **not measured** — re-evaluate |
  | 0.75 | 0.467 [0.353, 0.558] | 0.0029 [0.0022, 0.0037] | **not measured** — re-evaluate |

  The `R_fit_holdout_999` column on seeds 0..19 must be **re-evaluated from existing `final_population.npz` data** using `analyze_retention.py --include-holdout` before this prereg's sweep runs. That re-evaluation is itself a separate analysis step (not a new sweep) and must precede the 20..39 sweep so the chronicle has a seed-0..19 holdout baseline to compare against.

- **Metric definitions (principle 27, cited verbatim):**
  - `R_fit_999`: *"Fraction of final-population individuals whose training-task fitness is >= 0.999 (near-canonical fitness proxy, independent of structural distance from canonical)."*
  - `R_fit_holdout_999`: *"Fraction of final-population individuals whose HOLDOUT-task fitness is >= 0.999 (holdout generalization analogue of R_fit_999)."*
  - `R_fit_holdout_mean`: *"Mean holdout-task fitness across the full final population."*
  - `R2_decoded`: *"Fraction of final-population tapes whose BP_TOPK(k=topk) decoded view [...] is within Levenshtein edit distance 2 of canonical's decoded view."*

## Internal-control check (required)

- **Tightest internal contrast:** bp=0.70 vs bp=0.75 on seeds 20..39 (within-sweep, shared-seed paired). The upstream chronicle reported a 0.092 absolute R_fit_999 gap on seeds 0..19; the paired contrast on 20..39 is the direct replication.
- **Are you running it here?** Yes.

## Pre-registered outcomes (required — §26-compliant grid)

<!--
Axes:
  - R_fit_999 at {bp=0.65, 0.70, 0.75} on seeds 20..39 (primary)
  - R_fit_holdout_999 at same cells (primary — tests train-only-overfit hypothesis)
  - R₂_decoded at same cells (primary — flagged from §v2.4-proxy-5a-followup-mid-bp principle-26)
  - Non-monotone signature: is bp=0.70 < bp=0.65 AND bp=0.70 < bp=0.75? (binary: yes / no)

Grid bins:
  R_fit_999 at bp=0.70: < 0.4 (dip present) | ≥ 0.4 (no dip)
  Recovery: R_fit_999(bp=0.75) − R_fit_999(bp=0.70): > 0.05 (recovery) | ≤ 0.05 (no recovery)
  Train-vs-holdout divergence at bp=0.75: R_fit_999 − R_fit_holdout_999 > 0.1 (train-only) | ≤ 0.1 (tracks)
  R₂_decoded at bp=0.65..0.75: flat (< 0.006 across all cells) | lifted (≥ 0.006 at any cell)
-->

Primary observation cell: seeds 20..39 at bp ∈ {0.65, 0.70, 0.75}, sf=0.01.

| outcome | R_fit_999 profile (20..39) | Recovery magnitude (bp=0.75 − bp=0.70) | Holdout divergence at bp=0.75 | interpretation |
|---|---|---|---|---|
| **REPLICATE-AND-GENERALIZING** | bp=0.70 < 0.4 AND bp=0.75 > bp=0.70 by > 0.05 (dip + recovery match seeds 0..19) | > 0.05 | ≤ 0.1 (holdout tracks train) | Non-monotone dip-recovery survives independent-seed replication AND the recovery is in generalizing solvers. The "non-monotone single-mechanism cloud-destabilisation" name from §v2.4-proxy-5a-followup-mid-bp is confirmed. Promote to findings.md as a NARROWING of the existing proxy-basin-attractor claim. |
| **REPLICATE-AND-TRAIN-ONLY** | dip + recovery match | > 0.05 | > 0.1 (train-only overfit) | Non-monotone shape survives replication BUT the bp=0.75 recovery is in train-only proxy-fitters. Rename mechanism: "bp destabilises generalizing solvers monotonically; train-only proxy-overfitting partially recovers at high-bp." Narrows findings.md (new language) but the shape is informative. |
| **FAIL-TO-REPLICATE** | R_fit_999 at bp=0.70 on seeds 20..39 is NOT < bp=0.65 (no dip) OR bp=0.75 is NOT > bp=0.70 by 0.05 | ≤ 0.05 | any | Non-monotonicity was within-CI noise on seeds 0..19. Principle 8 applies — mechanism reverts to "monotone single-mechanism cloud-destabilisation." Update upstream chronicle with a supersession block (principle 13) noting the non-monotone reading is superseded by this replication. |
| **PARTIAL-REPLICATE** | one feature replicates (dip OR recovery) but not both | any | any | Mixed signal. Principle 2b: update grid before interpreting. Inspect plateau-edge populations on 20..39 via `inspect_plateau_edge.py` for mechanism signature. |
| **R₂_DECODED-LIFT** | any of above, PLUS R₂_decoded at bp=0.75 ≥ 0.006 (vs seeds 0..19 baseline 0.0029) | any | any | Secondary finding: canonical proximity lifts as part of the bp=0.75 recovery. Sub-outcome on top of the primary verdict. Reconsider the "canonical off-center" scope tag — may need "lever-dependent" qualifier. |
| **SWAMPED** | R_fit_999 at any bp on seeds 20..39 is < 0.1 or F_AND < 18/20 | any | any | One or more cells failed to solve on the new seed block. Investigate before comparing to seeds 0..19; seed block effect not attributable to mechanism. |
| **INCONCLUSIVE** | any pattern not matching above | any | any | Per principle 2b, update the grid before interpreting. |

**Threshold justification:** R_fit_999 "dip at bp=0.70" threshold of 0.4 sits midway between seeds 0..19's bp=0.70 value (0.375) and bp=0.75 value (0.467); below 0.4 the dip is present as measured. Recovery magnitude 0.05 is the §v2.4-proxy-5b-amended bin-edge tolerance. Holdout-train divergence 0.1 is 1× the bootstrap CI half-width observed in existing R_fit_999 measurements. R₂_decoded 0.006 is 2× the seeds-0..19 mid-bp mean (0.003).

## Degenerate-success guard (required)

- **Seed-block-shift artefact.** If the seeds 20..39 block happens to contain persistently-unsolved seeds (methodology principle 15 names {4, 11, 17} in the 0..19 block; their 20..39 analogues are unknown), the lower R_fit_999 at seeds 20..39 could be a seed-block composition effect, not a mechanism shift. Detection: compare per-seed best-of-run fitness distribution between 0..19 and 20..39 at the bp=0.5 anchor (not in this sweep's grid — use the §v2.4-proxy-4d baseline re-evaluated if needed). If 20..39's distribution is systematically shifted at the anchor, adjust per-cell comparisons by the seed-block bias.
- **Monotone-replicate-but-trivial artefact.** If all three cells in 20..39 show R_fit_999 < 0.2 (all collapsed), the profile is technically monotone but at the collapse floor — no information beyond "bp ≥ 0.65 collapses on this seed block." Flag as INCONCLUSIVE-BELOW-FLOOR; compare bp=0.5 anchor on 20..39 via separate re-analysis.
- **Holdout-evaluation staleness.** `R_fit_holdout_999` requires rebuilding the task from config.yaml + seed. If the task registry changed between the original seed-0..19 commits (5a: `169eb0e`; mid-bp: `5c6c539`) and the 20..39 sweep commit, holdout comparisons are invalid. Detection: compare `result.json:holdout_fitness` (stored at original commit) against `analyze_retention.py --include-holdout` re-evaluation of the same individual; must agree within 0.005 on a sample of 5 seeds per bp cell. Halt interpretation until validated.

## Statistical test (principle 22)

- **Primary:** paired bootstrap 95% CI on the per-seed R_fit_999(bp=0.75) − R_fit_999(bp=0.70) difference across both seed blocks (20 pairs × 2 blocks = 40 pairs total). If the 95% CI excludes 0, the non-monotone dip-recovery is load-bearing.
- **Per-block test:** per-seed R_fit_999 on seeds 20..39 alone; bootstrap 95% CI on the {R_fit(bp=0.75) − R_fit(bp=0.70)} contrast within the 20-pair block. Should be consistent with the 0..19 result.
- **Classification (principle 22): confirmatory.** This test gates the non-monotone mechanism name in `findings.md#proxy-basin-attractor`. Corrected α per proxy-basin FWER family = 0.05 / 4 = 0.0125 (expanding the family from 3 to 4 with this new confirmatory test).

**FWER audit note:** This prereg grows the proxy-basin FWER family from 3 confirmatory tests to 4. The α correction tightens from 0.05/3 ≈ 0.017 to 0.05/4 = 0.0125. Prior findings-layer claims may need to re-verify they clear the tighter α; queue an `fwer-audit` mode run before promoting.

## Diagnostics to log (beyond primary axes)

- Per-seed × per-cell R_fit_999, R_fit_holdout_999, R_fit_holdout_mean, R₂_decoded, R₂_active, unique_genotypes, final_generation_mean
- Per-cell bootstrap 95% CI on R_fit_999, R_fit_holdout_999, R₂_decoded
- ~~Per-generation R_fit_999 trajectory at gens ∈ {500, 1000, 1500}~~ — **REMOVED from this v1 prereg** (trajectory axis deferred to v2 follow-up, blocked on `sweep.py` snapshot infrastructure). `history.npz` continues to emit per-generation best-fitness and mean-fitness scalars as it always has; those are available as a partial proxy but do not substitute for full-population R_fit_999 trajectory.
- Winner-tape decode on all bp=0.70 and bp=0.75 best-of-run individuals (40 tapes) — attractor-category audit vs seeds 0..19
- Plateau-edge inspection via `inspect_plateau_edge.py` with seeds 20..39 data — the bp=0.70 vs bp=0.75 Pair-B analysis must replicate the seeds-0..19 CLOUD-DESTABILISATION pair verdict

## Measurement-infrastructure gate (principle 25)

| metric | state | producing code |
|---|---|---|
| R_fit_999 | produced directly | `analyze_retention.py:R_fit_999` |
| R_fit_holdout_999, R_fit_holdout_mean | produced directly | `analyze_retention.py --include-holdout` (2026-04-18 E1) |
| R₂_decoded, R₂_active | produced directly | `analyze_retention.py` |
| Attractor category per cell | produced directly | `inspect_bp9_population.classify_attractor` |
| Plateau-edge pair verdict | produced directly | `inspect_plateau_edge.py` |
| Per-generation R_fit_999 trajectory at {500, 1000, 1500} | **pending infra extension** | `sweep.py` must snapshot `final_population.npz` at checkpoints — est. ~100 LoC + corresponding changes in `evolve.py` to expose population snapshots during evolution. **This is the one remaining engineering blocker.** Until it lands, the trajectory axis can be reported only as best-fitness and mean-fitness per generation (already in `history.npz`); full-population trajectory snapshots are unavailable. |

**Gate status: PARTIAL — trajectory axis is explicitly deferred (2026-04-18, after codex review).** Per-cell R_fit_999 endpoint metric, R_fit_holdout_*, and plateau-edge inspection are all available. Per-generation full-population R_fit_999 trajectory is NOT available until `sweep.py` infrastructure extension lands. **The trajectory axis is REMOVED from this prereg's outcome grid and decision rule.** This prereg runs on endpoint measurements only; the v1 question is purely "does the non-monotone dip-recovery survive independent-seed replication + does R_fit_999 track R_fit_holdout_999?" A separate follow-up prereg (§v2.4-proxy-5d-v2-trajectory) will be drafted after this replication completes, gated on the trajectory infra landing, to probe "is bp=0.75 slower-convergence or different-equilibrium?" That question is genuinely important but cannot be answered without the trajectory infra, and shipping a half-answered question under this prereg's name would be principle-25 gate failure. The current prereg's scope is narrower but cleanly dischargeable.

## Scope tag (required for any summary-level claim)

**If REPLICATE-AND-GENERALIZING:** `within-family · n=20 per cell per seed block × 2 disjoint blocks (0..19, 20..39) · at BP_TOPK(k=3) preserve v2_probe pop=1024 gens=1500 tournament_size=3 elite_count=2 mutation_rate=0.03 disable_early_termination=true · on sum_gt_10_AND_max_gt_5 natural sampler seeded canonical 12-token AND body · bond_protection_ratio ∈ {0.65, 0.70, 0.75} at sf=0.01`.

**If REPLICATE-AND-TRAIN-ONLY:** scope tag adds the train-only qualifier and the bp=0.75 R_fit_999 vs R_fit_holdout_999 differential magnitude.

**If FAIL-TO-REPLICATE:** scope tag of the superseded upstream claim narrows to "non-monotone shape was within-CI noise on n=20; monotone reading restored."

## Decision rule

- **REPLICATE-AND-GENERALIZING →** promote `findings.md#proxy-basin-attractor` to include the non-monotone mechanism reading. Update mechanism-naming history with the confirmed tentative name from §v2.4-proxy-5a-followup-mid-bp (principle 16 rename history preserved). FWER family size grows to 4; update corrected α in the findings-layer scope block.
- **REPLICATE-AND-TRAIN-ONLY →** update `findings.md#proxy-basin-attractor` with a holdout-dissociation qualifier: "bp destabilises generalizing solvers monotonically; train-only proxy-overfitting partially recovers at high-bp via decoder-path masking." Narrows the claim (principle 16). Queue a mechanism-triangulation follow-up to characterise the bp value where train-only overfitting exceeds generalizing-solver retention.
- **FAIL-TO-REPLICATE →** add supersession block to the §v2.4-proxy-5a-followup-mid-bp chronicle per methodology §13. Do NOT delete the upstream chronicle's analysis; mark the non-monotone reading as superseded by this replication. Update the tentative mechanism name from "non-monotone single-mechanism cloud-destabilisation" to "monotone single-mechanism cloud-destabilisation"; update `findings.md#proxy-basin-attractor` with the corrected language.
- **PARTIAL-REPLICATE →** stop and inspect plateau-edge populations on seeds 20..39 via `inspect_plateau_edge.py`. Do not interpret without inspection. Draft a narrower follow-up prereg if needed.
- **R₂_DECODED-LIFT (sub-outcome) →** add "canonical proximity lifts at high-bp" qualifier to whichever primary outcome fires. Queue a sweep to test whether the R₂_decoded lift is bp-specific or general (cross-probe to mr=0.005 bp=0.5 via §v2.4-proxy-5ab-cross-probe-diff data if available).
- **SWAMPED →** investigate seed-block-shift artefact via bp=0.5 anchor re-run on seeds 20..39; do not compare 20..39 cells to 0..19 cells until block effect is accounted for.
- **INCONCLUSIVE →** update the grid per principle 2b.

## Status-transition checklist (from QUEUED → RUNNING)

- [ ] Sweep YAML created: `experiments/chem_tape/sweeps/v2/v2_4_proxy5d_replication.yaml`.
- [ ] Queue entry added to `queue.yaml` with timeout=3600.
- [x] Seeds 0..19 holdout baseline re-evaluated via `analyze_5ab.py <sweep_dir> bp --include-holdout` on both 5a and mid-bp sweep dirs (2026-04-18, post-commit `9c43c99`). Result: R_fit_holdout_999 == R_fit_999 at all 7 bp cells at sf=0.01, to 3 decimal places. Prediction P-2 (generalizing-solver-not-train-overfit) discharged on the existing data — the bp=0.75 recovery is NOT train-only overfit. See §v2.4-proxy-5a-followup-mid-bp chronicle Addendum (2026-04-18) in `docs/chem-tape/experiments-v2.md` and the updated `retention_grid_bp.json` files under each sweep dir. This narrows the v1 prereg's question to "does the non-monotone shape itself replicate on independent seeds?" — P-2 is already settled.
- [ ] FWER family audit run — confirm corrected α at 0.05/4 = 0.0125; flag any existing findings.md claims at risk.
- [ ] Decision whether to block on `sweep.py` trajectory-snapshot infra, or proceed with endpoint-only measurement and trajectory deferred.

---

*Audit trail.* Seven outcome rows (principle 2 + 2b). Baseline numbers are the §v2.4-proxy-5a-followup-mid-bp chronicle's values (principle 6 anchor); holdout baseline must be re-evaluated pre-sweep via E1 infrastructure. Internal control is within-sweep bp=0.70 vs bp=0.75 on paired seeds (principle 1). Degenerate-success guard covers seed-block-shift, monotone-collapse-floor, and holdout-staleness artefacts (principle 4). Principle 20 not triggered. Principle 22: **confirmatory** — grows proxy-basin FWER family from 3 to 4 tests, corrected α tightens to 0.05/4 = 0.0125. Principle 23: analysis combines 0..19 and 20..39 data within the upstream chronicle's framework; cross-block comparability is a principle-23 gate. Principle 24: FAIL-TO-REPLICATE outcome is a null first-class finding — if it lands, promote a FALSIFIED entry to findings.md per §24. Principle 25: **PARTIAL** gate — endpoint metrics produced directly via E1 engineering; per-generation trajectory snapshot is the one remaining blocker, deferred with explicit plan. Principle 26: R_fit_999, R_fit_holdout_999, R₂_decoded, and recovery-magnitude-per-pair all gridded as primary axes. Principle 27: metric definitions cited verbatim. Decision rule commits to specific findings.md edits per outcome including explicit supersession per §13 (principle 19).
