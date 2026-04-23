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


def _eval_at_delta(
    program: list[int],
    task: Task,
    indices: np.ndarray,
    delta: float,
    alphabet_name: str,
    safe_pop_consume: bool,
) -> float:
    """§v2.5-plasticity-2d extraction: shared between rank1_op_threshold and
    random_sample_threshold. Fraction correct over ``indices`` at threshold
    modifier ``delta``. Byte-identical to the inline ``_eval`` closure that
    ``adapt_and_evaluate_one`` used before §2d engineering.
    """
    if len(indices) == 0:
        return 0.0
    correct = 0
    for idx in indices:
        x = task.inputs[int(idx)]
        pred = execute_plastic(
            program, task.alphabet, x, task.input_type,
            delta=delta, alphabet_name=alphabet_name,
            safe_pop_consume=safe_pop_consume,
        )
        if pred == int(task.labels[int(idx)]):
            correct += 1
    return correct / len(indices)


def _make_individual_rng(
    cfg: ChemTapeConfig, individual_index: int
) -> np.random.Generator:
    """§v2.5-plasticity-2d: per-individual deterministic rng for
    random_sample_threshold.

    Seed combines ``cfg.seed``, ``individual_index``, and ``cfg.hash()`` so
    identical configs at identical individual positions produce identical
    k-draws across runs. ``cfg.hash()`` is a 12-char hex that already
    incorporates plasticity_mechanism and plasticity_budget (at non-default
    values), so changes to those fields perturb the draws appropriately.
    """
    cfg_hash_int = int(cfg.hash(), 16) & 0xFFFFFFFF
    ss = np.random.SeedSequence([int(cfg.seed), int(individual_index), cfg_hash_int])
    return np.random.default_rng(ss)


# ---------------- Per-individual plastic train/evaluate ----------------


def adapt_and_evaluate_one(
    program: list[int],
    task: Task,
    cfg: ChemTapeConfig,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    selection_only: bool = False,
) -> dict:
    """Train δ on ``train_idx`` via sign-gradient, then evaluate fitness for
    a single individual.

    When ``selection_only=False`` (default), computes all four
    (frozen/plastic × train/test) fitness values — used for the final-population
    dump in evolve.py. Returned dict keys:
      * ``delta_final``: float — δ after training.
      * ``train_fitness_frozen``: fraction correct on train with δ=0.
      * ``train_fitness_plastic``: fraction correct on train with δ_trained.
      * ``test_fitness_frozen``: fraction correct on test with δ=0.
      * ``test_fitness_plastic``: fraction correct on test with δ_trained.
      * ``has_gt``: bool — whether the program contains any GT token.
      * ``fitness_train_plastic``: alias of ``train_fitness_plastic``, used
        by the GA as the selection fitness (drives evolution on plastic
        semantics applied to train examples).

    When ``selection_only=True``, skips the three evaluation passes the GA
    does not consume (train_frozen, test_frozen, test_plastic) and returns
    the minimum set required to drive selection:
      * ``delta_final``, ``train_fitness_plastic``, ``has_gt``,
        ``fitness_train_plastic`` only.

    The selection-only path produces a ``fitness_train_plastic`` value that
    is bit-identical to the full-eval path — no shared mutable state between
    the four _eval calls, and δ is frozen after adaptation. Dropping the
    three unused passes saves ~64% of per-individual VM work (the fourth
    _eval, over 48 train examples with δ_trained, is the only one kept).
    Inner-loop of the GA uses ``selection_only=True``; the final-population
    dump in evolve.py uses the full path.

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
        return _eval_at_delta(
            program, task, indices, d, cfg.alphabet, consume
        )

    train_fit_plastic = _eval(train_idx, delta)
    if selection_only:
        return {
            "delta_final": float(delta),
            "train_fitness_plastic": float(train_fit_plastic),
            "has_gt": bool(has_gt),
            "fitness_train_plastic": float(train_fit_plastic),
        }

    train_fit_frozen = _eval(train_idx, 0.0)
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


def adapt_and_evaluate_one_random_sample(
    program: list[int],
    task: Task,
    cfg: ChemTapeConfig,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    individual_index: int,
    selection_only: bool = False,
) -> dict:
    """§v2.5-plasticity-2d random-δ-sampling mechanism.

    Draws ``k = cfg.plasticity_budget`` independent uniform-continuous samples
    from ``[-budget, +budget]``; evaluates each draw's train_fitness_plastic on
    ``train_idx``; selects the draw maximizing train_fitness_plastic (argmax;
    tiebreak: smallest absolute δ, then first-occurrence); evaluates that δ on
    ``test_idx`` for test_fitness_plastic. Matches the rank-1 plastic protocol
    on train/test split, scoring, and alphabet — only δ-selection differs.

    Per-individual rng is seeded deterministically by
    ``(cfg.seed, individual_index, cfg.hash())`` so identical configs at
    identical individual positions produce identical k-draws. This ensures
    reproducibility across re-runs of the same sweep.

    Returned dict keys (union of rank-1's keys + 4 new k-draw summary fields):

    * Always-present (matches rank-1 output schema):
      ``delta_final``, ``train_fitness_plastic``, ``has_gt``,
      ``fitness_train_plastic``, and — when ``selection_only=False`` —
      also ``train_fitness_frozen``, ``test_fitness_frozen``,
      ``test_fitness_plastic``.
    * New §2d per-individual k-draw summary (all present in both modes for
      schema uniformity; invariant-checked by the mechanism-sanity pre-check
      routed to Row 6 SWAMPED on violation):
        - ``k_draw_min``: float — min over the k draws.
        - ``k_draw_max``: float — max over the k draws.
        - ``k_draw_std``: float — std over the k draws.
        - ``k_argmax_index``: int — which draw (0..k-1) was selected.

    GT-bypass or budget=0 programs have no plasticisable op; δ stays 0 and the
    k-draw summary emits (0, 0, 0, 0) as vacuous values (filtered out of
    invariant checks in the mechanism-sanity pre-check via the ``has_gt``
    indicator; see Row 6 SWAMPED trigger documentation in the prereg).
    """
    has_gt = has_gt_token(program, cfg.alphabet)
    consume = cfg.safe_pop_mode == "consume"
    budget = int(cfg.plasticity_budget)

    if has_gt and budget > 0:
        rng = _make_individual_rng(cfg, individual_index)
        k_draws = rng.uniform(-float(budget), float(budget), size=budget)
        train_fits = np.empty(budget, dtype=np.float64)
        for j in range(budget):
            train_fits[j] = _eval_at_delta(
                program, task, train_idx, float(k_draws[j]),
                cfg.alphabet, consume,
            )
        # argmax with tiebreak: (1) max train fitness; among ties (2)
        # smallest |δ|; among further ties (3) first-occurrence.
        max_fit = float(np.max(train_fits))
        tie_mask = train_fits == max_fit
        tie_indices = np.where(tie_mask)[0]
        if tie_indices.size == 1:
            argmax_index = int(tie_indices[0])
        else:
            abs_deltas = np.abs(k_draws[tie_indices])
            min_abs = float(np.min(abs_deltas))
            abs_tie_indices = tie_indices[abs_deltas == min_abs]
            argmax_index = int(abs_tie_indices[0])  # first-occurrence
        delta = float(k_draws[argmax_index])
        k_draw_min = float(np.min(k_draws))
        k_draw_max = float(np.max(k_draws))
        k_draw_std = float(np.std(k_draws))
    else:
        # GT-bypass or budget=0: δ stays 0; k-draw summary vacuous.
        delta = 0.0
        k_draw_min = 0.0
        k_draw_max = 0.0
        k_draw_std = 0.0
        argmax_index = 0

    train_fit_plastic = _eval_at_delta(
        program, task, train_idx, delta, cfg.alphabet, consume
    )
    if selection_only:
        return {
            "delta_final": float(delta),
            "train_fitness_plastic": float(train_fit_plastic),
            "has_gt": bool(has_gt),
            "fitness_train_plastic": float(train_fit_plastic),
            "k_draw_min": k_draw_min,
            "k_draw_max": k_draw_max,
            "k_draw_std": k_draw_std,
            "k_argmax_index": int(argmax_index),
        }

    train_fit_frozen = _eval_at_delta(
        program, task, train_idx, 0.0, cfg.alphabet, consume
    )
    test_fit_frozen = _eval_at_delta(
        program, task, test_idx, 0.0, cfg.alphabet, consume
    )
    test_fit_plastic = _eval_at_delta(
        program, task, test_idx, delta, cfg.alphabet, consume
    )
    return {
        "delta_final": float(delta),
        "train_fitness_frozen": float(train_fit_frozen),
        "train_fitness_plastic": float(train_fit_plastic),
        "test_fitness_frozen": float(test_fit_frozen),
        "test_fitness_plastic": float(test_fit_plastic),
        "has_gt": bool(has_gt),
        "fitness_train_plastic": float(train_fit_plastic),
        "k_draw_min": k_draw_min,
        "k_draw_max": k_draw_max,
        "k_draw_std": k_draw_std,
        "k_argmax_index": int(argmax_index),
    }


def evaluate_population_plastic(
    programs: list[list[int]],
    task: Task,
    cfg: ChemTapeConfig,
    selection_only: bool = False,
) -> dict:
    """Evaluate a full population under plastic semantics.

    When ``selection_only=False`` (default; used on the final-population dump),
    returns all six per-individual arrays:
      * ``selection_fitness``: train plastic fitness (the GA's driving signal).
      * ``delta_final``, ``train_fitness_frozen``, ``train_fitness_plastic``,
        ``test_fitness_frozen``, ``test_fitness_plastic``, ``has_gt``.

    When ``selection_only=True`` (used by the GA inner loop in evaluate.py),
    returns only the minimum arrays needed to drive selection:
      * ``selection_fitness``, ``delta_final``, ``train_fitness_plastic``,
        ``has_gt``.

    The selection-only path skips three ``_eval`` passes per individual
    (train_frozen, test_frozen, test_plastic) that the GA does not consume,
    saving ~64% of per-individual VM work. Byte-identity preserved: the
    retained train_fitness_plastic computation depends on no shared mutable
    state with the skipped passes, so GA trajectories are unchanged.

    Deliberately pure-Python: the rank-1 plasticity state is per-individual
    and cannot trivially ride the Rust batched fast-path. For the §v2.5
    probe this is acceptable; porting ``adapt_and_evaluate_one`` to a Rust
    kernel is future work if the plasticity line grows further sweeps.
    """
    P = len(programs)
    n_examples = len(task.inputs)
    train_idx, test_idx = split_train_test_indices(
        n_examples, cfg.plasticity_train_fraction
    )
    # §v2.5-plasticity-2d: dispatch on plasticity_mechanism. rank1_op_threshold
    # is the default (byte-identical to pre-§2d path). random_sample_threshold
    # uses the uniform-[-b, +b] draw-and-argmax protocol and emits 4 extra
    # per-individual k-draw summary arrays for Guard-6 (c) / Row 6 SWAMPED
    # mechanism-sanity pre-check.
    mechanism = getattr(cfg, "plasticity_mechanism", "rank1_op_threshold")
    is_random_sample = mechanism == "random_sample_threshold"

    if selection_only:
        out = {
            "selection_fitness": np.empty(P, dtype=np.float64),
            "delta_final": np.empty(P, dtype=np.float32),
            "train_fitness_plastic": np.empty(P, dtype=np.float32),
            "has_gt": np.empty(P, dtype=bool),
        }
        if is_random_sample:
            out["k_draw_min"] = np.empty(P, dtype=np.float32)
            out["k_draw_max"] = np.empty(P, dtype=np.float32)
            out["k_draw_std"] = np.empty(P, dtype=np.float32)
            out["k_argmax_index"] = np.empty(P, dtype=np.int32)
        for i, prog in enumerate(programs):
            if is_random_sample:
                r = adapt_and_evaluate_one_random_sample(
                    prog, task, cfg, train_idx, test_idx,
                    individual_index=i, selection_only=True,
                )
                out["k_draw_min"][i] = r["k_draw_min"]
                out["k_draw_max"][i] = r["k_draw_max"]
                out["k_draw_std"][i] = r["k_draw_std"]
                out["k_argmax_index"][i] = r["k_argmax_index"]
            else:
                r = adapt_and_evaluate_one(
                    prog, task, cfg, train_idx, test_idx, selection_only=True
                )
            out["selection_fitness"][i] = r["fitness_train_plastic"]
            out["delta_final"][i] = r["delta_final"]
            out["train_fitness_plastic"][i] = r["train_fitness_plastic"]
            out["has_gt"][i] = r["has_gt"]
        return out

    out = {
        "selection_fitness": np.empty(P, dtype=np.float64),
        "delta_final": np.empty(P, dtype=np.float32),
        "train_fitness_frozen": np.empty(P, dtype=np.float32),
        "train_fitness_plastic": np.empty(P, dtype=np.float32),
        "test_fitness_frozen": np.empty(P, dtype=np.float32),
        "test_fitness_plastic": np.empty(P, dtype=np.float32),
        "has_gt": np.empty(P, dtype=bool),
    }
    if is_random_sample:
        out["k_draw_min"] = np.empty(P, dtype=np.float32)
        out["k_draw_max"] = np.empty(P, dtype=np.float32)
        out["k_draw_std"] = np.empty(P, dtype=np.float32)
        out["k_argmax_index"] = np.empty(P, dtype=np.int32)
    for i, prog in enumerate(programs):
        if is_random_sample:
            r = adapt_and_evaluate_one_random_sample(
                prog, task, cfg, train_idx, test_idx, individual_index=i,
            )
            out["k_draw_min"][i] = r["k_draw_min"]
            out["k_draw_max"][i] = r["k_draw_max"]
            out["k_draw_std"][i] = r["k_draw_std"]
            out["k_argmax_index"][i] = r["k_argmax_index"]
        else:
            r = adapt_and_evaluate_one(prog, task, cfg, train_idx, test_idx)
        out["selection_fitness"][i] = r["fitness_train_plastic"]
        out["delta_final"][i] = r["delta_final"]
        out["train_fitness_frozen"][i] = r["train_fitness_frozen"]
        out["train_fitness_plastic"][i] = r["train_fitness_plastic"]
        out["test_fitness_frozen"][i] = r["test_fitness_frozen"]
        out["test_fitness_plastic"][i] = r["test_fitness_plastic"]
        out["has_gt"][i] = r["has_gt"]
    return out
