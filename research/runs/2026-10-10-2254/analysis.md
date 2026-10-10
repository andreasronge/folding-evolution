---
outcome: "PASS partial, bounded geometric difference (DG Q 0.96 [0.68, 1.35] inside the margin, lower bound 0.013 above 0.67; penalty-sensitive, 1×cap unresolved 0.79 [0.58, 1.06]; positive arithmetic DG savings, repayment ~146 searches/build; TS descriptive: tree GP 5.7× cheaper, Q 0.175 [0.142, 0.217])"
---

# Analysis: frozen A8 versus family-blind subtree GP on the DG and TS rosters (2254)

Reviewer analysis of the queue in [execution.md](execution.md) (commit `c32ff04`,
all three entries exit 0). Raw data:
`experiments/output/2026-10-10/2026-10-10-2254-{prepare,dg,ts}/`. Written
before opening plan.md; the section "Against the predictions" was added after.

## 1. Data completeness

**Preparation (`-prepare`, 555 s of 1 800 s timeout).**

- Seed audit admitted: 256 calibration rows and 1 792 scoring rows scheduled,
  zero overlaps of any kind (calibration/scoring, smoke, historical 1 544
  saved seeds, tail diagnostics); intended pairing valid.
- 16 native A8 replays: all 16 match the saved records on every
  non-timing field.
- Validation: 1 998 Python/Rust interpreter checks, 16 fixtures, initializer
  bins 43/43/43/43/42/42 all passed.
- Calibration: 128 DG rows + 128 TS rows, 8 source/development cells per
  family × 8 repeats × 2 mixes; no overlap with the 8 target cells per family
  (checked by cell id). Mix 0.5 chosen for both families by lower geometric
  2×cap cost (DG: 0.5 solved 33/64, 0.9 solved 23/64; TS: 0.5 solved 64/64,
  0.9 solved 63/64).
- Timing admission: DG projected 2 907 s against 5 760 s limit, TS 1 466 s
  against 4 320 s; both admitted. The DG <25% solve stop did not fire
  (calibration solve fraction 51.6%).

**Scoring (`-dg` 1 955 s, `-ts` 386 s).** Each family's `search.jsonl` has
exactly 896 rows: 384 A8, 384 tree, 128 G4, 8 cells, no duplicate
(cell, arm, build, repeat) keys, 512 unique seeds of which 384 are shared
exactly once between the A8 and tree row of the same (cell, build, repeat)
and 128 are G4-only. Zero pairing mismatches. All rows carry cap 524 288 and
population 256; all tree rows use the frozen mix 0.5. The runner's
`validate_rows` re-verified every claimed solver on all 625 inputs (D625) and
re-interpreted every tree solver independently, so "solved" below means
exact on D625, not training-set-perfect. No error rows, no crashes, no
retries. The TS stage validated the DG result hash before scoring.

I recomputed the DG and TS Q points and the 1×cap points from the raw rows
and they match `result.json` to all printed digits (DG 0.96094, 0.78505; TS
0.17530, 0.17850).

**Budget use.** Summed wall 2 896 s of 14 400 s timeouts. The run is
complete; nothing is missing.

## 2. Key numbers

Cost is evaluations; failures count 2 × cap = 1 048 576 in the primary Q,
1 × cap in the sensitivity. Q = tree ÷ A8, so Q < 1 means tree GP is cheaper.
Intervals are the plan's 8 192-draw paired block bootstrap over 24 build
blocks (both repeats resampled jointly within block × cell), reproduced here.

### 2.1 Primary comparison (DG roster)

| Quantity | Value |
|---|---|
| Q, 2×cap penalty (primary) | **0.961 [0.683, 1.352]** |
| Q, 1×cap penalty (sensitivity) | 0.785 [0.583, 1.055] |
| Runner's classification | within_margin (primary); unresolved (1×cap); `penalty_sensitive: true` |
| A8 solved | 314/384 (81.8%) |
| Tree solved | 202/384 (52.6%) |
| G4 solved | 19/128 (14.8%) |
| Geometric 2×cap cost: A8 / tree / G4 | 92 009 / 88 415 / 840 165 |
| Tree ÷ G4 (descriptive) | 0.105 [0.075, 0.147] |
| Block log-ratio SD | 0.733 |

The primary interval's lower end, 0.683, sits 0.013 above the 0.67
boundary. The classification "within margin" is therefore a near-miss of
"unresolved", and the pre-registered 1×cap sensitivity *is* unresolved (its
upper end 1.055 excludes neither tree-better nor no-difference). The point
estimates move from 0.96 to 0.79 just by changing the failure penalty, which
is the runner's own `penalty_sensitive` flag.

### 2.2 Why the DG ratio sits near 1 despite very different solve rates

The two arms fail and succeed in different ways, and Q averages across them:

| Paired outcome (A8 solved, tree solved) | n of 384 |
|---|---:|
| both solved | 165 |
| A8 only | 149 |
| tree only | 37 |
| neither | 33 |

- **When tree GP solves, it is much faster.** Median evaluations to solve:
  tree 6 784 (q25–q75 3 904–16 192) versus A8 57 088 (22 848–145 088).
  Within the 165 pairs both solved, tree was faster in 134/165, median
  tree/A8 ratio 0.18.
- **Tree GP fails nearly half the time; A8 fails 18%.** Solved within 4 096
  evaluations: tree 58/384, A8 7/384. Within 65 536: tree 179, A8 174. At cap:
  tree 202, A8 314. The tree arm's cumulative solve curve flattens after
  about 2^16 evaluations; A8's keeps climbing to the cap.
- So the geometric cost is a wash (fast tree solves offset by tree failures
  at 2×cap) while the arithmetic cost favours A8 (DG arithmetic mean actual
  evaluations: tree 263 353 versus A8 177 639, because failed searches spend
  the full cap).

### 2.3 How the tree arm fails on DG (descriptive)

Among the 182 failed tree searches:

| Failure signature | n of 182 |
|---|---:|
| never reached a training-perfect individual (best training score 60–63 of 64) | 92 |
| reached training-perfect individuals, all of which were D625 shortcuts | 90 |

- Failed searches hit the 32-token size ceiling: median 48% of all evaluated
  individuals in a failed search were exactly 32 tokens (q25–q75 0.43–0.53),
  versus 9% in solved searches. Mean compiled length at the end: 28.3 (failed)
  vs 26.0 (solved). Operator rejection (oversize child reverts to parent 1,
  i.e. a clone): crossover 35% and mutation 42% rejected in failed searches,
  20% and 27% in solved ones. The DG dynamics plot in the output folder
  shows this as the token-length histogram spike at 32.
- Final phenotype diversity (distinct output vectors on the 64 training
  cases) is lower in failed tree searches (median 86) than in solved ones
  (118); A8 sits around 87–92 whether or not it solves.
- These are descriptions of the frozen tree procedure; they do not say what
  a larger token limit or a size-aware operator would do, and the plan
  forbids tuning.

### 2.4 Per-cell DG Q (descriptive, 48 paired searches per cell)

| Cell | A8 solved/48 | tree solved/48 | G4 solved/16 | Q [95%] |
|---|---:|---:|---:|---|
| (X0+X3)>(X1+X2)?X3:X0 | 41 | 26 | 5 | 0.98 [0.35, 2.66] |
| (X0+X1)>(X2+X3)?X3:X2 | 41 | 25 | 3 | 1.20 [0.42, 3.36] |
| (X1+X2)>(X0+X3)?X0:X2 | 39 | 20 | 1 | 1.47 [0.50, 4.17] |
| (X1+X2)>(X0+X3)?X3:X1 | 35 | 26 | 2 | 0.56 [0.21, 1.46] |
| (X1+X3)>(X0+X2)?X2:X0 | 38 | 29 | 2 | 0.48 [0.18, 1.33] |
| (X1+X3)>(X0+X2)?X3:X1 | 43 | 26 | 1 | 1.41 [0.57, 3.54] |
| (X1+X3)>(X0+X2)?X0:X2 | 39 | 31 | 1 | 0.63 [0.25, 1.57] |
| (X0+X2)>(X1+X3)?X3:X2 | 38 | 19 | 4 | 1.77 [0.55, 5.29] |

Every per-cell interval straddles 1. Per-build Q ranges from 0.21 to 4.26
(13 of 24 builds below 1); since tree "builds" are only independent seed
labels, this spread is seed-to-seed variance of both arms, not build effects.

### 2.5 TS roster (descriptive by pre-registration)

| Quantity | Value |
|---|---|
| Q, 2×cap | **0.175 [0.142, 0.217]** |
| Q, 1×cap | 0.178 [0.146, 0.220] |
| A8 solved | 372/384 (96.9%) |
| Tree solved | 382/384 (99.5%) |
| G4 solved | 90/128 (70.3%) |
| Geometric 2×cap cost: A8 / tree / G4 | 23 350 / 4 093 / 167 146 |
| Tree ÷ G4 | 0.024 [0.018, 0.033] |
| Median evaluations to solve: tree / A8 | 3 328 / 18 304 |
| Paired outcomes (A8, tree): both / A8 only / tree only / neither | 370 / 2 / 12 / 0 |

Tree GP is about 5.7× cheaper than frozen A8 on every TS cell; all eight
per-cell intervals lie below 0.67 (worst cell 0.40 [0.22, 0.74] touches it
only at the upper end). Solved within 4 096 evaluations: tree 252/384, A8
28/384. In worker seconds the ratio is 0.21 (tree 0.97 s per search versus
A8 3.34 s). This is a large, consistent effect on a development roster.

### 2.6 Time cost per evaluation and seconds-based ratios

| | DG µs/eval | TS µs/eval |
|---|---:|---:|
| A8 | 66 | 55 |
| tree | 107 | 84 |
| G4 | 61 | 52 |

Tree GP spends about 1.6× more wall time per evaluation (lexicase over
variable-length trees, 32-token compilation). The seconds-based geometric
ratio (actual spend, no penalty) is 1.21 on DG and 0.21 on TS. On DG,
tree GP therefore costs *more* worker time than A8 per search on average
(28.2 s vs 11.8 s) because of its many capped searches.

### 2.7 Acquisition repayment (arithmetic, actual expenditures, reported separately)

| | DG | TS |
|---|---|---|
| Mean A8 acquisition, evaluations | 12.54 M | 6.07 M |
| Mean saving per search (tree − A8), evaluations | +85 714 [47 278, 123 791] | −49 230 [−64 704, −34 126] |
| Repayment horizon, evaluations | 146 searches [99, 269] | unbounded (tree cheaper) |
| Mean saving per search, worker s | +16.4 [12.7, 19.9] | −2.38 [−3.39, −1.33] |
| Repayment horizon, worker s | 47 searches [38, 61] | unbounded |

On DG, A8 saves evaluations per search in the arithmetic sense and would
repay its acquisition after roughly 100–270 DG searches per build (about
40–60 in worker seconds). On TS, A8 never repays: the tree arm is cheaper
at every horizon. Caveat from the runner: acquisition seconds are historical
and search seconds contemporary.

### 2.8 Consistency with earlier runs

Native A8 and G4 solve rates match their historical values under fresh
seeds: A8 DG 314/384 here vs 312/384 in run 2001; A8 TS 372/384 vs 363/384;
G4 DG 19/128 (14.8%) vs 59/384 (15.4%); G4 TS 90/128 (70.3%) vs 266/384
(69.3%). The tree calibration solve rate on source/development cells
(DG 33/64 at mix 0.5, 51.6%) also matched the target roster (52.6%), so the
preparation projection was faithful.

## 3. What the data shows

1. **On the DG roster, frozen A8 and the frozen tree procedure have
   indistinguishable geometric search cost under the pre-registered 2×cap
   rule, but the comparison is penalty-sensitive and the interval barely
   clears the lower margin.** The honest reading is "no worthwhile advantage
   for A8 was found; whether tree GP is actually better on DG is unresolved"
   (1×cap: 0.79 [0.58, 1.06]). It is not equality.
2. **The near-1 DG ratio hides two large, opposite effects.** Tree GP is
   roughly 5–8× faster than A8 on the searches it solves, and fails about
   2.6× as often (182 vs 70 of 384). Which arm is "cheaper" on DG depends
   entirely on how a capped failure is priced.
3. **Tree GP's DG failures are a size-ceiling/convergence signature of this
   frozen procedure.** Half of failed searches never find a
   training-perfect program and sit at best 60–63/64 with the population
   saturated at 32 tokens and 35–42% of offspring rejected as oversize
   clones; the other half find only shortcut programs. These diagnostics
   were pre-specified as the check against "an advantage over a weak tree
   arm"; they show the tree arm is not weak in its solving speed but is
   fragile in its reliability.
4. **On the TS roster, tree GP is clearly cheaper than frozen A8**
   (Q 0.175 [0.142, 0.217], all eight cells below the margin, 382/384
   solved). This is descriptive by pre-registration but large and uniform.
5. **Both arms dominate the G4 prior** on both rosters (tree ÷ G4 0.11 on DG,
   0.024 on TS). The proposal's listed surprise "tree solves fewer DG
   searches than G4" did not occur (202 vs 19 of 128 scaled).
6. **Repayment:** A8's acquisition repays on DG only in arithmetic terms and
   only after on the order of 100–270 searches per build (or 40–60 in
   seconds); on TS it never repays.

## 4. What the data does not show

- **No transfer claim.** Both rosters are development cells of the x4 banks;
  the tree grammar (ADD, GT, IF_GT, X0–X3, four constants) is a closure
  grammar that already contains exactly the primitives the target families
  use. "Family-blind" means the tree arm has no bank, roles or learned
  objects, not that its primitive set is generic. A fresh-bank comparison
  with both procedures frozen would be needed for any claim beyond these
  16 cells.
- **No causal statement about learning.** This compares two complete
  procedures. It does not say whether A8's acquired bias is what makes it
  more reliable than tree GP on DG, nor whether a different tree
  configuration (larger token limit, size-aware operators, different
  population) would close the reliability gap. The plan forbade tuning and
  none was done.
- **No strong-typing comparison.** The tree arm is closure-based,
  single-type; a strongly-typed or grammar-guided arm was not run.
- **Not equality on DG.** The within-margin label with an interval width of
  1.98× and a lower bound 0.013 above the boundary does not establish that
  the two procedures cost the same.
- **Cost unit matters.** Evaluations are the pre-registered unit. In worker
  seconds tree GP is 1.6× slower per evaluation and on DG costs more per
  search in total; an engineering decision about which procedure to run on
  DG would hinge on that and on the failure penalty.

## 5. Plots

- [paired_costs.png](paired_costs.png): paired per-search evaluations
  (A8 vs tree) for DG and TS with failures plotted beyond the cap, and the
  per-cell and roster Q intervals against the 0.67–1.5 margin.
- Runner's dynamics plots: `experiments/output/2026-10-10/2026-10-10-2254-dg/dynamics.png`
  and `.../2026-10-10-2254-ts/dynamics.png` (training score, correctness
  pattern diversity, output diversity, compiled token-length histogram per
  arm).

## Against the predictions

Read [plan.md](plan.md) after writing the sections above.

**Outcome grid.** The primary axis is the DG Q 95% interval; the economic
axis is the arithmetic savings interval, judged independently.

- DG Q = 0.961 [0.683, 1.352]. The entire interval lies inside [0.67, 1.5],
  so the data lands on the plan's row **"PASS partial, bounded geometric
  difference"**. It is a near-miss of the "INCONCLUSIVE" row: the lower end
  clears 0.67 by 0.013, and the pre-registered 1×cap sensitivity
  (0.785 [0.583, 1.055]) would have been INCONCLUSIVE. The plan made 2×cap
  the routing rule and 1×cap a reported sensitivity, so the row stands, but
  the steward should treat "bounded geometric difference" as "no worthwhile
  A8 advantage was found", not as evidence that the two procedures cost the
  same (the plan says so itself: "No branch means equality").
- Economic axis: DG savings per search +85 714 evaluations [47 278, 123 791]
  and +16.4 worker seconds [12.7, 19.9], both excluding zero. That is the
  column **"Positive savings, interval excludes zero"**, whose cell reads
  "Redirect learning beyond tree; a smaller saving can still repay". The
  repayment horizon is about 146 searches per build in evaluations
  [99, 269] and 47 in worker seconds [38, 61].
- The bootstrap reliability conditions held (complete 24-block grid, finite
  positive costs, 8 192 finite draws), so the primary row is valid.

**Hypothesis.** The plan expected DG Q near 0.5–1.5 and tree competitive on
TS. Both happened: DG point 0.96, TS tree about 5.7× cheaper. The plan's
stated possibility that A8's acquired literal/context bias "may instead
remain useful beyond this structural prior" is not supported on the
geometric axis on either roster, and is supported on DG only in the
arithmetic sense through reliability (A8 solved 314/384 vs tree 202/384).

**Surprises listed in the proposal.** Neither occurred: the DG lower bound
is not above 1.5, and tree GP did not solve fewer DG searches than G4
(52.6% vs 14.8%).

**Degenerate-success guard.** The threshold-adjacent DG contrast and the
near-perfect TS solving triggered the inspection the plan asked for:
every solver re-verified on D625 and re-interpreted independently, seeds and
rows distinct, pairing intact, training indices reproduced from the seed.
No spurious solves were found. On the "suppressed exploration" side, the
tree arm is reversion-heavy in its failed DG searches (35–42% oversize
rejections, half of evaluated individuals at the 32-token cap) but not in its
solved ones (20–27%, 9% at cap) and not on TS. The plan's warning applies:
a weak or rejection-heavy GP arm "limits how strongly even a primary A8 win
can speak"; here there is no A8 win to limit, and the same fragility means
the DG tree cost is an upper bound on what a size-aware closure GP would
spend.

**Precision.** Preparation warned that a near-margin Q might remain
unresolved (tree-only width proxy 1.46× at 24 blocks). The realised paired
interval width was 1.98× on DG (block log-ratio SD 0.73, roughly 1.5× the
calibration proxy's 0.48) and 1.52× on TS. The plan's `resolution_price`
output reports zero additional blocks because the interval already sits
inside the margin; that figure refers to the 2×cap rule only.

**Routing.** Per the plan: return to strategy; no tuning or top-up. The
DG verdict is "no worthwhile geometric advantage for frozen A8 over this
tree procedure, with an arithmetic saving that repays after roughly 100–270
searches per build"; the TS verdict is a large tree advantage, descriptive.
