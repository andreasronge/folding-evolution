"""Allele decoder and paired composition search, using the production executor."""

from __future__ import annotations

import hashlib
import time

import numpy as np
from _folding_rust import rust_chem_execute_pop_batch

from folding_evolution.chem_tape.evolve import FastRandom, _lexicase_select
from experiments.chem_tape.composition_bank import INPUTS

R = 23000
ARMS = ("U", "F", "G", "G-marg")


def cumulative(weights):
    shares = np.asarray(weights, dtype=float) * R / np.sum(weights)
    counts = np.floor(shares).astype(np.int64)
    order = np.argsort(-(shares - counts), kind="stable")
    counts[order[: R - int(counts.sum())]] += 1
    return np.cumsum(counts)


def base_tables():
    u = np.tile(np.arange(1, 24) * 1000, (24, 1))
    w = np.ones(23)
    w[[1, 18, 22, 7, 9, 17]] = 3
    w[[5, 11]] = 1.5
    f = np.tile(cumulative(w), (24, 1))
    g = u.copy()
    start = np.full(23, 500)
    start[1] = 12000
    g[23] = np.cumsum(start)
    after_input = np.full(23, 500)
    after_input[[5, 11]] = 2250
    after_input[[18, 22]] = 4500
    g[1] = np.cumsum(after_input)
    after_int = np.full(23, 500)
    after_int[[1, 7, 9, 17]] = 3375
    for token in (2, 3, 5, 6, 7, 8, 11, 15, 16, 17, 18, 19, 22):
        g[token] = np.cumsum(after_int)
    assert np.min(np.diff(g, prepend=0, axis=1)) >= 250
    return {"U": u, "F": f, "G": g}


class Decoder:
    def __init__(self, table):
        table = np.asarray(table, dtype=np.int64)
        if (
            table.shape != (24, 23)
            or np.any(np.diff(table, prepend=0, axis=1) <= 0)
            or np.any(table[:, -1] != R)
        ):
            raise ValueError("invalid cumulative decoder table")
        self.table = table
        self.lookup = np.array(
            [np.searchsorted(row, np.arange(R), side="right") for row in table],
            dtype=np.uint8,
        )
        self.tied = np.all(table == table[0])

    def decode(self, alleles):
        alleles = np.asarray(alleles)
        if alleles.ndim != 2 or np.any(alleles < 0) or np.any(alleles >= R):
            raise ValueError("invalid allele array")
        if self.tied:
            return self.lookup[0, alleles]
        out = np.empty(alleles.shape, dtype=np.uint8)
        previous = np.full(len(alleles), 23)
        for j in range(alleles.shape[1]):
            out[:, j] = self.lookup[previous, alleles[:, j]]
            previous = out[:, j]
        return out

    def hash(self):
        return hashlib.sha256(self.table.astype("<i8").tobytes()).hexdigest()


def outputs(programs, inputs):
    return np.array(
        rust_chem_execute_pop_batch(
            programs.tolist() if isinstance(programs, np.ndarray) else programs,
            "NOP",
            "NOP",
            inputs,
            "intlist",
            "v2_rmin",
            0,
        ),
        dtype=np.int64,
    ).reshape(len(programs), len(inputs))


def search(job):
    cell, arm, table, seed, cap, pop_size = job[:6]
    inputs = job[6] if len(job) == 7 else INPUTS
    start = time.monotonic()
    decoder = Decoder(table)
    # Independent streams prevent arm-dependent selection from changing the
    # initialization, cases, crossover positions, or allele-resampling draws.
    cases_rng = np.random.default_rng([seed, 0])
    initial_rng = np.random.default_rng([seed, 1])
    variation = np.random.default_rng([seed, 2])
    selection = FastRandom(seed + 100000000)
    indices = cases_rng.choice(len(inputs), 64, replace=False)
    training = [inputs[i] for i in indices]
    label = np.asarray(cell["labels"])
    pop = initial_rng.integers(R, size=(pop_size, 32), dtype=np.int32)
    shortcuts = 0
    unique_shortcuts = 0
    training_perfect_individuals = 0
    checked = {}
    decode_seconds = 0.0
    curve = []
    budget_times = {}
    solved_at = None
    evaluations = 0
    budgets = (32768, 65536, 131072, 262144, 524288)
    for generation in range(cap // pop_size):
        tick = time.monotonic()
        programs = decoder.decode(pop)
        decode_seconds += time.monotonic() - tick
        observed = outputs(programs, training)
        correct = observed == label[indices]
        scores = correct.sum(1)
        evaluations += pop_size
        perfect = np.flatnonzero(scores == 64)
        for i in perfect:
            training_perfect_individuals += 1
            key = programs[i].tobytes()
            if key not in checked:
                checked[key] = bool(
                    np.array_equal(outputs(programs[i : i + 1], inputs)[0], label)
                )
                if not checked[key]:
                    unique_shortcuts += 1
            if not checked[key]:
                shortcuts += 1
            if checked[key]:
                solved_at = evaluations
                break
        elapsed = time.monotonic() - start
        for b in budgets:
            if evaluations >= b and str(b) not in budget_times:
                budget_times[str(b)] = elapsed
        if generation % 32 == 0 or solved_at is not None:
            curve.append(
                [evaluations, int(scores.max()), len(np.unique(correct, axis=0))]
            )
        if solved_at is not None:
            break
        if evaluations == cap:
            break
        _, inverse = np.unique(correct, axis=0, return_inverse=True)
        groups = [np.flatnonzero(inverse == i) for i in range(inverse.max() + 1)]
        group_cases = np.array([correct[g[0]] for g in groups])
        n = pop_size - 2
        # Both parent choices are consumed each generation, regardless of
        # whether the independently drawn crossover mask uses parent two.
        parents = np.array(
            [_lexicase_select(groups, group_cases, selection) for _ in range(2 * n)]
        ).reshape(2, n)
        crossing = variation.random(n) < 0.7
        points = variation.integers(1, 32, size=n)
        mask = variation.random((n, 32)) < 0.03
        replacements = variation.integers(R, size=(n, 32), dtype=np.int32)
        child = pop[parents[0]].copy()
        splice = crossing[:, None] & (np.arange(32)[None, :] >= points[:, None])
        child = np.where(splice, pop[parents[1]], child)
        child[mask] = replacements[mask]
        elite = np.argsort(-scores, kind="stable")[:2]
        pop = np.concatenate((pop[elite], child))
    elapsed = time.monotonic() - start
    for b in budgets:
        if solved_at is not None and solved_at <= b:
            budget_times[str(b)] = elapsed
    return dict(
        cell=cell["id"],
        arm=arm,
        seed=seed,
        cap=cap,
        pop_size=pop_size,
        solved=solved_at is not None,
        evaluations=solved_at or evaluations,
        seconds=elapsed,
        budget_seconds=budget_times,
        shortcuts=shortcuts,
        unique_shortcuts=unique_shortcuts,
        training_perfect_individuals=training_perfect_individuals,
        decode_seconds=decode_seconds,
        generations=generation + 1,
        training_indices=indices.tolist(),
        curve=curve,
        table_hash=decoder.hash(),
    )
