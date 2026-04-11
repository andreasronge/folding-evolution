"""Direct encoding baseline -- no folding.

Uses the same alphabet as the folding system but maps genotype to phenotype
sequentially: read characters left-to-right, skip spacers/wildcards, and build
a PTC-Lisp expression by recursive descent.

This is the control for measuring whether folding adds value. Same alphabet,
same genetic operators, same evaluation -- only the genotype-to-phenotype
mapping differs.
"""

from __future__ import annotations

import functools
from typing import Any

from .alphabet import to_fragment
from .ast_nodes import ASTNode, Keyword, ListExpr, Literal, NsSymbol, Symbol
from .evaluator import evaluate
from .phenotype import Program, ast_to_string, _count_bonds


def _parse(tokens: list[str]) -> tuple[ASTNode | None, list[str]]:
    """Parse one expression from the token list, return (ast_node, remaining)."""
    if not tokens:
        return None, []

    char = tokens[0]
    rest = tokens[1:]
    frag = to_fragment(char)

    # Skip spacers and wildcards
    if frag == "spacer" or frag == "wildcard":
        return _parse(rest)

    if isinstance(frag, tuple) and len(frag) == 2:
        kind, value = frag

        if kind == "fn_fragment":
            return _parse_fn_fragment(value, rest)
        if kind == "comparator":
            return _parse_binary_op(value, rest)
        if kind == "connective":
            return _parse_connective(value, rest)
        if kind == "data_source":
            return NsSymbol("data", value), rest
        if kind == "field_key":
            return Keyword(value), rest
        if kind == "literal":
            return Literal(value), rest

    return None, rest


def _parse_fn_fragment(op: str, rest: list[str]) -> tuple[ASTNode | None, list[str]]:
    """Parse a fn_fragment operator."""
    # Higher-order: consume fn-body + data -> (op (fn x body) data)
    if op in ("filter", "map", "group_by"):
        body, rest1 = _parse(rest)
        data, rest2 = _parse(rest1)
        if body is not None and data is not None:
            fn_ast = ListExpr((Symbol("fn"), Symbol("x"), body))
            return ListExpr((Symbol(op), fn_ast, data)), rest2
        return _fallback(op, rest)

    # Reduce: consume fn-body + init + data
    if op == "reduce":
        body, rest1 = _parse(rest)
        init, rest2 = _parse(rest1)
        data, rest3 = _parse(rest2)
        if body is not None and init is not None and data is not None:
            fn_ast = ListExpr((Symbol("fn"), Symbol("x"), body))
            return ListExpr((Symbol("reduce"), fn_ast, init, data)), rest3
        return _fallback(op, rest)

    # Wrappers: consume one -> (op expr)
    if op in ("count", "first", "reverse", "sort", "rest", "last"):
        return _parse_unary_op(op, rest)

    # Get: consume next as field key -> (get x key)
    if op == "get":
        key_expr, rest1 = _parse(rest)
        if key_expr is not None:
            return ListExpr((Symbol("get"), Symbol("x"), key_expr)), rest1
        return _fallback(op, rest)

    # Set: consume one
    if op == "set":
        return _parse_unary_op(op, rest)

    # Contains?: consume two
    if op == "contains?":
        return _parse_binary_op(op, rest)

    # Assoc: consume key + value -> (assoc x key value)
    if op == "assoc":
        key_expr, rest1 = _parse(rest)
        val_expr, rest2 = _parse(rest1)
        if key_expr is not None and val_expr is not None:
            return ListExpr((Symbol("assoc"), Symbol("x"), key_expr, val_expr)), rest2
        return _fallback(op, rest)

    # Fn: consume one, wrap in (fn x expr)
    if op == "fn":
        expr, rest1 = _parse(rest)
        if expr is not None:
            return ListExpr((Symbol("fn"), Symbol("x"), expr)), rest1
        return None, rest

    # Let: consume two -> (let x expr1 expr2)
    # Note: simplified from Elixir's (let [x e1] e2) since evaluator doesn't have let
    if op == "let":
        e1, rest1 = _parse(rest)
        e2, rest2 = _parse(rest1)
        if e1 is not None and e2 is not None:
            return ListExpr((Symbol("let"), Symbol("x"), e1, e2)), rest2
        return _fallback(op, rest)

    # If: consume 3 (pred, then, else)
    if op == "if":
        pred, rest1 = _parse(rest)
        then, rest2 = _parse(rest1)
        else_, rest3 = _parse(rest2)
        if pred is not None and then is not None and else_ is not None:
            return ListExpr((Symbol("if"), pred, then, else_)), rest3
        if pred is not None and then is not None:
            return ListExpr((Symbol("if"), pred, then)), rest2
        return _fallback(op, rest)

    # Match: treat as unary for direct encoding
    if op == "match":
        return _parse_unary_op(op, rest)

    # Unknown fn_fragment — fallback
    return _fallback(op, rest)


def _parse_connective(op: str, rest: list[str]) -> tuple[ASTNode | None, list[str]]:
    """Parse logical connectives."""
    if op in ("and", "or"):
        return _parse_binary_op(op, rest)
    if op == "not":
        return _parse_unary_op(op, rest)
    return _fallback(op, rest)


def _parse_unary_op(op: str, rest: list[str]) -> tuple[ASTNode | None, list[str]]:
    """Consume one expression -> (op expr)."""
    expr, rest1 = _parse(rest)
    if expr is not None:
        return ListExpr((Symbol(op), expr)), rest1
    return _fallback(op, rest)


def _parse_binary_op(op: str, rest: list[str]) -> tuple[ASTNode | None, list[str]]:
    """Consume two expressions -> (op e1 e2)."""
    e1, rest1 = _parse(rest)
    e2, rest2 = _parse(rest1)
    if e1 is not None and e2 is not None:
        return ListExpr((Symbol(op), e1, e2)), rest2
    return _fallback(op, rest)


def _fallback(op: str, rest: list[str]) -> tuple[ASTNode, list[str]]:
    """When an operator can't get enough arguments, return as bare symbol."""
    return Symbol(op), rest


@functools.lru_cache(maxsize=4096)
def develop_direct(genotype: str) -> Program:
    """Direct encoding: read genotype left-to-right, build AST by recursive descent.

    Returns a Program with the same interface as phenotype.develop().
    """
    tokens = list(genotype)
    ast, _rest = _parse(tokens)

    if ast is None:
        return Program(
            ast=None,
            source=None,
            bond_count=0,
            evaluate=lambda ctx: None,
        )

    bond_count = _count_bonds(ast)
    source = ast_to_string(ast)

    def eval_fn(ctx: dict[str, Any]) -> Any:
        try:
            return evaluate(ast, ctx)
        except Exception:
            return None

    return Program(
        ast=ast,
        source=source,
        bond_count=bond_count,
        evaluate=eval_fn,
    )
