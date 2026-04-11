"""Evolution configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvolutionConfig:
    population_size: int = 50
    genotype_length: int = 30
    generations: int = 100
    tournament_size: int = 3
    elite_count: int = 2
    mutation_rate: float = 0.3
    crossover_rate: float = 0.7
    seed: int = 42
