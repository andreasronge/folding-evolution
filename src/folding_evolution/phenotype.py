"""Phenotype: genotype-to-program pipeline.

Connects fold -> chemistry -> evaluator into a single develop() function
that maps a genotype string to an executable Program.

Two entry points:
- develop(genotype): cached, uses hard-coded or Rust chemistry (fast path)
- develop_with_dev(genotype, dev_genome): uncached, uses evolvable chemistry
"""

from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

from .ast_nodes import ASTNode, Keyword, ListExpr, Literal, NsSymbol, Symbol
from .chemistry import assemble, assemble_with_consumed
from .evaluator import evaluate
from .fold import fold

if TYPE_CHECKING:
    from .dev_genome import DevGenome

try:
    from _folding_rust import rust_develop as _rust_develop
    _USE_RUST = True
except ImportError:
    _USE_RUST = False

try:
    from _folding_rust import rust_develop_batch as _rust_develop_batch
except ImportError:
    _rust_develop_batch = None


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


def develop_batch(genotypes: list[str]) -> list[Program]:
    """Batch develop: process all genotypes in one FFI call using Rayon.

    Bypasses the LRU cache. Faster than per-individual develop when
    most genotypes are unique (after mutation/crossover).
    """
    if _rust_develop_batch is not None:
        return _develop_batch_rust(genotypes)
    return [develop(g) for g in genotypes]


def _develop_batch_rust(genotypes: list[str]) -> list[Program]:
    results = _rust_develop_batch(genotypes)
    programs = []
    for result in results:
        if result is None:
            programs.append(Program(ast=None, source=None, bond_count=0, evaluate=lambda ctx: None))
        else:
            ast_tuple, source, bond_count = result
            ast = _from_rust_ast(ast_tuple)

            def eval_fn(ctx: dict[str, Any], _ast=ast) -> Any:
                try:
                    return evaluate(_ast, ctx)
                except Exception:
                    return None

            programs.append(Program(ast=ast, source=source, bond_count=bond_count, evaluate=eval_fn))
    return programs


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


def develop_with_dev(genotype: str, dev_genome: DevGenome) -> Program:
    """Develop with evolvable chemistry. Not cached (dev_genome varies).

    Uses the Python chemistry path with DevGenome parameters.
    The Rust backend does not support DevGenome (it implements the
    fixed hard-coded chemistry only).
    """
    grid, _placements = fold(genotype)
    fragments = assemble(grid, dev_genome=dev_genome)

    if not fragments:
        return Program(
            ast=None,
            source=None,
            bond_count=0,
            evaluate=lambda ctx: None,
        )

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


def get_bonded_indices(genotype: str) -> set[int]:
    """Return genotype indices that participated in bonds.

    Folds the genotype onto a grid, runs chemistry, and maps consumed
    grid positions back to genotype character indices. Used by
    chemistry-aware operators that need to know which parts of the
    genotype are "active" (formed bonds during assembly).
    """
    grid, placements = fold(genotype)
    _, bonded_positions = assemble_with_consumed(grid)

    # Map grid positions back to genotype indices
    pos_to_index: dict[tuple[int, int], int] = {}
    for i, (pos, _char) in enumerate(placements):
        pos_to_index[pos] = i

    return {pos_to_index[pos] for pos in bonded_positions if pos in pos_to_index}


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
