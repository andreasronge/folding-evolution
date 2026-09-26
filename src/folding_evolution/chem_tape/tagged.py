"""Chem-tape tagged runs: connection by binding, not position (map-bias notebook §8).

Genome: a uint8 array of 2·L values — L ops followed by L tags. Cell i is
(op = g[i], tag = g[L + i]).
- ops 0..19 are the v2_probe ops; SEP (20) starts a run whose tag is its tag
  field; RECV (21) pushes the output of the run(s) whose tag equals its tag
  field. Tags are 0..63 and are ignored on every other op.
- Each run's body runs on its own fresh stack; its output is its top int (0 if
  the top is not an int). Cells before the first SEP are not a run (inert).
- RECV t: no run tagged t -> 0; several -> their elementwise max (no
  positional tie-break). Cycles and depth > MAX_DEPTH -> 0.
- The organism's output is the run(s) tagged OUTPUT_TAG, combined the same way.

Evaluation is vectorised over inputs: a program's stack types never depend on
the input, so every op acts on whole (E,) or (E, 4) arrays at once. Semantics
mirror executor.py's preserve-mode safe_pop for intlist tasks; see
tests/test_chem_tape_tagged.py for the parity check.
"""

from __future__ import annotations

import random

import numpy as np

SEP, RECV = 20, 21
N_OPS = 22          # ops 0..21
N_TAGS = 64
OUTPUT_TAG = 0
MAX_DEPTH = 8

_INT, _LIST, _CHARS = "int", "intlist", "charlist"


def split(g: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    L = len(g) // 2
    return g[:L], g[L:]


def join(ops, tags) -> np.ndarray:
    return np.concatenate([np.asarray(ops, dtype=np.uint8), np.asarray(tags, dtype=np.uint8)])


def parse_runs(g: np.ndarray) -> list[tuple[int, tuple[tuple[int, int], ...]]]:
    """[(tag, ((op, tag), ...))] for every run, in tape order."""
    ops, tags = split(g)
    runs, cur_tag, body = [], None, []
    for op, tg in zip(ops.tolist(), tags.tolist()):
        if op == SEP:
            if cur_tag is not None:
                runs.append((cur_tag, tuple(body)))
            cur_tag, body = tg, []
        elif cur_tag is not None:
            body.append((op, tg))
    if cur_tag is not None:
        runs.append((cur_tag, tuple(body)))
    return runs


def build(leader: list[tuple[int, int]], runs, L: int, rng: random.Random) -> np.ndarray:
    """Genome from leader cells + runs, truncated / NOP-padded to L cells."""
    cells = list(leader)
    for tag, body in runs:
        cells.append((SEP, tag))
        cells.extend(body)
    cells = cells[:L]
    while len(cells) < L:
        cells.append((0, rng.randrange(N_TAGS)))
    return join([c[0] for c in cells], [c[1] for c in cells])


def leader_cells(g: np.ndarray) -> list[tuple[int, int]]:
    ops, tags = split(g)
    out = []
    for op, tg in zip(ops.tolist(), tags.tolist()):
        if op == SEP:
            break
        out.append((op, tg))
    return out


# ---------------- vectorised interpreter ----------------

class _Machine:
    def __init__(self, inputs: np.ndarray, threshold: int):
        self.X = inputs                      # (E, 4) int64
        self.E = inputs.shape[0]
        self.threshold = threshold
        self.zero = np.zeros(self.E, dtype=np.int64)
        self.empty_list = np.zeros((self.E, 0), dtype=np.int64)

    def _default(self, t):
        return self.zero if t == _INT else self.empty_list if t == _LIST else None

    def _pop(self, st, t):
        if not st or st[-1][0] != t:
            return self._default(t)
        return st.pop()[1]

    def run(self, body, recv) -> np.ndarray:
        st: list = []
        for op, tg in body:
            if op == 0 or op in (12, 13):          # NOP; slots bound to NOP
                continue
            if op == 1:
                st.append((_LIST, self.X))
            elif op in (2, 3, 15, 16):
                st.append((_INT, np.full(self.E, {2: 0, 3: 1, 15: 2, 16: 5}[op], dtype=np.int64)))
            elif op == 19:
                st.append((_INT, np.full(self.E, self.threshold, dtype=np.int64)))
            elif op == 4:                           # CHARS: pops a str (never present) -> empty charlist
                if st and st[-1][0] == "str":
                    st.pop()
                st.append((_CHARS, None))
            elif op == 14:                          # MAP_EQ_E on the (always empty) charlist
                self._pop(st, _CHARS)
                st.append((_LIST, self.empty_list))
            elif op in (5, 11):                     # SUM, REDUCE_ADD
                st.append((_INT, self._pop(st, _LIST).sum(axis=1)))
            elif op == 6:                           # ANY
                st.append((_INT, (self._pop(st, _LIST) != 0).any(axis=1).astype(np.int64)))
            elif op == 18:                          # REDUCE_MAX (empty -> 0)
                xs = self._pop(st, _LIST)
                st.append((_INT, xs.max(axis=1) if xs.shape[1] else self.zero))
            elif op in (7, 8):                      # ADD, GT
                b = self._pop(st, _INT)
                a = self._pop(st, _INT)
                st.append((_INT, a + b if op == 7 else (a > b).astype(np.int64)))
            elif op == 9:                           # DUP
                if not st:
                    st.append((_INT, self.zero))
                    st.append((_INT, self.zero))
                else:
                    st.append(st[-1])
            elif op == 10:                          # SWAP (any type)
                b = st.pop() if st else (_INT, self.zero)
                a = st.pop() if st else (_INT, self.zero)
                st.append(b)
                st.append(a)
            elif op == 17:                          # IF_GT
                if len(st) < 3:
                    for _ in range(3):
                        self._pop(st, _INT)
                    st.append((_INT, self.zero))
                else:
                    cond = self._pop(st, _INT)
                    then = self._pop(st, _INT)
                    els = self._pop(st, _INT)
                    st.append((_INT, np.where(cond > 0, then, els)))
            elif op == RECV:
                st.append((_INT, recv(tg)))
        return st[-1][1] if st and st[-1][0] == _INT else self.zero


def _machine_for(task) -> _Machine:
    assert task.input_type == "intlist", "tagged runs support intlist tasks only"
    assert task.alphabet.slot_12 == "NOP" and task.alphabet.slot_13 == "NOP", "slots must be NOP"
    return _Machine(np.asarray(task.inputs, dtype=np.int64), int(task.alphabet.threshold))


def genome_outputs(g: np.ndarray, m: _Machine, body_cache: dict | None = None,
                   all_runs: bool = False):
    runs = parse_runs(g)
    by_tag: dict[int, list[int]] = {}
    for k, (tag, _) in enumerate(runs):
        by_tag.setdefault(tag, []).append(k)
    memo: dict[int, np.ndarray] = {}

    def value_of_tag(tag: int, depth: int, visiting: frozenset) -> np.ndarray:
        ks = by_tag.get(tag)
        if not ks:
            return m.zero
        vals = [value_of_run(k, depth, visiting) for k in ks]
        return vals[0] if len(vals) == 1 else np.maximum.reduce(vals)

    def value_of_run(k: int, depth: int, visiting: frozenset) -> np.ndarray:
        if k in memo:
            return memo[k]
        if k in visiting or depth > MAX_DEPTH:
            return m.zero
        body = runs[k][1]
        pure = all(op != RECV for op, _ in body)
        if pure and body_cache is not None:
            key = tuple(op for op, _ in body)
            v = body_cache.get(key)
            if v is None:
                v = body_cache[key] = m.run(body, None)
        else:
            v = m.run(body, lambda t: value_of_tag(t, depth + 1, visiting | {k}))
        if not visiting:
            memo[k] = v
        return v

    if all_runs:
        return [value_of_run(k, 0, frozenset()) for k in range(len(runs))]
    return value_of_tag(OUTPUT_TAG, 0, frozenset())


def run_values(g: np.ndarray, task, body_cache: dict | None = None) -> list[np.ndarray]:
    """Each run's own output (RECVs resolved), in tape order."""
    return genome_outputs(g, _machine_for(task), body_cache, all_runs=True)


def evaluate_tagged(population: list[np.ndarray], task) -> tuple[np.ndarray, np.ndarray]:
    """Same contract as evaluate.evaluate_population: (fitnesses, predictions)."""
    m = _machine_for(task)
    cache: dict = {}
    seen: dict[bytes, np.ndarray] = {}
    preds = np.zeros((len(population), m.E), dtype=np.int64)
    for p, g in enumerate(population):
        key = g.tobytes()
        if key not in seen:
            seen[key] = genome_outputs(g, m, cache)
        preds[p] = seen[key]
    fits = (preds == task.labels[None, :]).mean(axis=1).astype(np.float64)
    return fits, preds


# ---------------- variation ----------------

def random_genotype(L: int, rng: random.Random) -> np.ndarray:
    return join([rng.randrange(N_OPS) for _ in range(L)], [rng.randrange(N_TAGS) for _ in range(L)])


def _depends_on_itself(k: int, runs) -> bool:
    """Does run k read (through RECV, transitively) a tag that run k carries?"""
    own = runs[k][0]
    by_tag: dict[int, list[int]] = {}
    for i, (tag, _) in enumerate(runs):
        by_tag.setdefault(tag, []).append(i)
    todo = [tg for op, tg in runs[k][1] if op == RECV]
    seen: set[int] = set()
    while todo:
        t = todo.pop()
        if t == own:
            return True
        if t in seen:
            continue
        seen.add(t)
        for i in by_tag.get(t, []):
            todo += [tg for op, tg in runs[i][1] if op == RECV]
    return False


def duplicate_run(g: np.ndarray, rng: random.Random, same_tag: bool | None = None) -> np.ndarray:
    """Gene duplication: copy one run and insert the copy at a random run
    boundary; length kept at L.

    - same tag: an expressed, redundant copy. Same-tag runs combine by max, so
      max(A, A) = A — but only when the run does not read its own tag; for a
      self-dependent run the copy is skipped.
    - fresh tag: a silent copy. The tag must be unused by every run AND unread
      by every RECV (a RECV of a missing tag reads 0; giving the copy that tag
      would wire it in).
    Existing runs are never truncated: trailing NOPs (which never affect a
    run's output) are dropped first, and if the copy still does not fit the
    genome is returned unchanged. `same_tag=None` picks either with
    probability 1/2. Every branch draws the same RNG calls before deciding."""
    runs = parse_runs(g)
    if same_tag is None:
        same_tag = rng.random() < 0.5
    if not runs:
        return g
    k = rng.randrange(len(runs))
    at = rng.randint(0, len(runs))
    tag, body = runs[k]
    if same_tag:
        if _depends_on_itself(k, runs):
            return g
        new_tag = tag
    else:
        ops, tags = split(g)
        taken = {t for t, _ in runs} | {int(t) for o, t in zip(ops, tags) if o == RECV}
        free = [t for t in range(N_TAGS) if t not in taken]
        if not free:
            return g
        new_tag = rng.choice(free)
    L, lead = len(g) // 2, leader_cells(g)
    new = runs[:at] + [(new_tag, _strip_trailing_nops(body))] + runs[at:]
    if len(lead) + sum(1 + len(b) for _, b in new) > L:
        new = [(t, _strip_trailing_nops(b)) for t, b in new]
        if len(lead) + sum(1 + len(b) for _, b in new) > L:
            return g
    return build(lead, new, L, rng)


def _strip_trailing_nops(body):
    body = list(body)
    while body and body[-1][0] == 0:
        body.pop()
    return tuple(body)


def mutate(g: np.ndarray, mu: float, rng: random.Random, dup_rate: float = 0.0) -> np.ndarray:
    """Point mutation of ops and tags (rate mu each), plus insertion and
    deletion of whole cells (rate mu/2 each per cell); length kept at L.
    `dup_rate` > 0 adds gene duplication (duplicate_run) with that probability;
    at 0 no extra RNG is drawn, so earlier runs reproduce."""
    if dup_rate > 0 and rng.random() < dup_rate:
        g = duplicate_run(g, rng)
    ops, tags = split(g)
    L = len(ops)
    cells = []
    for op, tg in zip(ops.tolist(), tags.tolist()):
        if rng.random() < mu / 2:
            continue                                            # deletion
        if rng.random() < mu:
            op = rng.randrange(N_OPS)
        if rng.random() < mu:
            tg = rng.randrange(N_TAGS)
        cells.append((op, tg))
        if rng.random() < mu / 2:                               # insertion
            cells.append((rng.randrange(N_OPS), rng.randrange(N_TAGS)))
    cells = cells[:L]
    while len(cells) < L:
        cells.append((0, rng.randrange(N_TAGS)))
    return join([c[0] for c in cells], [c[1] for c in cells])


def crossover(a: np.ndarray, b: np.ndarray, rng: random.Random) -> np.ndarray:
    """Half the time homologous (runs with a tag present in both parents take
    the other parent's body with probability 1/2); otherwise a cut between
    runs (a's runs up to i, then b's runs from j). Falls back to the cut when
    the parents share no tag."""
    L = len(a) // 2
    ra, rb = parse_runs(a), parse_runs(b)
    b_body = {}
    for tag, body in rb:
        b_body.setdefault(tag, body)
    shared = [k for k, (tag, _) in enumerate(ra) if tag in b_body]
    if shared and rng.random() < 0.5:
        runs = [(tag, b_body[tag] if (tag in b_body and rng.random() < 0.5) else body) for tag, body in ra]
    else:
        i, j = rng.randint(0, len(ra)), rng.randint(0, len(rb))
        runs = ra[:i] + rb[j:]
    return build(leader_cells(a), runs, L, rng)
