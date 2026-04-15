# §v2.8 Phase A: HALT record (audit FAIL on all candidates)

**Status:** PHASE_A_HALT · target commit `75ab827` · 2026-04-15
**Source prereg:** [Plans/prereg_v2_8_integer_6token.md](prereg_v2_8_integer_6token.md)
**Audit script:** `experiments/chem_tape/phase_a_sampler_audit.py`
**Audit output:** `/tmp/v2_8_phase_a_audit.json` (transient; results recorded below)

## Result

Phase A sampler audit FAILED on **all 5 candidate tasks** for the §v2.8
6-token integer-domain body
`INPUT SUM CONST_2 ADD THRESHOLD_SLOT GT`. Per the prereg's hard gate,
Phase B does NOT run.

| candidate task | label | seeds 0-2 max proxy | accuracy | verdict |
|---|---|---|---|---|
| `sum_plus2_gt_15_slot` | `sum > 13` | `sum > 15` | 1.000 / 1.000 / 1.000 | FAIL |
| `sum_plus2_gt_17_slot` | `sum > 15` | `sum > 15` | 1.000 / 1.000 / 1.000 | FAIL |
| `sum_plus2_gt_20_slot` | `sum > 18` | `sum > 20` | 0.875 / 0.906 / 0.922 | FAIL (seeds 1,2) |
| `sum_plus2_gt_22_slot` | `sum > 20` | `sum > 20` | 1.000 / 1.000 / 1.000 | FAIL |
| `sum_plus2_gt_25_slot` | `sum > 23` | `sum > 20` | 0.891 / 0.906 / 0.938 | FAIL (seeds 1,2) |

All candidates: max proxy accuracy ≥ 0.90 on at least one of seeds {0, 1, 2}.

## Root cause

Under stratified-balanced sampling enforcing `label==1` for positives and
`label==0` for negatives, **any task with label `sum > X` admits a near-
perfect proxy `sum > Y` for Y close to X** because positives are
concentrated at sum > X and negatives at sum ≤ X — making any threshold
predicate near-X a near-perfect classifier of the sampler's distribution.

This is the §v2.4 single-predicate proxy basin attractor on a different
task family. The prereg's audit gate correctly identified the risk
before any GP compute ran.

## Methodology lesson

Two distinct audit shortcomings worth recording for the next prereg
cycle on this design space:

1. **Audit set was probably correct on intent but over-strict on sum-gt
   task families.** The current audit measures *label proxy accuracy* —
   does any predicate `sum > Y` agree with label `sum > X` on the
   training set? For sum-gt tasks under stratified sampling this is
   trivially high for Y close to X. The right audit may need to filter
   proxies by **alphabet-expressibility cost**: only flag proxies whose
   shortest expression in the v2_probe alphabet is ≤ canonical-body
   length. The current audit does not do this filtering.
2. **Sum-gt task families are intrinsically proxy-friendly under
   stratified sampling.** The §v2.3 mechanism worked because the proxy
   that fits task1 (`sum > 5`) FAILS on task2 (`sum > 10`) — under
   alternation, only the slot body solves both. The §v2.8 alternation
   would face the same dynamic, but the *fixed-task baselines* (which
   the prereg's "scales bar" anchors against) would still saturate. The
   audit caught the swamp risk on fixed-task baselines correctly.

## Next steps

§v2.8 is HALTED at Phase A. Re-prereg as **§v2.8'** with one of:

- **Different body shape that breaks the sum-gt proxy availability.**
  Candidate: `INPUT REDUCE_MAX CONST_5 ADD THRESHOLD_SLOT GT` (max+5 > t)
  pair with carefully-chosen thresholds so that no max-based proxy
  achieves ≥ 0.90 across both tasks.
- **Multi-slot body (two task-bound tokens)** so that no single-predicate
  proxy can express the label.
- **Proxy-cost-filtered audit** that only flags alphabet-expressible
  proxies up to a cost budget. Requires implementing a short-program
  enumerator over the v2_probe alphabet (~3-5h infrastructure work).

Not auto-queued; deferred pending paper-scope review on whether the
6-token body-length axis is worth additional design effort.

## What ran vs what didn't

- ✓ Phase A sampler audit (no GP, ~3 sec for 5 tasks × 3 seeds × 64 examples)
- ✗ Phase A scout sweep (would have been 25 GP runs; not needed since
  audit failed first)
- ✗ Phase B alternation main sweep (HALTED per prereg gate)
- ✗ Phase B fixed-baseline main sweep (HALTED per prereg gate)

Compute saved by Phase A gate: ~75 min wall (Phase B alt + fixed +
companion analysis).
