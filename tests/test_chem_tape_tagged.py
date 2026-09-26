"""Tagged-run chemistry (map-bias notebook §8)."""

from __future__ import annotations

import itertools
import random
from dataclasses import replace

import numpy as np

from folding_evolution.chem_tape import executor, tagged
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evolve import run_evolution
from folding_evolution.chem_tape.tasks import build_task
from folding_evolution.chem_tape.tagged import RECV, SEP

ALL = [tuple(x) for x in itertools.product(range(10), repeat=4)]
AND = np.array([int(sum(x) > 10 and max(x) > 5) for x in ALL])


def _task(inputs=None, labels=None):
    t = build_task(ChemTapeConfig(task="sum_gt_10_AND_max_gt_5", alphabet="v2_probe"), 0)
    if inputs is not None:
        t = replace(t, inputs=inputs, labels=np.asarray(labels))
    return t


def genome(runs, L=None, leader=()):
    """runs: [(tag, [ops or (op, tag)])]."""
    cells = list(leader)
    for tag, body in runs:
        cells.append((SEP, tag))
        cells += [c if isinstance(c, tuple) else (c, 0) for c in body]
    L = L or len(cells)
    cells += [(0, 0)] * (L - len(cells))
    return tagged.join([c[0] for c in cells], [c[1] for c in cells])


def outputs(g, task):
    return tagged.evaluate_tagged([g], task)[1][0]


def test_vectorised_interpreter_matches_python_executor():
    task = _task()
    rng = random.Random(0)
    for _ in range(600):
        body = [rng.randrange(20) for _ in range(rng.randrange(1, 14))]
        got = outputs(genome([(0, body)]), task)
        want = [executor.execute_program(body, task.alphabet, x, "intlist", alphabet_name="v2_probe")
                for x in task.inputs]
        assert list(got) == want, body


def test_hand_built_and_is_exact_on_all_lists():
    task = _task(ALL, AND)
    g = genome([(5, [1, 18, 16, 8]),                        # max>5
                (7, [1, 5, 16, 16, 7, 8]),                  # sum>10
                (0, [2, (RECV, 5), (RECV, 7), 17])])        # CONST_0 RECV5 RECV7 IF_GT
    assert (outputs(g, task) == AND).all()


def test_unreferenced_run_is_inert_and_position_free():
    task = _task(ALL, AND)
    base = [(5, [1, 18, 16, 8]), (7, [1, 5, 16, 16, 7, 8]), (0, [2, (RECV, 5), (RECV, 7), 17])]
    extra = (33, [1, 5, 9, 7])
    out = outputs(genome(base), task)
    assert (outputs(genome(base + [extra]), task) == out).all()
    assert (outputs(genome([extra] + base), task) == out).all()
    assert (outputs(genome(base[::-1]), task) == out).all()     # run order doesn't matter


def test_duplicate_tags_combine_by_max_and_missing_tag_is_zero():
    task = _task(ALL, AND)
    one = genome([(0, [3])])
    zero_and_one = genome([(0, [2]), (0, [3])])
    assert (outputs(zero_and_one, task) == outputs(one, task)).all()
    assert (outputs(genome([(0, [(RECV, 9)])]), task) == 0).all()


def test_cycles_terminate():
    task = _task()
    g = genome([(0, [(RECV, 1)]), (1, [(RECV, 0), 3, 7])])
    assert outputs(g, task).shape == (len(task.inputs),)


def test_leader_cells_before_first_sep_are_ignored():
    task = _task(ALL, AND)
    g = genome([(0, [3])], leader=[(1, 0), (5, 0)])
    assert (outputs(g, task) == 1).all()


def test_variation_keeps_shape_and_ranges():
    rng = random.Random(1)
    a, b = tagged.random_genotype(64, rng), tagged.random_genotype(64, rng)
    for _ in range(200):
        for c in (tagged.mutate(a, 0.05, rng), tagged.crossover(a, b, rng)):
            ops, tags = tagged.split(c)
            assert len(c) == 128 and ops.max() < tagged.N_OPS and tags.max() < tagged.N_TAGS


def test_tagged_evolution_runs_and_is_deterministic():
    cfg = ChemTapeConfig(task="mb_max_gt_5", arm="TAG", alphabet="tagged", tape_length=64, pop_size=64,
                         generations=15, mutation_rate=0.015, selection_mode="lexicase", backend="numpy",
                         holdout_size=32, seed=2)
    r1, r2 = run_evolution(cfg), run_evolution(cfg)
    assert r1.best_genotype.tobytes() == r2.best_genotype.tobytes()
    assert len(r1.best_genotype) == 128
