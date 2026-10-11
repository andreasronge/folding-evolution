# Frozen 2044 signed-chain development probe

`manifest.json` records the performance-blind D625 `v2_x4` screen of all 24
`(p(a,b)+n(b,c))+p(c,d)` permutations. Its canonical JSON digest is
`e3873e170b71ffcb69bea99b0d2cf4afd7062a5b6ab28ef2a9e59608f6c6d175`.
The canonical expansions have 14 nodes / 20 compiled tokens. Recursive,
Python stack and production VM execution agree, including zero conditions;
24 helpers and 64 random trees also pass the existing executor checks.
The exhaustive <=9 executable-token screen examined 17,807 distinct outputs
and found no exact alias. Maximum short agreement is 335/625, old-bank
agreement 305/625, and pairwise agreement 335/625. Longer aliases are not ruled
out. All candidates survive; the four seen stage-0 cells plus the lowest-hash
remaining two are development, and the eighteen others remain protected.

`saved_1938.json.gz` is an immutable archive of the original 1938 preparation,
including all 2,304 source search rows, all 24 complete saved libraries, bank,
method freeze, schedules, seeds, preparation hashes and queue metadata. Its
SHA-256 is `2e6b84e2b1c74a39005eb17fa7b273bc2249bbbdec80ce62224d88b8059b81ca`.
The runner checks the archive and file hashes, original acquisition envelope,
exact solvers, original method hashes, and source-only library reconstruction.
R-all uses the unmodified `semantic` entries; it does not use the two 1938
stage-0 libraries. No source acquisition is rerun. Library build identities
are carried into the new method freeze. Existing engine/extractor files and
Rust are unchanged.

`presearch.json.gz` records the method/schedule/seed freeze emitted by the
successful preparation before the first search smoke run; task-folder smoke
artifacts retain the preparation hash and raw searches. Preparation replays
bank admission and writes frozen parameters, schedules,
seeds, identities and libraries before any new search. New full seeds begin
20450000; smoke seeds begin 20460000, with eight disjoint seeds per paired
build/cell/repeat unit and explicit exclusion of 1938 and 2044 stage-0 seeds.
Only development cells can enter the search envelope. The full fixed probe
is 24 builds x 6 cells x 2 repeats x 3 arms = 864 jobs; smoke is two seen cells
x two saved builds x one repeat x three arms = 12 jobs. Both retain full
per-attempt limits and unchanged donor behavior. No protected scoring command
is implemented.

With this worktree's Python, `PYTHONPATH=.` and `RAYON_NUM_THREADS=1`, and a
fresh `$RUN_DIR` for each command:

- `python -m experiments.chem_tape.signed_chain_run prepare --workers 8`
- `python -m experiments.chem_tape.signed_chain_run development --prepared <prepare-dir> --workers 8`
- Add `--smoke` only to development for the small fixed fixture.

Every raw row retains attempts, evaluation/timing costs, rejection counters,
fitness and phenotype-diversity curves. Reports validate the exact grid,
charge failed jobs 524,288 evaluations, group by arm/cell/build, and emit
paired two-way bootstrap ratios, coverage strata, historical acquisition and
`A + N*S` curves. The historical worker cost was measured in 1938 and is only
approximately comparable to current worker cost. Plots show exact solving,
training fitness, phenotype diversity and library sizes. There is no folding
or bond distribution in this direct tree-GP experiment.

The confirmation price is conditional on the actual frozen protected roster.
Balanced crossed ANOVA estimates build, cell, interaction and residual/search
variances of the paired delta-method influence on the pooled arithmetic mean
ratio. Simulated normal sampling error yields illustrative intervals at
several effects around 0.80 for repeats 1, 2 and 4. Doubling all variance
components is a conservative sensitivity, not a validated upper bound. Small
six-cell/two-repeat development data and exchangeability assumptions can
make the forecast optimistic. Runtime uses measured effective concurrency,
plus 2x tails, scheduling/report overhead and a verification reserve.
Precision and affordability only recommend returning to strategy; neither
establishes a protected effect or authorizes confirmation.

The main-checkout task folder holds the plan, preparation/smoke evidence and
55-minute queue. No `research/` file belongs on this task branch.
