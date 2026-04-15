#!/usr/bin/env python3
"""Assembly-difficulty metrics (ADI) for chem-tape v2 sweeps.

Quantifies the "components present but full body not assembled" gap —
the dynamic signature of epistatic assembly difficulty that the
§v2.6 Pair 1 attractor inspection surfaced. See methodology §21.

For each sweep, for each seed:
  * components_present: does the winner's raw tape contain ALL required
    tokens for the task's canonical body? (designer-defined; see
    REQUIRED_COMPONENTS below)
  * behavioral_solve: does the winner score ≥ 0.999 on BOTH tasks in
    the alternation pair (from result.json's cross_task_fitness)? For
    single-task sweeps, just ≥ 0.999 on the one task.

Per-sweep summary:
  n                        = total seeds
  component_pass           = # seeds with all required components on tape
  behavioral_solve         = # seeds that BOTH-solve
  assembly_gap             = component_pass − behavioral_solve
                             (positive ⇒ components present, chain absent)
  ADI                      = assembly_gap / n
                             (fraction of seeds stuck at assembly barrier)

Interpretation:
  ADI ≈ 0.0 with solve=n     Clean scale — mechanism works, no barrier.
  ADI ≈ 0.0 with solve=0     Components absent — mechanism may not apply here.
  ADI > 0.3                  Significant assembly barrier. Compute-scaling
                             is the first test; decoder variation is the
                             second (principle 21).
  ADI swamp-risk note        If behavioral_solve = n, ADI=0 regardless
                             of component_pass. Swamped pairs produce
                             uninformative ADI (cf. §v2.6 Pair 2/3
                             baseline completion). ADI is meaningful
                             only when the pair is non-swamped.

Usage:
    python experiments/chem_tape/assembly_metrics.py <sweep_name>
    python experiments/chem_tape/assembly_metrics.py --all
    python experiments/chem_tape/assembly_metrics.py --all --write-json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from folding_evolution.chem_tape import alphabet as alph  # noqa: E402

OUTPUT_ROOT = REPO_ROOT / "experiments" / "chem_tape" / "output"
SOLVE_EPS = 0.999

# Per-task canonical body components — the token set that MUST appear on a
# winner's tape for "components present" to be true. This is the designer's
# canonical decomposition; behavioral_solve is the ground-truth check that
# doesn't depend on this. The gap between them is ADI's numerator.
REQUIRED_COMPONENTS: dict[str, set[int]] = {
    # §v2.3 sum-slot (4-token body: INPUT SUM THRESHOLD_SLOT GT)
    "sum_gt_5_slot":  {alph.INPUT, alph.SUM, alph.THRESHOLD_SLOT, alph.GT},
    "sum_gt_10_slot": {alph.INPUT, alph.SUM, alph.THRESHOLD_SLOT, alph.GT},
    # §v2.6 Pair 1 (6-token body: INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT)
    "any_char_count_gt_1_slot":
        {alph.INPUT, alph.CHARS, alph.SLOT_12, alph.SUM, alph.THRESHOLD_SLOT, alph.GT},
    "any_char_count_gt_3_slot":
        {alph.INPUT, alph.CHARS, alph.SLOT_12, alph.SUM, alph.THRESHOLD_SLOT, alph.GT},
    # §v2.6 Pair 2 (4-token, wider range)
    "sum_gt_7_slot_r12":  {alph.INPUT, alph.SUM, alph.THRESHOLD_SLOT, alph.GT},
    "sum_gt_13_slot_r12": {alph.INPUT, alph.SUM, alph.THRESHOLD_SLOT, alph.GT},
    # §v2.6 Pair 3 (4-token, aggregator slot_13 = REDUCE_MAX)
    "reduce_max_gt_5_slot":
        {alph.INPUT, alph.SLOT_13, alph.THRESHOLD_SLOT, alph.GT},
    "reduce_max_gt_7_slot":
        {alph.INPUT, alph.SLOT_13, alph.THRESHOLD_SLOT, alph.GT},
    # §v2.4 and §v2.4-alt compositional AND bodies
    # (IF_GT + CONST_0 + REDUCE_MAX + CONST_5 + GT + INPUT + SUM + THRESHOLD_SLOT)
    "compound_and_sum_gt_5_max_gt_5_slot":
        {alph.CONST_0, alph.INPUT, alph.REDUCE_MAX, alph.CONST_5,
         alph.SUM, alph.THRESHOLD_SLOT, alph.GT, alph.IF_GT},
    "compound_and_sum_gt_10_max_gt_5_slot":
        {alph.CONST_0, alph.INPUT, alph.REDUCE_MAX, alph.CONST_5,
         alph.SUM, alph.THRESHOLD_SLOT, alph.GT, alph.IF_GT},
    "sum_gt_10_AND_max_gt_5":
        {alph.CONST_0, alph.INPUT, alph.REDUCE_MAX, alph.CONST_5,
         alph.SUM, alph.GT, alph.IF_GT},
    "sum_gt_10_AND_max_gt_5_decorr":
        {alph.CONST_0, alph.INPUT, alph.REDUCE_MAX, alph.CONST_5,
         alph.SUM, alph.GT, alph.IF_GT},
}


def hex_to_tape(hex_str: str) -> np.ndarray:
    return np.frombuffer(bytes.fromhex(hex_str), dtype=np.uint8)


def compute_per_seed(result: dict) -> dict | None:
    """Compute component-present + behavioral-solve for one result.json."""
    task = result["task"]
    req = REQUIRED_COMPONENTS.get(task)
    if req is None:
        return None
    tape = hex_to_tape(result["best_genotype_hex"])
    token_set = set(int(t) for t in tape.tolist())
    components_present = req.issubset(token_set)
    cross = result.get("cross_task_fitness")
    if cross:
        behavioral_solve = all(
            v["fitness"] >= SOLVE_EPS for v in cross.values()
        )
        task_names = sorted(cross.keys())
    else:
        behavioral_solve = result["best_fitness"] >= SOLVE_EPS
        task_names = [task]
    return {
        "seed": result["seed"],
        "task_fallback": task,
        "components_present": components_present,
        "behavioral_solve": behavioral_solve,
        "required_components": sorted(TOKEN_NAMES[t] for t in req),
        "missing_components": sorted(
            TOKEN_NAMES[t] for t in req if t not in token_set
        ),
        "tasks_in_alt": task_names,
    }


def analyse_sweep(sweep: str) -> dict:
    sw_dir = OUTPUT_ROOT / sweep
    rows = []
    for d in sorted(sw_dir.iterdir()):
        rp = d / "result.json"
        if not rp.exists():
            continue
        r = json.loads(rp.read_text())
        per = compute_per_seed(r)
        if per is None:
            # Unknown task — skip, log below
            rows.append({"seed": r.get("seed"), "task": r.get("task"), "skipped": True})
            continue
        rows.append(per)

    scored = [r for r in rows if not r.get("skipped")]
    n = len(scored)
    comp_pass = sum(1 for r in scored if r["components_present"])
    solved = sum(1 for r in scored if r["behavioral_solve"])
    gap = comp_pass - solved
    adi = gap / n if n > 0 else 0.0

    # Informativeness flag: ADI is uninformative when every seed solves
    # (swamp) or no seeds have all components (mechanism likely absent).
    if n == 0:
        verdict = "empty"
    elif solved == n:
        verdict = "swamped (ADI=0 by construction; pair is ceiling-saturated)"
    elif comp_pass == 0:
        verdict = "components-absent (mechanism may not apply; low ADI uninformative)"
    elif adi >= 0.3:
        verdict = "high assembly barrier (compute-scaling or decoder-variation is the next test)"
    elif adi > 0.0:
        verdict = "mild assembly barrier"
    else:
        verdict = "clean scale (no barrier observed)"

    return {
        "sweep": sweep,
        "n": n,
        "components_present": comp_pass,
        "behavioral_solve": solved,
        "assembly_gap": gap,
        "ADI": adi,
        "verdict": verdict,
        "per_seed": scored,
        "skipped": [r for r in rows if r.get("skipped")],
    }


# Build TOKEN_NAMES from alphabet module (mirrors decode_winner.py).
TOKEN_NAMES = {
    alph.NOP: "NOP", alph.INPUT: "INPUT", alph.CONST_0: "CONST_0",
    alph.CONST_1: "CONST_1", alph.CHARS: "CHARS", alph.SUM: "SUM",
    alph.ANY: "ANY", alph.ADD: "ADD", alph.GT: "GT", alph.DUP: "DUP",
    alph.SWAP: "SWAP", alph.REDUCE_ADD: "REDUCE_ADD", alph.SLOT_12: "SLOT_12",
    alph.SLOT_13: "SLOT_13", alph.MAP_EQ_E: "MAP_EQ_E", alph.CONST_2: "CONST_2",
    alph.CONST_5: "CONST_5", alph.IF_GT: "IF_GT", alph.REDUCE_MAX: "REDUCE_MAX",
    alph.THRESHOLD_SLOT: "THRESHOLD_SLOT", alph.SEP_A: "SEP_A", alph.SEP_B: "SEP_B",
}


V2_SWEEPS = [
    "v2_3",
    "v2_4_alt", "v2_4_proxy",
    "v2_6_pair1", "v2_6_pair2", "v2_6_pair3",
    "v2_6_pair1_scale",  # runs later; present here for auto-discovery
]


def print_summary(s: dict) -> None:
    sweep = s["sweep"]
    print(f"\n=== {sweep}  n={s['n']} ===")
    print(f"  components present : {s['components_present']:>2}/{s['n']}")
    print(f"  behavioral solve   : {s['behavioral_solve']:>2}/{s['n']}")
    print(f"  assembly gap       : {s['assembly_gap']:>2}/{s['n']}   ADI = {s['ADI']:.3f}")
    print(f"  verdict            : {s['verdict']}")
    if s["skipped"]:
        print(f"  skipped (unknown task): {len(s['skipped'])}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sweep", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--write-json", action="store_true", help="write adi.json per sweep")
    args = ap.parse_args()

    targets = V2_SWEEPS if args.all else ([args.sweep] if args.sweep else [])
    if not targets:
        ap.error("provide sweep name or --all")

    print(f"\n{'SWEEP':22s}  {'n':>3}  {'comp':>4}  {'solve':>5}  {'gap':>3}  {'ADI':>5}  verdict")
    all_s: list[dict] = []
    for sw in targets:
        sw_dir = OUTPUT_ROOT / sw
        if not sw_dir.exists():
            print(f"  skip: {sw} (no output dir)")
            continue
        s = analyse_sweep(sw)
        all_s.append(s)
        print(f"  {sw:20s}  {s['n']:>3}  {s['components_present']:>4}  "
              f"{s['behavioral_solve']:>5}  {s['assembly_gap']:>3}  {s['ADI']:>5.2f}  {s['verdict']}")
        if args.write_json:
            (sw_dir / "adi.json").write_text(json.dumps(s, indent=2))

    # If --all, print the full per-sweep summary afterward for detail.
    if args.all and all_s:
        print()
        for s in all_s:
            print_summary(s)

    return 0


if __name__ == "__main__":
    sys.exit(main())
