#!/usr/bin/env python3
"""Per-prereg diagnostic: confirm byte-for-byte canonical best-of-run across all
seeded (sf>0) runs for a sweep directory. Reports total, matches, and any
non-matching genotype hexes."""
from __future__ import annotations
import json
import sys
from pathlib import Path

import yaml

CANONICAL = "0201121008010510100708110000000000000000000000000000000000000000"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_canonical.py <sweep-dir>", file=sys.stderr)
        return 2
    sweep = Path(sys.argv[1])
    match = 0
    total_seeded = 0
    total = 0
    mismatches: list[tuple[str, str]] = []
    for d in sorted(sweep.iterdir()):
        if not d.is_dir():
            continue
        cfg_path = d / "config.yaml"
        res_path = d / "result.json"
        if not cfg_path.exists() or not res_path.exists():
            continue
        cfg = yaml.safe_load(cfg_path.read_text())
        res = json.loads(res_path.read_text())
        total += 1
        sf = float(cfg.get("seed_fraction", 0.0))
        if sf <= 0:
            continue
        total_seeded += 1
        hex_str = res.get("best_genotype_hex", "")
        if hex_str == CANONICAL:
            match += 1
        else:
            mismatches.append((d.name, hex_str))
    print(
        f"{sweep.name}: {match}/{total_seeded} seeded runs canonical "
        f"(of {total} total)"
    )
    for name, h in mismatches[:5]:
        print(f"  mismatch {name}: {h}")
    if len(mismatches) > 5:
        print(f"  ... {len(mismatches) - 5} more")
    return 0 if not mismatches else 1


if __name__ == "__main__":
    sys.exit(main())
