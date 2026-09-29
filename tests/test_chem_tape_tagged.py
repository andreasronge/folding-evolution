"""Tagged-run chemistry (map-bias notebook §8)."""

from __future__ import annotations

import collections
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


def test_duplicate_run_copies_body_under_a_fresh_tag_and_stays_inert():
    task = _task(ALL, AND)
    g = genome([(5, [1, 18, 16, 8]), (7, [1, 5, 16, 16, 7, 8]), (0, [2, (RECV, 5), (RECV, 7), 17])], L=40)
    rng = random.Random(3)
    for _ in range(20):
        d = tagged.duplicate_run(g, rng, same_tag=False)
        runs, before = tagged.parse_runs(d), tagged.parse_runs(g)
        assert len(d) == len(g) and len(runs) == len(before) + 1
        new = [r for r in runs if r[0] not in {t for t, _ in before}]
        strip = tagged._strip_trailing_nops
        assert len(new) == 1 and strip(new[0][1]) in [strip(b) for _, b in before]
        assert (outputs(d, task) == AND).all()      # the copy is unreferenced, so inert


def test_zero_duplication_rate_draws_no_extra_randomness():
    g = tagged.random_genotype(64, random.Random(0))
    a = tagged.mutate(g, 0.02, random.Random(9))
    b = tagged.mutate(g, 0.02, random.Random(9), dup_rate=0.0)
    assert a.tobytes() == b.tobytes()


def test_xor_task_labels():
    t = build_task(ChemTapeConfig(task="sum_gt_10_XOR_max_gt_5", alphabet="v2_probe"), 0)
    for x, y in zip(t.inputs, t.labels):
        assert y == int((sum(x) > 10) != (max(x) > 5))


def test_same_tag_duplicate_is_neutral():
    task = _task(ALL, AND)
    g = genome([(5, [1, 18, 16, 8]), (7, [1, 5, 16, 16, 7, 8]), (0, [2, (RECV, 5), (RECV, 7), 17])], L=40)
    rng = random.Random(4)
    for _ in range(20):
        d = tagged.duplicate_run(g, rng, same_tag=True)
        assert len(tagged.parse_runs(d)) == 4
        assert (outputs(d, task) == AND).all()      # max(A, A) = A


def test_duplication_never_truncates_existing_runs_on_a_full_tape():
    task = _task(ALL, AND)
    # Exactly full, no padding: no copy fits, so nothing may be cut off.
    g = genome([(5, [1, 18, 16, 8]), (7, [1, 5, 16, 16, 7, 8]), (0, [2, (RECV, 5), (RECV, 7), 17])])
    rng = random.Random(0)
    strip = tagged._strip_trailing_nops
    before = {(t, strip(b)) for t, b in tagged.parse_runs(g)}
    for _ in range(50):
        d = tagged.duplicate_run(g, rng)
        assert (outputs(d, task) == AND).all()
        assert before <= {(t, strip(b)) for t, b in tagged.parse_runs(d)}   # every original run survives


def test_fresh_tag_avoids_tags_read_by_a_dangling_recv():
    task = _task(ALL, AND)
    # RECV 9 reads a missing tag (constant 0); a "fresh" copy must never take tag 9.
    g = genome([(0, [(RECV, 9), 3, 7]), (4, [2])], L=40)
    base = outputs(g, task)
    rng = random.Random(1)
    for _ in range(200):
        d = tagged.duplicate_run(g, rng, same_tag=False)
        assert 9 not in {t for t, _ in tagged.parse_runs(d)}
        assert (outputs(d, task) == base).all()


def test_same_tag_copy_of_a_self_dependent_run_is_skipped():
    task = _task(ALL, AND)
    g = genome([(0, [(RECV, 0), 3, 7])], L=30)    # reads its own tag
    base = outputs(g, task)
    rng = random.Random(2)
    for _ in range(50):
        d = tagged.duplicate_run(g, rng, same_tag=True)
        assert (outputs(d, task) == base).all()


def test_every_duplication_is_neutral_on_random_genomes():
    """Silent (fresh-tag) and redundant (same-tag, non-recursive) copies must
    never change the organism's output."""
    task = _task()
    rng = random.Random(5)
    for _ in range(300):
        g = tagged.random_genotype(64, rng)
        d = tagged.duplicate_run(g, rng)
        assert (outputs(d, task) == outputs(g, task)).all()


def test_stratified_tasks_share_inputs_and_cover_all_four_cells():
    cfg = ChemTapeConfig(task="mbs_or", alphabet="v2_probe", n_examples=64, holdout_size=256)
    ts = {n: build_task(replace(cfg, task=n), 7) for n in ("mbs_max_gt_5", "mbs_sum_gt_10", "mbs_and", "mbs_or")}
    first = ts["mbs_or"]
    for t in ts.values():
        assert t.inputs == first.inputs and t.holdout_inputs == first.holdout_inputs
    cells = {((max(x) > 5), (sum(x) > 10)) for x in first.inputs}
    assert len(cells) == 4 and len(first.inputs) == 64 and len(first.holdout_inputs) == 256
    assert not set(first.inputs) & set(first.holdout_inputs)
    for x, y in zip(first.inputs, ts["mbs_and"].labels):
        assert y == int(max(x) > 5 and sum(x) > 10)


def test_reselect_on_flip_records_new_task_start_and_selects_on_it():
    base = ChemTapeConfig(task="mbs_max_gt_5", arm="TAG", alphabet="tagged", tape_length=64, pop_size=64,
                          generations=12, mutation_rate=0.015, selection_mode="lexicase", backend="numpy",
                          holdout_size=0, seed=1, task_alternating_period=4,
                          task_alternating_values="mbs_max_gt_5,mbs_sum_gt_10,mbs_and")
    old = run_evolution(base)
    new = run_evolution(replace(base, reselect_on_flip=True))
    assert all("at_flip_best_new_task" not in e for e in old.flip_events)
    assert all("at_flip_best_new_task" in e for e in new.flip_events) and len(new.flip_events) == 3  # gens 4, 8, 12
    assert base.hash() != replace(base, reselect_on_flip=True).hash()


def test_balanced_fitness_scores_constant_output_at_one_half():
    from folding_evolution.chem_tape.evaluate import evaluate_population
    cfg = ChemTapeConfig(task="mbs_and", arm="TAG", alphabet="tagged", tape_length=16, n_examples=64,
                         holdout_size=0, fitness_metric="balanced")
    t = build_task(cfg, 0)
    const0 = genome([(0, [2])], L=16)
    max5 = genome([(0, [1, 18, 16, 8])], L=16)
    f, _ = evaluate_population([const0, max5], t, cfg)
    assert abs(f[0] - 0.5) < 1e-9 and abs(f[1] - (0.5 * (1 + 2 / 3))) < 1e-9
    acc, _ = evaluate_population([const0], t, replace(cfg, fitness_metric="accuracy"))
    assert abs(acc[0] - 0.75) < 1e-9


def test_duplication_uses_leader_space():
    # Full tape whose first cells are leader junk: the copy fits by dropping leader cells.
    task = _task(ALL, AND)
    g = genome([(5, [1, 18, 16, 8]), (7, [1, 5, 16, 16, 7, 8]), (0, [2, (RECV, 5), (RECV, 7), 17])],
               leader=[(1, 0)] * 10)
    rng = random.Random(0)
    grew = 0
    for _ in range(30):
        d = tagged.duplicate_run(g, rng)
        assert (outputs(d, task) == AND).all()
        grew += len(tagged.parse_runs(d)) == 4
    assert grew > 0


OR = np.array([int(sum(x) > 10 or max(x) > 5) for x in ALL])
MAXB, SUMB = [1, 18, 16, 8], [1, 5, 16, 16, 7, 8]


def test_two_output_runs_join_by_max_as_or():
    assert (outputs(genome([(0, MAXB), (0, SUMB)]), _task(ALL, OR)) == OR).all()


def test_combine_markers_turn_the_join_into_and():
    task = _task(ALL, AND)
    g = genome([(0, MAXB), (0, SUMB + [tagged.C_MIN])])          # second run joins by min
    assert (outputs(g, task) == AND).all()
    g = genome([(0, MAXB), (0, [tagged.C_GATE] + SUMB)])        # gate: sum>10 if max>5 else 0
    assert (outputs(g, task) == AND).all()
    g = genome([(0, [3]), (0, [3, tagged.C_ADD])])              # 1 + 1
    assert (outputs(g, task) == 2).all()


def test_markers_do_nothing_when_executed():
    task = _task(ALL, AND)
    assert (outputs(genome([(0, [tagged.C_ADD] + MAXB + [tagged.C_MIN])]), task)
            == outputs(genome([(0, MAXB)]), task)).all()


def test_leftmost_combine_ignores_later_same_tag_runs():
    from folding_evolution.chem_tape.evaluate import evaluate_population
    cfg = ChemTapeConfig(task="mbs_or", arm="TAG", alphabet="tagged", tape_length=16, n_examples=64,
                         holdout_size=0, tag_combine="leftmost")
    t = replace(build_task(cfg, 0), inputs=ALL, labels=OR)
    g = genome([(0, MAXB), (0, SUMB)], L=16)
    _, p_left = evaluate_population([g], t, cfg)
    _, p_max = evaluate_population([g], t, replace(cfg, tag_combine="max"))
    assert (p_left[0] == np.array([int(max(x) > 5) for x in ALL])).all() and (p_max[0] == OR).all()
    assert cfg.hash() != replace(cfg, tag_combine="max").hash()


def test_comb_alphabet_draws_markers_and_plain_alphabet_never_does():
    rng = random.Random(0)
    comb = tagged.random_genotype(64, rng, n_ops=tagged.n_ops_for("tagged_comb"))
    plain = [tagged.random_genotype(64, rng) for _ in range(50)]
    assert tagged.split(comb)[0].max() < tagged.N_OPS_COMB
    assert all(tagged.split(g)[0].max() < tagged.N_OPS for g in plain)
    mutated = [tagged.mutate(plain[0], 0.5, rng) for _ in range(50)]
    assert all(tagged.split(g)[0].max() < tagged.N_OPS for g in mutated)


# ---------------- crossover v2 (map-bias notebook §25) ----------------

def _runs(g):
    strip = tagged._strip_trailing_nops
    return [(t, strip(b)) for t, b in tagged.parse_runs(g)]


def test_v2_run_free_first_parent_receives_runs_from_the_second():
    a = genome([], L=64, leader=[(1, 3)] * 64)            # all leader, no run
    b = genome([(0, [1, 5, 16, 16, 7, 8]), (4, [1, 18])], L=64)
    rng = random.Random(0)
    got_v1 = sum(bool(tagged.parse_runs(tagged.crossover(a, b, rng, "v1"))) for _ in range(200))
    got_v2 = sum(bool(tagged.parse_runs(tagged.crossover(a, b, rng, "v2"))) for _ in range(200))
    assert got_v1 == 0 and got_v2 > 100                   # j = len(rb) leaves the child empty, p = 1/3


def test_v2_padding_never_displaces_runs_that_fit():
    # Two runs with long NOP tails: v1's child overflows and loses b's run; v2 strips
    # the padding and keeps both, whole.
    a = genome([(0, [1, 5, 16, 16, 7, 8] + [0] * 30)], L=64)
    b = genome([(4, [1, 18, 16, 8] + [0] * 40)], L=64)
    ra, rb = tagged.parse_runs(a), tagged.parse_runs(b)
    assert len(tagged.build([], ra + rb, 64, random.Random(0))) == 128
    assert len(tagged.parse_runs(tagged.build([], ra + rb, 64, random.Random(0)))) == 1
    child = tagged.fit_runs([], ra + rb, 64, random.Random(0))
    assert _runs(child) == [(0, tuple((o, 0) for o in [1, 5, 16, 16, 7, 8])), (4, tuple((o, 0) for o in [1, 18, 16, 8]))]


def test_v2_never_cuts_a_kept_run_and_keeps_order():
    rng = random.Random(3)
    pop = [tagged.random_genotype(64, rng) for _ in range(40)]
    for _ in range(2000):
        a, b = rng.choice(pop), rng.choice(pop)
        child = tagged.crossover(a, b, rng, "v2")
        assert len(child) == 128
        pool = _runs(a) + _runs(b)
        kept = _runs(child)
        # Every child run is a whole parent run (the last may carry padding, stripped here).
        assert all(r in pool for r in kept)


def test_v2_equals_v1_when_the_child_fits():
    rng = random.Random(5)
    for _ in range(300):
        runs = [(rng.randrange(64), tuple((rng.randrange(20), 0) for _ in range(rng.randrange(1, 6))))
                for _ in range(rng.randrange(0, 5))]
        lead = [(rng.randrange(20), 0) for _ in range(rng.randrange(0, 10))]
        s = rng.randrange(10 ** 6)
        assert (tagged.build(lead, runs, 64, random.Random(s)) == tagged.fit_runs(lead, runs, 64, random.Random(s))).all()


def test_v2_overflow_deletion_is_uniform_over_runs():
    # Three 30-cell runs (93 cells incl. SEPs) in L = 64: one must go, whichever it is
    # with equal chance — output run or not.
    runs = [(0, tuple((1, 0) for _ in range(30))), (5, tuple((5, 0) for _ in range(30))),
            (9, tuple((6, 0) for _ in range(30)))]
    rng = random.Random(0)
    lost = collections.Counter()
    for _ in range(3000):
        kept = {t for t, _ in tagged.parse_runs(tagged.fit_runs([], runs, 64, rng))}
        assert len(kept) == 2
        lost[({0, 5, 9} - kept).pop()] += 1
    assert all(900 < lost[t] < 1100 for t in (0, 5, 9))


def test_v2_drops_leader_before_runs():
    lead = [(1, 0)] * 40
    runs = [(0, tuple((5, 0) for _ in range(20))), (3, tuple((6, 0) for _ in range(10)))]
    child = tagged.fit_runs(lead, runs, 64, random.Random(0))
    assert [t for t, _ in tagged.parse_runs(child)] == [0, 3]
    assert len(tagged.leader_cells(child)) == 64 - 32


def test_run_census_follows_recv_and_leftmost():
    g = genome([(0, [(RECV, 5), (RECV, 7), 7]), (5, [1, 18]), (7, [(RECV, 5)]), (9, [1]), (0, [(RECV, 9)])], L=40)
    assert tagged.run_census(g, "max") == (5, 2, 5, 3, 40 - 13)
    assert tagged.run_census(g, "leftmost") == (5, 2, 3, 2, 40 - 13)


def test_crossover_v2_and_track_runs_in_evolution():
    cfg = ChemTapeConfig(task="mb_max_gt_5", arm="TAG", alphabet="tagged", tape_length=64, pop_size=64,
                         generations=10, mutation_rate=0.015, selection_mode="lexicase", backend="numpy",
                         holdout_size=32, seed=2, log_every=5)
    base = run_evolution(cfg)
    tracked = run_evolution(replace(cfg, track_runs=True))
    assert base.best_genotype.tobytes() == tracked.best_genotype.tobytes()      # tracking draws no RNG
    assert [r["gen"] for r in tracked.run_stats] == [0, 5, 10]
    v2 = run_evolution(replace(cfg, tagged_crossover="v2", track_runs=True))
    assert len(v2.best_genotype) == 128
    assert cfg.hash() == replace(cfg, tagged_crossover="v1").hash() != replace(cfg, tagged_crossover="v2").hash()
