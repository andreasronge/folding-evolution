# Map-bias — findings

Short, scoped summary of the map-bias line (notebook: [notebook.md](notebook.md) §1–§23;
§1–§14 results commit `e05aa5f`, §15–§16 commit `7c9cc42`, §17 `e3e3ff1`, §18–§19 `c922028`, §21–§22 `5a85eb5`).
Checked by an eighth Fable review; §16 changes by a ninth, §17 by a tenth, §19 by an eleventh.

**Question.** How does a developmental genotype→program map bias what evolution finds —
and can evolution combine building blocks by recombination without crashing?

**Scope of everything below.** Chem-tape programs on length-4 integer lists over [0, 9];
tasks built from two predicates (`max>5`, `sum>10`); pop 1024, 1500–3000 generations,
30 seeds per arm unless noted. "Exact" = right on all 10,000 possible lists. Baseline
(stack chemistry) vs tagged runs is a chemistry-*package* comparison: tape length,
indels and crossover operator differ. §15–§16 arms use `fast_rng` (a different random stream
from §1–§14) and `op_weights`, which renormalises op draw probabilities, so raising one op's
weight lowers every other op's share (markers are 35% of draws at 4× on all three; MIN 42% at 16×).
All §15–§19 arms use lexicase selection with balanced fitness. **Leftmost-wins**
(`tag_combine: leftmost`) means only the first run of each tag is read, for the output and
for RECV alike, so there is no automatic join of same-tag runs. Item 2's valley was found
under tournament selection; items 13–14 are lexicase results, so the two are not in tension.
**"Exact" counts the recorded champion only.** When several individuals fit all training
cases, the champion is one of them, arbitrarily; saved populations show many more exact
individuals behind training ties (§22). All XOR counts below are lower bounds.

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
    chemistry (§3, §9, §12). This also holds with both parents traced on 44 tagged solvers
    (§17) and on 12 leftmost solvers (§19). A silent run becomes tag 0 at a rate of μ/64 per
    run per generation, and silent runs are unprotected, so the route was barely available:
    untested rather than refuted.
12. **Frequency knob — the first direct manipulation of map bias.** Weighting an op in
    random genomes and point mutations changes how often it is made, not what is reachable.
    - **Rarity switches routes rather than delaying one.** Stack OR with IMAX at 0.05× /
      0.25× / 1× of uniform, 3000 generations: 21 / 15 / 21 exact, median first exact
      1243 / 1262 / 568. But at 0.05×, 18 of 21 solvers contain no IMAX at all (0.25×: 5 of
      15; 1×: 6 of 21), so the population solves OR by the join-free route, at that route's
      speed. Under a 1500-generation budget this looks like fewer solves (0.25× / 1× / 4×:
      9 / 19 / 17). The two rare arms are not distinguishable at n = 30; the effect
      saturates above uniform.
    - **Among equivalent joins, frequency picks the one used.** On AND with combine markers,
      min 4× / gate 0.25× gave 13 min-joined and 1 gate-joined solvers; the reverse weights
      gave 2 min and 14 gate (50 seeds each, p = 2×10⁻⁵). Solve counts were the same
      (15 vs 16 of 50).
    - **Adopting the joined route doesn't depend on frequency**, even at true rarity: with
      all markers at 0.02× (≈ 0.27% of draws), 9/10 solvers are joined runs, and solves are
      unchanged (10/30).
    - **Very high weights hurt through dilution** of the rest of the alphabet (MIN 16×:
      2/30 vs 10/30; 4× on all three markers: 6/30 vs 12/30).

    (§16, §19)
13. **XOR: no detectable difference between tagged runs and the stack once the stack has
    room; crossover is essential for tagged runs at this mutation rate.** On XOR (no
    near-linear shortcut; best `sum + w·max` rule 0.72), a 64-cell stack reaches 11–12/30,
    the tagged level (13/30). The earlier gap (5/30 and 2/30 at 32 cells) was tape length,
    and the result doesn't depend on the stack's rate (0.015 or 0.03); tagged_comb's 19/30
    vs 12/30 is p = 0.12. This is still a package comparison: the stack has single-point
    splice crossover, no indels and bond protection, while tagged runs have run-level
    crossover and indels. Tagged XOR falls from 13 to 2/30 without crossover (p = 0.002); no
    stack crossover-off arm was run on XOR at first; later the stack without crossover
    reached 7/30 (vs 12/30 with it, p = 0.27), so crossover matters less for the stack.
    (§16, §19, §22)
14. **A join can be built when none is handed out.** With leftmost-wins, tagged runs still
    solve XOR 12/30 (vs 13/30 with the free max).
    - **8/12 solve inside a single run** with no live RECV. In 7 of them the exact-making
      step is a 1–2 cell change of a body that was already near-XOR, or of an exact
      three-quadrant specialist (OR, NAND or one XOR half) that had sat at 0.75 for 250–1700
      generations. In seed 8, a crossover brought a sibling's other XOR half in as a second
      (inert) tag-0 run, and a SEP deletion in the same generation fused the two runs in
      front of a trailing `ADD` that had been neutral: a join by run fusion.
    - **4/12 have the output run read one helper by RECV.** Each helper descends from a
      tag-0 run. In 3/4 it descends from the *same* ancestral output run as the solver's own
      output run: sibling copies that diverged in different individuals and were reunited by
      crossover, as in §17, but wired by retag + RECV instead of the free max.
      - The retag 0→t happened in a crossover child in all 4. A reader existed at once in
        2/4 and within 25 generations in the rest, so no helper went unread for more than
        14 generations.
      - Only 1/4 helpers already computed, when retagged, what the solver uses it for (an
        exact XOR half). In the other three the body was rewritten or drifted after being
        wired in. So the retag mostly supplied a wired slot, not a finished part.
    - **Pooled over 100 seeds** (§22), 31 solvers: 26 single-run, 5 with a helper wired
      from a former output run. Co-option is the minority route (≈ 16%).
    - **These solving paths show plateaus, not valleys.** Partial solutions stayed selected
      under lexicase (three-quadrant specialists at 0.75, some hosts down to 0.5). Only
      solvers were inspected; the 18 non-solvers weren't. Whether a valley exists on XOR
      that lexicase can't cross is untested.
    - **Crossover matters for building the join:** leftmost XOR without crossover 4/30 vs
      12/30 (p = 0.04). Unsolved populations (with or without crossover) always hold
      complementary quadrant covers.

    (§17, §19, §22)
15. **Under summed fitness XOR is flat, not a valley; lexicase is what makes it solvable.**
    With tournament selection on balanced fitness, XOR is 0/30 with or without the free
    max join (vs 12–13/30 under lexicase). Champions end at 0.5, the constant-output level.
    - This follows from XOR's parity: a single predicate scores exactly 0.5 on XOR, so the
      building blocks carry no aggregate fitness signal.
    - Lexicase rewards them case by case.
    - Items 13–14 are therefore lexicase results. (§22)
16. **Slow, not stuck; many "failures" are training-set ties.**
    - Leftmost XOR run to 10,000 generations (first 3000 replay exactly) goes from 12 to
      17/30 exact champions. All 5 late solvers are runs whose generation-3000 champion
      had no fitter or dominating single or sampled double neighbour (§20).
    - Counting populations instead of champions: 21/30 hold an exact individual. The 4
      extra are runs whose training-perfect champion isn't exact while up to 470 population
      members are.
    - 64 training cases don't pin XOR down. With 256 cases, exact champions rise only
      slightly (max join 13 → 17/30, leftmost 12 → 14/30, not significant), and training-
      perfect but non-exact champions still occur. The undercount comes from arbitrary
      tie-breaking among training-perfect individuals. (§20, §22, §23)

## Open

- **Plateaus on XOR.** Champions have no fitter or dominating neighbour (§20) but many
  neutral and case-trading ones, and they escape later (§22). Is the escape neutral drift
  or crossover? Answering it needs population snapshots over time, not only final
  populations.
- **Stable machinery.** On fixed-goal solved runs, elitism freezes the champion: in all 4
  co-option runs the helper stayed unchanged, with one reader, to generation 3000. Reuse
  and entrenchment need a multi-output task (Plans/valley-crossing.md, Step 2 before
  Step 3).
- **The core map-bias question** needs a map whose bias differs from direct encoding (the
  folding map or a tree-GP generator); chem-tape's decoder is close to identity (item 1).
- The leftmost result reinforces items 8–9: when no join is handed out, evolution builds it
  by 1–2 cell edits, run fusion or retag + RECV, and crossover reuniting sibling copies is
  still the common solving step.
