"""Session-1 smoke for chem-tape v2-probe (Python executor only).

Runs each v2 task builder, hand-writes a target program for it, executes
that program against the task's inputs, and confirms every label is hit.
This is the pre-Rust end-to-end smoke — if this passes, the Python
semantics defined in alphabet.py/executor.py/tasks.py are internally
consistent with the architecture-v2 spec.

The smoke deliberately does NOT call evolve.py or the Rust backend.
Session 2 adds a Rust differential check; Session 3 adds an evolve smoke.

Usage:
    uv run python scripts/smoke_chem_tape_v2.py
Exits 0 on success, 1 on mismatch.
"""

from __future__ import annotations

import sys

from folding_evolution.chem_tape import alphabet as alph
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.executor import execute_program
from folding_evolution.chem_tape.tasks import build_task


ALPH = "v2_probe"


# ----- Target programs for each task -----
# Each entry: (task_name, program_tokens, human_note)

SCAN_MAP_BODY = [alph.INPUT, alph.CHARS, alph.SLOT_12, alph.ANY]
SUM_GT_SLOT_BODY = [alph.INPUT, alph.SUM, alph.THRESHOLD_SLOT, alph.GT]
SUM_GT_10_V2_BODY = [
    alph.INPUT, alph.SUM, alph.CONST_5, alph.CONST_5, alph.ADD, alph.GT,
]
AGG_BODY = [alph.INPUT, alph.SLOT_13, alph.THRESHOLD_SLOT, alph.GT]

# Compositional programs from experiments-v2.md §v2.4.
AND_PROG = [
    alph.CONST_0,
    alph.INPUT, alph.REDUCE_MAX, alph.CONST_5, alph.GT,
    alph.INPUT, alph.SUM, alph.CONST_5, alph.CONST_5, alph.ADD, alph.GT,
    alph.IF_GT,
]
OR_PROG = [
    alph.INPUT, alph.SUM, alph.CONST_5, alph.CONST_5, alph.ADD, alph.GT,
    alph.INPUT, alph.REDUCE_MAX, alph.CONST_5, alph.GT,
    alph.DUP,
    alph.IF_GT,
]

TASK_PROGRAMS = {
    "any_char_is_R": SCAN_MAP_BODY,
    "any_char_is_E": SCAN_MAP_BODY,
    "any_char_is_upper_v2": SCAN_MAP_BODY,
    "sum_gt_10_v2": SUM_GT_10_V2_BODY,
    "sum_gt_5_slot": SUM_GT_SLOT_BODY,
    "sum_gt_10_slot": SUM_GT_SLOT_BODY,
    "agg_sum_gt_10": AGG_BODY,
    "agg_max_gt_5": AGG_BODY,
    "sum_gt_10_AND_max_gt_5": AND_PROG,
    "sum_gt_10_OR_max_gt_5": OR_PROG,
}


def _run_task(task_name: str, program: list[int]) -> tuple[int, int, int]:
    """Build the task and run `program` against all of its training inputs.

    Returns (n_examples, n_matches, n_positives_in_labels).
    """
    cfg = ChemTapeConfig(
        task=task_name, n_examples=64, holdout_size=0, alphabet=ALPH,
    )
    task = build_task(cfg, seed=0)
    matches = 0
    for x, y in zip(task.inputs, task.labels):
        out = execute_program(
            program, task.alphabet, x, task.input_type, alphabet_name=ALPH
        )
        # Tasks here are all binary; coerce executor output to 0/1 via ">0".
        pred = 1 if out > 0 else 0
        if pred == int(y):
            matches += 1
    return len(task.inputs), matches, int(task.labels.sum())


def main() -> int:
    print(f"Chem-tape v2-probe smoke — alphabet={ALPH}")
    print(f"Config hash (default v1): {ChemTapeConfig().hash()}")
    print(f"Config hash (v2_probe):   {ChemTapeConfig(alphabet=ALPH).hash()}")
    print()

    any_fail = False
    for task_name, program in TASK_PROGRAMS.items():
        n, matches, pos = _run_task(task_name, program)
        status = "OK " if matches == n else "FAIL"
        if matches != n:
            any_fail = True
        print(f"  {status}  {task_name:30s}  {matches}/{n}  (pos={pos})  prog={len(program)} toks")

    # Also explicitly check §v2.3's body-invariance claim at the program level.
    cfg = ChemTapeConfig(n_examples=4, holdout_size=0, alphabet=ALPH)
    t5 = build_task(
        ChemTapeConfig(task="sum_gt_5_slot", n_examples=4, holdout_size=0, alphabet=ALPH),
        seed=0,
    )
    t10 = build_task(
        ChemTapeConfig(task="sum_gt_10_slot", n_examples=4, holdout_size=0, alphabet=ALPH),
        seed=0,
    )
    shared_body = SUM_GT_SLOT_BODY
    print()
    print(f"  §v2.3 body-invariance: both tasks use body={shared_body}")
    print(f"     sum_gt_5_slot threshold  = {t5.alphabet.threshold}")
    print(f"     sum_gt_10_slot threshold = {t10.alphabet.threshold}")

    # Direct-token dispatch coverage: every new primitive id must fire via
    # its token id on the tape (separate from slot-binding dispatch). Builds
    # a small hand-written program per token id with a known expected output.
    print()
    print("  Direct-token dispatch coverage:")
    direct_cases: list[tuple[int, str, list[int], object, str, int]] = [
        (alph.MAP_EQ_E,
         "MAP_EQ_E counts 'E' in 'ElE' → 2",
         [alph.INPUT, alph.CHARS, alph.MAP_EQ_E, alph.SUM],
         "ElE", "str", 2),
        (alph.CONST_2,
         "CONST_2 pushes 2",
         [alph.CONST_2],
         (), "intlist", 2),
        (alph.CONST_5,
         "CONST_5 pushes 5",
         [alph.CONST_5],
         (), "intlist", 5),
        (alph.IF_GT,
         "IF_GT(else=2, then=5, cond=1) → 5",
         [alph.CONST_2, alph.CONST_5, alph.CONST_1, alph.IF_GT],
         (), "intlist", 5),
        (alph.REDUCE_MAX,
         "REDUCE_MAX on (1,9,3) → 9",
         [alph.INPUT, alph.REDUCE_MAX],
         (1, 9, 3), "intlist", 9),
        (alph.THRESHOLD_SLOT,
         "THRESHOLD_SLOT with ta.threshold=7 → 7",
         [alph.THRESHOLD_SLOT],
         (), "intlist", 7),
    ]
    direct_fail = False
    new_ids_used: set[int] = set()
    for tid, note, prog, inp, inp_type, expected in direct_cases:
        ta = alph.TaskAlphabet(threshold=7) if tid == alph.THRESHOLD_SLOT else alph.TaskAlphabet()
        got = execute_program(prog, ta, inp, inp_type, alphabet_name=ALPH)
        ok = got == expected
        new_ids_used.add(tid)
        print(f"    {'OK ' if ok else 'FAIL'}  id={tid:<2d}  {note}  got={got}")
        if not ok:
            direct_fail = True
    expected_ids = {alph.MAP_EQ_E, alph.CONST_2, alph.CONST_5,
                    alph.IF_GT, alph.REDUCE_MAX, alph.THRESHOLD_SLOT}
    missing = expected_ids - new_ids_used
    if missing or direct_fail:
        print(f"    FAIL  Missing direct dispatch for: {sorted(missing)}")
        any_fail = True

    # Separator ids 20/21 under v2 must execute as NOP.
    sep_out = execute_program(
        [alph.CONST_1, alph.SEP_A, alph.SEP_B],
        alph.TaskAlphabet(), (), "intlist", alphabet_name=ALPH,
    )
    print(f"  Separator pass-through (expect top=1): got {sep_out}")
    if sep_out != 1:
        any_fail = True

    print()
    print("RESULT:", "FAIL" if any_fail else "PASS")
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
