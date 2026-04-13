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
    exclude: set | None = None,
    max_tries_per_half: int = 100_000,
) -> tuple[list, np.ndarray]:
    """Generate n examples with half satisfying positive_predicate, half not.

    `exclude` is a set of input hashes to reject (used to make the holdout
    disjoint from training). Odd n rounds up in the positive half.
    """
    want_pos = (n + 1) // 2
    want_neg = n - want_pos
    pos: list = []
    neg: list = []
    exclude = exclude if exclude is not None else set()
    tries = 0
    limit = max_tries_per_half * n
    while (len(pos) < want_pos or len(neg) < want_neg) and tries < limit:
        x = gen_one(rng)
        key = repr(x)
        if key in exclude:
            tries += 1
            continue
        if positive_predicate(x) and len(pos) < want_pos:
            pos.append(x)
            exclude.add(key)
        elif not positive_predicate(x) and len(neg) < want_neg:
            neg.append(x)
            exclude.add(key)
        tries += 1
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


def _sum_gt_10_label(xs: tuple[int, ...]) -> int:
    return 1 if sum(xs) > 10 else 0


def _build_training_and_holdout(
    seed: int,
    n_train: int,
    n_holdout: int,
    gen_one: Callable[[np.random.Generator], object],
    label_fn: Callable[[object], int],
    positive_predicate: Callable[[object], bool],
) -> tuple[list, np.ndarray, list | None, np.ndarray | None]:
    train_rng = np.random.default_rng(seed)
    train_inputs, train_labels = _gen_balanced(
        train_rng, n_train, gen_one, label_fn, positive_predicate
    )
    if n_holdout <= 0:
        return train_inputs, train_labels, None, None
    # Disjoint holdout: feed the train keys in as the exclude set.
    exclude = {repr(x) for x in train_inputs}
    hold_rng = np.random.default_rng(seed ^ 0xABCDEF)
    hold_inputs, hold_labels = _gen_balanced(
        hold_rng, n_holdout, gen_one, label_fn, positive_predicate, exclude=exclude
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


def make_has_upper_task(cfg: ChemTapeConfig, seed: int) -> Task:
    """has-upper: does a length-16 string contain any uppercase character?"""
    def gen(rng): return _rand_str(rng, length=16)
    def positive(s): return any(c.isupper() for c in s)
    train_inp, train_lab, hold_inp, hold_lab = _build_training_and_holdout(
        seed, cfg.n_examples, cfg.holdout_size, gen, _has_upper_label, positive
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


TASK_REGISTRY = {
    "count_r": make_count_r_task,
    "has_upper": make_has_upper_task,
    "sum_gt_10": make_sum_gt_10_task,
}


def build_task(cfg: ChemTapeConfig, seed: int) -> Task:
    if cfg.task not in TASK_REGISTRY:
        raise KeyError(f"Unknown task {cfg.task!r}; known: {list(TASK_REGISTRY)}")
    return TASK_REGISTRY[cfg.task](cfg, seed)
