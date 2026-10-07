---
node: questions/10-compositional-map-transfer/20-solver-corpus-context
title: Decoder context fitted to training-solver corpora versus a token-only fit, with an emitted-marginal control and holdout transfer
---

## Why this now

I follow [strategy 1707](strategy.md) and its [concept plan](../../plans/solver-corpus-context.md).
Four procedures that *selected* decoder changes by noisy search cost found no resolved benefit
from context. This run uses a different signal: the token tapes of exact solvers. It asks
whether those tapes hold assembly information (which token follows which) that speeds fresh
search beyond a token-only fit to the same tapes. This is external fitting. A positive result
gives a data-derived target for later map evolution. It does not show that evolution can find
that target. A negative result bounds this estimator and this corpus, not context in general.

New sub-question [20](../../questions/10-compositional-map-transfer/20-solver-corpus-context/question.md)
uses root 10's thirteenth and last slot. No budget is raised.

## Steward probe (already run, read-only, ≈ 6 min)

[`steward_probe.py`](steward_probe.py) ran in a scratch copy of `research/main` built with its
Rust extension. It used a copy of `composition_search.search` that also returns the first exact
solver's decoded tape. Per family, one corpus came from 48 G4 searches per training cell (seeds
17 070 000+, cap 524 288). From it I fitted T, C (α 50), C400 (α 400) and K (definitions below).
Each arm then ran 12 fresh seeds per training cell (17 170 000+), with seeds shared across arms.

| | yield | collect wall | G4 | T | C (α 50) | C400 | K |
|---|---|---|---|---|---|---|---|
| BE (4 cells, 48 searches/arm) | 175/192 | 64 s | 13.99 | 12.33 | **11.55** | 12.87 | 12.95 |
| PA (6 cells, 72 searches/arm) | 281/288 | 50 s | 14.16 | 12.83 | **12.55** | 12.53 | 12.84 |

The G4 through K columns give mean log2 evaluations to an exact solve, with unsolved runs counted
as 2 × cap. Solve rates were 47–72 of 48–72 in every arm. Evaluating 600 searches took 70 s on
10 workers, and fitted arms took 0.3–1.2 s per search under load.

What this shows:

- The token-only fit alone beats G4 by about 2.5–3×. That is at least as much as the 1723
  nested learner's 2.2×, at roughly 1/10 of its cost.
- C is ahead of T in both families: by 0.78 log2 on BE (about 2.4 per-search se) and by 0.28
  on PA. K, which emits the same token frequencies as C, is not ahead of T. So in this probe
  the C advantage looks contextual.
- The probe also shows α matters. C400 is worse than C on BE.
- This is one corpus per family. It is a calibration, not evidence. α 50 is frozen from it, and
  the confirmation uses new corpora and new seeds.
- Paired per-search sd of C − T was 2.2 log2 (BE) and 1.8 (PA). Seed correlation between arms
  was low (−0.05, 0.41).

## What would be run

**Code.** Reuse `research/main`: `composition_search.py`, `four_reducer_maps.tables()["G4"]`,
`map_learning.normalize`, `crossed_learning_run.load_bank` (frozen 1603 bank SHA, the 1723 split
and the holdout-leakage checks). Add an optional solver-tape return to `search`. It must not
change random-number consumption or any existing output field.

**Validation, before stage 0:**
- Replay the first 20 GG seeds of 0315 on two training cells. Their rows must be bit-identical
  to the saved rows, apart from the new field.
- Each saved solver tape must re-verify exact on all 1 331 inputs.
- Each fitted table must pass `Decoder`, with minimum count ≥ 250 and R = 24 000.

**Frozen fitting rule** (as in the probe; nothing tuned on the evaluation blocks):
- *Corpus.* One collection search per seed with G4, cap 524 288, P 256, under the unchanged
  search. Take the first exact solver's full 32-token decoded tape. Unsolved searches add
  nothing but are charged to cost.
- *Counts.* Count transitions (previous token → token), including the start row 24. Rescale
  each cell's counts to a total of 1 600, so cells weigh equally whatever their solve rate.
- *T (token-only control).* G4 rows × exp(λ), with λ ∈ [−ln 16, ln 16]^24. λ is chosen by
  maximum weighted likelihood (L-BFGS-B from 0), then quantized with `normalize`.
- *C (context).* p_row = (n_row + 50 · g4_row) / (N_row + 50), quantized with `normalize`.
- *K (emitted-marginal control).* G4 × exp(κ), with κ fitted by a fixed-point iteration (400
  steps, step 0.7) so that K's exact 32-position emitted token marginal matches quantized C's.
  The match is valid when the max absolute error is ≤ 0.001. If K fails validation for a
  corpus, that corpus enters C/T but not C/K, and the count is reported.

**Corpora.** 16 independent corpora per family, on disjoint seed blocks new to this run (not the
probe's). Each corpus has 48 seeds per own training cell: BE 4 × 48 = 192 searches, PA 6 × 48 =
288. Canonical programs, the hand-set grammars and the 1723 maps never enter fitting. No holdout
is searched before stage 2.

**Stage 1: training cells (primary).**
- Each corpus's T, C and K run 32 fresh seeds per own training cell, on a block unique to that
  corpus and shared by its three arms. That is 16 × 3 × (4 + 6) × 32 = 15 360 searches.
- G4 reference: 96 seeds per training cell (960 searches).
- Descriptive reference: the 20 saved 1723 maps (M) on their own-family cells, 16 seeds per
  cell (1 600 searches).

**Stage 2: holdouts.** This runs if stage 1 finished and the remaining queue time exceeds 1.5×
the projected stage-2 time. It does not depend on stage 1's result, because it is cheap. Its
interpretation is gated below.
- All 32 corpora's frozen T, C and K run on the three holdouts, BE `S?m:(M+F)`, PA `(F?S:M)+m`
  and PA `(S?M:m)+F`. Each corpus gets 32 seeds per cell, shared across its arms: 9 216 searches.
- G4: 128 seeds per holdout (384 searches).

**Estimator.**
- Per corpus, for each arm: the mean over cells of the per-cell mean log2 evaluations.
- The contrast is C − T (and C − K), per corpus.
- Family-pooled estimate: the mean of the BE and PA family means, with equal family weight.
  se = ½·√(se_BE² + se_PA²), t on 15 df.
- Reported as a speed ratio 2^(−Δ), with a 95% interval.
- Per-family estimates are reported alongside the pooled one.
- Precision expected from the probe's noise (per-corpus contrast sd ≈ 0.3 log2, allowing for
  between-corpus spread): pooled half-width ≈ 0.11 log2, about ±8%.

**Runtime.** These estimates use the measured 0315 G4 cost (2.14 s per training search; the
probe ran 4.2 searches/s) and the fitted arms' 0.3–1.2 s.

| stage | searches | time |
|---|---|---|
| stage 0 collection | 7 680 | ≈ 30 min |
| stage 1 | 17 920 | ≈ 25–35 min |
| stage 2 | 9 600 | ≈ 15–20 min |
| **total** | ≈ 35 000 | **≈ 70–85 min** |

Queue timeout: 2.25 h (strategy cap 3 h). If submitted by about 19:00, the queue ends by about
20:30 and at worst by 21:15. That leaves time for analysis and a decision before 22:25.

**Amortization.** Report corpus cost (G4 searches, evaluations and seconds) against per-search
savings over G4, and the break-even number of future searches.

## Outcome rules

The rows are evaluated on pooled stage-1 estimates. "C/T" is C's speed over T: the lower and
upper bounds are 95% bounds, and > 1 means C is faster.

| row | condition | meaning |
|---|---|---|
| 0 infeasible | any corpus cell yields < 24/48 solvers; or validation fails; or > 4 corpora per family fail K validation; or stage 1 does not finish | Report the measured feasibility; no comparison claim. |
| 1 | C/T lower > 1 **and** C/K lower > 1 | Solver corpora carry useful context beyond token fitting and beyond C's own emitted frequencies (training cells, this fit). Stage 2 is interpreted. |
| 2 | C/T lower > 1, C/K lower ≤ 1 | The fitting procedure beats token fitting, but its gain is not separated from emitted frequencies; no isolated context claim. Stage 2 is interpreted as procedure transfer. |
| 3 | C/T lower ≤ 1 and upper < 1.10 | This fitting rule adds no gain above 10% over token fitting (if upper < 1, C is worse). Bounds this estimator and corpus only. |
| 4 unresolved | C/T lower ≤ 1 and upper ≥ 1.10 | Unresolved; report the n a decision would need. |

**Stage-2 rules** (interpreted only in rows 1–2; otherwise descriptive):
- **Transfer.** C/T on the holdouts, per-corpus mean over the 3 cells, t over 32 corpora. It
  transfers if lower > 1; no transfer above 10% if lower ≤ 1 and upper < 1.10; otherwise
  unresolved. The same rule on C/K decides whether the transferred increment is contextual.
- **Family.** Per holdout cell, C fitted on the matched family over C fitted on the mismatched
  family (Welch, 16 vs 16 corpora). A family-specific claim needs lower > 1 on that cell, and
  slowing the other family alone is not adaptation. The BE holdout is one task.

**Always reported (descriptive):**
- T/G4 and C/G4 on training and holdouts. C/G4 upper < 1 means C damages search.
- T versus the 1723 maps M: unpaired, a procedure comparison, not a learner claim.
- Per-family C/T. The probe suggests BE > PA, but family is not separated from cell count and
  difficulty.

**Decisions.**
- Row 1 or 2: close 20 as answered and return to strategy. The next distinction is whether
  evolution can discover the fitted context, which needs a new allocation.
- Row 3: close 20 at this estimator's scope and return root 10 to strategy (budget spent).
- Row 4: return to strategy with the sizing.
- Row 0: write feasibility and return to strategy.

## Alternatives considered

- **Joint token/context learning from G4, or context that does not displace token steps.**
  Scientifically live, but the strategy judged it too long for the remaining 5 h. It is another
  nested optimizer, priced by 1137 at about 4–6 h.
- **Probe-only queue (one or two corpora per family).** Rejected. The probe already did this,
  and the strategy asks not to trade corpus replication for seeds; 16 corpora per family are
  affordable.
- **Calibrating α by a search sweep.** Rejected as an unbounded tuning loop (the plan forbids
  it). α 50 is frozen from the probe, which ran on training cells only, on separate seeds.
  C400 is reported here as the probe's sensitivity witness, not run again.
- **Fitting only active (executed) tokens.** Rejected for now. It needs an executable-structure
  extractor that has not been reviewed. Full tapes are the stated rule, so a null does not
  exclude a learner over executable structure.
- **Running stage 2 only if stage 1 passes, gated in code.** Rejected. The in-code statistics
  add review risk for a stage that costs about 15 min. Instead, its interpretation is gated by
  the rows above.
