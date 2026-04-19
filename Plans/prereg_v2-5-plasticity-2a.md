# Pre-registration: §v2.5-plasticity-2a — Arm A sf=0.0 seed-removal probe of P-1 diagnosis falsifiability (branching test for `selection-deception` vs rank-1-structural-mismatch)

**Status:** QUEUED (v6, amended) · target commit `895739c` · 2026-04-19

*This prereg follows from diagnosis `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md` (class: `selection-deception` / "deception of learning-to-learn" — Risi & Stanley 2010). Escalation path is pre-committed; scope is restricted to the path identified there. This prereg enacts P-1 from §v2.5-plasticity-1a's Falsifiability block — the cheapest branching test that distinguishes "INVERSE-BALDWIN driven by static-canonical shortcut" (selection-deception, EES next) from "INVERSE-BALDWIN is intrinsic to rank-1 plasticity on this task" (rank-2 first; diagnosis doc amended per §13).*

## Amendment history

**2026-04-19 (v6 — pre-data, pre-queue-launch).** v5 was committed at `1802146` and SHA-pinned at `b421fd8`. Codex adversarial review of v5 returned FAIL with 3 P1 + 1 P2 findings. v6 accepts all four and addresses them in this amendment (doc-only — one new analyzer field added to the Status-transition checklist, no sweep YAML or queue change; QUEUED preserved).

1. **Seed-minority denominator scaling fixed** (codex-v5 P1-a accepted). v5's `max_gap_at_budget_5_seed_minority_0_05` had a latent false-positive under partial-nan: the fixed `count < 10` cutoff with a non-nan denominator could fire rows 1/5 with 9/15 informative seeds (60%) above 0.05 — not a minority. v6 tightens the non-nan floor from 15/20 to **20/20** for ALL substantive rows (1, 2, 3, 4, 5) to fire: if any seed is nan on the confirmatory axis, the cell routes to row 7 (grid-miss) regardless of CI value. Rationale: §1a drift cell empirically had 20/20 non-nan at pop=512, so 20/20 is the expected modal behavior; partial nan is itself a novel signal worth pre-registering against, not slack for routing. This removes denominator ambiguity entirely — all count thresholds are over the nominal 20 and never scale with partial data. Updated in the v4 canonical `max_gap_at_budget_5` paragraph, the outcome grid row 7, the row-clause fidelity block, METRIC_DEFINITIONS extensions (`max_gap_at_budget_5_cell_boot_ci`, `_seed_majority`, `_seed_minority_0_05`), the statistical test block, the threshold-justification block, and the audit trail principle-25 entry.

2. **SWAMPED cap threaded through every substantive row** (codex-v5 P1-b accepted). v5 added `frozen_F_prop ≤ 0.45` to rows 1 and 2 in the outcome grid but omitted it from rows 3, 4, and 5 — row exclusivity broken because `frozen > 0.45` could satisfy a substantive row as well as row 6 (SWAMPED). v6 adds the `frozen_F_prop ≤ 0.45` clause to rows 3, 4, and 5 in the outcome grid AND restates the row-clause fidelity block so each substantive row explicitly enumerates `frozen_F_prop ≤ 0.45` as a required sub-clause. Row 6 (SWAMPED) remains the sole row firing on `frozen_F_prop > 0.45`; rows 1-5 require the cap negated. Exclusivity restored.

3. **Row-1 classical-Baldwin exclusion upgraded from unguarded cell-mean to CI-bootstrapped per-seed statistic** (codex-v5 P1-c accepted). v5 routing-critical clause was `max(Baldwin_gap_h0_mean, Baldwin_gap_h1_mean) < 0.05` — plain cell-means of two Hamming bins, no min-n occupancy guard, no uncertainty quantification. Codex: "the clause is fine conceptually; the problem is the metric has no uncertainty or occupancy guard." v6 replaces the unguarded cell-mean clause with a proper per-seed + sparse-bin + cell-bootstrap-CI statistic, parallel to the primary confirmatory axis:
   - NEW per-seed metric `classical_baldwin_gap_max`: per-seed max of `Baldwin_gap_h0_seed_mean` and `Baldwin_gap_h1_seed_mean`, with sparse-bin guard (bin excluded if fewer than 5 non-GT-bypass individuals at that Hamming distance in that seed; seed = nan if both bins excluded).
   - NEW cell-level seed-bootstrap CI `classical_baldwin_gap_max_cell_boot_ci` on the per-cell mean of per-seed `classical_baldwin_gap_max` (10 000 resamples, rng seed 42, matching `bootstrap_ci_spec`).
   - Row 1 clause becomes: `classical_baldwin_gap_max_cell_boot_ci CI_hi < 0.05` (plus the existing 20/20 non-nan requirement on the primary axis — classical-Baldwin axis inherits the same).
   - Two new METRIC_DEFINITIONS entries added verbatim; one new Status-transition checklist item 1(h) flagged UNDISCHARGED (~15 min engineering, exactly parallel to v4's `max_gap_at_budget_5` + `_cell_boot_ci` pattern).

4. **v5 softening + statistical-test propagation gaps closed** (codex-v5 P2 accepted). Three propagation gaps fixed: (i) scope tag at line 202 updated from "selection-deception supported" to "selection-deception remains viable / consistent with" (matches v5 row-1 prose softening). (ii) Primary-statistic descriptions at the Baseline-measurement prose, the Measurement-infrastructure gate block, the Statistical-test block, the Per-sweep test counting block, and the Diagnostics-to-log block updated from "CI + seed-majority / dual" (v4 state) to "CI + seed-majority-0.10 + seed-minority-0.05 + classical-Baldwin CI (four-clause)" (v6 state). (iii) Line 98 pytest-assertion reference corrected from "checklist item 2" to "checklist item 3" (tiny; accurate).

**Amendment-cycle acknowledgement.** This is the fifth amendment round on this prereg (v1 → v2 → v3 → v4 → v5 → v6), each triggered by codex adversarial review. A separate retrospective (`Plans/_v5_retrospective.md`) captures lessons from the cycle and proposes four methodology extensions (row-exclusivity invariant; metric-denominator invariance; routing-critical metric occupancy/uncertainty guards; amendment-propagation audit) to reduce churn on future preregs of comparable complexity. The retrospective is a scratch doc; methodology.md amendments require separate user approval.

v5 preserved at `1802146` (SHA-pinned at `b421fd8`); v4 at `09ceebd` (SHA-pinned at `aef841e`); v3 at `c8cf17b`; v2 at `f6ead25`; v1 at `9ff9bf8`. All six iterations preserved in git history per §13.

---

**2026-04-19 (v5 — pre-data, pre-queue-launch).** v4 was committed at `09ceebd` and SHA-pinned at `aef841e`. Codex adversarial review of v4 returned FAIL with 4 P1 + 2 P2 findings. Prior-session engineering triage classified them into 2 P1 + 2 P2 **accepted** (addressed in this v5 amendment) and 2 P1 **rejected** as design choices with reasoning recorded below. All edits are doc-only (no engineering code, no sweep YAML, no queue change; QUEUED status preserved). Summary of v5 edits:

1. **Row 6 SWAMPED plausibility window made asymmetric** (P1-a accepted). Under the §1a anchor frozen true-rate 0.15, Binomial(20, 0.15) gives P(F=0) ≈ 3.9%, P(F=1) ≈ 13.7%, P(F ≤ 1) ≈ 17.6%. The v4 symmetric window `[0.10, 0.40]` misfires row 6 on ~17% of noise-only runs on the low side (frozen F=0 or F=1 under the anchor). That is not infrastructure-bug territory. v5: row 6 fires only when `frozen_F_prop > 0.45` (F ≥ 9; P ≈ 0.002 under anchor) — asymmetric cap on the high side where the infra-bug interpretation (canonical leak or trivial task) actually applies. Low-side oddities (F ≤ 1 seeds) remain covered by the pre-existing `initial_population_canonical_count > 0` pytest invariant (Status-transition checklist item 3) plus chronicle-time manual inspection of very-low-frozen seeds. Updated in the v4 F-threshold note, outcome grid row 6, row-clause fidelity enumeration, and threshold-justification block.
2. **Row 1 h=0/1 exclusion sub-clause added** (P1-b accepted — option (a) taken). v4's `max_gap_at_budget_5` excludes h=0/1 from the per-seed max (sparse-bin guard is per-bin; h=0 and h=1 are structurally excluded from the max itself). Codex scenario: at sf=0.0, once the static canonical shortcut is removed, selection may actually reach the near-canonical basin via CLASSICAL Baldwin (closer-to-canonical benefits more → gap concentrates in h=0/h=1). v4 would then show `max_gap_at_budget_5 CI_hi < 0.05` and route to row 1 "selection-deception supported" — but the underlying mechanism is classical Baldwin, a different thing. v5 adds a row-1 sub-clause: AND `max(Baldwin_gap_h0_mean, Baldwin_gap_h1_mean) < 0.05` at the cell level. If either h=0 or h=1 cell-mean gap is ≥ 0.05, row 1 does NOT fire — route to row 7 (grid-miss); classical Baldwin was not pre-enumerated and the next prereg on this axis must enumerate it before interpreting. Pre-committed per principle 28a. The `Baldwin_gap_h0_mean` and `Baldwin_gap_h1_mean` cell-mean columns are already emitted by `analyze_plasticity.py:summarize` (lines 621-622); no new engineering for this sub-clause.
3. **`max_gap_at_budget_5_seed_minority_0_05` METRIC_DEFINITIONS entry added** (P2-a accepted — engineering follow-up flagged UNDISCHARGED). Rows 1 and 5 trigger on "fewer than 10/20 seeds with per-seed `max_gap_at_budget_5 > 0.05`"; v4 only provided the `> 0.10` seed-majority entry verbatim in METRIC_DEFINITIONS extensions, so the `> 0.05` count had no canonical definition. v5 adds the verbatim entry below (pre-committed per principle 27) and adds a new Status-transition checklist item 1(g) — analyzer currently emits `max_gap_at_budget_5_seed_majority` only; the `_seed_minority_0_05` count must land before the sweep can transition QUEUED → RUNNING. Effort: ~5 min (exactly parallel to the existing `_seed_majority` branch).
4. **Row 1 interpretive prose softened** (P2-b accepted). v4 said "selection-deception **SUPPORTED**" in the hypothesis block, outcome-grid cell, and decision-rule block. Row 1 does not establish Baldwin direction on its own (the existing caveat already notes chronicle-time per-seed Hamming analysis of top-1 winners is required), so "SUPPORTED" overclaims. v5 softens to "selection-deception **remains viable / consistent with**" in all three locations. Row-match conditions unchanged; the change is strictly prose-level.
5. **REJECTED — sparse-bin + 15/20 minimum creates structural row-7 bias** (codex P1-c). Worry was: if mass collapses to h=0/1, bins h ∈ {2, 3, ≥4} go simultaneously sparse → nan seeds → row 7 grid-miss systematically. Acknowledged but not fixed — §1a sf=0.0 drift cell empirically had 20/20 non-nan seeds at pop=512 (Baldwin_gap_h_ge4 defined for all seeds), so sparse collapse is a theoretical tail case, not a modal failure at this scale. If it fires at result time, row 7's "next prereg must enumerate observed pattern pre-data" punt is the designed escape.
6. **REJECTED — dual-conjunction hard cutoff dumps borderline true positives into row 7** (codex P1-d). Worry was: a cell with 9/20 seeds just above 0.10 and widespread 0.08-0.10 effects gets grid-missed even though it's arguably a positive signal. Acknowledged but intentional — the dual cell-CI + per-seed-count criterion is the conservatism choice; weakening it would raise false-positive rate and defeat the principle-28a pre-commitment. Row 7 is a punt (next prereg enumerates the borderline pattern), not a dead-end. The conservative bias is deliberate at this stage of the plasticity-narrow-plateau family.

v4 preserved at `09ceebd` (SHA-pinned at `aef841e`); v3 at `c8cf17b`; v2 at `f6ead25`; v1 at `9ff9bf8`. All iterations preserved in git history per §13.

---

**2026-04-19 (v4 — pre-data, pre-engineering).** Codex review of v3 flagged 1 new P1 (max_gap definitional inconsistency — per-cell vs per-seed max; no sparse-bin guard), 1 still-partial (row-1 F threshold still repackaged-absolute), and 3 P2s (row 5 defined inconsistently across sections; wrong config field name `cfg.seed_tapes_hex` → actual field is `cfg.seed_tapes` hex string; `max_gap_@5` vs `max_gap_at_budget_5` naming drift; `plasticity.csv` schema mix for frozen + plastic rows). v4 addresses all:

1. **`max_gap` definition pinned to per-seed** (NEW-P1). v3 had "per-cell max across bins" in the confirmatory-axis paragraph and "per-seed max then cell bootstrap" in the stat-test section. v4 canonical definition (one place, referenced everywhere else): `max_gap_at_budget_5` is **per-individual (actually per-seed after summarizing within-seed individuals via the existing `Baldwin_gap_h{2,3,_ge4}_mean` per-seed columns)** max across Hamming bins h ∈ {2, 3, ≥4}. The sparse-bin guard: any bin with fewer than 5 non-GT-bypass individuals in that seed is excluded from the max (emit nan for that bin, skip in max). If ALL three bins are below the threshold, per-seed `max_gap_at_budget_5 = nan` and the seed is excluded from the cell-level seed-bootstrap CI (bootstrap operates on the non-nan subset, with min 15/20 seeds required for the CI to be valid — else row 7 grid-miss fires).
2. **Row 1 F threshold reframed as genuine lift criterion** (P1-6 still-partial). v3's "plastic ≥ 0.75 AND frozen ≤ 0.25" admitted itself that those numbers are 15/20 and 5/20 repackaged. v4: row 1/2 F criterion becomes `(plastic_F_prop − frozen_F_prop) ≥ 0.40` (40-percentage-point lift; stronger than §1a drift's observed 0.20 lift). Frozen plausibility bounded to `[0.10, 0.40]` (row 6 SWAMPED fires outside). Row 3/5 F criterion stays `plastic ≤ frozen + 0.15` (already properly lift-based). Row 4 becomes `0.15 < plastic − frozen < 0.40` (intermediate lift).
3. **Row 5 definition unified** (NEW-P2). v3 had row 5 as `CI_hi < 0.05` in the grid, `CI_hi < 0.05 AND per-seed-minority < 10/20` in the stat test, and "seed-minority > 0.05" (garbled) in the threshold justification. v4: row 5 canonical = `max_gap_at_budget_5 cell-bootstrap CI_hi < 0.05 AND fewer than 10/20 seeds have per-seed max_gap > 0.05`. Reflected consistently across grid + stat test + justification.
4. **Config field name corrected** (NEW-P2). Actual code field is `cfg.seed_tapes: str` (a hex string; see `src/folding_evolution/chem_tape/config.py:121`), not `cfg.seed_tapes_hex`. v4 fixes all references.
5. **Metric name canonicalized** (NEW-P2). v3 used both `max_gap_@5` (shorthand in prose) and `max_gap_at_budget_5` (full verbatim name in METRIC_DEFINITIONS). v4: verbatim name `max_gap_at_budget_5` used everywhere.
6. **`plasticity.csv` schema handling** (NEW-P2). Codex observed that `analyze_plasticity.py:main` takes CSV header from `rows[0].keys()`, so mixing frozen-only rows (fewer columns) with plastic rows would produce malformed CSV. v4 adds to Status-transition checklist item 1(a): explicit schema normalization — frozen-only rows pad missing plastic-specific columns with empty/nan values, OR emit `plasticity.csv` + separate `plasticity_frozen_controls.csv` (choose at engineering time; document which in the checklist item). Effort bumped ~10 min.

v3 preserved at `c8cf17b`; v2 at `f6ead25`; v1 at `9ff9bf8`.

---

**2026-04-19 (v3 — pre-data, pre-engineering).** Codex review of v2 flagged 2 partially-fixed items (P1-2 residual, P1-6 residual), 1 new P1 (diagnosis-doc operationalization mismatch), and 2 new P2s (infra-scope understatement, missing verbatim METRIC_DEFINITIONS). This v3 amendment:

1. **Row 1 renamed from BALDWIN-EMERGES to F-RECOVERY-WITHOUT-INVERSE-SIGNATURE** (P1-2 residual). The row-1 trigger (F high + tail-gap absent + δ_std unrestricted) does not establish Baldwin direction (closer-to-canonical benefits more) — it establishes "plasticity recovers F without reproducing the INVERSE-BALDWIN tail-concentration signature." The label now describes what is actually measured; Baldwin-direction would require per-seed Hamming analysis of top-1 winners beyond the row-match clauses. Routing is unchanged — this outcome still supports the selection-deception diagnosis via the "shortcut removal unlocks plasticity's selection-layer contribution" signal.
2. **Row 3 clause (c) broadened to any h ∈ {2, 3, ≥4}** (NEW-P1). v2's gap-based trigger required `Baldwin_gap_h≥4 CI_lo ≥ 0.10`, which would miss an intrinsic INVERSE-BALDWIN pattern if the positive uplift concentrates in h=2 or h=3 instead. v3: clause (c) is `max(Baldwin_gap_h2, Baldwin_gap_h3, Baldwin_gap_h≥4) CI_lo ≥ 0.10` — any non-h=0,1 bin showing the seed-majority positive signal triggers. Also adds explicit note: row-3 gap clause operationalizes the diagnosis doc's slope-based INVERSE-BALDWIN definition for the sf=0.0 regime where slope is likely undefined; at result time, if Baldwin_slope IS defined, the slope sign is reported alongside the gap-based verdict for consistency.
3. **Row-3 threshold rationale corrected** (P1-6 residual). v2 claimed "CI_lo ≥ 0.10 means ≥ 10 of 20 seeds show gap > 0.10" — statistically wrong (CI_lo is on the cell mean, not on seed-majority). v3: drops the seed-majority equivalence claim; adds an explicit per-seed clause: "AND ≥ 10 of 20 seeds show max-across-bins Baldwin_gap > 0.10" as an additional sub-clause guarding the row-3 trigger. This makes the seed-majority intent explicit rather than implied.
4. **F thresholds reframed as proportion-based dual criterion** (P1-6 residual). v2's `frozen + 12` was flagged as effectively absolute 15/20 because §1a drift frozen happens to be 3/20. v3: row 1 criterion becomes `plastic best-budget F_proportion ≥ 0.75 AND frozen F_proportion ≤ 0.25`; row 3 criterion becomes `plastic best-budget F_proportion ≤ (frozen F_proportion + 0.15)`. Both are dual criteria tied to frozen, not single-number absolutes.
5. **Status-transition checklist infra scope corrected** (NEW-P2). Codex verified that `analyze_plasticity.py:analyze_run` skips frozen-only runs (returns None when no `delta_final` column); the paired R_fit merge is a genuine new code path, not a flag flip. `history.npz` does not currently contain `initial_population_canonical_count`; the gen-0 invariant check requires runner instrumentation in `run.py` or `evolve.py`, not just an assertion. v3: checklist rewritten with realistic effort estimates (~2-2.5 h total, up from ~65 min).
6. **New METRIC_DEFINITIONS block (verbatim) added** (NEW-P2). Per principle 27, the prereg must cite the exact entries that will land in `analyze_plasticity.py:METRIC_DEFINITIONS`. v3 adds a "METRIC_DEFINITIONS extensions" block with the exact wording for `Baldwin_gap_max_cell_boot_ci`, `R_fit_delta_paired_sf0`, and `initial_population_canonical_count`.

v2 is preserved in git history at commit `f6ead25`. v1 at `9ff9bf8`.

---

**2026-04-19 (v2 — pre-data, pre-engineering).** Original v1 committed at `9ff9bf8`; codex adversarial review of v1 flagged 6 P1 issues + 4 P2 issues. This v2 amendment addresses all of them pre-data (QUEUED status preserved — no sweep data exists yet, so amendments are legitimate per §13's spirit, which protects chronicles not preregs). Summary of changes from v1:

1. **Grid coverage honesty (P1-1).** v1 claimed full cross-product coverage; v2 acknowledges row 7 (grid-miss catchall) explicitly absorbs the F<5/δ_std ∈ (1.5, 2.0] and F<5/δ_std ≤ 1.5/gap ≥ 0.05 intermediate cells. §2b compliance: the grid is not truly exhaustive, and the catchall is load-bearing rather than cosmetic.
2. **Slope removed from row clauses (P1-2).** v1 was internally inconsistent — said slope "NOT load-bearing for row-matching" but rows 3 and 4 still keyed off slope. v2 removes slope from every row clause; slope is reported as descriptive diagnostic when defined. Primary confirmatory axis is `Baldwin_gap_h≥4` only. This sidesteps the sf=0.0 undefined-slope risk entirely.
3. **Confirmatory test collapsed to one statistic at one cell (P1-3).** v1's "1 confirmatory test" bookkeeping was at odds with row 3's "at ≥ 3/4 budgets" per-cell language — §22a bookkeeping slippage. v2 defines the confirmatory test as a single seed-bootstrap CI on `Baldwin_gap_h≥4` at budget=5 (the deepest-capacity cell, where §1a's strongest signatures concentrated). The three lower-budget cells are exploratory effect-size only; monotonicity-with-budget is a descriptive observation, not a confirmatory sub-test.
4. **Class-5 methodology amendment proposal removed (P1-4).** v1's row 3 decision rule pre-committed to a §29 `mechanism-mismatched` class-5 amendment. Codex called it "grid-miss in fancy clothing" and overreach. v2 removes the class-5 proposal; if row 3 fires, the consequence is a §13-style diagnosis-doc amendment (selection-deception retraction/narrowing) and a rank-2 queue entry. Any methodology amendment is deferred to a follow-up once multiple experiments show the same unclassifiable pattern.
5. **Bridging cell dropped (P1-5).** v1's sf=0.01 seeds-20..39 cell had counting-ambiguity under §22b commit-time-membership. v2 drops it entirely; replication of §1a's positive-slope signal on disjoint seeds deserves its own prereg if desired.
6. **Thresholds re-anchored (P1-6).** v1's F<5/20 was "2× drop from 10/20 midpoint" (not baseline-relative); Baldwin_gap > 0.15 was "halved §1a 0.260 point estimate" (not CI-anchored). v2 anchors F to frozen-control ("plastic best-budget F_AND_test within (frozen ± 3 seeds)") and Baldwin_gap to per-seed majority ("≥ 10 of 20 seeds > 0.10 at budget=5").
7. **§17a bundle consolidated (P2-1).** v1 enumerated 3 facets of sf axis as 3 confounds; they are 1 structural bundle. v2: "presence/absence of seeded canonical attractors in gen-0."
8. **Guard 7 moved to §23/§25 checklist (P2-2).** v1 listed "no-canonical-in-init invariant" as a principle-4 degenerate-success guard; it's an infrastructure-fidelity check. v2 relocates.
9. **Pre-allocated mechanism names removed from decision rules (P2-3).** v1 named "rank-1-plasticity-selection-deception-by-canonical-shortcut" etc. in row-1/2/3 routing without §16c falsifiability blocks. v2 defers naming to chronicle-time.
10. **Compute estimate softened (P2-4).** v1 said "~45 min wall"; v2 calls it "projected, extrapolated from pop=128×gens=100 profile."

v1 text is preserved in git history (`9ff9bf8`).

---

## Question (one sentence)

Under Arm A direct GP on `sum_gt_10_AND_max_gt_5` natural sampler with `seed_fraction=0.0` (canonical AND body removed from initial population), does rank-1 operator-threshold plasticity at `budget ∈ {1, 2, 3, 5}` reproduce §v2.5-plasticity-1a's `Baldwin_gap_h≥4` positive-monotone-in-budget pattern, or does the pattern collapse / flip when the static canonical shortcut is absent?

## Hypothesis

The `selection-deception` diagnosis (§29 class 4) predicts that removing the canonical shortcut will allow plasticity to produce selection-layer uplift that was previously masked by canonical-elite preservation. Four pre-committed readings (principle 2):

1. **F-RECOVERY-WITHOUT-INVERSE-SIGNATURE** (v3 renamed from BALDWIN-EMERGES; see v3 amendment note). `(plastic_F_prop − frozen_F_prop) ≥ 0.40` (lift criterion — 40-percentage-point F lift, stronger than §1a drift's observed 0.20 lift) AND `max_gap_at_budget_5` cell-bootstrap CI_hi < 0.05 AND fewer than 10/20 seeds have per-seed max_gap > 0.05 (tail-gap absent; INVERSE-BALDWIN signature does NOT survive shortcut removal) AND `max(Baldwin_gap_h0_mean, Baldwin_gap_h1_mean) < 0.05` (v5 — classical-Baldwin exclusion: h=0/1 cell-mean gap must also be absent; otherwise observed pattern is classical Baldwin, NOT shortcut-removal-unlocks-F-recovery, and routes to row 7 grid-miss). Selection-deception **remains viable / consistent with** shortcut-removal-unlocks-F-recovery signal (v5 softening per codex-v4 P2-b — row alone does not SUPPORT the diagnosis). Baldwin-direction NOT established by row alone — requires post-hoc per-seed Hamming analysis of top-1 winners. EES next leg.
2. **UNIVERSAL-ADAPTER.** F lift criterion same as row 1 (`(plastic − frozen) ≥ 0.40`) AND δ_std at budget=5 collapses to ≤ 1.5. Plasticity recovers canonical-equivalents via convergent δ regardless of starting genotype; selection-deception weakly supported; EES candidate for confirmation.
3. **INVERSE-BALDWIN-REPLICATES.** Frozen-anchored F criterion fails (`plastic_F_prop ≤ frozen_F_prop + 0.15`) AND δ_std at budget=5 > 2.0 AND `max_gap_at_budget_5` (per-seed max across h ∈ {2, 3, ≥4} — see v4 definition) cell-bootstrap CI_lo ≥ 0.10 AND ≥ 10/20 seeds have per-seed max_gap > 0.10. Selection-deception **REFUTED**: pattern is intrinsic to rank-1-on-this-task, not shortcut-induced. Consequence: diagnosis doc amended per §13; rank-2 memory queued ahead of EES.
4. **AMBIGUOUS / PARTIAL.** `0.15 < (plastic_F_prop − frozen_F_prop) < 0.40` OR mixed δ_std/gap signals. Decision: n-expansion on seeds 40..59 at budget=5 before routing, OR parallel rank-2 engineering while n-expansion runs.

Readings 1 and 2 support P-1; reading 3 refutes it; reading 4 forces replication before routing. Reading 3 is the pre-committed null that would falsify P-1.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_5_plasticity_2a.yaml` (to be created)
- **Arms / conditions:** Arm A only (direct GP). BP_TOPK is EXCLUDED per the §v2.5-plasticity-1a chronicle's caveat (structural R_fit ceiling → ΔR lift undetectable until a decoder-ceiling-lowering probe lands; §v2.4-proxy-5* sequel, not plasticity).
  - **Plastic cells (confirmatory source):** `arm=A, plasticity_enabled=true, plasticity_budget ∈ {1, 2, 3, 5}, seed_fraction=0.0, generations=1500, pop_size=512, mr=0.03, tournament_size=3, elite_count=2, crossover_rate=0.7, plasticity_mechanism=rank1_op_threshold, plasticity_delta=1.0, plasticity_train_fraction=0.75` × 4 budgets × 20 seeds = 80 runs. **Only budget=5 contributes a confirmatory test** — see Statistical test section. Budgets 1, 2, 3 are exploratory effect-size for monotonicity characterization.
  - **Frozen control cell (principle-23 anchor + row-3 baseline):** `arm=A, plasticity_enabled=false, seed_fraction=0.0, generations=1500, pop_size=512, mr=0.03, tournament_size=3, elite_count=2` × 20 seeds = 20 runs. Establishes sf=0.0 frozen baseline on shared seeds for (a) paired R_fit_999 delta and (b) row-3 F_AND_test anchor.
  - **Total:** 100 runs. Bridging cell from v1 dropped per P1-5.
- **Seeds:** 20..39 on all cells — **disjoint from §v2.5-plasticity-1a's seeds 0..19**, per principle 8 independent-seed-confirmation discipline.
- **Fixed params:** pop=512, gens=1500, mutation_rate=0.03, crossover_rate=0.7, tape_length=32, n_examples=64, alphabet=v2_probe, task=sum_gt_10_AND_max_gt_5, disable_early_termination=true, dump_final_population=true, backend=mlx, plasticity_mechanism=rank1_op_threshold, plasticity_delta=1.0, plasticity_train_fraction=0.75, holdout_size=256, seed_tapes=None (no canonical seeding at sf=0.0).
- **Est. compute (PROJECTED, extrapolated — NOT benchmarked at full scale).** The evaluate-loop optimization committed at `b1eab3c` measured 2.18× wall speedup on a pop=128 × gens=100 profile. Extrapolating to full scale (pop=512 × gens=1500 × budget=5) assumes the hot path scales linearly with `pop × gens × budget` while fixed GA overhead stays constant — plausible but not verified. Projected per-run wall: budget=5 ≈ 2.3 min (half of §1a's ~5 min/run pre-optimization at the same scale), budget=1 ≈ 1 min, frozen ≈ 1.5 min. Parallel at 10 workers, projected wall for 100 runs: 30-60 min. **90-min queue timeout is conservative headroom.** Actual runtime may diverge; true benchmark requires this sweep to land.
- **Related experiments:** §v2.5-plasticity-1a (primary predecessor); `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md` (the diagnosis this prereg enacts P-1 for); §v2.4-proxy-4c Arm A baseline (commit `9135345` — per-tape mutation budget reference at matched pop=1024 scale).

**Principle 17a audit (multi-variable confound disclosure — amended).** The prereg varies one axis (`plasticity_budget ∈ {1, 2, 3, 5}`) plus one structural contrast vs §1a (`seed_fraction=0.0` instead of §1a's `seed_fraction=0.01`). Derived variables on the budget axis: (a) max accumulated |δ| per tape, (b) adaptation-step count, (c) per-evaluation VM work — all three co-move with budget by design and do not represent an undisclosed confound (budget IS the capacity axis). The sf contrast against §1a is a **single structural bundle**: *presence/absence of seeded canonical attractors in generation 0*. The three facets the v1 enumeration named (initial-canonical-count, Hamming distribution, elite-slot capture) are restatements of that single bundle, not independent confounds. Principle-17b: tested integer budget values ∈ {1, 2, 3, 5}, not `≤ 5` continuous range.

**Principle 20 audit.** Sampler unchanged from §1a (natural sampler for sum_gt_10_AND_max_gt_5, 64 inputs, 48 train × 16 test at 0.75 split). Principle 20 not triggered.

**Principle 23 audit.** Frozen control at sf=0.0 must reproduce §1a frozen-Arm-A-sf=0.01 infrastructure behavior (pop=512, gens=1500, mr=0.03, per-tape mutation budget = 45), differing ONLY on the sf axis. Expected R_fit_999 at frozen sf=0.0 close to 0 (no canonical to seed; §1a drift cell showed R_fit_frozen_999 = 0.000 at pop=512 gens=1500).

**Infrastructure-fidelity check (moved from v1's principle-4 guard 7 per P2-2).** No-canonical-in-init invariant: verify via `history.npz:initial_population_canonical_count` or post-hoc gen-0 inspection that the canonical 12-token AND body does NOT appear in the initial population at sf=0.0 across all 80 plastic + 20 frozen runs. Expected 0/100; any nonzero count indicates the `seed_fraction=0.0` handling has a bug. Adjunct pytest assertion added to the Status-transition checklist (item 3 — v6 fix; v5 incorrectly said item 2).

## Baseline measurement (required)

- **Baseline quantity 1 — frozen Arm A sf=0.0 F_AND_test and R_fit_999 at pop=512 × gens=1500 × mr=0.03:** measured in-sweep by the frozen control cell on seeds 20..39. §1a drift precedent: F_AND_test_frozen_best = 3/20; R_fit_frozen_999 = 0.000. The row-3 F criterion below is tied to this frozen control via "plastic best-budget F within (frozen ± 3)" — principle 6 compliant.
- **Baseline quantity 2 — §v2.5-plasticity-1a Arm A budget=5 sf=0.01 signatures (for row-3 threshold motivation):** Baldwin_slope cell-level CI `[+0.0521, +0.0863]`; Baldwin_gap_h≥4 mean = 0.260 (max); δ_std = 2.67; F_AND_test = 20/20 (saturated under seeded canonical). The row-3 Baldwin_gap threshold is seed-majority-anchored rather than point-estimate-halved.
- **Baseline quantity 3 — §v2.5-plasticity-1a Arm A budget=5 sf=0.0 drift signatures:** Baldwin_gap_h≥4 mean = 0.284; δ_std = 2.53; F_AND_test_plastic = 7/20 vs frozen-best = 3/20. Single-budget data; this prereg adds 3 lower-budget points for budget-scaling.

**Metric definitions (principle 27).** Existing metrics cited from `experiments/chem_tape/analyze_plasticity.py:METRIC_DEFINITIONS` verbatim (same as §1a — see §1a chronicle's METRIC_DEFINITIONS block). **Eight NEW entries** (v6 — `max_gap_at_budget_5`, `max_gap_at_budget_5_cell_boot_ci`, `max_gap_at_budget_5_seed_majority`, `max_gap_at_budget_5_seed_minority_0_05`, `classical_baldwin_gap_max` (v6 NEW), `classical_baldwin_gap_max_cell_boot_ci` (v6 NEW), `R_fit_delta_paired_sf0`, `initial_population_canonical_count`) are pre-committed verbatim in the "METRIC_DEFINITIONS extensions" block below (before the Status-transition checklist). v5 had six entries and used the pre-existing `Baldwin_gap_h0_mean` / `h1_mean` cell-means directly as the row-1 classical-Baldwin exclusion; codex-v5 P1-c flagged that as an unguarded cell-mean used as a routing-critical classifier. v6 replaces the unguarded cell-mean clause with a proper per-seed + sparse-bin + cell-bootstrap-CI statistic — parallel to the primary confirmatory axis. The primary confirmatory statistic package is now **four-clause**: (i) cell-level seed-bootstrap CI on `max_gap_at_budget_5`, (ii) per-seed-majority-0.10 count, (iii) per-seed-minority-0.05 count, (iv) cell-level seed-bootstrap CI on `classical_baldwin_gap_max` — all three CI/count statistics require 20/20 non-nan seeds on their respective axes (v6 tightening from v5's 15/20); partial nan routes to row 7 grid-miss. None of the v6-NEW metrics are currently emitted by `analyze_plasticity.py`; Status-transition checklist item 1 covers the extensions (v6 adds item 1(g) for `_seed_minority_0_05`, item 1(h) for `classical_baldwin_gap_max` + its CI).

**Measurement-infrastructure gate (principle 25).** Three infrastructure facts disclosed:

- **Four-clause primary confirmatory statistic on `max_gap_at_budget_5` + classical-Baldwin exclusion (v6 expanded).** `analyze_plasticity.py` currently emits `Baldwin_gap_h_ge4_mean` per-cell (mean across seeds at h≥4 only, no CI). v6 requires: (a) per-seed metric `max_gap_at_budget_5` = per-seed max across h ∈ {2, 3, ≥4} with sparse-bin guard; (b) cell-level seed-bootstrap CI on the per-cell mean (10 000 resamples, rng seed 42, matching `bootstrap_ci_spec`) — requires 20/20 non-nan seeds (v6 tightened from v5's 15/20) or row 7 grid-miss; (c) `_seed_majority` count (seeds with per-seed max_gap > 0.10; out of nominal 20); (d) `_seed_minority_0_05` count (seeds with per-seed max_gap > 0.05; out of nominal 20). v6 additionally requires a parallel statistic on the classical-Baldwin axis: (e) per-seed `classical_baldwin_gap_max` = max of `Baldwin_gap_h0` and `Baldwin_gap_h1` per-seed bin means with the same sparse-bin guard (<5 individuals per bin → bin excluded; both bins excluded → seed nan); (f) cell-level seed-bootstrap CI on the per-cell mean of `classical_baldwin_gap_max` — same 20/20 non-nan requirement. Status-transition checklist item 1 (a-h).
- **Paired per-seed `R_fit_delta_paired_sf0` at sf=0.0 (secondary diagnostic).** Requires a cross-cell merge between plastic and frozen-control per-run CSVs on shared seeds 20..39. `analyze_plasticity.py:analyze_run` currently skips frozen-only runs entirely — this is a genuine new code path, not a flag flip. Status-transition checklist item 1(a)+(e).
- **Baldwin_slope definition at sf=0.0.** `analyze_plasticity.py:linreg_slope` returns nan when x-variance = 0 (all non-GT-bypass individuals in a single Hamming bin). §1a drift cell observed this. In v2 the Baldwin_slope is **descriptive-only**; it does NOT appear in any row clause. The undefined-slope risk is therefore not a gate on row-matching; slope is reported for reasoning-trail purposes (e.g., if the h<4 tail DOES emerge unexpectedly, slope becomes informative).

## Internal-control check (required)

- **Tightest internal contrast:** paired plastic(sf=0.0, budget=b) vs frozen(sf=0.0, no plasticity) on shared seeds 20..39 at every budget. Directly tests "does plasticity do work at sf=0.0" without the confound of the canonical shortcut.
- **Are you running it here?** Yes — the frozen control cell is in-sweep on seeds 20..39, giving paired per-seed anchors at matched pop × gens × mr.

## Pre-registered outcomes (required — principle 2 + 2b + 26)

<!--
Axes measured at per-seed resolution at budget=5 (the pre-committed confirmatory cell):
  - F_AND_test (primary; plastic discovery from noise; frozen-control-anchored)
  - δ_std (primary; mechanism-capacity-utilization axis)
  - Baldwin_gap_h≥4 (confirmatory; seed-majority anchored)

Baldwin_slope reported when defined; NEVER appears in row clauses (v2 fix per P1-2).

Honest grid-coverage acknowledgment (§2b compliance, v2 fix per P1-1): the 5 named rows do NOT
exhaustively cover the 3-axis cross-product. Row 7 (grid-miss catchall) explicitly catches
intermediate-δ_std ∈ (1.5, 2.0] states and mixed δ/gap combinations that don't fit rows 1-5.
If row 7 fires, the next prereg on this axis must enumerate the observed pattern per principle 2b.
-->

**Confirmatory axis (single statistic at single cell — v4 canonical definition):**

**`max_gap_at_budget_5` (v4 canonical definition, v6 tightened).** For each seed in the cell, compute the per-seed Baldwin_gap at each Hamming bin h ∈ {2, 3, ≥4} from the existing `Baldwin_gap_h{2,3,_ge4}` per-seed means emitted by `analyze_plasticity.py:analyze_run`. Any bin with fewer than 5 non-GT-bypass individuals in that seed is excluded from the max (sparse-bin guard — prevents noisy small-sample maxima from dominating). Per-seed `max_gap_at_budget_5` = max of the non-excluded bin means, or nan if all three bins are below threshold. The **one confirmatory test** is the cell-level seed-bootstrap 95% CI on the per-cell mean of per-seed `max_gap_at_budget_5` — 20 seeds, 10 000 resamples, rng seed 42, matching `bootstrap_ci_spec`. **v6 non-nan floor: 20/20 non-nan seeds required for rows 1, 2, 3, 4, 5 to fire (tightened from v5's 15/20 per codex-v5 P1-a). If any seed is nan, the cell routes to row 7 grid-miss regardless of CI value — partial nan is itself a novel signal worth pre-registering against, not slack for routing.** Row 3 additionally requires a per-seed-majority ≥ 10/20 of seeds showing per-seed max_gap > 0.10 (seeds counted over the nominal 20, always). Rows 1 and 5 additionally require a per-seed-minority < 10/20 of seeds showing per-seed max_gap > 0.05 (same nominal-20 denominator). **v6 classical-Baldwin exclusion (parallel statistic, row 1 only):** per-seed `classical_baldwin_gap_max` = max of `Baldwin_gap_h0` and `Baldwin_gap_h1` per-seed bin means (same sparse-bin guard: < 5 individuals in a bin excludes it; both excluded → seed nan). Cell-level seed-bootstrap CI on this statistic; row 1 fires only when `classical_baldwin_gap_max_cell_boot_ci CI_hi < 0.05` AND 20/20 non-nan on the classical-Baldwin axis (replaces v5's unguarded cell-mean-of-means clause per codex-v5 P1-c). Broadening from h≥4-only to {h=2, h=3, h≥4} (v3) handles the "positive uplift shifts to h=2/3 when initial population is random" case. Budgets 1, 2, 3 are exploratory effect-size for monotonicity characterization; their per-cell values are reported but do NOT enter the FWER family.

**v4 note (F thresholds — reframed as genuine lift criteria per P1-6 still-partial; v5 asymmetric SWAMPED cap per codex-v4 P1-a).** F criteria use `F_prop = F_AND_test / 20`. Row 1/2: `(plastic_F_prop − frozen_F_prop) ≥ 0.40` — 40-percentage-point lift, stronger than §1a drift's observed 0.20 lift. Row 3/5: `plastic_F_prop ≤ frozen_F_prop + 0.15` (strict falsifier: less lift than §1a drift's 0.20). Row 4: `0.15 < (plastic_F_prop − frozen_F_prop) < 0.40`. Row 6 SWAMPED (v5): fires only when `frozen_F_prop > 0.45` (F ≥ 9/20; P ≈ 0.002 under §1a anchor 0.15). v4's symmetric window `[0.10, 0.40]` was too tight on the low side — Binomial(20, 0.15) gives P(F ≤ 1) ≈ 17.6%, so ~17% of noise-only runs would misfire SWAMPED on frozen F=0 or F=1. Low-side plausibility is handled instead by the pre-existing `initial_population_canonical_count > 0` pytest invariant plus chronicle-time manual inspection of very-low-frozen seeds. All criteria are genuinely lift-based (plastic minus frozen), not absolute thresholds repackaged as proportions.

**v3 note (operationalization-to-diagnosis-doc mapping).** The diagnosis doc defines INVERSE-BALDWIN and Baldwin-direction in slope terms. At sf=0.0 the slope is likely undefined per principle 25. The gap-based row triggers here are the best-effort operationalization of the diagnosis's slope-based branches for the sf=0.0 regime. At result time, if `Baldwin_slope` IS defined (h<4 subpopulation unexpectedly emerges), the slope sign is reported alongside the gap-based verdict; disagreements between the two are flagged as open-mechanism signals for the chronicle.

**Outcome grid:**

| # | outcome | F lift `(plastic − frozen)` proportion | δ_std @ budget=5 | `max_gap_at_budget_5` (confirmatory axis — v4 per-seed max across h ∈ {2, 3, ≥4} with sparse-bin guard) | interpretation / routing |
|---|---------|-------------------|--------------|--------------------|--------------------------|
| 1 | **F-RECOVERY-WITHOUT-INVERSE-SIGNATURE** (v3 renamed from BALDWIN-EMERGES) | ≥ 0.40 (40-pp lift) AND frozen ≤ 0.45 (v5 asymmetric cap) | any | cell-bootstrap CI_hi < 0.05 on `max_gap_at_budget_5` AND fewer than 10/20 seeds have per-seed max_gap > 0.05 (tail-gap absent; INVERSE-BALDWIN signature does NOT survive shortcut removal) AND cell-bootstrap `classical_baldwin_gap_max_cell_boot_ci CI_hi < 0.05` (v6 — classical-Baldwin exclusion with per-seed + sparse-bin + CI; replaces v5's unguarded cell-mean-of-means per codex-v5 P1-c). ALL clauses require 20/20 non-nan seeds on both axes (v6 tightened from v5's 15/20); any nan routes to row 7. | Plasticity recovers canonical-equivalents without the static shortcut; selection-deception diagnosis **remains viable / consistent with** the shortcut-removal-unlocks-F-recovery signal (v5 softening). Baldwin-direction NOT established — per-seed Hamming analysis of top-1 winners required at chronicle time to confirm. Next leg: §v2.5-plasticity-2b (EES). Rank-2 deferred. Findings.md `plasticity-narrow-plateau` narrows. |
| 2 | **UNIVERSAL-ADAPTER** | ≥ 0.40 AND frozen ≤ 0.45 (v5 asymmetric cap) | ≤ 1.5 | any; 20/20 non-nan on primary axis required (v6) | Plastic discovery from noise via convergent δ. Selection-deception weakly supported; mechanism is "δ does the work regardless of genotype." EES candidate. Findings.md narrows. |
| 3 | **INVERSE-BALDWIN-REPLICATES** (pre-committed P-1 falsifier) | ≤ 0.15 (plasticity gives NO substantive F uplift) AND frozen ≤ 0.45 (v6 — SWAMPED cap threaded per codex-v5 P1-b) | > 2.0 | `max_gap_at_budget_5` cell-bootstrap CI_lo ≥ 0.10 AND ≥ 10/20 seeds have per-seed `max_gap > 0.10`; requires 20/20 non-nan on primary axis (v6) | Selection-deception diagnosis **REFUTED**. Pattern is intrinsic to rank-1 on this task. Consequence: (a) `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md` amended per §13 — class-4 narrowed/retracted; (b) §v2.5-plasticity-1b (rank-2 memory) queued ahead of EES; (c) findings.md `plasticity-narrow-plateau` broadens. No §29 methodology amendment pre-committed. Mechanism-name deferred. |
| 4 | **AMBIGUOUS / PARTIAL** | 0.15 < lift < 0.40 (mid-range F uplift) AND frozen ≤ 0.45 (v6 — SWAMPED cap threaded per codex-v5 P1-b) | any | any; 20/20 non-nan on primary axis required (v6) | Neither clean support nor clean refutation. Decision: n-expansion seeds 40..59 at budget=5 (~20 min wall projected); re-evaluate against rows 1-5. Do NOT queue EES or rank-2 sweeps until the expanded verdict lands. Parallel rank-2 engineering (VM implementation, 3-5 days) may START while n-expansion runs. |
| 5 | **FAIL — universal-null-at-sf=0.0** | ≤ 0.15 AND frozen ≤ 0.45 (v6 — SWAMPED cap threaded per codex-v5 P1-b) | ≤ 1.5 | cell-bootstrap CI_hi < 0.05 AND fewer than 10/20 seeds have per-seed max_gap > 0.05; 20/20 non-nan on primary axis required (v6) | Rank-1 plasticity does NO measurable work at sf=0.0 across all three axes. Both selection-deception AND rank-1-intrinsic-tail-effect are weakened. Rank-2 enters as "fill an empty mechanism bag" candidate under weaker motivation. |
| 6 | **SWAMPED** (v5 — asymmetric cap per codex-v4 P1-a) | frozen_F_prop > 0.45 (F ≥ 9/20; P ≈ 0.002 under §1a anchor 0.15). Exclusive of rows 1-5 (v6 — each substantive row requires `frozen ≤ 0.45`, so SWAMPED cannot co-fire). Low-side (F ≤ 1) is plausible under the anchor and is handled by the `initial_population_canonical_count > 0` pytest invariant + chronicle-time inspection, NOT by row 6. | any | any | Infrastructure or anchor-baseline bug on the high side (canonical leak or trivial task). Stop and inspect. |
| 7 | **INCONCLUSIVE — grid-miss catchall (§2b explicit)** | any | any | any pattern not fitting rows 1-6, OR ANY seed nan on `max_gap_at_budget_5` after sparse-bin guard (v6 — tightened from v5's < 15/20 non-nan trigger per codex-v5 P1-a), OR ANY seed nan on `classical_baldwin_gap_max` after sparse-bin guard (v6 — classical-Baldwin axis has same 20/20 floor) | §2b: grid is not exhaustive. Row 7 catches intermediate-δ_std ∈ (1.5, 2.0] states, mixed signal states, any partial-nan cell on either confirmatory axis (v6 tightened), and any other cell in the F-lift × δ_std × gap cross-product not enumerated in rows 1-5. If row 7 fires, the next prereg must enumerate the observed pattern pre-data before interpreting. |

**Row-clause fidelity (principle 28a pre-commitment — v6 row-exclusivity rewrite per codex-v5 P1-b).** Every substantive row (1-5) explicitly requires `frozen_F_prop ≤ 0.45` AND 20/20 non-nan on every confirmatory axis it uses. Row 6 (SWAMPED) fires ONLY on `frozen_F_prop > 0.45` and is therefore exclusive of rows 1-5 by construction. Row 7 (grid-miss) fires on any partial-nan seed on either confirmatory axis, OR any F-lift × δ_std × gap combination not enumerated in rows 1-5.

Per-row sub-clauses (all listed; any one failing → row 7 grid-miss, NOT a prose-only match):

- **Row 1 (F-RECOVERY-WITHOUT-INVERSE-SIGNATURE)** — five-way conjunction: (a) `(plastic_F_prop − frozen_F_prop) ≥ 0.40`; (b) `frozen_F_prop ≤ 0.45`; (c) `max_gap_at_budget_5 cell-bootstrap CI_hi < 0.05` AND `max_gap_at_budget_5_seed_minority_0_05 < 10` (fewer than 10/20 seeds with per-seed max_gap > 0.05); (d) `classical_baldwin_gap_max_cell_boot_ci CI_hi < 0.05` (v6 — upgraded from v5's unguarded cell-mean-of-means per codex-v5 P1-c; requires the classical-Baldwin bootstrap CI, not a plain max of two h-bin cell means); (e) 20/20 non-nan seeds on BOTH `max_gap_at_budget_5` AND `classical_baldwin_gap_max` (v6 — tightened from v5's 15/20 per codex-v5 P1-a).
- **Row 2 (UNIVERSAL-ADAPTER)** — four-way conjunction: (a) `(plastic_F_prop − frozen_F_prop) ≥ 0.40`; (b) `frozen_F_prop ≤ 0.45`; (c) δ_std at budget=5 ≤ 1.5; (d) 20/20 non-nan seeds on `max_gap_at_budget_5` (v6).
- **Row 3 (INVERSE-BALDWIN-REPLICATES)** — five-way conjunction: (a) `(plastic_F_prop − frozen_F_prop) ≤ 0.15`; (b) `frozen_F_prop ≤ 0.45` (v6 — SWAMPED cap threaded per codex-v5 P1-b); (c) δ_std at budget=5 > 2.0; (d) `max_gap_at_budget_5 cell-bootstrap CI_lo ≥ 0.10` AND `max_gap_at_budget_5_seed_majority ≥ 10`; (e) 20/20 non-nan seeds on `max_gap_at_budget_5` (v6).
- **Row 4 (AMBIGUOUS / PARTIAL)** — three-way conjunction: (a) `0.15 < (plastic_F_prop − frozen_F_prop) < 0.40`; (b) `frozen_F_prop ≤ 0.45` (v6 — SWAMPED cap threaded per codex-v5 P1-b); (c) 20/20 non-nan seeds on `max_gap_at_budget_5` (v6).
- **Row 5 (FAIL — universal-null-at-sf=0.0)** — five-way conjunction: (a) `(plastic_F_prop − frozen_F_prop) ≤ 0.15`; (b) `frozen_F_prop ≤ 0.45` (v6 — SWAMPED cap threaded per codex-v5 P1-b); (c) δ_std at budget=5 ≤ 1.5; (d) `max_gap_at_budget_5 cell-bootstrap CI_hi < 0.05` AND `max_gap_at_budget_5_seed_minority_0_05 < 10`; (e) 20/20 non-nan seeds on `max_gap_at_budget_5` (v6).
- **Row 6 (SWAMPED)** — one sub-clause: `frozen_F_prop > 0.45`. Exclusive of rows 1-5 by construction (each requires the cap negated).
- **Row 7 (INCONCLUSIVE — grid-miss catchall)** — fires if (a) any sub-clause in rows 1-5 fails while prose-match suggests partial fit, OR (b) ANY seed is nan on either `max_gap_at_budget_5` OR `classical_baldwin_gap_max` after sparse-bin guard (v6 strictness), OR (c) the observed pattern does not fit rows 1-6 at all.

**Threshold justifications (v4 re-anchored; v3 residuals fixed per P1-6 still-partial):**

- **F-lift ≥ 0.40 (rows 1/2).** §1a drift at sf=0.0 budget=5 showed plastic F = 7/20, frozen F = 3/20 → lift = 0.20. Row 1/2 require lift ≥ 0.40 — strictly MORE than §1a drift, consistent with "shortcut removal unlocks plasticity's selection-layer contribution" having a substantial effect. This is a genuinely lift-based criterion (plastic − frozen), not repackaged absolute thresholds.
- **F-lift ≤ 0.15 (rows 3/5).** §1a drift observed 0.20 lift. Row 3/5 require lift ≤ 0.15 — strictly LESS than §1a drift. If INVERSE-BALDWIN is truly intrinsic to rank-1 on this task, shortcut removal should not unlock MORE F uplift than §1a drift; plastic stays close to frozen.
- **Mid-range lift 0.15 < x < 0.40 (row 4).** Falls between the firm-support and firm-falsification thresholds; ambiguous signal → n-expansion before routing.
- **Frozen plausibility cap `frozen_F_prop ≤ 0.45` (row 6 SWAMPED boundary — v5 asymmetric per codex-v4 P1-a; v6 threaded into every substantive row per codex-v5 P1-b).** §1a drift frozen F = 3/20 = 0.15 is the anchor. Binomial(20, 0.15) low-side: P(F=0) ≈ 3.9%, P(F=1) ≈ 13.7%, P(F ≤ 1) ≈ 17.6% — a symmetric low-side cap like v4's 0.10 would misfire SWAMPED on ~17% of noise-only runs, which is ordinary sampling noise, not infrastructure bug. High-side: P(F ≥ 9) ≈ 0.002 under the anchor, so `frozen_F_prop > 0.45` is genuine evidence of canonical leakage or trivial-task behavior. Row 6 fires ONLY on the high-side cap. Low-side oddities (F=0 or F=1 seeds) are covered by the `initial_population_canonical_count > 0` pytest invariant + chronicle-time manual inspection (see Infrastructure-fidelity check block above); they are NOT a row-6 trigger. **v6 row-exclusivity per codex-v5 P1-b:** every substantive row (1, 2, 3, 4, 5) requires `frozen_F_prop ≤ 0.45` as an explicit sub-clause, so row 6 is strictly exclusive of rows 1-5. v5 added the cap only to rows 1 and 2; v6 threads it through rows 3, 4, 5 as well, in both the outcome grid and the row-clause fidelity block.
- **20/20 non-nan floor on every confirmatory axis (v6 tightening per codex-v5 P1-a).** v5 allowed rows 1-5 to fire with 15/20 non-nan seeds on `max_gap_at_budget_5`, with count thresholds (`_seed_majority ≥ 10`, `_seed_minority_0_05 < 10`) evaluated over the non-nan subset. Codex-v5 showed that produces a denominator-scaling bug: at 15 non-nan seeds, 9 seeds above 0.05 = 60% still fires minority (`count < 10`), even though 60% is not a minority. v6 fix: require FULL 20/20 non-nan seeds on `max_gap_at_budget_5` (primary axis) AND on `classical_baldwin_gap_max` (classical-Baldwin axis — used only by row 1) for any substantive row to fire. Partial nan on either axis routes to row 7 (grid-miss). §1a sf=0.0 drift precedent at pop=512 showed 20/20 non-nan empirically, so 20/20 is the modal expectation; partial nan is itself a novel signal worth pre-registering the next prereg against. All count thresholds are now unambiguously over the nominal-20 denominator — no scaling drift with partial data.
- **δ_std > 2.0 (row 3).** §1a observed 2.67 at sf=0.01 budget=5 and 2.53 at sf=0.0 budget=5 drift. 2.0 is the §1a minimum observed; substantial drop below 2.0 would signal different mechanism behavior, not INVERSE-BALDWIN replication.
- **δ_std ≤ 1.5 (rows 2, 5).** §1a never observed δ_std < 1.5 at budget=5; drop to ≤ 1.5 is a qualitative shift (mechanism-capacity saturating differently).
- **`max_gap_at_budget_5` CI_lo ≥ 0.10 AND ≥ 10/20 seeds per-seed max_gap > 0.10 (row 3 — v3 dual criterion preserved).** Cell-mean-CI catches "average signal is positive with sampling-variance-bounded precision"; per-seed-majority catches "signal isn't driven by a small tail of extreme seeds." Requiring BOTH sidesteps v2's statistically incorrect "CI_lo ≥ 0.10 = seed-majority" equivalence. §1a drift point estimate at h≥4 was 0.284; 0.10 is a substantive floor well below, reasonable for replication on disjoint seeds. Max-across-bins (v3 broadening) handles the h=2/h=3 shift case; sparse-bin guard (v4) prevents noisy small-sample maxima from dominating.
- **`max_gap_at_budget_5` CI_hi < 0.05 AND fewer than 10/20 seeds per-seed max_gap > 0.05 (rows 1 and 5 — v4 unified).** Symmetric upper-bound with dual criterion (cell-CI AND per-seed-minority). Plasticity produces no non-trivial tail-gap anywhere. v3 had inconsistent wording across sections; v4 uses this exact clause consistently in grid + stat test + threshold justification.

## Degenerate-success guard (principle 4 — amended per P2-2)

Six guards inherited from §v2.5-plasticity-1a (with sf=0.0-specific adjustments). The v1 "guard 7 (no-canonical-in-init invariant)" has been moved to the Infrastructure-fidelity check block above (principle 23/25), because it is an execution-fidelity check, not a degenerate-success risk.

1. **Universal-adapter artefact (row 2).** If F_AND_test ≥ frozen+12 at every budget with δ_std ≤ 1.5 at every budget, plasticity is acting as a universal canonical-recovery mechanism. Detection: compute per-seed Hamming-to-canonical of the top-1 winner at each budget; if ≥ 75% of winners are at h = 0 (exact canonical) regardless of budget, the mechanism is "plasticity-enables-random-search-to-find-canonical." Route as row 2.
2. **Train-test leakage.** Same as §1a guard 2. Suspicious near-zero `F_AND_test − F_AND_train` gap at high budget combined with high plastic discovery flags leakage.
3. **Threshold-saturation artefact (budget=5 cell, population and top-1-winner split).** Report **both** population-level and top-1-winner `|δ_final| ≥ 5` fractions at budget=5. §1a drift showed 0.738 population + 14/20 top-1 at sf=0.0 budget=5 — under this prereg if row 3 fires, expect similar (saturated mechanism-state in winners is consistent with INVERSE-BALDWIN-REPLICATES because the mechanism IS doing work in the winners; it's just not directed where selection rewards it). Report for chronicle transparency.
4. **GT-bypass artefact.** GT_bypass_fraction ≥ 0.50 at any cell → row 7.
5. **δ-convergence artefact (universal-adapter in δ-space).** If δ_std at budget=5 collapses to ≤ 0.5 across seeds, report as row 2 regardless of F_AND_test.
6. **Adaptation-budget-too-high at budget=5.** Sanity: max `|δ_final|` at budget=b = b × δ = b × 1 = b; any value strictly greater indicates an infrastructure bug.

## Statistical test (principle 22 — v3 per P1-3 + NEW-P1)

- **Primary confirmatory test (v6 four-clause, plus classical-Baldwin exclusion for row 1):** cell-level seed-bootstrap 95% CI on the per-cell mean of per-seed `max_gap_at_budget_5` (v4 canonical definition — per-seed max across h ∈ {2, 3, ≥4} with sparse-bin guard; see Pre-registered-outcomes Confirmatory axis paragraph), plus a parallel cell-level seed-bootstrap 95% CI on `classical_baldwin_gap_max` (v6 NEW — per-seed max of `Baldwin_gap_h0` and `Baldwin_gap_h1` with sparse-bin guard). 20 seeds per axis, 10 000 resamples, `numpy.random.default_rng(seed=42)`, per `bootstrap_ci_spec`. **v6: 20/20 non-nan seeds required on BOTH axes for any substantive row (1-5) to fire (tightened from v5's 15/20 per codex-v5 P1-a); partial nan routes to row 7 grid-miss regardless of CI value.** Row 3 fires when `max_gap_at_budget_5 CI_lo ≥ 0.10` AND `max_gap_at_budget_5_seed_majority ≥ 10/20`. Rows 1 and 5 fire (on their respective F-lift clauses) when `max_gap_at_budget_5 CI_hi < 0.05` AND `max_gap_at_budget_5_seed_minority_0_05 < 10/20`. Row 1 additionally fires only when `classical_baldwin_gap_max_cell_boot_ci CI_hi < 0.05` (v6 — classical-Baldwin exclusion via proper CI; replaces v5's unguarded cell-mean-of-means per codex-v5 P1-c). All count thresholds are unambiguously over the nominal-20 denominator (v6 — no scaling drift under partial data because partial data routes to row 7).
- **Secondary diagnostic (effect-size only, no FWER contribution):** per-cell `Baldwin_gap` by-Hamming-bin pattern at budgets 1, 2, 3; paired `R_fit_plastic_999 − R_fit_frozen_999` at sf=0.0 per cell; δ_std scaling with budget; per-seed Hamming distribution of top-1 winners (for row-1 Baldwin-direction post-hoc check). Used to characterize monotonicity / universal-adapter / row-distinguishing signals but NOT to gate α.
- **Classification:** **confirmatory.** Gates the diagnosis-routing decision for §1a's INVERSE-BALDWIN pattern.
- **Family:** NEW — `plasticity-inverse-baldwin-replicates`. Size 1 at this prereg; corrected α = 0.05 / 1 = 0.05. Distinct from the closed `plasticity-narrow-plateau` family (§1a tested the Baldwin-direction NULL; this tests whether the POSITIVE-gap signature replicates under shortcut removal).
- **Per-sweep test counting (principle 22a, v3; v6 clarified):** this prereg runs 4 plastic budget cells × 20 seeds = 80 plastic runs. **One** confirmatory test is gated: the budget=5 cell's four-clause statistic on `max_gap_at_budget_5` (CI + seed-majority-0.10 + seed-minority-0.05) conjoined with the classical-Baldwin-exclusion CI on `classical_baldwin_gap_max` for row 1. All four clauses (plus row 1's fifth classical-Baldwin clause) are evaluated together as a single conjunction routing to one pre-registered row; they are NOT separate family members under principle 22a. The budgets 1/2/3 cells are exploratory effect-size — they inform row routing via descriptive thresholds (e.g., monotonicity of δ_std across budgets as a universal-adapter disambiguator) but do NOT each open a family member. If a future audit counts differently, amend this block before rechronicle.

## Diagnostics to log (beyond fitness)

- Per-seed × per-cell `F_AND_train`, `F_AND_test` (best-of-run, binary), `R_fit_frozen_999`, `R_fit_plastic_999`.
- Per-individual `test_fitness_frozen`, `test_fitness_plastic`, `delta_final`, `has_gt` → `final_population.npz`.
- Per-cell `GT_bypass_fraction`, `Baldwin_gap` by Hamming bin {0, 1, 2, 3, ≥4}, `Baldwin_slope` when defined.
- Per-cell `std(delta_final)` stratified by Hamming bin — universal-adapter diagnostic.
- Per-cell seed-bootstrap 95% CI on `max_gap_at_budget_5` + `max_gap_at_budget_5_seed_majority` count (> 0.10) + `max_gap_at_budget_5_seed_minority_0_05` count (> 0.05) + cell-level seed-bootstrap 95% CI on `classical_baldwin_gap_max` — the primary confirmatory four-clause statistic at budget=5 plus row-1's classical-Baldwin exclusion (v6 expanded from v5's CI + seed-majority dual; adds seed-minority-0.05 count, replaces unguarded h=0/1 cell-mean with proper per-seed + CI).
- Per-cell paired `R_fit_plastic_999 − R_fit_frozen_999` on shared seeds — secondary diagnostic.
- Per-cell `|δ_final| ≥ 5` fraction at budget=5, split: population-level AND top-1 winner.
- Per-cell best-of-run hex for top-1 winner per seed — attractor inspection input (row-1 / row-2 / row-5 disambiguation).
- Per-seed `initial_population_canonical_count` in gen-0 — infrastructure-fidelity check.
- `Baldwin_slope` reported when defined with "nan (degenerate x-variance)" otherwise — transparent §25 disclosure.

## Scope tag (required for any summary-level claim)

**If row 1 or row 2 fires:** `plasticity-narrow-plateau` NULL narrows — "rank-1 does NOT narrow at sf=0.01, DOES narrow/recover at sf=0.0 — selection-deception remains viable / consistent with the observed pattern" (v6 softened per codex-v5 P2, matching the row-1 prose softening in the outcome grid and decision rule). Scope:
`within-task-family · n=20 per cell × 4 plastic Arm A sf=0.0 budget cells + 1 frozen sf=0.0 control · at pop=512 gens=1500 mr=0.03 tournament_size=3 elite_count=2 · sum_gt_10_AND_max_gt_5 natural sampler with 75/25 train/test split · rank1_op_threshold δ=1.0 budget ∈ {1,2,3,5} · random initial population sf=0.0` plus existing §1a scope.

**If row 3 fires:** `plasticity-narrow-plateau` NULL broadens — "pattern is shortcut-independent; rank-1-intrinsic on this task." Scope: same parameter set + the explicit selection-deception-retraction flag. No pre-commitment to a §29 taxonomy amendment; diagnosis doc amended per §13 and rank-2 queued as the empirical next step.

Explicitly NOT-broadening in any outcome: other tasks (P-3 open for cross-task); rank-2 or deeper mechanisms (untested); other selection regimes (EES/novelty-search separate legs); other δ values; other train/test splits. Principle 17b: tested integer budget values ∈ {1, 2, 3, 5}.

## Decision rule

- **Row 1 (F-RECOVERY-WITHOUT-INVERSE-SIGNATURE; v3 renamed; v5 prose softened per codex-v4 P2-b) →** narrow `plasticity-narrow-plateau` NULL in findings.md; queue §v2.5-plasticity-2b (EES) as next test of the selection-deception diagnosis (not "confirmatory leg" — row 1 leaves the diagnosis viable, not supported); rank-2 deferred. Additional chronicle-time work: per-seed Hamming analysis of top-1 winners to test whether Baldwin-direction (closer-to-canonical benefit) is established beyond row-match clauses — this is mechanism-layer follow-up, not routing-gating. Mechanism-name: deferred to the chronicle's §16-renaming cycle.
- **Row 2 (UNIVERSAL-ADAPTER) →** narrow findings.md; queue §v2.5-plasticity-2b (EES) with an axis testing whether EES preserves the convergent-δ behavior; rank-2 deferred. Mechanism-name: deferred to chronicle.
- **Row 3 (INVERSE-BALDWIN-REPLICATES; P-1 pre-committed falsifier) →** three actions: (a) amend `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md` per §13 — class-4 selection-deception reading retracted or narrowed in scope; (b) queue §v2.5-plasticity-1b (rank-2 memory) as the next escalation; (c) broaden findings.md `plasticity-narrow-plateau`. **No §29 methodology amendment pre-committed in this prereg** (P1-4 fix): if rank-2 reveals the same unclassifiable pattern, the methodology amendment is considered at THAT point based on 2+ experiments. Single-experiment taxonomy changes are not pre-committed. Mechanism-name: deferred.
- **Row 4 (AMBIGUOUS / PARTIAL) →** n-expansion seeds 40..59 at budget=5 (~20 min wall projected); re-evaluate against rows 1-5 and re-route. Do NOT queue EES or rank-2 sweeps until the expanded verdict lands. Parallel rank-2 engineering (VM implementation, 3-5 days) may START while n-expansion runs.
- **Row 5 (FAIL — universal-null-at-sf=0.0) →** queue §v2.5-plasticity-1b (rank-2) with weaker-motivation priority; EES unlikely to help. Methodology-backlog item: add a "null-across-selection-regime-AND-mechanism" case to the diagnosis doc's rejected-diagnoses tree. No §29 amendment pre-committed.
- **Row 6 (SWAMPED) →** stop and inspect. Do not chronicle until anchor check passes.
- **Row 7 (INCONCLUSIVE — grid-miss catchall) →** per principle 2b, update outcome grid BEFORE interpreting. Chronicle as INCONCLUSIVE-grid-miss with the observed pattern documented as a pre-commitment for a follow-up prereg.

## Audit trail

- **Principle 1:** plastic-vs-frozen on shared seeds at sf=0.0 is the tightest internal contrast; runs in-sweep.
- **Principle 2 + 2b:** 7 rows enumerated; row 7 explicitly acknowledged as the grid-miss catchall for intermediate δ_std ∈ (1.5, 2.0] and mixed-axis cells not covered by rows 1-5. §2b honest compliance — grid is not exhaustive by construction, catchall carries weight.
- **Principle 4:** 6 guards (universal-adapter, leakage, threshold-saturation, GT-bypass, δ-convergence, budget-saturation-sanity). Guard 7 (no-canonical-in-init) moved to infrastructure-fidelity check per P2-2.
- **Principle 6:** F_AND_test thresholds frozen-control-anchored; δ_std thresholds §1a-observed-anchored; Baldwin_gap threshold CI-anchored (seed-majority).
- **Principle 16c:** no new mechanism name pre-allocated; any renaming deferred to chronicle-time with its own falsifiability block per P2-3.
- **Principle 17a / 17b:** budget axis (one intended capacity variable, 3 co-moving derived variables); sf contrast (one structural bundle, not 3 independent confounds). Tested values discrete.
- **Principle 20:** sampler unchanged; not triggered.
- **Principle 22 + 22a + 22b:** confirmatory, 1 test at budget=5, family `plasticity-inverse-baldwin-replicates` size 1, α = 0.05. Per-sweep counting stated explicitly (not slipped to 4 tests via row-3 per-budget language).
- **Principle 23:** frozen-control-at-sf=0.0 is in-sweep anchor; pop/gens/mr byte-identical to §1a sf=0.01 frozen control except sf axis.
- **Principle 25:** primary confirmatory package (v6 four-clause on primary axis plus CI on classical-Baldwin axis): cell-level seed-bootstrap CI + per-seed-majority-0.10 count + per-seed-minority-0.05 count on `max_gap_at_budget_5`, PLUS cell-level seed-bootstrap CI on `classical_baldwin_gap_max` (v6 NEW, replacing v5's unguarded `max(Baldwin_gap_h0_mean, h1_mean)` cell-mean-of-means per codex-v5 P1-c). All confirmatory axes require 20/20 non-nan seeds for row firing (v6 tightened from v5's 15/20 per codex-v5 P1-a); partial nan routes to row 7. Secondary diagnostic: frozen-only run processing + cross-cell merge for `R_fit_delta_paired_sf0`. **Eight new METRIC_DEFINITIONS entries** pre-committed verbatim in the Metric-definitions-extensions block (v4 had 5; v5 added `_seed_minority_0_05`; v6 adds `classical_baldwin_gap_max` + `classical_baldwin_gap_max_cell_boot_ci`); Status-transition checklist item 1(a-h) covers the code. The pre-existing `Baldwin_gap_h0_mean` and `Baldwin_gap_h1_mean` cell-mean columns in `summarize` are NO LONGER used for row 1's classical-Baldwin exclusion in v6 — the plain cell-means are too weak for a routing-critical clause (no min-n, no CI, no occupancy guard).
- **Principle 26:** F_AND_test × δ_std × Baldwin_gap_h≥4 cross-product at budget=5 gridded; Baldwin_slope demoted to descriptive-only (never in row clauses) per P1-2.
- **Principle 27:** METRIC_DEFINITIONS inherited verbatim from §1a + new cell-level bootstrap CI entry added as part of infra extension.
- **Principle 28a/b/c:** row clauses are conjunctions of all sub-clauses (28a); guards cover multi-failure-mode cases with explicit bundles (28b); status-line inline qualifier discipline at chronicle time (28c).
- **Principle 29:** this prereg follows the pre-committed diagnosis doc; escalation path restricted to the doc's ladder. No §29 methodology amendment pre-committed (P1-4 fix).

## METRIC_DEFINITIONS extensions (principle 27 — verbatim; v3 per NEW-P2)

The following entries will be added verbatim to `experiments/chem_tape/analyze_plasticity.py:METRIC_DEFINITIONS` by Status-transition checklist item 1 before the sweep launches. These are the §27 pre-commitments the v3 confirmatory test depends on:

```python
"max_gap_at_budget_5": (
    "Per-seed maximum of Baldwin_gap across Hamming bins h in {2, 3, >=4} "
    "at plasticity_budget=5. Computed as max over non-excluded bin means "
    "of per-seed Baldwin_gap_h2, Baldwin_gap_h3, Baldwin_gap_h_ge4 for "
    "non-GT-bypass individuals only. Sparse-bin guard (v4): any bin with "
    "fewer than 5 non-GT-bypass individuals in the seed is excluded from "
    "the max (emits nan for that bin). If all three bins are excluded, "
    "per-seed max_gap_at_budget_5 = nan. Broader than §1a's "
    "Baldwin_gap_h_ge4 metric to handle the case where positive plastic "
    "uplift concentrates in h=2 or h=3 rather than h>=4 (expected at "
    "sf=0.0 where the Hamming-to-canonical distribution is shifted "
    "relative to sf=0.01)."
),
"max_gap_at_budget_5_cell_boot_ci": (
    "Seed-level nonparametric bootstrap 95% CI on the per-cell mean of "
    "per-seed max_gap_at_budget_5: 10 000 resamples with replacement over "
    "the 20 per-seed values via numpy.random.default_rng(seed=42); CI is "
    "the [2.5%, 97.5%] empirical quantile of the resampled means. Matches "
    "bootstrap_ci_spec. Requires 20/20 non-nan seeds (v6 tightened from "
    "v5's 15/20 per codex-v5 P1-a); if ANY seed is nan due to sparse-bin "
    "guard, the cell routes to row 7 grid-miss regardless of CI value. "
    "Partial nan is itself a novel signal the next prereg on this axis "
    "must enumerate pre-data. Distinct from the existing Baldwin_slope_ci95 "
    "columns, which bootstrap intra-population over individuals and cannot "
    "support cell-level row-match clauses."
),
"max_gap_at_budget_5_seed_majority": (
    "Count of seeds (out of the nominal 20 in the cell) with per-seed "
    "max_gap_at_budget_5 > 0.10. Because v6 requires 20/20 non-nan seeds "
    "for any substantive row to fire (see max_gap_at_budget_5_cell_boot_ci), "
    "the denominator is always unambiguously 20 when this count is "
    "evaluated for row firing — cells with any nan seed route to row 7 "
    "before this count is checked. Part of §v2.5-plasticity-2a's row-3 "
    "dual criterion: cell-bootstrap CI_lo >= 0.10 AND this count >= 10. "
    "Sidesteps v2's incorrect 'CI_lo >= 0.10 implies seed-majority-positive' "
    "equivalence claim — cell-mean CI and per-seed majority are distinct "
    "statistical statements that must both hold for the row."
),
"max_gap_at_budget_5_seed_minority_0_05": (
    "Count of seeds (out of the nominal 20 in the cell) with per-seed "
    "max_gap_at_budget_5 > 0.05. Because v6 requires 20/20 non-nan seeds "
    "for any substantive row to fire (see max_gap_at_budget_5_cell_boot_ci), "
    "the denominator is always unambiguously 20 when this count is "
    "evaluated for row firing — cells with any nan seed route to row 7 "
    "before this count is checked. Part of §v2.5-plasticity-2a's row-1 "
    "and row-5 tail-absence criterion: cell-bootstrap CI_hi < 0.05 AND "
    "this count < 10. Symmetric upper-bound counterpart to "
    "max_gap_at_budget_5_seed_majority (which gates the 0.10 positive-support "
    "floor); this entry gates the 0.05 tail-absence floor. Added in v5 "
    "per codex-v4 P2-a — v4 had the 0.10 majority entry verbatim but "
    "left the 0.05 minority count undefined. v6 denominator clarification "
    "per codex-v5 P1-a: the '< 10' cutoff was ambiguous under v5's 15/20 "
    "non-nan floor (9/15 = 60% still fired 'minority'); v6 sidesteps this "
    "by requiring full 20/20 non-nan — the count is always over 20, never "
    "over a variable non-nan subset."
),
"classical_baldwin_gap_max": (
    "Per-seed maximum of Baldwin_gap across the two classical-Baldwin "
    "Hamming bins h in {0, 1} at plasticity_budget=5 — the bins that "
    "max_gap_at_budget_5 explicitly excludes (max_gap_at_budget_5 is over "
    "h in {2, 3, >=4}). Computed as max over non-excluded bin means of "
    "per-seed Baldwin_gap_h0, Baldwin_gap_h1 for non-GT-bypass individuals "
    "only. Sparse-bin guard (parallel to max_gap_at_budget_5): any bin "
    "with fewer than 5 non-GT-bypass individuals in the seed is excluded "
    "from the max (emits nan for that bin). If both h=0 and h=1 bins are "
    "excluded, per-seed classical_baldwin_gap_max = nan. Used by §v2.5-"
    "plasticity-2a's row-1 classical-Baldwin-exclusion clause — if the "
    "cell bootstraps a positive CI_hi on this statistic, the observed "
    "gap is concentrated near the canonical basin (h=0 or h=1), which "
    "indicates CLASSICAL Baldwin (closer-to-canonical benefits more), "
    "not shortcut-removal-unlocks-F-recovery. Added in v6 per codex-v5 "
    "P1-c — replaces v5's unguarded max(Baldwin_gap_h0_mean, "
    "Baldwin_gap_h1_mean) cell-mean-of-means clause with a proper "
    "per-seed + sparse-bin + CI statistic."
),
"classical_baldwin_gap_max_cell_boot_ci": (
    "Seed-level nonparametric bootstrap 95% CI on the per-cell mean of "
    "per-seed classical_baldwin_gap_max: 10 000 resamples with replacement "
    "over the 20 per-seed values via numpy.random.default_rng(seed=42); "
    "CI is the [2.5%, 97.5%] empirical quantile of the resampled means. "
    "Matches bootstrap_ci_spec and is strictly parallel to "
    "max_gap_at_budget_5_cell_boot_ci (same resampling convention, same "
    "rng seed). Requires 20/20 non-nan seeds on the classical-Baldwin "
    "axis; if ANY seed is nan due to sparse-bin guard, the cell routes "
    "to row 7 grid-miss regardless of CI value. Used by §v2.5-plasticity-"
    "2a's row-1 classical-Baldwin-exclusion clause: row 1 fires only "
    "when CI_hi < 0.05 on this statistic (classical-Baldwin tail is "
    "absent on h=0/h=1 at the cell level). Added in v6 per codex-v5 P1-c."
),
"R_fit_delta_paired_sf0": (
    "Per-seed paired difference R_fit_plastic_999 - R_fit_frozen_999 at "
    "sf=0.0, where R_fit_frozen_999 is taken from the frozen control cell "
    "at the matching seed in the same sweep (NOT from the plastic run's "
    "own final_population frozen evaluation, which would compare plastic "
    "and frozen evaluation on the same evolved population rather than "
    "comparing the plastic cell's final population to the frozen control's "
    "final population). Requires cross-cell merge between the plastic "
    "cells and the frozen control cell on shared seeds 20..39. Used as "
    "§v2.5-plasticity-2a's secondary diagnostic."
),
"initial_population_canonical_count": (
    "Count of individuals in the generation-0 population whose tape "
    "byte-for-byte matches the canonical tape(s) parsed from "
    "cfg.seed_tapes (a hex string; see src/folding_evolution/chem_tape/"
    "config.py:121 — field is 'seed_tapes', NOT 'seed_tapes_hex'). "
    "Parsed via _parse_seed_tapes in evolve.py. Emitted per-run to "
    "history.npz as a scalar at generation-0 population build time. "
    "At sf=0.0 with cfg.seed_tapes == '' (empty string default), the "
    "expected value is 0 for every seed; any nonzero count flags an "
    "infrastructure bug in build_initial_population."
),
```

## Status-transition checklist (QUEUED → RUNNING — v3 per NEW-P2 infra-scope correction)

Before this prereg can move from QUEUED to RUNNING:

1. **`analyze_plasticity.py` extensions (~120 min total; v3 under-counted CSV schema normalization per codex-v3; v5 added ~5 min for 1(g); v6 adds ~15 min for 1(h) classical_baldwin_gap_max + CI per codex-v5 P1-c):**
   - (a) Modify `analyze_run` to ALSO process frozen-only runs (currently returns None when `delta_final` column is missing from `final_population.npz`). Frozen runs have `genotypes` + `fitnesses` arrays only; emit `R_fit_frozen_999` plus the config/seed identifiers needed for cross-cell merge. Schema normalization: frozen-only rows must pad missing plastic-specific columns with empty/nan so `plasticity.csv` header (taken from `rows[0].keys()` at `analyze_plasticity.py:409`) covers both schemas — OR emit a separate `plasticity_frozen_controls.csv`. Pick at engineering time; document choice in the commit message. ~30 min.
   - (b) Add `max_gap_at_budget_5` per-seed computation in `analyze_run`: per-seed max across existing `Baldwin_gap_h{2,3,_ge4}` keys with sparse-bin guard (bin excluded if fewer than 5 non-GT-bypass individuals at that Hamming distance in that seed). Reported per-run via `plasticity.csv`. ~15 min.
   - (c) Add cell-level seed-bootstrap CI on `max_gap_at_budget_5` in `summarize` (10 000 resamples, rng seed 42). Requires ≥ 15/20 non-nan seeds; returns nan CI otherwise. ~15 min.
   - (d) Add `max_gap_at_budget_5_seed_majority` count in `summarize` (count of seeds with per-seed max_gap > 0.10, excluding nan). ~5 min.
   - (e) Add cross-cell merge for `R_fit_delta_paired_sf0`: join plastic-cell per-seed `R_fit_plastic_999` with frozen-control per-seed `R_fit_frozen_999` on (arm, seed) and emit the paired delta per-cell. Current `analyze_run` emits per-run `R_fit_delta_999` within the same run's population — this is a NEW code path. ~30 min.
   - (f) Add the 8 METRIC_DEFINITIONS entries verbatim from the block above (v4: 5 entries; v5: +1 `_seed_minority_0_05`; v6: +2 `classical_baldwin_gap_max` and `classical_baldwin_gap_max_cell_boot_ci`). ~5 min.
   - (g) **NEW in v5 — UNDISCHARGED at v5 commit time.** Add `max_gap_at_budget_5_seed_minority_0_05` count in `summarize` (count of seeds with per-seed max_gap > 0.05, excluding nan). v6 note: because v6 requires 20/20 non-nan for any substantive row to fire, the denominator is always 20 when this count is used for routing; the "excluding nan" mechanics are only for the numerator (if any seed is nan, row 7 grid-miss fires before this count is checked). Rows 1 and 5 trigger on this count < 10. Exactly parallel to (d)'s existing majority branch — same pattern, different threshold. ~5 min. Must land before QUEUED → RUNNING transition.
   - (h) **NEW in v6 — UNDISCHARGED at v6 commit time.** Add per-seed `classical_baldwin_gap_max` computation in `analyze_run`: per-seed max over existing `Baldwin_gap_h0`, `Baldwin_gap_h1` with sparse-bin guard (bin excluded if fewer than 5 non-GT-bypass individuals at h=0 or h=1 in that seed). Reported per-run via `plasticity.csv`. Then in `summarize`: cell-level seed-bootstrap CI on per-cell mean of `classical_baldwin_gap_max` (10 000 resamples, rng seed 42, matching `bootstrap_ci_spec`); requires 20/20 non-nan seeds, returns nan CI otherwise. Exactly parallel to the existing `max_gap_at_budget_5` + `_cell_boot_ci` pattern from (b) and (c) — same sparse-bin guard, same bootstrap spec, different bin set {h=0, h=1}. ~15 min. Must land before QUEUED → RUNNING transition.
2. **`run.py` / `evolve.py` instrumentation (~20 min):** add `initial_population_canonical_count` to `history.npz` as a scalar computed in `build_initial_population` (parse `cfg.seed_tapes` via `_parse_seed_tapes` if non-empty, compare each gen-0 tape byte-for-byte; emit 0 when `cfg.seed_tapes == ""`). NEW — `history.npz` does not currently track this field; grep-verified at codex-v2 review time.
3. **Pytest assertion (~20 min):** `cfg.seed_tapes == "" AND cfg.seed_fraction == 0.0 → initial_population_canonical_count == 0` in `tests/test_chem_tape_seeded_init.py` (extend existing sf-related tests).
4. **Sweep YAML:** `experiments/chem_tape/sweeps/v2/v2_5_plasticity_2a.yaml` — 4 plastic cells × 20 seeds (seeds 20..39) + 1 frozen control × 20 seeds = 100 runs. Paired-seed structure required for the secondary R_fit diagnostic.
5. **Queue entry:** add to `queue.yaml` with 90-min timeout (conservative headroom over projected 30-60 min).
6. **Pin target commit SHA** in Status line above.
7. **Codex adversarial review of v6** — focused on: (a) whether the 20/20 non-nan floor (v6 tightening from v5's 15/20) correctly discharges the denominator-scaling bug codex-v5 P1-a flagged, and whether routing all partial-nan cases to row 7 is appropriate conservatism or is too aggressive; (b) whether the `frozen_F_prop ≤ 0.45` cap is now cleanly threaded through every substantive row's firing condition (outcome grid + row-clause fidelity block) and row exclusivity holds; (c) whether `classical_baldwin_gap_max` + its CI is an honest parallel to `max_gap_at_budget_5` — same sparse-bin guard, same bootstrap spec, same 20/20 floor; whether the classical-Baldwin-exclusion clause via CI_hi < 0.05 on that axis is now robust enough for a routing-critical clause (replaces v5's unguarded cell-mean-of-means); (d) whether the v5 softening propagation gaps (lines 98, 106, 110, 181, 185, 193, 202, 230) are all resolved and no NEW inconsistencies introduced; (e) whether the four-way conjunction on the primary axis (CI + seed-majority + seed-minority + classical-Baldwin CI for row 1) inflates the effective FWER beyond the single-test α = 0.05 (note: all clauses evaluate one cell's data for one pre-registered row, so under principle 22a they are one confirmatory test, not four). v4 returned FAIL with 4 P1 + 2 P2 findings; v5 returned FAIL with 3 P1 + 1 P2 findings; v6 must pass before sweep launch.

**Total engineering effort:** ≈ 2.75-3.25 h (v3's estimate was ~2-2.5 h; v4 added CSV schema normalization per codex-v3; v5 added ~5 min for the seed-minority-0.05 count per codex-v4 P2-a; v6 adds ~15 min for classical_baldwin_gap_max + CI per codex-v5 P1-c). Cumulative amendment cost is documented in `Plans/_v5_retrospective.md` with proposed methodology mitigations.

## References

- `Plans/prereg_v2-5-plasticity-1a.md` — primary predecessor prereg.
- `docs/chem-tape/experiments-v2.md#v2.5-plasticity-1a` — INVERSE-BALDWIN chronicle (grid-miss verdict, §29 class-4 diagnosis).
- `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md` — diagnosis doc this prereg enacts P-1 for.
- `docs/methodology.md` — §§1, 2, 2b, 4, 6, 16c, 17a, 17b, 20, 22, 22a, 22b, 23, 25, 26, 27, 28a/b/c, 29.
- `experiments/chem_tape/analyze_plasticity.py` — METRIC_DEFINITIONS source.
- `docs/chem-tape/runtime-plasticity-direction.md` — direction doc (rank-1 → rank-2 ladder).
- Risi, S. & Stanley, K. O. (2010). "Evolving Plastic Neural Networks with Novelty Search." *Adaptive Behavior* 18(6), 470-491 — literature anchor for class-4 `selection-deception`.
- Prior commits: `9ff9bf8` — v1; `f6ead25` — v2 amendment; `c8cf17b` — v3 amendment; `09ceebd` — v4 amendment (SHA-pinned at `aef841e`); `1802146` — v5 amendment (SHA-pinned at `b421fd8`); all superseded by this v6; reasoning trail preserved in git history per §13 spirit.
- `Plans/_v5_retrospective.md` — scratch retrospective on the v1 → v6 amendment cycle and four proposed methodology extensions (row-exclusivity invariant; metric-denominator invariance; routing-critical metric occupancy/uncertainty guards; amendment-propagation audit). Scratch doc; methodology.md amendments require separate user approval.
