# Chem-tape sweep performance — optimize & measure

## Context

The 14-entry v2 nightly run took **140 min wall time** at `cpu_efficiency=3.78/4` (4 workers near-fully saturated, but no more). Total user CPU was 528.8 min. `§v2.4` compute-scaling follow-ups are 45–75 min each — iteration is bottlenecked by this.

Root causes (from reading `evaluate.py:86`, `chem_tape.rs:419`, `evolve.py:96–110`, `engine_mlx.py`):

- **PyO3 crossings are the dominant cost.** `rust_chem_execute_batch` is batched over examples (E), not individuals (P). `evaluate.py:98` loops `for p in range(P)` → **~1.5M Python↔Rust crossings per seed** (P=1024 × G=1500).
- **Mutation is per-cell Python RNG.** `evolve.py:96–110` does `for i in range(L): if rng.random() < rate:` → 49M scalar `rng.random()` calls per seed.
- **MLX is a no-op for v2 sweeps.** `engine_mlx.py` explicitly delegates BP_TOPK to NumPy (comment: "does not benefit from MLX parallelism at the batch shapes this experiment uses"). All v2 experiments use BP_TOPK. The GPU is not the lever.
- **4 workers / 10 cores.** 8 perf + 2 efficiency cores available; only 4 in use.

Intended outcome: **3–5× total wall-time reduction on v2 sweeps** while preserving correctness and same-seed determinism. The MLX/GPU backend is NOT the lever — leave it in place for arms B/BP but don't try to make it help BP_TOPK.

## Phased approach

Three independent wins, landed in ascending-risk order. Each phase has its own verification and can be stopped after if the measured speedup is sufficient.

---

### Phase 1 — Worker + Rayon topology (trivial, zero code risk)

**Original plan:** bump `queue.yaml` workers 4 → 8, assuming Rayon would stay at default.

**Shipped config (revised after isolated measurement):** `queue.yaml` workers 4 → 10, AND `scripts/run_queue.py` pins `RAYON_NUM_THREADS=1` per child. The original 8-worker estimate left performance on the table because each Python worker was spawning its own num_cpus-wide Rayon pool inside the Rust executor, oversubscribing the cores. Pinning Rayon to 1 per worker lets the outer Pool provide the parallelism cleanly, and with that change 10 workers is better than 8.

**Isolated measurements** on `v2_1_partA_fixed_baseline.yaml` (20 seeds, pop=1024, gens=1500) — each knob turned alone on top of the previous:

| config | wall | speedup | notes |
|---|---|---|---|
| workers=4, default Rayon | 267.0s | 1.00× | baseline |
| workers=8, default Rayon | 194.7s | 1.37× | cpu_eff jumped 2.82→4.03; Rayon-in-Rust caps effective cores at ~4 |
| workers=8 + pop-batch, default Rayon | 187.0s | 1.43× | pop-batch adds only 4% at sweep level — Rayon still oversubscribing |
| workers=8 + pop-batch + RAYON=1 | 175.9s | 1.52× | pinning Rayon unlocks 6% more; workers now truly independent |
| **workers=10 + pop-batch + RAYON=1** (shipped) | **155.2s** | **1.72×** | 2 more workers = 14% more because cores are now 1:1 with workers |
| workers=20 + pop-batch + RAYON=1 | 148.2s | 1.80× | only +5% more for 2× process count — not worth the memory |

Rollout is 10, not 8, because the empirical data justifies it after the RAYON=1 pin. Rows appended to `benchmarks/chem_tape_results.csv` with `phase=sweep-*` for the audit trail.

**Why not go past 10:** The 20-worker test returned only +5% over 10 at 2× process count. On a 10-core machine (8 perf + 2 efficiency) with RAYON=1, 10 workers is the natural 1:1 ceiling; more just pays scheduling overhead.

**Risk check before editing:**
- `experiments/chem_tape/sweep.py:75` — `--workers` only feeds `mp.Pool(n)`; nothing seed-derived. Safe.
- Queue `timeout_seconds` are all ≥1800s with per-entry budgets ~20–30 min — faster wall strictly better.
- `RAYON_NUM_THREADS=1` in `run_queue.py` affects queue-launched children only; direct `uv run python run.py <cfg>` invocations are unaffected. Queue-driven single-worker runs (`--workers 1`) lose Rayon parallelism — acceptable since the queue's whole purpose is outer-pool parallelism; single-worker use is an edge case for debugging.

**Verification (done):**
- Workers=8 and workers=10 configs each produced bitwise-identical `sweep_index.json` vs the workers=4 baseline (20/20 configs match on `best_fitness`, `best_genotype_hex`, `final_generation_best`, `final_generation_mean`).

---

### Phase 2 — Population-batch Rust executor (biggest per-seed win)

**Add a new PyO3 function** `rust_chem_execute_pop_batch` in `rust/src/chem_tape.rs`, registered in `rust/src/lib.rs:223`. Signature mirrors the existing `rust_chem_execute_batch` at `chem_tape.rs:419` but takes `Vec<Vec<u8>>` programs and returns a **flat `Vec<i64>` of length P×E** (Python reshapes to `(P, E)` in one allocation — measurably cheaper than `Vec<Vec<i64>>` at P=1024).

**Design details** (validated by planning review):
- Convert `input_values` (`&Bound<'_, PyList>`) to `Vec<Value>` **once, under the GIL, before the par_iter**. `Value` is owned (`Int`/`IntList`/`Str`/`CharList`) — `Send + Sync`. No `Arc`/`Mutex` needed.
- Parallelize on programs axis (P≈1024), serial on inputs (E≤256). **Do not nest `par_iter`** — oversubscribes rayon at this shape.
- Wrap the compute in `py.allow_threads(|| { ... })`. Resolve `slot_fn`, `threshold`, `alphabet` once before the par_iter.
- Reuse `execute_inner` and `ExecCtx` unchanged — this is a pure dispatch-layer addition.
- Mirror the `rayon::prelude::*` + `par_iter()` pattern already in `rust/src/lib.rs:68` (`rust_develop_batch`) and `lib.rs:144` (`rust_develop_and_score_batch`). Rayon is already a dep in `rust/Cargo.toml:12`; no build-system change.

**Python call-site change:** `src/folding_evolution/chem_tape/evaluate.py:97–106` — when the new symbol is available, call once with all programs and reshape; fall through to the existing per-individual loop otherwise (and to pure-Python under `not _HAS_RUST_EXECUTOR`). Keep all three paths for fallback and testing.

**Critical files:**
- `rust/src/chem_tape.rs` — new `rust_chem_execute_pop_batch`
- `rust/src/lib.rs:223` — register the new pyfunction
- `src/folding_evolution/chem_tape/evaluate.py:86–109` — call site guarded by `_HAS_POP_BATCH`

**Expected speedup:** 3–5× on `evaluate_population`, which dominates per-generation cost. At the full-seed level, expect 2.5–4× before any Phase-1 worker scaling stacks on top.

**Verification:**
1. **New differential test** `tests/test_chem_tape_pop_batch_differential.py` (existing differential tests at `tests/test_chem_tape_executor_differential.py` and `tests/test_chem_tape_v2_executor_differential.py` cover single-call `rust_chem_execute` only — not `rust_chem_execute_batch` and not the new pop-batch; there's a latent gap we're filling). Assert:
   - **Rust-internal equivalence:** `pop_batch(programs)` equals `[[rust_chem_execute(p, inputs[e]) for e in E] for p in programs]` across N=64 random programs × M=16 inputs, v1 and v2_probe alphabets. Reuse the random-program generator from the existing differential files.
   - **Python↔Rust parity on a smaller shape** (N=8, M=4): pop_batch equals `[[py_execute(p, inp) for inp in inputs] for p in programs]`.
2. **End-to-end property test** at the `evaluate_population` layer: one seeded evolution run with `_HAS_POP_BATCH=True` vs `_HAS_POP_BATCH=False` (patched) — assert `np.array_equal` on `predictions` and `fitnesses`. This is the highest-value check — guarantees no user-visible change.
3. Run existing reproducibility test `tests/test_chem_tape_reproducibility.py` to confirm seeded determinism is preserved.

---

### Phase 3 — Vectorized batched mutation (invasive; breaks historical trajectory parity)

**Scope is larger than "just vectorize mutate" — explicit callout.** The bond-protection mask in `evolve.py:84–94` is computed on the **child tape post-crossover pre-mutation**, which today is produced one individual at a time inside `_reproduce_one_island`. To batch the mask (a hard prereq for vectorized mutation), `_reproduce_one_island` must be refactored to:

1. Batch-sample parent index pairs (P pairs, via `np.random.Generator`).
2. Batch-generate children: one `(P, L)` uint8 array via gather + single-point crossover cuts (also vectorizable).
3. Call `compute_topk_runnable_mask(children, k)` ONCE on the full `(P, L)` child tape.
4. Build `(P, L)` mutation-rate matrix from the mask (cells in mask → `rate * bond_protection_ratio`, others → `rate`).
5. Vectorized flip + resample:
   ```python
   flip = gen_np.random((P, L)) < rate_matrix
   fresh = gen_np.integers(0, hi + 1, size=(P, L), dtype=np.uint8)
   pop = np.where(flip, fresh, pop)
   ```

**`evolve_k=True` subtlety:** K is per-individual. To keep vectorization, group rows by `k_per_ind` into buckets, compute `compute_topk_runnable_mask` once per bucket (few distinct K values), scatter back. Don't fall back to a per-row loop inside the batched path.

**RNG migration — what changes, and what "determinism is preserved" actually means:**

Previous drafts of this plan framed Phase 3 as "only the mutation RNG stream diverges" — that framing was wrong and has been fixed here. What's actually happening:

- A `np.random.Generator` derived from `cfg.seed` joins the existing `random.Random` in `run_evolution`. The NumPy generator drives **all three** vectorized operations: parent-index sampling (step 1), crossover cut selection (step 2), and the flip+resample of mutation (step 5). This is wider than "just mutation."
- `random.Random` stays in place for `random_genotype` (population initialization, executed once at gen 0) and for `_migrate` sampling. Tournament selection and the crossover-vs-clone decision move into the NumPy stream along with crossover cuts.
- The two RNG streams are independent bit streams; draw counts don't interleave across them.

**Divergence from pre-Phase-3 trajectories is NOT isolated to mutation.** Once parent pairs and crossover cuts come from a different bit stream, the child population diverges from gen 1. From there, the mask computed over those children diverges, fitness diverges, the next generation's tournament winners diverge, migration source/destination sets diverge — the whole trajectory is a fresh chain from gen 1 onward. There is no substring of generations that stays bit-identical. The "Python RNG stays in phase" line in earlier drafts was a half-truth: the call *counts* stayed in phase because mutation no longer consumes them, but the *state* those calls operate on (populations, fitnesses, indices) had already forked by the time they ran.

**What determinism survives:**
- **Same-seed runs produce identical results** within Phase-3 code (`tests/test_chem_tape_reproducibility.py` contract holds). Running Phase-3 twice at `cfg.seed=13` gives bit-identical best_fitness, best_genotype, and full history.
- **Bitwise trajectories do NOT carry over from pre-Phase-3 runs.** Historical `result.json` fitness curves cannot be replayed bit-for-bit. This is a cost paid per-seed, and it applies to EVERY generation, not just mutation outputs.
- **Distributional equivalence across the refactor is an empirical question**, not a mathematical guarantee. Phase-3 verification must include a KS-test (or similar) on `best_fitness` distributions over ≥8 seeds before and after the refactor, to confirm the new RNG topology doesn't accidentally shift the evolutionary dynamics. This was in the plan already; this framing makes it load-bearing, not optional.

**Acceptable cost, but must be explicit:**
- Commit message for Phase 3 must state "bitwise trajectory parity with pre-Phase-3 result.json files is intentionally broken; same-seed determinism within Phase-3 preserved; distributional equivalence verified via KS-test."
- Any downstream analysis that reads historical `result.json` files with the expectation of bitwise reproducibility must be flagged before the Phase-3 commit lands.

**Critical files:**
- `src/folding_evolution/chem_tape/evolve.py:96–110` (`mutate`), `evolve.py:160–186` (`_reproduce_one_island`), `evolve.py:~288/419` (`rng` construction sites)

**Expected speedup:** 1.3–1.5× on total per-generation wall time. Higher share after Phase 2 because `evaluate_population` will no longer dominate — Amdahl pushes mutation's relative share up.

**Verification:**
1. `tests/test_chem_tape_reproducibility.py` — same-seed → same best fitness, best genotype, full history. Must pass.
2. Existing smoke test `tests/test_chem_tape_evolve_smoke.py` — end-to-end evolution, must pass.
3. **Add a one-off equivalence test against the pre-refactor mutate** (scoped to this PR only, not kept in the suite): snapshot a population + seed before refactor, snapshot the post-mutate population; confirm the distribution of flip rate matches expectation (statistical, not bitwise — different RNG stream).
4. Re-run one short sweep config (see measurement harness below) before/after — assert `best_fitness` distributions across seeds are statistically indistinguishable (KS test, n=8 seeds). This is the real check that the refactor preserves evolutionary behavior.

---

## Measurement harness

**Do not extend `benchmarks/regression.py`** — it benches the non-chem-tape `develop`/`evaluate_multi_target` pipeline and shares no hot path with chem-tape (`benchmarks/regression.py:63–100`).

**New file:** `benchmarks/chem_tape_regression.py`. One entry point that runs a fixed bench config and appends to `benchmarks/chem_tape_results.csv`.

**Bench config (one in-file config, not a YAML):**
```
pop_size=1024, generations=50, seeds=2 (seed=[0,1]),
arm=BP_TOPK, alphabet=v2_probe, task=sum_gt_10_v2,
tape_length=32, bond_protection_ratio=0.5, topk=3,
workers=1  (isolate from Phase 1)
```

This is ~3% of a real sweep entry, runs in ~30 s, exercises every v2 hot path. Reduced gens (50 vs 1500) because we're measuring per-generation throughput, not a real evolutionary outcome.

**Measured columns (median of 5 runs per column):**
- `pop_eval_sec` — wall time of `evaluate_population(pop, task, cfg)` alone
- `mutate_sec` — wall time of full-population mutation (extract from inside `_reproduce_one_island`)
- `gen_total_sec` — one full generation (reproduce + evaluate)
- `pyo3_crossings_per_gen` — Phase 2 drops this from 1024 to 1
- `git_hash`, `timestamp`, `phase` (baseline / phase1 / phase2 / phase3)

**Phase 1 (worker scaling) is measured differently** — `/usr/bin/time -l` on a real sweep entry (e.g. `v2_1_partA_fixed_baseline.yaml`) with `--workers 4` vs `--workers 8`. Not the micro-bench.

## Non-goals (explicit)

- **Don't remove MLX.** It's inactive for v2 arms but may still help non-BP_TOPK arms; leave the delegation in place.
- **Don't try to GPU-accelerate the stack-machine executor.** Branch-heavy divergent work; wrong shape for Metal.
- **Don't replace `random.Random` globally.** Minimal migration (mutation only) is enough and lowest-risk.
- **Don't bump workers past 8** without a measurement — thermal throttling and the 2 efficiency cores give diminishing returns.

## Sequencing summary

| Phase | Risk | Est. speedup | Reproducibility impact | Lands in |
|-------|------|--------------|------------------------|----------|
| 1. Workers 4→8 | ~none | 1.6–1.8× | none | minutes |
| 2. Pop-batch Rust | low (pure additive) | 2.5–4× | none (same-seed bitwise) | half a day |
| 3. Vectorized mutation | medium (refactor) | 1.3–1.5× | historical trajectories diverge | 1 day |

**Stacked estimate:** 140 min → 20–30 min nightly. **User can stop after Phase 2** and skip Phase 3 if historical-trajectory parity is worth keeping — P1+P2 alone should hit ~5–7× on total wall time.

## Verification — end-to-end

After each phase:

1. **Unit & parity:** `uv run pytest tests/test_chem_tape_*.py` (existing differential + new pop-batch differential for Phase 2).
2. **Reproducibility:** `uv run pytest tests/test_chem_tape_reproducibility.py`.
3. **Micro-bench:** `uv run python benchmarks/chem_tape_regression.py` — append row; compare to previous git-hash row.
4. **End-to-end smoke:** run `v2_2_fixed_baselines.yaml` (36 s at baseline → should be ~5–15 s stacked). Compare `sweep_index.json` for equivalence — for Phase 1/2 bitwise; for Phase 3 same-seed `best_fitness` distributional equivalence.
5. **Full overnight:** queue the whole nightly once all phases land; compare total wall to the 140-min baseline.

## Critical files (touch list)

- `rust/src/chem_tape.rs` — new `rust_chem_execute_pop_batch` (Phase 2)
- `rust/src/lib.rs:223` — register new pyfunction (Phase 2)
- `src/folding_evolution/chem_tape/evaluate.py:86–109` — call-site switch to pop-batch (Phase 2)
- `src/folding_evolution/chem_tape/evolve.py:96–110, ~160–186, ~288, ~419` — vectorized mutation + batched reproduce (Phase 3)
- `queue.yaml` (14 lines) — `--workers 4` → `--workers 8` (Phase 1)
- `tests/test_chem_tape_pop_batch_differential.py` — new test (Phase 2)
- `benchmarks/chem_tape_regression.py` — new bench harness (all phases)
