# Shared helpers: can tagged runs preserve and reuse a functional part?

Status: planned 2026-10-02, after the seventeenth (Fable) review (docs/map-bias/notebook.md §28)
and a direction check. Written as a hand-off: a coding agent should be able to implement, check,
run and write up stages 1–3 from this file alone. Stages 4–5 are outlined and need their own short
plan once stage 3 is read.

## Why

Nights 1–2 of the map-bias pivot answered "which map samples fixed-target solvers more often".
That is not the project's building-block question:

> Can the chemistry help evolution discover, preserve and reuse functional parts as programs
> become more complex?

What is already known (docs/map-bias/findings.md):
- Helper wiring by RECV happens, but rarely: 5 of 31 leftmost XOR solvers, helpers in 9–18% of
  exact individuals. 26 of 31 solve inside a single run (item 13).
- Keeping 2–6× more unread runs (crossover v2, v1c) does not raise helper use (items 13, 16).
- Elitism freezes the champion; reuse needs a multi-output task (Open, "Stable machinery").
- The earlier multi-output plan (Plans/valley-crossing.md, Step 2: 14 outputs on 128 cells) was
  skipped: too many outputs for the tape, weak helper signal, effect inside crossover noise.

This plan is a much smaller version of Step 2 with one addition the earlier one lacked: **a
reason for sharing to pay**, and a check that the chemistry can hold a shared solution at all
before asking evolution to find one.

## Read first

- `CLAUDE.md`; `docs/map-bias/findings.md` Setup, Measurement, items 3, 7, 11, 13, 14, 16.
- `Plans/valley-crossing.md` "Step 2 design choices to fix before coding" (lines ~81–98): the
  pitfalls listed there still apply.
- `src/folding_evolution/chem_tape/tagged.py` (runs, RECV, `genome_outputs`, `run_values`,
  `run_census`, `crossover` variants, `build`), `config.py` (`tag_combine`, `tagged_crossover`,
  `track_exact_any`, `seed_tapes` / `seed_fraction`), `tasks.py` (`mbs_*` stratified tasks).
- Process: hobby project, light lab notebook, no pre-registration. At most two codex reviews
  before a launch. Commit and push before launching. Results go in a new notebook section (§29)
  with the commit hash.

## The task

Inputs as in §15 onwards: length-4 integer lists over [0, 9], stratified cases, lexicase.
Predicates A = max > 5, B = sum > 10.

Three rewarded outputs, read from three output tags (0, 1, 2), leftmost-wins, no markers:

| output tag | function | note |
|---|---|---|
| 0 | A | cheap; also a possible helper for 1 and 2 |
| 1 | A and B | |
| 2 | A or B | |

B is never rewarded on its own and is needed by two outputs, so a B run read by both is a
genuine non-output shared helper. A is the "an output is also a helper" case, the only helper
route seen so far.

Expected hand-built sizes (verify in stage 1; op ids in `chem_tape/alphabet.py`):
- A: `INPUT REDUCE_MAX CONST_5 GT` (4 cells). B: `INPUT SUM CONST_5 CONST_5 ADD GT` (6 cells).
- and of two 0/1 values: `ADD CONST_1 GT`; or: `ADD CONST_0 GT` (3 cells each).
- **Shared form:** runs A (tag 0), B (a free tag), `RECV 0, RECV b, ADD, CONST_1, GT` (tag 1),
  `RECV 0, RECV b, ADD, CONST_0, GT` (tag 2): about 24 cells with separators.
- **Duplicated form:** tag 1 and tag 2 each recompute A and B inside their own body: about 33
  cells.

That gives the sharing knob for free: **tape length**. At 32 cells the duplicated form does not
fit and the shared form does; at 64 and 128 both fit. If the real sizes differ, pick the three
lengths so that the same statement holds, and say so.

## Measures (used in every stage)

- **Exact** = right on all 10,000 lists, per output. A genome is *fully exact* if all three are.
- **Knockout dependency.** For each run in a genome, replace its body with NOPs and re-evaluate
  all three outputs on all 10,000 lists. A run's *consumer count* is the number of rewarded
  outputs that change. Do not use structural RECV counts alone: a RECV can be read and ignored.
- **Shared helper** = a run with consumer count ≥ 2. Report separately:
  - *output-as-helper*: the tag-0 run with consumer count ≥ 2;
  - *pure helper*: a run that is not the first run of tags 0–2, with consumer count ≥ 2.
- **Form of a fully exact genome:** shared (has a pure helper), partly shared (output-as-helper
  only), duplicated (neither).

## Stage 1 — Express (no evolution; about half a day)

New file `experiments/chem_tape/shared_helper.py` (and tests). Do not change `src/` unless
multi-output evaluation cannot be done with `genome_outputs` / `run_values` as they are.

1. Build the shared and the duplicated genome by hand with `tagged.build` at tape lengths 32, 64
   and 128 (where they fit). Add a partly shared one (tags 1 and 2 read A by RECV but recompute B).
2. Evaluate all three outputs on all 10,000 lists: each form must be fully exact.
3. Run the knockout measure on each: the shared form must show a pure helper with consumer count
   2 and the tag-0 run with consumer count 3; the duplicated form must show none.
4. Record cell counts per form and which tape lengths each fits.

**Stop if** no shared form can be written under leftmost-wins with the `tagged` alphabet. Write
down what blocked it (that is the chemistry obstacle, and the input for an extension). Do not
switch to `tag_combine: max` or markers to make it work without saying so.

## Stage 2 — Preserve (variation only, no selection; minutes of compute)

For each hand-built form at each tape length it fits, 10,000 trials per cell:

| operator | what to apply |
|---|---|
| mutation | `tagged.mutate` at the rate used in §25 |
| crossover v1, v2, v1c | form as parent A with a random genome as parent B; form as parent B with a random parent A; form × the *other* form |

Report per cell: fraction of children fully exact; fraction keeping each single output; mean
number of outputs lost; fraction where the pure helper run survives intact. Compare shared vs
duplicated at the same tape length.

What would be interesting: the shared form is a smaller target (fewer cells to hit) but one hit
on B breaks two outputs. Which effect wins is not obvious and decides whether sharing is fragile
before selection even acts.

## Stage 3 — Retain (one short night)

Needs multi-output evolution. Code changes, as small as possible:
- a three-output task (labels for tags 0–2 on the same stratified cases);
- lexicase over the pooled output × case set (3 × 64 cases; findings item 14: tournament on
  balanced fitness is flat, do not use it);
- per-output and fully-exact population-level tracking (`track_exact_any` keyed by output);
- seeding of tagged genomes. Check whether `seed_tapes` handles the 2·L tagged layout; if not,
  add the smallest hook that does.
- every `log_every` generations, on a sample of the population: fraction fully exact, and among
  those the fraction shared / partly shared / duplicated by knockout.

Defaults must leave existing single-output sweeps byte-identical (replay 3 seeds of
`xover_v2_xor_leftmost.yaml` and compare champions).

Arms, crossover v2, population and rates as §25, 1000 generations, 30 seeds:

| arm | initial population | tape lengths |
|---|---|---|
| seed-shared | all copies of the shared form | 32, 64, 128 |
| seed-dup | all copies of the duplicated form | 64, 128 |
| seed-mixed | half shared, half duplicated | 64, 128 |

Queue file `experiments/chem_tape/sweeps/mapbias/queue_s29.yaml`, run with `scripts/run_queue.py`.
Pilot 2 seeds per arm first and set timeouts at 3× the estimate.

Readouts:
1. **seed-mixed is the main one.** Share of fully exact individuals that are shared, over
   generations. Neutral expectation is drift around 50%. Report the fraction of the 30 seeds
   ending above 90% shared and above 90% duplicated, per tape length.
2. seed-shared: does the population stay fully exact, and does the shared form persist or get
   replaced by duplicated or partly shared forms (at 64 and 128, where duplication fits)?
3. seed-dup: does sharing ever arise from a duplicated start?
4. Run census (`track_runs`) per arm, to see whether the B helper run is kept.

Reading it:
- Shared form is lost at 64/128 and kept only at 32 → sharing needs a size pressure; stage 4
  uses tape length as its knob.
- Shared form is lost even at 32 (population stops being fully exact) → preservation is the
  obstacle. Look at stage 2's numbers for which operator breaks it; that names the chemistry
  change worth trying (for example more robust connections under crossover).
- Shared form holds or wins at all lengths → retention is not the problem; discovery is. Go to
  stage 4.

## Stage 4 — Discover (outline; plan after stage 3)

From random starts, the three-output task at tape lengths 32, 64, 128, 50 seeds, 3000 generations.
- Readout: fraction of fully exact populations, and the shared / partly shared / duplicated split
  among them by knockout. Prediction if sharing is driven by size pressure: the shared fraction
  rises as the tape shrinks.
- Controls carried over from nights 1–2: a random-genome sample (how often is each form produced
  by chance at each tape length?), and exactness on all 10,000 lists.
- A single-output AND arm and a single-output OR arm at the same budget of case evaluations, to
  see whether the extra outputs help or hurt the hard ones.

## Stage 5 — Extend (outline; last)

Start from stage 4's solved populations, add a fourth output that can use A or B (for example
B and not A). Does a new consumer of an existing helper evolve while outputs 0–2 stay exact?
This is the riskiest stage: elitism freezes champions and tagged runs tracked goal switches
worse than the stack (item 10).

## Not in this plan

- Chemistry extensions (parameterised helpers, argument binding, two-argument functions). Add
  one only when a stage names the obstacle it would remove.
- The rarity ladder (findings Open) is optional background, one night with existing code. It
  does not block this plan.

## Write-up

Notebook §29 in `docs/map-bias/notebook.md`: one paragraph before, plain results after, the
commit hash, tables for stages 1–3, one figure (seed-mixed shared fraction over generations, one
line per tape length). Do not amend findings; leave that for the next Fable review.
