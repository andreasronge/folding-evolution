---
next: strategy
---
# Decision — run 2026-10-09-2033 (question 36)

**Close [36](../../questions/10-compositional-map-transfer/36-sparse-source-feedback/question.md);
return to strategy; no proposal written.**

**Result.** One adaptive batch (four attempts per training cell collected under each build's own
frozen C4+F4, A8) against four more G4 attempts (S8), each pooled to eight and refitted. Primary
σ = cost(S8)/cost(A8) **1.126× [1.039, 1.220]** on 16 corpora: resolved above 1 under every
sensitivity, **unresolved against the pre-set 1.10×** (rule 3). Secondary, no rule: full F/A8
1.031× [0.951, 1.117] (A8 slower than full F by more than about 5% excluded), full F/S8 0.915×
[0.839, 0.998], both enlarged sources beat the four-attempt seed (1.52×, 1.35×). A8's batch solved
92.5% against G4's 57.6% at 0.30× the evaluations; acquisition A8 6.5 M, S8 10.2 M, full F 61.3 M
evaluations; A8 cheaper than S8 at every horizon (resolved to 1 024 searches). Clean run: all hash,
replay and pairing gates passed, 16-seed roster admitted on timing only, code review pass.
([analysis](analysis.md))

**Why close rather than continue.** The question was whether a sparse, hole-ridden bias can improve
its own next batch or locks in. It improves it: no lock-in, search resolved faster than static
collection, every empty cell filled, and the rebuilt pipeline not resolved from the full one at a
tenth of its acquisition. The remaining uncertainty, whether σ clears 1.10, would change no
choice: A8 has both the cheaper acquisition and at least equal search, so it is the better policy
either way. Resolving it at the observed point needs about 163 corpora (ten times this one, each
with fresh sources and a full-F reference). That is the README's case for closing, not for a top-up.

**Why `next: strategy`.** Root 10 has used 28 of 28 slots, strategy 2033 granted exactly one slot
and routed every outcome back for review, and no other open question has budget. Parked questions
were re-checked: none has its reopen condition met by this run (root 23 asks for a selectable
inherited signal; this is external fitting; root 01's children are unchanged).

**For the strategist, candidates this result makes concrete (not proposals):**
- **Fresh-bank test of the cheap adaptive pipeline.** Every result for C4+F4 → A8 is on development
  sources and bank. A8 nearly matching full F at a tenth of acquisition is the strongest
  cost-efficiency claim root 10 has; a transfer claim needs a fresh bank frozen with the method
  before scoring. Main cost: new G4 first batches and, if kept, a full-F reference (the expensive
  part); A8 vs G4 and vs C4+F4 alone would be much cheaper.
- **A second adaptive round** (A12 under A8). The A8 builds exist; the question would be whether
  feedback carries beyond full F (ρ_A8's interval admits up to 1.12×). Cheap to prepare, but
  another development-bank increment.
- **Decoder versus library in the A8 gain** (bare C8 scoring). Explains rather than decides; the
  1743 strategy deferred the same split.
Run allowance: 15 of 40 experiments used, deadline 2026-10-10T08:12, about nine hours left at
the time of writing; a complete fresh-bank cycle may not fit.

Bookkeeping done this step: 36's log and question (closed), root 10's log (run entry plus the
correction of 1743's per-block overstatement, critique 2033 Digest check), root 10's summary
(corrected wording, 36 added, 35 and 36 in the sub-question list), digest (new 36 bullet, header,
Overall and "Not shown" updated).
