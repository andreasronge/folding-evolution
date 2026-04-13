"""GA loop for chem-tape evolution.

Mirrors `ca/evolve.py`. Genotype = length-L uint8 tape with values in {0..15};
per-byte mutation with fresh uniform resample; single-point crossover.

Two execution modes, selected by `cfg.n_islands`:
  - n_islands == 1: panmictic tournament (v1 default, unchanged behavior).
  - n_islands >  1: 8-island coarse-grained model with ring-topology
                    synchronous migration (experiments.md §4).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np

from .config import ChemTapeConfig
from .evaluate import evaluate_population, evaluate_on_inputs
from .metrics import ChemTapeStatsCollector
from .tasks import build_task


@dataclass
class EvolutionResult:
    best_genotype: np.ndarray
    best_fitness: float
    stats: ChemTapeStatsCollector
    generations_run: int
    holdout_fitness: float | None


def random_genotype(cfg: ChemTapeConfig, rng: random.Random) -> np.ndarray:
    """Uniform {0..15} per cell (spec §Layer 7). Three ids execute as NOP."""
    return np.array(
        [rng.randint(0, 15) for _ in range(cfg.tape_length)],
        dtype=np.uint8,
    )


def mutate(tape: np.ndarray, cfg: ChemTapeConfig, rng: random.Random) -> np.ndarray:
    """Per-byte fresh uniform resample at rate `mutation_rate`."""
    out = tape.copy()
    for i in range(out.shape[0]):
        if rng.random() < cfg.mutation_rate:
            out[i] = rng.randint(0, 15)
    return out


def crossover(
    a: np.ndarray, b: np.ndarray, cfg: ChemTapeConfig, rng: random.Random
) -> np.ndarray:
    """Single-point splice along the tape."""
    L = a.shape[0]
    cut = rng.randint(1, L - 1) if L > 1 else 0
    child = np.empty_like(a)
    child[:cut] = a[:cut]
    child[cut:] = b[cut:]
    return child


def _tournament_select(
    indices: list[int],
    fitnesses: np.ndarray,
    tournament_size: int,
    rng: random.Random,
) -> int:
    competitors = rng.sample(indices, min(tournament_size, len(indices)))
    return max(competitors, key=lambda i: fitnesses[i])


def _reproduce_one_island(
    population: list[np.ndarray],
    fitnesses: np.ndarray,
    cfg: ChemTapeConfig,
    rng: random.Random,
) -> list[np.ndarray]:
    """Produce the next generation's population for one island (or the whole
    panmictic pool, which is just a single-island call)."""
    order = np.argsort(-fitnesses)
    elites = [population[i].copy() for i in order[: cfg.elite_count]]
    new_pop: list[np.ndarray] = list(elites)
    pop_idx = list(range(len(population)))
    while len(new_pop) < len(population):
        if rng.random() < cfg.crossover_rate:
            i = _tournament_select(pop_idx, fitnesses, cfg.tournament_size, rng)
            j = _tournament_select(pop_idx, fitnesses, cfg.tournament_size, rng)
            child = crossover(population[i], population[j], cfg, rng)
        else:
            i = _tournament_select(pop_idx, fitnesses, cfg.tournament_size, rng)
            child = population[i].copy()
        child = mutate(child, cfg, rng)
        new_pop.append(child)
    return new_pop


def _migrate(
    islands: list[list[np.ndarray]],
    island_fits: list[np.ndarray],
    cfg: ChemTapeConfig,
    rng: random.Random,
) -> list[list[np.ndarray]]:
    """Ring-topology synchronous migration (experiments.md §4 pre-reg).

    From each island, copy `migrants_per_island` individuals — 1 elite (highest
    fitness) and the rest random from non-elite members. Send to island (i+1)
    mod n. Receiving island replaces its `migrants_per_island` worst individuals
    with the incoming migrants. Copy semantics: sending island keeps its members.
    Migration is synchronous — all migrants are selected from pre-migration state
    before any replacements happen.
    """
    n = cfg.n_islands
    n_migrate = cfg.migrants_per_island
    assert n_migrate >= 1, "migrants_per_island must be ≥ 1"

    # Phase 1: collect migrants (read-only over pre-migration state).
    outgoing: list[list[np.ndarray]] = []
    for i in range(n):
        fit = island_fits[i]
        pop = islands[i]
        elite_idx = int(np.argmax(fit))
        pool = [j for j in range(len(pop)) if j != elite_idx]
        # Want n_migrate total: 1 elite + (n_migrate-1) random non-elite.
        sampled = rng.sample(pool, min(n_migrate - 1, len(pool)))
        chosen = [elite_idx] + sampled
        outgoing.append([pop[j].copy() for j in chosen])

    # Phase 2: apply migrations. Destination = (i+1) % n (ring).
    new_islands: list[list[np.ndarray]] = []
    for i in range(n):
        src = (i - 1) % n
        migrants = outgoing[src]
        fit = island_fits[i]
        pop = [g.copy() for g in islands[i]]
        # Replace the `len(migrants)` worst by incoming migrants.
        order = np.argsort(fit)  # ascending: worst first
        for k, migrant in enumerate(migrants):
            pop[int(order[k])] = migrant
        new_islands.append(pop)
    return new_islands


def _run_evolution_panmictic(cfg: ChemTapeConfig) -> EvolutionResult:
    """Standard tournament-elitism GA (v1 default, unchanged semantics)."""
    rng = random.Random(cfg.seed)
    task = build_task(cfg, seed=cfg.seed)

    population = [random_genotype(cfg, rng) for _ in range(cfg.pop_size)]
    fitnesses, _ = evaluate_population(population, task, cfg)

    stats = ChemTapeStatsCollector()
    stats.record(0, fitnesses, population, arm=cfg.arm)

    gen = 0
    for gen in range(1, cfg.generations + 1):
        population = _reproduce_one_island(population, fitnesses, cfg, rng)
        fitnesses, _ = evaluate_population(population, task, cfg)
        stats.record(gen, fitnesses, population, arm=cfg.arm)

        if fitnesses.max() >= 1.0:
            break

    best_idx = int(np.argmax(fitnesses))
    best = population[best_idx].copy()

    holdout_fitness: float | None = None
    if task.holdout_inputs is not None and task.holdout_labels is not None:
        holdout_fitness = evaluate_on_inputs(
            best, task.holdout_inputs, task.holdout_labels, task, cfg
        )

    return EvolutionResult(
        best_genotype=best,
        best_fitness=float(fitnesses[best_idx]),
        stats=stats,
        generations_run=gen,
        holdout_fitness=holdout_fitness,
    )


def _run_evolution_islands(cfg: ChemTapeConfig) -> EvolutionResult:
    """Coarse-grained island GA (experiments.md §4).

    Splits `cfg.pop_size` into `cfg.n_islands` equal-sized islands. Each island
    runs within-island tournament/elitism/crossover/mutation independently.
    Every `cfg.migration_interval` generations, all islands synchronously
    exchange `cfg.migrants_per_island` individuals around a ring topology.

    Requires `cfg.pop_size` to be an exact multiple of `cfg.n_islands`.
    """
    n_islands = cfg.n_islands
    if cfg.pop_size % n_islands != 0:
        raise ValueError(
            f"pop_size ({cfg.pop_size}) must be divisible by n_islands ({n_islands})"
        )
    island_size = cfg.pop_size // n_islands

    rng = random.Random(cfg.seed)
    task = build_task(cfg, seed=cfg.seed)

    # Initialize islands.
    islands: list[list[np.ndarray]] = [
        [random_genotype(cfg, rng) for _ in range(island_size)]
        for _ in range(n_islands)
    ]

    def _evaluate_all(islands_: list[list[np.ndarray]]):
        flat = [g for isl in islands_ for g in isl]
        fits, _ = evaluate_population(flat, task, cfg)
        per_island = [
            fits[i * island_size : (i + 1) * island_size] for i in range(n_islands)
        ]
        return fits, per_island

    all_fitnesses, island_fits = _evaluate_all(islands)

    stats = ChemTapeStatsCollector()
    flat_pop = [g for isl in islands for g in isl]
    stats.record(0, all_fitnesses, flat_pop, arm=cfg.arm)

    gen = 0
    for gen in range(1, cfg.generations + 1):
        # Within-island reproduction (island-local tournament).
        islands = [
            _reproduce_one_island(islands[i], island_fits[i], cfg, rng)
            for i in range(n_islands)
        ]
        all_fitnesses, island_fits = _evaluate_all(islands)

        # Migration (synchronous ring). Fresh fitnesses from eval above.
        # Not applied on the final generation — no downstream gen would use it.
        if gen % cfg.migration_interval == 0 and gen < cfg.generations:
            islands = _migrate(islands, island_fits, cfg, rng)
            all_fitnesses, island_fits = _evaluate_all(islands)

        flat_pop = [g for isl in islands for g in isl]
        stats.record(gen, all_fitnesses, flat_pop, arm=cfg.arm)

        if all_fitnesses.max() >= 1.0:
            break

    flat_pop = [g for isl in islands for g in isl]
    best_idx = int(np.argmax(all_fitnesses))
    best = flat_pop[best_idx].copy()

    holdout_fitness: float | None = None
    if task.holdout_inputs is not None and task.holdout_labels is not None:
        holdout_fitness = evaluate_on_inputs(
            best, task.holdout_inputs, task.holdout_labels, task, cfg
        )

    return EvolutionResult(
        best_genotype=best,
        best_fitness=float(all_fitnesses[best_idx]),
        stats=stats,
        generations_run=gen,
        holdout_fitness=holdout_fitness,
    )


def run_evolution(cfg: ChemTapeConfig) -> EvolutionResult:
    """Top-level dispatcher. Panmictic if n_islands == 1, island-model otherwise."""
    if cfg.n_islands > 1:
        return _run_evolution_islands(cfg)
    return _run_evolution_panmictic(cfg)
