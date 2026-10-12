---
next: strategy
---
# Decision: run 2026-10-11-2353 (input-rebound libraries, question 61)

**Result.** R-bind/R-all **0.853× [0.785, 0.927]** on all 24 `x4-signed-chain-v1` cells (24 builds × 24 cells × 6
repeats per library arm; commit `465f2fa`). The pre-set rule says **unresolved**: material gain needed an upper
bound below 0.90, and small/none needed a lower bound above 0.85. Harm is excluded and a saving of at least about 7%
is shown. Precision matched the forecast (log half-width 0.084); the point estimate fell in the gap between the two
labels. Validity passed. R-bind/R-tree 0.664× [0.545, 0.801]; R-gate/R-bind 0.403× [0.317, 0.510]. By R-all's
needed-helper coverage (descriptive): 0.69 / 0.87 / 1.05 / 1.24 for 0–3 helpers present.
[Analysis](analysis.md).

**61: park.** Uniform rebinding helps somewhat, but whether it clears 10% is open. A top-up on the same contrast
needs r ≥ 14 (6–7 h of queue) and would still be a coin flip if the true ratio is about 0.86. That is precision on a
label, not a changed decision. The stratum pattern instead says the uniform design trades dose for reach. Reach wins
where the literal library lacked the binding and loses where it had it. A different design would test that. Reopen
condition in [61](../../questions/10-compositional-map-transfer/61-input-rebound-library-reuse/question.md).

**Root 10: open, 51/51 used, back to strategy.** Strategy 2353 funded one slot and asked for review after every
outcome, with no automatic top-up. No proposal is written, because root 10 has no budget and its next step is a
strategic choice, not a clear continuation.

**For the strategist: my recommendation.**
- **Preferred, if root 10's library line continues: a dose-preserving mixture (R-mix).** Keep each literal entry at
  its original weight and add its rebound copies with a fixed share of donor mass (e.g. half literal, half
  rebound), against R-all and R-bind on the same 24 development cells. It is a mechanism test that separates dose
  from reach, a predicted direction exists (better than both where coverage varies), and it reuses the 2353 harness,
  seeds and validation. It costs roughly 5–6 h. It is still development data and a supplied symmetry. Its value
  depends on whether a better donor policy would then be carried to a fresh-bank test. If not, skip it.
- **Alternative: a frozen fresh-bank test** of the acquisition-plus-rebinding procedure against R-tree and a
  supplied prior. Strategy 2353 tied this to a material gain, which was not earned. Without that gain, the case is
  weaker.
- **Or stop the library line here** with a summary: acquired libraries pay on this family's hard tier, supplied
  symmetry adds about 15% (unresolved against 10%), and supplied priors stay 2.5× ahead. Then the remaining
  allowance goes to another root (55's equal-dose choice is the strategist's named second).

**Digest.** Gains one belief (rebinding: 0.853× [0.785, 0.927], unresolved against 10%, development cells, supplied
symmetry; strata descriptive). The overall paragraph is updated, and the root-10 header now reads 51/51.

**Digest check (critique note 5).** Fixed 59's "no-helper stratum saved nothing". It now says point estimate near
parity (0.98), descriptive and confounded, and not bounded. A log entry was added in 59. The digest itself did not
carry that phrasing.

**Parked questions re-checked.**
- 54 would reopen for a parameterized-abstraction method proposed on its own bank. That is not proposed.
- 50 needs mixed-family default deployment.
- 55 and 23 need inheritance designs.
- 01's sub-questions are unaffected.
- 60's reopen ("a changed donor policy needs a deployment readout on this hard tier") is served by 61 itself. No
  reopening is needed.

None is reopened.
