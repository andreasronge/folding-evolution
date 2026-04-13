"""Per-generation metrics for chem-tape evolution.

Diagnostics (spec §Layer 11): alongside fitness statistics we record the
distribution of longest-active-run lengths across the population. This is an
arm-independent property of the genotype distribution — directly comparable
between Arm A and Arm B — and under the differential-outcome hypothesis it is
the mechanism-level quantity expected to diverge between them over training.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import engine_numpy


@dataclass
class ChemTapeGenerationStats:
    generation: int
    best_fitness: float
    mean_fitness: float
    std_fitness: float
    unique_genotypes: int
    best_genotype_hex: str
    mean_longest_run: float
    max_longest_run: int
    best_longest_run: int


def _longest_run_lengths(genotypes) -> np.ndarray:
    """Per-individual longest-active-run length under the spec §Layer 4 rule."""
    tapes = np.stack(genotypes, axis=0).astype(np.uint8)
    mask = engine_numpy.compute_longest_run_mask(tapes)
    return mask.sum(axis=1).astype(np.int32)


class ChemTapeStatsCollector:
    def __init__(self) -> None:
        self.history: list[ChemTapeGenerationStats] = []

    def record(
        self,
        generation: int,
        fitnesses,
        genotypes,
    ) -> ChemTapeGenerationStats:
        fits = np.asarray(fitnesses, dtype=np.float64)
        best_idx = int(fits.argmax())
        unique = len({g.tobytes() for g in genotypes})
        run_lengths = _longest_run_lengths(genotypes)
        stats = ChemTapeGenerationStats(
            generation=generation,
            best_fitness=float(fits.max()),
            mean_fitness=float(fits.mean()),
            std_fitness=float(fits.std()),
            unique_genotypes=unique,
            best_genotype_hex=genotypes[best_idx].tobytes().hex(),
            mean_longest_run=float(run_lengths.mean()),
            max_longest_run=int(run_lengths.max()),
            best_longest_run=int(run_lengths[best_idx]),
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
                "std_fitness", "unique_genotypes", "best_genotype_hex",
                "mean_longest_run", "max_longest_run", "best_longest_run",
            ])
            for s in self.history:
                w.writerow([
                    s.generation, s.best_fitness, s.mean_fitness,
                    s.std_fitness, s.unique_genotypes, s.best_genotype_hex,
                    s.mean_longest_run, s.max_longest_run, s.best_longest_run,
                ])

    @property
    def best_fitness(self) -> float:
        return max((s.best_fitness for s in self.history), default=0.0)
