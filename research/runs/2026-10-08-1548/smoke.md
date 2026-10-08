# Preparation smoke checks

Final implementation commit: `45b2bdb2cbe5dee7ef04c3b5ebc10c54ce3e233a`. Worktree clean after commit;
no research/ paths are in that commit.

The final training-only smoke completed 48 searches in 88.8 seconds,
with frozen BE1/PA1 tables and the eight v1 training cells only. At cap 524288,
mean worker seconds/search were C 4.86, T 8.53, G4 15.88.
Observed training smoke solves: C 14/16, T 13/16, G4 9/16.
These observations validate infrastructure and throughput; they are not target-row
results or an efficacy decision.

All 48 scientific rows match the initial smoke exactly after excluding timing fields
(and metadata excluded by the established replay helper). Source/binary hashes in
config match the committed implementation. All original source hashes, all 48 frozen
table hashes, both target schedule hashes and the fresh semantic bank SHA validate.
The 16 C/T case-pairing checks pass. See [replay_check.json](replay_check.json),
[validation.json](smoke_final/validation.json), [timing.json](smoke_final/timing.json),
and [diagnostics.png](smoke_final/diagnostics.png).

A forced one-second work deadline produced zero complete pairs, explicit timeout,
zero target searches, and no efficacy eligibility, with all expected checkpoint and
report artifacts saved. An injected validation error exited 1, saved failed
validation/error provenance, and provided no efficacy fallback. These checks use
training smoke mode; no protected target searches were performed.

Thirteen focused tests pass (`tests/test_then_addition.py` and
`tests/test_comparison_gate.py`); Ruff checks/formatting and diff whitespace checks
pass. The diagnostic charts were visually inspected. Queue validation confirms
two 4352-search rows, valid run IDs, this worktree as cwd, output under RUN_DIR,
and 27000 total timeout seconds (7.5 hours). No full queue was executed.

The final bank contains all 16 approved behaviours. Its retained alias audit explains
why repeated-reducer counts depend on representative convention (see plan.md and
`then_addition_1548_bank.README.md`); no cell was replaced or chosen by search performance.
