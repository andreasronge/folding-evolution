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
- **Mutation-neighbor sampling protocol:** for each (seed, task) pair, sample one-step mutation neighborhoods at **two milestone-source tiers**. Sampling is **stratified-uniform across the trajectory**, not earliest-first (earliest-first would bias the primary `M_near` readout toward first-encounter accessibility rather than generic near-canonical local geometry — a material mismatch with the landscape-cliff interpretation; addressed per codex P1 review):
  - **Near-canonical tier** (primary): collect all trajectory generations where best-of-pop milestone = `near-canonical`; deduplicate by extracted-program token-set (keep distinct token-sets, discard repeats); from the deduplicated set, sample up to 5 states **uniformly at random with a fixed RNG seed 42** (reproducible).
  - **Partial tier** (diagnostic): same protocol (all partial-milestone gens → dedup by token-set → uniform-random sample of 5). For Pair 1, additionally enforce at least one state at each of {2, 3, 4} canonical-token counts if available (stratified-by-token-count); for §v2.3 (where "partial" = exactly 2 of 4 tokens), stratification is not applicable.
  For each identified state at either tier, sample K=50 one-step mutations (single-byte change on the genotype), run each through `extract_bp_topk_program` + milestone classifier, evaluate on the task's `n_examples=64` training set using the existing fitness function. Record milestone + fitness for each mutant.
- **Expected sampling volume:** ≤ 20 seeds × 2 tasks × 2 tiers × 5 states × 50 mutants = ≤ 20 000 one-step fitness evaluations. At ~10 ms each ≈ 200 s. Adds ~3 min to prior CPU estimate; no evolutionary compute.
- **Seeds:** 0-19 for both tasks (existing sweep seeds; matched pairing).
- **Est. compute:** ~8 min total CPU. Milestone classification: ~20 k genotype decodes (20 seeds × 1500 gens × 2 tasks), each ~1 ms. Mutation-neighbor sampling across both tiers (near-canonical + partial): up to 20 k evaluations (≤200 source states × 50 mutants × 2 tasks), each ~10 ms fitness eval. No evolutionary compute.
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

Definitions (cluster-aware at the seed level per codex P1 review — mutants are clustered within source states and states within seeds; pooling mutants into one Wilson CI would overstate precision):

- `R_seed = per-seed per-generation transition rate to canonical`: for each seed, count generations where milestone transitions `∗ → canonical` (from any lower milestone), divide by generations spent below canonical (0 if seed never reaches canonical). `R` = mean of `R_seed` across the 20 seeds; report seed-level values.
- `M_near_seed = per-seed near-canonical escape rate`: for each seed with ≥1 sampled near-canonical state, compute the fraction of mutants (pooled across that seed's ≤5 sampled states × K=50 mutants, so ≤250 mutants per seed) whose extracted program is canonical. Seeds without a near-canonical sample are excluded from the `M_near_seed` distribution (reported separately as "seeds-without-sample count"). `M_near` = mean of `M_near_seed` across contributing seeds; inference is at the seed level (clustered, not pooled).
- `M_partial_seed = per-seed partial-tier bypass rate`: same per-seed construction on the partial tier. **Diagnostic only** — the partial bucket is heterogeneous across tasks with different canonical-set sizes, so cross-task ratios on all-of-partial are uninterpretable. See "Secondary diagnostic: matched-missing-tokens comparison" below for the one principled cross-task comparison.

**Secondary diagnostic: matched-missing-tokens `M_partial`.** Per codex P2 review, the pooled cross-task `M_partial` comparison is uninterpretable but a **missing-count-matched** comparison is principled: Pair 1's "partial-with-4-canonical-tokens-present" subset (missing 2 of 6) vs §v2.3's "partial-with-2-canonical-tokens-present" subset (missing 2 of 4) are both "missing-2-tokens" states. Diagnostic comparison of these matched subsets is reported (Wilson CI at seed-level); still not used in outcome-table thresholds.

**Row-fire gating order.** Before any PASS/INCONCLUSIVE row fires, the **CONTROL-DEGENERATE** row is evaluated first. If its criterion holds, it takes precedence and the ratio-based rows do not fire (per codex P1 review — §v2.3 `sum_gt_5_slot` spot-check shows 11/20 seeds solve before gen 10, 15/20 before gen 20; the R_23 denominator is dominated by gen 0-20 dynamics and ratios are division-noise).

| outcome | criterion | interpretation |
|---|---|---|
| **CONTROL-DEGENERATE** (evaluated first; short-circuits the ratio rows) | `sum_gt_5_slot` first-canonical-set generation < 20 for ≥ 10 / 20 seeds, OR average gens-below-canonical on §v2.3 < 50 | `R_23` denominator is dominated by gen 0-20 dynamics; the ratio `R_P1 / R_23` is division-noise. Ratio-based PASS / PASS-partial / INCONCLUSIVE verdicts are not supported. **Chronicle-only report** with raw per-seed counts (#seeds-canonical-by-gen-X for both tasks, per-seed `M_near_seed`). No findings-level claim. Follow-up: introduce a harder 4-token integer body as the new baseline, OR use §v2.3 `sum_gt_10_slot` secondary (Fmin = 19/20, likely slower canonical times — verify before using). Re-prereg as §v2.7'. |
| **PASS — landscape cliff at near→canonical** | **All of:** (a) `R_P1 / R_23 ≤ 0.1`, (b) one-sided paired test on per-seed `R_seed` gives p < 0.05 (test selection below), (c) `M_near_P1 / M_near_23 ≤ 0.1`, (d) one-sided paired Wilcoxon on per-seed `M_near_seed` gives p < 0.05 over contributing seeds | Pair 1's failure is a local landscape property: near-canonical → canonical is a sparse-neighbor cliff on the 6-token body. Supports "assembly difficulty via landscape-level transition bottleneck" as a mechanism reading for §v2.6 Pair 1. **Confound-bound:** body-length ↔ string-domain. |
| **PASS — partial: trajectory gap with *positive* evidence against local cliff** | **All of:** (a) `R_P1 / R_23 ≤ 0.1`, (b) one-sided paired test on `R_seed` p < 0.05, (c) `M_near_P1 / M_near_23 > 0.3` (clearly non-cliff on landscape, not just weaker-than-10×), (d) one-sided paired Wilcoxon on `M_near_seed` p > 0.05 (test also does not support cliff) | The transition gap is trajectory-level, not landscape-level: when Pair 1 *does* visit near-canonical, one-step escape to canonical is available, but the population rarely gets there. Mechanism reading shifts from "local cliff" to "upstream bottleneck" (population stuck at partial or below). **Note (codex round-2 P1):** prior version used `M_near_P1/M_near_23 > 0.1` OR `p > 0.05` which conflated "no evidence for cliff" with "evidence against cliff"; this row now requires affirmative non-cliff evidence on both ratio and test. Intermediate cases fall through to INCONCLUSIVE. |
| **INCONCLUSIVE — comparable rates OR landscape-signal ambiguous** | **Fires if either (i) or (ii):** **(i)** `(0.1 < R_P1 / R_23 < 3)` AND `(R_seed paired test p ≥ 0.05)` — i.e., R-gap not resolved. **(ii)** `(R_P1 / R_23 ≤ 0.1)` AND `(R_seed paired test p < 0.05)` — i.e., R-gap confirmed — AND `(M_near_P1 / M_near_23 ∈ (0.1, 0.3])` OR `(M_near paired Wilcoxon underpowered, \|S_paired\| < 10)` — i.e., landscape evidence is ambiguous even though R-gap is present. | Per-generation rate gap is absent or landscape signal is too weak to distinguish PASS from PASS-partial. Pair 1's failure may be earlier (seeds rarely reach partial), downstream (canonical-set reached but fails execution), OR a partial landscape cliff that this experiment cannot resolve at n=20 with the available near-canonical-visits. Follow-up: upstream-milestone breakdown, stack-order milestone, and — if landscape signal is what's ambiguous — a larger-n sweep or longer-trajectory sweep to boost near-canonical visit counts before re-running §v2.7. |
| **UNEXPECTED — Pair 1 never reaches near-canonical in trajectory** | 0 near-canonical trajectory states observed across all 20 Pair-1 seeds × all generations | §v2.6's winner decode (post-hoc on best-of-run) showed 8/20 at near-canonical; if 0 appear in the best-of-each-generation trajectory, the population visits near-canonical at evaluation-end but not as a best-of-pop state, meaning this milestone ladder (best-of-pop only) is the wrong granularity. Outcome table was incomplete (principle 2). Redesign: top-K-of-pop milestone tracking, re-prereg as §v2.7'. |

**Partial-outcome breakdown (always reported, regardless of outcome row):** `R` decomposed into `partial → near-canonical` and `near-canonical → canonical` sub-rates; report each separately to distinguish upstream from downstream bottlenecks.

**Interpretation augmentation from `M_partial` (diagnostic, does not change outcome-row assignment):**

`M_partial` tests whether a *direct* partial→canonical mutation edge exists locally, bypassing near-canonical as a waypoint. Under each primary outcome:

- **PASS (landscape cliff at near→canonical):** if `M_partial_P1 ≈ 0` **and** `M_near_P1 / M_near_23 ≤ 0.1`, the mechanism reading is **strong cliff** — no short path exists locally at either source tier. If `M_partial_P1 > 0`, a direct partial→canonical mutation edge exists but evolution doesn't route through it; the mechanism reading is **preferred-path-dead-ends** rather than absolute cliff — near-canonical is a local attractor that traps search even though bypass edges exist. The PASS row still stands but the interpretation narrows.
- **PASS-partial (trajectory gap without local cliff):** `M_partial_P1` is a secondary consistency check. A non-trivial `M_partial_P1 > 0` alongside `M_near_P1 / M_near_23 > 0.1` reinforces "local landscape is walkable; trajectory is the bottleneck." A near-zero `M_partial_P1` alongside non-cliff `M_near` is internally inconsistent and flags classifier mis-definition or sampling artifact — re-inspect before publishing.
- **INCONCLUSIVE:** `M_partial` is reported but adds no resolution; its comparable-across-tasks reading is uninterpretable because "partial" buckets differ in size.
- **UNEXPECTED (Pair 1 never reaches near-canonical in trajectory):** `M_partial_P1` becomes the **primary** landscape question post-hoc. If `M_partial_P1 > 0`, a direct partial→canonical edge exists — the UNEXPECTED outcome doesn't imply unreachable canonical, just unreachable-near-canonical-in-best-of-pop-trajectory. Report `M_partial_P1` with raw per-state counts and flag as "primary finding given UNEXPECTED primary outcome" rather than "diagnostic."

This augmentation does not change *which* outcome row fires; it adjusts the mechanism *interpretation* reported under the fired row. The outcome-table thresholds remain on `R` and `M_near` exclusively.

## Degenerate-success guard (required)

- **Too-clean result to guard against:** `R_P1 = 0` exactly (no Pair 1 seed ever reaches canonical in any trajectory generation) combined with `R_23 ≫ 0`. This is consistent with PASS but could also be a classifier artifact.
- **Candidate degenerate mechanisms, each checked individually before verdict:**
  1. **Classifier mis-definition on strings**: `MAP_EQ_R` has sibling tokens (`MAP_EQ_E`, etc). Our canonical-set is strict (exact `MAP_EQ_R` required). Precommit: strict match is primary; permissive (`any MAP_EQ_*` satisfies) is reported as secondary. **Hardening per codex P2:** if permissive and strict fire *different* outcome rows, this is **not** a minor sensitivity check — the core milestone definition is not robust, and the mechanism reading under the primary row must be qualified as "definition-sensitive" in the chronicle. If the two definitions fire the same row but with substantially different ratio magnitudes (e.g., strict ratio crosses the 0.1 threshold while permissive doesn't, or vice versa), flag equally. Any such instability pushes the outcome toward treating §v2.7 as a scaffolding experiment rather than a mechanism-grade reading; findings promotion in the future pass must wait for a definition-stable milestone (likely via a structurally-matched 4-token string body in §v2.8).
  2. **Stack-order invisibility**: 4/20 Pair 1 solvers may reach canonical-set earlier than they solve (fitness rises) because execution also requires correct token order. Guard: compute per-seed delta `first-gen-canonical-set − first-gen-solve (fitness ≥ 0.999)`. If the median delta is ≥ 100 gens, the token-set milestone is decoupled from fitness — report this and caveat the PASS.
  3. **§v2.3 control saturates too early (control-degenerate)**: codex spot-check on `experiments/output/2026-04-14/v2_3_fixed_baselines/*/history.csv` showed 11/20 `sum_gt_5_slot` seeds reach fitness ≥ 0.999 before gen 10 and 15/20 before gen 20 — canonical-set is likely reached even earlier. The denominator of `R_23` is then dominated by gen 0-20 dynamics and the ratio `R_P1 / R_23` is division-noise. This degeneracy is elevated to a **first-evaluated outcome row** ("CONTROL-DEGENERATE") in the outcome table, not just a guard: if `sum_gt_5_slot` first-canonical-set gen < 20 for ≥ 10 / 20 seeds, OR average gens-below-canonical < 50, the ratio rows short-circuit and the chronicle reports raw per-seed counts only. Guard inspection: compute both triggers and report, regardless of fire; if control-degenerate fires, follow-up is to redesign the baseline (harder 4-token integer body, or use `sum_gt_10_slot` Fmin=19/20 if it's slower). Addresses codex P1.
  4. **Best-of-pop-trajectory as primary data source (scope caveat)**: the entire analysis reads `history.csv` per-generation best-of-pop genotypes. Population-state claims (population diversity, second-best trajectories, migration dynamics) are out of scope — analysis is about best-of-pop trajectory only. The chronicle must state this caveat at the top, not just under the UNEXPECTED row.
- **Inspection commitment:** all four checks above (classifier-strictness, stack-order-invisibility, control-degenerate, best-of-pop-scope) run as standing diagnostics in the analysis script; each must report a pass/fail/flag status in the chronicle regardless of the primary verdict.

## Sampler-design audit (principle 20)

**Not triggered.** This experiment does not change the training input distribution for either task — it uses each task's existing `build_task(cfg, seed)` output verbatim, with the same `n_examples=64`, `holdout_size=256`, and the same seed values (0-19) as the source sweeps. Class balance was measured and logged for all six §v2.6 tasks on 2026-04-15 (0.500 train / 0.500 holdout across all tasks, stratified sampler); `sum_gt_5_slot` and `sum_gt_10_slot` are similarly stratified per their respective task builders. No sampler-driven proxy accuracy shift applies. If this prereg later expands to vary the sampler (e.g., to disambiguate the string-domain confound), the §20 audit (class balance, proxy accuracy, label-learnability) must be added before that variant runs.

## Statistical test

Two paired tests, chosen **before** looking at the data, with a pre-declared fallback for zero-dominated R distributions (per codex P1 review — Pair 1 has 4/20 solving seeds in the source sweep; canonical is stricter than solve, so the `R_seed_P1 = 0` mass is expected to be ≥ 8/20 on typical runs).

### Primary test on `R` (trajectory rate)

- **Default test:** paired Wilcoxon signed-rank on per-seed `R_seed`, Pair 1 vs §v2.3 on shared seeds 0-19. Null: `R_seed_P1 = R_seed_23`; alternative (one-sided): `R_seed_P1 < R_seed_23`.
- **Fallback when Wilcoxon is ill-posed (pre-declared, not reactive):** if ≥ 8 / 20 seeds have `R_seed_P1 = 0` (zero-mass fraction ≥ 40%), Wilcoxon on continuous-R loses power. Use **exact paired binary test on `I(R_seed > 0)`** — McNemar with exact binomial on the discordant-pair count (equivalent to an exact sign test on discordant pairs). Null: marginal rate of `R_seed > 0` equal between tasks; alternative (one-sided): Pair 1 has fewer seeds with any canonical-set transition than §v2.3. (At n=20 the discordant count `b + c ≤ 20`, so the large-sample Wilson approximation is never appropriate here — exact binomial only. Addresses codex round-2 P2.)
- **Both tests reported regardless of which fires.** The fallback is not a redo — it is a different test with a pre-declared trigger (per methodology §7 intent: paired McNemar on shared-seed comparisons).
- **Significance threshold:** α = 0.05, one-sided.

### Primary test on `M_near` (landscape metric)

- **Pre-declared paired-analysis set (codex round-2 P1):** let `S_P1 = seeds that contribute ≥1 near-canonical sample on any_char_count_gt_1_slot`, and `S_23 = seeds that contribute ≥1 near-canonical sample on sum_gt_5_slot`. The paired Wilcoxon test is computed **on `S_paired = S_P1 ∩ S_23`** — the intersection of seeds that contributed on *both* tasks. Seeds in `S_P1 \ S_23` or `S_23 \ S_P1` are reported descriptively (seed count + per-seed `M_near_seed` value on the contributing task) but are **not** used in the paired test. This is pre-declared, not chosen after looking at the data.
- **Test:** paired Wilcoxon signed-rank on per-seed `M_near_seed` restricted to `S_paired`, Pair 1 vs §v2.3. One-sided α = 0.05. Null: equal per-seed landscape escape; alternative: Pair 1 lower.
- **Cluster-awareness:** inference is at the seed level — 20 data points per condition at most, clustered. Mutants-within-state and states-within-seed are averaged into `M_near_seed` before testing, avoiding the pooled-Wilson over-precision problem (codex round-1 P1).
- **Power guard:** if `|S_paired| < 10`, the paired test is underpowered; flag and report `M_near_seed` distributions descriptively without hypothesis testing. The PASS rows' test-significance criterion cannot be satisfied in that case and the outcome falls to INCONCLUSIVE.

### Conjunction requirement for PASS

Per the outcome table, PASS / PASS-partial require **both** the ratio threshold **and** the corresponding paired-test significance. The ratio enforces the baseline-relative magnitude; the test enforces that the signal is not a tie-heavy coincidence. This closes the "ratio-vs-CI contradiction" flagged by codex P1 (previous version contradicted itself between outcome-row ratio language and stats-section CI language).

### Diagnostic reporting (no thresholds)

- `M_partial_P1` and `M_partial_23` reported as per-seed distributions with Wilson 95% CIs at the seed level; no ratio or hypothesis test on pooled partial.
- **Matched-missing-tokens `M_partial` (secondary diagnostic):** `M_partial at missing-2-tokens` on Pair 1 (subset with 4 of 6 tokens) vs §v2.3 (subset with 2 of 4 tokens) reported as per-seed distributions with Wilson 95% CIs; a one-sided paired Wilcoxon is reported if ≥ 10 seeds contribute on each side, but its result is **diagnostic** — not used in outcome-row assignment.

## Diagnostics to log (beyond fitness and milestone rates)

- Per-seed first-generation at each milestone for both tasks (`t_none`, `t_partial`, `t_near`, `t_canonical`).
- Per-seed total generations in each milestone (cumulative residence time).
- Per-seed missing-token identity at near-canonical (specifically MAP_EQ_R vs any-other on Pair 1; any-of-4 on §v2.3).
- Per-seed fitness delta at milestone advance (does token-set advance coincide with fitness jump, or decouple?).
- Stack-order validity on canonical and near-canonical states (secondary axis).
- Mutation-neighbor distribution — primary (near-canonical tier): for each sampled near-canonical state, count of mutants in each outcome bucket (canonical / near-canonical / partial / none / catastrophic-fitness-drop).
- Mutation-neighbor distribution — diagnostic (partial tier): for each sampled partial state, same outcome-bucket count plus per-state token-count (2/3/4 for Pair 1). Report per-task raw distributions; do **not** compute cross-task ratios.
- `M_partial` summary table per task: raw proportion of partial-tier mutants reaching canonical, with Wilson 95% CI and state count.
- Training-set class balance per task — already 0.500 (stratified sampler); re-verify in the script and log explicitly.

## Scope tag

**Scope-tag correction (codex P1):** the original "within-family" tag was wrong — `any_char_count_gt_1_slot` (string-domain char-count) and `sum_gt_5_slot` (integer-sum-threshold) are in different task families. The contrast is across-family with two confounded axes.

**If this experiment lands a PASS or PASS-partial, the §v2.7 chronicle records the mechanism reading — but does NOT enter `findings.md` in this pass (see Decision rule for the gating reason).** The candidate findings-entry language for a *future* promotion pass, assuming the rescue experiments have landed, would be scoped as:

`across-family · body-length + input-domain jointly confounded · n=20 on two tasks at matched compute · on INPUT <op-chain> THRESHOLD_SLOT GT bodies of length 4 (integer-sum, §v2.3) and 6 (string-count, §v2.6 Pair 1) · at pop=1024 gens=1500 BP_TOPK(k=3, bp=0.5) v2_probe alphabet · best-of-pop trajectory analysis only (no population-state claims)`

**Explicitly not claimed even after PASS:** "body length determines assembly difficulty" (confounded with input-domain), "sharp transitions are THE mechanism of assembly failure" (one signal of several — trajectory metrics without population-state analysis; full landscape metrics untested), "this generalises to other body shapes or task families beyond the two tested", "this is a BP_TOPK-specific phenomenon" (decoder-counterfactual needs §v2.6-pair1-scale-A).

## Decision rule

**Gating principle (codex P1 — resolved contradiction).** No outcome of §v2.7 promotes a claim to `findings.md` in this pass. Rationale: the body-length vs input-domain confound is unresolved by this experiment, and three rescue experiments (scale-8x, scale-A, tape24) are still in the queue. §v2.7 writes a chronicle with a mechanism *reading*; findings-promotion is a later pass, gated on at least one rescue experiment landing plus §v2.8 (body-length disambiguation).

- **CONTROL-DEGENERATE (evaluates first) →** §v2.7 chronicle reports raw per-seed counts on both tasks with no ratio-based verdict. Action: redesign baseline (harder 4-token integer body, or validate `sum_gt_10_slot` as a slower control). Re-prereg as §v2.7' once a workable baseline exists. **No findings-level claim and no mechanism reading** under this row — the ratio design did not produce interpretable data.
- **PASS (landscape cliff at near→canonical) →** §v2.7 chronicle records mechanism *reading*: "near-canonical → canonical landscape cliff on 6-token body, body-length confounded with input-domain, best-of-pop trajectory only, BP_TOPK-specific untested." Queue §v2.8 (body-length vs input-domain disambiguation: 6-token integer body OR 4-token string body) and cross-reference §v2.6-pair1-scale-A (decoder counterfactual). **No findings.md entry in this pass.** Findings promotion is gated on scale-A + §v2.8 outcomes.
- **PASS-partial (trajectory gap without cliff) →** §v2.7 chronicle reports trajectory-level bottleneck reading. Mechanism narrows from "landscape cliff" to "upstream assembly bottleneck." Follow-up: upstream-milestone breakdown (partial → near-canonical rate, none → partial rate) as single-task diagnostic §v2.7a on Pair 1 (no new sweep; same data). **No findings.md entry in this pass.**
- **INCONCLUSIVE (comparable rates) →** §v2.7 chronicle reports null result. No mechanism reading. No findings-level entry. Follow-up: stack-order milestone definition + "canonical reached but execution fails" diagnostic as §v2.7b.
- **UNEXPECTED (never reaches near-canonical in trajectory) →** §v2.7 chronicle reports classifier-granularity inadequacy per methodology §2. Best-of-pop milestone does not capture population-visited states. Redesign milestone to top-K-of-pop; re-prereg as §v2.7'. If `M_partial_P1 > 0` under this outcome, report prominently (direct partial → canonical mutation edge exists even though near-canonical isn't visited by best-of-pop) but still no findings-level claim.

**Downstream commitment (applies to the FUTURE promotion pass, not this one):** any paper-level claim about "assembly difficulty" or "transition cliffs" on chem-tape must carry the residual caveats available at the time of promotion — body-length vs input-domain (resolved by §v2.8 or still-confounded), decoder-family (tested via scale-A or not), best-of-pop vs population-state (this prereg restricts to best-of-pop). The caveats are load-bearing, not cosmetic, and must be enumerated in the findings scope tag when that promotion happens.

---

*Audit trail (skill gates + codex P1 resolution).* Outcome table has 5 rows including CONTROL-DEGENERATE (first-evaluated) and PASS-partial (Gate 2 ✓). Thresholds are ratios against this-experiment-measured baseline `R_23, M_near_23`, with matching paired tests required for PASS (Gate 6 ✓). Internal-control contrast named and confound acknowledged as across-family / body-length × input-domain confounded (Gate 1 ✓ — corrected from earlier "within-family"). Four degenerate-success candidates with detection protocols, including the control-degenerate case elevated to an outcome row (Gate 4 ✓). Sampler-design audit explicitly not-triggered with justification (Gate 20 ✓). Decision rule committed per outcome, with explicit gating that no §v2.7 outcome enters `findings.md` in this pass (principle 19 ✓, contradiction resolved). Zero new evolutionary compute; ADI run in flight is not disturbed.

**Codex adversarial review (2026-04-15, session `019d9251`).** Initial draft flagged by codex with 7 P1 findings: (1) M_near ratio-vs-CI contradiction, (2) pooled mutant Wilson CI overstates precision, (3) Wilcoxon on R likely decorative for zero-dominated data, (4) control-degenerate outcome missing from table, (5) earliest-first sampling biases landscape readout, (6) decision-rule inconsistency on findings-promotion, (7) scope tag "within-family" incorrect. **All 7 P1 addressed** in this revision. P2 findings addressed or documented: matched-missing-tokens `M_partial` added as secondary diagnostic; MAP_EQ_R strict-vs-permissive sensitivity elevated from "report both" to "flag as core-definition-instability" if outcome row changes; best-of-pop trajectory scope caveat elevated from UNEXPECTED-row-only to top-level restriction. P2 acknowledged: `partial = exactly 2 of 4` tier on §v2.3 is thin; this is a design limitation of the 4-token control rather than a fixable flaw, deferred to §v2.7' if a 5+ token integer control is introduced.
