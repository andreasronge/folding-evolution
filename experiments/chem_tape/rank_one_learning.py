"""0821 bounded rank-one residual, calibration, and timing-only admission."""

import numpy as np

from experiments.chem_tape.map_learning import BOUND, mutate, normalize

BASE = 1_821_000_000
SEEDS = {
    name: BASE + i * 1_000_000
    for i, name in enumerate(
        (
            "calibration",
            "learning",
            "selection",
            "fresh",
            "mutation",
            "direction",
            "bootstrap",
        )
    )
}


def row_direction(rng):
    return unit_rms(rng.normal(size=25))


def unit_rms(a):
    a = np.asarray(a, dtype=float) - np.mean(a)
    rms = np.sqrt(np.mean(a * a))
    if rms < 1e-15:
        raise ValueError("degenerate row direction")
    return a / rms


def start_vector(m, rng):
    return np.r_[m, row_direction(rng), np.zeros(24)]


def residual(vector):
    return np.clip(np.outer(vector[24:49], vector[49:]), -BOUND, BOUND)


def table(vector, g4):
    v = np.asarray(vector, dtype=float)
    if v.shape != (73,) or not np.all(np.isfinite(v)):
        raise ValueError("invalid rank-one vector")
    if np.max(np.abs(v[:24])) > BOUND + 1e-12:
        raise ValueError("token bound violated")
    if abs(v[24:49].mean()) > 1e-12 or abs(np.mean(v[24:49] ** 2) - 1) > 1e-12:
        raise ValueError("row direction must be centred and unit RMS")
    if abs(v[49:].mean()) > 1e-12:
        raise ValueError("column direction must be centred")
    counts = np.diff(g4, prepend=0, axis=1)
    return normalize(counts * np.exp(v[:24])[None, :] * np.exp(residual(v)), 24000)


def step(vector, rng, g4, arm="C", force=None):
    operator = force
    if operator is None:
        operator = "token" if arm == "T" or rng.random() < 0.5 else "context"
    if operator == "context":
        operator = "a" if np.any(vector[49:]) and rng.random() < 0.5 else "b"
    if operator not in ("token", "a", "b"):
        raise ValueError(operator)
    original = table(vector, g4) if operator != "token" else None
    redraws = 0
    redrawn_clips = 0
    while True:
        child = vector.copy()
        if operator == "token":
            child[:24], record = mutate(child[:24], np.zeros(24), rng)
        else:
            coordinates = rng.choice(25 if operator == "a" else 24, 3, replace=False)
            deltas = rng.normal(0, 0.5, 3)
            offset = 24 if operator == "a" else 49
            child[offset + coordinates] += deltas
            if operator == "a":
                child[24:49] = unit_rms(child[24:49])
            else:
                child[49:] -= child[49:].mean()
            record = dict(coordinates=coordinates.tolist(), deltas=deltas.tolist())
            if np.array_equal(table(child, g4), original):
                redrawn_clips += int(
                    np.sum(np.abs(np.outer(child[24:49], child[49:])) > BOUND)
                )
                redraws += 1
                if redraws > 1000:
                    raise RuntimeError("context step cannot change decoder")
                operator = "b"
                continue
        raw = np.outer(child[24:49], child[49:])
        return child, dict(
            operator=operator,
            redraws=redraws,
            clipped_elements=int(np.sum(np.abs(raw) > BOUND)),
            redrawn_clipped_elements=redrawn_clips,
            **record,
        )


def diagnostics(vector, g4, inherited):
    r = residual(vector)
    no_residual = vector.copy()
    no_residual[49:] = 0
    full, token = table(vector, g4), table(no_residual, g4)

    def counts(t):
        return np.diff(t, prepend=0, axis=1)

    raw = np.outer(vector[24:49], vector[49:])
    return dict(
        clipped_elements=int(np.sum(np.abs(raw) > BOUND)),
        post_clipping_column_means=r.mean(0).tolist(),
        residual_log_weights=r.tolist(),
        residual_rms=float(np.sqrt(np.mean(r * r))),
        residual_table_l1=float(np.abs(counts(full) - counts(token)).sum() / 24000),
        total_table_l1=float(np.abs(counts(full) - counts(inherited)).sum() / 24000),
    )


def calibration_point(units):
    """Records are paired mutant A/B effects and raw per-search noise."""
    cov = np.mean([np.cov(u["effects"], rowvar=False, ddof=1)[0, 1] for u in units])
    # The partial A score is solely a selected-quarter diagnostic.
    mu = np.mean([np.mean(np.asarray(u["effects"])[:, :2]) for u in units])
    v = np.mean([np.mean(u["variances"]) for u in units])
    selected = {}
    for field, column in (("48", 0), ("24", 2)):
        absolute, gain = [], []
        for u in units:
            e = np.asarray(u["effects"])
            k = len(e) // 4
            choices = np.argsort(e[:, column], kind="stable")[:k]
            chosen = e[choices, 1].mean()
            absolute.append(chosen)
            gain.append(chosen - e[:, 1].mean())
        selected[field] = dict(
            parent_effect=float(np.mean(absolute)),
            selected_minus_all=float(np.mean(gain)),
        )
    return dict(
        raw_covariance=float(cov),
        mean_effect=float(mu),
        per_search_variance=float(v),
        selected=selected,
    )


def calibration_estimate(units, rng, replicates=2000):
    point = calibration_point(units)
    boots = []
    for _ in range(replicates):
        resampled = []
        for unit in units:
            n = len(unit["effects"])
            indices = rng.integers(n, size=n)
            resampled.append(
                dict(
                    effects=np.asarray(unit["effects"])[indices],
                    variances=np.asarray(unit["variances"])[indices],
                )
            )
        boots.append(calibration_point(resampled))
    point["raw_covariance_interval_95"] = np.quantile(
        [b["raw_covariance"] for b in boots], [0.025, 0.975]
    ).tolist()
    for field in point["selected"]:
        for metric in ("parent_effect", "selected_minus_all"):
            point["selected"][field][metric + "_interval_95"] = np.quantile(
                [b["selected"][field][metric] for b in boots], [0.025, 0.975]
            ).tolist()
    point["scope"] = (
        "paired mutants resampled within fixed starts/directions; initial b-steps only"
    )
    return point


def choose_effort(context):
    variance = max(0.0, context["raw_covariance"])
    mu, v = context["mean_effect"], context["per_search_variance"]
    gamma = {}
    for n in (24, 48):
        denom = np.sqrt(variance + 2 * v / n)
        signal = 1.27 * variance / denom if denom else 0.0
        gamma[n] = max(0.0, signal - mu) / n
    n = 48 if gamma[48] > gamma[24] else 24
    return dict(
        n=n,
        gamma={str(k): float(v) for k, v in gamma.items()},
        nonnegative_variance=variance,
    )


def reservation(
    pairs,
    prospective,
    pair_times,
    slow_a,
    slow_b,
    workers,
    fresh_n=50,
    trajectory_searches=4040,
):
    pair = max(pair_times) if pair_times else 2 * trajectory_searches * slow_a / workers
    fresh_rate = 1.02 * max(slow_a, slow_b) / 0.66
    counts = dict(BE=4, PA=6)
    # Four maps per pair on its own cells, plus G4's ten cells.
    searches = fresh_n * (10 + 4 * sum(counts[p[:2]] for p in [*pairs, prospective]))
    return dict(
        pair_seconds=1.3 * pair,
        fresh_seconds=1.3 * searches * fresh_rate / workers,
        reporting_seconds=180,
        fresh_searches=searches,
        fresh_worker_seconds_per_search=fresh_rate,
    )
