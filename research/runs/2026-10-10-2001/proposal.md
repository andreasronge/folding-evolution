---
node: questions/10-compositional-map-transfer/42-family-bias-component-transfer
title: Table × library transplant — does the DG library carry the double-gate advantage onto a TS table?
bank: x4-double-gate-v1 (8 spare cells) + x4-branch-sum-v1 (8 targets), saved 1717 builds; development data
---
**Question.** Following [strategy 2001](strategy.md) and its [plan](../../plans/family-bias-component-transfer.md):
in [41](../../questions/10-compositional-map-transfer/41-same-alphabet-family-preference/question.md) DG-built A8
(D) cost a third of TS-built A8 (T) on DG cells, 2.98× [2.07, 4.33]. Each build is a context table plus a
literal block library. Does the D library help when moved onto a T table (portable package), does the
advantage sit in the D table, or does it need the native pair? This chooses what a later learner acquires.

**Closest technique.** Transfer of learned code fragments between GP problems, e.g. common subtrees from
source problems added to the target's function set ([O'Neill et al., CEC 2017](https://gpbib.cs.ucl.ac.uk/gp-html/oneill_2017_CEC.html));
the learned decoder follows [PIPE](https://pubmed.ncbi.nlm.nih.gov/10021756/). Swapping components between
independently trained models to test compatibility resembles stitching
([Lenc & Vedaldi, CVPR 2015](https://arxiv.org/abs/1411.5908)). All **external fitting**, frozen; no
selection or inheritance. A **mechanism test** of a known recipe; new is crossing a fragment library with a
separately learned context decoder.

**Arms (unit = donor pair).** A frozen random bijection π pairs D build i with T
build π(i) (24 pairs). Each pair gives six arms, written table/library:
D/D, T/T (fresh native references), **T/D** (primary transplant), D/T (reverse), D/∅ and T/∅ (bare tables,
block operator off by explicit mode, not the G4 label). Everything else as in 1717 (`b5697a1`).
Arms with the same table share initial programs (checked by hash). Ordinary search and block edits
use separate RNG streams. **16 cells (8 DG primary, 8 TS secondary) × 24 pairs × 2 new common seeds × 6 arms
= 4 608 searches.** No new acquisition, refit, G4 scoring or bank construction.

**Preparation (≤ 120 min agent).** Explicit table/library/operator fields; hashes of all 48 builds;
operator-off check; 16 1717 native rows replayed bit-exact; same-table initial-population equality.

**Feasibility.** 1717 per-search means: DG D 12.4 s, T 23.6 s, G4 29.4 s; TS D 4.4 s, T 3.4 s, G4 14.2 s;
9.8 workers. Hybrids and bare tables are unmeasured; bounded between native and G4 rates.
DG: 384 × (36 + 4 × 15–29 s) ≈ 37–58 k worker-s; TS ≈ 9–25 k. **Total ≈ 78–141 min.** A calibration entry
(6 arms × 2 families × 8 searches on development cells, ≈ 96 jobs) projects scoring time before any target
search. Over the timeouts → return to strategy, never drop arms.

**Full cost.** Queue: calibrate + validate 30 min, DG score 150 min, TS score 60 min = **240 min of
timeouts**, expected ≈ 1.5–2.5 h. Agent ≈ 4 h. **Total ≈ 6–7 h** of the 42 h left.

**Primary comparison.** Geometric capped cost over the 8 DG cells, failures at 2 × cap.
**R = cost(T/T) / cost(T/D)**: the gain from swapping in the D library on a fixed T table. 95% bootstrap:
resample the 24 pairs (each keeps its rows on all arms and both rosters), seeds jointly within pair × cell;
cells fixed. Worthwhile margin **1.5×**:
- lower bound > 1.5 → **portable library effect**. Then the residual gap G = cost(T/D)/cost(D/D) decides
  the type: upper < 1.5 → *library sufficient at this scope*; lower > 1.5 → *portable but partial*; otherwise
  *portable, sufficiency unresolved*;
- upper < 1.5 → **no worthwhile portable library effect**. Then report table-carried if bare
  B = cost(T/∅)/cost(D/∅) has lower > 1.5, or native combination if the library gain under D,
  cost(D/∅)/cost(D/D), has lower > 1.5 while R does not;
- otherwise **unresolved**, with a resolution price.

Also reported, with intervals, not decision rules: 1 × cap repeat (label flagged if it changes); the full
2 × 3 table on each roster; the reverse transplant D/T; on TS, the retention ratio cost(T/D)/cost(T/T); solve fractions, per-cell and per-pair costs; acquisition +
search cost, hybrids charged both acquisitions.

**Precision (planning only).** Per-search log-cost SD on DG ≈ 1.55 (1717); R is paired on table and
seeds; with library heterogeneity ≈ 0.4, per-pair SD ≈ 0.6, interval ≈ ×/÷ 1.3: a true R ≈ 2 should clear 1.5, R ≤ 1.15 below it;
R ≈ 1.6–1.8 likely unresolved.

**Expect.** The library carries a real but partial share: R ≈ 1.6–2.2, G ≈ 1.3–1.8. In 32 the libraries
gave 1.47–1.75× over their own table; D/∅ beats T/∅ by about 1.3–1.7×. On TS, retention within about 1.25×.
**Surprises:** R ≤ 1.1 while cost(D/∅)/cost(D/D) ≥ 1.5 (library helps only its own table); T/D cheaper than
D/D; a bare table cheaper than its native pair.

**Cannot show.** Content versus library size (D 7–32 fragments, T 32); why harder sources taught
better artifacts; a join motif; inheritance; fresh-bank transfer. Bare
tables were acquired with intermediate libraries, so D/∅ is not library-free acquisition.

**Next.** Exit to strategy in every case. Portable → learn repertoires separately and test library
transfer on a fresh family. Table-carried → decoder learning. Native combination → joint acquisition.
Unresolved → price it, no automatic top-up.
