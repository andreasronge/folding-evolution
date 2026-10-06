---
node: questions/10-compositional-map-transfer/16-crossed-family-adaptation
title: Crossed BE/PA token maps on the three holdouts, stage 2 (frozen evaluation, no new learning)
---
# Proposal 2229: score the 20 frozen stage-1 maps and G4 on the three withheld cells

## Why this now

Stage 1 ([run 1723](../2026-10-06-1723/analysis.md), row 4) found that both families learn.
Own-family gain over G4 is BE 2.18× [1.98, 2.40] and PA 2.27× [1.95, 2.65]. Most of that gain
is generic: each family's maps speed the other family's training cells by 1.9–2.1×. In-sample
the crossed preference is small and unresolved: 1.13× [0.93, 1.37] on BE cells and 1.10×
[0.93, 1.29] on PA cells. The stage-2 size rule, fixed before stage 1 ran, gives n = 10 per
family, so no trajectories are added. What is left is the question 16 exists for: on the
withheld cells, does matched training beat mismatched training, or is transfer generic? Only
these cells can tell. This is root 10's slot 8 and question 16's second slot. Slot 9 is left
for strategy after this result, as strategy 1723 requires.

## What would be run

**Maps (frozen, nothing learned).** The 20 final maps in stage 1's `trajectories.json`
(BE1–BE10, PA1–PA10) and G4 (hash `8a7b3091…`). Verify every table hash against stage 1. No
map is selected, dropped or re-weighted.

**Cells.** Only the three holdouts on D1331: BE `S?m:(M+F)`, PA `(F?S:M)+m`, PA `(S?M:m)+F`.
Their labels come from the frozen bank snapshot (SHA256 `b2b856cb…`). This is the first time any
learned map meets these cells. The bank screen and 1603's 50-seed G4 calibration did search them.

**Search.** Same engine and settings as stage 1's fresh scoring: cap 524 288, P 256, length 32,
crossover 0.7, mutation 0.03, 64 sampled training cases, exact check on all 1 331 inputs,
unsolved T = cap. **400 fresh seeds per holdout** (new block 2229000–2229399), shared by all 21
maps. In total 21 × 3 × 400 = 25 200 searches.

**Why 400 seeds.** My check of stage 1's fresh rows found that at 50 seeds about half of the
per-cell between-map variance is seed noise. Seed-noise sd was 0.15–0.33 log2; the remaining
between-map sd was 0–0.46. At 400 seeds the noise part falls to about 0.05–0.12. That matters
for the single BE cell. Going beyond 400 buys almost nothing, because the between-map spread
dominates.

**No training rescoring.** Stage 1's 50-seed fresh training rows are reused for the descriptive
training-to-holdout comparison.

**Runtime.** At 1603's loaded calibration G4 takes 1.5–2.0 s per full-cap search on these three
cells. In stage 1 the full-cap fresh searches took 1.0 s on average across maps. 25 200 searches
× about 1.1 s on 10 workers ≈ 45–55 min. Set the timeout to 2 h and the internal deadline to
1.75 h. One queue entry.

## Feasibility (measured)

| Quantity | Value | Source |
|---|---|---|
| G4 on the holdouts, 524k cap | BE 47/50, PA 49/50 and 50/50 solved; KM medians 8.7k, 12.5k, 18.3k | 1603 `search.jsonl` |
| Learned maps' training solve rates | 481–499/500 per map | 1723 analysis |
| Per-cell between-map sd of log2 gain (50 seeds) | BE cells 0.17–0.53, PA cells 0.24–0.48; s_off 0.355 | 1723 `fresh_scores.json` |
| Seed-noise share at 50 seeds | seed sd 0.15–0.33, between-map sd 0–0.46 log2 | steward re-analysis of the same rows |
| Full-cap search time | about 1.0 s average across 21 maps, 10 workers | 1723 analysis |

The code exists: stage 1's fresh-scoring path and report, with a different cell list and seed
block. The researcher adds a holdout mode that reads the saved maps and refuses to run any
learning.

## Readouts (fixed before any holdout is scored)

Per map m and holdout h, the log2 gain g(m, h) is the mean over the 400 shared seeds of
log2(T_G4 / T_map). The trajectory is the unit, n = 10 per family, with 95% t intervals:
one-sample within an arm, Welch between arms. Ratios are 2^(mean log2). The practical margin
is 1.25×, as in stage 1.

1. **Generic transfer, per arm and holdout.** The gain over G4 (6 estimates). Each is labelled
   L (lower bound > 1) or not.
2. **Crossed contrast per direction (primary).**
   - C_BE: BE-trained minus PA-trained maps on `S?m:(M+F)`.
   - C_PA: PA-trained minus BE-trained maps on the per-map mean of the two PA holdouts.
   - Each is labelled W (lower > 1), B (upper < 1.25) or X. W takes precedence over B; both
     flags are reported. Each PA holdout's contrast is also reported on its own (descriptive),
     so opposite effects are not hidden in the mean.
3. **Within-map interaction (pre-stated secondary).** Per map, d = g(BE holdout) − mean g(PA
   holdouts). I = mean d (BE maps) − mean d (PA maps) = C_BE + C_PA, Welch. In stage 1 this was
   post hoc: 1.24× [1.09, 1.41] in-sample. Here it is fixed in advance. It asks whether any
   family information reaches the withheld cells, pooled over both directions. It does not say
   which direction carries it.
4. **Damage check.** For any W direction, is the mismatched arm's gain over G4 on that
   direction's holdouts below 1 (upper bound < 1)?
5. **Descriptive.**
   - Holdout gain against each map's own stage-1 training gain: transfer loss per arm.
   - Solve counts.
   - Shortcut counts.
   - Per-map rows.

**Expected precision.** These estimates come from stage 1's per-cell spreads, adjusted to 400
seeds. They are not guarantees for these particular cells.
- C_BE: half-width about 0.35–0.45 log2, so it resolves only true effects of about 1.3–1.4× or
  more. B (upper < 1.25) is reachable only if the point estimate is near or below 1.
- C_PA: about 0.20–0.26 log2, so it resolves about 1.2×.
- I: about 0.25–0.35 log2.

A true 1.1× preference, the size seen in-sample, would most likely come out X in both
directions.

## Outcome rules (non-overlapping, applied in order)

| Row | Condition | Meaning | Next |
|---|---|---|---|
| U | Validation fails: a hash mismatch, missing or duplicate rows, a training cell or learning call in the job set, or G4 solving fewer than 85% on any holdout (1603: 94–100%) | Unresolved. The frozen maps can be re-scored. | Fix and re-run; the slot is used |
| 1 | C_BE and C_PA both W | Training-family-dependent transfer in both directions on these three cells. If the damage check fires for a direction, that direction is labelled "via harm to the mismatched arm", not useful specialization. | Strategy. Root 10's part-2 answer for token learning: positive on this screened bank, with one BE cell |
| 2 | Exactly one direction W | Family dependence shown in one direction only. The other direction is bounded (B) or unresolved (X), as labelled. | Strategy |
| 3 | Neither W, and no arm has an L gain over G4 on any holdout | Transfer lost: the stage-1 training gains do not carry to the withheld cells (C, specialization to training cells). | Strategy. This limits this learner, not learnable family structure |
| 4 | Neither W, and both B | The family preference on these holdouts is bounded below 1.25× in both directions. Transfer is generic to that resolution; this is not equality. | Strategy. Token learning here gives generic transfer; any family-specific part needs a different decoder or more tasks |
| 5 | Otherwise (neither W, not both B, some generic transfer) | Per-direction family dependence unresolved at n = 10. Sub-reading 5a: I is W, so family information reaches the withheld cells in aggregate, with direction unresolved. Sub-reading 5b: I is not W, so the family component is unresolved, with generic transfer as labelled in readout 1. | Strategy, with the n that would resolve 1.1× (about 35–40 per family) and its cost |

**My prediction:** row 5 (about 55%), most likely 5b.
- Generic transfer L on all six arm × holdout estimates, around 1.6–2.0× (0132's holdouts kept
  about three quarters of the training log-gain).
- C_BE about 1.1–1.2× and C_PA about 1.05–1.15×, both X.
- Row 1 or 2: about 25%. Row 4: about 10%. Row 3: under 10%.

## What it cannot show

- Anything beyond these three screened cells. The BE direction rests on one task, and repeated
  learning cannot add BE task replication.
- Learned context: G4's context stays hand-supplied, and only token weights moved.
- Whether a 1.1× family preference exists. At n = 10 such an effect would most likely stay
  unresolved, and an unresolved contrast is not equality.
- Shape alone as the cause: the two training sets differ in size (4 cells against 6) and in
  role distribution.

## Alternatives considered

- **Add trajectories to resolve about 1.1×.** That needs about 35–40 per family, roughly 11 h
  more learning. The frozen size rule rejects it, and choosing it now would be a rescue driven
  by the in-sample result. Rejected.
- **Rescore training at 400 seeds too.** About 1 h more. It would sharpen only the in-sample
  contrasts, which do not answer 16. Skipped; the 50-seed rows serve the descriptive transfer-loss
  comparison.
- **Add the 1603 hand-set grammars on the holdouts as a scale reference.** Strategy 1723 calls
  them a capacity witness that needs no further sweep. Skipped.
- **A union-trained arm (all ten training cells).** It would test whether family-specific
  training beats simply more data. That is a new learning study and strategy's call after this
  result.
- **Root 01 or parked questions.** No reopen condition is met (02, 04, 07, 08, 09 re-checked).
