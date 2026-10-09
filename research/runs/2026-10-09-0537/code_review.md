---
verdict: pass
---
# Code review — 2026-10-09-0537 (fixed-prior Q recoding, R30/R100)

Reviewed commit `fe196c1` against `853e928` (worktree `folding-evolution-research/2026-10-09-0537`), plus proposal.md, critique.md, plan.md, queue.yaml and the committed preparation/smoke artifacts. Ran `tests/test_recoded.py` in the worktree venv: 7 passed.

## Blocking issues

None.

## What was checked

**Recoding is what the proposal says.** `RecodedDecoder` builds, per corpus/dose/k, a permutation per body row (positions 1–31, contexts 0–23) from `default_rng([537, corpus_index, dose, k])`; position 0 and the start context (24) are untouched. R30 permutes exactly 7 200 = 24 000·30/100 selected entries among themselves; R100 permutes the whole row. `lookup_new[a] = lookup_Q[perm[a]]`, so every row's token counts are preserved (`validate()` checks counts, bijection and inverse consistency for all 800 rows). The inverse is `perm⁻¹`, and `recode()` maps Q alleles through it using Q's decoded previous token as context, then asserts the token tapes are unchanged. Hashes cover the actual lookup, permutation and inverse arrays, and `score()` reconstructs every map and refuses on any mismatch.

**Paired streams and arm wiring.** `search()` gains an `initial_transform` hook applied after the generation-0 draw and before hashing. It consumes no randomness; the case, initialization, variation and selection streams are the same as Q's (allele range unchanged at 24 000). The dose-0 path replays 16 historical Q rows bit-exactly through the same hook, and 16 C rows through the unchanged `decoder_for` path. Every scored row is checked against the paired Q reference for `training_indices` and `initial_tokens_hash`, and against the per-realization map hash. Seeds are the 2 048 historical Q triples (all distinct); roster has 4 096 rows, 4 per (corpus, cell, arm, realization), k = sorted seed index // 4 as frozen.

**Metrics match the plan.** G = exp(mean over corpora of mean over cells/seeds of log cost_Q − log cost_R30), unsolved at 2×cap, t interval on 15 df; route: lower ≥ 1.20 gain, upper ≤ 1.20 no gain, else unresolved. H = cost_R30/cost_C with "approaches C" only if upper ≤ 1.50. "No useful gain at either dose" requires both G and G100 upper bounds ≤ 1.20. 1×cap and both-solved sensitivities, per-cell and per-realization spread, gap share and resolution price are reported. Direction and df are pinned by a unit test. Any incomplete roster yields `outcome: incomplete`, not an efficacy call. The 1548 C references contain exactly 2 048 fresh C rows with no duplicate triples, so the pairing step cannot trip on reference data.

**Gates that decide whether scoring runs.** Preparation must finish ≤ 1 800 s, pass exact row counts for 64 maps, 4 096 initial-token hashes, 936 bit-exact C recoveries, 32 bit-exact replays, and admit on runtime: `1.15·max(sample, finite-batch) + setup + 120 < 11 760` and `all_capped + setup + 120 < 11 760`. Committed numbers: preparation 514 s, expected 7 636 s, all-capped bound 10 375 s. None of these can stop the main stage for a reason that would also bias the result: the timing sample is 64 fixed rows (both doses, both realizations, every corpus), rerun identically in scoring and checked for deterministic replay, with no selection by performance. Scoring deadline 11 880 s inside a 12 000 s timeout; total queue 13 800 s < 8 h.

**Critique disposition.** Notes 1–5 are implemented (measured throughput incl. setup; array hashes; frozen k assignment; conditional-uniform solver encoding and full offspring-operator audit; explicit G/H direction; both-dose rule for the "either dose" null; unresolved branches named). Note 6's reference is added to plan.md. Notes 7–9 are digest/question wording outside the researcher's write scope; plan.md says so and defers them to the steward. Acceptable.

**Source corrections.** The 23 000 → 24 000 allele-range correction and the absence of saved C solver tapes in 1246 are handled honestly: f = 0.30 is applied to the true range, and C solvers are recovered by bit-exact replay of the 936 historical solved rows (no new seeds), verified against D1331.

## Minor notes (non-blocking)

1. **All-capped admission margin is 13%.** The bound (10 375 s) sits 1 385 s under the 11 760 s ceiling with no safety multiplier. If the machine is noticeably slower when the queue runs (other load, thermal), preparation could refuse admission even though the expected price has a 54% margin. The failure mode is "does not run", not a wrong answer; if that happens, re-queue rather than write infeasible.md. The all-capped case itself is essentially impossible (Q solved 74%; R30 timing solved 23/32).
2. **Report generation sits outside the error handler.** In `Runner.run()`, `make_report`/`save_report` run after the `try/except`. If scoring fails before `variation.json` is copied into `RUN_DIR` (e.g. a map-hash mismatch), `save_report` raises `FileNotFoundError` and the traceback masks the original error. The original error is still in `validation.json`. No effect on a completed run.
3. **Per-search setup in scoring will be lower than the timing estimate.** Timing used 64 distinct maps for 64 searches, so every search paid cold construction (~0.5 s); scoring sorts by map and uses a per-worker cache. Conservative in the right direction.
4. **Audit parent sampling is uniform, not lexicase-selected.** The plan and `variation.json` state this. Treat the solver-tape audit as descriptive, as planned.
5. **Steward follow-up.** Critique notes 7–9 (digest wording on "pooled or per-position frequency does not carry it", "shows no advantage", and question 30's reopen clause) still need action at the decide step.
