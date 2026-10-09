# Frozen whole-library reuse (1036)

Run preparation with a fresh `RUN_DIR`:

```sh
RUN_DIR=/absolute/preparation RAYON_NUM_THREADS=1 .venv/bin/python \
  -m experiments.chem_tape.fragment_reuse_run --prepare --workers 10 \
  --deadline-seconds 1680
```

This freezes both permitted score rosters and the 96-search non-scoring timing
roster before any searches. It reconstructs the original 16 whole libraries,
checks them against the saved 0843 records, performs 20,000 edit-invariance
checks, replays 16 historical 1548 C searches with the operator off, and records
full-domain NOP-padded target hits without filtering. Preparation must finish
within 30 minutes. Only the measured worker-time projection (with 15% margin)
selects 16 or 12 primary seeds, retaining all eight reference seeds; neither
candidate fitting 195 minutes fails admission.

Scoring with `--preparation /absolute/preparation/preparation.json` validates
bank/source/table/library/code/backend/roster hashes, then replays all 96 smoke
scientific payloads before executing the complete selected score roster.
`--validate-preparation` stops after this handoff check, without efficacy
searches. Ten workers and `RAYON_NUM_THREADS=1` are the approved configuration.
A missing, duplicated or changed row prevents the efficacy report.

Then-addition is primary (4096 searches/arm at16 seeds or3072 at12); eight
comparison-gate holdouts are a separate reference (1024 searches/arm).
C/F/W share initial populations/cases and ordinary variation streams.
The reviewed `BlockOperator` supplies F/W with probability .2 on non-elite
children after ordinary variation. F samples a whole-corpus fragment uniformly;
W draws C's chain conditioned on the preceding token. Their empirical length,
uniform valid start, and suffix-repair laws match. `operator_laws.json` saves
the library-derived length counts/probabilities: W stores no token repertoire,
but does retain information derived from the library.

The report applies the approved harm/acquisition-review/small-increment/
unresolved rules to primary F/W and F/C, using 16 equally weighted source
corpora and 95% t intervals (15 df). It keeps holdout, family, cell, one-cap,
both-solved, edit/default, solver-window occurrence and timing descriptives
separate. Plots show cost, observed fitness/diversity, edits and solves for
both banks. Arithmetic consumed-evaluation savings and worker-time savings
against C **and W** are separate from geometric endpoint speed; measured
extraction worker-seconds are repaid only against positive arithmetic
worker-second savings. Corpus collection costs are separately reported.

Resolution pricing targets a ×1.05 half-width conditional on unchanged corpus
spread and charges new balanced source collection, frozen C fitting, library
reconstruction, scoring, reporting and agent work. It is a scenario for
strategy review, never authorization for another run.

Both banks are development data. Whole libraries use four source cells versus
three for 0843's LOO evaluation, so these differences cannot cleanly estimate
shape attenuation. This tests externally extracted literal blocks, without B;
a win does not isolate dependencies from token supply or establish modularity,
acquisition, or fresh-bank transfer. Library presence in solvers is occurrence,
not causal ancestry. W/C plus a tight small F/W bound can favor W; a broad
F/W interval does not establish a block-mechanics explanation.
