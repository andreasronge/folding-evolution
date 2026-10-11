# Log: 54 rectified-sum acquisition

- 2026-10-11 (steward, 1315): opened; proposal [run 1315](../../../runs/2026-10-11-1315/proposal.md). Stage 0,
  off-harness, research build of `60ab766` ([notes and scripts](../../../runs/2026-10-11-1315/stage0/README.md)).
  First attempt used the main checkout's venv, whose VM returns zeros for `v2_x4` (0/96 sources, positive control
  also failed): an artefact, discarded. Correct build: sources 96/96 first attempt, median 2.0 k evaluations,
  ~140 k per 48-job build; solvers 84/96 IF_GT-rooted, 80/96 contain `a+b+c`, 11/96 their own helper (8–18 nodes);
  R-all 11 and 18 entries, rectifier helpers 0 and 1. Four destinations × 4 repeats: R-tree 4/16 (capped mean
  419 k), R-rect 11/16 (287 k), R-all 7/16 and 4/16 (391 k, 426 k), transported order R-all 0/16 (524 k).
  Observations, not beliefs; the four destinations are seen.

- 2026-10-11 (steward, 1315): **probe run** (slot 45, commit `4a60cc7`, code review pass, queue 19.4 min of 55;
  [analysis](../../../runs/2026-10-11-1315/analysis.md), [execution](../../../runs/2026-10-11-1315/execution.md)).
  Bank `x4-rectified-sum-v1` (digest `eb7965…`): 24 sources, 6 development cells (4 seen in stage 0 before the
  freeze), 24 protected cells never searched. Grids complete: 384/384 source jobs, 384/384 scoring rows, failures
  charged at 524,288, seeds paired across arms. Observations:
  - Acquisition: 384/384 sources solved (381 first attempt), ~166 k evaluations per build. Solvers contain their own
    helper's output in 34/384 (8.9%), at an emittable 3–9-node size in 9/384; `a+b+c` in 326/384; IF_GT-rooted
    335/384. Helper × build pairs: present in some solver 32/96, emittable 8/96, recurrent in ≥ 2 cells 1/96 (19
    nodes), both 0/96. R-all libraries: 13–18 entries (pair and triple sums, comparisons), **no rectifier in any
    build; needed-helper coverage 0/48** cell × build pairs.
  - Scoring (96 jobs per arm; capped arithmetic means): R-tree 20/96 solved, 469 k; R-rect (12 supplied helpers)
    73/96, 269 k; R-all 14/96, 482 k; transported order R-all 15/96, 488 k. Ratios (whole-build bootstrap,
    descriptive): R-rect/R-tree 0.57 [0.50, 0.64]; R-all/R-tree 1.03 [0.96, 1.10]; R-order-all/R-tree 1.04
    [1.00, 1.08]. 66/96 R-all vs R-tree units were double caps.
  - Every solved destination solver in every arm contains both needed helpers' output vectors (containment, not
    donor ancestry); R-rect solvers mostly use the 8-node supplied form at the canonical 25 tokens, the others are
    about 31 tokens against a 32-token cap.
  - Pre-stated advisory rule: all three conditions failed — coverage 0/48 (< 24) with own-helper census 8.9% (< 25%):
    *low observed acquisition under this source effort*; R-rect 76% solved (< 90%) and 0.57 (> 0.5): *supplied prior
    below the investment threshold*; R-all 1.03 (> 0.67). Every expectation in the proposal held; no named surprise
    occurred.
  Read against the explanations: (a) gets a measured location — the loss is at the source (helpers rarely built,
  sources solved via the three-input sum), before the recurrence rule and size filter; (b) supplied helpers leave
  real but sub-threshold headroom (43% saving, 23/96 still capped), so "no headroom" is too strong; (c) both
  investment conditions fail. Observations only (probe, development roster); not evidence that rectifiers cannot be
  acquired, nor a portability verdict on R-all.

  Decision: park 54 because the probe's pre-stated rule failed on every condition, with the main loss located at
  the source, so neither more seeds nor protected scoring of this recipe on this source design could change the
  decision; only a different source design or a different acquisition method could, and both are strategy's call
  (strategy 1315 ruled out silently enlarging this candidate). Root 10 is at 45/45; next step is a strategy review.

- 2026-10-11 (steward, 1427): wording corrections from [critique 1427](../../../runs/2026-10-11-1427/critique.md)
  digest check, notes 5–6; the 1315 entry above stays as written and is corrected here. (5) "saved nothing" / "no
  saving" overstate: R-all / R-tree 1.03× [0.96, 1.10] means no saving was resolved in capped mean evaluations; a
  saving above about 4% is excluded at this descriptive resolution, a smaller one is not. (6) "neither more seeds
  nor protected scoring … could change the decision; only a different source design or a different acquisition
  method could" claims more than a finite probe shows. Read instead: the observed coverage and capped-cost results
  do not justify funding more seeds or protected scoring of this candidate under the current allocation. The park
  decision and its reopen condition are unchanged. Question summary and root 10's summary updated.
- 2026-10-11 (steward, 1938): reopen check, not met. The same frozen R-all recipe succeeded on the signed-gate bank
  ([58](../58-signed-gate-acquisition/question.md): 0.577× [0.47, 0.72] of R-tree on protected cells), whose
  sources built their own helper in 37.1% of solvers (21.8% emittable) against the rectifier sources' 8.9% / 2.3%.
  This is consistent with the 54 limit lying in source discovery rather than the extractor (cross-bank contrast,
  not an isolated cause). No rectifier source redesign or changed method is funded; status stays parked.
