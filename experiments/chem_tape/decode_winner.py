#!/usr/bin/env python3
"""Decode a best-of-run genotype into a human-readable program.

Given a sweep dir and config hash (or a hex tape), this prints:
  * The raw tape (token ids and mnemonic names)
  * The extracted canonical program (arm-dependent: BP_TOPK uses top-K
    permeable runs in tape order)
  * The per-task cross-eval fitness (when present in result.json)
  * A proxy-predicate heuristic classifier (flags the §v2.4 attractor category:
    max>5-alone, sum>threshold-alone, constant-predicate, etc.)

Usage:
    python experiments/chem_tape/decode_winner.py <sweep_name> <config_hash>
    python experiments/chem_tape/decode_winner.py <sweep_name> --all
    python experiments/chem_tape/decode_winner.py --hex <32-hex-chars>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from folding_evolution.chem_tape import alphabet as alph
from folding_evolution.chem_tape import engine
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.tasks import build_task

OUTPUT_ROOT = REPO_ROOT / "experiments" / "chem_tape" / "output"

TOKEN_NAMES = {
    alph.NOP: "NOP",
    alph.INPUT: "INPUT",
    alph.CONST_0: "CONST_0",
    alph.CONST_1: "CONST_1",
    alph.CHARS: "CHARS",
    alph.SUM: "SUM",
    alph.ANY: "ANY",
    alph.ADD: "ADD",
    alph.GT: "GT",
    alph.DUP: "DUP",
    alph.SWAP: "SWAP",
    alph.REDUCE_ADD: "REDUCE_ADD",
    alph.SLOT_12: "SLOT_12",
    alph.SLOT_13: "SLOT_13",
    alph.MAP_EQ_E: "MAP_EQ_E",
    alph.CONST_2: "CONST_2",
    alph.CONST_5: "CONST_5",
    alph.IF_GT: "IF_GT",
    alph.REDUCE_MAX: "REDUCE_MAX",
    alph.THRESHOLD_SLOT: "THRESHOLD_SLOT",
    alph.SEP_A: "SEP_A",
    alph.SEP_B: "SEP_B",
}


def hex_to_tape(hex_str: str) -> np.ndarray:
    raw = bytes.fromhex(hex_str)
    return np.frombuffer(raw, dtype=np.uint8).copy()


def format_tape(tape: np.ndarray) -> str:
    parts = []
    for i, t in enumerate(tape):
        name = TOKEN_NAMES.get(int(t), f"?{t}")
        parts.append(f"{i:2d}:{int(t):2d}({name})")
    return "\n    ".join("  ".join(parts[i:i+4]) for i in range(0, len(parts), 4))


def extract_bp_topk_program(tape: np.ndarray, k: int = 3) -> list[int]:
    """Mirror evaluate._programs_for_arm BP_TOPK path: permeable longest runs,
    top-K by length, concatenated in tape order.
    """
    tapes = tape.reshape(1, -1)
    mask = engine.compute_longest_runnable_mask(tapes, backend="numpy")
    # compute_longest_runnable_mask returns the longest run only; for TOPK
    # we would need a different primitive. For decoding purposes, fall back
    # to showing all active (non-separator, non-NOP) cells in tape order —
    # that is the permeable-all program, a superset of any BP_TOPK extraction.
    _ = mask  # reserved; not used here
    masks = alph.masks_for("v2_probe")
    active = masks["active"]
    sep = masks["separator"]
    # Permeable: non-separator cells survive; NOP treated as no-op; we return
    # tokens in tape order excluding separators.
    prog: list[int] = []
    for t in tape.tolist():
        if sep[int(t)]:
            # Separator ends a run — simulate permeable-all by continuing.
            continue
        if int(t) == 0:
            continue  # NOP
        prog.append(int(t))
    return prog


def classify_proxy(tape: np.ndarray) -> str:
    """Rough heuristic classifier for proxy-predicate attractors.

    Reads the extracted program (permeable-all view) and flags patterns:
      max_gt_5     : REDUCE_MAX + CONST_5 + GT
      max_gt_c     : REDUCE_MAX + any const + GT
      sum_gt_c     : INPUT + SUM + constant + GT
      chars_sum    : CHARS + MAP_* + SUM
      if_gt_compos : any IF_GT with CONST_0 prefix reachable
      has_threshold_slot : THRESHOLD_SLOT appears
      unclassified : otherwise
    """
    prog = extract_bp_topk_program(tape)
    names = [TOKEN_NAMES[t] for t in prog]
    joined = " ".join(names)
    tags: list[str] = []
    if "THRESHOLD_SLOT" in joined:
        tags.append("uses_THRESHOLD_SLOT")
    if "IF_GT" in joined:
        tags.append("has_IF_GT")
    if "REDUCE_MAX" in names:
        idx = names.index("REDUCE_MAX")
        after = names[idx:idx + 5]
        if "CONST_5" in after and "GT" in after:
            tags.append("max_gt_5_attractor")
        elif "GT" in after:
            tags.append("max_gt_const")
    if names.count("SUM") and "INPUT" in names:
        tags.append("sum_variant")
    if "CHARS" in names:
        tags.append("char_scan")
    return ",".join(tags) if tags else "unclassified"


def decode_one(sweep: str, cfg_hash: str, *, eval_task: str | None = None) -> None:
    rp = OUTPUT_ROOT / sweep / cfg_hash / "result.json"
    if not rp.exists():
        print(f"  {sweep}/{cfg_hash}: result.json missing")
        return
    r = json.loads(rp.read_text())
    tape = hex_to_tape(r["best_genotype_hex"])
    prog = extract_bp_topk_program(tape)
    cls = classify_proxy(tape)

    print(f"\n  seed={r['seed']:>2}  hash={cfg_hash}  task={r['task']}")
    print(f"    best_fitness={r['best_fitness']:.3f}  holdout={r.get('holdout_fitness','NA')}")
    ct = r.get("cross_task_fitness")
    if ct:
        for t, v in ct.items():
            solve = "★" if v["fitness"] >= 0.999 else " "
            print(f"    {solve} {t:48s}  train={v['fitness']:.3f}  hold={v['holdout_fitness']}")
    print(f"    tokens  : {' '.join(f'{t}' for t in tape.tolist())}")
    print(f"    program : {' '.join(TOKEN_NAMES[t] for t in prog)}  (len={len(prog)})")
    print(f"    classify: {cls}")


def decode_all(sweep: str) -> None:
    sw_dir = OUTPUT_ROOT / sweep
    for d in sorted(sw_dir.iterdir()):
        if (d / "result.json").exists():
            decode_one(sweep, d.name)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sweep", nargs="?")
    ap.add_argument("cfg_hash", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--hex", help="decode a raw hex tape")
    args = ap.parse_args()

    if args.hex:
        tape = hex_to_tape(args.hex)
        prog = extract_bp_topk_program(tape)
        print(f"tape    : {' '.join(f'{t}' for t in tape.tolist())}")
        print(f"program : {' '.join(TOKEN_NAMES[t] for t in prog)}")
        print(f"classify: {classify_proxy(tape)}")
        return 0
    if not args.sweep:
        ap.error("provide sweep name or --hex")
    if args.all:
        decode_all(args.sweep)
    elif args.cfg_hash:
        decode_one(args.sweep, args.cfg_hash)
    else:
        decode_all(args.sweep)
    return 0


if __name__ == "__main__":
    sys.exit(main())
