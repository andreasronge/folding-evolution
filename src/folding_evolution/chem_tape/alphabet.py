"""Token alphabet for chem-tape v1.

4-bit tokens packed into the low nibble of each tape byte. Ids 0..11 are the
task-invariant shared core; 12 and 13 are task-bound slots whose meaning is
declared per-task. Ids 14 and 15 are unused in v1 and execute as NOP — kept
reserved for v2 quotation tokens.

A cell is "active" iff its token id is in 1..13. Bonds (spec §Layer 4) form
between adjacent cells that are both active.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# Shared tokens (ids 0..11).
NOP = 0
INPUT = 1
CONST_0 = 2
CONST_1 = 3
CHARS = 4
SUM = 5
ANY = 6
ADD = 7
GT = 8
DUP = 9
SWAP = 10
REDUCE_ADD = 11

# Slot placeholders (task-bound).
SLOT_12 = 12
SLOT_13 = 13

# Reserved-as-NOP in v1.
RESERVED_14 = 14
RESERVED_15 = 15

N_TOKENS = 16

# Task-specific op names that slots 12/13 may bind to.
OP_NOP = "NOP"
OP_MAP_EQ_R = "MAP_EQ_R"
OP_MAP_IS_UPPER = "MAP_IS_UPPER"


# Active mask over all 16 ids: True iff the id executes a non-NOP operation.
# Indices 1..13 are active; 0, 14, 15 are inactive.
ACTIVE_MASK: np.ndarray = np.zeros(N_TOKENS, dtype=bool)
ACTIVE_MASK[1:14] = True


def is_active(tid: int) -> bool:
    """Spec §Layer 4: a cell is active iff its token id is in 1..13."""
    return 1 <= tid <= 13


@dataclass(frozen=True)
class TaskAlphabet:
    """Binds slot 12 and slot 13 to task-specific op names.

    The executor consults this when dispatching tokens 12 and 13 to decide
    which (if any) op to run. Op names are strings drawn from the constants
    above (OP_*). A slot name of OP_NOP means the token is a no-op.
    """

    slot_12: str = OP_NOP
    slot_13: str = OP_NOP
