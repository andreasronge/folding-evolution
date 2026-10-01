# Map-bias pivot, night 2: neutral drift, a frequency knob, random search at every budget

Status: planned 2026-10-01, from the sixteenth (Fable) review of night 1 (docs/map-bias/notebook.md
§27, findings item 17). Written as a hand-off: a coding agent should be able to implement, check,
run and write up from this file alone.

## Read first

- `CLAUDE.md` (project conventions; overnight queue runner).
- `Plans/map-bias-pivot.md` (night 1 design) and `docs/map-bias/notebook.md` §27 (night 1 results
  and the review) and `docs/map-bias/findings.md` item 17 + Open.
- `experiments/map_bias/fold_direct.py` (the only code file to change) and
  `experiments/map_bias/queue_pivot1.yaml` (queue format).
- Process: hobby project, light lab notebook. No pre-registration documents. Max two codex reviews
  before launch (`/codex review`), commit and push before launching.

## Why night 2

Night 1 (commit `cd7d463`) showed the folding map and direct encoding differ in behaviour bias and
folding solves more often where they differ. But:
1. The Phase B loop, copied from `exp_2x2.run_stable`, does (μ+λ) truncation with **parents first on
   fitness ties** (`fold_direct.py:187`, stable sort over `pop + kids`). An equal-fitness child never
   enters a population of plateau parents: 87–89% of unsolved final populations hold one behaviour.
   No neutral drift, so "arrival of the frequent" had no room to act, and runs froze on a deceptive
   plateau (`count(orders)`, fitness 0.593, under count∘rest(products)).
2. Evolution was no better than random search of the same budget (direct count∘rest(products):
   evolution 21–27/50 vs random search 45–46/50), and random search ran only at 200×1000.
3. "Solve rate follows P(exact)" is correlational: folding has the higher P(exact) on every task.

## Questions

- Q1 (drift): with ties broken at random (or offspring first), do populations stay diverse, do solve
  rates rise toward random-search levels, and does the fold/direct gap persist (→ frequency) or
  shrink (→ it was the plateau race)?
- Q2 (causal frequency): within one map, does raising/lowering how often the `rest` character
  appears — which changes P(exact) of count∘rest solvers without changing what is reachable — move
  solve rates in the same direction?
- Q3 (baseline): at every budget, is evolution better or worse than random search on each map?

## Code changes (all in `experiments/map_bias/fold_direct.py`)

Defaults must reproduce night 1 exactly (same RNG calls in the same order).

1. **Tie rule** `tie ∈ {"parents", "random", "offspring"}`, default `"parents"`.
   - `parents`: current code, unchanged.
   - `offspring`: build `allg, alls = kids + pop, ksc + sc` before the stable sort (children win
     ties).
   - `random`: sort key `(-fitness, u)` with `u` drawn from the run's `rng` per individual
     (`[rng.random() for _ in range(2 * pop_size)]`, drawn after scoring the kids).
   - Record `"tie"` in every result row; include it in the resume key in `cmd_evolve`.
2. **Frequency knob** `k_weight` (float, default 1.0): relative weight of the character `"k"`
   (`alphabet.py:69`, fn_fragment `rest`; it occurs once in the 62-character `ALPHABET`) in every
   character the experiment draws at random:
   - initial genotypes and random-search genotypes (`random_genotype`),
   - the replacement character of point mutation and the inserted character of insertion
     (`operators.py:15-29`, both `rng.choice(ALPHABET)`).
   Implement locally in `fold_direct.py` (don't change `src/`): `draw_char(rng, k_weight)` using
   `rng.choices(ALPHABET, weights)`; `rand_genotype(L, rng, k_weight)`; `mutate_w(g, rng, k_weight)`
   mirroring `operators.mutate` (choose point / insertion / deletion with `rng.choice` exactly as
   the original, then the weighted character draw). **When `k_weight == 1.0` call the original
   `random_genotype` / `operators.mutate`** so night-1 streams are untouched. Crossover is
   unaffected. Record `"k_weight"` per row and in the resume key.
   - P("k") per draw = w / (61 + w): 0.2× → 0.33%, 1× → 1.6%, 5× → 7.6%.
3. **Phase A knob:** `sample --k-weight W` writes `sample_{map}_L{L}_k{W}.json` when W ≠ 1 (keep
   the night-1 file names for W = 1). Use the same weighted `rand_genotype`.
4. **Record diversity:** add `"n_final_behaviours": len(final_beh)` (the full count, not just the
   top 20) and `"final_top_share"` to each row.
5. **CLI:** `evolve --tie ... --k-weights 0.2,5` (comma list; runs every weight given) and
   `sample --k-weight`. Keep `--random-budgets`.
6. **Analysis** (`analyze`, extend `phase_b` or add a function); it must accept several evolve
   directories (`--evolve DIR [DIR ...]`), including night 1's
   `experiments/output/2026-09-30/pivot_phase_b_L50` as the `tie=parents` arm (rows without a
   `tie` field are `parents`, without `k_weight` are 1.0). Tables:
   - **T1 drift check:** per (tie, map, budget): median `n_final_behaviours` and `final_top_share`
     in unsolved runs; median `best_len`.
   - **T2 solve rates:** per task × budget: solved/50 for fold and direct under each tie rule and
     under random search; McNemar on seed pairs fold vs direct within a tie rule; and per map
     evolution − random search (paired by seed: same task, budget, seed).
   - **T3 knob:** per map × task × budget: P(exact) at L0 for each k_weight (from the Phase A knob
     samples) next to the solve rate for each k_weight; within each (map, task, budget) report
     whether solve rate is monotone in P(exact) across the three weights, plus a logistic or
     Cochran-Armitage trend test across weights (pooled over seeds). Count(products) is the
     control task (the knob should not help it; it may hurt slightly by dilution).
   - Drop from the report: the d-difference steering table and the "at or above fitness" rank
     test (sixteenth review R5, R6).
   - The report must say PARTIAL if any input directory lacks its DONE marker (as now).

## Runs (queue `experiments/map_bias/queue_pivot2.yaml`, ~5 h on 10 cores)

All at start length 50, 50 seeds, tasks as night 1 unless stated.

| entry | what | runs | est. |
|---|---|---|---|
| `pivot2_phase_a_knob` | `sample --n 5000000 --lengths 50 --k-weight 0.2`, then `--k-weight 5` (two commands) | 4 groups × 5M | ~10 min |
| `pivot2_drift` | `evolve --tie random` and `--tie offspring`, budgets 50×300, 200×1000, all 11 tasks, both maps | 2 × 2 × 11 × 2 × 50 = 4,400 | ~1.5–2.5 h |
| `pivot2_knob` | `evolve --tie random --k-weights 0.2,5`, budgets 50×300, 200×1000, tasks count(rest(products)), count(rest(employees)), count(products) | 2 × 3 × 2 × 2 × 50 = 1,200 | ~30–45 min |
| `pivot2_random` | random search only: `--budgets` empty, `--random-budgets 50x300,500x2000`, all tasks | 2 × 11 × 2 × 50 = 2,200 | ~1–1.5 h |
| `pivot2_report` | `analyze` over night 1 Phase A + B (L50) and all night 2 directories | – | ~2 min |

Notes:
- The k = 1 arm of the knob is the `tie=random` arm of `pivot2_drift` (same seeds, same code path).
- `evolve` with no `--budgets` must be allowed (random-search-only entry).
- Each evolve entry writes to its own `$RUN_DIR`; the report references them as
  `"$RUN_DIR/../<id>"` and night 1 by absolute repo path.
- Timeouts: 3× the estimate. `evolve` resumes from `evolve.jsonl` if re-run.
- Drift may let genotypes grow faster (the 200-character cap stays); time a pilot first.

## Checks before launch (do all, record results in the notebook entry)

1. **Night-1 replay:** `evolve --tie parents` (k = 1) for 3 seeds of count(rest(products)) at
   50×300 and 200×1000 on both maps; `best_genotype` and `first_exact_gen` must equal the night-1
   rows in `experiments/output/2026-09-30/pivot_phase_b_L50/evolve.jsonl`.
2. **Knob sanity:** in 1M draws, the share of `"k"` matches w / (61 + w) for w = 0.2, 1, 5; at w = 1
   the code path is the original functions.
3. **Tie rules:** a tiny unit test (or assert script) where parents and kids tie: `parents` keeps
   parents, `offspring` keeps kids, `random` mixes them.
4. **Pilot timing:** 2 seeds × all tasks × both tie rules at 200×1000; scale the queue timeouts.
5. **End-to-end:** run `analyze` on the pilot outputs + night 1 and read every table.
6. `uv run python scripts/run_queue.py --queue experiments/map_bias/queue_pivot2.yaml --status
   experiments/map_bias/queue_pivot2.status.json --validate`.
7. Up to two codex reviews (fix P1s; fix P2s that would waste the night), then commit + push, then
   launch:
   `nohup caffeinate -s uv run python scripts/run_queue.py --queue experiments/map_bias/queue_pivot2.yaml --status experiments/map_bias/queue_pivot2.status.json --lock experiments/map_bias/queue_pivot2.lock > experiments/output/queue_pivot2.log 2>&1 &`
   and confirm the first entry finished and the second started.

## Reading the results

- **Q1.** Drift restored if unsolved populations hold many behaviours (T1). If solve rates rise to
  random-search levels and the fold/direct gap shrinks on count∘rest, night 1's gap was the plateau
  race; if the gap persists with drift, frequency (or another map property) still favours folding.
- **Q2 is the decisive test.** Solve rate rising with k_weight within a map on count∘rest (and not on
  count(products)) → frequency is causal, as chem-tape item 12. No trend → the frequency story for
  solve rates fails on this substrate; note it as a negative result.
- **Q3.** Report evolution − random search per map and budget. If evolution never beats random
  search with drift restored, these tasks are too easy/deceptive to study steering; next would be
  tasks with a gradient (or a different fitness than `partial_credit`).
- Steering (night 1 readout 2) is not re-run. Revisit only if drift is restored, with a per-arm
  test (endpoint frequency under its own map vs fitness-matched alternatives).

## Write-up (after the run)

- `docs/map-bias/notebook.md` §28: plan reference, commit hash, checks, tables T1–T3, take.
- `docs/map-bias/findings.md`: revise item 17 (scope every claim; commit hash in the header list),
  update Open.
- Ask for a Fable review of the write-up before promoting claims; commit and push.
