"""Frozen decoder parameterizations and the approved sparse outer operator."""

from __future__ import annotations

import numpy as np

from experiments.chem_tape.composition_search import R

LEARNERS = ("C", "M", "T")
BOUND = np.log(16.0)
MIN_COUNT = 250


def normalize(weights, allele_range=R):
    """Proportional water filling with support, then stable largest remainder.

    Fix underweight tokens at 250 and distribute the remaining mass among
    free tokens proportionally. This exactly preserves the integer starts.
    """
    weights = np.asarray(weights, dtype=float)
    if (
        weights.ndim != 2
        or weights.shape[0] != weights.shape[1] + 1
        or weights.shape[1] not in (23, 24)
        or allele_range < MIN_COUNT * weights.shape[1]
        or not np.all(np.isfinite(weights))
        or np.any(weights <= 0)
    ):
        raise ValueError("invalid positive weights")
    result = []
    for row in weights:
        fixed = np.zeros(weights.shape[1], dtype=bool)
        while True:
            shares = row * (allele_range - MIN_COUNT * fixed.sum()) / row[~fixed].sum()
            shares[fixed] = MIN_COUNT
            new_fixed = (~fixed) & (shares < MIN_COUNT)
            if not new_fixed.any():
                break
            fixed |= new_fixed
        counts = np.floor(shares).astype(np.int64)
        remaining = allele_range - int(counts.sum())
        order = np.argsort(-(shares - counts), kind="stable")
        counts[order[:remaining]] += 1
        assert counts.min() >= MIN_COUNT and counts.sum() == allele_range
        result.append(np.cumsum(counts))
    return np.asarray(result)


def initial(learner, controls):
    counts = np.diff(controls["G-marg" if learner == "T" else "G"], prepend=0, axis=1)
    if learner == "C":
        return np.log(counts).ravel()
    if learner == "M":
        return np.zeros(counts.shape[1])
    if learner == "T":
        return np.log(counts[0])
    raise ValueError(learner)


def table_for(learner, vector, controls):
    start = initial(learner, controls)
    vector = np.asarray(vector)
    if vector.shape != start.shape or np.any(np.abs(vector - start) > BOUND + 1e-12):
        raise ValueError("parameter bound violated")
    if learner == "C":
        weights = np.exp(vector.reshape(24, 23))
    elif learner == "M":
        weights = np.diff(controls["G"], prepend=0, axis=1) * np.exp(vector)[None, :]
    else:
        weights = np.tile(np.exp(vector), (24, 1))
    return normalize(weights, int(controls["G"][0, -1]))


def mutate(vector, start, rng):
    coordinates = rng.choice(len(vector), 3, replace=False)
    deltas = rng.normal(0, 0.5, 3)
    child = vector.copy()
    child[coordinates] += deltas
    child = np.clip(child, start - BOUND, start + BOUND)
    return child, dict(coordinates=coordinates.tolist(), deltas=deltas.tolist())


def drift(table, start_table):
    return float(
        np.abs(
            np.diff(table, prepend=0, axis=1) - np.diff(start_table, prepend=0, axis=1)
        ).sum()
        / R
    )


def log_cost(row, cap):
    return float(
        np.log2(
            row["evaluations"]
            if row["solved"] and row["evaluations"] <= cap
            else 2 * cap
        )
    )


def schedule_projection(
    rates, *, workers, elapsed, marginal_seconds, sample_seconds, analysis_seconds=180
):
    """Freeze budget using timings only, in the critic's priority order."""

    def project(t_count, generations, sampling):
        counts = dict(C=6, M=6, T=t_count)
        learning = {
            a: counts[a] * (generations * 16 * 24 + 480) * rates[a]["train"] / workers
            for a in LEARNERS
        }
        tests = {a: counts[a] * rates[a]["test500"] / workers for a in LEARNERS}
        tests["C-marg"] = 6 * rates["G-marg"]["test500"] / workers
        references = (
            rates["C"]["test500"]
            + rates["G-marg"]["test500"]
            + rates["U"]["holdout200"]
            + rates["F"]["holdout200"]
        ) / workers
        extra = 6 * marginal_seconds + (
            12 * sample_seconds / workers if sampling else 0
        )
        remaining = 1.15 * (
            sum(learning.values()) + sum(tests.values()) + references + extra
        )
        return dict(
            trajectories=counts,
            generations=generations,
            sampling=sampling,
            learning_seconds=learning,
            test_seconds=tests,
            reference_seconds=references,
            marginal_sampling_seconds=extra,
            remaining_seconds=remaining + analysis_seconds,
            projected_total_seconds=elapsed + remaining + analysis_seconds,
        )

    attempts = [
        project(6, 25, True),
        project(6, 25, False),
        project(4, 25, False),
        project(4, 20, False),
    ]
    selected = next(
        (p for p in attempts if p["projected_total_seconds"] <= 7 * 3600), None
    )
    return dict(attempts=attempts, selected=selected, feasible=selected is not None)
