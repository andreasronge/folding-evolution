"""Phenotype: genotype-to-program pipeline.

Connects fold -> chemistry -> evaluator into a single develop() function
that maps a genotype string to an executable Program.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import Any, Callable

from .ast_nodes import ASTNode, Keyword, ListExpr, Literal, NsSymbol, Symbol
from .chemistry import assemble
from .evaluator import evaluate
from .fold import fold

try:
    from _folding_rust import rust_develop as _rust_develop
    _USE_RUST = True
except ImportError:
    _USE_RUST = False


@dataclass(frozen=True)
class Program:
    ast: ASTNode | None
    source: str | None
    bond_count: int
    evaluate: Callable


@functools.lru_cache(maxsize=4096)
def develop(genotype: str) -> Program:
    """Full pipeline: genotype -> fold -> chemistry -> evaluator wrapper."""
    if _USE_RUST:
        return _develop_rust(genotype)
    return _develop_python(genotype)


def _develop_rust(genotype: str) -> Program:
    """Rust-accelerated develop path."""
    result = _rust_develop(genotype)
    if result is None:
        return Program(ast=None, source=None, bond_count=0, evaluate=lambda ctx: None)

    ast_tuple, source, bond_count = result
    ast = _from_rust_ast(ast_tuple)

    def eval_fn(ctx: dict[str, Any]) -> Any:
        try:
            return evaluate(ast, ctx)
        except Exception:
            return None

    return Program(ast=ast, source=source, bond_count=bond_count, evaluate=eval_fn)


def _develop_python(genotype: str) -> Program:
    """Pure Python develop path (fallback)."""
    grid, _placements = fold(genotype)
    fragments = assemble(grid)

    if not fragments:
        return Program(
            ast=None,
            source=None,
            bond_count=0,
            evaluate=lambda ctx: None,
        )

    # Pick the most complex AST (highest bond count)
    best = max(fragments, key=_count_bonds)
    bond_count = _count_bonds(best)
    source = ast_to_string(best)

    def eval_fn(ctx: dict[str, Any]) -> Any:
        try:
            return evaluate(best, ctx)
        except Exception:
            return None

    return Program(
        ast=best,
        source=source,
        bond_count=bond_count,
        evaluate=eval_fn,
    )


def _from_rust_ast(t: tuple) -> ASTNode:
    """Reconstruct Python ASTNode from Rust tagged tuple."""
    tag = t[0]
    if tag == "Lit":
        return Literal(t[1])
    if tag == "Sym":
        return Symbol(t[1])
    if tag == "Kw":
        return Keyword(t[1])
    if tag == "Ns":
        return NsSymbol(t[1], t[2])
    if tag == "Expr":
        return ListExpr(tuple(_from_rust_ast(item) for item in t[1]))
    raise ValueError(f"Unknown AST tag: {tag}")


def _count_bonds(node: ASTNode) -> int:
    """Count ListExpr nodes in the AST (each represents one or more bonds)."""
    if isinstance(node, ListExpr):
        return 1 + sum(_count_bonds(item) for item in node.items)
    return 0


def ast_to_string(node: ASTNode) -> str:
    """Convert an AST node to a human-readable source string."""
    if isinstance(node, Literal):
        return str(node.value)
    if isinstance(node, Keyword):
        return f":{node.name}"
    if isinstance(node, NsSymbol):
        return f"{node.ns}/{node.name}"
    if isinstance(node, Symbol):
        return node.name
    if isinstance(node, ListExpr):
        inner = " ".join(ast_to_string(item) for item in node.items)
        return f"({inner})"
    return "?"
