# Digest: what we currently believe, and why

As of 2026-10-06 (last completed run 2026-10-06-1603, commit `92ba7c5`: the four-reducer FIRST bank feasibility study; before it run 2026-10-06-1425, `b397f72`, the saved-map shape-shift check, after runs 1400 and 1419 with the same design were blocked by a merge conflict; before it run 2026-10-06-0811, `0709104`, contextual moves versus continued token learning from the learned post-addition maps; before 0811 run 2026-10-06-0132, `02cf76f`, root 10's first decoder-learning study; run 2026-10-06-0001, `a65ded0`, and run 2026-10-05-2247, `0995d33`; runs 2026-10-05-1510, 2026-10-05-2039 and 2026-10-05-2242 were blocked before running). This covers the **map-bias line**, the current
core question since the 2026-09-25 reframe: *how does the genotype→program map bias what
evolution finds and keeps ("arrival of the frequent")?* Until 2026-10-05 the line studied
whether the chemistry can discover, preserve and reuse a **shared helper** (one functional part
read by several outputs); that line has stopped. The README's part 2, fitting the map's bias
to a task family ([08](questions/01-map-bias/08-evolve-bias/question.md),
[09](questions/01-map-bias/09-generic-bias-speedup/question.md)), gave a bounded answer and is
parked too; root 01's budget is spent (last slot: run 1957, stopped at its pilot). The strategist
opened root [10-compositional-map-transfer](questions/10-compositional-map-transfer/question.md)
to test part 2 on held-out operation combinations with an adaptable decoder. The first bank
failed its split/headroom requirements; the second failed the two-family requirement but kept a
usable one-family post-addition split (see "Composition bank" and "Assembly-family screen"
below). On that split, learned token multipliers on the hand-set grammar G transferred to the
two withheld compositions (about 2×) and to the related branch-else cells; allowing learned
contextual moves on top gave no resolved training gain (≤ 1.11×) and an unresolved holdout
increment, and their one off-family hint did not replicate (see "Decoder learning on
post-addition", "Contextual moves on top of M" and "Saved-map shape shift"). The four-reducer
bank meant to supply a second family fails the split rule for branch-else (see "Four-reducer
bank").

Sources: [notebook](../docs/map-bias/notebook.md) (§1–§32, one section per experiment; reviews and report tables in [docs/map-bias/reviews/](../docs/map-bias/reviews/)) and
[findings](../docs/map-bias/findings.md) (items 1–17; the owner-promoted, reviewed claims).
§NN below always means a section of the notebook. Everything is exploratory hobby work, mostly
30–50 seeds per cell, not pre-registered.

## Map bias itself

- **Random-genotype frequency predicts which tasks are easy, not which hard ones get
  solved.** Evolution routinely finds behaviours rarer than 1 in 50M random tapes. On the
  chem-tape alphabet the chem decoder and direct encoding have almost the same bias.
  ([findings item 1](../docs/map-bias/findings.md), §1)
- **Folding and direct encoding do differ in bias**, and folding solves more often wherever
  the two differ, but that looks like a *sampling* advantage: folding makes exact solvers
  1.3–30× more common. ([findings item 17](../docs/map-bias/findings.md), §27)
- **On those fixed-target tasks, evolution is mostly a worse sampler than random search**
  with the same budget. It beat sampling only on one task (direct, count∘rest(employees))
  where solvers are rare but the plateau is not deceptive. (item 17 "Night 2", §28) Not
  general: on TAG threshold tasks with lexicase (run 2026-10-05-1705) every arm reached its
  median exact solve 9–40× sooner than random search with the same vector would (random
  search computed from sampling rates, not run).
- **The frequency knob changes how often a part is made, not what is reachable.** Weighting
  one op switches between equivalent routes (e.g. min vs gate joins, 13:1 vs 2:14) without
  changing solve rates; very high weights hurt only by diluting the rest of the alphabet.
  ([item 12](../docs/map-bias/findings.md), §16, §19; also the `rest` weight in §28)
- **On the TAG alphabet, simple threshold tasks were observed at usable sampling rates only
  when the threshold is a built-in constant.** sum/max > 1, 2, 5 on length-4 lists come up about once
  per 1M uniform tapes; one ADD away (max>3, sum>7) about once per 30–100M; larger thresholds
  not once in 95M (an upper bound, not unreachability). Reviewer probes, one seed each; good enough for task design, not a claim.
  ([run 2026-10-05-1510 code review](runs/2026-10-05-1510/code_review.md))
- **A frequency bias fitted on two members of a threshold family transfers to a held-out
  member, mainly through one op's weight (a post-hoc model that later failed out of sample).** Fitting `op_weights` on sum>1, sum>5 (or max>1,
  max>5) raised held-out sum>2 (max>2) P(exact) 4.9× (8.9×) over uniform and 4.8× (6.7×) over
  the other family's fit; mismatched fits gave the holdouts nothing (1.0×, 1.3×). Every rate
  is reproduced by multiplying four op folds (INPUT, GT, the aggregator, the threshold
  constant), and swapping aggregator mass swaps the family, so the transferable part is the
  aggregator weight. The fits also suppressed the unseen constant (CONST_2 0.37×), costing
  about 2.7× of holdout gain. Sampling only, one seed, M from one fit trajectory. The product
  model was post hoc and **failed out of sample** (run 1705): a hand-set INPUT/GT/aggregator
  vector sampled 5.45× / 11.07× over uniform, not the predicted 17× / 22×, though still a bit
  better than the fit (1.11×, 1.25×). Fairly sure of the numbers, narrow in meaning.
  ([08](questions/01-map-bias/08-evolve-bias/question.md),
  [run analysis](runs/2026-10-05-1558/analysis.md))
- **In evolution, the fitted bias helps about 4×; how much of that is family-specific is
  unresolved.** Same holdouts,
  tagged harness (lexicase, crossover v2 0.7 selected mate, L 64, P1024), median evaluations
  to an exact solve, paired seeds: matched is 4.33× (sum>2) and 3.58× (max>2) faster than
  uniform (lower bounds 2.6×, 1.9×), so "supply, not success" (item 12's prediction) is out
  here. A hand-set INPUT/GT/aggregator scaffold matches the fit (0.93×, 1.08×). Matched beats
  the other family's fit only 1.66× / 1.80× (unresolved against a 2× bar, 100 pairs). And the
  other family's fit, with **no resolved sampling lift** on these tasks (1.02×, 1.33×), is itself 3.3× / 1.9× faster
  than uniform (unregistered, 50 pairs). So exact-solver supply does not predict evolution
  speed (pass-through 0.35–3.2). Fairly sure of the 4× and of hand-set ≈ fit; the
  generic/specific split is rough. Median speed only; one evolution setup.
  ([08](questions/01-map-bias/08-evolve-bias/question.md),
  [09](questions/01-map-bias/09-generic-bias-speedup/question.md),
  [run analysis](runs/2026-10-05-1705/analysis.md))
- **The generic speed-up is real, and on max>2 it is the INPUT/GT raise.** On fresh seeds
  (250 pairs, pre-registered) the other family's vector is 2.73× (sum>2) and 2.02× (max>2)
  faster than uniform (lower bounds 2.12, 1.45). Raising only its INPUT and GT (rest thinned
  evenly) matches it on max>2 (0.90×, 0.71–1.08); the rest of the vector alone gives no gain
  there and leaves more runs unsolved. On sum>2 both parts beat uniform (2.11×, 1.61×) and
  neither is resolved against a 1.5× margin of the full vector. And the flat sampling rate was
  a **cancellation**: INPUT/GT alone raises exact solvers 3.2× / 3.9×, the rest alone cuts
  them to 0.23× / 0.35×. So on max>2 the carrying part is a supply-raising change (speed-up
  smaller than its lift). Speed-up against supply survives only for the rest-of-vector arm on
  sum>2 (1.61× faster, 0.23× the solvers), where a max>2 shortcut stepping stone fits but was
  not tested. Arms differ in when a training-perfect program first appears, not in the step
  from it to exact. Fairly sure of the replication and of max>2; sum>2 open; sampling split
  descriptive. Initialization and mutation coupled, so no mechanism is named.
  ([09](questions/01-map-bias/09-generic-bias-speedup/question.md),
  [run analysis](runs/2026-10-05-1814/analysis.md))
- **On sum>2 the exact max>2 shortcut is used as the last step, but it is not needed.**
  Pilot only (run 1957, 50 seeds, 4 cells; the registered main stage did not run because a
  pilot-based power gate failed). On training sets where max>2 always fits, in runs where an
  exact max>2 program appears (U 25/50, R 35/50), it is the solver's immediate parent in 55/60
  and the solve follows within 1–2 generations. Barring it from reproduction delays those runs
  (49/55 pairs slower; a few to ten generations) but every run still solves (100/100), through
  near-max inexact programs whose share rises 2–3×. Whether the shortcut explains R's advantage
  over uniform is **not known** (R's gain on these sets 1.30, 0.71–2.32; interaction 1.38,
  0.82–2.00). Exploratory; do not read the stop as a null on the stepping stone.
  ([09](questions/01-map-bias/09-generic-bias-speedup/question.md),
  [run analysis](runs/2026-10-05-1957/analysis.md))
- Steering is untested: (μ+λ) truncation leaves one behaviour per unsolved population under
  every tie rule. (§28) → [02-fixed-target-sampling](questions/01-map-bias/02-fixed-target-sampling/question.md)

## Building blocks on chem-tape (tagged runs)

- **Lexicase, not a new primitive, is what supplies blocks**; arrangement is then the
  bottleneck. ([items 4–5](../docs/map-bias/findings.md), §3, §5, §7)
- **Tagged runs make transplants safe** (0 crashes in 940), and **crossover merges blocks
  when the join is cheap**, but a stack with a one-op join does as well: the advantage is the
  join's cost, not modularity. ([items 7–9](../docs/map-bias/findings.md), §9, §12, §14)
- **The XOR/valley thread is closed:** joins can be built by small edits when none is handed
  out; no fitness valley was found. ([items 13–16](../docs/map-bias/findings.md), §16–§26)

## Shared helpers (line stopped 2026-10-05)

Task: three outputs on tags 0/1/2 (A = max>5, A and B, A or B; B = sum>10, never rewarded
alone), leftmost-wins, crossover v2, lexicase, population 1024. Forms: **shared** (one A run,
one B helper run, both read by the consumers), **partly shared** (consumers read A, recompute
B), **duplicated** (everything recomputed).

- **Retention is not the problem.** A fully exact shared form, once at a majority or an equal
  share, persists at 32/64/128 cells and beats an equal share of duplicated. (§29)
- **Establishment from rare is the problem, and crossover with a selected mate causes it.** From 1/32 or 1/10 with
  crossover 0.7, the shared form was lost in 294/300 runs and won none (§30). The barrier is
  graded against duplicated (whose "wins" are really partly-shared endings, see below) and steep against partly shared: crossover 0.3 already stops it
  (§31 D). Both crossover branches remove it: as recipient it takes self-contained bodies, as
  donor its RECV consumers land in hosts with no helper run (§30).
- **Whichever form holds the majority wins** (270/270 runs at ≥ 3/4 shared, §31 E). Without
  crossover, establishment is about 3% per copy against duplicated and 1% against partly
  shared, consistent with independent copies (§30, §31 F).
- **But crossover is also what solves.** From random starts, 48–50 of 50 runs solve the
  training cases with crossover v2 at L 64/128; 0–4 of 50 reach a fully exact individual
  without it. (§31 G)
- **The first established form is mostly kept** (121 of 129 runs). Solutions arrive mostly
  partly shared or duplicated; a real B helper ends the run in 8 of 450 runs, often as "B
  shared, A duplicated", a form the hand-built seeds never had. Two established populations
  changed to a helper form from inside. (§31 G)
- **Shortcuts are common:** about a third of each final population fits the 64 training
  cases without being exact; 92 of 196 training-solved runs end as shortcut populations.
  (§31 G)
- **32 cells does not force sharing**; evolved shared forms are not smaller. (§31 G)

- **Discovery does not need mixing between lineages.** Crossing a parent with itself solves
  68–80% of runs by generation 3000, about three times slower than a selected mate; a random
  mate solves as rarely as crossover off. (§32 J)
- **A helper already in the host does not rescue a rare shared form** at crossover ≥ 0.3: it
  repairs hybrids, but the repaired children are partly shared. (§32 K)
- **Shortcuts are structural, not a 64-case artefact:** with 256 cases 9 of 35 runs still end
  as shortcuts, all failing only the OR output. (§32 L, partial)
- **Shared endings are rare:** 4 in 100 runs at L 64/0.3, all B-type. (§31 G + §32 G2)

- **The establishment barrier is mixing between lineages, not crossover as such.** With
  self as the mate, crossover v2 at 0.3 or 0.7 lets a rare seeded shared form win 183 of 240
  contests, against 34 of 240 with a selected mate on the same seeds and 75 of 120 with
  crossover off; no cell falls below crossover off by more than one win, and the shared share
  does not drop early. Self-crossover never turns one form into another and breaks shared
  only about 1 point more often (20% vs 19%). One soft spot: at 0.7 against partly shared, 5
  of 30 runs reached ≥ 95% shared and then fell back. Fairly sure for these hand-built
  layouts at L 64; nothing about single copies.
  ([06](questions/01-map-bias/06-self-mate-establishment/question.md),
  [run analysis](runs/2026-10-04-1839/analysis.md))
- **So discovery and establishment can coexist under one operator** (self-mating: slower
  discovery, §32 J; no establishment barrier, 06).
- **Shared is never beaten by duplicated as such.** In every seeded contest against
  duplicated (off, self or selected mate), runs that lose shared end *partly shared*, a form
  nobody seeded. Read old "lost to duplicated" rows that way.

- **Shared children do arrive, and single copies drift out.** In established partly
  populations (§32 J self/0.3/L 64, final populations), exact shared children appear at about
  1.6e-6 per child, about 2 per run over the non-shared phase (per run 0–7). Put back as one
  copy into their own population, 0 of 100 established (≤ 3.6%), all gone within 30
  generations; untouched controls show the same transient shared individuals. So "shared
  helpers are rare because they never arrive" is wrong as stated. Fairly sure for these final
  populations; the mid-phase check had no power.
  ([07](questions/01-map-bias/07-shared-arrival/question.md),
  [run analysis](runs/2026-10-04-2135/analysis.md))
- **But the arrivals are the wrong kind.** All 56 were A-only or other; **0 B-helper** in 30M
  partly-parent children (≤ 1.2e-7 per child), while both runs that ended shared are B-helper.
  Hypothesis, not shown: A-only copies arrive and drift out; B-helper almost never arrives and
  wins when it does. 100 insertions also cannot tell neutral drift (≈ 0.25%) from a
  disadvantage. Why shared endings are rare is therefore **unresolved**; the shared-helper line
  stops here by its stop rule (07 and 04 parked).

## Composition bank (root 10, run 2026-10-05-2247)

One run, 50 paired seeds per cell × arm (150 where topped up), cap 524 288 evaluations, stack
tape `v2_rmin`, length-4 lists in {-2..2}, P 256, lexicase on 64 cases with an exact check on
all 625 inputs. Reviewed analysis; fairly sure of the numbers, narrow in scope (one bank, one
harness, one hand-set grammar). ([11](questions/10-compositional-map-transfer/11-composition-bank/question.md),
[run analysis](runs/2026-10-05-2247/analysis.md))

- **The 3×3 reducer/combiner bank has no usable split at 524k.** Exhaustive screening to depth
  6 kept 8 of 9 cells (SM-SEL is an exact alias). Uniform search solved 7 of the 8 in ≥ 35/50
  runs; Sm-SEL reached 27/50 (95% 39–68%), still rising at the cap. That leaves 0 of 6
  transversals eligible. Whether a 2–4× larger cap fixes this is untested (a reviewer probe
  on other seeds: 36/50 at 2M).
- **All four structural splits fail the 4 096-evaluation headroom rule under a hand-set
  previous-token grammar; raising the search cap alone does not remedy this.** G
  (INPUT → reducer; int → INPUT/ADD/DUP/IF_GT; ≥ 0.25× uniform mass everywhere) solved every
  cell in every seed: median 768–1 024 evaluations on ADD, 1 792–2 304 on DADD, 3 584–4 096
  on SEL (the SEL intervals span 4 096). Every split holds out an ADD and a DADD cell, so every
  split has two holdouts under the 4 096 line. Whether another decoder could improve on G here
  was not tested. G's rows are this bank's syntax (67–100% of
  each cell's canonical bigrams occur in other cells), so whether G is a fair "generic"
  control here or an oracle is a design question, now
  [12](questions/10-compositional-map-transfer/12-generic-grammar-headroom/question.md).
- **Context in the decoder speeds search beyond its token frequencies, on this bank.** Median
  evaluations to solve, paired bootstrap 95%: G vs G-marg (same token marginals, no context)
  2.6–4.5× faster on the six ADD/DADD cells, 9.9× (4.7–28) and 19.5× (4.6–36) on the two SEL
  cells; all eight intervals exclude 1. Not a mechanism: G also emits more exact solvers
  (10–47× G-marg's sampling rate) and changes 1.65 tokens per allele mutation against 0.95.
- **A fixed token bias gives about 2–3.5×, and supply again overstates speed.** F/U 1.9–3.5×
  on the seven resolved cells (interval lower ends 1.45–2.26); G/U 8.6–13× on ADD/DADD and 31× (18–44)
  on Mm-SEL. Exact-solver sampling rates rose 11–82× (F) and 120–1 650× (G) over U, so search
  gained roughly a tenth of the supply gain or less — the same direction as root 01's
  pass-through below 1, on a different alphabet and task family.
- **64 training cases do not pin these targets down:** training-perfect but inexact programs
  appeared in 43 of 2 400 runs (all caught by the 625-input check).

## Assembly-family screen (root 10, run 2026-10-06-0001)

One run, commit `a65ded0`, complete data. Same tape, harness, cap and frozen U/F/G/G-marg tables
as 2247; ten-token canonicals; exhaustive ≤ 9-token alias screen (typed-stack dedup) on three
domains (625, 1 331, 2 401 inputs); search on the 16 cells retained on D1331, 50 paired seeds per
cell × arm. Reviewed analysis; fairly sure of the numbers, narrow in scope.
([12](questions/10-compositional-map-transfer/12-generic-grammar-headroom/question.md),
[run analysis](runs/2026-10-06-0001/analysis.md))

- **None of the six screened same-primitive shapes gives two families with enough distinct
  cells.** Of 162 canonicals over {S, M, m} (gate `(A+B)>0 ? C : D`, branch-then, branch-else,
  post-addition `(S>0 ? X : Y) + Z`, two linear DUP placements), 11/16/16 survive on the three
  domains: gate and branch-then 0, branch-else ≤ 2, post-addition 4–8, linear 3 + 3 by
  construction. 0 of 45 shape-pair × domain rows meet the frozen ≥ 4-cell rule; unchanged for
  any alias cutoff in 0.70–0.85. Mechanism from the witnesses: ADD distributes out of an IF_GT
  branch via CONST_0, DUP reuses the condition, and S-sign correlation and constant substitution
  give near-aliases. Scope: these six shapes and rules only; other tokens, longer canonicals or
  a fourth reducer were not screened, and the run does not show an alphabet change is required.
- **Ten-token branch cells leave room above the frozen G.** G medians 8 192–41 728 on the ten
  post-addition/branch-else cells (2–10× the 4 096 line; ≥ 42/50 solves); linear cells 2 304–5 120
  (3 below the line). F and G-marg medians above the line on all 16. So G's sub-4 096 speed on
  2247's 5–7-token cells does not extend to these ten-token branch cells. Uniform search is uneven: 13/16
  cells ≥ 35/50, BE:S?M:(S+m) 8/50 (F 22/50, G 42/50).
- **G's advantages replicate on a second bank.** Paired capped-time ratios: G/U 8.4–11.3×
  (16/16 intervals exclude 1), G/G-marg 1.5–6.0× (15/16), F/U 1.0–3.6× (4 intervals include 1).
  Capped-time ratios, not KM medians, so not directly comparable with 2247's figures. G samples
  13–180 exact solvers per 10⁸ genotypes; U none on any cell (≤ 3×10⁻⁸ each), so supply ratios
  are lower bounds and the supply-versus-speed pass-through is not estimable here.

## Decoder learning on post-addition (root 10, run 2026-10-06-0132)

One run, commit `02cf76f`, complete data (18 trajectories, 197 528 searches). Same tape, harness
and frozen maps as 0001. Six post-addition training cells, two withheld `(S?M:S)+M`,
`(S?M:S)+m` (then/else pair never seen in training) on D1331. Three learners, 6 matched
trajectories each: (4 + 12) with re-scored parents, three-coordinate N(0, 0.5) mutations,
25 generations, selection on 24 fresh 65k-cap training searches per candidate. Final maps
scored on shared fresh seeds (training 6 × 50, holdouts 2 × 100, cap 524 288). Speed ratios
with 95% two-level bootstrap. Reviewed analysis; fairly sure of the numbers, narrow in scope:
one screened family, starts at G, one optimizer and budget.
([13](questions/10-compositional-map-transfer/13-post-addition-map-learning/question.md),
[run analysis](runs/2026-10-06-0132/analysis.md))

- **Learned token multipliers on G's template speed the withheld compositions about 2×** (1.7–2.25× across two seed sets). M (23
  global multipliers applied to every row of G) vs frozen G: fresh training 2.23× [1.82, 2.75];
  holdouts 2.01× [1.47, 2.81] and 1.71× [1.26, 2.32]; all 6 trajectories faster on every set.
  On 0132's 100 holdout seeds a ≥ 1.5× gain was not established (lower bounds 1.47, 1.26);
  re-scored on 200 new seeds in run 0811 the same maps give 2.25× [1.81, 2.81] and 2.06×
  [1.60, 2.63]. About a quarter of the training log-gain is lost on the holdouts on average
  (≈ 22% pooled; 14% and 33% per holdout; descriptive). The context is G's, supplied by hand;
  what was learned is token weighting: INPUT up (×3.4) and DUP down (×0.5) in all six M maps and
  in T, IF_GT up in all six M maps, reducer changes with exceptions. Curves were still declining
  at generation 25; 35 more generations of the same steps gave another 1.45× on training (run
  0811). Branch-else results are in the next section.
- **The full contextual learner showed no resolved gain with three-coordinate steps.** C (all 552
  log-weights, from G): fresh training 0.92× [0.78, 1.09] vs G, so a gain above 1.09× is excluded
  at this budget; flat curves; it drifted modestly (L1 1.1–1.5 vs M's 11–14). Its context-free
  marginals show no resolved improvement over G's (C-marg/G-marg 1.01–1.10; training interval
  [0.92, 1.23], holdouts [0.79, 1.30] and [0.79, 1.52], which admit appreciable gains).
  Holdouts split: 1.16× [0.86, 1.54] and 0.80× [0.60, 1.07]. Each child changes three table cells by about e^±0.5, far below the per-run score sd (≈ 1.6 log2, 24 runs
  per candidate). The operator is a plausible explanation, not an isolated cause; the result does
  not show that contextual preferences cannot be learned or would not transfer.
- **Frequency-only learning helps a context-free start but does not reach G.** T (23 tied weights,
  from G-marg): 1.69–2.12× faster than G-marg on all sets, still 0.41–0.57× of G's speed. It
  agrees with M on DUP down and INPUT up. G/G-marg on these seeds 3.0–4.8×, replicating 0001.
- **Token-weight learning found maps 2.2× faster than G on fresh training searches,** contrary to
  the steward's pre-run expectation (random whole-table perturbations and a hand-set PA grammar
  had not beaten G). This shows accessible improvement, not the shape of G's neighbourhood.

## Contextual moves on top of M (root 10, run 2026-10-06-0811)

One run, commit `0709104`, complete data (12/12 matched pairs, 376 796 searches, 4 h 50 min).
Same harness and split as 0132. From each of the six saved M maps, two continuations per arm,
35 generations, same outer loop and shared seeds within a pair: M+ (M's token steps) vs R
(M's multipliers plus 24 × 23 row residuals; half token steps, half whole-row N(0, 0.5 or 1.0)
steps). Shared fresh test seeds (training 6 × 50, holdouts 2 × 200, 524k cap); bootstrap over
six start clusters and seeds. Reviewed analysis; fairly sure of the numbers, narrow in scope:
one screened family, one outer loop and operator, starts at M.
([13](questions/10-compositional-map-transfer/13-post-addition-map-learning/question.md),
[run analysis](runs/2026-10-06-0811/analysis.md))

- **Allowing contextual row moves gave no resolved training gain over continued token
  learning.** R / M+ on fresh training 1.00× [0.90, 1.11]: a gain above 1.11× is excluded. Both
  arms gained the same 0.54 log2 over their starts (R / M 1.46×, M+ / M 1.45×).
- **On the withheld pair the increment is unresolved (points 1.06–1.16×).** R / M+ 1.16× [0.91, 1.48]
  and 1.06× [0.83, 1.31]; R faster in 8 and 9 of 12 pairs. The between-start spread (0.41–0.45
  log2) is about twice the planned one; bounding a true null below 1.25× needs about 7–9
  independent starts, resolving a true 1.16× about 20. The residual ablation (R / R_abl
  1.15× [0.97, 1.41], 1.10× [0.97, 1.25], 1.17× [0.88, 1.53] on the three PA sets) has no
  resolved speed advantage anywhere; appreciable gains remain possible, so no gain is
  attributed to the residuals, which is not the same as showing they contribute nothing.
- **Operator acceptance was near the chance rate.** Children of every operator (token,
  row σ 0.5, row σ 1.0) entered the next parent set at 23.7–25.8% against 25%. Equal average
  acceptance across operator classes can coexist with selection of better children within each
  class, so these counts do not establish how well selection ranks individual steps. Slow
  cumulative improvement is a proposed explanation, not an isolated mechanism.
- **M's learned change also speeds the branch-else cells, so its benefit is not confined to
  post-addition.** Frozen M / G on the two branch-else cells 2.23× [1.66, 3.06], a point
  estimate similar to the PA holdout gains (2.25×, 2.06×; separate estimates, not an
  equivalence test, so a PA preference is not ruled out); on the six linear cells 1.08×
  [0.72, 1.57], unresolved with G near the population floor. Branch-else is a related shape,
  not an independently trained family.
- **Unregistered hint (not replicated in run 1425): in the six "a" maps, allowing row moves
  shifted speed toward branch shapes and away from linear ones.** Six "a" maps: R / M+
  1.33× [1.05, 1.66] on branch-else (faster in 5/6) and 0.65× [0.44, 0.88] on linear (slower in 6/6), while M+
  alone got 1.52× faster than M on linear. R doubled PA-training solver supply over M+ in 5 of
  6 starts and lowered linear supply in 5 of 6, without a resolved PA search gain. Post hoc, six
  maps, no attribution to residuals: a pattern to test, not a finding. The pre-registered check
  on the "b" continuations (run 1425, next section) found the opposite shift.

## Saved-map shape shift (root 10, run 2026-10-06-1425)

One run, commit `b397f72`, complete data (55 frozen maps × 8 off-family cells × 200 fresh
seeds = 88 000 searches, 48 min; gate passed, G within 0.05 log2 of 0811). Maps: G, M1–M6, and
for each of the 12 0811 pairs M+, R, R_abl (residuals zeroed) and R_fm (G's context rows with
token multipliers fitted so its pooled uniform-allele emitted token frequencies match R's; TV
≤ 7e-5). Cells: the two branch-else (BE) and six linear (LIN) cells of 0811. Pre-registered;
primary layer the six "b" continuations, which share their M starts with the "a" maps, so this
is a conditional replication over learning runs, not over starts. 95% t intervals over six
start clusters; > 1 means the first map is faster. Reviewed analysis; fairly sure of the
numbers, narrow in scope.
([14](questions/10-compositional-map-transfer/14-saved-map-shape-shift/question.md),
[run analysis](runs/2026-10-06-1425/analysis.md))

- **The branch-over-linear shift of R over M+ did not replicate; on the "b" maps it reversed.**
  "b" R / M+: BE 0.94× [0.77, 1.16], LIN 1.29× [0.88, 1.91], shift (BE ÷ LIN) 0.73× [0.57,
  0.94], below 1 in 6/6 starts. Outcome row 3: any BE gain on these maps is bounded below
  1.17×. The reversal was not pre-stated; read it as run-to-run variation, not a lead.
- **The "a" pattern is real for those six maps, so the shift is a property of individual
  learning runs.** Re-scored on the fresh seeds, "a" R / M+ gives shift 1.86× [1.41, 2.44]
  (0811: 2.03×). Two sets of runs of the same learner from the same starts disagree in sign;
  both were selected on post-addition cells only, so off-family linear speed is unconstrained
  and wanders by about 0.5 log2 within a family.
- **On the unselected "b" maps, a token-only map matched to R's pooled emitted token
  frequencies on G's context was not resolved from R; R's advantage is bounded to about 17% on
  BE and 12% on the shift.** R / R_fm: BE 1.04× [0.91, 1.17], LIN 1.02× [0.97, 1.06], shift 1.02× [0.92, 1.12]; R_fm / M+
  shows the same reversed shift as R / M+ (0.72× [0.54, 0.95]). The pooled a/b residual effect
  (shift 1.23× [1.11, 1.36]) comes from the selected "a" maps; its point estimates combine a
  linear slow-down (0.94× [0.87, 1.03]) and a BE gain (1.16× [0.97, 1.39]), neither resolved alone. This bounds, not excludes, a residual
  contribution, and matches only pooled frequencies, not positional or in-population ones.
- **Continued post-addition learning carried over to branch-else for both learners.** Against
  their M start on BE: M+ 1.40× ("a") and 1.42× ("b"), R 1.74× and 1.34×; lower bounds
  1.05–1.10. Branch-else is a related shape, not a separately trained family.

## Four-reducer bank (root 10, run 2026-10-06-1603)

One run, commit `92ba7c5`, complete data (validation, three exhaustive screens, 5 200 searches,
43.7 min). FIRST (first list element) added to SUM/MAX/MIN as a 24-token alphabet. Cells:
branch-else (BE) `A?B:(C+D)` and post-addition (PA) `(A?B:C)+D`, with A–D a permutation of
S, M, m, F. Ten tokens each, with identical token counts. 0001's ≤ 9-token, 80% alias screen and
role-covered split rule. Search on the 13 retained D1331 cells, 8 arms × 50 paired seeds, with
G4 (G extended to four reducers before the data). Reviewed analysis. Sure of the screen (exact);
fairly sure of the search numbers; narrow in scope.
([15](questions/10-compositional-map-transfer/15-four-reducer-family-bank/question.md),
[run analysis](runs/2026-10-06-1603/analysis.md))

- **This bank cannot carry the symmetric two-family test: branch-else has no role-covered
  holdout pair.** 13 of 36 cells survive on D1331 (BE 5, PA 8; D625 4 + 6, D2401 5 + 8). Every
  M- or m-conditioned cell is a near-alias, because M > 0 and m > 0 are nearly constant on these
  domains. In BE's `then` role, S, F and M each occur once, so no BE pair is covered on any of the
  three domains. One BE cell, `S?m:(M+F)`, could be held out alone. PA splits (2 holdouts, 6
  training). Scope: this shape pair, these domains and the frozen rules. The asymmetric designs
  were not tested.
- **G4 is tractable and leaves room above the 4 096 line on all 13 cells.** G4 solves 45–50/50,
  KM medians 8.7k–28.7k. G4 / U is 10.3× [7.9, 13.5] (BE) and 8.1× [6.8, 9.6] (PA). G4 / G4-marg
  is 4.4× [3.4, 5.6] and 3.3× [2.7, 4.0]: the contextual grammar beats its own marginals on a
  third bank.
- **Two hand-set family grammars carried a crossed family preference, located in context.**
  Matched over swapped: BE 1.68× [1.39, 2.05], PA 1.32× [1.12, 1.57]; per-cell point estimates
  are above 1 on 13 of 13 cells. Their tied marginals give no resolved contrast (BE 1.11× [0.90,
  1.36]; PA 0.91× [0.76, 1.10]). The directly paired context-over-marginal contrast is resolved
  in both families (1.51× [1.09, 2.09], 1.46× [1.16, 1.82]). This is asymmetric against G4: the BE
  grammar beats G4 on BE (1.36× [1.04, 1.75]) and slows PA (0.66× [0.56, 0.77]). The PA grammar
  does not beat G4 on PA (0.87× [0.75, 1.04], unresolved). So the PA half is "the BE grammar
  hurts PA", not "the PA grammar helps PA", as with 0001's hand-set PA grammar against G. This
  witnesses what a fixed previous-token decoder can express. It says nothing about what a
  learner would find.
- **Measured learner cost on this bank.** G4 takes about 1.9 s per full-cap search and 0.4–1.2 s
  per 65k-cap inner search. A 4-trajectory × 25-generation token-learner pilot projects to about
  2.4 h, or 4.7 h with a 2× slower-candidate allowance. The 10–20 min per trajectory carried over
  from 0132 does not hold here.

## Open questions

- [10-compositional-map-transfer](questions/10-compositional-map-transfer/question.md) (open,
  root, budget 7, 5 used): can a decoder adapted across related tasks help fresh populations
  solve unseen operation combinations beyond a token-frequency bias? Two feasibility studies
  (one bank failed split/headroom, one failed the two-family requirement but kept a PA split),
  then two learning studies: learned token multipliers on G transfer about 2× to the withheld
  pair and to branch-else; contextual row moves on top add no resolved training gain (≤ 1.11×),
  holdout increment unresolved, and their off-family branch shift did not replicate (14).
  Budget 7, 6 used: the four-reducer feasibility study (15) failed the branch-else split, so
  the last slot (a matched/mismatched family comparison) has no symmetric bank; back to
  strategy.
  - [11-composition-bank](questions/10-compositional-map-transfer/11-composition-bank/question.md)
    (closed, run 2026-10-05-2247): this 3×3 bank has no eligible split at 524k (Sm-SEL 27/50
    under U), and all four splits fail the 4 096 headroom rule under the hand-set grammar G.
  - [12-generic-grammar-headroom](questions/10-compositional-map-transfer/12-generic-grammar-headroom/question.md)
    (closed, run 2026-10-06-0001): ten-token branch cells leave 2–10× headroom above G, but none
    of six same-primitive assembly shapes yields an eligible two-family pair (alias identities).
  - [13-post-addition-map-learning](questions/10-compositional-map-transfer/13-post-addition-map-learning/question.md)
    (closed, runs 2026-10-06-0132 and 2026-10-06-0811): G-based token multipliers transfer to the
    withheld PA pair (2.25×, 2.06× on 200 seeds); the 552-weight learner showed no resolved
    training gain (0.92× [0.78, 1.09]); row residuals on top of M vs continued token steps:
    training 1.00× [0.90, 1.11], holdouts 1.16× and 1.06×, unresolved.
  - [14-saved-map-shape-shift](questions/10-compositional-map-transfer/14-saved-map-shape-shift/question.md)
    (closed, run 2026-10-06-1425, row 3): 0811's branch-versus-linear shift of R over M+ did not
    replicate on the "b" continuations (shift 0.73× [0.57, 0.94], opposite sign); the "a" maps
    keep it on fresh seeds, so it is run-specific; on "b" a frequency-matched token-only map
    was not resolved from R (shift 1.02× [0.92, 1.12]).
  - [15-four-reducer-family-bank](questions/10-compositional-map-transfer/15-four-reducer-family-bank/question.md)
    (closed, run 2026-10-06-1603, row 1): with FIRST added, branch-else has no role-covered
    holdout pair on three domains; PA splits; G4 has headroom on all 13 cells; hand-set family
    grammars show a crossed, context-located preference (descriptive).
- [01-map-bias](questions/01-map-bias/question.md) (open, root, budget spent): how does the map
  bias what evolution finds and keeps?
- [02-fixed-target-sampling](questions/01-map-bias/02-fixed-target-sampling/question.md)
  (parked): does folding help evolution beyond making solvers common? Rarity ladder not run.
- [03-rare-shared-establishment](questions/01-map-bias/03-rare-shared-establishment/question.md)
  (closed): can a rare shared form establish under crossover? No at crossover ≥ 0.3.
- [04-random-start-discovery](questions/01-map-bias/04-random-start-discovery/question.md)
  (parked): discovery needs no lineage mixing (§32 J); shortcuts are structural (§32 L).
  Left: duplication-only companion, 0.3 vs 0.7 parity.
- [05-latent-helper](questions/01-map-bias/05-latent-helper/question.md) (closed): a helper
  already present does not let a rare shared form establish (§32 K).
- [06-self-mate-establishment](questions/01-map-bias/06-self-mate-establishment/question.md)
  (closed): yes, under self-mating a rare seeded shared form establishes at the crossover-off
  rate; the barrier is mixing between lineages.
- [07-shared-arrival](questions/01-map-bias/07-shared-arrival/question.md) (parked): about 2
  A-only/other shared arrivals per run, 0/100 single copies established, no B-helper arrival.
  Reopen if a B-helper single copy becomes testable or in-situ replay exists.
- [08-evolve-bias](questions/01-map-bias/08-evolve-bias/question.md) (parked): the README's
  part 2. Can the map's frequency bias be fitted to a task family and help evolution on unseen
  members? Yes over uniform (about 4×), barely over the other family's fit (1.7–1.8×,
  unresolved), and a hand-set scaffold does as well (run 2026-10-05-1705). Parked with 09;
  root 01's last slot went to 09 (run 1957).
- [09-generic-bias-speedup](questions/01-map-bias/09-generic-bias-speedup/question.md)
  (parked): why does a vector with no resolved sampling lift speed evolution 2–3×? Replicated; INPUT/GT
  raise carries it on max>2, unresolved on sum>2; the "no lift" was a cancellation (run
  2026-10-05-1814). The direct shortcut test (run 2026-10-05-1957) stopped at its pilot: the
  max>2 shortcut is used but not needed; its share of the gain is unmeasured. Budget spent.
  Reopen on a no-lift speed-up in another family, a heritable-bias design that needs the
  answer, or an owner-funded rerun of the veto at n ≈ 1600.

## Older context

Earlier tracks are background, not the current line. The original folding track (3-bond
ceiling broken via Pareto scaffold preservation, regime-shift result):
[docs/folding/findings.md](../docs/folding/findings.md). The chem-tape track before the
reframe: [docs/chem-tape/findings.md](../docs/chem-tape/findings.md) and
[experiments.md](../docs/chem-tape/experiments.md). The CA track:
[docs/ca/experiments.md](../docs/ca/experiments.md). Also
[docs/coevolution.md](../docs/coevolution.md), [docs/theory.md](../docs/theory.md)
(Altenberg's constructional selection) and
[docs/python-rewrite-results.md](../docs/python-rewrite-results.md). Process lessons:
[docs/methodology.md](../docs/methodology.md) (the line now runs in light hobby mode).
