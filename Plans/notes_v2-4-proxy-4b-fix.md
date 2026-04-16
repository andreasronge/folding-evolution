# Note: §v2.4-proxy-4b follow-up (early-termination fix)

**Status:** planned · Phase 1 cleanup · 2026-04-16

## The issue

§v2.4-proxy-4 ran at commit `9455d04` and produced the signature:

| seed_fraction | BOTH-solve | wall | gens run |
|---|---|---|---|
| 0.0  | 0/20  | 151s  | 1500 (full) |
| 0.001 | 20/20 | 0.2s | **1** |
| 0.01  | 20/20 | 0.2s | **1** |

All 40 seeded winners are exact byte-for-byte copies of the injected canonical
body. Arms 1/2 terminated at gen 1 because `fitness.max() >= 1.0 and not alternating`
triggered early termination (`evolve.py:436-437` in island path,
`evolve.py:554-555` in panmictic path).

## Why this breaks the test

The prereg's outcome axis was **discoverability-limited (PASS)** vs
**maintainability-limited (FAIL)**, distinguished by **retention rate `R_i`
at final generation** after the canonical body has had the chance to drift
or be displaced by proxies under mutation + tournament selection.

With early-termination at gen 1:
- `R_i` trivially equals 1.0 (no mutations applied yet to seeded individuals).
- We only learn that a gen-0 perfect-fitness individual fixates under
  tournament selection — which is tautological.
- Nothing is measured about maintainability under proxy-basin competitive
  pressure.

## The fix (deferred until Phase 1 queue completes)

Add a new `ChemTapeConfig` field:

```python
# §v2.4-proxy-4b: when True, do not break out of the GA loop when
# fitness.max() >= 1.0 — instead run the full `generations` count.
# Required for maintainability probes (§v2.4-proxy-4) where the gen-0
# seeded population already contains perfect-fitness individuals.
disable_early_termination: bool = False
```

Hash-exclusion at default (principle 11):
```python
if not self.disable_early_termination:
    d.pop("disable_early_termination", None)
```

Guards in `evolve.py`:
- Line 436-437 (island path):
  ```python
  if fitnesses.max() >= 1.0 and not alternating and not cfg.disable_early_termination:
      break
  ```
- Line 554-555 (panmictic path): analogous.

Estimated: ~6-8 LoC, one pytest for the flag being respected.

## §v2.4-proxy-4b sweep design

Identical to §v2.4-proxy-4 except:
- `disable_early_termination: true` in `base`
- Add diagnostics: per-generation retention-rate trajectory (fraction of
  population whose program matches the canonical body within edit-distance 2)

Sweep file: `experiments/chem_tape/sweeps/v2/v2_4_proxy4b_seeded.yaml`.
Re-use the same 3-arm structure + 20 seeds = 60 runs at pop=1024, gens=1500.

Expected wall: full 1500 gens × 60 configs / 10 workers ≈ 15-20 min.

## Scope tagging note

The §v2.4-proxy-4 result (as-run) is **not retractable** — it still measures
something real (gen-0 fixation of a perfect-fitness seeded individual), just
not what the prereg intended. Per methodology principle 13, it should be
chronicled as **SUPERSEDED by §v2.4-proxy-4b** rather than deleted, with the
original observation preserved for the reasoning trail.

The prereg file itself should be updated with a supersession block at the
top when §v2.4-proxy-4b lands.

## Ordering

1. Wait for Phase 1 queue to complete (§v2.15 grid sweeps).
2. Add `disable_early_termination` flag + test (single commit).
3. Write `v2_4_proxy4b_seeded.yaml`.
4. Queue.yaml append + run.
5. Log both §v2.4-proxy-4 (superseded) and §v2.4-proxy-4b to
   experiments-v2.md via research-rigor log-result mode (user-invoked).
