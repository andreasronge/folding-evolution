---
verdict: pass
---
# Code review — 0843 learned fragment block operator

Reviewer: Claude Fable 5.1. Reviewed `git diff 68e4a78..e347793` in the worktree
(`composition_search.py` hook, `fragment_library.py`, `fragment_operator.py`,
`fragment_report.py`, `fragment_run.py`, `tests/test_fragment_operator.py`), plus
proposal.md, critique.md, plan.md, queue.yaml and the smoke artifacts under `smoke/`.
`tests/test_fragment_operator.py` passes in the worktree venv (9 tests); `_folding_rust`
and `folding_evolution` import from the worktree.

## Blocking issues

None.

## What I checked and why it holds

1. **Arm wiring.** `BlockOperator.edit` implements the three block arms as proposed:
   F copies an intact fragment drawn uniformly; B samples each position independently
   from the library's fragments of the same length; W walks C's conditional chain
   (`decoder.lookup[previous, uniform allele]`) starting from the decoded token before
   the window (start state at position 0). All three share one length law (a uniform
   fragment index) and a uniform start in `[0, 32-L]`. C passes children through
   untouched. Edit probability is per child (`rng.random(n) < 0.2`), realized token
   changes are counted separately (`changed_tokens`), as the proposal requires.
2. **Inverse encoding.** Positions `start..start+L` (window plus next) are redrawn
   uniformly inside the conditional allele interval for the *desired* token, so the
   decoded suffix including the tape end is preserved. The 10k-per-arm audit in
   `validate_edits` checks desired == decoded, outside tokens unchanged, alleles beyond
   the repair position untouched, and interval containment; it passed with ~2.7k
   start and ~2.7k end edits per arm.
3. **Seeds and pairing.** Search streams are `[seed,0..3]`; the operator uses `[seed,4]`.
   Scoring seeds use base 203610090843 (+1e9 over the task stamp), smoke seeds phase 1;
   `prepare()` asserts no overlap with the 1246 source roster or between smoke and
   scoring. `jobs()` asserts all four arms of a (corpus, cell, seed) share the initial
   token hash and case draw, and that `eligible_children == (generations-1)*254`,
   i.e. the two elites are never edited and the variation count is unchanged.
4. **Search unchanged for C.** The only change to `composition_search.search` is the
   optional `child_transform` after ordinary variation and before elite concatenation.
   Prepare replays one historical 1246 C row per corpus with the hook off and compares
   a fixed substantive-field allowlist; the unit test also shows a C-arm operator with
   the hook on leaves every scientific field identical.
5. **Library extraction.** Token 0 is NOP in `v2_rmin_first` (verified), so the
   knockout and padding are correct. Leave-one-cell-out, recurrence in ≥ 2 other cells,
   rank (−cells, −count, −length, tuple), full-domain padded-solver exclusion, top 32,
   floor 8 all match the proposal. Each scoring cell uses `libraries[corpus|cell]`,
   the library that excludes that cell. All 64 libraries have 32 fragments.
6. **Metric and rules.** `comparison()` pairs rows by (corpus, cell, seed), uses
   `log cost_Y − log cost_X` with unsolved = 2·cap, averages per corpus and takes a
   t interval over 16 corpora (df 15). `route()` applies rules 1–5 in the approved
   order, with rule 3 relabelled per critique note 4. `report()` refuses incomplete or
   duplicated rosters.
7. **Gates and admission.** The only gate that decides whether scoring runs is
   `admit()`: largest of 32/24/16 seeds with `Σ_arm 64·n·mean_s ·1.15/10 ≤ 12600` and
   `+ smoke replay + 240 ≤ 11700`, plus preparation ≤ 2700 s. It is recomputed from the
   queue's own prepare smoke, not the dev smoke. The dev smoke projects 5976 s at 32
   seeds against an 11460 s internal deadline; at historical per-evaluation speed the
   deadline tolerates roughly 30 % capped searches in every arm, versus 3–13 % in the
   smoke and 8.6 % for historical C. The library floor cannot fail (deterministic from
   the frozen source, all libraries at 32). I see no way the gate stops the main stage
   for a wrong reason; a severely loaded machine would reduce seeds to 24/16 by the
   predeclared rule, which is the intended behaviour.
8. **Queue.** `${RUN_DIR%/*}` expands correctly: `run_queue.py` runs commands with
   `shell=True`, exports an absolute `RUN_DIR`, and fixes the date directory once at
   startup, so both entries share it (same pattern as 0537, which worked). Timeouts
   2700 + 11700 = 14400 s (4 h) are below `max_queue_hours`. `--deadline-seconds` leaves
   120 s under each entry timeout and the runner subtracts a further 120 s.
9. **Critique disposition.** Notes 1–5 are addressed in plan.md and in code
   (timeout ledger 45 + 195 min; explicit saved precision reconstruction with seed and
   procedure; rule 3 label; scope wording; Rosca attribution). Note 6 needed nothing.
10. **Handoff.** `score()` checks implementation/backend hashes, bank and provenance
    SHAs, library, table, schedule and smoke-schedule hashes, then replays all 128
    smoke searches and compares solver and operator counters before any scored search.
    The handoff smoke passed against the final commit.

## Minor notes (non-blocking)

- Prepare's `search.jsonl` contains 16 operator-off replays of *historical* 1246 C
  rows that keep `phase: training` (copied from the source row). They are only in the
  prepare directory and `report()` never sees them, but an analyst reading that file
  should not mistake them for 0843 scoring rows; the analysis should mention this.
- `route()` sends the case "F/C and F/W lower bounds > 1 but F/B upper bound < 1.10"
  (F beats C and W, no worthwhile increment over B) to `otherwise_unresolved`. That
  follows the proposal's rule 5 literally, but it is an interpretable outcome (library
  marginals matter, joint content does not); the analysis should name it rather than
  treat it as uninformative.
- The smoke was timed during daytime agent load (capped searches at 4.5–17e-5 s per
  evaluation; historical capped mean 28.9 s, smoke tails 67–91 s). The projection is
  therefore conservative for a quiet night run; nothing to change.
- `precision()` resamples with replacement (bootstrap pseudo-arms) rather than
  splitting rows; plan.md says so and it is a scenario, not a gate.
- `report()` writes `result.json` and `report.md` before plotting, and rows stream to
  `search.jsonl`, so a late plotting error (the 0537 failure mode) would not lose the
  decision. The full report path including plots is exercised by a complete-roster
  unit test.
