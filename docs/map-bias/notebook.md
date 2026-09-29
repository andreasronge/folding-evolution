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
  This *is* standard lexicase — an earlier note here said otherwise; see §5.
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
- ~~**The lexicase variant adds niching.**~~ **Retracted in §5.** The claim was that picking
  a surviving behaviour group uniformly (rather than weighting by size) adds niching. It
  can't: groups are built from complete case rows, so exactly one group ever survives
  the filter and the weighting never applies. Standard and group variants gave identical
  runs on all 30 seeds. The 14/30 is plain lexicase.
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

1. ~~**Fix lexicase to the standard version.**~~ **Done (§5): nothing to fix** — the old
   code already was standard lexicase in practice.
2. **Parent tracking + lineage labels.** **Done (§5).** Record each child's parents and how it was made
   (crossover / mutation). Tracking uses no random numbers, so re-running the solved seeds
   reproduces them exactly. Label every fitness-raising step on the path to each solver, and
   for crossover steps record child fitness against both parents and whether both parents'
   expressed blocks survive in the child. That gives the real jump routes and the real
   crash spectrum.
   - Mutation-only arithmetic walks → retire this task for jump questions.
   - Crossover steps that merge two parents' blocks with only a small drop → keep it; v3 vs
     baseline under lexicase is then a fair comparison.
3. **Fix the separator bug** (decoders use v1 masks under v2 alphabets). **Done (§5) as
   opt-in `alphabet_separators: true`**, so old sweep configs still reproduce.
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

---

## 5. Steps 1-3: lexicase check, solver lineages, separator fix (2026-09-26)

**What would be interesting to see:** whether the 14 lexicase solvers got there by
recombining blocks (a jump) or by a smooth mutation walk, and whether they compute AND
at all.

**Setup.** `experiments/chem_tape/sweeps/mapbias/lexicase_lineage.yaml`, 30 seeds each of
`lexicase_group`, `lexicase`, and `lexicase` + `alphabet_separators`, otherwise as §3.
New config flags: `track_lineage` saves the final best genome's ancestry to `lineage.npz`
(main line = the fitter parent at each crossover; no RNG, so runs are unchanged);
`alphabet_separators` makes the BP/BP_TOPK decoders (NumPy, MLX, Rust) split on 20/21
under v2. Analysis: `experiments/chem_tape/analyze_lineage.py`. About 17 min on 10 cores.
Also includes the Rust top-K decode speed-up from another session (commit `35a5433`).

**Results.**

1. **The two lexicase variants are the same algorithm.** Identical runs on 30/30 seeds (see
   the retraction in §3). 14/30 solved, same seeds as §3.
2. **Only 6 of the 14 "solvers" compute AND.** Scored on all 10,000 length-4 lists, 6 are
   exact (1.000); the other 8 are approximations that happen to fit the 64 training cases
   (0.918–0.9965; median of all 14 is 0.9915). The 256-case holdout doesn't catch most of
   them.
3. **No evidence that crossover on its own drives innovation.** Along the 14 solver main
   lines there were 95 innovations (child beats both parents). *Corrected after review:*
   most "crossover" children were also mutated afterwards. Split: 26 pure crossover, 50
   crossover + mutation, 19 mutation only. Pure crossover is 27% of innovations, roughly
   its share of all children. The final step to 1.0 was a crossover in 10 of 14 runs,
   which is what a 0.7 crossover rate predicts (9.8). Caveat: only solver main lines were
   looked at, so everything here is conditioned on success; §6 measures all children.
   (The earlier "big jumps ≥ 0.05" count is dropped: 0.05 is only 3 of 64 cases.)
4. **My "merges both parents" measure doesn't discriminate.** 52/76 innovating crossovers
   put executed material from each parent into the child — but 70% of *all* main-line
   crossovers do too. A better measure is needed to say whether a step combined two
   functional blocks.
5. **Fable's prediction was half right.** The task has an arithmetic shortcut (§3) and most
   solvers use one, but the lineages are not mutation-only walks: crossover drives most
   innovations.
6. **Separator fix: 7/30 solved** (3 exact AND) vs 14/30 without it. Suggestive (p ≈ 0.1),
   not conclusive. Enabling `MAP_EQ_E`/`CONST_2` and the real separators changes the
   landscape; why it's harder is unexplored.

**Take.** On this task "solved" mostly means "fits 64 cases", and crossover is the main
innovator mainly because it's the main operator. Two changes before comparing chemistries
(plan step 4): score fitness on all 10,000 lists so approximations can't pass, and build
a functional "did this crossover combine two blocks" measure — e.g. does the child's
behaviour match an AND of the parents' behaviours on the cases where they differ.

---

## 6. Crossover spectrum on the exact-AND solvers (2026-09-26)

**What would be interesting to see:** whether any crossover actually merged two
working blocks — one from each parent — and how often crossover crashes compared
with mutation. Suggested by the third Fable review.

**Setup.** `experiments/chem_tape/crossover_spectrum.py`. The 6 exact-AND lexicase
solvers from §5 (seeds 0, 5, 6, 8, 9, 29) re-run with lineage tracking; every re-run
reproduced its saved best genome. On sampled generations (every 10th, plus the last
10 before the solve), every child except elites and unmutated clones is scored on
all 10,000 lists (balanced accuracy, since 84% of lists are positive) and compared
with its parent(s): **better** (> fitter parent + 0.001), **neutral**, **small
degradation** (not below the weaker parent − 0.05), **crash** (below that).
**Combination** = the child passes every list either parent passed, and each parent
passed ≥ 3 lists the other didn't. About 5 min on 6 cores.

**Results.**

| operator | children | better | neutral | small degradation | crash | combination |
|---|---|---|---|---|---|---|
| crossover, no mutation | 192,256 | 0.61% | 62.7% | 27.5% | 9.2% | 18 |
| crossover + mutation | 117,888 | 0.73% | 41.2% | 18.1% | 40.0% | 12 |
| mutation only | 50,326 | 1.27% | 60.3% | 2.2% | 36.3% | 0 |

1. **Pure crossover rarely crashes here: 9%, against 36% for mutation.** *Overstated —
   see §7:* this bar let crossover children fall to the weaker parent; against the
   fitter parent it is 18.5% vs 33%. The "converged parents" explanation offered here
   is also wrong (§7).
2. **Mutation is twice as likely to improve a child** (1.27% vs 0.61%). Crossover makes
   ~4× more children, so it still delivers more improvements in total.
3. **Combinations are rare and cluster at the solve.** 30 of ~360,000 children, in 3 of
   the 6 seeds, all in the last generation or two before solving. Seeds 5, 9 and 29 had
   none in the sampled generations.
4. **No combination merged one block from each parent.** Test 1: no child contains
   pieces behaving like both whole parents (0 of 15 unique events; parents were
   approximations, so this test is strict). Test 2, pieces computing `max>5` / `sum>10`
   exactly:
   - Seed 0: the child is the canonical `CONST_0 … INPUT REDUCE_MAX CONST_5 GT IF_GT …
     INPUT SUM … GT` form — but parent 2 *already had both* blocks (score 0.978). The
     crossover fixed their arrangement, not their supply.
   - Seed 8: one event had `max>5` in parent 1 and `sum>10` in parent 2, but the child
     kept only `sum>10`; the max test ended up folded into arithmetic.
   - Seed 6: `max>5` in all three, no `sum>10` piece anywhere.

**Take.** On this task and chemistry, crossover does not jump by merging two blocks
from two parents. It mostly supplies a similar genome in which a small change does the
work, and the few "combinations" are rearrangements of blocks one parent already had.
Per the plan agreed with Fable, the next step is therefore not an evolution race but a
static test: **v3's crash spectrum against baseline** — does domain isolation keep
crossover children from crashing, and does it make one-parent-per-block merges
possible at all?

**Caveats.** Sampled generations only; 6 solvers; crash / degrade thresholds are my
choice; the predicate-piece test uses task knowledge (analysis only, not selection).

---

## 7. Waiting times, fair crash bar, and a guaranteed-supply merge test (2026-09-26)

**What would be interesting to see:** (a) once both blocks exist, how long evolution
takes to arrange them into a solution — a long wait means arrangement, not supply, is
the bottleneck; (b) whether recombination can put a `max>5` block and a `sum>10` block
together at all when both are guaranteed to be there. From the fourth Fable review.

### 7a. The six exact-AND solvers again

Same re-run as §6 (`crossover_spectrum.py`, output `crossover_spectrum2/`), now with
crossover scored against the **fitter** parent like mutation, crash rate by how many
executed cells differ between the parents, the last 10 generations reported
separately, and waiting times (first generation a genome contains a piece computing
`max>5` / `sum>10` exactly, both in the population, both in one genome).

| operator (vs fitter parent) | every 10th gen: crash | endgame: crash | better |
|---|---|---|---|
| crossover, no mutation | 18.5% | 23.1% | 0.6–0.9% |
| crossover + mutation | 44.5% | 63.5% | 0.7–1.1% |
| mutation only | 33.4% | 53.6% | 1.2–1.8% |

1. **Pure crossover is gentler than mutation, but less than §6 said** (18.5% vs 33%).
2. **Populations are not converged.** 145,596 of 192,256 pure crossovers are between
   parents whose executed programs differ in ≥ 16 cells. Crash rises with that distance
   (1.8% → 6.0% → 9.5% → 17.8% → 20.3%) but stays near 20% even for very different
   parents. Crossover + mutation crashes ~57% at every distance, so the extra mutation
   does most of that damage.
3. **Supply is early, arrangement is slow.**

| seed | both blocks in population | both in one genome | solve | one genome → solve | solver has both blocks |
|---|---|---|---|---|---|
| 0 | 124 | 124 | 622 | 498 | yes |
| 5 | 123 | 328 | 1028 | 700 | yes |
| 6 | 151 | 1174 | 1178 | 4 | yes |
| 8 | 103 | never | 234 | — | no (arithmetic) |
| 9 | 217 | 253 | 390 | 137 | no |
| 29 | 5 | 8 | 369 | 361 | no |

   Both blocks exist within 5–217 generations; from co-presence in one genome to the solve
   takes 137–700 generations in 4 of 5 seeds. And 3 of 6 exact solvers contain neither
   pair of blocks — they reach exact AND another way. So once lexicase supplies the
   blocks, **arrangement is the bottleneck**.

### 7b. Guaranteed-supply merge test

`experiments/chem_tape/merge_test.py`, output `merge_test/` (an earlier run with a wrong
crash bar is kept as `merge_test_v1_wrong_crash_bar/`). New tasks `mb_max_gt_5` and
`mb_sum_gt_10` use exactly the AND task's slot/threshold bindings, so a block means the
same thing after a transplant. Donors: 25 genomes per predicate and chemistry, each
exact on all 10,000 lists, from pop 1024 × 400 gens runs (baseline needs the long budget
for `sum>10`). Every max>5 × sum>10 donor pair, both orders, crossed three ways; every
child scored on all 10,000 lists against AND. Crash = clearly worse than *both* parents.

| chemistry | operator | children | exact AND | both blocks kept | same as a parent | crash |
|---|---|---|---|---|---|---|
| baseline | single-point | 38,750 | 0 | 0 | 74.1% | 25.9% |
| v3 | single-point | 38,750 | 0 | 0 | 53.5% | 46.4% |
| v3 | domain transplant (all 6 linkers) | 393,204 | 0 | 0 | 69.7% | 30.2% |

**No child in either chemistry computes AND or keeps both blocks.** Why:
- **Baseline: blocks compete for the same place.** Donors end with their predicate's
  final comparison at the *end* of the tape, because the output is the top of the stack.
  A single-point cut keeps X's start and Y's end, so X's block is almost always cut off.
- **v3: blocks are not domains.** v3 donors spread a predicate across several domains and
  use the linkers as the arithmetic (e.g. `const MIN const MAX [reads max] GT const GT
  const`). A single domain never carries the block, and because the linker chain is a
  left-to-right fold with no grouping, two multi-domain chains can't be combined as
  units. Silent transplants are harmless (1.45% crash) but useless.

**Take.** Supply is solved by lexicase; the jump that remains is *arrangement*, and
neither chemistry gives evolution a way to treat an evolved block as one unit. That is
now the sharp design question for a crash-free recombination chemistry: blocks need to
be **closed units with one output** that recombination can move and a combinator can
join — e.g. nested / tree-shaped domains (a linker combines two *sub-chains*, not one
domain), or blocks that must return their value to a named slot instead of the shared
stack top. A first cheap check: whether evolution under such a chemistry keeps each
predicate inside one unit, before any evolution race.

**Caveats.** Waiting-time scan every 5 generations, refined to the exact generation;
donors come from 8 seeds per pool; "both blocks kept" is checked on a 10% sample for
baseline (piece search is costly) and on whole domains for v3.

---

## 8. Plan: tagged runs — connection by binding, not position (2026-09-26)

**Idea (nature-inspired, no imposed shape).** In both chemistries so far position
decides meaning: the output is the stack top, so blocks compete for the tape end, and
v3's linker chain order decides how values combine. Biology separates the two:
transcription factors and protein domains connect by what they *bind*, wherever they
sit. Tagged runs:
- The tape is split into runs; each run has a **tag** (like a binding site) and a body
  that runs on its own fresh stack; its output is its top int.
- `RECV t` pushes the output of the run tagged `t` (exact match; no match → 0).
- The organism's output is the run tagged with a fixed output tag.
- Nothing imposes a tree or chain; chains, DAGs, shared sub-results and redundant copies
  can all emerge from which tags match.

**Fifth Fable review (corrections to my pitch).**
- Fixes "blocks compete for the tape end" outright, but probably *not* smearing: any
  glue between units gets used as computation (v3's lesson), and nothing pushes toward
  closed blocks. Open-ended pressures if needed: **noisy links** (each RECV fails with a
  small probability, so deep chains lose) and **modularly varying goals**.
- "Inert for free" is false under closest-tag matching (a new run hijacks references):
  use **exact matching** and a tag space much larger than the number of runs (64 values,
  in a separate tag field).
- "Graded rewiring" is false: nearby tags are unrelated runs. Start exact.
- The AND jump is not one mutation: a ~6-token combining run is still needed. What tags
  buy is that it can be built silently and switched on by one retag, but it needs
  lexicase partial credit to be built at all.
- Use a longer tape (64) with deletion, crossover that aligns runs by tag (swap bodies of
  same-tagged runs — homologous recombination), no positional tie-breaking, a RECV depth
  cap, and log RECV frameshifts separately.

**First experiment (merge-test style).** Evolve exact `max>5` and `sum>10` donors under
tagged runs, then measure:
1. **Smear:** knock out each non-output run; count runs whose removal changes the output.
2. **Inertness:** transplant every run of donor B into donor A; fraction of children
   exactly unchanged, fraction crashing.
3. **Paths to AND:** 1- and 2-mutation neighbourhoods of transplanted children; count exact
   AND and partly built combiners.

**Kill** if donors typically need ≥ 3 load-bearing runs, or < 80% of transplants are
inert (v3 repeated). **Confirm** if predicates sit in 1–2 runs, ≥ 90% of transplants are
inert, and a 2-step path to AND exists (baseline: 0 in 38,750).

---

## 9. Tagged runs: first results (2026-09-26)

**Setup.** `src/folding_evolution/chem_tape/tagged.py` (arm `TAG`, alphabet `tagged`):
genome = 64 cells, each an op (the 20 v2 ops, `SEP`, `RECV`) plus a separate 64-value
tag field. `SEP` starts a run with that tag; `RECV t` pushes the output of the run(s)
tagged exactly `t` (none → 0; several → max); output = tag 0; cycle guard and depth cap 8;
cells before the first `SEP` are inert. Vectorised interpreter, checked against the Python
executor on 600 random programs (`tests/test_chem_tape_tagged.py`). Variation: point
mutation of ops and tags, cell insertion/deletion (rate 0.015), crossover that either swaps
bodies of same-tagged runs or cuts between runs. Donors: lexicase, pop 1024 × 400 gens,
8 seeds per predicate (exact `max>5` in 7/8 seeds, exact `sum>10` in 4/8); 20 exact donors
each, round-robin across seeds. Script: `experiments/chem_tape/tag_merge_test.py`.

**Results.**

1. **Blocks stay closed.** Load-bearing runs per donor (removal changes the output):
   median 1 for both predicates (`max>5`: 11 donors with 1, 9 with 0 — the 0s have
   redundant copies under the same tag, so no single knockout matters; `sum>10`: all 20
   with 1). Kill threshold was ≥ 3. So far each predicate lives inside one run — the
   output run itself (Fable's "everything in the output run" attractor), but a closed
   unit either way.
2. **Transplants are inert.** 940 transplants of a non-output run: **100% inert, 0%
   crash** (kill threshold < 80%). Transplanting B's *output* run is not inert (19% inert,
   81% crash), as expected: two tag-0 runs combine by max, i.e. an OR.
   Compare §7: baseline single-point 26% crash and 0 blocks kept; v3 30–46% crash.
3. **No short path to AND.** 40 silent module imports (B's runs added with its output run
   retagged to an unused tag): the import itself is inert 40/40. Exhaustive 1-mutation
   neighbourhoods (324,576 mutants) and 120,000 sampled 2-mutation neighbours: **0 exact
   AND, 0 better than both parents**. A mutation that wires the imported module into the
   output path occurs (361 and 309 cases, ~0.1–0.3%), but wiring alone doesn't compute AND.
   Caveat: these neighbourhoods use point mutations over existing cells only; the minimal
   combiner (e.g. `RECV f ADD CONST_1 GT` appended to the output run, or a 6-token
   `CONST_0 RECV a RECV b IF_GT` run) needs 3–6 *new* cells, so 0 was expected — this
   measures the combiner's cost, not the chemistry.

**Take.** Tagged runs are the first chemistry where evolved blocks are closed units and
recombination can move one without damage — both kill criteria pass, and the silent
insertion is real, not designed in. What's left is the combiner: joining two blocks costs
several new tokens with nothing rewarding the intermediate steps. Next: an evolution race
on the AND task under lexicase (tagged runs vs baseline), measuring solve rate and time
from "both blocks in one genome" to solve — does a chemistry where blocks can sit side by
side safely shorten the arrangement wait of 137–700 generations (§7a)?

---

## 10. Evolution race: tagged runs vs baseline on AND (2026-09-26)

**What would be interesting to see:** now that blocks can sit side by side safely (§9),
does evolution use that — shorter wait from "both blocks in one genome" to the solve?

**Setup.** `experiments/chem_tape/sweeps/mapbias/tag_race.yaml`: 30 seeds, AND task,
lexicase, pop 1024 × 1500 gens, 64 training cases, tape 64, mutation 0.015. Baseline =
the lexicase runs of §5 (same budget and cases). Analysis:
`experiments/chem_tape/tag_race_analysis.py` (waiting times from a deterministic re-run of
each exact solver; structure from knockouts). ~11 min for the sweep.

**Results.**

| chemistry | solved (64 cases) | exact AND (all 10k lists) | median solve gen (exact) |
|---|---|---|---|
| baseline (BP_TOPK) | 14/30 | 6/30 | 506 |
| tagged runs | 13/30 | 7/30 | 1044 |

1. **No difference in outcome.** Same solve and exact-AND counts within noise; tagged
   solvers are, if anything, slower.
2. **No shorter arrangement wait.** Both blocks in one genome → solve: tagged 109–901
   generations (6 seeds; one solver never had both), baseline 4–700.
3. **Evolution doesn't use the modular route.** Every exact tagged solver has exactly one
   load-bearing run, and that run computes AND by itself. Where the output run contains a
   `RECV`, it fetches a tag that no run has — i.e. it's used as a constant 0. Blocks that
   co-exist as separate runs are not wired together; AND is rebuilt inside one run.
   This is Fable's "everything in the output run" attractor.

**Take.** Making modular recombination *safe* is not enough; nothing on this task makes
it *pay*. A block that sits in its own run is worth nothing extra here, because it is
used exactly once. Biology's modularity is selected where parts are **reused** (one
signal read by many genes) or where **goals change in a modular way**. Candidate next
steps, both open-ended (no imposed shape):
- **Reuse:** a task with several outputs that share sub-results (e.g. output tags 0, 1, 2
  for `max>5 AND sum>10`, `max>5 OR sum>10`, `max>5 AND NOT sum>10`), so one block
  referenced by tag serves all of them.
- **Modularly varying goals:** switch the target between `max>5`, `sum>10` and the AND
  every ~20 generations (Kashtan & Alon), with tagged runs vs baseline.

---

## 11. Overnight queue: OR race, varying goals, fixed-AND control (2026-09-26, running)

**Why.** Sixth Fable review: tagged runs combine same-tag runs by max, so the chemistry's
built-in combinator is OR — the modular route (duplicate the output run, let the copy
diverge) exists for OR and not for AND, and §10 only tested AND. And building a block in
place is always cheaper than wiring two runs, so single-use tasks never reward modularity;
varying goals (Kashtan & Alon) might.

**Queue** (`experiments/chem_tape/sweeps/mapbias/overnight_queue.yaml`, 3 arms each:
baseline BP_TOPK / tagged / tagged + gene duplication at 0.1 per child; lexicase, pop
1024, lineage tracking, balanced-accuracy fitness):
1. `or_race` — OR on stratified inputs, 30 seeds × 1500 gens, no early stop.
2. `mvg_p20` — goal cycles max>5 → sum>10 → AND every 20 gens on one shared input set,
   re-selecting on the new goal at each switch; 30 × 3000.
3. `and_fixed` — fixed AND on the same inputs and budget (control for #2); 30 × 3000.
4. `mvg_period` — periods 5 and 50, baseline vs tagged+dup; 30 × 3000 (runs last).
Morning analysis: `experiments/chem_tape/overnight_analysis.py <output dir>`.

**Pre-launch review (Codex gpt-6-sol, two rounds) — fixed before launch:**
- Gene duplication could truncate existing runs, and a "silent" copy could take a tag a
  dangling RECV reads (wiring it in); same-tag copies of self-reading runs changed output.
  Now: never truncates (makes room from trailing NOPs, then never-executed leader cells,
  else skips), fresh tags avoid read tags, self-dependent runs are not copied same-tag.
  Neutrality tested on random genomes. Accepted for ~20–30% of evolved genomes.
- OR training could be solved by `sum>10` alone (38% of 32-positive samples had no
  max-only case). Now `mbs_*` tasks draw inputs equally from all four (max>5, sum>10)
  cells, shared across max / sum / AND / OR for a given seed.
- Equal cells make AND 25% and OR 75% positive, so "always 0/1" scored 0.75 and
  populations drifted to run-less genomes. Now fitness = balanced accuracy (constant → 0.5,
  `max>5` alone on AND → 0.83); lexicase itself is per case and unchanged. A pilot reached
  exact AND in 2 of 9 short runs.
- The old recovery metric compared fitness across different goals, and selection lagged one
  generation on the old goal at each switch. Now `reselect_on_flip` re-scores on the new
  goal before reproducing and logs the new goal's starting score; recovery is computed in
  the morning from per-generation data.
- Sweeps now write their index after every run and a `SWEEP_COMPLETE` marker only when all
  configs are done; the queue checks the marker; re-running a sweep resumes.
- Remaining caveats: baseline vs tagged is a chemistry-package comparison (tape length,
  indels, crossover differ); tagged vs tagged+dup isolates duplication. Lineage saves only
  the final champion's ancestry; phase-end champions come from history.csv.

---

## 12. Overnight results (2026-09-27)

All four sweeps completed (`experiments/output/2026-09-26/mapbias_*`, commit `05ad45e`;
30 / 58 / 65 / 73 min). Analysis: `experiments/chem_tape/overnight_analysis.py` →
`overnight_summary.md`; follow-ups: `experiments/chem_tape/overnight_followup.py`.
Exact = the final (or phase-end) best genome is right on all 10,000 lists.

### 12a. OR race — the modular route is used when it pays

| arm | exact OR | median first exact gen | tagged solvers using ≥ 2 runs |
|---|---|---|---|
| baseline | 10/30 | 595 | — |
| tagged | 19/30 | 290 | 18/19 |
| tagged + duplication | **25/30** | **250** | **25/25** |

- tagged+dup vs baseline p = 0.0002; tagged vs baseline p = 0.04; tagged vs tagged+dup
  p = 0.14 (Fisher). Baseline vs tagged is a chemistry-package comparison.
- Tagged solvers have two load-bearing output (tag-0) runs, combined by max = OR.
- **Crossover is where the second output run arrives.** On each solver's main line, the
  step where the champion first got its second output run was a crossover in 19/19
  (tagged) and 24/25 (tagged+dup) solvers, against a ~70% base rate (0.7¹⁹ ≈ 0.001).
  In **20 of 44** the new output run is an exact copy of the *other* parent's output run —
  confirmed two-parent block merges. The other 24 are crossovers where the new run matches
  neither parent exactly (crossover plus modification; not shown to be merges). This is
  lineage correlation; the causal test (crossover off) is in §13. Gene duplication was
  almost never the route (1/25), and its extra solves (25 vs 19) are not significant —
  no claim that duplication helps.
- **Not yet attributable to modularity.** Baseline vs tagged is a chemistry-package
  comparison, and the baseline has no integer MAX, so OR costs it a combiner
  (`ADD CONST_0 GT`) that tagged runs get free. §13 controls separate the two.
- Fixed AND for comparison: 9/30 in all three arms, single-run solvers (as §10).

### 12b. Varying goals — helps the baseline, not tagged runs

Runs with an exact AND phase-end in the last third (ever) vs the fixed-AND control
(exact at end): period 20: baseline **14/30** (18/30) vs 9/30; tagged 2/30 (6/30);
tagged+dup 2/30 (3/30). Period 5: baseline 11/30 (18/30); tagged+dup 8/30 (14/30).
Period 50: baseline 2/30 (7/30); tagged+dup 3/30 (3/30).
- Tagged runs track the goals worse than baseline at every period (e.g. period 20, early
  phases reaching 1.0: max>5 71% vs 95%, sum>10 47% vs 77%), and their phase-end solvers
  are single runs — no persistent modules formed. *Possible artefact (seventh review):*
  per-genome mutation rates are matched, but many tagged cells are inert, so a tagged child
  may change its behaviour less often, which is exactly what tracking speed depends on.
  Measured and controlled in §13.
- Sampling note: the fixed control was checked every 10 generations (~300 looks), the MVG
  arms only at ~50 AND phase ends, so the baseline's MVG gain (18/30 vs 9/30 ever exact)
  is if anything conservative.
- The baseline benefits from switching every 5–20 generations (Kashtan & Alon-like);
  slow switching (50) does not help.

### Take (provisional until §13's controls)

The question since §3 was whether evolution can combine building blocks by
recombination without crashing. Answer on this system so far:
- **Apparently yes, when the chemistry's combinator matches the task.** Tagged runs combine same-tag
  runs by max; on OR, crossover merges one parent's output run into another's, safely,
  and that raises exact solves from 10/30 to 19–25/30 and halves the time.
- **No, when joining needs a new combiner** (AND): building in place wins (§10, 12a).
- **Varying goals** did not make tagged runs modular; they helped the stack baseline.
The next open-ended step is therefore a chemistry where the way same-tag runs combine is
itself evolvable (e.g. the combiner depends on the tag), so AND-, OR- and other joins are
all as cheap as OR is now — no shape imposed, the combinator becomes a heritable trait.

---

## 13. Plan: attribution controls and an evolvable combiner (seventh review)

**Controls for 12a (OR, 30 seeds × 1500 gens each):**
1. Tagged runs with **crossover off** (mutation only). Collapse → recombination is the
   route; no collapse → a single retag of an existing run to tag 0 may be doing the work.
2. Tagged runs where several same-tag runs give **leftmost wins** instead of max: same
   chemistry package, no free combinator.
3. **Baseline + an integer MAX op**, and baseline with a 64-cell tape.
   Rule: (2) falls to ~10/30 and (3) stays ~10/30 → the modular route is the cause;
   (3) rises to ~25/30 → the finding is combiner cost (narrower).
**Varying goals:**
4. Effective mutation rate: fraction of children whose behaviour differs from their parent,
   per arm, on stored populations.
5. MVG period 20 with tagged runs' mutation rate raised to match baseline's effective rate.
   Does the tracking gap vanish?
**Closing experiment:**
6. **Evolvable combiner**: a combine field on each run (max / min / add / gate), mutable
   like the tag; same-tag runs fold with their fields. On AND and OR. Confirm: AND rises
   from 9/30 toward OR's level with two-run solvers. Kill: stays ~9/30.
Then stop this line and promote to findings; building a combiner across a valley (§9) is a
separate project.

---

## 14. Attribution controls and evolvable combiner — results, and wrap-up (2026-09-27)

Queue `experiments/chem_tape/sweeps/mapbias/queue_s13.yaml` (commits `34a4529`, `7e8699b`),
outputs `experiments/output/2026-09-27/mapbias_*`, analysis
`experiments/chem_tape/s13_analysis.py` → `s13_summary.md`. All OR runs: 30 seeds × 1500
gens, stratified inputs, balanced fitness, lexicase; exact = right on all 10,000 lists.

**OR controls** (references from §12: tagged 19/30, tagged+dup 25/30, baseline 10/30):

| setup | exact OR | median first exact gen |
|---|---|---|
| tagged, **crossover off** | **2/30** (p < 0.0001 vs tagged) | 465 |
| tagged, **leftmost wins** (no free OR) | 11/30 (p = 0.07 vs tagged) | 870 |
| **baseline + IMAX** (OR = one op) | **18/30** (p = 1.0 vs tagged) | 315 |
| baseline, tape 64, rate 0.03 | 15/30 | 600 |
| baseline, tape 64, rate 0.015 | 9/30 | 870 |

1. **Crossover is causal in tagged runs.** Without it, exact OR collapses to 2/30 and no
   solver has two output runs.
2. **The OR advantage over the baseline is combiner cost, not modularity.** Giving the stack
   baseline a one-op OR (integer MAX) brings it to 18/30 — the tagged level. Taking the free
   OR away from tagged runs brings them down to 11/30 — the baseline level (this control also
   makes run order matter, so it tests the max rule, not "max alone"). Per the §13 rule, the
   finding is the narrower one.

**Evolvable combiner** (`tagged_comb`; combine markers are ordinary body cells):
- AND: **9/30** — same count as every other arm (and_fixed: 9/30 each), so by the §13 kill
  rule it does not raise solve rates. But **9/9 solvers are two-run modular solutions**
  joined by `min` (7) or `gate` (2), against 1/9 and 3/9 for tagged / tagged+dup, and they
  are found sooner (median first exact gen 640 vs 1000–1580).
- OR: 17/30 (vs 19/30; p = 0.79) — the larger alphabet (25 ops) costs nothing measurable;
  joins used are mostly max.

**Varying goals, mutation-matched:** tagged runs' rate lowered to match the baseline's
effective rate (realised: 0.205 and 0.227 vs 0.21 — tagged children change behaviour *more*
often at the nominal rate, 0.35, the opposite of the review's hypothesis). Tagged still
track worse: exact AND at a late phase end 1/30 and 2/30 (vs baseline 14/30); early phases
reaching 1.0 fell further (max>5 43–61%, sum>10 28–36%). The tracking gap is a property of
the chemistry, not a mutation-rate artefact.

### What this line found (§1–§14)

*Superseded by the scoped, reviewed version in [findings.md](findings.md) (eighth review).*

- **Bias in the map shapes outcomes but is not destiny.** Random-tape frequency predicts
  easy tasks; evolution routinely finds behaviours rarer than 1 in 50M (§1).
- **The AND "proxy basin" is a wide valley:** no solver within two mutations of any stuck
  genome; a whole second block is missing (§2).
- **Lexicase fixes block supply** (1/30 → 14/30 on AND); **arrangement is then the
  bottleneck**, 137–700 generations from both blocks in one genome to a solve (§3, §5, §7).
- **In a stack chemistry, blocks compete for the tape end;** v3's linker chains smear blocks
  across domains; neither lets recombination merge two blocks (§7).
- **Tagged runs** (connection by tag, not position) keep blocks closed and make transplants
  inert — safe modular recombination is achievable without imposing a shape (§9).
- **Recombination does merge blocks when the join is cheap** (crossover is causal), but the
  advantage comes from the join's cost: a stack with an equivalent one-op join does as well
  (§12, §14).
- **When joins are heritable, evolution adopts the modular route completely** (all AND
  solvers become two joined runs, found sooner) — **but success rates don't rise** (§14).
- **Varying goals helped the stack baseline** (Kashtan & Alon-like), not tagged runs, and
  that is not a mutation-rate artefact (§12, §14).

**Stopping point.** The open follow-on — evolving a join that must be *built* across a
fitness valley (§9), rather than chosen from a menu — is a separate project.

---

## 15. Plan: a frequency knob, and XOR (2026-09-27, overnight)

**Why.** The line never manipulated map bias: chem-tape's decoder is close to identity (§1),
so "frequent" and "easy" were confounded. `op_weights` (config) makes chosen ops k× as
likely in random genomes and point mutations, the same as giving them k synonyms, so what
can be reached stays the same and only how often it is made changes. XOR is the harder
task: on the stratified inputs its best `sum + w·max` threshold scores 0.72 (cell-balanced)
against 0.96–0.97 for AND and OR, so the linear shortcut is gone and exact solvers must
compose. A hand-built tagged XOR (two tag-0 runs `p1 p2 GT`, `p2 p1 GT`, max-joined) is
exact on all 10,000 lists.

**Queue** (`experiments/chem_tape/sweeps/mapbias/queue_s15.yaml`, all fast_rng, lexicase,
balanced fitness, 30 seeds unless noted, each sweep has its own 1× reference arm):
1. `knob_comb_and`: tagged_comb AND, combine markers at 0.25×, 1×, 4×, and gate alone 4×.
   *Interesting if* the joined-solver share and the min:gate split move with weight
   (arrival of the frequent on route choice) while the solve count stays ~9/30.
2. `xor_race`: stack v2_probe, stack v2_imax, tagged, tagged_comb on XOR.
3. `knob_imax_or`: stack v2_imax OR, IMAX at 0.25×, 1×, 4× (dose-response on the join).
4. `knob_min_and`: stack v2_min AND, MIN at 1×, 4×, 16× (is the stack AND valley just rarity?).
5. Seed top-ups, 100 seeds: OR tagged vs tagged+dup; stack fixed AND vs varying goals
   period 20. Last in the queue; fine if they get cut.

Morning: exactness on all 10,000 lists (`overnight_analysis.py` now knows `mbs_xor`), route
per exact solver (number of tag-0 runs, join marker), first exact generation.

---

## 16. §15 results (2026-09-28)

All 7 sweeps completed (`experiments/output/2026-09-27/mapbias_{knob_*,xor_race,seeds100_*}`,
commit `7c9cc42`, ~4 h). Analysis: `experiments/chem_tape/overnight_analysis.py` →
`overnight_summary.md` (exactness now checked every generation). p = two-sided Fisher.
Caveat for every knob: raising one op's weight lowers every other op's share (at MIN 16× the
MIN token is 42% of draws), so high weights also dilute the rest of the alphabet.

**Frequency knob: join marker on tagged_comb AND** (share of each marker in draws: 0.25× ≈ 1%, 1× 4%, 4× 14%)

| markers | exact AND | median first exact | multi-run solvers | joins used (min / gate / other) |
|---|---|---|---|---|
| 0.25× | 10/30 | 608 | 10/10 | 8 / 2 / 1 |
| 1× | 12/30 | 556 | 11/12 | 5 / 6 / 1 |
| 4× (all three) | 6/30 (p = 0.16 vs 1×) | 1219 | 5/6 | 3 / 2 / 0 |
| gate only 4× | 12/30 | 863 | 11/12 | 4 / 8 / 1 |

- At 0.25× (≈ 2 marker cells per genome, ~30 new marker cells per generation across the
  population) the joined route is still used by 10/10 solvers. This does not test true rarity.
- Gate share is ordered as frequency predicts (18% / 50% / 62% at 0.25× / 1× / gate 4×), but
  only the extreme pair is near significance (p = 0.047; 1× vs gate 4× p = 0.70; §14's 1× run
  gave 2/9 gate). Consistent with a frequency effect on which join is used, not shown.
- More markers does not help the solve rate; 4× on all three (35% of all draws) is worse,
  most likely dilution (runs reaching train 1.0: 24 → 16).

**Frequency knob on the stack baseline**

| setup | 0.25× | 1× | 4× | 16× |
|---|---|---|---|---|
| OR, IMAX weight (exact / median first gen) | 9/30 / 857 | 19/30 / 466 | 17/30 / 370 | — |
| AND, MIN weight | — | 10/30 / 1493 | 9/30 / 1101 | 2/30 / 1852 |

- IMAX frequency sets when the join arrives: median first exact 857 / 466 / 370 at 0.25× /
  1× / 4× (solves by gen 750: 4 / 15 / 14). Under a fixed 1500-gen budget that becomes fewer
  solves at 0.25× (9 vs 19, p = 0.02) and saturates above 1× (17).
- MIN at 16× (42% of draws) hurts (2 vs 10, p = 0.02) — dilution: runs reaching train 1.0
  fall 15 → 4, the whole program suffers, not just the join. MIN at 4× (16%) changes nothing.
- Within this protocol MIN adds nothing to stack AND: v2_min 10/30 vs v2_probe 9/30 (§12)
  and 30/100 (below). §3's 1/30 differed in selection, inputs, fitness and budget.

**XOR** (no linear shortcut)

| arm | exact XOR | median first exact | multi-run solvers |
|---|---|---|---|
| stack v2_probe | 5/30 | 990 | — |
| stack v2_imax | 2/30 | 1466 | — |
| tagged | 13/30 (p = 0.047 vs stack) | 873 | 8/13 |
| tagged_comb | **19/30** (p = 0.0005 vs stack) | 1157 | 17/19 |

- Tagged runs beat the stack on XOR, but it is a chemistry-package result with two
  uncontrolled confounds. (a) Tape: every stack solver uses ≥ 28 of its 32 cells, and the
  stack fits the training cases in only 6/30 runs (tagged 22/30, tagged_comb 25/30); §14
  showed a 64-cell tape lifts stack OR 10 → 15/30. (b) Free OR: XOR = max(p1>p2, p2>p1),
  and 8/13 tagged solvers are exactly that — two near-identical output runs differing by a
  SWAP, joined by the free max; the second run arrived by crossover in 8/8 (an exact copy of
  the other parent's output run in 7/8). tagged_comb solvers use 3 output runs (median),
  with a mix of all four joins.
- IMAX doesn't help the stack on XOR (2/30): with ~30 of 32 cells in use, one op is not the
  constraint.

**Seed top-ups (100 seeds, fast_rng; seeds 0–29 re-run, so a replication, not an extension)**
- Gene duplication on OR: 62/100 vs 67/100 without (p = 0.55). §12's 25 vs 19 was noise;
  no duplication effect.
- Varying goals, stack baseline: exact AND at a late-third phase end in 21/100 runs, at any
  phase end in 36/100; fixed AND 30/100 (fixed ever = final: exact champions persist under
  elitism, so the extra looks don't matter). p = 0.45 (late-third: 0.19, favouring fixed).
  The §12 MVG benefit (18/30 vs 9/30) does not replicate at 100 seeds.

Multiple comparisons: of ~10 tests here only XOR tagged_comb vs stack (p = 0.0005) survives
a family correction; the p ≈ 0.02–0.05 results are trends. All §15 arms use fast_rng, so
comparisons with §12/§14 are approximate; each sweep's own 1× arm is the comparator.

**Take** (revised after the ninth Fable review).
- *Arrival of the frequent, causally:* op frequency acts as a supply rate on the join. It
  sets arrival time (IMAX), converts to fewer solves under a fixed budget when rare, and
  saturates above uniform; very high weights hurt only through dilution. Whether frequency
  steers the choice among equivalent joins is suggestive (ordered gate shares), not shown.
- *XOR* removes the linear-shortcut asterisk, and tagged runs win clearly (13–19/30 vs
  2–5/30), but until a 64-cell stack and a leftmost-wins tagged arm run on XOR it is a
  chemistry-package win, not a modularity win.
- Two suggestive earlier results (duplication, varying goals) are retracted as noise.

**Next (ninth review's ranked shortlist, ~4 h):** (1) XOR controls: stack tape 64 at rates
0.015 and 0.03, v2_imax tape 64, tagged leftmost-wins, tagged crossover off. (2) Crossed
min/gate weights on tagged_comb AND (`22:4,24:0.25` vs `22:0.25,24:4`, 50 seeds). (3) True
rarity: all markers at 0.02× and 0.05×. (4) IMAX 0.05× / 0.25× / 1× at 3000 gens, analysed
as time to first solve. Then close the chem-tape map-bias line; the core question needs a map
whose bias differs from direct encoding (folding map or tree-GP generator, as §1 said).
Tagged-run modularity is a separate, chemistry-design thread.

---

## 17. Valley crossing, Step 0: lineage post-mortem with both parents traced (2026-09-28)

**What would be interesting to see** ([Plans/valley-crossing.md](../../Plans/valley-crossing.md)):
whether any solver's output runs arrived by *silence, then switch* — built under an unread
tag, then retagged to 0. The saved lineages follow only the fitter parent, so they were
biased against finding it.

**Setup.** `experiments/chem_tape/postmortem_lineage.py` re-ran all 44 tagged solvers from
§16 (tagged XOR 13, tagged_comb XOR 19, tagged_comb AND 1× 12) up to their first exact
generation. **44/44 reproduced the original genome exactly.** Each output (tag-0) run was
traced back through *both* parents, following the run itself: the predecessor is the most
similar run in either parent, comparing ops plus tags on RECV cells only, with trailing NOPs
stripped. A run under another tag counts only if ≥ 90% similar. Runs are traced jointly, so
identical runs in one parent aren't read as a copy.
- One Codex review before the run: retags could be over-counted, and runs that didn't
  reproduce weren't excluded. Both fixed.
- The tenth (Fable) review then found that the first version also compared inert tags on
  non-RECV cells and the re-randomised padding. That mislabelled op-identical runs as
  "written" and could hide real retags. Fixed and re-run (v2).

Output: `experiments/output/2026-09-28/postmortem_v2/postmortem.md`.

| solvers | later output runs | copy of an earlier output run | … made inside one genome | retag from silent | RECV rewired (all output runs) |
|---|---|---|---|---|---|
| tagged_comb AND (12) | 12 | 11 | 0 | 0 | 4/24 |
| tagged_comb XOR (19) | 31 | 28 | 2 | 0 | 6/50 |
| tagged XOR (13) | 9 | 8 | 1 | 0 | 6/22 |

- **Silence, then switch: not seen, and not really tested.** None of the 52 later output runs
  came from a retag. The one retag (tagged XOR seed 18, run #1) was a tag flicker: one
  generation under tag 1, body unchanged. But the null is forced by the setup (tenth review):
  - a silent run becomes tag 0 at μ/64 ≈ 2×10⁻⁴ per run per generation (0–4 such events
    per solver), against 177–393 retags *away* from 0;
  - silent runs are few (0.2–1.5 per genome) and their bodies are junk;
  - half of all crossovers reshuffle expressed tag-0 bodies instead.

  So the route is outcompeted about 10⁴-fold. Untested rather than refuted.
- **Later output runs share ancestry with an earlier one ("homologous", not duplicated).**
  - Almost every later output run's trace joins an earlier output run's trace: 47 of 52.
  - Only 3 copies were made inside one genome; the rest sat in different individuals, apart
    for a median of 51–90 generations, until crossover joined them.
  - This is largely structural: in a converged population any two tag-0 runs share an
    ancestor, and homologous crossover fills every tag-0 slot from the donor's *first*
    tag-0 body.
- **Plain tagged XOR has no valley on the solving path** (tenth review, per-generation check
  of the 8 copy paths):
  - the common ancestor computed one XOR half (p1∧¬p2 or p2∧¬p1) at 1.0;
  - the other half arose as a single SWAP on one branch;
  - both halves sat in hosts scoring 0.73–0.88 (a half is right on 3 of 4 stratified cells),
    never masked;
  - crossover joining them under the free max was the solving step in 7/8.

  Fitness along the path: 0.75 → 0.75 → 1.0. tagged_comb AND is similar: the copy turned
  from p1 into p2 within 2–38 generations in single-run hosts at 0.83–0.90, and the solve
  came a median of 1 generation after the rejoin.
- **tagged_comb XOR is different.** Both branches changed (16/26), hosts dipped to 0.34–0.42
  (kept by lexicase on a few cases), and the solve came a median of 81 generations after
  the rejoin (> 500 in 8/26).
- **Interpretation (reworded after the review).** The intermediates are rewarded by partial
  credit on the target's own lexicase cases, not by a family of other functions, and the
  join is the free max. So this describes how a two-specialist polymorphism is recombined
  under a free join, not how a valley is crossed. Whether a *family* of rewarded functions
  adds anything beyond partial credit is exactly Step 2's question.

**Decision.** Follow the plan as revised after the tenth review (see the plan's "Revision"
section): move the valley work to tagged runs with **leftmost-wins** (no free join), where
XOR needs a join built inside one run. Tonight's queue (§18) starts with that.

---

## 18. Plan: XOR with no free join, and XOR controls (queue_s18)

**What would be interesting to see:** whether evolution can *build* the XOR join when the
chemistry gives none away. With leftmost-wins, the two-run max route fails. A one-run join,
e.g. `RECV a RECV b GT RECV b RECV a GT ADD`, is exact (checked by hand).

**Queue** (`experiments/chem_tape/sweeps/mapbias/queue_s18.yaml`; fast_rng, lexicase,
balanced fitness, 3000 gens):
1. `xor_leftmost`: tagged, leftmost-wins, 30 seeds.
   - ≥ ~8/30 exact → the join can be built; post-mortem the solvers and look for RECV rewiring.
   - ≤ 2/30 → the valley is real; build the ruler on this chemistry.
2. `xor_nox`: tagged (max join), crossover off, 30 seeds. §16 got 13/30 with crossover, and
   §17 says the solve is crossover joining two specialists, so collapse is expected.
3. `xor_stack64`: stack with a 64-cell tape at mutation rates 0.015 and 0.03, and v2_imax at
   64 cells. If the stack reaches ~13/30, §16's gap was tape length.
4. Parked map-bias items (ninth review):
   - `comb_cross`: min/gate weights crossed, 50 seeds;
   - `comb_rare`: markers at 0.02× and 0.05×;
   - `imax_time`: IMAX at 0.05×, 0.25× and 1× over 3000 gens, read as time to first solve.

`overnight_analysis.py` now labels arms by tape length, mutation rate, join rule and
crossover rate as well, so these arms are reported separately.

---

## 19. §18 results: XOR with no free join, XOR controls, parked map-bias items (2026-09-28)

All 6 sweeps completed (`experiments/output/2026-09-28/mapbias_*`, commit `c922028`, ~2.6 h).
Analysis: `overnight_analysis.py` → `overnight_summary.md`. Leftmost post-mortem:
`postmortem_lineage.py --target "mapbias_xor_leftmost=tagged leftmost"` →
`postmortem_leftmost/postmortem.md` (12/12 re-runs reproduced exactly). p = two-sided
Fisher, uncorrected. The "output runs / load-bearing" columns of `overnight_summary.md`
knock runs out under the max rule, so they are wrong for the leftmost arm; use the
post-mortem instead.

**XOR attribution**

| setup | exact XOR |
|---|---|
| tagged, max join (§16) | 13/30 |
| tagged, **leftmost-wins** (no free join) | **12/30** (p = 1.0 vs max) |
| tagged, max join, **crossover off** | **2/30** (p = 0.002 vs 13/30) |
| stack, 32 cells (§16) | 5/30; v2_imax 2/30 |
| stack, **64 cells**, rate 0.03 / 0.015 | **12/30 / 11/30** |
| stack v2_imax, 64 cells | 9/30 |

- **§16's tagged-vs-stack XOR gap was mostly tape length.** A 64-cell stack reaches 11–12/30,
  the tagged level (p = 1.0 vs 13/30). Findings item 13's "tagged runs beat the stack on XOR"
  does not survive this control; tagged_comb's 19/30 vs 12/30 is p = 0.12.
- **Crossover is causal for tagged XOR** (13 → 2/30 without it), as it was for OR (§14).
- **Removing the free join costs nothing.** Leftmost-wins solves 12/30. So the join can be
  built, and the "≥ ~8/30" branch of the plan applies: inspect the solvers.

**How leftmost solvers join the predicates** (post-mortem, live runs only)
- **8/12 compute XOR inside one run** (no live RECV). Their output run was built under tag 0
  (or drifted from an initial run) and gained its RECVs or ops in place.
- **4/12 join across runs: the output run reads one helper by RECV.** In all 4, the helper was
  a **former output run**. It was the live (first) tag-0 run of its lineage for 91–100% of
  115–540 generations, as a partial solution at fitness 0.42–0.75. It was then retagged away
  from 0 to the tag an output run reads. The solve followed 7, 96, 221 and 941 generations
  later.
  - Seed 7: the individual's output run already read that tag, so a dangling RECV was
    waiting. Seed 29: the read and the retag arrived in the same step. Seeds 2 and 19: the
    reading output run came later.
  - This is not silence-then-switch: the helper was expressed and selected the whole time.
    It is **co-option**. A working partial solution is demoted to a subroutine, and a new
    output run reuses it. That's the reuse event Step 3a of the plan wants to follow.
  - (The first version of the leftmost report labelled these "retag from silent", because
    nothing RECV-reads tag 0. The script now labels a retag from tag 0 as "retag from
    output run".)

**Parked map-bias items**
- **Frequency does steer which join is used** (`comb_cross`, 50 seeds each). With min at 4×
  and gate at 0.25×, the exact AND solvers joined by min 13, gate 1. Reversed weights: gate
  14, min 2. p = 2×10⁻⁵ for the gate share. Solves were the same: 15/50 vs 16/50. This
  settles §16's suggestive "which" result: among equivalent joins, frequency picks the one.
- **Route adoption survives true rarity** (`comb_rare`). With all markers at 0.02×
  (≈ 0.27% of draws), 9/10 exact solvers are joined runs, and solves are unchanged at 10/30.
  The same holds at 0.05× (9/10, 10/30).
- **IMAX frequency is a rate, not a floor** (`imax_time`, stack OR, 3000 gens):

  | IMAX | exact by 750 | by 1500 | by 3000 | median first exact |
  |---|---|---|---|---|
  | 0.05× | 7 | 15 | 21 | 1243 |
  | 0.25× | 4 | 9 | 15 | 1262 |
  | 1× | 15 | 19 | 21 | 568 |

  At 0.05× the arm catches up with 1× by generation 3000. Rarity delays the join and
  doesn't prevent it. The 0.25× arm sits lower than 0.05× at every point, so the ordering
  between the two rare arms is noise at 30 seeds.

**Take.**
- *Valley crossing:* without a free join, evolution still solves XOR at the same rate.
  Mostly it builds XOR inside one run; in a third of solvers it co-opts a former output run
  as a helper. No silent build was seen. So far there is still no evidence of a valley that
  selection can't climb here: partial solutions stay rewarded (lexicase, 0.42–0.75), and
  crossover is essential.
- *Map bias:* the frequency-knob picture is now complete for this system. Frequency sets
  arrival time (rate, not floor), picks among equivalent routes strongly (13:1 vs 2:14), and
  doesn't change whether a route is adopted even at 0.27% of draws.
- *Findings to revise:* item 13 (the XOR gap was tape), item 12 (the "which" part is now
  shown; IMAX is a rate).

**Next per the plan:** Step 3a on the 4 co-option solvers. Follow the helper past the first
solve: does it stay conserved, does anything else come to read it, and does it tolerate
mutation differently once read? Plus the recovery ruler (Step 1) on leftmost, which now has
real anchors (8 one-run and 4 two-run solvers).

**Corrections after the eleventh (Fable) review** (details in findings items 12–14):
- *IMAX "rate, not floor" was wrong.* At 0.05×, 18 of 21 solvers contain no IMAX. The rare
  arm solved OR by the join-free route at that route's speed, so rarity switches routes.
- *Co-option was overstated.* In 3/4 the helper is a sibling copy of the solver's own output
  run, reunited by crossover (the §17 pattern, wired by retag + RECV). Only 1/4 helpers
  already computed at the retag what the solver uses them for, so the retag mostly supplied
  a wired slot.
- *The 8 "one-run" solvers* are 1–2 cell edits of near-XOR bodies or of 0.75 specialists,
  except seed 8, which made the join by run fusion (a SEP deletion in front of a neutral
  `ADD`).
- *"No valley" is survivorship.* Only solving paths were inspected, and they show plateaus.
  The non-solvers need a neighbourhood scan.
- *Step 3a on these runs can't show reuse:* after the solve, elitism freezes the champion
  (helper unchanged, one reader, to generation 3000 in all 4). It needs a multi-output task
  (Step 2) first.

---

## 20. Neighbourhood scan: leftmost-XOR plateau genomes and non-solvers (2026-09-28)

**What would be interesting to see** (eleventh review, item 1): whether the genomes stuck on
the XOR plateau have any step up. Non-solvers with empty neighbourhoods would mean a
valley that lexicase can't climb.

**Setup.** `experiments/chem_tape/xor_neighbourhood.py` on `mapbias_xor_leftmost` (§19),
about 10 s. Genomes scanned: each solver's champion 100 generations before its first exact
generation, and each non-solver's final champion (generation 3000).
- **Single mutants (~11,000 per genome):** every op change; tag changes on SEP and RECV cells
  (other tags are inert); every deletion; and every insertion after a cell, as the mutation
  operator does it (SEP and RECV with every tag, other ops with one inert tag).
- **Double mutants:** 20,000 sampled per genome.

Counted: mutants exact on all 10,000 lists; mutants gaining a training case without losing
one; mutants with higher balanced fitness.

**Sanity check.** One generation before the solve, champions do have exact single mutants
(seeds 22: 6, 3: 9, 1: 4, 23: 2), so the tool finds steps when they exist. At that point the
solver itself is not a single mutant of the previous champion (9–121 cells differ); it came
from elsewhere in the population, by crossover.

**Results** (reworded after an outside read; see the correction below).
- **No neighbour dominates, none is fitter, many trade or are neutral.** For all 18
  non-solvers and all 12 solvers' champions 100 generations before the solve, none of
  ~11,000 single or 20,000 sampled double mutants dominates the champion (gains a training
  case without losing one) or raises balanced fitness.
  - Case-*trading* mutants (gain some cases, lose others) are common: 486–6,388 singles
    per genome, 1,238–13,611 sampled doubles. Lexicase can select those when a gained case
    comes early in the case order, depending on the rest of the population.
  - Neutral singles: 854–9,995 per genome.
  - So these are plateaus with many neutral moves, **not strict local optima**. The
    supported statement: no fitter or dominating neighbour was found (singles enumerated,
    doubles sampled). A longer neutral route, or selection of a trade, remains possible.
- **Where solves came from.** One generation before the solve, the champions do have exact
  single mutants, but the solver itself came from elsewhere in the population (9–121 cells
  differ), by crossover.
- **3/18 non-solvers fit all 64 training cases but are not exact** (seeds 15, 20, 26; 98–100%
  on all lists). Two of them are one point mutation from exact XOR (seed 20: 9 single
  mutants; seed 26: 3). Selection can't see it, because training is already perfect. These
  count as training-set overfit, not stuck; 15/30 runs are genuinely unsolved.

**Take.** The champions' immediate neighbourhoods hold no strict improvement. Improvements
seen in solvers arrived through the population, mostly by crossover. "Valleys under mutation
that recombination crosses" is a **hypothesis**. It is consistent with crossover-off XOR
collapsing to 2/30 (§19), but not shown by this scan. The open question is whether
non-solver *populations* (not only champions) still hold complementary parts; §21 saves
final populations to answer that.

**Correction.** The first version of this entry said "strict local optima" and "no step
improves anything lexicase sees". Both were too strong: the scan's "case gain" required
gaining without losing any case, which misses lexicase-selectable trades, and the neutral
counts rule out strict optima.

**Review.** One Codex review before tonight's run: the insertion moves didn't match the
mutation operator (front insertion; SEP insertions need every tag). Fixed and re-run; the
conclusion holds.

**Caveats.** Double mutants are sampled (20,000 of ~10⁸). Only the champion of each
generation is on disk (history.csv), not the population. The plateau genome is the
champion at a fixed offset (100 generations), not a measured plateau start.

---

## 21. Plan: XOR valley controls (queue_s21)

**What would be interesting to see:** whether the XOR plateau becomes a valley once lexicase
stops protecting partial solutions, and whether recombination is essential when the join
has to be built. One sweep, `xor_valley_ctrl` (30 seeds × 3000 gens, ~45 min):
1. leftmost-wins, **tournament** on balanced fitness. Prediction: well below 12/30. A
   collapse would mean the partial solutions are no longer reachable under that selection
   scheme, not that the landscape changed: fitness values are identical, only who gets to
   reproduce differs.
2. leftmost-wins, lexicase, **crossover off**. Prediction: ≤ 3/30 (max-join XOR went 13 → 2).
3. max join, tournament: a reference, so a drop in arm 1 can be told apart from tournament
   hurting XOR in general.
`overnight_analysis.py` now also labels tournament arms, and its knockout summary uses the
run's own join rule (it used max before, which was wrong for leftmost). All runs save
`final_population.npz`, so non-solver populations can be checked for complementary parts,
and for training-perfect individuals that generalise when the champion doesn't.

---

## 22. §21 results: XOR valley controls, and stack crossover-off (2026-09-29, overnight)

`xor_valley_ctrl` (queue_s21, commit `5a85eb5`, 22 min) and `xor_stack64_nox` (queue_s22).
Outputs in `experiments/output/2026-09-28/`. Population analysis:
`experiments/chem_tape/population_parts.py`, which evaluates every final-population genome
on all 10,000 lists, per (max>5, sum>10) quadrant. A genome "covers" a quadrant at ≥ 95%.

| arm | exact XOR | final champion train balanced (median, range) |
|---|---|---|
| tagged leftmost, lexicase (§19) | 12/30 | — |
| tagged leftmost, **tournament** | **0/30** (p = 0.0001) | 0.50 (0.50–0.75) |
| tagged max, **tournament** | **0/30** (p < 0.0001 vs 13/30) | 0.50 (0.50–0.75) |
| tagged leftmost, lexicase, **crossover off** | **4/30** (p = 0.04 vs 12/30) | 0.80 (0.67–1.0) |
| stack 64 cells, **crossover off** | 7/30 (p = 0.27 vs 12/30) | — |

- **Without lexicase, XOR is out of reach under either join rule, and it isn't a valley in
  the usual sense: it's flat.** Under tournament the champions end at balanced 0.5, the
  constant-output level. In 26/30 populations the largest class covers only the two
    quadrants where XOR is 0, i.e. programs that output 0 (or nearly) on every list.
  - The reason is XOR's parity: a single predicate scores exactly 0.5 on XOR (right on half
    of each class). So the building blocks carry no aggregate fitness signal. Even the 0.75
    partial solutions (p1∧¬p2 etc.) need both blocks first.
  - Lexicase sees the blocks case by case and keeps them. That is the whole difference
    between 0/30 and 12–13/30.
  - This also scopes items 13–14: those are lexicase results, and under summed fitness
    XOR's plateau is at 0.5, not 0.75.
- **Crossover matters for building the join (4 vs 12/30), less for the stack (7 vs 12/30).**
  All 26 unsolved crossover-off leftmost populations hold individuals whose quadrant covers
  together reach all four quadrants. So the parts exist, but without recombination they
  rarely end up in one genome. That fits "recombination crosses what mutation doesn't"
  (§20 hypothesis), without proving it. The stack's smaller drop (not significant) matches
  §19: stack solvers are mostly built in place.
- 1 stack crossover-off population holds an exact individual that isn't the recorded
  champion; elsewhere, the champion is exact whenever any individual is.

**Leftmost XOR to 10,000 generations (`xor_leftmost_long`, queue_s22).** Same config and
seeds as §19, lineage tracking off. **All 30 seeds replay §19's first 3,000 generations
exactly** (champion genome by generation), so the extension is a pure continuation. The
machine slept for much of the run: 4.9 h wall time for ~1 h of compute.
- **Slow, not all stuck.** Exact by generation 3000: 12/30; by 5000: 14; by 10,000: 17.
  The late solvers (seeds 10, 28, 5, 27, 12 at 3801, 4945, 5027, 5632, 9356) are all among
  the non-solvers §20 scanned at generation 3000. There, their champions had no fitter or
  dominating single or sampled double neighbour. So the plateau was left later anyway, by
  neutral moves or through the rest of the population, as §20's rewording expected.
- **Training-set overfit grows with time.** The three §20 overfit runs (15, 20, 26) never
  become exact. By generation 10,000, 6 of the 13 unsolved runs fit all 64 training cases
  without being exact on all lists, so selection has nothing left to act on. The other 7
  sit at 0.75–0.97 training balanced.
  - So at this budget about half the remaining failures are a training-set limitation
    (64 cases; exactness judged on 10,000), not a landscape property.
  - Any follow-up on "stuck" runs should use more training cases, or resample them.

**Final populations: the champion-only score undercounts solves**
(`population_parts.py` on the §22 sweeps).
- **Exact individuals hide behind training ties.** When several individuals fit all 64
  training cases, the recorded champion is one of them, arbitrarily, and may not be exact
  even when many others are.
  - Long runs: seeds 20, 26, 15 (the "overfit" non-solvers of §20 and above) hold 470, 439
    and 358 exact individuals out of 1,024 at generation 10,000. Seed 6 holds 6.
  - Seeds 30–99: seed 45 holds 449.
  - **Populations containing an exact individual:** long runs 21/30 (vs 17/30 exact
    champions); seeds 30–99 20/70 (vs 19/70). Every champion-based XOR count in §16–§22
    is a lower bound. The §20 "overfit" seeds were probably solved at the population level
    already; the sweeps that ran to 3000 saved no population to check.
  - Fix for future sweeps: report population-level exactness (saved populations), or pick
    the champion by holdout among training ties.
- **Unsolved lexicase populations always hold complementary parts.** In every unsolved
  population (seeds 30–99: 50/50; long: 9/9; crossover-off: 26/26; stack crossover-off:
  22/22), the quadrant covers present together reach all four quadrants. Under tournament
  only 6–7/30 do. The largest class in unsolved lexicase populations covers only the two
  quadrants where XOR is 0: programs that output 0 on the positive lists.
  "Parts present" is weak evidence: covers can come from different, incompatible programs.

**More leftmost solvers** (`xor_leftmost_more`, seeds 30–99: 19/70 exact champions;
post-mortem `postmortem_leftmost_more/`, 19/19 reproduced).
- 18/19 solve inside a single run, and 1/19 has a helper (retag from a former output run).
  Seed 54's one "live RECV" reads tag 0, i.e. its own output run, which evaluates as a
  cycle (0), so it counts as self-contained.
- Pooled with §19: 31 solvers from 100 seeds; 26 single-run, 5 helper (all from a former
  output run). §19's 4/12 helpers was high by chance; helper co-option is the minority
  route (≈ 16%).
