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

---

## 3. Crossing the AND valley: MIN token vs lexicase vs v3 domains (2026-09-26)

**What would be interesting to see:** which of three ideas gets evolution across the
AND valley — the missing primitive (MIN token), keeping specialists alive (lexicase),
or a chemistry where a block can arrive silently and be switched on in one step (v3).
Suggested by a Fable review of the v3 design.

**Setup.** `experiments/chem_tape/sweeps/mapbias/and_jump.yaml`, 30 seeds per setup,
`sum_gt_10_AND_max_gt_5`, pop 1024 × 1500 gens, same seeds in every setup.
- baseline: current chem decoder (BP_TOPK k=3), tournament.
- min: same + a `MIN` token (id 22, alphabet `v2_min`).
- lexicase: same as baseline, lexicase selection over the 64 training cases.
  **Not standard lexicase** — see "Review and corrections" below.
- v3: `chem_tape/domains.py`. Linker tokens split the tape into domains; each domain
  runs on its own stack; linkers are SILENT / ADD / GT / MIN / MAX / GATE; a silent
  linker skips only its own domain.
Analysis: `experiments/chem_tape/analyze_and_jump.py`. About 23 min on 10 cores.

**Results.**

| setup | solved | median best |
|---|---|---|
| baseline | 1/30 | 0.922 |
| min | 1/30 | 0.922 |
| lexicase | **14/30** | 0.984 |
| v3 | 2/30 | 0.922 |

1. **Lexicase is the big lever.** 14/30 with no change to the chemistry. Solvers
   generalise (median holdout 0.988). 13 of 14 solving programs end in a single `GT`
   comparison, so evolution seems to find its own AND — some arithmetic score compared
   to a threshold — rather than the canonical `IF_GT` form. (Reading, not yet verified.)
2. **The missing primitive is not the issue.** Adding `MIN` gave 1/30, same as baseline.
3. **v3 did not produce the silent-then-switch jump.** 2/30, and in neither solve did the
   best genome carry a silent `sum>10` or `max>5` domain before the jump; the domains
   just before solving were mixed "other" computations. With tournament selection the
   `sum>10` block never forms silently — Fable's hitchhiking prediction.
4. The baseline got its first ever solve (seed 27, gen 1411) — so "0/100" is really
   "rare", about 1 in 30–130.

**Take.** What mattered was *which individuals survive*, not the chemistry: lexicase
keeps alive the individuals that get the ~8% of cases the proxy fails, and those carry
the second half of the answer. The chemistry only helps if something keeps the needed
block alive. Next obvious cell: v3 + lexicase — does the silent route appear once the
`sum>10` block has a reason to exist?

**Review and corrections (second Fable review, same day).**
- **The lexicase variant adds niching.** `_lexicase_select` picks a surviving *behaviour
  group* uniformly, then a member. Standard lexicase picks a surviving *individual*
  uniformly. So a group of 1 got the same parent share as a group of 800. The 14/30 is
  "lexicase + behaviour-level niching"; how much of it is lexicase alone is unknown.
- **This task has an arithmetic shortcut, so it may not need a jump at all.** Both
  predicates are monotone, so their AND is nearly linearly separable: `sum + 10·max > 70`
  scores 98.6% on all 10,000 length-4 lists (95.3% on the seed-0 training set). 13 of 14
  lexicase solvers ending in one `GT` fits a smooth arithmetic walk, not a jump.
- **Silent route estimate (Fable).** A silent block dies mainly from its own tokens being
  mutated (~1 − 0.97⁶ ≈ 17%/gen), not from its lineage drifting out. That gives
  silent : direct ≈ 1 : 80, independent of the mutation rate. Only a faster linker mutation
  rate or a decay-free reservoir changes it. Elitism could be that reservoir, but a neutral
  child never displaces the incumbent elite on a tie, so it never gets seeded.

**Bugs found on the way.**
- Fixed: the Rust executor had no `v2_split` dispatch, so `SUM_LEFT2`/`SUM_RIGHT2` ran as
  NOPs. The old `split_and` sweeps (experiments-v2.md) were unsolvable as run — the
  canonical body scored 0.5 instead of 1.0. Those 0/20 results are invalid.
- Not fixed: the BP/BP_TOPK decoders use the v1 separator mask for every alphabet, so
  under v2 `MAP_EQ_E` (14) and `CONST_2` (15) act as separators and never execute, while
  the intended separators 20/21 bond through. Affects every v2 chem-decoder run; left
  as-is so new runs stay comparable.

---

## 4. Plan: a fair test of jumps and crash-free recombination (2026-09-26)

Entry 3 showed that the AND task can probably be solved by a smooth arithmetic walk, so it
cannot tell whether a chemistry helps evolution *jump*. The plan, in order:

1. **Fix lexicase to the standard version** (uniform over surviving individuals). Re-run the
   30 seeds with both variants, standard and niching, to see what the niching contributed.
   About 10 min of compute.
2. **Parent tracking + lineage labels.** Record each child's parents and how it was made
   (crossover / mutation). Tracking uses no random numbers, so re-running the solved seeds
   reproduces them exactly. Label every fitness-raising step on the path to each solver, and
   for crossover steps record child fitness against both parents and whether both parents'
   expressed blocks survive in the child. That gives the real jump routes and the real
   crash spectrum.
   - Mutation-only arithmetic walks → retire this task for jump questions.
   - Crossover steps that merge two parents' blocks with only a small drop → keep it; v3 vs
     baseline under lexicase is then a fair comparison.
3. **Fix the separator bug** (decoders use v1 masks under v2 alphabets). New testbeds don't
   need comparability with the old runs.
4. **Testbeds with no arithmetic shortcut**, scored on all 10,000 lists so an approximate
   threshold can't pass:
   - `(max>5) XOR (sum>10)`.
   - **Modify-after-arrival curriculum:** donors evolve `sum>5`, the target needs `sum>10`,
     so a transplanted block must be edited after it arrives (`CONST_5` → `CONST_5 CONST_5
     ADD`). This is the one setting where silent insertion *should* beat direct insertion.
5. **Then compare chemistries** (baseline vs v3 domains+linkers, under standard lexicase),
   reporting solves against evaluations rather than a solve count at a fixed budget. v3
   additions to try, cheapest first: domain-transplant crossover (one whole domain, inserted
   at a domain boundary with its own linker); a higher mutation rate on linker cells; elite
   ties broken toward the newer genome, so a silent block can sit in a protected copy; a
   domain library of blocks ever expressed by specialists as a transplant source (only if
   step 4 shows silence pays).

Skipped on purpose: MAP-Elites over case-pass vectors (the descriptor would smuggle in the
task's decomposition) and epsilon/down-sampled lexicase (evaluation is not the bottleneck).
