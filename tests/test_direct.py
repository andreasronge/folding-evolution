"""Tests for direct encoding baseline."""

import random

import folding_evolution.direct as direct
from folding_evolution.alphabet import ALPHABET
from folding_evolution.direct import develop_direct
from folding_evolution.ast_nodes import Literal, NsSymbol


def test_fallback_reparsing_is_bounded(monkeypatch):
    # This short evolved genotype previously made >200,000 parser calls.
    genotype = 'RUCIREEdTTDLWYTREExxTEQxyFKeEBimKREEdTYm5xTEkTEyKKWYKeYDLWYkRR8FIyFKTDLWYkkm5xTEkxyFdEi2L2xxTEQxyFKeEkx5BimKREEdTY'
    direct._PARSE_CACHE.clear()
    original = direct._parse_uncached
    calls = 0

    def counted(tokens):
        nonlocal calls
        calls += 1
        assert calls <= len(genotype) + 1
        return original(tokens)

    monkeypatch.setattr(direct, '_parse_uncached', counted)
    program = develop_direct.__wrapped__(genotype)
    assert program.source is not None


def test_cached_remaining_tokens_are_not_mutable():
    direct._PARSE_CACHE.clear()
    ast, rest = direct._parse(list('ST'))
    assert rest == ['T']
    rest.clear()
    assert direct._parse(list('ST')) == (ast, ['T'])


def test_parser_handles_experiment_length_cap():
    # Cache wrappers must not introduce RecursionError at the experiment's cap.
    for char in ALPHABET:
        develop_direct.__wrapped__(char * 200)


def test_cached_parser_matches_original_recursion(monkeypatch):
    rng = random.Random(1745)
    memoized = direct._parse
    for _ in range(300):
        tokens = [rng.choice(ALPHABET) for _ in range(rng.randrange(1, 101))]
        with monkeypatch.context() as context:
            context.setattr(direct, '_parse', direct._parse_uncached)
            expected = direct._parse(tokens)
        direct._PARSE_CACHE.clear()
        assert memoized(tokens) == expected


def test_count_products():
    """develop_direct("BS") -> source contains count and data/products."""
    prog = develop_direct("BS")
    assert prog.source is not None
    assert "count" in prog.source
    assert "data/products" in prog.source
    assert prog.bond_count >= 1


def test_leaf_data_source():
    """develop_direct("S") -> just data/products."""
    prog = develop_direct("S")
    assert prog.source == "data/products"
    assert isinstance(prog.ast, NsSymbol)


def test_literal():
    """develop_direct("0") -> Literal(0)."""
    prog = develop_direct("0")
    assert isinstance(prog.ast, Literal)
    assert prog.ast.value == 0


def test_all_spacers():
    """develop_direct with all spacers -> empty program."""
    prog = develop_direct("Z" * 20)
    assert prog.ast is None
    assert prog.source is None
    assert prog.bond_count == 0


def test_count_field_key():
    """develop_direct("Ba") -> (count :price)."""
    prog = develop_direct("Ba")
    assert prog.source is not None
    assert "count" in prog.source
    assert ":price" in prog.source


def test_count_literal():
    """develop_direct("B5") -> (count 500)."""
    prog = develop_direct("B5")
    assert prog.source is not None
    assert "count" in prog.source
    assert "500" in prog.source


def test_random_genotypes_no_crash():
    """1000 random genotypes complete without exception."""
    rng = random.Random(42)
    alphabet = [chr(c) for c in range(ord("A"), ord("Z") + 1)]
    alphabet += [chr(c) for c in range(ord("a"), ord("z") + 1)]
    alphabet += [chr(c) for c in range(ord("0"), ord("9") + 1)]

    for _ in range(1000):
        length = rng.randint(1, 50)
        genotype = "".join(rng.choice(alphabet) for _ in range(length))
        prog = develop_direct(genotype)
        # Should always return a Program, never raise
        assert prog is not None


def test_evaluate_count():
    """Verify evaluate works: develop_direct("BS").evaluate(ctx) -> 3."""
    prog = develop_direct("BS")
    result = prog.evaluate({"products": [1, 2, 3]})
    assert result == 3


def test_filter_higher_order():
    """Test higher-order function: filter."""
    # AaS -> (filter (fn x :price) data/products)
    prog = develop_direct("AaS")
    assert prog.source is not None
    assert "filter" in prog.source
    assert prog.bond_count >= 1


def test_get_with_key():
    """Test get: Da -> (get x :price)."""
    prog = develop_direct("Da")
    assert prog.source is not None
    assert "get" in prog.source
    assert ":price" in prog.source


def test_comparator():
    """Test comparator: K0S -> (> 0 data/products)."""
    prog = develop_direct("K0S")
    assert prog.source is not None
    assert ">" in prog.source
    assert prog.bond_count >= 1


def test_not():
    """Test not: P0 -> (not 0)."""
    prog = develop_direct("P0")
    assert prog.source is not None
    assert "not" in prog.source


def test_fallback_no_args():
    """When operator can't get args, falls back to bare symbol."""
    prog = develop_direct("B")
    assert prog.source is not None
    # B=count with no args -> bare "count" symbol
    assert prog.source == "count"
