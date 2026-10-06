"""24-token fixed decoders and exact finite-length tied marginals."""

import numpy as np
from experiments.chem_tape.composition_search import cumulative, Decoder

R = 24000
ARMS = ("U", "F4", "G4", "G4-marg", "G4-BE", "G4-PA", "G4-BE-marg", "G4-PA-marg")


def marginal(table):
    # Exact emitted-token expectations across the 32 positions, including start.
    p = np.diff(table, prepend=0, axis=1) / R
    position = p[24].copy()
    total = position.copy()
    for _ in range(31):
        position = position @ p[:24]
        total += position
    tied = np.tile(cumulative(total, R), (25, 1))
    assert np.max(np.abs(np.diff(tied[0], prepend=0) / R - total / 32)) <= 1 / R
    return tied


def tables():
    u = np.tile(np.arange(1, 25) * 1000, (25, 1))
    w = np.ones(24)
    w[[1, 18, 22, 23, 7, 9, 17]] = 3
    w[[5, 11]] = 1.5
    f = np.tile(cumulative(w, R), (25, 1))
    g = u.copy()
    start = np.full(24, 500)
    start[1] = 12500
    g[24] = np.cumsum(start)
    after_input = np.full(24, 500)
    after_input[[5, 11]] = [1813, 1812]
    after_input[[18, 22, 23]] = 3625
    g[1] = np.cumsum(after_input)
    after_int = np.full(24, 500)
    after_int[[1, 7, 9, 17]] = 3500
    for t in (2, 3, 5, 6, 7, 8, 11, 15, 16, 17, 18, 19, 22, 23):
        g[t] = np.cumsum(after_int)
    result = dict(U=u, F4=f, G4=g)
    for family in ("BE", "PA"):
        table = g.copy()

        def row(previous, targets):
            counts = np.full(24, 500)
            for t in targets:
                counts[t] += 12000 // len(targets)
            table[previous] = np.cumsum(counts)

        if family == "BE":
            row(7, [1])
            row(17, [9])
        else:
            row(17, [1, 7])
            row(7, [9])
        result["G4-" + family] = table
    for name in ("G4", "G4-BE", "G4-PA"):
        result[name + "-marg"] = marginal(result[name])
    for t in result.values():
        Decoder(t)
    return {a: result[a] for a in ARMS}
