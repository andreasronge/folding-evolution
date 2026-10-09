# Log: 01-map-bias

## Seeded 2026-10-04 from prior work

Notebook: [docs/map-bias/notebook.md](../../../docs/map-bias/notebook.md); findings:
[docs/map-bias/findings.md](../../../docs/map-bias/findings.md). Items below are the
root-level history; child questions carry their own logs.

- §1–§2 (commit 67413dd): reframe to GP-map bias; 50M random tapes per decoder setup, AND neighbourhood probe → map bias predicts easy tasks, not hard ones; chem decoder ≈ direct encoding; AND proxy basin is a wide valley (findings items 1–2). [notebook §1–§2](../../../docs/map-bias/notebook.md)
Decision: reframe the core question to GP-map bias in two parts, measure the bias and evolve the bias (README "Core Question"), and run it as a light hobby notebook because the rigor apparatus had grown larger than the findings it supported (2026-09-25). Part 2 (evolve the bias) has not been started.
- §3–§14 (commit e05aa5f): MIN token, lexicase, v3 domains, tagged runs, OR race, varying goals, combine markers → lexicase supplies blocks; tagged runs make transplants safe; crossover merges blocks when the join is cheap, but the advantage is the join's cost (items 3–10). [notebook §3–§14](../../../docs/map-bias/notebook.md)
Decision: stop the first line at §14 because the open follow-on (a join built across a valley) was judged a separate project.
- §15–§16 (commit 7c9cc42, results 90867ad): op_weights frequency knob, XOR → frequency changes how often a part is made, not what is reachable (item 12). [notebook §15–§16](../../../docs/map-bias/notebook.md)
- §17–§26 (commits e3e3ff1 … 08b315e, closed at 3ee1230 and a419d40): valley crossing, XOR without a free join, population-level exactness, crossover v2 and v1c → joins are built by small edits; no valley found; crossover assembly changes XOR discovery (items 13–16). [notebook §17–§26](../../../docs/map-bias/notebook.md)
Decision: close the XOR/valley thread because the join question was answered and no valley was found (3ee1230).
Decision: skip valley-crossing Step 2 and pivot to folding vs direct map bias (2f681a3) because helper signals were weak and any effect would sit inside the range crossover assembly alone moves.
- §27–§28 (commits cd7d463, f483aaf + a86c49c): folding vs direct, nights 1–2 → see [02-fixed-target-sampling](02-fixed-target-sampling/log.md).
Decision: return to the building-block question (shared-helper reuse, Plans/shared-helper-reuse.md) because nights 1–2 answered "which map samples solvers more often", not whether the chemistry helps discover, preserve and reuse parts (826fb68).
- §29 (commits 9848d08, 7141ecf; write-up 441be87, review 26688f4): shared-helper stages 1–3, hand-built shared / partly shared / duplicated forms, seeded populations → shared form persists from 100% and takes over from 50% at L 64/128; from duplicated starts evolution shares A (cheap RECV0) but never factors out a B helper; seed-dup speed was likely helped by tag-0 latent cells. [notebook §29](../../../docs/map-bias/notebook.md)
Decision: test establishment from a small share next (§30) because a newly discovered shared genome starts rare and Fable's 3-seed probe showed it wiped out with crossover on.
- §30–§31 (commits d49f4ec, 8844b6c; write-ups a623cb3, 3587de6, 4d44db3, d8e8725): establishment, dose, reciprocal, few copies, stage 4 → see [03-rare-shared-establishment](03-rare-shared-establishment/log.md) and [04-random-start-discovery](04-random-start-discovery/log.md).
Decision: drop the planned tie-break toward fewer cells because evolved shared forms are not smaller (§31, Fable's twentieth review).
- §32 (commit 805a641): crossover mate (J), latent helper (K), 256 cases (L), more stage-4 seeds (G2) built and committed; results in notebook §32 (dd684f9, 298c1de) → see [04](04-random-start-discovery/log.md) and [05](05-latent-helper/log.md).
Decision: close 05 (latent helper does not help); keep 04 open on the self-mating establishment test.
- Run 2026-10-04-1839 (commit f2e4048): self-mate contest, 240 runs + self-crossover census → shared wins 183/240 vs 34/240 with a selected mate and 75/120 with crossover off; no early loss; no form change under self-crossover. See [06](06-self-mate-establishment/log.md).
Decision: close 06 (barrier is mixing between lineages) and open [07-shared-arrival](07-shared-arrival/question.md) as the last shared-helper experiment, because the line cannot be closed honestly on "shared is rare because it rarely arrives" until arrival and single-copy fixation are measured. After 07 the line is parked or closed and attention moves to part 2 (evolving the bias) or 02.
- Run 2026-10-04-2135 (commit f418c91): shared-arrival census (173.7M children from 50 §32 J self/0.3 final populations) + 100 natural single-copy insertions → exact shared children arrive about 2 per run in established partly populations, all A-only/other, 0 B-helper; 0 of 100 single copies established (≤ 3.6%), all lost within 30 generations. See [07](07-shared-arrival/log.md).
Decision: park 07 (both factors may limit; bounds too broad to call it arrival- or fixation-limited) and park 04, which ends the shared-helper line as 07's stop rule said. Open [08-evolve-bias](08-evolve-bias/question.md) for the README's part 2, because it is the root's only untested half and 02's reopen condition still needs an owner wish that is not recorded.
- Runs 2026-10-05-1510 (blocked), 1558 (commit `cd69bce`), 1705 (`9abc25c`): fit the map's op bias to a threshold family → sampling transfers to the held-out member (4.9× / 8.9×); evolution about 4× faster than uniform, a hand-set scaffold as good, the other family's fit already 3.3× / 1.9×. See [08](08-evolve-bias/log.md); 09 opened.
- Run 2026-10-05-1814 (commit `31d4408`): component test of the other family's vector, 2,000 runs → speed-up replicates (2.73× / 2.02×); INPUT/GT raise carries it on max>2, unresolved on sum>2; its flat sampling rate is a cancellation. See [09](09-generic-bias-speedup/log.md).
Decision: park 09 (tasks disagree, frozen rule) and 08 (follows 09; specificity can at best show "real but small"), and return to strategy because no open sub-question is left under the root, which has 1 experiment left.

## 2026-10-08 — digest condensing (run 2026-10-07-2243): former digest text moved here

The digest was rewritten as current beliefs only (word limit). This is the root-01 sections (map bias itself, building blocks, shared helpers) and the root-01 open-question lines, moved verbatim as it stood before the rewrite; no belief changed. Relative links below are relative to `research/`, not to this folder.

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


## 2026-10-08 — digest condensing (run 2026-10-08-1831): wording moved here

The digest was compressed under its word limit; no belief changed. These root-01 passages were
cut or shortened there and are kept here verbatim. Relative links are relative to `research/`.

- Run 1558 (08): "the post-hoc product model that explained it **failed out of sample**
  (hand-set vector 5.45× / 11.07×, predicted 17× / 22×). Fairly sure of the numbers, narrow in
  meaning."
- Run 1705 (08): "matched beats the other family's fit only 1.66× / 1.80× (not resolved against a
  2× bar, 100 pairs). … Median speed, one evolution setup."
- Run 1814 (09): "on sum>2 both parts beat uniform and neither is resolved against the full
  vector. … Initialization and mutation are coupled, so no mechanism is named; sum>2 open."
- Run 1957 (09): "Its share of the rest-of-vector gain is unknown (R's gain 1.30, 0.71–2.32)."
- Shared helpers header: "hand-built shared, partly shared and duplicated forms".
- Status line: "Status: 03, 05, 06 closed; 02, 04, 07, 08, 09 parked with reopen conditions in
  their question files." (now in the root-01 intro of the digest)

## 2026-10-09 — digest condensing (run 2026-10-09-0843): wording moved here

The digest was compressed under its word limit (3105 → about 2950 words); no belief changed. These
root-01 passages were cut or shortened there and are kept here verbatim. Relative links are
relative to `research/`.

- Run 1558 (08): "the post-hoc product model that explained it failed out of sample".
- Run 1705 (08): "Family specificity unresolved: matched over the other family's fit 1.66× / 1.80×
  (not resolved against a 2× bar)."
- Run 1814 (09): "Its flat sampling rate was a cancellation (INPUT/GT raises solvers 3.2× / 3.9×,
  the rest cuts them to 0.23× / 0.35×)."
- Run 1957 (09): "Its share of the gain is unknown (rest-of-vector gain 1.30, 0.71–2.32)".
- Shared helpers (§31 G, §32 L): "Shared endings are rare (about 4–8 in 100–450 runs, B-helper
  type); shared never loses to duplicated as such (losers end partly shared)."

## 2026-10-09 — digest rewrite (run 2026-10-09-1350): wording moved here

The digest was rewritten under its word limit (3031 → about 2870 words); no belief changed. These
root-01 passages were shortened there and are kept here verbatim. Relative links are relative to
`research/`. Dropped from the digest: the shared-helper line's stop date (2026-10-05) and
"INPUT/GT raises solvers, the rest cuts them" (the cancellation's direction).

```
- **In evolution the fitted bias is about 4× faster than uniform** (4.33× / 3.58×, lower bounds
  2.6×, 1.9×); a hand-set INPUT/GT/aggregator scaffold is within the registered 0.5–2× margin of it
  (0.93×, 1.08×; a broad margin, not equality). Family specificity unresolved (matched over the
  other family's fit 1.66× / 1.80× against a 2× bar). Sampling lift does not predict speed
  (pass-through 0.35–3.2). Median speed, one setup. ([08](questions/01-map-bias/08-evolve-bias/question.md), [run 1705](runs/2026-10-05-1705/analysis.md))
```

```
- **The other family's vector gives a real generic speed-up; on max>2 INPUT/GT alone reproduces it
  within the tested margin.** Pre-registered, 250 pairs: 2.73× (sum>2), 2.02× (max>2) over uniform
  (lower bounds 2.12, 1.45). INPUT/GT alone versus the full vector on max>2: 0.90× [0.71, 1.08]
  (registered 1.5× margin); on sum>2 neither part is resolved against the full vector. Its flat
  sampling rate was a cancellation (INPUT/GT raises solvers, the rest cuts them). Initialization
  and mutation are coupled, so no mechanism is named.
  ([09](questions/01-map-bias/09-generic-bias-speedup/question.md), [run 1814](runs/2026-10-05-1814/analysis.md))
```

```
**Shared helpers** (line stopped 2026-10-05; three outputs on tags 0/1/2 sharing parts A and B;
crossover v2, lexicase, P 1024, L 64). Fairly sure for these layouts; nothing beyond them.
- **Retention is easy; establishment from rare is blocked by mixing between lineages.** A majority
  shared form persists, and the majority form wins (270/270). From 1/32–1/10 with a selected mate
  it was lost in 294/300 runs; with self as mate it won 183/240 contests (selected mate 34/240,
  crossover off 75/120). (§29–§31, [06](questions/01-map-bias/06-self-mate-establishment/question.md))
```

## 2026-10-09 — digest condensing (run 2026-10-09-1743): former digest text moved here

The digest was rewritten under its word limit (3035 → about 2920 words); no belief changed. This
is the section as it stood before the rewrite, verbatim. Relative links are relative to
`research/`. Wording only was shortened (e.g. "a broad margin, not equality" → "not equality"; "hurt by dilution" → "dilute"). The digest header before the rewrite, kept here too:

```
# Digest: what we currently believe, and why

As of 2026-10-09, after run 2026-10-09-1743 (commit `652fde5`). Core question since the
2026-09-25 reframe: *how does the genotype→program map bias what evolution finds and keeps
("arrival of the frequent"), and can that bias be adapted to a task family?* History, superseded
numbers and fuller wording are in the questions' `log.md` files.

Sources: [notebook](../docs/map-bias/notebook.md) (§1–§32; reviews in
[docs/map-bias/reviews/](../docs/map-bias/reviews/)) and [findings](../docs/map-bias/findings.md)
(items 1–17, owner-promoted). §NN is a notebook section. Exploratory hobby work, mostly 30–50
seeds per cell; pre-registration is noted where it applies. Ratios are speed (> 1 = first arm
faster) with 95% intervals unless stated.

## 01 Map bias (root open, budget spent)

[01](questions/01-map-bias/question.md). Chem-tape and TAG alphabets, threshold and fixed-target
tasks. 03, 05, 06 closed; 02, 04, 07, 08, 09 parked with reopen conditions in their question files.

**Measuring the bias.**
- **Random-genotype frequency predicts which tasks are easy, not which hard ones get solved.**
  Evolution routinely finds behaviours rarer than 1 in 50M random tapes; on the chem-tape alphabet
  chem decoder and direct encoding have almost the same bias. ([item 1](../docs/map-bias/findings.md), §1)
- **Folding's advantage over direct encoding on fixed targets looks like sampling**: where the maps
  differ, folding makes exact solvers 1.3–30× more common and solves more often, and evolution was
  mostly a worse sampler than random search (one exception). Not general: on TAG threshold tasks
  with lexicase every arm solved 9–40× sooner than computed (not run) random search. Steering
  untested. ([item 17](../docs/map-bias/findings.md), §27–§28; [02](questions/01-map-bias/02-fixed-target-sampling/question.md), parked)
- **The frequency knob changes how often a part is made, not what is reachable**: weighting one op
  switches between equivalent routes without changing solve rates; very high weights hurt by
  dilution. ([item 12](../docs/map-bias/findings.md), §16, §19)

**Fitting the bias to a threshold family** (sum/max > k, TAG, lexicase, crossover v2, L 64, P 1024).
- **In sampling, a fitted `op_weights` vector transfers to a held-out member**: 4.9× (sum>2) and
  8.9× (max>2) more exact solvers than uniform, against 1.0× / 1.3× for the other family's fit;
  mainly the aggregator weight. One seed, one fit; the post-hoc product model failed out of sample.
  Numbers solid, meaning narrow. ([08](questions/01-map-bias/08-evolve-bias/question.md), [run 1558](runs/2026-10-05-1558/analysis.md))
- **In evolution the fitted bias is about 4× faster than uniform** (4.33× / 3.58×, lower bounds
  2.6×, 1.9×); a hand-set INPUT/GT/aggregator scaffold is within the registered 0.5–2× margin of it
  (0.93×, 1.08×; broad, not equality). Family specificity unresolved (1.66× / 1.80× over the other
  family's fit, against a 2× bar). Sampling lift does not predict speed (pass-through 0.35–3.2).
  Median speed, one setup. ([08](questions/01-map-bias/08-evolve-bias/question.md), [run 1705](runs/2026-10-05-1705/analysis.md))
- **The other family's vector gives a real generic speed-up; on max>2 INPUT/GT alone reproduces it
  within the tested margin.** Pre-registered, 250 pairs: 2.73× (sum>2), 2.02× (max>2) over uniform
  (lower bounds 2.12, 1.45); INPUT/GT alone versus the full vector on max>2 0.90× [0.71, 1.08]
  (registered 1.5× margin); on sum>2 neither part is resolved against the full vector. Its flat
  sampling rate was a cancellation. Initialization and mutation are coupled; no mechanism named.
  ([09](questions/01-map-bias/09-generic-bias-speedup/question.md), [run 1814](runs/2026-10-05-1814/analysis.md))
- **On sum>2 the exact max>2 shortcut is used as a last step but is not needed** (pilot, 50 seeds):
  the solver's parent in 55/60 exposed runs; barring it delays 49/55 pairs but 100/100 still solve.
  Its share of the gain is unknown (1.30, 0.71–2.32); not a null on the stepping stone.
  ([09](questions/01-map-bias/09-generic-bias-speedup/question.md), [run 1957](runs/2026-10-05-1957/analysis.md))

**Building blocks (chem-tape, tagged runs).** Lexicase, not a new primitive, supplies blocks;
arrangement is then the bottleneck. Tagged transplants are safe (0 crashes in 940); crossover
merges blocks when the join is cheap, but a one-op-join stack does as well, so the advantage is the
join's cost, not modularity. XOR/valley thread closed: joins are built by small edits, no valley found.
([items 4–16](../docs/map-bias/findings.md), §3–§26)

**Shared helpers** (three outputs on tags 0/1/2 sharing parts A and B; crossover v2, lexicase,
P 1024, L 64). Fairly sure for these layouts; nothing beyond them.
- **Retention is easy; establishment from rare is blocked by mixing between lineages.** A majority
  shared form persists and wins (270/270). From 1/32–1/10 with a selected mate it was lost in
  294/300 runs; with self as mate it won 183/240 contests (selected mate 34/240, crossover off
  75/120). (§29–§31, [06](questions/01-map-bias/06-self-mate-establishment/question.md))
- **Crossover is also what solves, but discovery needs no lineage mixing**: random starts solve
  48–50/50 with crossover, 0–4/50 without; self-mating solves 68–80% by generation 3000, about 3×
  slower than a selected mate. A helper already in the host does not rescue a rare shared form.
  (§31 G, §32 J–K; [04](questions/01-map-bias/04-random-start-discovery/question.md) parked, [05](questions/01-map-bias/05-latent-helper/question.md) closed)
- **Solutions arrive mostly partly shared or duplicated, and the first established form is kept**
  (121/129). Shared endings are rare (about 4–8 in 100–450 runs); shared never loses to duplicated
  as such. Shortcuts are structural: about a third of each final population fits training without
  being exact (9/35 runs still so at 256 cases). (§31 G, §32 L)
- **Why shared endings are rare is unresolved.** Exact shared children arrive (about 2 per run, all
  A-only/other); single copies drift out (0/100 established, ≤ 3.6%); no B-helper in 30M children
  (≤ 1.2e-7). 100 insertions cannot tell drift from a disadvantage.
  ([07](questions/01-map-bias/07-shared-arrival/question.md), parked; [03](questions/01-map-bias/03-rare-shared-establishment/question.md) closed)
```

## 2026-10-09 — digest condensing (run 2026-10-09-2033): former digest text moved here

The digest was rewritten under its word limit (3058 → about 2930 words); no belief changed. This
is the section as it stood before the rewrite, verbatim. Relative links are relative to
`research/`. Dropped from the digest: "(not run)" on the computed random search (item 17); "(pass-through
0.35–3.2)" for sampling lift versus speed (08, run 1705); "Its flat sampling rate was a cancellation" (09,
run 1814); "not a null on the stepping stone" (09 pilot, covered by "its share of the gain is unknown"); the
XOR/valley sentence was reworded.

```
## 01 Map bias (root open, budget spent)

[01](questions/01-map-bias/question.md). Chem-tape and TAG alphabets, threshold and fixed-target
tasks. 03, 05, 06 closed; 02, 04, 07, 08, 09 parked (reopen conditions in their question files).

**Measuring the bias.**
- **Random-genotype frequency predicts which tasks are easy, not which hard ones get solved.**
  Evolution routinely finds behaviours rarer than 1 in 50M random tapes; on chem-tape, chem decoder
  and direct encoding have almost the same bias. ([item 1](../docs/map-bias/findings.md), §1)
- **Folding's advantage over direct encoding on fixed targets looks like sampling**: where the maps
  differ, folding makes exact solvers 1.3–30× more common and solves more often; evolution was
  mostly a worse sampler than random search (one exception). Not general: on TAG threshold tasks
  with lexicase every arm solved 9–40× sooner than computed (not run) random search. Steering
  untested. ([item 17](../docs/map-bias/findings.md), §27–§28; [02](questions/01-map-bias/02-fixed-target-sampling/question.md), parked)
- **The frequency knob changes how often a part is made, not what is reachable**: weighting one op
  switches between equivalent routes without changing solve rates; very high weights dilute.
  ([item 12](../docs/map-bias/findings.md), §16, §19)

**Fitting the bias to a threshold family** (sum/max > k, TAG, lexicase, crossover v2, L 64, P 1024).
- **In sampling, a fitted `op_weights` vector transfers to a held-out member**: 4.9× (sum>2) and
  8.9× (max>2) more exact solvers than uniform, against 1.0× / 1.3× for the other family's fit;
  mainly the aggregator weight. One seed, one fit; a post-hoc product model failed out of sample.
  Numbers solid, meaning narrow. ([08](questions/01-map-bias/08-evolve-bias/question.md), [run 1558](runs/2026-10-05-1558/analysis.md))
- **In evolution the fitted bias is about 4× faster than uniform** (4.33× / 3.58×, lower bounds
  2.6×, 1.9×); a hand-set INPUT/GT/aggregator scaffold is within the registered 0.5–2× margin of it
  (0.93×, 1.08×; not equality). Family specificity unresolved (1.66× / 1.80× over the other
  family's fit, against a 2× bar). Sampling lift does not predict speed (pass-through 0.35–3.2).
  Median speed, one setup. ([08](questions/01-map-bias/08-evolve-bias/question.md), [run 1705](runs/2026-10-05-1705/analysis.md))
- **The other family's vector gives a real generic speed-up; on max>2 INPUT/GT alone reproduces it
  within the tested margin.** Pre-registered, 250 pairs: 2.73× (sum>2), 2.02× (max>2) over uniform
  (lower bounds 2.12, 1.45); INPUT/GT alone versus the full vector on max>2 0.90× [0.71, 1.08]
  (registered 1.5× margin); on sum>2 neither part is resolved. Its flat sampling rate was a
  cancellation; initialization and mutation are coupled, so no mechanism is named.
  ([09](questions/01-map-bias/09-generic-bias-speedup/question.md), [run 1814](runs/2026-10-05-1814/analysis.md))
- **On sum>2 the exact max>2 shortcut is used as a last step but is not needed** (pilot, 50 seeds):
  the solver's parent in 55/60 exposed runs; barring it delays 49/55 pairs but 100/100 still solve.
  Its share of the gain is unknown (1.30, 0.71–2.32); not a null on the stepping stone.
  ([09](questions/01-map-bias/09-generic-bias-speedup/question.md), [run 1957](runs/2026-10-05-1957/analysis.md))

**Building blocks (chem-tape, tagged runs).** Lexicase, not a new primitive, supplies blocks;
arrangement is then the bottleneck. Tagged transplants are safe (0 crashes in 940); crossover
merges blocks when the join is cheap, but a one-op-join stack does as well, so the advantage is the
join's cost, not modularity. XOR/valley thread closed: joins are built by small edits, no valley
found. ([items 4–16](../docs/map-bias/findings.md), §3–§26)

**Shared helpers** (three outputs on tags 0/1/2 sharing parts A and B; crossover v2, lexicase,
P 1024, L 64). Fairly sure for these layouts; nothing beyond them.
- **Retention is easy; establishment from rare is blocked by mixing between lineages.** A majority
  shared form persists and wins (270/270). From 1/32–1/10 with a selected mate it was lost in
  294/300 runs; with self as mate it won 183/240 contests (selected mate 34/240, crossover off
  75/120). (§29–§31, [06](questions/01-map-bias/06-self-mate-establishment/question.md))
- **Crossover is also what solves, but discovery needs no lineage mixing**: random starts solve
  48–50/50 with crossover, 0–4/50 without; self-mating solves 68–80% by generation 3000, about 3×
  slower than a selected mate. A helper already in the host does not rescue a rare shared form.
  (§31 G, §32 J–K; [04](questions/01-map-bias/04-random-start-discovery/question.md) parked, [05](questions/01-map-bias/05-latent-helper/question.md) closed)
- **Solutions arrive mostly partly shared or duplicated, and the first established form is kept**
  (121/129). Shared endings are rare (about 4–8 in 100–450 runs); shared never loses to duplicated
  as such. Shortcuts are structural: about a third of each final population fits training without
  being exact (9/35 runs still so at 256 cases). (§31 G, §32 L)
- **Why shared endings are rare is unresolved.** Exact shared children arrive (about 2 per run, all
  A-only/other); single copies drift out (0/100 established, ≤ 3.6%); no B-helper in 30M children
  (≤ 1.2e-7). 100 insertions cannot tell drift from a disadvantage.
  ([07](questions/01-map-bias/07-shared-arrival/question.md), parked; [03](questions/01-map-bias/03-rare-shared-establishment/question.md) closed)

```

## 2026-10-10 — digest condensing (steward task 2026-10-09-2303): former digest text moved here

The digest was rewritten under its word limit (3009 → about 2890 words); no belief changed. Dropped
from this root's section: the post-hoc product model that failed out of sample (run 1558); the
scaffold-versus-fitted ratios 0.93× and 1.08× (run 1705); "registered" before the 1.5× margin
(run 1814; the margin is still pre-registered). Former 08/09 bullets, verbatim, links relative to
`research/`:

```
**Fitting the bias to a threshold family** (sum/max > k, TAG, lexicase, crossover v2, L 64, P 1024).
- **In sampling, a fitted `op_weights` vector transfers to a held-out member**: 4.9× (sum>2) and
  8.9× (max>2) more exact solvers than uniform, against 1.0× / 1.3× for the other family's fit;
  mainly the aggregator weight. One seed, one fit; a post-hoc product model failed out of sample.
  Numbers solid, meaning narrow.
  ([08](questions/01-map-bias/08-evolve-bias/question.md), [run 1558](runs/2026-10-05-1558/analysis.md))
- **In evolution the fitted bias is about 4× faster than uniform** (4.33× / 3.58×, lower bounds
  2.6×, 1.9×); a hand-set INPUT/GT/aggregator scaffold is within the registered 0.5–2× margin of it
  (0.93×, 1.08×; not equality). Family specificity unresolved (1.66× / 1.80× over the other
  family's fit, against a 2× bar). Sampling lift does not predict speed. Median speed, one setup.
  ([08](questions/01-map-bias/08-evolve-bias/question.md), [run 1705](runs/2026-10-05-1705/analysis.md))
- **The other family's vector gives a real generic speed-up; on max>2 INPUT/GT alone reproduces it
  within the tested margin.** Pre-registered, 250 pairs: 2.73× (sum>2), 2.02× (max>2) over uniform
  (lower bounds 2.12, 1.45); INPUT/GT alone versus the full vector on max>2 0.90× [0.71, 1.08]
  (registered 1.5× margin); on sum>2 neither part is resolved. Initialization and mutation are
  coupled, so no mechanism is named.
  ([09](questions/01-map-bias/09-generic-bias-speedup/question.md), [run 1814](runs/2026-10-05-1814/analysis.md))
- **On sum>2 the exact max>2 shortcut is used as a last step but is not needed** (pilot, 50 seeds):
  the solver's parent in 55/60 exposed runs; barring it delays 49/55 pairs but 100/100 still solve.
  Its share of the gain is unknown (1.30, 0.71–2.32).
  ([09](questions/01-map-bias/09-generic-bias-speedup/question.md), [run 1957](runs/2026-10-05-1957/analysis.md))
```
