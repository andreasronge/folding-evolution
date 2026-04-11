"""Tests for the AST evaluator."""

from folding_evolution.ast_nodes import Keyword, ListExpr, Literal, NsSymbol, Symbol
from folding_evolution.evaluator import evaluate

CTX = {
    "products": [
        {"price": 600, "name": "Widget", "status": "active"},
        {"price": 400, "name": "Gadget", "status": "inactive"},
        {"price": 800, "name": "Doohickey", "status": "active"},
    ],
    "employees": [
        {"name": "Alice", "department": "eng"},
        {"name": "Bob", "department": "sales"},
    ],
}


def test_literal():
    assert evaluate(Literal(500), CTX) == 500


def test_ns_symbol_products():
    result = evaluate(NsSymbol("data", "products"), CTX)
    assert isinstance(result, list)
    assert len(result) == 3


def test_count_products():
    expr = ListExpr((Symbol("count"), NsSymbol("data", "products")))
    assert evaluate(expr, CTX) == 3


def test_count_employees():
    expr = ListExpr((Symbol("count"), NsSymbol("data", "employees")))
    assert evaluate(expr, CTX) == 2


def test_first():
    expr = ListExpr((Symbol("first"), NsSymbol("data", "products")))
    result = evaluate(expr, CTX)
    assert result == {"price": 600, "name": "Widget", "status": "active"}


def test_rest():
    expr = ListExpr((Symbol("rest"), NsSymbol("data", "products")))
    result = evaluate(expr, CTX)
    assert len(result) == 2
    assert result[0]["name"] == "Gadget"


def test_get_with_env():
    expr = ListExpr((Symbol("get"), Symbol("x"), Keyword("price")))
    result = evaluate(expr, CTX, env={"x": {"price": 600}})
    assert result == 600


def test_comparison_gt():
    expr = ListExpr((Symbol(">"), Literal(600), Literal(500)))
    assert evaluate(expr, CTX) is True


def test_arithmetic_add():
    expr = ListExpr((Symbol("+"), Literal(100), Literal(200)))
    assert evaluate(expr, CTX) == 300


def test_filter_with_fn():
    get_price = ListExpr((Symbol("get"), Symbol("x"), Keyword("price")))
    gt_500 = ListExpr((Symbol(">"), get_price, Literal(500)))
    pred_fn = ListExpr((Symbol("fn"), Symbol("x"), gt_500))
    filter_expr = ListExpr((Symbol("filter"), pred_fn, NsSymbol("data", "products")))
    result = evaluate(filter_expr, CTX)
    assert len(result) == 2
    assert result[0]["name"] == "Widget"
    assert result[1]["name"] == "Doohickey"


def test_count_non_list_returns_none():
    expr = ListExpr((Symbol("count"), Literal(5)))
    assert evaluate(expr, CTX) is None


def test_none_propagation():
    expr = ListExpr((Symbol("get"), Literal(5), Keyword("price")))
    assert evaluate(expr, CTX) is None


def test_if_true():
    expr = ListExpr((Symbol("if"), Literal(1), Literal(10), Literal(20)))
    assert evaluate(expr, CTX) == 10


def test_if_false():
    expr = ListExpr((Symbol("if"), Literal(0), Literal(10), Literal(20)))
    assert evaluate(expr, CTX) == 20


def test_and_short_circuit():
    expr = ListExpr((Symbol("and"), Literal(0), Literal(99)))
    assert evaluate(expr, CTX) == 0


def test_or_short_circuit():
    expr = ListExpr((Symbol("or"), Literal(0), Literal(99)))
    assert evaluate(expr, CTX) == 99


def test_not():
    expr = ListExpr((Symbol("not"), Literal(0)))
    assert evaluate(expr, CTX) is True


def test_map_with_fn():
    get_price = ListExpr((Symbol("get"), Symbol("x"), Keyword("price")))
    fn_expr = ListExpr((Symbol("fn"), Symbol("x"), get_price))
    map_expr = ListExpr((Symbol("map"), fn_expr, NsSymbol("data", "products")))
    result = evaluate(map_expr, CTX)
    assert result == [600, 400, 800]


def test_arithmetic_sub():
    expr = ListExpr((Symbol("-"), Literal(500), Literal(200)))
    assert evaluate(expr, CTX) == 300


def test_comparison_lt():
    expr = ListExpr((Symbol("<"), Literal(100), Literal(200)))
    assert evaluate(expr, CTX) is True


def test_equality():
    expr = ListExpr((Symbol("="), Literal(5), Literal(5)))
    assert evaluate(expr, CTX) is True
