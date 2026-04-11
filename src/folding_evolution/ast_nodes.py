"""AST node types for the folding evolution phenotype.

These are the output of the chemistry assembly pass. The evaluator
consumes these nodes to produce a runtime value.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True, slots=True)
class Literal:
    """Numeric constant (0, 100, 200, ... 900)."""
    value: int | float


@dataclass(frozen=True, slots=True)
class Symbol:
    """Named symbol (e.g. variable reference 'x' inside fn bodies)."""
    name: str


@dataclass(frozen=True, slots=True)
class Keyword:
    """Field key like :price, :status, :department."""
    name: str


@dataclass(frozen=True, slots=True)
class NsSymbol:
    """Namespaced symbol like data/products, data/employees."""
    ns: str
    name: str


@dataclass(frozen=True, slots=True)
class ListExpr:
    """S-expression: (operator operand1 operand2 ...).

    items is a tuple of ASTNode. The first element is typically a Symbol
    naming the operation (e.g. Symbol("filter"), Symbol("count")).
    """
    items: tuple


ASTNode = Union[Literal, Symbol, Keyword, NsSymbol, ListExpr]
