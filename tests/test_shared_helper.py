"""Shared helpers, stages 1-2 (Plans/shared-helper-reuse.md, map-bias notebook §29)."""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "experiments" / "chem_tape"))

import shared_helper as sh  # noqa: E402
from folding_evolution.chem_tape import tagged  # noqa: E402
from folding_evolution.chem_tape.tagged import RECV  # noqa: E402



def genome(runs, L):
    """runs: [(tag, [ops or (op, tag)])], NOP-padded to L cells."""
    return tagged.build([], [(t, tuple(sh._cells(b))) for t, b in runs], L, random.Random(0))


def test_form_sizes_and_fit():
    assert (sh.form_cells("shared"), sh.form_cells("partly"), sh.form_cells("duplicated")) == (24, 27, 33)
    assert sh.form_genome("duplicated", 32) is None
    for name in sh.FORMS:
        for L in (64, 128):
            assert sh.form_genome(name, L).shape == (2 * L,)
    assert sh.form_genome("shared", 32) is not None and sh.form_genome("partly", 32) is not None


@pytest.mark.parametrize("name", list(sh.FORMS))
def test_hand_built_forms_are_fully_exact(name):
    m = sh.machine()
    for L in sh.LENGTHS:
        g = sh.form_genome(name, L)
        if g is not None:
            assert (sh.outputs(g, m) == sh.LABELS).all(), (name, L)


def test_output_tag_0_matches_evaluate_tagged():
    """Output 0 equals the existing single-output evaluator (leftmost)."""
    from dataclasses import replace
    from folding_evolution.chem_tape.config import ChemTapeConfig
    from folding_evolution.chem_tape.tasks import build_task
    task = build_task(ChemTapeConfig(task="mbs_max_gt_5", alphabet="tagged", arm="TAG"), 0)
    task = replace(task, inputs=[tuple(x) for x in sh.X_ALL[::7]], labels=sh.LABELS[0, ::7])
    m = sh.machine(sh.X_ALL[::7])
    r = random.Random(0)
    gs = [tagged.random_genotype(64, r) for _ in range(300)]
    gs += [sh.form_genome(n, 64) for n in sh.FORMS]
    _, preds = tagged.evaluate_tagged(gs, task, combine="leftmost")
    for g, p in zip(gs, preds):
        assert (sh.outputs(g, m)[0] == p).all()


def test_knockout_consumer_counts_on_hand_built_forms():
    m = sh.machine()
    c = sh.classify(sh.form_genome("shared", 32), m)
    assert c["tags"] == [0, 3, 1, 2] and c["consumer_counts"] == [3, 2, 1, 1]
    assert c["form"] == "shared" and c["pure_helpers"] == [1] and c["output_as_helper"]
    c = sh.classify(sh.form_genome("partly", 64), m)
    assert c["consumer_counts"] == [3, 1, 1] and c["form"] == "partly" and not c["pure_helpers"]
    c = sh.classify(sh.form_genome("duplicated", 64), m)
    assert c["consumer_counts"] == [1, 1, 1] and c["form"] == "duplicated"
    assert not c["output_as_helper"] and not c["other_output_helper"]


def test_knockout_ignores_a_read_but_unused_recv():
    """A RECV that is read and then buried under the real result counts for nothing."""
    A, B = sh.A_BODY, sh.B_BODY
    g = genome([(0, A), (3, B),
                (1, [(RECV, 3)] + A + B + sh.AND_TAIL),          # RECV 3 left at the bottom
                (2, A + B + sh.OR_TAIL)], L=64)
    c = sh.classify(g, sh.machine())
    assert c["fully_exact"] and c["consumer_counts"] == [1, 0, 1, 1]
    assert c["form"] == "duplicated"


def test_knockout_only_blanks_the_chosen_body():
    g = sh.form_genome("shared", 64)
    k = sh.knockout(g, 1)
    spans = sh.run_spans(g)
    _, lo, hi = spans[1]
    assert (k[lo:hi] == 0).all()
    mask = np.ones(len(g), dtype=bool)
    mask[lo:hi] = False
    assert (k[mask] == g[mask]).all()
    assert [t for t, _, _ in sh.run_spans(k)] == [t for t, _, _ in spans]


def test_leftmost_reads_only_the_first_run_of_an_output_tag():
    A, B = sh.A_BODY, sh.B_BODY
    good = genome([(0, A), (1, A + B + sh.AND_TAIL), (2, A + B + sh.OR_TAIL)], L=64)
    shadowed = genome([(0, A), (1, [3]), (1, A + B + sh.AND_TAIL), (2, A + B + sh.OR_TAIL)], L=64)
    assert sh.classify(good)["fully_exact"]
    c = sh.classify(shadowed)
    assert c["exact"] == [True, False, True]
    assert c["consumer_counts"][2] == 0                        # the silent second tag-1 run


def test_exactness_cache_and_prefilter_agree_with_full_evaluation():
    r = random.Random(1)
    ex = sh.Exactness()
    m = sh.machine()
    gs = [sh.form_genome("shared", 64)]
    gs += list(tagged.mutate_batch(np.repeat(gs[0][None], 200, axis=0), 0.03, np.random.default_rng(2)))
    gs += [tagged.random_genotype(64, r) for _ in range(50)]
    for g in gs:
        assert (ex(g) == (sh.outputs(g, m) == sh.LABELS).all(axis=1)).all()


def test_preserve_cell_smoke():
    row = sh.preserve_cell(("shared", 64, "v2", "other", 30, 0))
    assert 0 <= row["fully_exact"] <= 1 and len(row["keep"]) == 3 and "helper_intact" in row
    row = sh.preserve_cell(("duplicated", 64, "mutation", None, 30, 1))
    assert 0 <= row["mean_lost"] <= 3 and "helper_intact" not in row


def test_homologous_crossover_of_identical_forms_keeps_them_exact():
    """Crossover of a form with itself only ever reassembles the same runs."""
    r = random.Random(3)
    g = sh.form_genome("shared", 64)
    ex = sh.Exactness()
    for v in sh.VARIANTS:
        kids = [tagged.crossover(g, g, r, v) for _ in range(50)]
        assert all(sh.helper_intact(k) for k in kids if ex(k).all())


def test_preserve_cells_cover_the_plan():
    cells = sh.preserve_cells(10)
    keys = {(f, L, op, p) for f, L, op, p, _, _ in cells}
    assert ("shared", 32, "mutation", None) in keys
    assert ("shared", 32, "v2", "other") not in keys                  # duplicated does not fit at 32
    assert ("partly", 32, "v2", "other") in keys
    assert ("duplicated", 64, "v1c", "form_B") in keys
    assert len({s for *_, s in cells}) == len(cells)
