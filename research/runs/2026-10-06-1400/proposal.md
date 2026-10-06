---
node: questions/10-compositional-map-transfer/14-saved-map-shape-shift
title: Saved-map branch/linear shift — replication on the "b" continuations, residual ablation and a frequency-matched control
---
# Proposal: does R's branch-over-linear shift replicate, and does it need its residuals?

This follows [strategy 1400](strategy.md): one bounded check of the only contextual lead,
using saved maps and no new learning. The next slot then goes to the
[four-reducer feasibility study](../../plans/four-reducer-family-transfer.md). I opened
sub-question [14](../../questions/10-compositional-map-transfer/14-saved-map-shape-shift/question.md)
with a budget of 1. Root 10 has 3 slots left at 7. 13 is closed and has no budget left.

## Why now

In 0811 the R maps (M's token multipliers plus 24×23 row residuals) tied M+ (token steps
only) on the post-addition (PA) training cells: 1.00× [0.90, 1.11]. The one hint that
learned context does anything is an unregistered six-map pattern from the "a" continuations
on the off-family cells ([0811 analysis §2.5](../2026-10-06-0811/analysis.md)). There R
was 1.33× [1.05, 1.66] faster than M+ on branch-else (BE), with 6/6 starts in that
direction (one, start 4, at 0.94). It was 0.65× [0.44, 0.88] on linear, slower in 6/6.
That pattern was found on the same 50 seeds per cell that it was measured on. The six "b"
continuations were never scored on these cells. They share their M starts with "a", so
they are a conditional replication: same starts, independent learning seeds. They are not
new starting maps.

Two readings are cheap to separate now, and they decide how the two-family study treats
the contextual learner. One is that residuals encode a shape preference. The other is
that R simply emits different token frequencies, for example more IF_GT, which linear
cells do not use.

## What would be run

**Maps (55, all frozen; loaded from saved files with hash checks):**
- G and M1–M6 (0132 `final_maps.json`) are references for baseline difficulty.
- 12 × M+, 12 × R and 12 × R_abl (R's multipliers with residuals zeroed) come from 0811
  `final_maps.json`, pairs 1a–6b.
- **12 × R_fm (new, deterministic, no search):** G-based token multipliers fitted so the
  map's emitted token frequencies match R's. "Emitted" means the expected token frequency
  pooled over the 32 tape positions under uniform alleles. This is computed exactly by
  propagating the previous-token chain from the start row, so no sampling is needed.
  - Fit by iterative proportional scaling of the 23 log-multipliers within ±ln 16. Then
    apply the production `normalize()` (250 floor, integer counts).
  - Accept a map if, after normalization, the total variation (TV) distance to R's
    frequencies is < 0.005. Otherwise drop R_fm for that pair and report it.
  - R_fm keeps G's context rows and R's marginals, but not R's learned row residuals.
    Beating R_fm therefore means R's *residual* context matters beyond its frequencies. It
    does not mean the context is new, because G already has context.

**Cells (frozen, as in 0811; no additions):**
- The two BE cells `S?M:(S+m)` and `S?m:(S+M)`.
- The six linear cells (D1: `2M+S+m`, `2S+M+m`, `2m+S+M`; D2: `2(M+m)+S`, `2(S+M)+m`,
  `2(S+m)+M`).
- D1331, the 0811 harness unchanged: P 256, L 32, crossover 0.7, lexicase, 524 288-eval
  cap, cost = mean log2 evaluations to exact, unsolved = log2(2 × cap).
- I will not add PA cells or search for further IF_GT shapes. Strategy 1400 rules out an
  expanding search for favourable cells.

**Seeds:** 200 fresh seeds per cell (new base, e.g. 1 401 000 000). Every map gets the
same seed set on a cell.

**Order** (so a deadline stop leaves complete starts):
1. Harness check: G on the 8 cells.
2. The "b" pairs (M+, R, R_abl, R_fm), start by start.
3. The "a" pairs.
4. G and M1–M6.

**Group means:** BE = mean over the 2 BE cells; LIN = mean over the 6 linear cells (equal
cell weights). A speed ratio X/Y = 2^(cost_Y − cost_X); > 1 means X is faster.

**Pre-stated contrasts** (per pair, then summarized across starts):
- BE ratio: R/M+ on BE.
- LIN ratio: R/M+ on LIN.
- Shift: (R/M+ on BE) ÷ (R/M+ on LIN).
- The same three for R/R_fm, R/R_abl and R_fm/M+.

**Intervals:** take one log2 contrast per start and form a t interval with 5 df.
- "b" only: one pair per start.
- Pooled: the mean of a and b within each start, so starts are the clusters.
- This keeps all six starts, start 4 included. With only six clusters, a bootstrap would
  understate the spread.

**Descriptive reports (no inference):**
- Each map's exact emitted IF_GT frequency, and how the per-pair shift relates to the R−M+
  IF_GT difference.
- G costs per cell and M/G, so the linear floor is visible.
- Per-pair ratios and solved counts.

**Runtime:**
- 55 maps × 8 cells × 200 seeds = 88 000 searches.
- 0811's off-family phase cost 0.36 CPU-s per search on average, measured from 7 600 rows
  in its `search.jsonl` (BE `S?M:(S+m)` 1.54 s; the others 0.11–0.37 s). That gives about
  580 CPU-s per map and ≈ 32 000 CPU-s in total, **about 55 min at 10 workers**.
- The R_fm fit takes about 6 s for all 12 maps.
- Proposed queue timeout: 2.5 h. The researcher should write a small evaluator that
  reuses 0811's test harness from `research/main`, where 0811 is merged. No learning code
  is needed.

## Feasibility

- **The frequency-matched control exists.** Steward probe
  ([steward_probes/marginal_fit.py](steward_probes/marginal_fit.py), 6 s): for all 12 R
  maps a G-based multiplier vector reproduces R's emitted frequencies.
  - Float TV < 1e-4, with no multiplier at the bound. The integer `normalize()` step still
    needs checking, which is the acceptance rule above.
  - R differs from M+ in emitted frequencies by TV 0.09–0.21, and from R_abl by only
    0.01–0.10. So R_abl alone is a weak frequency control, which is why R_fm is added.
- **Precision at the observed spread** (from the "a" maps on the 0811 seeds):
  - Per-start log2 R/M+ on BE: 0.52, 0.56, 0.60, −0.10, 0.47, 0.42 (mean 0.41, sd 0.27).
  - Per-start shift: 0.65, 1.23, 1.24, 1.77, 0.81, 0.43 (mean 1.02, sd 0.48).
  - If "b" repeats this at the same spread, the six-start t intervals are BE about
    [1.09, 1.62]× and shift about [1.43, 2.87]×, both resolved.
  - The smallest effects six starts can resolve at this spread are about 1.22× on BE and
    1.41× on the shift. A real effect half as large as in "a" would come out unresolved.
    I accept that limit and do not plan a follow-up that only adds precision (see below).
- **Seed noise is minor.** Per-cell seed sd is about 0.96 log2. At 200 seeds the per-map
  group-mean SE is ≤ 0.05 (BE) and ≤ 0.03 (LIN), well below the between-start sd. More
  seeds would not help; more starts would.
- **Harness gate (row 0):** stop and report if G's 8-cell mean cost differs from 0811's G
  off-family mean by more than 0.6 log2. Also stop if any loaded table hash differs from
  the saved one.

## Outcome rules (primary: the six "b" pairs only; first match)

| row | condition (95% t intervals, 5 df) | meaning |
|---|---|---|
| 0 | harness or hash gate fails | no result; fix and rerun |
| 1 | BE R/M+ lower bound > 1 **and** shift lower bound > 1 | **branch-tied shift replicates** (conditionally, same starts) |
| 2 | shift lower bound > 1, BE R/M+ lower bound ≤ 1 | **only a linear loss replicates**: not a branch gain (S3) |
| 3 | shift lower bound ≤ 1 **and** shift upper bound < 1.41 **and** BE R/M+ upper bound < 1.25 | **does not replicate** at the size seen in "a" (S4) |
| 4 | anything else | **unresolved**; report the intervals, do not call it equality |

**Dependency layer.** This uses the pooled 12 pairs, clustered by start. It is interpreted
only under rows 1–2 and reported in every case.

| sub-row | condition | meaning |
|---|---|---|
| D-a | R/R_fm shift lower bound > 1 | the shift needs R's residual context beyond its token frequencies (S1) |
| D-b | R/R_fm shift upper bound < 1.25 **and** R_fm/M+ shift lower bound > 1 | token frequencies reproduce the shift (S2) |
| D-c | otherwise | dependency unresolved |

R/R_abl is reported alongside, labelled as a co-adaptation dependency check. Removing
residuals changes frequencies too, so it does not attribute the shift by itself.

**What each outcome would change:**
- **Row 1 + D-a:** the first evidence, on the training-related shape, that learned row
  context does something token frequencies do not. The contextual learner then enters the
  two-family study as a full arm next to the token learner. It is still not family
  specificity: BE is one related shape, and "b" shares its starts.
- **Row 1 + D-b**, or row 2: the shift is token frequency, or only a linear loss. The
  two-family study is built around the token learner, with context as at most a secondary
  arm.
- **Row 3:** the lead was noise on six maps. Drop it; every resolved gain on root 10 is
  token retuning.
- **Row 4:** do not buy precision. At this spread only new starts would help, and the
  strategy rules out an indefinite precision loop. Record the intervals and move to the
  four-reducer feasibility study, with context as a secondary arm.

In every case I close 14 and return to strategy, as strategy 1400 asks. My expectation is
row 1 or row 4 at about 35% each, row 3 at about 20% and row 2 at about 10%. In the "a"
maps the linear loss was larger and noisier than the BE gain, and start 4 was degenerate.

## Alternatives considered

- **R_fm and R_abl on the PA holdouts**, to see whether R's 1.16× holdout edge is
  frequency-driven. This is cheap (about 5 000 searches), but it reopens the deferred PA
  increment, which is limited by the number of starts. Left out to keep this check on one
  question.
- **Fully context-free marginal maps** (R's frequencies, tied rows). Beating these would
  only repeat "G-type context helps", which is shown many times already. R_fm is the
  sharper control.
- **Sampling solver supply for the "b" and R_fm maps** (about 80 min at 10⁸ per map). It
  is descriptive only, and supply and neighbourhood move together. The exact emitted
  frequencies cover the covariate that matters here.
- **Going straight to the four-reducer feasibility study.** The strategist asked for this
  check first. It costs about an hour of queue time and decides how the contextual arm is
  weighted in that study.
