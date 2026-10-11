Implementation validation only; no protected efficacy outcomes were collected.

- 14 targeted pytest cases passed in 4.18 s, covering the 1228/default-engine
  replay, uncapped extraction/provenance boundaries, fixed protected roster,
  seed pairing, pooled whole-build bootstrap, threshold precedence and
  reliability, exact-grid/cap rejection, partial-block exclusion, repeat
  barriers and per-row fsync.
- Ruff and git diff whitespace checks passed. Queue parser accepted both
  entries; timeouts sum to 6,900 s (115 min), below the two-hour allocation.
- Preparation completed in 29.29 s: reconstructed and verified all 24 saved
  libraries (25–37 entries each), immutable saved library hash
  375c7b69544131cbea5683fd77bcc13e6299353ed6394eba4c90f17f759010d5,
  and the bank/source/method/seed artifacts. All seed audits admitted.
- Development smoke: 36 jobs, 12 per arm; all 36 solved at unchanged caps.
  Batch wall time 21.11 s. Mean worker-s/job: R-tree 2.63, R-all 2.63,
  R-order 0.272. At 1,152 units and the historical 9.7 effective workers,
  these rates project about 11 min; protected runtime remains unmeasured.
  Even extrapolating the small smoke's barrier/tail wall time directly gives
  about 34 min. The 90-min score allowance remains credible. This tiny
  development smoke is a correctness/timing check, not an efficacy verdict
  and never selects a library or changes the approved design.
- Separate score --smoke loaded preparation, rechecked/rebuilt its provenance,
  completed both barriers and scored the same 36 development jobs in 21.21 s;
  costs reproduced exactly. Both phases recorded zero protected searches.
- Deleting a top-level saved library entry was rejected by load_prepared as
  a provenance mismatch; restored the original artifact afterward.
- Mean historical cost across all 24 builds: 214,186.67 evaluations and
  13.2816 worker-s including extraction/census/validation. These exact saved
  costs, retaining failures, are used for economics; reconstruction timings
  are reported separately.

Smoke raw outputs and plots are in the worktree's ignored
experiments/output/2026-10-11/2026-10-11-1530-smoke/{prepare,score}/.
They were moved from this task's temporary smoke directory after validation;
queue preparation will generate a new method freeze on the committed code.
The full protected run is queued, not executed by the researcher.

Timeout handling: internal scoring stops submission/work 30 seconds before
its phase deadline, then reports all two repeats, a complete repeat-zero
fallback, or incomplete/no efficacy verdict. An external termination still
leaves fsynced score.jsonl and score_completion.json markers. For recovery,
read complete JSONL rows and call order_protected_run.summarize(rows, libs,
bank): it validates exact row keys/seeds/caps/solvers and selects only the
full grid or complete repeat zero. No partial repeat-one rows enter inference.
A malformed trailing row after external termination is not a completed row;
verify the complete first block against the saved schedules and marker before
using the fallback. The fallback has 576 units, allowance 6, and its own
whole-build interval, with no assumed two-repeat precision.

Implementation commit: 53f0e06 on research/2026-10-11-1530. Only the new
runner and its tests are committed; no research/ files were committed on the
task branch. Git status is clean. The development dynamics plot was visually
inspected; all four panels and legends are readable.
