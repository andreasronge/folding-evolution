# Map-bias — findings

Short, scoped summary of the map-bias line (notebook: [notebook.md](notebook.md) §1–§14;
branch `map-bias`, final results commit `e05aa5f`). Checked by an eighth Fable review.

**Question.** How does a developmental genotype→program map bias what evolution finds —
and can evolution combine building blocks by recombination without crashing?

**Scope of everything below.** Chem-tape programs on length-4 integer lists over [0, 9];
tasks built from two predicates (`max>5`, `sum>10`); pop 1024, 1500–3000 generations,
30 seeds per arm unless noted. "Exact" = right on all 10,000 possible lists. Baseline
(stack chemistry) vs tagged runs is a chemistry-*package* comparison: tape length,
indels and crossover operator differ.

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
   or v3's isolated domains (2/30) left AND unsolved, like the baseline (1/30). (§3)
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
   max fall to 11/30. Gene duplication was the merge route in 1/25 solvers, and its extra
   solves (25/30 vs 19/30) are not significant (p = 0.14). (§12, §14)
9. **With heritable joins, evolution adopts the modular route every time — but no more
   often succeeds.** With combine markers, 9/9 exact AND solvers are two runs joined by
   `min` or `gate` (vs 1/9 and 3/9 without), found sooner (median first exact generation
   640 vs 1000–1580); AND is 9/30 in all four arms. (§14)
10. **Varying goals: suggestive benefit for the stack baseline; tagged runs track worse.**
    Switching max>5 → sum>10 → AND every 5–20 generations, the baseline reached exact AND
    in 18/30 runs at some phase end (fixed goal: 9/30, checked every 10 generations, so that
    comparison is conservative); the late-phase comparison (11–14/30 vs 9/30 at the end)
    has more looks and is not corrected for it. Tagged runs track switches worse at every
    period, also with effective mutation rate matched — a property of the chemistry package.
    (§12, §14)
11. **Negative: the silent-then-switch (pseudogene) route was never observed** in any
    chemistry. (§3, §9, §12)

## Open

Evolving a join that must be *built* across a fitness valley (§9), rather than chosen from
a menu of combine markers, is a separate project.
