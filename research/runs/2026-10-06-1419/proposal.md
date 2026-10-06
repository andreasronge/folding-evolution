---
node: questions/10-compositional-map-transfer/14-saved-map-shape-shift
title: Saved-map branch/linear shift — replication on the "b" continuations, residual ablation and a frequency-matched control (re-proposal of 1400)
---
# Proposal: does R's branch-over-linear shift replicate, and does it need its residuals?

**Re-proposal.** Run [1400](../2026-10-06-1400/proposal.md) proposed this design and the critic
approved it with notes ([critique](../2026-10-06-1400/critique.md)). It was blocked before
prepare by a merge conflict, so nothing ran
([decision](../2026-10-06-1400/decision.md)). The design is unchanged. The critic's notes are
applied below; the changes are marked **[note N]**.

**Precondition:** resolve the add/add conflict on
`research/runs/2026-10-06-0811/code_review.md` by keeping main's second-pass review
(`verdict: pass`). Otherwise this run blocks the same way.

Root 10 is at 4 of 7 slots and 14 has 1 of 1 left. As in [strategy 1400](../2026-10-06-1400/strategy.md),
the slot after this goes to the [four-reducer feasibility study](../../plans/four-reducer-family-transfer.md).

## Why now

In 0811 the R maps tied M+ on the post-addition (PA) training cells: 1.00× [0.90, 1.11]. R is M's
token multipliers plus 24×23 learned row residuals; M+ is continued token steps only. The only
hint that learned context does anything is an unregistered six-map pattern from the "a"
continuations on the off-family cells ([0811 analysis §2.5](../2026-10-06-0811/analysis.md)).
There R was 1.33× [1.05, 1.66] faster than M+ on branch-else (BE), faster on **5/6 starts**
(start 4 at 0.94) **[note 4]**. On linear (LIN) R was 0.65× [0.44, 0.88], slower on 6/6.

That pattern was found on the same 50 seeds per cell it was measured on. The six "b"
continuations were never scored on these cells. They share their M starts with "a" but have
independent learning seeds, so they give a conditional replication, not six new starting maps.
This check decides how the four-reducer study weights the contextual learner.

## What would be run

**Maps (55, all frozen; loaded from saved files with hash checks):**
- G and M1–M6 (0132 `final_maps.json`) as references.
- 12 × M+, 12 × R and 12 × R_abl (R's multipliers with residuals zeroed) from 0811
  `final_maps.json`, pairs 1a–6b.
- **12 × R_fm (new, deterministic, no search):** G-based token multipliers fitted so the map's
  emitted token frequencies match R's.
  - "Emitted" means the expected frequency pooled over the 32 tape positions under uniform
    alleles. It is computed exactly by propagating the previous-token chain, so no sampling.
  - Fit: iterative proportional scaling of the 23 log-multipliers within ±ln 16, then the
    production `normalize()`.
  - Accept if TV distance to R < 0.005 after normalization; otherwise drop that pair's R_fm and
    report it. The evaluator keeps this check.
  - R_fm keeps G's context rows and R's pooled marginals but not R's learned row residuals.

**Cells (frozen, as in 0811):**
- Two BE cells: `S?M:(S+m)`, `S?m:(S+M)`.
- Six linear cells: `2M+S+m`, `2S+M+m`, `2m+S+M`, `2(M+m)+S`, `2(S+M)+m`, `2(S+m)+M`.
- Harness: D1331, P 256, L 32, crossover 0.7, lexicase, 524 288-eval cap. Cost = mean log2
  evaluations to exact; unsolved = log2(2 × cap).
- No added cells and no search for further IF_GT shapes.

**Seeds:** 200 fresh seeds per cell (base 1 419 000 000), shared across maps on each cell.

**Order** (a deadline stop leaves complete starts):
1. G on the 8 cells. This is the harness check, and these rows are reused as the G reference,
   not rerun **[note 1]**.
2. "b" pairs (M+, R, R_abl, R_fm), start by start.
3. "a" pairs.
4. M1–M6.

**Group means and contrasts:**
- BE = mean of the 2 BE cells; LIN = mean of the 6 linear cells.
- X/Y = 2^(cost_Y − cost_X), so > 1 means X is faster.
- Per pair: BE ratio, LIN ratio and shift = BE ratio ÷ LIN ratio. Computed for R/M+, R/R_fm,
  R/R_abl and R_fm/M+.

**Intervals:** one log2 contrast per start, then a t interval with 5 df.
- "b"-only: one pair per start.
- Pooled: the a/b mean within each start, so starts are the clusters.
- All six starts are required for any declared verdict. If a start or an R_fm fit is missing,
  the affected layer is reported as unresolved. It is not rerun with fewer df **[note 4]**.

**Descriptive reports:**
- Exact emitted IF_GT frequency per map, and the per-pair shift against the R−M+ IF_GT
  difference.
- G costs and M/G per cell.
- Per-pair ratios and solved counts.
- "b"-only dependency contrasts beside the pooled ones, since the pooled layer includes the "a"
  maps that selected the lead **[note 3]**.

## Feasibility (measured)

- **Runtime:** 55 maps × 8 cells × 200 seeds = 88 000 searches. 0811's off-family phase took a
  mean of 0.3615 **worker-elapsed seconds** per search **[note 1]**. That is about 53 min at 10
  workers before overhead. Queue timeout 2.5 h. The R_fm fit takes about 6 s.
- **Solve forecast [note 1]:** in 0811's raw `search.jsonl` the hardest cell, `S?M:(S+m)`,
  solved 931/950 searches (G 47/50; learned "a" maps 588/600). Every other cell solved 950/950.
  At those rates expect about 196/200 per learned map on the hard cell and nearly 200/200
  elsewhere. Censoring is minor but not zero. R_fm and off-family R_abl solve rates are
  unmeasured.
- **R_fm exists:** the steward probe ([1400 probe](../2026-10-06-1400/steward_probes/marginal_fit.py))
  matched all 12 R maps, float TV < 1e-4, with no multiplier at the bound. The critic ran the
  fit through production `normalize()` from research/main: 12/12 pass, TV 0.000029–0.000070.
  R vs M+ differ by TV 0.09–0.21, and R vs R_abl by only 0.01–0.10, so R_abl alone is a weak
  frequency control.
- **Precision:**
  - Per-start "a" log2 R/M+ on BE: 0.52, 0.56, 0.60, −0.10, 0.47, 0.42 (sd 0.27).
  - Per-start "a" shifts: 0.65, 1.23, 1.24, 1.77, 0.81, 0.43 (sd 0.48).
  - If "b" repeats this, the expected intervals are BE ≈ [1.09, 1.62]× and shift
    ≈ [1.43, 2.87]×.
  - These are expected widths, not assured power. Effects much below about 1.22× (BE) or
    1.41× (shift) are likely to come out unresolved.
  - Seed SE per map is ≤ 0.05 log2, so more seeds would not help; only new starts would.
- **Gate (row 0):** stop if G's 8-cell mean differs from 0811's G off-family mean by > 0.6
  log2, or if any loaded hash differs.

## Outcome rules (primary: the six "b" pairs; first match)

| row | condition (95% t, 5 df) | meaning |
|---|---|---|
| 0 | gate fails, or fewer than six complete "b" starts | no verdict; fix and rerun |
| 1 | BE R/M+ lower > 1 **and** shift lower > 1 | the BE gain and the shift replicate (conditionally, same starts) |
| 2 | shift lower > 1, BE R/M+ lower ≤ 1 | a relative shift replicates without a resolved BE gain; call it "a linear loss" only if LIN R/M+ upper < 1 **[note 4]** |
| 3 | shift lower ≤ 1, shift upper < 1.41, BE upper < 1.25 | no replication at the size seen in "a"; any shift is bounded below 1.41× and any BE gain below 1.25×, not shown to be zero **[note 4]** |
| 4 | otherwise | unresolved; report intervals, not equality |

**Dependency layer** (pooled 12 pairs by start, "b"-only beside it; interpreted under rows
1–2, reported always). First match, so D-a takes precedence over D-b **[note 4]**:

| sub-row | condition | meaning |
|---|---|---|
| D-a | R/R_fm shift lower > 1 | the shift needs R's residuals beyond its pooled uniform-allele emitted frequencies **[note 3]** |
| D-b | R/R_fm shift upper < 1.25 **and** R_fm/M+ shift lower > 1 | pooled emitted frequencies reproduce the shift; any residual contribution is bounded below 1.25× |
| D-c | otherwise | dependency unresolved |

**Reading D-a [note 3].** A shift can come entirely from residuals hurting linear search. For
example, R/R_fm = 1 on BE and 0.5 on LIN gives a shift of 2. So under D-a, use the BE and LIN
R/R_fm intervals as well:
- BE R/R_fm lower > 1: residuals help branch search.
- Otherwise: a residual-dependent trade-off only, not a useful branch gain.

R/R_abl is reported as a co-adaptation check. It changes frequencies too, so it attributes
nothing on its own.

**What each outcome changes:**
- **Row 1 + D-a with BE R/R_fm > 1:** the contextual learner enters the four-reducer study as
  a full arm. This is the first evidence that learned row context does something pooled
  frequencies do not, though it is still not family specificity.
- **Row 1 + D-a with only a trade-off,** row 1 + D-b, or row 2: build the two-family study
  around the token learner. Context is at most a secondary arm.
- **Row 1 + D-c [note 4]:** the pattern replicates but its source is unresolved. Context is a
  secondary arm with an R_fm control carried along. Do not buy precision here.
- **Row 3:** drop the lead at the stated bounds. Token-only adaptation stays the demonstrated
  gain.
- **Row 4:** record the intervals and move on. Only new starts would help, and the strategy
  rules out a precision loop.

In every case, close 14 and return to strategy. Expected outcomes: row 1 ≈ 35%, row 4 ≈ 35%,
row 3 ≈ 20%, row 2 ≈ 10%.

## Alternatives considered

- **R_fm/R_abl on the PA holdouts** (about 5 000 searches): reopens the start-limited PA
  increment. Left out.
- **Context-free marginal maps:** would only repeat "G-type context helps".
- **Sampling solver supply:** descriptive only; the exact emitted frequencies cover the
  relevant covariate.
- **Skip to the four-reducer feasibility study:** the strategist asked for this check first.
  It costs about an hour of queue time and sets the contextual arm's weight there.
