"""Individual: wraps genotype + fitness + developed program."""

from __future__ import annotations

from dataclasses import dataclass, field

from .phenotype import Program


@dataclass
class Individual:
    genotype: str
    fitness: float = 0.0
    program: Program | None = None
