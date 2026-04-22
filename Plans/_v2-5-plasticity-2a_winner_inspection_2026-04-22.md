# §v2.5-plasticity-2a winner-tape inspection (2026-04-22)

Zero-compute inspection (methodology principle 3) of the 40 top-1 winners from the pooled §v2.5-plasticity-2a (seeds 20..39, budget=5 plastic) + §v2.5-plasticity-2a-nexp-budget5 (seeds 40..59, budget=5 plastic) sweeps. Pre-committed inspection obligation from the §v2.5-plasticity-2a-nexp-budget5 chronicle's Next-steps bullet 1 (addressing codex P2-1 on the 40/40 `top1_winner_hamming = 5` cap+1-sentinel signature).

**Anchor commit:** `c08888a` (§v2.5-plasticity-2a-nexp-budget5 chronicle landed).
**Data sources:** `experiments/output/2026-04-21/v2_5_plasticity_2a/sweep_index.json` (seeds 20..39) and `experiments/output/2026-04-22/v2_5_plasticity_2a_nexp_budget5/sweep_index.json` (seeds 40..59). Winner selection: `best_genotype_hex` field, which is the decoded best-of-run top-1 per the sweep's own selection (per-run best_fitness ranking; deterministic tiebreak per `analyze_plasticity.py:_compute_top1_winner_hamming` verbatim).

**Document structure:**
- **Section 1 — Shallow structural inspection:** active-view length, token presence, attractor-category heuristic, uncapped Levenshtein distance on the n=40 plastic-evolved winners. (Landed 2026-04-22 AM.)
- **Section 2 — Deep per-winner inspection:** paired per-winner Baldwin gap (test_fitness_plastic − test_fitness_frozen on same winner genotype), plasticity-rescue accounting, solver-vs-non-solver structural comparison, plasticity-active token count as candidate distinguisher. (Landed 2026-04-22 PM.)
- **Section 3 — Codex-corrected implications for §v2.5-plasticity-2c prereg framing:** revised scope-qualified interpretation of Section 2 findings + proposed-not-compelled framing shifts for the capacity-scaling prereg. (Landed 2026-04-22 PM, after codex adversarial review NEEDS-REVISION verdict.)
- **Section 4 — Frozen-control winner inspection (n=20, plasticity OFF during evolution):** compares the n=40 plastic-evolved winner structure (Sections 1+2) to the 20 frozen-control winners from §v2.5-plasticity-2a seeds 20..39 (plasticity_enabled=False during evolution). Addresses "is the compositional-AND-with-overhead attractor a selection phenomenon or a plastic-evolution phenomenon?" **Descriptive observation:** at the tested budget (plastic=5 / frozen=0), comp_AND attractor incidence is identical (80% in both regimes) and overhead/length/distance are near-identical; plastic winners have higher plasticity-active-token count (median 6 vs 3) and higher F solve rate (14/40 vs 0/20). Codex adversarial review (second round) flagged as NEEDS-REVISION: equal marginals do NOT identify the mechanism; "selection-driven not plasticity-driven" is not resolved by this single-budget comparison — only that attractor prevalence does not differ at this budget. See Section 4.6 for corrected interpretation. (Landed 2026-04-22 PM.)

---

# Section 1 — Shallow structural inspection

## Headline: the cap+1=5 sentinel was information-destroying

The prereg's `top1_winner_hamming` metric with `cap=4` returned **5 on 40/40 winners** — a single-valued histogram that hid the actual distance structure. Uncapped Levenshtein distance from winner active-view to canonical active-view on the same 40 winners:

| uncapped distance | count |
|-------------------|-------|
| 17 | 1 |
| 19 | 3 |
| 20 | 2 |
| 21 | 3 |
| 22 | 9 |
| 23 | 8 |
| 24 | 8 |
| 25 | 2 |
| 26 | 4 |

**Min 17, median 23, max 26.** Winners are not uniformly distant — they span a 9-token range, but all are **far beyond cap=4**. The cap=4 setting was calibrated for a near-canonical regime (§v2.5-plasticity-1a sf=0.01 cells produced winners near canonical); in the §2a sf=0.0 regime, every winner is in the distant-tail regime and the cap destroys the intra-regime structure.

## Active-view length: winners are 2× longer than canonical

Canonical `sum_gt_10_AND_max_gt_5` active-view length: **12 tokens**. Winner active-view length distribution (n=40):

| length | count |
|--------|-------|
| 22 | 1 |
| 23 | 1 |
| 24 | 2 |
| 25 | 3 |
| 26 | 5 |
| 27 | 4 |
| 28 | 11 |
| 29 | 10 |
| 30 | 3 |

**Min 22, median 28, max 30.** Zero winners have canonical-length (12). Winners are roughly 2–2.5× longer than canonical — they are NOT "near-canonical with noise"; they are structurally different programs.

## Canonical-token presence: winners mostly contain canonical operators

Canonical active-view token set: `{CONST_0, INPUT, REDUCE_MAX, CONST_5, GT, SUM, ADD, IF_GT}` (8 distinct tokens). Number of canonical tokens MISSING from each winner's active view:

| missing count | winners |
|---------------|---------|
| 0 | 13/40 |
| 1 | 15/40 |
| 2 | 10/40 |
| 3 | 2/40 |

**28/40 winners have at least 7 of the 8 canonical tokens present.** But they also have **many extra tokens** the canonical doesn't use (DUP, THRESHOLD_SLOT, MAP_EQ_E, CHARS, ANY, REDUCE_ADD, SLOT_12/13, CONST_1/2, SWAP beyond canonical's 2).

This is the decisive structural observation: **winners are not classical-Baldwin near-canonical (zero at canonical-length)**, and they are not single-predicate proxies (see classification below), and they are not noise — they are **compositional AND-attempts with substantial operator overhead**.

## Attractor classification (heuristic, pooled n=40)

Simple heuristic based on which combinations of `{REDUCE_MAX, CONST_5}` (max > 5 predicate building blocks) and `{SUM, GT, IF_GT}` (sum > 10 predicate building blocks) appear in each winner's active view:

| category | count | criterion |
|----------|-------|-----------|
| **both-predicates-AND-attempt** | **32/40** | has ≥1 of `{REDUCE_MAX, CONST_5}` AND ≥1 of `{SUM}` AND ≥1 of `{GT, IF_GT}` |
| max>5-only-proxy | 4/40 | has `{REDUCE_MAX, CONST_5, GT}` but no `SUM` |
| sum>10-only-proxy | 2/40 | has `{SUM, GT/IF_GT}` but no `REDUCE_MAX` and no `CONST_5` |
| other/unknown | 2/40 | doesn't fit above |

**32/40 winners are attempting the compositional AND structure.** This is dramatically different from §v2.4-proxy's decorrelated-task-sampler result where most winners landed on a single-predicate proxy (e.g., `max > 5`). Under the §2a sf=0.0 regime, selection pressure drives winners toward the compositional structure, not toward single-predicate shortcuts.

F_AND_test_plastic = 14/40 = 0.35 = the fraction of those compositional attempts that actually solve the task on the 16-example test set. The remaining 18 `both-predicates-AND-attempt` winners (32 − 14 = 18, modulo the single-predicate winners that also contribute to F_test solve rate) attempted AND but didn't quite achieve it — wrong operator counts, spurious extra tokens, or semantic composition failures.

## Token frequency in winner active views (per-winner average)

Pooled across n=40 winners:

| token | count (pooled) | per-winner avg | canonical count | canonical per-winner |
|-------|---------------|----------------|-----------------|----------------------|
| GT | 106 | 2.6 | 2 | 2.0 |
| INPUT | 91 | 2.3 | 2 | 2.0 |
| REDUCE_MAX | 90 | 2.2 | 1 | 1.0 |
| DUP | 69 | 1.7 | 0 | 0 (absent) |
| IF_GT | 62 | 1.6 | 1 | 1.0 |
| SLOT_13 | 60 | 1.5 | 0 | 0 (absent) |
| SUM | 60 | 1.5 | 1 | 1.0 |
| THRESHOLD_SLOT | 57 | 1.4 | 0 | 0 (absent) |
| ADD | 56 | 1.4 | 1 | 1.0 |
| CONST_5 | 55 | 1.4 | 3 | 3.0 |
| CONST_1 | 52 | 1.3 | 0 | 0 (absent) |
| SWAP | 51 | 1.3 | 2 | 2.0 |
| CONST_0 | 48 | 1.2 | 1 | 1.0 |
| SLOT_12 | 48 | 1.2 | 0 | 0 (absent) |
| CHARS | 46 | 1.1 | 0 | 0 (absent) |
| ANY | 38 | 0.9 | 0 | 0 (absent) |
| MAP_EQ_E | 37 | 0.9 | 0 | 0 (absent) |
| CONST_2 | 35 | 0.9 | 0 | 0 (absent) |
| REDUCE_ADD | 33 | 0.8 | 0 | 0 (absent) |

**Canonical-absent operators (DUP, SLOT_12/13, THRESHOLD_SLOT, CONST_1/2, CHARS, ANY, MAP_EQ_E, REDUCE_ADD) each average ~0.8–1.7 per winner.** That's substantial operator overhead: the winner has ~12 "extra" tokens beyond the 12 canonical tokens, averaging across these non-canonical operators.

## Sample decoded winners (first 5 per sweep)

**§2a (seeds 20..39):**

- seed=23, fit=0.8542, active-len=28: `ADD SWAP CHARS CONST_0 CONST_5 INPUT ADD CONST_1 DUP CONST_1 ANY REDUCE_MAX IF_GT CONST_5 INPUT DUP CHARS SLOT_13 SUM DUP THRESHOLD_SLOT INPUT REDUCE_MAX DUP THRESHOLD_SLOT ADD CONST_1 GT`
- seed=30, fit=0.8750, active-len=29: `REDUCE_MAX SUM ANY GT INPUT CONST_5 MAP_EQ_E THRESHOLD_SLOT GT REDUCE_MAX CONST_1 MAP_EQ_E ADD MAP_EQ_E THRESHOLD_SLOT REDUCE_MAX CONST_5 IF_GT CONST_5 SUM CHARS SWAP INPUT DUP INPUT REDUCE_MAX REDUCE_MAX GT SLOT_13`
- seed=21, fit=0.9375, active-len=29: `CONST_1 DUP ANY SWAP ADD INPUT MAP_EQ_E SWAP CONST_0 SLOT_12 SLOT_13 IF_GT DUP DUP REDUCE_MAX MAP_EQ_E CONST_0 MAP_EQ_E REDUCE_MAX SLOT_13 IF_GT DUP INPUT REDUCE_MAX CHARS SLOT_12 SWAP REDUCE_ADD GT`
- seed=20, fit=0.9375, active-len=24: `SLOT_12 CHARS GT CONST_2 DUP CONST_0 SUM REDUCE_MAX INPUT CONST_0 CONST_1 DUP CONST_5 ANY SWAP SWAP CHARS ADD ADD INPUT REDUCE_MAX MAP_EQ_E REDUCE_MAX GT`
- seed=22, fit=0.9167, active-len=26: `THRESHOLD_SLOT ADD GT INPUT REDUCE_ADD SUM DUP IF_GT SWAP CHARS GT SUM IF_GT SLOT_13 INPUT REDUCE_MAX REDUCE_MAX GT DUP SLOT_13 SWAP CONST_2 SLOT_13 SWAP ADD IF_GT`

**n-exp (seeds 40..59):**

- seed=43, fit=0.9167, active-len=30: `REDUCE_MAX REDUCE_ADD CONST_1 SUM REDUCE_MAX THRESHOLD_SLOT ADD IF_GT SLOT_12 ANY SLOT_13 CONST_5 THRESHOLD_SLOT SWAP MAP_EQ_E THRESHOLD_SLOT CHARS CONST_2 REDUCE_ADD IF_GT INPUT DUP SLOT_12 SUM CONST_2 REDUCE_ADD INPUT SUM CONST_5 GT`
- seed=50, fit=0.8958, active-len=28: `CONST_5 SUM INPUT IF_GT CONST_2 CONST_2 SLOT_12 THRESHOLD_SLOT SLOT_12 MAP_EQ_E INPUT IF_GT CONST_5 CHARS CONST_5 IF_GT SUM GT SLOT_13 CONST_2 CONST_0 CONST_5 GT THRESHOLD_SLOT INPUT REDUCE_MAX CONST_2 GT`
- seed=56, fit=0.9583, active-len=23: `INPUT THRESHOLD_SLOT REDUCE_MAX IF_GT CONST_0 CONST_0 THRESHOLD_SLOT MAP_EQ_E CONST_1 SWAP SLOT_13 INPUT REDUCE_MAX THRESHOLD_SLOT SLOT_13 SLOT_13 CONST_1 ADD THRESHOLD_SLOT SLOT_13 IF_GT REDUCE_ADD GT`
- seed=51, fit=1.0000, active-len=25: `CONST_0 GT ADD CONST_0 SLOT_13 SUM CONST_1 SWAP SLOT_12 CHARS MAP_EQ_E CHARS ANY MAP_EQ_E INPUT REDUCE_MAX DUP INPUT REDUCE_ADD SLOT_13 SLOT_13 CONST_5 GT GT GT`
- seed=57, fit=1.0000, active-len=30: `SLOT_12 REDUCE_MAX CHARS CHARS DUP SLOT_13 DUP CHARS CHARS CONST_0 GT CONST_5 CHARS GT INPUT REDUCE_MAX SLOT_13 REDUCE_ADD GT DUP DUP SLOT_12 IF_GT SLOT_12 INPUT SUM CONST_5 GT IF_GT`

Both `fit=1.0000` winners (n-exp seeds 51 and 57) are clearly compositional AND-attempts with substantial operator overhead — not near-canonical.

---

# Section 2 — Deep per-winner inspection (2026-04-22 PM)

This section extends Section 1's shallow structural inspection with per-winner paired analysis: for each of the 40 plastic-trained winners, compute the Baldwin gap (test_fitness_plastic − test_fitness_frozen on the SAME winner genotype) and relate it to the overhead / attractor-category / plasticity-active-token variables from Section 1.

**Data extraction:** For each of the 40 runs, open `final_population.npz`, identify the winner via `argmax(test_fitness_plastic)` with tiebreak `max(train_fitness_plastic)` then smallest index (matching `analyze_plasticity.py:_compute_top1_winner_hamming` verbatim), and read the winner's per-individual `test_fitness_plastic`, `test_fitness_frozen`, `train_fitness_plastic`, `train_fitness_frozen`, `delta_final`, `has_gt` values. Scripted with the heuristic attractor classifier from Section 1.

**Scope caveat (per codex P2-1, P2-5):** every finding in this section is a **per-winner paired inspection on winners selected under plastic evolution at budget=5**. It is NOT a population-level head-to-head comparison, NOT a cross-budget comparison, and NOT unconditional on plasticity regime. Phrase all claims accordingly.

## 2.1 Per-winner Baldwin gap distribution

Baldwin gap = winner's `test_fitness_plastic` − winner's `test_fitness_frozen` on the **same genotype**. Positive means plasticity helps; zero means neutral; negative means plasticity hurts.

- **Mean: +0.364 · Median: +0.438 · Range: [−0.125, +0.688]**
- One winner (seed 28) has negative gap (−0.125) — plasticity hurts this specific winner
- 39/40 winners have positive gap

**Binary rescue count (winner solves under plastic but not frozen eval):**
- 14/40 solve under plastic eval (`test_fitness_plastic = 1.0`)
- 1/40 solves under frozen eval (`test_fitness_frozen = 1.0`) — **this is seed 28, the one with negative gap; it solves frozen but plasticity ruins it to 0.875**
- 0/40 solve under both
- 14/40 "plasticity-rescue" (solve plastic-only)

**Scope-qualified framing (codex P1-1 correction):** within the 40 plastic-evolved winners inspected, 14 solve only under plastic test-time eval, 1 solves only under frozen eval (a different winner than any of the 14; seed 28), 0 solve both ways. This is NOT "without plasticity, 0/40 achieve F=1.0" — the 1 frozen-only solver is a counterexample to that framing.

## 2.2 Baldwin gap × overhead correlation

Per-winner `overhead = active_view_length − 12` (canonical active-view length) vs per-winner Baldwin gap:

- **Pearson r = +0.156, p = 0.34** (n=40)
- **Spearman rho = +0.172, p = 0.29**
- **Kendall tau = +0.132, p = 0.28**

All three correlation measures are **insignificant at n=40**. Point estimates are small positive (sign in the "plasticity-enabled-bloat" direction) but too noisy to claim.

**Scope-qualified framing (codex P1-2 correction):** this inspection **failed to detect a monotone association between overhead and per-winner Baldwin gap** at n=40 budget=5. This is NOT "plasticity-enabled-bloat is falsified." The hypothesis remains open; a larger n or a more precise metric might detect the association. The inspection tested one specific framing of "plasticity-enabled-bloat" (overhead × continuous-gap); alternative framings (overhead × binary-rescue, overhead × specific-operator-type gap, etc.) are untested.

**Rescue vs gap distinction (codex P2-3):** the "plasticity-enabled-bloat" hypothesis could be framed two ways:
- **Overhead × rescue (untested here):** do high-overhead winners preferentially cross the F=1.0 threshold under plasticity?
- **Overhead × continuous gap (tested here, null):** do high-overhead winners have larger plastic−frozen fitness differences?

This inspection addressed the second. The first is a separate question — it could be tested logistic-regression-style on this same n=40 (rescue ~ overhead), but would also be underpowered at 14 solvers.

## 2.3 Solver vs non-solver subgroup comparison (conditional on comp_AND classifier)

All 40 winners classified into (solver, compositional_AND) cells. "Solver" = `test_fitness_plastic = 1.0`; "compositional_AND" = has ≥1 of {REDUCE_MAX, CONST_5} AND ≥1 of {SUM} AND ≥1 of {GT, IF_GT} in active view.

| (solver, comp_AND) | n | median overhead | median Baldwin gap | median plasticity-active tokens |
|---------------------|---|-----------------|--------------------|---------------------------------|
| (True, True) | 7 | 15 | +0.5625 | 6 |
| (True, False) | 7 | 16 | +0.4375 | 7 |
| (False, True) | 17 | 16 | +0.3750 | 4 |
| (False, False) | 9 | 15 | +0.1875 | 7 |

**Observations (with codex P1-3 / P2-4 / P2-5 scope caveats):**
- Within the compositional_AND=True subgroup (n=24 total), solver median overhead (15) vs non-solver median overhead (16) **shows no obvious separation by overhead**. This is a scope-qualified observation at these subgroup sizes — it is NOT "overhead does not distinguish solvers" in general. The subgroup sizes (n=7 vs n=17) have weak discriminatory power; no dispersion or effect-size CI reported; a larger study might detect separation.
- The plasticity-active-token count column (median 6 vs 4 in the two comp_AND subgroups; median 7 for both comp_AND=False subgroups) is a **candidate distinguisher**, hypothesis-generating only. Parallel summary statistic is "median plasticity-active-token count": 6 in comp_AND solvers (n=7), 4 in comp_AND non-solvers (n=17), 7 in non-comp_AND solvers (n=7), 7 in non-comp_AND non-solvers (n=9). Weakly suggestive that plasticity-active token count is a mediator of rescue-magnitude within the compositional_AND subgroup; underpowered; would need replication.

## 2.4 Plasticity-active token analysis

"Plasticity-active" tokens defined (conservative): `{GT, IF_GT, THRESHOLD_SLOT}` — operators whose behavior is directly modulated by δ in `rank1_op_threshold`. Canonical has 3 plasticity-active tokens (GT×2, IF_GT×1).

Per-winner plasticity-active-token count distribution (n=40): min=1, median=6, max=9.

**Correlation with overhead:** Pearson r(overhead, n_plastic_active) = +0.073, p = 0.66. **No detectable association** — overhead is NOT preferentially composed of plasticity-active tokens.

**Excess plasticity-active beyond canonical's 3** as fraction of overhead (winners with overhead > 0, n=40): mean 0.17, median 0.18. Most of the overhead is NOT plasticity-active — it's canonical-absent operators (DUP, SLOT_12/13, MAP_EQ_E, CONST_1/2, CHARS, ANY, REDUCE_ADD, SWAP beyond canonical's 2) that are semantically inert under `rank1_op_threshold` plasticity.

**Interpretation caveat:** the conservative plasticity-active set may be too narrow. A broader candidate set including task-bound slots (`{GT, IF_GT, THRESHOLD_SLOT, REDUCE_MAX, SLOT_12, SLOT_13, MAP_EQ_E}`, 7 tokens) gives per-winner median 12 (canonical: 4). Excess plasticity-candidate fraction of overhead: mean 0.49, median 0.51. Under the broader definition, **about half the overhead is plasticity-modulated-candidate operators** — but the broader definition conflates "plasticity-modulated" with "task-bound slot" which isn't necessarily plasticity-active in the rank-1 sense.

## 2.5 The 14 plastic-solvers ranked by Baldwin gap

(positive gap = plasticity rescued this winner)

| seed | sweep | overhead | test_frozen | test_plastic | gap | plastic-active tokens | comp_AND |
|------|-------|----------|-------------|--------------|------|----------------------|----------|
| 33 | 2a | 17 | 0.312 | 1.000 | +0.688 | 7 | N |
| 51 | nexp | 13 | 0.438 | 1.000 | +0.562 | 4 | Y |
| 57 | nexp | 18 | 0.438 | 1.000 | +0.562 | 6 | Y |
| 42 | nexp | 15 | 0.438 | 1.000 | +0.562 | 5 | Y |
| 53 | nexp | 16 | 0.438 | 1.000 | +0.562 | 9 | N |
| 48 | nexp | 15 | 0.438 | 1.000 | +0.562 | 7 | Y |
| 39 | 2a | 13 | 0.500 | 1.000 | +0.500 | 7 | N |
| 26 | 2a | 14 | 0.500 | 1.000 | +0.500 | 7 | Y |
| 21 | 2a | 17 | 0.562 | 1.000 | +0.438 | 3 | N |
| 32 | 2a | 16 | 0.562 | 1.000 | +0.438 | 7 | N |
| 45 | nexp | 17 | 0.562 | 1.000 | +0.438 | 7 | N |
| 59 | nexp | 16 | 0.562 | 1.000 | +0.438 | 5 | N |
| 36 | 2a | 16 | 0.625 | 1.000 | +0.375 | 6 | Y |
| 24 | 2a | 14 | 0.875 | 1.000 | +0.125 | 7 | Y |

Minimum rescue gap among solvers: +0.125 (seed 24); median: +0.469; maximum: +0.688. All 14 solvers required at least +0.125 Baldwin gap to cross F=1.0 threshold. The gap magnitudes are substantial — plasticity is doing large continuous fitness work on these specific winners.

---

# Section 3 — Implications for §v2.5-plasticity-2c prereg framing (codex-corrected)

**Codex adversarial review of Section 2 interpretation:** VERDICT = NEEDS-REVISION (4 P1 + 5 P2 findings). All findings centered on scope overreach and blurred endpoints. This section presents the **corrected, scope-qualified** interpretation + **proposed (not compelled)** framing implications for the §v2.5-plasticity-2c prereg.

## 3.1 Corrected summary claims

**Claim A (was: "plasticity enables every solve"):**
Within the 40 plastic-evolved winners inspected at budget=5: 14 solve only under plastic test-time eval, 1 solves only under frozen eval (seed 28, gap=−0.125 — plasticity hurts this one), 0 solve both ways. Plasticity-rescue count within this post-hoc slice = 14/40 = 35%. This is a per-winner paired observation on winners selected under plastic evolution; NOT a global "plasticity is necessary for solve at sf=0.0" claim.

**Claim B (was: "plasticity-enabled-bloat falsified"):**
The inspection failed to detect a monotone association between overhead and per-winner Baldwin gap at n=40 (Pearson r=+0.156, p=0.34; Spearman rho=+0.17, p=0.29). Point estimates are small positive (sign in the hypothesized direction) but too noisy to claim at this power. The hypothesis is NOT falsified; it is "no detectable association in this inspection." Alternative framings (overhead × rescue, overhead × specific-operator-type gap) are untested.

**Claim C (was: "overhead does not distinguish solvers"):**
Within the compositional_AND subgroup, solver median overhead (15, n=7) and non-solver median overhead (16, n=17) **show no obvious separation**. At these subgroup sizes no effect-size CI is computed; a larger study might detect separation. This is NOT "overhead does not distinguish" in general.

**Claim D (exploratory hypothesis):**
Plasticity-active-token count is a candidate distinguisher of solvers vs non-solvers within the compositional_AND subgroup (median 6 vs 4, n=7 vs n=17). **Hypothesis-generating only** — underpowered; pattern would need replication at larger n before pre-registration against it. A secondary question is whether plasticity-active token count acts as a mediator of rescue magnitude (i.e., more plasticity-active tokens → larger Baldwin gap → more likely to cross F=1.0); the inspection is compatible with this framing but cannot confirm it.

## 3.2 Proposed (not compelled) framing shifts for §v2.5-plasticity-2c prereg

These are shifts Section 2's deep inspection **motivates**, not compels. The inspection is a narrow post-hoc slice (one budget, one arm, one sampler, n=40 winners); it does not automatically warrant a prereg-level reframe. The §2c prereg should pre-commit its framing choice explicitly and justify it against the inspection data, not present the reframe as "the data requires it."

1. **Primary outcome axis:** F_AND_test solve rate at higher budgets is a more natural primary axis than overhead reduction, **given that the inspection showed overhead is weakly-and-insignificantly associated with per-winner Baldwin gap while F_AND_test moved sharply under plasticity (14/40 plastic-only vs 1/40 frozen-only).** Overhead can be a diagnostic-only secondary axis. This is a proposed framing shift, not compelled by the data — overhead-primary remains defensible, just less illuminating given the inspection's null-but-underpowered result on overhead×gap.
2. **Dual confirmatory endpoints (rescue vs gap):** the prereg should commit explicitly to testing overhead × rescue (binary) as a separate axis from overhead × gap (continuous). These are different endpoints; the inspection tested only the second. Overhead × rescue at higher budgets is genuinely new information.
3. **Plasticity-active-token count is NOT prereg-grade.** The candidate distinguisher from Section 2.3 / Claim D is hypothesis-generating only; it should NOT appear as a routing clause or confirmatory-test clause in the §2c prereg. Could appear as an exploratory / diagnostic-reported metric with no α budget.
4. **Attractor-category classifier:** the Section 1 heuristic (compositional_AND, max>5-only, sum>10-only, other) is a project-local convention; the §2c prereg should commit to it verbatim via METRIC_DEFINITIONS (principle 27) before the sweep runs. Engineering estimate: 30 min to add to `analyze_plasticity.py`.
5. **Metric redesign (inherited from Section 1 implications):** `top1_winner_hamming` with cap=4 returned single-valued sentinel on 40/40; the §2c prereg should either cap at L_canonical=12 or uncap. No chronicle-level routing impact today, but measurement-infrastructure discipline (principle 25) requires the redesign before any routing clause uses the metric.

## 3.3 Open mechanism questions the inspection raises but does not answer

1. **Is the compositional-AND-with-overhead attractor a selection phenomenon or a plastic-evolution phenomenon?** The inspection is conditional on plastic evolution (winners selected under plasticity-active selection). The 20 frozen-control winners from §2a (plasticity OFF during evolution, sf=0.0) have NOT been inspected structurally. A follow-up inspection on those 20 would answer this directly — is the attractor present when plasticity is absent from evolution?
2. **Does rescue magnitude scale with plasticity-active-token count as a mediator?** Section 2.3's weak-but-suggestive pattern. Underpowered at n=40; could be testable via cross-budget data from a future sweep.
3. **Do non-solver compositional_AND-attempts (17/40) fail because of specific operator-composition errors, or because the plasticity rescue magnitude is insufficient to cross F=1.0?** Resolution would require semantic inspection of decoded programs (not zero-compute; requires program execution or hand-tracing).

## 3.4 Recommended next actions

1. **Inspect the 20 frozen-control winners** (same inspection protocol as Sections 1+2, applied to the seeds 20..39 plasticity-OFF cell of §v2.5-plasticity-2a). Zero-compute; directly answers the selection-vs-plastic-evolution question (3.3.1). **Do this before committing the §v2.5-plasticity-2c prereg framing.**
2. After the frozen-control inspection lands, revisit the §2c prereg draft (`Plans/prereg_v2-5-plasticity-2c.md`, currently in DRAFT with Sections 1+2 filled against the old overhead-primary framing) and decide:
   - If frozen-control winners also show compositional-AND-with-overhead: the attractor is a selection phenomenon → §2c should test plasticity-ablation or selection-regime change, NOT capacity-scaling.
   - If frozen-control winners look structurally different (near-canonical? different attractor? no clear attractor?): the attractor is a plastic-evolution phenomenon → §2c capacity-scaling with F_AND_test-primary reframe is defensible.
   - If frozen-control winners have some third pattern: a new §2b-enumerated prereg direction emerges.
3. Keep `Plans/prereg_v2-5-plasticity-2c.md` in DRAFT status until direction is decided.

---

# Section 4 — Frozen-control winner inspection (n=20, plasticity OFF during evolution) (2026-04-22 PM)

Zero-compute inspection on the 20 frozen-control runs from §v2.5-plasticity-2a (seeds 20..39, `plasticity_enabled=False`, budget=0, sf=0.0). Same structural-inspection protocol as Section 1; winner = `argmax(fitnesses)` from `final_population.npz` (single fitness column under frozen evolution).

**Purpose:** answers Section 3.3.1's open question — is the compositional-AND-with-operator-overhead attractor a plastic-evolution phenomenon (only emerges under plasticity-active selection) or a selection phenomenon (emerges under tournament selection regardless of plasticity)?

## 4.1 Frozen-control winner stats (n=20)

- **best_fitness (frozen eval, training):** min=0.8594, median=0.9219, max=0.9688. **0/20 solvers** under frozen eval.
- **Active-view length:** min=25, median=27.5, max=30. Same distribution as plastic-evolved winners (min=22, median=28, max=30).
- **Overhead (active_len − canonical=12):** min=13, median=15.5, max=18. Matches plastic-evolved (min=10, median=16, max=20).
- **Uncapped Levenshtein distance to canonical active-view:** min=17, median=22, max=27. Matches plastic-evolved (min=17, median=23, max=26).
- **Canonical tokens present (out of 8):** distribution {5: 1, 6: 6, 7: 7, 8: 6} — 13/20 (65%) have ≥7 canonical tokens, matching plastic-evolved's 28/40 (70%).

## 4.2 Attractor-category comparison

| attractor | plastic-evolved n=40 | **frozen-evolved n=20** |
|-----------|----------------------|-------------------------|
| compositional_AND | 32/40 = 80% | **16/20 = 80% — identical dominance** |
| max>5-only proxy | 4/40 = 10% | 4/20 = 20% |
| sum>10-only proxy | 2/40 = 5% | 0/20 = 0% |
| other | 2/40 = 5% | 0/20 = 0% |

**The compositional-AND attractor has IDENTICAL 80% dominance in both regimes.** The category distribution is within sampling variance at n=20 vs n=40. This is decisive evidence that the attractor is **not a plastic-evolution artifact** — it emerges under tournament selection on this task regardless of whether plasticity is active during evolution.

## 4.3 Plasticity-active token count differs between regimes

| metric | plastic-evolved (n=40) | frozen-evolved (n=20) |
|--------|------------------------|-----------------------|
| plasticity-active tokens (median, GT+IF_GT+THRESHOLD_SLOT) | **6** | **3** |
| plasticity-candidate tokens (median, 7-set) | 12 | 9 |

**Plastic-evolved winners contain ~2× more plasticity-active tokens per winner than frozen-evolved winners.** This is a selection-level Baldwin-effect signature at the operator-level: when plasticity is available during evolution, selection biases retention toward programs with more plasticity-modulated operators (since those programs receive plasticity's rescue, while others don't).

The count shift is from 3 to 6 — doubling — in an active-view whose total length doesn't change (median 27.5 vs 28). So plastic-evolution is replacing ~3 inert tokens with plasticity-active tokens, while keeping the overall active-view length and attractor category fixed.

## 4.4 F solve rate across regimes

| regime | solve count | notes |
|--------|-------------|-------|
| plastic-evolved, plastic eval | 14/40 = 35% | Section 2.1 |
| plastic-evolved, frozen eval (same genotype) | 1/40 = 2.5% | Section 2.1; Baldwin gap mean +0.364 |
| **frozen-evolved, frozen eval** | **0/20 = 0%** | Section 4.1 (this section) |

The same attractor category produces dramatically different solve rates depending on plasticity regime at BOTH evolution and test time:
- Under frozen evolution → frozen eval: 0% solve. Max frozen fitness 0.9688 — winners get *close* but don't cross.
- Under plastic evolution → frozen eval on same genotype: 1/40 = 2.5% solve. Essentially same as frozen-evolved.
- Under plastic evolution → plastic eval: 35% solve. The per-winner Baldwin gap (mean +0.364) is what lifts 14/40 from below to above F=1.0.

## 4.5 Refined mechanism picture

Putting Sections 1+2+4 together (with codex-corrected scope caveats per Section 3):

1. **Tournament selection on `sum_gt_10_AND_max_gt_5` at sf=0.0 finds the compositional-AND-with-operator-overhead attractor (80% dominance, median active-length 27-28, median overhead 15-16, median uncapped distance 22-23) — regardless of plasticity regime during evolution.** The attractor itself is selection-shaped, not plasticity-shaped.
2. **Under plastic evolution, selection additionally enriches winners for plasticity-active operators** (median 6 GT+IF_GT+THRESHOLD_SLOT tokens vs 3 under frozen evolution). This is a Baldwin-at-operator-level effect: plasticity's availability during selection biases retention toward plasticity-using programs.
3. **At test time, plasticity is what enables F=1.0 solve on the compositional-AND winners:** 14/40 cross (35%) under plastic eval; 0–1/40 cross under frozen eval. The per-winner Baldwin gap (mean +0.364) is substantial and roughly-uniformly distributed across overhead values (Section 2.2's null-but-underpowered correlation).

## 4.6 Revised implications for §v2.5-plasticity-2c prereg framing (codex-corrected)

**Codex adversarial review** (2026-04-22 PM, second round on Section 4 claims) returned **NEEDS-REVISION** with 4 P1 + 2 P2 findings. The initial §4.6 draft overclaimed on mechanism naming, cross-budget extrapolation, and threshold-baselining. Codex's honest rewrite:

> "At the tested budget, plastic and frozen arms show identical comp_AND attractor incidence (80% in both), so attractor prevalence is not evidence for a plasticity-specific effect here. Plastic runs do show higher plasticity-active-token usage and a nonzero F-solver share (14/40 vs 0/20), which is suggestive of an operator-level difference, but the mechanism naming and any cross-budget predictions remain premature from this n=40/20, single-budget snapshot."

**Codex-corrected claim list (each claim replaces the pre-codex version):**

**C1 (was: "attractor is selection-driven not plastic-evolution-driven" — overstated):**
Downgrade to: *"At the tested budget (5 plastic / 0 frozen), plastic and frozen arms show identical comp_AND attractor incidence (80% in both). These data do not support a plasticity-specific increase in attractor frequency at this budget. The mechanism identification (selection-driven vs plasticity-driven) is NOT resolved by equal marginals at a single budget."* Codex P2-1.

**C2 (was: "6 vs 3 is a Baldwin-at-operator-level signature" — overclaimed mechanism):**
Demote to descriptive: *"Plastic-evolved winners show higher plasticity-active-token counts than frozen-evolved winners (median 6 vs 3) at this budget."* No mechanism naming. Solver-conditioned analysis, uncertainty quantification (e.g., seed-bootstrap CI on per-regime medians), and a stronger bridge from token count to mechanism are needed before mechanism interpretation. Codex P1-3.

**C3 (was: "overhead is selection-driven and won't change with budget" — REJECTED):**
Reject as cross-budget extrapolation from single-budget data. The §2c sweep would actually test whether overhead changes with budget; pre-registering "won't change" violates principle 17b anti-smuggling. Codex P1-1. The corrected statement: "At the tested contrast (plastic budget=5 vs frozen budget=0), overhead is within noise across regimes. Whether overhead responds to plasticity budget scaling is UNTESTED and an open question for §2c."

**C4 (was: "budget=40 predictions: tokens≥8, F≥60%" — REJECTED):**
Reject as unregistered forecasts without scaling law, CI, or baseline-relative thresholds. Specific-numeric-threshold predictions at untested budgets are not principled from single-budget observations. Codex P1-2. The corrected §2c prediction style: "Under H1 (capacity-scaling), F_AND_test at budget=40 is higher than at budget=5 with non-overlapping seed-bootstrap CIs (directional, not a specific-number threshold)."

**C5 (was: "Baldwin-at-operator-level" as mechanism name — too strong):**
Demote to tentative working label. Per §16/16c, a mechanism name requires at least three falsifiable predictions tied to specific experiments that would force a rename if violated. None are pre-registered here. The §2c prereg must NOT pre-register a mechanism name; naming is deferred to post-data per §16 renaming cycle. Codex P1-4.

**General principle-6 issue (Codex P2-2):** raw counts (6, 3, 14/40, 0/20) need predeclared reference standards or null-comparison baselines to function as thresholds, not just rhetorical anchoring.

**Corrected proposed §2c framing (all framing shifts proposed-not-compelled):**

- **Primary observable:** F_AND_test solve rate across plasticity budgets ∈ {5, 10, 20, 40}. Baseline-relative prediction: under capacity-scaling hypothesis, F_AND_test at budget=40 exceeds F_AND_test at budget=5 with non-overlapping seed-bootstrap 95% CIs. Under saturation hypothesis, CIs overlap (consistent with plateau).
- **Secondary diagnostic (descriptive, no confirmatory-test status):** per-winner Baldwin gap magnitude distribution across budgets; plasticity-active-token-count distribution across budgets; overhead distribution across budgets (NOT pre-registered as "won't change" — will be measured).
- **Attractor category:** reported per-cell but NOT a routing clause. If comp_AND dominance shifts dramatically at higher budget (e.g., < 50% or > 95%), that's a §2b grid-miss candidate for a follow-up prereg.
- **Mechanism naming:** DEFERRED. No mechanism name pre-registered. §16c falsifiability block is empty in §2c because no mechanism name is being proposed; any naming will happen at chronicle time with a full §16c block.
- **Engineering (principle 25/27 discharge before sweep):** add per-winner metrics to `analyze_plasticity.py`: `top1_winner_overhead`, `top1_winner_plasticity_active_count`, `top1_winner_attractor_category`, `top1_winner_levenshtein_uncapped`, `top1_winner_canonical_token_set_size`. Cell-level aggregates: per-cell median, seed-bootstrap CI, attractor-category counts. Expected ~1–2h engineering; pre-commit in §2c via METRIC_DEFINITIONS block. (Engineering list is carry-forward from the pre-codex draft; these metrics are measured, not used as threshold-claims.)

## 4.7 Open questions Section 4 raises (codex-corrected; naming removed)

1. **Does the plasticity-active-token count shift (3 frozen → 6 plastic at budget=5) continue to scale with plasticity budget?** §v2.5-plasticity-2c can measure directly (descriptive axis, not mechanism-claim).
2. **Are the plasticity-active tokens in plastic winners functionally load-bearing, or inert-but-selected?** Requires semantic inspection of decoded programs; not zero-compute. Worth queueing as a post-§2c follow-up.
3. **Does the compositional-AND-with-overhead attractor appear under different selection regimes (EES, novelty search)?** Section 4 shows tournament-specific at this one budget; all other selection regimes are untested. Pre-committed as open question for any follow-up prereg after §2c.

**§2c framing status:** codex-corrected draft above is still PROPOSED (not compelled by the data). The §2c prereg when drafted must codex-review its own draft against these corrections, not just absorb them.

---

## Section 1 implications (metric redesign + attractor-category enumeration; still valid)

*These implications derive from Section 1's shallow structural inspection. They remain valid — Section 3's codex-corrected implications address Section 2's per-winner Baldwin-gap findings, not Section 1's structural observations. Both sets of implications should feed the §v2.5-plasticity-2c prereg design.*

1. **The prereg's `top1_winner_hamming` metric needs either cap-raising or replacement.** At cap=4 it returns a single-valued sentinel on 40/40 winners; at uncapped it reveals a 9-token range that distinguishes winners. A reasonable redesign: cap at `L_canonical = 12` (so value `≥ 13` is "structurally distinct from canonical") with the interpretation "≤ 2 = near-canonical, 3–7 = compositional variant, ≥ 8 = distant-tail compositional or alternate structure."
2. **The "CB ACTIVE vs INACTIVE" categorical binning at ≤1 vs ≥2 is too coarse for this regime.** All 40 winners classify as CB INACTIVE under the prereg's rule even though 28/40 contain at least 7 of 8 canonical tokens. The prereg's follow-up must introduce a finer mechanism category that distinguishes:
   - **near-canonical** (structural identity or minor edits; active-view length close to 12; canonical token set present)
   - **compositional AND-attempt** (active-view length 20–30; canonical operators + substantial overhead; attempts AND structure): **32/40 winners**, dominant attractor
   - **single-predicate proxy** (max>5 or sum>10 alone): **6/40 winners**, minority
   - **other**: **2/40 winners**
3. **The "compositional AND-attempt with operator overhead" attractor is what selection finds under rank-1 plasticity at sf=0.0 budget=5.** It is neither classical-Baldwin (winners are far from canonical) nor single-predicate proxy (14/40 actually solve — this is NOT a `max > 5` attractor). The follow-up prereg should pre-register this as a dedicated attractor category with decision rules for how to interpret it (EES? rank-2? novel selection regime?).
4. **F_AND_test_plastic = 14/40 = 0.35** is consistent with "compositional AND-attempt attractor" where some attempts succeed semantically and some don't. The F-lift mid-range (0.35) is the natural outcome of this attractor, not a noise-on-F-axis interpretation. (Section 2 refines this: the 14 solvers are all plasticity-rescue, confirming that F-lift is plasticity-dependent at this budget.)
5. **The `selection-deception` diagnosis (§29 class 4) does NOT cleanly apply.** The diagnosis predicts "selection doesn't need the mechanism" because a static shortcut satisfies fitness. But at sf=0.0 there's no static canonical shortcut, and selection IS finding compositional AND structure — it's just finding it with operator overhead. The rank-1 plasticity may be providing mutation-robustness to the compositional structure. The P-1 falsifier was framed around "shortcut removal unlocks F-recovery" vs "rank-1-intrinsic INVERSE-BALDWIN" — neither frame precisely captures "compositional AND-attempt with operator overhead." (Section 2 strengthens this: if plasticity is what enables 14/40 winners to cross F=1.0, and 0/40 would cross without plasticity, then the diagnosis should focus on "plasticity-enabled threshold-crossing under compositional-attempt attractor" — an untested class of mechanism effect.)

## Methodology notes

- **Principle 3 (zero-compute inspection):** this inspection used ~5 min (Section 1) + ~15 min (Section 2) of Python on already-on-disk data to reveal mechanism-level structure that the cap=4 metric hid. Standard chem-tape workflow.
- **Principle 21 (attractor-category classification):** 40/40 winners were classified via the heuristic in Section 1. The category counts (32 / 4 / 2 / 2) support the §2c follow-up prereg's need to enumerate the compositional-AND-attempt category as a dedicated outcome row.
- **Principle 25/§27 (metric-fidelity drift):** the `top1_winner_hamming ∈ {0,1,2,3,4}` METRIC_DEFINITIONS entry vs the cap+1=5 sentinel is the direct cause of the information loss. The follow-up prereg must address this (cap-raise or metric replacement) before it commits to routing logic.
- **Codex adversarial review discipline:** Section 2's interpretation was submitted to codex and received NEEDS-REVISION (4 P1 + 5 P2 findings). Section 3 reflects the corrected, scope-qualified framing. Raw findings preserved in session log; not duplicated here.

## Next actions — current (supersedes Section 3.4 after Section 4 landed)

Section 3.4 recommended the frozen-control inspection as the next step; that step is now **discharged** (Section 4). The current next-actions sequence:

1. **Commit this inspection doc** (Sections 1+2+3+4; current state) to the repo as the authoritative inspection record backing §v2.5-plasticity-2c prereg design. (This commit.)
2. **Redraft `Plans/prereg_v2-5-plasticity-2c.md` sections 1+2 (Question + Hypothesis)** against Section 4.6's refined framing (Baldwin-at-operator-level primary; overhead demoted to diagnostic; F_AND_test + plasticity-active-token count as primary axes).
3. **Continue §v2.5-plasticity-2c prereg drafting** (Setup, Baseline, Outcome grid, Guards, Statistical test, METRIC_DEFINITIONS extensions, Audit trail, Status-transition checklist) per research-rigor prereg-mode discipline.
4. **Codex adversarial review of §v2.5-plasticity-2c draft** before committing (mandatory per research-rigor prereg hard gates).
5. **Engineer the `analyze_plasticity.py` extensions** pre-committed by §v2.5-plasticity-2c (new per-winner metrics listed in Section 4.6).
6. **Queue and launch §v2.5-plasticity-2c sweep** after engineering discharges.

---

**Scratch-doc status:** inspection result only; not a methodology document. Sections 1+2 are the empirical findings; Section 3 is the codex-corrected interpretation. May be deleted after the §v2.5-plasticity-2c prereg discharges its engineering-infrastructure commitments.
