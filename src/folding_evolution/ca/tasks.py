"""Task registry for CA-GP.

A task knows how to:
  - generate (inputs, labels) for a given seed
  - encode an input into an `input_clamp` row of shape (grid_n,) of cell states
  - decode an output cell state into a label
  - score predictions vs labels → fitness in [0, 1]
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable

import numpy as np

from .config import CAConfig


@dataclass
class Task:
    name: str
    inputs: np.ndarray         # (n_examples, n_bits) int, for parity; generic shape for others
    labels: np.ndarray         # (n_examples,) int
    encode: Callable[[np.ndarray, CAConfig], np.ndarray]
    """(batch_inputs, cfg) -> (batch, grid_n) uint8 clamp row"""
    decode: Callable[[np.ndarray, CAConfig], np.ndarray]
    """(batch_output_states,) -> (batch,) int predicted label"""


def _parity_encode(batch_inputs: np.ndarray, cfg: CAConfig) -> np.ndarray:
    """Encode n_bits of parity input into a (batch, grid_n) clamp row.

    Places the bits in the center of row 0, padded with zeros on both sides.
    Cell state for bit 0 = 0, bit 1 = 1 (states 2..K-1 unused by encoding).
    """
    b, n_bits = batch_inputs.shape
    clamp = np.zeros((b, cfg.grid_n), dtype=np.uint8)
    start = (cfg.grid_n - n_bits) // 2
    clamp[:, start : start + n_bits] = batch_inputs.astype(np.uint8)
    return clamp


def _parity_decode(out_states: np.ndarray, cfg: CAConfig) -> np.ndarray:
    """Decode cell state → predicted bit. state > K/2 maps to 1, else 0."""
    threshold = cfg.n_states / 2.0
    return (out_states > threshold).astype(np.int8)


def make_parity_task(cfg: CAConfig, seed: int) -> Task:
    """Build a parity task with n_examples drawn from the 2**n_bits possibilities."""
    rng = np.random.default_rng(seed)
    n = cfg.n_bits
    total = 1 << n
    if cfg.n_examples >= total:
        inputs = np.array([[(i >> k) & 1 for k in range(n)] for i in range(total)], dtype=np.int8)
    else:
        idx = rng.choice(total, size=cfg.n_examples, replace=False)
        inputs = np.array([[(i >> k) & 1 for k in range(n)] for i in idx], dtype=np.int8)
    labels = inputs.sum(axis=1).astype(np.int8) % 2
    return Task(
        name="parity",
        inputs=inputs,
        labels=labels,
        encode=_parity_encode,
        decode=_parity_decode,
    )


def make_majority_task(cfg: CAConfig, seed: int) -> Task:
    """Strict-majority task: output 1 iff count_1s(input) > n_bits / 2.

    Reuses the parity encode/decode conventions (row-0 clamp, center readout bit)
    so the only thing changing vs `make_parity_task` is the label function.
    Ties (equal 1s and 0s) map to 0.
    """
    rng = np.random.default_rng(seed)
    n = cfg.n_bits
    total = 1 << n
    if cfg.n_examples >= total:
        inputs = np.array([[(i >> k) & 1 for k in range(n)] for i in range(total)], dtype=np.int8)
    else:
        idx = rng.choice(total, size=cfg.n_examples, replace=False)
        inputs = np.array([[(i >> k) & 1 for k in range(n)] for i in idx], dtype=np.int8)
    labels = (inputs.sum(axis=1) * 2 > n).astype(np.int8)
    return Task(
        name="majority",
        inputs=inputs,
        labels=labels,
        encode=_parity_encode,   # same row-0 bit-placement encoding
        decode=_parity_decode,   # same threshold decode
    )


TASK_REGISTRY = {
    "parity": make_parity_task,
    "majority": make_majority_task,
}


def build_task(cfg: CAConfig, seed: int) -> Task:
    if cfg.task not in TASK_REGISTRY:
        raise KeyError(f"Unknown task {cfg.task!r}; known: {list(TASK_REGISTRY)}")
    return TASK_REGISTRY[cfg.task](cfg, seed)


def score(predictions: np.ndarray, labels: np.ndarray) -> float:
    """Fraction correct — used as fitness for classification tasks."""
    return float((predictions == labels).mean())
