# Can evolution snap building blocks together? — A hobby research log

*Source notes for a ~30 minute podcast (e.g. Google NotebookLM). Audience: software developers
with basic knowledge of evolutionary algorithms and genetic programming. Dense on purpose; the
podcast can unpack it. All numbers come from the project notebook
(`docs/map-bias/notebook.md`, sections §1–§14) and the reviewed summary
(`docs/map-bias/findings.md`).*

---

## 1. The one-paragraph pitch

This is a hobby research project about *genetic programming* — evolving small programs with
mutation, crossover and selection. It started from a biological hunch: in nature, a gene is a
linear sequence that folds into a 3D protein, and the protein's shape, not its raw sequence,
decides what it does. What if evolved programs worked the same way — a genome that "develops"
into a program, instead of being the program? Over several months that hunch turned into a much
sharper question: **can evolution combine two working building blocks into a new solution by
recombination (crossover), without the combination crashing?** Two days of intensive,
AI-assisted experiments — with one AI model writing and running code, another reviewing the
design, and a third reviewing the code before every overnight run — produced a clear answer:
*yes, but it only pays when joining the blocks is cheap, and the thing that really makes it
work is keeping the blocks alive in the population.* Along the way the project found its own
bugs, retracted several of its own claims, and ended with a short list of findings that
survived review.

---

## 2. Background: what problem are we poking at?

### 2.1 Genetic programming in one minute

Genetic programming (GP) evolves programs. You keep a population of candidate programs, score
each one on test cases (its *fitness*), keep the better ones, and make new ones by *mutation*
(random small edits) and *crossover* (splicing parts of two parents together). Repeat for
hundreds or thousands of generations.

Two classic worries in GP are relevant here:

- **Building blocks.** The textbook story (Holland, Goldberg) is that evolution works by
  finding useful partial solutions — building blocks — and crossover combining them into
  bigger ones. In practice it is hard to show crossover actually does this; often it just
  breaks things.
- **Deception / local optima.** Evolution follows fitness gradients. If a cheap shortcut gets
  most of the test cases right, the population piles onto the shortcut and never finds the
  real solution.

### 2.2 The genotype–phenotype map

In biology the *genotype* (DNA) is not the *phenotype* (the organism); development sits in
between. In GP the analogous thing is the **genotype–phenotype map (GP map)**: the rule that
turns a genome into a program. Most GP systems use a trivial map (the genome *is* the program
tree). This project has explored non-trivial ones:

- **Folding track (earlier, completed):** a character string folds on a 2D grid, and
  characters that end up adjacent "bond" into program fragments. Protein-inspired.
- **Chem-tape (the track used here):** a 1D tape of tokens. Adjacent tokens "bond" into runs,
  and the longest runs are executed as a stack program. Simpler, faster, and the workhorse for
  everything in this episode.
- **Cellular automata (paused):** evolve CA rules that compute functions like parity.

Theory backdrop: Lee Altenberg's *constructional selection* and Wagner & Altenberg's work on
*evolvability* argue that the GP map itself shapes what evolution can find — a map can make
some variations likely and others essentially impossible.

### 2.3 The reframing

An early critical review of the project pointed out that "does a developmental encoding beat a
direct one?" is an old question with a known answer — *it depends on the problem* (see Clune
et al. 2011 on indirect encodings). So the project was reframed around two sharper questions:

1. **How does the map bias which programs evolution finds?** (Measure the bias; test whether it
   predicts outcomes — the "arrival of the frequent" idea from Schaper & Louis.)
2. **Can evolution combine building blocks without crashing — and what does it take?**

The project is explicitly a *hobby*: lab-notebook style, a short "what would be interesting
to see" note before each run, plain results after, and heavier rigor only when a result looks
worth promoting.

---

## 3. The system under the microscope: chem-tape

A **genome** is a tape of 32 tokens from a ~22-token alphabet: `INPUT` (push the input list),
constants (`CONST_0`, `CONST_1`, `CONST_2`, `CONST_5`), list reductions (`SUM`, `REDUCE_MAX`),
arithmetic and comparison (`ADD`, `GT`), stack shuffling (`DUP`, `SWAP`), a selector (`IF_GT`),
a no-op, and two *separator* tokens.

**Decoding:** adjacent non-separator tokens "bond" into runs; the decoder (called `BP_TOPK`)
takes the three longest runs, concatenates them, and executes them as a postfix program on one
stack. **The output is whatever ends up on top of the stack.** A control arm ("Arm A") simply
executes the whole tape, i.e. direct encoding.

**Tasks:** inputs are lists of four digits 0–9 (so there are exactly 10,000 possible inputs).
Tasks are built from two predicates:

- `max > 5` (is any element bigger than 5?)
- `sum > 10`
- and combinations: **AND**, **OR**, XOR of those two.

The canonical AND program is 12 tokens:
`CONST_0 INPUT REDUCE_MAX CONST_5 GT INPUT SUM CONST_5 CONST_5 ADD GT IF_GT`
— compute `max>5`, compute `sum>10`, then select.

Why this toy? Because it is small enough to enumerate *everything*: every possible input, every
single and double mutation of a genome, 50 million random genomes per setting. That makes it
possible to measure things that are usually just assumed.

---

## 4. The story, experiment by experiment

### Episode 1 — How biased is the map? (notebook §1)

**Experiment:** sample 50 million random tapes for each of 61 decoder/task settings, run them,
and count how often each *behaviour* (the vector of answers on the training cases) appears.
Then look up how common the behaviours were that past evolution runs (1,230 of them) actually
ended on.

**Results:**
- The map is *extremely* biased. One constant behaviour takes 66–88% of all random tapes; only
  22–636 distinct behaviours show up out of 50 million tapes.
- If ≥ 1 in 20,000 random tapes solves a task, evolution solves it essentially always.
- But evolution also routinely finds behaviours rarer than 1 in 50 million — cumulative
  selection climbs where random sampling never looks. **Bias shapes outcomes but isn't
  destiny.**
- Surprise: the "developmental" chem decoder and the direct encoding had nearly identical
  bias on this alphabet — the map is close to an identity map, which limits what map-level
  claims can say.

Research link: *arrival of the frequent* (Schaper & Louis 2014) and *simplicity bias* in
input–output maps (Dingle, Camargo & Louis 2018).

### Episode 2 — The AND trap is a wide valley (§2)

Past runs on the AND task got stuck at 92% accuracy: they learned `max > 5` alone, which is
right on most training cases (a "proxy"). **Experiment:** take all 40 stuck genomes and try
*every* single mutation and *every* double mutation — 8.7 million neighbours.

**Result:** not one neighbour is better than the stuck parent. Building the true solution from
the proxy one token at a time gives fitness 0.92 → 0.92 → 0.50 → 0 → 0 → 0 → 0 → 0.72 → 1.0:
six steps that are all *worse* than the proxy, because a half-built `sum>10` block leaves junk
on top of the shared stack. The missing piece isn't a bit of glue; it's a whole building block.

### Episode 3 — Three ways across the valley (§3)

Four setups, 30 seeds each, same budget:

| setup | solved AND |
|---|---|
| baseline | 1/30 |
| add a `MIN` primitive (AND in one op) | 1/30 |
| **lexicase selection** | **14/30** |
| "v3" domains + linkers chemistry | 2/30 |

- **Lexicase selection** (Spector; Helmuth, Spector & Matheson 2015) doesn't average test cases
  into one number. For each parent it picks, it shuffles the cases and keeps only individuals
  that pass case 1, then case 2, and so on. Individuals that are the *only* ones to solve some
  rare cases survive even with a worse average — so the half-built `sum>10` specialists aren't
  wiped out by the `max>5` proxy. It's diversity preservation for free.
- The **missing primitive wasn't the problem**: adding `MIN` did nothing.
- **v3** was a first chemistry attempt at "add silently, switch on in one step": runs become
  *domains* on their own stacks, joined by *linker* tokens (one of them "silent"). It didn't
  help — the silent route never formed, because under tournament selection nothing keeps a
  silent block around.

A later check showed the AND task has an **arithmetic shortcut**: `sum + 10·max > 70` is right
on 98.6% of all inputs. And only 6 of the 14 lexicase "solvers" were exactly right on all
10,000 inputs; the other 8 were approximations that fit the 64 training cases. Lesson that
changed the whole method: **judge solutions on every possible input, not the training set.**

### Episode 4 — Following the family tree (§5–§7)

The runs were re-run with **lineage tracking** (every child records its parents and whether it
came from crossover or mutation; tracking uses no randomness, so runs replay exactly). Then:

- **Crossover spectrum:** ~360,000 children scored on all 10,000 inputs. Pure crossover crashed
  (fell clearly below the fitter parent) 18.5% of the time vs 33% for mutation — gentler, but
  mutation was twice as likely to *improve* a child.
- **Waiting times:** in the exact solvers, both blocks (`max>5` and `sum>10` pieces) were
  present somewhere in the population within 5–217 generations, but from "both blocks in one
  genome" to the solve took 137–700 generations. **Supply is fast; arrangement is slow.**
- **Guaranteed-supply merge test:** evolve 25 exact `max>5` donors and 25 exact `sum>10`
  donors, then cross every pair (≈470,000 children). **Zero** children computed AND or even kept
  both blocks. Why: in the stack chemistry both donors put their final comparison at the *end*
  of the tape (the output is the top of the stack), so a single cut always cuts one block off.
  Blocks compete for the same position. In v3, evolution smeared each predicate across several
  domains and used the linkers as arithmetic, so no single domain carried a block.

The diagnosis: **blocks need to be closed units with one output that recombination can move
and something can join.**

### Episode 5 — Tagged runs: connection by binding, not position (§8–§10)

Nature's answer to "position means meaning" is *binding*: a transcription factor finds its
target sequence wherever it sits in the genome; protein domains connect through binding
surfaces. The project borrowed that idea (it exists in GP too — Spector's tag-based modules,
Lalejini & Ofria's SignalGP, Banzhaf's artificial regulatory networks, Holland's tags):

- Each **run** gets a **tag** (a separate 64-value field). A run executes on its own stack.
- A new op, **`RECV t`**, pushes the output of the run tagged `t` (no match → 0; several
  runs with the same tag → combined by **max**).
- The organism's output is the run tagged 0.
- Nothing imposes a tree or a chain; any wiring can emerge.

**Results:**
- Blocks stay closed: each evolved predicate lived in exactly one run.
- 940 transplants of a run from one donor into another were **100% inert** — zero crashes
  (vs 26–46% crashes in the other chemistries).
- But in an AND race, tagged runs did no better than baseline (7/30 vs 6/30 exact), and every
  solver computed AND inside a single run. Building in place is simply cheaper than wiring two
  runs together; with each block used once, modularity has nothing to gain.

A reviewer's key insight: "several same-tag runs → max" means **the chemistry's built-in join
is OR** (for true/false values, max = OR). The modular route exists for OR, not AND — and the
AND race had tested the one case where it doesn't exist.

### Episode 6 — The overnight run (§11–§12)

Before launching an ~5-hour overnight queue, the code went through **two rounds of review by
a separate AI code reviewer**, which found real problems: the gene-duplication operator could
truncate genomes, the OR task could be solved by `sum>10` alone in 38% of training samples,
the "recovery after goal switch" metric compared scores across different goals, and more. After
fixes, a subtle issue surfaced: with training inputs drawn equally from all four
(`max>5`, `sum>10`) combinations, AND is only 25% positive, so "always answer 0" scored 75%
and populations drifted into doing nothing. Fix: **balanced accuracy** as fitness.

Three arms: baseline stack chemistry, tagged runs, tagged runs + **gene duplication** (copy a
run under the same tag — a redundant expressed copy — or a fresh tag — a silent "pseudogene",
after Ohno's *Evolution by Gene Duplication*).

**OR race (the task where the modular route is free):**

| arm | exact OR | median generation of first exact solve |
|---|---|---|
| baseline | 10/30 | 595 |
| tagged runs | 19/30 | 290 |
| tagged + duplication | 25/30 | 250 |

Tagged solvers were two output runs joined by max. Lineage showed the second output run
arrived by **crossover** in 43 of 44 solvers (against a ~70% base rate), and in 20 cases it
was an exact copy of the *other parent's* output run — a genuine two-parent block merge.

**Fixed AND:** 9/30 in all three arms — no change.

**Modularly varying goals** (Kashtan & Alon 2005; Kashtan, Noor & Alon 2007): switch the goal
max>5 → sum>10 → AND every 5, 20 or 50 generations. Surprise: it helped the *stack baseline*
(exact AND reached in 18/30 runs vs 9/30 with a fixed goal, at periods 5–20), not tagged runs,
which tracked the switches worse.

### Episode 7 — Is it modularity or just a cheap join? (§13–§14)

A good positive result deserves controls. Three were run, plus the "closing" experiment:

| OR setup | exact OR |
|---|---|
| tagged runs, **crossover turned off** | **2/30** |
| tagged runs where same-tag runs give the **leftmost** value (no free OR) | 11/30 |
| **stack baseline + one integer MAX op** (OR costs one op) | **18/30** |
| reference: tagged runs | 19/30 |
| reference: stack baseline | 10/30 |

- **Crossover is causal:** without it, tagged runs collapse.
- **The advantage over the baseline is the cost of the join, not modularity:** give the plain
  stack a one-op OR and it matches tagged runs; take the free OR away from tagged runs and they
  drop to baseline level.

**Evolvable combiner** (the closing experiment): add three "combine marker" ops that can sit
anywhere in a run's body — like a regulatory motif — and decide how that run joins earlier
runs with the same tag (min, add, or gate; default max). Result on AND:
- Still **9/30** solved — the same as every other arm.
- But **all 9 solvers were two separate runs joined by `min` or `gate`** (vs 1–3 of 9 before),
  and found sooner (median generation 640 vs 1,000–1,580).

**When joins are heritable, evolution chooses the modular route every time — it just doesn't
succeed more often.**

One more check killed a tempting explanation: tagged runs tracking goal switches badly was
*not* because their mutations were too gentle. Measured directly, tagged children change
behaviour *more* often (35% vs 21%); even with the rate lowered to match, tagged runs tracked
worse. It's a property of the chemistry.

---

## 5. The findings (reviewed, scoped)

Scope: chem-tape programs on length-4 lists over 0–9; two-predicate tasks; population 1,024;
1,500–3,000 generations; 30 seeds per arm; "exact" = right on all 10,000 inputs. Baseline vs
tagged is a comparison of whole chemistries (tape length, indels and crossover differ).

1. Map bias predicts which tasks are easy; evolution routinely finds behaviours rarer than 1 in
   50 million random genomes. On this alphabet the developmental decoder ≈ direct encoding.
2. The AND proxy basin is a wide valley: no fitter neighbour within two mutations of any of 40
   stuck genomes (8.7M neighbours).
3. Exactness on all inputs is the only meaningful solve criterion: every two-predicate
   composition here is 92–97% linearly separable, and 8 of 14 "solvers" only fit training data.
4. A new primitive (MIN) or a safe container (v3 domains) alone did nothing.
5. Lexicase fixes block supply (AND 1/30 → 14/30); arrangement then becomes the bottleneck
   (suggestive; small n).
6. In a stack chemistry, blocks compete for the tape end; a guaranteed-supply merge test gave
   0 children with both blocks.
7. Tagged runs make safe transplants possible without imposing a shape: 100% of 940
   non-output transplants inert.
8. On OR, crossover merges blocks (causal), but the advantage is the join's cost: a stack with
   a one-op join does as well (18/30 vs 19/30).
9. With heritable joins, every AND solver becomes two joined runs, found sooner — but solve
   rates don't rise.
10. Varying goals: a suggestive benefit for the stack baseline; tagged runs track worse, and not
    because of mutation rate.
11. The silent-then-switch-on ("pseudogene") route was never observed in any chemistry.

---

## 6. How the research was done — the AI-assisted workflow (good podcast material)

- **Three AI roles.** One model (Claude) wrote code, ran experiments, analysed results and kept
  the notebook. A second model (Fable, via a sub-agent) acted as a critical design reviewer
  after each result — eight review rounds. A third (OpenAI Codex, GPT-6 Sol, high reasoning)
  reviewed the *code and experiment design* before each overnight run.
- **The reviewers disagreed usefully — and were sometimes wrong.** Fable claimed the lexicase
  implementation added hidden "niching"; checking showed it can't (identical runs on 30/30
  seeds), and the claim was retracted. Fable proposed a replacement task "a linear rule can't
  carve"; checking with balanced accuracy showed it was just as linear. Fable predicted tagged
  mutations were too gentle; measurement showed the opposite. The human-in-the-loop lesson:
  **treat every reviewer claim as a hypothesis to check with a cheap computation.**
- **Bugs found in old results.** Building new features exposed two bugs in earlier work: a
  Rust fast path that silently ignored two tokens (making an entire old experiment unsolvable
  as run — now marked invalid), and a decoder that never switched to the new separator tokens
  (documented, fixed behind an opt-in flag so old runs stay reproducible).
- **Self-corrections were recorded, not hidden.** A wrong "crash" bar, an overstated "80% of
  innovations come from crossover" (most were also mutated), and "inert for free" are all
  visible as retractions in the notebook.
- **Practical engineering:** deterministic runs (lineage tracking uses no randomness, so any
  seed can be replayed exactly), an overnight queue runner with completion markers, smoke tests
  at tiny scale before every big launch, a vectorised interpreter checked for exact parity
  against the reference executor on hundreds of random programs.

---

## 7. What it means (for people who build evolutionary systems)

- **Selection often matters more than representation.** Lexicase selection did more for the
  hard task than any chemistry change.
- **Measure solutions on the whole input space when you can.** Training-set "solves" were
  approximations more than half the time.
- **Crossover can be a real merge operator** — but only when blocks are closed units and the
  representation doesn't make blocks compete for the same position.
- **Modularity has to pay.** Evolution will happily build everything in one piece if that's
  cheaper; making modular recombination *safe* isn't enough to make it *chosen* unless blocks
  are reused, goals shift, or joins are cheap.
- **"Cheap join" is the real lever.** The plain stack with a one-op join did as well as the
  fancy modular chemistry. Before building an elaborate representation, check whether a
  missing primitive explains the difference.
- **Always run the boring controls.** Crossover-off, "remove the free join", and "give the
  baseline the same primitive" turned an exciting modularity story into a more honest, narrower
  one.

---

## 8. Future directions

1. **Build the join across a valley.** Here the combiner was chosen from a menu (min / add /
   gate markers). The open question is whether evolution can *construct* a join that takes
   several unrewarded steps — the original valley from Episode 2 — and what makes it possible
   (lexicase partial credit, neutral networks, duplication then divergence).
2. **Reuse as the driver of modularity.** Tasks where one block is used by several consumers
   (e.g. several outputs sharing a sub-result, or XOR, which uses a block twice) — the classic
   biological reason modules exist.
3. **Varying goals, properly powered.** The stack baseline's suggestive benefit from switching
   goals (a Kashtan–Alon-style effect) deserves a replication with matched evaluation budgets.
4. **Maps that actually differ.** Since the chem decoder turned out to be near-identity, redo
   the bias measurements on the folding map and a tree-GP generator, where the biases should
   differ a lot.
5. **A standard tree-GP baseline** (e.g. DEAP) on the same tasks, to anchor all numbers.
6. **LLMs as variation operators.** Systems like FunSearch and AlphaEvolve use language models
   to propose program edits; an obvious hybrid is an LLM crossover operator used for a small
   fraction of children, evaluated with the same crash/improvement spectrum used here.
7. **Cellular-automata development.** The paused CA track plans damage/regeneration assays
   ("is the CA actually developing?"), in the spirit of Growing Neural Cellular Automata.

---

## 9. Glossary

- **Genotype / phenotype / GP map:** genome / resulting program / the rule turning one into the
  other.
- **Chem-tape:** this project's 1D representation — tokens bond into runs, runs execute on a
  stack.
- **Run:** a contiguous bonded stretch of tokens; in "tagged runs", a unit with its own tag and
  stack.
- **Proxy / proxy basin:** a simple rule (e.g. `max>5`) that scores well on most cases and
  traps the population.
- **Lexicase selection:** parent selection that filters candidates case-by-case in random order
  instead of averaging.
- **Balanced accuracy:** mean of accuracy on positive and on negative cases; a constant answer
  scores 0.5.
- **Exact:** correct on all 10,000 possible inputs.
- **Lineage / main line:** the ancestry of the final best genome, following the fitter parent at
  each crossover.
- **Gene duplication (Ohno):** copying a gene; the copy can be redundant (same tag) or silent (new
  tag) and free to diverge.
- **Modularly varying goals (MVG):** switching between goals that share sub-problems, known to
  promote modular structure in some systems.

---

## 10. Reading list (titles given so they can be looked up)

**Genotype–phenotype maps, bias, evolvability**
- Lee Altenberg (1995), *Genome growth and the evolution of the genotype–phenotype map*, in
  *Evolution and Biocomputation*, LNCS 899. Author site: https://dynamics.org/Altenberg/
- Günter P. Wagner & Lee Altenberg (1996), *Complex adaptations and the evolution of
  evolvability*, Evolution 50(3). https://doi.org/10.1111/j.1558-5646.1996.tb02339.x
- Steffen Schaper & Ard A. Louis (2014), *The arrival of the frequent: how bias in
  genotype–phenotype maps can steer populations to local optima*, PLoS ONE.
  https://doi.org/10.1371/journal.pone.0086635
- Kamaludin Dingle, Chico Q. Camargo & Ard A. Louis (2018), *Input–output maps are strongly
  biased towards simple outputs*, Nature Communications.
  https://doi.org/10.1038/s41467-018-03101-6
- Kenneth O. Stanley & Risto Miikkulainen (2003), *A taxonomy for artificial embryogeny*,
  Artificial Life 9(2). https://doi.org/10.1162/106454603322221487
- Jeff Clune, Kenneth O. Stanley, Robert T. Pennock & Charles Ofria (2011), *On the performance
  of indirect encoding across the continuum of regularity*, IEEE Trans. Evolutionary
  Computation. https://doi.org/10.1109/TEVC.2010.2104157

**Modularity, varying goals, learning in evolution**
- Nadav Kashtan & Uri Alon (2005), *Spontaneous evolution of modularity and network motifs*,
  PNAS. https://doi.org/10.1073/pnas.0503610102
- Nadav Kashtan, Elad Noor & Uri Alon (2007), *Varying environments can speed up evolution*,
  PNAS. https://doi.org/10.1073/pnas.0611630104
- Richard A. Watson & Eörs Szathmáry (2016), *How can evolution learn?*, Trends in Ecology &
  Evolution. https://doi.org/10.1016/j.tree.2015.11.009
- Kostas Kouvaris, Jeff Clune, Loizos Kounios, Markus Brede & Richard A. Watson (2017), *How
  evolution learns to generalise*, PLoS Computational Biology.
  https://doi.org/10.1371/journal.pcbi.1005358

**Building blocks, selection, diversity**
- David E. Goldberg (2002), *The Design of Innovation: Lessons from and for Competent Genetic
  Algorithms* (building-block supply, growth and mixing).
- Thomas Helmuth, Lee Spector & James Matheson (2015), *Solving uncompromising problems with
  lexicase selection*, IEEE Trans. Evolutionary Computation.
  https://doi.org/10.1109/TEVC.2014.2362729
- Joshua D. Knowles, Richard A. Watson & David W. Corne (2001), *Reducing local optima in
  single-objective problems by multi-objectivization*, EMO 2001.
- Jose Guadalupe Hernandez, Alexander Lalejini, Emily Dolson & Charles Ofria (2019), *Random
  subsampling improves performance in lexicase selection* (down-sampled lexicase), GECCO
  companion.

**Tags, binding and regulatory-network GP**
- John H. Holland (1995), *Hidden Order: How Adaptation Builds Complexity* (tags in the Echo
  model).
- Lee Spector, Brian Martin, Kyle Harrington & Thomas Helmuth (2011), *Tag-based modules in
  genetic programming*, GECCO 2011.
- Alexander Lalejini & Charles Ofria (2018), *Evolving event-driven programs with SignalGP*,
  GECCO 2018. https://arxiv.org/abs/1804.05445
- Wolfgang Banzhaf (2003), *Artificial regulatory networks and genetic programming*, in Genetic
  Programming Theory and Practice.
- John R. Koza (1994), *Genetic Programming II: Automatic Discovery of Reusable Programs*
  (automatically defined functions).

**Gene duplication**
- Susumu Ohno (1970), *Evolution by Gene Duplication*.
- Allan Force, Michael Lynch, F. Bryan Pickett, Angel Amores, Yi-Lin Yan & John Postlethwait
  (1999), *Preservation of duplicate genes by complementary, degenerative mutations*, Genetics.
  https://doi.org/10.1093/genetics/151.4.1531

**Cellular automata and development**
- Melanie Mitchell, Peter Hraber & James P. Crutchfield (1993), *Revisiting the edge of chaos:
  evolving cellular automata to perform computations*, Complex Systems.
  https://arxiv.org/abs/adap-org/9303003
- Alexander Mordvintsev, Ettore Randazzo, Eyvind Niklasson & Michael Levin (2020), *Growing
  neural cellular automata*, Distill. https://distill.pub/2020/growing-ca/

**LLMs as evolutionary operators**
- Bernardino Romera-Paredes et al. (2023), *Mathematical discoveries from program search with
  large language models* (FunSearch), Nature. https://doi.org/10.1038/s41586-023-06924-6
- Joel Lehman et al. (2022), *Evolution through Large Models*. https://arxiv.org/abs/2206.08896

**Precursor idea for "strings that fold into programs"**
- Douglas Hofstadter (1979), *Gödel, Escher, Bach* — the *Typogenetics* chapter.
