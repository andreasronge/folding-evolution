"""Multi-output tagged genomes: exactness, knockout and form (map-bias notebook §29).

Plans/shared-helper-reuse.md. Outputs are read from several output tags; "exact" means
right on all 10,000 length-4 lists over [0, 9]. Knockout: replace one run's body with
NOPs and re-evaluate every output on all lists; the run's consumer count is the number of
outputs that change on some input. A RECV that is read and ignored counts for nothing.

Form of a fully exact genome: shared (has a pure helper: a run that is not the first run
of an output tag, with consumer count >= 2), partly (the first run of the first output tag
has consumer count >= 2, no pure helper), duplicated (neither).
"""

from __future__ import annotations

import itertools

import numpy as np

from . import tagged
from .tagged import RECV, SEP

X_ALL = np.array(list(itertools.product(range(10), repeat=4)), dtype=np.int64)
SUBSET = slice(None, None, 20)      # prefilter: every 20th list (500), as evolve._ExactTracker


def full_labels(label_fn) -> np.ndarray:
    """(n_outputs, 10000) labels on all lists from a multi-output label_fn."""
    return np.array([label_fn(tuple(x)) for x in X_ALL], dtype=np.int64).T


def machine(inputs: np.ndarray = X_ALL, threshold: int = 0):
    """Interpreter over `inputs`; mbs_* tasks bind THRESHOLD_SLOT to 0."""
    return tagged._Machine(np.asarray(inputs, dtype=np.int64), threshold)


def outputs(g: np.ndarray, m, out_tags, body_cache: dict | None = None,
            combine: str = "leftmost") -> np.ndarray:
    """(n_outputs, E) values of the output tags (as tagged.evaluate_tagged)."""
    return np.stack(tagged.genome_outputs(g, m, body_cache, combine=combine, out_tags=out_tags))


def run_spans(g: np.ndarray) -> list[tuple[int, int, int]]:
    """(tag, first body cell, end) per run, in tape order (runs as tagged.parse_runs)."""
    ops, tags = tagged.split(g)
    spans, cur = [], None
    for i, op in enumerate(ops.tolist()):
        if op == SEP:
            if cur is not None:
                spans.append((cur[0], cur[1], i))
            cur = (int(tags[i]), i + 1)
    if cur is not None:
        spans.append((cur[0], cur[1], len(ops)))
    return spans


def knockout(g: np.ndarray, k: int) -> np.ndarray:
    """g with run k's body replaced by NOPs (its SEP, tag and every other cell kept)."""
    _, lo, hi = run_spans(g)[k]
    out = g.copy()
    out[lo:hi] = 0
    return out


def consumer_counts(g: np.ndarray, m, out_tags, body_cache: dict | None = None,
                    base: np.ndarray | None = None, combine: str = "leftmost") -> list[int]:
    """Per run (tape order): how many outputs change on some input when its body is
    knocked out."""
    base = outputs(g, m, out_tags, body_cache, combine) if base is None else base
    return [int((outputs(knockout(g, k), m, out_tags, body_cache, combine) != base).any(axis=1).sum())
            for k in range(len(run_spans(g)))]


def classify(g: np.ndarray, m, out_tags, labels: np.ndarray, body_cache: dict | None = None,
             combine: str = "leftmost") -> dict:
    """Exactness per output, consumer counts and form. `labels`: (n_outputs, m.E).
    `other_output_helper`: the first run of a later output tag has consumer count >= 2
    (not one of the three forms; reported so it is not silently called duplicated)."""
    base = outputs(g, m, out_tags, body_cache, combine)
    exact = [bool(v) for v in (base == labels).all(axis=1)]
    counts = consumer_counts(g, m, out_tags, body_cache, base, combine)
    tags = [t for t, _, _ in run_spans(g)]
    first: dict[int, int] = {}
    for k, t in enumerate(tags):
        first.setdefault(t, k)
    out_runs = {first[t] for t in out_tags if t in first}
    oah = out_tags[0] in first and counts[first[out_tags[0]]] >= 2
    pure = [k for k, c in enumerate(counts) if c >= 2 and k not in out_runs]
    other = any(t in first and counts[first[t]] >= 2 for t in out_tags[1:])
    full = all(exact)
    form = None
    if full:
        form = "shared" if pure else "partly" if oah else "duplicated"
    return {"exact": exact, "fully_exact": full, "consumer_counts": counts, "tags": tags,
            "output_as_helper": bool(oah), "pure_helpers": pure,
            "other_output_helper": bool(other), "form": form}


def semantic_key(g: np.ndarray) -> tuple:
    """What a genome computes: its runs with RECV tags, trailing NOPs stripped (as
    evolve._ExactTracker._semantic_keys)."""
    return tuple((t, tuple((op, tg if op == RECV else 0) for op, tg in tagged._strip_trailing_nops(body)))
                 for t, body in tagged.parse_runs(g))


class Exactness:
    """Per-output exactness on all lists, cached by semantic key; a genome wrong on the
    500-list subset for every output skips the full evaluation."""

    def __init__(self, out_tags, labels: np.ndarray, combine: str = "leftmost") -> None:
        self.out_tags, self.labels, self.combine = tuple(out_tags), labels, combine
        self.m_sub, self.m_full = machine(X_ALL[SUBSET]), machine(X_ALL)
        self.c_sub, self.c_full = {}, {}
        self.cache: dict[tuple, np.ndarray] = {}

    def __call__(self, g: np.ndarray) -> np.ndarray:
        key = semantic_key(g)
        hit = self.cache.get(key)
        if hit is None:
            ok = (outputs(g, self.m_sub, self.out_tags, self.c_sub, self.combine)
                  == self.labels[:, SUBSET]).all(axis=1)
            if ok.any():
                ok = ok & (outputs(g, self.m_full, self.out_tags, self.c_full, self.combine)
                           == self.labels).all(axis=1)
            if len(self.cache) > 200_000:
                self.cache.clear()
            hit = self.cache[key] = ok
        return hit


class SharedCensus:
    """cfg.track_shared: on a sample of the population, per-output and full exactness on
    all lists, and the form of each fully exact genome by knockout. Sampling uses its own
    generator, so evolution's random stream is untouched."""

    SAMPLE = 256

    def __init__(self, task, seed: int, combine: str = "leftmost") -> None:
        if not getattr(task, "output_tags", None):
            raise ValueError("track_shared needs a multi-output task")
        self.out_tags = tuple(task.output_tags)
        self.labels = full_labels(task.label_fn)
        self.combine = combine
        self.exact = Exactness(self.out_tags, self.labels, combine)
        self.m = machine()
        self.body_cache: dict = {}
        self.forms: dict[tuple, dict] = {}
        self.gen = np.random.default_rng([seed, 29])

    def _form(self, g: np.ndarray) -> dict:
        key = semantic_key(g)
        hit = self.forms.get(key)
        if hit is None:
            if len(self.forms) > 50_000:
                self.forms.clear()
            if len(self.body_cache) > 20_000:
                self.body_cache.clear()
            c = classify(g, self.m, self.out_tags, self.labels, self.body_cache, self.combine)
            hit = self.forms[key] = {"form": c["form"], "other": c["other_output_helper"],
                                     "pure": len(c["pure_helpers"])}
        return hit

    def record(self, gen: int, population, cases: np.ndarray) -> dict:
        n = min(self.SAMPLE, len(population))
        idx = self.gen.choice(len(population), size=n, replace=False)
        E = np.array([self.exact(population[i]) for i in idx])          # (n, n_outputs)
        full = E.all(axis=1)
        forms = [self._form(population[i]) for i, f in zip(idx, full) if f]
        nf = len(forms)

        def share(pred):
            return float(sum(map(pred, forms)) / nf) if nf else None

        return {"gen": gen, "n": n, "exact": [float(v) for v in E.mean(axis=0)],
                "fully_exact": float(full.mean()), "n_fully_exact": nf,
                "shared": share(lambda f: f["form"] == "shared"),
                "partly": share(lambda f: f["form"] == "partly"),
                "duplicated": share(lambda f: f["form"] == "duplicated"),
                "other_output_helper": share(lambda f: f["other"]),
                "train_perfect": float(cases.all(axis=1).mean())}
