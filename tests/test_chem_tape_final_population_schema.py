"""Tests for §v2.5-plasticity-2a runtime-invariant pytest (prereg v14,
amendment cycle closed at 74f141f; checklist item 3(b)).

Verbatim spec of the two helpers is in Plans/prereg_v2-5-plasticity-2a.md
item 3(b). The helpers enforce the runtime invariants that
top1_winner_hamming's artifact-complete floor depends on:

- ``assert_plasticity_final_population_schema`` — schema + range checks
  against a ``final_population.npz`` file. Covers field-presence, rank,
  shape, dtype, finiteness, value-range, and (v14) integer-token-range
  invariants.
- ``assert_canonical_hex_length`` — length AND (v14 closure) token-range
  check against a canonical-hex string decoded via
  ``analyze_retention.hex_to_tape``.

Any failure routes the chronicle-time row-1 verdict to BLOCKED per the
Chronicle-time classical-Baldwin disambiguation discipline section.

The synthetic-fixture suite enumerates 13 invalid classes (12 for the npz
helper, 2 for the canonical helper — the canonical wrong-length and the
canonical invalid-token); each fixture verifies the corresponding
assertion fires.

The pytest proper also runs the helpers against a real ``final_population.npz``
fixture produced by a synthetic-but-plausible population (shape-matched
to the sweep literals pop_size=512, tape_length=32, alphabet=v2_probe).
The full pilot-sweep validation is run separately at engineering-discharge
time; this module validates the helpers themselves.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

# Wire analyze_retention from experiments/chem_tape onto sys.path so
# hex_to_tape is the same definition the analyze_plasticity pipeline
# uses (principle 23 — consistent decode across sibling analyses).
_REPO_ROOT = Path(__file__).resolve().parents[1]
_EXPERIMENTS_CHEM_TAPE = _REPO_ROOT / "experiments" / "chem_tape"
if str(_EXPERIMENTS_CHEM_TAPE) not in sys.path:
    sys.path.insert(0, str(_EXPERIMENTS_CHEM_TAPE))

from analyze_retention import hex_to_tape  # type: ignore[import-not-found]


# --- Helpers under test (verbatim from prereg v14 + v14 closure) ---


def assert_plasticity_final_population_schema(
    npz_path: Path,
    pop_size: int,
    expected_tape_length: int,
    alphabet_size: int,
) -> None:
    """Enforce runtime invariants required by top1_winner_hamming's
    artifact-complete floor. Raises AssertionError on violation; any
    failure routes the chronicle-time row-1 verdict to BLOCKED per the
    Chronicle-time classical-Baldwin disambiguation discipline section's
    floor.
    """
    data = np.load(npz_path)
    required = {
        "genotypes",
        "test_fitness_plastic",
        "train_fitness_plastic",
    }
    missing = required - set(data.files)
    assert not missing, f"missing fields: {missing}"

    g = data["genotypes"]
    assert g.ndim == 2, f"genotypes ndim={g.ndim}, expected 2"
    assert g.shape[0] == pop_size, (
        f"genotypes.shape[0]={g.shape[0]}, expected {pop_size}"
    )
    assert g.shape[1] == expected_tape_length, (
        f"genotypes.shape[1]={g.shape[1]}, "
        f"expected {expected_tape_length}"
    )
    assert np.issubdtype(g.dtype, np.integer), (
        f"genotypes dtype={g.dtype}, expected integer"
    )
    bad_tokens = np.argwhere((g < 0) | (g >= alphabet_size))
    assert bad_tokens.size == 0, (
        f"genotypes has out-of-alphabet token values "
        f"(alphabet_size={alphabet_size}) at (row, col) indices: "
        f"{bad_tokens.tolist()[:10]}"
    )

    for name in ("test_fitness_plastic", "train_fitness_plastic"):
        arr = data[name]
        assert arr.ndim == 1, f"{name} ndim={arr.ndim}, expected 1"
        assert arr.shape[0] == pop_size, (
            f"{name}.shape[0]={arr.shape[0]}, expected {pop_size}"
        )
        assert np.issubdtype(arr.dtype, np.floating), (
            f"{name} dtype={arr.dtype}, expected floating"
        )
        bad = np.where(~np.isfinite(arr))[0]
        assert bad.size == 0, (
            f"{name} has non-finite values at indices: "
            f"{bad.tolist()[:10]}"
        )
        out_of_range = np.where((arr < 0.0) | (arr > 1.0))[0]
        assert out_of_range.size == 0, (
            f"{name} has values outside [0, 1] at indices: "
            f"{out_of_range.tolist()[:10]} "
            f"(values are fractions per METRIC_DEFINITIONS)"
        )


def assert_canonical_hex_length(
    canonical_hex: str,
    expected_tape_length: int,
    alphabet_size: int,
) -> None:
    """Enforce that the CLI-provided canonical tape decodes to the
    prereg's committed tape length AND contains only in-alphabet tokens.

    A length mismatch silently perturbs top1_winner_hamming via
    mismatched-length active-view Levenshtein at analyze time
    (analyze_plasticity.py:655). A token-range violation (v14 closure
    per codex-v14 P1) silently skews top1_winner_hamming because
    extract_active masks only id 0 and separators — a canonical
    containing token id 22 or 23 would be treated as an active token.

    Raises AssertionError on violation; any failure routes the
    chronicle-time row-1 verdict to BLOCKED.
    """
    canonical_tape = hex_to_tape(canonical_hex)
    assert len(canonical_tape) == expected_tape_length, (
        f"canonical_hex decodes to length={len(canonical_tape)}, "
        f"expected {expected_tape_length}"
    )
    bad_tokens = np.argwhere(
        (canonical_tape < 0) | (canonical_tape >= alphabet_size)
    )
    assert bad_tokens.size == 0, (
        f"canonical_hex decodes to tokens outside "
        f"[0, {alphabet_size}) at indices: "
        f"{bad_tokens.flatten().tolist()[:10]}"
    )


# --- Sweep literals (principle 27: match
#     experiments/chem_tape/sweeps/v2/v2_5_plasticity_2a.yaml verbatim) ---

SWEEP_POP_SIZE = 512
SWEEP_TAPE_LENGTH = 32
# v2_probe alphabet size — token ids 0..21. See
# src/folding_evolution/chem_tape/alphabet.py:76 (N_TOKENS_V2 = 22).
SWEEP_ALPHABET_SIZE = 22

# The sweep's canonical hex is the sum_gt_10_AND_max_gt_5 canonical,
# sourced from analyze_retention.CANONICAL_AND_BODY_HEX per
# analyze_plasticity.py:644 (--canonical-hex default).
from analyze_retention import CANONICAL_AND_BODY_HEX  # type: ignore[import-not-found]

SWEEP_CANONICAL_HEX = CANONICAL_AND_BODY_HEX


# --- Synthetic-fixture builders ---


def _valid_genotypes() -> np.ndarray:
    """Random but valid genotypes: shape=(512, 32), uint8, tokens in
    [0, alphabet_size). Deterministic per numpy seed 42."""
    rng = np.random.default_rng(42)
    return rng.integers(
        0, SWEEP_ALPHABET_SIZE, size=(SWEEP_POP_SIZE, SWEEP_TAPE_LENGTH),
        dtype=np.uint8,
    )


def _valid_fitness() -> np.ndarray:
    """Random but valid fitness: shape=(512,), float32, in [0, 1]."""
    rng = np.random.default_rng(43)
    return rng.uniform(0.0, 1.0, size=SWEEP_POP_SIZE).astype(np.float32)


def _write_npz(tmp_path: Path, name: str, **arrays: np.ndarray) -> Path:
    """Write an npz with the given arrays to tmp_path; return the path."""
    p = tmp_path / f"{name}.npz"
    np.savez(p, **arrays)
    return p


def _valid_npz_path(tmp_path: Path) -> Path:
    return _write_npz(
        tmp_path,
        "valid",
        genotypes=_valid_genotypes(),
        test_fitness_plastic=_valid_fitness(),
        train_fitness_plastic=_valid_fitness(),
    )


# --- Positive control: valid npz + valid canonical pass ---


def test_valid_npz_passes(tmp_path):
    assert_plasticity_final_population_schema(
        _valid_npz_path(tmp_path),
        pop_size=SWEEP_POP_SIZE,
        expected_tape_length=SWEEP_TAPE_LENGTH,
        alphabet_size=SWEEP_ALPHABET_SIZE,
    )


def test_valid_canonical_passes():
    assert_canonical_hex_length(
        SWEEP_CANONICAL_HEX,
        expected_tape_length=SWEEP_TAPE_LENGTH,
        alphabet_size=SWEEP_ALPHABET_SIZE,
    )


# --- Synthetic invalid fixtures (12 classes for npz + 2 for canonical) ---
#
# Each fixture verifies the corresponding assertion fires. Classes per
# prereg v14 checklist item 3(b) "Synthetic-fixture test suite" block.


# Class 1: missing field.
def test_missing_field_fails(tmp_path):
    p = _write_npz(
        tmp_path,
        "missing_field",
        genotypes=_valid_genotypes(),
        train_fitness_plastic=_valid_fitness(),
        # test_fitness_plastic OMITTED
    )
    with pytest.raises(AssertionError, match="missing fields"):
        assert_plasticity_final_population_schema(
            p, pop_size=SWEEP_POP_SIZE,
            expected_tape_length=SWEEP_TAPE_LENGTH,
            alphabet_size=SWEEP_ALPHABET_SIZE,
        )


# Class 2: wrong-rank genotypes (1D instead of 2D).
def test_wrong_rank_genotypes_fails(tmp_path):
    p = _write_npz(
        tmp_path, "wrong_rank_g",
        genotypes=_valid_genotypes().reshape(-1),  # 1D
        test_fitness_plastic=_valid_fitness(),
        train_fitness_plastic=_valid_fitness(),
    )
    with pytest.raises(AssertionError, match="genotypes ndim"):
        assert_plasticity_final_population_schema(
            p, pop_size=SWEEP_POP_SIZE,
            expected_tape_length=SWEEP_TAPE_LENGTH,
            alphabet_size=SWEEP_ALPHABET_SIZE,
        )


# Class 3: wrong-first-dim genotypes (shape[0] != pop_size).
def test_wrong_first_dim_genotypes_fails(tmp_path):
    rng = np.random.default_rng(44)
    bad = rng.integers(
        0, SWEEP_ALPHABET_SIZE, size=(511, SWEEP_TAPE_LENGTH), dtype=np.uint8,
    )
    p = _write_npz(
        tmp_path, "wrong_first_dim_g",
        genotypes=bad,
        test_fitness_plastic=_valid_fitness(),
        train_fitness_plastic=_valid_fitness(),
    )
    with pytest.raises(AssertionError, match=r"genotypes\.shape\[0\]"):
        assert_plasticity_final_population_schema(
            p, pop_size=SWEEP_POP_SIZE,
            expected_tape_length=SWEEP_TAPE_LENGTH,
            alphabet_size=SWEEP_ALPHABET_SIZE,
        )


# Class 4: wrong-second-dim genotypes (shape[1] != tape_length; v13).
def test_wrong_second_dim_genotypes_fails(tmp_path):
    rng = np.random.default_rng(45)
    bad = rng.integers(
        0, SWEEP_ALPHABET_SIZE, size=(SWEEP_POP_SIZE, 31), dtype=np.uint8,
    )
    p = _write_npz(
        tmp_path, "wrong_second_dim_g",
        genotypes=bad,
        test_fitness_plastic=_valid_fitness(),
        train_fitness_plastic=_valid_fitness(),
    )
    with pytest.raises(AssertionError, match=r"genotypes\.shape\[1\]"):
        assert_plasticity_final_population_schema(
            p, pop_size=SWEEP_POP_SIZE,
            expected_tape_length=SWEEP_TAPE_LENGTH,
            alphabet_size=SWEEP_ALPHABET_SIZE,
        )


# Class 5: non-integer genotypes dtype (float).
def test_non_integer_genotypes_fails(tmp_path):
    rng = np.random.default_rng(46)
    bad = rng.uniform(
        0.0, float(SWEEP_ALPHABET_SIZE),
        size=(SWEEP_POP_SIZE, SWEEP_TAPE_LENGTH),
    ).astype(np.float32)
    p = _write_npz(
        tmp_path, "non_integer_g",
        genotypes=bad,
        test_fitness_plastic=_valid_fitness(),
        train_fitness_plastic=_valid_fitness(),
    )
    with pytest.raises(AssertionError, match="genotypes dtype"):
        assert_plasticity_final_population_schema(
            p, pop_size=SWEEP_POP_SIZE,
            expected_tape_length=SWEEP_TAPE_LENGTH,
            alphabet_size=SWEEP_ALPHABET_SIZE,
        )


# Class 6: wrong-rank fitness (2D).
def test_wrong_rank_fitness_fails(tmp_path):
    p = _write_npz(
        tmp_path, "wrong_rank_fit",
        genotypes=_valid_genotypes(),
        test_fitness_plastic=_valid_fitness().reshape(16, 32),  # 2D
        train_fitness_plastic=_valid_fitness(),
    )
    with pytest.raises(AssertionError, match="test_fitness_plastic ndim"):
        assert_plasticity_final_population_schema(
            p, pop_size=SWEEP_POP_SIZE,
            expected_tape_length=SWEEP_TAPE_LENGTH,
            alphabet_size=SWEEP_ALPHABET_SIZE,
        )


# Class 7: wrong-length fitness (shape[0] != pop_size).
def test_wrong_length_fitness_fails(tmp_path):
    rng = np.random.default_rng(47)
    short = rng.uniform(0.0, 1.0, size=511).astype(np.float32)
    p = _write_npz(
        tmp_path, "wrong_length_fit",
        genotypes=_valid_genotypes(),
        test_fitness_plastic=short,
        train_fitness_plastic=_valid_fitness(),
    )
    with pytest.raises(AssertionError, match=r"test_fitness_plastic\.shape\[0\]"):
        assert_plasticity_final_population_schema(
            p, pop_size=SWEEP_POP_SIZE,
            expected_tape_length=SWEEP_TAPE_LENGTH,
            alphabet_size=SWEEP_ALPHABET_SIZE,
        )


# Class 8: non-floating fitness dtype (int).
def test_non_floating_fitness_fails(tmp_path):
    bad = np.ones(SWEEP_POP_SIZE, dtype=np.int32)
    p = _write_npz(
        tmp_path, "non_floating_fit",
        genotypes=_valid_genotypes(),
        test_fitness_plastic=bad,
        train_fitness_plastic=_valid_fitness(),
    )
    with pytest.raises(AssertionError, match="test_fitness_plastic dtype"):
        assert_plasticity_final_population_schema(
            p, pop_size=SWEEP_POP_SIZE,
            expected_tape_length=SWEEP_TAPE_LENGTH,
            alphabet_size=SWEEP_ALPHABET_SIZE,
        )


# Class 9: NaN fitness.
def test_nan_fitness_fails(tmp_path):
    bad = _valid_fitness()
    bad[100] = np.nan
    p = _write_npz(
        tmp_path, "nan_fit",
        genotypes=_valid_genotypes(),
        test_fitness_plastic=bad,
        train_fitness_plastic=_valid_fitness(),
    )
    with pytest.raises(AssertionError, match="non-finite"):
        assert_plasticity_final_population_schema(
            p, pop_size=SWEEP_POP_SIZE,
            expected_tape_length=SWEEP_TAPE_LENGTH,
            alphabet_size=SWEEP_ALPHABET_SIZE,
        )


# Class 10: Inf fitness.
def test_inf_fitness_fails(tmp_path):
    bad = _valid_fitness()
    bad[200] = np.inf
    p = _write_npz(
        tmp_path, "inf_fit",
        genotypes=_valid_genotypes(),
        test_fitness_plastic=bad,
        train_fitness_plastic=_valid_fitness(),
    )
    with pytest.raises(AssertionError, match="non-finite"):
        assert_plasticity_final_population_schema(
            p, pop_size=SWEEP_POP_SIZE,
            expected_tape_length=SWEEP_TAPE_LENGTH,
            alphabet_size=SWEEP_ALPHABET_SIZE,
        )


# Class 11: out-of-range fitness (> 1.0 or < 0.0; v13).
def test_out_of_range_fitness_fails(tmp_path):
    bad = _valid_fitness()
    bad[300] = 1.5  # > 1.0
    p = _write_npz(
        tmp_path, "out_of_range_fit",
        genotypes=_valid_genotypes(),
        test_fitness_plastic=bad,
        train_fitness_plastic=_valid_fitness(),
    )
    with pytest.raises(AssertionError, match=r"values outside \[0, 1\]"):
        assert_plasticity_final_population_schema(
            p, pop_size=SWEEP_POP_SIZE,
            expected_tape_length=SWEEP_TAPE_LENGTH,
            alphabet_size=SWEEP_ALPHABET_SIZE,
        )


# Class 12: invalid-token genotypes (values >= alphabet_size; v14).
def test_invalid_token_genotypes_fails(tmp_path):
    bad = _valid_genotypes()
    bad[10, 5] = 25  # out of v2_probe's 0..21 range
    p = _write_npz(
        tmp_path, "invalid_token_g",
        genotypes=bad,
        test_fitness_plastic=_valid_fitness(),
        train_fitness_plastic=_valid_fitness(),
    )
    with pytest.raises(AssertionError, match="out-of-alphabet token"):
        assert_plasticity_final_population_schema(
            p, pop_size=SWEEP_POP_SIZE,
            expected_tape_length=SWEEP_TAPE_LENGTH,
            alphabet_size=SWEEP_ALPHABET_SIZE,
        )


# Canonical wrong-length fixture (v14).
def test_wrong_length_canonical_fails():
    # 30-byte canonical (60 hex chars) instead of 32.
    short_hex = "00" * 30
    with pytest.raises(AssertionError, match="canonical_hex decodes to length"):
        assert_canonical_hex_length(
            short_hex,
            expected_tape_length=SWEEP_TAPE_LENGTH,
            alphabet_size=SWEEP_ALPHABET_SIZE,
        )


# Canonical invalid-token fixture (v14 closure per codex-v14 P1).
def test_invalid_token_canonical_fails():
    # 32-byte canonical with token 25 at position 0 (>= v2_probe's 22).
    # Remaining bytes are valid zeros.
    bad_hex = "19" + "00" * 31  # 0x19 = 25
    with pytest.raises(AssertionError, match="tokens outside"):
        assert_canonical_hex_length(
            bad_hex,
            expected_tape_length=SWEEP_TAPE_LENGTH,
            alphabet_size=SWEEP_ALPHABET_SIZE,
        )
