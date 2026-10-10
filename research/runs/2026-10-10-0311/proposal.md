---
node: questions/10-compositional-map-transfer/39-independent-input-family-bank
title: Independent-input double-gate bank, source discovery and pilot acquisition (stage 1)
bank: x4-double-gate-v1
kind: probe
---
**Question.** This follows the [strategy](strategy.md) and [plan](../../plans/independent-input-family-acquisition.md). Can the unchanged A8 recipe learn from a family with addition inside the predicate, `(Xa+Xb)>(Xc+Xd) ? Xe:Xf`, over four independent indexed readouts? A8 means four G4 attempts per source cell → C4+F4 → four more attempts under it → refit. This stage checks only the preconditions: a protected split, source discovery, headroom, a development-cell pilot signal and a measured stage-2 price. Protected cells stay unscored.

**The semantic obstacle is cleared in Python.**
- Probe: [script](independent_input_probe.py), [result](independent-input-probe-keep.json), 127 s on `b6d1974`. D625 (length-4 vectors over −2..2); SUM/MAX/MIN/FIRST reinterpreted as X0–X3 in the semantic machine.
- 492 distinct active behaviours; 72 have four distinct predicate indices.
- A conservative exhaustive ≤ 9-token screen (whole-list sum and ANY kept) removes every collapsed predicate and 24 proper ones, leaving 48.
- **The maximum pairwise-separated set (< 80% agreement, exact clique) has 24 cells**, covering all three pairings. The earlier candidates gave 6 and 4 ([audit](semantic-split-audit.json)).
- Rust validation is still to do.
- The canonical is 16 tokens, the same as two-sum, where G4 solved 20% at the 524k cap. Discovery under the new alphabet is unmeasured.

**Closest technique.** [PIPE (Salustowicz & Schmidhuber 1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/) updates a program distribution from successful searches. A8 is external fitting of that kind (context plus fragment library, reused frozen), not selection or inheritance. This is a boundary test of a known method on a new bank, plus a check that old-family builds don't already carry the help.

**Build (≤ 120 min preparation).**
- **Alphabet `v2_x4`**, named in every artifact. Tokens 5 and 11 → X0; 18 → X1; 22 → X2; 23 → X3.
  - Explicit wrong-type and empty-input rules.
  - Python, Rust and semantic machine; legacy alphabets must replay.
  - Under this mapping the unchanged G4 already gives every readout equal mass (3 625), so **G4 itself is the fixed prior**.
- **Bank `x4-double-gate-v1`.**
  - Run the screen with the real tokens and take the maximum separated set.
  - Make a deterministic, hash-ordered split before any search: 4 source, 4 development, 8 protected.
  - Sources span ≥ 2 pairings and use every Xi as an output. The protected cells span all three pairings.
  - Validate the canonicals in both executors and freeze by SHA.

**Arms (fixed seeds; unit = build).** The 0145 acquisition code is used unchanged: cap 524 288, population 256, 64 lexicase cases, exact 625-input check.
1. **Sources.** 8 independent A8 pilot builds: 128 G4 attempts, then 128 under C4+F4. These 64-job batches also measure throughput under load, which fixes 0145's admission defect.
2. **Development scoring.** The 4 development cells, 16 seeds per cell per arm:
   - **G4**;
   - **A8**: 8 builds × 2 seeds;
   - **O**: 8 frozen 0145 A8′ builds (4 BE, 4 PA), run under `v2_x4` with token ids unchanged. This is a declared reinterpretation: old fragments like `INPUT SUM INPUT MAX ADD` become readout sums.

**Feasibility and cost.**
- 0145 measured G4 at 22.6 worker-s per search, A8 at 17.3 and sources at 205 per build, with about 9.4 effective workers.
- This stage has 448 searches, about 11 000 worker-s: about 20 min of compute.
- Queue timeouts sum to 55 min (probe cap 60): 25 min for bank and sources, 30 min for scoring.
- About 2.5 h of agent time, so about 3.5 h in total.

**Outputs (descriptive).**
- Per source cell: first-batch and adaptive solve rates.
- Per build: acquisition evaluations.
- Exact-check tail times.
- G4's development solve fraction.
- cost(G4)/cost(A8) and cost(O)/cost(A8), with build-resampled intervals (log capped evaluations, unsolved = 2 × cap).
- Between-build log-SD.

**Readings stated now** (feasibility, not verdicts):
- **Bank obstacle:** fewer than 12 separated cells after the real screen or Rust validation. The candidate stops; the screen is not relaxed.
- **Discovery obstacle:** median first-batch G4 yield below 4/16 per build. Report it; do not raise the attempt count.
- **Headroom:** G4's development solve fraction lies in 10–80%.
- **Stage-2 price:** the number of builds whose protected G4/A8 interval has a half-width factor ≤ 1.25 at the measured log-SD, costed under measured load.
- **O/A8:**
  - Unresolved from 1, with a point ≥ 0.9: the old syntax already carries the help, and stage 2 must include O.
  - O clearly costlier: fresh acquisition is needed.

**What I expect.** First-batch discovery of 15–35%. G4/A8 of 1.5–3× on development cells. O between G4 and A8, since it shares the push/ADD/GT syntax but not the double sum.

**What would surprise me.** A8 no better than G4, or O as good as A8.

**Next action.** Return to strategy with the frozen split, the measured price and the O reading. Stage 2 needs its own allocation. I open [39](../../questions/10-compositional-map-transfer/39-independent-input-family-bank/question.md) with a budget of 1.
