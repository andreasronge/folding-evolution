# Then-addition-v1 and frozen comparison-gate fits (1548)

`then_addition_1548_bank.json` is pinned by SHA-256 in `then_addition_bank.py`.
Reproduce the deterministic, performance-blind semantic audit with:

```sh
RUN_DIR=/absolute/empty/output RAYON_NUM_THREADS=1 .venv/bin/python -m experiments.chem_tape.then_addition_bank
```

D1331 contains all 1331 length-three lists in [-5,5]^3. All 240 canonical
`A>B ? C+D : E` assignments have the same 13-token inventory. Every canonical
is checked in both Python and Rust. Of 162 nonconstant-gate assignments, 86
distinct behaviours remain after selecting the lexicographically first ID
per behaviour. The exhaustive typed-stack screen through nine executable tokens
retains 37 with agreement below 80% against every shorter behaviour. Of these,
16 agree with every one of v1's 220 distinct nonconstant behaviours on fewer
than 80% of inputs. No selected cell is an exact alias of the 1603 bank.
This proves only the stated nine-token screen, not 13-token minimality.

The artifact retains every raw assignment and its behaviour hash, constants,
alias IDs, screen witnesses/agreement, v1 closest IDs/agreement, exclusion
reasons, canonical checks and final IDs. Timing is separate so repeated builds
produce the same bank bytes. Two retained behaviours have aliases spanning
repeated-reducer inventories: `F>m?M+S:F` equals `F>m?M+S:m`, and
`M>F?S+m:F` equals `M>F?S+m:M` on D1331. The original probe's S/M/m/F
enumeration-order representatives yield S3/M5/m4/F4, while lexicographic
representatives yield S3/M4/m3/F6. Both counts and the alias reducer sets are
recorded; the selected 16 behaviours are identical under either convention.

`comparison_gate_1246_frozen/` vendors the source run's original config,
corpora, freeze, full schedule and compressed search log. `provenance.json`
is independently pinned in `then_addition_run.py`; every decompressed input
and all 48 table hashes (including unscored K) are checked before scoring.
The source commit/output path and original file hashes are recorded there.
No source data is refitted, and no canonical/witness enters any search job.

Run the approved rows with a fresh RUN_DIR each:

```sh
RUN_DIR=/absolute/fresh/F .venv/bin/python -m experiments.chem_tape.then_addition_run --row F --workers 10 --deadline-seconds 14280
RUN_DIR=/absolute/fresh/D .venv/bin/python -m experiments.chem_tape.then_addition_run --row D --workers 10 --deadline-seconds 12480
```

Both full target rosters and their bank/table/method hashes are frozen before
any search in either invocation. F uses new phase-6/7 seeds and a 10000 corpus
stride, because the old 2000 stride collides at 16 cells. D copies the source
holdout roster exactly. All source/target/smoke seed blocks are disjoint;
only same-corpus/cell C/T share a seed. `--smoke` always selects v1 training
cells, frozen BE1/PA1 tables and separate seeds, regardless of `--row`.

G4 runs first, followed by fixed BE1/PA1 through BE8/PA8 pairs. Search rows
are flushed as they finish and progress is checkpointed by block. Reporting
uses only complete initial balanced pairs, requires at least six, and refuses
an efficacy fallback after an error. Two minutes are reserved inside each
internal deadline; queue commands leave two further minutes before timeout.
Unsolved endpoint costs use 2*cap (1*cap sensitivity), and the independent
unit for the 95% t interval is the corpus. Both arms below 25% solve rate
force a capped-endpoint interpretation. D is development-bank generalization;
F conditions on this deliberately selected then-addition bank. C/T compares
fitting procedures and does not isolate token order or the cause of a boundary.
