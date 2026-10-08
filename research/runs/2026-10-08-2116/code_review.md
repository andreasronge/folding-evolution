---
verdict: pass
---

# Code review: 2026-10-08-2116 partial-program feedback vs equal allocation

Reviewed `git diff 18f24da..393a4dc` (new `partial_feedback_run.py`,
`partial_feedback_report.py`, `tests/test_partial_feedback.py`, replay
manifest + README), proposal.md, critique.md, plan.md, queue.yaml, smoke.md and
the verified smoke outputs under
`experiments/output/2026-10-08/2026-10-08-2116-smoke-verified/`.

## Blocking issues

None.

## What was checked

**Arm wiring** (`Runner.envelope`, `Runner.collect`). Round 1 is all-G4 with
the 1831 seeds (phase 0, base 202610081831). Round 2 F searches under
`rounds["1"]["F"]["table"]` = C1, round 3 F under C2; TF under T1 then T2
(`fitted["T"]`); O always under G4 and fitted once, at round 3, to the pooled
96 sources (`fit` skipped at round 2 for O). Scoring tables: F = C3, TF = T3,
O = 96-source C fit, R = C1 (saved at round 1), G4, C_exact = 1246 frozen C.
The per-job table hash check in the inherited `jobs()` guards the wiring at
runtime. Matches proposal and plan.

**Weighting** (`partial_transition_counts` on the pooled list). Each
contributing source is normalised then averaged within cell, then the cell is
rescaled to 1600, so rounds with different yields are not equal-weighted
(critique note 3). An empty later cell-round adds nothing and retains earlier
sources; an empty round-1 cell raises `empty partial corpus cell`, which the
runner records as a fatal error rather than resampling. Pre-solve exclusion
and archive provenance checks are inherited from 1831 and tested.

**Seeds and pairing** (`roster`). Rounds 2/3 use phases 2/3 of base
202610082116 shared by F/TF/O; scoring uses phase 4 shared by all six arms.
Ranges are disjoint from 1831's phase 0/1 seeds and from the smoke seeds
(base +1e8); `roster` raises on any seed collision or incomplete pairing, and
the test asserts the full allocation (2048 + 12288 + 6144 rows, 96 sources per
cell per acquisition arm). Training case indices derive from the seed, so
paired arms see the same 64 cases (`pairing_checks` 288 in smoke).

**Endpoint and decision rule** (`contrasts`, `route`). Primary = exp(mean over
lineages of mean over 4 cells x 16 seeds of log cost_O - log cost_F), unsolved
= 2 x cap, 95% t over 16 lineages. `route` implements the plan's precedence
exactly (UB<1 degradation; UB<1.15 small gain/prefer O even if LB>1; LB>1 and
point>=1.15 adopt provisionally, worthwhile only if LB>1.15; LB>1 and
point<1.15 prefer O; else unresolved), which resolves critique note 2.
Efficacy requires `completed_pairs == 8`, no stop, not smoke; otherwise the
label is `incomplete`. 1x-cap and both-solved sensitivities, per-family and
per-cell tables, solves, payback and lineage-sizing are all emitted.

**Replay gate.** All 16 lineages' round-1 sources are regenerated and compared
to the manifest (fingerprint over all scientific fields, counts hash, C1/T1
table hashes); the manifest's own SHA is pinned. Smoke replayed BE1 and PA1
bit-exactly. Every file on the search path (collector, search, fitter, bank,
maps, `folding_evolution/`, `rust/`) is unchanged since 998a9fe, so the 14
un-smoked lineages should replay identically.

**Critique disposition.** Notes 1-3 and 6 are implemented in code and plan
(worker count, replay/fit/verification in projection, decision precedence,
pooled-source weighting, fatal replay/empty-cell handling, sizing output).
Notes 4-5 need no action. Notes 7-8 concern wording in question 27's log and
the 1831 analysis, outside this task's writable folder; plan.md says so and
promises not to propagate the stronger claims. That is an adequate answer for
this stage; the steward should pick them up at decide.

**Feasibility gate.** The 240-min gate passed (227.4 min projected with
C_exact); it did not stop the main stage, so there is no wrong-reason stop
risk. Timeout 18000 s is under `max_queue_hours` 8. All 13 `expect_outputs`
were produced by the smoke. The queue command has no `cd`, but the driver runs
`run_queue.py` from the worktree and `run_queue` uses the repo root as cwd, so
`.venv/bin/python` resolves to the worktree venv (import_check also guards
this). 19 targeted tests pass locally.

## Minor notes

1. **Deadline headroom.** Internal work cutoff is 17760 s against a 13644 s
   projection; scoring would have to average about 41% slower per search than
   in the smoke for pair 8 to miss the cutoff (e.g. every arm behaving like
   TF's 20.8 s/search would overrun). The smoke projection (1.62 s wall per
   search) is already more pessimistic than 1831's full-run actual
   (1.29 s), so the risk looks low. If it does overrun, the result is
   `incomplete` with no efficacy label, by design; nothing to change now.
2. **Replay failure is sunk cost.** A replay mismatch in a later lineage
   would abort the run mid-way (correct behaviour) after up to ~2 h; mitigated
   by the unchanged search-path code above.
3. **Fresh-RUN_DIR guard (inherited from 1831).** If the driver resumes an
   interrupted queue, `run_queue` reuses `experiments/output/<date>/<id>/` and
   the runner will exit immediately with `use a fresh RUN_DIR`. Pre-existing
   behaviour, not specific to this experiment; worth knowing when reading a
   failed resume.
4. **Smoke provenance.** The smoke `config.json` records `git_commit`
   18f24da because the code was uncommitted when it ran; the recorded code
   hashes match the files at 393a4dc, so provenance is by hash.
5. Round-1 `fit()` is computed three times (F, TF, O) on identical counts.
   Harmless, ~1 s.
