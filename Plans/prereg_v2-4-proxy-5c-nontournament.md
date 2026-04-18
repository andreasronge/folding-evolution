# Pre-registration: §v2.4-proxy-5c — non-tournament selection probe on BP_TOPK preserve (selection-coupled vs decoder-intrinsic neutral network)

**Status:** QUEUED · 2026-04-18 · chronicled target: [docs/chem-tape/experiments-v2.md §v2.4-proxy-5c](../docs/chem-tape/experiments-v2.md)

**Engineering note:** prerequisites 1–5 below landed (commit TBD). `selection_mode` / `selection_top_fraction` fields added to `ChemTapeConfig` (hash-excluded at defaults); `_ranking_select` / `_truncation_select` implementations added to `evolve.py`; `METRIC_DEFINITIONS["selection_mode"]` added to `analyze_retention.py`; `tests/test_chem_tape_selection_mode.py` verifies principle-23 byte-identical reproduction under `selection_mode="tournament"` and principle-11 hash exclusion at defaults.

## Supersession / upstream context

§v2.4-proxy-4d (commit `cca2323`) confirmed decoder-specific F/R dissociation: under BP_TOPK preserve, canonical sits off-center in a wide solver neutral network (R_fit_999 ≈ 0.72, R₂_decoded ≈ 0.002 — structurally distinct decoded solvers populate the solver plateau alongside canonical). Tournament selection (tournament_size=3, elite_count=2) has been constant across all cells in the 4b/4c/4d/5a/5b family.

§v2.4-proxy-5b returned BOTH-KINETIC (both arms respond to mutation_rate), confirming that the wide solver neutral network is not purely structural — mutation kinetics shift retention. This makes the selection probe MORE informative: if non-tournament selection also shows kinetic sensitivity in R_fit (comparable kinetics under ranking/truncation), the mechanism implicates the variation+selection coupling; if R_fit breadth persists unchanged under ranking/truncation, the neutral network is decoder-intrinsic and independent of tournament-specific selection pressure.

## Engineering prerequisites (MUST land before sweep can run — per methodology §25)

This prereg transitions from QUEUED to RUNNING only after the following engineering gates are satisfied at a committed and clean HEAD:

1. **`selection_mode` config field** in `ChemTapeConfig` (`src/folding_evolution/chem_tape/config.py`): new string field accepting `"tournament"` (default, current behaviour), `"ranking"`, `"truncation"`. At default (`"tournament"`), all code paths are byte-identical to the current implementation. Excluded from `ChemTapeConfig.hash()` at the `"tournament"` default (principle 11).
2. **Ranking selection implementation** in `evolve.py`: select top-`selection_top_fraction` of population by fitness, sample parents proportional to rank within that group. `selection_top_fraction` is a new config field (default 0.5; excluded from hash at default, principle 11). Ranking preserves elite_count elites (same as tournament path).
3. **Truncation selection implementation** in `evolve.py`: top-`selection_top_fraction` directly replace the bottom (1-`selection_top_fraction`); standard (µ,λ) truncation with crossover. Preserves elite_count elites (same as tournament path).
4. **`METRIC_DEFINITIONS` entry for `selection_mode`** in `experiments/chem_tape/analyze_retention.py`'s `METRIC_DEFINITIONS` dict: add `"selection_mode"` entry noting the field's meaning and hash-exclusion behaviour at default.
5. **Pytest round-trip**: `selection_mode="tournament"` with identical seeds must reproduce byte-identical results to the current default path on at least one reference sweep (≥10 seeds).
- **Est. engineering cost**: ~50–100 LoC in `evolve.py` + `ChemTapeConfig` + pytest.

## Question (one sentence)

Under `seed_fraction=0.01` on `sum_gt_10_AND_max_gt_5` natural sampler, does replacing tournament selection (tournament_size=3, elite_count=2) with ranking or truncation selection change the BP_TOPK preserve solver neutral network width (R_fit_999) or canonical retention (R₂_decoded)?

## Hypothesis

Two competing readings:

1. **SELECTION-COUPLED.** Tournament selection is load-bearing for the wide solver neutral network: tournament's fitness-proportional sampling among near-peak individuals preferentially visits decoder-equivalent (non-canonical) high-fitness tapes, creating and sustaining the wide cloud. Under ranking or truncation selection — which impose a sharper fitness cutoff, reducing lateral drift across the solver plateau — R_fit_999 should decrease and/or R₂_decoded should increase (canonical becomes relatively more prevalent). **Prediction:** ≥0.1 absolute shift in R_fit_999 or R₂_decoded under at least one non-tournament mode.

2. **DECODER-INTRINSIC.** The wide solver neutral network is a property of the BP_TOPK decoder's many-to-one mapping: the sheer volume of non-canonical decoded programs that achieve near-perfect task fitness (because the AND task is satisfiable by many 3-run assemblies) determines population distribution regardless of how selection samples from the fitness landscape. Tournament, ranking, and truncation all route the population to the same high-fitness plateau; the lateral geometry within that plateau is decoder-determined. **Prediction:** R_fit_999 and R₂_decoded within bootstrap CI of the tournament baseline under all non-tournament modes.

Reading (2) is the most theoretically informative outcome given the existing probe series: it would cement the "wide solver neutral network" as a decoder-intrinsic property, making representation-layer interventions (evolvable chemistry) the principal direction for BP_TOPK, and earning the "selection-insensitive" qualifier for the §v2.4-proxy-4d canonical-off-center claim.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_4_proxy5c_nontournament.yaml` (to be created after engineering lands)
- **Arms / conditions:** `selection_mode ∈ {tournament (baseline), ranking, truncation}` × `seed_fraction ∈ {0.0, 0.01}`. 3 × 2 = 6 cells. All cells use BP_TOPK preserve.
- **Seeds:** 0..19 per cell (shared with 4b/4c/4d for paired comparability)
- **Fixed params:** `safe_pop_mode=preserve`, `pop_size=1024`, `generations=1500`, `mutation_rate=0.03`, `crossover_rate=0.7`, `tape_length=32`, `alphabet=v2_probe`, `task=sum_gt_10_AND_max_gt_5`, `topk=3`, `bond_protection_ratio=0.5`, `disable_early_termination=true`, `dump_final_population=true`, `seed_tapes="0201121008010510100708110000000000000000000000000000000000000000"`, `n_examples=64`, `holdout_size=256`, `backend=mlx`. Only `selection_mode` and `seed_fraction` vary.
- **Est. compute:** after engineering lands — ~3 cells × 2 sf × 20 seeds = 120 runs × ~15 min ÷ 10 workers ≈ 30–45 min wall.
- **Related experiments:** §v2.4-proxy-4b (BP_TOPK preserve tournament baseline, commit `f10b066`), §v2.4-proxy-4d decode-consistent follow-up (commit `cca2323` — R_fit_999 + R₂_decoded baselines this prereg anchors against), §v2.4-proxy-5a (bp sweep; dissolved, commit `169eb0e`), §v2.4-proxy-5b (mutation_rate sweep; BOTH-KINETIC, commit `169eb0e`).

**Principle 20 audit:** label function, input distribution, and sampler unchanged from §v2.4-proxy-4b/4c/4d. Only `selection_mode` and `seed_fraction` vary. Principle 20 not triggered.

**Principle 23 audit:** `selection_mode=tournament` cells (both sf values) must reproduce §v2.4-proxy-4d numbers at the same commit — this is the baseline comparability gate. If `selection_mode=tournament` does not reproduce within bootstrap CI, investigate before interpreting non-tournament cells.

## Baseline measurement (required)

- **Baseline quantity at `selection_mode=tournament` × `sf=0.01` (principle 6 anchor):**
  - BP_TOPK preserve: `R₂_decoded = 0.0024` 95% CI `[0.0019, 0.0030]`; `R_fit_999 = 0.723`; `R₂_active = 0.0025` 95% CI `[0.0020, 0.0031]`. (§v2.4-proxy-4d decode-consistent follow-up, commit `cca2323`.)
- **Measurement:** The `selection_mode=tournament` cells in this sweep replay the §v2.4-proxy-4d configuration byte-for-byte (the only difference being the new `selection_mode` field at its default value, which is hash-excluded). The tournament cells serve as the paired within-sweep baseline; deviation from `cca2323` numbers triggers the BASELINE-DRIFT outcome.
- **Metric definitions (per principle 27, cited verbatim from `experiments/chem_tape/analyze_retention.py` METRIC_DEFINITIONS):**
  - `R2_decoded`:
    > Fraction of final-population tapes whose BP_TOPK(k=topk) decoded view — the exact token sequence passed to the VM under arm=BP_TOPK, computed as the top-K longest non-separator runs concatenated in tape order via engine.compute_topk_runnable_mask — is within Levenshtein edit distance 2 of canonical's decoded view. For arm=A runs this view is informational (the VM executes the raw tape), not execution-semantic.
  - `R_fit_999`:
    > Fraction of final-population individuals whose training-task fitness is >= 0.999 (near-canonical fitness proxy, independent of structural distance from canonical).
  - `R2_active`:
    > Fraction of final-population tapes whose permeable-all active view (non-NOP, non-separator tokens in tape order) is within Levenshtein edit distance 2 of canonical's 12-token active program. This view is a SUPERSET of the BP_TOPK(k) decode; active-view and decoded-view distances can disagree in either direction (Levenshtein is not monotone under the top-K-longest-run subsequence restriction).
  - `bootstrap_ci_spec`:
    > Nonparametric bootstrap over per-seed values: 10 000 resamples with replacement via numpy.random.default_rng(seed=42); 95% CI is the [2.5%, 97.5%] empirical quantile of the resampled means.
- **Drift-check expectation at sf=0.0:** F=0/20 at all three selection modes (no solving without seed).

## Internal-control check (required)

- **Tightest internal contrast:** `selection_mode=ranking` vs `selection_mode=tournament` at the same `sf=0.01`, same seeds 0..19, same commit. This directly tests whether tournament-specific sampling creates the neutral network width (SELECTION-COUPLED) or the width is decoder-invariant across selection regimes (DECODER-INTRINSIC).
- **Are you running it here?** Yes. All three selection-mode cells at sf=0.01 provide the pairwise within-sweep contrasts.

## Pre-registered outcomes (required — §26-compliant grid)

<!--
Measured axes per-seed at sf=0.01:
  - R_fit_999 (primary — solver neutral network width proxy)
  - R₂_decoded (primary — canonical structural retention)
  - F_AND (solve rate; sanity / SWAMPED gate)

Both R_fit_999 and R₂_decoded are primary mechanism axes (principle 26 — neither is diagnostic-only).
Grid bins:
  R_fit_999: {stable ≥ 0.65 | shifted <0.65 or >0.85}
  R₂_decoded: {stable within CI | shifted >0.05 above baseline}
  F_AND: {≥18/20 | SWAMPED <18/20}

"Within CI" = within the 95% bootstrap CI of the tournament baseline (R₂_decoded=0.0024,
  CI [0.0019, 0.0030]; R_fit_999=0.723, no CI reported — use ±0.05 as conservative spread).
"Substantial shift" = >0.1 absolute for R_fit_999 or >0.05 absolute for R₂_decoded
  (coarser bar for R₂_decoded since its baseline is near zero; 0.05 is the §v2.4-proxy-4b
  PARTIAL floor and represents a meaningful move away from near-zero retention).
-->

Outcome cells compare `selection_mode=ranking` or `selection_mode=truncation` against `selection_mode=tournament` baseline, at `sf=0.01`, on seeds 0..19.

| outcome | R_fit_999 under ranking/truncation | R₂_decoded under ranking/truncation | F_AND | interpretation |
|---|---|---|---|---|
| **DECODER-INTRINSIC** | Stable: both modes within ±0.05 of tournament baseline (≈0.72) | Stable: both modes within bootstrap CI of tournament baseline (≈0.002) | ≥18/20 | The wide solver neutral network is a property of the BP_TOPK decoder's many-to-one mapping, independent of selection pressure. Points toward representation-layer interventions (evolvable chemistry) as the principal direction for BP_TOPK. §v2.4-proxy-4d "canonical off-center in wide solver neutral network" gains a "selection-insensitive" qualifier. |
| **SELECTION-COUPLED** | Shifted: at least one mode differs by >0.1 from tournament baseline | Any | ≥18/20 | Tournament selection is load-bearing for the neutral network geometry. The solver cloud is tournament-specific — selection-layer interventions (lexicase, Pareto) become the natural Tier-2 direction. R₂_decoded shift direction informs mechanism: if R₂_decoded rises alongside R_fit drop, sharper selection narrows the cloud toward canonical. |
| **R₂-ONLY SHIFT** | Stable: both modes within ±0.05 of tournament baseline | Shifted: at least one mode above 0.05 (R₂_decoded lifts) | ≥18/20 | The solver neutral network width (R_fit) is decoder-intrinsic, but canonical's position within the cloud is selection-sensitive. Sharper selection improves canonical retention without narrowing the cloud. Points to a two-component mechanism: cloud width = decoder geometry; canonical position within cloud = selection geometry. |
| **PARTIAL-COUPLED** | One selection mode shifts R_fit substantially; the other doesn't | Any | ≥18/20 | Tournament has properties not shared by ALL selection regimes (ranking and truncation have distinct profiles). Further narrowing needed — the specific selection-pressure dimension that matters is not yet identified. |
| **SWAMPED** | Any | Any | F_AND < 18/20 under any non-tournament mode | Non-tournament selection breaks convergence at this budget (pop=1024, gens=1500). The sweep is uninformative for the neutral-network question in the affected mode(s). Repeat at larger budget or with higher `selection_top_fraction` before claiming decoder-intrinsic. |
| **BASELINE-DRIFT** | `selection_mode=tournament` cell does not reproduce §v2.4-proxy-4d numbers within CI | — | — | Commit-level drift between commit `cca2323` and this sweep's engineering commit. Investigate before interpreting any non-tournament cell; no claim update until tournament baseline reproduces. |
| **INCONCLUSIVE** | Any pattern not fitting above | Any | Any | Per principle 2b, update the outcome grid before interpreting. |

**Threshold justification:** R_fit_999 ±0.05 tolerance is set to bracket the bootstrap variability at n=20; the §v2.4-proxy-4d point estimate (0.723) has no CI reported, but run-to-run variability across 5a/5b was ≤0.03 at equivalent configs. The 0.1 "substantial shift" bar is 14× the expected noise floor. R₂_decoded 0.05 floor matches the §v2.4-proxy-4b PARTIAL floor (cross-sweep comparability) and is 21× the tournament baseline point estimate (0.0024), so any R₂_decoded lift to ≥0.05 is a genuine signal. F_AND gate at 18/20 matches the SWAMPED row in §v2.4-proxy-5b for consistency.

## Degenerate-success guard (required)

- **Tournament-arm-reproduces-too-cleanly artefact:** if `selection_mode=tournament` reproduces §v2.4-proxy-4d numbers with suspiciously narrow within-cell variance (all 20 seeds produce nearly identical R_fit_999), inspect unique_genotypes and final-population edit-distance histogram. The tournament baseline is healthy at R_fit_999 ≈ 0.723 and unique_genotypes ≈ 990/1024; deviation from these secondaries would flag an infrastructure bug (e.g., seeds are not being propagated correctly through the new selection_mode code path).
- **Ranking/truncation convergence starvation:** at `selection_top_fraction=0.5`, ranking/truncation keep only the top 512/1024 individuals as parents. If the seeded canonical tape is in the bottom 512 at generation 1 (it won't be — it solves the task — but if the seeded fraction doesn't dominate early), the seeded individual could be culled before establishing a foothold. Detection: per-seed best-of-run fitness at generation 1 (must be 1.0 for the seeded individual). If any seed shows gen-1 best_fitness < 1.0, the seeding mechanism has a bug.
- **DECODER-INTRINSIC false positive via budget ceiling:** if ranking/truncation converge faster but hit the same 1500-generation endpoint as tournament, the populations may be at the same equilibrium from different kinetic paths. Detection: per-generation R_fit_999 curves should differ during burn-in (faster convergence under ranking/truncation is expected and non-artifactual); only the final-generation comparison enters the outcome grid.
- **Selection-mode non-monotonicity:** if ranking shows shift but truncation does not, inspect whether `selection_top_fraction=0.5` is creating different effective population sizes under ranking vs truncation (ranking samples all 512 elites proportionally; truncation directly copies them). The non-monotone signature would be PARTIAL-COUPLED, not SELECTION-COUPLED.

## Statistical test

- **Primary:** per-cell bootstrap 95% CI on `R₂_decoded`, `R₂_active`, and `R_fit_999`. Per-mode comparison uses paired McNemar on `F_AND` across `selection_mode` values on shared seeds (gating the SWAMPED row at raw α = 0.05).
- **Classification (principle 22):** **exploratory.** Does not gate a new findings.md claim; informs the decoder-specific mechanism split already ACTIVE in `docs/chem-tape/findings.md#proxy-basin-attractor`. Results that clearly land on DECODER-INTRINSIC would earn a findings.md narrowing note, but the claim itself (wide solver neutral network under BP_TOPK) is already promoted — this probe adds a "selection-insensitive" qualifier, not a new claim.
- **Family:** n/a (exploratory). Proxy-basin FWER family size unchanged at 3; corrected α stays at 0.05/3 ≈ 0.017.

## Diagnostics to log (beyond fitness)

- Per-seed × per-cell `F_AND`, `best-of-run` fitness (expected 20/20 and 1.0 respectively at sf=0.01 under all selection modes)
- Per-cell `R₂_decoded`, `R₂_active`, `R₂_raw`, `R_fit_999`, `unique_genotypes`, `final_generation_mean` (via `analyze_retention.py`)
- Edit-distance histogram `{0, 1, 2, 3, ≥4}` decoded-view per cell
- Per-cell bootstrap 95% CI on all three R₂ views + R_fit_999
- Per-seed best-of-run hex at sf=0.01 per mode — confirm byte-for-byte canonical across all 60 seeded runs; deviations flag degenerate-success guard
- Per-generation R_fit_999 trajectory (first 100 generations) per cell — detects differential burn-in kinetics between selection modes without changing the final-generation outcome comparison
- **Paired R_fit_999 difference (ranking − tournament) and (truncation − tournament) per seed at sf=0.01** — the direct within-sweep contrast metric that resolves DECODER-INTRINSIC vs SELECTION-COUPLED

## Scope tag (required for any summary-level claim)

**If this experiment's result enters a findings.md narrowing:**
`within-family · n=20 per cell (6 cells) · at pop=1024 gens=1500 mutation_rate=0.03 elite_count=2 crossover_rate=0.7 v2_probe disable_early_termination=true · on sum_gt_10_AND_max_gt_5 natural sampler · BP_TOPK(k=3, bp=0.5) preserve · selection_mode ∈ {tournament, ranking, truncation} · seeded canonical 12-token AND body at sf ∈ {0.0, 0.01}`.

Not expected to broaden the top-line `proxy-basin-attractor` claim — this probe adds a "selection-insensitive" qualifier (DECODER-INTRINSIC) or a "selection-geometry component" qualifier (SELECTION-COUPLED / PARTIAL-COUPLED) to the already-promoted claim.

## Decision rule

- **DECODER-INTRINSIC →** update `docs/chem-tape/findings.md#proxy-basin-attractor`: the wide solver neutral network under BP_TOPK is selection-insensitive. Add qualifier "selection-insensitive" to the one-sentence claim. Representation-layer interventions (evolvable chemistry, AutoMap) become the principal direction for BP_TOPK. Queue an n=20 replication block on independent seeds (20-39) before paper-level citation.
- **SELECTION-COUPLED →** update findings.md: tournament selection is a load-bearing ingredient in the wide solver neutral network. Selection-layer probes (lexicase, Pareto-front multi-objective) become the natural Tier-2 direction per the post-4d decision tree. Update `docs/chem-tape/arcs/proxy-basin-attractor-arc.md` open-Q #1 to "resolved: tournament-coupled."
- **R₂-ONLY SHIFT →** update findings.md with a two-component qualifier: cloud width = decoder geometry (selection-insensitive); canonical position within cloud = selection-sensitive. This is the most theoretically detailed outcome. Queue a narrowing sweep with `selection_top_fraction ∈ {0.3, 0.5, 0.7}` under ranking mode to characterise the selection-pressure → canonical-position curve.
- **PARTIAL-COUPLED →** interpret per-mode; do not update BP_TOPK scope globally. Note that ranking and truncation have distinct profiles; the specific selection-pressure dimension that matters is unresolved. Queue a targeted probe with a third selection variant (e.g., fitness-proportionate roulette) to triangulate.
- **SWAMPED →** repeat at `selection_top_fraction=0.7` (larger breeding pool) if SWAMPED was triggered only under the sharper selection mode. Do not claim decoder-intrinsic if the non-tournament cells were uninformative.
- **BASELINE-DRIFT →** investigate immediately; no findings-layer update until tournament baseline reproduces within CI of commit `cca2323`.
- **INCONCLUSIVE →** update the outcome grid per principle 2b, then re-interpret.

---

*Audit trail.* Seven outcome rows (principle 2 + 2b; DECODER-INTRINSIC, SELECTION-COUPLED, R₂-ONLY SHIFT, PARTIAL-COUPLED, SWAMPED, BASELINE-DRIFT, INCONCLUSIVE — the four non-trivial cells of the R_fit × R₂_decoded grid plus infrastructure / swamp guards). §v2.4-proxy-4d decode-consistent follow-up numbers are the measured baseline at selection_mode=tournament (principle 6). Internal control is the within-sweep selection_mode contrast on shared seeds 0..19 (principle 1). Degenerate-success guard covers three distinct artefacts (principle 4). Principle 20 not triggered (sampler unchanged). Principle 22 classified as exploratory; does not grow the proxy-basin FWER family. Principle 23 gate preserved — selection_mode=tournament cells must reproduce §v2.4-proxy-4d baselines. Principle 25 satisfied: R_fit_999, R₂_decoded, R₂_active, R₂_raw produced by `experiments/chem_tape/analyze_retention.py` via `dump_final_population=True`; per-generation trajectory from `history.npz:r_fit_999_curve` (pending infra addition — see engineering prerequisite §1 above, which must also add this column to the NPZ writer). Principle 26 satisfied — both R_fit_999 and R₂_decoded are primary grid axes, not diagnostic. Principle 27 satisfied — metric definitions cited verbatim from the module's `METRIC_DEFINITIONS` dict. Decision rule commits to specific arc-doc / findings-layer edits per outcome (principle 19). Prereq file: `Plans/prereg_v2-4-proxy-5c-nontournament.md`.
