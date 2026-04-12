"""CA performance benchmark harness — Phase 0 baseline for Plans/performance-opt-ca.md.

Runs five instrumentation points across two shape regimes (small realistic and
heavy budget) and writes a markdown summary anchored to the current git commit.

Usage:
    python scripts/bench_ca.py                       # both shapes, write docs/perf_baseline.md
    python scripts/bench_ca.py --shapes small        # single shape
    python scripts/bench_ca.py --no-write            # stdout only, don't touch docs/
    python scripts/bench_ca.py --cprofile            # also run cProfile for 10 generations
"""

from __future__ import annotations

import argparse
import cProfile
import io
import pstats
import random
import statistics
import subprocess
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

import mlx.core as mx

from folding_evolution.ca import engine_mlx, engine_numpy, rule as rule_mod
from folding_evolution.ca.config import CAConfig
from folding_evolution.ca.evaluate import _read_predictions, evaluate_population
from folding_evolution.ca.tasks import build_task
from folding_evolution.ca import rule as ca_rule


# ---------------- Shape regimes ----------------

SHAPES: dict[str, CAConfig] = {
    "small": CAConfig(
        grid_n=16, steps=16, n_states=4,
        pop_size=256, n_examples=64,
        task="parity", n_bits=8,
        backend="mlx",
    ),
    "heavy": CAConfig(
        grid_n=32, steps=64, n_states=4,
        pop_size=256, n_examples=256,
        task="parity", n_bits=8,
        backend="mlx",
    ),
}


# ---------------- Timing helpers ----------------

def _mlx_sync():
    """Force MLX to flush pending work. Cheap no-op value as sync barrier."""
    mx.eval(mx.array(0))


def _peak_memory_mb() -> float | None:
    """Return MLX peak memory in MB, or None if unavailable."""
    for attr_chain in (("get_peak_memory",), ("metal", "get_peak_memory")):
        obj = mx
        try:
            for a in attr_chain:
                obj = getattr(obj, a)
            return obj() / 1e6
        except AttributeError:
            continue
        except Exception:
            return None
    return None


def _reset_peak_memory() -> None:
    for attr_chain in (("reset_peak_memory",), ("metal", "reset_peak_memory")):
        obj = mx
        try:
            for a in attr_chain:
                obj = getattr(obj, a)
            obj()
            return
        except AttributeError:
            continue
        except Exception:
            return


def best_of_medians(fn, warmup: int = 2, n_runs: int = 10, n_medians: int = 3) -> float:
    """Best of `n_medians` medians of `n_runs` runs (after warmup).

    Best-of-medians reduces thermal / scheduler variance on Apple Silicon.
    """
    for _ in range(warmup):
        fn()
    medians = []
    for _ in range(n_medians):
        times = []
        for _ in range(n_runs):
            t0 = time.perf_counter()
            fn()
            t1 = time.perf_counter()
            times.append(t1 - t0)
        medians.append(statistics.median(times))
    return min(medians)


# ---------------- Shared setup ----------------

def build_pop_and_task(cfg: CAConfig):
    rng = random.Random(cfg.seed)
    pop = [ca_rule.random_genotype_for(cfg, rng) for _ in range(cfg.pop_size)]
    task = build_task(cfg, seed=cfg.seed)
    return pop, task


def materialize_inputs(cfg: CAConfig, pop, task):
    """Produce (initial_grid, tables_be, clamp_pe) on host. Mirrors engine._run_outer_totalistic."""
    P = len(pop)
    E = task.inputs.shape[0]
    N = cfg.grid_n

    tables = np.stack([rule_mod.decode(g, cfg.n_states) for g in pop], axis=0)
    tables_be = np.broadcast_to(tables[:, None, :, :], (P, E, *tables.shape[1:]))
    tables_be = np.ascontiguousarray(tables_be).reshape(P * E, *tables.shape[1:])

    clamp_e = task.encode(task.inputs, cfg).astype(np.uint8)
    clamp_pe = np.broadcast_to(clamp_e[None, :, :], (P, E, N))
    clamp_pe = np.ascontiguousarray(clamp_pe).reshape(P * E, N)

    initial_grid = np.zeros((P * E, N, N), dtype=np.uint8)
    return initial_grid, tables_be, clamp_pe


# ---------------- Instrumentation points ----------------

def bench_end_to_end(cfg: CAConfig) -> tuple[float, float | None]:
    """(1) One full evaluate_population + one argsort (proxy for selection)."""
    pop, task = build_pop_and_task(cfg)
    _reset_peak_memory()

    def run():
        fitnesses, _ = evaluate_population(pop, task, cfg)
        _mlx_sync()
        np.argsort(-fitnesses)

    t = best_of_medians(run)
    return t, _peak_memory_mb()


def bench_evaluate_subtimers(cfg: CAConfig) -> tuple[float, float, float]:
    """(2) Decode+broadcast / CA loop (backend=mlx) / readout — timed separately."""
    pop, task = build_pop_and_task(cfg)
    P = len(pop)
    E = task.inputs.shape[0]
    N = cfg.grid_n

    # Sub-timer A: decode + broadcast rule tables + input clamp (host-side setup).
    clamp_e = task.encode(task.inputs, cfg).astype(np.uint8)

    def decode_broadcast():
        tables = np.stack([rule_mod.decode(g, cfg.n_states) for g in pop], axis=0)
        tables_be = np.broadcast_to(tables[:, None, :, :], (P, E, *tables.shape[1:]))
        np.ascontiguousarray(tables_be).reshape(P * E, *tables.shape[1:])
        clamp_pe = np.broadcast_to(clamp_e[None, :, :], (P, E, N))
        np.ascontiguousarray(clamp_pe).reshape(P * E, N)

    t_decode = best_of_medians(decode_broadcast)

    # Pre-materialize for sub-timers B and C.
    initial_grid, tables_be, clamp_pe = materialize_inputs(cfg, pop, task)

    # Sub-timer B: CA loop (includes host→device, T-step kernel, device→host).
    def ca_loop():
        engine_mlx.run(initial_grid, tables_be, clamp_pe, cfg.steps)

    t_ca = best_of_medians(ca_loop)

    # Sub-timer C: readout. Uses a single materialized final grid to isolate decode work.
    final = engine_mlx.run(initial_grid, tables_be, clamp_pe, cfg.steps)

    def readout():
        _read_predictions(final, cfg, task, P, E)

    t_readout = best_of_medians(readout)
    return t_decode, t_ca, t_readout


def bench_ca_inner(cfg: CAConfig, backend: str) -> float:
    """(3) CA inner loop only, pre-materialized inputs, explicit MLX sync barriers.

    NumPy at heavy shapes is ~minute-per-run; bail out after a single probe
    instead of the full best-of-3×10 protocol.
    """
    pop, task = build_pop_and_task(cfg)
    initial_grid, tables_be, clamp_pe = materialize_inputs(cfg, pop, task)

    if backend == "mlx":
        init_mx = mx.array(initial_grid)
        tab_mx = mx.array(tables_be)
        clamp_mx = mx.array(clamp_pe)
        _mlx_sync()

        def run():
            grid = init_mx
            clamped_row0 = clamp_mx.reshape(grid.shape[0], 1, cfg.grid_n)
            grid = mx.concatenate([clamped_row0, grid[:, 1:, :]], axis=1)
            for _ in range(cfg.steps):
                grid = engine_mlx.step(grid, tab_mx, clamp_mx)
            mx.eval(grid)

        return best_of_medians(run)

    # NumPy: adaptive run count. Probe once; scale reps based on single-run cost.
    def run_np():
        engine_numpy.run(initial_grid, tables_be, clamp_pe, cfg.steps)

    t0 = time.perf_counter()
    run_np()
    probe = time.perf_counter() - t0

    # Budget ~20 seconds total for the NumPy measurement.
    if probe > 5.0:
        return probe  # single probe is the measurement
    if probe > 1.0:
        return best_of_medians(run_np, warmup=0, n_runs=3, n_medians=1)
    return best_of_medians(run_np, warmup=1, n_runs=5, n_medians=2)


def bench_cprofile(cfg: CAConfig, n_generations: int = 10) -> str:
    """(5) cProfile over `n_generations` back-to-back evaluate_population calls.

    Wraps the timed region with _mlx_sync() at both ends — MLX async work would
    otherwise be blamed on the wrong line.
    """
    pop, task = build_pop_and_task(cfg)

    profiler = cProfile.Profile()
    _mlx_sync()
    profiler.enable()
    for _ in range(n_generations):
        evaluate_population(pop, task, cfg)
        _mlx_sync()
    profiler.disable()

    buf = io.StringIO()
    stats = pstats.Stats(profiler, stream=buf).sort_stats("cumulative")
    stats.print_stats(20)
    return buf.getvalue()


# ---------------- Orchestration ----------------

def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=Path(__file__).resolve().parent.parent,
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def format_report(results: dict) -> str:
    """Format all shape results into the markdown that goes into docs/perf_baseline.md."""
    lines = [
        "# CA Performance Baseline",
        "",
        f"Commit: `{results['commit']}`",
        f"Host: `{results['host']}`",
        f"MLX version: `{results.get('mlx_version', 'unknown')}`",
        "",
        "All times are seconds, best-of-3 medians of 10 runs after 2 warmups.",
        "Peak memory is MLX Metal peak across the measured region, in MB.",
        "",
    ]

    for shape_name, r in results["shapes"].items():
        cfg: CAConfig = r["cfg"]
        lines.extend([
            f"## {shape_name} — {cfg.grid_n=} {cfg.steps=} {cfg.n_states=} {cfg.pop_size=} {cfg.n_examples=}",
            "",
            "| Measurement | Wall (s) | Peak mem (MB) | Share of end-to-end |",
            "|---|---:|---:|---:|",
        ])
        e2e_t = r["end_to_end"][0]
        e2e_mem = r["end_to_end"][1]
        lines.append(f"| End-to-end (evaluate+argsort) | {e2e_t:.4f} | {_fmt_mem(e2e_mem)} | 100% |")

        t_decode, t_ca, t_readout = r["evaluate_subtimers"]
        lines.append(f"|  └ decode + broadcast (host) | {t_decode:.4f} | — | {100*t_decode/e2e_t:.1f}% |")
        lines.append(f"|  └ CA loop (engine_mlx.run) | {t_ca:.4f} | — | {100*t_ca/e2e_t:.1f}% |")
        lines.append(f"|  └ readout (_read_predictions) | {t_readout:.4f} | — | {100*t_readout/e2e_t:.1f}% |")

        t_inner_mlx = r["ca_inner_mlx"]
        lines.append(f"| CA kernel only — MLX (no setup, no D→H) | {t_inner_mlx:.4f} | — | {100*t_inner_mlx/e2e_t:.1f}% |")

        t_inner_np = r.get("ca_inner_numpy")
        if t_inner_np is not None:
            lines.append(f"| CA kernel only — NumPy | {t_inner_np:.4f} | — | {100*t_inner_np/e2e_t:.1f}% (ratio MLX/NP {t_inner_mlx/t_inner_np:.2f}×) |")

        lines.append("")

        share = t_ca / e2e_t
        if share < 0.20:
            lines.append(f"> **Exit criterion triggered:** CA loop is {100*share:.1f}% of end-to-end — below 20% threshold. Per plan, close and address the evolutionary / host overhead instead.")
        elif share < 0.30:
            lines.append(f"> **Phase 2 (`mx.compile`) gate:** CA loop is {100*share:.1f}% of end-to-end — below the 30% gate threshold. Phase 2 payoff likely small; consider skipping.")
        else:
            lines.append(f"> CA loop is {100*share:.1f}% of end-to-end — above 30% gate; Phase 2 justified.")
        lines.append("")

        if r.get("cprofile"):
            lines.extend([
                "### cProfile (10 generations, `evaluate_population` + `mx.eval`)",
                "",
                "```",
                r["cprofile"].rstrip(),
                "```",
                "",
            ])

    return "\n".join(lines) + "\n"


def _fmt_mem(m: float | None) -> str:
    return f"{m:.1f}" if m is not None else "—"


def run_shape(shape_name: str, cfg: CAConfig, include_cprofile: bool) -> dict:
    print(f"\n[{shape_name}] cfg: grid={cfg.grid_n} T={cfg.steps} K={cfg.n_states} "
          f"P={cfg.pop_size} E={cfg.n_examples} task={cfg.task} n_bits={cfg.n_bits}")

    print(f"  (1) end-to-end …", flush=True)
    e2e = bench_end_to_end(cfg)
    print(f"      {e2e[0]*1000:.1f} ms   peak_mem={_fmt_mem(e2e[1])} MB")

    print(f"  (2) evaluate sub-timers …", flush=True)
    subs = bench_evaluate_subtimers(cfg)
    print(f"      decode+broadcast={subs[0]*1000:.1f} ms  ca_loop={subs[1]*1000:.1f} ms  readout={subs[2]*1000:.1f} ms")

    print(f"  (3) CA kernel only (MLX) …", flush=True)
    t_inner_mlx = bench_ca_inner(cfg, "mlx")
    print(f"      {t_inner_mlx*1000:.1f} ms")

    print(f"  (4) CA kernel only (NumPy) …", flush=True)
    t_inner_np = bench_ca_inner(cfg, "numpy")
    print(f"      {t_inner_np*1000:.1f} ms   (ratio MLX/NP {t_inner_mlx/t_inner_np:.2f}×)")

    result = {
        "cfg": cfg,
        "end_to_end": e2e,
        "evaluate_subtimers": subs,
        "ca_inner_mlx": t_inner_mlx,
        "ca_inner_numpy": t_inner_np,
    }

    if include_cprofile:
        print(f"  (5) cProfile over 10 generations …", flush=True)
        result["cprofile"] = bench_cprofile(cfg, n_generations=10)

    return result


def main():
    import platform

    parser = argparse.ArgumentParser(description="CA perf benchmark harness")
    parser.add_argument("--shapes", nargs="+", choices=list(SHAPES) + ["all"], default=["all"])
    parser.add_argument("--no-write", action="store_true", help="don't write docs/perf_baseline.md")
    parser.add_argument("--cprofile", action="store_true", help="include cProfile pass (slow)")
    parser.add_argument("--out", default=None, help="output markdown path (default: docs/perf_baseline.md)")
    args = parser.parse_args()

    shapes_to_run = list(SHAPES) if args.shapes == ["all"] else args.shapes

    try:
        mlx_version = mx.__version__
    except AttributeError:
        mlx_version = "unknown"

    results = {
        "commit": git_commit(),
        "host": platform.platform(),
        "mlx_version": mlx_version,
        "shapes": {},
    }

    for name in shapes_to_run:
        results["shapes"][name] = run_shape(name, SHAPES[name], include_cprofile=args.cprofile)

    report = format_report(results)
    print("\n" + "=" * 72)
    print(report)

    if not args.no_write:
        out_path = Path(args.out) if args.out else Path(__file__).resolve().parent.parent / "docs" / "perf_baseline.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report)
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
