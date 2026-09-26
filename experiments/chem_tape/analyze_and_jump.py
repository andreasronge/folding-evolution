"""Analyze the and_jump sweep (map-bias notebook §3).

Per setup: solve rate and best fitness. For v3 runs that solved: walk the
best-of-generation genomes backwards from the solve and ask whether the jump was
"silent then switch on" — a domain computing sum>10 (or max>5) sitting behind a
silent linker before a linker mutation expressed it.

Usage: uv run python experiments/chem_tape/analyze_and_jump.py experiments/output/2026-09-26/and_jump
"""

from __future__ import annotations

import collections
import csv
import json
import sys
from pathlib import Path

import numpy as np
import yaml

from folding_evolution.chem_tape import alphabet as A
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.domains import LINKER_NAMES, SILENT, domain_values, split_domains
from folding_evolution.chem_tape.evaluate import _programs_for_arm
from folding_evolution.chem_tape.tasks import build_task

NAMES = {v: k for k, v in vars(A).items()
         if isinstance(v, int) and k.isupper() and not k.startswith(("N_", "RESERVED", "SLOT", "SEP", "SUM_"))}
NAMES.update({12: "SLOT12", 13: "SLOT13", 20: "|", 21: "|"})


def setup_name(c: dict) -> str:
    if c["arm"] == "V3":
        return "v3"
    if c.get("selection_mode") == "lexicase":
        return "lexicase"
    return "min" if c["alphabet"] == "v2_min" else "baseline"


def show(tokens, alphabet: str) -> str:
    names = dict(NAMES)
    if alphabet == "v2_min":
        names[22] = "MIN"
    return " ".join(names.get(int(t), str(t)) for t in tokens if int(t) != 0)


def domain_roles(genome: np.ndarray, task) -> list[tuple[str, str]]:
    """[(linker, role)] per domain; role = sum>10 / max>5 / const / other."""
    doms = split_domains(genome)
    if not doms:
        return []
    vals = domain_values([d for _, d in doms], task)
    mx = np.array([max(x) > 5 for x in task.inputs], dtype=np.int64)
    sm = np.array([sum(x) > 10 for x in task.inputs], dtype=np.int64)
    out = []
    for (linker, _), v in zip(doms, vals):
        role = ("AND" if (v == task.labels).all() else "sum>10" if (v == sm).all()
                else "max>5" if (v == mx).all() else "const" if (v == v[0]).all() else "other")
        out.append((LINKER_NAMES.get(linker, "start") if linker is not None else "start", role))
    return out


def trace_v3(run_dir: Path, cfg: ChemTapeConfig) -> dict:
    task = build_task(cfg, cfg.seed)
    rows = list(csv.DictReader(open(run_dir / "history.csv")))
    fits = [float(r["best_fitness"]) for r in rows]
    solve_gen = next(i for i, f in enumerate(fits) if f >= 0.999)
    genomes = [np.frombuffer(bytes.fromhex(r["best_genotype_hex"]), dtype=np.uint8) for r in rows]
    final = domain_roles(genomes[solve_gen], task)
    # Longest stretch before the solve during which the best genome carried a
    # silent sum>10 or max>5 domain.
    silent_since = None
    for g in range(solve_gen - 1, -1, -1):
        roles = domain_roles(genomes[g], task)
        if any(l == LINKER_NAMES[SILENT] and r in ("sum>10", "max>5") for l, r in roles):
            silent_since = g
        else:
            break
    return {"solve_gen": solve_gen, "final_domains": final,
            "silent_block_gens_before_jump": None if silent_since is None else solve_gen - silent_since,
            "pre_jump_fitness": fits[solve_gen - 1] if solve_gen else None,
            "pre_jump_domains": domain_roles(genomes[solve_gen - 1], task) if solve_gen else None}


def main(out_dir: str) -> None:
    out = Path(out_dir)
    index = json.loads((out / "sweep_index.json").read_text())
    by_setup: dict[str, list] = collections.defaultdict(list)
    for r in index:
        c = yaml.safe_load(open(Path(r["run_dir"]) / "config.yaml"))
        by_setup[setup_name(c)].append((r, c))

    lines = ["# AND-jump sweep", "",
             "| setup | solved | median best | median holdout (solved) | median solve gen |", "|---|---|---|---|---|"]
    for name in ("baseline", "min", "lexicase", "v3"):
        runs = by_setup.get(name, [])
        solved = [r for r, _ in runs if r["best_fitness"] >= 0.999]
        hold = [r["holdout_fitness"] for r in solved]
        gens = [r["generations_run"] for r in solved]
        lines.append(f"| {name} | {len(solved)}/{len(runs)} | {np.median([r['best_fitness'] for r, _ in runs]):.3f} | "
                     f"{np.median(hold) if hold else float('nan'):.3f} | {np.median(gens) if gens else '-'} |")

    for name in ("min", "lexicase", "baseline"):
        solved = [(r, c) for r, c in by_setup.get(name, []) if r["best_fitness"] >= 0.999]
        if solved:
            lines += ["", f"## {name}: solving programs", ""]
            for r, c in solved:
                cfg = ChemTapeConfig(**{k: v for k, v in c.items() if k in ChemTapeConfig.__dataclass_fields__})
                g = np.frombuffer(bytes.fromhex(r["best_genotype_hex"]), dtype=np.uint8)
                prog = _programs_for_arm(cfg, g.reshape(1, -1))[0]
                lines.append(f"- seed {c['seed']} (gen {r['generations_run']}): `{show(prog, c['alphabet'])}`")

    v3 = [(r, c) for r, c in by_setup.get("v3", []) if r["best_fitness"] >= 0.999]
    if v3:
        lines += ["", "## v3: how the jump happened", "",
                  "| seed | solve gen | fitness just before | domains just before | final domains | silent block carried for |",
                  "|---|---|---|---|---|---|"]
        for r, c in sorted(v3, key=lambda x: x[1]["seed"]):
            cfg = ChemTapeConfig(**{k: v for k, v in c.items() if k in ChemTapeConfig.__dataclass_fields__})
            t = trace_v3(Path(r["run_dir"]), cfg)
            fmt = lambda ds: " ".join(f"{l}:{ro}" for l, ro in ds) if ds else "-"
            sb = t["silent_block_gens_before_jump"]
            lines.append(f"| {c['seed']} | {t['solve_gen']} | {t['pre_jump_fitness']} | {fmt(t['pre_jump_domains'])} | "
                         f"{fmt(t['final_domains'])} | {'-' if sb is None else f'{sb} gens'} |")

    (out / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1])
