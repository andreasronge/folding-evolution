---
node: questions/10-compositional-map-transfer/15-four-reducer-family-bank
title: Four-reducer bank (FIRST added) — reviewed alias/split screen, 13-cell search calibration under G4, family-grammar capacity diagnostic, gated learner cost pilot (root 10, slot 6 of 7)
---
## Why this now

The [strategy](strategy.md) gives root 10's slot 6 to the feasibility study in the
[four-reducer plan](../../plans/four-reducer-family-transfer.md). The question is whether adding
FIRST to SUM/MAX/MIN gives two families, branch-else (BE `A?B:(C+D)`) and post-addition
(PA `(A?B:C)+D`), each with a usable split, headroom over a fixed grammar, and an affordable
learning comparison. I follow it, but **my read-only probe says the frozen split rule will
probably fail for BE.** So this proposal is built to be worth running even if that happens. It
also runs the **family-grammar capacity check** that run 0001 planned but never reached
(its stage C was gated on a pair). That check asks whether a previous-token decoder can use a
BE/PA difference at all. Slot 7 depends on the answer however the split turns out. A
learned map cannot show family specificity in a decoder class where even hand-set family rows
show no difference.

## Probe (this cycle; unreviewed; [`steward_probes/`](steward_probes/))

`probe.py` extends `composition_bank.SemanticMachine` (research/main @ `b397f72`) with FIRST as
token 23 (first element; empty or wrong-type list → 0, like the other reducers). It enumerates
all 19 executable tokens with exact typed-state dedup: depth 8 stored, depth 9 output-only, as
in run 0001. Canonicals were checked on the semantic machine only; Rust has no FIRST yet.
To rerun it, check out research/main at `/tmp/fr4` and run `python probe.py D1331 9 oo`.

| | D625 | D1331 | D2401 |
|---|---|---|---|
| cost (depth 8 + 9 output-only) | 117 s, 4.0 GB | 114 s, 5.1 GB | 122 s, 4.5 GB |
| depth-8 states | 14.0 M | 14.2 M | 14.1 M |
| retained / 36 (≥ 80% rule, no exact duplicates) | 10 (BE 4, PA 6) | **13 (BE 5, PA 8)** | 13 (BE 5, PA 8) |
| role-covered holdout pairs, BE / PA | 0 / – | **0 / 9** | 0 / – |

- Every cell conditioned on M or m dies by depth 6 (M>0 holds on 84% of D1331 and m>0 on 9%, so
  one branch is a near-alias). Twelve cells are left (6 BE, 12 PA). Depth 9 removes 5 more,
  at 0.84–0.86; the closest survivors are at 0.77.
- D1331 BE survivors: `S?m:(M+F)`, `S?M:(m+F)`, `S?F:(M+m)`, `F?S:(M+m)`, `F?m:(S+M)`.
  `then` = S, F and M each occur in only one cell, so no pair can be held out with every
  (role, reducer) still in training (0001's rule; I even treat the two summands as one unordered
  role, which is more lenient). The missing sixth cell, `F?M:(S+m)`, is a 0.857 near-alias.
- Cross-family agreement is low: each BE cell's closest PA cell agrees on 0.41–0.60 of inputs.
  Within PA the closest pair is at 0.72.

These are one-pass probe numbers, not results. The reviewed screen below is what counts.

## What would be run (one queue entry, staged and gated in code)

**Frozen now (before any search):**
- **Alphabet `v2_rmin_first`** = `v2_rmin` plus FIRST at id 23, in Python and Rust. Before
  anything else: the semantic machine must match brute-force Python execution to depth 4; Python
  and Rust must agree on 10⁵ random 32-token programs; all 36 canonicals, NOP-padded, must
  reproduce their labels in Rust.
- **Roster:** the 36 cells above (BE 12 = ordered A, B with unordered {C, D}; PA 24), with
  canonicals `push(C) push(D) ADD push(B) push(A) IF_GT` and `push(C) push(B) push(A) IF_GT push(D) ADD`.
- **Retention:** 0001's rule unchanged. A cell is dropped if any program of ≤ 9 tokens agrees on
  ≥ 80% of inputs, or if its labels equal another cell's. **Domain D1331** is the plan's domain
  and is the only one selectable. D625 and D2401 are screened and reported (≈ 4 min) so the
  strategist sees that the obstacle does not depend on the domain.
- **Split rule:** 0001's rule unchanged, per family. Each family needs ≥ 4 retained cells and a
  holdout pair such that every (role, reducer) in it also occurs in that family's remaining
  cells. Roles are BE {cond, then, sum} and PA {cond, then, else, summand}. The holdout pair is
  the lexicographically first valid one. No training cell may have the same labels as any holdout.
- **Decoders** (R = 24 000 alleles, so U stays 1 000 per token; 24 tokens; 25 rows including start):
  - U: uniform.
  - F4: F's weights plus FIRST = 3, the same as MAX and MIN.
  - G4: G's rules with FIRST as a fourth reducer, floor 500.
    - Start row: INPUT 12 500.
    - After INPUT: the four reducer functions get 3 625 each; SUM's share is split 1 813 / 1 812
      with REDUCE_ADD.
    - After every integer-producing token (G's list plus FIRST): INPUT, ADD, DUP and IF_GT get
      3 500 each.
    - Other rows uniform.
    - Boosted mass is 60.4% (after INPUT) and 58.3% (after integers) of each row, against G's
      58.7%. Every row sums to 24 000.
  - G4-marg: G4's tied marginals, measured as in 2247.
  - **Family grammars** (diagnostic priors, not learned evidence): G4 with only the rows after
    ADD and after IF_GT replaced, floor 500. These are 0001's stage-C rules.
    - G4-BE: after ADD, INPUT 12 500; after IF_GT, DUP 12 500.
    - G4-PA: after IF_GT, INPUT 6 500 and ADD 6 500; after ADD, DUP 12 500.
    - G4-BE-marg and G4-PA-marg: their tied marginals.
- **Search:** 0001's harness. P 256, cap 524 288, lexicase on 64 cases with an exact check on
  all 1 331 inputs, 50 paired seeds per cell × arm, fresh seed block.
- **Speed ratio:** for arm X over arm Y on a cell, 2^(mean over seeds of log₂ min(T_Y, cap) −
  log₂ min(T_X, cap)). A family's value is the geometric mean over its retained cells. 95%
  intervals come from bootstrapping seeds within cells, with cells fixed (0001's paired
  capped-time method).

**Stage A — validation and screen (≈ 15 min, ≤ 6 GB).** It always runs.

**Stage B — search calibration on all retained D1331 cells (predicted 13).** It always runs.
- Eight arms: U, F4, G4, G4-marg, G4-BE, G4-PA and the two family marginals.
- Size: 13 × 8 × 50 = 5 200 runs.
- Cost: 0001 measured 1.1 s (G) to 4.3 s (U) per run, including capped runs, on ten-token cells.
  That gives ≈ 4–6 CPU-h, or 30–60 min on 10 workers. A 24th token may slow search, so
  budget up to 2×.
- Seeds run in balanced blocks of 10, so if the deadline hits, the data is still usable.

**Stage C — learner cost pilot.** It runs only if both families split, the capacity rule passes,
G4 has headroom (row 4 conditions), and G4's KM median is ≤ 65 536 on every training cell.
Prediction: it will not run.
- Two independent token-multiplier trajectories per family, starting from G4: 24 multipliers,
  0132's outer loop ((4 + 12), 25 generations, 24 fresh 65k-cap searches per candidate spread
  over the family's training cells).
- Scoring: G4 and the four maps on fresh seeds, 50 per training cell and 100 per holdout, both
  families.
- Purpose: cost per trajectory, training gain over G4, and how well a candidate's selection score
  predicts its re-score in the next generation (a ranking-reproducibility check, as the strategy
  asks). Matched/mismatched transfer is reported only descriptively, at two trajectories per family.
- Time: ≈ 10–20 min per trajectory (0132's M: 9–11 min on 10 workers), plus ≈ 30 min of scoring.

**Queue:** one entry, timeout 4 h, internal deadline 3 h 30 min. Expected wall time is about
1–1.5 h if stage C is skipped and about 3 h if it runs.

## Outcome rules (first match decides; D1331)

"Usable contrast" means: in **both** families, matched family grammar is faster than swapped
(swapped/matched geometric mean ≥ 1.5×), with a 95% lower bound > 1. "Not usable" means
anything else, **including a broad interval**: the rows decide on what is resolved.

| # | Condition | Meaning / next step |
|---|---|---|
| U | Stage A incomplete, or stage B < 50 seeds on any cell × arm, or a validation check fails | Unresolved; fix and re-plan the missing part. |
| 1 | A family has no valid split, **and** contrast not usable | **Probe prediction for the split.** Candidate rejected under the frozen split rule. The hand-set rows also show no resolved family contrast on these cells (with its interval), so a learned map could not be expected to show family specificity in this decoder class here. Close 15 and return to strategy with the obstacle table. |
| 2 | A family has no valid split, contrast usable | Candidate rejected on the split rule alone. This decoder class can carry a BE/PA difference. Return to strategy with the measured costs and with what the asymmetric options would hold: all 5 BE cells as a training-only family against PA holdouts, or BE's single role-covered holdout `S?m:(M+F)`. Only strategy may approve such a design. |
| 3 | Both split, contrast not usable | Split exists but no hand-set family contrast is resolved. Return to strategy; a matched/mismatched test with this decoder is unlikely to separate. |
| 4 | Both split, usable, but no room above G4: the matched family grammar is not faster than G4 (G4/matched lower bound ≤ 1) in both families, or F4, G4 or G4-marg has median < 4 096 on ≥ 2 of the 4 holdouts | No headroom; return to strategy. |
| 5 | Rows 1–4 do not apply | **Go** for slot 7. Freeze split, decoders and controls; size slot 7 from stage C's cost and between-trajectory spread. If stage C was skipped by its G4 ≤ 65 536 condition, report the cap that slot 7 would need. |

Every row reports the following. Per cell × arm: solves, KM median (95% bootstrap), and mean
seconds per run including capped runs. Ratios: G4/U, F4/U and G4/G4-marg. Family contrast both
from the grammars and from their marginals. The last one matters for slot 7's primary learner:
if the contrast disappears in the marginals, it lives in context, and a token-only learner can
hardly carry it with identical canonical token counts. Rows 1–4 reject this candidate only;
they are not a negative answer to root 10.

## Alternatives considered

- **Return to strategy now, without a run.** The probe nearly justifies this. But the
  strategist would get an unreviewed, Rust-free screen and nothing on search. The capacity
  question, never measured, decides whether *any* two-family test with a previous-token decoder
  is worth a slot. If the critic judges the probe enough, I accept going straight to strategy.
- **Relax role coverage, or hold out one BE cell.** Rejected as the selection rule: it would
  change a frozen rule after seeing the data. The asymmetric options are reported in row 2 for
  the strategist to judge.
- **Pick another domain.** Not needed: the probe shows BE has 0 role-covered pairs on all three
  domains. The strategy also rules out a domain sweep.
- **More PA learning starts / a better outer objective, or root 01 mechanism work.** Deferred
  by the strategy; none of root 01's parked reopen conditions is met.

**Budget:** root 10 has 7 slots with 5 used, so 2 left. This run uses sub-question 15's single
slot. Slot 7 stays conditional on row 5 and on strategy review.
