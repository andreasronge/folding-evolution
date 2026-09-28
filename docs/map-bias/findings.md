# Map-bias — findings

Short, scoped summary of the map-bias line (notebook: [notebook.md](notebook.md) §1–§16;
§1–§14 results commit `e05aa5f`, §15–§16 commit `7c9cc42`). Checked by an eighth Fable review;
§16 changes by a ninth.

**Question.** How does a developmental genotype→program map bias what evolution finds —
and can evolution combine building blocks by recombination without crashing?

**Scope of everything below.** Chem-tape programs on length-4 integer lists over [0, 9];
tasks built from two predicates (`max>5`, `sum>10`); pop 1024, 1500–3000 generations,
30 seeds per arm unless noted. "Exact" = right on all 10,000 possible lists. Baseline
(stack chemistry) vs tagged runs is a chemistry-*package* comparison: tape length,
indels and crossover operator differ. §15–§16 arms use `fast_rng` (a different random stream
from §1–§14) and `op_weights`, which renormalises op draw probabilities, so raising one op's
weight lowers every other op's share (markers are 35% of draws at 4× on all three; MIN 42% at 16×).

## Findings

1. **Map bias predicts easy tasks, not hard ones.** Random-tape behaviour frequency
   predicts which tasks are easy; on this alphabet the chem decoder and direct encoding have
   near-identical bias (a near-identity map). Evolution routinely finds behaviours rarer
   than 1 in 50M random tapes. (§1)
2. **The AND "proxy basin" is a wide valley.** No fitter neighbour within two point
   mutations of any of 40 stuck genomes (8.7M neighbours; BP_TOPK, tournament). One
   hand-traced build order needs six unrewarded steps. (§2)
3. **Exactness on all inputs is the only meaningful solve criterion here.** The AND task has
   an arithmetic shortcut (best linear rule: 0.966 balanced accuracy); 8 of 14 lexicase
   "solvers" only fit their 64 training cases. Every two-predicate composition on this
   input domain is at least 0.92 linear. (§3, §5)
4. **A primitive or a safe container alone does nothing.** Adding a MIN primitive (1/30)
   or v3's isolated domains (2/30) left AND unsolved under tournament, like the baseline
   (1/30) (§3). Under lexicase on stratified inputs MIN still adds nothing: 10/30 vs 9/30
   and 30/100 without it. (§16)
5. **Lexicase fixes block supply; arrangement is then the bottleneck** (suggestive, small
   n). Lexicase raised AND from 1/30 to 14/30 on 64 training cases, but only 6 of those 14
   were exact on all inputs. In 4 of the 5 exact solvers that ever held both blocks in one
   genome, the solve came 137–700 generations later. (§3, §5, §7)
6. **In a stack chemistry, blocks compete for the tape end;** v3's linker chains smear a
   predicate across domains. In a guaranteed-supply merge test (25 × 25 exact donors, all
   pairs), 0 children kept both blocks under either chemistry. (§7)
7. **Tagged runs make safe transplants possible without imposing a shape.** Runs connect by
   tag, not position; each evolved predicate lived in a single run (the output run itself),
   and 100% of 940 non-output transplants were inert (0 crashes). Closure was only tested
   on single-predicate donors. (§9)
8. **On OR, crossover merges blocks — but the advantage is the join's cost, not
   modularity.** Crossover is causal for tagged runs (2/30 with it off vs 19/30). A stack
   baseline given a one-op join (integer MAX) reaches 18/30; tagged runs without their free
   max fall to 11/30. Gene duplication does not help: it was the merge route in 1/25 solvers,
   and at 100 seeds OR is 62/100 with it vs 67/100 without (p = 0.55); §12's 25/30 vs 19/30
   was noise. (§12, §14, §16)
9. **With heritable joins, evolution adopts the modular route every time — but no more
   often succeeds.** With combine markers, 9/9 exact AND solvers are two runs joined by
   `min` or `gate` (vs 1/9 and 3/9 without), found sooner (median first exact generation
   640 vs 1000–1580); AND is 9–12/30 in all arms. The joined route persists at 0.25× marker
   weight (≈ 2 marker cells per genome; 10/10 solvers joined), so at that level marker rarity
   does not deter it. (§14, §16)
10. **Varying goals: no benefit for the stack baseline at 100 seeds; tagged runs track worse.**
    Switching max>5 → sum>10 → AND every 20 generations, the baseline reached exact AND at
    some phase end in 36/100 runs vs 30/100 with a fixed goal (p = 0.45); at a late-third
    phase end in 21/100. The 30-seed 18/30 vs 9/30 (§12) did not replicate. Tagged runs track
    switches worse at every period, also with effective mutation rate matched — a property
    of the chemistry package. (§12, §14, §16)
11. **Negative: the silent-then-switch (pseudogene) route was never observed** in any
    chemistry. (§3, §9, §12)
12. **Frequency knob — the first direct manipulation of map bias: op frequency acts as a
    supply rate on the join.** Weighting a needed op in random genomes and point mutations
    changes how often it is made, not what is reachable. Stack OR with IMAX at 0.25× / 1× /
    4× of uniform (≈ 1 / 4 / 15% of draws): median first exact generation 857 / 466 / 370,
    exact by generation 1500 9 / 19 / 17. The effect saturates above the default; very high
    weights hurt through dilution of the rest of the alphabet (MIN 16×: 2/30 vs 10/30; 4× on
    all three markers: 6/30 vs 12/30). Among equivalent joins for AND (min vs gate), the
    more frequent one's share is ordered as frequency predicts (18 / 50 / 62% gate) but is
    not established at 30 seeds. (§16)
13. **XOR (provisional; controls pending).** On XOR, where no near-linear shortcut exists
    (best `sum + w·max` rule: 0.72), tagged runs reach 13/30 and tagged_comb 19/30, vs 5/30
    for the stack and 2/30 for stack + IMAX (tagged_comb vs stack p = 0.0005). Two
    confounds are untested: every stack solver uses ≥ 28 of its 32 cells (a 64-cell tape
    lifted stack OR from 10 to 15/30 in §14), and 8/13 tagged solvers are two near-identical
    output runs differing by a SWAP, joined by the chemistry's free max (the outer OR of
    XOR = max(p1>p2, p2>p1)); the second run arrived by crossover in 8/8. Until a 64-cell
    stack and a leftmost-wins tagged arm run on XOR, this is a chemistry-package result, not
    a modularity result. (§16)

## Open

Evolving a join that must be *built* across a fitness valley (§9), rather than chosen from
a menu of combine markers, is a separate project.

Whether marker frequency steers route choice among equivalent joins (crossed min/gate
weights), and whether route adoption survives true rarity (< 0.1% of draws), are each one
sweep away (notebook §16, next). The core map-bias question needs a map whose bias differs
from direct encoding (the folding map or a tree-GP generator); chem-tape's decoder is close
to identity (item 1).
