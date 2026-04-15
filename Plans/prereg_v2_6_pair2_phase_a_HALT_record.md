# §v2.6'-Pair2 Phase A: HALT record (audit FAIL on all candidates)

**Status:** PHASE_A_HALT · target commit `75ab827` · 2026-04-15
**Source prereg:** [Plans/prereg_v2_6_pair2_redesigned.md](prereg_v2_6_pair2_redesigned.md)
**Audit script:** `experiments/chem_tape/phase_a_sampler_audit.py`

## Result

Phase A sampler audit FAILED on **all 5 candidate tasks** for the
§v2.6'-Pair2 redesigned threshold pairs over [0,12]. Per the prereg's
hard gate, Phase B does NOT run.

| candidate task | label | seeds 0-2 max proxy | accuracy | verdict |
|---|---|---|---|---|
| `sum_gt_18_slot_r12` | `sum > 18` | `sum > 20` | 0.953 / 0.969 / 0.969 | FAIL |
| `sum_gt_22_slot_r12` | `sum > 22` | `sum > 20` | 0.953 / 0.891 / 0.938 | FAIL (seeds 0,2) |
| `sum_gt_24_slot_r12` | `sum > 24` | `sum > 25` | 0.984 / 0.906 / 0.969 | FAIL |
| `sum_gt_28_slot_r12` | `sum > 28` | `sum > 30` / `sum > 25` | 0.906 / 0.875 / 0.891 | FAIL (seed 0) |
| `sum_gt_30_slot_r12` | `sum > 30` | `sum > 30` | 1.000 / 1.000 / 1.000 | FAIL |

## Root cause and methodology lesson

Same root cause as §v2.8 Phase A HALT: under stratified-balanced sampling
on a sum-gt task family, any proxy `sum > Y` for Y close to the label
threshold X scores ≥ 0.90 trivially. The audit set includes such
proxies; all candidates trip the gate.

**Caveat — the audit may be over-strict for §v2.6'-Pair2 specifically.**
Unlike §v2.8 (where the canonical body has 6 tokens and competing
proxies might be cheaper to construct), §v2.6'-Pair2's canonical body
is 4 tokens (`INPUT SUM THRESHOLD_SLOT GT`). The cheapest alphabet
expression of competing proxies like `sum > 20` requires constructing
the constant 20 from {CONST_0, 1, 2, 5}, costing ≥ 6 tokens of constant-
construction (e.g., `CONST_5 CONST_5 CONST_5 CONST_5 ADD ADD ADD = 7
tokens for value 20`) plus 3 tokens for `INPUT SUM ... GT` framework =
10+ tokens total. The slot body is FAR cheaper.

So while the *label* admits a high-accuracy proxy, the *alphabet-
expressible* proxy is not cheap. §v2.3's 80/80 succeeded under
analogous proxy availability because (a) §v2.3's tasks have small
thresholds {5, 10} where one task's proxy IS cheap (`INPUT SUM CONST_5
GT` = 4 tokens for `sum > 5`) but the OTHER task's proxy is not; and
(b) under alternation, the proxy-fitting-one-task fails on the other,
so the slot body wins.

The §v2.6'-Pair2 candidates likely have the same dynamic: each task's
proxy is expensive in this alphabet, AND under alternation a single
proxy cannot fit both tasks. The audit's strict label-only check does
not capture this.

## Honest disposition

The hard gate fired. Per the prereg's own discipline, Phase B does not
run tonight. **HOWEVER**, this HALT may be over-cautious for §v2.6'-Pair2
specifically. The right next step is to add an **alphabet-expressibility
cost filter** to the audit, then re-run. If the filter shows no cheap
proxy (≤ 6-token expression) achieves ≥ 0.90, the audit should pass and
Phase B should be queueable.

This filter is also the right addition to the project-wide audit
methodology (will reduce false positives on sum-gt task families
without losing the §v2.4-style attractor protection on compositional
tasks).

## What ran vs what didn't

- ✓ Phase A sampler audit (no GP)
- ✗ Phase A scout sweep (would have been 25 GP runs; not needed since audit failed first)
- ✗ Phase B alternation main sweep (HALTED per prereg gate)
- ✗ Phase B fixed-baseline main sweep (HALTED per prereg gate)

Compute saved by Phase A gate: ~50-60 min wall.

## Next steps

1. **§v2.6''-Pair2:** add alphabet-expressibility cost filter to
   `phase_a_sampler_audit.py`. Re-run audit. If passes, queue scout +
   main sweeps.
2. **§v2.8'-redesign:** harder — sum-gt body family is intrinsically
   proxy-friendly even with the cost filter, because §v2.8's 6-token
   canonical body is itself sum-gt-based. Need a different body shape
   (REDUCE_MAX-based, or multi-slot).
3. **Audit improvement (project-wide methodology):** the alphabet-
   expressibility filter is itself worth a small infrastructure prereg
   (~3-5h work). Defer pending paper-scope review.
