# Plan: crossing the valley — what comes after the lineage post-mortem

Written 2026-09-28. Hobby mode: one "what would be interesting to see" paragraph per arm
in the notebook, results written up plainly afterwards. No pre-registration apparatus.
Context: map-bias notebook §1–§16, findings.md items 2, 9, 11–13.

## Question

How does evolution cross a structural valley — a missing join that no intermediate step
rewards — without the designer handing it the join? The map-bias line showed that a join
the chemistry gives away (free max, IMAX, combine markers) becomes easy. It never showed
evolution *building* one (§9 open problem). The general theme is still map bias: whether
the genotype→program map makes half-built things harmful (stack: junk on the stack),
neutral (tagged runs: inert transplants), or useful (a task family that rewards them).

Five routes, from the discussion (literature from memory, not checked):
1. **Drift / tunnelling** (Weissman et al. 2009): large populations cross narrow valleys;
   the cost grows roughly exponentially with width. This is the null curve to beat.
2. **Recombining blocks**: already understood here (§12–§14). It moves parts but doesn't
   create the join.
3. **Lifetime learning over structure** (Hinton & Nowlan 1987). The earlier threshold-plasticity
   null tuned a number; the valley is structural.
4. **Silence, then switch** (pseudogenes, Hsp90, Lenski's citrate duplication/promoter
   capture). Never seen in any chemistry (item 11); the silent-route estimate (§3) is
   ~1:80 against direct building because silent blocks mutate at the full rate.
5. **Useful intermediates** (Lenski, Ofria, Pennock & Adami 2003: EQU evolved only when
   simpler logic functions were also rewarded). Best supported in nature, and it changes
   what the world rewards rather than the machine.

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
3. Leftmost XOR ≥ ~8/30: post-mortem its solvers (look for rewiring, the first *built*
   join). Leftmost XOR ≤ 2/30: the valley is real; build the ruler on leftmost.
   This needs tagged `seed_tapes` plus a hand-written leftmost XOR solver with k cells
   deleted from the join run, and rewiring/retag on vs off (~1 h).
4. Step 2 on leftmost, three arms (family / target-only lexicase / target-only summed);
   needs a coding session.
5. Route 4 with a promote/wire mutation; structural plasticity parked.

The original steps below are kept for reference.

## Step 0 — lineage post-mortem (overnight, runs before this plan starts)

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

## Step 1 — valley ruler on XOR (markers off)

**What would be interesting to see:** the recovery time as a function of valley width k,
and whether switching off header retags changes it.

- **Design.** Start from tagged XOR two-run solvers (the 8/13 with two SWAP'd output
  runs). Delete k cells from the *join only* — the second output run's
  RECV, RECV, SWAP, GT and the header retag to 0 — for k = 1, 2, 3, 4 (the join is only
  ~4–5 cells, so k stops at 4). Seed the whole population with the damaged genome.
  mbs_xor, tagged, tape 64, rate 0.015, lexicase, balanced, fast_rng, 1000–2000 gens.
- **Arms.** Each k × {header-retag mutation on, off}. 30 seeds per cell (spread over the
  8 base solvers). 8 cells × 30 runs ≈ 1.5–2 h.
- **Readout per run.** Generations to exact XOR, and the endpoint class: rebuilt the join,
  found a different route (e.g. single-run XOR), or never exact.
- **New code.**
  - `seed_tapes` currently assumes length-L stack tapes; extend it to TAG genomes (2L).
  - A header-retag switch: freeze mutation of SEP cells' tags only, so RECV targets
    still mutate.
  - A small "damage" script that builds the k-deleted seeds from the solvers.
- **Interesting if:** the curve is steep (roughly exponential in k), which confirms the
  valley and gives every other route a baseline. Retag off slowing recovery → the silent
  route matters. **Kill / boring if:** k = 4 recovers as fast as k = 1 (no valley), or all
  recoveries take a different route (then the ruler measures that route, not the join).

## Step 2 — generic-reward staircase (useful intermediates)

**What would be interesting to see:** whether rewarding a generic family of simpler
functions lets evolution build a join it can't build when only the target is rewarded —
Avida's EQU result on this system.

- **Design.** Multi-output tagged genomes: each output tag t = 1..14 is one of the 14
  non-constant two-input Boolean functions of p1 = max>5 and p2 = sum>10 (target
  included, as EQU was in Avida). Compare:
  - *family*: all 14 rewarded;
  - *target only*: only the target output rewarded (AND, and separately XOR).
  Chemistry with **no free join**: tagged with leftmost-wins, so max isn't handed out
  (or the stack, if multi-output is easy there). Otherwise the family is solved by the
  free max and says nothing.
- **Open design choice: how to combine 14 outputs into one selection signal.**
  - Lexicase over the pooled cases of all outputs (natural here).
  - Avida-style multiplicative bonus per output that is exact.
  - Summed balanced accuracy.

  These behave very differently. Pick one on purpose and note it; lexicase-pooled is the
  default. A count output (p1 + p2, values 0/1/2) would need exact-match scoring;
  leave it out unless added deliberately.
- **Arms.** family vs target-only, for AND and XOR: 4 arms × 30 seeds × 3000 gens,
  ~1 h.
- **New code.** Multi-output evaluation (the output of tag t for each rewarded t), the
  family task definition, and the fitness combiner. About half a day.
- **Interesting if:** family ≫ target-only on the target's exact solves, with lineages
  showing the target assembled from rewarded sub-functions. **Kill:** no difference →
  intermediates don't help here, or the combiner drowns the target (check the per-output
  solve rates before concluding).

## Step 3 — duplication on XOR (markers off)

Rerun gene duplication (`run_duplication_rate: 0.1`) vs none on mbs_xor, tagged, 30 seeds
× 3000 (~25 min). XOR solvers are two SWAP'd copies, so a copy of a working comparison run
is exactly the right starting material — the place where duplication *should* help.
**Prediction: null.** Crossover already supplies the copies (7/8 second runs were exact
copies of the other parent's output run, §16), so duplication supplies something that
isn't scarce. Write the prediction down before running it.

## Step 4 — silent-run protection (only if Steps 0–3 leave route 4 open)

Lower mutation on runs that nothing reads, like `bond_protection_ratio` but for silent
runs. Describe it as an **engineered capacitor**, not a biological analogue: in nature,
expressed genes are repaired *faster* and pseudogenes decay at the neutral rate or faster.
Test it on the Step 1 ruler (does protection flatten the curve with retag on?).

## Step 5 — structural lifetime learning

A few "wildcard" cells whose op or RECV target the individual picks during evaluation by
trying the options on its training lists (Hinton & Nowlan style, discrete switches).
Lifetime trials **must be charged against the evaluation budget**, otherwise it is brute
force hidden inside each individual. Compare against the Step 1 ruler at equal total
evaluations. The most code of all steps; only after 1–2 have results.

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

## Order and budget

| step | what | new code | compute |
|---|---|---|---|
| 0 | post-mortem, both parents | trace mode + script | ~15 min (tonight) |
| 1 | XOR valley ruler, retag on/off | TAG seeding, retag switch, damage script | ~2 h |
| 2 | generic-reward staircase | multi-output eval + combiner | ~1 h, ½ day code |
| 3 | duplication on XOR | none | ~25 min |
| 4 | silent-run protection | protection knob | ~1 h, only if needed |
| 5 | structural plasticity | wildcard cells + charged budget | later |

Steps 1 and 3 fit one night together; the parked XOR controls also fit that night if
wanted. Step 2 needs a coding session first.
