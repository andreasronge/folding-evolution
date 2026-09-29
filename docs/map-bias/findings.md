# Map-bias — findings

Short, scoped summary of the map-bias line (notebook: [notebook.md](notebook.md) §1–§23;
§1–§14 results commit `e05aa5f`, §15–§16 `7c9cc42`, §17 `e3e3ff1`, §18–§19 `c922028`,
§21–§22 `5a85eb5`, §23 `fab1d10`). Checked by an eighth Fable review; §16 changes by a
ninth, §17 by a tenth, §19 by an eleventh, §20–§23 by a twelfth.

**Question.** How does a developmental genotype→program map bias what evolution finds —
and can evolution combine building blocks by recombination without crashing?

**Setup.**
- Chem-tape programs on length-4 integer lists over [0, 9], with tasks built from two
  predicates (`max>5`, `sum>10`).
- Population 1024, 1500–3000 generations (one sweep to 10,000), 30 seeds per arm unless
  noted.
- Stack (baseline) vs tagged runs is a chemistry-*package* comparison: tape length, indels
  and crossover operator differ.
- §15 onwards arms use `fast_rng` (a different random stream from §1–§14) and lexicase
  selection with balanced fitness, unless noted.
- `op_weights` renormalises op draw probabilities, so raising one op's weight lowers every
  other op's share (markers are 35% of draws at 4× on all three; MIN 42% at 16×).
- **Leftmost-wins** (`tag_combine: leftmost`) means only the first run of each tag is read,
  for the output and for RECV alike, so there is no automatic join of same-tag runs.
- Item 2's valley was found under tournament selection; items 13–14 are lexicase results.

**Measurement.** "Exact" = right on all 10,000 possible lists, judged on the **recorded
champion**.
- That champion is locked in: it is the first individual to fit all training cases.
  Elitism keeps it at the front of the population and the argmax that picks the champion
  returns the first maximum, so it is never displaced (0 champion changes after first
  reaching training 1.0 in 26/29 long runs).
- A run whose first training-perfect individual isn't exact can therefore never count as
  solved, however many exact individuals arise later.
- Holdout doesn't break the tie: 10 of 21 locked champions also score 1.0 on 256 holdout
  cases. Only evaluating training-perfect individuals on all lists does.
- **All champion-based XOR counts are lower bounds, and how much they can miss differs by
  arm.** Runs locked on a non-exact champion: tagged max 9/30, stack + IMAX 9/30, stack 64
  cells 4–5/30, leftmost 3/30, crossover-off arms 1–2/30. (§22, twelfth review)

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
    chemistry (§3, §9, §12), including with both parents traced on 44 tagged solvers (§17)
    and on 31 leftmost solvers (§19, §22). A silent run becomes tag 0 at μ/64 per run per
    generation and silent runs are unprotected, so the route was barely available:
    untested rather than refuted.
12. **Frequency knob — the first direct manipulation of map bias.** Weighting an op in
    random genomes and mutations changes how often it is made, not what is reachable.
    - **Rarity switches routes.** With IMAX at 0.05× on stack OR, 18 of 21 solvers use no
      IMAX: the join-free route, at its own speed.
    - **Frequency picks among equivalent joins.** Crossed min/gate weights on AND: 13:1 vs
      2:14 (p = 2×10⁻⁵), with equal solve counts.
    - **Adopting the joined route doesn't depend on frequency**, even with markers at
      0.27% of draws (9/10 solvers joined).
    - **Very high weights hurt only through dilution** of the rest of the alphabet.

    (§16, §19)
13. **XOR: no detectable difference between tagged runs and the stack at the champion
    level, once the stack has room.** A 64-cell stack reaches 11–12/30, the tagged level
    (13/30). The earlier gap (5/30 and 2/30 at 32 cells) was tape length.
    - The two arms can miss different numbers of solves (tagged max: 9 locked runs; stack
      64: 4–5), so the population-level comparison is open.
    - Still a package comparison.

    (§16, §19)
14. **A join can be built when none is handed out.** With leftmost-wins, tagged XOR
    solves 12/30 (vs 13/30 with the free max). No significant cost at n = 30, but every
    measure that can see hidden solvers favours the free max (256 cases: populations with
    an exact individual 20 vs 14, p = 0.19).
    - **How:** pooled over 100 seeds, 31 solvers.
      - 26 solve inside a single run: 1–2 cell edits of a near-XOR body or of a 0.75
        specialist, and once by run fusion.
      - 5 wire a helper by RECV. The helper is a former output run, and in 3/4 a sibling
        copy reunited by crossover.
      - The 4/12 vs 1/19 helper rate across batches is p = 0.06. (§19, §22)
    - **Crossover off** (all vs 12–13/30 with crossover): tagged max 2/30, leftmost 4/30
      (p = 0.04; no hidden solvers, so larger at population level), stack 64 cells 7/30
      (8 populations). Every arm drops; the drops can't be told apart at n = 30.
    - When no join is handed out, evolution builds it by small edits, run fusion or retag +
      RECV, and crossover reuniting sibling copies is still the common solving step (as in
      items 8–9).
15. **Under summed fitness the XOR building blocks carry no signal.** On the stratified
    sample, any single predicate and any constant score exactly 0.5 balanced; anything
    above 0.5 needs at least two comparisons combined.
    - Tournament on balanced fitness: 0/30 with or without the free max (vs 12–13/30 under
      lexicase). In 52/60 runs no individual ever exceeded 0.5, and populations collapse to
      constant 0, the most frequent phenotype (item 1).
    - Parity explains *where* the tournament plateau sits (0.5 vs 0.75). It is not yet
      shown to be *why* tournament fails: tournament hasn't been run in the tagged package
      on a task whose blocks carry signal (OR, AND), and stack AND under tournament also
      failed (§3). (§22)
16. **Slow, not stuck; and the champion metric hides solves.**
    - Leftmost XOR run to 10,000 generations (the first 3000 replay §19 exactly) goes from
      12 to 17/30 exact champions, and 21/30 populations hold an exact individual.
    - Locked non-exact champions hide the rest: seeds 20, 26 and 15 locked in at
      generations 778, 2864 and 1333, and hold 470, 439 and 358 exact members at 10,000.
    - Of the 6 training-perfect non-exact champions at 10,000, 4 hide exact individuals;
      only 2 (seeds 9, 25) are a genuine training-set limitation.
    - With 256 training cases, lock-in falls from 12/60 to 6/60 runs in the two tagged arms
      but doesn't disappear.
    - The §20 neighbourhood scan doesn't predict which runs solve later (0/18 had an
      improving neighbour; 5 later solved). Under lexicase the champion is the wrong object
      to scan; the selected parents are.
    - In unsolved lexicase populations, a three-quadrant specialist is present in ~80%
      (vs 1/30 under tournament) and a complementary pair of specialists in roughly a
      third to a half. (The earlier "complementary quadrant covers always present" was too
      weak: constant 0 plus constant 1 satisfies it.)

    (§20, §22, §23)

## Open

- **Population-level counts.** Evaluate training-perfect individuals on all lists each
  generation, then replay the §16/§19 XOR arms (runs replay exactly) to get
  population-level counts. Items 13–14's comparisons depend on it.
- **Tournament on OR/AND in the tagged package**, to test item 15's attribution.
- **How plateaus are left:** a parent-level trace of the 5 late solvers (crossover child
  or mutant, and were the parents training-perfect?).
- **Stable machinery.** On fixed-goal solved runs, elitism freezes the champion (in all 4
  co-option runs the helper stayed unchanged, with one reader, to generation 3000). Reuse
  and entrenchment need a multi-output task (Plans/valley-crossing.md, Step 2 before
  Step 3).
- **The core map-bias question** needs a map whose bias differs from direct encoding (the
  folding map or a tree-GP generator); chem-tape's decoder is close to identity (item 1).
