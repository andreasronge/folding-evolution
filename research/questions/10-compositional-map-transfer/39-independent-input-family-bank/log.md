# Log: 39 independent-input family bank

2026-10-10 (steward, run 2026-10-10-0311): opened under strategy 0311 (autonomous run 2026-10-10-1419).

**Read-only semantic probe** ([script](../../../runs/2026-10-10-0311/independent_input_probe.py), 127 s, research/main `b6d1974`):
- Setup: D625; SUM/MAX/MIN/FIRST reinterpreted as X0–X3 in the semantic machine only.
- Behaviours: 492 distinct active double-gate behaviours, 72 of them with four distinct predicate indices.
- Screen: the ≤ 9-token screen kept whole-list sum and ANY, so it is conservative. It removes all collapsed predicates and leaves 48, all proper. The aliases it found have witnesses of 6–9 tokens.
- Separation: the exact maximum set at < 80% pairwise agreement has 24 cells. It is an observation, not a validated bank.

Note: G4's after-INPUT row already gives equal mass to {5+11}, 18, 22 and 23. Mapping 5 and 11 → X0 therefore keeps G4 unchanged as the prior.

Decision: propose stage 1 as a probe, because it settles the bank, discovery and price questions the strategy names. The probe has these parts:
- build `v2_x4` and the bank, with a 4/4/8 split;
- 8 pilot A8 builds;
- development scoring of G4, A8 and old-family A8′ (O) under a declared reinterpretation.

2026-10-10 (steward, run 2026-10-10-0311): **stage 1 probe ran** (commit `09c850d`, code review pass;
[analysis](../../../runs/2026-10-10-0311/analysis.md), [execution](../../../runs/2026-10-10-0311/execution.md)).
Descriptive probe; every number below is an observation on development cells, not a belief.

- **Bank.** `x4-double-gate-v1` under `v2_x4`: the real-token ≤ 9-token screen kept 48 of 492 behaviours,
  maximum separated set 24 (as in the semantic probe). Frozen split 4 source / 4 development /
  8 protected, 8 cells spare. Python, Rust and the semantic machine agree on all 492 canonicals and
  witnesses, 7 240 depth-3 programs and 10 000 random tapes. Sources cover pairings {01|23} (3) and
  {03|12} (1); development adds one {02|13} cell; protected has {01|23} 3, {02|13} 3, {03|12} 2.
  Protected cells unscored.
- **Discovery.** First-batch G4 solved 22/128 (17.2% [11.6, 24.7]); per-build median 2.5/16, below the
  pre-stated 4/16 reading, so the *discovery obstacle* reading applies. Four of eight builds had an
  empty intermediate library (C4 only). The adaptive batch under C4+F4 solved 81/128 (63% [55, 71]);
  every build ended with a full 32-fragment library (fragments 3–6 tokens; canonical is 16).
- **Development scoring** (4 cells × 16 shared seeds per arm, failures charged 2 × cap): solved G4 7/64,
  A8 55/64, O 22/64. G4/A8 12.2× [6.7, 20.7] (1 × cap: 7.3×), A8 cheaper in every cell, including the
  {02|13} cell no source shares. G4/O 1.8× [1.3, 2.5]; O/A8 6.7× [3.5, 12.5]. 57/64 G4 searches hit
  the cap, so the magnitudes are penalty-driven; the ordering is not. G4 headroom 10.9% [5.4, 20.9],
  at the band's lower edge.
- **Spread.** Between-build SD of A8 log cost 0.79 (factor 2.2); builds 3 and 5 solved only 4/8 and 5/8.
- **Cost.** 448 searches, 9 780 worker-s, 17.4 min queue wall at 9.2–9.5 effective workers (55 min of
  timeouts). Acquisition about 694 worker-s per build. Runtime admission worked under load, fixing
  0145's timing defect for this harness.
- **Price for protected scoring** (conditional on development variance): 53–64 builds for a ±1.25×
  half-width, about 2 h compute; a margin test at 1.5× needs far fewer (see decision).

Against expectations: discovery inside the expected 15–35% pooled but below the 4/16 median reading;
G4/A8 far above the expected 1.5–3× (censoring); O between G4 and A8 as expected. No named surprise.

Decision: close 39 because its question is answered at this scope: the independent-input bank
supports a fair, protected test, source discovery is sparse but the unchanged recipe still completes
every build, G4 leaves (just) measurable headroom, and the protected comparison is priced. The pilot
signal (A8 ≫ G4, O ≪ A8 on four development cells) motivates the protected-cell confirmation, opened
as [40](../40-independent-input-protected-transfer/question.md); it is not a belief and does not
enter the digest. Strategy 0311 asked for a return to strategy after this stage, so the decision goes
to strategy with the stage-2 design as the steward's suggestion.
