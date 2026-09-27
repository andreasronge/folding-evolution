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
