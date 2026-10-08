---
node: questions/10-compositional-map-transfer/26-then-addition-fresh-bank
title: Frozen comparison-gate fits (C vs T) on a fresh then-addition bank, with v1's frozen holdouts as a development row
bank: then-addition-v1
---

**Question.** On comparison-gate-v1's training cells, corpus context C beat the token-only fit T
to the same tapes by 3.11× [2.78, 3.48] over 16 corpora ([1246](../2026-10-08-1246/analysis.md)).
v1 is a development bank ([1534 critique](../2026-10-08-1534/critique.md)), so this run scores the same frozen tables on a **fresh bank
of a new shape**, then-addition `A>B ? C+D : E`. It has the same 13-token inventory, with the sum in the
*then* branch, where neither training shape puts it. Does C's advantage survive a new
arrangement of parts?
([26](../../questions/10-compositional-map-transfer/26-then-addition-fresh-bank/question.md))

**Closest technique.** [Ardeh et al. 2020](https://gpbib.cs.ucl.ac.uk/gp-html/Ardeh_2020_CEC.html)
learn a distribution of good programs on source problems and reuse it on a changed target.
Its model lineage is [N-gram GP](https://repository.essex.ac.uk/9722/1/ces-479.pdf) and
[PIPE](https://pubmed.ncbi.nlm.nih.gov/10021756/). The subtree-transfer alternative is
[Dinh et al. 2015](https://gpbib.cs.ucl.ac.uk/gp-html/Dinh_2015_CEC.html). Here the map adapts
by external fitting, frozen, and populations start fresh. This is a **transfer test** of a known
procedure, with a same-corpus token control and 16 corpora.

**Fresh bank (semantic probe this cycle, no search).** research/main's `screen_domain` on all 240
then-addition programs: 86 distinct non-constant behaviours remain, and
37 survive v1's ≤9-token alias screen. Most of those are tie-level variants of gate-swapped BE
cells. **16 agree with every v1 behaviour on fewer than 80% of inputs** (S3 M5 m4 F4; gates F>m
and M>F; [list](../../questions/10-compositional-map-transfer/26-then-addition-fresh-bank/log.md)).
The bank is all 16 cells (minus any exact 1603-bank alias), checked in Rust and Python, and SHA-pinned
before any search. No G4 timing or screening touches them; smoke runs use v1 training cells only.

**Arms and unit.** The 32 tables come from 1246's `corpora.json`, hash-checked against
`freeze.json`, with no refit. Cap 524 288, P 256, exact D1331 check. The unit is the corpus
(n = 16, 8 per family).
- *Row F (primary).* Each corpus's C and T runs on 16 cells × 8 paired seeds, from a new seed
  base: 4 096 searches. G4 runs 16 seeds per cell (256 searches, descriptive).
- *Row D (secondary).* 1246's frozen 4 352-search roster on v1's eight holdouts, unchanged.
  It reports within-shape generalization on a development bank, never transfer, and answers 25.
- Both rows use 1246's balanced prefix: BE*i*/PA*i* corpus pairs in order, ≥ 6 complete pairs or
  "incomplete", and no fallback after an error.

**Feasibility and cost.** These numbers are measured in 1246.
- Worker time per training search: C 5.5 s, T 11.2 s, G4 13.5 s. Unsolved searches average
  28.5 s (max 85 s), on 9.57 effective workers.
- Row F takes about 66 min at training difficulty, and 3.6 h if every search hits the cap.
- Row D: 66 min projected, the same 3.6 h ceiling.
- Timeouts are F 4 h and D 3.5 h: 7.5 h, under the 8 h limit. The expected queue is about 2.2 h.

Fresh-cell solve rates are unknown. On v1's 13-token cells G4 solved 68%. Agent time is about
3 h. Total 6–10 h of the 40 h left; one of root 10's four granted slots.

**Primary comparison (row F).** Fresh C/T = exp(mean over corpora of [mean over 16 cells × 8
paired seeds of log cost_T − log cost_C]). Unsolved runs count as 2 × cap, and families are
weighted equally. The interval is a 95% t over 16 corpora. The rules apply in this order:
1. **LB > 1.0:** C's advantage over T transfers to a fresh bank of a new shape, at this
   procedure's scope. If UB < 1.10 as well, report it as resolved but below 10%.
2. **UB < 1.10:** the gain is bounded below 10%. C's advantage is then tied to the fitted shapes
   (explanation B). Not absence.
3. **Otherwise unresolved.** Report the number of extra corpora needed (423 s each, plus scoring).

**Guard.** If C and T solve fewer than 25% of fresh searches, the ratio describes a capped
endpoint, not speed. Solve counts always accompany the ratio.

**Secondaries (intervals only).**
- Row D C/T. Together, rows D and F separate within-shape from cross-shape transfer.
- Per-cell C/T, with a leave-one-cell-out range.
- BE-fitted minus PA-fitted log C/T, 8 vs 8 corpora.
- Shrinkage from training.
- 1 × cap sensitivity; C/G4 and T/G4 (unpaired).

At a per-corpus sd of 0.30 log (training: 0.21), the half-width is ×1.17, so a true 1.3× resolves.

**Expectation.** Fresh C/T of about 1.3–2× (resolved), below row D, with BE-fitted tables slightly
ahead because BE also nests a sum in a branch. Surprise: fresh C/T < 1.10 while row D stays large
(C learned shape order, not parts), or no shrinkage.

**Next action.** Build and pin the bank, add both rows, smoke on training cells; no fresh-bank
or holdout search before the queue. If the result is positive, score K
on the fresh bank to test token order. If it is bounded, context transfer is shape-specific, and
the question returns to strategy.
