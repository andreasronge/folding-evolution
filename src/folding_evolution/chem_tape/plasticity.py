"""Runtime-plasticity (Baldwin-effect) execution for chem-tape §v2.5-plasticity-1a.

Rank-1 operator-threshold plasticity: every GT operation in a decoded program
shares a single learnable scalar modifier ``delta`` (one float per program —
"rank 1"). During the **train phase** of evaluation, ``delta`` is updated via
a sign-gradient rule:

    * false-negative (label=1, pred=0): ``delta += plasticity_delta``
    * false-positive (label=0, pred=1): ``delta -= plasticity_delta``

up to ``plasticity_budget`` updates per evaluation. After training, ``delta``
is frozen for the held-out **test phase**. The GT comparison becomes
``a > (b - delta)`` — a positive ``delta`` shifts the threshold DOWN, making
GT more likely to fire (correctly increasing positive rate when the program
was under-predicting).

Scope and intentional limitations
---------------------------------
* Only GT is plastic in this rank-1 probe. The prereg mentions GT/LT/EQ as
  "comparison operators", but the v1/v2_probe alphabets currently expose only
  GT as a stack op (id 8); LT/EQ do not exist. The delta is thus applied to
  GT tokens only. If LT/EQ are ever added, extend ``_gt_shifted`` accordingly.
* IF_GT's internal ``cond > 0`` check is NOT plasticised — the prereg pins
  the modifier to comparison-operators-on-the-stack semantics, and IF_GT's
  internal cond check is a control-flow positivity test rather than a general
  comparison.
* Execution is pure-Python. The frozen fast-path in ``evaluate.py`` continues
  to use the Rust executor when available; plastic execution runs in Python
  because the per-individual δ state is not Rust-accelerated. This is an
  acknowledged compute cost of the plastic probe.

When ``ChemTapeConfig.plasticity_enabled=False`` (default), this module is
NEVER imported at evaluation time — ``evaluate.py`` dispatches through the
unmodified Rust/Python fast-path and produces byte-identical final-population
dumps (principle 23).
"""

from __future__ import annotations

from typing import Iterable

import numpy as np

from . import alphabet as alph
from . import executor as _exec
from .config import ChemTapeConfig
from .tasks import Task


# ---------------- Plastic op implementations ----------------
#
# All non-plastic ops are delegated to the standard executor. GT is the only
# op whose semantics change when δ ≠ 0. The plastic GT pops (b, a) — same as
# the frozen GT — and compares ``a > b - delta`` instead of ``a > b``. With
# δ = 0 this is a strict no-op vs the frozen path.


def _plastic_gt_factory(delta: float):
    """Return a _op_gt replacement that compares a > (b - delta)."""
    def _plastic_gt(stack, inp_value, inp_type, ta):
        b = _exec.safe_pop(stack, "int")
        a = _exec.safe_pop(stack, "int")
        _exec.push_int(stack, 1 if a > (b - delta) else 0)
    return _plastic_gt


def execute_plastic(
    tokens: Iterable[int],
    tape_alphabet: alph.TaskAlphabet,
    input_value,
    input_type: str,
    delta: float,
    alphabet_name: str = "v1",
    safe_pop_consume: bool = False,
) -> int:
    """Execute ``tokens`` under rank-1 plastic GT with threshold modifier ``delta``.

    Identical to ``executor.execute_program`` when ``delta == 0.0``. Otherwise
    every GT (id 8) performs ``a > b - delta`` instead of ``a > b``.
    """
    # Pre-bind dispatch table and slot ops in the same way as the frozen
    # executor. We copy the dispatch dict so we can override GT without
    # mutating module-level tables (which would cross-contaminate other
    # evaluations).
    table = dict(_exec._dispatch_table(alphabet_name))
    table[alph.GT] = _plastic_gt_factory(delta)

    # The safe_pop mode is a module-level flag in executor.py — we set it the
    # same way the frozen path does. We do NOT restore it afterwards because
    # the frozen path also leaves it set; callers that care set it explicitly
    # on every call via execute_program.
    _exec._SAFE_POP_CONSUME = safe_pop_consume
    stack: list = []
    ops_run = 0
    for tid in tokens:
        if ops_run >= _exec.OP_CAP:
            break
        tid_i = int(tid)
        if tid_i == alph.SLOT_12:
            op = _exec._SLOT_OPS.get(tape_alphabet.slot_12, _exec._op_nop)
        elif tid_i == alph.SLOT_13:
            op = _exec._SLOT_OPS.get(tape_alphabet.slot_13, _exec._op_nop)
        else:
            op = table.get(tid_i, _exec._op_nop)
        op(stack, input_value, input_type, tape_alphabet)
        ops_run += 1
    if not stack:
        return 0
    ttag, payload = stack[-1]
    if ttag == "int":
        return int(payload)
    return 0


def has_gt_token(
    program: list[int],
    alphabet_name: str = "v2_probe",
) -> bool:
    """Return True if ``program`` contains at least one GT token.

    Plasticity cannot act on a program with no GT — such programs trivially
    satisfy ``test_fitness_plastic == test_fitness_frozen``. They are
    "GT-bypass" individuals in the prereg's terminology, reported via
    ``GT_bypass_fraction`` and excluded from the Baldwin slope regression.
    """
    return any(int(t) == alph.GT for t in program)


# ---------------- Train/test split ----------------


def split_train_test_indices(
    n_examples: int,
    train_fraction: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (train_idx, test_idx) for a deterministic train/test split.

    Per-seed determinism is inherited from the upstream task's input ordering
    (``Task.inputs`` is already generated by a seeded numpy RNG). The split
    takes the first ``round(n_examples * train_fraction)`` indices as train
    and the remainder as test — option (b) in prereg §3.

    For ``n_examples=64`` and ``train_fraction=0.75`` this yields 48 train
    and 16 test indices.
    """
    n_train = int(round(n_examples * train_fraction))
    n_train = max(1, min(n_examples - 1, n_train))  # keep both halves non-empty
    train_idx = np.arange(n_train, dtype=np.int64)
    test_idx = np.arange(n_train, n_examples, dtype=np.int64)
    return train_idx, test_idx


# ---------------- Per-individual plastic train/evaluate ----------------


def adapt_and_evaluate_one(
    program: list[int],
    task: Task,
    cfg: ChemTapeConfig,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
) -> dict:
    """Train δ on ``train_idx`` via sign-gradient, then evaluate frozen and
    plastic fitness on train and test partitions for a single individual.

    Returns a dict with keys:
      * ``delta_final``: float — δ after training.
      * ``train_fitness_frozen``: fraction correct on train with δ=0.
      * ``train_fitness_plastic``: fraction correct on train with δ_trained.
      * ``test_fitness_frozen``: fraction correct on test with δ=0.
      * ``test_fitness_plastic``: fraction correct on test with δ_trained.
      * ``has_gt``: bool — whether the program contains any GT token.
      * ``fitness_train_plastic``: alias of ``train_fitness_plastic``, used
        by the GA as the selection fitness (drives evolution on plastic
        semantics applied to train examples).

    Budget semantics
    ----------------
    One budget step = one ``δ`` update of magnitude ``plasticity_delta``
    triggered by a misclassified train example. Examples are iterated in
    their fixed train_idx order; the first ``plasticity_budget`` mistakes
    each produce one update, after which δ is frozen even if further train
    examples are still misclassified. This caps ``|δ_final|`` at
    ``plasticity_budget * plasticity_delta`` (rigid, per-prereg §2
    "task-scale justification").
    """
    has_gt = has_gt_token(program, cfg.alphabet)
    consume = cfg.safe_pop_mode == "consume"
    delta_step = float(cfg.plasticity_delta)
    budget = int(cfg.plasticity_budget)

    # --- Train δ ---
    # GT-bypass programs have no plasticisable op; skip the loop so δ stays 0.
    delta = 0.0
    if has_gt and budget > 0:
        updates = 0
        for idx in train_idx:
            if updates >= budget:
                break
            x = task.inputs[int(idx)]
            pred = execute_plastic(
                program, task.alphabet, x, task.input_type,
                delta=delta, alphabet_name=cfg.alphabet,
                safe_pop_consume=consume,
            )
            label = int(task.labels[int(idx)])
            # Binary tasks: sign rule on (label - pred). On graded tasks
            # (e.g., count_r with integer labels) we still use sign(label -
            # pred) — a correct generalisation for monotone-threshold
            # targets; non-binary plasticity is out of scope for this probe.
            if pred == label:
                continue
            if label > pred:
                delta += delta_step
            else:
                delta -= delta_step
            updates += 1

    # --- Evaluate frozen and plastic on both splits ---
    def _eval(indices: np.ndarray, d: float) -> float:
        if len(indices) == 0:
            return 0.0
        correct = 0
        for idx in indices:
            x = task.inputs[int(idx)]
            pred = execute_plastic(
                program, task.alphabet, x, task.input_type,
                delta=d, alphabet_name=cfg.alphabet,
                safe_pop_consume=consume,
            )
            if pred == int(task.labels[int(idx)]):
                correct += 1
        return correct / len(indices)

    train_fit_frozen = _eval(train_idx, 0.0)
    train_fit_plastic = _eval(train_idx, delta)
    test_fit_frozen = _eval(test_idx, 0.0)
    test_fit_plastic = _eval(test_idx, delta)

    return {
        "delta_final": float(delta),
        "train_fitness_frozen": float(train_fit_frozen),
        "train_fitness_plastic": float(train_fit_plastic),
        "test_fitness_frozen": float(test_fit_frozen),
        "test_fitness_plastic": float(test_fit_plastic),
        "has_gt": bool(has_gt),
        "fitness_train_plastic": float(train_fit_plastic),
    }


def evaluate_population_plastic(
    programs: list[list[int]],
    task: Task,
    cfg: ChemTapeConfig,
) -> dict:
    """Evaluate a full population under plastic semantics.

    Returns a dict of (P,)-shaped numpy arrays:
      * ``selection_fitness``: train plastic fitness (the GA's driving signal).
      * ``delta_final``, ``train_fitness_frozen``, ``train_fitness_plastic``,
        ``test_fitness_frozen``, ``test_fitness_plastic``, ``has_gt``.

    Deliberately pure-Python: the rank-1 plasticity state is per-individual
    and cannot trivially ride the Rust batched fast-path. For the §v2.5
    probe this is acceptable; optimising to a Rust plastic kernel is future
    work if the probe passes.
    """
    P = len(programs)
    n_examples = len(task.inputs)
    train_idx, test_idx = split_train_test_indices(
        n_examples, cfg.plasticity_train_fraction
    )

    out = {
        "selection_fitness": np.empty(P, dtype=np.float64),
        "delta_final": np.empty(P, dtype=np.float32),
        "train_fitness_frozen": np.empty(P, dtype=np.float32),
        "train_fitness_plastic": np.empty(P, dtype=np.float32),
        "test_fitness_frozen": np.empty(P, dtype=np.float32),
        "test_fitness_plastic": np.empty(P, dtype=np.float32),
        "has_gt": np.empty(P, dtype=bool),
    }
    for i, prog in enumerate(programs):
        r = adapt_and_evaluate_one(prog, task, cfg, train_idx, test_idx)
        out["selection_fitness"][i] = r["fitness_train_plastic"]
        out["delta_final"][i] = r["delta_final"]
        out["train_fitness_frozen"][i] = r["train_fitness_frozen"]
        out["train_fitness_plastic"][i] = r["train_fitness_plastic"]
        out["test_fitness_frozen"][i] = r["test_fitness_frozen"]
        out["test_fitness_plastic"][i] = r["test_fitness_plastic"]
        out["has_gt"][i] = r["has_gt"]
    return out
