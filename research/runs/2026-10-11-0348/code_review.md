---
verdict: pass
---
# Code review: 2026-10-11-0348 (commit `1f02bb7`, diff from `82e4bd0`)

Reviewed `gate_sum_run.py`, `gate_sum_bank.py`, `gate_sum_report.py`, the
generalisation of `tree_library_report.py`, `tests/test_gate_sum.py`, the frozen
data snapshots, `proposal.md`, `plan.md`, `queue.yaml`, `critique.md` and the
smoke evidence (`smoke-stage/`, `smoke-small/`, `smoke-admission/`, `probe/`).
`tests/test_gate_sum.py` re-run in the worktree: 13 passed.

## Blocking issues

None.

## What was checked

1. **Arm wiring.** `envelope()` is 0150's: R-tree gets `donors=None`, R-lib gets
   `libraries[build]["entries"]`, R-size gets `libraries[build]["controls"]`.
   Libraries used for scoring must equal the frozen 0150 `libraries.json`
   byte-for-byte (`libraries != original` check in `score()`), and are
   re-derived from the 0150 acquisition rows with the original extractor and
   control seeds (`reconstruct()`), including the four failed source jobs in the
   charged acquisition cost. The frozen search core (`tree_gp_search.py`,
   `tree_library.py`, `restart_gp_run.py`, `src/`, `rust/src/`) must hash equal
   to 0150's provenance.
2. **Seeds.** Stage seeds 34,000,000 + 1000·ci + 32·b + k (ci < 4), score seeds
   34,200,000 + 1000·ci + 32·b + 8·r + k (ci < 18, r < 4): the per-cell offsets
   stay below 1000, so no collision inside a phase; phases, smoke (34,100,000–7)
   and bootstrap (34,100,200) are disjoint from each other and from every
   0150 namespace (31.5–32.0 M) and both probe namespaces (934.8/934.9 M). The
   audit enforces that each seed is used by exactly the three arms with the
   same (cell, build, repeat, attempt), and tests confirm tampering is caught.
3. **Bank and split are performance-blind and deterministic.** Roster order is
   label-hash order and must match the planning audit's 144 roles; admission is
   the exact ≤9-token screen only (near-alias diagnostics retained, no stricter
   rule added, as plan.md states). Development = first four; `split()` raises
   rather than re-splits if either probed cell lands outside development or any
   pair split has fewer than six survivors. The two probe cells in
   `probe/rows.json` are development cells 1 and 2. Protected = 6 × 3 splits.
4. **Timing gate.** Reproduced from `smoke-stage/stage_gate.json`:
   90 + 1.3 · 1728 · (6.972 + 1.327 + 6.504) / 9.239 = 3,689 s ≤ 5,400 s. The
   gate measures the actual eight-attempt wrapper, all 24 builds, all four
   development cells and all three arms (critique 1). It can only stop the main
   stage on measured wall time, not on an outcome, so there is no risk of
   stopping for the wrong reason. Smoke preparations write `admitted=false`
   and `score()` refuses them (tested).
5. **Scoring fail-closed path.** `score()` re-checks freeze, audit, bank hash,
   libraries, stage rows, stage timing and recomputed gate before submitting
   any job; `smoke-admission/` exercised this against real preparation output
   and intercepted at the submission boundary with 5,184 jobs and 24 libraries.
6. **Metrics match the proposal.** Capped mean evaluations with failures at
   524,288 (enforced by `restart.validate_rows`), equal cell weight (balanced
   grid), paired 24-block bootstrap with one `selected` matrix shared across
   arms, costs and acquisition (joint resampling, critique 4); guard is the
   R-lib − R-tree solve-fraction lower bound > −0.03. `classify()` precedence
   (harm → transfers with guard → reliability inferior/unresolved → small or
   none → unresolved) matches plan.md and is unit-tested on the overlap case
   [0.86, 0.89]. Unbounded repayment is retained when savings cross zero.
7. **Learned-predicate split flag.** All `GT(ADD,ADD)` entries in the 24
   frozen libraries compare X2+X3 against X0+X1 (20 libraries), so the
   hard-coded `((0,1),(2,3))` flag in `gate_sum_report.py` is correct; the
   three explicit `pair_split` groups cover the per-split secondary.
8. **Queue.** Two sequential entries, 2,400 + 5,400 s = 2.2 h ≤ 8 h;
   `$RUN_DIR/../2026-10-11-0348-prepare` resolves because `run_queue.py`
   fixes the date directory at launch; every `expect_outputs` file is written
   by the code (all preparation outputs present in `smoke-stage/`).
9. **Critique.** Points 1, 2, 4, 5 are implemented; 3 needs no action; 6–8
   are digest/question wording outside the researcher's folder and plan.md
   says so and carries them to the steward.

## Minor notes

- **Scoring timeout headroom is about 1.95×.** Raw projected scoring is
  2,769 s against a 5,370 s usable deadline. Development R-tree attempt
  success ranged 0.45–0.63 across the four cells; if the 18 protected cells
  average roughly 0.3, R-tree and R-size jobs would cost 3–4 attempts and the
  scoring run would overrun. A timeout writes `infeasible.json` and the
  reporter rejects an incomplete grid, so there is no partial-analysis risk,
  only the loss of the 90-minute slot. Not blocking; the gate is the approved
  one.
- The seed audit reserves probe seeds only for k ≤ max k among valid probe
  rows (0); the discarded long probe jobs at k ≥ 1 are not listed. Harmless
  because the probe namespaces are 900 M away from the new ones.
- `rust_extension` is hashed into `method_freeze.json` but is not part of the
  frozen core compared against 0150, so a rebuilt extension passes the freeze.
  Semantics are guarded by the eight-job off-path replay and the independent
  D625 verification of every solver, which is adequate.
- If the prepare entry fails, the queue still launches the scoring entry,
  which then fails closed with `infeasible.json`. Expected behaviour.
- For the steward: critique 6–8 (digest wording "resolved", "do not" vs "no
  resolved gain", literal-match caveat) remain unaddressed in the tree.
