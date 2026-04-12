"""Per-generation metrics for CA evolution."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CAGenerationStats:
    generation: int
    best_fitness: float
    mean_fitness: float
    std_fitness: float
    unique_rules: int
    best_genotype_hex: str


class CAStatsCollector:
    def __init__(self) -> None:
        self.history: list[CAGenerationStats] = []

    def record(
        self,
        generation: int,
        fitnesses,
        genotypes,
    ) -> CAGenerationStats:
        import numpy as np
        fits = np.asarray(fitnesses, dtype=np.float64)
        best_idx = int(fits.argmax())
        unique = len({g.tobytes() for g in genotypes})
        stats = CAGenerationStats(
            generation=generation,
            best_fitness=float(fits.max()),
            mean_fitness=float(fits.mean()),
            std_fitness=float(fits.std()),
            unique_rules=unique,
            best_genotype_hex=genotypes[best_idx].tobytes().hex(),
        )
        self.history.append(stats)
        return stats

    def to_csv(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow([
                "generation", "best_fitness", "mean_fitness",
                "std_fitness", "unique_rules", "best_genotype_hex",
            ])
            for s in self.history:
                w.writerow([
                    s.generation, s.best_fitness, s.mean_fitness,
                    s.std_fitness, s.unique_rules, s.best_genotype_hex,
                ])

    @property
    def best_fitness(self) -> float:
        return max((s.best_fitness for s in self.history), default=0.0)
