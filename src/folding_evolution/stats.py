"""StatsCollector: records per-generation metrics."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

from .individual import Individual


@dataclass
class GenerationStats:
    generation: int
    best_fitness: float
    avg_fitness: float
    best_genotype: str
    best_source: str | None
    best_bond_count: int
    population_size: int


class StatsCollector:
    def __init__(self) -> None:
        self.history: list[GenerationStats] = []

    def record(self, generation: int, population: list[Individual]) -> GenerationStats:
        """Record stats for a generation."""
        best = max(population, key=lambda ind: ind.fitness)
        avg = sum(ind.fitness for ind in population) / len(population)
        stats = GenerationStats(
            generation=generation,
            best_fitness=best.fitness,
            avg_fitness=avg,
            best_genotype=best.genotype,
            best_source=best.program.source if best.program else None,
            best_bond_count=best.program.bond_count if best.program else 0,
            population_size=len(population),
        )
        self.history.append(stats)
        return stats

    def to_csv(self, path: str | Path) -> None:
        """Write stats history to a CSV file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "generation", "best_fitness", "avg_fitness",
                "best_genotype", "best_source", "best_bond_count",
                "population_size",
            ])
            for s in self.history:
                writer.writerow([
                    s.generation, s.best_fitness, s.avg_fitness,
                    s.best_genotype, s.best_source, s.best_bond_count,
                    s.population_size,
                ])

    @property
    def best_fitness(self) -> float:
        if not self.history:
            return 0.0
        return max(s.best_fitness for s in self.history)
