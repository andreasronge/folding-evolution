# Pre-registration: §v2.7 — Pair 1 partial→canonical assembly-transition rates

**Status:** QUEUED · target commit `dbca965` · 2026-04-15

Derived from [docs/chem-tape/experiments-v2.md §v2.6 "Pair 1 compute-scaling"](../docs/chem-tape/experiments-v2.md#v26) and the open question in [findings.md#constant-slot-indirection](../docs/chem-tape/findings.md) "does Pair 1 resolve at 4× compute, separating search-landscape-difficulty from mechanism-absence on 6-token bodies?"

## Question (one sentence)

Is Pair 1's 4/20 failure on `any_char_count_gt_1_slot` driven by a partial→canonical assembly bottleneck — specifically a low per-generation transition rate to canonical and/or a local mutation-neighbor cliff at near-canonical states — relative to §v2.3's `sum_gt_5_slot` which solves 20/20 at matched compute?

## Hypothesis

§v2.6's winner-genotype inspection showed 8/20 failing `any_char_count_gt_1_slot` seeds reach near-canonical (5/6 tokens, missing MAP_EQ_R) and 0/20 reach canonical (6/6). Against `sum_gt_5_slot` at Fmin = 20/20 on the 4-token `INPUT SUM THRESHOLD_SLOT GT` body, if Pair 1's failure is a **landscape-level** assembly cliff at the partial→canonical step, Pair 1 will show both (a) a much lower per-generation transition rate to canonical than §v2.3, AND (b) a lower fraction of one-step mutations from near-canonical states that reach canonical. If Pair 1's failure is **trajectory-level** (population rarely visits near-canonical at all), (a) fires but (b) does not. If neither fires, the assembly-bottleneck framing is wrong and the failure is elsewhere (stack-order, execution-validity, mechanism-absence).

## Setup

- **Data source (primary, existing on disk):**
  - Pair 1 fixed-task trajectories: `experiments/output/2026-04-15/v2_6_fixed_baselines/` — `any_char_count_gt_1_slot` n=20 (primary), `any_char_count_gt_3_slot` n=20 (secondary). `history.csv` contains per-generation `best_genotype_hex`.
  - §v2.3 control trajectories: `experiments/output/2026-04-14/v2_3_fixed_baselines/` — `sum_gt_5_slot` n=20 (primary control), `sum_gt_10_slot` n=20 (secondary control). Same `history.csv` schema.
- **Analysis scripts to write:** `experiments/chem_tape/analyses/milestone_trajectories.py` (milestone classification + transition-rate computation) and `experiments/chem_tape/analyses/mutation_neighbor_sampling.py` (local neighbor sampling at near-canonical states).
- **Mutation-neighbor sampling protocol:** for each (seed, task) pair, identify up to 5 near-canonical states from the trajectory (earliest-first, deduplicated by extracted-program token-set). For each identified state, sample K=50 one-step mutations (single-byte change on the genotype), run each through `extract_bp_topk_program` + milestone classifier, evaluate on the task's n_examples=64 training set using the existing fitness function. Record milestone + fitness for each mutant.
- **Seeds:** 0-19 for both tasks (existing sweep seeds; matched pairing).
- **Est. compute:** ~5 min total CPU. Milestone classification: ~20 k genotype decodes (20 seeds × 1500 gens × 2 tasks), each ~1 ms. Mutation-neighbor sampling: ~10 k evaluations (≤100 near-canonical states × 50 mutants × 2 tasks), each ~10 ms fitness eval. No evolutionary compute.
- **Related experiments:**
  - §v2.3 — one-pair precision control providing the §v2.3 fixed-task baselines used as `R_23`/`M_23`.
  - §v2.6 Pair 1 — the assembly-failure case this experiment characterises.
  - **Queued Pair-1 follow-ups (complementary axes, independent preregs):**
    - §v2.6-pair1-scale-8x (pop=4096, gens=6000) — budget axis: does 8× compute close the solve-rate gap?
    - §v2.6-pair1-scale-A (Arm A direct GP) — decoder-arm counterfactual: is the bottleneck BP_TOPK-specific or decoder-agnostic?
    - §v2.6-pair1-tape24 — tape-length axis: does a shorter tape close the component-discovery barrier?
  - Relationship: §v2.7 (this prereg) characterises the *shape* of Pair 1's failure on existing data; the three queued experiments test *which axis can rescue* it. The §v2.7 PASS verdict is not a standalone mechanism claim — it is a mechanism *reading* that must be cross-referenced with the three rescue experiments before any findings-level claim is made. See Decision rule for the explicit dependency.

## Baseline measurement (required)

- **Baseline quantity:** §v2.3 control task's trajectory statistics — specifically (i) per-generation transition rate to canonical `R_23` on `sum_gt_5_slot`, (ii) local mutation-neighbor-to-canonical rate `M_23` from sampled near-canonical states.
- **Measurement:** this experiment computes `R_23` and `M_23` from the existing `sum_gt_5_slot` fixed-task runs; Pair 1's `R_P1` and `M_P1` are compared against these as ratios.
- **Value:** to be measured in this experiment; thresholds in the outcome table are ratios (`R_P1/R_23`, `M_P1/M_23`), not absolute numbers. Principle 6 satisfied.

## Internal-control check (required)

- **Tightest internal contrast:** `any_char_count_gt_1_slot` (6-token string body, `F_task = 4/20`) vs `sum_gt_5_slot` (4-token integer body, `F_task = 20/20`). Identical config: alphabet=v2_probe, pop=1024, gens=1500, BP_TOPK(k=3, bp=0.5), tape_length=32, n_examples=64.
- **Are you running it here?** Yes — both tasks are the comparison. No external-validity extension planned in this prereg.
- **Confound acknowledgment (required before the sweep runs):** body-length (6 vs 4 tokens) is confounded with input-domain (string vs integer) in this contrast. This experiment cannot disambiguate which axis drives any observed transition-rate gap. Clean separation needs a 6-token integer body or a 4-token string body — noted as queued follow-up §v2.8, **not claimed** by this experiment.

## Milestone definitions (pre-registered before data inspection)

**Primary axis — token-set membership** of the extracted BP_TOPK program, exact token-ID match (no wildcard unification of `MAP_EQ_*` variants):

`near-canonical` is defined structurally as all-but-one canonical token, not by matching the same percent-of-canonical across tasks.

For `any_char_count_gt_1_slot` with canonical body `{INPUT, CHARS, MAP_EQ_R, SUM, THRESHOLD_SLOT, GT}` (6 tokens):
- `none`: 0-1 canonical tokens present
- `partial`: 2-4 canonical tokens
- `near-canonical`: exactly 5 canonical tokens (one missing — label the specific missing token in diagnostics)
- `canonical`: all 6 canonical tokens

For `sum_gt_5_slot` with canonical body `{INPUT, SUM, THRESHOLD_SLOT, GT}` (4 tokens):
- `none`: 0-1 canonical tokens
- `partial`: 2 canonical tokens
- `near-canonical`: 3 canonical tokens
- `canonical`: all 4 canonical tokens

**Secondary axis — stack-order validity** (diagnostic only, not part of primary milestone): a subsequence of the extracted program that matches the canonical order `INPUT → <unary op-chain> → THRESHOLD_SLOT → GT`. Reported alongside token-set milestone for canonical and near-canonical states; not used in transition-rate thresholds.

**Per-generation milestone assignment:** for each (seed, task, generation), decode `history.csv[generation].best_genotype_hex` via `hex_to_tape` + `extract_bp_topk_program`, compute canonical-token-set intersection, assign milestone. Store the full (seed, task, generation) → milestone table as a parquet/csv for post-hoc diagnostics.

## Pre-registered outcomes (required — at least three)

Definitions:
- `R = per-seed per-generation transition rate to canonical`: for each seed, count generations where milestone transitions `∗ → canonical` (from any lower milestone), divide by generations spent below canonical. Average across seeds with standard error.
- `M = local mutation-neighbor escape rate to canonical`: across all sampled near-canonical states × K=50 one-step mutations, fraction of mutants whose extracted program is canonical.

| outcome | criterion | interpretation |
|---|---|---|
| **PASS — landscape cliff at near→canonical** | `R_P1 / R_23 ≤ 0.1` AND `M_P1 / M_23 ≤ 0.1` (one-sided paired Wilcoxon p < 0.05 on per-seed R) | Pair 1's failure is a local landscape property: near-canonical → canonical is a sparse-neighbor cliff on the 6-token body. Supports "assembly difficulty via landscape-level transition bottleneck" as a mechanism reading for §v2.6 Pair 1. **Confound-bound:** body-length ↔ string-domain. |
| **PASS — partial: trajectory gap without local cliff** | `R_P1 / R_23 ≤ 0.1` AND `M_P1 / M_23 > 0.1` | The transition gap is trajectory-level, not landscape-level: when Pair 1 *does* visit near-canonical, one-step escape to canonical is available, but the population rarely gets there. Mechanism reading shifts from "local cliff" to "upstream bottleneck" (population stuck at partial or below). |
| **INCONCLUSIVE — comparable rates** | `0.1 < R_P1 / R_23 < 3` | Per-generation transition rate differences don't explain the 4/20 vs 20/20 solve-rate gap. Pair 1's failure must be *earlier* (seeds rarely reach partial) OR *downstream* (canonical-token-set is reached but execution fails on stack-order). Follow-up: upstream-milestone breakdown + stack-order milestone. |
| **UNEXPECTED — Pair 1 never reaches near-canonical in trajectory** | 0 near-canonical trajectory states observed across all 20 Pair-1 seeds × all generations | §v2.6's winner decode (post-hoc on best-of-run) showed 8/20 at near-canonical; if 0 appear in the best-of-each-generation trajectory, the population visits near-canonical at evaluation-end but not as a best-of-pop state, meaning this milestone ladder (best-of-pop only) is the wrong granularity. Outcome table was incomplete (principle 2). Redesign: top-K-of-pop milestone tracking, re-prereg as §v2.7'. |

**Partial-outcome breakdown (always reported, regardless of outcome row):** `R` decomposed into `partial → near-canonical` and `near-canonical → canonical` sub-rates; report each separately to distinguish upstream from downstream bottlenecks.

## Degenerate-success guard (required)

- **Too-clean result to guard against:** `R_P1 = 0` exactly (no Pair 1 seed ever reaches canonical in any trajectory generation) combined with `R_23 ≫ 0`. This is consistent with PASS but could also be a classifier artifact.
- **Candidate degenerate mechanisms, each checked individually before verdict:**
  1. **Classifier mis-definition on strings**: `MAP_EQ_R` has sibling tokens (`MAP_EQ_E`, etc). Our canonical-set is strict (exact `MAP_EQ_R` required). If switching to "any `MAP_EQ_*` token satisfies" would change the outcome-row assignment, report both and flag the definition-dependence. Precommit: strict match is primary; report permissive as secondary diagnostic.
  2. **Stack-order invisibility**: 4/20 Pair 1 solvers may reach canonical-set earlier than they solve (fitness rises) because execution also requires correct token order. Guard: compute per-seed delta `first-gen-canonical-set − first-gen-solve (fitness ≥ 0.999)`. If the median delta is ≥ 100 gens, the token-set milestone is decoupled from fitness — report this and caveat the PASS.
  3. **§v2.3 control trivially at canonical from gen 0-1**: if `sum_gt_5_slot` reaches canonical in the initial random population, the denominator of `R_23` is tiny (average < 5 gens-below-canonical across seeds), and the ratio `R_P1 / R_23` is dominated by division noise. Guard: if the average seed's gens-below-canonical on §v2.3 is < 10, report raw per-seed counts instead of the rate ratio and flag the control as "canonical-trivial-at-start."
- **Inspection commitment:** all three checks run as standing diagnostics in the analysis script; each must report a pass/fail/flag status in the chronicle regardless of the primary verdict.

## Sampler-design audit (principle 20)

**Not triggered.** This experiment does not change the training input distribution for either task — it uses each task's existing `build_task(cfg, seed)` output verbatim, with the same `n_examples=64`, `holdout_size=256`, and the same seed values (0-19) as the source sweeps. Class balance was measured and logged for all six §v2.6 tasks on 2026-04-15 (0.500 train / 0.500 holdout across all tasks, stratified sampler); `sum_gt_5_slot` and `sum_gt_10_slot` are similarly stratified per their respective task builders. No sampler-driven proxy accuracy shift applies. If this prereg later expands to vary the sampler (e.g., to disambiguate the string-domain confound), the §20 audit (class balance, proxy accuracy, label-learnability) must be added before that variant runs.

## Statistical test

- **Test:** paired Wilcoxon signed-rank on per-seed `R_seed`, Pair 1 vs §v2.3 on shared seeds 0-19. Null: `R_seed_P1 = R_seed_23`; alternative (one-sided): `R_seed_P1 < R_seed_23`.
- **Significance threshold:** α = 0.05, one-sided.
- **Degenerate-test guard:** if ≥ 15 / 20 seeds have `R_seed_P1 = 0`, the test is ill-posed (massive tied-at-zero block). Report raw counts (`# seeds with R_seed_P1 = 0`, `# seeds with R_seed_23 = 0`) alongside the test result; treat the counts as the primary comparison in that case.
- **Secondary comparison:** `M_P1 vs M_23` as proportion difference with Wilson 95% CI; no separate test, CI overlap is the criterion.

## Diagnostics to log (beyond fitness and milestone rates)

- Per-seed first-generation at each milestone for both tasks (`t_none`, `t_partial`, `t_near`, `t_canonical`).
- Per-seed total generations in each milestone (cumulative residence time).
- Per-seed missing-token identity at near-canonical (specifically MAP_EQ_R vs any-other on Pair 1; any-of-4 on §v2.3).
- Per-seed fitness delta at milestone advance (does token-set advance coincide with fitness jump, or decouple?).
- Stack-order validity on canonical and near-canonical states (secondary axis).
- Mutation-neighbor distribution: for each sampled near-canonical state, count of mutants in each outcome bucket (canonical / near-canonical / partial / none / catastrophic-fitness-drop).
- Training-set class balance per task — already 0.500 (stratified sampler); re-verify in the script and log explicitly.

## Scope tag

**If this experiment lands a PASS or PASS-partial, the claim enters `findings.md` as a new entry (not a supersession of `constant-slot-indirection`), scoped as:**

`within-family · body-length-vs-string-domain confounded · n=20 on two tasks at matched compute · on INPUT <op-chain> THRESHOLD_SLOT GT bodies of length 4 (integer) and 6 (string) · at pop=1024 gens=1500 BP_TOPK(k=3, bp=0.5) v2_probe alphabet`

**Explicitly not claimed:** "body length determines assembly difficulty" (confounded), "sharp transitions are THE mechanism of assembly failure" (one signal of several — trajectory metrics and full landscape metrics untested here), "this generalises to other body shapes or task families beyond the two tested."

## Decision rule

- **PASS (landscape cliff at near→canonical) →** write up as §v2.7 chronicle. Mechanism-level reading for §v2.6 Pair 1's failure is "near-canonical → canonical assembly cliff on 6-token body (body-length confounded with string-domain)." Queue §v2.8 to disambiguate body-length from string-domain (needs a 6-token integer body or 4-token string body). New findings entry candidate: "assembly-transition cliff on long-chain bodies (body-length / string-domain confounded; n=20 × 2 tasks; within-family)".
- **PASS-partial (trajectory gap without cliff) →** §v2.7 chronicle reports trajectory-level bottleneck. Mechanism reading shifts from "landscape cliff" to "upstream assembly bottleneck." Follow-up: upstream-milestone breakdown as a single-task diagnostic §v2.7a on Pair 1 (no new sweep; same data).
- **INCONCLUSIVE (comparable rates) →** §v2.7 chronicle reports null result. No findings-level entry. Follow-up: stack-order milestone definition + "canonical reached but execution fails" diagnostic as §v2.7b.
- **UNEXPECTED (never reaches near-canonical in trajectory) →** §v2.7 chronicle reports classifier inadequacy per principle 2. Outcome table was incomplete: best-of-pop milestone does not capture population-visited states. Redesign milestone to top-K-of-pop, re-prereg as §v2.7'. No findings.md entry.

**Downstream commitment if PASS:** any subsequent paper-level claim about "assembly difficulty" or "transition cliffs" on chem-tape must carry the explicit confound ("body-length ↔ string-domain untested") and point at §v2.8 as the resolving experiment. The confound is not a minor caveat — it's load-bearing for interpretation.

---

*Audit trail (skill gates satisfied).* Outcome table has 4 rows with an explicit "partial" row (Gate 2 ✓). Thresholds are ratios against this-experiment-measured baseline `R_23, M_23`, not absolutes (Gate 6 ✓). Internal-control contrast named with explicit confound acknowledgment (Gate 1 ✓). Three specific degenerate-success candidates with detection protocols (Gate 4 ✓). Sampler-design audit explicitly not-triggered with justification (Gate 20 ✓). Decision rule committed per outcome (principle 19 ✓). Zero new evolutionary compute; ADI run in flight is not disturbed.
