"""Shared helpers, stage 3 code (multi-output task, seeding, wide lexicase, census; §29)."""

from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "experiments" / "chem_tape"))

import shared_helper as sh  # noqa: E402
from folding_evolution.chem_tape import evolve, multi_output, tagged  # noqa: E402
from folding_evolution.chem_tape.config import ChemTapeConfig  # noqa: E402
from folding_evolution.chem_tape.tasks import build_task  # noqa: E402

BASE = dict(arm="TAG", alphabet="tagged", tag_combine="leftmost", task="mbs_three", n_examples=64,
            holdout_size=256, selection_mode="lexicase", fitness_metric="balanced", fast_rng=True,
            tagged_crossover="v2", mutation_rate=0.015, backend="numpy", disable_early_termination=True)


def _cfg(**kw):
    return ChemTapeConfig(**{**BASE, **kw})


def _seeds(*forms, L=64):
    return ",".join(sh.form_genome(f, L).tobytes().hex() for f in forms)


def _random_pop(n=200, L=64, seed=0):
    r = random.Random(seed)
    pop = [tagged.random_genotype(L, r) for _ in range(n)]
    for f in sh.FORMS:
        g = sh.form_genome(f, L)
        pop += [g] + list(tagged.mutate_batch(np.repeat(g[None], 40, axis=0), 0.03, np.random.default_rng(seed)))
    return pop


def test_three_output_task_labels_and_predictions():
    task = build_task(_cfg(tape_length=64), 3)
    assert task.output_tags == (0, 1, 2) and task.labels.shape == (192,)
    X = np.array(task.inputs)
    a, b = (X.max(axis=1) > 5).astype(int), (X.sum(axis=1) > 10).astype(int)
    assert (task.labels == np.concatenate([a, a & b, a | b])).all()
    assert task.holdout_labels.shape == (3 * 256,)
    pop = _random_pop()
    _, preds = tagged.evaluate_tagged(pop, task, combine="leftmost")
    m = multi_output.machine(X)
    for g, p in zip(pop, preds):
        assert (p.reshape(3, 64) == sh.outputs(g, m)).all()


def test_three_output_task_needs_tag_arm():
    with pytest.raises(ValueError):
        build_task(ChemTapeConfig(task="mbs_three", alphabet="v2_probe"), 0)


def test_src_classify_matches_stage1_classify():
    m = multi_output.machine()
    for g in _random_pop(60):
        a = sh.classify(g, m)
        b = multi_output.classify(g, m, (0, 1, 2), sh.LABELS)
        assert a == b


def test_default_single_output_paths_unchanged():
    r = random.Random(5)
    task = build_task(ChemTapeConfig(arm="TAG", alphabet="tagged", task="mbs_xor"), 0)
    m = tagged._machine_for(task)
    for _ in range(300):
        g = tagged.random_genotype(64, r)
        for comb in ("max", "leftmost"):
            assert tagged.run_census(g, comb) == tagged.run_census(g, comb, (0,))
            one = tagged.genome_outputs(g, m, combine=comb)
            assert (tagged.genome_outputs(g, m, combine=comb, out_tags=(0,))[0] == one).all()


def test_run_census_reads_from_every_output_tag():
    g = sh.form_genome("shared", 64)
    runs, out, read, helpers, _ = tagged.run_census(g, "leftmost", (0, 1, 2))
    assert (runs, out, read, helpers) == (4, 3, 4, 1)
    assert tagged.run_census(g, "leftmost")[2:4] == (1, 0)


def test_tagged_seed_tapes_and_split():
    cfg = _cfg(tape_length=64, pop_size=100, seed_tapes=_seeds("shared", "duplicated"),
               seed_fraction=1.0, seed_split=True)
    pop = evolve.build_initial_population(cfg, evolve.make_rng(cfg), 100)
    c = Counter(g.tobytes() for g in pop)
    assert c == {sh.form_genome("shared", 64).tobytes(): 50, sh.form_genome("duplicated", 64).tobytes(): 50}
    cfg = _cfg(tape_length=32, pop_size=64, seed_tapes=_seeds("shared", L=32), seed_fraction=1.0)
    pop = evolve.build_initial_population(cfg, evolve.make_rng(cfg), 64)
    assert all(np.array_equal(g, sh.form_genome("shared", 32)) for g in pop)
    with pytest.raises(ValueError):
        evolve._parse_seed_tapes(_cfg(tape_length=32, seed_tapes=_seeds("shared", L=64), seed_fraction=1.0))


def test_seed_split_and_track_shared_are_tag_only_and_hash_neutral():
    with pytest.raises(ValueError):
        ChemTapeConfig(seed_split=True)
    with pytest.raises(ValueError):
        ChemTapeConfig(track_shared=True)
    assert ChemTapeConfig(arm="TAG").hash() == ChemTapeConfig(arm="TAG", seed_split=False, track_shared=False).hash()
    assert ChemTapeConfig(arm="TAG").hash() != ChemTapeConfig(arm="TAG", track_shared=True).hash()


def _lexicase_by_hand(rows: np.ndarray, order) -> int:
    alive = list(range(len(rows)))
    for c in order:
        passing = [a for a in alive if rows[a, c]]
        if passing:
            alive = passing
    assert len(alive) == 1
    return alive[0]


@pytest.mark.parametrize("E", [70, 128, 192, 200])
def test_wide_lexicase_matches_case_by_case_lexicase(E):
    rng = np.random.default_rng(E)
    cases = rng.random((300, E)) < rng.random((300, 1))          # varied pass rates
    cases[:40] = cases[0]                                         # a large group
    group_cases, _ = np.unique(cases, axis=0, return_inverse=True)
    n = 600
    got = evolve._lex_winners_wide(group_cases, n, np.random.default_rng(1))
    perms = np.random.default_rng(1).random((n, E)).argsort(axis=1)
    want = [_lexicase_by_hand(group_cases, p) for p in perms]
    assert list(got) == want


def test_wide_lexicase_batch_returns_members_of_winning_groups():
    rng = np.random.default_rng(0)
    cases = rng.random((500, 192)) < 0.6
    cases[100:300] = True                                         # 200 perfect individuals
    picks = evolve._lexicase_batch(cases, 2000, np.random.default_rng(2), wide=True)
    assert set(picks.tolist()) <= set(range(100, 300))
    assert len(set(picks.tolist())) > 150                         # uniform within the group


@pytest.mark.parametrize("arm,L,seeds,want", [
    ("shared", 32, ("shared",), {"shared": 1.0}),
    ("shared", 128, ("shared",), {"shared": 1.0}),
    ("dup", 64, ("duplicated",), {"duplicated": 1.0}),
    ("mixed", 64, ("shared", "duplicated"), {"shared": 0.5, "duplicated": 0.5}),
])
def test_generation_zero_census(arm, L, seeds, want):
    cfg = _cfg(tape_length=L, pop_size=512, generations=2, log_every=1, seed=4,
               seed_tapes=_seeds(*seeds, L=L), seed_fraction=1.0, seed_split=True,
               track_shared=True, track_runs=True)
    res = evolve.run_evolution(cfg)
    g0 = res.shared_stats[0]
    assert g0["gen"] == 0 and g0["fully_exact"] == 1.0 and g0["exact"] == [1.0, 1.0, 1.0]
    assert g0["train_perfect"] == 1.0 and g0["n"] == 256
    for form, share in want.items():
        assert g0[form] == pytest.approx(share, abs=0.1 if arm == "mixed" else 0)
    assert len(res.shared_stats) == 3 and res.run_stats[0]["helpers"] == (1.0 if arm == "shared" else
                                                                         0.5 if arm == "mixed" else 0.0)


def test_track_shared_draws_no_evolution_randomness():
    kw = dict(tape_length=64, pop_size=128, generations=6, log_every=2, seed=9,
              seed_tapes=_seeds("shared", "duplicated"), seed_fraction=1.0, seed_split=True)
    a = evolve.run_evolution(_cfg(**kw))
    b = evolve.run_evolution(_cfg(track_shared=True, **kw))
    assert np.array_equal(a.best_genotype, b.best_genotype)
    assert [s.mean_fitness for s in a.stats.history] == [s.mean_fitness for s in b.stats.history]


def test_track_exact_any_refuses_multi_output():
    with pytest.raises(ValueError):
        evolve.run_evolution(_cfg(tape_length=32, pop_size=32, generations=1, track_exact_any=True))


def test_outputs_in_a_cycle_are_evaluated_independently():
    """Codex review 1 (P2): two output runs reading each other must give the same values
    as evaluating each output alone, whatever the order of the output tags."""
    m = multi_output.machine(multi_output.X_ALL[:50])
    g = tagged.build([], [(0, ((tagged.RECV, 1), (3, 0), (7, 0))),
                          (1, ((tagged.RECV, 0), (3, 0), (7, 0)))], 16, random.Random(0))
    alone = [tagged.genome_outputs(g, m, combine="leftmost", out_tags=(t,))[0] for t in (0, 1)]
    for order in ((0, 1), (1, 0)):
        got = tagged.genome_outputs(g, m, combine="leftmost", out_tags=order)
        for t, v in zip(order, got):
            assert (v == alone[t]).all()
    assert (alone[0] == 2).all() and (alone[1] == 2).all()
    r = random.Random(7)
    for _ in range(300):
        g = tagged.random_genotype(24, r)
        for comb in ("max", "leftmost"):
            got = tagged.genome_outputs(g, m, combine=comb, out_tags=(0, 1, 2))
            for t, v in zip((0, 1, 2), got):
                assert (v == tagged.genome_outputs(g, m, combine=comb, out_tags=(t,))[0]).all()


def test_multi_output_rejects_task_alternation():
    """Codex review 2 (P2): census and run census keep the first task's outputs."""
    for kw in (dict(task_alternating_values="mbs_three,mbs_xor"),
               dict(task="mbs_xor", task_alternating_values="mbs_xor,mbs_or", track_shared=True)):
        with pytest.raises(ValueError):
            evolve.run_evolution(_cfg(**{"tape_length": 32, "pop_size": 16, "generations": 2,
                                         "task_alternating_period": 1, **kw}))
