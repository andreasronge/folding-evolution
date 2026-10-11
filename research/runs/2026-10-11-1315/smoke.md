# Execution and feasibility smoke

Final smoke used the production engine and full eight-attempt restart cap, with
11 processes and RAYON_NUM_THREADS=1. Distinct smoke seeds were audited against
318,134 historical seeds. Raw outputs: [prepare](smoke-final-prepare/preparation.json),
[score report](smoke-final-score/report.json), [scoring rows](smoke-final-score/score.jsonl),
[screen log](smoke-bank/stdout.log) and [targeted tests](tests.log).

- Worktree extension path: `.venv/lib/python3.12/site-packages/_folding_rust/_folding_rust.cpython-312-darwin.so`.
  Binary SHA256: f64069e7fee52892014edf91064b98c2641775f0e1a6596d0eeec2763614507b.
  All 54 nonconstant canonical programs agree with independent labels through
  recursive interpreter, Python executor and production VM. Alias witnesses
  also agree with the independent screen machine.
- Complete nine-token screen: 106.23 seconds, 17,807 distinct outputs, all 24
  sources and 30 destinations admitted; zero exact/near aliases. Maximum old
  agreement 425/625. Split 24 sources, six development, 24 protected; zero
  protected searches, including the smoke.
- Acquisition: 48/48 solves, all first attempt; 121,344 evaluations, 2,528 mean
  and 2,304 median. Batch 1.20 wall seconds, 6.13 worker seconds. One uncapped
  library with 16 entries, including neg01; own-helper census 3/48, three-input
  sum census 42/48. These are execution observations, not a recommendation.
- Scoring: all 16 fixed jobs completed in 50.83 wall seconds and 432.60 worker
  seconds. Eleven jobs exhausted 524,288 evaluations each. Maximum worker time
  39.60 seconds, effective concurrency 8.51, throughput 0.315 jobs/s. Projection
  at observed mixture: 1,219.92 s (20.33 min) for 384 jobs. Conservative all-cap
  projection at observed maximum worker cost/effective concurrency: 1,786.83 s
  (29.78 min), within 2,370 s internal deadline and 2,400 s queue timeout.
- Full-budget smoke solves: R-tree 1/4, R-rect 3/4, R-all 0/4, R-order-all 1/4.
  Shared attempt seeds and distinct smoke/full domains are verified. Smoke
  intentionally has no investment recommendation. No protected or additional
  fresh development cells were searched.
- Thirty-six targeted tests pass: rectifier bank/seed schedules, reporting-only
  census isolation, fixed donor envelopes and protected refusal, complete-grid
  analysis, ratio-of-pooled-means paired build bootstrap, recommendation labels,
  source-only deterministic replay and tampered preparation/transport refusal;
  existing order, library and tree GP checks also pass. Dynamics PNG inspected.
- Queue parses through scripts/queue_lib.py: exactly two entries, required id
  prefix, 900 + 2,400 = 3,300 timeout seconds (55 min), full schedules contain
  384 acquisition and 384 score jobs. No full queue was executed by the researcher.

The initial smoke preceded a reporting-only refinement adding source cost fields
and removing duplicate literal timing from transported preparation economics;
smoke-final-* and the final test log verify the committed implementation.
The smoke preparation records the pre-commit HEAD; exact method, artifact and
binary hashes in its method freeze identify the tested contents. The full queue
will record the research branch's implementation commit in preparation.json.

Implementation commit: `4a60cc7dee19ed980bec75966af558ef90d7c379`. Post-commit canonical method-freeze digest equality verified; worktree clean.
