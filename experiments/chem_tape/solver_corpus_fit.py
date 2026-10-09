"""Frozen 1707 full-tape estimators; no evaluation observations enter fitting."""

import numpy as np
from scipy.optimize import minimize

from experiments.chem_tape.composition_search import Decoder
from experiments.chem_tape.four_reducer_maps import R, tables
from experiments.chem_tape.map_learning import normalize


def validate_table(table):
    d = Decoder(table)
    if (
        d.table.shape != (25, 24)
        or d.allele_range != R
        or np.min(np.diff(d.table, prepend=0, axis=1)) < 250
    ):
        raise ValueError("required decoder shape/range/support validation failed")
    return d.hash()


def transition_counts(rows, cells):
    per = {c: np.zeros((25, 24)) for c in cells}
    yields = dict.fromkeys(cells, 0)
    for r in rows:
        if r["cell"] not in per:
            raise ValueError("non-training corpus tape")
        tape = r["solver"]
        if (tape is not None) != r["solved"]:
            raise ValueError("solver tape/solve mismatch")
        if tape is None:
            continue
        if len(tape) != 32 or any(type(t) is not int or not 0 <= t < 24 for t in tape):
            raise ValueError("invalid solver tape")
        yields[r["cell"]] += 1
        previous = 24
        for token in tape:
            per[r["cell"]][previous, token] += 1
            previous = token
    if any(n == 0 for n in yields.values()):
        raise ValueError("empty corpus cell")
    n = sum(counts / counts.sum() * 1600 for counts in per.values())
    return n, yields


def emitted(table):
    p = np.diff(table, prepend=0, axis=1) / R
    position = p[24].copy()
    total = position.copy()
    for _ in range(31):
        position = position @ p[:24]
        total += position
    return total / 32


def small_source_counts(rows, cells):
    """Legacy cell normalization, with expected G4 counts for empty cells."""
    g = np.diff(tables()["G4"], prepend=0, axis=1) / R
    expected = np.zeros((25, 24))
    position = np.zeros(25)
    position[24] = 1
    for _ in range(32):
        expected += position[:, None] * g
        next_position = position @ g
        position = np.zeros(25)
        position[:24] = next_position
    if any(r['cell'] not in cells for r in rows):
        raise ValueError('non-training source')
    counts = np.zeros((25, 24))
    yields = {}
    for cid in cells:
        sub = [r for r in rows if r['cell'] == cid]
        # Validate failures too; transition_counts raises only after validation.
        if any((r['solver'] is not None) != r['solved'] for r in sub):
            raise ValueError('solver tape/solve mismatch')
        yields[cid] = sum(r['solved'] for r in sub)
        if yields[cid]:
            cell_counts, _ = transition_counts(sub, [cid])
        else:
            cell_counts = expected / expected.sum() * 1600
        counts += cell_counts
    return counts, yields


def fit_context(counts):
    """Unchanged alpha-50 C estimator, without fitting unused T/K controls."""
    g = np.diff(tables()["G4"], prepend=0, axis=1) / R
    return normalize((counts + 50 * g) / (counts.sum(1, keepdims=True) + 50), R)


def fit(n):
    g = np.diff(tables()["G4"], prepend=0, axis=1) / R

    def objective(lw):
        q = g * np.exp(lw)
        q /= q.sum(1, keepdims=True)
        ll = (n * np.log(q)).sum()
        grad = n.sum(0) - (n.sum(1, keepdims=True) * q).sum(0)
        return -ll, -grad

    res = minimize(
        objective,
        np.zeros(24),
        jac=True,
        method="L-BFGS-B",
        bounds=[(-np.log(16), np.log(16))] * 24,
    )
    if not res.success or not np.all(np.isfinite(res.x)):
        raise ValueError(f"T optimizer failed: {res.message}")
    T = normalize(g * np.exp(res.x)[None, :], R)
    C = normalize((n + 50 * g) / (n.sum(1, keepdims=True) + 50), R)
    target = emitted(C)
    lw = np.zeros(24)
    for _ in range(400):
        tab = normalize(g * np.exp(lw)[None, :], R)
        lw += 0.7 * (np.log(target) - np.log(emitted(tab)))
    K = normalize(g * np.exp(lw)[None, :], R)
    error = float(np.max(np.abs(emitted(K) - target)))
    fitted = dict(T=T, C=C, K=K)
    hashes = {a: validate_table(t) for a, t in fitted.items()}
    diagnostics = dict(
        T_success=bool(res.success),
        T_message=str(res.message),
        T_iterations=int(res.nit),
        T_loss=float(res.fun),
        T_multipliers=np.exp(res.x).tolist(),
        K_log_multipliers=lw.tolist(),
        K_steps=400,
        K_step=0.7,
        K_max_error=error,
        K_valid=error <= 0.001,
        hashes=hashes,
        C_emitted=target.tolist(),
        K_emitted=emitted(K).tolist(),
    )
    return fitted, diagnostics


BASE = 2026100717


def seed_for(phase, family, corpus, cell, index, base=BASE):
    return (
        base
        + phase * 1000000
        + (family == "PA") * 100000
        + corpus * 2000
        + cell * 200
        + index
    )


def admit_holdouts(remaining, projected):
    return bool(remaining > 1.5 * projected)


def partial_transition_counts(rows, cells, kind):
    """Explicit non-solver interface: equal source weights, then 1,600 per cell."""
    if kind not in ("S", "P"):
        raise ValueError("invalid partial archive kind")
    per = {c: [] for c in cells}
    seen = set()
    for source in rows:
        cid = source["cell"]
        if cid not in per:
            raise ValueError("non-training partial tape")
        key = (cid, source["seed"])
        if key in seen:
            raise ValueError("duplicate source attempt")
        seen.add(key)
        count = np.zeros((25, 24))
        for row in source["archive"]:
            if row["kind"] != kind:
                continue
            tape = row["tape"]
            if (
                row["exact"] is not False
                or row["cell"] != cid
                or row["source_seed"] != source["seed"]
                or (source["solved"] and row["evaluations"] >= source["evaluations"])
            ):
                raise ValueError("invalid pre-solution archive provenance")
            if len(tape) != 32 or any(
                type(t) is not int or not 0 <= t < 24 for t in tape
            ):
                raise ValueError("invalid partial tape")
            previous = 24
            for token in tape:
                count[previous, token] += 1
                previous = token
        if count.sum():
            per[cid].append(count / count.sum())
    if any(not sources for sources in per.values()):
        raise ValueError("empty partial corpus cell")
    counts = sum(np.mean(sources, axis=0) * 1600 for sources in per.values())
    return counts, {cid: len(sources) for cid, sources in per.items()}
