"""Task registry for chem-tape v1.

Each task declares:
  - input generator (with a balanced label distribution)
  - label function
  - task-specific alphabet binding (slot 12 / slot 13)
  - held-out generalization sample (disjoint from training; §Layer 10)

Tasks are built fresh per `(cfg.task, cfg.seed)`; the sub-rng stays fixed for
the lifetime of the evolutionary run so the fitness landscape does not shift
between generations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from . import alphabet as alph
from .config import ChemTapeConfig


# ---------------- Task dataclass ----------------


@dataclass
class Task:
    name: str
    input_type: str                          # "str" | "intlist"
    inputs: list                             # len E, raw inputs
    labels: np.ndarray                       # (E,) int64
    alphabet: alph.TaskAlphabet
    label_fn: Callable[[object], int]
    holdout_inputs: list | None = None
    holdout_labels: np.ndarray | None = None


# ---------------- Sampling helpers ----------------

_STR_ALPHABET = [
    c for c in
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "
]  # 53 chars


def _rand_str(rng: np.random.Generator, length: int = 16) -> str:
    idx = rng.integers(0, len(_STR_ALPHABET), size=length)
    return "".join(_STR_ALPHABET[i] for i in idx)


def _rand_intlist(rng: np.random.Generator, length: int = 4) -> tuple[int, ...]:
    return tuple(int(x) for x in rng.integers(0, 10, size=length))


def _gen_balanced(
    rng: np.random.Generator,
    n: int,
    gen_one: Callable[[np.random.Generator], object],
    label_fn: Callable[[object], int],
    positive_predicate: Callable[[object], bool],
    gen_negative: Callable[[np.random.Generator], object] | None = None,
    exclude: set | None = None,
    max_tries_per_half: int = 100_000,
) -> tuple[list, np.ndarray]:
    """Generate n examples with half satisfying positive_predicate, half not.

    `exclude` is a set of input hashes to reject (used to make the holdout
    disjoint from training). Odd n rounds up in the positive half.

    If `gen_negative` is provided, it is used as a dedicated sampler for the
    negative half (saves massive rejection-sampling cost when one class is
    rare under `gen_one`, e.g. has_upper's "no uppercase" strings). Generated
    negatives are verified against `positive_predicate` and skipped if they
    don't match — the dedicated sampler is trusted but not blindly.
    """
    want_pos = (n + 1) // 2
    want_neg = n - want_pos
    exclude = exclude if exclude is not None else set()

    def _sample_until(n_wanted: int, sampler, expect_positive: bool) -> list:
        out: list = []
        tries = 0
        limit = max_tries_per_half * max(n_wanted, 1)
        while len(out) < n_wanted and tries < limit:
            x = sampler(rng)
            key = repr(x)
            tries += 1
            if key in exclude:
                continue
            if positive_predicate(x) == expect_positive:
                out.append(x)
                exclude.add(key)
        return out

    pos = _sample_until(want_pos, gen_one, True)
    neg_sampler = gen_negative if gen_negative is not None else gen_one
    neg = _sample_until(want_neg, neg_sampler, False)

    inputs = pos + neg
    # Shuffle so positives and negatives interleave.
    order = rng.permutation(len(inputs))
    inputs = [inputs[i] for i in order]
    labels = np.array([label_fn(x) for x in inputs], dtype=np.int64)
    return inputs, labels


# ---------------- Tasks ----------------


def _count_r_label(s: str) -> int:
    return s.count("R")


def _has_upper_label(s: str) -> int:
    return 1 if any(c.isupper() for c in s) else 0


def _has_at_least_1_R_label(s: str) -> int:
    return 1 if "R" in s else 0


def _sum_gt_10_label(xs: tuple[int, ...]) -> int:
    return 1 if sum(xs) > 10 else 0


def _sum_gt_5_label(xs: tuple[int, ...]) -> int:
    return 1 if sum(xs) > 5 else 0


def _build_training_and_holdout(
    seed: int,
    n_train: int,
    n_holdout: int,
    gen_one: Callable[[np.random.Generator], object],
    label_fn: Callable[[object], int],
    positive_predicate: Callable[[object], bool],
    gen_negative: Callable[[np.random.Generator], object] | None = None,
) -> tuple[list, np.ndarray, list | None, np.ndarray | None]:
    train_rng = np.random.default_rng(seed)
    train_inputs, train_labels = _gen_balanced(
        train_rng, n_train, gen_one, label_fn, positive_predicate,
        gen_negative=gen_negative,
    )
    if n_holdout <= 0:
        return train_inputs, train_labels, None, None
    # Disjoint holdout: feed the train keys in as the exclude set.
    exclude = {repr(x) for x in train_inputs}
    hold_rng = np.random.default_rng(seed ^ 0xABCDEF)
    hold_inputs, hold_labels = _gen_balanced(
        hold_rng, n_holdout, gen_one, label_fn, positive_predicate,
        gen_negative=gen_negative, exclude=exclude,
    )
    return train_inputs, train_labels, hold_inputs, hold_labels


def make_count_r_task(cfg: ChemTapeConfig, seed: int) -> Task:
    """count-R: count occurrences of 'R' in a length-16 string over [A-Za-z ]."""
    def gen(rng): return _rand_str(rng, length=16)
    def positive(s): return "R" in s
    train_inp, train_lab, hold_inp, hold_lab = _build_training_and_holdout(
        seed, cfg.n_examples, cfg.holdout_size, gen, _count_r_label, positive
    )
    return Task(
        name="count_r",
        input_type="str",
        inputs=train_inp,
        labels=train_lab,
        alphabet=alph.TaskAlphabet(slot_12=alph.OP_MAP_EQ_R, slot_13=alph.OP_NOP),
        label_fn=_count_r_label,
        holdout_inputs=hold_inp,
        holdout_labels=hold_lab,
    )


def make_has_at_least_1_R_task(cfg: ChemTapeConfig, seed: int) -> Task:
    """has-at-least-1-R: binary version of count_r. Returns 1 if the length-16
    string contains 'R', else 0. Same slot binding as count_r (slot_12 =
    MAP_EQ_R), same domain/generator — differs only in label function (binary
    instead of graded integer). Designed for §v1.5 basin-width test: matched
    scaffold structure, broader-basin criterion.
    """
    _NO_R_ALPHABET = [c for c in "ABCDEFGHIJKLMNOPQSTUVWXYZabcdefghijklmnopqstuvwxyz "]
    def gen(rng): return _rand_str(rng, length=16)
    def gen_neg(rng):
        idx = rng.integers(0, len(_NO_R_ALPHABET), size=16)
        return "".join(_NO_R_ALPHABET[i] for i in idx)
    def positive(s): return "R" in s
    train_inp, train_lab, hold_inp, hold_lab = _build_training_and_holdout(
        seed, cfg.n_examples, cfg.holdout_size, gen, _has_at_least_1_R_label, positive,
        gen_negative=gen_neg,
    )
    return Task(
        name="has_at_least_1_R",
        input_type="str",
        inputs=train_inp,
        labels=train_lab,
        alphabet=alph.TaskAlphabet(slot_12=alph.OP_MAP_EQ_R, slot_13=alph.OP_NOP),
        label_fn=_has_at_least_1_R_label,
        holdout_inputs=hold_inp,
        holdout_labels=hold_lab,
    )


def make_has_upper_task(cfg: ChemTapeConfig, seed: int) -> Task:
    """has-upper: does a length-16 string contain any uppercase character?"""
    # Negatives (no uppercase) have probability ~(27/53)^16 ≈ 2e-5 under the
    # full alphabet, so rejection sampling burns seconds. Draw negatives
    # directly from the non-upper subset (26 lowercase + 1 space).
    _LOWER_ALPHABET = [c for c in "abcdefghijklmnopqrstuvwxyz "]
    def gen(rng): return _rand_str(rng, length=16)
    def gen_neg(rng):
        idx = rng.integers(0, len(_LOWER_ALPHABET), size=16)
        return "".join(_LOWER_ALPHABET[i] for i in idx)
    def positive(s): return any(c.isupper() for c in s)
    train_inp, train_lab, hold_inp, hold_lab = _build_training_and_holdout(
        seed, cfg.n_examples, cfg.holdout_size, gen, _has_upper_label, positive,
        gen_negative=gen_neg,
    )
    return Task(
        name="has_upper",
        input_type="str",
        inputs=train_inp,
        labels=train_lab,
        alphabet=alph.TaskAlphabet(slot_12=alph.OP_MAP_IS_UPPER, slot_13=alph.OP_NOP),
        label_fn=_has_upper_label,
        holdout_inputs=hold_inp,
        holdout_labels=hold_lab,
    )


def make_sum_gt_10_task(cfg: ChemTapeConfig, seed: int) -> Task:
    """sum-gt-10: is the sum of a length-4 intlist (values in [0,9]) > 10?"""
    def gen(rng): return _rand_intlist(rng, length=4)
    def positive(xs): return sum(xs) > 10
    train_inp, train_lab, hold_inp, hold_lab = _build_training_and_holdout(
        seed, cfg.n_examples, cfg.holdout_size, gen, _sum_gt_10_label, positive
    )
    return Task(
        name="sum_gt_10",
        input_type="intlist",
        inputs=train_inp,
        labels=train_lab,
        alphabet=alph.TaskAlphabet(slot_12=alph.OP_NOP, slot_13=alph.OP_NOP),
        label_fn=_sum_gt_10_label,
        holdout_inputs=hold_inp,
        holdout_labels=hold_lab,
    )


def make_sum_gt_5_task(cfg: ChemTapeConfig, seed: int) -> Task:
    """sum-gt-5: threshold-variation sibling of sum-gt-10. Same structure
    (intlist input, same scaffold shape), same basin (binary), differs only
    in threshold constant (5 vs 10). Designed for §v1.5a-internal-control:
    same-structure variation test of the basin-width × scaffold-length
    framework."""
    def gen(rng): return _rand_intlist(rng, length=4)
    def positive(xs): return sum(xs) > 5
    train_inp, train_lab, hold_inp, hold_lab = _build_training_and_holdout(
        seed, cfg.n_examples, cfg.holdout_size, gen, _sum_gt_5_label, positive
    )
    return Task(
        name="sum_gt_5",
        input_type="intlist",
        inputs=train_inp,
        labels=train_lab,
        alphabet=alph.TaskAlphabet(slot_12=alph.OP_NOP, slot_13=alph.OP_NOP),
        label_fn=_sum_gt_5_label,
        holdout_inputs=hold_inp,
        holdout_labels=hold_lab,
    )


# ---------------- v2-probe tasks (architecture-v2.md / experiments-v2.md) ----------------
#
# These task builders require `ChemTapeConfig.alphabet == "v2_probe"` at
# execution time, because they return programs / alphabets that reference
# ids 14..19 (MAP_EQ_E, IF_GT, REDUCE_MAX, THRESHOLD_SLOT). Under
# alphabet="v1" the executor would treat those ids as NOP.


def _any_char_is(target: str, task_name: str, slot_12_op: str):
    """Factory: build an `any_char_is_<target>` binary task.

    Body used by evolution is the 4-cell scan-map-aggregate shape
    `INPUT CHARS slot_12 ANY` (architecture-v2.md §v2.2). `slot_12_op`
    determines which character the MAP primitive flags.
    """
    # Negatives exclude the target char directly — keeps sampling fast
    # (same trick as has_upper's _LOWER_ALPHABET).
    _NO_TARGET = [c for c in _STR_ALPHABET_STR if c != target]

    def _label(s: str) -> int:
        return 1 if target in s else 0

    def _make(cfg: ChemTapeConfig, seed: int) -> Task:
        def gen(rng):
            return _rand_str(rng, length=16)
        def gen_neg(rng):
            idx = rng.integers(0, len(_NO_TARGET), size=16)
            return "".join(_NO_TARGET[i] for i in idx)
        def positive(s):
            return target in s
        train_inp, train_lab, hold_inp, hold_lab = _build_training_and_holdout(
            seed, cfg.n_examples, cfg.holdout_size, gen, _label, positive,
            gen_negative=gen_neg,
        )
        return Task(
            name=task_name,
            input_type="str",
            inputs=train_inp,
            labels=train_lab,
            alphabet=alph.TaskAlphabet(slot_12=slot_12_op, slot_13=alph.OP_NOP),
            label_fn=_label,
            holdout_inputs=hold_inp,
            holdout_labels=hold_lab,
        )

    return _make


_STR_ALPHABET_STR = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "


# §v2.2 Multi-slot indirection: three binary char-scan tasks sharing the same
# 4-cell body `INPUT CHARS slot_12 ANY` and differing only in slot_12 binding.
make_any_char_is_R_task = _any_char_is("R", "any_char_is_R", alph.OP_MAP_EQ_R)
make_any_char_is_E_task = _any_char_is("E", "any_char_is_E", alph.OP_MAP_EQ_E)


def make_any_char_is_upper_v2_task(cfg: ChemTapeConfig, seed: int) -> Task:
    """§v2.2 Pair B: uppercase variant of the char-scan task. Under v2
    alphabet so Pair B can be matched against Pair A directly."""
    _LOWER_ALPHABET = [c for c in "abcdefghijklmnopqrstuvwxyz "]
    def gen(rng):
        return _rand_str(rng, length=16)
    def gen_neg(rng):
        idx = rng.integers(0, len(_LOWER_ALPHABET), size=16)
        return "".join(_LOWER_ALPHABET[i] for i in idx)
    def positive(s):
        return any(c.isupper() for c in s)
    train_inp, train_lab, hold_inp, hold_lab = _build_training_and_holdout(
        seed, cfg.n_examples, cfg.holdout_size, gen, _has_upper_label, positive,
        gen_negative=gen_neg,
    )
    return Task(
        name="any_char_is_upper_v2",
        input_type="str",
        inputs=train_inp,
        labels=train_lab,
        alphabet=alph.TaskAlphabet(slot_12=alph.OP_MAP_IS_UPPER, slot_13=alph.OP_NOP),
        label_fn=_has_upper_label,
        holdout_inputs=hold_inp,
        holdout_labels=hold_lab,
    )


def make_sum_gt_10_v2_task(cfg: ChemTapeConfig, seed: int) -> Task:
    """§v2.1 Part A: sum_gt_10 label function on the v2 alphabet. Semantics
    identical to v1's sum_gt_10 — only the canonical target body differs
    (`CONST_5 CONST_5 ADD` instead of `CONST_1 + DUP + ADD` chain).
    """
    def gen(rng):
        return _rand_intlist(rng, length=4)
    def positive(xs):
        return sum(xs) > 10
    train_inp, train_lab, hold_inp, hold_lab = _build_training_and_holdout(
        seed, cfg.n_examples, cfg.holdout_size, gen, _sum_gt_10_label, positive
    )
    return Task(
        name="sum_gt_10_v2",
        input_type="intlist",
        inputs=train_inp,
        labels=train_lab,
        alphabet=alph.TaskAlphabet(slot_12=alph.OP_NOP, slot_13=alph.OP_NOP),
        label_fn=_sum_gt_10_label,
        holdout_inputs=hold_inp,
        holdout_labels=hold_lab,
    )


def _make_sum_gt_slot_task(threshold: int, task_name: str):
    """§v2.3 factory: `INPUT SUM THRESHOLD_SLOT GT` with the threshold bound
    via `TaskAlphabet.threshold`. Two instances — `sum_gt_5_slot` and
    `sum_gt_10_slot` — share the identical token body and differ only in
    `threshold`.
    """
    def _label(xs: tuple[int, ...]) -> int:
        return 1 if sum(xs) > threshold else 0

    def _make(cfg: ChemTapeConfig, seed: int) -> Task:
        def gen(rng):
            return _rand_intlist(rng, length=4)
        def positive(xs):
            return sum(xs) > threshold
        train_inp, train_lab, hold_inp, hold_lab = _build_training_and_holdout(
            seed, cfg.n_examples, cfg.holdout_size, gen, _label, positive
        )
        return Task(
            name=task_name,
            input_type="intlist",
            inputs=train_inp,
            labels=train_lab,
            alphabet=alph.TaskAlphabet(
                slot_12=alph.OP_NOP,
                slot_13=alph.OP_NOP,
                threshold=threshold,
            ),
            label_fn=_label,
            holdout_inputs=hold_inp,
            holdout_labels=hold_lab,
        )

    return _make


make_sum_gt_5_slot_task = _make_sum_gt_slot_task(5, "sum_gt_5_slot")
make_sum_gt_10_slot_task = _make_sum_gt_slot_task(10, "sum_gt_10_slot")


def _compositional_label(xs: tuple[int, ...], op: str) -> int:
    s_pred = 1 if sum(xs) > 10 else 0
    m_pred = 1 if max(xs, default=0) > 5 else 0
    if op == "AND":
        return 1 if (s_pred and m_pred) else 0
    return 1 if (s_pred or m_pred) else 0


def _make_compositional_task(op: str, task_name: str):
    """§v2.4 factory for `sum_gt_10_{AND,OR}_max_gt_5`. Binary label on
    length-4 intlists (values in [0,9]). Uses v2 IF_GT semantics."""
    def _label(xs):
        return _compositional_label(xs, op)

    def _make(cfg: ChemTapeConfig, seed: int) -> Task:
        def gen(rng):
            return _rand_intlist(rng, length=4)
        def positive(xs):
            return _label(xs) == 1
        train_inp, train_lab, hold_inp, hold_lab = _build_training_and_holdout(
            seed, cfg.n_examples, cfg.holdout_size, gen, _label, positive
        )
        return Task(
            name=task_name,
            input_type="intlist",
            inputs=train_inp,
            labels=train_lab,
            alphabet=alph.TaskAlphabet(slot_12=alph.OP_NOP, slot_13=alph.OP_NOP),
            label_fn=_label,
            holdout_inputs=hold_inp,
            holdout_labels=hold_lab,
        )

    return _make


make_sum_gt_10_AND_max_gt_5_task = _make_compositional_task("AND", "sum_gt_10_AND_max_gt_5")
make_sum_gt_10_OR_max_gt_5_task = _make_compositional_task("OR", "sum_gt_10_OR_max_gt_5")


def _make_agg_task(
    aggregator_op: str,
    threshold: int,
    task_name: str,
    label_fn: Callable[[tuple[int, ...]], int],
):
    """§v2.5 factory: aggregator-variation pair sharing body
    `INPUT slot_13 THRESHOLD_SLOT GT` with slot_13 bound to REDUCE_ADD or
    REDUCE_MAX and threshold task-bound.
    """
    def _make(cfg: ChemTapeConfig, seed: int) -> Task:
        def gen(rng):
            return _rand_intlist(rng, length=4)
        def positive(xs):
            return label_fn(xs) == 1
        train_inp, train_lab, hold_inp, hold_lab = _build_training_and_holdout(
            seed, cfg.n_examples, cfg.holdout_size, gen, label_fn, positive
        )
        return Task(
            name=task_name,
            input_type="intlist",
            inputs=train_inp,
            labels=train_lab,
            alphabet=alph.TaskAlphabet(
                slot_12=alph.OP_NOP,
                slot_13=aggregator_op,
                threshold=threshold,
            ),
            label_fn=label_fn,
            holdout_inputs=hold_inp,
            holdout_labels=hold_lab,
        )

    return _make


def _max_gt_5_label(xs: tuple[int, ...]) -> int:
    return 1 if max(xs, default=0) > 5 else 0


make_agg_sum_gt_10_task = _make_agg_task(alph.OP_REDUCE_ADD, 10, "agg_sum_gt_10", _sum_gt_10_label)
make_agg_max_gt_5_task = _make_agg_task(alph.OP_REDUCE_MAX, 5, "agg_max_gt_5", _max_gt_5_label)


TASK_REGISTRY = {
    # v1 (unchanged).
    "count_r": make_count_r_task,
    "has_at_least_1_R": make_has_at_least_1_R_task,
    "has_upper": make_has_upper_task,
    "sum_gt_10": make_sum_gt_10_task,
    "sum_gt_5": make_sum_gt_5_task,
    # v2-probe (require cfg.alphabet == "v2_probe").
    "any_char_is_R": make_any_char_is_R_task,
    "any_char_is_E": make_any_char_is_E_task,
    "any_char_is_upper_v2": make_any_char_is_upper_v2_task,
    "sum_gt_10_v2": make_sum_gt_10_v2_task,
    "sum_gt_5_slot": make_sum_gt_5_slot_task,
    "sum_gt_10_slot": make_sum_gt_10_slot_task,
    "sum_gt_10_AND_max_gt_5": make_sum_gt_10_AND_max_gt_5_task,
    "sum_gt_10_OR_max_gt_5": make_sum_gt_10_OR_max_gt_5_task,
    "agg_sum_gt_10": make_agg_sum_gt_10_task,
    "agg_max_gt_5": make_agg_max_gt_5_task,
}


def build_task(cfg: ChemTapeConfig, seed: int) -> Task:
    if cfg.task not in TASK_REGISTRY:
        raise KeyError(f"Unknown task {cfg.task!r}; known: {list(TASK_REGISTRY)}")
    return TASK_REGISTRY[cfg.task](cfg, seed)
