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
    # §10: per-flip-event metrics under K-alternating schedule. Empty list
    # when alternation is inactive. Each entry is a dict with keys:
    #   flip_gen, old_k, new_k, pre_flip_best, post_flip_best, recovery_gen
    flip_events: list[dict] | None = None


def random_genotype(cfg: ChemTapeConfig, rng: random.Random) -> np.ndarray:
    """Uniform {0..15} per cell (spec §Layer 7). Three ids execute as NOP."""
    return np.array(
        [rng.randint(0, 15) for _ in range(cfg.tape_length)],
        dtype=np.uint8,
    )


def mutate(
    tape: np.ndarray,
    cfg: ChemTapeConfig,
    rng: random.Random,
    topk_override: int | None = None,
) -> np.ndarray:
    """Per-byte fresh uniform resample. Uniform rate `mutation_rate` unless
    bond-protected mutation is active (experiments.md §9): when
    `cfg.bond_protection_ratio < 1.0` and the arm has a bond structure
    (BP / BP_TOPK), cells inside the decode mask mutate at
    `mutation_rate * bond_protection_ratio` while cells outside the mask
    mutate at full `mutation_rate`. The mask is computed on the child tape
    (post-crossover, pre-mutation). `topk_override` supplies the per-generation
    K under the §10 K-alternating schedule."""
    out = tape.copy()
    L = out.shape[0]

    protect_mask: np.ndarray | None = None
    if cfg.bond_protection_ratio < 1.0 and cfg.arm in ("BP", "BP_TOPK"):
        from . import engine_numpy as _np_engine
        tape_2d = out[None, :]
        if cfg.arm == "BP":
            protect_mask = _np_engine.compute_longest_runnable_mask(tape_2d)[0]
        elif cfg.evolve_k:
            # §12: protect body cells under this individual's own K. Header cell 0
            # is always unprotected so K can evolve.
            k_for_protection = cfg.individual_k(out)
            body = out[1:][None, :]
            body_mask = _np_engine.compute_topk_runnable_mask(body, k_for_protection)[0]
            protect_mask = np.zeros(L, dtype=bool)
            protect_mask[1:] = body_mask
        else:  # BP_TOPK fixed/alternating
            k_for_protection = topk_override if topk_override is not None else cfg.topk
            protect_mask = _np_engine.compute_topk_runnable_mask(tape_2d, k_for_protection)[0]

    if protect_mask is None:
        for i in range(L):
            if rng.random() < cfg.mutation_rate:
                out[i] = rng.randint(0, 15)
    else:
        mu = cfg.mutation_rate
        mu_prot = mu * cfg.bond_protection_ratio
        for i in range(L):
            rate = mu_prot if protect_mask[i] else mu
            if rng.random() < rate:
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


def _compute_niched_fitnesses(
    raw: np.ndarray, population: list[np.ndarray], cfg: ChemTapeConfig
) -> np.ndarray:
    """§12b: compute K-niched fitnesses for tournament selection.

    effective_fit[i] = raw_fit[i] * (1 / share_same_K[i]) ** alpha

    Elitism and solve-detection should use raw fitness; only tournament
    selection uses the niched values. Falls back to raw when niching is
    inactive.
    """
    if cfg.k_niching_alpha <= 0.0 or not cfg.evolve_k:
        return raw
    values = cfg.evolve_k_value_list()
    if not values:
        return raw
    n = len(population)
    k_per_ind = np.array([cfg.individual_k(g) for g in population], dtype=np.int64)
    unique_k, counts = np.unique(k_per_ind, return_counts=True)
    count_map = {int(k): int(c) for k, c in zip(unique_k, counts)}
    shares = np.array([count_map[int(k)] / n for k in k_per_ind], dtype=np.float64)
    # share > 0 always (individual itself counts). Avoid 0**α domain issues.
    multiplier = (1.0 / shares) ** cfg.k_niching_alpha
    return raw * multiplier


def _reproduce_one_island(
    population: list[np.ndarray],
    fitnesses: np.ndarray,
    cfg: ChemTapeConfig,
    rng: random.Random,
    topk_override: int | None = None,
) -> list[np.ndarray]:
    """Produce the next generation's population for one island (or the whole
    panmictic pool). `topk_override` flows through to `mutate()` for §10.

    §12b: elitism uses raw `fitnesses`; tournament uses niched fitness when
    cfg.k_niching_alpha > 0 (no-op otherwise).
    """
    order = np.argsort(-fitnesses)
    elites = [population[i].copy() for i in order[: cfg.elite_count]]
    new_pop: list[np.ndarray] = list(elites)
    pop_idx = list(range(len(population)))
    sel_fitnesses = _compute_niched_fitnesses(fitnesses, population, cfg)
    while len(new_pop) < len(population):
        if rng.random() < cfg.crossover_rate:
            i = _tournament_select(pop_idx, sel_fitnesses, cfg.tournament_size, rng)
            j = _tournament_select(pop_idx, sel_fitnesses, cfg.tournament_size, rng)
            child = crossover(population[i], population[j], cfg, rng)
        else:
            i = _tournament_select(pop_idx, sel_fitnesses, cfg.tournament_size, rng)
            child = population[i].copy()
        child = mutate(child, cfg, rng, topk_override=topk_override)
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

    # §12c: precompute host-K header per island (only when active).
    host_headers: dict[int, int] = {}
    adopt_host_k = (
        cfg.migrate_body_adopt_host_k
        and cfg.evolve_k
        and cfg.n_islands > 1
        and cfg.island_k_prior_list()
    )
    if adopt_host_k:
        priors = cfg.island_k_prior_list()
        for i in range(n):
            host_headers[i] = cfg.header_cell_for_k(priors[i])

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
            # §12c: overwrite migrant's cell 0 with host island's K header.
            # Body (cells 1..L-1) migrates; K context is inherited from host.
            if adopt_host_k:
                migrant = migrant.copy()
                migrant[0] = np.uint8(host_headers[i])
            pop[int(order[k])] = migrant
        new_islands.append(pop)
    return new_islands


def _is_k_alternating(cfg: ChemTapeConfig) -> bool:
    return cfg.k_alternating_period > 0 and bool(cfg.k_alternating_values)


def _run_evolution_panmictic(cfg: ChemTapeConfig) -> EvolutionResult:
    """Standard tournament-elitism GA. Supports §10 K-alternating schedule:
    when active, the top-K decode K cycles every `k_alternating_period`
    generations through `k_alternating_values`.
    """
    rng = random.Random(cfg.seed)
    task = build_task(cfg, seed=cfg.seed)

    alternating = _is_k_alternating(cfg)

    population = [random_genotype(cfg, rng) for _ in range(cfg.pop_size)]
    current_k_0 = cfg.current_k(0)
    fitnesses, _ = evaluate_population(population, task, cfg, topk_override=current_k_0)

    stats = ChemTapeStatsCollector()
    evolve_k_values_list = cfg.evolve_k_value_list() if cfg.evolve_k else None
    stats.record(0, fitnesses, population, arm=cfg.arm, evolve_k_values=evolve_k_values_list)

    flip_events: list[dict] = []
    last_k = current_k_0
    # Track the "pre-flip best" for each pending flip — the best fitness at
    # the last generation under the previous K before the flip lands.
    pending_pre_flip: dict | None = None

    gen = 0
    for gen in range(1, cfg.generations + 1):
        current_k = cfg.current_k(gen)

        # Detect K flip transition at this generation.
        if alternating and current_k != last_k:
            pending_pre_flip = {
                "flip_gen": gen,
                "old_k": int(last_k),
                "new_k": int(current_k),
                "pre_flip_best": float(stats.history[-1].best_fitness),
            }

        # Reproduce under current K (mutation uses current_k for protection mask).
        population = _reproduce_one_island(
            population, fitnesses, cfg, rng, topk_override=current_k
        )
        fitnesses, _ = evaluate_population(
            population, task, cfg, topk_override=current_k
        )
        stats.record(gen, fitnesses, population, arm=cfg.arm,
                     evolve_k_values=evolve_k_values_list)

        # Record the immediate post-flip best.
        if pending_pre_flip is not None:
            pending_pre_flip["post_flip_best"] = float(fitnesses.max())
            pending_pre_flip["recovery_gen"] = -1  # filled in later
            flip_events.append(pending_pre_flip)
            pending_pre_flip = None

        # Check recovery for any flip event awaiting recovery.
        for ev in flip_events:
            if ev["recovery_gen"] < 0 and fitnesses.max() >= ev["pre_flip_best"]:
                ev["recovery_gen"] = int(gen)

        last_k = current_k

        if fitnesses.max() >= 1.0 and not alternating:
            break

    best_idx = int(np.argmax(fitnesses))
    best = population[best_idx].copy()

    holdout_fitness: float | None = None
    if task.holdout_inputs is not None and task.holdout_labels is not None:
        # Under alternating, score holdout under the final generation's K.
        final_k = cfg.current_k(gen)
        holdout_fitness = evaluate_on_inputs(
            best, task.holdout_inputs, task.holdout_labels, task, cfg,
            topk_override=final_k,
        )

    return EvolutionResult(
        best_genotype=best,
        best_fitness=float(fitnesses[best_idx]),
        stats=stats,
        generations_run=gen,
        holdout_fitness=holdout_fitness,
        flip_events=flip_events if alternating else None,
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

    # Initialize islands. §12a: if evolve_k AND island_k_priors is set,
    # force cell 0 of each island's initial population to the corresponding
    # K-prior's header value. Length must equal n_islands.
    k_priors = cfg.island_k_prior_list() if cfg.evolve_k else []
    if k_priors and len(k_priors) != n_islands:
        raise ValueError(
            f"island_k_priors has {len(k_priors)} entries but n_islands={n_islands}"
        )
    islands: list[list[np.ndarray]] = []
    for i in range(n_islands):
        pop = [random_genotype(cfg, rng) for _ in range(island_size)]
        if k_priors:
            header = cfg.header_cell_for_k(k_priors[i])
            for g in pop:
                g[0] = np.uint8(header)
        islands.append(pop)

    def _evaluate_all(islands_: list[list[np.ndarray]]):
        flat = [g for isl in islands_ for g in isl]
        fits, _ = evaluate_population(flat, task, cfg)
        per_island = [
            fits[i * island_size : (i + 1) * island_size] for i in range(n_islands)
        ]
        return fits, per_island

    all_fitnesses, island_fits = _evaluate_all(islands)

    stats = ChemTapeStatsCollector()
    evolve_k_values_list = cfg.evolve_k_value_list() if cfg.evolve_k else None
    flat_pop = [g for isl in islands for g in isl]
    stats.record(0, all_fitnesses, flat_pop, arm=cfg.arm,
                 island_fits=island_fits, evolve_k_values=evolve_k_values_list)

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
        stats.record(gen, all_fitnesses, flat_pop, arm=cfg.arm,
                     island_fits=island_fits, evolve_k_values=evolve_k_values_list)

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
