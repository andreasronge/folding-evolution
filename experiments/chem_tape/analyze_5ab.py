#!/usr/bin/env python3
"""Per-cell retention grid for §v2.4-proxy-5a (bp axis) and §v2.4-proxy-5b
(mutation_rate × arm axes). Thin wrapper around analyze_retention.analyze_run
that groups by axes the shared tool doesn't currently key on.

Usage:
    python experiments/chem_tape/analyze_5ab.py <absolute-sweep-dir> <group-spec>

where <group-spec> is one of:
    bp       — group by (bond_protection_ratio, seed_fraction)
    mr       — group by (arm, mutation_rate, seed_fraction)
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "experiments" / "chem_tape"))

from analyze_retention import (  # noqa: E402
    CANONICAL_AND_BODY_HEX,
    analyze_run,
    bootstrap_ci,
    hex_to_tape,
)


def collect(sweep_dir: Path) -> list[dict]:
    canonical = hex_to_tape(CANONICAL_AND_BODY_HEX)
    rows: list[dict] = []
    for d in sorted(sweep_dir.iterdir()):
        if not d.is_dir():
            continue
        r = analyze_run(d, canonical, "v2_probe")
        if r is None:
            continue
        cfg = yaml.safe_load((d / "config.yaml").read_text())
        r["bond_protection_ratio"] = float(cfg.get("bond_protection_ratio", 0.5))
        r["mutation_rate"] = float(cfg.get("mutation_rate", 0.03))
        rows.append(r)
    return rows


def summarize(rows: list[dict], keys: list[str]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        groups[tuple(r[k] for k in keys)].append(r)
    out: list[dict] = []
    for key, grp in sorted(groups.items()):
        r2d = np.array([r["R2_decoded"] for r in grp])
        r2a = np.array([r["R2_active"] for r in grp])
        r0d = np.array([r["R0_decoded"] for r in grp])
        rfit = np.array([r["R_fit_999"] for r in grp])
        uniq = np.array([r["unique_genotypes"] for r in grp])
        bfit = np.array([r["best_fitness"] for r in grp])
        fmean = np.array([r["final_generation_mean"] for r in grp])
        r2d_lo, r2d_hi = bootstrap_ci(r2d)
        r2a_lo, r2a_hi = bootstrap_ci(r2a)
        rfit_lo, rfit_hi = bootstrap_ci(rfit)
        solve = int(np.sum(bfit >= 0.999))
        cell = {k: v for k, v in zip(keys, key)}
        cell.update({
            "n_seeds": len(grp),
            "R2_decoded_mean": float(r2d.mean()),
            "R2_decoded_ci95": [r2d_lo, r2d_hi],
            "R2_active_mean": float(r2a.mean()),
            "R2_active_ci95": [r2a_lo, r2a_hi],
            "R0_decoded_mean": float(r0d.mean()),
            "R_fit_999_mean": float(rfit.mean()),
            "R_fit_999_ci95": [rfit_lo, rfit_hi],
            "unique_genotypes_mean": float(uniq.mean()),
            "final_mean_fitness_mean": float(fmean.mean()),
            "solve_count": solve,
        })
        out.append(cell)
    return out


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    sweep_dir = Path(sys.argv[1])
    spec = sys.argv[2]
    if not sweep_dir.exists():
        print(f"sweep dir missing: {sweep_dir}", file=sys.stderr)
        return 2

    rows = collect(sweep_dir)
    print(f"analyzed {len(rows)} run(s)")

    if spec == "bp":
        keys = ["bond_protection_ratio", "seed_fraction"]
    elif spec == "mr":
        keys = ["arm", "mutation_rate", "seed_fraction"]
    else:
        print(f"unknown group spec: {spec}", file=sys.stderr)
        return 2

    summary = summarize(rows, keys)
    out_path = sweep_dir / f"retention_grid_{spec}.json"
    out_path.write_text(json.dumps({"per_cell": summary, "keys": keys}, indent=2))
    print(f"  grid summary: {out_path}\n")

    for cell in summary:
        label = "  ".join(f"{k}={cell[k]}" for k in keys)
        print(
            f"  {label:<50s} n={cell['n_seeds']:>2} "
            f"R2d={cell['R2_decoded_mean']:.4f} "
            f"CI=[{cell['R2_decoded_ci95'][0]:.4f},{cell['R2_decoded_ci95'][1]:.4f}] "
            f"R2a={cell['R2_active_mean']:.4f} "
            f"R_fit={cell['R_fit_999_mean']:.3f} "
            f"uniq={cell['unique_genotypes_mean']:.1f} "
            f"fmean={cell['final_mean_fitness_mean']:.3f} "
            f"solve={cell['solve_count']}/{cell['n_seeds']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
