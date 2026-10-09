"""Steward probe (read-only, numpy only): how often would a W chain block, WITHOUT its
boundary repair (arm R), change the decoded suffix, and by how many tokens?
Tapes: (a) uniform random alleles (generation 0); (b) 1036 then-addition W solver token
tapes, re-encoded uniformly within their conditional intervals (late search).
Block law: 1036 per-corpus length law, uniform start, C-chain tokens. R's boundary allele
keeps its value (immediate decode = unrepaired); the refresh in the plan does not change
decoded output, so it is irrelevant here."""
import json, sys
from collections import defaultdict
import numpy as np


class Decoder:  # copied from research/main composition_search.Decoder (decode path only)
    def __init__(self, table):
        table = np.asarray(table, dtype=np.int64)
        self.allele_range = int(table[0, -1])
        self.n_tokens = table.shape[1]
        self.table = table
        self.lookup = np.array([np.searchsorted(row, np.arange(self.allele_range), side="right") for row in table], dtype=np.uint8)

    def decode(self, alleles):
        out = np.empty(alleles.shape, dtype=np.uint8)
        previous = np.full(len(alleles), self.n_tokens)
        for j in range(alleles.shape[1]):
            out[:, j] = self.lookup[previous, alleles[:, j]]
            previous = out[:, j]
        return out

ROOT = '/Users/andreas/developer/folding-evolution/experiments/output/'
corpora = json.load(open(ROOT + '2026-10-08/2026-10-08-1246-comparison-gate-training/corpora.json'))
laws = json.load(open(ROOT + '2026-10-09/2026-10-09-1036-fragment-reuse-prepare/operator_laws.json'))
solvers = defaultdict(list)
for line in open(ROOT + '2026-10-09/2026-10-09-1036-fragment-reuse-score/search.jsonl'):
    r = json.loads(line)
    if r['phase'] == 'then_addition' and r['arm'] == 'W' and r['solved']:
        solvers[r['corpus']].append(r['solver'])

def encode(dec, tokens, rng):
    tokens = np.asarray(tokens)
    lower = np.concatenate((np.zeros((dec.n_tokens + 1, 1), dtype=np.int64), dec.table[:, :-1]), axis=1)
    prev = np.concatenate(([dec.n_tokens], tokens[:-1]))
    return rng.integers(lower[prev, tokens], dec.table[prev, tokens])

def run(dec, law, alleles, rng):
    n = len(alleles)
    before = dec.decode(alleles)
    Ls = np.array([int(k) for k in law['length_probabilities']])
    ps = np.array(list(law['length_probabilities'].values()))
    L = rng.choice(Ls, size=n, p=ps)
    s = rng.integers(0, 33 - L)
    child = alleles.copy()
    for i in range(n):
        prev = dec.n_tokens if s[i] == 0 else before[i, s[i] - 1]
        for j in range(L[i]):
            tok = dec.lookup[prev, rng.integers(dec.allele_range)]
            lo = 0 if tok == 0 else dec.table[prev, tok - 1]
            child[i, s[i] + j] = rng.integers(lo, dec.table[prev, tok])
            prev = tok
    after = dec.decode(child)  # R: boundary + suffix alleles untouched
    end = s + L
    has_suffix = end < 32
    suffix_changed = np.array([np.sum(after[i, end[i]:] != before[i, end[i]:]) for i in range(n)])
    boundary_changed = np.array([end[i] < 32 and after[i, end[i]] != before[i, end[i]] for i in range(n)])
    block_noop = np.array([np.array_equal(after[i, s[i]:end[i]], before[i, s[i]:end[i]]) for i in range(n)])
    last_same = np.array([after[i, end[i]-1] == before[i, end[i]-1] for i in range(n)])
    return dict(edits=n, at_tape_end=float(np.mean(~has_suffix)), block_noop=float(block_noop.mean()),
                last_token_unchanged=float(last_same.mean()),
                boundary_token_changed=float(boundary_changed.mean()),
                suffix_any_changed=float(np.mean(suffix_changed > 0)),
                mean_suffix_tokens_changed=float(suffix_changed.mean()),
                mean_suffix_changed_given_any=float(suffix_changed[suffix_changed > 0].mean()) if np.any(suffix_changed) else 0.0,
                mean_suffix_length=float(np.mean(32 - end)))

out = {}
for tid in sorted(corpora):
    dec = Decoder(corpora[tid]['tables']['C'])
    rng = np.random.default_rng([1606, int(tid[2:]), tid[:2] == 'BE'])
    rand = rng.integers(dec.allele_range, size=(2000, 32))
    sol = np.array([encode(dec, t, rng) for t in solvers[tid][:250]])
    sol = np.repeat(sol, 8, axis=0)
    out[tid] = dict(random=run(dec, laws[tid], rand, rng), solvers=run(dec, laws[tid], sol, rng))
keys = ['block_noop', 'last_token_unchanged', 'boundary_token_changed', 'suffix_any_changed', 'mean_suffix_tokens_changed', 'mean_suffix_changed_given_any', 'mean_suffix_length', 'at_tape_end']
for kind in ('random', 'solvers'):
    print(kind)
    for k in keys:
        v = [out[t][kind][k] for t in out]
        print(f'  {k:32s} mean {np.mean(v):.3f}  range {min(v):.3f}-{max(v):.3f}')
json.dump(out, open(__file__.replace('.py', '.json'), 'w'), indent=1)
