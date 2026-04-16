"""ChemTapeConfig: the sweep-axis catalog for chem-tape v1 experiments."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ChemTapeConfig:
    # Representation
    tape_length: int = 32
    arm: str = "B"                  # "A" = direct stack-GP, "B" = chem-tape v1 strict,
                                    # "BP" = v1 permeable (NOP passes through bonded runs),
                                    # "BP_TOPK" = BP with K longest runs concatenated
                                    #             in tape order (experiments.md §8).

    # Top-K decode breadth (only meaningful when arm == "BP_TOPK"). K=1 is
    # identical to "BP"; K large ⇒ every non-separator cell executes.
    topk: int = 1

    # Bond-protected mutation (experiments.md §9, 2×2 redesign). r=1.0 ⇒
    # uniform mutation (unchanged). r<1.0 ⇒ cells in the arm's decode mask
    # (the *executing* cells) mutate at rate `mutation_rate * r`; cells
    # outside the mask mutate at full `mutation_rate`. Meaningful only when
    # arm ∈ {"BP", "BP_TOPK"}; ignored for "A" and "B".
    bond_protection_ratio: float = 1.0

    # K-alternating schedule (experiments.md §10 plasticity test). When
    # period > 0 AND values is non-empty, the BP_TOPK decode K cycles
    # through `values` every `period` generations:
    #   current_k(gen) = values[(gen // period) % len(values)]
    # The `topk` field is ignored in this mode. Values are stored as a
    # comma-separated string (e.g. "3,999") for stable dataclass hashing.
    k_alternating_period: int = 0
    k_alternating_values: str = ""

    # Evolve-K-per-individual (experiments.md §12). When True:
    #   - Cell 0 of each tape is the K-header: tape[0] % len(values) selects
    #     K for that individual from `evolve_k_values`.
    #   - Cells 1..L-1 are the program body — decode / protect on that region
    #     only. Cell 0 is mutated at full rate regardless of protection.
    #   - Mutually exclusive with k_alternating; `topk` and any fixed-K
    #     config are ignored when evolve_k=True.
    evolve_k: bool = False
    evolve_k_values: str = "1,2,3,4,8,999"

    # §12a: K-prior island initialization. When non-empty AND evolve_k=True
    # AND n_islands > 1, this sets each island's initial-population K by
    # forcing cell 0 during initialization. String format is the K value
    # per island (e.g. "1,1,3,3,8,8,999,999" for 8 islands biased toward
    # K = {1, 3, 8, 999} with 2 islands each). Length must equal n_islands;
    # each entry must be in evolve_k_values. Mutation afterward is free
    # (cell 0 drifts at full rate); selection maintains K if adaptive.
    island_k_priors: str = ""

    # §12b: K-niching via fitness sharing. When alpha > 0 AND evolve_k is on,
    # tournament selection uses effective_fit[i] = raw_fit[i] / share_same_K[i]^alpha.
    # Rare-K individuals get a selection-pressure bonus inversely proportional
    # to their K's population share, raised to the alpha power. Elitism and
    # solve-detection still use raw fitness; only tournament uses the niched
    # signal. alpha=0 recovers standard tournament.
    k_niching_alpha: float = 0.0

    # §12c: "migrate body, adopt host K" migration variant. When True AND
    # evolve_k AND island_k_priors set AND n_islands > 1, migrants' cell 0
    # is overwritten with the destination island's prior K header before
    # replacement. This decouples the migrant's body from its source-island K
    # context. Tests whether body-propagation across K-islands (rather than
    # K-plus-body co-propagation) is the missing ingredient.
    migrate_body_adopt_host_k: bool = False

    # §v1.5: task-alternating schedule (task-axis analogue of §10 K-alternation).
    # When period > 0 AND values is non-empty, the active task cycles through
    # `task_alternating_values` every `period` generations:
    #   current_task(gen) = values[(gen // period) % len(values)]
    # The `task` field is used as fallback when alternation is inactive.
    # Values are comma-separated task names (e.g. "sum_gt_10,count_r,has_upper").
    task_alternating_period: int = 0
    task_alternating_values: str = ""

    # Task
    task: str = "count_r"           # "count_r" | "has_upper" | "sum_gt_10"
    n_examples: int = 64
    holdout_size: int = 256         # 0 disables holdout

    # Evolution (identical defaults to CA)
    pop_size: int = 256
    generations: int = 200
    tournament_size: int = 3
    elite_count: int = 2
    mutation_rate: float = 0.03
    crossover_rate: float = 0.7

    # Island-model GA (experiments.md §4). n_islands=1 → panmictic (default, unchanged
    # from v1). n_islands>1 splits the population into equal-sized islands with ring-
    # topology synchronous migration every `migration_interval` generations.
    n_islands: int = 1
    migration_interval: int = 50
    migrants_per_island: int = 2    # 1 elite + 1 random non-elite per migration

    # v2-probe alphabet switch (architecture-v2.md). "v1" (default) preserves
    # the 16-id alphabet and hash-stability for all prior sweeps. "v2_probe"
    # enables ids 14..19 as new primitives and shifts separators to 20/21.
    alphabet: str = "v1"

    # §v2.14: safe-pop executor semantics. "preserve" (default) leaves wrong-
    # typed values on the stack; "consume" always pops regardless of type.
    safe_pop_mode: str = "preserve"

    # §v2.4-proxy-4: seeded-initialization hook. When non-empty, seed_tapes
    # is a comma-separated list of hex strings (one tape per entry, one byte
    # per token). seed_fraction ∈ [0.0, 1.0] specifies the fraction of the
    # initial population drawn (with replacement) from this seed pool; the
    # remainder are uniform-random. Seeds shorter than tape_length are
    # zero-padded on the right (NOP tail); longer seeds raise ValueError.
    # Incompatible with evolve_k / island_k_priors (which overwrite cell 0
    # post-seeding) — validated in build_initial_population. Excluded from
    # hash at defaults so pre-§v2.4-proxy-4 sweeps remain addressable.
    seed_tapes: str = ""
    seed_fraction: float = 0.0

    # Infra
    seed: int = 0
    backend: str = "mlx"            # "numpy" | "mlx"
    log_every: int = 10

    def hash(self) -> str:
        """Stable short hash of this config — used for output directory names.

        `topk` is excluded from the hash for arms other than BP_TOPK so that
        existing cached sweep results (A/B/BP) remain addressable unchanged.
        `bond_protection_ratio` is excluded when it equals its 1.0 default,
        so pre-§9 cached results remain addressable.
        """
        d = asdict(self)
        if self.arm != "BP_TOPK":
            d.pop("topk", None)
        if self.bond_protection_ratio == 1.0:
            d.pop("bond_protection_ratio", None)
        # K-alternating fields excluded from hash when inactive → existing
        # cached BP_TOPK results (§8, §9, §9b, §9c, §11) remain addressable.
        if self.k_alternating_period == 0 and self.k_alternating_values == "":
            d.pop("k_alternating_period", None)
            d.pop("k_alternating_values", None)
        # Evolve-K fields excluded at defaults for the same reason.
        if not self.evolve_k:
            d.pop("evolve_k", None)
            d.pop("evolve_k_values", None)
        # §12a island K priors: excluded at default empty string.
        if self.island_k_priors == "":
            d.pop("island_k_priors", None)
        # §12b / §12c: excluded at default-off values.
        if self.k_niching_alpha == 0.0:
            d.pop("k_niching_alpha", None)
        if not self.migrate_body_adopt_host_k:
            d.pop("migrate_body_adopt_host_k", None)
        # §v1.5: task-alternating excluded at default-off.
        if self.task_alternating_period == 0 and self.task_alternating_values == "":
            d.pop("task_alternating_period", None)
            d.pop("task_alternating_values", None)
        # v2-probe alphabet: excluded from hash at default "v1" so existing
        # v1 sweep hashes are unchanged.
        if self.alphabet == "v1":
            d.pop("alphabet", None)
        # §v2.14 safe-pop mode: excluded at default "preserve".
        if self.safe_pop_mode == "preserve":
            d.pop("safe_pop_mode", None)
        # §v2.4-proxy-4 seeded-init: excluded at defaults.
        if self.seed_tapes == "" and self.seed_fraction == 0.0:
            d.pop("seed_tapes", None)
            d.pop("seed_fraction", None)
        blob = json.dumps(d, sort_keys=True).encode()
        return hashlib.sha1(blob).hexdigest()[:12]

    def current_k(self, generation: int) -> int:
        """Return the K to use at `generation` (for BP_TOPK decode).

        If K-alternation is inactive (period=0 or empty values), returns
        `self.topk`. Otherwise cycles through parsed values every `period`
        generations. Also defines what `evolve.py` passes to the decode.
        """
        if self.k_alternating_period <= 0 or not self.k_alternating_values:
            return self.topk
        values = [int(x) for x in self.k_alternating_values.split(",") if x.strip()]
        if not values:
            return self.topk
        idx = (generation // self.k_alternating_period) % len(values)
        return values[idx]

    def evolve_k_value_list(self) -> list[int]:
        """Parse evolve_k_values into a list of ints, e.g. "1,2,3,4,8,999"."""
        return [int(x) for x in self.evolve_k_values.split(",") if x.strip()]

    def individual_k(self, tape) -> int:
        """§12 evolve-K: cell 0's value (mod len(values)) selects K for this
        individual. Undefined behavior if evolve_k is False.
        """
        import numpy as np
        values = self.evolve_k_value_list()
        if not values:
            return self.topk
        header = int(np.asarray(tape).ravel()[0])
        return values[header % len(values)]

    def island_k_prior_list(self) -> list[int]:
        """§12a: parse island_k_priors string into a list of K values,
        one per island. Returns [] if unset."""
        if not self.island_k_priors:
            return []
        return [int(x) for x in self.island_k_priors.split(",") if x.strip()]

    def header_cell_for_k(self, k: int) -> int:
        """§12a: smallest valid cell-0 value that maps to target K under the
        current evolve_k_values mapping. Raises if K is not in the value set.
        """
        values = self.evolve_k_value_list()
        if k not in values:
            raise ValueError(f"K={k} not in evolve_k_values={values}")
        return values.index(k)  # in range [0, len(values)-1] ⊂ [0, 15]

    def task_alternating_value_list(self) -> list[str]:
        """§v1.5: parse task_alternating_values into a list of task names."""
        if not self.task_alternating_values:
            return []
        return [x.strip() for x in self.task_alternating_values.split(",") if x.strip()]

    def current_task(self, generation: int) -> str:
        """§v1.5: return the active task name at this generation.
        When alternation inactive, returns self.task.
        """
        if self.task_alternating_period <= 0 or not self.task_alternating_values:
            return self.task
        values = self.task_alternating_value_list()
        if not values:
            return self.task
        idx = (generation // self.task_alternating_period) % len(values)
        return values[idx]
