# Chem-tape top-K hot path, 2026-09-26

Representative setup: BP_TOPK, K=3, bond protection 0.5, `sum_gt_10_v2`,
v2_probe alphabet, 1024 tapes of length 32, 64 training examples, seed 0,
MLX backend, `RAYON_NUM_THREADS=1`. The native and fallback measurements below
were taken in the same working tree with the native functions toggled off for
the fallback. Each figure is the median of seven fixed-workload repetitions.

| Per-generation operation | Python/NumPy fallback | Native top-K | Speedup |
| --- | ---: | ---: | ---: |
| Population evaluation | 27.5 ms | 12.8 ms | 2.16× |
| Mutation over 1024 tapes | 28.0 ms | 4.2 ms | 6.60× |
| Reproduce and evaluate | 61.8 ms | 22.2 ms | 2.78× |

The native code scans each tape for runs, then ranks those runs by length. Population
decoding uses one Rust call for the full tape matrix. Protected mutation uses
one Rust call per child for the mask while retaining Python's `random.Random`
calls and their order. This preserves seeded evolutionary trajectories.

The optional prediction cache is **off by default**. In a 1500-generation
instrumented run, cache size 16384 reduced median Rust execution from 11.1 to
8.6 ms per generation, but median evaluation changed only from 13.9 to 13.4
ms and total wall time was effectively unchanged (about 35 s in both runs).
At the final generation, 21.7% of decoded programs had appeared earlier, and
97.8% of programs in the generation were unique. Enable the cache only when a
workload shows a stronger repeat rate, using
`run_evolution(cfg, prediction_cache_size=16384)`.

Reproduce the profile with:

```sh
RAYON_NUM_THREADS=1 uv run python benchmarks/chem_tape_profile.py --generations 500
RAYON_NUM_THREADS=1 uv run python benchmarks/chem_tape_profile.py --generations 500 --cache-size 16384
```

The decoder intentionally matches the current Python engine's run boundaries,
including its v2 behavior, so this is a performance change rather than a
decoder-semantics change.
