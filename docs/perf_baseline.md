# CA Performance Baseline

Host: `macOS-26.3.1-arm64-arm-64bit-Mach-O` · MLX `0.31.1`

All times are seconds, best-of-3 medians of 10 runs after 2 warmups.
Peak memory is MLX peak across the measured region, in MB.
Bench source: `scripts/bench_ca.py`.

## Summary across phases

| Shape | Phase 0 (commit `5377d84`) | Phase 1 (int32→int16, uncommitted) | Δ wall | Δ peak mem |
|---|---:|---:|---:|---:|
| small (16/16/P256/E64) | 0.0630 s, 1662.8 MB | **0.0261 s, 717.0 MB** | **2.41× faster** | 2.32× lower |
| heavy (32/64/P256/E256) | 3.7629 s, 2184.4 MB | **1.9505 s, 1049.9 MB** | **1.93× faster** | 2.08× lower |

Target (from `Plans/performance-opt-ca.md`): 2× on heavy. **Phase 1 alone hits 1.93× — within rounding of the bar.** Phase 2 (`mx.compile`) is still the headline phase per the plan and should push further.

Correctness gate: fitness/predictions SHA-256 fingerprints (`scripts/verify_correctness.py`) are bit-identical between Phase 0 and Phase 1.

- small  `fit_sha=fd9919e5c18f4545  pred_sha=3d27dc9d1be848f5`
- heavy  `fit_sha=e118cb36fb1f41a6  pred_sha=45cea333a1782be0`

---

## Phase 0 — baseline (commit `5377d84`)

### small — grid_n=16 steps=16 n_states=4 pop_size=256 n_examples=64

| Measurement | Wall (s) | Peak mem (MB) | Share of end-to-end |
|---|---:|---:|---:|
| End-to-end (evaluate+argsort) | 0.0630 | 1662.8 | 100% |
|  └ decode + broadcast (host) | 0.0003 | — | 0.5% |
|  └ CA loop (engine_mlx.run) | 0.0625 | — | 99.2% |
|  └ readout (_read_predictions) | 0.0003 | — | 0.5% |
| CA kernel only — MLX (no setup, no D→H) | 0.0619 | — | 98.4% |
| CA kernel only — NumPy | 0.8845 | — | ratio MLX/NP 0.07× |

### heavy — grid_n=32 steps=64 n_states=4 pop_size=256 n_examples=256

| Measurement | Wall (s) | Peak mem (MB) | Share of end-to-end |
|---|---:|---:|---:|
| End-to-end (evaluate+argsort) | 3.7629 | 2184.4 | 100% |
|  └ decode + broadcast (host) | 0.0006 | — | 0.0% |
|  └ CA loop (engine_mlx.run) | 3.7644 | — | 100.0% |
|  └ readout (_read_predictions) | 0.0006 | — | 0.0% |
| CA kernel only — MLX (no setup, no D→H) | 3.8406 | — | 102.1% |
| CA kernel only — NumPy | 41.3052 | — | ratio MLX/NP 0.09× |

### cProfile takeaways (heavy shape, 10 generations)

- `engine_mlx.run` = 38.69 s of 38.72 s total (~99.9%). CA step fully dominates.
- `_read_predictions` = 0.009 s over 10 generations. Readout is irrelevant.
- Decode / broadcast / stack / reshape together = ~0.04 s. Irrelevant.

Phase 5 (readout vectorize) and Phase 6 (on-device readout) are **cosmetic**. Skip.

---

## Phase 1 — drop int32 inflation to int16 (uncommitted)

**Change:** `engine_mlx.py` — `_neighbor_sum`, `step`, `step_banded` cast `mx.int32` → `mx.int16` on the neighbor-sum accumulator, `self_idx`, and the linear index used by `take_along_axis`. Also removed a spurious `flat_table.astype(mx.int32)` on the gather — `take_along_axis` only needs integer *indices*, the source can stay uint8.

**Dtype safety check:** with int16 as the accumulator, overflow would require `((2r+1)² − 1) · (K − 1) > 32767`. At r=1 that's K > 4096; at r=3 (48 neighbors) it's K > 683. Every planned experiment is far below.

For `step_banded` the combined `band * K*(max_sum+1) + within` index *could* exceed int16 at large `n_bands × K × max_sum`, so that single multiply is promoted to int32 explicitly. Within-band index stays int16.

### small — grid_n=16 steps=16 n_states=4 pop_size=256 n_examples=64

| Measurement | Wall (s) | Peak mem (MB) | Share of end-to-end |
|---|---:|---:|---:|
| End-to-end (evaluate+argsort) | 0.0261 | 717.0 | 100% |
|  └ decode + broadcast (host) | 0.0003 | — | 1.2% |
|  └ CA loop (engine_mlx.run) | 0.0254 | — | 97.5% |
|  └ readout (_read_predictions) | 0.0003 | — | 1.3% |
| CA kernel only — MLX (no setup, no D→H) | 0.0253 | — | 97.0% |
| CA kernel only — NumPy | 0.8920 | — | ratio MLX/NP 0.03× |

### heavy — grid_n=32 steps=64 n_states=4 pop_size=256 n_examples=256

| Measurement | Wall (s) | Peak mem (MB) | Share of end-to-end |
|---|---:|---:|---:|
| End-to-end (evaluate+argsort) | 1.9505 | 1049.9 | 100% |
|  └ decode + broadcast (host) | 0.0006 | — | 0.0% |
|  └ CA loop (engine_mlx.run) | 1.9482 | — | 99.9% |
|  └ readout (_read_predictions) | 0.0006 | — | 0.0% |
| CA kernel only — MLX (no setup, no D→H) | 1.9438 | — | 99.7% |
| CA kernel only — NumPy | 41.2428 | — | ratio MLX/NP 0.05× |

### Interpretation

Kernel is bandwidth-bound — halving the per-step integer width halves the bus traffic, and wall time dropped accordingly. NumPy times are unchanged (NumPy path wasn't modified in Phase 1), which is why the MLX/NP ratio looks more favorable post-Phase-1.

CA loop still owns 97-100% of wall time, so Phase 2 (`mx.compile`) is still the next lever.

---

## Re-run checklist (for the next phase)

1. `.venv/bin/python scripts/verify_correctness.py > /tmp/fp_before.txt` (pre-change)
2. Implement the phase.
3. `.venv/bin/python scripts/verify_correctness.py > /tmp/fp_after.txt` — `diff` must be empty.
4. `.venv/bin/python scripts/bench_ca.py --shapes all` to regenerate numbers.
5. Hand-edit this doc to append the new phase section and update the summary table.
