# Map-bias pivot: arrival of the frequent on folding vs direct encoding

Status: planned 2026-09-30 (fifteenth review, findings Open). Night 1 queue:
`experiments/map_bias/queue_pivot1.yaml`; code `experiments/map_bias/fold_direct.py`.

## Question

Does a genotype→program map bias what evolution finds? Chem-tape can't answer it: its
decoder has nearly the same behaviour bias as direct encoding (findings item 1). The
folding map (`phenotype.develop`) and direct encoding (`direct.develop_direct`) share the
62-character alphabet, the operators and the evaluator; only genotype → program differs.
The folding track showed they differ in static properties (neutrality, breaks) but never
measured item 1's quantity: how often each behaviour arises from random genotypes.

A behaviour is a program's output vector (a canonical `repr` per context: functions, which
direct encoding can return, become `<fn>`; no memory addresses) on the 8 discriminating
contexts of `exp_task_verification_strict.make_discriminating_contexts`. Tasks: that file's
`CANDIDATE_TASKS` (count, count∘rest, count∘filter, a sum of two filtered counts) plus
`count(expenses)`: 11 tasks, 1–6 intended bonds.

## Phase A — does the bias differ? (no evolution)

- 20M uniform random genotypes per map at lengths 30, 50, 80, 120, 200 (paired: the same
  genotypes go through both maps). Lengths up to 200 because evolved genotypes drift in
  length (cut at 200). Program sources counted on the first 500k.
- Measures per map: distinct behaviours, top-1 share, share with no output (None) and with
  constant output, P(exact) and P(fitness ≥ 0.75) per task.
- Across maps: Spearman rho of log frequency over well-sampled behaviours (≥ 100 in either
  map), with and without constant outputs; top-20 overlap; P(exact) ratio per task.
- Pilot (200k per length): fold 481 behaviours vs direct 288 at length 50; None 74% vs
  43%; P(exact) fold/direct 4–6× on count tasks, 25× on count∘rest, 0 for both on filter
  tasks; rho over well-sampled behaviours 0.2–0.8 depending on length.
- **Kill branch:** rho > 0.9, the same top behaviours, and P(exact) within ~2× on every
  task → folding isn't a different-bias map at the behaviour grain; next would be a tree-GP
  generator or a structural phenotype (the program-source counts are a first look).
  The pilot already shows ratios of 4–25×, so the kill branch is unlikely on P(exact).

## Phase B — does evolution follow each map's own bias? (one night)

- Arms: 11 tasks × 2 maps × 3 budgets (pop × gens: 50×300 as in the old folding
  experiments, 200×1000, 500×2000) × 50 seeds, at start lengths 50 and 80. Same start
  population for both maps within a (task, budget, seed), so arms are paired by seed.
- Baselines: each run's generation-0 best behaviour (the start bias), and random search
  with the 200×1000 budget (fresh random genotypes at the start length every generation,
  best 200 kept): how far each map's bias carries the endpoint without evolution.
- Loop as `exp_2x2.run_stable`: tournament 3, crossover 0.7 (else one mutation:
  point / insertion / deletion), (μ+λ) truncation on fitness. Fitness =
  `dynamics.evaluate_multi_target` on one target (mean partial credit, 0 if the output is the
  same on every context). Genotypes are cut to 200 characters (bloat guard; not in the old
  loop).
- Solved = some individual exact on all 8 contexts (`==` and same type) at any generation.
  Recorded per run: first exact generation, endpoint behaviour and genotype, final exact
  members, final top behaviours, mean length.
- Readouts:
  1. Per task and budget: solve rates fold vs direct next to Phase A's P(exact) — does the
     map with more random solvers solve more often? McNemar on seed pairs.
  2. **Own-map steering:** for seed pairs where neither map ever solved, d = log10 P_fold(b)
     − log10 P_direct(b) of each endpoint behaviour b, with frequencies at the sampled length
     nearest the endpoint genotype's length (unseen floored at 0.5/n). Steering predicts
     d(fold run) > d(direct run): one-sided Wilcoxon signed-rank on the pairs, read against
     the same statistic at generation 0 and under random search. Steering *by evolution*
     means the evolved separation exceeds both baselines.
  3. Endpoint rank among own-map behaviours at or above its fitness vs a uniform-choice
     baseline (item 1's test).
- Cost: ~50 s per 500×2000 run (pilot); Phase A ~30–45 min, Phase B ~2 h (start length
  50) and ~3 h (80); ~6 h in all on 10 cores.

## What changes the plan

- Phase A kill → tree-GP generator or structural phenotype next.
- Phase A differs and readout 2 shows own-map steering → the first positive map-bias
  result; next, the cases where evolution beats its own bias (item 1's point 4), traced on
  lineages.
- Phase A differs, readout 1 follows P(exact) but readout 2 is null → frequency sets which
  tasks are easy (as item 1) but not where evolution gets stuck; the question narrows to
  accessibility.
- Everything null → the folding map's bias doesn't steer evolution at this grain.

## Caveats known in advance

- Filter tasks may have P(exact) = 0 in 50M under both maps; they still contribute
  unsolved endpoints to readout 2.
- Readout 2's length matching is to the nearest of five sampled lengths; mean and best
  genotype lengths are recorded.
- Fitness gives a bool output full partial credit where an int is expected (True == 1);
  exactness requires the same type. Such runs count as unsolved.
- 18 cells of readout 1 and up to 66 of readout 2: treat single p-values as descriptive;
  look for consistent direction across tasks and budgets.
