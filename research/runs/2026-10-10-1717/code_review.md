---
verdict: pass
---

# Code review — 2026-10-10-1717 (crossed DG/TS family preference)

Reviewed `git diff 7cd049e..b5697a1` (three new modules, tests, frozen data),
proposal.md, critique.md, plan.md, queue.yaml, and the smoke evidence under
`smoke/`. I also ran independent checks (listed at the end).

## Blocking issues

None.

## Critique disposition

All seven critique notes are either implemented in plan.md and the report code
or explicitly deferred with a reason:

- Notes 1–5 (feasibility measurement, interaction vs dominance, own-family
  usefulness, precision as scenario, scope) are implemented. `classify()` in
  `family_preference_report.py` reports directional intervals, `dominant_bias`,
  `dominant_bias_with_interaction`, `own_family_useful`, and makes
  `family_specific_acquisition_candidate` conditional on reciprocity, own-family
  usefulness, and the I lower bound. Measured development rates and the full
  projected price are recorded in plan.md and enforced by the admission check.
- Note 6 (Wild & Porter precedent) is added in plan.md and report.md.
- Note 7 (digest wording) is deferred to the steward; plan.md says why
  (researcher may only write into the task folder). Acceptable.

## Gates and stop rules

The only gate that decides whether scoring runs is `admitted` in `prepare()`:
projected scoring time (1.3 × Σ calibration rates / effective workers + 90 s)
≤ 8370 s, and preparation elapsed ≤ 4770 s. It is a price/validity gate, not a
yield or outcome gate, and `score()` recomputes it from the stored calibration
rows. Could it stop the main stage for the wrong reason?

- Full-cap pilot projection is 4963 s against the 8370 s limit, so the gate
  needs ~1.7× worse rates on targets than development cells to fire. Even an
  all-capped worst case (~32 s per search, 9.15 workers) lands near 8150 s.
  Spurious stop risk is low. Preparation projection (~18 min of 80) is far from
  its limit.
- The other validity stops (`semantic_bank` mismatch, `cross_alias_check`,
  DG provenance checks) cannot fire spuriously: I regenerated the TS bank in the
  worktree and it equals the frozen artifact both in memory and after JSON
  round-trip (`digest` equal too); max label agreement between any TS split
  cell and any DG clique cell is 0.227, so the exact-equality alias check cannot
  trigger; the frozen DG files are byte-identical to the 1536 prepare output.

## Arm wiring, seeds, metrics (verified)

- `envelope()`: G4 → G4 table, no fragments; D → frozen DG builds; T → TS
  builds (intermediate `seed_builds` only during the adaptive source phase).
  Arm name is metadata only; search RNG streams derive from the seed.
- Score schedule: 16 cells × 48 ordinals × 3 arms = 2304; build = ordinal//2
  gives exactly 2 seeds per build per cell; the same seed is shared across
  G4/D/T for each (cell, ordinal). Seeds are disjoint from TS source,
  calibration, smoke blocks and from all 1536 DG seeds.
- 8 spare DG targets are the clique cells outside the 4/4/8 split; they appear
  in neither the 0311 nor the 1536 schedules. TS protected cells cover 5 GT
  pairings, sources 4 pairings and all four readouts.
- `arrays()`/`summarize()`: P_DG = T/D on DG, P_TS = D/T on TS, I = √(P_DG·P_TS),
  failures at 2×cap (1×cap repeat), log-mean over fixed cells; bootstrap
  resamples builds independently per cohort, keeps each build on both rosters,
  draws two-seed offsets jointly per build×cell, G4 resampled once per draw.
  Matches the proposal and plan.
- `rebuild()` reproduces the base A8 recipe (same `build_source` envelope,
  membership check) with a TS source roster; `load_dg()` re-verifies all 1536
  hashes, membership, and the production method hashes.
- Committed `family_preference_run.py` hash equals the one frozen in the final
  smoke prepare/score (`smoke/final-prepare/method_freeze.json`), so the smoked
  orchestration is the committed one. 7 unit tests pass.

## Minor notes

1. Every smoke/pilot prepare used `--bank` from a prebuilt file, so the in-run
   `build_bank()` + `semantic_bank` comparison path had not been exercised
   before this review. I ran it; it reproduces the frozen bank in 125 s. No
   change needed, but worth knowing when reading the smoke logs.
2. `score()` compares recorded `rates` with exact float equality while using
   `np.isclose` for the other two quantities. It works because the rows are
   re-sorted identically and JSON float round-trip is exact; a tolerance would
   be more robust.
3. If scoring ever exceeded its 8370 s deadline, `search.jsonl` is streamed
   line by line so completed rows survive, but `result.json`/`report.md` would
   not be written. The analyst can rerun `report()` offline on the rows.
4. New `rebuild()` omits `record["alphabet"] = ALPHABET` that the base runner
   sets; `source_summary` and the report do not read it. Cosmetic.
5. `cross_alias_check`'s solver branch is redundant (every solver is verified
   to equal its source labels, which already differ from all targets). Harmless.

## Independent checks run

- SHA256 of all ten frozen DG files vs `experiments/output/2026-10-10/2026-10-10-1536-independent-input-prepare/` and vs `provenance.json`: all equal; 1536 config commit is 7244fa1.
- `build_bank()` regeneration vs `load_ts()`: semantic fields equal (in memory and after JSON round-trip); `digest(banks)` stable across round-trip.
- Schedule counts 768/96/2304; calibration cycles all 24 builds; common seeds across arms; no seed overlap with 1536.
- `pytest tests/test_family_preference.py`: 7 passed.
