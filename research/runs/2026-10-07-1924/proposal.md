---
node: questions/10-compositional-map-transfer/21-iterated-solver-corpus
title: One feedback refit of the solver-corpus decoder (C2 from solvers found under C) against its parent and a fresh one-shot G4 refit, with holdout transfer
---

## Why this now

I follow [strategy 1924](strategy.md) and its [concept plan](../../plans/iterated-solver-corpus.md).
Run 1707 fitted a previous-token table C to exact solver tapes from G4 searches. On training cells
C beat a token-only fit to the same tapes 1.37× [1.29, 1.45], and on the withheld cells 1.29×
[1.21, 1.38]. Those tables were never used to collect solvers. This run asks whether one feedback
step helps further. Each C collects new exact training solvers, which are refitted with the
unchanged rule to give C2. A further transferable gain would be the first evidence that the map can
keep adapting from its own discoveries, through an external fit with no selection on search cost.
A null or a loss bounds this one step. It does not bound iterative learning in general.

I opened sub-question [21](../../questions/10-compositional-map-transfer/21-iterated-solver-corpus/question.md)
under root 10, using the slot the strategist added (root 10 budget 13 → 14). 20 stays closed.
Root 10 will have no slots left after this run. Any second step returns to strategy.

## Steward probe (already run, read-only, about 4 min)

[`steward_probe.py`](steward_probe.py) ran in a scratch worktree of `research/main` (`627336d`,
Rust built), using its `search(return_solver=True)`, `transition_counts` and `fit`. For four of the
1707 lineages it collected 48 searches per own training cell under the saved C (seeds 19 240 000+).
It refitted C2 with the frozen rule. Then C2 and C each ran 16 fresh seeds per cell (19 340 000+),
with seeds shared between them.

| lineage | yield under C | worker-s | C mean log2 | C2 mean log2 | C2 − C (se) |
|---|---|---|---|---|---|
| BE1 | 190/192 | 130 | 12.10 | 11.76 | −0.34 (0.29) |
| BE2 | 190/192 | 152 | 12.17 | 11.34 | −0.83 (0.27) |
| PA1 | 288/288 | 120 | 12.64 | 12.35 | −0.29 (0.27) |
| PA2 | 288/288 | 158 | 12.54 | 12.11 | −0.43 (0.21) |

- Yield under C is near full: every cell gave at least 46/48 (G4 in 1707: at least 40/48). Tapes
  are diverse: 190 distinct per BE corpus and 288 per PA corpus.
- Collection under C cost about 0.5–0.8 worker-s per search, against 2.08 for G4.
- C2's body rows are a little sharper than C's (mean entropy 3.78–3.81 bits against 3.91; G4
  4.19). Amplification is a live risk, but it did not show here.
- C2 was ahead of C in 4/4 lineages. Pooled with equal family weight this is about −0.47 log2
  (1.39×). With four lineages and 16 seeds this is a calibration, not evidence. Nothing in the
  design is tuned from it. The run collects new corpora on new seeds, including for these four
  lineages.

## What would be run

**Code.** Extend `research/main` (`627336d`): `solver_corpus_run.py`, `solver_corpus_fit.py`
(`transition_counts`, `fit`, `validate_table`, `seed_for`), `composition_search.search(...,
return_solver=True)`, and the frozen bank, split and holdout-leakage checks. The 32 saved 1707 C
tables are in `experiments/output/2026-10-07/2026-10-07-1707-solver-corpus-context/corpora.json`
(git-ignored). Copy the tables into a committed data folder with sha256 provenance.

**Validation, before stage A:**
- Replay 1707's 20 GG rows bit-identically.
- Each loaded C must hash to the `table_hash` of that corpus's 1707 C rows.
- Every saved solver tape must re-verify exact on all 1 331 inputs.
- Every fitted table must pass `validate_table`.
- Arms must share seeds and case indices within each lineage × cell. Collection and evaluation
  seeds come from `seed_for` with new phase indices 10–16, disjoint from 1707 (phases 0–5) and from
  the probe's blocks.

**Lineages.** The 32 saved 1707 tables (BE1–16, PA1–16). Every lineage is kept; none is selected
by its reported speed.

**Frozen fitting rule.** Fit only to the new tapes, with the 1707 rule unchanged: full 32-token
tapes, transition counts, each cell rescaled to 1 600 transitions, C = (n + 50·G4 row) / (N + 50)
via `fit`. The shrinkage stays toward G4, not toward C, and the first-round corpus is not pooled
in. The per-cell rescaling also means total data weight does not depend on yield. `fit` also
returns T and K for the new corpora. Save them, but do not evaluate them.

**Arms per lineage.**
- **C**: the saved parent.
- **C2**: fitted to 48 collection searches per own training cell, run under C.
- **C'**: fitted to 48 collection searches per own training cell, run under G4 (a fresh one-shot
  refit, matched in collection attempts).

C2 and C' are each fitted once per lineage. Unsolved collection searches add no tapes but count
toward cost.

**Stages, in queue order:**

| stage | content | searches | projected |
|---|---|---|---|
| A | collect under C, fit C2 (32 lineages × 48 × own cells) | 7 680 | ≈ 9–10 min (probe: about 145 worker-s per lineage) |
| B (primary) | training: C2 and C, 32 fresh seeds per own training cell, shared | 10 240 | ≈ 14 min (1707: C cost about 4 000 worker-s per arm) |
| C | holdouts: C2 and C on the three withheld cells, 32 seeds per cell and lineage, shared | 6 144 | ≈ 9 min |
| D (source control) | collect under G4, fit C'; C' on stage B's and stage C's seeds | 7 680 + 5 120 + 3 072 | ≈ 43 min (G4 collection about 31 min, as in 1707) |
| **total** | | ≈ 40 000 | **≈ 75–80 min** |

**Admission and deadline.** Stage C runs whenever stage B completes. Stage D is admitted at full
size (16 lineages per family) if the remaining work time exceeds 1.25 × its projection. If not, it
is admitted at half size (lineages 1–8 of each family, fixed now) if the remaining time exceeds
1.25 × that projection. Otherwise it is skipped. Projections use 1707's per-search worker-seconds
(G4 collection 2.08) and the worker throughput measured in stages A–C. No result enters any gate.
- Internal work deadline: 100 min. Queue timeout: 1.85 h.
- C' contrasts use only lineages whose C' rows are complete for that phase.
- Expected clock: submitted at about 20:30, stages A–C end at about 21:05 and D at about 21:50.
  The worst case is the timeout at about 22:20.

**Estimator.** As in 1707. Per lineage and arm, take the mean over cells of the per-cell mean log2
evaluations (unsolved = 2 × cap). The contrast is per lineage. On training, the pooled estimate is
the equal-weight mean of the BE and PA family means, se = ½·√(se_BE² + se_PA²), t on 15 df. On
holdouts, each lineage's score is its mean over the three cells, with t over 32 lineages (31 df).
Results are reported as speed ratios 2^(−Δ) with 95% intervals. > 1 means the first arm is faster.

**Precision.** 1707's per-corpus C − T sd was 0.27 log2 (BE) and 0.16 (PA). Assuming 0.25 for C2 − C
gives a pooled half-width of about 0.09 log2 (±7%). That is enough to resolve a 1.10× increment
from 1. C2/C' has independent tables, so it should be a little wider (about ±8%; at half-size D,
about ±11%).

## Outcome rules

Rows are evaluated on the pooled stage-B C2/C. Bounds are 95%.

| row | condition | meaning |
|---|---|---|
| 0 infeasible | any lineage × cell yields < 24/48 under C; or any validation fails; or stage B is incomplete | Report yield, cost and validation; no comparison claim. |
| 1 | C2/C lower > 1 **and** C2/C' lower > 1 | A further training gain from this feedback step, attributable to collecting under C rather than G4. |
| 2 | C2/C lower > 1, and C2/C' lower ≤ 1 or stage D not run | C2 beats its parent; whether collecting under C caused it is unresolved. If C'/C is itself resolved > 1, the parent was not representative; say so. |
| 3 | C2/C lower ≤ 1 and 1 ≤ upper < 1.10 | No increment above 10% from this step (a small gain or loss not excluded). |
| 4 degradation | C2/C upper < 1 | Feedback slows training search at this scope. |
| 5 unresolved | C2/C lower ≤ 1 and upper ≥ 1.10 | Unresolved; report the n needed. |

**Holdout rule.** Interpreted in rows 1, 2 and 4; descriptive otherwise. It uses C2/C over 32
lineages:
- **transfers** if lower > 1;
- **harms withheld cells** if upper < 1;
- **no transfer above 10%** if lower ≤ 1 ≤ upper < 1.10;
- **unresolved** otherwise.

The same rule applied to C2/C' says whether the transferred part is attributable to the source.
"A useful second feedback step" (strategy) needs row 1 plus holdout C2/C transfers plus holdout
C2/C' lower > 1. A training-only gain limits transfer.

**Always reported (descriptive):**
- C'/C on training and holdouts, a replication check of the one-shot fit (expected ≈ 1).
- Per-family C2/C. Family is not separated from cell count and difficulty.
- Yields and distinct tapes under C and G4; row entropy and previous-token mutual information of
  C2, C' and C; start-row top-token share.
- Second-round collection cost (evaluations, worker-s) against C2's per-search saving over C, with
  the break-even number of future searches.
- No family-specificity contrast is pre-stated (strategy: stop rescoring tiny family contrasts).
  Matched/mismatched is not computed.

**Decisions.** Root 10 has no slots left after this run, so every row returns to strategy (`next:
strategy`).
- Row 1 with holdout transfer: close 21 as answered. One feedback step gives a further transferable
  gain, and a second step needs a new allocation.
- Row 1 or 2 without transfer: close 21 with the training-only limit.
- Row 2: close 21 with source attribution unresolved.
- Row 3: close 21. One round captures the gain to within 10% at this rule.
- Row 4: close 21 as harmful at this scope, with the entropy and diversity readouts as candidate
  reasons.
- Row 5: send the sizing to strategy.
- Row 0: write up feasibility.

## Alternatives considered

- **Drop C' (save about 43 min).** Lineages are not selected, so C and C' are exchangeable in
  expectation, and C2/C already compares a fit from a C-collected corpus with a fit from a
  G4-collected one, at matched attempts and the same rule. C' remains useful for three reasons:
  the strategy asks for it; it replicates the one-shot fit with new code and seeds; and it guards
  against C2 inheriting a parent's quirks. I keep it, but last and gated by time, so it cannot
  cost the primary contrast or its transfer.
- **Token-only refit T2 to attribute the increment to context.** Not funded. No claim that C2's
  increment is contextual will be made.
- **Pooling the first corpus, or shrinking toward C.** Rejected: data volume or a changed
  regularizer could then explain the gain.
- **A third round (C3) or a smoothing sweep.** Excluded by strategy until one step looks good.
- **Fitting executable (active) tokens.** The strategy's second priority, and it needs an
  extractor that has not been reviewed.
- **More seeds instead of C'.** The probe's effect (about 0.47 log2) is several times the planned
  half-width. Extra seeds would mostly narrow an interval that already decides.
