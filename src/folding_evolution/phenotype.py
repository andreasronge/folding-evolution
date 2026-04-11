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


@dataclass(frozen=True)
class Program:
    ast: ASTNode | None
    source: str | None
    bond_count: int
    evaluate: Callable


@functools.lru_cache(maxsize=4096)
def develop(genotype: str) -> Program:
    """Full pipeline: genotype -> fold -> chemistry -> evaluator wrapper."""
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
