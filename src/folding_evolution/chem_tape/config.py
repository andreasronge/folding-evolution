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
        blob = json.dumps(d, sort_keys=True).encode()
        return hashlib.sha1(blob).hexdigest()[:12]
