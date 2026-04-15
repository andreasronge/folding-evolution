"""Differential test for the population-batch Rust executor.

The new `rust_chem_execute_pop_batch` entry point parallelises execution over
programs via Rayon and returns a flat `Vec<i64>` of length P*E. This harness
pins two equivalences:

1. **Rust-internal:** pop_batch(programs, inputs) equals the per-program
   `rust_chem_execute` for every (p, e) cell, under both v1 and v2_probe
   alphabets. Catches rayon partitioning bugs, shared-state corruption,
   or off-by-one indexing in row packing.

2. **Python↔Rust:** pop_batch equals the reference Python executor on a
   smaller shape (covered to keep total test time low — the existing
   differential suites already do full Py↔Rust parity per-single-program).
"""

from __future__ import annotations

import random

import pytest

from folding_evolution.chem_tape import alphabet as alph
from folding_evolution.chem_tape.executor import execute_program as py_execute
from _folding_rust import (  # type: ignore
    rust_chem_execute,
    rust_chem_execute_pop_batch,
)


def _to_i64(x: int) -> int:
    return ((int(x) + (1 << 63)) % (1 << 64)) - (1 << 63)


def _gen_program_v1(rng: random.Random, length: int) -> list[int]:
    return [rng.randint(0, 15) for _ in range(length)]


def _gen_program_v2(rng: random.Random, length: int) -> list[int]:
    return [rng.randint(0, 21) for _ in range(length)]


def _gen_str(rng: random.Random, length: int) -> str:
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ RE"
    return "".join(rng.choice(chars) for _ in range(length))


def _gen_intlist(rng: random.Random, length: int) -> tuple[int, ...]:
    return tuple(rng.randint(-5, 20) for _ in range(length))


SLOTS_V1 = [alph.OP_NOP, alph.OP_MAP_EQ_R, alph.OP_MAP_IS_UPPER]
SLOTS_V2 = [
    alph.OP_NOP,
    alph.OP_MAP_EQ_R,
    alph.OP_MAP_IS_UPPER,
    alph.OP_MAP_EQ_E,
    alph.OP_REDUCE_ADD,
    alph.OP_REDUCE_MAX,
]


def _pop_batch_flat_to_rows(flat, n_programs, n_inputs):
    assert len(flat) == n_programs * n_inputs, (
        f"flat shape mismatch: got {len(flat)}, expected {n_programs * n_inputs}"
    )
    return [list(flat[p * n_inputs:(p + 1) * n_inputs]) for p in range(n_programs)]


# -----------------------------------------------------------------------------
# 1. Rust-internal equivalence: pop_batch == per-program rust_chem_execute loop.
# -----------------------------------------------------------------------------


_ALPH_SALT = {"v1": 0x11, "v2_probe": 0x22}
_KIND_SALT = {"str": 0xA0, "intlist": 0xB0}


@pytest.mark.parametrize("alphabet_name,gen_program,slots", [
    ("v1", _gen_program_v1, SLOTS_V1),
    ("v2_probe", _gen_program_v2, SLOTS_V2),
])
@pytest.mark.parametrize("input_kind", ["str", "intlist"])
def test_pop_batch_matches_per_program_rust(alphabet_name, gen_program, slots, input_kind):
    # PYTHONHASHSEED-stable: use literal per-axis salts instead of hash().
    rng = random.Random(0xC0FFEE ^ _ALPH_SALT[alphabet_name] ^ _KIND_SALT[input_kind])
    n_programs = 64
    n_inputs = 16
    prog_len = 20

    programs = [gen_program(rng, prog_len) for _ in range(n_programs)]
    if input_kind == "str":
        inputs = [_gen_str(rng, 12) for _ in range(n_inputs)]
    else:
        inputs = [_gen_intlist(rng, 4) for _ in range(n_inputs)]

    s12 = rng.choice(slots)
    s13 = rng.choice(slots)
    threshold = rng.randint(-3, 20)

    flat = rust_chem_execute_pop_batch(
        [[int(t) for t in p] for p in programs],
        s12, s13, inputs, input_kind,
        alphabet_name=alphabet_name, threshold=threshold,
    )
    rows = _pop_batch_flat_to_rows(flat, n_programs, n_inputs)

    for pi, prog in enumerate(programs):
        for ei, inp in enumerate(inputs):
            expected = rust_chem_execute(
                [int(t) for t in prog], s12, s13, inp, input_kind,
                alphabet_name=alphabet_name, threshold=threshold,
            )
            got = rows[pi][ei]
            assert got == expected, (
                f"pop_batch divergence at (p={pi}, e={ei}) under {alphabet_name}:\n"
                f"  program  = {prog}\n"
                f"  input    = {inp!r}\n"
                f"  expected = {expected}\n"
                f"  got      = {got}"
            )


# -----------------------------------------------------------------------------
# 2. Python↔Rust parity on smaller shape — both alphabets, both input types.
# -----------------------------------------------------------------------------


@pytest.mark.parametrize("alphabet_name,gen_program,slots", [
    ("v1", _gen_program_v1, SLOTS_V1),
    ("v2_probe", _gen_program_v2, SLOTS_V2),
])
@pytest.mark.parametrize("input_kind", ["str", "intlist"])
def test_pop_batch_matches_python_reference(alphabet_name, gen_program, slots, input_kind):
    rng = random.Random(0xBEEF ^ _ALPH_SALT[alphabet_name] ^ _KIND_SALT[input_kind])
    n_programs = 8
    n_inputs = 4
    prog_len = 16

    programs = [gen_program(rng, prog_len) for _ in range(n_programs)]
    if input_kind == "str":
        inputs = [_gen_str(rng, 10) for _ in range(n_inputs)]
    else:
        inputs = [_gen_intlist(rng, 4) for _ in range(n_inputs)]

    s12 = rng.choice(slots)
    s13 = rng.choice(slots)
    threshold = rng.randint(-3, 15)
    task_alph = alph.TaskAlphabet(slot_12=s12, slot_13=s13, threshold=threshold)

    flat = rust_chem_execute_pop_batch(
        [[int(t) for t in p] for p in programs],
        s12, s13, inputs, input_kind,
        alphabet_name=alphabet_name, threshold=threshold,
    )
    rows = _pop_batch_flat_to_rows(flat, n_programs, n_inputs)

    for pi, prog in enumerate(programs):
        for ei, inp in enumerate(inputs):
            expected = _to_i64(py_execute(
                prog, task_alph, inp, input_kind, alphabet_name=alphabet_name,
            ))
            got = rows[pi][ei]
            assert got == expected, (
                f"pop_batch vs python divergence at (p={pi}, e={ei}) under {alphabet_name}:\n"
                f"  program  = {prog}\n"
                f"  input    = {inp!r}\n"
                f"  expected = {expected}\n"
                f"  got      = {got}"
            )


# -----------------------------------------------------------------------------
# 3. Edge cases: empty program, empty inputs.
# -----------------------------------------------------------------------------


def test_pop_batch_empty_inputs():
    """Zero inputs → zero output cells per program."""
    flat = rust_chem_execute_pop_batch(
        [[int(t) for t in [1, 5, 7, 8]]],
        alph.OP_NOP, alph.OP_NOP, [], "intlist",
        alphabet_name="v1",
    )
    assert flat == []


def test_pop_batch_empty_program_tape():
    """Empty program tape → executor pushes default int 0 (spec §Layer 3)."""
    flat = rust_chem_execute_pop_batch(
        [[]],
        alph.OP_NOP, alph.OP_NOP, [(1, 2, 3, 4)], "intlist",
        alphabet_name="v1",
    )
    assert flat == [0]


# -----------------------------------------------------------------------------
# 4. Forced-parallel Rayon execution: shape the workload so rayon partitions
#    across multiple threads, then confirm row ordering is stable across runs
#    and matches the serial reference. Catches thread-interleaving bugs
#    (mis-ordered chunks, shared-state corruption) that single-threaded
#    testing would miss.
# -----------------------------------------------------------------------------


def test_pop_batch_rayon_parallel_stability(monkeypatch):
    """Run the same pop_batch twice at large-P and compare to the sequential
    per-program reference. Rayon thread count is already controlled by the
    surrounding test environment — this test calls pop_batch at a shape
    (P=512, E=8) that forces par_iter to actually chunk across workers.
    """
    # Unset RAYON_NUM_THREADS for this test so rayon picks num_cpus threads.
    monkeypatch.delenv("RAYON_NUM_THREADS", raising=False)

    rng = random.Random(0xDEADBEEF)
    n_programs = 512
    n_inputs = 8
    prog_len = 22

    programs = [_gen_program_v2(rng, prog_len) for _ in range(n_programs)]
    inputs = [_gen_intlist(rng, 4) for _ in range(n_inputs)]

    kwargs = dict(
        slot_12=alph.OP_MAP_EQ_R, slot_13=alph.OP_REDUCE_MAX,
        input_values=inputs, input_type="intlist",
        alphabet_name="v2_probe", threshold=7,
    )

    # Two consecutive runs — if there's a parallelism-dependent ordering bug,
    # they'll diverge (or diverge from the serial reference below).
    flat1 = rust_chem_execute_pop_batch(
        [[int(t) for t in p] for p in programs], **kwargs,
    )
    flat2 = rust_chem_execute_pop_batch(
        [[int(t) for t in p] for p in programs], **kwargs,
    )
    assert flat1 == flat2, "pop_batch output not stable across consecutive runs"

    # Serial reference: build the same answers one program at a time.
    reference = []
    for prog in programs:
        for inp in inputs:
            reference.append(rust_chem_execute(
                [int(t) for t in prog],
                kwargs["slot_12"], kwargs["slot_13"], inp, kwargs["input_type"],
                alphabet_name=kwargs["alphabet_name"], threshold=kwargs["threshold"],
            ))
    assert flat1 == reference, "pop_batch diverges from serial per-program execution"
