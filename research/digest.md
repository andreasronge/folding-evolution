# Digest: what we currently believe, and why

As of 2026-10-05 (last commit `f418c91`, run 2026-10-04-2135). This covers the **map-bias line**, the current
core question since the 2026-09-25 reframe: *how does the genotype→program map bias what
evolution finds and keeps ("arrival of the frequent")?* Until 2026-10-05 the line studied
whether the chemistry can discover, preserve and reuse a **shared helper** (one functional part
read by several outputs); that line has stopped, and the next one is the README's part 2,
fitting the map's bias to a task family ([08](questions/01-map-bias/08-evolve-bias/question.md)).

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
  where solvers are rare but the plateau is not deceptive. (item 17 "Night 2", §28)
- **The frequency knob changes how often a part is made, not what is reachable.** Weighting
  one op switches between equivalent routes (e.g. min vs gate joins, 13:1 vs 2:14) without
  changing solve rates; very high weights hurt only by diluting the rest of the alphabet.
  ([item 12](../docs/map-bias/findings.md), §16, §19; also the `rest` weight in §28)
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

## Open questions

- [01-map-bias](questions/01-map-bias/question.md) (open, root): how does the map bias what
  evolution finds and keeps?
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
- [08-evolve-bias](questions/01-map-bias/08-evolve-bias/question.md) (open, new): the README's
  part 2. Can the map's frequency bias be fitted to a task family and help evolution on unseen
  members? First experiment proposed in run 2026-10-05-0040.

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
