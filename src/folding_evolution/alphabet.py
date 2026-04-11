"""Alphabet: maps genotype characters to fragment types and fold instructions.

Each of the 62 valid characters (A-Z, a-z, 0-9) encodes:
1. A fragment type (what program construct it represents)
2. A fold instruction (how it bends the chain during folding)
"""

from __future__ import annotations

import random
from typing import Literal as TypingLiteral

# Type aliases for fragment types
FragmentType = tuple[str, str | int] | str  # e.g. ("fn_fragment", "filter") or "spacer"

# All valid genotype characters
ALPHABET = (
    [chr(c) for c in range(ord("A"), ord("Z") + 1)]
    + [chr(c) for c in range(ord("a"), ord("z") + 1)]
    + [chr(c) for c in range(ord("0"), ord("9") + 1)]
)

# Fragment type mapping
_FRAGMENT_MAP: dict[str, FragmentType] = {
    # Functions
    "A": ("fn_fragment", "filter"),
    "B": ("fn_fragment", "count"),
    "C": ("fn_fragment", "map"),
    "D": ("fn_fragment", "get"),
    "E": ("fn_fragment", "reduce"),
    "F": ("fn_fragment", "group_by"),
    "G": ("fn_fragment", "set"),
    "H": ("fn_fragment", "contains?"),
    "I": ("fn_fragment", "first"),
    # Operators / comparators
    "J": ("comparator", "+"),
    "K": ("comparator", ">"),
    "L": ("comparator", "<"),
    "M": ("comparator", "="),
    "N": ("connective", "and"),
    "O": ("connective", "or"),
    "P": ("connective", "not"),
    # Function wrappers
    "Q": ("fn_fragment", "fn"),
    "R": ("fn_fragment", "let"),
    # Data sources
    "S": ("data_source", "products"),
    "T": ("data_source", "employees"),
    "U": ("data_source", "orders"),
    "V": ("data_source", "expenses"),
    # Structural / conditional
    "W": ("fn_fragment", "match"),
    "X": ("fn_fragment", "if"),
    "Y": ("fn_fragment", "assoc"),
    # Spacer
    "Z": "spacer",
    # Field keys (lowercase a-h)
    "a": ("field_key", "price"),
    "b": ("field_key", "status"),
    "c": ("field_key", "department"),
    "d": ("field_key", "id"),
    "e": ("field_key", "name"),
    "f": ("field_key", "amount"),
    "g": ("field_key", "category"),
    "h": ("field_key", "employee_id"),
    # Collection-returning functions (i-l)
    "i": ("fn_fragment", "reverse"),
    "j": ("fn_fragment", "sort"),
    "k": ("fn_fragment", "rest"),
    "l": ("fn_fragment", "last"),
}

# Wildcards: m-z
for _c in range(ord("m"), ord("z") + 1):
    _FRAGMENT_MAP[chr(_c)] = "wildcard"

# Digits: 0->0, 1->100, ..., 9->900
for _c in range(ord("0"), ord("9") + 1):
    _FRAGMENT_MAP[chr(_c)] = ("literal", (_c - ord("0")) * 100)


def to_fragment(char: str) -> FragmentType:
    """Convert a single character to its fragment type."""
    return _FRAGMENT_MAP.get(char, "spacer")


def fold_instruction(char: str) -> str:
    """Return the fold instruction for a character.

    Returns one of: "left", "right", "straight", "reverse"
    """
    if char == "W":
        return "straight"
    if char == "X":
        return "left"
    if char == "Y":
        return "right"
    if char == "Z":
        return "reverse"
    if "a" <= char <= "z":
        return "straight"
    if "0" <= char <= "9":
        return "straight"
    if "A" <= char <= "V":
        return "left"
    return "straight"


def random_genotype(length: int, rng: random.Random | None = None) -> str:
    """Generate a random genotype string of the given length."""
    r = rng or random.Random()
    return "".join(r.choice(ALPHABET) for _ in range(length))
