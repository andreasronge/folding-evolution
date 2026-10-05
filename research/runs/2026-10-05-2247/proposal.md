---
node: questions/10-compositional-map-transfer/11-composition-bank
title: Composition bank, decoder harness and headroom feasibility, third attempt (root 10, experiment 1)
---
## Why this now

Runs [2026-10-05-2039](../2026-10-05-2039/proposal.md) and [2026-10-05-2242](../2026-10-05-2242/proposal.md)
proposed this study; the critic approved both with notes ([first](../2026-10-05-2039/critique.md),
[second](../2026-10-05-2242/critique.md)). Neither ran: the driver stopped at `prepare` both times
because merging `main` into `research/main` conflicted on `research/runs/2026-10-05-1957/code_review.md`
(add/add). Nothing was measured and no slot was charged. **That block is now removed:** merge
commit `823bc27` on `research/main` takes `main`'s version of the file (the later, second-pass
review). `main` is an ancestor of `research/main`, and the driver tests pass on it (38/38).

The question is unchanged. The [strategy](../2026-10-05-2039/strategy.md) asks root 10 first for a
tractable set of held-out operation combinations, measured search cost, and an affordable design
for experiment 2. This is the same study. The first critic's six notes are marked *N1–N6*; the
second critic's notes 3–5 are folded in and marked *C3–C5* (C1 and C2 needed no design change).

## Feasibility: what is measured and what is not

Read-only probes from the first proposal (`research/main` at `2a002a8`, arm A = whole tape is one
RPN program, alphabet v2_probe, domain = all 625 lists in {-2..2}^4). They are unreviewed and one
run each.
- ANY is 1 on 624/625 inputs, so every ANY cell has a constant twin (≥ 99.8% agreement). GT cells
  are ≥ 96.6% single-reducer thresholds, and `sum>any`/`max>any` *equal* `sum>1`/`max>1`. Both
  are excluded.
- X+Y, 2X+Y and `S>0 ? X : Y` over SUM (S), MAX (M) and MIN (m), as label vectors: the best
  program in a listed menu of simple comparators agrees with them on 14–69% of inputs. Selects conditioned on M or m agree 87–98% and are excluded.
- Uniform search (P 256, L 32, mutation 0.03, crossover 0.7, lexicase on 64 cases, exact check on
  625): `S+M` 6/6 solved at 5k–48k evaluations; `2M+S` 8/8 (median ≈ 21k); `S?S:M` 7/8 (median
  ≈ 10k); `S?M:S` 4/8 by 524k. A solved run takes 0.2–3 s, a capped run 5–15 s. 12 cores.
- Random sampling: two-reducer cells about 1–10 per million uniform tapes, about 0.65M tapes/s.

**Not measured:** every MIN cell (the op does not exist yet), seven-token sampling rates, the new
decoder's overhead, stage A enumeration throughput (and how much semantic deduplication saves),
and throughput with 8 concurrent workers. The probe agreements above came from a named menu of
simple comparators, not from all shorter programs; stage A is the exhaustive version.
Stage 0 measures these before anything else (*N1*). The old v2_probe numbers are runtime and
discovery estimates only, not correctness targets (*N5*).

## What would be run

**Build (researcher, in the worktree):**
1. Alphabet `v2_rmin` = v2_probe + `REDUCE_MIN` at id 22, in the pattern of `v2_min`/`v2_imax`.
   Python and Rust executors, with a differential test. REDUCE_MIN is a generic list reducer like
   SUM/MAX. It appears in training and held-out cells alike and encodes no withheld combination.
2. Latent-allele decoder for arm-A tapes: genotype = 32 alleles in [0, R) with R = 23 000. Each
   allele is decoded to one of 23 tokens through a cumulative table row. The row is selected by
   the previously emitted token (a start row at position 0). Tied rows give a frequency-only map;
   R is a multiple of 23, so tied-uniform is exactly uniform. Shared across arms: initialization
   (uniform alleles), per-allele resample mutation 0.03, single-point crossover on alleles.
   **Checks before any run** (*N5*): decoding is deterministic. On 10⁶ tied-uniform tokens, a χ²
   test against 1/23 per token. On 10⁵ decoded genotypes, executing the decoded tape gives
   output identical to the direct `v2_rmin` executor on the same token tape, on all 625 inputs.
   Every canonical program, at the end of a NOP-padded tape, solves its cell exactly.
3. Task grid: 3 reducer pairs ({S,M}, {S,m}, {M,m}) × 3 combiners. ADD = `X+Y` (5 tokens). DADD
   = `2X+Y` (7 tokens, `INPUT X DUP ADD INPUT Y ADD`). SEL = `S>0 ? X : Y` (7 tokens, IF_GT with
   SUM as the condition). SUM and REDUCE_ADD both count as S. Orientation for DADD and SEL: X
   is the reducer whose oriented cell has the lower best-simpler agreement in stage A. On a tie,
   X is the earlier of S, M, m (*N3*).

**Stage 0: calibration (≤ 15 min, gated in code; N1).** Measure stage A throughput on a 10⁶-program
slice. Measure decoded sampling throughput per arm with 8 workers. Run 2 capped U searches per
cell with 8 workers in parallel. Mean seconds per run counts unsolved runs at their capped time.
Project stages A–C, including decoder validation, G-marg construction, enumeration, sampling
and top-ups (C1). Search has priority over descriptive sampling: if the projection exceeds the
internal deadline, first cut sampling to 5·10⁷ per arm, then drop it. Stage B always runs in seed
blocks of 10 across all cells × arms, so a deadline hit leaves balanced partial data. G's table and the G-marg measurement
(below) are frozen and hashed before stage 0's searches.

**Stage A: bank screen (exhaustive, faithful to the executor; C3).** Enumerate every program of up
to 6 tokens over the executable `v2_rmin` tokens, with **no** pruning of underflowing or
type-mismatched prefixes: in this executor underflow supplies defaults (`DUP` on an empty stack
pushes two zeros) and mismatched ops still change the stack. Fixed bindings for every cell alike:
SLOT_12 and SLOT_13 bound to NOP, THRESHOLD_SLOT bound to one fixed constant (the plan states
which). The plan lists the exact enumerated token ids. Tokens may be left out only if they execute
as NOP (NOP, SEP_A, SEP_B, and the NOP-bound slots), shown by a test. The only pruning allowed is
exact *semantic deduplication*: two prefixes whose full typed stacks are identical on all 625
inputs behave identically under every suffix, so only the shortest representative is extended.
The plan tests this against brute-force enumeration up to length 4. Evaluate every distinct
program's output on all 625 inputs. A cell with canonical length L fails if (*N3*):
- a program shorter than L solves it exactly, or
- a program shorter than L agrees with it on ≥ 80% of inputs, or
- its label vector equals another cell's. Then both cells fail.

ADD (L = 5) is therefore screened only against programs of ≤ 4 tokens. Its own 5-token solvers do
not count against it. For each cell, also report the share of its canonical bigrams that appear
in other cells' canonical programs. This is descriptive and goes to experiment 2.

**Stage B: search and sampling on all cells that pass stage A.** Four map arms, all through the
decoder:
- **U:** tied rows, uniform.
- **F:** tied rows with a fixed relevant-token bias: INPUT, MAX, MIN, ADD, DUP and IF_GT at 3×;
  SUM and REDUCE_ADD at 1.5× each, so every reducer has equal mass; the rest 1×.
- **G:** untied, hand-set, task-agnostic grammar. After INPUT, mass goes to the reducers, equal
  per reducer. After an int-producing token, mass goes to INPUT/ADD/DUP/IF_GT, equal per token.
  The start row favours INPUT. No row may prefer a reducer pair or a cell. Every token keeps
  ≥ 0.25× uniform mass. The numeric table is written out and hashed before stage 0 (*N2*).
- **G-marg:** tied rows set to G's token marginals over all 32 positions, measured on 10⁷ tokens
  from 3·10⁵ uniform-allele genotypes. A check on 10⁷ G-marg tokens must match within 2%
  relative or 0.0005 absolute per token, whichever is larger. The measurement distribution is
  fixed before stage 0 (*N2*).

Each cell × arm runs 50 seeds. Seeds are paired across arms: the same 64 distinct training cases,
the same initial alleles and the same variation RNG stream. P 256, cap 524 288 evaluations
(2048 generations), elite 2, lexicase. Every training-perfect individual is checked on all 625
inputs; inexact ones are counted as shortcuts. That is ≤ 9 × 4 × 50 = 1800 runs, about 30–60 min
on 8 workers. Sampling draws 2·10⁸ decoded genotypes per arm, screens them on 48 inputs and checks
the hits exactly. A cell with no hits is reported as a 95% upper bound. Also recorded: G's
mutation cascade (emitted tokens changed per allele mutation) and decode overhead per generation.
G vs G-marg is read as the combined effect of context on supply *and* variation, not as a
mechanism (*N2*).

**Stage C: top-up (≤ 30 min, gated in code; N4).** Any cell whose U count is 30–39/50, training or
holdout candidate, gets 100 fresh U seeds. Any cell where the 95% bootstrap interval of the
G or F median contains 4 096 gets 100 fresh seeds of that arm. The pooled count then decides,
with no second band: 35/50 corresponds to ≥ 105/150. A top-up still unfinished at the deadline
makes that comparison unresolved.

**Medians (N4).** These are Kaplan–Meier medians with 95% bootstrap intervals. If a cell × arm
solves < 50%, its median is reported as "> 524 288". It enters split ranking as 524 288, and it
counts as ≥ 4 096 in the headroom rule.

**Headroom (C4).** A transversal *lacks headroom* if one fixed arm, F or G, has a median
< 4 096 evaluations (16 generations) on at least 2 of its 3 holdouts. The rule is per arm: F fast
on one holdout and G fast on another does not count. Headroom is reported for all six
transversals, with each arm's three holdout medians.

**Split rule (pre-stated, applied to stage B/C data; experiment 2 uses fresh seeds; N3).**
- *Retained* cells passed stage A. *Tractable* cells have U ≥ 35/50, or ≥ 105/150 pooled.
- A candidate holdout set is a transversal: 3 retained cells with distinct pairs and distinct
  combiners. The 3×3 grid has 6 transversals.
- Its training set is every retained, tractable cell not held out. Untractable non-holdout cells
  are dropped from training; they do not disqualify the split.
- A transversal is **eligible** if each of the following holds:
  - all 3 holdouts are tractable;
  - the training set has ≥ 4 cells;
  - training covers all three reducers and all three combiners;
  - each holdout's pair and its combiner each appear in ≥ 1 training cell.

  This needs at least 7 retained cells. 7-, 8- and 9-cell banks are all allowed.
- Among eligible transversals **with headroom**, pick the largest geometric mean of U medians
  over the holdouts (most room). Ties go to more training cells, then to the lowest sorted cell
  ids. A failure of the U-hardest split under F or G therefore does not end the study while
  another eligible split keeps headroom (C4).
- The pooled tractability count is an operational selection rule, not evidence that the true
  solve probability exceeds 70%. Intervals are reported, and experiment 2 uses fresh seeds (C5).

**Queue:** one entry, timeout 3 h, internal deadline 2 h 40 min with an output reserve. Expected
1.5–2.5 h.

## Measured outputs

- Per cell × arm: solve fraction by the cap, KM median with a 95% bootstrap interval, P(solve ≤ B)
  for B ∈ {32k, 65k, 131k}, mean seconds per run (censored runs included), shortcut counts, and
  the sampling rate or its 95% upper bound.
- Per cell and per candidate inner budget B ∈ {32k, 65k, 131k}: SD under U of the capped
  objective log₂ min(T, B), where T is the evaluations to solve and every run counts (C4). From
  this, the inner seeds needed per decoder: k = ⌈(2·SD_B)²⌉ at the chosen B, so the standard
  error of a decoder's mean capped log₂ cost is ≤ 0.5. A 2× faster decoder is then 2 SE apart.
- **Projected experiment-2 cost (N6).** Inner budget B = the smallest of {32k, 65k, 131k} at which
  U solves *every* training cell in ≥ 50% of runs. The adaptation cost is 8 trajectories × outer
  population 16 × training cells × k × 40 outer generations × measured seconds per run at B. That
  figure includes censored runs and decoder overhead. If no B in the set has U solving every
  training cell in ≥ 50% of runs, the bank has **no feasible inner budget in the tested set**,
  and no cost is computed (row 4a). Add the transfer test: 5 learned decoders, each with its own
  marginal-matched control (the root plan requires these; C4), plus U, F, fitted frequency, G,
  G-marg and mismatched-family training, × holdouts × 50 fresh seeds. The adaptation run for the
  mismatched-family control is also included. Report the total CPU-hours, the total wall-hours on
  8 workers, and the largest single queue. Splitting into queues does not reduce the total.
- Descriptive, not gates: F/U, G/U and G/G-marg speed ratios per cell with paired-bootstrap 95%
  intervals, each against its sampling-rate ratio. A null G/G-marg leaves learned transfer
  untested (*N6*).

## Outcome rules

Applied in order; the first match decides. Incomplete data is checked first (*N4*).

| # | Condition | Meaning / next step |
|---|---|---|
| U | Stage A did not complete, or stage B did not finish ≥ 50 seeds for every retained cell × arm by the deadline, or a stage C top-up was still unfinished | **Unresolved.** Report what was measured. The steward re-plans the missing cells; this is not a negative result. |
| 1 | Fewer than 7 retained cells, or no transversal meets the eligibility rules when tractability is ignored | The bank fails the alias screens. Park 11 and return to strategy with the failing cells and a revised bank: three-part sums (`S+M+m`), or v2_split's half-list reducers (no new op). |
| 2 | No transversal is eligible once tractability is applied (after top-up) | Too hard for this harness at 524k. Return to strategy with per-cell solve curves. Note whether F or G make the cells tractable; that is itself a map-bias result. |
| 3 | Eligible transversals exist, but every one lacks headroom as defined above (after top-up) | No headroom: a fixed bias or generic grammar nearly solves the holdouts. Return to strategy proposing a deeper tier (three-reducer and nested cells) before experiment 2. |
| 4a | A split with headroom exists, but no inner budget in {32k, 65k, 131k} has U solving every training cell in ≥ 50% of runs | No feasible inner budget in the tested set. Return to strategy with the per-cell solve curves and the cost at 262k and 524k; not a Go. |
| 4 | Eligible with headroom, but the projected total for experiment 2 > 8 h even with 6 trajectories at the inner budget B defined above | Feasible but costly. Propose experiment 2 as a staged allocation (adaptation queue, then transfer queue), with the total cost stated. |
| 5 | Eligible, with headroom, and projected total ≤ 8 h | **Go.** Freeze the split, the inner harness and the U/F/G/G-marg controls. The next proposal is experiment 2 (adapt and transfer) on fresh seeds, with a mismatched-family training control. |

Every row logs the per-arm descriptive numbers to 11 and to root 10.

**What each kind of result can and cannot teach (C5).** An incomplete stage A cannot show that a
cell has no alias. Incomplete searches or top-ups cannot settle the chosen split. Sparse samples
of seven-token cells may give only wide upper bounds. A null G/G-marg comparison does not test
learned transfer. By contrast, a completed row 1 or 2 is a concrete limitation of this candidate
bank, and row 3 is a concrete limitation of these task types. None of these is a negative answer
to root 10, and none justifies enlarging this feasibility run by default.

## Alternatives considered

- **The plan's SUM/MAX/ANY bank with ADD/GT.** Rejected: probes show ANY is a near-constant and GT
  is ≥ 96% thresholds. Holdouts would differ from training by a constant, which the plan forbids.
- **v2_split's SUM_LEFT2/SUM_RIGHT2 instead of a new MIN.** These add no op, but they read the
  input directly, and `L2+R2 ≡ SUM` is an alias. Kept as the row-1 fallback.
- **Build the outer adaptation loop now.** Premature: its inner budget, seed count and cost all
  come from stage B.
- **Drop G and G-marg (U and F only).** Saves about 30 min, but then row 3 cannot be checked
  against generic syntax.
- **Return to strategy because the cycle was blocked twice.** No: the block was operational and
  is now removed, the critic's notes are all addressable, and no other open question has a
  reopen condition met (re-checked: 02, 04, 07, 08, 09).

Budget: root 10 has 4 slots, 0 used; 11 has 1, 0 used (neither blocked run was charged). This
uses 11's slot.
