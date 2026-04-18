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
    # §10 / §v1.5: per-flip-event metrics. Empty/None when alternation is off.
    # Each entry is a dict with keys:
    #   flip_gen, pre_flip_best, post_flip_best, recovery_gen,
    #   plus (old_k, new_k) for K flips OR (old_task, new_task) for task flips.
    flip_events: list[dict] | None = None
    # §v1.5: cross-task fitness of the best-of-run genotype, evaluated under
    # each task in task_alternating_values. None when task-alternating is off.
    # Dict of task_name → {fitness, holdout_fitness}.
    cross_task_fitness: dict | None = None
    # §v2.4-proxy-4d: when cfg.dump_final_population is True, these hold the
    # final-generation population (genotypes stacked as (pop_size, tape_length)
    # uint8) and the per-individual fitness (pop_size,) float32. None when
    # the flag is off, so existing callers are unaffected.
    final_population: np.ndarray | None = None
    final_population_fitness: np.ndarray | None = None
    # §v2.5-plasticity-1a: per-individual plastic metrics emitted when
    # cfg.plasticity_enabled=True AND cfg.dump_final_population=True.
    # Each is a (pop_size,)-shaped array; None when plasticity is off.
    final_delta_final: np.ndarray | None = None
    final_test_fitness_frozen: np.ndarray | None = None
    final_test_fitness_plastic: np.ndarray | None = None
    final_train_fitness_frozen: np.ndarray | None = None
    final_train_fitness_plastic: np.ndarray | None = None
    final_has_gt: np.ndarray | None = None


def _token_max(cfg: ChemTapeConfig) -> int:
    """Inclusive upper bound for `random.randint(0, token_max)` on this
    alphabet. v1: 15 (ids 0..15 — all 16 v1 tokens incl. separators 14/15).
    v2_probe: 21 (ids 0..21 — 20 primitives + separators 20/21).

    Separators are part of the representation (they break bonded runs under
    every arm), so the mutation range includes them — same shape as v1.
    """
    if cfg.alphabet == "v2_split":
        return 23
    return 21 if cfg.alphabet == "v2_probe" else 15


def random_genotype(cfg: ChemTapeConfig, rng: random.Random) -> np.ndarray:
    """Uniform {0..token_max} per cell (spec §Layer 7). Token range depends
    on `cfg.alphabet`: v1 → 0..15 (unchanged), v2_probe → 0..21."""
    hi = _token_max(cfg)
    return np.array(
        [rng.randint(0, hi) for _ in range(cfg.tape_length)],
        dtype=np.uint8,
    )


def _parse_seed_tapes(cfg: ChemTapeConfig) -> list[np.ndarray]:
    """§v2.4-proxy-4: parse cfg.seed_tapes into length-tape_length uint8 arrays.

    Each comma-separated entry is a hex string (one byte per token). Shorter
    seeds are zero-padded on the right (NOP tail); longer seeds raise
    ValueError. Returns [] when seed_tapes is empty.
    """
    if not cfg.seed_tapes:
        return []
    hi = _token_max(cfg)
    L = cfg.tape_length
    out: list[np.ndarray] = []
    for s in cfg.seed_tapes.split(","):
        s = s.strip()
        if not s:
            continue
        try:
            raw = bytes.fromhex(s)
        except ValueError as e:
            raise ValueError(f"seed_tapes entry is not valid hex: {s!r}") from e
        if len(raw) > L:
            raise ValueError(
                f"seed_tapes entry has {len(raw)} bytes > tape_length={L}; "
                "longer seeds are not truncated. Trim the seed explicitly."
            )
        arr = np.zeros(L, dtype=np.uint8)
        arr[: len(raw)] = np.frombuffer(raw, dtype=np.uint8)
        if int(arr.max()) > hi:
            raise ValueError(
                f"seed_tapes entry contains token id > token_max={hi} "
                f"for alphabet={cfg.alphabet!r}: {s!r}"
            )
        out.append(arr)
    return out


def build_initial_population(
    cfg: ChemTapeConfig,
    rng: random.Random,
    size: int,
) -> list[np.ndarray]:
    """Build an initial population of `size` genotypes with optional seeding.

    When cfg.seed_fraction > 0 and cfg.seed_tapes is non-empty, ``round(size *
    seed_fraction)`` individuals are copies drawn uniformly-with-replacement
    from the parsed seed pool; the remainder are uniform-random. The combined
    population is shuffled so seeded individuals do not cluster at the start.

    Raises if seeded-init is requested alongside evolve_k or island_k_priors,
    because those paths overwrite cell 0 after init and would silently clobber
    the seed's first byte.
    """
    seeds = _parse_seed_tapes(cfg)
    if not seeds or cfg.seed_fraction <= 0.0:
        return [random_genotype(cfg, rng) for _ in range(size)]

    if cfg.evolve_k or cfg.island_k_priors:
        raise ValueError(
            "seeded-init (seed_fraction > 0) is incompatible with evolve_k "
            "or island_k_priors — cell 0 would be overwritten after seeding."
        )
    if not (0.0 < cfg.seed_fraction <= 1.0):
        raise ValueError(
            f"seed_fraction must be in (0.0, 1.0], got {cfg.seed_fraction}"
        )

    n_seed = int(round(cfg.seed_fraction * size))
    n_random = size - n_seed
    pop: list[np.ndarray] = []
    for _ in range(n_seed):
        idx = rng.randint(0, len(seeds) - 1)
        pop.append(seeds[idx].copy())
    for _ in range(n_random):
        pop.append(random_genotype(cfg, rng))
    rng.shuffle(pop)
    return pop


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
    hi = _token_max(cfg)

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
                out[i] = rng.randint(0, hi)
    else:
        mu = cfg.mutation_rate
        mu_prot = mu * cfg.bond_protection_ratio
        for i in range(L):
            rate = mu_prot if protect_mask[i] else mu
            if rng.random() < rate:
                out[i] = rng.randint(0, hi)
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


def _ranking_select(
    indices: list[int],
    fitnesses: np.ndarray,
    rng: random.Random,
) -> int:
    """Linear-rank selection over `indices`. Assigns selection probability
    proportional to rank (rank 1 = worst, rank N = best). Does not use
    tournament_size — the whole pool is ranked."""
    if len(indices) == 1:
        return indices[0]
    ranked = sorted(indices, key=lambda i: fitnesses[i])  # ascending rank
    n = len(ranked)
    weights = list(range(1, n + 1))  # rank 1..n, higher = better
    total = n * (n + 1) // 2
    r = rng.random() * total
    cumulative = 0
    for rank_idx, idx in enumerate(ranked):
        cumulative += weights[rank_idx]
        if cumulative >= r:
            return idx
    return ranked[-1]


def _truncation_select(
    indices: list[int],
    fitnesses: np.ndarray,
    top_fraction: float,
    rng: random.Random,
) -> int:
    """Truncation / (µ,λ) selection. Restricts the parent pool to the top
    `top_fraction` of `indices` by fitness, then samples uniformly from that
    pool. When fewer than 2 individuals qualify, falls back to the full pool."""
    n_keep = max(2, int(round(len(indices) * top_fraction)))
    ranked = sorted(indices, key=lambda i: fitnesses[i], reverse=True)
    pool = ranked[:n_keep]
    return rng.choice(pool)


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

    # §v2.4-proxy-5c: dispatch by selection_mode. At default "tournament"
    # the RNG sequence is byte-identical to the pre-5c implementation
    # (same _tournament_select calls in the same order).
    def _select() -> int:
        if cfg.selection_mode == "ranking":
            return _ranking_select(pop_idx, sel_fitnesses, rng)
        elif cfg.selection_mode == "truncation":
            return _truncation_select(
                pop_idx, sel_fitnesses, cfg.selection_top_fraction, rng
            )
        else:  # "tournament" (default)
            return _tournament_select(
                pop_idx, sel_fitnesses, cfg.tournament_size, rng
            )

    while len(new_pop) < len(population):
        if rng.random() < cfg.crossover_rate:
            i = _select()
            j = _select()
            child = crossover(population[i], population[j], cfg, rng)
        else:
            i = _select()
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


def _is_task_alternating(cfg: ChemTapeConfig) -> bool:
    return cfg.task_alternating_period > 0 and bool(cfg.task_alternating_values)


def _build_tasks_for_config(cfg: ChemTapeConfig):
    """§v1.5: if task-alternating, build a dict of {task_name → Task} for all
    tasks in the schedule. Else build a single {cfg.task → Task} dict.
    All tasks use cfg.seed — deterministic per-task example generation.
    """
    from .tasks import TASK_REGISTRY
    if _is_task_alternating(cfg):
        task_names = cfg.task_alternating_value_list()
    else:
        task_names = [cfg.task]
    tasks: dict = {}
    for name in task_names:
        if name not in TASK_REGISTRY:
            raise KeyError(f"Unknown task {name!r}; known: {list(TASK_REGISTRY)}")
        tasks[name] = TASK_REGISTRY[name](cfg, cfg.seed)
    return tasks


def _run_evolution_panmictic(cfg: ChemTapeConfig) -> EvolutionResult:
    """Standard tournament-elitism GA. Supports §10 K-alternating and
    §v1.5 task-alternating schedules (both may be active simultaneously
    but the intended use is one at a time).
    """
    rng = random.Random(cfg.seed)
    tasks_by_name = _build_tasks_for_config(cfg)

    k_alt = _is_k_alternating(cfg)
    task_alt = _is_task_alternating(cfg)
    alternating = k_alt or task_alt

    population = build_initial_population(cfg, rng, cfg.pop_size)
    current_k_0 = cfg.current_k(0)
    current_task_0 = cfg.current_task(0)
    task_0 = tasks_by_name[current_task_0]
    fitnesses, _ = evaluate_population(population, task_0, cfg, topk_override=current_k_0)

    stats = ChemTapeStatsCollector()
    evolve_k_values_list = cfg.evolve_k_value_list() if cfg.evolve_k else None
    stats.record(0, fitnesses, population, arm=cfg.arm, evolve_k_values=evolve_k_values_list)

    flip_events: list[dict] = []
    last_k = current_k_0
    last_task = current_task_0
    pending_pre_flip: dict | None = None

    gen = 0
    for gen in range(1, cfg.generations + 1):
        current_k = cfg.current_k(gen)
        current_task_name = cfg.current_task(gen)
        current_task_obj = tasks_by_name[current_task_name]

        # Detect K-flip or task-flip transition.
        if k_alt and current_k != last_k:
            pending_pre_flip = {
                "flip_gen": gen, "flip_type": "k",
                "old_k": int(last_k), "new_k": int(current_k),
                "pre_flip_best": float(stats.history[-1].best_fitness),
            }
        elif task_alt and current_task_name != last_task:
            pending_pre_flip = {
                "flip_gen": gen, "flip_type": "task",
                "old_task": last_task, "new_task": current_task_name,
                "pre_flip_best": float(stats.history[-1].best_fitness),
            }

        # Reproduce under current K.
        population = _reproduce_one_island(
            population, fitnesses, cfg, rng, topk_override=current_k
        )
        fitnesses, _ = evaluate_population(
            population, current_task_obj, cfg, topk_override=current_k
        )
        stats.record(gen, fitnesses, population, arm=cfg.arm,
                     evolve_k_values=evolve_k_values_list)

        # Record immediate post-flip best.
        if pending_pre_flip is not None:
            pending_pre_flip["post_flip_best"] = float(fitnesses.max())
            pending_pre_flip["recovery_gen"] = -1
            flip_events.append(pending_pre_flip)
            pending_pre_flip = None

        for ev in flip_events:
            if ev["recovery_gen"] < 0 and fitnesses.max() >= ev["pre_flip_best"]:
                ev["recovery_gen"] = int(gen)

        last_k = current_k
        last_task = current_task_name

        # Early termination only if no alternation is active (would cut a run
        # short mid-regime, skipping the interesting post-flip dynamics).
        # §v2.4-proxy-4b: also suppressed when disable_early_termination is set,
        # so maintainability probes can observe full-horizon drift.
        if (
            fitnesses.max() >= 1.0
            and not alternating
            and not cfg.disable_early_termination
        ):
            break

    best_idx = int(np.argmax(fitnesses))
    best = population[best_idx].copy()

    # Holdout on the final-gen task/K.
    final_k = cfg.current_k(gen)
    final_task_name = cfg.current_task(gen)
    final_task = tasks_by_name[final_task_name]
    holdout_fitness: float | None = None
    if final_task.holdout_inputs is not None and final_task.holdout_labels is not None:
        holdout_fitness = evaluate_on_inputs(
            best, final_task.holdout_inputs, final_task.holdout_labels,
            final_task, cfg, topk_override=final_k,
        )

    # §v1.5: cross-task fitness of the best-of-run genotype under every task.
    cross_task_fitness: dict | None = None
    if task_alt:
        cross_task_fitness = {}
        for name, t in tasks_by_name.items():
            fit = evaluate_on_inputs(best, t.inputs, t.labels, t, cfg, topk_override=final_k)
            hold = None
            if t.holdout_inputs is not None and t.holdout_labels is not None:
                hold = evaluate_on_inputs(
                    best, t.holdout_inputs, t.holdout_labels, t, cfg, topk_override=final_k
                )
            gap = None if hold is None else float(fit) - float(hold)
            cross_task_fitness[name] = {
                "fitness": float(fit),
                "holdout_fitness": hold,
                "gap": gap,
            }

    final_pop_arr: np.ndarray | None = None
    final_pop_fit: np.ndarray | None = None
    final_delta: np.ndarray | None = None
    final_tff: np.ndarray | None = None
    final_tfp: np.ndarray | None = None
    final_trf: np.ndarray | None = None
    final_trp: np.ndarray | None = None
    final_has_gt: np.ndarray | None = None
    if cfg.dump_final_population:
        final_pop_arr = np.stack(population).astype(np.uint8, copy=False)
        final_pop_fit = np.asarray(fitnesses, dtype=np.float32)
        # §v2.5-plasticity-1a: emit per-individual plastic metrics. These
        # are the inputs the analysis pipeline needs (delta_final,
        # test_fitness_frozen, test_fitness_plastic, has_gt → GT_bypass).
        if cfg.plasticity_enabled:
            from .plasticity import evaluate_population_plastic
            from .evaluate import _programs_for_arm
            # Re-decode programs under the final-gen K (same dispatch path
            # as evaluate_population).
            tapes_final = np.stack(population).astype(np.uint8, copy=False)
            progs_final = _programs_for_arm(cfg, tapes_final, topk_override=final_k)
            pm = evaluate_population_plastic(progs_final, final_task, cfg)
            final_delta = pm["delta_final"]
            final_tff = pm["test_fitness_frozen"]
            final_tfp = pm["test_fitness_plastic"]
            final_trf = pm["train_fitness_frozen"]
            final_trp = pm["train_fitness_plastic"]
            final_has_gt = pm["has_gt"]

    return EvolutionResult(
        best_genotype=best,
        best_fitness=float(fitnesses[best_idx]),
        stats=stats,
        generations_run=gen,
        holdout_fitness=holdout_fitness,
        flip_events=flip_events if alternating else None,
        cross_task_fitness=cross_task_fitness,
        final_population=final_pop_arr,
        final_population_fitness=final_pop_fit,
        final_delta_final=final_delta,
        final_test_fitness_frozen=final_tff,
        final_test_fitness_plastic=final_tfp,
        final_train_fitness_frozen=final_trf,
        final_train_fitness_plastic=final_trp,
        final_has_gt=final_has_gt,
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
        pop = build_initial_population(cfg, rng, island_size)
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

        if all_fitnesses.max() >= 1.0 and not cfg.disable_early_termination:
            break

    flat_pop = [g for isl in islands for g in isl]
    best_idx = int(np.argmax(all_fitnesses))
    best = flat_pop[best_idx].copy()

    holdout_fitness: float | None = None
    if task.holdout_inputs is not None and task.holdout_labels is not None:
        holdout_fitness = evaluate_on_inputs(
            best, task.holdout_inputs, task.holdout_labels, task, cfg
        )

    final_pop_arr: np.ndarray | None = None
    final_pop_fit: np.ndarray | None = None
    final_delta: np.ndarray | None = None
    final_tff: np.ndarray | None = None
    final_tfp: np.ndarray | None = None
    final_trf: np.ndarray | None = None
    final_trp: np.ndarray | None = None
    final_has_gt: np.ndarray | None = None
    if cfg.dump_final_population:
        final_pop_arr = np.stack(flat_pop).astype(np.uint8, copy=False)
        final_pop_fit = np.asarray(all_fitnesses, dtype=np.float32)
        if cfg.plasticity_enabled:
            from .plasticity import evaluate_population_plastic
            from .evaluate import _programs_for_arm
            progs_final = _programs_for_arm(cfg, final_pop_arr)
            pm = evaluate_population_plastic(progs_final, task, cfg)
            final_delta = pm["delta_final"]
            final_tff = pm["test_fitness_frozen"]
            final_tfp = pm["test_fitness_plastic"]
            final_trf = pm["train_fitness_frozen"]
            final_trp = pm["train_fitness_plastic"]
            final_has_gt = pm["has_gt"]

    return EvolutionResult(
        best_genotype=best,
        best_fitness=float(all_fitnesses[best_idx]),
        stats=stats,
        generations_run=gen,
        holdout_fitness=holdout_fitness,
        final_population=final_pop_arr,
        final_population_fitness=final_pop_fit,
        final_delta_final=final_delta,
        final_test_fitness_frozen=final_tff,
        final_test_fitness_plastic=final_tfp,
        final_train_fitness_frozen=final_trf,
        final_train_fitness_plastic=final_trp,
        final_has_gt=final_has_gt,
    )


def run_evolution(cfg: ChemTapeConfig) -> EvolutionResult:
    """Top-level dispatcher. Panmictic if n_islands == 1, island-model otherwise."""
    if cfg.n_islands > 1:
        return _run_evolution_islands(cfg)
    return _run_evolution_panmictic(cfg)
