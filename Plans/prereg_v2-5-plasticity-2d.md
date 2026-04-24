# Pre-registration: §v2.5-plasticity-2d — capacity-matched random-δ-sampling control of §v2.5-plasticity-2c's F_AND_test capacity-scaling observation

**Status:** READY-TO-LAUNCH v7.2 (post-compute amendment; codex-v7-review-1 FAIL (2 P1 + 1 P2), codex-v7-review-2 FAIL (persistent 4-cell refs + stale counts + determinism-check gap + Row 6 trigger), and codex-v7-review-3 FAIL (queue.yaml notes still 8/80 + banner only named one file) all discharged in-place; scope = budget=40 primary-confirmatory cell; supporting cells {5, 10, 20} deferred to §2d-supplemental; partial-run count corrected everywhere to 18/80 with full breakdown (5/5/4/4 at budgets 5/10/20/40); determinism check implemented as committed script `scripts/check_v2d_overlap_determinism.sh` covering both `final_population.npz` and `result.json`) · target commit `TBD` (will be pinned post-commit) · 2026-04-24.

*Codex review history: v1 FAIL (5 P1 + 3 P2) → v2 FAIL (2 P1 + 2 P2) → v3 PASS-WITH-P2 (0 P1 + 2 P2 discharged in-place) → v4 FAIL post-engineering (2 P1 + 4 P2; engineering items 1-5 discharged but new §2d helpers were dead from the analyzer entrypoint) → v5 FAIL (2 new P1 + 2 P2 surfaced by deeper inspection on argmax aggregation and missing-k-draw-data gap) → v6 FAIL (1 P1 + 1 P2: 4-tuple all-or-none enforcement was single-column and prereg had stale 3-tuple wording) → v6 post-engineering codex-v7 PASS-WITH-P2 (discharged READY-TO-LAUNCH at commit ee44b1c) → **v7 post-compute amendment codex-review FAIL** (2 P1 + 1 P2: partial-run count mis-stated; 4-cell body text still present; line 7 wording leftover) → all P1 + P2 discharged in this working text. See Amendment history.*

---

> **⚠ v7 SCOPE OVERRIDE (authoritative — supersedes any conflicting v1–v6 body text below):**
>
> **Scope:** §2d-primary is now exactly ONE cell: `random_sample_threshold × plasticity_budget=40 × seeds 20..39` = 20 new runs. Supporting cells at `plasticity_budget ∈ {5, 10, 20}` are **DEFERRED to §2d-supplemental** — NOT measured and NOT consumed in §2d-primary analysis.
>
> **Body-text status:** the v1–v6 Setup / Hypothesis / Outcome / Statistical-test / Scope-tag / Diagnostics / Checklist sections below were written for the ORIGINAL 4-cell / 80-run design. They are preserved for provenance. **Where v7 conflicts with v1–v6 body text, v7 wins.** The specific locations where v7 differs have been rewritten in-line and are flagged `(v7 rewrite)` at the edit site. Any residual 4-cell language outside those flags is historical context only and does NOT bind execution.
>
> **Partial-run provenance:** the 2026-04-23 launch at v6 engineering commit `ee44b1c` was SIGTERM'd at 10800s; **18 runs completed** (5 at budget=5 seeds 20..24; 5 at budget=10 seeds 20..24; 4 at budget=20 seeds 20..23; 4 at budget=40 seeds 20..23) and persist on disk at `experiments/output/2026-04-23/v2_5_plasticity_2d/`. This includes **4 runs at the primary-confirmatory cell (budget=40, seeds 20..23)**. Researcher observation disclosure: directory names, `config.yaml` presence, and `result.json`/`final_population.npz` file counts were observed; no `F_AND_test_plastic` value or winner metadata was read. **v7 explicitly quarantines this data: §2d-primary analysis consumes ONLY the NEW 2026-04-24 sweep output at `experiments/output/2026-04-24/v2_5_plasticity_2d_primary_b40/` (fresh 20-run sweep at same seeds 20..39). The 2026-04-23 partial data is NOT a baseline and NOT consumed by any §2d-primary routine.** Post-sweep determinism check: because v7 introduces no code changes, the 4 overlap seeds (20..23, budget=40) MUST produce byte-identical `final_population.npz` AND `result.json` at the new sweep (both files checked by `scripts/check_v2d_overlap_determinism.sh`); divergence on ANY file at ANY overlap seed routes Row 6 SWAMPED (reason: determinism-failure) and the chronicle halts.
>
> **Supporting-cell (§2d-supplemental) plan:** supporting cells {5, 10, 20} will be queued as a separate sweep when compute permits (not pre-registered here). Descriptive-only statistical treatment (§26). Direction-only routing still applies.

---

*This prereg pre-registers a capacity-matched control for §v2.5-plasticity-2c's F_AND_test capacity-scaling observation (Row 2 PARTIAL at CI-boundary knife-edge, chronicle commit `1112e36`: paired-bootstrap 97.5% CI [0.00, +0.50]; point est +0.25; monotone non-decreasing point-estimate trend 0.35 → 0.50 → 0.50 → 0.60 across plasticity_budget ∈ {5, 10, 20, 40}). The interpretive question that motivates §2d — "is the F_AND_test capacity scaling about within-lifetime adaptation, or just about giving the system another cheap degree of freedom at matched nominal k?" — is discussed as framing only; **§2d's pre-registered routing is direction-only on the paired F_AND_test_plastic axis at matched `plasticity_budget`, without pre-commitment to any mechanism-level naming**. Mechanism-interpretation narrative is deferred to chronicle time under §16c discipline (cf. codex-v1 P1-3, P1-4 corrections). (v7 correction 2026-04-24: "matched compute" wording replaced throughout with "matched `plasticity_budget`" — the two mechanisms differ in whether they exhaust k draws, so VM work is NOT matched at matched k; the §17a 3-variable process bundle already named this as variable (c) stopping semantics. See v7 amendment history block.)*

*The design compares the **existing** `rank1_op_threshold` mechanism to a **new** `random_sample_threshold` mechanism at matched plasticity_budget: k independent uniform-continuous draws from `[-b, +b]`, evaluate each draw's train_fitness_plastic on 48 train examples, select the draw maximizing train_fitness_plastic, evaluate that δ on 16 held-out test examples. The `plasticity_mechanism` axis is a single nominal config field, but per §17a it carries a bundle of co-moving process variables: (a) δ-selection procedure (gradient-like sign-update vs argmax-on-train over k uniform draws), (b) reachable-δ space (integer lattice bounded by budget-many signed steps vs continuous `[−b, +b]`), (c) stopping semantics (update-loop halts on correct-classification vs always-k-draws). Matched on: `plasticity_budget` (k=40), task, sampler, seeds, pop, gens, mr, tournament_size, elite_count, δ scale, sf, alphabet, train/test split, scoring. **NOT matched on eval-time VM work** (v7 correction 2026-04-24): `random_sample_threshold` always evaluates k independent train_fitness draws per individual while `rank1_op_threshold`'s update loop halts early on correct-classification — this asymmetry IS the §17a variable-(c) stopping-semantics bundle element, already named in the §17a audit block. The prereg's outcome rows route on **direction of paired F_AND_test_plastic difference at budget=40** only; the 3-variable process bundle is named honestly at every qualifier per §17a.*

## Question (one sentence)

**At matched `plasticity_budget`=40 (20 paired seeds 20..39) on `sum_gt_10_AND_max_gt_5` (Arm A, sf=0.0, pop=512, gens=1500, mr=0.03), does rank-1 operator-threshold plasticity's gradient-like directed-update δ-selection produce higher `F_AND_test_plastic` than uniform-continuous random-δ-sampling `[-b, +b]` with best-on-train selection at matched k, as measured by a paired-seed bootstrap 98.333% CI (Bonferroni-corrected at family size 3) on the per-seed difference `F_AND_test_plastic[plastic, seed=s] − F_AND_test_plastic[random, seed=s]` for s ∈ {20..39}?**

## Hypothesis

**Primary confirmatory statistic (single; authoritative for all row clauses):** `f_and_test_plastic_paired_boot_ci_plastic40_vs_random40` — seed-bootstrap 98.333% CI on the per-seed paired difference `F_AND_test_plastic[mechanism=rank1_op_threshold, budget=40, seed=s] − F_AND_test_plastic[mechanism=random_sample_threshold, budget=40, seed=s]` for s ∈ {20..39}, n=20 paired differences. 10 000 resamples via `numpy.random.default_rng(seed=42)`, CI quantiles [0.8333%, 99.1667%]. Bonferroni-corrected at family size 3 per §22a/§22b (see Statistical test block). **This is the ONLY routing statistic** for §2d's outcome grid; rows fire on direction only (CI_lo > 0 / CI_hi < 0 / overlap plus point-estimate sign).

**Sample space framing (interpretive context for the reader; NOT pre-committed mechanism-level interpretation per codex-v1 P1-3 correction):**

> §2d is designed as a control for "adaptive structure vs unconstrained slack." The uniform-continuous `[-b, +b]` support intentionally gives the random control a **broader search surface** than plastic's reachable δ space (plastic's reachable δ is a subset of the integer-scaled lattice `{−k·δ, …, +k·δ}` in budget-k steps; random-sample covers the full continuous interval). This framing anticipates the *direction* of the routing decision but does not pre-commit the mechanism-name attached to either outcome — that naming happens at chronicle time with a full §16c falsifiability block if any name is proposed. Readers should note:
>
> - Budget=5 is interpretively noisy because uniform-continuous over `[-5, +5]` is richer than plastic's 5-step trajectory; budget=5 is **descriptive-only** and does not enter any routing clause. Budget=10 and budget=20 are reported as chronicle-time descriptive context across mechanisms (see §26 demotion below); they are NOT in row conjunctions either (codex-v1 P1-1, P1-2 corrections — supporting-cell axis cannot carry routing weight under the §25b discipline because its distribution at cross-mechanism cells is not known from precedent).

**Mechanism naming: DEFERRED for this prereg** (§16c falsifiability block empty). No mechanism name is pre-registered and no mechanism name is used as a routing variable, outcome-row title, or decision-rule gate. Candidate-name labels (e.g., "plasticity-specific adaptation," "extra-slack-sufficient," "Baldwin-at-operator-level," or new labels) may appear in explanatory prose below (Hypothesis framing, decision-rule narrative, scope-tag clarifications) **solely to describe chronicle-time interpretive options**; at every such appearance the label is explicitly scoped "chronicle-time only under §16c" and does NOT gate any prereg-level routing. Candidate names are evaluated at chronicle time, gated by the §16c hard-gate requirement of ≥ 3 falsifiable predictions each tied to a specific named experiment. §2d's outcome provides one axis of directional evidence that a chronicle-time naming round may use as **one** such falsifier (if a name is proposed and that falsifier is explicitly pre-committed in the chronicle's §16c block), but this prereg does not itself propose a name nor pre-commit any name's falsifier list. (Codex-v1 P1-4 correction: v1 silently invoked `Baldwin-at-operator-level` as a named object whose falsifiers this prereg could discharge; v2 strips all prereg-level routing semantics from names while v3 — per codex-v2 P2-2 + codex-v3 P2-1 discharges — scopes the stronger "no name appears anywhere" claim down to the accurate "no name is a routing variable.")

**H1-DIRECTION-POSITIVE (plastic > random at budget=40):** paired-bootstrap 98.333% CI excludes 0 on the POSITIVE side (`CI_lo > 0`) AT BUDGET=40. Routing (direction-only): `findings.md#plasticity-narrow-plateau` NARROWS with scope `at tested confirmatory cell plasticity_budget=40, rank-1 operator-threshold plasticity's F_AND_test_plastic exceeds uniform-continuous random-δ-sampling's F_AND_test_plastic on the paired seeds 20..39 bootstrap CI basis`. Mechanism-name interpretation (plasticity-specific vs other readings) is chronicle-time only under §16c.

**H0-OVERLAP (no directional evidence at budget=40):** paired-bootstrap 98.333% CI INCLUDES 0 AT BUDGET=40 AND paired point estimate `F̂_plastic(40) − F̂_random(40) ≤ 0` (including tie). Routing (direction-only): `findings.md#plasticity-narrow-plateau` BROADENS with qualifier `at tested confirmatory cell plasticity_budget=40, no directional evidence (CI overlaps 0 and point estimate is non-positive) between rank-1 operator-threshold and uniform-continuous random-δ-sampling at matched `plasticity_budget``. Mechanism-name interpretation (extra-slack-sufficient vs other readings) is chronicle-time only under §16c; rank-2 escalation deprioritized pending chronicle-time interpretation.

**H-partial (directional but CI-inconclusive):** paired-bootstrap 98.333% CI INCLUDES 0 AT BUDGET=40 AND paired point estimate `F̂_plastic(40) − F̂_random(40) > 0` strictly. Routing: no `findings.md` change; report effect size + CI; budget ≥ 80 follow-up under user judgment (not pre-committed); `plasticity-narrow-plateau` status unchanged.

**H-reverse (random > plastic at budget=40):** paired-bootstrap 98.333% CI EXCLUDES 0 on the NEGATIVE side (`CI_hi < 0`) AT BUDGET=40. Routing (direction-only): `findings.md#plasticity-narrow-plateau` BROADENS with qualifier `at tested confirmatory cell plasticity_budget=40, uniform-continuous random-δ-sampling's F_AND_test_plastic exceeds rank-1 operator-threshold plasticity's on the paired seeds 20..39 bootstrap CI basis`. Mechanism-name interpretation (including any falsification of candidate names) is chronicle-time only under §16c; investigate infrastructure before naming (e.g., directed-update locking onto a local optimum unreachable by discrete-step gradient that random draws routinely escape is one chronicle-time hypothesis to consider, not a pre-committed mechanism claim).

**H-SWAMPED (infrastructure):** `initial_population_canonical_count > 0` on any run (sf=0.0 invariant violated) OR **hash collision** between the §2d random-sample budget=40 cell and any §2c reused plastic budget=40 cell (dedup accidentally short-circuits one of the 20 new runs) `(v7 rewrite: 80 → 20)` OR **seed-integrity pre-check fails** (any missing/duplicated/extra seed in either the plastic budget=40 reference subset from §2c or the random-sample budget=40 cell per Setup § "Seed-integrity pre-check") OR **mechanism-sanity pre-check fails** (random-sample budget=40 cell's `delta_final` distribution violates uniform-`[-b, +b]` support bounds, OR per-run k-draw summary shows draws outside `[−b, +b]` support or collapsed std per Setup § "Mechanism-sanity pre-check" — both support-bound and draw-distribution checks are mandatory at launch per codex-v1 P1-5 correction) OR **determinism pre-check fails** `(v7 new)` (any of the 4 overlap seeds 20..23 at budget=40 produces `final_population.npz` NOT byte-identical to the 2026-04-23 partial data at commit ee44b1c; v7 codex-review P1-1 discharge). Routing: stop and inspect; no routing until infrastructure check passes.

**Secondary diagnostics (descriptive-only; NO confirmatory-test status; NO α budget; NO routing clauses — explicit §26 demotion, inherits §2c precedent). Expanded in v2 to include supporting-cell cross-mechanism sign information (per codex-v1 P1-1 correction — previously routed in row clauses, now demoted to §26 chronicle-time discipline):**

- **Supporting-cell cross-mechanism per-cell point estimates and 98.333% seed-bootstrap CIs at plasticity_budget ∈ {5, 10, 20}** — `(v7 rewrite: DEFERRED to §2d-supplemental; NOT measured in §2d-primary and NOT consumed by any §2d-primary analysis routine. The v1–v6 intent of §26 chronicle-time descriptive context on these budgets is preserved for §2d-supplemental when that sweep runs.)` Original v1–v6 intent: reported descriptively at chronicle time; paired point-estimate signs at those budgets reported per §26 discipline; sign-flip or dramatic pattern would flag §2b grid-miss for follow-up prereg. Supporting cells DO NOT gate routing at chronicle time.
- `top1_winner_overhead` per winner across cells × mechanisms
- `top1_winner_plasticity_active_count` per winner across cells × mechanisms
- `top1_winner_levenshtein_uncapped` per winner across cells × mechanisms
- `top1_winner_attractor_category` per winner across cells × mechanisms
- `top1_winner_canonical_token_set_size` per winner across cells × mechanisms
- `top1_winner_baldwin_gap` per winner across cells × mechanisms (note: for random_sample, `test_fitness_frozen` still evaluates at δ=0; `baldwin_gap` measures "does the selected random-sample δ help over δ=0 on test?" — meaningful comparator to plastic's analogous quantity)
- per-cell delta_final_std_mean (per-cell std of `delta_final` across seeds; ancillary rng-sanity diagnostic)
- per-cell GT_bypass_fraction
- **per-run k-draw summary at every random-sample cell** — (min_draw, max_draw, std_draws, argmax_index) over the k uniform draws for each individual's δ-selection; per-run aggregation reports top-1 winner's full 4-tuple (min_draw, max_draw, std_draws, argmax_index) to CSV columns winner_k_draw_{min,max,std} + winner_k_argmax_index. Mandatory at launch per codex-v1 P1-5 correction (4-tuple fully enforced per codex-v6 P1-1: all four columns checked for presence in Guard-6(c)); not deferrable.

**§26 explicit demotion rationale (mirrors §2c):** §2c observed all six secondary axes STABLE across plasticity_budget at a single mechanism. No pre-experiment basis to pre-commit cross-mechanism thresholds on these axes at the 98.333% CI discipline — any observed mechanism-dependence would be a chronicle-time §2b grid-miss discovery for a follow-up prereg, not a routing clause here. Chronicle-time: if any secondary axis shows a dramatic pattern not anticipated by §2c's stability observation, the chronicle reports it as a chronicle-time §2b grid-miss and the follow-up prereg enumerates the observed pattern. Parallel to §2c's own §26-demoted handling.

**Prediction linkage to prior experiments:**

- §v2.5-plasticity-2c Row 2 PARTIAL (chronicle commit `1112e36`, prereg commit `06e8732`): paired-bootstrap 97.5% CI [0.00, +0.50] on `F_AND_test_plastic[budget=40] − F_AND_test_plastic[budget=5]` (plastic mechanism, sf=0.0 Arm A); point est +0.25; monotone non-decreasing point-estimate trend 0.35 → 0.50 → 0.50 → 0.60. §2c's CI-boundary PARTIAL is what §2d is controlling for: the observed capacity scaling could be plasticity-specific OR extra-slack-sufficient, and the §2c design cannot distinguish.
- §v2.5-plasticity-2a pooled n=40 budget=5 plastic anchor (data commit `7361631`): F_AND_test_plastic = 14/40 = 0.35; 97.5% seed-bootstrap CI [0.20, 0.525].
- §v2.5-plasticity-2a budget=5 seeds 20..39 subset (n=20 in the §2a primary cell): F_AND_test_plastic = 7/20 = 0.35.
- §v2.5-plasticity-2a frozen control (seeds 20..39, n=20, data commit `7361631`): F_AND_test = 0/20 (not relevant as a direct baseline for §2d's paired test; reported for FWER-family provenance).
- §v2.5-plasticity-2a winner inspection (commit `00d00e8`): at pooled n=40 budget=5, per-winner Baldwin gap mean +0.364 (range [−0.125, +0.688]); plasticity-active-token count median 6 in plastic vs 3 in frozen.
- §v2.5-plasticity-1a at commit `4ceb22b`: opened `plasticity-narrow-plateau` FWER family at size 1 (FALSIFIED at sf=0.01 seeded, α=0.05 pre-correction).
- `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md`: diagnosis class `selection-deception`.
- `docs/chem-tape/runtime-plasticity-direction.md`: mechanism ladder (rank-1 = current tested rung). §2d's outcome gates whether rank-2 or alternative directions take priority.

## Setup

- **Sweep file `(v7 rewrite)`:** `experiments/chem_tape/sweeps/v2/v2_5_plasticity_2d_primary_b40.yaml` (v7 single-cell YAML; the v1–v6 `v2_5_plasticity_2d.yaml` is preserved in-tree but its queue entry timed out on 2026-04-23 and its 18 partial run_dirs are quarantined — see v7 banner and v7 amendment history).
- **Arms / conditions `(v7 rewrite)`:** Arm A only (direct GP). BP_TOPK EXCLUDED per §v2.5-plasticity-1a structural `R_fit` ceiling caveat (same as §v2.5-plasticity-2a/2c). **ONE new `random_sample_threshold` cell at plasticity_budget=40:**
  - `arm=A, plasticity_enabled=true, plasticity_mechanism=random_sample_threshold, plasticity_budget=40, seed_fraction=0.0, generations=1500, pop_size=512, mutation_rate=0.03, tournament_size=3, elite_count=2, crossover_rate=0.7, plasticity_delta=1.0, plasticity_train_fraction=0.75, tape_length=32, n_examples=64, holdout_size=256, alphabet=v2_probe, task=sum_gt_10_AND_max_gt_5, disable_early_termination=true, dump_final_population=true, backend=mlx` × 20 seeds = **20 new runs**.
  - **`rank1_op_threshold` budget=40 cell is REUSED from §2c at commit `06e8732` (n=20, seeds 20..39).** NOT re-run here. The 20 per-winner artifacts for plastic budget=40 seeds 20..39 are on disk at the §2c sweep output directory.
  - Supporting cells {5, 10, 20} are NOT part of §2d-primary; deferred to §2d-supplemental (separate sweep, not pre-registered here).
  - No new frozen-control cell needed (§2d is a cross-mechanism comparison, not a plasticity-vs-frozen comparison).
- **Seeds `(v7 rewrite)`:** **seeds 20..39** on the single new `random_sample_threshold` budget=40 cell. Identical seed block to §2c's plastic budget=40 cell. The paired-seed structure on shared seeds 20..39 at budget=40 is the internal-control contrast (principle 1).
- **Fixed params `(v7 rewrite: single budget, not 4)`:** pop=512, gens=1500, mr=0.03, crossover_rate=0.7, tournament_size=3, elite_count=2, tape_length=32, n_examples=64, alphabet=v2_probe, task=sum_gt_10_AND_max_gt_5, disable_early_termination=true, dump_final_population=true, backend=mlx, plasticity_delta=1.0, plasticity_train_fraction=0.75, holdout_size=256, seed_tapes="" (no canonical seeding at sf=0.0). All params byte-identical to §2c's plastic budget=40 cell EXCEPT `plasticity_mechanism` (new value `random_sample_threshold`). The `plasticity_budget` is matched at 40 for the per-budget cross-mechanism paired test.

**Shared-seed extraction (plastic budget=40 reference for the paired confirmatory test):** the primary confirmatory statistic compares random-sample budget=40 (20 new runs at seeds 20..39) vs plastic budget=40 on the same 20 seeds. The plastic budget=40 per-seed indicators are extracted by:

1. Load `experiments/output/<§2c sweep output dir>/plasticity.csv` (post-§2c data at commit `06e8732` or its §2c sweep-output commit; the canonical path is named in the sweep YAML and queue entry).
2. Filter to rows where `plasticity_enabled == 'True' AND plasticity_mechanism == 'rank1_op_threshold' AND plasticity_budget == '40' AND arm == 'A' AND seed_fraction == '0.0'`.
3. Retain only rows with `seed ∈ {20, 21, ..., 39}` (n=20).
4. Compute per-seed binary indicator `best_fitness_test_plastic >= 1.0 - 1e-9`.
5. Join to random-sample budget=40 per-seed indicators (new runs at seeds 20..39) on the `seed` column; paired n=20 difference vector.

**Seed-integrity pre-check (mirrors §2c's pre-check exactly):** before forming the paired n=20 vector, verify that **exactly 20 seeds** are present in the filter-retained plastic budget=40 subset (seeds 20..39) AND **exactly 20 seeds** are present in the random-sample budget=40 cell AND **every seed ∈ {20..39} appears exactly once** in each subset. Any deviation — missing seed (fewer than 20), duplicated seed (same seed twice), or extra seed (seed outside {20..39}) in either cell — **routes the chronicle verdict to Row 6 (SWAMPED)**. Implemented in the paired-bootstrap routine (Status-transition checklist item 1(h)) with explicit assertion naming which cell and which seed anomaly triggered the SWAMPED routing.

**Mechanism-sanity pre-check (new in §2d; fires pre-confirmatory-test; all sub-checks mandatory per codex-v1 P1-5 correction):** at every `random_sample_threshold` cell, verify:
1. Per-run `delta_final` satisfies `−budget ≤ delta_final ≤ +budget` (uniform-continuous support bounds on the selected draw; any violation indicates a sampling-range bug).
2. Per-cell `std(delta_final)` across 20 seeds is `≥ 0.01` (non-degenerate rng at the across-seeds aggregation — zero variance across seeds would flag that every seed's argmax converged on the same discrete draw).
3. Per-cell `mean(|delta_final|)` is within `[0, budget]` with a non-degenerate distribution (not all individuals converged on `delta_final = 0`).
4. **Per-run k-draw support-bound check (MANDATORY at launch; closes the gap that cell-level `delta_final` cannot see):** every logged per-individual k-draw tuple `(min_draw, max_draw, std_draws, argmax_index)` satisfies `−budget ≤ min_draw ≤ max_draw ≤ +budget` strictly AND `std_draws ≥ 0.05 · budget` (non-degenerate rng at the per-individual level) AND `argmax_index ∈ [0, k−1]`. Per-run aggregation emits the top-1 winner's `(min_draw, max_draw, std_draws, argmax_index)` to CSV columns `winner_k_draw_min`, `winner_k_draw_max`, `winner_k_draw_std`, `winner_k_argmax_index` (4-element schema consistent with Guard-6 (c), Diagnostics list, METRIC_DEFINITIONS `random_sample_mechanism_draw_spread`, and Status-transition checklist item 1(g) — codex-v3 P2-2 alignment). Any per-individual violation flags the run; any run flag routes to Row 6 SWAMPED.

Any sanity-check failure routes to Row 6 (SWAMPED). These are infrastructure invariants, not confirmatory axes; a genuine research finding of "all random-sample individuals converged on δ=0" would be diagnosed post-SWAMPED-inspection, not routed through the primary outcome grid.

- **Est. compute (v6 projection; superseded by v7):** per-run wall for `random_sample_threshold` at budget=k was originally projected to match plastic budget=k timings: budget=5 ≈ 7 min, budget=10 ≈ 12 min, budget=20 ≈ 18 min, budget=40 ≈ 30 min; parallel wall at 10 workers projected ~2.5-3h total for 80 runs; queue timeout 10800s. **Observed at 2026-04-23 launch (v7 correction):** ~8× over projection — budget=5 ≈ 54 min, budget=10 ≈ 102 min (linear-in-budget scaling holds). Root cause: `random_sample_threshold` always evaluates k train_fitness draws per individual while `rank1_op_threshold` short-circuits on correct-classification, so at matched `plasticity_budget` VM work is NOT matched — see §17a variable-(c). **v7 scope:** run only the budget=40 primary-confirmatory cell (20 runs); supporting cells {5, 10, 20} deferred to §2d-supplemental. Projected v7 per-run wall at budget=40: ~6.7h (linear extrapolation). Parallel wall at 10 workers over 20 runs: 2 waves × 6.7h ≈ 13.4h. v7 queue timeout **57600s (16h, ~1.2× headroom)** per codex-consult 2026-04-24 recommendation.
- **Related experiments:** §v2.5-plasticity-2c chronicle commit `1112e36`, prereg commit `06e8732`; §v2.5-plasticity-2a primary (commit `4d331ad`); §v2.5-plasticity-2a-nexp-budget5 (commit `9ad15ea`); §v2.5-plasticity-2a winner-inspection scratch (commit `00d00e8`); §v2.5-plasticity-1a at commit `4ceb22b`; diagnosis doc `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md`; `docs/chem-tape/runtime-plasticity-direction.md`.

**Principle 17a audit:** the `plasticity_mechanism` axis is a single nominal config field, but per §17a it carries a **3-variable process bundle** that must be named honestly in every qualifier (codex-v1 P2-2 correction — v1 alternated between "only plasticity_mechanism differs" and the bundle audit; v2 is consistent throughout). Derived *process* variables co-moving with the mechanism choice: (a) δ-selection procedure (gradient-like sign-step vs argmax-on-train over k uniform draws); (b) per-individual reachable-δ space (integer lattice of size `2·budget + 1` for plastic vs continuous `[−budget, +budget]` for random); (c) stopping semantics (plastic applies ≤ budget updates, stopping when train is correctly classified; random always draws k samples, no early termination). All three are direct consequences of the mechanism choice — they ARE the mechanism. The prereg's outcome discrimination is therefore a **direction-only** comparison on the F_AND_test_plastic axis between the two mechanism-choice bundles at matched `plasticity_budget`=40; no sub-variable in the bundle is individually isolated. Mechanism-level interpretation (e.g., attributing a directional outcome to any one of the three co-moving variables) is chronicle-time §16c discussion only, not pre-committed by this prereg's routing. Principle 17b `(v7 rewrite)`: tested mechanism values ∈ {`rank1_op_threshold`, `random_sample_threshold`}; tested integer budget value = 40 (confirmatory); supporting cells {5, 10, 20} are DEFERRED to §2d-supplemental and NOT tested in §2d-primary. Scope qualifiers use verbatim tested-set `{40}`, not continuous-range phrasing; supporting cells do not enter any §2d-primary scope tag.

**Principle 20 audit:** sampler unchanged from §2c (`sum_gt_10_AND_max_gt_5` natural sampler, 75/25 train/test split, 48 train / 16 test, 256-example holdout). Not triggered.

**Principle 23 audit `(v7 rewrite)`:** the single §2d-primary random-sample budget=40 cell's params are byte-identical to §2c's plastic budget=40 cell EXCEPT `plasticity_mechanism`. Reusing §2c's budget=40 plastic data (seeds 20..39, n=20) requires that sweep YAML's hash-dedup NOT accidentally reuse plastic hashes for random-sample runs (mechanism is hash-relevant since it is NOT at the default when `random_sample_threshold`; `ChemTapeConfig.hash()` pops `plasticity_mechanism` only at its default `rank1_op_threshold`, so any non-default mechanism produces a distinct hash — already verified by `test_v2d_sweep_yaml_hashes_disjoint_from_v2c` which covers the original v1–v6 YAML; the new single-cell YAML's base section is unchanged and its paired list is a subset of the original paired list, so the hash-dedup discipline continues to hold for the budget=40 cell).

## Baseline measurement (required — principle 6 + 25)

**Baseline quantity 1 — plastic budget=40 F_AND_test_plastic seed-bootstrap 98.333% CI (n=20, seeds 20..39, reused from §2c):**

- Measurement: seed-bootstrap 98.333% CI on per-cell F_AND_test_plastic fraction using 20 per-seed binary indicators from §2c's budget=40 cell, 10 000 resamples via `numpy.random.default_rng(seed=42)`, CI quantiles [0.8333%, 99.1667%]. Matches `bootstrap_ci_spec` at the §2d family-α discipline.
- **Value (to be measured pre-data at Status-transition checklist item 2):** point estimate = **12/20 = 0.60** (from §2c chronicle commit `1112e36`); 98.333% CI = **to be computed** (expected wider than §2c's 97.5% CI of analogous cell).
- Rationale: direct per-cell descriptive comparator for the random-sample budget=40 cell. Principle 6 satisfied — threshold is data-derived, not imported.

**Baseline quantity 2 `(v7 rewrite)` — DEFERRED to §2d-supplemental.** The v1–v6 design computed plastic budgets {5, 10, 20} F_AND_test_plastic point estimates + per-cell 98.333% CIs as §26-demoted descriptive baselines. §2d-primary does NOT compute these; they move to §2d-supplemental. Historical note from §2c chronicle commit `1112e36` (for reader context only — not consumed by §2d-primary): budget=5 seeds-20..39: 7/20=0.35; budget=10: 10/20=0.50; budget=20: 10/20=0.50.

**Baseline quantity 3 — observational context from §2c chronicle (NOT pre-registered as baseline for routing clauses):**

- §2c chronicle commit `1112e36`: all six §26-demoted secondary axes STABLE across plasticity_budget (no significant differences across {5, 10, 20, 40}). Reported for chronicle-time context only; NOT pre-committed as routing thresholds (per §26 explicit demotion).

**Metric definitions (principle 27 — verbatim):** all existing metrics cited from `experiments/chem_tape/analyze_plasticity.py:METRIC_DEFINITIONS` verbatim (§2a + §2c entries). New metrics pre-committed verbatim in the METRIC_DEFINITIONS extensions section below.

**Measurement-infrastructure gate (principle 25):** the primary confirmatory statistic and secondary diagnostics require engineering extensions:

1. **Mechanism executor extension (`src/folding_evolution/chem_tape/plasticity.py`):** new `random_sample_threshold` branch in `adapt_and_evaluate_one` (or a sibling `adapt_and_evaluate_one_random_sample` function dispatched from `evaluate_population_plastic` on `cfg.plasticity_mechanism`). The branch:
   - Seeds a per-individual rng deterministically from `(cfg.seed, individual_index, cfg.hash())` so all subsequent draws are reproducible across runs sharing the same genotype and global seed.
   - Draws `k = cfg.plasticity_budget` independent samples from `rng.uniform(-k, +k)` (continuous).
   - For each δ sample, runs a full train-fitness evaluation on 48 train examples.
   - Selects the δ maximizing train_fitness_plastic (argmax; tiebreak: smallest-absolute-δ, then first-occurrence).
   - Sets the individual's `delta_final` to the chosen δ; computes the four (frozen/plastic × train/test) fitness values identically to the plastic path using the chosen δ.
   - Preserves byte-identical output dict schema; `has_gt` and downstream columns unchanged.
   - Engineering estimate: **~6-10h** (per session-prompt scratch doc).
   - Status: **pending infra extension** (Status-transition checklist item 1).

2. **Analyzer grouping-key extension (`experiments/chem_tape/analyze_plasticity.py:_cell_key`):** extend the grouping tuple from `(arm, plasticity_enabled, plasticity_budget, seed_fraction)` to `(arm, plasticity_enabled, plasticity_mechanism, plasticity_budget, seed_fraction)`. **Without this extension §2c's plastic budget=40 cell and §2d's random-sample budget=40 cell would collapse into the same cell key and per-cell summaries would double-count.** Engineering: ~30 min (cell_key + downstream summary field propagation + existing-row-backfill for plastic_mechanism column; existing §2a/§2c data already stores plasticity_mechanism per run so the backfill is pure read-side). Pytest coverage: verify old §2a/§2c CSVs still parse to the correct cells under new grouping (backward compatibility invariant — plasticity_mechanism defaults to rank1_op_threshold on existing runs).

3. **Paired-bootstrap CI routine (`analyze_plasticity.py` new function):** `paired_bootstrap_plastic40_vs_random40` — takes per-run CSV + cross-cell extraction and outputs a 98.333% CI tuple. Engineering: ~30 min. Pending.

4. **Per-cell 98.333% seed-bootstrap CI routine:** extension of existing `f_and_test_plastic_seed_boot_ci` to accept a quantile parameter (or new routine `f_and_test_plastic_seed_boot_ci_98_333`). Engineering: ~15 min. Pending.

5. **Per-cell mechanism-sanity diagnostics:** per-cell `delta_final` support-bound check (min/max/std) emitted in cell-level summary. Engineering: ~20 min. Pending.

6. **Glue:** paired-subset extraction routine, pytest coverage for the new mechanism (unit tests for k draws, uniform continuous sampling, seed reproducibility, best-on-train selection, mirror of plastic protocol on train/test split), sweep-YAML, queue entry, hash-dedup pytest, pilot timing, pre-data baseline CI precompute. Engineering: ~2-3h total.

Status-transition checklist item 1 covers all engineering; sweep does not launch until items 1-7 pass.

**Grouping-script attribution (principle 25 clarification) `(v7 rewrite)`:** after the `_cell_key` extension in step 2 above, the per-cell seed-bootstrap CI routine lives in `analyze_plasticity.py:summarize` and the grouping keys cover (arm, plasticity_enabled, plasticity_mechanism, plasticity_budget, seed_fraction) — for §2d-primary this resolves to exactly two cells at budget=40 (rank1_op_threshold reused from §2c + random_sample_threshold new from the v7 sweep). The paired-bootstrap routine lives in the NEW function `paired_bootstrap_plastic40_vs_random40` (Status-transition checklist item 1(h)) which takes the per-run CSV + cross-cell extraction as inputs and outputs a CI tuple. No new grouping wrapper script needed; the `summarize` function is the grouping surface.

## Internal-control check (required — principle 1)

- **Tightest internal contrast:** paired random-sample at budget=40 vs plastic at budget=40 on shared seeds 20..39 — holds task, sampler, seeds, pop, gens, mr, tournament_size, elite_count, sf, alphabet, δ scale, plasticity_train_fraction, train/test split, budget ALL fixed; the mechanism-choice bundle varies (single nominal config field `plasticity_mechanism`, but 3 directly-derived co-moving process variables per §17a audit: δ-selection procedure, reachable-δ space, stopping semantics). This is the primary confirmatory test.
- **Are you running it here? `(v7 rewrite)`** Yes — random-sample budget=40 at seeds 20..39 is the single new cell in §2d-primary; the shared-seed paired-bootstrap against reused §2c plastic budget=40 data is the confirmatory test.

## Pre-registered outcomes (required — principle 2 + 2b + 26)

**Axis structure (v2 — codex-v2 P1-1 correction to v1's stale "supporting-cell conjunction" sentence):** the primary routing axis is **1D** — the paired-bootstrap 98.333% CI on `F_plastic(40) − F_random(40)` at shared seeds 20..39, PLUS the paired point-estimate sign at budget=40 (used only for tie-breaking between PARTIAL and SATURATION when the CI includes 0; not a separate axis). No supporting-cell conjunction enters the routing. Supporting-cell cross-mechanism information at plasticity_budget ∈ {5, 10, 20} is explicitly §26-demoted to chronicle-time descriptive-only context (no outcome-table rows; parallel to §2c's §26-demoted handling of secondary axes). All other secondary axes also §26-demoted.

**Row precedence (v2):** rows evaluated in precedence order; the FIRST matching row fires. This resolves tie-ambiguity and multi-row collisions. Precedence: Row 6 (SWAMPED) → Row 5 (REVERSE) → Row 1 (PASS-POSITIVE) → Row 2 (PARTIAL) → Row 3 (SATURATION) → Row 4 (CATCHALL).

**Outcome grid (v2: 6 rows — Row 2 GRID-MISS-SUPPORTING from v1 REMOVED per codex-v1 P1-1/P1-2 corrections; supporting-cell axis §26-demoted to chronicle-time descriptive-only):**

| # | outcome | Conjunction (paired CI at budget=40 only) | Precedence |
|---|---------|------------------------------------------|------------|
| 6 | **SWAMPED** (infrastructure) | `initial_population_canonical_count > 0` on any run, OR hash-dedup accidentally short-circuits any new run, OR seed-integrity pre-check fails (missing/duplicated/extra seed in either cell per Setup § "Seed-integrity pre-check"), OR mechanism-sanity pre-check fails (any random-sample cell's `delta_final` violates uniform-`[-b, +b]` support bounds, OR per-run k-draw summary shows draws outside `[−b, +b]` or std-collapse, OR zero std across seeds, OR all individuals converged on δ=0 per Setup § "Mechanism-sanity pre-check"), OR any other infrastructure-fidelity failure. | 1st (highest) |
| 5 | **REVERSE — random > plastic at budget=40** (direction-only, §2b grid-miss on anticipated direction) | Paired-bootstrap 98.333% CI on `F_plastic(40) − F_random(40)` EXCLUDES 0 on the NEGATIVE side (`CI_hi < 0`). | 2nd |
| 1 | **PASS-POSITIVE — plastic > random at budget=40** (direction-only routing; mechanism-name DEFERRED to chronicle) | Paired CI excludes 0 on POSITIVE side (`CI_lo > 0`) AT BUDGET=40. | 3rd |
| 2 | **PARTIAL — directional but CI-inconclusive** | Paired CI INCLUDES 0 AT BUDGET=40 AND paired point estimate `F̂_plastic(40) − F̂_random(40) > 0` strictly. | 4th |
| 3 | **SATURATION — CI overlaps 0 with non-positive point estimate** (direction-only routing; mechanism-name DEFERRED to chronicle) | Paired CI INCLUDES 0 AT BUDGET=40 AND paired point estimate `F̂_plastic(40) − F̂_random(40) ≤ 0` (including tie `F̂_plastic(40) = F̂_random(40)`). | 5th |
| 4 | **INCONCLUSIVE — catchall** (§2 follow-up) | Any pattern not matched by rows 1-3 or 5-6 above (expected extremely rare under the well-defined paired-bootstrap predicate; included only to preserve §2 grid-completeness). | 6th (lowest) |

**Row-clause fidelity (principle 28a — explicit):** every row fires only when its full conjunction is satisfied AND no higher-precedence row fires first. Tie-breaking on paired point estimate at budget=40: `F̂_plastic(40) = F̂_random(40)` routes to Row 3 (SATURATION, not Row 2 PARTIAL), since Row 2 requires strict `F̂_plastic(40) − F̂_random(40) > 0`. Row precedence also resolves the v1 precedence bug (codex-v1 P1-2): a `CI_hi < 0` primary-endpoint REVERSE now routes unambiguously to Row 5, with no higher-precedence routing-level row that could swallow it (Row 6 SWAMPED is infrastructure-only and orthogonal).

**Coverage verification (principle 2b grid-cell enumeration):** the routing axis is 1D (the paired-bootstrap CI at budget=40); every (CI sign × point-estimate sign) cell has an explicit outcome token —

- CI_lo > 0 (POSITIVE exclusion) → Row 1 PASS-POSITIVE. (Note: CI_lo > 0 mathematically implies `F̂_plastic(40) − F̂_random(40) > 0`; the point-estimate check is redundant for this cell.)
- CI_hi < 0 (NEGATIVE exclusion) → Row 5 REVERSE. (Note: CI_hi < 0 mathematically implies `F̂_plastic(40) − F̂_random(40) < 0`; the point-estimate check is redundant for this cell.)
- CI includes 0 AND `F̂_plastic(40) − F̂_random(40) > 0` → Row 2 PARTIAL.
- CI includes 0 AND `F̂_plastic(40) − F̂_random(40) ≤ 0` (including tie) → Row 3 SATURATION.
- Any infrastructure-fidelity failure → Row 6 SWAMPED (highest precedence; orthogonal).
- Any residual pattern not covered above → Row 4 CATCHALL (§2 follow-up).

All cells covered; no blank cells. Every routing cell has a unique Row assignment under precedence (verified: the four routing-cell predicates are mutually exclusive by construction given CI and point-estimate are a single 1D axis).

**Supporting-cell information at budgets {5, 10, 20} `(v7 rewrite)`: DEFERRED to §2d-supplemental — NOT measured in §2d-primary.** The v1–v6 §26-demoted handling of supporting cells (descriptive-only; no routing contribution; sign-flips flagged as §2b grid-miss for follow-up prereg) is preserved in intent but moved to §2d-supplemental execution. §2d-primary computes zero statistics at supporting budgets and reports nothing on supporting cells; all supporting-cell claims in the v1–v6 body text are void for §2d-primary. If a §2d-supplemental sweep executes later, descriptive-only §26 chronicle-time treatment applies there.

**Threshold justifications (principle 6 — all baseline-relative):**

- **Paired-bootstrap CI exclusion criterion (rows 1, 5):** derived from the bootstrap distribution on the same 20 paired seeds; no imported threshold.
- **Paired point-estimate sign at budget=40 (rows 2, 3):** direct data comparison; no imported threshold.
- **Row-6 SWAMPED triggers:** `initial_population_canonical_count > 0` is an infrastructure-fidelity invariant (should always be 0 at sf=0.0; any violation is a bug); hash-dedup mismatch verified by pytest (checklist item 3); seed-integrity pre-check and mechanism-sanity pre-check (including per-run k-draw support/std) are implementation invariants.

## Degenerate-success guard (required — principle 4 + principle 28b)

Six guards: the first five inherited from §2c (with mechanism-scaling adaptations), guard 6 new and specific to random-sample.

1. **Universal-adapter artefact.** Single-criterion: `top1_winner_levenshtein_uncapped` at any cell (plastic or random) ≤ 4 for ≥ 15/20 seeds. If triggered, top-1 winners converge to near-canonical structure under the new mechanism — a pattern not anticipated by §2c's observed distant-tail winners (range 17-26). Chronicle-time: flag as §26 secondary-axis grid-miss (no pre-registered row fires from this guard per §26 discipline).

2. **Train-test leakage.** Single-criterion: `F_AND_test_plastic_count − F_AND_train_plastic_count` near zero at any random-sample cell AND `F_AND_test_plastic_count ≥ 15/20` (high solve rate with indistinguishable train/test). Chronicle-time inspection.

3. **Threshold-saturation (population + top-1 winner split; §28b conjunction).** Conjunction: per-cell `|delta_final| ≥ budget` fraction on population AND on top-1 winner, BOTH reported per cell. Physical-ceiling violation (`|delta_final| > budget`) indicates a bug; discharge in chronicle. **§28b multi-mode coverage:** for random-sample cells, this guard covers both (a) `|delta_final|` within bounds (normal) and (b) `|delta_final|` at exact `±budget` endpoint (rare but physically possible at closed-interval boundaries — not a bug, requires chronicle-time commentary); for plastic cells the saturation semantics are unchanged from §2c. Violation of `|delta_final| > budget` strict is the SWAMPED-triggering failure mode.

4. **GT-bypass artefact.** Single-criterion: `GT_bypass_fraction ≥ 0.50` at any cell. Chronicle-time.

5. **δ-convergence artefact.** Single-criterion: `delta_final_std_mean ≤ 0.5` at any plastic cell OR any random-sample cell (δ convergence across genotypes; at random-sample cells this additionally flags potential rng-sanity issue per guard 6). Chronicle-time; if triggered, §26 secondary-axis grid-miss flag at chronicle time.

6. **Random-sample rng-sanity artefact (new in §2d).** Conjunction per §28b — random-sample cells have multiple mechanism-specific failure modes, ALL MANDATORY at launch per codex-v1 P1-5 correction (sub-criterion (c) upgraded from optional-defer to mandatory; engineering item 1(g) is launch-blocking):
   - (a) `std(delta_final)` across 20 seeds at any random-sample cell `< 0.01` (near-zero variance; suggests rng seeding bug OR coincidental argmax convergence — ambiguous without inspection). Row 6 SWAMPED trigger.
   - (b) `mean(|delta_final|)` at any random-sample cell ≤ `0.1 · budget` (all individuals converged near δ=0; suggests either k-sample argmax has a strong zero bias because zero train-fitness differences exist OR an implementation bug where draws collapsed to zero). Row 6 SWAMPED trigger.
   - (c) **MANDATORY at launch:** per-individual k-draw summary `(min_draw, max_draw, std_draws, argmax_index)` logged during mechanism execution; per-run aggregation emits the top-1 winner's 4-element tuple `(min_draw, max_draw, std_draws, argmax_index)` to CSV columns `winner_k_draw_min`, `winner_k_draw_max`, `winner_k_draw_std`, `winner_k_argmax_index`. Expected invariants per-individual on every random-sample run: `min_draw ≥ −budget` strictly, `max_draw ≤ +budget` strictly (support-bound), `std_draws ≥ 0.05 · budget` (non-degenerate rng at the individual level), and `argmax_index ∈ [0, k−1]`. Any violation is a Row 6 SWAMPED trigger. This sub-criterion covers the failure modes (a) and (b) cannot see: individual-level collapse where k draws cluster but argmax produces a different-looking `delta_final`, or support-bound overshoot from rng-library edge cases.
   
   All three sub-criteria are active at launch; (a) and (b) are cell-level aggregates, (c) is per-individual with per-run top-1 aggregation. Any sub-criterion trigger → Row 6 SWAMPED (mechanism-sanity pre-check) + chronicle-time inspection.

**Infrastructure-fidelity check:** `history.npz:initial_population_canonical_count == 0` across every run (Row 6 SWAMPED trigger if violated). Covered by existing pytest `tests/test_chem_tape_seeded_init.py`.

**Conjunction-guard check (principle 28b):** guards 3 and 6 are multi-mode conjunctions. Guard 3 covers population + top-1 winner split. Guard 6 covers three sub-criteria with non-overlapping failure modes: (a) cell-level rng variance, (b) cell-level δ-magnitude collapse, (c) per-individual draw-distribution sanity including support-bounds. All three are mandatory at launch; no sub-criterion is deferred. Guards 1, 2, 4, 5 are single-criterion over single-failure-mode regimes — verified that each gate uniquely detects its guarded regime's known failure mode. No single-criterion guard misses a known multi-mode failure.

## Statistical test (principle 22 + 22a + 22b)

- **Primary confirmatory test (authoritative for all row clauses):** paired-seed bootstrap 98.333% CI on per-seed difference `F_AND_test_plastic[plastic, budget=40, seed=s] − F_AND_test_plastic[random, budget=40, seed=s]` for s ∈ {20..39}, n=20 paired differences. 10 000 resamples, `numpy.random.default_rng(seed=42)`, 98.333% quantile CI on paired-difference mean. H1-DIRECTION-POSITIVE rejection criterion: `CI_lo > 0` (excludes 0 positive). H-reverse trigger: `CI_hi < 0` (excludes 0 negative).
- **Secondary (NOT confirmatory, effect-size only, NO α budget) `(v7 rewrite)`:** per-cell seed-bootstrap 98.333% CI on F_AND_test_plastic fraction at the single random-sample budget=40 cell (descriptive visualization); per-cell descriptive statistics on §26-demoted secondary axes at budget=40 only. Supporting-cell point estimates / CIs at budgets {5, 10, 20} are DEFERRED to §2d-supplemental (not computed in §2d-primary; v7 codex-review P1-2 discharge).
- **Classification:** **confirmatory.** Gates the direction-only narrowing/broadening decision for `findings.md#plasticity-narrow-plateau`. Mechanism-level interpretation (e.g., "plasticity-specific vs extra-slack-sufficient") is **not** pre-committed by this prereg's routing — it happens at chronicle time under §16c if any mechanism name is proposed (codex-v1 P1-3 correction).
- **Family:** **`plasticity-narrow-plateau`** (joins the existing family; commit-time membership per §22b). Prior members: §v2.5-plasticity-1a at commit `4ceb22b` (size 1, FALSIFIED at sf=0.01 seeded); §v2.5-plasticity-2c at commit `06e8732` (size 2, PARTIAL at CI-boundary knife-edge per chronicle commit `1112e36`). §2d adds a **third confirmatory test** on the same claim family, growing the family to **size 3** at this prereg's commit. **Bonferroni-corrected family α = 0.05 / 3 ≈ 0.01667.** Operationalized as a **98.333% two-sided CI** (quantiles [0.8333%, 99.1667%]) with either-side rejection (Row 1 PASS-POSITIVE on `CI_lo > 0`; Row 5 REVERSE on `CI_hi < 0`), consuming exactly 0.01667 total family α. This is TIGHTER than §2c's 97.5% — acknowledged explicitly: §2d raises the directional-rejection bar by applying Bonferroni correction at the current family size, which is the honest accounting per §22b commit-time membership. No shorter-CI phrasing appears in the authoritative sections (Hypothesis / Outcome grid / Statistical test / METRIC_DEFINITIONS); 98.333% is the authoritative CI for all row clauses.
- **Per-sweep test counting (principle 22a) `(v7 rewrite)`:** this prereg produces **ONE** confirmatory test (the paired-bootstrap CI on random-sample budget=40 vs plastic budget=40 at shared seeds 20..39). Supporting-cell point estimates/CIs at budgets {5, 10, 20} are DEFERRED to §2d-supplemental and NOT computed in §2d-primary; they do not enter any row-clause conjunction and do not open additional family members.
- **Commit-time family membership (principle 22b):** the confirmatory test counts in the family regardless of rejection outcome. If Row 3 (SATURATION) fires (overlapping CI with non-positive point estimate), the null is recorded under §24 but the family member count remains at 3; the corrected α stays at 0.01667 for any future test that joins this family.

## Diagnostics to log (beyond primary confirmatory axis)

`(v7 rewrite)` §2d-primary scope: diagnostics are computed only on the single random-sample budget=40 cell (20 new runs, seeds 20..39) and on the reused §2c plastic budget=40 cell where cross-mechanism comparison is meaningful. Any v1–v6 bullet that references supporting cells {5, 10, 20} ("per cell across budgets", "per-budget diagnostic") is SCOPED to budget=40 only in §2d-primary; supporting-cell diagnostics are deferred to §2d-supplemental. The per-run k-draw summary is computed on the 20 new random-sample runs.

Per prereg Diagnostics-to-log discipline (inherited from §v2.5-plasticity-2c):

- Per-seed × per-cell F_AND_train, F_AND_test (plastic eval for both rank-1 and random-sample cells; rank-1 cells reused from §2a/§2c).
- R_fit_frozen_999, R_fit_plastic_999 per cell.
- Per-individual test_fitness_frozen, test_fitness_plastic, train_fitness_frozen, train_fitness_plastic, delta_final, has_gt, genotypes → `final_population.npz`.
- Per-cell GT_bypass_fraction.
- Per-cell Baldwin_gap by Hamming bin (h=0..≥4) for all cells; Baldwin_slope (nan expected at sf=0.0).
- Per-cell std(delta_final) stratified by Hamming bin.
- Per-cell seed-bootstrap 98.333% CI on F_AND_test_plastic fraction (descriptive; secondary).
- **Per-run `top1_winner_baldwin_gap`, `top1_winner_plasticity_active_count`, `top1_winner_overhead`, `top1_winner_levenshtein_uncapped`, `top1_winner_attractor_category`, `top1_winner_canonical_token_set_size`** — all §26-demoted secondary axes; reported per-run per-cell (both mechanisms).
- Per-cell `|delta_final| ≥ budget` fraction (pop-level + top-1 winner split, both mechanisms).
- Per-cell `|delta_final|` support-bound verification: `min(delta_final)`, `max(delta_final)`, `std(delta_final)` per cell (mechanism-sanity diagnostic; Row 6 SWAMPED trigger on support-bound violation).
- Per-run k-draw summary at every random-sample cell: `winner_k_draw_min`, `winner_k_draw_max`, `winner_k_draw_std`, `winner_k_argmax_index` (per-run top-1 winner aggregation; per-individual k-draw tuple logged during mechanism execution). Mandatory at launch per codex-v1 P1-5 correction.
- Per-cell best-of-run hex for top-1 winner per seed.
- Per-seed initial_population_canonical_count in gen-0.

## Scope tag (required — principle 17 + 17b + 18)

Scope tag uses direction-only language and scopes confirmatory claim to tested **confirmatory cell** only; supporting-cell information enters as descriptive-not-confirmatory context (codex-v1 P2-1 correction).

**If Row 1 (PASS-POSITIVE — plastic > random at budget=40) fires `(v7 rewrite)`:** `findings.md#plasticity-narrow-plateau` NARROWS with scope:
`within-task-family · confirmatory cell: n=20 paired at plasticity_budget=40 (plastic rank1_op_threshold vs random_sample_threshold) · pop=512 gens=1500 mr=0.03 tournament_size=3 elite_count=2 · sum_gt_10_AND_max_gt_5 natural sampler with 75/25 train/test split · tested mechanisms ∈ {rank1_op_threshold, random_sample_threshold} · δ=1.0 · tested integer budget = {40} (supporting cells {5, 10, 20} DEFERRED to §2d-supplemental; not measured here) · sf=0.0 · Arm A only · seeds 20..39`. Mechanism-interpretation (e.g., "plasticity-specific vs other readings") is chronicle-time only under §16c and does NOT appear in this scope tag.

**If Row 3 (SATURATION — CI overlaps 0, non-positive point estimate) fires:** `findings.md#plasticity-narrow-plateau` BROADENS with the same scope tag plus explicit `at tested confirmatory cell plasticity_budget=40 and tested mechanisms ∈ {rank1_op_threshold, random_sample_threshold}, no directional evidence detected between the two mechanisms at matched `plasticity_budget`` qualifier per principle 17b (no extrapolation beyond tested set; no mechanism-name attached to the null direction).

**If Row 5 (REVERSE — random > plastic at budget=40) fires:** `findings.md#plasticity-narrow-plateau` BROADENS with additional qualifier `at tested confirmatory cell plasticity_budget=40 and tested mechanisms ∈ {rank1_op_threshold, random_sample_threshold}, uniform-continuous random-δ-sampling's F_AND_test_plastic exceeds rank1_op_threshold's on the paired seeds 20..39 bootstrap CI basis`. No mechanism-level falsification claim (that is chronicle-time §16c work).

**Explicitly NOT-broadening in any outcome:** other tasks (P-3 from §1a open for cross-task); BP_TOPK arm (EXCLUDED); rank-2 or deeper mechanisms (untested); other selection regimes; other δ values; other train/test splits; budgets beyond 40; supporting-cell budgets {5, 10, 20} as confirmatory (they are descriptive-only); seeds beyond 20..39; other mechanisms not in the tested-set (e.g., Gaussian sampling, lattice-restricted sampling, Bayesian optimization of δ).

## Decision rule

- **Row 1 (PASS-POSITIVE — plastic > random at budget=40) →** narrow `findings.md#plasticity-narrow-plateau` with the direction-only scope tag above (no mechanism-name pre-commitment at this prereg's routing level). At chronicle time, a §16c mechanism-naming round MAY be attempted (≥ 3 falsifiable predictions required per §16c hard gate); if a name is proposed, §2d's directional-positive result may be cited as one such pre-committed falsifier (the falsifier list is proposed fresh at chronicle time, not pre-committed here). Rank-2 (§v2.5-plasticity-1b) deprioritized on the capacity-axis ladder; cross-task extension (P-3) opens as a candidate follow-up.
- **Row 2 (PARTIAL — directional but CI-inconclusive) →** no findings change; report effect-size + paired-bootstrap CI; document as directional-but-CI-inconclusive at tested confirmatory cell budget=40; budget ≥ 80 follow-up under user judgment (not pre-committed); rank-2 on hold pending follow-up.
- **Row 3 (SATURATION — CI overlaps 0, non-positive point estimate) →** broaden `findings.md#plasticity-narrow-plateau` with the direction-only scope tag above (no mechanism-name pre-commitment). Chronicle-time interpretation of the null direction happens under §16c discipline if any mechanism name is proposed (e.g., "extra-slack-sufficient" is NOT pre-committed here; it is a chronicle-time candidate for discussion with its own ≥ 3-falsifier requirement). Rank-2 deprioritized on the capacity-axis ladder; next escalation targets are chronicle-time decisions: selection-regime changes (EES §v2.5-plasticity-2b; novelty-search; strip-static-shortcut per `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md`); the `selection-deception` diagnosis class holds and selection-regime lever is a chronicle-time option.
- **Row 4 (CATCHALL) →** §2 follow-up; note outcome table was incomplete; update for future prereg.
- **Row 5 (REVERSE — random > plastic at budget=40) →** broaden `findings.md#plasticity-narrow-plateau` with the direction-only scope tag above. Stop and inspect before any mechanism-level interpretation; random-wins-over-plastic is an unexpected direction at matched `plasticity_budget`. Investigate for (a) infrastructure issues (mechanism-sanity pre-check should catch this; if pre-check passes and REVERSE still fires, novel); (b) data-distribution changes (unlikely given matched sampler/seeds); (c) chronicle-time hypothesis generation. Mechanism-naming (whether falsifying a candidate name or proposing a new one) is §16c chronicle-time work.
- **Row 6 (SWAMPED) `(v7 rewrite: add determinism-failure trigger)` →** stop and inspect; no routing until infrastructure check passes. Report which specific trigger fired (init_canonical, hash-dedup, seed-integrity, mechanism-sanity including per-run k-draw support/std, or **v7: determinism-failure** — byte-identity diff on any of the 4 overlap seeds 20..23 at budget=40 between 2026-04-23 partial data and the 2026-04-24 re-run) in the chronicle.

## Audit trail

- **Principle 1:** paired-seed internal contrast (random-sample budget=40 vs plastic budget=40 on seeds 20..39) is in-sweep; tightest within-family cross-mechanism contrast.
- **Principle 2 + 2b + 26:** **6 rows** enumerated with explicit precedence order (Row 2 GRID-MISS-SUPPORTING from v1 REMOVED per codex-v1 P1-1 correction); primary axis is 1D on paired-bootstrap CI at budget=40; coverage enumerated across all (CI sign × point-estimate sign) cells on the 1D routing axis. Supporting-cell cross-mechanism information at budgets {5, 10, 20} is fully §26-demoted to chronicle-time descriptive context (no routing clauses; parallel to §2c's §26-demoted handling of secondary axes). Partial (Row 2), catchall (Row 4), and SWAMPED (Row 6) all present per principle 2.
- **Principle 4 + 28b:** 6 guards (guard 6 new and mechanism-specific, with 3 mandatory sub-criteria at launch per codex-v1 P1-5 correction). Guards 3 and 6 are multi-mode conjunctions.
- **Principle 6:** all thresholds baseline-relative (paired-bootstrap on same dataset; point-estimate sign at budget=40 on same data). No imported numeric thresholds.
- **Principle 16c:** mechanism naming DEFERRED; §16c block empty. **No mechanism name is used as a routing label, outcome-row title, or decision-rule variable.** Candidate-name *labels* appear in some explanatory prose (Hypothesis framing, decision-rule narrative, scope-tag clarifications) solely to describe chronicle-time interpretive options; these labels do NOT gate any routing decision and are explicitly marked "chronicle-time only under §16c" at every appearance. Candidate names (whether pre-existing like `Baldwin-at-operator-level` or new) are chronicle-time §16c discussion material only and require their own ≥ 3 falsifiable predictions pre-committed in the chronicle's §16c block at time of proposal (codex-v1 P1-4 correction: v1 silently invoked `Baldwin-at-operator-level` as a named object with prereg-level falsifier-discharge semantics; v2 strips all such prereg-level semantics while retaining chronicle-time-scoped labels as examples in explanatory prose; codex-v2 P2-2 clarification: the self-audit claim is scoped to "no mechanism name is a routing variable," not the stronger "no label appears anywhere in the file").
- **Principle 17a + 17b `(v7 rewrite)`:** mechanism axis is single nominal config field (`plasticity_mechanism`) with 3 directly-derived co-moving process variables (δ-selection procedure, reachable-δ space, stopping semantics). All three are direct consequences of mechanism choice — they ARE the mechanism and are named honestly at every qualifier per codex-v1 P2-2 correction. Tested mechanism values ∈ {`rank1_op_threshold`, `random_sample_threshold`} and tested integer budget = {40} per 17b; supporting cells {5, 10, 20} DEFERRED to §2d-supplemental (not tested in §2d-primary). Scope qualifiers use verbatim tested-set `{40}`.
- **Principle 20:** sampler unchanged from §2c; not triggered.
- **Principle 22 + 22a + 22b:** confirmatory, **1 test** (paired-bootstrap on seeds 20..39 at budget=40). Joins existing `plasticity-narrow-plateau` family, growing from size 2 (§2c confirmatory at commit `06e8732`) to **size 3** at this prereg's commit; corrected α = 0.05/3 ≈ **0.01667**. Commit-time membership per 22b. Explicit acknowledgment: this raises the directional-rejection bar (98.333% CI vs §2c's 97.5%) and is the honest accounting under family growth. Supporting-cell point estimates at {5, 10, 20} do NOT open new family members (codex-v1 P1-1 correction).
- **Principle 23:** param-identity to §2c except mechanism axis. Reusing §2a's budget=5 seeds-20..39 subset and §2c's budgets {10, 20, 40} data. Hash-dedup verified at checklist item 3 (mechanism is non-default for random-sample cells, so hash includes it, so no collision with plastic cells).
- **Principle 25 + 25b + 25c + 27:** primary confirmatory statistic is routing-only on the paired-bootstrap CI (F_AND_test_plastic distribution well-understood from §2c precedent — direct CI gate is valid per §25b option b); supporting-cell axis and all secondary metrics are §25b option (c) demoted (chronicle-time descriptive discipline only, no routing role — codex-v1 P1-1 correction applied the option-(c) treatment to the supporting-cell axis that v1 tried to route on); no clause does double duty as routing + mechanism-discriminator (§25c satisfied — routing is direction-only; mechanism-interpretation is chronicle-time §16c — codex-v1 P1-3 correction). Engineering estimate **~9-14h** total including mandatory per-individual k-draw logging (~1-2h added over v1) + mechanism implementation (~6-10h) + analyzer/pytest/YAML glue (~2-3h).
- **Principle 26:** secondary axes EXPLICITLY demoted per escape hatch, now including supporting-cell cross-mechanism signs at budgets {5, 10, 20}; cite-the-reason documented in Hypothesis block (no pre-experiment basis to pre-commit cross-mechanism thresholds at supporting budgets given §2c observed only plastic-vs-plastic cross-budget; supporting-cell cross-mechanism distribution is not known from precedent). No outcome-grid rows on secondary axes or supporting-cell signs; chronicle-time discipline handles dramatic patterns via §2b grid-miss flag (mirror §2c).
- **Principle 28a/b/c:** row clauses are explicit conjunctions on the 1D routing axis with precedence (28a); guards 3 and 6 multi-mode (28b, all guard-6 sub-criteria mandatory at launch); status-line inline qualifier at chronicle time (28c).
- **Principle 29:** this prereg does NOT follow from a formal diagnosis doc — §2c was Row 2 PARTIAL (pre-registered row at CI-boundary knife-edge), not FAIL/grid-miss. §29 not directly invoked. The §2d design is motivated by §2c's scientific ambiguity between candidate mechanism readings; the routing, however, is direction-only and does not pre-commit to any mechanism reading, so §29's diagnose-before-escalate discipline is not applicable at the routing level (codex-v1 P1-3 scope adjustment).

## METRIC_DEFINITIONS extensions (principle 27 — verbatim)

The following entries will be added verbatim to `experiments/chem_tape/analyze_plasticity.py:METRIC_DEFINITIONS` by Status-transition checklist item 1 before sweep launches. Inherits §2c's 6 per-run diagnostic entries (reused verbatim; no changes). Adds 2 new cell-level CI entries + 2 new cell-level mechanism-sanity diagnostics:

```python
"f_and_test_plastic_seed_boot_ci_98_333": (
    "Per-cell seed-bootstrap 98.333% CI on F_AND_test_plastic fraction. "
    "10 000 resamples with replacement over 20 per-seed binary indicators "
    "(best_fitness_test_plastic >= 1.0) via numpy.random.default_rng(seed=42); "
    "CI = [0.8333%, 99.1667%] empirical quantiles of resampled fractions. "
    "Matches bootstrap_ci_spec at the §v2.5-plasticity-2d family-α=0.01667 "
    "discipline (family = 'plasticity-narrow-plateau', size 3 per §22b "
    "commit-time membership). Extends §v2.5-plasticity-2c's "
    "f_and_test_plastic_seed_boot_ci (97.5% CI) to the §2d quantile. "
    "Descriptive (not confirmatory). Added in §v2.5-plasticity-2d."
),
"f_and_test_plastic_paired_boot_ci_plastic40_vs_random40": (
    "Paired-seed bootstrap 98.333% CI on per-seed difference "
    "F_AND_test_plastic[mechanism=rank1_op_threshold, budget=40, seed=s] "
    "minus F_AND_test_plastic[mechanism=random_sample_threshold, budget=40, "
    "seed=s] for s in {20..39}, n=20 paired differences. 10 000 resamples "
    "via numpy.random.default_rng(seed=42); CI = [0.8333%, 99.1667%] "
    "empirical quantiles of resampled paired-difference means. Plastic "
    "budget=40 per-seed indicators extracted from §v2.5-plasticity-2c data "
    "(commit `06e8732`) via (mechanism, budget, seed) filter. "
    "**Primary confirmatory test for §v2.5-plasticity-2d family "
    "'plasticity-narrow-plateau' (family size now 3, corrected alpha = "
    "0.01667).** H1 rejection: CI_lo > 0. H-reverse trigger: CI_hi < 0. "
    "Added in §v2.5-plasticity-2d."
),
"delta_final_cell_support_bounds": (
    "Per-cell tuple (min, max, std) of delta_final across 20 seeds. "
    "Mechanism-sanity diagnostic: for plasticity_mechanism="
    "'random_sample_threshold' cells, verifies -budget <= min, max <= "
    "+budget (uniform-continuous support bounds); verifies std >= 0.01 "
    "(non-degenerate rng); verifies 0 < mean(|delta_final|) <= budget "
    "(not all-δ=0). Violation of any sub-check routes Row 6 (SWAMPED) "
    "per Setup Mechanism-sanity pre-check. For plasticity_mechanism="
    "'rank1_op_threshold' cells, support bound is the integer-lattice "
    "+-budget*delta endpoint (same formal bound, different reachability). "
    "Reported per-cell at chronicle time. Added in §v2.5-plasticity-2d."
),
"random_sample_mechanism_draw_spread": (
    "Per-individual tuple (min_draw, max_draw, std_draws, argmax_index) "
    "summarizing the k uniform-continuous draws at a random_sample_"
    "threshold cell. Logged per-individual during adapt_and_evaluate_one_"
    "random_sample as part of the individual's output dict; per-run top-1 "
    "winner aggregation emitted to CSV columns winner_k_draw_min, "
    "winner_k_draw_max, winner_k_draw_std, winner_k_argmax_index. "
    "**MANDATORY at launch per §v2.5-plasticity-2d codex-v1 P1-5 "
    "correction (previously optional-defer; v2 upgrades to launch-"
    "blocking).** Per-individual invariants (any violation on any "
    "individual in any random-sample cell → Row 6 SWAMPED): min_draw "
    ">= -budget, max_draw <= +budget, std_draws >= 0.05 * budget, "
    "argmax_index in [0, k-1]. Covers failure modes that cell-level "
    "delta_final cannot see: individual-level collapse where k draws "
    "cluster but argmax produces a different-looking delta_final; "
    "support-bound overshoot from rng-library edge cases. Schema is "
    "(min_draw, max_draw, std_draws, argmax_index) — consistent with "
    "Setup mechanism-sanity pre-check, Guard-6 sub-criterion (c), and "
    "Status-transition checklist item 1(g). Added in §v2.5-plasticity-2d."
),
```

4 new entries (2 cell-level CIs + 2 cell/run-level mechanism-sanity diagnostics). §2a's and §2c's existing 6 per-run diagnostic entries are reused verbatim with no changes.

## Status-transition checklist (must discharge before sweep launch)

Engineering total estimate **~9-14h** (mechanism implementation + mandatory per-individual k-draw logging + analyzer/pytest/YAML glue). Bumped from v1's ~8-12h per codex-v1 P1-5 correction (sub-criterion (c) upgraded from optional-defer to mandatory launch-blocking; engineering item 1(g) adds ~1-2h).

1. **Engineering: extend `src/folding_evolution/chem_tape/plasticity.py` with `random_sample_threshold` mechanism** + dispatch from `evaluate_population_plastic`. Each sub-item has pytest coverage.
   - (a) New `adapt_and_evaluate_one_random_sample` (or branch in `adapt_and_evaluate_one` on `cfg.plasticity_mechanism`): per-individual rng seeded by `(cfg.seed, individual_index, cfg.hash())`; draws k = `cfg.plasticity_budget` samples from `rng.uniform(-k, +k)`; evaluates each on 48 train examples; picks argmax (tiebreak: smallest-absolute-δ, then first-occurrence); evaluates chosen δ on 16 test examples; emits byte-identical output dict schema as plastic PLUS per-individual k-draw summary `(min_draw, max_draw, std_draws, argmax_index)`. Preserves selection_only fast-path. (~4-6h.)
   - (b) Dispatch extension in `evaluate_population_plastic`: branch on `cfg.plasticity_mechanism ∈ {rank1_op_threshold, random_sample_threshold}`; rank-1 path unchanged. Default = `rank1_op_threshold` preserves byte-identity for existing §2a/§2c reruns. (~30 min.)
   - (c) `analyze_plasticity.py:_cell_key` extension to include `plasticity_mechanism` in the grouping tuple. Backward-compat: existing §2a/§2c CSV rows all have `plasticity_mechanism=rank1_op_threshold` so re-parsing into the extended cell-key matches the old cell-set. Downstream audit: also check `summarize()` field names and any per-cell summary fields that depend on the old cell-key tuple (none found in v1 scan, but engineering must re-grep to confirm no silent cell-collapse site remains). (~45 min.)
   - (d) Cell-level routine extensions: `f_and_test_plastic_seed_boot_ci_98_333` (parameterize the existing `f_and_test_plastic_seed_boot_ci` on quantile or add sibling). (~30 min.)
   - (e) New paired-bootstrap routine `paired_bootstrap_plastic40_vs_random40` with explicit (mechanism, budget, seed) extraction from pooled §2c plastic data. (~30 min.)
   - (f) Cell-level mechanism-sanity diagnostics: `delta_final_cell_support_bounds` (min/max/std per cell). (~30 min.)
   - (g) **MANDATORY at launch (codex-v1 P1-5 correction; no longer optional-defer):** per-individual k-draw logging emitted from `adapt_and_evaluate_one_random_sample`, propagated through evaluate_population_plastic output dict, written to per-run CSV columns `winner_k_draw_min`, `winner_k_draw_max`, `winner_k_draw_std`, `winner_k_argmax_index` (top-1 winner aggregation). Cell-level summary routine computes per-cell aggregates for Row 6 SWAMPED mechanism-sanity pre-check. (~1-2h.)
   - (h) Glue: per-run + per-cell schema pytest, mechanism-sanity pytest (rng reproducibility, support bounds, argmax ties, per-individual k-draw invariants), CI-reproducibility pytest, `_cell_key` extension pytest for backward compat, per-individual k-draw support-bound pytest. (~2-3h.)
   - (i) Re-run `analyze_plasticity.py` on existing §2a + §2c data to validate new cell-key + new columns; confirm no regression on existing cells. (~30 min.)
   - Sub-total: **~9-14h**.

2. **Pre-data: compute baseline CI on reused plastic data at 98.333% quantile `(v7 rewrite)`.** Run new CI routine on existing §2c plastic budget=40 data (seeds 20..39, n=20); report point estimate + 98.333% CI. Direct descriptive comparator for H1/H0/H-partial at the §2d-primary cell. Supporting-cell baselines at budgets {5, 10, 20} are DEFERRED to §2d-supplemental.

3. **Pytest: hash-dedup discipline.** Verify dry-run invocation of `sweep.py` on the new sweep YAML does NOT re-compute existing rank-1 cells (different mechanism → different config hash; dedup should skip nothing inappropriately). Pure sanity check given `plasticity_mechanism` is hash-relevant when non-default. (~15 min.)

4. **Sweep YAML creation `(v7 rewrite — DISCHARGED)`.** Original v1–v6: `experiments/chem_tape/sweeps/v2/v2_5_plasticity_2d.yaml` with 4 cells × 20 seeds = 80 runs (created; attempted 2026-04-23; timed out). v7 SUPERSESSION: `experiments/chem_tape/sweeps/v2/v2_5_plasticity_2d_primary_b40.yaml` with 1 cell × 20 seeds = 20 runs. Base section byte-identical to v1–v6; paired list reduced from 4 entries to 1 (budget=40 only). Committed at v7 target SHA.

5. **Queue.yaml entry `(v7 rewrite — DISCHARGED)`.** Original v1–v6: `v2_5_plasticity_2d` with timeout 10800s (status=timeout in queue.status.json; preserved as historical record; runner skips). v7 SUPERSESSION: new entry `v2_5_plasticity_2d_primary_b40` with timeout 57600s (16h per codex-consult 2026-04-24). Committed at v7 target SHA.

6. **Pilot timing.** Run 1 seed at random-sample budget=40 (~30 min wall projected) to calibrate compute estimate before committing sweep YAML params; verify mechanism-sanity pre-check passes on pilot run. (~30-45 min.)

7. **Codex adversarial review of this prereg (mandatory per research-rigor prereg-mode hard gate; v1 FAIL with 5 P1 + 3 P2 completed at 2026-04-23; v2 is the P1-discharged rewrite).** Re-submit v2 to codex; address every new P1; acknowledge/defer P2. Document in Amendment history below. (Expect 1-2 more rounds based on §2c prereg history — 4 codex rounds on prereg total.)

8. **Target commit SHA pin.** After items 1-7 land, re-pin target commit in this prereg's status line.

9. **Sanity-check cross-reference** with `Plans/_v2-5-plasticity-2d_session_prompt.md` scratch doc: confirm locked design (uniform-continuous `[-b, +b]`; k draws; best-on-train; primary budget=40; descriptive at {5, 10, 20}; §26-demoted secondaries; mechanism-name DEFERRED) is fully reflected in the prereg before final codex round. Delete scratch doc after §2d is READY-TO-LAUNCH.

Total engineering + review: **~9-14h** for mechanism + analyzer + pytest + per-individual k-draw logging; plus 2-4h for review rounds + target-SHA pin.

## Amendment history

**2026-04-24 (v7 post-compute amendment; scope re-targeted to budget=40 primary-confirmatory cell after 2026-04-23 launch timeout; "matched eval-time compute" wording corrected throughout).**

**Launch attempt at commit `ee44b1c` (2026-04-23) timed out at 10800s (SIGTERM exit 143).** Initial post-kill file-count at the 10800s SIGTERM reported 8 runs with `final_population.npz`; post-review inspection at 2026-04-24 found **18 runs completed** (more writes landed between SIGTERM-delivery and child-process teardown). Corrected counts below. Partial output at `experiments/output/2026-04-23/v2_5_plasticity_2d/`; `queue.status.json` entry `v2_5_plasticity_2d` is status=timeout (preserved as historical record; not renamed — only a single attempt under this id).

Observed completion counts (CORRECTED 2026-04-24 by v7 codex-review P1-1):

| budget | completed / 20 | seeds completed | observed wall       | v6 projection | over |
|--------|----------------|-----------------|---------------------|---------------|------|
| 5      | 5              | 20, 21, 22, 23, 24 | ~3220s (54 min)  | ~7 min        | ~8×  |
| 10     | 5              | 20, 21, 22, 23, 24 | ~6100s (102 min) | ~15 min       | ~7×  |
| 20     | 4              | 20, 21, 22, 23  | (interrupted mid-sweep) | ~22 min | — |
| 40     | **4**          | **20, 21, 22, 23** | (interrupted mid-sweep; ~6.7h projected steady-state) | ~30 min | — |

**Provenance disclosure (v7 codex-review P1-1 discharge):** 4 runs at the primary-confirmatory cell (budget=40, seeds 20..23) completed at v6 code commit `ee44b1c`. v7 introduces NO code changes (scope + wording + timeout only). Researcher observation record: directory listings, `config.yaml` contents (budget + seed labels only), and `result.json`/`final_population.npz` file-presence counts were observed; **no `F_AND_test_plastic` value or winner metadata was read at any seed**. The primary metric values remain unseen by the researcher.

**Quarantine and re-run plan (Path A, codex-v7-review-discharge):**
1. §2d-primary analysis consumes ONLY the NEW 2026-04-24 sweep output. The 2026-04-23 partial data is quarantined (preserved on disk but not a baseline, not consumed, not cited as "partial §2d-primary data").
2. Fresh 20-run sweep at same seeds 20..39, budget=40, new run_dir `experiments/output/2026-04-24/v2_5_plasticity_2d_primary_b40/`.
3. **Post-sweep determinism check (mandatory, v7) `(v7.2 rewrite: implementation is bash script, not analyzer-layer)`:** compute SHA-256 of `final_population.npz` and `result.json` at each of the 4 overlap seeds (20..23) at budget=40 between 2026-04-23 partial data and the new 2026-04-24 sweep. Code is unchanged between `ee44b1c` and the v7 target SHA, so overlap-seed outputs MUST be byte-identical; any divergence flags Row 6 SWAMPED ("determinism-failure" reason) and halts the chronicle pending investigation. Implemented as the committed shell script `scripts/check_v2d_overlap_determinism.sh <old_sweep_dir> <new_sweep_dir>` (exit 0 = all overlap seeds byte-identical; exit non-zero = divergence). Chronicle workflow runs this script BEFORE invoking `analyze_plasticity.py` on the new sweep output; the analyzer does NOT embed the determinism check itself (audit boundary kept at shell rather than mingling into the analyzer's paired-bootstrap path).
4. Residual contamination risk: codex's strict reading ("fresh paired seeds with matching rank1 comparator") would require seeds 40..59 + a new rank1 comparator at those seeds (~27h compute), exceeding the user's 15h budget. Path A is the user's explicit choice with the determinism check as the defense; if the determinism check fails on any overlap seed, §2d's primary confirmatory is demoted to post-hoc/supplemental per codex P1-1's alternate prescription.

**Root cause:** `random_sample_threshold` always evaluates `plasticity_budget` independent train_fitness draws per individual; `rank1_op_threshold` short-circuits its update loop on correct-classification, so at matched `plasticity_budget` VM work is NOT matched. This asymmetry is the §17a variable-(c) stopping-semantics bundle element — it was already named honestly in the §17a audit block. What was incorrect in v1–v6 was the "Matched on: eval-time VM work" claim at line 9, and the "matched eval-time compute" phrasing at six other locations. **v7 corrects all seven occurrences to "matched `plasticity_budget`"** and adds an explicit "NOT matched on eval-time VM work" qualifier at line 9 cross-referencing §17a(c).

**Codex consult 2026-04-24** (read-only, `model_reasoning_effort="high"`; prompt included observed walls, partial completion, user's ~13h remaining budget, 5-option menu A-E). Verdict: **Rank A > E > C > D > B**. Recommended Path A with caveats:
- Execution: launch ONLY `random_sample_threshold, plasticity_budget=40, seeds 20..39` (20 runs) tonight.
- Mark `{5, 10, 20}` supporting cells as deferred to **§2d-supplemental** (separate night).
- Rewrite "matched eval-time compute" → "matched `plasticity_budget` / named mechanism-choice bundle; observed VM work is not matched because random sampling always evaluates k full train-fitness draws while rank1 has stopping/update-loop semantics".
- Queue timeout **57600s (16h)**; 30000s insufficient (budget=40 ≈ 2 waves × 6.7h + overhead ≈ 48000s expected; 57600s gives ~1.2× headroom).
- **Primary-confirmatory outcome rows unchanged** (Row 1 / Row 3 / Row 5 / Row 6 route direction-only on budget=40 paired-bootstrap CI).
- Supporting-cell §26 demotion pre-committed in v1–v6 means dropping them is methodologically clean; chronicle reports them as "deferred to §2d-supplemental" rather than "missing".

**Verdict interpretation (v7 clarification):** §2d does NOT isolate "adaptive update structure" from "stopping semantics." The §2d primary compares the `rank1_op_threshold` bundle (δ-selection + integer lattice + early-stop) vs the `random_sample_threshold` bundle (k uniform draws + continuous [−b,+b] + always-k-draws) at matched `plasticity_budget`=40. All three §17a variables co-move with the mechanism choice; no individual variable is isolated. Mechanism-level interpretation (attributing a directional outcome to any single bundle element) remains chronicle-time §16c discussion, UNCHANGED.

**Execution plan (v7):**
- New sweep YAML: `experiments/chem_tape/sweeps/v2/v2_5_plasticity_2d_primary_b40.yaml` (1 cell × 20 seeds = 20 runs).
- New queue entry: `v2_5_plasticity_2d_primary_b40` with `timeout_seconds: 57600`.
- Old `v2_5_plasticity_2d` queue entry left in place (status.json entry status=timeout → runner skips).
- The 2026-04-23 partial data (corrected count: 5 at budget=5, 5 at budget=10, 4 at budget=20, 4 at budget=40 seeds 20..23 — v7.2 correction) is NOT consumed by §2d-primary analysis except as input to the post-sweep determinism check. It may inform §2d-supplemental at chronicle time if re-run at those budgets later.
- §2d-supplemental (future; NOT pre-registered here): separate sweep covering `{5, 10, 20}` × 20 seeds with appropriately-sized timeout. Direction-only routing still applies; descriptive-only statistical treatment (§26).

**Primary-confirmatory routing (UNCHANGED from v6):**
- Statistic: `f_and_test_plastic_paired_boot_ci_plastic40_vs_random40` — paired-seed bootstrap 98.333% CI (Bonferroni-corrected at FWER family `plasticity-narrow-plateau` size 3) on `F_AND_test_plastic[rank1_op_threshold, budget=40, seed=s] − F_AND_test_plastic[random_sample_threshold, budget=40, seed=s]` for s ∈ {20..39}, n=20 paired.
- 10000 resamples, `numpy.random.default_rng(seed=42)`, quantiles [0.8333%, 99.1667%].
- Row 1 (PASS-POSITIVE): CI_lo > 0. Row 3 (SATURATION): CI overlaps 0, point estimate ≤ 0. Row 2 (PARTIAL): CI overlaps 0, point estimate > 0. Row 5 (REVERSE): CI_hi < 0. Row 6 (SWAMPED): any infrastructure / seed-integrity / mechanism-sanity trigger.

**Engineering state at v7:** **unchanged from v6** — 765 total tests passing (1 unrelated pre-existing mask-test failure). No code changes required; v7 is scope + wording + timeout only. Target-SHA to be pinned at the v7 commit in a follow-up one-line commit (same pattern as v6's `1d54a4d → ee44b1c`-style SHA pin).

---

**2026-04-23 (v6 post-codex-v6 review; 1 P1 + 1 P2 discharged in-place; READY-TO-LAUNCH).**

Codex-v6 review verdict: **GATE FAIL** (1 P1 + 1 P2; both traceable to incomplete v5 work rather than fresh design issues).

- **Codex-v6 P1-1** (4-tuple enforcement was single-column: the v5 missing-k-draw-data SWAMPED trigger only keyed off `winner_k_draw_min`; a cell with `winner_k_draw_min` present but `winner_k_draw_max` / `winner_k_draw_std` / `winner_k_argmax_index` missing would silently pass Guard-6(c)): v6 upgrades the enforcement to all-or-none across all 4 columns. The SWAMPED trigger now detects: (a) any fully-missing column (0 rows with values), AND (b) any partial-coverage column (fewer rows with values than total members). Parametrized pytest `test_summarize_flags_random_sample_swamped_on_single_missing_kdraw_column` added, covering each of the 4 columns; the partial-coverage test updated to cover `winner_k_draw_max` (not `_min`, so it doesn't alias the v5 case).
- **Codex-v6 P2-1** (prereg text had stale 3-tuple wording "top-1 aggregation reports k-draw (min, max, std)" at line 48, undercutting the amendment-history claim that the 4-tuple contract is coherent end-to-end): rewrote the Diagnostics bullet to "top-1 winner's full 4-tuple (min_draw, max_draw, std_draws, argmax_index) to CSV columns winner_k_draw_{min,max,std} + winner_k_argmax_index. Mandatory at launch per codex-v1 P1-5 correction (4-tuple fully enforced per codex-v6 P1-1: all four columns checked for presence in Guard-6(c))".

Engineering state at v6: **765 total tests passing** across the full project (749 pre-§2d + 16 new §2d tests; 1 unrelated pre-existing failure in `test_chem_tape_v2_executor.py::test_masks_for_v2_active_runs_1_to_19` — shape mismatch in alphabet masks, not touched by §2d).

§2d-specific test counts:
- `tests/test_chem_tape_plasticity.py`: 4 pre-existing + 6 new = 10 mechanism tests (rank-1 path byte-identity; random-sample schema; rank-1 unaffected; reproducibility; hash-dedup vs rank-1; k=1 edge; GT-bypass vacuous).
- `tests/test_analyze_plasticity_v2d_metrics.py`: 30 analyzer tests (CI width 98.333% vs 97.5%; bootstrap nan-drop; paired-bootstrap directional cases; SWAMPED triggers for missing/duplicated/extra seeds on both cells; rank-1 row filtering; non-budget-40 filtering; extract-CSV roundtrip with duplicate detection; cell-key separation + backward compat; summarize() cell-separation integration; 98.333% CI emission; bootstrap_spec_v2d; k-draw SWAMPED for support violation / std collapse / argmax OOB / missing data / single-missing-column × 4 / partial coverage; exact std-floor boundary at 1.999 vs 2.001; sweep-YAML hash-dedup; main() end-to-end subprocess integration with `--paired-plastic40-baseline-csv`).

READY-TO-LAUNCH state: all engineering items (1-5) discharged; codex-v1 through codex-v6 review rounds complete with all P1 + P2 findings addressed; pytest suite green excluding one pre-existing unrelated mask-test. Target-SHA will be pinned upon commit.

**2026-04-23 (v5 post-codex-v5 review; 2 new P1 + 2 P2 surfaced by deeper inspection on argmax aggregation and missing-k-draw-data gap; all 4 discharged in-place on the v4 working text).**

Codex-v5 re-review (second post-engineering round) verdict: **GATE FAIL** (2 P1 + 2 P2; original codex-v4 P1s both PASSED). The failures were traceable to incomplete v4 coverage rather than fresh design issues.

- **Codex-v5 P1-1** (`random_sample_mechanism_draw_spread` 4-tuple not fully surfaced — `argmax_index` never aggregated or bound-checked at the cell level): v5 discharge adds `winner_k_argmax_index_min`/`winner_k_argmax_index_max` aggregates to the per-cell summary row; adds Guard-6(c) argmax bound check that routes Row 6 SWAMPED on any seed with `argmax_index ∉ [0, budget-1]`. Pytests `test_summarize_flags_random_sample_swamped_on_argmax_out_of_bounds` + `test_summarize_emits_argmax_aggregates` added.
- **Codex-v5 P1-2** (Guard-6(c) silently passes when `winner_k_draw_*` data is entirely missing on a random-sample cell): v5 discharge adds explicit SWAMPED triggers for (a) random-sample cell with 0 k-draw values AND ≥1 member, and (b) random-sample cell with partial k-draw coverage. Pytests `test_summarize_flags_random_sample_swamped_on_missing_kdraw_data` + `test_summarize_flags_random_sample_swamped_on_partial_kdraw_data` added. (Note: v5's missing-data check was single-column on `winner_k_draw_min`; codex-v6 surfaced this gap and v6 upgrades to all-4-column enforcement — see next entry.)
- **Codex-v5 P2-1** (std-collapse test didn't verify the exact `0.05 * budget` boundary): v5 discharge adds `test_summarize_std_collapse_exact_threshold_boundary` with 1.999 (below-floor, SWAMPED) and 2.001 (above-floor, clean) cases at budget=40.
- **Codex-v5 P2-3** (no integration test for `main()` with `--paired-plastic40-baseline-csv`): v5 discharge adds `test_main_paired_plastic40_baseline_flag_writes_confirmatory_to_summary_json` — subprocess invocation of `analyze_plasticity.py` + JSON inspection. Asserts `paired_bootstrap_plastic40_vs_random40` appears in the written summary JSON with all expected keys and non-NaN CI values.

---

**2026-04-23 (v4 post-engineering + post-codex-v4 review; engineering items 1-5 discharged; all 2 P1 + 4 P2 codex-v4 findings discharged in-place on this working text).**

Engineering landed:
- `src/folding_evolution/chem_tape/plasticity.py`: new `adapt_and_evaluate_one_random_sample` + `_eval_at_delta` shared helper + `_make_individual_rng` per-individual deterministic rng + dispatch in `evaluate_population_plastic` on `cfg.plasticity_mechanism`.
- `src/folding_evolution/chem_tape/evolve.py`: 4 new `final_k_draw_*` fields on `EvolutionResult`; call-site capture at both `run_evolution` and `_run_evolution_islands`.
- `experiments/chem_tape/run.py`: NPZ writer extended for the 4 k-draw arrays (gated on random-sample mechanism presence).
- `experiments/chem_tape/analyze_plasticity.py`: METRIC_DEFINITIONS +4 entries (f_and_test_plastic_seed_boot_ci_98_333, f_and_test_plastic_paired_boot_ci_plastic40_vs_random40, delta_final_cell_support_bounds, random_sample_mechanism_draw_spread); `_cell_key` extended to 5-tuple including `plasticity_mechanism`; `_row_common` carries `plasticity_mechanism` per row with backward-compatible default; `analyze_run` extracts per-run `winner_k_draw_*` from NPZ; `summarize()` emits per-cell delta_final support-bounds, k-draw min/max/std/argmax aggregates, and Guard-6(c) `winner_k_draw_swamped` flag; new `bootstrap_mean_ci_98_333`, `extract_plastic_budget40_indicators_from_csv` (with duplicate-seed detection), `paired_bootstrap_plastic40_vs_random40` (primary confirmatory); `main()` grows `--paired-plastic40-baseline-csv` flag that wires the confirmatory test into the written summary JSON.
- `experiments/chem_tape/sweeps/v2/v2_5_plasticity_2d.yaml`: new sweep YAML (4 cells × 20 seeds = 80 runs).
- `queue.yaml`: new `v2_5_plasticity_2d` entry with 10800s timeout.
- Tests: `tests/test_chem_tape_plasticity.py` extended with 6 §2d mechanism tests; `tests/test_analyze_plasticity_v2d_metrics.py` created with 30 §2d analyzer tests covering CI width, SWAMPED triggers, argmax bounds, missing-data detection, std-floor boundary, cell-key separation, mixed-mechanism integration through summarize(), sweep-YAML hash-dedup, and main() end-to-end integration with the paired-bootstrap flag.

Codex-v4 review verdict: **GATE FAIL** (2 P1 + 4 P2).

- **Codex-v4 P1-1** (new §2d helpers dead from `summarize()`/`main()` entrypoint; live path still used 97.5% CI; no §2d outputs in summary JSON): v5 extended `summarize()` to emit `f_and_test_plastic_seed_boot_ci_98_333_{lo,hi}`, `delta_final_cell_support_bounds_*`, `winner_k_draw_*`, `winner_k_draw_swamped{,_reason}`, and added `bootstrap_spec_v2d` at the top level. Extended `main()` with `--paired-plastic40-baseline-csv` flag that invokes `paired_bootstrap_plastic40_vs_random40` and appends result as `summary['paired_bootstrap_plastic40_vs_random40']`.
- **Codex-v4 P1-2** (`extract_plastic_budget40_indicators_from_csv` silently overwrote duplicate seeds; `paired_bootstrap` didn't detect baseline duplicates): v5 changed the extract function's return type to `dict[int, int | list[int]]` — duplicate seeds yield list values; `paired_bootstrap_plastic40_vs_random40` now detects `isinstance(value, list)` and routes Row 6 SWAMPED with "duplicated seed(s)" reason.
- **Codex-v4 P2-1 (cell support-bounds + k-draw sanity not emitted at summary level):** v5 emits `delta_final_cell_support_bounds_{min,max,std}`, `delta_final_cell_abs_mean`, `winner_k_draw_{min_min,max_max,std_min,std_mean}`, `winner_k_draw_swamped{,_reason}` per cell.
- **Codex-v4 P2-2 (no integration test for mixed rank-1/random-sample rows through summarize()):** v5 added `test_summarize_separates_rank1_and_random_cells_at_matched_budget`.
- **Codex-v4 P2-3 (no test at `std_draws >= 0.05 * budget` threshold):** v5 added two SWAMPED trigger tests (`test_summarize_flags_random_sample_swamped_on_std_collapse`, `test_summarize_flags_random_sample_swamped_on_support_violation`) and then added an exact-boundary edge test (`test_summarize_std_collapse_exact_threshold_boundary`) at 1.999 vs 2.001 for budget=40.
- **Codex-v4 P2-4 (no hash-dedup dry-run pytest on actual §2d sweep YAML):** v5 added `test_v2d_sweep_yaml_hashes_disjoint_from_v2c` + `test_v2d_sweep_yaml_all_random_sample_mechanism`.

Codex-v5 review verdict: **GATE FAIL** (2 P1 + 2 P2 residual; both original P1s PASS):

- **Codex-v5 P1-1** (`random_sample_mechanism_draw_spread` 4-tuple not fully surfaced; `argmax_index` never aggregated or bound-checked at the cell level): v6 (this working text) adds `winner_k_argmax_index_min`/`winner_k_argmax_index_max` aggregates to the per-cell summary row; added Guard-6(c) argmax bound check that routes Row 6 SWAMPED on any seed with `argmax_index ∉ [0, budget-1]`. Pytest `test_summarize_flags_random_sample_swamped_on_argmax_out_of_bounds` + `test_summarize_emits_argmax_aggregates` added.
- **Codex-v5 P1-2** (Guard-6(c) silently passes when `winner_k_draw_*` data is entirely missing on a random-sample cell): v6 adds explicit SWAMPED triggers for (a) random-sample cell with 0 k-draw values AND ≥1 member, and (b) random-sample cell with partial k-draw coverage (fewer rows with data than members). Pytest `test_summarize_flags_random_sample_swamped_on_missing_kdraw_data` + `test_summarize_flags_random_sample_swamped_on_partial_kdraw_data` added.
- **Codex-v5 P2-1** (std-collapse test didn't verify the exact `0.05 * budget` boundary): v6 added `test_summarize_std_collapse_exact_threshold_boundary` with 1.999 (below-floor, SWAMPED) and 2.001 (above-floor, clean) cases.
- **Codex-v5 P2-3** (no integration test for `main()` with `--paired-plastic40-baseline-csv`): v6 added `test_main_paired_plastic40_baseline_flag_writes_confirmatory_to_summary_json` — builds a synthetic sweep output dir + synthetic §2c baseline CSV, invokes `analyze_plasticity.py` as a subprocess, asserts `paired_bootstrap_plastic40_vs_random40` appears in the written summary JSON with all expected keys and non-NaN CI values.

Engineering state at this working text: **74 §2d-related tests passing** (6 mechanism + 30 analyzer + 2 §2c analyzer precedent = 74). Full project test suite: **755 passed** (1 unrelated pre-existing failure in `test_chem_tape_v2_executor.py::test_masks_for_v2_active_runs_1_to_19` — shape mismatch in alphabet masks, not touched by §2d). End-to-end pipeline smoke run confirmed mechanism dispatch + k-draw logging + support-bound invariants on Arm A `random_sample_threshold` budget=5 seed=20.

Final codex round pending to verify v5 discharges + target-SHA pin.

---

**2026-04-23 (v3 post-codex-v3 P2-discharge; PASS-WITH-P2 both P2s discharged in-place on the v3 working text — pre-engineering).**

Codex-v3 review verdict: **GATE PASS-WITH-P2** (0 P1; 2 P2). Both P2s discharged in-place per §2c precedent (the PASS-WITH-P2 discharge pattern):

- **Codex-v3 P2-1** (Hypothesis block mechanism-naming paragraph at line 23 still carried v2's stronger "no mechanism name appears in any routing clause, decision rule, or scope tag" claim, not literally true given candidate-name labels in chronicle-time-only explanatory prose): rewrote the paragraph to match the accurate audit-trail formulation — "no mechanism name is used as a routing variable, outcome-row title, or decision-rule gate" — plus explicit clarifier that chronicle-time-only labels in explanatory prose are NOT prereg-level routing.
- **Codex-v3 P2-2** (Setup mechanism-sanity pre-check sub-check 4 at line 85 and Guard-6 sub-criterion (c) at line 204 described top-1 aggregation as `(min_draw, max_draw, std_draws)` — 3-element — while Diagnostics / METRIC_DEFINITIONS / Status-transition checklist used 4-element `(min_draw, max_draw, std_draws, argmax_index)`): aligned both locations to the 4-element schema explicitly naming the CSV columns `winner_k_draw_min`, `winner_k_draw_max`, `winner_k_draw_std`, `winner_k_argmax_index`. Instrumentation contract is now fully coherent end-to-end.

Codex-v3 discharge verification (all prior P1s pass): axis-structure 1D (PASS), METRIC_DEFINITIONS tuple schema match (PASS), internal-control 3-variable bundle (PASS), audit-trail scoped claim (PASS), reverse precedence reachable (PASS), F-axis routing/interpretation split (PASS), Baldwin-name-as-routing-object stripped (PASS).

v3 is the current READY-TO-LAUNCH-PENDING-ENGINEERING state. Next required Status-transition items: engineering (1-6) + final codex round after engineering lands + target-SHA pin.

---

**2026-04-23 (v3 — DRAFT, pre-engineering, pre-sweep-YAML, post-codex-v2-FAIL with 2 residual P1 + 2 P2 all discharged in-place — initial v3 write).**

Codex-v2 re-review (second round) verdict: **GATE FAIL** (2 P1 + 2 P2, all traceable to incomplete v1→v2 text migration rather than fresh design issues). v3 applies corrections in-place on the v2 working text:

- **Codex-v2 P1-1 (supporting-cell routing survived in Axis structure sentence at line 151 despite v2's grid + coverage + demotion updates):** v3 REWRITES the Axis structure block to explicitly state the routing axis is **1D** (paired-bootstrap CI + point-estimate sign tie-breaker) with NO supporting-cell conjunction. Labels the correction inline as "codex-v2 P1-1 correction to v1's stale 'supporting-cell conjunction' sentence" so the reasoning trail is preserved.
- **Codex-v2 P1-2 (METRIC_DEFINITIONS `random_sample_mechanism_draw_spread` tuple schema mismatched the rest of the file):** v2 used `(min_draw, max_draw, argmax_train_fitness_plastic, std_draws)` in METRIC_DEFINITIONS but `(min_draw, max_draw, std_draws, argmax_index)` everywhere else (Setup mechanism-sanity pre-check, Guard-6 sub-criterion (c), Status-transition checklist item 1(g)). v3 aligns the METRIC_DEFINITIONS entry to the `(min_draw, max_draw, std_draws, argmax_index)` schema and adds a closing sentence naming the consistency obligation. Guard-6 launch-blocking instrumentation contract is now internally coherent end-to-end.
- **Codex-v2 P2-1 (Internal-control check block still read "only `plasticity_mechanism` varies" despite v2's §17a updates elsewhere):** v3 rewrites the Internal-control "Tightest internal contrast" line to say "the mechanism-choice bundle varies (single nominal config field `plasticity_mechanism`, but 3 directly-derived co-moving process variables per §17a audit: δ-selection procedure, reachable-δ space, stopping semantics)" — matching the summary block and the principle-17a audit consistently.
- **Codex-v2 P2-2 (audit-trail absolute claim "no mechanism name appears in any routing clause, decision rule, scope tag, or outcome-row title" was not literally true because candidate-name *labels* appear in explanatory prose at the chronicle-time-only scope):** v3 softens the audit-trail claim to "no mechanism name is used as a routing label, outcome-row title, or decision-rule variable" (what is actually true) and adds a clarifying sentence distinguishing prereg-level routing semantics (stripped in v2) from chronicle-time-scoped explanatory labels (retained as non-routing prose examples). No new content added to the prereg's routing pre-commitments.

v3 also re-verifies codex-v2 PASS findings (P1-2 reverse-precedence; P1-3 routing/discrimination split; P1-4 Baldwin-name-as-routing-object stripped). All remain PASS at v3.

v3 submits to codex-v3 next; expect 0-1 more rounds based on §2c precedent (4 codex rounds total to READY-TO-LAUNCH).

---

**2026-04-23 (v2 — DRAFT, pre-engineering, pre-sweep-YAML, post-codex-v1-FAIL with 5 P1 + 3 P2 all discharged).**

Codex-v1 adversarial review verdict: **GATE FAIL** (5 P1 + 3 P2). v2 applies full correction set:

- **Codex-v1 P1-1 (supporting-cell predicate was routing-critical on plain point-estimate sign; §25b violation — plain cell-means cannot route a critical clause on a metric whose distribution is not known from precedent):** v2 REMOVES the supporting-cell consistency predicate from row clauses entirely. Row 2 (GRID-MISS-SUPPORTING) from v1 is DELETED. Supporting-cell cross-mechanism information at plasticity_budget ∈ {5, 10, 20} is §26-demoted to chronicle-time descriptive-only context (parallel to §2c's §26 handling of secondary axes). Fix per §25b option (c): metric demoted from routing to pre-committed chronicle-time inspection.
- **Codex-v1 P1-2 (precedence wrong — primary-endpoint REVERSE at budget=40 could be swallowed by supporting-cell grid-miss, rendering H-reverse unreachable when supporting is also negative):** resolved as a direct consequence of P1-1 fix. With the supporting-cell routing axis removed, Row 5 REVERSE has no higher-precedence row that can pre-empt it (Row 6 SWAMPED is orthogonal infrastructure-only). Precedence clarified in v2 outcome-grid block.
- **Codex-v1 P1-3 (primary F-axis doing double duty as routing gate AND mechanism discriminator; §25c violation + §17a aggravated — "plasticity-specific vs extra-slack" framing smuggled mechanism-naming into routing):** v2 SPLITS routing from mechanism-interpretation per §25c. Routing is **direction-only** on the paired-bootstrap CI at budget=40 (CI_lo > 0 / CI_hi < 0 / overlap plus point-estimate sign). Mechanism-interpretation narrative (plasticity-specific vs extra-slack vs other readings) is chronicle-time §16c work only, gated by the §16c ≥3-falsifier requirement at time of any name proposal. All outcome-row titles renamed to direction-only tokens (PASS-POSITIVE, PARTIAL, SATURATION, REVERSE, CATCHALL, SWAMPED).
- **Codex-v1 P1-4 (§16c not actually deferred — `Baldwin-at-operator-level` repeatedly invoked as named object whose falsifiers this prereg can discharge or falsify pre-commit):** v2 STRIPS all references to `Baldwin-at-operator-level` as a named object from routing clauses, decision rules, scope tags, hypothesis descriptions, and audit trail. No mechanism name appears anywhere in the prereg's routing or interpretation pre-commitments. Chronicle-time §16c work may propose names (including `Baldwin-at-operator-level` or alternatives) but must do so with its own ≥3-falsifier block; §2d provides at most one axis of directional evidence that a chronicle-time naming round MAY use as a pre-committed falsifier, without this prereg pre-committing the name or the falsifier list.
- **Codex-v1 P1-5 (Guard 6 under-instrumented if sub-criterion (c) deferred — only `delta_final` selected value was validated, not the k-draw distribution; Row 7 SWAMPED-level authority was unearned):** v2 UPGRADES Guard 6 sub-criterion (c) from optional-defer to **MANDATORY at launch**. Engineering item 1(g) is now launch-blocking: per-individual k-draw logging `(min_draw, max_draw, std_draws, argmax_index)` emitted from `adapt_and_evaluate_one_random_sample`, propagated to per-run CSV columns, with per-run invariants `min_draw ≥ −budget`, `max_draw ≤ +budget`, `std_draws ≥ 0.05 · budget`, `argmax_index ∈ [0, k−1]` enforced via mechanism-sanity pre-check. Engineering estimate bumped from ~8-12h to **~9-14h**.
- **Codex-v1 P2-1 (scope tag overclaims across budgets {5, 10, 20, 40}; only budget=40 is confirmatory):** v2 tightens scope tags to explicitly separate "confirmatory cell: n=20 paired at plasticity_budget=40" from "descriptive-only (not confirmatory): n=20 per cell at plasticity_budget ∈ {5, 10, 20}". §17b tested-set discipline preserved.
- **Codex-v1 P2-2 (§17a prose inconsistency — summary says "only plasticity_mechanism differs" while audit admits 3-variable bundle):** v2 harmonizes across all mentions: the summary, internal-control block, and principle 17a audit all consistently say "mechanism-choice bundle with 3 directly-derived co-moving process variables (δ-selection, reachable-δ space, stopping semantics)." The "only plasticity_mechanism" phrasing is removed.
- **Codex-v1 P2-3 (false "already implied" sentence in coverage verification — a negative-CI at budget=40 is NOT implied to come with negative supporting-cell signs):** v2 REWRITES the coverage verification block. With the supporting-cell axis removed from routing (P1-1), the coverage verification is now a 1D enumeration across (CI sign × point-estimate sign); the false implied-negative sentence is deleted.

v1 is preserved in git commit history at the pre-amendment commit; v2 is the current working state. v2 submits to codex-v2 next; expect additional P1/P2 rounds per §2c precedent.

---

**2026-04-23 (v1 — DRAFT, pre-engineering, pre-sweep-YAML, pre-codex-review).** First committed draft. Drafted via research-rigor skill prereg-mode against locked design from `Plans/_v2-5-plasticity-2d_session_prompt.md`. Hard-gate summary:

- **Principle 1** (internal control): paired cross-mechanism at matched budget=40 is the tightest within-family contrast — in-sweep.
- **Principle 2 + 2b + 26**: 7-row precedence-ordered outcome grid with coverage verification across (CI sign × consistency status) cells; secondary axes §26-demoted with explicit rationale.
- **Principle 4 + 28b**: 6 guards, 2 multi-mode conjunctions (guards 3 and 6).
- **Principle 6**: all thresholds baseline-relative; no imported numerics.
- **Principle 16c**: mechanism naming DEFERRED; `Baldwin-at-operator-level` label remains deferred; Row 1 PASS discharges one future §16c falsifier pre-commit.
- **Principle 17a/17b**: single nominal mechanism field with 3 directly-derived co-moving process variables named explicitly; tested-sets used verbatim.
- **Principle 20**: sampler unchanged — not triggered.
- **Principle 22 + 22a + 22b**: 1 confirmatory test; joins `plasticity-narrow-plateau` family at size 3; corrected α = 0.05/3 ≈ 0.01667 → 98.333% two-sided CI.
- **Principle 23**: param-identity to §2c except mechanism; hash-dedup verified at checklist item 3.
- **Principle 25 + 25b + 25c + 27**: primary routing-only (§25b option b valid given §2c distribution precedent); secondary axes §26-demoted (§25b option c by design); no double-duty clauses (§25c satisfied); engineering discharged at checklist item 1; METRIC_DEFINITIONS extensions pre-committed verbatim.
- **Principle 29**: §2c's Row 2 PARTIAL was a pre-registered row, not FAIL/grid-miss, so §29 not directly invoked; §2d motivated by §2c's scientific ambiguity between plasticity-specific and extra-slack readings (a §2b-style interpretive hole).

v1 submitted to codex adversarial review after engineering items 1-6 discharge and baseline-CI precompute lands. Expect at least 1 P1/P2 round based on §2c precedent (4 rounds pre-data, 3 rounds post-data on §2c chronicle).
