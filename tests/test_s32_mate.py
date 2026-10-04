"""Map-bias §32: crossover_mate (selected / self / random)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments" / "chem_tape"))

from folding_evolution.chem_tape import evolve, tagged  # noqa: E402
from folding_evolution.chem_tape.config import ChemTapeConfig  # noqa: E402
from sweep import expand_grid  # noqa: E402

BASE = dict(arm="TAG", alphabet="tagged", tag_combine="leftmost", task="mbs_three", n_examples=64,
            holdout_size=256, selection_mode="lexicase", fitness_metric="balanced", fast_rng=True,
            tagged_crossover="v2", mutation_rate=0.015, backend="numpy", disable_early_termination=True,
            tape_length=64, pop_size=128, generations=8, crossover_rate=0.7, seed=3)


def test_default_mate_is_hash_neutral_and_replays():
    a = ChemTapeConfig(**BASE)
    b = ChemTapeConfig(**BASE, crossover_mate="selected")
    assert a.hash() == b.hash()
    ra, rb = evolve.run_evolution(a), evolve.run_evolution(b)
    assert np.array_equal(ra.best_genotype, rb.best_genotype)
    assert [s.mean_fitness for s in ra.stats.history] == [s.mean_fitness for s in rb.stats.history]


def test_default_replays_a_s31_config():
    cfg = expand_grid(yaml.safe_load((ROOT / "experiments/chem_tape/sweeps/mapbias/s31_stage4.yaml").read_text()))[0]
    from dataclasses import replace
    cfg = replace(cfg, generations=5, pop_size=128)
    r1 = evolve.run_evolution(cfg)
    r2 = evolve.run_evolution(replace(cfg, crossover_mate="selected"))
    assert np.array_equal(r1.best_genotype, r2.best_genotype)


def test_mate_values_validated():
    with pytest.raises(ValueError):
        ChemTapeConfig(**BASE, crossover_mate="other")
    with pytest.raises(ValueError):
        ChemTapeConfig(crossover_mate="self")
    assert ChemTapeConfig(**BASE, crossover_mate="self").hash() != ChemTapeConfig(**BASE).hash()
    with pytest.raises(ValueError):                         # codex review 1: lineage would record the wrong mate
        ChemTapeConfig(**BASE, crossover_mate="self", track_lineage=True)
    ChemTapeConfig(**BASE, track_lineage=True)


@pytest.mark.parametrize("batched", [True, False])
def test_self_mate_children_only_contain_the_parents_runs(batched, monkeypatch):
    cfg = ChemTapeConfig(**{**BASE, "fast_rng": batched, "crossover_mate": "self", "crossover_rate": 1.0,
                            "mutation_rate": 0.0})
    rng = evolve.make_rng(cfg)
    pop = [tagged.random_genotype(64, rng) for _ in range(64)]
    seen = []
    real = evolve.crossover

    def spy(a, b, cfg_, rng_):
        seen.append((a, b))
        return real(a, b, cfg_, rng_)
    monkeypatch.setattr(evolve, "crossover", spy)
    fits = np.ones(len(pop))
    cases = np.ones((len(pop), 192), dtype=bool)
    evolve._reproduce_one_island(pop, fits, cfg, rng, cases=cases)
    assert seen and all(a is b for a, b in seen)
    for a, _ in seen[:20]:
        child = real(a, a, cfg, rng)
        parent_runs = {(t, tagged._strip_trailing_nops(b)) for t, b in tagged.parse_runs(a)}
        assert {(t, tagged._strip_trailing_nops(b)) for t, b in tagged.parse_runs(child)} <= parent_runs


def test_random_mate_uses_fresh_genomes(monkeypatch):
    cfg = ChemTapeConfig(**{**BASE, "crossover_mate": "random", "crossover_rate": 1.0})
    rng = evolve.make_rng(cfg)
    pop = [tagged.random_genotype(64, rng) for _ in range(32)]
    ids = {id(g) for g in pop}
    seen = []
    real = evolve.crossover
    monkeypatch.setattr(evolve, "crossover", lambda a, b, c, r: seen.append(b) or real(a, b, c, r))
    evolve._reproduce_one_island(pop, np.ones(32), cfg, rng, cases=np.ones((32, 192), dtype=bool))
    assert seen and all(id(b) not in ids for b in seen)


@pytest.mark.parametrize("name,n", [("s32_latent_rare", 180), ("s32_latent_copy", 200), ("s32_latent_alone", 30),
                                    ("s32_mate", 200), ("s32_cases256", 50), ("s32_stage4_more", 50)])
def test_s32_sweeps(name, n):
    cfgs = expand_grid(yaml.safe_load((ROOT / f"experiments/chem_tape/sweeps/mapbias/{name}.yaml").read_text()))
    assert len(cfgs) == n and len({c.hash() for c in cfgs}) == n


def test_s32_latent_competitor_and_start_counts():
    import shared_helper as sh
    from s32_make_sweeps import partly_plus_b
    from collections import Counter
    g = partly_plus_b(64)
    c = sh.classify(g, sh.machine())
    assert c["form"] == "partly" and c["consumer_counts"] == [3, 0, 1, 1] and sh.helper_intact(g)
    for name in ("s32_latent_rare", "s32_latent_copy"):
        seen = set()
        for cfg in expand_grid(yaml.safe_load((ROOT / f"experiments/chem_tape/sweeps/mapbias/{name}.yaml").read_text())):
            if cfg.seed_tapes + cfg.seed_counts in seen:
                continue
            seen.add(cfg.seed_tapes + cfg.seed_counts)
            pop = evolve.build_initial_population(cfg, evolve.make_rng(cfg), cfg.pop_size)
            cnt = Counter(x.tobytes() for x in pop)
            k = len(cfg.seed_tapes.split(","))
            want = 1 if cfg.seed_counts else -(-1024 // k)
            assert cnt[sh.form_genome("shared", 64).tobytes()] == want and cnt[g.tobytes()] == 1024 - want
