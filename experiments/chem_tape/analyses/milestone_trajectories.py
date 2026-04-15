#!/usr/bin/env python3
"""§v2.7 milestone-trajectory analysis.

Reads per-generation `best_genotype_hex` from history.csv across §v2.3 and
§v2.6 Pair 1 fixed-task sweeps, classifies each best-of-pop into milestones
{none, partial, near-canonical, canonical} per the pre-registered
token-set definition (Plans/prereg_pair1-transitions.md §"Milestone
definitions"), and computes:

  * Per-seed first-generation at each milestone (t_none/partial/near/canonical)
  * Per-seed residence time in each milestone
  * Per-seed transition rate R_seed = #(*→canonical transitions) / #(gens below canonical)
  * CONTROL-DEGENERATE row trigger on §v2.3 (sum_gt_5_slot):
      sum_gt_5_slot first-canonical-set gen < 20 for ≥ 10/20 seeds,
      OR average gens-below-canonical on §v2.3 < 50

Outputs:
  * Printed per-task summary with key numbers + CONTROL-DEGENERATE verdict
  * CSV of per-(seed, task, generation, milestone) — stored next to
    experiments/chem_tape/output/v2_7_milestones/milestones.csv

Strict vs permissive classification:
  strict   = canonical token must appear on the tape (exact IDs).
             For Pair 1: {INPUT, CHARS, SLOT_12, SUM, THRESHOLD_SLOT, GT}.
             For §v2.3:  {INPUT, SUM, THRESHOLD_SLOT, GT}.
  permissive (for Pair 1 only) = SLOT_12 OR MAP_EQ_E counts as the map-op slot
             (sibling-token tolerance per the prereg's §v2.4-alt-style
             alternative-assembly acknowledgment).

Usage:
    uv run python experiments/chem_tape/analyses/milestone_trajectories.py
"""

from __future__ import annotations

import csv
import json
import statistics
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from folding_evolution.chem_tape import alphabet as alph

V23_ROOT = REPO_ROOT / "experiments" / "output" / "2026-04-14" / "v2_3_fixed_baselines"
V26_ROOT = REPO_ROOT / "experiments" / "output" / "2026-04-15" / "v2_6_fixed_baselines"
OUT_DIR = REPO_ROOT / "experiments" / "chem_tape" / "output" / "v2_7_milestones"

# Canonical token sets (strict IDs on tape). SLOT_12 is the generic slot-12
# token; the task alphabet binds it to MAP_EQ_R at execution time.
CANONICAL_STRICT: dict[str, set[int]] = {
    "any_char_count_gt_1_slot": {
        alph.INPUT, alph.CHARS, alph.SLOT_12, alph.SUM, alph.THRESHOLD_SLOT, alph.GT,
    },
    "any_char_count_gt_3_slot": {
        alph.INPUT, alph.CHARS, alph.SLOT_12, alph.SUM, alph.THRESHOLD_SLOT, alph.GT,
    },
    "sum_gt_5_slot": {
        alph.INPUT, alph.SUM, alph.THRESHOLD_SLOT, alph.GT,
    },
    "sum_gt_10_slot": {
        alph.INPUT, alph.SUM, alph.THRESHOLD_SLOT, alph.GT,
    },
}

# Permissive variant: for Pair 1, accept SLOT_12 OR MAP_EQ_E as the "map-op" slot.
# §v2.3 is unaffected (no ambiguous op slot in its canonical body).
PERMISSIVE_SUBSTITUTES: dict[str, dict[int, set[int]]] = {
    "any_char_count_gt_1_slot": {alph.SLOT_12: {alph.SLOT_12, alph.MAP_EQ_E}},
    "any_char_count_gt_3_slot": {alph.SLOT_12: {alph.SLOT_12, alph.MAP_EQ_E}},
}

SIZES: dict[str, int] = {
    "any_char_count_gt_1_slot": 6,
    "any_char_count_gt_3_slot": 6,
    "sum_gt_5_slot": 4,
    "sum_gt_10_slot": 4,
}


def hex_to_tape(hex_str: str) -> np.ndarray:
    return np.frombuffer(bytes.fromhex(hex_str), dtype=np.uint8)


def extract_bp_topk_tokenset(tape: np.ndarray) -> set[int]:
    """Approximate BP_TOPK(k=3) extracted-program token-set.

    Strictly correct BP_TOPK extraction requires the top-K longest permeable
    runs; for the milestone CLASSIFIER the token-SET (not order) is what
    matters. We use the raw tape token set excluding NOP (0), SEP_A (20),
    and SEP_B (21). This is a superset of the BP_TOPK extraction, which is
    the correct direction for a "tokens present on tape" classifier: if a
    canonical token isn't in the raw tape, it certainly isn't in the
    extracted program. A token being in the raw tape but not extracted is
    captured by the separate COMP vs solve diagnostic (`assembly_metrics.py`).
    """
    s = {int(t) for t in tape.tolist()}
    s.discard(alph.NOP)
    s.discard(alph.SEP_A)
    s.discard(alph.SEP_B)
    return s


def classify_milestone(
    tokenset: set[int], task: str, *, permissive: bool = False
) -> str:
    canon = CANONICAL_STRICT[task]
    if permissive and task in PERMISSIVE_SUBSTITUTES:
        # Count how many canonical tokens are satisfied (slot subs allowed).
        subs = PERMISSIVE_SUBSTITUTES[task]
        present = 0
        for c in canon:
            if c in tokenset or any(sub in tokenset for sub in subs.get(c, set())):
                present += 1
    else:
        present = len(canon & tokenset)

    size = SIZES[task]
    if present == size:
        return "canonical"
    if present == size - 1:
        return "near-canonical"
    if present >= 2 and present <= size - 2:
        return "partial"
    return "none"


def load_trajectory(run_dir: Path) -> list[tuple[int, str]]:
    """Return list of (generation, best_genotype_hex) from history.csv."""
    hc = run_dir / "history.csv"
    out: list[tuple[int, str]] = []
    with open(hc) as f:
        for row in csv.DictReader(f):
            out.append((int(row["generation"]), row["best_genotype_hex"]))
    return out


def load_result(run_dir: Path) -> dict:
    return json.loads((run_dir / "result.json").read_text())


def discover_seeds(root: Path, task: str) -> dict[int, Path]:
    """Map seed → run dir for all runs of `task` under `root`."""
    out: dict[int, Path] = {}
    for d in sorted(root.iterdir()):
        rp = d / "result.json"
        if not rp.exists():
            continue
        r = load_result(d)
        if r.get("task") == task:
            out[int(r["seed"])] = d
    return out


def analyse_task(root: Path, task: str, *, permissive: bool = False) -> dict:
    seeds = discover_seeds(root, task)
    per_seed: dict[int, dict] = {}
    milestones_csv_rows: list[tuple[int, str, int, str, int]] = []

    for seed, run_dir in seeds.items():
        traj = load_trajectory(run_dir)
        if not traj:
            continue
        # Classify each gen.
        m_series: list[tuple[int, str, int]] = []  # (gen, milestone, canonical_count)
        for gen, hexstr in traj:
            tape = hex_to_tape(hexstr)
            ts = extract_bp_topk_tokenset(tape)
            ms = classify_milestone(ts, task, permissive=permissive)
            # Also report raw canonical count for diagnostics.
            canon = CANONICAL_STRICT[task]
            if permissive and task in PERMISSIVE_SUBSTITUTES:
                subs = PERMISSIVE_SUBSTITUTES[task]
                n = sum(1 for c in canon if c in ts or any(sub in ts for sub in subs.get(c, set())))
            else:
                n = len(canon & ts)
            m_series.append((gen, ms, n))
            milestones_csv_rows.append((seed, task, gen, ms, n))

        # Extract per-seed first-generation at each milestone + residence times.
        first_gens: dict[str, int | None] = {k: None for k in ("none", "partial", "near-canonical", "canonical")}
        residence: dict[str, int] = {k: 0 for k in first_gens}
        transitions_to_canonical = 0
        prev_ms = None
        reached_canonical_at: int | None = None
        for gen, ms, _n in m_series:
            if first_gens[ms] is None:
                first_gens[ms] = gen
            residence[ms] += 1
            if prev_ms is not None and ms == "canonical" and prev_ms != "canonical":
                transitions_to_canonical += 1
                if reached_canonical_at is None:
                    reached_canonical_at = gen
            prev_ms = ms

        # Per-seed transition rate: (*→canonical transitions) / (gens spent below canonical).
        gens_below_canonical = sum(v for k, v in residence.items() if k != "canonical")
        r_seed = transitions_to_canonical / gens_below_canonical if gens_below_canonical > 0 else 0.0

        # First-gen-solve (fitness ≥ 0.999).
        # Use history.csv best_fitness column for this.
        first_solve_gen: int | None = None
        hc = run_dir / "history.csv"
        with open(hc) as f:
            for row in csv.DictReader(f):
                if float(row["best_fitness"]) >= 0.999:
                    first_solve_gen = int(row["generation"])
                    break

        per_seed[seed] = {
            "first_gens": first_gens,
            "residence": residence,
            "transitions_to_canonical": transitions_to_canonical,
            "gens_below_canonical": gens_below_canonical,
            "R_seed": r_seed,
            "first_canonical_set_gen": first_gens["canonical"],
            "first_solve_gen": first_solve_gen,
            "token_set_to_solve_delta": (
                None if first_solve_gen is None or first_gens["canonical"] is None
                else first_solve_gen - first_gens["canonical"]
            ),
        }

    return {
        "task": task,
        "n_seeds": len(per_seed),
        "per_seed": per_seed,
        "milestones_csv_rows": milestones_csv_rows,
    }


def control_degenerate_trigger(analysis: dict) -> tuple[bool, dict]:
    """CONTROL-DEGENERATE (§v2.3 sum_gt_5_slot): fires if first-canonical-set gen
    < 20 for ≥ 10/20 seeds, OR average gens-below-canonical < 50."""
    per_seed = analysis["per_seed"]
    below_20 = sum(1 for ps in per_seed.values()
                   if ps["first_canonical_set_gen"] is not None and ps["first_canonical_set_gen"] < 20)
    avg_gbc = statistics.mean(ps["gens_below_canonical"] for ps in per_seed.values()) if per_seed else 0
    seeds_reaching_canon = sum(1 for ps in per_seed.values() if ps["first_canonical_set_gen"] is not None)
    triggered = (below_20 >= 10) or (avg_gbc < 50)
    return triggered, {
        "sum_gt_5_slot_first_canonical_gen_below_20": below_20,
        "sum_gt_5_slot_avg_gens_below_canonical": avg_gbc,
        "sum_gt_5_slot_seeds_reaching_canonical_set": seeds_reaching_canon,
        "trigger": triggered,
    }


def summarise(tag: str, analysis: dict) -> None:
    per_seed = analysis["per_seed"]
    if not per_seed:
        print(f"  {tag}: no seeds")
        return
    n = len(per_seed)
    reach_canon = sum(1 for ps in per_seed.values() if ps["first_canonical_set_gen"] is not None)
    first_canon_gens = [ps["first_canonical_set_gen"] for ps in per_seed.values() if ps["first_canonical_set_gen"] is not None]
    first_solve_gens = [ps["first_solve_gen"] for ps in per_seed.values() if ps["first_solve_gen"] is not None]
    R_values = [ps["R_seed"] for ps in per_seed.values()]
    zero_R = sum(1 for r in R_values if r == 0.0)
    token_to_solve_deltas = [ps["token_set_to_solve_delta"] for ps in per_seed.values() if ps["token_set_to_solve_delta"] is not None]
    print(f"\n  {tag}  (n={n}, canonical reached by {reach_canon}/{n} seeds)")
    if first_canon_gens:
        print(f"    first_canonical_set_gen : median={int(statistics.median(first_canon_gens))}  mean={statistics.mean(first_canon_gens):.1f}  min={min(first_canon_gens)}  max={max(first_canon_gens)}")
    if first_solve_gens:
        print(f"    first_solve_gen         : median={int(statistics.median(first_solve_gens))}  n_solved={len(first_solve_gens)}")
    print(f"    R_seed                  : mean={statistics.mean(R_values):.5f}  median={statistics.median(R_values):.5f}  #zero={zero_R}/{n}")
    if token_to_solve_deltas:
        print(f"    token_set→solve delta   : median={int(statistics.median(token_to_solve_deltas))} gens  (canonical-set reached before solve by this many gens)")

    # Milestone-reached breakdown (across trajectory, not just "ever reached"):
    ever_near = sum(1 for ps in per_seed.values() if ps["first_gens"]["near-canonical"] is not None)
    ever_partial = sum(1 for ps in per_seed.values() if ps["first_gens"]["partial"] is not None)
    print(f"    seeds ever reaching     : partial={ever_partial}/{n}  near-canonical={ever_near}/{n}  canonical={reach_canon}/{n}")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    tasks = [
        (V23_ROOT, "sum_gt_5_slot", "§v2.3 primary control"),
        (V23_ROOT, "sum_gt_10_slot", "§v2.3 secondary control"),
        (V26_ROOT, "any_char_count_gt_1_slot", "§v2.6 Pair 1 primary"),
        (V26_ROOT, "any_char_count_gt_3_slot", "§v2.6 Pair 1 secondary"),
    ]

    all_analyses = {}
    print("\n=== §v2.7 milestone-trajectory analysis (strict classifier) ===")
    for root, task, label in tasks:
        if not root.exists():
            print(f"  skip: {root} (missing)")
            continue
        a = analyse_task(root, task, permissive=False)
        all_analyses[task] = a
        summarise(f"{label} [{task}]", a)

    # CONTROL-DEGENERATE evaluation on the primary control (sum_gt_5_slot).
    print("\n=== CONTROL-DEGENERATE evaluation (§v2.3 sum_gt_5_slot) ===")
    if "sum_gt_5_slot" in all_analyses:
        trigger, info = control_degenerate_trigger(all_analyses["sum_gt_5_slot"])
        print(f"  first_canonical_gen < 20 for: {info['sum_gt_5_slot_first_canonical_gen_below_20']}/20 seeds  (trigger if ≥ 10)")
        print(f"  avg gens below canonical   : {info['sum_gt_5_slot_avg_gens_below_canonical']:.1f}  (trigger if < 50)")
        print(f"  seeds reaching canonical   : {info['sum_gt_5_slot_seeds_reaching_canonical_set']}/20")
        print(f"  CONTROL-DEGENERATE fires?  : {trigger}")

    # Permissive re-classification for Pair 1 (sensitivity check).
    print("\n=== Permissive classifier sensitivity (Pair 1 only; SLOT_12 ∨ MAP_EQ_E) ===")
    for task in ("any_char_count_gt_1_slot", "any_char_count_gt_3_slot"):
        a = analyse_task(V26_ROOT, task, permissive=True)
        all_analyses[task + "__permissive"] = a
        summarise(f"{task} (permissive)", a)

    # Write milestones.csv.
    mcsv = OUT_DIR / "milestones.csv"
    with open(mcsv, "w") as f:
        w = csv.writer(f)
        w.writerow(["seed", "task", "generation", "milestone", "canonical_count"])
        for task, a in all_analyses.items():
            if task.endswith("__permissive"):
                continue
            for row in a["milestones_csv_rows"]:
                w.writerow(row)
    print(f"\n  milestones.csv → {mcsv}")

    # Write per-seed summary JSON.
    summary = {
        task: {
            "n_seeds": a["n_seeds"],
            "per_seed": {str(k): {kk: vv for kk, vv in v.items()} for k, v in a["per_seed"].items()},
        }
        for task, a in all_analyses.items() if not task.endswith("__permissive")
    }
    (OUT_DIR / "per_seed_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"  per_seed_summary.json → {OUT_DIR / 'per_seed_summary.json'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
