---
status: parked
tags: [shared-helper, arrival, arrival-of-the-frequent, form-transitions, single-copy, self-mate, tagged-runs]
budget: {experiments: 2, used: 0}
---
# Are shared helpers rare in evolved solutions because variation rarely produces them, or because new copies rarely fix?

Current summary (2026-10-05, parked): In the §32 J self/0.3/L 64 cohort, established partly
shared populations do produce exact shared children, about 2 per run over the non-shared
phase (rate 1.6e-6 per child, 12 of 15 populations with ≥ 1), and a natural single copy put
back into its own population never established (0 of 100, ≤ 3.6%; all gone within 30
generations). Controls show the same arrive-and-vanish pattern in situ. The product (~32
arrivals × ≤ 3.6%) is consistent with the one observed late replacement but does not explain
it. Every arrival seen was A-only or other; **no B-helper child arrived** (≤ 1.2e-7 per child),
yet B-helper is the form in both shared-ending runs. Hypothesis, not shown: A-only copies
arrive and drift out; the B-helper form almost never arrives and wins when it does. Scope:
one task, one cell, final populations only (the mid-phase check had no power), late
replacement only; first discovery untested. ([run 2026-10-04-2135](../../../runs/2026-10-04-2135/analysis.md))

Earlier context: once 3–10% of the population is shared, the form is kept under crossover off
or self-mate (06). Random-start runs end shared in only 2/50, 0/50 and 2/50 runs under
self-mate (§32 J) and 4 of 100 with a selected mate (§31 G, §32 G2).

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
- D (form-specific, added 2026-10-05): "shared" is two things. A-only shared children
  arrive a few times per run and drift out like any single copy (B-like); B-helper children
  almost never arrive but take over when they do (A-like). Fits run 2026-10-04-2135; untested,
  since no B-helper copy was ever inserted.

Related: [01-map-bias](../question.md),
[06-self-mate-establishment](../06-self-mate-establishment/question.md) (kept once common),
[04-random-start-discovery](../04-random-start-discovery/question.md) (random-start endings,
§31 G, §32 J), [03-rare-shared-establishment](../03-rare-shared-establishment/question.md)
(§31 F single copies, crossover off),
[runs/2026-10-04-2135](../../../runs/2026-10-04-2135/analysis.md) (census + insertions), [notebook §31, §32](../../../../docs/map-bias/notebook.md),
sweep `experiments/chem_tape/sweeps/mapbias/s31_few_copies.yaml`, final populations under
`experiments/output/2026-10-03/mapbias_s31_stage4/` and
`experiments/output/2026-10-04/mapbias_s32_mate/`

Stop rule: this is the last experiment planned for the shared-helper line. Whatever it shows,
the line is parked or closed afterwards, and attention moves to the root's part 2 or to 02.

Reopen if: (a) a B-helper single copy becomes testable: a B-helper child turns up in a census
or replay, or the owner accepts B-helper copies taken from seed 7 / seed 18 as a labelled
transfer test, and ≥ 300 insertions under self-mate 0.3 are affordable (needed to bound p near
1%); or (b) instrumented deterministic replay of the §32 J runs exists (arrivals and their
fates recorded in situ, including seed 7's partly phase and first discovery); or (c) another
line (e.g. 08) needs to know whether helper type decides establishment. Separating "neutral"
(≈ 0.25%) from "disadvantaged" single copies needs thousands of insertions; do not reopen for
that alone.
