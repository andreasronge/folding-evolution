# Frozen references for uniform compatible donor labels (0652)

Deterministic gzip snapshots preserve the admitted 0524 libraries, preparation,
seed audit, six fixed R-perm search jobs (first cell/repeat per predicate split
for builds 0 and 23), and B/C worker rates from 0524 and 0348. The provenance
records decompressed SHA256 hashes, source directory and reviewed 0524 method
hashes at `7c0e5df`. Replay jobs are validation exceptions, never scoring data.
The gate-sum bank, source cohort (including failures), original R-size controls
and 0524 permutations are unchanged. All 72 R-perm constructions are rebuilt
and compared with the archived content; 72 R-unif constructions are seeded
independently and validated on D625 without filtering or deduplication.

```sh
RUN_DIR=/path/to/fresh/prepare RAYON_NUM_THREADS=1 .venv/bin/python -m experiments.chem_tape.tree_uniform_run --prepare --workers 10 --deadline-seconds 2400
RUN_DIR=/path/to/fresh/score RAYON_NUM_THREADS=1 .venv/bin/python -m experiments.chem_tape.tree_uniform_run --workers 10 --preparation /path/to/fresh/prepare --deadline-seconds 7200
```

`--prepare --smoke` calibrates 36 full-budget R-unif jobs on fixed builds
0/11/23, four existing development cells and all three realizations, in a
disjoint namespace. Smoke preparation always has `admitted=false`. Production
preparation calibrates all 288 development jobs, measures solves and tails,
replays six saved 0524 jobs and freezes the admitted scoring schedule.

Scoring is 24 builds x twelve B/C cells x six repeats x five contemporaneous
arms (8,640 jobs). The ordered runtime fallback drops descriptive R-size first
(6,912 jobs), then reduces the four remaining arms to four repeats (4,608 jobs),
or exits infeasible if the 100-minute projection still fails. Projection uses
archived B/C rates with upward replay host adjustment, measured uniform rate
with R-tree floor, measured concurrency capped at ten, 30% reserve and 90s.

Uniform classes are ADD/GT, IF_GT, X0/X1/X2/X3/ANY, and 0/1/2/5. Entry order,
count, ordered arity/width skeletons and sizes are fixed; both frequencies and
finite-library dependencies differ from R-perm. The seed rule is SHA256 of
canonical JSON `[task, domain, parts...]`, first eight bytes big-endian masked
to 63 bits, separate from 0524's historical rule. Seeds, library hashes,
method implementations, replay and production calibration are independently
revalidated before scoring. All arms share each job's eight search seeds.

Realization is always repeat modulo three. Mean capped cost and reliability
first average searches within each realization, then weight all three
realizations, cells and builds equally. Thus four repeats give 2/1/1 searches
without overweighting realization zero. The paired bootstrap resamples builds
and nested realization blocks, keeping all associated reference rows together.
Raw solve/operator totals are explicitly descriptive. The report includes
primary R-unif/R-perm, separate R-unif/R-lib retention and reliability checks,
R-tree validity guards, split/cell costs, realization spread, motif/behaviour
and label audits, insertion/rejection rates, and conditional precision prices.
R-unif is charged the proposal's 2.88M-evaluation acquisition budget per build;
actual archived source evaluations remain logged. Source worker time includes
failures, extraction and original verification, plus measured construction time.

This is an ingredient replacement on a development bank, conditional on
inherited shapes and widths. It implements no PIPE learning loop, isolates no
single label mechanism and establishes no new transfer or no-learning claim.
The plan and queue live in the main checkout's research/runs/2026-10-11-0652;
no research files belong in this worktree commit.
