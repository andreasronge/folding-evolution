---
node: questions/10-compositional-map-transfer/15-four-reducer-family-bank
title: Four-reducer bank (FIRST added) — reviewed alias/split screen, 13-cell search calibration under G4, descriptive family-grammar witness, learner cost pilot gated on split/headroom/cost only (root 10, slot 6 of 7; revision of 1536)
---
## Why this now, and what changed since 1536

[Strategy 1536](../2026-10-06-1536/strategy.md) gives root 10's slot 6 to the feasibility study
in the [four-reducer plan](../../plans/four-reducer-family-transfer.md). The study asks whether
adding FIRST to SUM/MAX/MIN gives two families, each with a usable split, headroom over a fixed
grammar and an affordable learning comparison. The families are branch-else (BE `A?B:(C+D)`)
and post-addition (PA `(A?B:C)+D`). The [1536 proposal](../2026-10-06-1536/proposal.md) was
sent back ([critique](../2026-10-06-1536/critique.md)). Its blocking point was correct:

- The proposal treated the hand-set family grammars as a necessary condition. A missing
  matched-vs-swapped contrast was read as "this decoder class cannot carry family
  specificity", and a missing gain over G4 as "no headroom". Both readings gated stage C and
  slot 7.
- Two hand-set row replacements do not exhaust previous-token decoders, still less G4-based
  token multipliers. In 0132 a hand-set PA grammar did not beat G, yet learned multipliers gave
  2.23× on fresh training.

**This revision:**
1. **The contrast is a positive witness only.** A resolved matched-over-swapped contrast counts
   as evidence of capacity. Anything else is reported as bounded or unresolved, never as
   incapacity. It gates nothing.
2. **The learner pilot is gated only on things that make it uninterpretable or unaffordable:**
   a split in both families, G4 headroom (the frozen 4 096 rule), G4 tractability on training
   cells, and measured cost. "Matched grammar beats G4" is reported but does not decide
   headroom.
3. **If the split fails, the run returns the exact obstacle, the calibration and the contrast
   intervals.** It draws no conclusion about learned specificity.
4. **Notes 1 and 3 are folded in:** a provisional solve forecast; a first-block checkpoint that
   measures solves, seconds and projected cost; incomplete search reported as unresolved; a
   separate reading for cap-dominated contrasts; a seed-paired bootstrap; and per-family logic
   stated explicitly.

I also applied the critic's digest notes 5–8 to the digest, to root 10 and to question 14
(wording only; see 14's log).

**The probe still predicts that BE fails the split rule.** The run is still worth it, for three
reasons:
- The strategist gets a reviewed, Rust-checked screen.
- It measures search headroom, censoring and cost on all 13 retained cells under the new
  24-token alphabet. Old G rates do not carry over to G4, and the asymmetric options need these
  numbers.
- It gives the first measurement of the family-grammar witness. Run 0001 planned it but never
  reached it.

Critique note 4 judged this proportionate. No learning runs after a failed split.

## Probe (1536 cycle; unreviewed; [`steward_probes/`](../2026-10-06-1536/steward_probes/))

`probe.py` extends `composition_bank.SemanticMachine` (research/main @ `b397f72`) with FIRST as
token 23. FIRST returns the first element; an empty or wrong-type list gives 0, as for the other
reducers. The probe enumerates all 19 executable tokens with exact typed-state dedup: depth 8
stored, depth 9 output-only, as in 0001. Checks ran on the semantic machine only, because Rust
has no FIRST yet.

| | D625 | D1331 | D2401 |
|---|---|---|---|
| cost (depth 8 + 9 output-only) | 117 s, 4.0 GB | 114 s, 5.1 GB | 122 s, 4.5 GB |
| retained / 36 (≥ 80% rule, no exact duplicates) | 10 (BE 4, PA 6) | **13 (BE 5, PA 8)** | 13 (BE 5, PA 8) |
| role-covered holdout pairs, BE / PA | 0 / – | **0 / 9** | 0 / – |

- **No cell conditioned on M or m survives.** They all die by depth 6: M>0 holds on 84% of D1331
  inputs and m>0 on 9%, so one branch is a near-alias.
- **The D1331 BE survivors are** `S?m:(M+F)`, `S?M:(m+F)`, `S?F:(M+m)`, `F?S:(M+m)` and
  `F?m:(S+M)`. In the `then` role, S, F and M each occur only once, so no BE pair can be held
  out with its roles covered by training.
- **One BE cell could be held out alone:** `S?m:(M+F)`.
- **The sixth BE cell, `F?M:(S+m)`, is a near-alias** (0.857 agreement).

## What would be run (one queue entry, staged and gated in code)

**Frozen before any search** (unchanged from 1536 except where marked):

- **Alphabet `v2_rmin_first`.** This is `v2_rmin` plus FIRST at id 23, in both Python and Rust.
  Validation comes first:
  - the semantic machine matches brute-force Python execution up to depth 4;
  - Python and Rust agree on 10⁵ random 32-token programs;
  - all 36 canonicals, NOP-padded, reproduce their labels in Rust.
- **Roster: 36 cells.**
  - BE: 12 cells (A and B ordered, {C, D} unordered); canonical `push(C) push(D) ADD push(B) push(A) IF_GT`.
  - PA: 24 cells; canonical `push(C) push(B) push(A) IF_GT push(D) ADD`.
- **Retention: 0001's rule.** A cell is dropped if any program of ≤ 9 tokens agrees with it on
  ≥ 80% of inputs, or if its labels equal another cell's.
  - Only D1331 can be selected.
  - D625 and D2401 are screened and reported only (about 4 min).
- **Split rule: 0001's rule, applied per family.**
  - The family needs ≥ 4 retained cells and a holdout pair whose every (role, reducer) also
    occurs in the family's training cells.
  - Roles are BE {cond, then, sum} (summands unordered) and PA {cond, then, else, summand}.
  - The holdout pair is the first valid one in lexicographic order.
  - No training cell may share labels with a holdout.
- **Decoders** (24 000 alleles, so U stays at 1 000 per token; 24 tokens; 25 rows):
  - **U:** uniform.
  - **F4:** F's weights, plus FIRST = 3 (as MAX and MIN).
  - **G4:** G's rules with FIRST as a fourth reducer, floor 500.
    - Start row: INPUT 12 500.
    - After INPUT: each of the four reducers gets 3 625; SUM's share is split 1 813 / 1 812
      with REDUCE_ADD.
    - After any integer-producing token (including FIRST): INPUT, ADD, DUP and IF_GT get
      3 500 each.
    - Every other row is uniform.
  - **G4-marg:** G4's tied marginals.
  - **G4-BE:** G4 with two rows replaced. After ADD: INPUT 12 500. After IF_GT: DUP 12 500.
  - **G4-PA:** G4 with two rows replaced. After IF_GT: INPUT 6 500 and ADD 6 500. After ADD:
    DUP 12 500.
  - **G4-BE-marg and G4-PA-marg:** the tied marginals of the two family grammars.

  The family grammars are 0001's stage-C rules: diagnostic priors, not learned evidence.
- **Search:** 0001's harness.
  - P 256, cap 524 288.
  - Lexicase on 64 cases, with an exact check on all 1 331 inputs.
  - Fresh seed block, the same seeds for every arm on a cell (paired).
- **Speed ratio X over Y on a cell:** 2^(mean over seeds of log₂ min(T_Y, cap) − log₂ min(T_X, cap)).
  - A family's ratio is the geometric mean over its retained cells.
  - 95% interval: bootstrap of seed indices within each cell, cells fixed. Each resampled
    seed index carries **all** its arms together, so the pairing is kept.

**Stage A: validation and screen** (about 15 min, ≤ 6 GB). Always runs.

**Stage B: search calibration on every retained D1331 cell** (13 predicted). Always runs.
- 8 arms: U, F4, G4, G4-marg, G4-BE, G4-PA, G4-BE-marg, G4-PA-marg.
- 50 paired seeds, run in balanced blocks of 10: 13 × 8 × 50 = 5 200 runs.
- **Provisional solve forecast** (explicitly a guess). It comes from 0001's ten-token PA/BE
  cells on this harness. There G solved 42–50/50 (medians 8k–42k), F 22–49/50, G-marg
  34–50/50 and U 8–48/50 (one hard BE cell at 8/50). For this run I expect:
  - G4 and the family grammars at ≥ 40/50 on most cells;
  - U at ≥ 30/50 on most cells, with one or two hard cells;
  - unknown rates on F-conditioned cells, which are new.
- **Cost:** 0001 measured 1.1 s (G) to 4.3 s (U) per run, including capped runs. Assuming
  about 3 s on branch cells gives about 4.3 CPU-h, or 25–50 min on 10 workers. Up to 2× is
  budgeted for the 24th token.
- **Checkpoint after the first balanced block (10 seeds)**, written to `checkpoint_b1.json`:
  - solves per cell × arm;
  - mean seconds per run, including capped runs;
  - projected time to finish stage B and, if gated in, stage C.

  If the projection overruns the internal deadline, stage B keeps running whole blocks and
  stage C is skipped for cost (row 3). Missing blocks are reported as incomplete, never treated
  as a negative result.

**Stage C: token-multiplier learner pilot.** It runs **only if all four gates pass**, and it does
not depend on the family-grammar contrast:
- (a) both families have a valid split;
- (b) headroom: F4, G4 and G4-marg each have a KM median ≥ 4 096 on at least 3 of the 4
  holdouts. This is 0001's frozen rule minus its "matched beats G" clause;
- (c) tractability: G4 solves ≥ 35/50 on every training cell, with a KM median ≤ 65 536 (the
  inner training cap);
- (d) cost: the time for stage C projected from stage B's measured G4 seconds per run fits
  before the internal deadline.

The probe predicts gate (a) fails, so stage C is not expected to run. If it does:
- **Learning:** 2 independent trajectories per family, starting from G4. Each learns
  24 multipliers with 0132's outer loop: (4 + 12), 25 generations, and 24 fresh 65k-cap
  searches per candidate spread over the family's training cells.
- **Scoring:** G4 and the 4 learned maps on fresh seeds, both families. That is 50 seeds per
  training cell and 100 per holdout.
- **Reported:** cost per trajectory; fresh-training gain over G4 for each trajectory; and
  ranking reproducibility (Spearman correlation between a parent's selection score and its
  re-score in the next generation).
- **Descriptive only:** matched/mismatched holdout scores. Two trajectories per family cannot
  test specificity.
- **Time:** 10–20 min per trajectory (0132's M took 9–11 min on 10 workers), plus about 20 min
  of scoring.

**Queue:** one entry, `timeout_seconds` 4 h, internal deadline 3 h 30 min. Expected wall time is
about 1–1.3 h if stage C is skipped and about 2.5 h if it runs.

## Outcome rules

Two independent readouts. **Table A** decides feasibility and the next step. **Table B** is
descriptive and gates nothing.

**A. Feasibility** (D1331; the first matching row decides):

| # | Condition | Meaning / next step |
|---|---|---|
| U | Validation fails, stage A is incomplete, any retained cell × arm in stage B has < 50 seeds, or stage C started but did not finish scoring | Unresolved. Report what finished; re-plan the missing part. Incomplete search is never a negative capacity or headroom result. |
| 1 | A family has no valid split (**probe prediction**) | Candidate rejected under the frozen split rule. Close 15 and return to strategy. **Report:** the obstacle table (role coverage per family and domain, near-alias witnesses); stage B's per-cell headroom, censoring and costs; Table B with intervals. **For the strategist to judge:** the asymmetric options (all BE cells as a training-only family against PA holdouts, or BE's single covered holdout `S?m:(M+F)`). **Not concluded:** anything about learned specificity or decoder capacity. |
| 2 | Both families split, gate (b) fails | No headroom over the fixed comparators on these holdouts. Return to strategy with the per-holdout medians. |
| 3 | Both families split, (b) passes, (c) or (d) fails | Pilot skipped. Report the training-cell cap and the cost slot 7 would need, from stage B's measured rates. Return to strategy. |
| 4 | Pilot ran; in **each** family at least one trajectory beats G4 on fresh training (95% lower bound > 1) | **Go** for slot 7, subject to strategy review. Freeze split, decoders and controls. Size slot 7 from the measured cost per trajectory and the training-gain spread (only two per family, so it is a rough guide). |
| 5 | Pilot ran; in some family neither trajectory has a resolved training gain | Learning on that family is not shown at this budget. A transfer test would compare maps that may not have learned anything. Return to strategy with cost and ranking reproducibility. |

**B. Family-grammar witness** (descriptive; read per family, so BE and PA are not pooled).
- **Ratio:** r_f = T(swapped grammar) / T(matched grammar) over family f's retained cells.
  - On BE cells this is G4-PA over G4-BE.
  - On PA cells this is G4-BE over G4-PA.
- **Capped run:** a run that hits the cap unsolved.

| Reading for family f | Condition | Meaning |
|---|---|---|
| W (witness) | Lower bound of r_f > 1 ("large" if the point estimate is ≥ 1.5) | A previous-token decoder can carry a family preference on f. If W holds in both families, both directions are shown. |
| C (cap-limited) | Not W, and > 25% of f's runs are capped in either grammar arm | Unresolved: censoring pulls the ratio toward 1. |
| B (bounded small) | Not W or C, and upper bound of r_f < 1.25 | These two hand-set priors carry no large contrast on f. Says nothing about other previous-token decoders or learned token weights. |
| X (unresolved) | Anything else | Broad interval; no reading. |

Reported alongside Table B:
- **The same four readings for the marginals pair** (G4-PA-marg vs G4-BE-marg). Suppose the
  grammars give W but the marginals do not. Then, for these priors, the contrast sits in
  context. That would inform whether slot 7 needs a contextual secondary arm next to the
  primary token learner. It is not a verdict on token-only learning: discovered-solution
  frequencies can differ even when canonical token counts are equal.
- **Matched grammar vs G4, per family, as a ratio with its interval.** This is descriptive
  only and is not a headroom test.

**Reported in every row:**
- per cell × arm: solves, KM median (95% bootstrap), solve curves at 4k/32k/131k/524k, and
  mean seconds per run including capped runs;
- the ratios G4/U, F4/U and G4/G4-marg;
- censoring per family.

Rows 1–3 and 5 reject or pause **this candidate** only, not root 10's question.

## Alternatives considered

- **Return to strategy now on the probe alone.** Cheaper, and the probe probably settles
  eligibility. But the strategist would get an unreviewed, Rust-free screen with no search or
  cost numbers. The asymmetric options it would weigh need exactly those numbers. I accept this
  path if the owner or critic prefers it.
- **Drop the family-grammar arms (4 of 8, about 40% of stage B, roughly 15–20 min).** Rejected.
  The plan asks for this diagnostic and no other run has measured it. As a positive witness it
  is cheap to read correctly.
- **Run an asymmetric design now** (BE as a training-only family, or one BE holdout). Rejected:
  it changes a frozen rule after seeing data, and the strategy reserves that choice for itself.
- **More independent PA learning starts, or root 01 mechanism work.** The strategy defers these.
  None of root 01's parked reopen conditions is met.

**Budget:** root 10 has 7 slots, 5 used, so 2 are left. This run uses question 15's single slot.
Slot 7 stays conditional on row 4 and on strategy review.
