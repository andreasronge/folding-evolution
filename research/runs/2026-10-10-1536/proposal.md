---
node: questions/10-compositional-map-transfer/40-independent-input-protected-transfer
title: Fresh A8 builds on the independent-input double-gate family, scored on its protected cells (stage 2)
bank: x4-double-gate-v1
---
**Question and mechanism.** Does the unchanged A8 recipe (four G4 attempts per source cell → fit
C4+F4 → four more attempts under it → refit on all eight), rebuilt on a family with addition
*inside* the predicate, `(Xa+Xb)>(Xc+Xd) ? Xe:Xf` over four independent readouts (`v2_x4`, D625),
give fresh populations a worthwhile frozen speed-up on its held-out members? Earlier A8
successes were all output-addition families. [Strategy](strategy.md) allocated exactly this test. The [stage-1 probe](../2026-10-10-0311/analysis.md)
saw G4/A8 12.2× [6.7, 20.7] on four development cells (7.3× at 1 × cap; 57/64 G4 searches capped),
an observation only. The 8 protected cells, SHA-frozen in 0311, have never been searched; three use
the predicate pairing {02|13}, which no source cell has.

**Closest technique.** [PIPE (Salustowicz & Schmidhuber 1997)](https://gpbib.cs.ucl.ac.uk/gp-html/Salustowicz_97ecj.html):
search outcomes update a program-generating distribution. A8 is **external fitting** (a
previous-token context table plus a literal fragment library), then frozen reuse; nothing is
selected or inherited. [DreamCoder (Ellis et al., PLDI 2021)](https://people.csail.mit.edu/asolar/papers/EllisWNSMHCST21.pdf)
is the richer relative. This is a **boundary/replication test** of a known recipe: does it carry
over to a different assembly requirement, judged on unseen cells?

**Arms (unit = acquisition build; fixed seeds).** The runner at `09c850d` (research/main),
unchanged except for a protected-scoring mode, the build count and fresh seed blocks (disjoint
from 310k–333k and smoke 390k/420k): sources 500000 / 600000 + 1000·build + 10·cell + attempt,
scoring 700000 + 1000·cell + ordinal. Cap 524 288, P 256, 64 lexicase cases, exact check on all
625 inputs; failures and empty-cell/library fallbacks kept as in 0311.
1. **A8″:** 24 fresh builds from the same 4 source cells.
2. **G4:** the fixed prior, run alongside.
3. **O (descriptive):** the same eight reinterpreted 0145 A8′ builds as in stage 1.

Scoring: 8 protected cells × 48 shared seeds for G4 and A8″ (build = ordinal // 2, so 2 seeds
per build per cell); O on the first 16 seeds per cell (2 per artifact). 384 + 384 + 128 = 896
searches. Method, builds, seeds and roster are hash-frozen before the first protected search;
pilot builds are not reused; nothing is tuned on protected scores.

**Feasibility (0311, under load).** Acquisition 694 worker-s per build (first batch 22/128
solved; all 8 builds still ended with full 32-fragment libraries). Per search: G4 30, A8 9.2, O 26.9 worker-s; 9.2–9.5 effective workers.

**Full cost.** Acquisition 24 × 694 ≈ 16.7 k worker-s ≈ 30 min; scoring 18.5–22.7 k worker-s
(A8 at 9–20 s if protected cells are harder) ≈ 33–41 min. Two entries, timeouts 50 + 70 min = 2 h.
Agent time 2.5–3 h; 4.5–5 h in total, well inside the 46.6 h left.

**Primary comparison and decision rule.** R = cost(G4)/cost(A8″), the geometric mean of capped
cost over the 8 protected cells, failures charged at 2 × cap (as in 37/38/0311). The 95% interval
comes from a build-resampled bootstrap: builds resampled, seeds resampled within build and cell,
and one shared cell-stratified G4 seed draw per replicate, so both build and baseline uncertainty
are kept. Pre-set margin 1.5×:
- lower bound > 1.5 → **useful transfer to the new family** (relative to G4 at this cap);
- upper bound < 1.5 → **not worthwhile at this margin**: the unchanged recipe's portability is bounded;
- otherwise **unresolved**, reported with a resolution price, not as equality.

A label that changes at 1 × cap is called penalty-sensitive. Precision: at the pilot's
between-build log variance (0.63) and G4 seed variance (0.33), the conservative half-width factor
is about 1.43, so a true R of about 2.2× or more should clear 1.5 (planning, not a guarantee).

Reported without a rule: solve fractions (Wilson intervals; penalty-free); per-cell results; R
for the 3 unseen-pairing cells and the other 5 (descriptive); G4/O and O/A8″; per-build first-batch
yield and empty-intermediate-library rate against target cost; repayment as arithmetic
acquisition-plus-search evaluations, charged once per build. No wall-time claims; 0145's
calibration is not reused.

**What I expect.** R clearly above 1.5 (point 4–10×, smaller at 1 × cap); A8″ solving most
protected searches, G4 under 20%; unseen-pairing cells helped but less; O between.

**What would surprise me.** R unresolved or below 1.5. Or unseen-pairing cells no better than G4:
that would hint the libraries teach specific predicate pairings rather than double-sum assembly
(3 cells, so only a lead for a follow-up).

**What it cannot show.** Context versus fragments versus supply; family specificity (O's token
reinterpretation); predicate placement alone (alphabet, domain and family changed together);
inheritance. G4 is a supplied prior, not a proven competitive baseline here.

**Next action.** Useful: the recipe extends beyond output addition at this scope. Return to
strategy, which can weigh a crossed-family test in the same alphabet, PSB2 or root 23.
Unresolved: price the resolution. Not worthwhile: locate the failure (discovery or fit) from
per-build data before any redesign. Always exit to strategy.
