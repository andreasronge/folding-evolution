Implemented the blocking code-review fix in commit `2bab2c2`, on top of
`0faced8` and integration `4f1d432` (approved 0239 commit `37c78c1`). The revised
plan was written before any new tests or preparation. Scientific arms, data,
fitting, tolerances, hashes, seeds, operators, scoring, and roster are unchanged.
No Rust edits or rebuild were needed. No research/ files were committed on this
branch; task artifacts remain in the main checkout's task folder.

The runtime admission predicate now follows code_review.md exactly:
`elapsed <= 1800 and expected < 11700 and bound < 11700`, where
`expected = 1.15 * max(sample, batch_projection) + fitting + 120` and
`bound = all-capped (including scheduling tail) + fitting + 120`.
The expected price retains 15% safety; the zero-solve hard bound has no additional
multiplier. The original published conservative price formula and all measured
fields remain intact as diagnostics. preparation.json adds the two admission
prices and an explicit versioned admission_rule with formulas and safety scope.
This is the review-requested predicate change, explicitly documented in plan.md
and queue notes. The prior smoke/ measurements are preserved, including its
198.86 s preparation and 11,078.95 s published conservative price.

The minor review items are addressed: config.task is now `2026-10-09-0306`, and
the inherited data README documents the 195-minute timeout, 11,580 s deadline,
and revised admission rule. The frozen data folder and deterministic validation
seeds retain their historical names/values. The sibling preparation path assumes
one sequential queue invocation on the same run date, as reviewed; no cross-day
resume mechanism was added to this scoped implementation.

Targeted tests:
`.venv/bin/python -m pytest -q tests/test_position_matched.py tests/test_frequency_matched.py`
— **18 passed in 63.51 seconds**. New regression checks cover 1.9% and 6% timing
drift, independent expected/hard-bound/preparation refusals, inclusive preparation
and strict scoring boundaries. Inherited projection, decoder, pairing, complete
roster and inference tests also pass. Git diff whitespace checks passed.

Smoke command, on the clean commit with this worktree as cwd:

```sh
RUN_DIR=/Users/andreas/developer/folding-evolution/research/runs/2026-10-09-0306/smoke-review RAYON_NUM_THREADS=1 .venv/bin/python -m experiments.chem_tape.position_matched_run --prepare --workers 10 --deadline-seconds 1780
```

Exit code 0. Evidence: [config](smoke-review/config.json),
[validation](smoke-review/validation.json), [preparation](smoke-review/preparation.json),
[timing](smoke-review/timing.json), [search rows](smoke-review/search.jsonl), and
[variation](smoke-review/variation.json). C/T replays passed 32/32 and K passed
16/16, excluding only clock fields. All 16 Q/P projections and exhaustive lookup
checks passed. All 16 Q start rows equal C exactly. Projected table hashes and
all 32 Q/P timing search rows match the prior smoke deterministically; only
clocks differ. Source, roster and preparation schedule hashes remain unchanged.
Preparation implementation/binary hashes match the committed code.

Worst token errors: Q 0.0000384510, P 0.0000273016; worst positional TV:
Q 0.0001593589, P 0.0001608541. These pass the unchanged 0.001 token and
0.005 TV gates; support remains at least 250 counts/token.

Preparation wall time 197.02 s (3.28 min);
fitting/checking 49.40 s. Mean worker seconds/search:
Q 13.9652, P 17.3773.
Q timing solves 9/16 and P 6/16 on rotating cells, unpaired with C: preparation
observations only, neither full-roster solve forecasts nor efficacy evidence.

| Projection | Seconds | Minutes |
|---|---:|---:|
| Average-worker cost | 6,418.95 | 106.98 |
| Finite-batch wall | 7,731.84 | 128.86 |
| All capped, with scheduling tail | 9,341.84 | 155.70 |
| Published conservative diagnostic: 1.15 x max + fitting + 120 s | 10,912.52 | 181.88 |
| Admission expected: 1.15 x max(average, batch) + fitting + 120 s | 9,061.02 | 151.02 |
| Admission hard bound: all capped + fitting + 120 s | 9,511.24 | 158.52 |
| Approved scoring timeout | 11,700.00 | 195.00 |

The expected-runtime admission margin is 2638.98 s
(22.56% of timeout); the hard-bound margin is
2188.76 s (18.71%). The published conservative price is
unchanged in definition and remains recorded even though it no longer controls
admission. Both new prices were independently recomputed from preparation.json.
Expected queue wall time is about 110–132 minutes including preparation; this
is a small-sample forecast. The fixed 4,096-search queue has not been run and no
efficacy decision exists.

[queue.yaml](queue.yaml) has two sequential entries, timeout sum
1,800 + 11,700 = 13,500 s (3 h 45 min), below the four-hour strategy ceiling.
All IDs start with this task ID; commands use this worktree and outputs use
RUN_DIR. Scoring requires newly admitted preparation with matching code/binary,
source, map and roster hashes; older preparation is refused. The internal
scoring deadline remains 11,460 s, with 120 s reserved for reporting inside the
11,580 s command deadline and another 120 s before the outer timeout.

Queue validation (`scripts/run_queue.py --validate`) passed: two pending
sequential entries. Both commands pass /bin/sh syntax checks; task IDs, worktree
cwd and timeout sum pass. No driver_feedback.md was present. Review fixes are
ready for independent re-review; code_review.md itself has not been rewritten.
