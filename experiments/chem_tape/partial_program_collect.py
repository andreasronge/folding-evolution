"""Pre-solution checkpoint archive; instrumentation never consumes search randomness."""

import hashlib
import time

import numpy as np

from experiments.chem_tape.composition_search import outputs, search

CHECKPOINTS = (64, 128, 256)


class Collector:
    def __init__(self, seed, checkpoints=CHECKPOINTS):
        self.rng = np.random.default_rng([seed, 1831])
        self.checkpoints = checkpoints
        self.rows = []

    def __call__(self, generation, programs, correct, parents, terminal):
        if generation not in self.checkpoints:
            return
        population_hash = hashlib.sha256(programs.tobytes()).hexdigest()
        for kind, candidates in (
            ("S", parents.ravel()),
            ("P", np.arange(len(programs))),
        ):
            slots = self.rng.integers(len(candidates), size=8)
            for slot in slots:
                index = int(candidates[slot])
                self.rows.append(
                    dict(
                        kind=kind,
                        checkpoint=generation,
                        evaluations=generation * len(programs),
                        terminal=terminal,
                        slot=int(slot),
                        population_index=index,
                        population_hash=population_hash,
                        tape=programs[index].tolist(),
                        training_correct=int(correct[index].sum()),
                    )
                )


def collect_search(envelope):
    job, meta = envelope
    collector = Collector(job[3])
    tick = time.monotonic()
    result = search(job, collector=collector)
    archive = collector.rows
    verify = time.monotonic()
    if archive:
        accuracy = (
            outputs([r["tape"] for r in archive], job[6], job[7])
            == np.asarray(job[0]["labels"])
        ).sum(1)
        for row, correct in zip(archive, accuracy):
            if correct == len(job[6]):
                raise ValueError("exact tape entered pre-solution archive")
            if result["solved"] and row["evaluations"] >= result["evaluations"]:
                raise ValueError("archive from solve generation or descendants")
            row.update(
                cell=result["cell"],
                source_seed=result["seed"],
                d1331_correct=int(correct),
                exact=False,
                source_later_solved=result["solved"],
            )
    result.update(
        meta,
        archive=archive,
        archive_verification_seconds=time.monotonic() - verify,
        worker_seconds=time.monotonic() - tick,
    )
    return result
