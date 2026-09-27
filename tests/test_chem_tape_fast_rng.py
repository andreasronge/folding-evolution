"""cfg.fast_rng: batched lexicase and tagged mutation match the reference
operators in distribution (the random stream differs by design)."""

import random

import numpy as np

from folding_evolution.chem_tape import evolve, tagged
from folding_evolution.chem_tape.config import ChemTapeConfig


def test_lexicase_batch_matches_reference_frequencies():
    r = np.random.default_rng(1)
    cases = r.random((120, 64)) < np.linspace(0.3, 0.9, 120)[:, None]
    gc, inv = np.unique(cases, axis=0, return_inverse=True)
    inv = inv.ravel()
    groups = [np.flatnonzero(inv == g) for g in range(gc.shape[0])]
    n = 20000
    ref = np.bincount([evolve._lexicase_select(groups, gc, random.Random(i)) for i in range(n)], minlength=120)
    bat = np.bincount(evolve._lexicase_batch(cases, n, np.random.default_rng(2)), minlength=120)
    assert np.abs(ref - bat).max() / n < 0.01


def test_lexicase_batch_short_case_rows():
    cases = np.zeros((6, 10), dtype=bool)
    cases[3] = True                                  # dominates on every case
    assert set(evolve._lexicase_batch(cases, 50, np.random.default_rng(0))) == {3}


def test_mutate_batch_matches_reference_rates():
    L, mu, n = 64, 0.015, 5000
    g0 = tagged.random_genotype(L, random.Random(0), n_ops=tagged.N_OPS_COMB)
    b = tagged.mutate_batch(np.tile(g0, (n, 1)), mu, np.random.default_rng(3), tagged.N_OPS_COMB)
    rr = random.Random(4)
    a = np.stack([tagged.mutate(g0, mu, rr, n_ops=tagged.N_OPS_COMB) for _ in range(n)])
    assert b.shape == a.shape and b.dtype == np.uint8
    assert (b[:, :L] < tagged.N_OPS_COMB).all() and (b[:, L:] < tagged.N_TAGS).all()
    assert abs((a != g0).any(1).mean() - (b != g0).any(1).mean()) < 0.02


def test_fast_rng_smoke_and_hash():
    base = dict(task="mbs_and", generations=3, n_examples=64, pop_size=64, selection_mode="lexicase",
                backend="numpy", arm="TAG", alphabet="tagged", tape_length=32, mutation_rate=0.015)
    cfg = ChemTapeConfig(**base, fast_rng=True)
    assert evolve.run_evolution(cfg).generations_run >= 1
    assert ChemTapeConfig(**base).hash() != cfg.hash()
