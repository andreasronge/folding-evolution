# Self-mate establishment implementation plan

Written before experiment or smoke execution, 2026-10-04. Implements the approved
[proposal](proposal.md), with diagnostic reporting requested in [critique](critique.md).
This is an implementation plan for that proposal, not a new experiment or promotion.

## Conditions and seeds

- Exactly 240 full evolution runs: shared vs duplicated / partly shared × starting
  shared fraction 1/32 / 1/10 × crossover rate 0.3 / 0.7 × seeds 0–29.
- Copy the L=64 seed tapes and all other parameters from `s31_dose.yaml`:
  population 1024, lexicase, mutation 0.015, 300 generations, seed_split,
  two elites, tagged alphabet, leftmost combination, crossover v2, fixed task
  mbs_three, 64 training cases, 256 holdout cases, census every 5 generations,
  exact/shared and run tracking, final population dump. Only mate selection
  changes to `crossover_mate: self` (lineage tracking remains off).
- Historical crossover-off and selected-mate comparisons are existing data;
  no extra control evolution runs. Starting counts follow the existing split
  implementation (1/10 is a nominal fraction, not a promise of exactly 102.4).
- One-crossover census: each of the same three L=64 hand-built seed forms,
  10,000 independent v2 crossovers with itself, fixed RNG seed 0 per form.
  No mutation, selection, or chaining children as parents. Use the evolution
  operator implementation and its defaults; record operator parameters and
  parent genomes. The existing API returns one child per event: 10,000 calls and 10,000
  children per form. This corrects the initial two-child assumption after
  inspecting the API, before running any experiments.
- Smoke only: seed 0 in all eight cells at population 64 for 20 generations,
  and 100 census events per form. Smoke verifies wiring, not hypotheses.

## Measurements and producing paths

- Final verdict: reuse `s31_report.classify_run` and `outcome`, exhaustive
  exactness and knockout form classification of final non-elites. A win needs
  at least 20 exact non-elites and >90% shared among them; zero shared is gone;
  remaining valid populations are between; fewer than 20 exact is no_solution.
  Report all four counts per competitor × start × rate, final form counts,
  exact counts, and elite forms separately. Implement a task-specific report
  wrapper grouping on these axes and enforcing all expected seeds/configs.
- Early shared shares at generations 5, 10, 20: direct `result.json:shared_stats`
  census values, with exact and sampled denominators. Missing exact populations
  remain null, not zero. These are sampled census shares, not full population
  measurements. Retain the complete trajectory and late (250–300) census
  values to distinguish persistent mixed populations from disappearance.
- Census: new small script using `shared_helper.Exactness` and `classify`:
  fully exact shared / partly / duplicated, broken (not fully exact), and any
  fully exact other form separately so unknown forms cannot become broken.
  Record clone frequencies separately (a clone can also be an exact form).
  Cache repeated genomes/semantic classifications without changing counts.
- Full output: config.yaml, result.json, history.npz, final_population.npz,
  sweep_index.json, SWEEP_COMPLETE; per-run and per-cell readout JSON/Markdown,
  trajectory plot; census JSON/Markdown. All full outputs go under `$RUN_DIR`.
  No statistical significance tests: counts and baseline-relative rescue
  thresholds are exploratory decision aids, not equivalence tests.

## Pre-data interpretation

Historical crossover-off wins (out of 30), in 1/32 then 1/10 order:
vs duplicated 19,29; vs partly 8,19. Selected mate at 0.3: duplicated 10,24,
partly 0,0; at 0.7: 0,0 against both.

| Establishment pattern | Shared seed census damage exceeds competitors | No excess shared seed census damage |
|---|---|---|
| Strong rescue: at both rates each cell reaches roughly 2/3 of its off baseline (ceilings: duplicated 13/20; partly 6/13 wins) | Mixing-dependent barrier supported; rearrangement damage exists but does not prevent establishment in these cells. | Mixing-dependent barrier supported for these layouts; discovery and seeded establishment compatible under self-mating. |
| Weak: partly wins remain 0–3/30 and duplicated at 0.7 far below off baseline | Rearrangement contributes to failure; removing hybridization is insufficient (proposal B). Inspect late populations before calling failure definitive. | Removing mixing is insufficient, but the proposed seed fragility mechanism is unsupported; mechanism unresolved. |
| Partial rescue across competitor, rarity, or rate | Mixed explanation; census conversion vs brokenness helps locate the gap; proposal C. | Partial compatibility established for the rescued settings, mechanism of remaining gap unresolved; proposal C. |

The proposal's 1/10 examples use ≥19 and ≥12; exact two-thirds ceilings above
are 20 and 13. Report raw counts and both comparisons rather than making a
one-win boundary mechanistic. No numeric gate is invented for "far below".
Early retention and final wins are independent: early decline followed by rescue
suggests recovery; early persistence followed by failure suggests a late barrier;
early decline plus failure suggests rapid loss; persistence plus rescue suggests
retention. Census is advisory evidence about initial layouts only, not evolved ones.

Persistent/increasing shared mixed populations at generation 300 are unresolved
rather than evidence of impossibility; report their late trajectories. Too-clean
success (all clones or all wins) first triggers operator/config/seed checks; unchanged
children are an expected self-crossover possibility and must be quantified.
Missing runs, short runs, wrong configs, missing snapshots, or denominator failures
invalidate a complete-grid report; do not silently exclude them.

Any closure or follow-up is for the subsequent reviewer/steward. Results here cannot
justify a general arrival-limited claim: seeded populations begin with many hand-built
copies, not one newly arisen natural helper. No follow-up is queued in this task.

## Implementation and validation sequence

1. Preserve this plan; generate the eight-cell sweep from the historical YAML.
2. Reuse the existing dynamics engine unchanged. Add census and report wrappers.
3. Smoke all eight cells and a small census; check deterministic replay, original
   parameters/seed tapes, verdict boundaries, clone/form count conservation,
   exact parent forms, early/late metrics, and incomplete-grid rejection.
4. Write task `queue.yaml` only after smoke passes. Evolution uses 10 workers;
   census is sequential. Size remains 240 runs, with a timeout allowing about
   three times the proposal's 20-minute estimate. Require completion/readouts.
5. Copy task plan/queue into this worktree for versioning, document smoke evidence
   in the task folder, commit on research/2026-10-04-1839, verify clean status.
