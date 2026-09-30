# Plan: crossing the valley, then evolving stable machinery

Written 2026-09-28. Hobby mode: one "what would be interesting to see" paragraph per arm
in the notebook, results written up plainly afterwards. No pre-registration apparatus.
Updated 2026-09-28 after the stable-machinery discussion. This remains an exploratory
roadmap, not a pre-registration or a queue submission.
Context: map-bias notebook §1–§18, findings.md items 2, 9, 11–13.

## Question

Can evolution build a missing join, and, where a fitness valley exists, cross it without
the designer handing it the join? Then: **can yesterday's evolved solution become
tomorrow's stable building material?** The map-bias line showed that supplied joins
(free max, IMAX, combine markers) can make particular routes accessible. It has not yet
established evolution building a join across a valley (§9 open problem).
The general theme is still map bias: whether
the genotype→program map makes half-built things harmful (stack: junk on the stack),
neutral (tagged runs: inert transplants), or useful (a task family that rewards them).

Five candidate routes, from the original discussion (these historical references remain
from memory; checked references for the machinery follow-up are at the end):

1. **Drift / tunnelling** (Weissman et al. 2009): large populations cross narrow valleys;
   crossing times depend on mutation, selection, population size and path structure.
   Measure the recovery curve rather than assuming exponential scaling with width.
2. **Recombining blocks**: already understood here (§12–§14). It moves parts but doesn't
   create the join.
3. **Lifetime learning over structure** (Hinton & Nowlan 1987). The earlier threshold-plasticity
   null tuned a number; the valley is structural.
4. **Silence, then switch** (pseudogenes, Hsp90, Lenski's citrate duplication/promoter
   capture). Not observed in the inspected lineages; §17 shows the setup gives this
   route little opportunity, so its absence is not a general refutation.
5. **Useful intermediates** (Lenski, Ofria, Pennock & Adami 2003: EQU evolved only when
   simpler logic functions were also rewarded in their tested setup). This changes
   what the world rewards rather than the machine.

## What stable machinery would mean here

Keep three questions separate:

- **Supplied machinery:** a fixed interpreter operation or join rule, such as max or a
  threshold. Tests what infrastructure makes evolution accessible.
- **Protected machinery:** an evolved block that the experimenter freezes or mutates
  less often. Tests the consequence of imposed protection.
- **Entrenched machinery:** an evolved block acquires functional dependants; mutations
  still occur normally, but selection preserves its behaviour because changing it
  damages those dependants. This is the main new follow-up (Step 3).

Conservation is not necessarily robustness: a core may be fragile to intervention and
therefore strongly conserved. Nor does conservation alone establish entrenchment: an
isolated useful block can stay unchanged under selection on its original task.

Leftmost-wins removes automatic aggregation of same-tag runs. It still supplies tag
lookup, isolated stacks, RECV, arithmetic and comparisons. The immediate question is
whether evolution assembles a join from those stable primitives. The later question is
whether the resulting structure itself becomes reusable infrastructure.

## Revision after the thirteenth review (2026-09-29)

Notebook §17–§24, findings items 11, 13–15.
- **XOR/valley thread closed.** A join can be built when none is handed out (leftmost-wins
  15/30 vs 19/30 with the free max, population level). No valley was found on solving or
  non-solving paths: plateaus are left by small edits, mostly via crossover, and
  non-solvers are slow, not stuck. **Step 1 (recovery ruler) is dropped**: it would measure
  reassembly on a plateau, not a valley crossing.
- **"Tagged runs make half-built things neutral" needs a qualifier:** inert at evaluation,
  not neutral under variation. Tagged crossover keeps parent A's leading inert cells and
  truncates, so runs nothing reads are purged within a few generations (with no selection:
  2.9 → 0.2 runs per genome in 100 generations).
- **Before Step 2:** (done, notebook §25)
  1. ~~The item 14 package contrast~~: the stack fails the same way under tournament;
     crossover off, v1 and v2 all fail. Closed.
  2. ~~A crossover variant that loses fewer runs~~: crossover v2 (`fit_runs`) lifts leftmost
     XOR from 38 to 68/100, mechanism open (findings item 16). Step 2 uses v2 by default;
     run the v1c compaction control and a 128-cell drift alongside the pilot.
- **Project boundary (2026-09-29):** one crossover comparison (done), the cheap tournament
  controls (done), one bounded Step 2 experiment, then the map-bias pivot. Entrenchment only
  if Step 2 shows identifiable cross-output dependencies.
- **Step 2 design choices to fix before coding:**
  - Tags 0..13 are the 14 non-constant two-input functions of (p1, p2); tag 0 is the target
    (AND or XOR), so all tag-0 tooling stays valid.
  - A 128-cell tape in *all* arms (14 output runs don't fit in 64).
  - Leftmost-wins, no markers.
  - Pooled lexicase over 14 × 64 output-cases, down-sampled per generation if too slow.
    The target-only arm uses the same machinery with tag-0 cases only.
  - Drop the summed-fitness arm for now: under balanced fitness with exact-match labels,
    all-constant genomes score 0.5 on every output, so it is flat by construction (item
    14). If a scalar arm is wanted, use plain accuracy and call it a different fitness.
  - Per-output population-level exactness (`track_exact_any` keyed by output tag).
  - Reuse measured by knockout (does an output change when another output's run is
    removed), with the Boolean interface tested on all four quadrants.
  - Pitfalls:
    - the crossover run loss;
    - lexicase rewards cheap constants on every output first;
    - OR/NOR pairs are one run plus a negation, not independent problems;
    - under leftmost, a second same-tag run is silent, so reuse must go through RECV.
- **Core map-bias pivot:** write its plan now and run it after Step 2 — a map whose bias
  differs from direct encoding (the folding map or a tree-GP generator). Measure behaviour
  frequency under random genomes vs direct encoding on the same task family, plus one
  evolutionary comparison. Step 3 (entrenchment) only if Step 2 shows any cross-output
  dependency.

## Revision after Step 0 and the tenth review (2026-09-28)

Step 0 ran (notebook §17): no retag-from-silence, and later output runs share ancestry with
the first. The tenth (Fable) review changed the plan:
- **Plain tagged XOR has no valley on the solving path.** Each XOR half is a 0.75 lexicase
  specialist, the halves differ by one SWAP, and the free max join does the rest. Rejoining
  them by crossover was the solving step in 7/8 cases. So Step 1 as first written would
  give a fast recovery that doesn't change with k.
- **The valley programme moves to a chemistry with no free join:** tagged runs with
  leftmost-wins (`tag_combine: leftmost`). There, XOR needs a join built inside one run
  (e.g. `RECV a RECV b GT RECV b RECV a GT ADD`; checked exact, while the two-run max route
  fails).
- **The route-4 null was forced by the setup.** A silent run becomes tag 0 at μ/64 per run
  per generation, far below the rate of retags away from 0. Protection is the wrong knob;
  if route 4 is tested, add a "promote to tag 0 / wire a RECV" mutation instead.
- **Step 3 (duplication) dropped:** crossover already makes the pairs.
- **Step 2 gets a third arm:** target-only with summed fitness instead of lexicase, to
  control for partial credit on the target's own cases.
- The post-mortem matching was fixed: compare ops + RECV tags with padding stripped, and
  record RECV-rewiring events.

**Revised order:**
1. Fix and re-run the post-mortem (done).
2. Overnight (`queue_s18`): leftmost XOR, crossover-off XOR, stack 64-cell XOR controls,
   then parked map-bias items.
3. Inspect every available leftmost solver, whether common or rare. ≥ ~8/30 gives a
   useful collection of paths; ≤ 2/30 establishes difficulty at this budget, not a
   valley. For intermediate counts, use the same lineage inspection before choosing
   the next probe. Build Step 1's recovery ruler if assembly remains the bottleneck.
4. Step 2 on leftmost, three arms (family / target-only lexicase / target-only summed);
   needs a coding session.
5. Step 3: follow evolved joins beyond their first solve, looking for reuse, dependency
   and conservation under ordinary mutation. Start with existing saved lineages.
6. Route 4 with a promote/wire mutation if needed; threshold machinery and structural
   plasticity remain separate, parked comparisons.

**2026-09-28 update:** Steps 1–4 and the budget below now reflect this order. The former
Step 3 duplication sweep was dropped after §17; its slot now holds the machinery
follow-up. No new experiments have been run by this plan revision.

## Step 0 — lineage post-mortem (completed; original design retained)

Completed in notebook §17, including the corrected matching and both-parent trace.
The decisions below record the original design; the revision above governs next steps.

Re-run last night's tagged solvers with a both-parents ancestry trace, then classify
where each output run came from.

- **Code.** Add a both-parents mode to `_trace_lineage` (`evolve.py:88`): walk the full
  ancestor DAG (both parents at every crossover) back N generations before the first
  exact generation (N ≈ 300–500), saving genomes and kinds. Off by default; uses no RNG,
  so re-runs reproduce the originals exactly. The script checks that, per run (final best
  genome must match the original `history.csv`).
- **Runs.** tagged XOR solvers (13, `xor_race` tagged arm), tagged_comb XOR (19),
  tagged_comb AND 1× (12, `knob_comb_and`). ~45 runs × 3000 gens, ~15 min on 10 cores.
- **Classification per output (tag-0) run of the solver:**
  - *built in place*: its cells were assembled under tag 0 on the ancestral line;
  - *merged by crossover*: arrived whole from the other parent;
  - *retagged after silence*: the run existed under a non-zero, unread tag in some
    ancestor and became tag 0 by a header-tag mutation (route 4);
  - for marker runs: whether the second run existed under another tag before the retag
    (the join itself is one cell there, so the retag is the telling event).
- Also record, for merged runs, how the donor's run was built (recurse one level).

**Decision after Step 0**
- Retag-after-silence found in ≥ a few solvers → route 4 already happens; Step 1's retag
  on/off split becomes the main test, and Step 3 moves up.
- Not found (with both parents traced, so the null is not biased) → route 4 stays a
  hypothesis; keep the order below.
- Mostly "built in place" even for the second run → recombination matters less than
  §12 suggested on these tasks; note it before Step 2.

## Step 1 — recovery ruler on leftmost XOR (markers off)

**What would be interesting to see:** how recovery time changes with damage to a built
join, and whether recovery traverses unrewarded intermediates or finds another route.

- **Design.** Use leftmost solvers with an identifiable join, or a hand-written exact
  leftmost solver as an explicitly engineered starting point. Leave the predicate runs
  undamaged at initialization; they still mutate normally during recovery. Replace k
  join-body cells with NOP for k = 1, 2, 3, 4, preserving run boundaries
  and tape length. Use several damage patterns per k and report the initial behaviours;
  k is damage size, not an established minimum valley width. Verify the undamaged
  anchor on all 10,000 inputs and include a k = 0 retention control.
  mbs_xor, tagged, leftmost, tape 64, rate 0.015, lexicase, balanced, fast_rng,
  1000–2000 gens as an initial budget.
- **Arms.** First measure ordinary recovery, provisionally 30 seeds per k spread over
  the available anchors and damage patterns. Add a matched header-retag on/off
  contrast only if traces implicate that route; keep RECV-target mutations enabled.
- **Readout per run.** Generations to exact XOR, and the endpoint class: rebuilt the join,
  found a different route (e.g. single-run XOR), or never exact.
- **New code.**
  - `seed_tapes` currently assumes length-L stack tapes; extend it to TAG genomes (2L).
  - Optional header-retag switch: freeze mutation of SEP cells' tags only, so RECV
    targets still mutate. Separate this intervention from the ordinary recovery arm.
  - A small "damage" script that builds the k-cell NOP-replacement seeds from solvers.
- **Interpretation.** A steep curve motivates local-neighbourhood and path inspection;
  it does not by itself prove a valley. Record per-case errors as well as scalar fitness,
  because lexicase can preserve specialists despite a lower aggregate score. A retag
  effect needs ancestry evidence before attributing it to silent activation. Flat
  curves or alternative-route recovery make this a poor ruler for the intended join;
  they do not rule out valleys elsewhere. Recovery from intact predicates measures
  conditional assembly, not discovery from random genomes.

## Step 2 — generic-reward staircase (useful intermediates)

**What would be interesting to see:** whether rewarding a generic family of simpler
functions lets evolution build a join it can't build when only the target is rewarded —
Avida's EQU result on this system.

- **Design.** Multi-output tagged genomes: each output tag t = 1..14 is one of the 14
  non-constant two-input Boolean functions of p1 = max>5 and p2 = sum>10 (target
  included, as EQU was in Avida). Compare:
  - *family*: all 14 rewarded;
  - *target only*: only the target output rewarded (AND, and separately XOR).
  Chemistry with **no automatic same-tag join**: tagged with leftmost-wins, so max
  isn't handed out (or the stack, if multi-output is easy there). Supplying max would
  confound attribution on the compositions it directly helps.
- **Arms.** For AND and separately XOR: family with pooled-case lexicase, target-only
  lexicase, target-only summed balanced accuracy with the same documented scalar
  selector in both target experiments. Six cells × 30 seeds × 3000 gens provisionally.
  Give each family output equal case weight. Keep training samples, mutation and tape
  budget comparable; record total case evaluations, since family evaluation costs more.
  Any search-efficiency comparison also needs an equal-case-evaluation budget view.
  The target-only summed arm checks the role of specialist-preserving selection; it
  does not isolate a single numerical fitness transformation from the selector.
- **New code.** Multi-output evaluation (the output of tag t for each rewarded t), the
  family task definition, and the fitness combiner. About half a day.
- **Interesting if:** family ≫ target-only on the target's exact solves, with lineages
  showing the target assembled from rewarded sub-functions. **Kill:** no difference →
  intermediates don't help here, or the combiner drowns the target (check the per-output
  solve rates before concluding).

## Step 3 — from an evolved join to entrenched machinery

**What would be interesting to see:** evolution builds a join, other functions begin
using it, and its behaviour becomes conserved while surrounding wiring continues to
change. The core remains exposed to the ordinary mutation operators throughout.

### 3a. Observe reuse before engineering protection

Start by inspecting saved leftmost and family solvers. Follow candidate joins beyond
their first exact solve; extend selected lineages if existing runs stop too early.
A candidate is an evolved run or connected group of runs with a verified combining
function, not necessarily the hand-written join or a fixed token sequence.

For each candidate, record body changes separately from header/RECV rewiring, behaviour
on its interface inputs, and which rewarded outputs functionally depend on it. Count
dependencies by intervention (perturb the candidate and re-evaluate each output), not
just by counting RECV references. Repeated computation, unused reads and bypass paths
can make apparent reuse misleading. Where the interface is Boolean, test all four input
combinations as well as the actual input lists. Stable output on current data alone may
hide a changing internal function.

If no shared combining structure appears, report that observation at the tested budget.
Do not insert a designer join and describe its subsequent preservation as spontaneous
entrenchment. Predicate reuse alone is useful but distinct from reuse of a combiner.

### 3b. Ask whether acquired dependencies preserve the core

At snapshots before and after additional outputs acquire a dependency, measure how the
same available single mutations affect the candidate's behaviour and the dependent
outputs. Record proposed mutations and their survival along lineages, normalized by
mutation opportunity and block size; raw sequence conservation is insufficient.

For a small causal follow-up, fork the same evolved snapshot into paired continuations:

- **Dependants rewarded:** maintain selection on the acquired downstream functions.
- **Dependency selection released:** remove those downstream rewards while keeping
  the original task reward, genome, mutation operators and remaining task weights.

Compare core-behaviour retention, accepted core changes and downstream losses at equal
continuation budgets. Removing rewards changes selection; that is the intended
intervention. A matched removal of rewards for non-dependent outputs, when available,
helps distinguish dependence from simply having fewer objectives. Fix the selector and
reward normalization before running this comparison. It tests maintenance of existing
dependencies, not how the first dependency arose.
Check whether the original task already fully constrains the candidate's behaviour:
if so, additional rewards may add no detectable constraint and a null contrast is
uninformative about dependency-driven conservation.

**Interesting evidence:** acquired functional dependencies, broader damage from core
perturbations, and stronger conservation when those dependants remain rewarded. A
stable core with no acquired dependency is ordinary conservation; shared dependencies
without detectable extra conservation demonstrate reuse but leave entrenchment open.
Mutation intolerance alone is fragility, not evidence that evolution preserved a core.

### 3c. Ask whether stable machinery enables further innovation

Use a separate training curriculum with explicitly held-out combinations, then transfer
the evolved populations to those goals. Step 2 rewards all 14 non-constant Boolean
functions, so its training run cannot supply an unseen two-input Boolean combination
of the same predicates. Specify the held-out goals before this new training run; verify
that both useful subfunctions and unsolved transfer goals exist.

Measure exact transfer success, evaluations to adaptation, retained old functions and
whether adaptation reuses the candidate through rewiring or replaces it. Include a
fixed-goal training control with matched resources. Faster transfer alone does not
attribute the gain to the candidate: use the lineage and dependency interventions.

Distinguish four possible observations: conservation with useful transfer; conservation
with poor transfer (entrenchment may constrain innovation); transfer through replacement
of the core; and neither. The earlier varying-goal null (§16) remains relevant; benefits
from this new curriculum are a hypothesis, not an assumed consequence of modular goals.

**Practical order.** Do 3a first. Pilot 3b on several independently evolved candidates
before sizing a sweep. Attempt 3c only when there is identifiable machinery to follow.
Optional later controls may freeze or lower mutation on the *same evolved* candidates,
but label these imposed-protection arms. No bonuses for reuse, stability, dependency
count or modularity in the main arms: those are observations, not rewarded objectives.

## Step 4 — silence, then activation (conditional)

If the silent route remains interesting after Steps 1–3, test a promote-to-output or
wire-a-RECV mutation against the ordinary mutation operator. Keep the total mutation
budget comparable and trace whether useful material actually developed while silent.
Separate increased activation opportunity from survival of the silent material.
Lowering mutation on silent runs is a later engineered-protection control, not the
first intervention and not evidence for naturally arising entrenchment.

## Step 5 — structural lifetime learning

A few "wildcard" cells whose op or RECV target the individual picks during evaluation by
trying the options on its training lists (Hinton & Nowlan style, discrete switches).
Lifetime trials **must be charged against the evaluation budget**, otherwise it is brute
force hidden inside each individual. Compare against the Step 1 ruler at equal total
evaluations. The most code of all steps; only after 1–2 have results.

## Separate comparison — supplied threshold machinery (parked)

**What would be interesting to see:** whether a fixed, generic summation/threshold
interface makes several combinations accessible and robust through small wiring or
threshold changes. This changes the supplied machinery; it is a separate question from
building a join in leftmost-wins or observing entrenchment.

For Boolean p1 and p2, `p1 p2 ADD CONST_0 GT` is OR and replacing CONST_0 with CONST_1
gives AND. That single-edit relationship concerns completed programs; it does not
establish an easy path to building either, or a valley-free biological transition.

Before implementing this arm, specify where thresholds live, how multiple same-tag
runs interact, and whether inputs are Boolean or arbitrary integers. **Positive-only
sum/threshold networks cannot express XOR at any feed-forward depth.** An XOR-capable
version needs inhibition, negation, signed weights or existing non-monotonic operations
such as GT. If stack runs retain GT, trace where it supplies that capability rather than
attributing success to an extra threshold layer alone. Verify expressibility with a
hand-built witness before an evolutionary sweep.

Measure the fraction of mutations that preserve the whole task and the candidate join's
interface behaviour separately, alongside access to other useful functions. Report
whole-genome mutation outcomes under the actual operator, then break them down by body,
wiring and threshold mutations. Account for inactive cells, block size and mutation
opportunity. A fixed interpreter join cannot be broken by genome mutations; treating
that immunity as evolved robustness would make the comparison circular.

## Parked (map-bias shortlist from the ninth review, and the min-default idea)

Not on the valley path, but cheap and ready (existing knobs, no new code), if a night
has spare budget:
- XOR attribution controls: stack tape 64 (rates 0.015, 0.03), v2_imax tape 64, tagged
  leftmost-wins, tagged crossover off (~1.5 h). Needed before findings item 13 stops
  being provisional.
- Crossed min/gate weights on tagged_comb AND (`22:4,24:0.25` vs `22:0.25,24:4`, 50 seeds).
- True rarity: all markers at 0.02× and 0.05×.
- IMAX 0.05× / 0.25× / 1× at 3000 gens, read as time to first solve.
- Min-default join (`combine: "min"`, a few lines in `tagged.genome_outputs`) on AND and OR.
  Predicted ~11/30 each from §16's marker data, plus an offline count of crossover children
  broken under min vs max (the junk-run fragility explanation of the AND/OR gap).

## Order and budget (current roadmap)

| step | what | new code | compute |
|---|---|---|---|
| 0 | post-mortem, both parents | completed, notebook §17 | done |
| next | queue_s18 attribution controls, then inspect solvers | existing queue + lineage analysis | existing estimate ~1.5 h for XOR controls |
| 1 | leftmost recovery ruler | TAG seeding, damage script; optional retag switch | re-estimate after anchor/damage pilot |
| 2 | useful intermediates, six cells | multi-output evaluation + selectors | profile case cost; about ½ day initial coding estimate |
| 3a | observe join reuse and conservation | behavioural/dependency tracing | saved-artifact inspection first |
| 3b–c | dependency release, then held-out transfer | paired continuation + curriculum | size after pilot; no overnight estimate yet |
| 4 | silent activation opportunity | promote/wire mutation | conditional, profile first |
| 5 | structural plasticity | wildcard cells + charged budget | later |
| separate | supplied threshold machinery | threshold semantics + expressibility check | parked |

Keep the current queue unchanged. The first new action is to inspect its available
solvers; the first machinery action is 3a, which may reuse those artifacts. Follow-ups
need their own short notebook setup and concrete runtime estimate before execution.

## Biological inspiration and checked reading

The useful analogy is conserved processes recruited through changing regulatory
connections. Conservation does not imply an experimentally lowered mutation rate, and
does not by itself establish that acquired dependencies caused it. The staged questions
above distinguish these possibilities in this system; they do not test the whole
biological theory.

- [Gerhart & Kirschner (2007), *The theory of facilitated variation*](https://pubmed.ncbi.nlm.nih.gov/17494755/).
  Conserved core processes and weak regulatory linkage motivate the stable-interface
  question. Read as a biological framework, not evidence that arbitrary evolved code
  will acquire those properties.
- [Buchler, Gerland & Hwa (2003), *On schemes of combinatorial transcription logic*](https://garcialab.berkeley.edu/courses/papers/Buchler2003a.pdf).
  Promoters are richer than simple perceptrons; their model includes a single-promoter
  XOR construction. Do not claim that biological XOR necessarily requires another
  regulatory layer or is rarer on that basis. The project's 0.72 is the best tested
  `sum + w·max` rule on its input distribution, not a universal XOR linear ceiling.
- [Parter, Kashtan & Alon (2008), *Facilitated Variation: How Evolution Learns from Past Environments To Generalize to New Environments*](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000206).
  Computational precedent for modularly varying goals and transfer to unseen goals;
  motivates 3c without overriding this project's existing varying-goal null.

Generative entrenchment is the conceptual lead for Step 3. Obtain and read a primary
Wimsatt source before attributing the operational test here to his precise formulation;
that reference was mentioned from memory in the discussion, not checked in this update.
