# Frozen positional replacements (0239)

`K_*` preserves the complete 0125 K observations and configuration, metadata,
freeze, validation, progress and schedule from clean commit
`8e628310bba8f4cca6c473fb5c2102de3854df3a`. Search bytes are compressed with
gzip; the SHA in `K_provenance.json` names decompressed bytes. The provenance
file itself is pinned independently in `position_matched_run.py`.
The unchanged 1246 C/T/K tables and 1548 C/T/G4 observations remain in
`../comparison_gate_1246_frozen/` and `../then_addition_1548_frozen/`.

Q fitting uses fixed 400 iterations per body position, step 0.7, no multiplier
bounds, and existing normalize (floor 250, stable integer largest remainder)
inside every iteration. The actual quantized Q marginal is propagated onward.
Q's start row is C's exact start row; unused body rows at position zero use
normalized G4. P normalizes each C positional marginal, duplicated across all
previous-token rows. Marginal gates are maximum token error <=0.001 and total
variation <=0.005 at every position, for both arms. The implementation publishes
all positional errors, support counts, actual marginals and table hashes.
These externally fitted maps are frozen before any target scoring.

The narrow extension supplies a decoder factory to the unchanged search loop.
The original Decoder remains the default. Positional decoding uses cumulative
lookups indexed by position and previous token (Q), or by position alone (P).
Repeated K copies retain K's canonical map hash but execute the actual positional
lookup. This permits comparison of every deterministic search field against
historical K, excluding only clocks. No inverse encoder is introduced.

Reproduce with fresh output directories, ten workers, and the current worktree
venv (Rust has not changed):

```sh
RUN_DIR=/absolute/preparation RAYON_NUM_THREADS=1 .venv/bin/python -m experiments.chem_tape.position_matched_run --prepare --workers 10 --deadline-seconds 1780
RUN_DIR=/absolute/full RAYON_NUM_THREADS=1 .venv/bin/python -m experiments.chem_tape.position_matched_run --preparation /absolute/preparation/preparation.json --workers 10 --deadline-seconds 10680
```

Preparation requires 32 bit-exact C/T replays, 16 bit-exact positional-K
replays, exhaustive lookup checks, and 32 fixed full-cap Q/P timing searches
(one per arm/corpus, rotating across all 16 target cells). Full execution
requires admitted preparation with matching implementation/binary hashes,
source provenance, roster and projected map hashes. Timed rows replay in the
4,096-search full roster. Admission prices observed average cost, finite-batch
wall time, all-capped tails and lookup/fit overhead, with 15% safety and 120 s
reporting reserve, against the approved three-hour scoring timeout.

No incomplete roster can give an efficacy decision. C/Q is cost_Q/cost_C;
C/P is cost_P/cost_C, Q/K is cost_K/cost_Q, and Q/P is cost_P/cost_Q. Corpus
means weight 16 cells and eight seeds equally. Primary unsolved cost is 2*cap,
with 1*cap and both-solved sensitivities. C/P is always interpreted alongside
C/Q; a Q failure does not rule out independent positional P. Uniform-tape
mutation and crossover diagnostics use an independent fixed seed and are
never used to tune the projections. Supply versus variation, learning and
transfer beyond this development bank remain unresolved by this design.

The saved `preparation.json` is **not admitted**: conservative complete scoring
price is 10,869.70 s, above the approved 10,800 s. All scientific intervention
and historical replay gates passed; no full queue was issued. It preserves the
measurements and exact implementation/binary hashes for reviewer inspection;
the full runner correctly refuses this preparation. See the task's infeasible.md
in the research checkout for the steward's priced timeout alternative.
