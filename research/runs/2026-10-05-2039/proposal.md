---
node: questions/10-compositional-map-transfer/11-composition-bank
title: Composition bank, decoder harness and headroom feasibility (root 10, experiment 1)
---
## Why this now

The [strategy](strategy.md) asks for root 10's first experiment: a tractable set of held-out
operation combinations, measured search cost, and an affordable next-stage design. I follow it.
My probes show the [plan's](../../plans/compositional-map-transfer.md) example bank does not
survive its own alias rule, so this experiment uses a revised bank. Without it, experiment 2
would be testing threshold transfer again.

Probes (read-only, `research/main` code at `2a002a8`, executor arm A = whole tape is one RPN
program, alphabet v2_probe, domain = all 625 lists in {-2..2}^4):

- **ANY is nearly constant:** it is 1 on 624/625 inputs. `max+any` agrees with `max+1` on
  99.8% of inputs, and every ANY task has such a twin.
- **GT comparisons are threshold tasks in disguise.** `sum>max` matches `sum>2` on 98.4% of
  inputs, `sum>min` matches `sum>-2` on 96.6%, and `sum>any`/`max>any` *equal* `sum>1`/`max>1`
  (exhaustive search over programs up to 5 tokens finds 4-token solvers). Selecting holdouts
  from these tasks would bring back root 01's threshold family.
- **Integer-valued compositions are clean.** For X+Y, 2X+Y and `S>0 ? X : Y` (IF_GT with SUM as
  the condition) over reducers SUM (S), MAX (M) and MIN (m), the best simpler program
  (one reducer, 2×reducer, reducer+constant, a two-reducer sum, a constant) agrees on 14–69% of
  inputs. Selects conditioned on M or m are not clean (87–98%) and are excluded.
- **Search cost (uniform, P 256, L 32, mutation 0.03, crossover 0.7, lexicase on 64 cases,
  exact check on all 625):** `S+M` solved 6/6 at 5k–48k evaluations; `2M+S` solved 8/8
  (median ≈ 21k); `S?S:M` solved 7/8 (median ≈ 10k); `S?M:S` solved 4/8 by 524k (20k–113k).
  A solved run takes 0.2–3 s; a capped 524k run 5–15 s, single process. The machine has 12 cores.
- **Random sampling (uniform, L 32):** two-reducer cells about 1–10 per million tapes at
  about 0.65M tapes/s (Rust batch executor). Seven-token cells were not sampled.

The executor has no MIN reducer, so this needs one new primitive: `REDUCE_MIN`, a generic list
reducer in the same family as SUM/MAX. It appears in training and held-out cells alike and
encodes no withheld combination. The MIN cells are therefore unmeasured. Their cost is
estimated from the MAX cells, and measuring it is part of this experiment.

## What would be run

**Build (researcher, in the worktree):**
1. Alphabet `v2_rmin` = v2_probe + `REDUCE_MIN` at id 22 (pattern of `v2_min`/`v2_imax`), in
   Python and Rust executors, with a differential test.
2. A latent-allele decoder for arm A tapes: genotype = 32 alleles; each allele is decoded to
   one of the 23 tokens through a categorical table row. The row is selected by the
   previously emitted token (a start row for position 0). Tied rows give a frequency-only map.
   Use one allele range for every arm, chosen so the uniform tied map is exactly uniform.
   Every arm uses the same initialization, per-allele mutation (resample, 0.03) and
   single-point crossover on alleles. Checks before any run: decode is deterministic. The
   tied-uniform map reproduces direct arm-A token frequencies (χ² on 10⁶ tokens) and the
   `S+M` sampling rate within its interval. Every canonical program, placed at the end of a
   NOP-padded tape, solves its cell exactly.
3. The task grid: 3 reducer pairs ({S,M}, {S,m}, {M,m}) × 3 combiners (ADD `X+Y`, 5 tokens;
   DADD `2X+Y`, 7 tokens, `INPUT X DUP ADD INPUT Y ADD`; SEL `S>0 ? X : Y`, 7 tokens). That is
   9 cells. For DADD and SEL, a pre-stated rule fixes the orientation (which reducer is X):
   take the one with the lower best-simpler agreement in the stage A screen. SUM and REDUCE_ADD
   are both allowed for S.

**Stage A: bank screen (exhaustive, about 5 min).** Enumerate every program of up to 6 tokens
over the 15 non-inert tokens and compare it on all 625 inputs. A cell fails if a program
shorter than its canonical length solves it exactly, or agrees with it on ≥ 80% of inputs.
It also fails if its label vector equals another cell's. For each candidate holdout, also
report the share of its canonical bigrams that appear in training cells' canonical programs
(descriptive). This tells experiment 2 whether a previous-token decoder could carry the
needed structure.

**Stage B: search and sampling on all passing cells (about 45–70 min with 8 workers).** Four
map arms, all through the decoder:
- **U:** tied rows, uniform.
- **F:** tied rows, a fixed relevant-token bias: INPUT, MAX, MIN, ADD, DUP, IF_GT at 3× weight,
  SUM and REDUCE_ADD at 1.5× each (so every reducer has equal mass), others 1×.
- **G:** untied, hand-set, task-agnostic grammar. After INPUT, mass goes to reducers, equal per
  reducer. After an int-producing token, mass goes to INPUT/ADD/DUP/IF_GT, equal per token.
  Start row favours INPUT. No row may prefer a reducer pair or a cell. Every token keeps
  ≥ 0.25× uniform mass. Frozen and hashed before stage B.
- **G-marg:** G's context removed: tied rows set to G's *measured* emitted token marginals,
  checked to within 1% per token.

Each cell × arm runs 50 seeds. Seeds are paired across arms: the same 64 distinct training
cases and the same initial latent alleles and variation RNG stream. P 256, cap 524,288
evaluations (2048 generations), elite 2, lexicase. Every training-perfect individual is
checked exactly on all 625 inputs; inexact ones are counted as shortcuts. That is
9 × 4 × 50 = 1800 runs, about 6–15 s mean, so 30–60 min on 8 workers. Sampling uses 2·10⁸
decoded genotypes per arm with a 48-input screen, then an exact check, about 5 min per arm.
Also recorded: G's mutation cascade (emitted tokens changed per allele mutation), and decode
overhead per generation.

**Stage C: top-up, gated in code (≤ 30 min).** If a decisive comparison below straddles its cut,
run 100 more fresh seeds of the relevant cell(s) and arm(s), then decide on the pooled data.
Decisive comparisons: a holdout's U solve count is in 30–39/50, or the 95% bootstrap interval
of G's holdout median contains 4,096.

**Split rule (pre-stated, applied to stage B data; experiment 2 uses fresh seeds).** Hold out a
transversal: 3 cells, one per pair and one per combiner. Each held-out cell's pair and
combiner are then each seen twice in training. A transversal is eligible if all its cells
passed stage A, every cell in the grid has U solve ≥ 35/50 (training cells must be tractable
for adaptation), and each holdout has U solve ≥ 35/50. Among eligible transversals, choose the
one with the largest geometric mean of U median evaluations over its holdouts (most room).
If a failed cell leaves fewer than 6 grid cells, use the transversal that keeps ≥ 4 training
cells covering every reducer and combiner.

**Queue:** one entry, timeout 3 h, internal deadline 2 h 40 min with output reserve. Expected
1.5–2 h.

## Measured outputs

These are the numbers experiment 2's design needs:
- Per cell × arm: solve fraction by cap, Kaplan–Meier median evaluations with a 95% bootstrap
  interval, P(solve ≤ B) for B ∈ {32k, 65k, 131k}, mean seconds per run, shortcut counts.
- Per cell × arm: sampling rate (or a 95% upper bound when there are no hits).
- Per cell: the spread of log evaluations across seeds under U. This gives how many inner seeds
  per decoder are needed to tell a 2× faster decoder apart in an outer loop.
- **Projected experiment-2 cost:** 8 independent adaptation trajectories × outer population 16 ×
  training cells × inner seeds (from the spread) × 40 outer generations at the inner budget B
  where U solves training cells ≥ 50%. Add the transfer test (5 learned decoders + controls ×
  holdouts × 50 fresh seeds), all from measured seconds per run.
- Descriptive, not gates: speed ratios F/U, G/U and G/G-marg per cell with paired-bootstrap
  95% intervals, and each against its sampling-rate ratio. G vs G-marg is a first read on
  whether *context* adds anything beyond token marginals on this bank, the crux of
  explanation A vs B. A null here does not rule out a learned decoder.

## Outcome rules

Applied in order; the first that matches decides.

| # | Condition | Meaning / next step |
|---|---|---|
| 1 | No split meets the stage A requirements (3 holdouts, ≥ 4 training cells covering every reducer and combiner) | Bank fails the alias screens. Park 11 and return to strategy with the failing cells and a revised bank: three-part sums (`S+M+m`), or v2_split's half-list reducers (no new op). |
| 2 | Screen passes, but no transversal is eligible on U tractability (after top-up) | Too hard for this harness at 524k. Return to strategy with the per-cell solve curves. Note whether F or G make the cells tractable; that would itself be a map-bias result. |
| 3 | Chosen split eligible, but G's median on ≥ 2 of 3 holdouts is < 4,096 evaluations (16 generations), after top-up | No headroom: generic grammar nearly solves the holdouts, so experiment 2 could not separate learned family structure from syntax. Return to strategy proposing a deeper tier (three-reducer and nested cells) before experiment 2. |
| 4 | Eligible with headroom, but projected experiment-2 cost > 8 h even with 6 trajectories and inner budget 32k | Feasible but costly. Propose experiment 2 as a staged allocation (adaptation queue, then transfer queue), with the measured numbers. |
| 5 | Eligible, headroom, and projected cost ≤ 8 h | **Go.** Freeze the split, the inner harness and the U/F/G/G-marg controls. The next proposal is experiment 2 (adapt and transfer) on fresh seeds, plus a different-family training control. |
| U | The run hits its deadline before stage B completes on every cell, or a stage C top-up still leaves a decisive count inside its band | **Unresolved.** Report what was measured. The steward re-plans the missing cells; that is not a negative result. |

In every row, the per-arm descriptive numbers are logged to 11 and the root.

## Alternatives considered

- **The plan's SUM/MAX/ANY with ADD/GT bank, unchanged.** Rejected: ANY is nearly constant and GT
  cells are ≥ 96% thresholds (probes above), so holdouts would differ from training by a
  constant, which the plan itself forbids.
- **v2_split's SUM_LEFT2/SUM_RIGHT2 instead of a new MIN.** No new op, but the arity differs
  (they read the input directly) and `L2+R2 ≡ SUM` is an alias. Kept as the row-1 fallback.
- **TAG harness instead of a straight stack tape.** The plan prefers the stack tape, to keep
  shared-helper establishment out. The TAG baselines would not transfer anyway.
- **Build the outer adaptation loop now.** Premature: its inner budget, seeds per decoder and
  cost all come from stage B. A broken bank would waste that code.
- **No G/G-marg arms (U and F only, as the plan's experiment 1 lists).** Cheaper by about 30 min.
  But without G, row 3 cannot be checked, and experiment 2 could spend its queue on a bank where
  syntax alone wins. I think the 30 min are worth it.

Budget: root 10 has 4 slots, 0 used; this uses 1 (sub-question 11, budget 1).
