# Retrospective: §v2.5-plasticity-2a v1 → v6 amendment cycle

Scratch doc — not a methodology doc. Paired with `Plans/_v5_amendment_session_prompt.md`. Delete once lessons are folded into `docs/methodology.md` (or explicitly rejected). Written 2026-04-19 alongside the v6 amendment commit.

## Summary

Five codex adversarial-review rounds before data collection. Rough per-round finding counts:

| Round | P1 | P2 | Dominant failure class |
|---|---|---|---|
| v1 → v2 | 6 | 4 | Overclaim + undisclosed confounds + absolute-vs-relative thresholds |
| v2 → v3 | 1 new + 1 partial | 3 | Operationalization-to-diagnosis mismatch; missing verbatim METRIC_DEFINITIONS; CSV schema unchecked |
| v3 → v4 | 1 new + 1 partial | 3 | Metric definition per-cell vs per-seed drift; sparse-bin guard missing; config field name wrong; row 5 inconsistent across sections |
| v4 → v5 | 4 | 2 | Symmetric plausibility window too tight for n=20; h=0/1 blindness; missing verbatim `_seed_minority_0_05`; "supported" overclaim |
| v5 → v6 | 3 | 1 | Denominator scaling under partial nan; SWAMPED cap not threaded through all rows; unguarded cell-mean-as-routing-classifier; soften-prose propagation gaps |

Total: **15 P1 + 13 P2 codex findings** resolved before the first row of data was collected. The prereg file grew from ~200 lines (v1) to ~420 lines (v6). Every amendment was pre-data, pre-queue-launch.

## What the codex findings had in common

Not one finding was a new experimental-design insight — all were **consistency or rigor failures** in a prereg that had already passed the author's mental model:

1. **Between-section consistency drift.** Outcome grid says X; row-clause fidelity block says X'; threshold justification says X''. Every amendment cycle produced new drift because edits landed in one location but not all.
2. **Denominator / scaling ambiguity.** Absolute thresholds (`F ≥ 15`) repackaged as proportions (`F_prop ≥ 0.75`) repackaged as differences (`(plastic − frozen) ≥ 0.40`). Each rewrite fixed one drift but introduced another — the fix-and-regress pattern.
3. **Row-exclusivity assumed, not enforced.** SWAMPED cap was added to row 6 but never audited against rows 1-5. Codex-v5 caught the overlap; codex-v1 through -v4 all missed it.
4. **Routing-critical metrics with no occupancy / uncertainty guard.** v5's `max(Baldwin_gap_h0_mean, h1_mean) < 0.05` is a plain cell-mean of two bins, used as a routing gate. No min-n, no CI. Easy to write, easy to let slide — and easy for codex to catch once the metric is flagged as routing-critical.
5. **Soften-prose-in-three-places propagation gaps.** v5 softened "SUPPORTED" in the outcome grid, hypothesis block, and decision rule — but missed the scope-tag block at line 202 and the primary-statistic prose at lines 110, 185, 193. Each amendment introduces N new locations that need updating, and N is usually > the number the author remembers.
6. **Verbatim METRIC_DEFINITIONS entries lagging behind row clauses.** Principle 27 requires verbatim pre-commitments. Each row-clause refinement needs a corresponding METRIC_DEFINITIONS update; that coupling was consistently under-specified.

## What the codex findings did NOT include

- Wrong experimental design (arm choice, seed block, sampler, compute budget) — settled in v1.
- Wrong diagnosis class (selection-deception vs mechanism-weak) — settled before v1 via `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md`.
- Wrong falsifier identification (P-1 as the branching test) — settled pre-v1.
- Wrong thresholds in the sense of "the number is miscalibrated for the signal we're looking for." Most threshold issues were anchoring-choice or framing, not the value.

The experimental frame was right from v1. The codex rounds polished it — without changing design — from ~70% compliance with methodology principles to ~99% compliance. That polish had non-trivial cost.

## Why so many amendment rounds?

A few hypotheses, ranked by my guess at contribution:

1. **Prereg complexity scales super-linearly with row count.** 7-row grid × 3-4 sub-clauses per row × 3+ mirror locations (grid, fidelity block, threshold block, decision rule, METRIC_DEFINITIONS, audit trail, scope tag, diagnostics, statistical test) = 60-100 independent invariants that must stay coherent. Each amendment perturbs ~10 of those and leaks inconsistencies into ~3 others.
2. **Codex is an adversarial reviewer that catches things I don't, and the author is the author.** The feedback loop is designed for iteration. Multiple rounds is the feature, not a bug — but the round-count would drop if the author's initial draft caught more of the predictable issues.
3. **Methodology.md doesn't enumerate the "propagation audit" as a gate.** Principle 28a says row clauses must be conjunctions; it doesn't say "changes to row clauses must propagate to every section that restates them." So the author can be 28a-compliant on v5 and still break 28a-spirit on the row-clause fidelity block.
4. **High-stakes prereg earns higher scrutiny.** This prereg gates a diagnosis-doc falsifier under principle 29. A lower-stakes prereg would not have attracted 5 rounds of review. The amendment count correlates with stakes, not defect.
5. **The first draft was ambitious about grid coverage.** 7 rows is a lot. A 3-row prereg would have 1/3 the between-section invariants to maintain.

Hypothesis (1) is the dominant contributor. (3) is the actionable one.

## Proposed methodology extensions

Four principles, all aimed at the between-section-consistency failure class. None changes experimental rigor — they add audits that a computer could run. I'm proposing them here for your review, not applying to `docs/methodology.md` — that requires your explicit approval.

### Principle 28d (new — row-exclusivity invariant)

For any pre-registered outcome grid, enumerate pairs of rows explicitly and verify that no observed data can satisfy both rows' firing conditions simultaneously. Exclusivity is a property that must be asserted, not assumed. When a cap / guard / bound fires one row (e.g., SWAMPED on `frozen > 0.45`), every other row's firing condition must require the cap negated, explicitly in the row clause.

**Rationale.** Without an exclusivity audit, asymmetric bounds added to guard rows silently leak — as happened in v5's `frozen_F_prop > 0.45` SWAMPED cap vs rows 3/4/5. The audit is mechanical: for each pair (i, j) in rows 1-N, write the conjunction of row-i clauses AND row-j clauses and check satisfiability. Any satisfiable pair is a bug.

**Case.** §v2.5-plasticity-2a v5 — SWAMPED cap added to rows 1 and 2 but not rows 3, 4, 5. Codex-v5 caught the overlap; v6 added the cap to all five substantive rows + added an explicit exclusivity audit to the row-clause fidelity block.

### Principle 28e (new — metric-denominator invariance)

When a pre-registered threshold is expressed as a count (e.g., "≥ 10/20 seeds," "< 10 seeds"), the prereg must state explicitly how the threshold adapts under partial-data cells (nan seeds, sparse bins, dropped runs). Three valid treatments:

- **(a) Fractional threshold scaling with non-nan denominator** — e.g., `count / non_nan < 0.5`. Semantics preserved under partial data.
- **(b) Strict count-over-nominal-N** — nan seeds count toward the denominator as "no signal." Conservative direction depends on which side of the threshold nan sits on.
- **(c) Full-nominal-N requirement** — any nan routes to grid-miss; the count is always over N.

Silent count-over-non-nan (fixed cutoff, variable denominator) fails this gate — threshold semantics drift with partial data in a way the author usually hasn't reasoned through.

**Rationale.** Fixed `count < K` on a variable non-nan denominator has inconsistent semantics: at denominator N, `K/N` is the fractional threshold; at denominator N' < N, the fractional threshold becomes `K/N' > K/N`, so the count fires on more-populated cells. For minority-count thresholds, this is a silent false-positive pipeline.

**Case.** §v2.5-plasticity-2a v5 — `max_gap_at_budget_5_seed_minority_0_05 < 10` on non-nan denominator fires at 9/15 = 60% above 0.05, which is not a minority. v6 took treatment (c): require 20/20 non-nan for row firing, routing partial nan to row 7. Treatment (a) would have worked too; (c) was chosen for simplicity + alignment with §1a precedent.

### Principle 25b (extension — routing-critical metric occupancy/uncertainty guards)

When a pre-registered row clause is **routing-critical** (its satisfaction gates a specific escalation path and differentiates verdicts with material consequences for downstream experiments), the metric backing that clause must have one of:

- **(a) A minimum-N occupancy guard** — stating explicitly how many per-seed observations, or how many cells, are required for the clause to evaluate.
- **(b) Uncertainty quantification** — CI, bootstrap, equivalent. The threshold is stated against the CI bound, not the point estimate.
- **(c) An explicit "advisory-only, confirmed at chronicle-time" label** — the clause is diagnostic not routing; routing deferred to chronicle-time per-seed inspection with its own pre-committed discipline.

Plain-mean-as-classifier for routing-critical clauses fails this gate. Occupancy-uncertainty concerns are not secondary — they're first-class when the metric steers an escalation ladder.

**Rationale.** v5's `max(Baldwin_gap_h0_mean, h1_mean) < 0.05` is a plain cell-mean of two bins, used as routing gate between "selection-deception viable" (EES next) and "classical-Baldwin grid-miss" (new prereg). No min-n, no CI. Codex-v5 was exactly right: the threshold is defensible; the metric is too weak.

**Case.** §v2.5-plasticity-2a v5 → v6 — replaced the unguarded cell-mean clause with `classical_baldwin_gap_max` + its cell-level seed-bootstrap CI. Parallel to the primary confirmatory axis. ~15 min extra engineering for a routing gate previously inferred from point estimates alone.

### Principle 27b (extension — amendment propagation audit)

When a pre-registered prereg is amended (v_n → v_{n+1}), the amendment commit must include a **propagation audit** enumerating every location where each changed element appears and confirming the change landed everywhere. The audit covers at minimum:

- Outcome grid (per-row rows + columns)
- Row-clause fidelity block (principle 28a enumeration)
- Statistical test block (primary confirmatory statistic description)
- METRIC_DEFINITIONS extensions block (verbatim entries)
- Status-transition checklist (engineering effort, discharged/undischarged flags)
- Decision rule per row
- Threshold justifications block
- Baseline measurement block (when thresholds change)
- Audit trail principle-N entries (when principles are re-invoked or re-scoped)
- Scope tag (when interpretation-language changes)
- Diagnostics to log (when metric sets change)

Silent non-propagation to any location fails this gate. The audit is a recurring discipline — every amendment round, not just the first one.

**Rationale.** v5 softened "SUPPORTED" → "remains viable" in 3 locations but missed 4 others (lines 110, 185, 193, 202). v4 and v3 had similar propagation gaps. Each amendment introduces ~10-15 locations that need synchronized update, and the author reliably misses 3-5 of them — codex catches them, and another amendment round fires.

**Case.** §v2.5-plasticity-2a v1 → v6 — every amendment cycle produced propagation gaps catalogued by codex; explicit propagation audit would have reduced gap count by ~60% on inspection of the v5 codex report.

## Meta-observation

The four proposed extensions are all **mechanical** — a script over the prereg file could enforce them. The most expensive audit (28d row-exclusivity) is at worst O(N²) over row count and trivially automatable as an SMT query on the row clauses. A prereg-linter tool could run all four checks on every commit.

That tool does not exist. Building it is a ~4-8 hour project. If the amendment cycle's expected cost on high-stakes preregs is ~3-5 rounds × ~1-2 hours of author time each, the linter pays for itself after one high-stakes prereg.

Whether to build it, fold the principles into `methodology.md`, or neither, is your call — this doc flags the option, not the decision.

## Deliverables from this retrospective

- This doc (`Plans/_v5_retrospective.md`).
- `Plans/prereg_v2-5-plasticity-2a.md` v6 amendment (addresses all codex-v5 findings).
- Nothing added to `docs/methodology.md` (the four principle proposals require explicit user approval).
- No engineering code changed.
- No sweep YAML or queue change.

## Open question for the user

Do you want me to:
- **(A)** Submit a separate PR amending `docs/methodology.md` with principles 28d, 28e, 25b, 27b as described above?
- **(B)** Leave the retrospective as a scratch doc, don't touch methodology.md, and revisit after this prereg's sweep runs (so the principles have more case-evidence behind them)?
- **(C)** Build the prereg-linter tool described in the meta-observation section as a follow-up project?

Defaulting to (B) — the principles are novel, one-case precedents, and methodology.md has a high bar. This doc + the v6 commit preserve the reasoning trail for later.
