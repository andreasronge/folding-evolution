# Frozen Q source and context-specific recoding (0537)

Q/P tables, all 4,096 historical observations, roster, freeze, configuration,
validation, progress and runner metadata are preserved from the completed
0306 run at clean commit `2bab2c29db138dac4ef92f76d80707f5fe84f7e6`.
`provenance.json` names original artifacts and hashes of **uncompressed**
bytes. Search, projected tables and validation use gzip with mtime zero.
The provenance file itself is independently pinned in `recoded_smoke.py`.
C tables and historical rows remain in the existing 1246/1548 snapshots.

The actual Q allele range is 24,000. The proposal's 23,000 is a count typo;
frozen f=0.30 means exactly 7,200 entries per body/context row. Construction
uses `[537, corpus_index, integer_dose, k]`, with indices BE1=0, PA1=1,
BE2=2, PA2=3, through PA8=15. Position zero and context 24 are unchanged.
`lookup_new[a] = lookup_Q[permutation[a]]`; the inverse maps original Q
alleles to the new representation once at initialization, using original
Q previous-token contexts. Exact row counts preserve every complete tape's
uniform-prior probability. Realizations are fixed: sorted seed indices 0–3
in each corpus/cell use k=0, and 4–7 use k=1. No realization selection.

The optional search initialization hook does not consume search randomness.
Original case, initialization, selection and variation streams and exact
verification remain unchanged. Jobs are sorted by map for cache reuse;
process scheduling does not affect a search's RNG. Hashes name actual lookup,
permutation and inverse arrays, not just unchanged cumulative probabilities.

1246 saved no C solution tapes: 1,024 C searches include 936 solves, whereas
its 1,808 saved tapes were G4 collection solvers. Preparation deterministically
replays exactly the 936 solved C rows to recover their solutions, verifies all
non-clock search fields and D1331 outputs, then audits those C-derived tapes.
This adds no scientific seeds, collection, fitting or tuning. Recovery must
fit the same 1,800-second preparation timeout. Recovered rows are sorted by
historical key before audits so timing order cannot affect the diagnostic RNG.

Reproduce with fresh output directories and ten workers:

```sh
RUN_DIR=/absolute/preparation RAYON_NUM_THREADS=1 .venv/bin/python -m experiments.chem_tape.recoded_run --prepare --workers 10 --deadline-seconds 1780
RUN_DIR=/absolute/full RAYON_NUM_THREADS=1 .venv/bin/python -m experiments.chem_tape.recoded_run --preparation /absolute/preparation/preparation.json --workers 10 --deadline-seconds 11880
```

The cheap one-corpus smoke is `python -m experiments.chem_tape.recoded_smoke`
with RUN_DIR set. It replays one Q/C row, validates identity/R30/R100 arrays,
checks initial hashes and conditional encoding and runs short searches. Its
encoder check uses explicitly labeled G4 tapes, not a C audit substitute.

Full preparation validates all 64 fixed recodings, all 4,096 initial token
hashes, sixteen Q and sixteen C historical replays, and 64 fixed full-cap
timing searches covering both doses and realizations in every corpus.
Identity-Q replays execute the recoded decoder and inverse-initialization
hook with dose zero, retaining every historical non-clock field. Scoring reconstructs and hashes every
map, requires admitted preparation with matching implementation/backend and
source/roster hashes, and replays the timing rows deterministically. Exactly
4,096 new searches are scored. No partial roster gives an efficacy decision.

Setup, audits and memory construction are timed. Runtime admission requires
preparation <=1,800 s, expected work `1.15*max(sample,batch)+setup+120 < 11760`,
and a separate zero-solve bound `all_capped+setup+120 < 11760`. All-capped work
includes a capped scheduling tail, without another safety multiplier. The
scoring outer timeout is 12,000 s, with a 11880 s internal deadline and 120 s
reporting reserve. No unseen solve-rate assumption is needed for admission.

Uniform and recovered-C-tape audits report single resampling, Bernoulli .03,
crossover and the complete crossover-then-mutation offspring operator,
including changed-count and bounding-span histograms. Saved C token tapes
receive conditionally uniform preimage alleles under each map; the same
conditional RNG couples Q/recoded aliases. Audit parent choices are uniform
within the supplied population, not a simulation of lexicase selection.

Ratios are explicit: G=cost_Q/cost_R30, H=cost_R30/cost_C, and
G100=cost_Q/cost_R100. Corpus intervals have 15 df, with equally weighted
cells/seeds and nested realization diagnostics. Failures cost 2*cap;
1*cap and both-solved sensitivities are reported. G's lower bound >=1.20
establishes useful gain for this recoding; upper bound <=1.20 bounds a useful
gain; otherwise it is unresolved. H upper bound <=1.50 approaches C. Gap
share log(G)/log(cost_Q/cost_C) is descriptive arithmetic. Width, correlations
and crossover all change; no causal partition, acquisition or transfer claim.
