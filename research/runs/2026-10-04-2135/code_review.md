---
verdict: pass
---
# Code review: 2026-10-04-2135 shared arrival

Reviewed `fbd63a1..f418c91` (`experiments/chem_tape/shared_arrival.py`, the
parent-row change in `chem_tape/evolve.py`, `tests/test_shared_arrival.py`)
against proposal.md, approval.md, plan.md (including the dated amendment) and
queue.yaml.

## Blocking issues

None. I found nothing that would make the stage-1 rates, the exposure
weighting, or the stage-2 lineage verdicts wrong.

## What I checked

- **Tests.** `tests/test_shared_arrival.py`: 12 passed. `test_s32_mate`,
  `test_shared_helper`, `test_chem_tape_mapbias_step1_3`: 37 passed.
- **Source cohort on the real data.** The manifest finds exactly 50 seeds.
  The 16 targets are wired as the plan says:
  - seed 7 (`017735…`, the replacement run) is a target but not
    insertion-eligible (421 of 422 exact non-elites are shared);
  - seed 23 is a target with unknown duration, zero exposure weight, and is
    excluded from insertion sampling;
  - seeds 13 and 16 (4 and 10 exact non-elites) and seed 18 (shared first) are
    not targets.
- **Stage-1 census.** It calls the engine's own `_reproduce_one_island` with
  lexicase over the whole population and counts only the 1022 offspring.
  - The parent stratum comes from the actual parent index (`row[0]`).
  - Arrivals exclude shared parents.
  - Rates are per all offspring; `E_k = T_k · arrivals_k / children_k`.
  - One real frozen generation on seed 27 gave 998 children from partly
    parents, 24 from shortcut parents and 0 from non-perfect parents, as
    lexicase should.
- **Caches.** Training results and forms are cached by semantic key, the same
  key the engine's `SharedCensus` uses. A 45 s replay of seed 27 on the real
  data matched every history column and the saved shared/run census for 734
  generations, so the cached scoring reproduces the original run.
- **Seeds.** Census seeds (`321350 + 1000·source seed`, `+100` for mid),
  continuation seeds (`321351000 + trial`) and the slot RNG are all distinct
  and do not collide with the source seeds. Insert and control arms share the
  continuation seed on purpose; the first generation is identical before the
  slot is replaced.
- **Stage-2 sampling.** Each arrival occurrence is weighted by
  `exposure / children` of its source, so source k is drawn in proportion to
  `E_k`. No layout balancing, no 1/5 cap, no transfer controls.
- **Lineage.** Descendant flags propagate through the engine's parent rows,
  elites included. The verdict needs ≥ 20 exact non-elites and ≥ 50%
  descendant-shared share. Descendant share and total shared share are kept
  separate, so an independent arrival cannot count as an inserted-lineage win.
- **Engine change.** It only alters the recorded second-parent index for
  `self`/`random` mates and draws no RNG. `track_lineage` remains forbidden
  for those mates, so existing consumers are unaffected.

## Minor notes (non-blocking; for the analysis)

1. **The mid-phase side check cannot do its job as queued.** Treat the result
   as final populations only.
   - A full replay runs at about 16 generations/s, so roughly 190 s per source
     run one after another on the main process. The 600 s budget completes
     about 3 of the 5 replays.
   - The scope string needs exactly 5 verified replays, so it will always say
     "final populations only". That fallback is the one the plan prescribes.
   - The third replay candidate is seed 16 (`1e3778…`): not a target,
     established for one 20-generation interval, and its "midpoint" 2620 lies
     outside any occupied interval. The fourth, seed 20, has intermittent
     occupancy. Candidates are simply the first five partly-first sources;
     they are not filtered by target status or midpoint occupancy.
   - Each verified midpoint gets 32 frozen generations (about 33k children).
     At rates near 1e-6 the `endpoint_midpoint_ci_overlap` flag will be true
     whatever the truth is. Do not read it as support for representativeness;
     check each mid record's `baseline.exact_nonelite`.
   - If the owner wants the side check to count: run the replays in the idle
     worker pool, pick target sources with an occupied midpoint, and give the
     mid census many more generations.
2. **Per-source bounds are loose even at target.** 3e7 partly-parent draws is
   about 2e6 children per target source. A zero-arrival source then has an
   upper rate near 1.5e-6, which is about 2–3 expected arrivals over its own
   exposure. The reported `joint_rate_duration_envelope_per_run` is
   Bonferroni-conservative and will not by itself show `E ≤ 1`. The analysis
   should say which bound it uses.
3. **Seed 7's rate is measured on its shared final population.** Almost all
   children there have shared parents, so its `E_k` is low by construction.
   It is 380 generations, about 1.8% of the known exposure, and is listed in
   `historical_scope_limitations`.
4. **Seed 1 established duplicated but ends partly.** Its 1020 generations of
   exposure are multiplied by a rate measured on a partly population. This is
   the same proxy caveat as the plan's amendment.
5. **The low-arrival stop branch can never fire.** `e <= 1` also requires no
   missing exposure, and seed 23 is always missing. A low-arrival run
   therefore still does 100 insertion pairs and is labelled "intermediate
   exposure". This matches the amendment; just read the `stage2_stop` label
   with that in mind.
6. **`lineage_outcome: extinct` means no exact-shared descendant at
   generation 500.** Non-shared descendants may still be alive; use
   `descendant_loss` for full lineage loss. For controls,
   `total_shared_first_absence` assumes presence at generation 1 and is not
   meaningful when shared was never present.
7. **Unequal draws per source.** Sources are split five per worker and
   workers stop on a shared counter, so sources get somewhat different
   numbers of frozen generations. Rates are per source, so this is harmless,
   but pooled unweighted rates should not be quoted.
8. **Disk.** Per-source offspring batches for the full run will be a few
   hundred MB.
