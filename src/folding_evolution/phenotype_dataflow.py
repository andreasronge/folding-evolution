"""Dataflow phenotype: alternative to the chemistry pipeline.

Folds the genotype onto a fixed 32×32 grid, then evaluates via K rounds
of broadcast message passing. No ASTs, no closures — values propagate
through cells and filter uses boolean masks.

This is a new representation for comparison, not a faithful port.
See docs/gpu-dataflow-design.md for design rationale.
"""

from __future__ import annotations

from typing import Any, Callable

from .individual import Individual
from .phenotype import Program

try:
    from _folding_rust import (
        RustContexts,
        RustTargetOutputs,
        rust_dataflow_develop_and_score_batch as _rust_dataflow_batch,
        rust_dataflow_evaluate as _rust_dataflow_evaluate,
    )
    _DATAFLOW_AVAILABLE = True
except ImportError:
    _DATAFLOW_AVAILABLE = False


def dataflow_available() -> bool:
    """Check if the Rust dataflow backend is compiled and available."""
    return _DATAFLOW_AVAILABLE


def develop_and_score_dataflow(
    population: list[Individual],
    rust_ctx: Any,
    rust_targets: Any,
) -> None:
    """Develop + evaluate + score a population using the dataflow pipeline.

    Drop-in replacement for dynamics._develop_and_score_vm.
    Sets ind.fitness and ind.program for each individual.
    """
    genotypes = [ind.genotype for ind in population]
    results = _rust_dataflow_batch(genotypes, rust_ctx, rust_targets)
    for ind, (fitness, source, depth) in zip(population, results):
        ind.fitness = fitness
        ind.program = Program(
            ast=None,
            source=source,
            bond_count=depth,
            evaluate=None,
        )


def dataflow_evaluate(genotype: str, contexts: list[dict]) -> list:
    """Evaluate a single genotype on all contexts using dataflow.

    Returns list of output values (one per context).
    Useful for testing and debugging.
    """
    rust_ctx = RustContexts(contexts)
    return _rust_dataflow_evaluate(genotype, rust_ctx)
