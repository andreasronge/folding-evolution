# Log: 59 signed-chain depth

- 2026-10-11 (steward, 2044): opened on strategy 2044. Stage 0 ran off-harness in the 1938 export of `3a18ef5`,
  ~1 min of compute ([notes and scripts](../../../runs/2026-10-11-2044/stage0/README.md)). Observations, not
  beliefs:
  - Four chain cells (lowest label hashes) × 3 repeats: R-tree 12/12 solved, **6/12 first attempt**, up to 7 of 8
    attempts, mean 138 k evaluations (1938 protected R-tree: 7.8 k, 97.7% first attempt). R-gate 31 k (9/12
    first attempt). Two 1938 stage-0 R-all builds 100 k and 101 k.
  - Saved 1938 libraries cover all three needed helpers in 3.3% of build × cell, none in 25%.
  - Worker seconds per job: mean 2–8, max 22.
  - These four cells are seen and join the development roster.
  Proposal: [run 2044](../../../runs/2026-10-11-2044/proposal.md).
- 2026-10-11 (steward, 2044): probe [run 2044](../../../runs/2026-10-11-2044/analysis.md), commit `8a621df`
  (`kind: probe`; observations, not beliefs). Bank `x4-signed-chain-v1`: all 24 destinations admitted (no short
  aliases through nine tokens, max agreement 335/625), 6 development cells (the 4 stage-0 cells plus 2 lowest-hash
  survivors), 18 protected cells frozen with the method and never searched. 24 saved 1938 R-all libraries
  (hash-verified), R-tree, R-gate; 24 builds × 6 cells × 2 repeats = 288 paired jobs per arm, fresh seeds.
  - Hard but not capped: R-tree 272/288 solved, **30% first attempt**, 16 capped, mean 159 k evaluations (1938:
    7.8 k, 97.7% first attempt). R-gate 288/288, max 5 attempts.
  - **R-all/R-tree 0.79 [0.60, 1.03]** (pooled capped mean evaluations, two-way build × cell bootstrap,
    descriptive); worker seconds 0.78 [0.58, 1.00]. Below 1 in 6/6 cells (0.56–0.90), 14/24 builds, 160/288
    paired units. A 40% saving is excluded; any saving and the 0.80 bar are both unresolved. Solves +2.1 points
    [−3, +8], first attempt +6.6 points [−4, +17], both unresolved.
  - **R-gate/R-tree 0.30 [0.23, 0.38]; R-gate/R-all 0.38 [0.27, 0.51]**: the supplied repertoire keeps large
    headroom over the acquired libraries, as on the easy family (0.25).
  - Needed-helper coverage (descriptive, confounded with library size and seed luck; 16 units in the top stratum):
    R-all/cell-matched R-tree 1.02 / 0.81 / 0.64 / 0.37 with 0 / 1 / 2 / 3 of the three helpers present. In 1938
    the no-helper stratum still saved (0.77); here it does not by point estimate.
  - Repayment of 1938's ~216 k acquisition: about 7 searches by point (1938: 66), interval from ~3 to never.
  - Pricing a protected confirmation (18 cells × 24 builds): r = 2, 2,592 jobs, ~38 min central / 76 min with
    doubled tails, 112 min summed timeouts; r = 4, 207 min. The variance model under-predicted the probe's own
    interval (1.54 vs 1.72 width ratio), so the doubled-variance column is the planning anchor (r = 2: 1.60;
    r = 4: 1.53). With a 0.80 materiality rule an r = 2 confirmation is expected to be unresolved for true effects
    between about 0.63 and 1.01 (2×); an "any saving" rule (upper < 1) resolves at r = 2 for true effects below
    about 0.79 (2×) or 0.85 (central).
  - All three recommendation criteria met (hard, not ceilinged, precise and affordable); this is a flag to
    strategy, not an authorisation.
  Against the competing explanations: "linking, not supply, limits search" is not supported (R-gate never capped
  and cost 0.30× of R-tree); acquired helpers versus other library content is not separated, but the
  coverage gradient leans toward helper supply (a hint only).
  Decision: keep 59 open and return to strategy, because the probe did what it was for (a hard, uncapped tier and
  a price), its one slot is used, the strategy and proposal both route a confirmation through a separate
  allocation, and the R-all effect is unresolved at both thresholds that matter. Steward's recommendation for
  strategy is in [decision 2044](../../../runs/2026-10-11-2044/decision.md).
