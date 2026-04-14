"""Token alphabet for chem-tape.

v1 uses 16 token ids; ids 0..11 are the task-invariant shared core, 12 and 13
are task-bound slots, 14 and 15 execute as NOP and are "separator" / "reserved"
in various v1 rules. Storage is one token per byte (uint8) — the "low nibble"
framing in earlier comments is historical and does not constrain the alphabet
size.

v2-probe (architecture-v2.md) extends the alphabet to 22 token ids:
  * ids 14..19 add six new primitives (MAP_EQ_E, CONST_2, CONST_5, IF_GT,
    REDUCE_MAX, THRESHOLD_SLOT)
  * ids 20..21 are the v2 separators (shifted from v1's 14/15)
The expansion is gated at the *config* level (`ChemTapeConfig.alphabet`). When
`alphabet == "v1"`, ids 14..21 either execute as NOP (14, 15 — reserved) or
never appear in tapes at all (evolve.py inits ids 0..15). Under
`alphabet == "v2_probe"`, the full v2 dispatch is live and ids 20/21 become
separators.

A cell is "active" iff its token id is in the alphabet-appropriate active set:
  * v1: 1..13 (ids 0, 14, 15 inactive)
  * v2_probe: 1..19 (id 0 inactive; 20/21 are separators)
Bonds (spec §Layer 4) form between adjacent active cells.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# Shared tokens (ids 0..11) — unchanged between v1 and v2_probe.
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

# v1 reserved / separator ids (execute as NOP in v1). In v2_probe these ids
# host new primitives — see below.
RESERVED_14 = 14
RESERVED_15 = 15

# v2-probe primitives (architecture-v2.md §Proposed alphabet expansion).
# These ids coincide with v1's RESERVED_14/15 plus four new ones. Under
# alphabet="v1", ids 14..19 execute as NOP (the v1 reserved rule still
# applies); under alphabet="v2_probe", they dispatch to the new ops.
MAP_EQ_E = 14
CONST_2 = 15
CONST_5 = 16
IF_GT = 17
REDUCE_MAX = 18
THRESHOLD_SLOT = 19

# v2-probe separators (shifted from v1's 14/15).
SEP_A = 20
SEP_B = 21

N_TOKENS_V1 = 16
N_TOKENS_V2 = 22
# Legacy alias — existing v1 code paths (engine_numpy, engine_mlx) import
# N_TOKENS; keep it pointing at the widest mask so lookup-table indexing stays
# in-bounds when a v2 token appears on a tape.
N_TOKENS = N_TOKENS_V2

# Task-specific op names that slots 12/13 may bind to.
OP_NOP = "NOP"
OP_MAP_EQ_R = "MAP_EQ_R"
OP_MAP_IS_UPPER = "MAP_IS_UPPER"
# v2-probe slot-binding extensions (architecture-v2.md §Slot-binding generalization).
OP_MAP_EQ_E = "MAP_EQ_E"
OP_REDUCE_ADD = "REDUCE_ADD"
OP_REDUCE_MAX = "REDUCE_MAX"


# ----- v1 masks (indexed by token id, length N_TOKENS_V2 so lookup-table
# indexing of a v2 token on a v1-alphabet tape stays in bounds and yields
# "inactive" for the v2-only ids) -----

# Active: ids 1..13 only. Ids 0, 14..21 inactive.
ACTIVE_MASK_V1: np.ndarray = np.zeros(N_TOKENS_V2, dtype=bool)
ACTIVE_MASK_V1[1:14] = True

# Separators (v1): 14, 15.
SEPARATOR_MASK_V1: np.ndarray = np.zeros(N_TOKENS_V2, dtype=bool)
SEPARATOR_MASK_V1[14:16] = True

# Transparent (Arm BP): id 0 only.
TRANSPARENT_MASK_V1: np.ndarray = np.zeros(N_TOKENS_V2, dtype=bool)
TRANSPARENT_MASK_V1[0] = True

NON_SEPARATOR_MASK_V1: np.ndarray = ~SEPARATOR_MASK_V1


# ----- v2-probe masks -----

# Active: ids 1..19. Id 0 inactive; 20, 21 separators.
ACTIVE_MASK_V2: np.ndarray = np.zeros(N_TOKENS_V2, dtype=bool)
ACTIVE_MASK_V2[1:20] = True

# Separators (v2): 20, 21.
SEPARATOR_MASK_V2: np.ndarray = np.zeros(N_TOKENS_V2, dtype=bool)
SEPARATOR_MASK_V2[20:22] = True

# Transparent (Arm BP): id 0 only — unchanged across alphabets.
TRANSPARENT_MASK_V2: np.ndarray = np.zeros(N_TOKENS_V2, dtype=bool)
TRANSPARENT_MASK_V2[0] = True

NON_SEPARATOR_MASK_V2: np.ndarray = ~SEPARATOR_MASK_V2


# ----- Legacy (v1) module-level aliases -----
#
# Existing callers (engine_numpy, engine_mlx, metrics) import these names
# directly and assume v1 semantics. Keep them pointing at the v1 masks so
# no v1 code path changes behaviour. v2-aware callers select masks via
# `masks_for(alphabet_name)` below.
ACTIVE_MASK = ACTIVE_MASK_V1
SEPARATOR_MASK = SEPARATOR_MASK_V1
TRANSPARENT_MASK = TRANSPARENT_MASK_V1
NON_SEPARATOR_MASK = NON_SEPARATOR_MASK_V1


def masks_for(alphabet_name: str) -> dict[str, np.ndarray]:
    """Return the mask set for a given alphabet name.

    `alphabet_name` is one of "v1" (default) or "v2_probe". Keys:
    `active`, `separator`, `transparent`, `non_separator`.
    """
    if alphabet_name == "v2_probe":
        return {
            "active": ACTIVE_MASK_V2,
            "separator": SEPARATOR_MASK_V2,
            "transparent": TRANSPARENT_MASK_V2,
            "non_separator": NON_SEPARATOR_MASK_V2,
        }
    return {
        "active": ACTIVE_MASK_V1,
        "separator": SEPARATOR_MASK_V1,
        "transparent": TRANSPARENT_MASK_V1,
        "non_separator": NON_SEPARATOR_MASK_V1,
    }


def is_active(tid: int, alphabet_name: str = "v1") -> bool:
    if alphabet_name == "v2_probe":
        return 1 <= tid <= 19
    return 1 <= tid <= 13


def is_separator(tid: int, alphabet_name: str = "v1") -> bool:
    if alphabet_name == "v2_probe":
        return tid in (20, 21)
    return tid in (14, 15)


@dataclass(frozen=True)
class TaskAlphabet:
    """Binds per-token op resolution for a task.

    v1 fields (`slot_12`, `slot_13`) are unchanged. v2-probe adds `threshold`
    (the integer constant THRESHOLD_SLOT pushes). `threshold` is ignored
    when the executing alphabet is "v1" — the tape id 19 is inactive under
    v1 masks and is reserved-as-NOP on the dispatch path.
    """

    slot_12: str = OP_NOP
    slot_13: str = OP_NOP
    threshold: int = 0
