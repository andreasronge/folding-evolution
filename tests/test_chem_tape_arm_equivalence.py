"""Arm A and Arm B produce identical programs on a fully-active tape.

Spec §Layer 9: "Arm A = Arm B minus Layers 4 and 5." When no separators exist
(no inactive cells), the longest-run on Arm B spans the entire tape, which is
exactly what Arm A executes.
"""

import numpy as np

from folding_evolution.chem_tape import alphabet as alph
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evaluate import _programs_for_arm


def test_fully_active_tape_programs_identical():
    # All ids in {1..13} — fully active, no separators.
    tape = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 1, 2, 3]], dtype=np.uint8)

    cfg_a = ChemTapeConfig(tape_length=16, arm="A", backend="numpy")
    cfg_b = ChemTapeConfig(tape_length=16, arm="B", backend="numpy")

    prog_a = _programs_for_arm(cfg_a, tape)
    prog_b = _programs_for_arm(cfg_b, tape)

    assert prog_a == prog_b
    assert prog_a[0] == tape[0].tolist()


def test_arms_differ_when_separators_present():
    tape = np.array([[1, 2, 0, 3, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.uint8)
    cfg_a = ChemTapeConfig(tape_length=16, arm="A", backend="numpy")
    cfg_b = ChemTapeConfig(tape_length=16, arm="B", backend="numpy")

    prog_a = _programs_for_arm(cfg_a, tape)[0]
    prog_b = _programs_for_arm(cfg_b, tape)[0]

    # Arm A sees all 16 cells (including 0 padding).
    assert len(prog_a) == 16
    # Arm B sees only the longest run — cells 3,4,5 (length 3).
    assert prog_b == [3, 4, 5]
