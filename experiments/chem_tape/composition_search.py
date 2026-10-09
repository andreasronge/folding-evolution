"""Allele decoder and paired composition search, using the production executor."""

from __future__ import annotations

import copy
import hashlib
import time

import numpy as np
from _folding_rust import rust_chem_execute_pop_batch

from folding_evolution.chem_tape.evolve import FastRandom, _lexicase_select
from experiments.chem_tape.composition_bank import INPUTS

R = 23000
ARMS = ("U", "F", "G", "G-marg")


def cumulative(weights, allele_range=R):
    shares = np.asarray(weights, dtype=float) * allele_range / np.sum(weights)
    counts = np.floor(shares).astype(np.int64)
    order = np.argsort(-(shares - counts), kind="stable")
    counts[order[: allele_range - int(counts.sum())]] += 1
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
            table.ndim != 2
            or table.shape[0] != table.shape[1] + 1
            or table.shape[1] not in (23, 24)
            or np.any(np.diff(table, prepend=0, axis=1) <= 0)
            or np.any(table[:, -1] != table[0, -1])
        ):
            raise ValueError("invalid cumulative decoder table")
        self.allele_range = int(table[0, -1])
        self.n_tokens = table.shape[1]
        self.table = table
        self.lookup = np.array(
            [
                np.searchsorted(row, np.arange(self.allele_range), side="right")
                for row in table
            ],
            dtype=np.uint8,
        )
        self.tied = np.all(table == table[0])

    def decode(self, alleles):
        alleles = np.asarray(alleles)
        if (
            alleles.ndim != 2
            or np.any(alleles < 0)
            or np.any(alleles >= self.allele_range)
        ):
            raise ValueError("invalid allele array")
        if self.tied:
            return self.lookup[0, alleles]
        out = np.empty(alleles.shape, dtype=np.uint8)
        previous = np.full(len(alleles), self.n_tokens)
        for j in range(alleles.shape[1]):
            out[:, j] = self.lookup[previous, alleles[:, j]]
            previous = out[:, j]
        return out

    def hash(self):
        return hashlib.sha256(self.table.astype("<i8").tobytes()).hexdigest()

    def encode(self, programs, rng):
        """Draw independently and uniformly within each conditional allele interval."""
        programs = np.asarray(programs)
        if (
            programs.ndim != 2
            or programs.dtype.kind not in "iu"
            or np.any(programs < 0)
            or np.any(programs >= self.n_tokens)
        ):
            raise ValueError("invalid token tapes")
        lower = np.concatenate(
            (np.zeros((self.n_tokens + 1, 1), dtype=np.int64), self.table[:, :-1]),
            axis=1,
        )
        alleles = np.empty(programs.shape, dtype=np.int32)
        previous = np.full(len(programs), self.n_tokens)
        for j in range(programs.shape[1]):
            token = programs[:, j]
            lo, hi = lower[previous, token], self.table[previous, token]
            alleles[:, j] = rng.integers(lo, hi, dtype=np.int32)
            if np.any(alleles[:, j] < lo) or np.any(alleles[:, j] >= hi):
                raise AssertionError("inverse encoding escaped conditional interval")
            previous = token
        return alleles


def outputs(programs, inputs, alphabet="v2_rmin"):
    return np.array(
        rust_chem_execute_pop_batch(
            programs.tolist() if isinstance(programs, np.ndarray) else programs,
            "NOP",
            "NOP",
            inputs,
            "intlist",
            alphabet,
            0,
        ),
        dtype=np.int64,
    ).reshape(len(programs), len(inputs))


def search(job, *, return_solver=False, collector=None, decoder_factory=Decoder,
           initial_transform=None):
    cell, arm, table, seed, cap, pop_size = job[:6]
    inputs = job[6] if len(job) >= 7 else INPUTS
    alphabet = job[7] if len(job) >= 8 else "v2_rmin"
    initialization = job[8] if len(job) >= 9 else None
    start = time.monotonic()
    decoder = decoder_factory(table)
    # Independent streams prevent arm-dependent selection from changing the
    # initialization, cases, crossover positions, or allele-resampling draws.
    cases_rng = np.random.default_rng([seed, 0])
    initial_rng = np.random.default_rng([seed, 1])
    variation = np.random.default_rng([seed, 2])
    selection = FastRandom(seed + 100000000)
    indices = cases_rng.choice(len(inputs), 64, replace=False)
    training = [inputs[i] for i in indices]
    label = np.asarray(cell["labels"])
    pop = initial_rng.integers(
        decoder.allele_range, size=(pop_size, 32), dtype=np.int32
    )
    source = decoder
    reencoded = False
    if initial_transform is not None:
        if initialization is not None:
            raise ValueError("choose one initialization transformation")
        pop = initial_transform(pop, decoder)
    if initialization is not None:
        source = Decoder(initialization["source_table"])
        if (source.allele_range, source.n_tokens) != (
            decoder.allele_range, decoder.n_tokens
        ):
            raise ValueError("source and destination alphabets/ranges must agree")
        reencoded = initialization["reencode"]
        if not reencoded and source.hash() != decoder.hash():
            raise ValueError("different source requires population-preserving reencoding")
        if reencoded:
            source_programs = source.decode(pop)
            pop = decoder.encode(source_programs, np.random.default_rng([seed, 3]))
            if not np.array_equal(decoder.decode(pop), source_programs):
                raise AssertionError("generation-0 token tapes changed during encoding")
    initial_tokens_hash = hashlib.sha256(decoder.decode(pop).tobytes()).hexdigest()
    shortcuts = 0
    unique_shortcuts = 0
    training_perfect_individuals = 0
    checked = {}
    decode_seconds = 0.0
    curve = []
    budget_times = {}
    solved_at = None
    solver = None
    evaluations = 0
    budgets = (4096, 32768, 65536, 131072, 262144, 524288)
    for generation in range(cap // pop_size):
        tick = time.monotonic()
        programs = decoder.decode(pop)
        decode_seconds += time.monotonic() - tick
        observed = outputs(programs, training, alphabet)
        correct = observed == label[indices]
        scores = correct.sum(1)
        evaluations += pop_size
        perfect = np.flatnonzero(scores == 64)
        for i in perfect:
            training_perfect_individuals += 1
            key = programs[i].tobytes()
            if key not in checked:
                checked[key] = bool(
                    np.array_equal(
                        outputs(programs[i : i + 1], inputs, alphabet)[0], label
                    )
                )
                if not checked[key]:
                    unique_shortcuts += 1
            if not checked[key]:
                shortcuts += 1
            if checked[key]:
                solved_at = evaluations
                if return_solver:
                    solver = programs[i].tolist()
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
        if evaluations == cap and collector is None:
            break
        _, inverse = np.unique(correct, axis=0, return_inverse=True)
        groups = [np.flatnonzero(inverse == i) for i in range(inverse.max() + 1)]
        group_cases = np.array([correct[g[0]] for g in groups])
        n = pop_size - 2
        # Terminal instrumentation must not advance the search selection stream.
        parent_rng = selection
        if evaluations == cap:
            parent_rng = FastRandom(0)
            parent_rng.setstate(selection.getstate())
            parent_rng.np.bit_generator.state = copy.deepcopy(
                selection.np.bit_generator.state
            )
        # Both parent choices are consumed each generation, regardless of
        # whether the independently drawn crossover mask uses parent two.
        parents = np.array(
            [_lexicase_select(groups, group_cases, parent_rng) for _ in range(2 * n)]
        ).reshape(2, n)
        if collector is not None:
            collector(generation + 1, programs, correct, parents, evaluations == cap)
        if evaluations == cap:
            break
        crossing = variation.random(n) < 0.7
        points = variation.integers(1, 32, size=n)
        mask = variation.random((n, 32)) < 0.03
        replacements = variation.integers(
            decoder.allele_range, size=(n, 32), dtype=np.int32
        )
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
    result = dict(
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
        initial_tokens_hash=initial_tokens_hash,
        initial_source_hash=source.hash(),
        initial_reencoded=reencoded,
    )
    if return_solver:
        result["solver"] = solver
    return result
