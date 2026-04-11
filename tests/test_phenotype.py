"""Tests for the phenotype module."""

from folding_evolution.phenotype import Program, ast_to_string, develop
from folding_evolution.ast_nodes import Keyword, ListExpr, Literal, NsSymbol, Symbol


class TestAstToString:
    def test_literal(self):
        assert ast_to_string(Literal(500)) == "500"

    def test_keyword(self):
        assert ast_to_string(Keyword("price")) == ":price"

    def test_ns_symbol(self):
        assert ast_to_string(NsSymbol("data", "products")) == "data/products"

    def test_symbol(self):
        assert ast_to_string(Symbol("x")) == "x"

    def test_list_expr(self):
        expr = ListExpr((Symbol("count"), NsSymbol("data", "products")))
        assert ast_to_string(expr) == "(count data/products)"

    def test_nested_expr(self):
        get = ListExpr((Symbol("get"), Symbol("x"), Keyword("price")))
        cmp = ListExpr((Symbol(">"), get, Literal(500)))
        assert ast_to_string(cmp) == "(> (get x :price) 500)"


class TestDevelop:
    def test_empty_genotype(self):
        prog = develop("")
        assert prog.ast is None
        assert prog.source is None
        assert prog.bond_count == 0
        assert prog.evaluate({}) is None

    def test_single_data_source(self):
        prog = develop("S")
        assert prog.ast == NsSymbol("data", "products")
        assert prog.source == "data/products"
        assert prog.bond_count == 0

    def test_caching(self):
        p1 = develop("QDaK5XASBw")
        p2 = develop("QDaK5XASBw")
        assert p1 is p2  # same cached object


class TestBondCount:
    def test_golden_bond_count(self):
        prog = develop("QDaK5XASBw")
        # (filter (fn x (> (get x :price) 500)) data/products) = 4 ListExprs
        assert prog.bond_count == 4
