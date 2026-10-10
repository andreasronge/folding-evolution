Implemented the approved design in `experiments/chem_tape/source_replication_run.py`
and `source_replication_report.py`, reusing the reviewed search executor, batch
scheduler, fitting/extraction, F operator, two-sum schedules and shared-baseline
bootstrap. The explicit replacement loader validates the frozen complementary
split while retaining the original training-only loader. The six-field legacy
build interface and extraction default retain exact historical behavior.

The plan was written before any experiment or test execution. All critique notes
are addressed in plan.md; notes 7–8 are left for the steward because the
researcher may not edit digest/question files.

Verification:

- 68 targeted tests passed across source replication, small-source, sparse
  feedback, two-sum, fragment operators/reuse, partial extraction and corpus fits.
- Exact old-default replay of 2033 `BE1|0|A8`: decoder, library, source membership,
  attempt order/hashes, yields and empty cells match the archived artifact.
- Full-cap two-build [smoke](smoke/smoke.json): 96 collection attempts, four final
  artifacts, 16 disjoint timing-cell target searches, 153.7 seconds overall.
  G4 first/static means 10.60/10.39 worker-s; adaptive 1.80 worker-s. Source solve
  counts 25/32 first, 22/32 static, 32/32 adaptive are descriptive only.
- Empty-library fallback audit and 10,000 suffix-edit audit passed. Tests also
  demonstrate explicit-roster recurrence, padded-full-solver exclusion and
  leave-one-cell-out membership, plus membership rejection and empty-cell fallback.
- [Scientific replay](smoke_validation.json) of all 16 smoke timing rows passed;
  scoring refuses the unadmitted smoke preparation before launching confirmation.
- Ruff checks and `git diff --check` passed. Queue parser validation passed for
  both entries; total timeout 9,600 seconds, expected wall-clock 125 minutes.

The small timing batch's conservative projection is about 110 minutes scoring
for both arms, plus replay/report reserves (~115 total). This fits the approved
120-minute scoring timeout; the full prepare still decides admission from its
32 reserved-cell searches and the actual 07:12:10+02:00 finish deadline. Neither
smoke solve rates nor scores select arms or sizes. No full confirmation was run
by the researcher. If full preparation cannot admit both arms, it keeps all
16 A8 builds at four seeds and drops S8 only; if that cannot fit, it fails with
a cost-obstacle artifact and the scorer refuses the handoff.

`queue.yaml` is in this task folder, with commands rooted in the worktree and
all full-run outputs under RUN_DIR. No research-tree files are committed on
the task branch. The compressed historical reference snapshot has fixed byte
hashes and provenance, and is never used to seed new acquisitions.

Implementation commit: `b6d1974` on `research/2026-10-10-0145`. Final git status
is clean; the commit contains no `research/` paths. After the final metadata
clarification, all nine source-replication tests passed again.
