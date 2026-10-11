# Log: 58 signed-gate acquisition

- 2026-10-11 (steward, 1938): opened on strategy 1938. Stage 0 ran off-harness, in a research build of `3a18ef5`,
  ~3 min of compute ([notes and scripts](../../../runs/2026-10-11-1938/stage0/README.md)). Observations, not beliefs:
  - The 24 helper trees agree across interpreter, VM and labels.
  - Sources: 192/192 solved on the first attempt, ~200 k evaluations per build. 71/192 contain their own helper,
    44/192 at an emittable 3–9 nodes.
  - R-all: 37 entries per build, with 11/24 and 6/24 signed-gate helpers. Coverage of both needed helpers per
    destination: 3/24 and 2/24.
  - Four destinations (now seen; development roster), 12 jobs per arm, mean evaluations: R-tree 5.2 k (all first
    attempt), R-gate 1.5 k, R-all 2.8 k / 2.7 k, transported 1228 R-all 3.3 k / 4.6 k.
  - Question 50's ≥ 90% first-attempt condition is met; no harm was observed.
  Proposal: [run 1938](../../../runs/2026-10-11-1938/proposal.md).
- 2026-10-11 (steward, 1938): experiment [run 1938](../../../runs/2026-10-11-1938/analysis.md), commit `9da9c2c`,
  bank `x4-signed-gate-v1` frozen with the method before any protected search (18 protected cells, 6 development
  cells, fresh seeds). 24 new R-all acquisitions (2,304/2,304 source jobs solved; ~216 k evaluations per build).
  Protected roster, 1,728 jobs per arm, all solved in every arm, no capped job:
  - **Primary, R-all ÷ R-tree 0.577 [0.47, 0.72]** (pooled capped mean evaluations, two-way build × cell
    bootstrap; pre-stated rule upper < 0.80 → met). Below 1 in 18/18 cells and 22/24 builds (builds 5 and 20 at
    1.17 and 1.14). Worker seconds 0.535 [0.42, 0.69]. Development cells (descriptive) 0.583 [0.39, 0.86].
  - R-all ÷ R-order (transported 1228 order libraries) 0.516 [0.44, 0.61]: an incremental advantage of the new
    acquisition over owned order content is resolved on this family.
  - R-order ÷ R-tree 1.12 [0.94, 1.34] (reviewer's computation, not pre-stated): no saving from the order
    libraries; a 20% saving excluded, harm unresolved under the two-way unit (11/18 cells above 1).
  - R-gate ÷ R-tree 0.246 [0.21, 0.30]; R-all ÷ R-gate 2.34 [1.99, 2.76]: the supplied helper prior stays far
    ahead.
  - Library content (descriptive): 8.6 of 24 helpers kept per build (5–14); 37.4 entries per build, 255/897 with
    IF_GT. Needed-helper coverage on protected cell × build pairs: both 51, one 191, none 190; R-all ÷ R-tree by
    stratum 0.31 / 0.47 / 0.77, confounded with build and library size; part of the saving occurs with no needed
    helper present. Source own-helper census 37.1% (21.8% emittable), replicating stage 0.
  - Economics: repays acquisition after about 66 [46, 110] searches against R-tree; 51 [40, 69] against owned
    order libraries.
  - R-tree first-attempt solving 97.7% (easy targets; [50](../50-library-easy-target-harm/question.md)'s condition
    met, no harm from R-all or R-gate in any cell).
  Decision: close 58, return to strategy, because the pre-stated primary comparison is resolved (the frozen R-all
  recipe cut search cost on a second, freshly frozen content family) and the transport contrast is resolved too,
  so no extra run on this bank would change a decision; root 10's allocation is used. Scope: one construction
  (`p(a,b)+n(c,d)` input rebindings in D625), easy destinations, one extractor and search regime; helper causality
  and the ~2.3× gap to the supplied prior are unexplained.
- 2026-10-11 (steward, 2044): wording correction after [critique 2044](../../../runs/2026-10-11-2044/critique.md)
  notes 6–7; no number changed. (1) The 1938 entry's "no saving from the order libraries" overstates R-order/R-tree
  1.12 [0.94, 1.34]: read "no resolved saving; a 20% saving excluded, harm unresolved". (2) question.md said
  explanation (e) "did not occur" because development and protected point ratios both round to 0.58; the intervals
  ([0.39, 0.86] development, [0.47, 0.72] protected) do not establish equality. Read: "the protected result
  independently met the usefulness rule, with a point estimate similar to development". Both fixed in
  question.md. The 1938 bank is now a development bank: its protected cells have been scored. The hard tier of this
  family is now [59](../59-signed-chain-depth/question.md) (probe 2044; 58 stays closed).
