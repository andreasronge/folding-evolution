---
verdict: pass
---
Reviewed `4842a53..a65ded0` (assembly_bank / assembly_maps / assembly_run / assembly_report,
the two small composition_* parametrisations, tests), proposal, critique, plan, queue and smoke.

## Blocking issues

None.

## What I checked

- **Screen correctness.** Depth ≤ 8 states are deduplicated on the full typed stack, depth 9
  is output-only; a 9-token program whose 8-prefix was first reached at a shallower depth is
  covered because its child was already expanded there. Alias rule is `5·best ≥ 4·n` (≥ 80 %
  fails), duplicates reject all members across shapes, canonical programs and every witness
  are re-executed on the Rust executor. `tests/test_assembly_family.py`: 11 passed here
  (includes raw Rust enumeration to depth 4 vs the output-only screen on D625, and typed-stack
  checks on all three domains). I did not rerun the older composition tests.
- **Pair gate stability** (the gate that decides whether stage C runs). It is exhaustive and
  deterministic, so there is nothing to resample; I recomputed it on the smoke's D1331 screen
  with the alias cutoff moved. Retained counts and "no eligible pair" are unchanged for every
  cutoff from 0.75 to 0.82 (nearest agreements to 0.80 are 0.736 and 0.822); 0.85 adds 2 BT
  and 1 PA, still no pair; a pair (BT/PA) appears only at 0.90. At 0.70 PA drops to 4 and
  loses role coverage. So the gate is not sitting on its threshold on D1331. D625 and D2401
  are measured only by the proposal's unreviewed probe; the queue recomputes them. The screen
  is not truncated: depth 9 is the maximum meaningful depth for 10-token canonicals.
- **Arm wiring and seeds.** U/F/G/G-marg come from the vendored 2247 file with a file hash,
  per-table hashes and equality with `base_tables()`. Seeds 260601000+i are shared across
  cells and arms by design (paired; `search` uses separate streams for cases, init and
  variation); top-up, sampling, marginal and smoke seeds are disjoint from them. Stage C
  reuses the B seeds, so G/matched and swapped/matched are paired on 50 seeds even when F was
  topped up (contrasts intersect seeds).
- **Outcome logic.** Order U → 1 → 2 → 3 → 4/5 matches the plan; swapped/matched and
  G/matched ratios point the right way (> 1 means matched is faster); an interval spanning 1
  or any undefined bootstrap replicate gives U, not a row.
- **Deadline and size.** Work deadline 7 620 s, internal 7 800 s, timeout 9 000 s; one entry,
  2.5 h. Smoke rate (128 full-cap runs in 46.75 s on 8 workers) gives about 20 min for
  3 200 B runs. Machine has 32 GB against 4.7 GB measured peak for D1331, screens run one
  process at a time. Empty top-up lists return immediately.
- **Critique.** Notes 1–5 are answered in plan.md and reflected in code (block timing on the
  real roster, alias kinds and split failures separated, row 2 renamed, tied-marginal
  contrast reported, both-shape requirement for row 3, conditional cost projection). Notes
  6–7 are deferred to the steward with a stated reason (researcher cannot edit the digest).

## Minor notes (for the analysis, not blocking)

1. **The linear pair can never be eligible.** D1 and D2 each have exactly 3 cells with three
   distinct reducers; every other linear cell is an exact ≤ 9-token identity (`3x+z` via
   `DUP DUP ADD ADD`) or a duplicate (`2M+S+S` = `2S+M+M`). With the ≥ 4-cells rule, D1/D2
   fails by roster size on every domain. If row 1 is reached, report this as a split-rule
   failure, not as aliasing; `pairing.json` already separates the reasons.
2. **Stage C's "unresolved" rule is strict in one direction.** A shape contrast is unresolved
   if any of 2 000 bootstrap replicates has an arm under 50 % solves in any cell. A cell-arm
   solving about 70 % of 50 seeds will usually trigger this, and a swapped grammar that is
   censored on most seeds (the strongest possible contrast) also lands in U. This follows the
   plan and errs toward U; read `capped_time_ratio` and `defined_bootstrap_fraction` beside
   it. Stage C is unlikely to run at all.
3. **Top-up and stage C paths were not run end to end.** `--smoke` skips both; only
   `report()` is tested on synthetic stage C rows. The runner code for them is short and
   reads correctly.
4. **GA/BT/BE share one diagnostic table** (plan says so), and GA's canonical has
   `ADD → IF_GT`, which that table does not favour. A BT/BE pair would give identical
   matched and swapped arms, ratio exactly 1, outcome U.
5. **Block projections are recorded, not acted on.** The order is fixed (B, top-ups, C,
   sampling) and only the deadline cuts work. Fine at the measured rates.
6. Sampling submits 4 jobs per block to an 8-worker pool, so it uses half the workers
   (about 12 min for 10⁸ per arm at smoke throughput). The 48-case prefilter RNG seed
   260604999 equals the genotype seed of arm U chunk 999; harmless.
7. The projected `k` uses `summaries`' per-cell SD pooled as mean variance, as the plan
   states; the unused per-cell `k` field in `summaries` is the 2247 formula and should not be
   quoted.
