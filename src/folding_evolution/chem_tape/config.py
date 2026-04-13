"""ChemTapeConfig: the sweep-axis catalog for chem-tape v1 experiments."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ChemTapeConfig:
    # Representation
    tape_length: int = 32
    arm: str = "B"                  # "A" = direct stack-GP, "B" = chem-tape v1

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

    # Infra
    seed: int = 0
    backend: str = "mlx"            # "numpy" | "mlx"
    log_every: int = 10

    def hash(self) -> str:
        """Stable short hash of this config — used for output directory names."""
        blob = json.dumps(asdict(self), sort_keys=True).encode()
        return hashlib.sha1(blob).hexdigest()[:12]
