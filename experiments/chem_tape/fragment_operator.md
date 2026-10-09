# Learned literal block edits (0843)

`fragment_run.py --prepare` loads the SHA-pinned 1246 corpus, builds 64
leave-one-training-cell-out libraries and 16 whole-corpus libraries, checks
30,000 block edits, verifies frozen C by reconstruction and historical replay,
and runs 128 non-scoring timing searches over both families and all corpora.
It selects the largest admitted 32/24/16-seed roster while retaining every arm,
corpus and cell. Preparation below the library floor or above the runtime
allocation stops with its measured artifacts; it does not resize the method.

`fragment_run.py --preparation PATH` checks source, table, code/backend,
library and roster hashes, replays all smoke scientific payloads, then scores
the frozen complete roster. `--validate-preparation` performs only that
handoff/replay check and exits. Use a fresh `RUN_DIR` for each invocation and
`RAYON_NUM_THREADS=1`; ten process workers are the priced configuration.

All ordinary search draws and elite handling remain in `composition_search`.
Its optional `child_transform` runs only on the non-elite offspring after
ordinary variation. F/B/W use a separate RNG and edit probability .2. F draws
an intact library fragment uniformly. B independently samples the library's
position marginals conditional on length. W samples the C token chain given
the previous token. The window plus its next allele is encoded with uniform
conditional preimages; the decoded suffix, including the tape end, is kept.
The 10k-per-arm audit covers every corpus/cell and interior/start/end positions.

The library's activity mask is source-program NOP knockout contribution on
96 fixed inputs. Padded-fragment exclusion and saved solver verification use
the full domain. Provenance records every contributing source seed/cell/start.
Standalone stack deltas are measured from an empty stack on those 96 inputs;
source-context stack/default statistics use their first four. Default-use
counts are underflow plus wrong-type safe-pop events, including DUP/SWAP's
inline underflow defaults. They do not count ordinary zero outputs or
constant instructions. Full offspring diagnostics sample the first non-elite
child every 32 generations on four fixed inputs, for all arms; they consume
no search or operator random draws. These are descriptive samples.

`search.jsonl` contains phase-tagged replay, smoke, and training rows. Only
`phase=training` fresh-scoring rows are supplied to the efficacy report (the
historical replay rows exist only in preparation). Never pool preparation or
scoring smoke rows into efficacy. `result.json` requires the exact full
schedule and exposes corpus contrasts, approved rule precedence, one-cap and
both-solved sensitivities, family contrasts, edit diagnostics, and complete
continuation cost scenarios. `diagnostics.png` shows sorted costs, observed
fitness/diversity (conditioned on searches still running), edit histograms and
solve fractions. Library occurrence in solvers does not measure causal use.

Reuse pricing is explicitly an extrapolation from training difficulty, with
whole-library build, validation/reporting and agent work included. Resolution
pricing assumes observed corpus SD persists in new independent balanced
corpora, and charges source collection, fitting, extraction and scoring.
Neither price authorizes continuation. A gain is scoped to this externally
fitted literal-block procedure on development banks.
