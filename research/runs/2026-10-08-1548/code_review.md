---
verdict: pass
---

# Code review: 2026-10-08-1548 (frozen C/T on then-addition-v1 and v1 holdouts)

Reviewed `git diff e56c29d..45b2bdb` in the worktree (HEAD `45b2bdb`, clean), plus
proposal.md, critique.md, plan.md, queue.yaml and the smoke artifacts. I re-ran
`tests/test_then_addition.py` and `tests/test_comparison_gate.py` (13 passed), recomputed
the bank and roster summaries from the committed data, and checked the vendored 1246
source files against the originals in `experiments/output/2026-10-08/2026-10-08-1246-comparison-gate-training/`
(all five SHA-256 values match).

## Blocking issues

None.

## What was checked

1. **Arm wiring.** `envelope()` selects the G4 table for G4 rows and the frozen per-corpus
   C or T table otherwise; the table hash of every returned row is checked against the
   expected hash in the inherited `jobs()` save path. The search payload carries only
   `{id, labels}`; no canonical program or screen witness reaches a search. K is never
   scored. All 48 frozen table hashes (C/T/K × 16 corpora) are validated against
   `freeze.json` and `corpora.json` before any search, and the source log is checked to
   contain no holdout rows.
2. **Seeds.** F uses base 202610081548 with phases 6/7 and a 10 000 corpus stride, so the
   16-cell × 8-seed block (3 200 per corpus) cannot collide across corpora or families.
   D is the exact 1246 holdout roster (4 352 rows: 2 048 C, 2 048 T, 256 G4; 16 paired
   seeds per corpus × cell, 32 G4 per cell), protected by the frozen `schedule_hash`.
   Only same-corpus/cell C/T pairs share a seed; `check_seeds` is applied to F + D and
   to F + D + smoke in the tests, and target seeds are checked disjoint from all 5 376
   source searches. Case draws are seed-derived and re-verified per row, so C and T see
   identical 64-case training sets.
3. **Bank.** `then_addition_bank.py` reproduces the approved screen deterministically:
   240 → 162 → 86 → 37 → 16, with every canonical verified in Python and Rust on all
   1 331 inputs, agreement against all 220 distinct non-constant v1 behaviours (max
   retained agreement 0.782), and exact 1603-bank alias exclusion (none hit). The 16
   selected IDs all use the F>m or M>F gates as the proposal states. The S/M/m/F count
   discrepancy (S3 M5 m4 F4 vs S3 M4 m3 F6) is a representative-naming convention; the
   16 behaviour hashes are identical under both conventions and the code pins the
   probe-order counts. No performance data touches bank construction. The SHA is pinned
   in code and checked in `load()`.
4. **Endpoint.** `contrast()` computes exp(mean over corpora of mean over cell × paired
   seed of log cost_T − log cost_C), unsolved = 2 × cap with a 1 × cap sensitivity, 95% t
   over the balanced corpus prefix. The prefix rule is the fixed BE1/PA1…BE8/PA8 order,
   ≥ 6 complete pairs, G4 complete, and no efficacy after an error; the report refuses a
   prefix with missing, duplicate or extra rows and ignores trailing rows. Precedence is
   incomplete → shared < 25 % censoring → numeric rule, as in the plan.
5. **Stop rules.** There is no pilot or power gate that decides whether the main stage
   runs; the only ways to end without a decision are fewer than six complete pairs or an
   execution error, both of which are correctly reported as `incomplete`. Work cutoffs
   (14 160 s for F, 12 360 s for D) leave 120 s for reporting plus 120 s queue margin;
   smoke reporting took 0.24 s for 48 rows. Queue timeouts sum to 27 000 s (7.5 h), under
   `max_queue_hours = 8`. At the 1246 all-capped scenario (28.5 s per search, 9.57
   workers) F needs ~3.6 h, within its 3.93 h cutoff; D would reach at least six pairs.
6. **Critique dispositions.** All seven notes are addressed in plan.md and in code:
   auditable bank artifact with IDs, aliases, agreement and exclusion reasons (note 3);
   restricted boundary language and censoring precedence in `route()` (note 4);
   matched/mismatched and own-family holdout-minus-training shrinkage restored for D,
   source-family BE−PA for F (note 5); reporting reserve and incomplete-prefix rule
   (note 2); note 7 deferred to the steward, which is correct for the researcher's write
   scope.
7. **Smoke.** The committed-commit smoke ran 48 training-only searches, replayed
   deterministically against the first smoke, hit the forced-deadline and injected-error
   paths, and performed no target search.

## Minor notes (non-blocking)

- `bank.json` written for row D and for smoke is the full v1 bank including holdout
  labels and canonicals. This is output provenance only, not search payload, but the
  analyst should not mistake it for the search envelope.
- The per-corpus interval conditions on the 16 fixed cells (a cell × arm interaction
  common to all corpora is not sampled). The report's scope string says this; the
  analysis should repeat it.
- The shrinkage secondary for F compares 16 then-addition cells against 4 own-family
  training cells per corpus, so it mixes bank composition with transfer; treat it as
  descriptive.
- `envelope()` does a linear `row not in self.schedule` check over 4 352 rows per job;
  harmless at this scale.
