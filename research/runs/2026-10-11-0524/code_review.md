---
verdict: pass
---
# Code review: 0524 label-rearranged tree libraries (pre-run)

Reviewed commit `7c0e5df` against `96039d1` in the experiment worktree, plus
proposal.md, critique.md, plan.md, queue.yaml, smoke.md and the
`validation-prepare/` outputs in this folder. `tests/test_tree_permutation.py`
passes here (11 tests, 1.8 s).

## Blocking issues

None.

## What was checked

**Arm wiring.** `tree_permutation_run.envelope` gives R-tree no donors, R-lib
the intact `entries` of the build's library and R-perm
`constructions[realization].entries`; all three go through the unchanged
`tree_library_run.execute` → `tree_gp_search.search(donor_library=…)` path, so
the half-of-mutations draw rule, oversize rejection and ordinary-donor fallback
are identical across donor arms. The six frozen 0150/0348 method files
(`tree_gp_search.py`, `tree_library.py`, `tree_library_run.py`,
`restart_gp_run.py`, `tree_gp_run.py`, `composition_search.py`) are byte-identical
to `1f02bb7` (empty `git diff`), and `gate_sum_run.freeze` re-checks their
hashes at run time.

**Seeds.** Attempt seeds are a function of (phase, cell, build, repeat, k) only,
so the three arms share each job's eight seeds; `seed_audit` enforces exactly
three arms per seed with identical (cell, build, repeat, k), disjointness from
0150/0348 history and probe seeds, and disjointness across the construction,
stage, score, smoke and bootstrap domains. `validate_rows` additionally checks
that the paired arms share the initial-population hash and training indices.
The four-repeat fallback uses a subset of the audited six-repeat seeds.

**Construction.** `permute` pools slots by (entry nodes, compiled length, node
arity, token width) and shuffles every pool once with a fixed construction
seed; `signature` asserts the ordered arity/width skeleton of every entry and the
size-conditioned label multiset are unchanged, and `build` asserts replay
determinism and Rust/interpreter/Python agreement on D625. Token widths allow
ADD↔GT and X0–X3↔constant exchanges as the plan describes. Duplicates,
unchanged entries and accidental originals are kept (unit test covers an
all-duplicate pool). Realization = repeat mod 3 (or mod 2 in fallback, first two
constructions), so each construction gets exactly two repeats.

**Primary analysis.** `grid` requires the complete 24×18×repeats×3 grid with
shared seeds and correct realization assignment. B/C = 12 cells, learned
then-pair subgroup = 4 cells (checked against the bank). The bootstrap resamples
24 builds, then constructions within each build, with both repeats of a
construction and the matching R-tree/R-lib rows kept together; the same indices
are used for every arm and metric. `classify` implements the proposal's
thresholds (retention: primary upper < 1.25 and R-perm/R-tree upper < 0.80;
intact advantage: lower > 1.10 and point ≥ 1.25; replication guard upper < 0.60;
reliability lower > −0.03; A control lower > 1.5), with no post-hoc seed top-up.

**Stage gate.** The only decisions the gate can make are 6 repeats, 4 repeats
or stop. Validation measured a 6-repeat projection of 3,800 s against the
6,000 s limit (4-repeat: 2,563 s), so a wrong drop to 4 needs the queue host
to be about 1.6× slower than during validation, and a wrong stop about 2.3×.
The queue runs alone, so this is acceptable; see minor note 2 for the
underpricing direction.

**Critique.** Notes 1–5 are addressed in plan.md and the code (stage-0 solves
and throughput reported, fixed fallback with repeat mod 2, restricted
interpretation strings in `summarize`, nested paired bootstrap, exact ordered
predicate audit in `construction_audit.json`, fixed decision grid). Notes 6–8
concern digest/question prose outside the researcher's writable folder; plan.md
says so explicitly. The steward should pick those up at decide.

## Minor notes

1. **Predicate-survival wording in plan.md is misoriented.** The original
   libraries' 21 split-A predicates are all `GT(ADD(X2,X3), ADD(X0,X1))`
   (ordered key `((2,3),(0,1))` in `construction_audit.json`), as 0348's
   analysis also records. Those survive 0, 1 and 0 times in realizations 0, 1
   and 2. The "1, 5 and 0" figure in plan.md counts the opposite orientation,
   which the originals never contained. Either way, A predicates of any
   orientation across all 24 builds fall from 21 to 1, 6 and 0, far below the
   proposal's planning estimate that about a third survive. This makes the A
   positive control stronger, not weaker, but the analysis should quote the
   ordered counts from the audit and name the orientation.
2. **Gate prices R-perm from development cells with an R-lib floor.** If
   R-perm behaves like R-tree on protected B/C, scoring would take roughly
   5,300 s of the 7,170 s deadline; a timeout needs R-perm to average about
   19 s per job (three times R-tree). Development data (288/288 solved, 1.9 s
   per job across 1 A, 2 B and 1 C cell) make this implausible. Underpricing
   cannot cause a wrong stop, only a lost scoring run, which would surface as
   `infeasible.json` with a partial `search.jsonl`.
3. `schedule_audit.json` is written in `__init__` for the six-repeat grid even
   when the gate later selects four; `schedules.json` and
   `preparation.json.stage_gate.repeats` are authoritative.
4. `classify` lets a reliability-guard failure take precedence over an
   "intact information" outcome, as plan.md states. The analysis should still
   report the primary ratio and interval in that case.
5. The six 0348 R-lib replay jobs reuse historical protected-cell seeds. This
   is the documented validation exception and does not touch new scoring
   seeds.
6. Gate projection assumptions worth reading back after the run: the
   replay-host scale factor was exactly 1.0 during validation, and effective
   concurrency 9.68 came from a 57 s batch.
