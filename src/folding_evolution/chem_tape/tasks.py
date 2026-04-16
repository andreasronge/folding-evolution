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


# §v2.4-alt: body-matched compositional AND pair. Both tasks use the identical
# canonical body template
#     CONST_0 INPUT REDUCE_MAX CONST_5 GT INPUT SUM THRESHOLD_SLOT GT IF_GT
# and differ *only* in the task-bound `threshold` integer (5 vs 10). Disentangles
# compositional-depth from decode-position hypotheses left open by §v2.4.
# Label: 1 iff (max(input) > 5) AND (sum(input) > threshold).


def _make_compound_and_slot_task(threshold: int, task_name: str):
    def _label(xs: tuple[int, ...]) -> int:
        return 1 if (max(xs, default=0) > 5 and sum(xs) > threshold) else 0

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


make_compound_and_sum_gt_5_max_gt_5_slot_task = _make_compound_and_slot_task(
    5, "compound_and_sum_gt_5_max_gt_5_slot"
)
make_compound_and_sum_gt_10_max_gt_5_slot_task = _make_compound_and_slot_task(
    10, "compound_and_sum_gt_10_max_gt_5_slot"
)


# §v2.4-proxy: same AND label as §v2.4, but trained under a sampler that
# decorrelates `max > 5` from the label. Four-way stratified balanced sampling
# across (label, max>5) gives P(max>5|+) = P(max>5|−) = 0.5, so `max > 5`
# alone is a 0.50 predictor (vs ~0.92 under §v2.4's natural sampling).


def _sum_gt_10_and_max_gt_5(xs: tuple[int, ...]) -> int:
    return 1 if (sum(xs) > 10 and max(xs, default=0) > 5) else 0


def _sample_and_cohort_0_9(
    rng: np.random.Generator,
    cohort: str,
    max_tries: int = 100_000,
) -> tuple[int, ...]:
    """Draw a length-4 intlist over [0,9] matching one of five cohorts:
      "pos"          = sum>10 AND max>5        (label=1; all have max>5)
      "neg_max_hi"   = sum≤10 AND max>5        (label=0; has max>5)
      "neg_max_lo"   = max≤5                   (label=0; no max>5, sum any)
      "neg_hi_lo"    = sum>10 AND max≤5        (label=0; §v2.4-proxy-2 dual-decorr)
      "neg_lo_hi"    = sum≤10 AND max>5        (label=0; alias for neg_max_hi)
    """
    for _ in range(max_tries):
        xs = tuple(int(x) for x in rng.integers(0, 10, size=4))
        s = sum(xs)
        m = max(xs)
        if cohort == "pos" and s > 10 and m > 5:
            return xs
        if cohort == "neg_max_hi" and s <= 10 and m > 5:
            return xs
        if cohort == "neg_max_lo" and m <= 5:
            return xs
        if cohort == "neg_hi_lo" and s > 10 and m <= 5:
            return xs
        if cohort == "neg_lo_hi" and s <= 10 and m > 5:
            return xs
    raise RuntimeError(f"Failed cohort sample ({cohort}) in {max_tries} tries")


def _build_decorrelated_and_training(
    seed: int,
    n_train: int,
    n_holdout: int,
) -> tuple[list, np.ndarray, list | None, np.ndarray | None]:
    """Label-balanced 50/50 with max>5 decorrelated across negatives.

    Target proportions: 50% positives (all with max>5 by AND construction),
    25% neg_max_hi (max>5 AND sum≤10), 25% neg_max_lo (max≤5). Under this
    sampler, P(max>5 | +) = 1.0 and P(max>5 | −) = 0.5, so the `max > 5`
    predictor alone scores accuracy = 32/64 · 1.0 + 32/64 · 0.5 ≈ 0.75
    vs ~0.92 under the natural sampler (§v2.4) — substantial weakening.
    Perfect decorrelation (P(max>5|−) = 1.0) would collapse the task to
    sum_gt_10_v2; this partial decorrelation preserves AND structure.
    """
    def _draw(rng_for, n: int, exclude: set) -> list[tuple[int, ...]]:
        n_pos = n // 2
        n_neg_hi = n // 4
        n_neg_lo = n - n_pos - n_neg_hi
        targets = [("pos", n_pos), ("neg_max_hi", n_neg_hi), ("neg_max_lo", n_neg_lo)]
        out: list[tuple[int, ...]] = []
        for cohort, want in targets:
            got = 0
            while got < want:
                xs = _sample_and_cohort_0_9(rng_for, cohort)
                key = repr(xs)
                if key in exclude:
                    continue
                out.append(xs)
                exclude.add(key)
                got += 1
        return out

    train_rng = np.random.default_rng(seed)
    exclude: set = set()
    train_inputs = _draw(train_rng, n_train, exclude)
    order = train_rng.permutation(len(train_inputs))
    train_inputs = [train_inputs[i] for i in order]
    train_labels = np.array(
        [_sum_gt_10_and_max_gt_5(xs) for xs in train_inputs], dtype=np.int64
    )
    if n_holdout <= 0:
        return train_inputs, train_labels, None, None
    hold_rng = np.random.default_rng(seed ^ 0xABCDEF)
    hold_inputs = _draw(hold_rng, n_holdout, exclude)
    order = hold_rng.permutation(len(hold_inputs))
    hold_inputs = [hold_inputs[i] for i in order]
    hold_labels = np.array(
        [_sum_gt_10_and_max_gt_5(xs) for xs in hold_inputs], dtype=np.int64
    )
    return train_inputs, train_labels, hold_inputs, hold_labels


def make_sum_gt_10_AND_max_gt_5_decorr_task(cfg: ChemTapeConfig, seed: int) -> Task:
    train_inp, train_lab, hold_inp, hold_lab = _build_decorrelated_and_training(
        seed, cfg.n_examples, cfg.holdout_size
    )
    return Task(
        name="sum_gt_10_AND_max_gt_5_decorr",
        input_type="intlist",
        inputs=train_inp,
        labels=train_lab,
        alphabet=alph.TaskAlphabet(slot_12=alph.OP_NOP, slot_13=alph.OP_NOP),
        label_fn=_sum_gt_10_and_max_gt_5,
        holdout_inputs=hold_inp,
        holdout_labels=hold_lab,
    )


# §v2.4-proxy-2: dual-proxy decorrelation. Simultaneous weakening of both
# `max > 5` and `sum > 10` from ~0.92/0.91 accuracy to 0.75. Negatives are
# split 50/50 between neg_hi_lo (sum>10, max≤5) and neg_lo_hi (max>5, sum≤10).
# No neg_lo_lo (max≤5 AND sum≤10) examples — by design to maximize
# decorrelation of both top-2 proxies simultaneously.


def _build_dual_decorr_and_training(
    seed: int,
    n_train: int,
    n_holdout: int,
) -> tuple[list, np.ndarray, list | None, np.ndarray | None]:
    """Label-balanced 50/50 with BOTH max>5 and sum>10 decorrelated.

    Target proportions: 50% positives (sum>10 AND max>5),
    25% neg_hi_lo (sum>10 AND max≤5), 25% neg_lo_hi (max>5 AND sum≤10).
    Under this sampler:
      P(max>5 | neg) = 0.50 → `max > 5` predictor accuracy ≈ 0.75
      P(sum>10 | neg) = 0.50 → `sum > 10` predictor accuracy ≈ 0.75
    """
    def _draw(rng_for, n: int, exclude: set) -> list[tuple[int, ...]]:
        n_pos = n // 2
        n_neg_hi_lo = n // 4
        n_neg_lo_hi = n - n_pos - n_neg_hi_lo
        targets = [
            ("pos", n_pos),
            ("neg_hi_lo", n_neg_hi_lo),
            ("neg_lo_hi", n_neg_lo_hi),
        ]
        out: list[tuple[int, ...]] = []
        for cohort, want in targets:
            got = 0
            while got < want:
                xs = _sample_and_cohort_0_9(rng_for, cohort)
                key = repr(xs)
                if key in exclude:
                    continue
                out.append(xs)
                exclude.add(key)
                got += 1
        return out

    train_rng = np.random.default_rng(seed)
    exclude: set = set()
    train_inputs = _draw(train_rng, n_train, exclude)
    order = train_rng.permutation(len(train_inputs))
    train_inputs = [train_inputs[i] for i in order]
    train_labels = np.array(
        [_sum_gt_10_and_max_gt_5(xs) for xs in train_inputs], dtype=np.int64
    )
    if n_holdout <= 0:
        return train_inputs, train_labels, None, None
    hold_rng = np.random.default_rng(seed ^ 0xABCDEF)
    hold_inputs = _draw(hold_rng, n_holdout, exclude)
    order = hold_rng.permutation(len(hold_inputs))
    hold_inputs = [hold_inputs[i] for i in order]
    hold_labels = np.array(
        [_sum_gt_10_and_max_gt_5(xs) for xs in hold_inputs], dtype=np.int64
    )
    return train_inputs, train_labels, hold_inputs, hold_labels


def make_sum_gt_10_AND_max_gt_5_dual_decorr_task(
    cfg: ChemTapeConfig, seed: int
) -> Task:
    train_inp, train_lab, hold_inp, hold_lab = _build_dual_decorr_and_training(
        seed, cfg.n_examples, cfg.holdout_size
    )
    return Task(
        name="sum_gt_10_AND_max_gt_5_dual_decorr",
        input_type="intlist",
        inputs=train_inp,
        labels=train_lab,
        alphabet=alph.TaskAlphabet(slot_12=alph.OP_NOP, slot_13=alph.OP_NOP),
        label_fn=_sum_gt_10_and_max_gt_5,
        holdout_inputs=hold_inp,
        holdout_labels=hold_lab,
    )


# §v2.6: three additional body-invariant constant-indirection pairs. Tests
# whether §v2.3's 80/80 on sum_gt_{5,10}_slot generalises across task families.


# Pair 1 — string-domain count. Body: INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT.
# Label: 1 iff count('R' in s) > threshold. Slot_12 = MAP_EQ_R.


def _make_any_char_count_gt_slot_task(threshold: int, task_name: str, target: str):
    _STR_NO_TARGET = [c for c in _STR_ALPHABET_STR if c != target]

    def _label(s: str) -> int:
        return 1 if s.count(target) > threshold else 0

    def _make(cfg: ChemTapeConfig, seed: int) -> Task:
        def gen(rng):
            return _rand_str(rng, length=16)
        def gen_neg(rng):
            # Fast negatives: strings with count(target) ≤ threshold biased via
            # sparser target injection. At threshold≥1 the natural sampler is
            # already fine, but for very tight thresholds we still rejection-
            # sample from it — simpler and threshold-robust.
            return _rand_str(rng, length=16)
        def positive(s):
            return s.count(target) > threshold
        train_inp, train_lab, hold_inp, hold_lab = _build_training_and_holdout(
            seed, cfg.n_examples, cfg.holdout_size, gen, _label, positive,
            gen_negative=gen_neg,
        )
        return Task(
            name=task_name,
            input_type="str",
            inputs=train_inp,
            labels=train_lab,
            alphabet=alph.TaskAlphabet(
                slot_12=alph.OP_MAP_EQ_R,
                slot_13=alph.OP_NOP,
                threshold=threshold,
            ),
            label_fn=_label,
            holdout_inputs=hold_inp,
            holdout_labels=hold_lab,
        )

    return _make


make_any_char_count_gt_1_slot_task = _make_any_char_count_gt_slot_task(
    1, "any_char_count_gt_1_slot", "R"
)
make_any_char_count_gt_3_slot_task = _make_any_char_count_gt_slot_task(
    3, "any_char_count_gt_3_slot", "R"
)


# Pair 2 — wider integer range. Body: INPUT SUM THRESHOLD_SLOT GT on length-4
# intlists over [0,12]. Thresholds {7, 13}. Factory mirrors _make_sum_gt_slot_task
# but with configurable range.


def _rand_intlist_range(rng: np.random.Generator, length: int, hi_exclusive: int) -> tuple[int, ...]:
    return tuple(int(x) for x in rng.integers(0, hi_exclusive, size=length))


def _make_sum_gt_slot_range_task(threshold: int, hi_exclusive: int, task_name: str):
    def _label(xs: tuple[int, ...]) -> int:
        return 1 if sum(xs) > threshold else 0

    def _make(cfg: ChemTapeConfig, seed: int) -> Task:
        def gen(rng):
            return _rand_intlist_range(rng, 4, hi_exclusive)
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


make_sum_gt_7_slot_r12_task = _make_sum_gt_slot_range_task(7, 13, "sum_gt_7_slot_r12")
make_sum_gt_13_slot_r12_task = _make_sum_gt_slot_range_task(13, 13, "sum_gt_13_slot_r12")

# §v2.6'-Pair2 redesigned (Plans/prereg_v2_6_pair2_redesigned.md): same body shape
# `INPUT SUM THRESHOLD_SLOT GT` over [0,12], thresholds picked to land Fmin
# intermediate. Phase A scout chooses one of three candidate pairs.
make_sum_gt_18_slot_r12_task = _make_sum_gt_slot_range_task(18, 13, "sum_gt_18_slot_r12")
make_sum_gt_22_slot_r12_task = _make_sum_gt_slot_range_task(22, 13, "sum_gt_22_slot_r12")
make_sum_gt_24_slot_r12_task = _make_sum_gt_slot_range_task(24, 13, "sum_gt_24_slot_r12")
make_sum_gt_28_slot_r12_task = _make_sum_gt_slot_range_task(28, 13, "sum_gt_28_slot_r12")
make_sum_gt_30_slot_r12_task = _make_sum_gt_slot_range_task(30, 13, "sum_gt_30_slot_r12")


# Pair 3 — aggregator variant. Body: INPUT REDUCE_MAX THRESHOLD_SLOT GT.
# Thresholds {5, 7} on [0,9] (tightened from doc-draft {2,5} to avoid swamp).


def _make_reduce_max_gt_slot_task(threshold: int, task_name: str):
    def _label(xs: tuple[int, ...]) -> int:
        return 1 if max(xs, default=0) > threshold else 0

    def _make(cfg: ChemTapeConfig, seed: int) -> Task:
        def gen(rng):
            return _rand_intlist(rng, length=4)
        def positive(xs):
            return max(xs, default=0) > threshold
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
                slot_13=alph.OP_REDUCE_MAX,
                threshold=threshold,
            ),
            label_fn=_label,
            holdout_inputs=hold_inp,
            holdout_labels=hold_lab,
        )

    return _make


make_reduce_max_gt_5_slot_task = _make_reduce_max_gt_slot_task(5, "reduce_max_gt_5_slot")
make_reduce_max_gt_7_slot_task = _make_reduce_max_gt_slot_task(7, "reduce_max_gt_7_slot")


# §v2.8 (Plans/prereg_v2_8_integer_6token.md): 6-token integer-domain body to
# disambiguate body-length from input-domain on Pair 1's failure. Canonical
# body `INPUT SUM CONST_2 ADD THRESHOLD_SLOT GT` evaluates `(sum + 2) > t`
# which equals `sum > t - 2`. The +2 offset forces the canonical body to be
# 6 tokens AND use THRESHOLD_SLOT — the 4-token alternative `INPUT SUM
# CONST_C GT` requires constructing constant `t-2` from {CONST_0,1,2,5},
# which costs ≥ 4 additional ADD-chain tokens for the relevant thresholds
# (15..25), making the 6-token slot body the cheapest path.
def _make_sum_plus2_gt_slot_task(threshold: int, task_name: str):
    def _label(xs: tuple[int, ...]) -> int:
        return 1 if (sum(xs) + 2) > threshold else 0

    def _make(cfg: ChemTapeConfig, seed: int) -> Task:
        def gen(rng):
            return _rand_intlist(rng, length=4)
        def positive(xs):
            return (sum(xs) + 2) > threshold
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


make_sum_plus2_gt_15_slot_task = _make_sum_plus2_gt_slot_task(15, "sum_plus2_gt_15_slot")
make_sum_plus2_gt_17_slot_task = _make_sum_plus2_gt_slot_task(17, "sum_plus2_gt_17_slot")
make_sum_plus2_gt_20_slot_task = _make_sum_plus2_gt_slot_task(20, "sum_plus2_gt_20_slot")
make_sum_plus2_gt_22_slot_task = _make_sum_plus2_gt_slot_task(22, "sum_plus2_gt_22_slot")
make_sum_plus2_gt_25_slot_task = _make_sum_plus2_gt_slot_task(25, "sum_plus2_gt_25_slot")


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
    # §v2.4-alt: body-matched compositional pair (shared IF_GT+CONST_0 body).
    "compound_and_sum_gt_5_max_gt_5_slot": make_compound_and_sum_gt_5_max_gt_5_slot_task,
    "compound_and_sum_gt_10_max_gt_5_slot": make_compound_and_sum_gt_10_max_gt_5_slot_task,
    # §v2.4-proxy: max>5 decorrelated from label via stratified sampling.
    "sum_gt_10_AND_max_gt_5_decorr": make_sum_gt_10_AND_max_gt_5_decorr_task,
    # §v2.4-proxy-2: both max>5 AND sum>10 decorrelated simultaneously.
    "sum_gt_10_AND_max_gt_5_dual_decorr": make_sum_gt_10_AND_max_gt_5_dual_decorr_task,
    # §v2.6: three body-invariant constant-indirection pairs.
    "any_char_count_gt_1_slot": make_any_char_count_gt_1_slot_task,
    "any_char_count_gt_3_slot": make_any_char_count_gt_3_slot_task,
    "sum_gt_7_slot_r12": make_sum_gt_7_slot_r12_task,
    "sum_gt_13_slot_r12": make_sum_gt_13_slot_r12_task,
    "reduce_max_gt_5_slot": make_reduce_max_gt_5_slot_task,
    "reduce_max_gt_7_slot": make_reduce_max_gt_7_slot_task,
    # §v2.6'-Pair2 redesigned: same body shape as §v2.6 Pair 2, threshold pair
    # picked by Phase A scout to land Fmin intermediate.
    "sum_gt_18_slot_r12": make_sum_gt_18_slot_r12_task,
    "sum_gt_22_slot_r12": make_sum_gt_22_slot_r12_task,
    "sum_gt_24_slot_r12": make_sum_gt_24_slot_r12_task,
    "sum_gt_28_slot_r12": make_sum_gt_28_slot_r12_task,
    "sum_gt_30_slot_r12": make_sum_gt_30_slot_r12_task,
    # §v2.8: 6-token integer body to disambiguate body-length vs input-domain.
    "sum_plus2_gt_15_slot": make_sum_plus2_gt_15_slot_task,
    "sum_plus2_gt_17_slot": make_sum_plus2_gt_17_slot_task,
    "sum_plus2_gt_20_slot": make_sum_plus2_gt_20_slot_task,
    "sum_plus2_gt_22_slot": make_sum_plus2_gt_22_slot_task,
    "sum_plus2_gt_25_slot": make_sum_plus2_gt_25_slot_task,
}


def build_task(cfg: ChemTapeConfig, seed: int) -> Task:
    if cfg.task not in TASK_REGISTRY:
        raise KeyError(f"Unknown task {cfg.task!r}; known: {list(TASK_REGISTRY)}")
    return TASK_REGISTRY[cfg.task](cfg, seed)
