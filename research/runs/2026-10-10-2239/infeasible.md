---
status: infeasible
next: strategy
targets_scored: false
---

# Frozen seed schedule fails the disjointness gate

Implementation commit: `6b40e16` on `research/2026-10-10-2239` (base tree code
restored from `3e961ad` by cherry-pick `057479c`). Code/tests only are committed;
task artifacts remain in the main checkout as requested. No queue is written.

The corrected initializer works, and preliminary full-cap timing is consistent
with the proposal. The obstruction is the **unchanged inherited seed formulas**
from [plan 2214](../2026-10-10-2214/plan.md), carried over by this approved retry.
That plan requires calibration, scoring and smoke seeds to be disjoint. The
formulas cannot meet that gate. Reusing a seed on different cells does not itself
prove biased results, but it violates the approved independence/disjointness
specification; the researcher cannot silently amend it after smoke outcomes.

## Measured schedule collision

Reproducer in this worktree (intentional nonzero exit, no search):

```sh
RUN_DIR=<fresh directory> RAYON_NUM_THREADS=1 .venv/bin/python -m experiments.chem_tape.tree_gp_run
```

[Committed schedule audit](smoke-committed/schedule_audit.json),
[256 calibration rows](smoke-committed/calibration_schedule.json),
[1792 proposed scoring rows](smoke-committed/target_schedule.json).

|Quantity|Measured count / range|
|---|---|
|Calibration seed rule|22140000 + 1000 × (8 × family_index + cell_index) + repeat0–7|
|Scoring paired seed rule|22150000 + 1000 × (8 × family_index + cell_index) + 2 × build + repeat|
|Calibration/scoring shared seed values|48: 22150000–22150007, 22151000–22151007, …, 22155000–22155007|
|Implicated calibration searches|96 (both mixes, TS calibration cells2–7)|
|Implicated proposed target searches|96 (A8 and tree, DG cells0–5, builds0–3)|
|Prescribed complete-search smoke collisions|22160000 and 22161000 are also TS scoring seeds|

Calibration spans 22140000 through 22155007; proposed scoring spans 22150000
through 22165115. Spacing the bases by10000 is insufficient because each phase
has sixteen indexed cells spanning15000. This is deterministic schedule
arithmetic, independent of search outcomes. The auditor writes evidence and
exits before calibration; its regression test verifies counts and refusal.

## What passed

- Corrected initialization: depths1/2/3 edges; function roots for full and grow
  initialization; mutation retains terminal-root probability0.5. Six bins hold
  43/43/43/43/42/42 individuals at P256, with272 draws and16 rejections on the
  prescribed smoke seed. Metadata records both root rules.
- [Six-bin validation](smoke-corrected/validation.json): 20000 draws/bin;
  all four depth1/2 bins accept100%; full depth3 accepts14427/20000 (72.135%);
  grow depth3 accepts19891/20000 (99.455%). Raw median lengths: full5/11/27,
  grow5/8/12. The full-depth3 exact acceptance is0.719348. Committed replay:
  [validation](smoke-committed/validation.json).
- All16 target canonicals compile to16 tokens and match D625 labels in the
  independent recursive interpreter, Python VM and Rust VM. They are validation
  fixtures only, never search seeds. 1998 generated-tree/operator comparisons,
  missing readouts, explicit signed overflow, conditional order and oversize
  reversion passed. Saved artifact/source/cohort/method audit passes.
- [Complete development search smoke](smoke/search_smoke.json), repeated with
  identical deterministic fields: DG seed22160000 solves at6144 evaluations in
  0.255s; TS seed22161000 spends524288 evaluations without solving in30.17s.
  These two development searches cannot adjudicate the procedure comparison.
- [Ten-worker forced-cap diagnostic](smoke/benchmark.json): ten development
  searches per family, every search524288 evaluations, Rayon1. DG wall55.31s,
  mean worker50.54s, max54.84s, effective workers9.138. TS wall53.11s,
  mean worker48.52s, max53.11s, effective workers9.135. Forced-cap jobs deliberately
  ignore exact solves to measure the whole path; their solve field is not a solve
  rate. No target cell is searched.
- Preliminary scoring projection using these means and historical native/G4
  rates, 30% reserve and120s overhead: DG4048s versus5760s gate; TS3223s versus4320s
  gate. This is a planning calculation, **not Stage0 admission**: source/development
  calibration and the16 fresh A8 replays have not run. Preparation timing and
  calibration solve/precision diagnostics remain unmeasured.
- Four focused tests and Ruff pass; git worktree is clean. Rust code is unchanged.

Timing/search artifacts above were measured in the working tree before commit;
the tree-search implementation was committed unchanged as `6b40e16`. The quick
semantic and schedule audits were replayed from that clean commit, and record
its hash. Benchmark adapter was simplified after stopping; it invokes the same
unchanged force-cap search on the same jobs. No efficacy/acquisition result is
claimed from these smoke artifacts.

## Not executed

The attempted six-arm small-cap pipeline refused at seed audit before any
search. No16 fresh native A8 replays, no256 Stage0 searches, no mix selection,
no1792 target searches, no uncertainty/repayment report, and no queue. Unvalidated
scoring/report drafts were discarded after the stop; committed code covers only
the corrected tree implementation, validation, smoke and failing schedule audit.
The code reviewer should verify this obstruction before any next proposal.

## What would work instead (steward option, not applied)

Retain the corrected initializer, arms, search budget, counts, pairing and all
statistical/timing gates, but explicitly re-register the scoring base as
**22180000**, keeping calibration base22140000 and smoke base22160000. The scoring
range then becomes22180000–22195115, disjoint from calibration and all smoke
seeds used here. The prospective [alternative seed audit](alternative-seed-audit.json)
also checks against saved DG/TS acquisition and native replay seed sets; no
collision is found. The runnable auditor deliberately retains the approved
colliding formulas. The steward decides whether this seed-only amendment is
worth another retry given the proposal's strategy-exit instruction; it is not a
baseline redesign or a result supporting either competing explanation.

A later retry still needs16 full native replays, sustained256-search calibration,
the frozen-mix precision estimate, full-cap tails, both80% timing admissions and
the DG <25% reviewer diagnostic. Initializer and throughput smoke alone do not
satisfy those gates. The current comparison remains untested.
