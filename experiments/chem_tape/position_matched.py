"""Frozen Q/P projections; support-preserving quantized finite-tape fitting."""

import hashlib
import time

import numpy as np

from experiments.chem_tape.composition_search import Decoder
from experiments.chem_tape.four_reducer_maps import R, tables
from experiments.chem_tape.map_learning import normalize

METHOD = dict(positions=32, tokens=24, allele_range=R, minimum_count=250,
              Q_steps=400, Q_step=0.7, Q_multiplier_bounds=None,
              Q_start='exact C start row; unreachable body rows use normalized G4',
              P='normalize tiled C positional marginal; all previous rows identical',
              max_token_error=0.001, max_total_variation=0.005)


def table_hash(table):
    t = np.asarray(table, dtype=np.int64)
    # Identical positional copies name the same map, including for K replay.
    if t.ndim == 3 and np.all(t == t[0]):
        t = t[0]
    return hashlib.sha256(t.astype('<i8').tobytes()).hexdigest()


class PositionalDecoder:
    def __init__(self, table):
        tick = time.monotonic()
        t = np.asarray(table, dtype=np.int64)
        if (t.shape != (32, 25, 24) or np.any(t[..., -1] != R)
            or np.min(np.diff(t, prepend=0, axis=2)) < 250):
            raise ValueError('invalid positional shape/range/support')
        self.table, self.allele_range, self.n_tokens = t, R, 24
        self.tied = np.all(t == t[:, :1, :])
        active = t[:, :1, :] if self.tied else t
        self.lookup = np.array([[np.searchsorted(row, np.arange(R), side='right')
                                 for row in position] for position in active], dtype=np.uint8)
        self.construction_seconds = time.monotonic() - tick

    def hash(self):
        return table_hash(self.table)

    def decode(self, alleles):
        a = np.asarray(alleles)
        if (a.ndim != 2 or a.shape[1] != 32 or a.dtype.kind not in 'iu'
            or np.any(a < 0) or np.any(a >= R)):
            raise ValueError('invalid positional allele array')
        if self.tied:
            return self.lookup[np.arange(32)[None, :], 0, a]
        out = np.empty(a.shape, dtype=np.uint8)
        previous = np.full(len(a), 24)
        for j in range(32):
            out[:, j] = self.lookup[j, previous, a[:, j]]
            previous = out[:, j]
        return out


def decoder_for(table):
    return PositionalDecoder(table) if np.asarray(table).ndim == 3 else Decoder(table)


def marginals(table):
    t = np.asarray(table)
    if t.ndim == 2:
        t = np.broadcast_to(t, (32, 25, 24))
    p = np.diff(t, prepend=0, axis=2) / R
    out = [p[0, 24].copy()]
    for j in range(1, 32):
        out.append(out[-1] @ p[j, :24])
    return np.asarray(out)


def project(c):
    target = marginals(c)
    g = np.diff(tables()['G4'], prepend=0, axis=1) / R
    q, p, multipliers = [], [], []
    previous = target[0].copy()
    start = normalize(g, R)
    start[24] = np.asarray(c)[24]
    q.append(start)
    multipliers.append(None)
    for j in range(1, 32):
        lw = np.zeros(24)
        for _ in range(METHOD['Q_steps']):
            tab = normalize(g * np.exp(lw)[None, :], R)
            actual = previous @ (np.diff(tab, prepend=0, axis=1)[:24] / R)
            lw += METHOD['Q_step'] * (np.log(target[j]) - np.log(actual))
        tab = normalize(g * np.exp(lw)[None, :], R)
        q.append(tab)
        previous = previous @ (np.diff(tab, prepend=0, axis=1)[:24] / R)
        multipliers.append(lw.tolist())
    for row in target:
        p.append(normalize(np.tile(row, (25, 1)), R))
    controls = dict(Q=np.asarray(q), P=np.asarray(p))
    checks = {}
    for arm, t in controls.items():
        actual = marginals(t)
        delta = np.abs(actual - target)
        checks[arm] = dict(hash=table_hash(t), maximum_token_error=float(delta.max()),
                           maximum_total_variation=float((delta.sum(1) / 2).max()),
                           per_position_max_token_error=delta.max(1).tolist(),
                           per_position_total_variation=(delta.sum(1) / 2).tolist(),
                           target=target.tolist(), actual=actual.tolist(),
                           minimum_count=int(np.diff(t, prepend=0, axis=2).min()))
        PositionalDecoder(t)
        if (checks[arm]['maximum_token_error'] > METHOD['max_token_error']
            or checks[arm]['maximum_total_variation'] > METHOD['max_total_variation']):
            raise ValueError(f'{arm} positional marginal match failed: {checks[arm]}')
    if not np.array_equal(controls['Q'][0, 24], np.asarray(c)[24]):
        raise ValueError('Q start row differs from C')
    return controls, dict(checks=checks, Q_log_multipliers=multipliers, start_row_equal=True)


def reference_decode(table, alleles):
    """Scalar cumulative-threshold oracle, independent of lookup indexing."""
    t, a = np.asarray(table), np.asarray(alleles)
    result = np.empty(a.shape, dtype=np.uint8)
    for i in range(len(a)):
        previous = 24
        for j in range(32):
            result[i, j] = np.searchsorted(t[j, previous], a[i, j], side='right')
            previous = result[i, j]
    return result


def validate_lookup(table, seed):
    d = PositionalDecoder(table)
    # Exhaustively validate every threshold/allele for each position and context.
    contexts = [0] if d.tied else range(25)
    for j in range(32):
        for previous in contexts:
            oracle = np.searchsorted(d.table[j, previous], np.arange(R), side='right')
            if not np.array_equal(d.lookup[j, previous], oracle):
                raise ValueError('positional lookup differs from threshold oracle')
    a = np.random.default_rng(seed).integers(R, size=(128, 32), dtype=np.int32)
    if not np.array_equal(d.decode(a), reference_decode(table, a)):
        raise ValueError('changing-position decoder differs from scalar reference')
    return dict(passed=True, positions=32, contexts=1 if d.tied else 25,
                alleles_per_row=R, reference_tapes=128,
                construction_seconds=d.construction_seconds, lookup_bytes=d.lookup.nbytes)


def variation_diagnostics(corpora):
    rng = np.random.default_rng(202610090239)
    n = 4096
    a = rng.integers(R, size=(n, 32), dtype=np.int32)
    b = rng.integers(R, size=(n, 32), dtype=np.int32)
    mutation = a.copy()
    positions = rng.integers(32, size=n)
    mutation[np.arange(n), positions] = rng.integers(R, size=n)
    points = rng.integers(1, 32, size=n)
    crossover = np.where(np.arange(32)[None, :] >= points[:, None], b, a)
    res = {}
    for tid, record in corpora.items():
        res[tid] = {}
        for arm in ('C', 'T', 'K', 'Q', 'P'):
            d = decoder_for(record['tables'][arm])
            base = d.decode(a)
            mutation_changed = np.sum(base != d.decode(mutation), axis=1)
            cross_changed = np.sum(base != d.decode(crossover), axis=1)
            res[tid][arm] = dict(
                single_allele_resample_mean=float(mutation_changed.mean()),
                crossover_mean=float(cross_changed.mean()),
                single_allele_resample_histogram=np.bincount(mutation_changed, minlength=33).tolist(),
                crossover_histogram=np.bincount(cross_changed, minlength=33).tolist())
    return dict(seed=202610090239, n_per_corpus_arm=n, prior='uniform independent latent tapes',
                mutation='one position uniformly chosen; uniform resample, including same allele',
                crossover='one point uniformly 1..31; suffix from independent parent, no mutation',
                corpora=res)
