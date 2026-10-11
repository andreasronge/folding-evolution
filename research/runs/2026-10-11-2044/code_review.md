---
verdict: pass
---

# Code review — 2026-10-11-2044 signed-chain depth probe

Reviewed commit `8a621df` against `7cce3cf` (new files only: `signed_chain_bank.py`,
`signed_chain_run.py`, `tests/test_signed_chain.py`, frozen data under
`experiments/chem_tape/data/signed_chain_2044/`; no engine, extractor or Rust change),
plus proposal.md, critique.md, plan.md, queue.yaml and smoke.md. Ran the five probe tests
(pass, 19 s) and `run_queue.py --validate` on queue.yaml (OK, 2 entries, 3,300 s).

## Blocking issues

None.

## What was checked and holds

1. **Arm wiring.** R-tree gets no donors; R-all gets the `semantic` entries of saved 1938
   library `build` (same field 1938's R-all used, not `semantic_all`); R-gate gets the 24
   supplied p/n helpers (2 kinds × 12 ordered pairs). Jobs pass only `id` and `labels`;
   canonical trees cannot seed search (test confirms envelopes are unchanged when
   `helpers`/`canonical_tree` are blanked).
2. **Seeds.** Eight disjoint seeds per build × cell × repeat, identical across the three
   arms (deliberate pairing, as in 1938). Full grid 20450000–20452303, smoke 20460000+,
   both outside stage 0 (20440000–20443027) and all 1938 seeds; `seed_audit` fails closed on
   any collision or unintended reuse.
3. **Roster and protection.** Split is performance-blind: four stage-0 cells plus the two
   lowest label-hash survivors; the 18 others are protected. `envelopes` rejects any
   protected cell or any schedule entry not in the frozen grid. No protected scoring
   command exists.
4. **Labels and semantics.** `(p(a,b)+n(b,c))+p(c,d)` labels computed independently in
   numpy, checked against the recursive interpreter, Python stack interpreter and the VM;
   14 nodes / 20 tokens, under the 32-token solver limit. Admission replay in `prepare`
   must reproduce the committed manifest exactly.
5. **Metrics.** Failed jobs are 8 × 65,536 = 524,288 evaluations (enforced by
   `validate_rows`: unsolved attempts must be exactly 65,536 and unsolved jobs must have 8
   attempts); exact solvers are re-executed against labels. First-attempt rate, attempt
   distribution, capped jobs, per-arm/cell/build stats and two-way build × cell bootstrap
   match the proposal's descriptive outputs.
6. **Coverage.** `helper_diagnostics[h]["semantic"]["included"]` exists in all 24 saved
   libraries; the smoke report's coverage over 576 build × cell pairs gives 19 with all
   three helpers (3.3%) and 144 with none (25%), matching stage 0's independent count.
7. **1938 provenance.** Archive SHA, per-file SHAs, bank digest, source-only library
   reconstruction and 1938's frozen method hashes are all re-verified before any search;
   the two stage-0 libraries are not used.
8. **Critique.** Notes 1–4 are addressed in plan.md and in code: runtime arithmetic
   corrected (4.6 min cap scenario), stage-0 anchors distinguished from the saved
   libraries, forecast priced on the actual protected count (`len(split["protected"])`,
   tested with 11), hypothetical effects 0.60–1.00 with 0.80 explicitly unresolved, a
   doubled-variance sensitivity, and "width ≤ 1.6 is precision, not decisiveness" wording.
   Notes 5–8 concern digest/question wording outside the researcher's write scope and are
   deferred to the steward with that reason; acceptable.
9. **Recommendation criteria.** The three criteria (R-tree first attempt ≤ 85%, R-gate
   solves ≥ 95% and R-tree capped ≤ 25%, some r with central precision ≤ 1.6 and summed
   timeouts ≤ 4 h) only produce a flag returned to strategy; nothing runs automatically on
   it, so no stop-for-the-wrong-reason risk affects this stage.

## Minor notes

- **Runtime reserve.** Central estimate 10–15 min against a 2,370 s internal deadline;
  the 10%-cap scenario is 24 min. A pathological batch (most jobs capped, ≈ 30 worker-s
  each) would exceed the deadline. `run_batch` then preserves the completed rows in
  `score.jsonl` but writes `failure.json` and no `report.json`; the reviewer can still
  describe partial rows, and heavy capping would itself be the finding. Not a gate.
- **Prepared-directory lookup.** `--prepared "$(dirname "$RUN_DIR")/…-prepare"` assumes
  both entries run in one `run_queue` invocation (the date directory is fixed at queue
  start). A resume on a later calendar day with prepare already done would fail closed.
  Same construct as 1938.
- **Sensitivity scenario not in the flag.** `precise_and_affordable` uses only the
  central variance scenario; the doubled-variance scenario is reported alongside. The
  analysis should read both before recommending anything.
- **Concurrency for the price.** The confirmation forecast uses the 864-job run's measured
  effective concurrency, which is appropriate; the smoke's 3.37 is a 12-job artefact and
  should not be quoted as throughput.
- **Post-report deadline check.** If the fixed deadline passes during report writing, the
  outputs exist but the process exits non-zero with `failure.json`. Report generation
  takes seconds, so this is unlikely.
- The hard-coded denominator 288 in the recommendation is correct for the full grid and
  is skipped for smoke.
