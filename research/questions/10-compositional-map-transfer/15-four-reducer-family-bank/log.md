# Log: 15-four-reducer-family-bank

- 2026-10-06 (run 2026-10-06-1536, proposal): opened from strategy 1536 (root 10 slot 6). Steward
  probe (`runs/2026-10-06-1536/steward_probes/`, ≈ 2 min and 5 GB per domain): 13/36 cells
  survive the ≤ 9-token, 80% screen on D1331 (5 BE, 8 PA); BE has no role-covered holdout pair
  on D625, D1331 or D2401. Proposal: reviewed screen with Rust FIRST, search calibration of all
  13 cells under U/F4/G4/G4-marg, and the never-run family-grammar capacity diagnostic. A
  learner cost pilot runs only if both families split.
- 2026-10-06 (run 2026-10-06-1536, critique): `revise`. Blocking: the family-grammar contrast
  was used as a necessary condition (rows 1/3 inferred decoder incapacity; row 4 inferred no
  headroom from the hand-set rows not beating G4). Decision: resubmit (run 2026-10-06-1603) with
  the contrast as a descriptive positive witness only; the learner pilot is gated on split,
  G4 headroom and measured cost, not on the contrast; split failure returns the obstacle and the
  contrast intervals without concluding anything about learned specificity.
- 2026-10-06 (run 2026-10-06-1603, ran; Table A row 1). Approved with notes by the critic; commit
  `92ba7c5`, complete data, 43.7 min ([analysis](../../../runs/2026-10-06-1603/analysis.md)).
  Validation passed: brute force to depth 4, 10⁵ random programs Python = Rust, 36/36
  canonicals in Rust on each domain. The screen reproduces the probe exactly: on D1331, 13 of 36
  cells survive (BE 5, PA 8; all 23 drops are near-aliases at 0.84–0.95 agreement). **BE has no
  role-covered holdout pair on D625, D1331 or D2401.** In the `then` role, S, F and M each occur
  once, and the two `then = m` cells leave m uncovered; all 10 pairs fail. One BE cell,
  `S?m:(M+F)`, can be held out alone. PA splits: holdouts `(F?S:M)+m` and `(S?M:m)+F`, 6 training
  cells. Stage B (13 cells × 8 arms × 50 paired seeds, all complete): G4 solves 45–50/50 on
  every cell (KM medians 8.7k–28.7k), U 29–49/50. G4 / U is 10.3× [7.9, 13.5] on BE and 8.1×
  [6.8, 9.6] on PA; G4 / G4-marg is 4.4× [3.4, 5.6] and 3.3× [2.7, 4.0]. Gates (b)–(c) were not
  evaluated because the split failed; recomputed from the rows, both would have passed on PA.
  Gate (d) cost had already excluded stage C after block 1: projected 16 881 s against 9 800 s
  left. That projection includes the frozen 2× allowance; without it about 8 500 s, which would
  have fit. Rows 4 and 5 were unreachable in this queue. Table B, descriptive: matched over
  swapped grammar on BE 1.68× [1.39, 2.05] (W, large), on PA 1.32× [1.12, 1.57] (W). The paired
  context-over-marginal contrast is 1.51× [1.09, 2.09] on BE and 1.46× [1.16, 1.82] on PA. The
  marginal pairs alone are BE 1.11× [0.90, 1.36] (X) and PA 0.91× [0.76, 1.10] (B). Against G4,
  G4-BE is 1.36× [1.04, 1.75] on BE and 0.66× [0.56, 0.77] on PA. **G4-PA does not beat G4 on
  PA** (0.87× [0.75, 1.04]), so the PA witness comes from the BE grammar slowing PA. Decision:
  close 15, because row 1 answers it under the frozen split rule: FIRST does not give a
  role-covered BE split on any of the three domains, so this candidate cannot support the
  symmetric matched/mismatched test. Nothing is concluded about learned specificity. The
  asymmetric options (BE as a training-only family; the single BE holdout `S?m:(M+F)`) change a
  frozen rule after seeing data, so they go to strategy, along with the measured learner cost.
- 2026-10-06 (wording correction from critique 1723's digest check, notes 5–7; no new data).
  In the 1603 entry above, "G4-PA does not beat G4 on PA" should read "no PA improvement over G4
  was resolved (0.87× [0.75, 1.04], admitting gains up to about 4%)". The context attribution
  should read "context strengthens the crossed preference relative to the tied-marginal
  controls; the marginal contrasts alone are unresolved". The stage-C cost was a conservative
  projection, not a measured runtime. question.md updated accordingly. The one-cell BE holdout
  design runs in 16, not here; 15 stays closed.
