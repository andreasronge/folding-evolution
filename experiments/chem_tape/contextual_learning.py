"""Approved 0811 continuation operators and timing-only scheduling."""

import numpy as np

from experiments.chem_tape.map_learning import (
    BOUND,
    drift,
    mutate,
    normalize,
    table_for,
)


def start_vector(multiplier, arm):
    return np.r_[multiplier, np.zeros(552)] if arm == "R" else np.array(multiplier)


def table(vector, controls):
    vector = np.asarray(vector)
    if vector.shape == (23,):
        return table_for("M", vector, controls)
    if vector.shape != (575,) or not np.all(np.isfinite(vector)):
        raise ValueError("invalid R vector")
    if np.any(np.abs(vector) > BOUND + 1e-12):
        raise ValueError("parameter bound violated")
    weights = np.diff(controls["G"], prepend=0, axis=1)
    return normalize(
        weights * np.exp(vector[:23])[None, :] * np.exp(vector[23:].reshape(24, 23))
    )


def step(vector, rng, *, row_only=False):
    child = vector.copy()
    if len(vector) == 23 or (not row_only and rng.random() < 0.5):
        child[:23], details = mutate(vector[:23], np.zeros(23), rng)
        return child, dict(operator="token", **details)
    row = int(rng.integers(24))
    sigma = float(rng.choice([0.5, 1.0]))
    delta = rng.normal(0, sigma, 23)
    sl = slice(23 + row * 23, 23 + (row + 1) * 23)
    child[sl] = np.clip(child[sl] + delta, -BOUND, BOUND)
    return child, dict(operator="row", row=row, sigma=sigma, deltas=delta.tolist())


def diagnostics(vector, start, controls):
    full, inherited = table(vector, controls), table(start, controls)
    token = table(vector[:23], controls)
    counts = np.diff(full, prepend=0, axis=1)
    token_counts = np.diff(token, prepend=0, axis=1)
    result = dict(
        l1_drift=drift(full, inherited),
        multiplier_table_drift=drift(token, inherited),
        residual_table_drift=drift(full, token),
        multiplier_delta=(vector[:23] - start[:23]).tolist(),
        residual_row_table_l1=(np.abs(counts - token_counts).sum(1) / 23000).tolist(),
    )
    result["residuals"] = (
        vector[23:].reshape(24, 23).tolist() if len(vector) == 575 else None
    )
    return result


def projection(rates, workers, elapsed, sample_seconds):
    """Headroom once; all reductions in the approved priority order."""
    attempts = []
    choices = [
        (35, True, True),
        (35, False, True),
        (35, False, False),
        (28, False, False),
    ]
    for gens, sampling, off_family in choices:
        learn = (
            12
            * (gens * 384 + 480)
            * (rates["M+"]["train"] + rates["R"]["train"])
            / workers
        )
        test = 12 * 700 * sum(rates[a]["test"] for a in ("M+", "R", "R_abl")) / workers
        references = (
            7
            * (700 * rates["reference"]["test"] + 400 * rates["reference"]["off"])
            / workers
        )
        off = (
            6 * 400 * (rates["M+"]["off"] + rates["R"]["off"]) / workers
            if off_family
            else 0
        )
        sample = 18 * sample_seconds if sampling else 0
        total = elapsed + 1.1 * (learn + test + references + off + sample) + 180
        attempts.append(
            dict(
                generations=gens,
                sampling=sampling,
                off_family=off_family,
                learning_seconds=learn,
                test_seconds=test,
                reference_seconds=references,
                off_family_seconds=off,
                sampling_seconds=sample,
                pair_seconds=(learn + test) / 12,
                projected_total_seconds=total,
            )
        )
    selected = next(
        (p for p in attempts if p["projected_total_seconds"] <= 7 * 3600), None
    )
    return dict(attempts=attempts, selected=selected, feasible=selected is not None)
