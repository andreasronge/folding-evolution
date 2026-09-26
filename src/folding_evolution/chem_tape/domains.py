"""Chem-tape v3 prototype: domains + linkers (map-bias notebook §3).

Principle: new material can arrive silently and be switched on by one small step.

- Linker tokens (ids 20..25) split the tape into domains. Everything else is a
  v2_probe token (ids 0..19).
- Each domain runs on its own fresh stack; its value is the top int (0 if the top
  is not an int). Junk in one domain cannot corrupt another.
- The first non-empty domain is the base value. Each later non-empty domain is
  combined into the running value by the linker directly before it:
      SILENT  domain is skipped (unexpressed, neutral)
      ADD     acc + v
      GT      1 if acc > v else 0
      MIN     min(acc, v)
      MAX     max(acc, v)
      GATE    v if acc > 0 else 0
  A silent linker skips only its own domain, so every silent domain can be
  switched on individually by one linker mutation.
- A domain with no non-NOP token is empty and ignored.

Domains contain only v2_probe tokens, so they run through the fast Rust
pop-batch executor under alphabet "v2_probe".
"""

from __future__ import annotations

import numpy as np

from .tasks import Task

SILENT, L_ADD, L_GT, L_MIN, L_MAX, L_GATE = 20, 21, 22, 23, 24, 25
LINKERS = (SILENT, L_ADD, L_GT, L_MIN, L_MAX, L_GATE)
TOKEN_MAX = 25
LINKER_NAMES = {SILENT: "~", L_ADD: "+ADD", L_GT: "+GT", L_MIN: "+MIN", L_MAX: "+MAX", L_GATE: "+GATE"}


def split_domains(tape) -> list[tuple[int | None, tuple[int, ...]]]:
    """[(linker before domain or None, domain tokens)] for non-empty domains."""
    out: list[tuple[int | None, tuple[int, ...]]] = []
    linker: int | None = None
    cur: list[int] = []
    for t in (int(x) for x in tape):
        if t >= SILENT:
            if any(cur):
                out.append((linker, tuple(cur)))
            cur = []
            linker = t
        else:
            cur.append(t)
    if any(cur):
        out.append((linker, tuple(cur)))
    return out


def domain_values(domains: list[tuple[int, ...]], task: Task, safe_pop_consume: bool = False) -> np.ndarray:
    """(D, E) int64 value of each domain on each task input."""
    from _folding_rust import rust_chem_execute_pop_batch

    flat = rust_chem_execute_pop_batch(
        [list(d) for d in domains], task.alphabet.slot_12, task.alphabet.slot_13,
        task.inputs, task.input_type, alphabet_name="v2_probe",
        threshold=int(task.alphabet.threshold), safe_pop_consume=safe_pop_consume,
    )
    return np.asarray(flat, dtype=np.int64).reshape(len(domains), len(task.inputs))


def _combine(linker: int, acc: np.ndarray, v: np.ndarray) -> np.ndarray:
    if linker == L_ADD:
        return acc + v
    if linker == L_GT:
        return (acc > v).astype(np.int64)
    if linker == L_MIN:
        return np.minimum(acc, v)
    if linker == L_MAX:
        return np.maximum(acc, v)
    if linker == L_GATE:
        return np.where(acc > 0, v, 0)
    return acc  # SILENT


def evaluate_v3(population: list[np.ndarray], task: Task, safe_pop_consume: bool = False):
    """Same contract as evaluate.evaluate_population: (fitnesses, predictions)."""
    E = len(task.inputs)
    parsed = [split_domains(g) for g in population]
    uniq: dict[tuple[int, ...], int] = {}
    for doms in parsed:
        for _, d in doms:
            uniq.setdefault(d, len(uniq))
    vals = domain_values(list(uniq), task, safe_pop_consume) if uniq else np.zeros((0, E), np.int64)
    preds = np.zeros((len(population), E), dtype=np.int64)
    for p, doms in enumerate(parsed):
        if not doms:
            continue
        acc = vals[uniq[doms[0][1]]].copy()
        for linker, d in doms[1:]:
            acc = _combine(linker, acc, vals[uniq[d]])
        preds[p] = acc
    fitnesses = (preds == task.labels[None, :]).mean(axis=1).astype(np.float64)
    return fitnesses, preds
