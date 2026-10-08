---
next: strategy
---
# Decision: run 2026-10-07-2243 (root 23, slot 1) — stopped at the cost gate

**Continue root 23; return to strategy before re-planning.** Budget unchanged: 2 experiments,
0 used (no execution). No belief in the digest changed.

## What happened

The researcher built the inherited-modifier path (commit `25f929e`, 151 tests pass, all four
threshold targets validated, σ = 0 identical-row replay matches legacy search on 20 seeds)
and stopped at the plan's admission gate ([infeasible.md](infeasible.md)). The gate charged
every one of 71 scoring batches twice the single worst observed search (max1 uniform, 170.6 s,
mostly shortcut verification) and priced the roster at 569 min against 210. Using measured
means with a 2× margin gives about 136 min; the point estimate is about 54 min of queue.
**Cost is not the real obstacle; the gate was too strict.** That alone would justify re-running
the approved design with a mean-based gate.

## Why not simply re-run it

Stage 0 ran one acquisition per family × arm and 4 paired frozen searches per vector and
target. These are observations, not results ([log](../../questions/23-heritable-variation-bias/log.md)),
but two of them bear on the design rather than the hypotheses:

1. **The primary contrast is confounded with exposure.** Episodes stop at the first exact solve,
   so the arm that solves less runs longer: sum inherited 1 679 generations (47/48 solved),
   sum broken 5 053 (17/48). More generations mean more neutral drift (≈ 2.1 log units per
   component at σ = 0.03 over 5 000 generations; the proposal assumed ≈ 1 over 2 000). The
   broken sum vector drifted onto SLOT_13/IF_GT/SEP_B and was about 4× *slower than uniform*
   (163k vs 42k geo-mean evaluations on sum1). Broken ÷ inherited would then be large partly
   because the control is degraded, not because linkage learned something. The plan already
   says useful acquisition requires inherited to beat uniform; that comparison should be the
   primary one, with equal generation counts across arms.
2. **The max family barely gets selection signal.** 7/48 and 6/48 episodes solved; both learned
   max vectors were censored on all 8 frozen searches, worse than uniform (max1 86k, max5 231k),
   and the inherited one *lost* INPUT (0.006). A comparison with both arms at the cap is
   unresolved by the plan's own rule.

For reference, the sum inherited vector raised INPUT to 0.36 and GT slightly, and on 8 paired
searches sat between uniform (about 1.3–1.6× faster) and the hand scaffold (about 5× slower).
n = 1; this does not show acquisition.

## Why strategy, not a proposal

The opening [strategy](strategy.md) and root 23's allocation ask for review "after a
feasibility-only first result, any build/cost failure". This is a cost failure, and the fix I
would propose changes the primary contrast and the exposure rule, which the strategist fixed
the scope of. A strategist pass costs one short cycle; the alternative risks the critic sending
back a proposal that skipped the agreed review. Root 23 still deserves its slot: the code is
built and validated, and the question is the owner's untested selection route.

## Recommended re-plan (for the strategist to accept, change or decline)

Revised slot 1, same harness and roster size, no tuning sweep:
- **Equal exposure:** every episode runs exactly 128 generations in both arms (solves recorded,
  no early stop): 6 144 generations per run, ≈ 250 s each from the max timings.
- **Primary:** uniform ÷ inherited, per family, on the shared frozen seeds; crossed bootstrap
  of acquisition runs and seeds as approved. Useful acquisition: lower bound > 1 and point
  ≥ 1.5×. Broken ÷ inherited and scaffold ÷ inherited become pre-stated secondaries.
- **Families:** keep both; max is cheap (censored searches cost ≈ 10 s) and its failure would
  itself bound this procedure. Decide per family; do not pool a sum success into a claim for max.
- **σ:** keep 0.03. Lowering it shrinks selection as well as drift (selection/drift scales
  roughly with σ√T), so it is not an obvious fix; record drift magnitude instead.
- **Admission:** mean-based 2× gate; acquisition and scoring as separate queue entries so a
  scoring overrun keeps the acquisition data.
- **Cost:** acquisition ≈ 27 min, scoring ≈ 35 min at means; ≈ 2.5 h of timeouts with
  margin; ≈ 3 h agent work (code exists). Well inside the remaining 10–14 h block.

The alternative is the strategy's next candidate, a fresh multi-holdout bank. I would not park
23 on a gate artefact. Parked questions re-checked (02, 04, 07, 08, 09): none has its reopen
condition met. 08/09's "heritable-bias design that needs the answer" is not triggered: the
max1 shortcut shows up as verifier cost, not as something this design must explain.

Digest check (critique note 6) fixed: the digest, question 22's `Reopen if` and a correction
entry in 22's log now say both lineage and seed uncertainty matter for the 1.09× holdout
interaction, and that seed-only resolution is not excluded.
