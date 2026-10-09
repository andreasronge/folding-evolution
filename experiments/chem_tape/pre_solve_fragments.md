# Pre-solve source assay (1350)

The new `pre_solve_run` reuses the reviewed 1036 search, exact C tables and
0843 block operator. Public E/W_E labels adapt to F/W at the operator boundary;
there is no new search randomness or changed ordinary variation. Preparation:

```sh
RUN_DIR=/absolute/fresh-preparation RAYON_NUM_THREADS=1 .venv/bin/python \
  -m experiments.chem_tape.pre_solve_run --prepare --workers 10 \
  --deadline-seconds 1680
```

`data/pre_solve_1350/provenance.json` pins the saved 1831 and 1036 source files
by SHA256, including their absolute archive locations. Missing/changed files
fail closed; raw multi-megabyte historical outputs are not copied into git.
The unchanged exact C fixture and whole F libraries have their existing SHA
gates. No canonicals or source-solver tapes enter the E extractor.

`pre_solve_sources` verifies all 2048 collection identities and all archive
checkpoint/first-solve metadata. Selection is the stable lowest S slot at each
checkpoint64/128/256, including ties in original archive order. It retains all
source attempts in the manifest, without using eventual success or accuracy for
selection. Selected tapes must remain non-exact on the full source domain,
with saved accuracy reproduced. Their explicit interface is `tape`, never
fabricated `solved`/`solver` fields.

The shared extractor preserves the old exact-source interface and old whole
library records. Partial extraction uses all-active3–6 windows, the fixed96
activity inputs (`default_rng(0)`), at least2 source cells and top32 after the
family training-cell NOP-pad exclusion. Ranking is descending cell count,
raw occurrence count, length, ascending tokens. Repeated positions/checkpoints
can increase rank. Distinct source searches are reported, not ranked. Activity
means output influence. Source-context traces use4 inputs, standalone traces96;
all agree with Rust. An empty E library is retained: E and W_E both draw chain
blocks with the historical whole-library length law, with fallback reported.
Then-addition padded hits are reported without filtering.

Preparation freezes both16/12-seed rosters and64 smoke rows before searches.
Smoke covers all16 target cells in both families and all16 corpora; no efficacy
result affects admission. Replays cover48 historical C/F/W rows, one per arm
and corpus. Any scientific mismatch demotes **all three** historical procedures
to unpaired references. It does not invalidate the newly paired E/W_E contrast.
Both F/W implementations receive10000 forced edit audits, including boundaries,
conditional allele preimages and decoded suffix preservation.

Admission uses the measured worker-seconds and smoke concurrency efficiency,
with15% margin. Try16 seeds (8192 new searches), then12 (6144); scoring must fit
135 minutes and handoff/reporting150, preparation30. Only these two sizes are
permitted. Ten processes and one Rayon thread per process are frozen.

Scoring:

```sh
RUN_DIR=/absolute/fresh-score RAYON_NUM_THREADS=1 .venv/bin/python \
  -m experiments.chem_tape.pre_solve_run \
  --preparation /absolute/fresh-preparation/preparation.json \
  --workers 10 --deadline-seconds 8880
```

Add `--validate-preparation` to check source/backend/code/bank/table/library/law/
roster/manifest hashes and replay all64 smoke scientific payloads, then stop.
Only the complete selected score roster enters efficacy; phase-tagged smoke
and historical replay rows stay separate in `search.jsonl`. Preparation and
scoring require fresh output directories.

`pre_solve_report` computes E/W_E=exp(mean16-corpus paired log(cost_W_E/cost_E)),
unsolved2cap,95% t15df. Harm precedes useful early source (lower>1,point>=1.10),
then no worthwhile increment (upper<1.10), then unresolved. Secondary E/F,E/C,
W_E/W require successful historical replay and complete seed-matched records;
all initial-token/case/table/budget metadata are checked. BE/PA, each cell,
1cap and both-solved sensitivities, solver-window occurrence and fitness/
diversity/edit plots are descriptive. Raw historical timing is descriptive.

Costs keep measured partial collection, extraction/verification, shared exact
C acquisition and historical replay separate. Arithmetic savings use consistent
worker-second/evaluation units. Geometric cost ratios are not repayment.
Resolution pricing assumes observed corpus spread persists, charges new
balanced partial and exact-C acquisition/fitting/extraction/scoring, targets
x1.05 and requires strategy review. The complete early-data stage remains an
unallocated6–9h planning scenario; its partial-decoder then-addition rate is
unmeasured. No inference isolates gate joins, joint content versus token supply,
modularity, solver-free acquisition, inheritance or fresh-bank transfer.
