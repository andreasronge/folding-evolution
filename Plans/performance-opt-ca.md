# CA Performance Optimization — Plan

## Goal

Speed up `evaluate_population` for CA experiments without changing what it computes. Target: 2× wall-time improvement on the `ca_dynamic_budget` heavy shape (grid_n=32, steps=64, pop=256, examples=256). Stop as soon as that target is hit — further phases are optional.

**Correctness gate (non-negotiable):** every phase must produce bit-identical fitness trajectories given the same seed. CA math is integer, so "close enough" is not acceptable here — either the diff is zero or the phase reverts.

## Context — upcoming experiments (§11, §12 from `docs/ca/experiments.md`)

This plan was audited against the round-2 experiments that are queued or partially landed. §11.a (banded non-uniform CA) has already landed — `rule_banded.py` exists and the `banded_ot` family is in `CAConfig`. §11.b/c/d (phase schedules, radius, memory) are hypothesised but not yet landed. §12 (particle / space-time diagnostic) is a post-hoc analysis pass that needs trajectory capture.

Implications folded into the plan below:

- **Phase 1 dtype bound was radius-dependent; formula below replaces the `K=32` claim.**
- **Phase 4 payoff scales with table size; §11 variants inflate the table by 3×–16× → Phase 4 becomes more material, but gets more invasive to replicate per kernel.**
- **§12 needs a non-optimized `run_with_trace` path that the perf phases must not try to optimize.**
- **Sequencing: if any §11.b/c/d kernel lands before the perf work, prioritize `mx.compile` (kernel-agnostic) and pause Phase 4 until the kernel set stabilizes.**

## Bottlenecks — verified against source

All line references checked against current HEAD.

1. **No `mx.compile` on the step kernel.** `engine_mlx.py:89-91` runs a plain Python T-loop over `step()`. Wrapping with `mx.compile` lets MLX JIT and kernel-fuse the 8 shifts + gather + concat. Typically 2-5× on graph-heavy kernels like this on M1.
2. **Rule table broadcast-then-materialized across E.** `engine.py:28-30` copies the P rule tables E times into a contiguous P*E block. Same pattern for `input_clamp_pe` at `evaluate.py:36-37`. Alternative: keep `(P, K, S)` and index by `b // E` inside `step`.
3. **Dtype inflation to int32.** `engine_mlx.py:25, 56, 59` casts to int32. NumPy path already uses int16 (`engine_numpy.py:38`) — MLX is the outlier. NumPy indices at `engine_numpy.py:52-53` are int64; int32 is plenty.
4. **Row-0 clamp via `mx.concatenate` every step.** `engine_mlx.py:69` allocates a fresh `(B, N, N)` per call. `mx.where(row0_mask, clamp_broadcast, new_grid)` is cheaper and fuses better under `mx.compile`.
5. **Python `range(P)` loop in readout.** `evaluate.py:73-75, 87-90` calls `task.decode` once per population member. If decode is a pure lookup / threshold, one vectorized call over `(P, E, k)` replaces it.
6. **Per-genotype Python decode.** `engine.py:28` uses a list comprehension over `rule_mod.decode`. `rule_decision_tree` already has `decode_batch` (used at `engine.py:48`); `rule_banded.decode_batch` also exists. Add `rule_mod.decode_batch` for symmetry.
7. **Host↔device round-trip every generation.** `engine_mlx.py:92` forces device→host sync; readout runs in NumPy; next generation ships initial grids host→device. Keeping readout + fitness on MLX removes the sync.

## What NOT to change

- Current `(B, N, N)` layout — correct for the vectorized kernel.
- uint8 state — right dtype.
- Lazy `mx.eval` at end of run — don't eval per step.
- Shift-based neighbor sum — competitive with conv on MLX.

---

## Phase 0 — Baseline ✅ complete (commit `5377d84`)

Result summary (full numbers in `docs/perf_baseline.md`):

| Shape | End-to-end | CA loop share | decode+readout share | MLX vs NumPy | Peak mem |
|---|---:|---:|---:|---:|---:|
| small (16/16/P256/E64) | 63 ms | **99.2%** | 1.0% | 14× | 1.66 GB |
| heavy (32/64/P256/E256) | 3.76 s | **100%** | 0.02% | 11× | 2.18 GB |

**Phase-level implications:**
- Phase 2 (`mx.compile`) is the main event — CA loop is the whole wall time.
- Phase 1 (dtype) is near-free and the kernel is ~4 s at heavy; any bandwidth recovery shows up. Do first per the ordering note below.
- Phase 5 (readout vectorization) confirmed cosmetic (~0.5% at small, 0.02% at heavy). cProfile agrees — `_read_predictions` is ~7 ms over 10 heavy generations. **Skip unless a later phase changes the ratio.**
- Phase 6 (keep generation on device) also cosmetic — host↔device round-trip is dominated by the kernel itself. Skip.
- Phase 4 (E-broadcast) second priority — peak memory at heavy (2.18 GB) has headroom concerns for §11.d memory-depth=2 (16× table inflation). Revisit if §11.d lands.
- NumPy is confirmed non-competitive (11-14× slower). No backend-by-shape split needed.
- **Exit criterion is not triggered** on either shape (CA is far above 20% of end-to-end). Plan continues.

---

## Phase 0 — Methodology (for re-runs after each phase)

Every later phase is a hypothesis until measured. On M1/MLX the ranking changes with shape: at small P·E·N² Python overhead can dominate; at large shapes the CA step dominates. Don't land `mx.compile` or rearchitect the rule broadcast without a before/after number.

**Where:** `scripts/bench_ca.py` — self-contained benchmark harness using real `CAConfig` and the real pipeline. Not a test.

**Shapes:**
- *Small realistic:* grid_n=16, steps=16, n_states=4, pop=256, examples=64 (matches `CAConfig` defaults).
- *Heavy budget:* grid_n=32, steps=64, pop=256, examples=256 (matches `ca_dynamic_budget.yaml`).

**Instrumentation points** — each timed with `time.perf_counter()` and `mx.eval()` as a sync barrier:

1. End-to-end per generation (`evaluate_population` + one evolve step).
2. `evaluate_population` broken into three sub-timers: decode+broadcast (`engine.py:28-30`) / CA loop (`engine_*.run`) / readout (`_read_predictions`).
3. CA inner loop only — pre-materialize inputs, `mx.eval` before and after. Isolates the T-step kernel from host-side setup.
4. NumPy vs MLX at both shapes. If NumPy wins at small shapes, the answer is backend-by-shape, not optimize MLX.
5. cProfile over 10 generations — only if end-to-end is much slower than the CA loop alone (signal that Python overhead matters).

**Benchmark hygiene:**
- Run on AC power (thermal variance ~10% on M1 battery).
- 3 medians of 10 runs each; report the best median.
- Log `mx.metal.get_peak_memory()` alongside wall time — catches "faster but blows memory budget" regressions.
- cProfile caveat: wrap the timed region with `mx.eval(grid)` at both ends. MLX kernels run async; unsynchronized profiles blame the wrong line.

**Output:** `docs/perf_baseline.md` with the commit hash (per project convention). Every future change compares against it.

**Exit criteria for the whole plan (either triggers "close the plan"):**
1. Phase 0 shows the CA step is <20% of generation wall time at the shapes we run experiments on. The bottleneck is elsewhere (probably evolutionary loop or I/O) and belongs in a different plan.
2. A §11.b/c/d kernel lands before the perf work and changes `step` materially. Re-baseline against the new kernel before continuing.

---

## Phase 1 — Drop dtype inflation *(moved before compile)* ✅ complete (uncommitted)

**Result:** 1.93× faster on heavy, 2.41× faster on small. Peak memory roughly halved (2.18 GB → 1.05 GB at heavy). Bit-identical per `scripts/verify_correctness.py`. Full numbers: `docs/perf_baseline.md`.

**Change landed in `engine_mlx.py`:** `_neighbor_sum`, `step`, and `step_banded` now use `mx.int16` for the neighbor-sum accumulator, `self_idx`, and the index into `take_along_axis`. A spurious `flat_table.astype(mx.int32)` on the gather was removed (gather source can stay uint8; only indices need int). `step_banded`'s combined `band * K*(max_sum+1) + within` index is explicitly promoted to int32 — safe for any `n_bands × K × max_sum` we'd run.

**Dtype safety in the source**: int16 overflow would require `((2r+1)² − 1) · (K − 1) > 32767`. At r=1 that's K > 4096; at r=3 it's K > 683. Far above anything planned. Documented in `_neighbor_sum`'s docstring.

**Kernel is bandwidth-bound confirmed** — halving per-element width halved wall time almost linearly. This is diagnostic for Phase 2: `mx.compile` kernel fusion should recover additional bandwidth by reducing the number of read-then-write passes.

**Not touched** (intentional scope limit):
- NumPy path (`engine_numpy.py:52-53` int64 indices). NumPy is 11-14× slower than MLX — not the hot path; would be cosmetic.
- `step_dt` (decision-tree family). Not the default; bench didn't cover it. Can be a small follow-up.

---

## Phase 2 — `mx.compile` on `step`, `step_dt`, and `step_banded`

- Add `_step_compiled = mx.compile(step)` in `engine_mlx.py`. Same for `step_dt`. If `step_banded` has landed on MLX, wrap it too.
- Re-run bench immediately; commit if measurable win, revert if neutral.

**Risks:**
- `mx.compile` may reject the `mx.concatenate` for row-0 clamp. If it does, do Phase 3 first and return here.
- Dynamic shapes across generations could trigger recompile. Shapes are stable within a run (pinned by `cfg`), so this should be fine — verify by logging compile events during the first few generations.
- `mx.compile` caches per-signature — each variant (OT, DT, banded, future phase/radius/memory) compiles independently. That's fine; it's not a combinatorial cost.

**Gate:** only if CA-loop timing is ≥30% of generation time from Phase 0.

**Sequencing note:** Phase 2 is kernel-agnostic — a new §11 kernel landing after Phase 2 gets the same `mx.compile` treatment for the cost of one decorator. Prefer landing Phase 2 early, before the kernel zoo grows.

---

## Phase 3 — Row-0 clamp via `where`

Bundle with Phase 2 if `mx.compile` rejects `concatenate`.

- Precompute `row0_mask` of shape `(1, N, N)` once in `run`.
- Replace `mx.concatenate([clamped_row0, new_grid[:, 1:]])` with `mx.where(row0_mask, input_clamp_broadcast, new_grid)`.
- Minor on its own; material inside the T-step loop once fused with compile.

---

## Phase 4 — Eliminate E-broadcast of rule table and clamp

Biggest architectural change. Do last — only justified if Phases 1-3 aren't enough, or if an §11 variant has inflated the table enough that broadcast dominates memory.

- Kernel signature change: `step(grid, rule_table_P, input_clamp_E, E)` — rule indexed by `b // E`, clamp indexed by `b % E`.
- Touches `engine.py`, `engine_mlx.py`, `engine_numpy.py`, `evaluate.py`, and (if landed) `step_banded`.

**Critical caveat:** eliminating the broadcast changes the gather from "batch-local table" to "strided per-batch table". On Metal this can be *slower* due to less coalesced access, even though memory drops. Measure both variants. If gather slows more than the bandwidth savings, keep the broadcast and accept the ~6 MB cost (P=256, E=256, K=4).

**Why this scales with §11 variants:**
- §11.a banded (`n_bands=3`) already makes the table 3× at K=4 (300 bytes vs 100 per rule); per-row would be 16×.
- §11.c radius=3 makes the table ~2× (196 vs 100 bytes at K=4).
- §11.d memory-depth=2 makes the table 16× (1600 vs 100 bytes at K=4).
- At 16× inflation, broadcast-across-E hits ~100 MB. That's where Phase 4 moves from "measure and maybe skip" to "do it".

**Replication cost:** every kernel needs its own indexing path. If kernels churn during §11, don't land Phase 4 — it's the most code-invasive change. Defer until the kernel set stabilizes.

**Gate:** Phase 0 shows memory/bandwidth is the bottleneck, OR a high-inflation §11 variant has landed.

---

## Phase 5 — Vectorize readout + `rule.decode_batch` *(probably cosmetic)*

- Add `rule_mod.decode_batch(genotypes, K) -> (P, K, S)` mirroring `rule_decision_tree.decode_batch` and `rule_banded.decode_batch`.
- Rewrite `_read_predictions` to call `task.decode` once on the full `(P, E, k)` tensor instead of looping over P.

**Reality check:** Python decode for P=256 outer-totalistic is likely sub-millisecond — Phase 0 profiling will probably show this is cosmetic, not perf-critical. Ship only if cProfile flags it; otherwise skip and note as "verified non-issue" in `docs/perf_baseline.md`.

---

## Phase 6 — Keep generation on device (stretch)

Only if MLX↔NumPy handoff is measurable (Phase 0 instrumentation point 2 will show this).

- Move `_read_predictions` and fitness reduction into MLX.
- Requires `task.decode` on MLX.

**Per-task audit required before committing:** read `tasks.py` and classify each task's decode. Parity and majority currently share `_parity_decode` (threshold on cell state — trivial to vectorize on MLX). Future tasks may have Python branching; add a CPU fallback path rather than forcing every task onto MLX.

---

## §12 carve-out — `run_with_trace` for diagnostic use

§12 (particle / space-time analysis) needs trajectories `(T+1, N, N)`, not just the final grid. This is post-hoc best-of-run, B=1 typical — not on the hot path.

- Add `engine_mlx.run_with_trace(...)` (and NumPy mirror) returning `(T+1, B, N, N)`.
- **Do NOT wrap with `mx.compile`.** Trajectory capture inside a compiled loop breaks fusion — the append/collect forces host sync per step.
- None of Phases 1-6 should optimize `run_with_trace`. It's a separate path with different constraints.

---

## Workflow per phase

1. Re-run `bench_ca.py` on both shapes.
2. Update `docs/perf_baseline.md` with new numbers + commit hash.
3. Verify correctness: existing CA tests pass AND fitness trajectory is bit-identical to baseline for a fixed seed. If it drifts, revert.
4. Decide whether the next phase is worth it based on measured remaining headroom vs. the 2× target.

## Risks to watch

- `mx.compile` with data-dependent shapes may re-compile. Shapes are pinned per run, but log compile events in the first generations to confirm.
- Dropping contiguous copies from the P×E broadcast can silently change memory layout and invalidate downstream assumptions — check `_read_predictions` still sees expected shapes after Phase 4.
- Any change to rule-table layout breaks the `decision_tree` and `banded_ot` paths unless mirrored.
- Peak memory is as load-bearing as wall time — a 2× speedup that OOMs at experiment shapes is a regression.
- §11.b/c/d kernels may land during this work. Re-baseline; don't carry forward phase conclusions across a kernel change.
