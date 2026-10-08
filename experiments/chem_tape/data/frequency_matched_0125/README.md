# Frozen K replacement (0125)

`../then_addition_1548_frozen/` contains unchanged row F observations,
configuration, freeze, schedule, completion/validation and queue metadata
from clean commit `45b2bdb2cbe5dee7ef04c3b5ebc10c54ce3e233a`.
Its provenance SHA is independently pinned in `frequency_matched_run.py`;
all original file bytes, including decompressed search.jsonl, are checked.
The original C/T/K tables remain in `../comparison_gate_1246_frozen/`.
No targets, fits or source observations are regenerated.

`preparation.json` records the current-build 32-row bit-exact C/T replay,
16 fixed full-cap K timing rows at ten workers, marginal mismatch,
implementation/binary hashes and conservative runtime admission. The full
runner requires the exact prepared implementation/build; it also rechecks
all 16 timing rows deterministically when their seeds are run in the full
roster. Only clocks are excluded from deterministic equality. A different
build requires a new preparation run, even if its scientific outputs agree.

Reproduce with fresh output directories (from the repository root):

```sh
RUN_DIR=/absolute/preparation .venv/bin/python -m experiments.chem_tape.frequency_matched_run --prepare --workers 10 --deadline-seconds 1780
RUN_DIR=/absolute/full .venv/bin/python -m experiments.chem_tape.frequency_matched_run --preparation /absolute/preparation/preparation.json --workers 10 --deadline-seconds 8880
```

The approved full roster is exactly 2,048 K searches, paired to all original
C/T rows and their 64-case draws. All 16 corpora must finish for an efficacy
decision. An error or timeout preserves partial observations, writes an
incomplete report, and exits nonzero. The report's C/K ratio is cost_K/cost_C;
K/T is cost_T/cost_K. Corpus means weight all 16 cells and eight seeds equally.
Unsolved costs are 2*cap, with a 1*cap sensitivity. Both-solved summaries
condition on successful pairs, weight occupied cells equally within corpus,
and expose omitted cells via occupancy. Independent G4 sampling uncertainty
is not included in the descriptive K/G4 corpus interval.

The replacement control matches pooled finite-tape emitted frequencies while
retaining G4 dependencies. Its sufficiency decision is restricted to this
selected development bank and capped endpoint. It does not isolate token
order, identify active structure, or establish an executable-fragment benefit.
