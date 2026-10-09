"""Fixed context-specific allele recodings of frozen positional Q maps."""

import hashlib
import time

import numpy as np

from experiments.chem_tape.position_matched import PositionalDecoder, table_hash
from experiments.chem_tape.four_reducer_maps import R

CORPORA = tuple(f'{f}{i}' for i in range(1, 9) for f in ('BE', 'PA'))
DOSES = (30, 100)
METHOD = dict(seed_prefix=537, corpus_indices=list(CORPORA), doses=list(DOSES),
              realizations=[0, 1], k_assignment='sorted seed index // 4 within corpus/cell',
              positions=list(range(1, 32)), contexts=list(range(24)),
              selected_entries={30: 7200, 100: 24000}, position_zero='unchanged',
              permutation_convention='lookup_new[a] = lookup_Q[permutation[a]]')


def array_hash(a):
    a = np.asarray(a)
    return hashlib.sha256(a.astype(a.dtype.newbyteorder('<'), copy=False).tobytes()).hexdigest()


class RecodedDecoder(PositionalDecoder):
    def __init__(self, spec):
        tick = time.monotonic()
        super().__init__(spec['table'])
        self.q_lookup = self.lookup.copy()
        self.source_hash = table_hash(self.table)
        self.dose, self.k = spec['dose'], spec['k']
        if self.dose not in (0, *DOSES) or self.k not in (0, 1):
            raise ValueError('invalid fixed recoding')
        self.inverse = np.broadcast_to(np.arange(R, dtype=np.int32), (32, 25, R)).copy()
        permutation_hash = hashlib.sha256()
        rng = np.random.default_rng([537, CORPORA.index(spec['corpus']), self.dose, self.k])
        identity = np.arange(R, dtype=np.int32)
        for j in range(32):
            for prev in range(25):
                perm = identity.copy()
                if self.dose and j and prev < 24:
                    selected = (rng.choice(R, R * 30 // 100, replace=False) if self.dose == 30 else identity)
                    perm[selected] = rng.permutation(selected)
                self.lookup[j, prev] = self.q_lookup[j, prev, perm]
                self.inverse[j, prev, perm] = identity
                permutation_hash.update(perm.astype('<i4', copy=False).tobytes())
        self.permutation_hash = permutation_hash.hexdigest()
        self.lookup_hash = array_hash(self.lookup)
        self.inverse_hash = array_hash(self.inverse)
        self.map_hash = (self.source_hash if not self.dose else hashlib.sha256(
            (self.source_hash + self.permutation_hash + self.lookup_hash).encode()).hexdigest())
        self.construction_seconds = time.monotonic() - tick

    def hash(self):
        return self.map_hash

    def q_decode(self, a):
        out = np.empty(a.shape, dtype=np.uint8)
        previous = np.full(len(a), 24)
        for j in range(32):
            out[:, j] = self.q_lookup[j, previous, a[:, j]]
            previous = out[:, j]
        return out

    def recode(self, a):
        tokens = self.q_decode(a)
        previous = np.full(len(a), 24)
        out = np.empty(a.shape, dtype=np.int32)
        for j in range(32):
            out[:, j] = self.inverse[j, previous, a[:, j]]
            previous = tokens[:, j]
        if not np.array_equal(self.decode(out), tokens):
            raise AssertionError('recoding changed token tapes')
        return out

    def encode(self, tokens, rng):
        """Uniform draw from each conditional preimage, including recoded aliases."""
        tokens = np.asarray(tokens)
        if tokens.ndim != 2 or tokens.shape[1] != 32 or tokens.dtype.kind not in 'iu' or np.any(tokens < 0) or np.any(tokens >= 24):
            raise ValueError('invalid solver tapes')
        tokens = tokens.astype(np.int64, copy=False)
        previous = np.full(len(tokens), 24)
        a = np.empty(tokens.shape, dtype=np.int32)
        for j in range(32):
            token = tokens[:, j]
            hi = self.table[j, previous, token]
            lo = np.where(token == 0, 0, self.table[j, previous, np.maximum(token - 1, 0)])
            original = rng.integers(lo, hi, dtype=np.int32)
            a[:, j] = self.inverse[j, previous, original]
            previous = token
        if not np.array_equal(self.decode(a), tokens):
            raise AssertionError('conditional encoding changed solver')
        return a

    def validate(self):
        for j in range(32):
            for p in range(25):
                counts = np.bincount(self.lookup[j, p], minlength=24)
                if not np.array_equal(counts, np.diff(self.table[j, p], prepend=0)):
                    raise ValueError('row counts changed')
                inv = self.inverse[j, p]
                if not np.array_equal(np.sort(inv), np.arange(R)):
                    raise ValueError('inverse is not a bijection')
                if not np.array_equal(self.lookup[j, p, inv], self.q_lookup[j, p]):
                    raise ValueError('inverse lookup mismatch')
        return dict(passed=True, rows=800, lookup_sha256=self.lookup_hash,
                    permutation_sha256=self.permutation_hash, inverse_sha256=self.inverse_hash,
                    map_hash=self.hash(), construction_seconds=self.construction_seconds,
                    lookup_bytes=self.lookup.nbytes, inverse_bytes=self.inverse.nbytes)


def edits(base, edited, positions=None):
    changed = base != edited
    count = changed.sum(1)
    first = np.where(changed, np.arange(32), 32).min(1)
    last = np.where(changed, np.arange(32), -1).max(1)
    span = np.where(count, last - first + 1, 0)
    result = dict(mean=float(count.mean()), probability_ge4=float(np.mean(count >= 4)),
                  count_histogram=np.bincount(count, minlength=33).tolist(),
                  span_histogram=np.bincount(span, minlength=33).tolist(), n=len(base))
    if positions is not None:
        downstream = (changed & (np.arange(32)[None, :] > positions[:, None])).sum(1)
        result.update(direct_mean=float(changed[np.arange(len(base)), positions].mean()),
                      downstream_mean=float(downstream.mean()))
    return result


def audit(decoder, parents, seed):
    """Use the production variation order, with supplied uniformly drawn parents."""
    rng = np.random.default_rng(seed)
    n = len(parents)
    base = decoder.decode(parents)
    positions = rng.integers(32, size=n)
    single = parents.copy()
    single[np.arange(n), positions] = rng.integers(R, size=n)
    other = parents[rng.permutation(n)]
    crossing = rng.random(n) < .7
    points = rng.integers(1, 32, size=n)
    mask = rng.random((n, 32)) < .03
    replacements = rng.integers(R, size=(n, 32), dtype=np.int32)
    cross = np.where(crossing[:, None] & (np.arange(32)[None, :] >= points[:, None]), other, parents)
    child = cross.copy()
    child[mask] = replacements[mask]
    mutated = parents.copy()
    mutated[mask] = replacements[mask]
    return dict(single_resample=edits(base, decoder.decode(single), positions),
                bernoulli_003=edits(base, decoder.decode(mutated)),
                crossover=edits(base, decoder.decode(cross)),
                full_offspring=edits(base, decoder.decode(child)))
