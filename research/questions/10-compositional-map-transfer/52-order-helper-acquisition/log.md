# Log: 52 order-helper acquisition

- 2026-10-11 (steward, 1129): opened on [strategy 1129](../../../runs/2026-10-11-1129/strategy.md) and the
  [order-helper plan](../../../plans/order-helper-acquisition.md). Read-only stage 0 at `e29219b`, off-harness
  ([notes and scripts](../../../runs/2026-10-11-1129/stage0/README.md)): sources easy (71/72, ~3 k evaluations);
  R-tree 10/18 on 3 destinations at a single 65,536 attempt (capped mean 34.4 k); R-order 18/18, mean 1.4 k (near
  floor); unchanged extractor: helper entries in 1/4 pilot builds, and helper-free builds solved fewer destinations
  than R-tree (4–5/18); 41/71 source solvers contain a subtree computing their own helper on D625, mostly 10–22
  nodes (11/44 in the 6-node form). Observations, not beliefs. Consequence: "learned beats R-order" is not testable
  on these destinations (floor); the open question is whether acquisition recovers the gap, and whether literal keying is
  the limit. Proposal: harness probe with an added behaviour-keyed extractor on the same sources
  ([proposal](../../../runs/2026-10-11-1129/proposal.md)).

- 2026-10-11 (steward, 1129): **probe run** (`kind: probe`, slot 43, commit `db30b15`, code review pass, queue
  7.5 min of 50 approved; [analysis](../../../runs/2026-10-11-1129/analysis.md),
  [execution](../../../runs/2026-10-11-1129/execution.md)). Bank `x4-order-v1`: 24 sources and 30 destinations
  admitted; 6 development cells searched, 24 protected cells frozen and never searched. The 12 `hi(a,b)+Xc` sources
  are ≤ 9-token near-aliases at 84% agreement; admission excluded only exact aliases (code review note 1), so a later
  protected study must state which rule it freezes. Acquisition: 8 builds × 24 sources × 2 R-tree jobs, 384/384
  solved (mean 4.2 k evaluations). Scoring: 5 arms × 6 cells × 16 paired seeds (96 jobs per arm), ≤ 8 × 65,536.
  **Observations (descriptive, development cells only).**
  - Geometric mean evaluations: R-tree 38.7 k (96/96 solved, 56% first attempt) · R-order (12 supplied helpers)
    1.87 k (96/96, 95%) · R-sum (1019 prior) 82.2 k (93/96) · R-L (unchanged literal extractor) 60.0 k (94/96) ·
    R-S (behaviour-keyed extractor) 38.8 k (93/96). Paired ratios against R-tree (pair bootstrap; cell-cluster
    interval in the analysis is similar): R-order 0.048× [0.04, 0.06]; R-sum 2.12× [1.54, 2.91]; R-L 1.55× [1.09,
    2.17]; R-S 1.00× [0.68, 1.46]; R-S/R-L 0.65× [0.43, 0.97]. R-tree → R-order gap 3.03 nats (20.7×); gap recovered
    R-S −0.001, R-L −0.14. Pre-stated routing rule (helper in ≥ 6/8 builds and ≥ 50% gap) not met by either arm.
  - Acquisition: R-L held an order helper in 0/8 builds; R-S in 3/8 (a destination-needed one in 2/8). Of 96
    helper × build cases under R-S: 26 not recurrent in ≥ 2 cells, 21 recurrent only in > 9-node forms (emission
    size), 44 admissible but ranked 17–32 (cap crowding), 5 included. Under R-L the 6-node literal recurred in only
    5/96 cases, never inside the cap: the same behaviour is written in different syntaxes across solvers. The crowd
    is 3-node pair sums, `GT` comparators and one semantically constant class (always 0 on D625), recurring in 3–8
    cells; by bank construction each helper can recur in at most 2 source cells.
  - Census: 242/384 source solvers (63%) contain a subtree computing their own helper; 91 have an emittable
    (≤ 9-node) form, 151 only 10–23-node forms. Evolution builds the helper; availability is not the limit.
  - Post-hoc build split (suggestive only): in the two builds holding a needed helper R-S/R-tree 0.67× [0.33,
    1.31] (24 pairs); in builds with no helper 1.14× [0.69, 1.85] (60 pairs). Usefulness of an included helper is
    neither shown nor refuted.
  - Donor libraries of irrelevant 3-node content raised cost on a target R-tree solves only 56% first time
    (R-sum 2.12×, R-L 1.55×, intervals exclude 1): library harm is not only an easy-target effect (cf. 50).
  Read against the explanations: (a) nothing to extract — not supported (census 63%); (b) literal keying — the
  limit for the unchanged recipe (5/96 vs 49/96 recurrent admissible cases); (c) crowding under cells-first ranking
  and the 16 cap — the first limit for behaviour keying, with emission size behind it. R-S changes keying, pooled
  sizes and representative choice together, so (b) implicates that bundle, not keying alone. All of this is one
  probe on six development cells; none of it enters the digest as a belief.

  Decision: park 52 because the probe answered its routing question — the unchanged recipe acquired no order helper
  in 0/8 builds and recovered none of the 20× gap to a supplied order prior, with the limit located (literal keying,
  then cap crowding, then emission size) — and the pre-stated rule sends it back to strategy rather than to a
  protected comparison. Whether relieving the ranking/cap turns acquired helpers into a search saving is a new
  extractor-mechanism question that strategy 1129 reserved for its own review (no variant sweeps), and root 10's
  43-slot budget is spent.

- 2026-10-11 (steward, 1228): wording corrections from [critique 1228](../../../runs/2026-10-11-1228/critique.md)
  digest check, notes 6–8; the 1129 entry above stays as written and is corrected here. (6) "neither learned arm
  recovered any of that gap" holds for the point estimates only: neither met the probe's continuation rule, and
  R-S's benefit was unresolved (1.00× [0.68, 1.46]), not shown absent. (7) "by bank construction each helper can
  recur in at most 2 source cells" overstates: construction makes each helper required by two source targets; it
  was observed only in those targets' solvers (0 non-own helpers in 384), which is a finite observation, not a
  structural ceiling. (8) "availability is not the limit" overstates: the census refutes "nothing to extract", but
  26/96 helper × build cases were nonrecurrent and 21/96 lacked an emittable form; helpers are often present, and
  literal pooling, cap crowding, nonrecurrence and emission size restrict usable coverage. Question summary updated.
- 2026-10-11 (steward, 1228): follow-up [53](../53-order-library-cap-release/question.md) (run 1228, commit
  `60ab766`, full pre-registered experiment, 24 new builds) removed R-S's 16-entry cap: R-all / R-tree 0.40 [0.32,
  0.50] in capped arithmetic mean evaluations, R-all / R-S 0.33 [0.27, 0.39], R-S / R-tree 1.23 [1.07, 1.41]; a
  needed helper in the pool in 126/144 cell × build pairs (R-S 14/144). This confirms, at experiment level, that
  cap crowding blocked useful behaviour-keyed acquisition here (helper causality not isolated).

  Decision: close 52 because its question is answered on these development cells — the unchanged literal recipe
  did not acquire order helpers (probe), and the behaviour-keyed recipe did and saved search once the cap was
  removed (53) — and further work with the uncapped extractor is a separate question.

- 2026-10-11 (steward, 1315): wording correction after [critique 1315](../../../runs/2026-10-11-1315/critique.md)
  (digest check, note 5). The summary's "the unchanged literal recipe does not acquire them here" and the reopen
  text's "literal reuse is known to fail" turned eight capped literal libraries with zero helpers into absence.
  Now: no order helper entered the eight capped literal libraries in the 1129 probe; the uncapped literal recipe is
  untested. No numbers change.
