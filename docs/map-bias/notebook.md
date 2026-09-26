# Map-bias notebook

Lab notebook for the reframed core question (see README): how does the genotype→program
map bias what evolution finds? Hobby mode — one paragraph before, plain results after.

---

## 1. Arrival of the frequent on chem-tape (2026-09-25)

**What would be interesting to see:** if the behaviours random tapes hit often are the ones
evolution ends up on, the old proxy-basin story is just "the proxy is common, the solution is rare."

**Setup.** `experiments/chem_tape/arrival_frequent.py`, run on top of commit `d41d1e5`
(script not yet committed at run time). 50M uniform random tapes per decoder setup
(61 setups), decoded and executed on each task's seed-0 training inputs (64 examples).
"Behaviour" = the 64-long prediction vector. Then the best genotype of all 1,230 past
fixed-task runs was re-scored on the same inputs. Output:
`experiments/output/2026-09-25/arrival_frequent/` (`summary.md`, two plots). About 2 h on 10 cores.

**Results.**

1. **The maps are extremely biased.** One behaviour (a constant output) takes 66–88% of
   random tapes; only 22–636 distinct behaviours show up out of 50M tapes. Rank-frequency
   falls roughly as a power law with steps.
2. **Chem decoder and direct Arm A have almost the same bias.** Their rank-frequency curves
   overlap, and P(solve) differs by at most ~2× between them on the same task. At the level
   of behaviour, the "developmental" decoder hardly changes what is common. Same-task
   decoder pairs predicted solve-rate order in only 3/6 cases — no signal.
3. **Common solutions are always found; rare ones sometimes are.** If ≥ ~5e-5 of random tapes
   solve the task, evolution solves it 90–100% of the time. Below ~1e-6 (or never seen in 50M),
   solve rates range from 0 to 0.85. Spearman rho = 0.89 across setups, but that is mostly
   "easy tasks are easy."
4. **Evolution routinely finds behaviours rarer than 1 in 50M.** v1 `sum_gt_5`: no random tape
   scored ≥0.8, yet 85% of runs solved it. Frequency is not a ceiling — cumulative selection
   climbs where there is a gradient.
5. **The proxy basin reads as arrival of the frequent.** On `sum_gt_10_AND_max_gt_5`, ~5e-5
   of random tapes already sit at 0.92 (the single-predicate proxy) and none at ≥0.95; 0/100
   runs solve it. Decorrelating the proxy drops P(fit≥0.8) to ~1e-6 and solve rate rises to
   5–15%. Dual decorrelation removes it entirely but solve rate stays 0–5%, so rarity of the
   proxy is not the whole story.
6. **Stuck runs lean toward the common behaviour, but less than pure frequency would.**
   Among 479 runs with ≥2 sampled behaviours at or above their fitness, the evolved one was
   the most frequent in 326. Uniform-choice null: 169. Frequency-proportional null: 416.
   So evolution sits between "pick at random" and "pick by frequency."

**Take.** Bias matters (points 1, 5, 6) but it is not destiny (point 4). The interesting
cases are the ones where evolution beats the bias — what does the path look like there?
And point 2 says chem-tape's decoder is too close to direct encoding to show map effects;
a map comparison needs maps that actually differ (folding, tree GP).

**Caveats.** Behaviour measured on seed-0 inputs only, while runs trained on their own seed's
inputs. Past runs span different budgets and eras (v1 vs v2 alphabets). "Unseen" means < 2e-8.

**Next ideas.**
- Trace lineages in the solved-but-rare cases (v1 `sum_gt_5`, `sum_gt_10_v2`): which stepping
  stones were climbed, and how common was each?
- Run the same sampling on the folding map and a tree-GP generator, where biases should
  differ much more than chem-tape vs Arm A.

---

## 2. Is the AND proxy one or two steps from a solution? (2026-09-26)

**What would be interesting to see:** if a solver sits 1–2 mutations from the stuck
genomes, a smarter operator is enough. If not, the missing piece is a whole building block.

**Setup.** `experiments/chem_tape/and_neighbourhood.py`. The 40 stuck best genomes on
`sum_gt_10_AND_max_gt_5` (20 Arm A + 20 BP_TOPK, pop 1024 × 1500 gens). Every single
mutation (672 per genome) and every double mutation (218,736 per genome) was scored on
the seed-0 inputs. About 40 s on 10 cores.

**Results.**

1. **No solver within two mutations, in any of the 40 genomes.** None of the 8.7M
   neighbours even scores above the parent's fitness (0.922 for the `max>5` proxy). The
   proxy is a strict local optimum out to radius 2. 50–88% of single mutations are neutral,
   so the plateau is wide, but it leads nowhere within two steps.
2. **The gap is a whole missing block, not a bit of glue.** Building the canonical solution
   (`CONST_0 INPUT REDUCE_MAX CONST_5 GT INPUT SUM CONST_5 CONST_5 ADD GT IF_GT`) from the
   proxy one token at a time gives fitness
   0.922 → 0.922 (`CONST_0`) → 0.50 → 0 → 0 → 0 → 0 → 0.72 → 1.0.
   All six genomes between the proxy and the solution score below the proxy (0.50, 0, 0,
   0, 0, 0.72), because a half-built `sum>10` block leaves junk on top of the stack. The `sum>10` block (6 tokens) is simply not in the genome.

**Take.** Mutation can't cross this. What would: a crossover that can bring in a whole
`sum>10` block from another individual in one step, plus `IF_GT`. That only works if the
population still holds that block, and each run collapses onto one proxy. Next idea: task
switching between `max>5`, `sum>10` and AND to keep both blocks alive (Kashtan & Alon's
modularly varying goals), plus a whole-program combining crossover with random glue.
