# Map-bias — findings

Short, scoped summary of the map-bias line (notebook: [notebook.md](notebook.md) §1–§26;
§1–§14 results commit `e05aa5f`, §15–§16 `7c9cc42`, §17 `e3e3ff1`, §18–§19 `c922028`,
§21–§22 `5a85eb5`, §23 `fab1d10`, §24 `02b2606`–`1b6778b`: or_tournament, xor_leftmost_pop and
xor_race_pop ran under the first version of the exactness check, the other replays under
the two faster versions; first-exact generation and final count are the same under all
three; §25 `85e3da1`, §26 `08b315e`). Checked by an eighth Fable review; §16 changes by a ninth, §17 by a
tenth, §19 by an eleventh, §20–§23 by a twelfth, §24 by a thirteenth, §25 by a fourteenth, §26 by a fifteenth.

**Question.** How does a developmental genotype→program map bias what evolution finds —
and can evolution combine building blocks by recombination without crashing? Items 1 and
12 are about map bias; items 13–15 are chem-tape *design* results (joins, crossover,
selection) from the valley-crossing follow-up (Plans/valley-crossing.md).

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
- Item 2's valley was found under tournament selection; item 13 is a lexicase result.
- **Tagged crossover loses runs.** The child keeps parent A's leading inert cells in full,
  then is truncated to the tape length: overflow drops runs, underflow adds none, and a
  run-free parent A gives a run-free child. With no selection at all, mutation + crossover
  (0.7) takes a random population from 2.9 to 0.2 runs per genome within 100 generations.
  Under lexicase the output run is protected (final populations hold 1.1–1.3 runs per
  genome), but runs nothing reads are purged continuously. This scopes items 7, 10, 11,
  13 and 14. Crossover-off tagged arms keep ~3 runs per genome, so they differ from the
  crossover-on arms in population structure as well as in recombination. (thirteenth review)
- **Crossover v2** (`tagged_crossover: v2`, §25) reassembles the child only on overflow:
  bodies lose trailing NOPs, whole runs are deleted at random (the output run included),
  then the leader is trimmed. With no selection it keeps 0.88 runs per genome at generation
  300 (v1 0.19, crossover off 2.63): less loss, not none. It also shortens executed bodies
  and the leader, so v1-vs-v2 differences are not attributable to run loss alone.
  (fourteenth review)

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
- Locked non-exact champions hide solves. In leftmost XOR run to 10,000 generations,
  seeds 20, 26 and 15 locked in at generations 778, 2864 and 1333 and hold 470, 439 and 358
  exact members at 10,000. Of the 6 training-perfect non-exact champions there, 4 hide exact
  individuals and only 2 (seeds 9, 25) are a genuine training-set limitation. With 256
  training cases, lock-in falls from 12/60 to 6/60 runs in the two tagged arms but doesn't
  disappear.
- **Population-level exactness** (`track_exact_any`, §24) counts a run as solved if any
  individual is ever exact. The XOR arms of §16/§19/§22 were replayed with it. The replay
  guarantees the evolution is identical (330/330 runs end on the original champion); the
  counts rest on the check itself being sound (reviewed: its caches and filters can't hide
  an exact individual). Item 13 uses those counts. Champion counts are lower bounds, by
  0–6 runs per arm. (§22, §23, §24)

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
    generation, silent runs are unprotected, and crossover actively removes runs nothing
    reads (Setup), so under crossover v1 a silent run survives only a handful of
    generations. The route was barely available: untested rather than refuted. Under the
    compaction-only crossover (v1c, item 16) 58% of genomes in solved populations carry a
    silent second output run, so the route is now available for a test. (§26)
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
13. **XOR: a join can be built when none is handed out; tagged runs and a 64-cell stack
    are not detectably different.** Population-level counts (§24).
    - **Package comparison:** tagged max 19/30, tagged_comb 22/30, stack 64 cells 14–15/30
      (p = 0.43 and 0.11). The earlier stack deficit was mostly tape length: 32 → 64 cells
      lifts the stack from 6 to 15/30 (p = 0.03).
    - **Join not handed out:** with leftmost-wins, 15/30 vs 19/30 with the free max
      (p = 0.43; at 256 training cases 14 vs 20). No significant cost at n = 30, but every
      measure favours the free max.
    - **How the join is built** (pooled over 100 seeds, 31 solvers): 26 solve inside a
      single run (1–2 cell edits of a near-XOR body or of a 0.75 specialist, once by run
      fusion); 5 wire a helper by RECV, a former output run, in 3/4 a sibling copy reunited
      by crossover (4/12 vs 1/19 across batches, p = 0.06). Keeping unread runs does not
      raise helper use: crossovers v2 and v1c keep 2–6× more of them, and helpers stay at
      9–18% of exact individuals (item 16).
    - **Crossover off:** tagged max 19 → 2/30 (p < 0.0001), leftmost 15 → 4/30
      (p = 0.005), stack 64 cells 15 → 9/30 (p = 0.19). Crossover matters most for tagged
      runs.
    - When no join is handed out, evolution builds it by small edits, run fusion or retag +
      RECV, and crossover reuniting sibling copies is still the common solving step (as in
      items 8–9). No valley was found on solving or non-solving paths. (§16, §19, §22, §24)
14. **Tournament on balanced fitness fails in both packages, regardless of crossover; the
    landscape is flat from constants.**
    - Under tournament, tagged XOR is 0/30 with either join, and tagged OR 0/30 (leftmost)
      and 2/30 (max), although a single predicate scores 0.83 on OR (population level).
      Under lexicase: 12–13/30 (XOR) and 11–19/30 (OR, champion level).
    - In 26/30 OR runs the best individual never left balanced 0.5 in 1500 generations. In
      the 4 that did, the first step was small (0.53, at generations 88–1384), and
      tournament then climbed to ≥ 0.83 within 65–225 generations, reaching exact OR in 2
      (max join). So amplification works; the wait is for the first output run that gives
      0/1 answers correlated with the input.
    - Why the wait is long: 96% of random tagged genomes have no tag-0 run (output 0,
      balanced 0.5). Those with one mostly output 0, or a non-{0,1} integer that scores 0.0
      under exact-match labels. None of 20,000 scores above 0.5.
    - Crossover run loss is not the cause: stuck v1 populations are 54% NOP (Setup), but
      crossover-off and v2 arms also stay at 0.5 with 74–83% of genomes lacking an output
      run.
    - Lexicase escapes because a constant-0 and a constant-1 output run are different
      specialists case by case, which keeps output runs in the population.
    - The 64-cell stack under the same tournament on OR: 0/30 (rate 0.015) and 2/30 (rate
      0.03); its random genomes look the same (88% at 0.5, 0.015% above). Tagged OR under
      tournament: 0/30 with crossover off (both joins), 4/30 (max) and 0/30 (leftmost) with
      crossover v2. The failure is balanced fitness on a map whose frequent phenotype is a
      constant, in both packages. XOR's parity only sets the later plateau (0.5 vs 0.75).
      (§22, §24, §25)
15. **Slow, not stuck.**
    - Leftmost XOR run to 10,000 generations (the first 3000 replay §19 exactly) goes from
      12 to 17/30 exact champions, and 21/30 populations hold an exact individual.
    - The §20 neighbourhood scan doesn't predict which runs solve later (0/18 had an
      improving neighbour; 5 later solved). Under lexicase the champion is the wrong object
      to scan; the selected parents are.
    - In unsolved lexicase populations, a three-quadrant specialist is present in ~80%
      (vs 1/30 under tournament), and a complementary pair of specialists in roughly a
      third to a half. (The earlier "complementary quadrant covers always present" was too
      weak: constant 0 plus constant 1 satisfies it.) (§20, §22, §23)

16. **Crossover assembly changes XOR discovery.**
    - Leftmost XOR, lexicase, 100 seeds each: populations with an exact individual 68/100
      (v2) vs 38/100 (v1), p = 3.5×10⁻⁵; exact champions 52 vs 31 (p = 0.004); exact
      members still present at generation 3000 in 58 vs 35 (p = 0.002).
    - Max-join XOR 25 vs 19/30 (p = 0.14) and leftmost OR 25 vs 24/30 (p = 1) are not
      significant.
    - Not shown: that run loss is the cause. v2 doubles unread runs (0.81 vs 0.36 per
      genome, generations ≥ 1000) but helper use is unchanged (8% of genomes in both; 9% vs
      13% of exact individuals, §26), and behaviour diversity is the same. v2 populations carry
      shorter output bodies (37 vs 47 cells in solved populations) and more silent second
      output runs (17% vs 12%).
    - **A control sharing v2's compaction but not its deletion** (v1c: strip trailing NOPs
      and trim the leader on overflow, then truncate as v1) reaches 61/100 at generation
      3000 (vs v1 38, p = 0.002; vs v2 68, p = 0.38). It does not reproduce v2's early lead:
      solved by generation 1000, v1 12, v1c 14, v2 32. v1c also keeps a cut-off tail run
      (a buffer against later truncation, and the source of silent output copies in 58% of
      genomes), so the design does not isolate compaction as the cause. (§26, fifteenth
      review)
    - Median first-exact generations (1090 vs 1277) are conditional on solving and not
      comparable at 68 vs 38 solvers. (§25, fourteenth review)

## Open

The XOR/valley thread is closed: the join question is answered (item 13) and no valley was
found. Remaining:
- **Step 2 is skipped (2026-09-30, fifteenth review).** Its substrate signals were weak
  before it started (helpers in 9–18% of exact individuals; a 128-cell tape holds ~1.3 runs
  under v2 without selection, against 14 outputs), and any effect would sit inside the range
  crossover assembly alone moves (items 13–16). The line pivots to the core map-bias
  question: a map whose bias differs from direct encoding (Plans/map-bias-pivot.md).
- **Silent-then-switch under v1c** (optional, one night): lineage tracing on v1c solvers
  for a change in which output run is read.
- **How plateaus are left** (low priority): a parent-level trace of the 5 late solvers.
- **Stable machinery** (parked with Step 2). On fixed-goal solved runs, elitism freezes the
  champion (in all 4 co-option runs the helper stayed unchanged, with one reader, to
  generation 3000). Reuse and entrenchment would need a multi-output task.
- **The core map-bias question** needs a map whose bias differs from direct encoding (the
  folding map or a tree-GP generator); chem-tape's decoder is close to identity (item 1).
