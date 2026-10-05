# Log: 07-shared-arrival

## Opened 2026-10-04 by the steward

Opened after [06](../06-self-mate-establishment/log.md) closed with "kept once common, under
self-mate too". The critic of run 2026-10-04-1839 pointed out that closing the shared-helper
line with "rare because it rarely arrives" would be an unshown claim. Proposed in
[runs/2026-10-04-2044](../../../runs/2026-10-04-2044/proposal.md).

## 2026-10-04: proposal revised (run 2026-10-04-2135)

The owner set aside the 2044 proposal and asked for a revision along its critique. The new
proposal uses the §32 J self/0.3/L 64 cohort only:
- a selection-weighted offspring census of the final populations (the engine's own lexicase
  reproduction, shared → shared excluded, B-helper vs A-only split);
- natural shared children inserted as single copies into their own populations, with matched
  no-insertion controls, staged from 100 to at most 300 insertions;
- an explicit "unresolved" outcome.

Observed target, from the saved `shared_stats`: in that cohort, 1 of 16 runs that first
established a non-shared form was later replaced by shared. In `017735…`, partly shared
established at generation 1340 and B-shared took over between 1600 and 1800. First discovery
as shared happened in 1 of 17 runs (`a81465…`, generation 680) and is out of scope.

## 2026-10-05: run 2026-10-04-2135, shared arrival (commit `f418c91`)

Experiment: §32 J self/0.3/L 64 cohort, 50 saved final populations. Stage 1: offspring census
with the engine's own lexicase reproduction, 173.7M children, 30.0M of them from partly
parents (stopped on target, not on the 2 h cap). Stage 2: 100 natural shared children,
sampled by expected arrivals, each inserted as one copy into its own population and continued
500 generations, with matched no-insertion controls.
[analysis](../../../runs/2026-10-04-2135/analysis.md), [plan](../../../runs/2026-10-04-2135/plan.md),
data `experiments/output/2026-10-04/2026-10-04-2135-shared-arrival/`.

Result:
- **Arrival:** 56 new exact shared children in the 16 target populations, all from partly
  parents, 12 of 15 measurable populations with ≥ 1. Rate 1.6e-6 per child; per population
  0 to 5.3e-6, a real spread. Times each run's non-shared duration: about 32 arrivals across
  the 15 runs with a known duration, about 2 per run (per-run 0–7; joint envelope 0.34–9.2).
  Many come from self-crossover, not point mutation (half differ at > 10 of 128 cells).
- **Helper type:** 44 A-only, 12 other, **0 B-helper**. Both historical shared populations
  (seed 7 after its replacement, seed 18) are B-helper. B-helper arrival ≤ 1.2e-7 per child,
  ≤ about 2.6 across the cohort's history.
- **Single copies:** 0 of 100 established (95% upper bound 3.6%), all exact-shared
  descendants gone by generation 30. Controls show the same thing in situ: 35 of 100 had
  transient spontaneous shared individuals (at most 8), all lost.
- **Reference (analysis's own calculation):** a neutral single copy among ~400 exact
  individuals would establish about 0.25% of the time, so 100 trials cannot tell neutral from
  disadvantaged. Losses are somewhat faster than a neutral branching model (6 vs ~16 of 100
  left at generation 10), so shared copies may be less heritable. Suggestive only.
- **Consistency:** ~32 arrivals × ≤ 3.6% gives ≤ ~1.2 expected replacements; 1 was observed.
- **Gaps:** mid-phase side check had no power (2 of 5 replays verified, 33k children each), so
  every per-run figure extrapolates from generation-3000 populations. Seed 7's partly phase,
  the one that actually switched, was not sampled. Seed 23 has no known duration.

Decision: park 07 because the result falls in the plan's "both may limit, bounds broad" cell,
which the plan counts as unresolved, and the stop rule ends the shared-helper line here.
What it does settle: "shared helpers are rare because they never arrive" is wrong for A-only
shared children (about 2 per run, all lost); it may be right for the B-helper form, which did
not arrive once in 30M partly-parent children yet is the form that won both times. That is a
hypothesis, not a result.
