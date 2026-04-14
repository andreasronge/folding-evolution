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
    unique_programs: int
    best_genotype_hex: str
    mean_longest_run: float
    max_longest_run: int
    best_longest_run: int
    # Per-island best fitness vector (islands-only; empty for panmictic).
    # Stored as np.float64 so NPZ roundtrip is clean. (§11 diagnostic.)
    per_island_best: np.ndarray | None = None
    per_island_mean: np.ndarray | None = None


def _longest_run_mask(genotypes) -> tuple[np.ndarray, np.ndarray]:
    """Return (tapes, mask) for the population using the spec §Layer 4 rule."""
    tapes = np.stack(genotypes, axis=0).astype(np.uint8)
    mask = engine_numpy.compute_longest_run_mask(tapes)
    return tapes, mask


def _count_unique_programs(tapes: np.ndarray, mask: np.ndarray, arm: str) -> int:
    """Count distinct executor-visible programs.

    Arm A: full tape (32 cells; every cell executes).
    Arm B: v1 longest-active-run (mask passed in is the strict mask).
    Arm BP: the permeable mask must be computed separately — the caller
    passes the strict mask as the diagnostic; we recompute the permeable
    mask here so the "unique programs" count reflects what the executor
    actually sees.
    """
    if arm == "A":
        return len({tapes[b].tobytes() for b in range(tapes.shape[0])})
    if arm == "BP":
        perm_mask = engine_numpy.compute_longest_runnable_mask(tapes)
        seen: set[bytes] = set()
        for b in range(tapes.shape[0]):
            seen.add(tapes[b][perm_mask[b]].tobytes())
        return len(seen)
    # Arm B: strict active-run mask already computed by the caller.
    seen: set[bytes] = set()
    for b in range(tapes.shape[0]):
        seen.add(tapes[b][mask[b]].tobytes())
    return len(seen)


class ChemTapeStatsCollector:
    def __init__(self) -> None:
        self.history: list[ChemTapeGenerationStats] = []

    def record(
        self,
        generation: int,
        fitnesses,
        genotypes,
        arm: str = "B",
        island_fits: list | None = None,
    ) -> ChemTapeGenerationStats:
        fits = np.asarray(fitnesses, dtype=np.float64)
        best_idx = int(fits.argmax())
        unique = len({g.tobytes() for g in genotypes})
        tapes, mask = _longest_run_mask(genotypes)
        run_lengths = mask.sum(axis=1).astype(np.int32)
        unique_progs = _count_unique_programs(tapes, mask, arm)

        per_island_best = None
        per_island_mean = None
        if island_fits is not None:
            per_island_best = np.array([float(np.asarray(f).max()) for f in island_fits], dtype=np.float64)
            per_island_mean = np.array([float(np.asarray(f).mean()) for f in island_fits], dtype=np.float64)

        stats = ChemTapeGenerationStats(
            generation=generation,
            best_fitness=float(fits.max()),
            mean_fitness=float(fits.mean()),
            std_fitness=float(fits.std()),
            unique_genotypes=unique,
            unique_programs=unique_progs,
            best_genotype_hex=genotypes[best_idx].tobytes().hex(),
            mean_longest_run=float(run_lengths.mean()),
            max_longest_run=int(run_lengths.max()),
            best_longest_run=int(run_lengths[best_idx]),
            per_island_best=per_island_best,
            per_island_mean=per_island_mean,
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
                "std_fitness", "unique_genotypes", "unique_programs",
                "best_genotype_hex",
                "mean_longest_run", "max_longest_run", "best_longest_run",
            ])
            for s in self.history:
                w.writerow([
                    s.generation, s.best_fitness, s.mean_fitness,
                    s.std_fitness, s.unique_genotypes, s.unique_programs,
                    s.best_genotype_hex,
                    s.mean_longest_run, s.max_longest_run, s.best_longest_run,
                ])

    @property
    def best_fitness(self) -> float:
        return max((s.best_fitness for s in self.history), default=0.0)
