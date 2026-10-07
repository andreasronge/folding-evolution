---
verdict: pass
---

# Code review: 2026-10-07-0315 training-bank initialization intervention

Reviewed `git diff a39bffe..5dae3a6` in the experiment worktree, plus proposal.md,
critique.md, plan.md, queue.yaml, smoke.md and the probe/smoke artifacts in
`preparation/`. The search engine, operators, decoder inverse and RNG streams are
unchanged (only `initialization_run.py` gained a `law_count=0` guard and
`initialization_report.py` gained weighting/gate parameters). The new runner subclasses
the 2331 runner and reuses its `job`, `check_block` and `initialized_search`
unchanged.

## Blocking issues

None.

## What was checked

**Arm wiring and seeds.** `job()` maps GG→(src G4, dst G4), MM→(M, M),
MG→(src M, dst G4, re-encode), GM→(src G4, dst M, re-encode); re-encoding uses stream
`[seed, 3]` and asserts the token tapes are unchanged
(`composition_search.py:162-166`). All four arms share the seed per (cell, seed) block,
GG is one shared row per cell/seed, and `check_block` verifies MG=MM and GM=GG
generation-0 token hashes, `initial_reencoded` flags, training indices, cap and pop
size on every block. I re-verified these invariants independently on the 1220 probe
rows: 0 duplicates, 0 pairing/flag mismatches, and smoke (cap 8192) and probe
(cap 524288) produce identical generation-0 hashes for the same seeds. The 786
reproduction rows (420 from 1723, 366 from 2331) have 0 mismatched substantive fields.

**Grid count and roster.** `block_jobs` gives 10 GG + 20×10×3 = 610 jobs per seed,
122 000 over 200 seeds, no MMr (tested). Cells are exactly `TRAINING` (4 BE + 6 PA),
in the order the weighting and Welch code assume; `frozen_source` pins the 1723
config, trajectories and `fresh_scores.json.gz` by SHA256, and the 2331 subset
and descriptive reference are hash-pinned.

**Metrics match the proposal.** Contrasts are paired log2 ratios per
(map, cell, seed). Cell weights are 0.125 for BE and 1/12 for PA (equal families,
equal cells within family); map weights come from the shared crossed bootstrap
(multinomial per 10-map family, each family summing to 0.5), identical to 2331.
S_c = mean over maps and seeds of P1−P2; C = mean BE S_c − mean PA S_c with the
Welch interval over cells (df formula and pooled within-family SD verified by hand
against the test). Label precedence B→E→R→X and N/P/X with δ=0.25 are as plan.md
states; direction and `inside_margin` are reported separately. `masked_summary`
reproduces the base estimator when all masks are true (same einsum, same 0.5 family
split) and refuses to manufacture costs when a stratum is empty.

**Gates and stop rules (stability).** The only gates that decide whether the grid runs
are deterministic: 40 round trips at a fixed RNG seed and bit-exact reproductions
(both passed on this code). The row-U gates are post hoc and stable: recomputing
them on the 1723 fresh-score pilot (50 paired seeds, same ten cells), the per-cell
G4 solve rates are 86–100 %, so the probability of any cell falling under 75 % at
n=200 is ≤1.2e-5 (binomial); the pooled D under the planned weighting is
1.08 log2 with resampled 95 % lower bounds of 0.42–0.46 log2 at n=50–200, well above
the log2 1.25 = 0.32 gate. Minimum 120 seeds is reached at roughly 2.5 h even at
2331's lower efficiency.

**Deadline handling.** Two consecutive seed blocks are interleaved; only seeds whose
block fully passed `check_block` are appended to `complete_seeds`, and a seed is
dropped if an earlier one in the pair is incomplete (tested), so the retained set
is a balanced seed prefix. `run_jobs` returns at the deadline without waiting on
in-flight work; the longest observed single search is 27 s. Internal deadline
25 200 s includes a 360 s reporting reserve (synthetic full-size report measured
19 s); the queue timeout 27 000 s leaves 1 800 s slack and is under the 8 h cap.
Measured probe throughput (76 wall-s/seed, 9.5 effective workers) projects 4.2 h for
200 seeds; the conservative 6.4 h plan figure also fits.

**Failure paths.** Any exception in validation or `check_block` sets
`validation.passed=False`, routes to U, and still writes result.json and summary.md
(verified with an empty-seed report). `validation.passed` is only set true after
encoding and reproduction pass.

**Critique points.** Notes 1–4 are addressed in plan.md and implemented (conservative
budget retained; first-batch timing logged without selection; family means, per-cell
S, in-sample/off-family split and label precedence in the report; N vs. absence and
antagonism flag preserved). Notes 5–6 concern steward-owned digest/question text;
plan.md explicitly defers them to the steward, which is appropriate for the
researcher's scope.

**Tests and environment.** 35 tests in the two initialization suites pass in the
worktree (smoke.md's 47 includes `test_composition_bank.py`). The worktree has its
own `.venv` with `_folding_rust` importable, and the queue command follows the 2331
precedent exactly.

## Minor notes (non-blocking)

1. **Seed count is fixed at 200 while time allows ~330.** Measured throughput would
   fit about 330 seeds in the 7 h deadline. The proposal's argument that C is
   cell-limited, not seed-limited, is sound, and 200 was the approved design, so this
   is a design choice rather than a truncated gate. If a future stage repeats this,
   letting the grid run to the deadline would be nearly free extra precision for the
   pooled contrasts.
2. **Label precedence hides margin containment in the row.** An interval such as
   [−0.20, −0.01] routes to B (row 1) even though it lies inside ±0.25. This is
   pre-stated and deterministic, and `inside_margin` is reported, but the analysis
   should state containment next to the row whenever B or R is also inside the
   margin.
3. **`expect_outputs` includes `family_balance.png`,** which is only produced when
   all ten cells have finite S. If validation fails before the grid, the queue will
   flag the run as failed on outputs as well as on the exit code. That is the desired
   signal, just noting the mechanism.
4. **Redundant mask term.** In the uncapped-triplet sensitivity, `triplet & GG<cap`
   equals `triplet` (GG is already in the triplet conjunction). Harmless.
5. **Row-U gates with 2-seed diagnostics.** The probe report lands on row U by design
   (diagnostic flag); its effect estimates in `preparation/` should not be quoted,
   as smoke.md already says.
