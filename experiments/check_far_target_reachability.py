"""
Reachability check for the far-transfer rerun target.

Tests whether two candidate far-transfer targets are producible at
non-trivial rates by the random-genotype pipeline. Uses FULL
target-family signatures, not just top-level operator presence, so
that "reachable" means "the compositional assembly evolution would
need is actually available."

Primary target:
  (reduce (fn a b (+ a (get b :price))) 0 data/products)

  Signature requires ALL of:
    - top-level reduce
    - 2-arg lambda (fn with two symbol args)
    - + expression in the body
    - get-accessor in the body

Fallback target:
  (first (filter (fn x (= (get x :category) "tools")) data/products))

  Signature requires ALL of:
    - first wrapping a filter
    - = comparator in the predicate
    - get-accessor with a :category keyword
    - string literal in the = expression

Decision rule:
  Reachable ⇔ at least 5 random genotypes per 10k produce the full
  signature (rate ≥ 0.05%). A single top-level occurrence is not
  enough — the assembly must include the load-bearing substructure.
"""

import random
from collections import Counter

from folding_evolution.alphabet import random_genotype
from folding_evolution.ast_nodes import ListExpr, Symbol, Keyword, NsSymbol
from folding_evolution.phenotype import develop_batch


# ---------------------------------------------------------------------------
# Signature detectors
# ---------------------------------------------------------------------------

def has_reduce_signature(node) -> bool:
    """Check for the full reduce-sum signature.

    Requires (reduce LAMBDA INIT DATA) with:
      - LAMBDA = (fn ARG1 ARG2 BODY) (2 args, both symbols)
      - BODY contains `+` and (get _ :KEY) somewhere
    """
    found = [False]
    _walk_for_reduce(node, found)
    return found[0]


def _walk_for_reduce(node, found):
    if found[0]:
        return
    if not isinstance(node, ListExpr) or not node.items:
        return
    head = node.items[0]
    hn = head.name if isinstance(head, Symbol) else None

    if hn == "reduce" and len(node.items) >= 3:
        lam = node.items[1]
        if _is_2arg_lambda_with_get_plus(lam):
            found[0] = True
            return

    for item in node.items:
        _walk_for_reduce(item, found)


def _is_2arg_lambda_with_get_plus(node) -> bool:
    """(fn A B BODY) where A,B are symbols and BODY contains both + and get."""
    if not isinstance(node, ListExpr) or not node.items:
        return False
    h = node.items[0]
    if not (isinstance(h, Symbol) and h.name == "fn"):
        return False
    if len(node.items) < 4:  # fn + 2 args + body
        return False
    a1, a2 = node.items[1], node.items[2]
    if not (isinstance(a1, Symbol) and isinstance(a2, Symbol)):
        return False
    body = node.items[3]
    has_plus = [False]
    has_get = [False]
    _walk_for_plus_and_get(body, has_plus, has_get)
    return has_plus[0] and has_get[0]


def _walk_for_plus_and_get(node, has_plus, has_get):
    if not isinstance(node, ListExpr) or not node.items:
        return
    head = node.items[0]
    if isinstance(head, Symbol):
        if head.name == "+":
            has_plus[0] = True
        elif head.name == "get" and len(node.items) >= 3:
            if isinstance(node.items[2], Keyword):
                has_get[0] = True
    for item in node.items:
        _walk_for_plus_and_get(item, has_plus, has_get)


def has_first_filter_equals_signature(node) -> bool:
    """Check for (first (filter (fn x (= (get x :KEY) STRING)) data/DS))."""
    found = [False]
    _walk_for_first_filter_eq(node, found)
    return found[0]


def _walk_for_first_filter_eq(node, found):
    if found[0]:
        return
    if not isinstance(node, ListExpr) or not node.items:
        return
    head = node.items[0]
    hn = head.name if isinstance(head, Symbol) else None

    if hn == "first" and len(node.items) >= 2:
        arg = node.items[1]
        if _is_filter_with_eq_predicate(arg):
            found[0] = True
            return

    for item in node.items:
        _walk_for_first_filter_eq(item, found)


def _is_filter_with_eq_predicate(node) -> bool:
    if not isinstance(node, ListExpr) or not node.items:
        return False
    h = node.items[0]
    if not (isinstance(h, Symbol) and h.name == "filter"):
        return False
    if len(node.items) < 3:
        return False
    fn = node.items[0] if False else node.items[1]
    data = node.items[2]
    if not (isinstance(data, NsSymbol) and data.ns == "data"):
        return False
    # fn = (fn x BODY) where BODY has (= (get x :KEY) STRING)
    return _fn_has_eq_get(fn)


def _fn_has_eq_get(node) -> bool:
    if not isinstance(node, ListExpr) or not node.items:
        return False
    if not (isinstance(node.items[0], Symbol) and node.items[0].name == "fn"):
        return False
    if len(node.items) < 3:
        return False
    body = node.items[-1]
    found = [False]
    _walk_for_eq_get(body, found)
    return found[0]


def _walk_for_eq_get(node, found):
    if found[0]:
        return
    if not isinstance(node, ListExpr) or not node.items:
        return
    head = node.items[0]
    if isinstance(head, Symbol) and head.name == "=" and len(node.items) == 3:
        # Accept any (= ... ...) where one side is (get _ :KEY) — we don't
        # require a specific keyword at this reachability layer.
        for arg in node.items[1:]:
            if (isinstance(arg, ListExpr) and len(arg.items) == 3 and
                    isinstance(arg.items[0], Symbol) and arg.items[0].name == "get" and
                    isinstance(arg.items[2], Keyword)):
                found[0] = True
                return
    for item in node.items:
        _walk_for_eq_get(item, found)


# ---------------------------------------------------------------------------
# Partial-signature diagnostics (for interpreting borderline results)
# ---------------------------------------------------------------------------

def reduce_partial_counts(node, counts: Counter):
    if not isinstance(node, ListExpr) or not node.items:
        return
    head = node.items[0]
    if isinstance(head, Symbol):
        if head.name == "reduce":
            counts["has_reduce"] += 1
            if len(node.items) >= 2 and _is_any_2arg_lambda(node.items[1]):
                counts["reduce_with_2arg_fn"] += 1
        if head.name == "+":
            counts["has_plus"] += 1
        if head.name == "get" and len(node.items) == 3 and isinstance(node.items[2], Keyword):
            counts["has_get_field"] += 1
    for item in node.items:
        reduce_partial_counts(item, counts)


def _is_any_2arg_lambda(node):
    if not isinstance(node, ListExpr) or len(node.items) < 4:
        return False
    return (isinstance(node.items[0], Symbol) and node.items[0].name == "fn"
            and isinstance(node.items[1], Symbol)
            and isinstance(node.items[2], Symbol))


def first_filter_partial_counts(node, counts: Counter):
    if not isinstance(node, ListExpr) or not node.items:
        return
    head = node.items[0]
    if isinstance(head, Symbol):
        if head.name == "first":
            counts["has_first"] += 1
        if head.name == "filter":
            counts["has_filter"] += 1
        if head.name == "=":
            counts["has_eq"] += 1
    for item in node.items:
        first_filter_partial_counts(item, counts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(n_random=10000, genotype_length=100, seed=7):
    rng = random.Random(seed)
    genos = [random_genotype(genotype_length, rng) for _ in range(n_random)]
    progs = develop_batch(genos)

    reduce_full = 0
    first_filter_full = 0
    reduce_partial = Counter()
    first_filter_partial = Counter()

    for p in progs:
        if p is None or p.ast is None:
            continue
        if has_reduce_signature(p.ast):
            reduce_full += 1
        if has_first_filter_equals_signature(p.ast):
            first_filter_full += 1
        reduce_partial_counts(p.ast, reduce_partial)
        first_filter_partial_counts(p.ast, first_filter_partial)

    n = n_random
    print(f"Reachability check — {n} random length-{genotype_length} genotypes\n")

    print("PRIMARY: (reduce (fn a b (+ a (get b :price))) 0 data/products)")
    print(f"  full signature:         {reduce_full}/{n}  ({reduce_full/n*100:.3f}%)")
    print(f"  partial has_reduce:     {reduce_partial['has_reduce']}/{n}  ({reduce_partial['has_reduce']/n*100:.3f}%)")
    print(f"  partial reduce+2arg_fn: {reduce_partial['reduce_with_2arg_fn']}/{n}  ({reduce_partial['reduce_with_2arg_fn']/n*100:.3f}%)")
    print(f"  partial has_plus:       {reduce_partial['has_plus']}/{n}  ({reduce_partial['has_plus']/n*100:.3f}%)")
    print(f"  partial has_get_field:  {reduce_partial['has_get_field']}/{n}  ({reduce_partial['has_get_field']/n*100:.3f}%)")

    print(f"\nFALLBACK: (first (filter (fn x (= (get x :KEY) STR)) data/DS))")
    print(f"  full signature:         {first_filter_full}/{n}  ({first_filter_full/n*100:.3f}%)")
    print(f"  partial has_first:      {first_filter_partial['has_first']}/{n}  ({first_filter_partial['has_first']/n*100:.3f}%)")
    print(f"  partial has_filter:     {first_filter_partial['has_filter']}/{n}  ({first_filter_partial['has_filter']/n*100:.3f}%)")
    print(f"  partial has_eq:         {first_filter_partial['has_eq']}/{n}  ({first_filter_partial['has_eq']/n*100:.3f}%)")

    print(f"\n--- Decision ---")
    threshold = 5
    print(f"Threshold: ≥{threshold}/{n} (≥{threshold/n*100:.3f}%) full signature for reachable.")
    print(f"  PRIMARY reduce:       {'REACHABLE' if reduce_full >= threshold else 'UNREACHABLE'}")
    print(f"  FALLBACK first/filter: {'REACHABLE' if first_filter_full >= threshold else 'UNREACHABLE'}")


if __name__ == "__main__":
    main()
