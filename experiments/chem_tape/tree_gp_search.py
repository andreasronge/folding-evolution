"""Family-blind closure GP over int expressions, compiled to production v2_x4.

Prefix trees are immutable tuples; subtree spans permit single-child subtree
exchange. No bank, roles, canonical or learned object enters construction.
"""

from dataclasses import dataclass, field
import hashlib
import time

import numpy as np

from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.independent_input_bank import ALPHABET
from folding_evolution.chem_tape.evolve import FastRandom, _lexicase_select

TERMINALS = ("X0", "X1", "X2", "X3", "ANY", "0", "1", "2", "5")
FUNCTIONS = ("ADD", "GT", "IF_GT")
ARITY = (0,) * 9 + (2, 2, 3)
TOKENS = ((1, 5), (1, 18), (1, 22), (1, 23), (1, 6),
          (2,), (3,), (15,), (16,), (7,), (8,), (17,))
MAX_TOKENS = 32
MIXES = (0.9, 0.5)
GRAMMAR = dict(terminals=TERMINALS, functions=FUNCTIONS, arity=ARITY,
               tokens=TOKENS, max_tokens=MAX_TOKENS, depths=[2, 3, 4],
               grow_terminal_probability=0.5, mutation_depth=3,
               point_sampling="uniform all nodes", offspring="one into parent1",
               oversize="revert parent1", initialization="retry same bin, max10000")


@dataclass(frozen=True, slots=True)
class Tree:
    prefix: tuple[int, ...]
    program: tuple[int, ...] = field(init=False)
    ends: tuple[int, ...] = field(init=False)

    def __post_init__(self):
        if not self.prefix or any(type(x) is not int or not 0 <= x < 12 for x in self.prefix):
            raise ValueError("invalid prefix symbols")
        stack, ends = [], [0] * len(self.prefix)
        for i in range(len(self.prefix) - 1, -1, -1):
            op = self.prefix[i]
            if len(stack) < ARITY[op]:
                raise ValueError("incomplete tree")
            children = [stack.pop() for _ in range(ARITY[op])]
            end = children[-1][1] if children else i + 1
            ends[i] = end
            stack.append((sum((c[0] for c in children), ()) + TOKENS[op], end))
        if len(stack) != 1 or stack[0][1] != len(self.prefix):
            raise ValueError("extra prefix expressions")
        object.__setattr__(self, "program", stack[0][0])
        object.__setattr__(self, "ends", tuple(ends))

    def insert(self, point, donor, donor_point=0):
        if not 0 <= point < len(self.prefix) or not 0 <= donor_point < len(donor.prefix):
            raise ValueError("invalid subtree point")
        candidate = Tree(self.prefix[:point] + donor.prefix[donor_point:donor.ends[donor_point]]
                         + self.prefix[self.ends[point]:])
        rejected = len(candidate.program) > MAX_TOKENS
        return (self if rejected else candidate), rejected


def random_tree(rng, depth, full=False):
    def draw(remaining):
        if remaining == 0 or (not full and rng.random() < 0.5):
            return (int(rng.integers(9)),)
        op = int(rng.integers(9, 12))
        return (op,) + sum((draw(remaining - 1) for _ in range(ARITY[op])), ())
    return Tree(draw(depth))


def initialize(rng, size):
    bins = [(d, full) for d in (2, 3, 4) for full in (True, False)]
    allocation = [bins[i % len(bins)] for i in range(size)]
    rng.shuffle(allocation)
    pop, attempts, rejected = [], 0, 0
    per_bin = {f"{d}/{f}": dict(accepted=0, attempts=0, rejected=0) for d, f in bins}
    for d, full in allocation:
        rec = per_bin[f"{d}/{full}"]
        for _ in range(10000):
            tree = random_tree(rng, d, full)
            attempts += 1
            rec["attempts"] += 1
            if len(tree.program) <= MAX_TOKENS:
                pop.append(tree)
                rec["accepted"] += 1
                break
            rejected += 1
            rec["rejected"] += 1
        else:
            raise ValueError(f"initialization cannot fill size-limited bin: depth={d}, full={full}, draws=10000")
    return pop, dict(attempts=attempts, rejected=rejected, bins=per_bin)


def interpret(tree, inp):
    """Independent recursive interpreter; no compiler/VM or cached spans used."""
    def evaluate(i):
        op = tree.prefix[i]
        i += 1
        if op < 4:
            return (int(inp[op]) if len(inp) > op else 0), i
        if op == 4:
            return int(any(inp)), i
        if op < 9:
            return (0, 1, 2, 5)[op - 5], i
        args = []
        for _ in range(ARITY[op]):
            value, i = evaluate(i)
            args.append(value)
        if op == 9:
            return ((args[0] + args[1] + 2**63) % 2**64) - 2**63, i
        if op == 10:
            return int(args[0] > args[1]), i
        return (args[1] if args[2] > 0 else args[0]), i
    value, end = evaluate(0)
    if end != len(tree.prefix):
        raise ValueError("invalid interpreter tree")
    return value


def from_postfix(tokens):
    """Validation-fixture parser; never used by search/initialization."""
    stack, i = [], 0
    while i < len(tokens):
        if tokens[i] == 1:
            pair = tuple(tokens[i:i + 2])
            op = TOKENS.index(pair)
            i += 2
        else:
            op = TOKENS.index((tokens[i],))
            i += 1
        n = ARITY[op]
        children = stack[-n:] if n else []
        if n and len(children) != n:
            raise ValueError("fixture underflow")
        if n:
            del stack[-n:]
        stack.append((op,) + sum(children, ()))
    if len(stack) != 1:
        raise ValueError("fixture does not have one output")
    return Tree(stack[0])


def search(job, *, force_cap=False):
    cell, seed, cap, pop_size, inputs, crossover = job
    if cap < pop_size or cap % pop_size or pop_size < 3 or crossover not in MIXES:
        raise ValueError("invalid GP search budget/mix")
    start = time.monotonic()
    indices = np.random.default_rng([seed, 0]).choice(len(inputs), 64, replace=False)
    training = [inputs[i] for i in indices]
    label = np.asarray(cell["labels"])
    pop, initialization = initialize(np.random.default_rng([seed, 1]), pop_size)
    initial_hash = hashlib.sha256(bytes(sum((p.program + (255,) for p in pop), ()))).hexdigest()
    variation = np.random.default_rng([seed, 2])
    selection = FastRandom(seed + 100000000)
    stats = dict(crossover=0, mutation=0, rejected_crossover=0, rejected_mutation=0)
    checked, curve, budget_times = {}, [], {}
    shortcuts = unique_shortcuts = perfect_count = 0
    exact_seconds = exact_max = variation_seconds = compile_seconds = 0.0
    total_length = total_nodes = 0
    max_length = 0
    length_histogram = np.zeros(33, dtype=np.int64)
    solved_at, solver, solver_tree = None, None, None
    budgets = (4096, 32768, 65536, 131072, 262144, 524288)
    for generation in range(cap // pop_size):
        tick = time.monotonic()
        programs = [p.program for p in pop]  # variable lengths: no padded token capacity
        compile_seconds += time.monotonic() - tick
        lengths = [len(p) for p in programs]
        total_length += sum(lengths)
        total_nodes += sum(len(p.prefix) for p in pop)
        max_length = max(max_length, max(lengths))
        length_histogram += np.bincount(lengths, minlength=33)
        observed = outputs(programs, training, ALPHABET)
        correct = observed == label[indices]
        scores = correct.sum(1)
        evaluations = (generation + 1) * pop_size
        for i in np.flatnonzero(scores == 64):
            perfect_count += 1
            key = programs[i]
            if key not in checked:
                tick = time.monotonic()
                checked[key] = bool(np.array_equal(outputs([key], inputs, ALPHABET)[0], label))
                elapsed = time.monotonic() - tick
                exact_seconds += elapsed
                exact_max = max(exact_max, elapsed)
                unique_shortcuts += not checked[key]
            if not checked[key]:
                shortcuts += 1
            elif not force_cap:
                solved_at, solver, solver_tree = evaluations, list(key), list(pop[i].prefix)
                break
        elapsed = time.monotonic() - start
        for b in budgets:
            if evaluations >= b and str(b) not in budget_times:
                budget_times[str(b)] = elapsed
        if generation % 32 == 0 or solved_at is not None or evaluations == cap:
            curve.append([evaluations, int(scores.max()), len(np.unique(correct, axis=0)),
                          float(np.mean(lengths))])
        if solved_at is not None or evaluations == cap:
            break
        tick = time.monotonic()
        _, inverse = np.unique(correct, axis=0, return_inverse=True)
        groups = [np.flatnonzero(inverse == i) for i in range(inverse.max() + 1)]
        group_cases = np.array([correct[g[0]] for g in groups])
        n = pop_size - 2
        parents = np.array([_lexicase_select(groups, group_cases, selection) for _ in range(2 * n)]).reshape(2, n)
        crossing = variation.random(n) < crossover
        children = []
        for j in range(n):
            p1, p2 = pop[parents[0, j]], pop[parents[1, j]]
            point = int(variation.integers(len(p1.prefix)))
            if crossing[j]:
                kind = "crossover"
                donor_point = int(variation.integers(len(p2.prefix)))
                child, rejected = p1.insert(point, p2, donor_point)
            else:
                kind = "mutation"
                child, rejected = p1.insert(point, random_tree(variation, 3))
            stats[kind] += 1
            stats["rejected_" + kind] += int(rejected)
            children.append(child)
        elite = np.argsort(-scores, kind="stable")[:2]
        pop = [pop[i] for i in elite] + children
        variation_seconds += time.monotonic() - tick
    seconds = time.monotonic() - start
    for b in budgets:
        if solved_at is not None and solved_at <= b:
            budget_times[str(b)] = seconds
    return dict(cell=cell["id"], arm="tree", seed=seed, cap=cap, pop_size=pop_size,
                crossover=crossover, solved=solved_at is not None, evaluations=evaluations,
                seconds=seconds, budget_seconds=budget_times, generations=generation + 1,
                solver=solver, solver_tree=solver_tree, training_indices=indices.tolist(),
                curve=curve, initial_tokens_hash=initial_hash, initialization=initialization,
                operator=stats, compiled_length_histogram=length_histogram.tolist(),
                compiled_tokens_evaluated=total_length, tree_nodes_evaluated=total_nodes,
                primitive_case_work=total_length * 64, max_compiled_length=max_length,
                mean_compiled_length=total_length / evaluations,
                compile_seconds=compile_seconds, variation_seconds=variation_seconds,
                exact_check_seconds=exact_seconds, exact_check_max_seconds=exact_max,
                exact_checks=len(checked), training_perfect_individuals=perfect_count,
                shortcuts=shortcuts, unique_shortcuts=int(unique_shortcuts), force_cap=force_cap)
