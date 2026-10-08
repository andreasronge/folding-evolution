---
next: strategy
---
# Decision: run 2026-10-08-1831

**Close [27](../../questions/10-compositional-map-transfer/27-partial-program-context/question.md),
answered at its scope. Write no proposal: [strategy 1831](strategy.md) allocated only this first
stage and asked for a review after it, and the follow-up it named (bounded feedback, 8–12 h) is
not allocated. Hand it to the strategist with a priced recommendation.**

Why:
- The run was complete and clean: 7 168 rows, 16/16 corpora (8 balanced BE/PA pairs), 89 536
  archived tapes all verified non-exact, 0 holdout searches, 120 min against a 144-min projection
  ([analysis](analysis.md), [code review](code_review.md): pass).
- The pre-stated rule routes to **useful partial-program context**: C_S/T_S **1.28× [1.12, 1.45]**
  (upper bound not below 1.20; lower bound above 1) and C_S/G4 **1.62× [1.37, 1.90]** (16/16
  corpora). A worthwhile 1.20× over T is plausible, not established.
- Three qualifications travel with the label:
  1. The C-over-T gain shows up mostly as more searches solving within the cap (73% vs 66%); on
     pairs where both solved it is 1.05× [0.88, 1.24]. The both-solved subset is
     selection-conditioned, so this is a decomposition, not a separate test. C_S/G4 holds there too
     (1.41×).
  2. It is BE-carried: BE 1.42× [1.17, 1.72], PA 1.15× [0.96, 1.38], unresolved. Two of eight
     cells are below 1, the ones T already solves most.
  3. The exact-solver fit stays much better: C_S/C_exact 0.27× [0.24, 0.30], with C_exact using
     about 7.9× more source evaluations per cell (15.3M vs 1.94M, computed from both runs'
     `search.jsonl`). Unequal budgets, so this is not a per-evaluation efficiency comparison.
- No parent-selection enrichment was resolved (C_S/C_P 1.04× [0.92, 1.16]) even though selected
  tapes are much more accurate (D1331 0.68 vs 0.49). Any useful signal sits in the evolved
  population at large, at this resolution.
- Resolving the 1.20× margin (≈ 64 corpora, ≈ 6 h queue plus agents, and only if the point
  estimate held) or PA alone would not change the next choice, so it is not recommended.

**Belief changes.** The digest gains one bullet under root 10 (scope: own training cells of a
development bank, one collection horizon, external fitting, K unscored) and an amended overall line.
Critique 1831 notes 6–7 are fixed: the 1.38× in 26, root 10 and the digest is now described as
a ratio of C/T ratios; 25 says no holdout had been searched when the roster was frozen.

**Parked questions.** None reopens. Root 23's condition needs a changed inheritance rule with a
measured selectable signal; this run is external fitting on another system. It is still relevant
to root 23: token frequencies of evolved, not-yet-solving populations already beat G4 (T_S/G4
1.27× [1.10, 1.45]). That is a population-level signal, not a per-individual one, and it bears on
the owner note's deferred "competing population-level maps" item. Root 01's threads have no new
evidence.

**Recommendation to the strategist (root 10 has 2 of 20 slots left; ≈ 34 h to the deadline).**

| Candidate | Cost (incl. agents) | Value |
|---|---|---|
| **Bounded partial-program feedback** (the plan's stage 2) | 8–12 h, one slot | **Recommend.** The real question now is whether repeated refitting to the population's own unfinished programs moves toward the exact-fit level (0.27× gap) at much lower acquisition cost. That would be a working EDA-style acquisition loop without exact solvers. Design points to settle: (a) as the decoder improves, more sources solve before checkpoints. The rule for excluding solvers then starves later rounds, so fix shorter checkpoints or a per-round evaluation budget in advance; (b) compare against a one-shot fit at equal total source evaluations (retain-first-fit arm), plus a token-feedback arm; (c) P samples suffice (C_P ≈ C_S), which simplifies collection; (d) freeze, then score on training cells. Transfer stays a later, fresh-bank question. |
| Fresh-bank transfer of partial fits | unpriced: needs a new shape screened and frozen with the method (then-addition is development data now) | Defer until a partial or feedback method is worth transferring. |
| Score frozen K on 1548's fresh-bank rows | ≈ 1 h queue + ≈ 3 h agents | Defer, as before. It does not touch acquisition. |
| Resolve 1.20× / PA for this collector | ≈ 6 h queue + agents | Do not run. It would not change the feedback choice. |
| Longer collection horizon | ≈ 3–4 h | Do not run on its own. The plan warns against drifting back into exact-solver fitting by extending collection. |

If the strategist funds feedback, the steward opens it as a new sub-question (28) with one slot.
