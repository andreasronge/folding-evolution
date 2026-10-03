"""Map-bias §30 (Plans/establishment-s30.md): random latent tags and the sweep files."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments" / "chem_tape"))

import shared_helper as sh  # noqa: E402
from folding_evolution.chem_tape import evolve, tagged  # noqa: E402
from sweep import expand_grid  # noqa: E402

SWEEPS = ROOT / "experiments" / "chem_tape" / "sweeps" / "mapbias"


@pytest.mark.parametrize("name", list(sh.FORMS))
def test_random_latent_forms_compute_the_same_and_classify_the_same(name):
    m = sh.machine()
    for L in sh.LENGTHS:
        z, r = sh.form_genome(name, L), sh.form_genome(name, L, "random")
        if z is None:
            assert r is None
            continue
        assert sh.semantic_key(z) == sh.semantic_key(r)
        ops_z, tags_z = tagged.split(z)
        ops_r, tags_r = tagged.split(r)
        assert (ops_z == ops_r).all()
        body = np.array([op not in (0, tagged.SEP, tagged.RECV) for op in ops_z.tolist()])
        assert (tags_z[body] == 0).all() and (tags_r[body] != 0).sum() > body.sum() // 2
        assert (tags_r[~body] == tags_z[~body]).all()          # SEP, RECV and padding tags kept
        assert sh.classify(r, m) == sh.classify(z, m)


def test_default_latent_is_unchanged():
    assert sh.form_genome("shared", 64).tobytes() == sh.form_genome("shared", 64, "zero").tobytes()
    with pytest.raises(ValueError):
        sh.form_genome("shared", 64, "other")


def _configs(name):
    return expand_grid(yaml.safe_load((SWEEPS / f"{name}.yaml").read_text()))


@pytest.mark.parametrize("name,n,cells", [("s30_est_dup", 480, 16), ("s30_est_partly", 540, 18),
                                          ("s30_dup_latent", 60, 2)])
def test_sweep_sizes_and_unique_hashes(name, n, cells):
    cfgs = _configs(name)
    assert len(cfgs) == n and len({c.hash() for c in cfgs}) == n
    assert len({(c.tape_length, c.crossover_rate, c.seed_tapes) for c in cfgs}) == cells


@pytest.mark.parametrize("name,competitor", [("s30_est_dup", "duplicated"), ("s30_est_partly", "partly")])
def test_initial_shares_are_exact(name, competitor):
    seen = set()
    for c in _configs(name):
        key = (c.tape_length, c.seed_tapes)
        if key in seen:
            continue
        seen.add(key)
        k = len(c.seed_tapes.split(","))
        pop = evolve.build_initial_population(c, evolve.make_rng(c), c.pop_size)
        cnt = Counter(g.tobytes() for g in pop)
        shared = sh.form_genome("shared", c.tape_length).tobytes()
        other = sh.form_genome(competitor, c.tape_length).tobytes()
        assert set(cnt) == {shared, other}
        assert cnt[shared] == -(-1024 // k)                   # 32, 103, 256, 512
        assert c.generations == 300 and c.log_every == 5 and c.crossover_rate in (0.7, 0.0)


def test_latent_arm_seeds_random_latent_duplicated_form():
    for c in _configs("s30_dup_latent"):
        assert c.seed_tapes == sh.form_genome("duplicated", c.tape_length, "random").tobytes().hex()
        assert c.generations == 1000 and c.crossover_rate == 0.7
