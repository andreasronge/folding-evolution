---
node: questions/10-compositional-map-transfer/40-independent-input-protected-transfer
title: Fresh A8 builds on the independent-input double-gate family, scored on its protected cells (stage 2)
bank: x4-double-gate-v1
---
**Question and mechanism.** Does the unchanged A8 recipe (four G4 attempts per source cell → C4+F4 →
four more attempts under it → refit), rebuilt on a family with addition *inside* the predicate,
`(Xa+Xb)>(Xc+Xd) ? Xe:Xf` over four independent readouts, give fresh populations a worthwhile frozen
speed-up on held-out members of that family? All earlier A8 successes used output-addition families.
The [stage-1 probe](../2026-10-10-0311/analysis.md) cleared the bank, measured sparse first-batch
discovery (22/128) and saw G4/A8 12.2× [6.7, 20.7] on four development cells, inflated by G4
censoring. That is an observation on hash-chosen development cells; this run is the confirmation on
the 8 protected cells, frozen by SHA in run 0311 and never searched.

**Closest technique.** [PIPE (Salustowicz & Schmidhuber 1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/):
search updates a program distribution. A8 is external fitting (previous-token context plus a literal
fragment library), reused frozen; nothing is selected or inherited. Library learning
([DreamCoder, Ellis et al. 2021](https://people.csail.mit.edu/asolar/papers/EllisWNSMHCST21.pdf)) is
the richer relative. This is a **boundary/replication test** of a known
recipe on a new family; it adds whether the recipe's portability extends beyond output addition.

**Arms (unit = acquisition build; fixed seeds).** Code from `09c850d` unchanged except a protected-
scoring mode, build count and fresh seed blocks (disjoint from 310k–333k and smoke 390k/420k, e.g.
sources 500000/600000 + 1000·build + 10·cell + attempt, scoring 700000 + 1000·cell + ordinal). Cap
524 288, P 256, 64 lexicase cases, exact D625 check.
1. **A8″:** 24 fresh builds from the same 4 source cells, empty-cell/library fallbacks unchanged.
2. **G4:** the fixed prior.
3. **O (descriptive):** the same 8 reinterpreted 0145 A8′ builds as stage 1.

Scoring: 8 protected cells × 48 shared seeds for G4 and A8″ (build = ordinal // 2, 2 seeds per build
per cell); O on the first 16 seeds per cell (2 per artifact). Total 384 + 384 + 128 = 896 searches.
Method, artifacts, seeds and roster frozen by hash before the first protected search; pilot builds are
not reused.

**Feasibility (measured in 0311).** Acquisition 694 worker-s per build (sparse first batch included);
G4 30, A8 9.2, O 26.9 worker-s per search; 9.2–9.5 effective workers under load; all eight pilot builds
completed full libraries despite four empty intermediate libraries.

**Full cost.** Acquisition 16.7 k worker-s ≈ 30 min; scoring 18.5–22.7 k worker-s (A8 at 9–20 s per
search, protected cells may be harder) ≈ 35–41 min. Two queue entries, timeouts 50 + 70 = 2 h
(< 8 h cap). Agent time ≈ 2.5–3 h (small runner change, smoke, review, analysis). About 4.5–5 h in
total, inside the plan's 4–6 h stage-2 allowance.

**Primary comparison and decision rule.** R = geometric capped cost(G4)/cost(A8″) over the 8 protected
cells, failures charged 2 × cap, 95% interval from a build-resampled bootstrap (seeds within build and
cell, one shared cell-stratified G4 seed draw per replicate, as in 0311). Pre-set margin 1.5×:
- lower bound > 1.5 → **useful transfer on the new family**;
- upper bound < 1.5 → **not worthwhile at this margin** (bounds portability of the unchanged recipe);
- otherwise **unresolved**, reported with a resolution price, not as equality.

Precision: with the pilot's between-build log variance 0.63 and G4 seed variance 0.33, 24 builds and
48 G4 seeds per cell give a conservative half-width factor of about 1.43 (variance not divided across
cells), so a true R of about 2.2× or more should clear 1.5. If protected cells are much noisier, the
result is unresolved and priced.

Reported without a rule: 1 × cap sensitivity (57/64 G4 rows were capped in the pilot) and solve
fractions with Wilson intervals, which are not penalty-driven; R split into the 3 cells whose predicate
pairing {02|13} no source has and the 5 that share one; G4/O and O/A8″; per-build first-batch yield
and empty-library incidence against target cost; acquisition repayment in evaluations.

**What I expect.** R clearly above 1.5 (point 5–10×, smaller at 1 × cap), A8″ solving most protected
searches where G4 solves under 20%; the unseen-pairing cells helped but less; O again between.

**What would surprise me.** R unresolved or below 1.5; or the unseen-pairing cells no better than G4,
which would suggest the libraries teach specific predicate pairings rather than double-sum assembly
(3 cells: a hint for a follow-up, not a conclusion).

**What it cannot show.** Context versus fragments versus supply, family specificity, or inheritance;
predicate placement in isolation (alphabet, domain and family changed together).

**Next action.** Useful → the recipe extends beyond output addition at this scope; return to strategy,
which can weigh a crossed-family specificity test, PSB2, or root 23 against it. Not worthwhile or
unresolved → place the failure (discovery vs fit) from the per-build data before any redesign.
