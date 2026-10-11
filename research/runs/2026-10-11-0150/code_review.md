---
verdict: pass
---
# Code review: frozen source-subtree donors (0150)

Reviewed `git diff 8b18eb1..d7ec100` (donor hook in `tree_gp_search.search`,
`tree_library.py`, `tree_library_run.py`, `tree_library_report.py`, fixtures,
tests), [proposal.md](proposal.md), [plan.md](plan.md), [queue.yaml](queue.yaml),
[critique.md](critique.md) and the stage-only evidence in `smoke-stage/`.
Independently re-ran the four relevant test files (36 passed, 24 s) and
recomputed the schedule sizes and the coverage split from the frozen bank.

## Blocking issues

None.

## What was checked and holds

1. **Arm wiring.** `envelope()` gives R-tree no donors, R-lib the learned
   `entries`, R-size the `controls` of the same acquisition `build`;
   libraries are indexed by build 0..23 (stage: `build = r % 2` over two
   stage libraries). The off path (`donor_library=None`) is byte-identical to
   0024: eight saved 0024 jobs replayed on all deterministic fields
   (`smoke-stage/replay.json`).
2. **Pairing and RNG.** All three arms share eight attempt seeds per
   (cell, build, repeat); the audit verifies this and reports zero overlaps
   with the 191,682-seed historical snapshot plus reconstructed old
   schedules. R-lib and R-size consume the variation RNG identically (one
   `random()` then either `integers(len)` or an ordinary draw; same library
   length), so until the first oversize divergence the two arms differ only
   in donor content. An empty library makes no extra RNG draw (tested).
3. **Source-only extraction.** `extract` raises on any row that is not an
   R-tree job on a source cell, so target or saved solvers cannot enter.
   Proper subtrees only (`range(1, …)`), 3–9 nodes, must contain X0–X3,
   recurrence once per solver, ≥ 2 cells, cap 16, most common literal form.
   Scoring rebuilds every library from `acquisition.jsonl` and every control
   from its recorded seed and refuses on mismatch.
4. **Metrics.** Grid check enforces the full 24×8×8×3 cube and seed pairing;
   failures cost 524,288 via the unchanged restart accounting; per-build
   means give cells equal weight; block bootstrap resamples the 24
   acquisitions for both contrasts, solve differences, per-cell, covered /
   uncovered and economics. `classify` implements the plan's six-row
   precedence exactly (tested on the [0.86, 0.89] overlap case, resolved
   control loss, reliability guard).
5. **Gates.** Preparation refuses projected scoring > 9,000 s or
   preparation > 2,700 s; scoring refuses non-admitted, smoke, stage-only or
   hash-changed preparation. The stage measured 100 min projected scoring
   (threshold 150) and 23 min preparation (threshold 45) with every per-arm
   mean floored at 8.9 s and a 30 % reserve, so the gate is conservative
   rather than fragile: the scoring gate fails only if stage-0 effective
   concurrency drops below about 6.0 (measured 9.0). No pilot resampling is
   involved and I see no way for it to stop the main stage for a reason that
   would not also predict a real timeout.
6. **Queue.** Two sequential entries, 2,700 + 9,000 s = 195 min; the
   `$RUN_DIR/../…-prepare` path is the pattern 0024 used; `expect_outputs`
   match what each phase writes; `RAYON_NUM_THREADS=1` and ten workers are
   enforced by the CLI.
7. **Critique.** Points 1–5 are addressed in code (concrete stage gate with
   per-cell source solves and costs, support enumeration and bounded draws
   that fail rather than substitute, resolution prices for both contrasts,
   corrected labels with explicit precedence and a resolved-loss row,
   measured repayment with unbounded intervals, no top-up). Points 6–9 are
   digest/question wording outside the researcher's write scope; plan.md says
   so and defers them to the steward, which is a valid answer. The steward
   should pick them up in decision.md.
8. **Plan correction verified.** The proposal's 5/3 covered split was wrong;
   the frozen bank gives 4 covered targets (pair splits {01|23}, {03|12}) and
   4 uncovered ({02|13}), as plan.md states.

## Minor notes (non-blocking)

- Stage R-lib mean of 2.45 s/job versus 7.9 s for R-tree is on
  source/development cells with libraries extracted from those same source
  cells; it is a feasibility number, not a preview of the target effect.
  The analysis should not cite it.
- Size controls are not required to contain an input (stage controls include
  `GT(ANY, 2)`), whereas learned entries must. This matches the approved
  spec and the plan already states that size matching does not control token
  content; the analysis should remember that "contains an input" is part of
  what R-lib/R-size tests.
- Ranking ties break on the canonical key rather than the literal prefix;
  immaterial to the result.
- Stage libraries are pair sums plus one or two `GT(ADD, ADD)` predicates
  (6 and 12 entries), consistent with the proposal's feasibility probe.
- The 0024 harness's pristine-file gate now refuses to run from this commit
  (intentional, documented in the fixture README and asserted by the updated
  test). 0024 cannot be re-executed from this branch; its artifacts remain
  hash-locked.
