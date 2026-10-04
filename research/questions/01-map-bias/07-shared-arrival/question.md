---
status: open
tags: [shared-helper, arrival, arrival-of-the-frequent, form-transitions, single-copy, self-mate, tagged-runs]
budget: {experiments: 2, used: 0}
---
# Are shared helpers rare in evolved solutions because variation rarely produces them, or because new copies rarely fix?

Current summary: Once 3–10% of the population is shared, the form is kept and usually wins
under crossover off or self-mate crossover (06). Yet random-start runs end shared in only
2/50, 0/50 and 2/50 runs under self-mate (§32 J) and 4 of 100 with a selected mate (§31 G,
§32 G2); a real B helper ends 8 of 450 §31 G runs. Two things can make that rare: shared
exact children are seldom produced by variation (arrival), or they are produced but a single
new copy almost never fixes (§31 F: about 3% vs duplicated and 1% vs partly shared with
crossover off, single-copy self-mate untested). Side evidence for biased arrival: in every
seeded contest against duplicated, runs that lose shared end partly shared, a form nobody
seeded (run 2026-10-04-1839 analysis). Untested.

Competing explanations:
- A (arrival): variation from the populations evolution actually reaches produces exact
  shared children far more rarely than partly-shared or duplicated ones; arrival rate ×
  single-copy fixation predicts about the observed handful of shared endings. This is the
  root's "arrival of the frequent" at the level of program forms.
- B (fixation): shared children arrive often enough, but a new single copy fixes much less
  often than a seeded 3% share, e.g. because it arises in an established population of
  another form (first-form persistence) or arrives non-exact.
- C (path): shared arrives through non-exact intermediates over several steps, so one-step
  offspring rates undercount it and neither A nor B is measured correctly by a one-step
  census.

Related: [01-map-bias](../question.md),
[06-self-mate-establishment](../06-self-mate-establishment/question.md) (kept once common),
[04-random-start-discovery](../04-random-start-discovery/question.md) (random-start endings,
§31 G, §32 J), [03-rare-shared-establishment](../03-rare-shared-establishment/question.md)
(§31 F single copies, crossover off), [notebook §31, §32](../../../../docs/map-bias/notebook.md),
sweep `experiments/chem_tape/sweeps/mapbias/s31_few_copies.yaml`, final populations under
`experiments/output/2026-10-03/mapbias_s31_stage4/` and
`experiments/output/2026-10-04/mapbias_s32_mate/`

Stop rule: this is the last experiment planned for the shared-helper line. Whatever it shows,
the line is parked or closed afterwards, and attention moves to the root's part 2 or to 02.
