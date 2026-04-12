"""CAConfig: the sweep-axis catalog for CA-GP experiments."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CAConfig:
    # Representation
    grid_n: int = 16
    steps: int = 16
    n_states: int = 4
    rule_family: str = "outer_totalistic"

    # Task
    task: str = "parity"
    n_bits: int = 4
    n_examples: int = 64

    # I/O layout
    input_row: int = 0
    output_row: int = -1
    output_col: int = -1  # -1 → center column

    # Evolution
    pop_size: int = 256
    generations: int = 200
    tournament_size: int = 3
    elite_count: int = 2
    mutation_rate: float = 0.03
    crossover_rate: float = 0.7

    # Infra
    seed: int = 0
    backend: str = "mlx"  # "numpy" | "mlx"
    log_every: int = 10

    def hash(self) -> str:
        """Stable short hash of this config — used for output directory names."""
        blob = json.dumps(asdict(self), sort_keys=True).encode()
        return hashlib.sha1(blob).hexdigest()[:12]

    def resolved_output_col(self) -> int:
        return self.grid_n // 2 if self.output_col == -1 else self.output_col

    def resolved_output_row(self) -> int:
        return self.grid_n - 1 if self.output_row == -1 else self.output_row
