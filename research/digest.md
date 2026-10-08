# Digest: what we currently believe, and why

As of 2026-10-07 (run 2026-10-07-2156, commit `36c665d`: token-only fits T1 and T2 scored on the exact seeds of the saved C1 and C2, completing the four-arm feedback crossing on training and withheld cells; its first attempt, run 2026-10-07-2129, stopped at preparation on the autonomous deadline with no result; before it run 2026-10-07-1924, commit `5565d54`: one feedback refit of the solver-corpus tables from solvers found under them, against the parent and a fresh one-shot refit, training and withheld cells; before it run 2026-10-07-1707, commit `627336d`: previous-token and token-only tables fitted directly to exact G4 solver tapes, training and withheld cells; before it run 2026-10-07-1137, commit `86ef669`: the same token-only versus rank-one-context continuation from the saved token maps, at 96 searches per candidate, training cells only; before it run 2026-10-07-0821, commit `f61aec4`: the same comparison at 24 searches per child; before that run 2026-10-07-0315, commit `5dae3a6`: the same starting-program × search-decoder crossing on the ten training cells; before that run 2026-10-06-2331, commit `8f42f38`: the frozen maps' starting programs crossed with the decoder used during search, on the three withheld cells; before that run 2026-10-06-2229, commit `33fcee2`: the frozen crossed BE/PA token maps scored on the three withheld cells, stage 2; before that run 2026-10-06-1723, `db96645`, crossed BE/PA token learning on the four-reducer bank, stage 1, training cells only; before that run 2026-10-06-1603, `92ba7c5`, the four-reducer FIRST bank feasibility study; before that run 2026-10-06-1425, `b397f72`, the saved-map shape-shift check, after runs 1400 and 1419 with the same design were blocked by a merge conflict; before it run 2026-10-06-0811, `0709104`, contextual moves versus continued token learning from the learned post-addition maps; before 0811 run 2026-10-06-0132, `02cf76f`, root 10's first decoder-learning study; run 2026-10-06-0001, `a65ded0`, and run 2026-10-05-2247, `0995d33`; runs 2026-10-05-1510, 2026-10-05-2039 and 2026-10-05-2242 were blocked before running). This covers the **map-bias line**, the current
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
bank"). On that bank, with a narrower split authorized by strategy, the token learner improves
the four-reducer grammar G4 about 2.2× on both families' training cells and 2–3× on the three
withheld cells; which family the maps were trained on made no detectable difference on the
withheld cells (matched over mismatched 1.02× and 0.96×; 95% upper bounds 1.2485× on BE, rising to
about 1.3× in leave-one-map-out checks, and 1.15× on PA; a 1.1× preference is not excluded)
(see "Crossed family learning"). On those three cells and on the ten training cells, the maps' gain
comes both from the programs the search starts with and from using the map during search, each
about 1.3× given the other, and the two gains are strongly sub-additive; on the training cells
the start weighs relatively more on branch-else cells than on plus-arg cells (see "Starting
programs versus ongoing decoder"). A third contextual procedure (rank-one context steps mixed
into token continuation from the saved maps) first ran in a loop where token continuation did
not resolve learning (0821). With 4× more search evidence per candidate, token-only continuation
did learn (about 1.12–1.14× on two fresh seed blocks), and in that loop context under equal
search funding added no resolved increment (C/T 0.967× [0.871, 1.073]) (see "Compact context
continuation" and "Selection-calibrated continuation"). A different signal did work: a
previous-token table fitted directly to the token tapes of exact G4 solvers beat a token-only
fit to the same tapes about 1.37× on training cells and 1.29× on the withheld cells, over 32
independent corpora, with no resolved family advantage (see "Solver-corpus context fit"). One
feedback step added further search speed: refitting each table to exact solvers found under it
beat its parent about 1.40× on training and 1.29× on the withheld cells, while a fresh one-shot
refit was not resolved from the parent (see "Solver-corpus feedback refit"). On the training
cells that step also raised the fitted context's advantage over a token-only fit to the same
corpora, by about 1.17× and mostly on BE, while the token-only fit itself improved about 1.20×;
on the withheld cells that interaction is unresolved (see "Feedback context increment"). Root 10
has used all 15 of its slots.

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
- **Two hand-set family grammars carried a crossed family preference; context strengthens it
  over the tied-marginal controls.**
  Matched over swapped: BE 1.68× [1.39, 2.05], PA 1.32× [1.12, 1.57]; per-cell point estimates
  are above 1 on 13 of 13 cells. Their tied marginals give no resolved contrast (BE 1.11× [0.90,
  1.36]; PA 0.91× [0.76, 1.10]). The directly paired context-over-marginal contrast is resolved
  in both families (1.51× [1.09, 2.09], 1.46× [1.16, 1.82]); that is an increment beyond the
  marginal controls, not a zero marginal preference. This is asymmetric against G4: the BE
  grammar beats G4 on BE (1.36× [1.04, 1.75]) and slows PA (0.66× [0.56, 0.77]). For the PA
  grammar no PA improvement over G4 was resolved (0.87× [0.75, 1.04], admitting gains up to about
  4%). So the PA half is mainly "the BE grammar hurts PA", with no resolved "the PA grammar
  helps PA", as with 0001's hand-set PA grammar against G. This
  witnesses what a fixed previous-token decoder can express. It says nothing about what a
  learner would find.
- **Search costs on this bank; learner runtime was projected, not measured, in 1603.** G4 takes
  about 1.9 s per full-cap search and 0.4–1.2 s per 65k-cap inner search. Those costs implied a
  conservative pilot projection (2.4 h for 4 trajectories, 4.7 h with the frozen 2× allowance),
  and the allowance excluded stage C. Run 1723 then measured 9.5–13.7 min per trajectory, in line
  with 0132.

## Crossed family learning (root 10, runs 2026-10-06-1723 and 2026-10-06-2229)

One run, commit `db96645`, complete data (20 trajectories, 216 420 searches, 4.28 h, no holdout
searched). Same bank, D1331, `v2_rmin_first` and G4 as 1603. Narrower split authorized by
strategy 1723 after the bank data were seen: BE trains on 4 cells (holds out `S?m:(M+F)`), PA on
6 (holds out `(F?S:M)+m`, `(S?M:m)+F`). 0132's token learner (24 multipliers on G4's rows, 25
generations) run independently 10 times per family from G4. Final maps scored on all ten training
cells, 50 shared fresh seeds, 524k cap; paired capped-time ratios over G4; trajectory as the unit,
95% t (Welch between families). Pre-registered readouts; reviewed analysis. Fairly sure of the
numbers; narrow in scope (ten screened training cells, one learner, starts at G4).
([16](questions/10-compositional-map-transfer/16-crossed-family-adaptation/question.md),
[run analysis](runs/2026-10-06-1723/analysis.md))

- **Token learning improves G4 about 2.2× on both families' training sets.** Own-family fresh
  gain BE 2.18× [1.98, 2.40], PA 2.27× [1.95, 2.65]; 20/20 maps above 1. Same size as M over G on
  post-addition in 0132 (2.23×). Mostly speed: G4 already solves 480/500 at the cap.
- **Most of that gain is generic on training cells.** BE-trained maps speed PA training cells
  2.07× [1.94, 2.21]; PA-trained maps speed BE training cells 1.93× [1.61, 2.30]. All 20 maps had
  positive estimated gains averaged over the other family's training cells; both arm-level
  averages are resolved. Both families make the same big moves (INPUT up in 20/20 maps, IF_GT and
  REDUCE_ADD up, DUP and CHARS down); mean vectors differ by about half the within-family spread
  (permutation p 0.20).
- **In-sample, the family preference estimates are 1.13× and 1.10×, both unresolved.** Matched
  over mismatched: 1.13× [0.93, 1.37] on BE cells and 1.10× [0.93, 1.29] on PA cells; neither
  excludes 1 or 1.25×. Eight of ten cell point estimates favour matched training; the other two
  are within 0.02 log2 of zero. A post hoc within-map interaction (sum of both contrasts) is
  1.24× [1.09, 1.41]: suggestive of some family information on the cells each map was trained
  on. On the withheld cells the interaction was unresolved, 0.98× [0.83, 1.15]; transfer of a
  modest family preference remains possible (below).
- **Learning is cheap enough on this bank:** 9.5–13.7 min per trajectory on 10 workers. The 24-
  search candidate score barely ranks parents (median Spearman 0.20 BE, 0.00 PA between successive
  rescorings), but the 120-search selection score predicts fresh gain (Spearman −0.45, −0.83).

Stage 2, run 2026-10-06-2229 (commit `33fcee2`, complete, 35 min): the same 20 maps, frozen, and
G4 on the three withheld cells, 400 shared fresh seeds each, no learning. Pre-registered
readouts; reviewed analysis. Fairly sure of the numbers; three screened cells, only one of them BE.
([analysis](runs/2026-10-06-2229/analysis.md))

- **The token maps transfer to the withheld cells about 2–3×.** All six arm × cell gains over G4
  are resolved: BE maps 2.01× [1.86, 2.18] on the BE cell and 2.59× [2.41, 2.77] on the PA
  cells; PA maps 1.97× [1.63, 2.39] and 2.48× [2.07, 2.96]. Holdout gains remain substantial:
  BE's point gain is slightly lower than on training (2.18× → 2.01×) and PA's higher (2.27× →
  2.48×); these cross-block comparisons do not establish equality or absence of overfitting.
- **No matched-family advantage was resolved on the withheld cells; 95% upper bounds 1.2485×
  (BE) and 1.15× (PA), a 1.1× one not excluded.** Matched over mismatched: 1.02× [0.84, 1.25] on BE, 0.96× [0.79,
  1.15] on PA; pre-stated within-map interaction 0.98× [0.83, 1.15]. The BE upper bound (1.2485)
  is at the margin: dropping any one of 14 maps lifts it to 1.25–1.30. Which cell is searched
  moves the gain by about 50%; which family trained the map, by a few percent in the point
  estimates (the intervals allow up to about 1.25×). This is a
  bound, not equality; detecting a true 1.1× at 80% would need about 64–75 trajectories per family.
- **Not separated:** whether the generic gain is a better prior for this reducer family or a
  correction of G4's weak spots, and anything about learned context (token weights only).

## Starting programs versus ongoing decoder (root 10, runs 2026-10-06-2331 and 2026-10-07-0315)

One run, commit `8f42f38`, complete data (79 200 searches, 3.0 h). The 20 frozen 1723 maps (M)
and G4 (G) on the three 2229 cells (BE `S?m:(M+F)`, PA `(F?S:M)+m`, PA `(S?M:m)+F`), 400 fresh
shared seeds, no learning. Four arms cross the source of the generation-0 programs with the
decoder used during search: GG, MM, MG (MM's exact starting tapes, searched under G) and GM
(GG's exact tapes, searched under M). The tapes are carried across by drawing new alleles
uniformly inside each token's interval in the destination table (conditional-uniform
re-encoding); round trips, a marginal law check, 630 bit-identical historical rows and an M→M
re-encoding control (1.02×, 99% [0.95, 1.09], not an equivalence test) all passed. Paired log2
cost ratios, crossed map/seed bootstrap; pre-registered rows; reviewed analysis. Fairly sure of
the pooled numbers; narrow in scope (three reused screened cells, G4's hand-supplied context,
this population/operator/budget regime).
([17](questions/10-compositional-map-transfer/17-decoder-initialization-variation/question.md),
[analysis](runs/2026-10-06-2331/analysis.md))

- **Both components help, each by about 1.3–1.4× given the other.** Same starting tapes,
  searched under M rather than G: 1.39× [1.31, 1.47] faster. Same search decoder M, starting
  from M's programs rather than G's: 1.30× [1.24, 1.36]. Both lower bounds clear the 1.19×
  margin; both survive dropping capped searches or winsorising at 65 536 (P1 moves ≤ 0.07 log2).
  The full diagonal is 2.29× [2.05, 2.54], reproducing 2229.
- **The two gains are sub-additive.** Starting from G, either component alone gives 1.65×
  (start) or 1.76× (ongoing), 60–68% of the diagonal in log units; the interaction is −0.34 log2
  [−0.40, −0.29] and negative in 20/20 maps. This is sub-additivity on capped log cost,
  consistent with — but not establishing — a shared supply of useful partial programs.
- **Direct solver seeding is unlikely to explain the start gain.** 12 of 79 200 searches solved
  at generation 0; searches take 20–40 generations. Effects are distribution shifts (MG slower
  than MM in 57% of pairs, faster in 39%). Which properties of the starting population carry the
  gain is unresolved.

Second run, 2026-10-07-0315 (commit `5dae3a6`, complete, 122 000 searches, 4.3 h): the same
design on the ten 1723 training cells (4 BE, 6 PA), 200 fresh seeds; all validation passed,
including 786 bit-identical historical rows. Pre-registered rows (row 1); reviewed analysis.
These are the cells the maps were trained and selected on, so this is a screened, in-sample
bank, not a holdout. ([analysis](runs/2026-10-07-0315/analysis.md))

- **Both components replicate on the training cells.** Ongoing decoder given M's start 1.28×
  [1.22, 1.34]; start given ongoing M 1.33× [1.26, 1.40]; diagonal 2.44× [2.23, 2.66];
  interaction −0.52 log2 [−0.62, −0.42], again sub-additive. No label changes under either cap
  sensitivity.
- **On the training cells, the start weighs relatively more on BE cells than on PA cells.** The
  balance S = log2(T_MG/T_GM) (positive: losing the ongoing decoder costs more than losing the
  start) is −0.21 to −0.39 on all four BE cells, each resolved below 0, and −0.05 to +0.54 on the
  six PA cells (three resolved above 0, none below). BE minus PA: −0.45 log2, Welch 95% [−0.68,
  −0.22] over cells; leave-one-cell-out −0.38 to −0.50; 20/20 maps lower on BE cells; S differed
  more between cell families than between map families (descriptive; map-family equivalence and
  the cause of the cell-group difference are not established). The difference is relative: both components
  are resolved positive within each family (P1 on BE about 1.15× [1.08, 1.23]; on PA 1.42×
  [1.34, 1.51]). 2331's withheld BE cell (S −0.27) fits the BE range (different seeds; descriptive).
- **"Family" is not separated from shape or difficulty.** Across the ten cells S correlates with
  MM median cost (r 0.77, post hoc); the two PA cells with the largest S are the two hardest PA
  cells. At matched difficulty the families still separate, but four and six cells from one
  screened bank cannot tell family, branch-else versus plus-arg shape and difficulty tail apart,
  and say nothing about a fresh cell.
- **Not separated (both runs):** mutation versus crossover versus inherited latent alleles within
  "ongoing"; supply of useful programs versus neighbourhood structure; why the balance differs
  between the cell groups; anything about learned context or family specificity of the maps.

## Compact context continuation (root 10, run 2026-10-07-0821)

One run, commit `f61aec4`, complete data (174 964 searches, 2.64 h, all validation passed, no
holdout touched). Ten 1723 training cells (4 BE, 6 PA), G4, D1331. From 16 saved 1723 token maps
(8 BE, 8 PA), two equally funded continuations each, sharing inner seeds: T (token steps only)
and C (each step a token step or, with probability ½, a step on a centred rank-one log-weight
residual over G4's previous-token × next-token table). 2 parents + 6 children per generation,
24 searches per child at the 65k cap, 20 generations, 4 040 searches per arm. Final maps scored
on 50 shared fresh seeds per own-family cell at the 524k cap; family-balanced paired t interval
over 16 starts. A calibration stage first scored single steps from the same kind of start on
two independent seed blocks. Pre-registered rows (row 3); reviewed analysis. Fairly sure of
the numbers; narrow in scope (one loop and budget, token-tuned starts, training cells only).
([18](questions/10-compositional-map-transfer/18-compact-context-learning/question.md),
[analysis](runs/2026-10-07-0821/analysis.md))

- **Adding rank-one context steps gave no resolved training increment over token-only
  continuation at this budget.** C/T 0.955× [0.833, 1.095]; a gain above about 1.10× is
  excluded for this procedure and budget. BE 1.05× [0.84, 1.32], PA 0.87× [0.71, 1.06]
  (descriptive). Pair sd 0.38 log2, above the planned 0.29.
- **Token continuation alone did not resolve learning in this loop either, so the null does not
  test context fairly.** T/S 1.03× [0.90, 1.16], C/S 0.98× [0.90, 1.07]; in-loop parent scores
  flat in both arms (slopes −0.003 and +0.003 log2 per generation, intervals spanning 0) while
  parents were replaced 1.4 times per generation. T/S's upper bound still admits about 5 × 10⁻⁵
  log2 per search, the rate 0811's longer token continuation achieved on another bank (0.54 log2
  over 13 440 searches), so "too shallow" is not excluded.
- **Single context steps have repeatable effects; selected ones beat the average mutant, but
  their difference from the parent was unresolved.**
  True step-effect variance from two independent seed blocks: context 0.047 [0.027, 0.065],
  token 0.028 [0.005, 0.051] log2². The best quarter of 24 mutants (by 48 searches) beat the
  average mutant on new seeds by 0.12 log2 [0.06, 0.18]; their difference from the parent
  was unresolved (−0.017 [−0.085, +0.041]); the average step was harmful (+0.06 context, +0.03 token). Per-child score noise
  (0.33 log2 at 24 searches) exceeds the spread of true step effects (sd 0.17–0.22); that this
  is why neither arm climbed is the reviewer's interpretation, not a measured contrast. Only
  initial steps from a zero residual were calibrated.
- **Descriptive only:** in PA, removing the learned residual made C faster (C/C0 0.91× [0.85,
  0.98], 7/8 pairs; pooled 0.96× [0.90, 1.02]; removal also shifts emitted token frequencies).
  Final residuals had small absolute cosine alignment with the hand-set BE − PA direction
  (≤ 0.105). Observed survival proportions into the parent set ranged from 0.22 to 0.27 across
  operators (token 210/954, b 133/552, a 111/414); these do not measure ranking quality.
- **Not separated:** ineffective context versus a loop too noisy or too short to climb; anything
  about transfer, family specificity, or context learned jointly with tokens from G4. Run 1137
  (next section) supplies a loop that climbs.

## Selection-calibrated continuation (root 10, run 2026-10-07-1137)

One run, commit `86ef669`, complete data (335 700 searches, 4.63 h, all validation passed;
0821's 4 000 fresh S rows reproduced bit-identically; no holdout touched). Same 16 saved 1723
starts (8 BE, 8 PA), cells, G4 and operators as 0821. Changed: every candidate, rescored parents
included, scored on the same 96 new in-loop searches (2 + 6 loop, 12 generations, 9 600 searches
per trajectory, 2.4× 0821's). Stage 1: token-only T, scored on 0821's fresh block F1 and gated
in code on T/S(F1) ≥ 1.10. Stage 2: C (token or rank-one context step, ½ each) on T's in-loop
seeds, all 16 admitted; S, T, C and C0 scored on a new fresh block F2. Family-balanced paired t
intervals, 14 df. Pre-registered rows (row 6); reviewed analysis. Fairly sure of the pooled
numbers; narrow in scope (one loop, these token-tuned starts, training cells only).
([19](questions/10-compositional-map-transfer/19-selection-calibrated-continuation/question.md),
[analysis](runs/2026-10-07-1137/analysis.md))

- **At 96 searches per candidate, token continuation from the saved maps improved fresh training
  search.** T/S 1.143× [1.089, 1.200] on F1 (16/16 starts), 1.122× [1.031, 1.222] on F2 (lower
  bound 1.031–1.047 across sensitivity variants, so close to the row 5 boundary); in-loop parent
  score fell (−0.013 [−0.021, −0.005] log2 per generation, 14/16). 0821's maps from the same
  starts were 1.026× [0.904, 1.165] on F1. Which change made the difference (4× evidence per
  candidate, 12 instead of 20 generations, 2.4× total searches) is not isolated: T96/T24 1.114×
  [0.987, 1.257] is a procedure comparison and unresolved. Learning had not resolved a plateau
  (T/T_mid 1.058× [0.990, 1.130]). F2 re-scores the same learned maps; learning was not
  replicated.
- **In that loop, mixing in rank-one context steps added no resolved increment over token-only
  continuation under equal search funding.** C/T 0.967× [0.871, 1.073]: a mean gain above about
  1.07× is excluded for this loop and these starts; smaller gains and losses up to 13% are not.
  BE 1.04× [0.86, 1.25], PA 0.90× [0.79, 1.03] (descriptive). C/S 1.084× [0.993, 1.184]; C/C0
  1.037× [0.972, 1.107].
- **C's token component was slower in the point estimate; the direction is unresolved**
  (C0/T 0.932× [0.860, 1.010], not pre-stated). C spent half its proposals on context, so it made
  564 token proposals against T's 1 152; their causal contribution to the difference is not isolated. "Context steps neutral but displacing token steps" and "context mildly harmful on PA"
  both fit; the data do not separate them.
- **Per-start gains are not measurable at 50 fresh seeds per cell.** Per-start T/S on F1 and F2
  correlate 0.15; the implied true between-start sd of the token gain is about 0.07 log2. Only
  pooled means are informative; per-family differences are not supported.
- **Descriptive:** accepted children scored 0.14–0.16 log2 better at acceptance than on the next
  independent block (winner's curse about the size of the whole gain); observed survival into the
  parent set 0.22–0.25 for every operator; final residuals' absolute cosine with the hand-set
  BE − PA direction ≤ 0.045.
- **Not tested:** context learned jointly with tokens from G4; context added on top of a full
  token budget; transfer to withheld cells; depth beyond 12 generations.

## Solver-corpus context fit (root 10, run 2026-10-07-1707)

One run, commit `627336d`, complete data (35 240 searches, 81 min; 0315 replay bit-identical,
7 447 solver re-verifications and all table checks passed, no exclusions). Same bank, 1723 split,
D1331, G4, P 256 and 524k cap as 1723–1137. A different learning signal: no search-cost
selection. Per corpus, 48 G4 searches per own training cell (16 corpora per family on disjoint
seeds; 7 408/7 680 solved, every cell ≥ 40/48); the first exact solver's 32-token tape is kept and
transition counts are equalized per cell. Three tables per corpus: **T**, 24 token multipliers on
G4 fitted by maximum likelihood; **C**, the previous-token counts shrunk toward G4's rows (α 50,
frozen from a steward probe on other seeds); **K**, G4 × multipliers matched to C's pooled emitted
token marginal (max error 3.3e−5). Each scored on 32 fresh seeds per cell, shared within corpus;
then all frozen tables on the three withheld cells. Per-corpus contrasts, families weighted
equally, t intervals. Pre-registered rows (row 1); reviewed analysis. Fairly sure of the
numbers; narrow in scope (one bank and split, full-tape fitting, one α, external fitting).
([20](questions/10-compositional-map-transfer/20-solver-corpus-context/question.md),
[analysis](runs/2026-10-07-1707/analysis.md))

- **A previous-token table fitted to solver tapes speeds fresh search beyond a token-only fit to
  the same tapes.** C/T 1.365× [1.288, 1.446] on training cells; BE 1.46× [1.32, 1.61], PA 1.28×
  [1.20, 1.35]; C faster in 31/32 corpora and 129/160 corpus × cell pairs; unchanged with
  unsolved runs charged 1 × instead of 2 × cap (1.360×). Per-corpus sd 0.27 (BE) and 0.16 (PA)
  log2. T here is the likelihood-best token fit, not the search-fastest token map; T was not
  resolved from the 20 search-selected 1723 maps, and these intervals allow appreciable
  differences (BE 0.95× [0.81, 1.11], PA 1.02× [0.81, 1.28], unpaired).
- **The gain transfers to the withheld cells.** C/T 1.293× [1.213, 1.378] over 32 corpora (30/32
  faster); C/G4 2.75×, T/G4 2.13× (unpaired). So this procedure supplies held-out gain beyond a
  token-frequency bias on this bank.
- **Matching C's pooled emitted token frequencies does not reproduce the gain, but that control
  is not neutral.** C/K 1.654× [1.568, 1.744] (32/32 corpora); K is itself slower than T, 0.825×
  [0.776, 0.878] (training) and 0.841× (withheld). C/T, not C/K, is the better size of the
  contextual increment. Position-specific and in-population frequencies were not matched.
- **No matched-family advantage was resolved on any withheld cell.** C fitted on the matched family over C fitted on the other: 1.02×
  [0.91, 1.15] on the single BE withheld cell, 0.75× [0.63, 0.89] and 0.99× [0.89, 1.10] on the PA
  ones; on `(F?S:M)+m` the BE-fitted tables (both T and C) are faster. C's gains extend to both
  families; the carrying structure and modest family preferences remain unresolved, and one BE
  cell cannot refute a BE preference.
- **The tapes carry order information and the fit is cheap.** About 0.45 bits per transition of
  previous-token dependence above a within-tape shuffle, consistently across all 32 corpora. C has
  lower start-row top-token concentration than G4 (0.52–0.63 against 0.69, though also lower
  start-row entropy); the start row's contribution to the speed gain is unmeasured. One corpus costs
  about 12 M evaluations (500 worker-s); C pays it back against G4 in about 120–590 training-cell
  searches (descriptive, at this cap).
- **Not shown:** that evolution or any search-cost learner can reach C (four selection-based
  context procedures gave no resolved gain, 13–19); which structure carries it (specific bigrams,
  executed versus inert tokens, position); how it depends on α (the probe's α 400 was weaker on
  BE). (Whether one refit from C's own solvers helps further: see the next section.)

## Solver-corpus feedback refit (root 10, run 2026-10-07-1924)

One run, commit `5565d54`, complete data (39 976 searches, 73 min; 1707 replay bit-identical; all
32 parent hashes, 224 fitted tables and 22 448 solver re-verifications passed; every stage at
full size). Same bank, split, D1331, G4, P 256 and 524k cap as 1707. Each of the 32 saved 1707
tables C collected 48 searches per own training cell under itself (7 623/7 680 solved, worst
cell 44/48) and was refitted with the unchanged 1707 rule (fit to the new tapes only, shrunk
toward G4 at α 50): **C2**. A fresh G4 corpus per lineage, matched in attempts (7 378/7 680), gave
the one-shot control **C'**. All three scored on 32 shared fresh seeds per cell, then on the three
withheld cells. Per-lineage contrasts, families weighted equally, t intervals. Pre-registered
rows (row 1); reviewed analysis. Fairly sure of the numbers; narrow in scope (one step, one rule,
one bank and split, external fitting).
([21](questions/10-compositional-map-transfer/21-iterated-solver-corpus/question.md),
[analysis](runs/2026-10-07-1924/analysis.md))

- **One feedback refit speeds fresh training search beyond its parent.** C2/C 1.404× [1.347,
  1.464]; BE 1.56× [1.46, 1.66], PA 1.27× [1.20, 1.34]; C2 faster in 32/32 lineages (1.09–1.84×).
  The median-per-cell and solved-only variants give 1.33× and 1.37×. Per paired seed C2 wins about
  58%; the whole cost distribution shifts (median 4 352 → 3 328 evaluations), most in the upper
  tail (unsolved 39 → 14 of 5 120).
- **The increment transfers to the withheld cells.** C2/C 1.289× [1.204, 1.381], 28/32 lineages.
  These three cells were never used in collection or fitting, but they have been inspected in
  several runs and only one is BE.
- **Collecting under C beats a fresh G4-collected refit at matched attempts.** Against the fresh one-shot
  refit, C2/C' is 1.408× [1.342, 1.478] (training) and 1.330× [1.263, 1.401] (withheld); C'/C is
  0.997× [0.940, 1.058] and 0.969× [0.908, 1.035], not resolved from 1 (differences up to about
  6% and 9% not excluded). "Collecting under C" is a procedure: it gave higher yield (99.3%
  against 96.1%), slightly more distinct tapes and possibly different kinds of tapes; these are
  not separated.
- **The refit sharpens the decoder without (yet) hurting transfer.** Body-row entropy 3.91 → 3.80
  bits and previous-token mutual information 0.41 → 0.48 bits, in every lineage; C' has similar
  mean entropy and mutual information to C (3.905 against 3.907 bits; 0.409 against 0.407; no
  equivalence test). Sharpening accompanied the gain; it is not shown to cause it.
  Collection under C costs 0.63 worker-s per search against 2.17 under G4; C2's evaluation saving
  pays back the second round in a median of about 350 training searches (descriptive).
- **Not shown:** whether a second step keeps helping or the sharpening compounds into harm; why
  C2 is faster (no start-row ablation, no active-token analysis; the token-only refit T2 was run
  later, see the next section); how
  often C2 re-emits its own corpus tapes; a C2-over-G4 number (not run; multiplying ratios
  assumes independence); family specificity. On one PA training cell, `(S?M:F)+m`, no gain was
  resolved (0.98× [0.84, 1.13], descriptive among 13 cells; a gain or a loss is not excluded).

## Feedback context increment (root 10, run 2026-10-07-2156)

One run, commit `36c665d`, complete data (16 384 new T searches, 26 min; 128 table hashes, the
16 384 saved C1/C2 rows and 64/64 replays validated; no duplicates; holdout admitted by a
timing-only gate). T1 = 1707's token-only fit, T2 = the token-only fit to the 1924 feedback
corpus (saved in 1924, never scored); both scored on the exact seeds and training indices where
1924 scored C1 (= 1707's C) and C2. 32 lineages, 5 120 training and 3 072 withheld searches per
arm; unsolved 0.3–1.5% per arm, charged 2 × cap. Interaction I = (C2/T2)/(C1/T1); I > 1 means
feedback raised the contextual fit's advantage. Training families weighted equally (15 df);
withheld cells over 32 lineages (31 df). Pre-registered rows; reviewed analysis. Fairly sure of
the training numbers; this extends 1924's seeds, it is not an independent replication.
([22](questions/10-compositional-map-transfer/22-feedback-context-increment/question.md),
[analysis](runs/2026-10-07-2156/analysis.md))

- **On training cells, feedback raised the fitted context's advantage over the token-only fit
  (BE-carried, partly tail-driven).** I = 1.169× [1.093, 1.250]; 25/32 lineages above 1; no
  single lineage carries it (leave-one-out lower bounds 1.08–1.11); stable under 1× or 4× cap
  and dropping unsolved seeds (lowest 1.131× [1.059, 1.209]). BE 1.337× [1.19, 1.50]; PA 1.021×
  [0.953, 1.094], unresolved and inside ±10%. A median-over-seeds variant (not pre-registered)
  gives 1.089× [1.008, 1.177], so part of the mean effect sits in slow or unsolved seeds.
- **The token-only fit also gained from feedback.** T2/T1 1.201× [1.150, 1.255] on training,
  1.186× [1.107, 1.271] on the withheld cells. Of C2's 1.40× over C1 on training, the token-only
  fit matched about 1.20× and the interaction is the remaining 1.17×. In PA the two gains were
  similar (T2/T1 1.24×, C2/C1 1.27×). The context fit still wins after feedback: C2/T2 1.580×
  [1.520, 1.641] training, 1.365× [1.287, 1.447] withheld.
- **On the withheld cells the interaction is unresolved.** I = 1.087× [0.984, 1.200], 21/32
  lineages above 1. This is neither equality nor absence. Between-lineage variance there is about
  1.6× the seed noise, so more seeds on these lineages would not settle it; about 46 new balanced
  lineages would put the lower bound above 1 at the observed effect (about twice that for good
  power).
- **C1/T1 reproduced on 1924's seeds.** 1.352× [1.274, 1.434] against 1707's independent-seed
  1.365×.
- **Not shown:** what the extra contextual advantage is made of (yield, diversity, tape content
  and the fitting rule stay bundled in "feedback"); why it is BE-specific in this sample (one BE
  withheld cell, family not separated from shape or difficulty); anything about token maps in
  general (T is 24 global multipliers over G4's fixed context, fitted by likelihood); a second
  feedback step.

## Open questions

- [10-compositional-map-transfer](questions/10-compositional-map-transfer/question.md) (open,
  root, budget 15, 15 used): can a decoder adapted across related tasks help fresh populations
  solve unseen operation combinations beyond a token-frequency bias? Two feasibility studies
  (one bank failed split/headroom, one failed the two-family requirement but kept a PA split),
  then two learning studies: learned token multipliers on G transfer about 2× to the withheld
  pair and to branch-else; contextual row moves on top add no resolved training gain (≤ 1.11×),
  holdout increment unresolved, and their off-family branch shift did not replicate (14). The
  four-reducer bank failed the symmetric split (15); on a narrower split, crossed token learning
  improves both families about 2.2× on training and 2–3× on the withheld cells, with no resolved
  family advantage there (95% upper bounds 1.25× BE, 1.15× PA; 16, closed). The frozen maps' gain comes from both starting
  programs and ongoing decoder use, about 1.3× each given the other and sub-additive, on the
  withheld and the training cells; the balance differs between BE and PA training cells (17,
  closed). Rank-one context steps mixed into token continuation: no resolved training increment,
  first in a loop where token continuation did not resolve learning (18), then in one where it
  did, C/T 0.967× [0.871, 1.073] (19; 18 and 19 closed). A previous-token table fitted to exact
  solver tapes beat a token-only fit to the same tapes 1.37× on training and 1.29× on the
  withheld cells, no resolved family advantage (20, closed). Refitting those tables to solvers
  found under them gave a further 1.40× on training and 1.29× on the withheld cells, attributable
  to the collection procedure (21, closed). On training cells that feedback step raised C's
  advantage over a token-only fit, I 1.17× [1.09, 1.25], mostly in BE, while the token-only fit
  also improved 1.20×; on the withheld cells I is unresolved, 1.09× [0.98, 1.20] (22, closed).
  15 of 15 slots used.
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
    grammars show a crossed preference that context strengthens over the marginal controls
    (descriptive).
  - [16-crossed-family-adaptation](questions/10-compositional-map-transfer/16-crossed-family-adaptation/question.md)
    (closed, runs 2026-10-06-1723 and 2026-10-06-2229, row 4 both): BE- and PA-trained token maps
    beat G4 about 2.2× on training cells and 2–3× on the three withheld cells; matched over
    mismatched on the withheld cells 1.02× (BE) and 0.96× (PA), 95% upper bounds 1.2485× (about
    1.3× leave-one-map-out) and 1.15×, a
    1.1× preference not excluded.
  - [17-decoder-initialization-variation](questions/10-compositional-map-transfer/17-decoder-initialization-variation/question.md)
    (closed, 2 of 2 slots, runs 2026-10-06-2331 row 3 and 2026-10-07-0315 row 1): with starting
    tapes held identical, the learned decoder during search adds 1.39× [1.31, 1.47] (withheld
    cells) and 1.28× [1.22, 1.34] (training cells); with the search decoder held at M, learned
    starting programs add 1.30× [1.24, 1.36] and 1.33× [1.26, 1.40]; sub-additive in both. On
    the training cells the start weighs relatively more on BE than PA cells (−0.45 log2 [−0.68,
    −0.22]); not separated from shape or difficulty.
  - [18-compact-context-learning](questions/10-compositional-map-transfer/18-compact-context-learning/question.md)
    (closed at tested scope, 1 of 2 slots, run 2026-10-07-0821 row 3, then via 19): rank-one
    context steps mixed into token continuation from the saved maps add no resolved training
    increment; in the loop where token continuation learned, C/T 0.967× [0.871, 1.073]. Context
    learned jointly from G4, or added without displacing token steps, untested.
  - [19-selection-calibrated-continuation](questions/10-compositional-map-transfer/19-selection-calibrated-continuation/question.md)
    (closed, 1 of 2 slots, run 2026-10-07-1137 row 6): at 96 searches per candidate token
    continuation from the saved maps learned, T/S 1.143× [1.089, 1.200] and 1.122× [1.031, 1.222]
    on two fresh blocks; the cause is not isolated from the changed depth and total effort.
  - [20-solver-corpus-context](questions/10-compositional-map-transfer/20-solver-corpus-context/question.md)
    (closed, 1 of 1 slot, run 2026-10-07-1707 row 1): over 32 independent solver corpora, the
    fitted previous-token table beats the token-only fit C/T 1.365× [1.288, 1.446] (training) and
    1.293× [1.213, 1.378] (withheld); no matched-family advantage was resolved on the three
    withheld cells, and one PA cell favoured the mismatched fit; external fitting, not
    evolutionary discovery.
  - [21-iterated-solver-corpus](questions/10-compositional-map-transfer/21-iterated-solver-corpus/question.md)
    (closed, 1 of 1 slot, run 2026-10-07-1924 row 1): refitting each C to exact solvers found
    under it (C2) gives C2/C 1.404× [1.347, 1.464] (training) and 1.289× [1.204, 1.381] (withheld);
    a fresh one-shot G4 refit C' is not resolved from C (0.997× [0.940, 1.058]) and C2/C' is
    1.41× / 1.33×. One step, external fitting; yield, diversity and tape content not separated.
  - [22-feedback-context-increment](questions/10-compositional-map-transfer/22-feedback-context-increment/question.md)
    (closed, 1 of 1 slot, run 2026-10-07-2156, training row 1, holdout row 4; first attempt 2129
    stopped at preparation): I = (C2/T2)/(C1/T1) 1.169× [1.093, 1.250] on training (BE 1.34×
    [1.19, 1.50], PA 1.02× [0.95, 1.09]); T2/T1 1.20×; withheld I 1.087× [0.984, 1.200],
    unresolved. Reopen on a funded replication with about 46–90 new lineages.
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
