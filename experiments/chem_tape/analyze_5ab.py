#!/usr/bin/env python3
"""Per-cell retention grid for §v2.4-proxy-5* and §v2.5* sweeps. Thin
wrapper around analyze_retention.analyze_run that groups by axes the
shared tool's summarize_arm doesn't currently key on (summarize_arm only
groups by (arm, safe_pop_mode, seed_fraction)).

Usage:
    python experiments/chem_tape/analyze_5ab.py <absolute-sweep-dir> <group-spec> [--include-holdout]

where <group-spec> is one of:
    bp       — group by (bond_protection_ratio, seed_fraction)
    mr       — group by (arm, mutation_rate, seed_fraction)
    mr_gens  — group by (arm, mutation_rate, generations, seed_fraction)
               (§v2.4-proxy-5b-crosstask budget-decoupling cells)
    ts       — group by (tournament_size, seed_fraction)
               (§v2.4-proxy-5c-tournament-size axis)
    selmode  — group by (selection_mode, seed_fraction)
               (§v2.4-proxy-5c-nontournament axis)
    any:FIELD[,FIELD...]  — group by the comma-separated cfg fields + seed_fraction

--include-holdout: re-evaluate each final-population tape on the task's
holdout inputs and emit per-cell R_fit_holdout_999_mean + ci +
R_fit_holdout_mean_mean. Matches analyze_retention.py --include-holdout
semantics. Adds ~0.3-2 sec/run (batched via Rust executor).
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


def collect(sweep_dir: Path, include_holdout: bool = False) -> list[dict]:
    canonical = hex_to_tape(CANONICAL_AND_BODY_HEX)
    rows: list[dict] = []
    for d in sorted(sweep_dir.iterdir()):
        if not d.is_dir():
            continue
        r = analyze_run(d, canonical, "v2_probe", include_holdout=include_holdout)
        if r is None:
            continue
        cfg = yaml.safe_load((d / "config.yaml").read_text())
        # Attach every cfg field that a known group-spec may key on; default
        # values are preserved so absent fields don't break grouping.
        r["bond_protection_ratio"] = float(cfg.get("bond_protection_ratio", 0.5))
        r["mutation_rate"] = float(cfg.get("mutation_rate", 0.03))
        r["tournament_size"] = int(cfg.get("tournament_size", 3))
        r["generations"] = int(cfg.get("generations", 1500))
        r["selection_mode"] = str(cfg.get("selection_mode", "tournament"))
        r["_cfg_all"] = cfg  # retained so any:FIELD specs can key on arbitrary fields
        rows.append(r)
    return rows


def _get_key(row: dict, field: str):
    """Pull a grouping-key value from a row, falling back to the stashed
    _cfg_all dict when the field is an arbitrary cfg name for `any:` specs."""
    if field in row:
        return row[field]
    cfg = row.get("_cfg_all") or {}
    return cfg.get(field)


def summarize(rows: list[dict], keys: list[str]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        groups[tuple(_get_key(r, k) for k in keys)].append(r)
    out: list[dict] = []
    for key, grp in sorted(groups.items(), key=lambda kv: tuple(str(x) for x in kv[0])):
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
        # Holdout aggregation (only when --include-holdout was passed; rows
        # with None holdout are silently skipped for the aggregate).
        hfit_vals = [r.get("R_fit_holdout_999") for r in grp if r.get("R_fit_holdout_999") is not None]
        hmean_vals = [r.get("R_fit_holdout_mean") for r in grp if r.get("R_fit_holdout_mean") is not None]
        if hfit_vals:
            arr = np.array(hfit_vals)
            hf_lo, hf_hi = bootstrap_ci(arr)
            cell["R_fit_holdout_999_mean"] = float(arr.mean())
            cell["R_fit_holdout_999_ci95"] = [hf_lo, hf_hi]
            cell["R_fit_holdout_999_n"] = len(hfit_vals)
        if hmean_vals:
            cell["R_fit_holdout_mean_mean"] = float(np.mean(hmean_vals))
        out.append(cell)
    return out


def main() -> int:
    args = list(sys.argv[1:])
    include_holdout = "--include-holdout" in args
    if include_holdout:
        args.remove("--include-holdout")
    if len(args) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    sweep_dir = Path(args[0])
    spec = args[1]
    if not sweep_dir.exists():
        print(f"sweep dir missing: {sweep_dir}", file=sys.stderr)
        return 2

    if spec == "bp":
        keys = ["bond_protection_ratio", "seed_fraction"]
    elif spec == "mr":
        keys = ["arm", "mutation_rate", "seed_fraction"]
    elif spec == "mr_gens":
        keys = ["arm", "mutation_rate", "generations", "seed_fraction"]
    elif spec == "ts":
        keys = ["tournament_size", "seed_fraction"]
    elif spec == "selmode":
        keys = ["selection_mode", "seed_fraction"]
    elif spec.startswith("any:"):
        raw = spec[len("any:"):]
        keys = [f.strip() for f in raw.split(",") if f.strip()]
        if "seed_fraction" not in keys:
            keys.append("seed_fraction")
    else:
        print(f"unknown group spec: {spec}", file=sys.stderr)
        return 2

    rows = collect(sweep_dir, include_holdout=include_holdout)
    print(f"analyzed {len(rows)} run(s)" + (" (with holdout)" if include_holdout else ""))

    summary = summarize(rows, keys)
    out_path = sweep_dir / f"retention_grid_{spec.replace(':', '_').replace(',', '_')}.json"
    out_path.write_text(json.dumps(
        {"per_cell": summary, "keys": keys, "include_holdout": include_holdout},
        indent=2,
    ))
    print(f"  grid summary: {out_path}\n")

    for cell in summary:
        label = "  ".join(f"{k}={cell[k]}" for k in keys)
        hf = cell.get("R_fit_holdout_999_mean")
        hf_str = f" R_fit_hold={hf:.3f}" if hf is not None else ""
        print(
            f"  {label:<50s} n={cell['n_seeds']:>2} "
            f"R2d={cell['R2_decoded_mean']:.4f} "
            f"CI=[{cell['R2_decoded_ci95'][0]:.4f},{cell['R2_decoded_ci95'][1]:.4f}] "
            f"R2a={cell['R2_active_mean']:.4f} "
            f"R_fit={cell['R_fit_999_mean']:.3f}"
            f"{hf_str} "
            f"uniq={cell['unique_genotypes_mean']:.1f} "
            f"fmean={cell['final_mean_fitness_mean']:.3f} "
            f"solve={cell['solve_count']}/{cell['n_seeds']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
