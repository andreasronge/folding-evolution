# Log: 61 input-rebound library reuse

- 2026-10-12 (steward, 2353): opened on strategy 2353 (root 10 budget 50 → 51; this sub-question gets 1 slot).
  Proposal: [run 2353](../../../runs/2026-10-11-2353/proposal.md).
  - Primary: R-bind/R-all on all 24 cells, 24 builds, r = 6.
  - Material gain if the upper bound is < 0.90. Small, none or harm if the lower bound is > 0.85. Unresolved
    otherwise.
  - Precision was estimated from 2150's R-all rows: expected log half-width about 0.08–0.09.

## 2026-10-12: run 2026-10-11-2353, R-bind vs R-all on all 24 signed-chain cells (slot 51)

Experiment: commit `465f2fa` on the frozen `83c7c5b` engine; bank `x4-signed-chain-v1`, all 24 cells (development);
24 saved 1938 R-all libraries and their rebound copies (every entry × 24 consistent X0–X3 permutations, 21,528
slots, original weights, no dedup; all slots verified against the production VM and D625 column permutation).
24 builds × 24 cells × r = 6 per library arm (r fixed by the timing smoke, R-bind/R-all worker cost 0.48), R-tree and
R-gate at repeat 0; 8,064 jobs, none missing, 136 min queue.
[Analysis](../../../runs/2026-10-11-2353/analysis.md), [reanalysis](../../../runs/2026-10-11-2353/reanalysis.json).

Result:
- Validity passed: R-tree 27.4% first attempt, 7.3% capped; R-gate 576/576; R-all/R-tree 0.791 [0.650, 0.968]
  (2150 gave 0.778).
- **Primary R-bind/R-all 0.853 [0.785, 0.927]** (pooled capped mean, paired build × cell bootstrap; log half-width
  0.084, as forecast). Pre-set rule: **unresolved**. A saving > 10% is not established, > 15% is not excluded;
  harm is excluded. Geometric mean of unit ratios 0.856, median ratio 0.882; R-bind lower in 354/576 units.
- Solves 3,375 vs 3,316 of 3,456 (caps 81 vs 140); first-attempt 40.6% vs 35.4%. Worker seconds track evaluations
  (0.858 [0.790, 0.934]).
- Secondaries (repeat-0 pairing): R-bind/R-tree 0.664 [0.545, 0.801]; R-gate/R-bind 0.403 [0.317, 0.510]. With
  acquisition charged, R-bind/R-tree at N = 10 searches 0.787 [0.661, 0.932]; R-all/R-tree 0.914 [0.763, 1.099].
- By R-all's needed-helper coverage (descriptive, unit bootstrap, confounded): 0 / 1 / 2 / 3 helpers present →
  R-bind/R-all 0.695 / 0.871 / 1.050 / 1.240 (144 / 275 / 138 / 19 units). R-bind's own cost is nearly flat across
  these strata. The slope survives 23 build and 23 cell dummies (+0.26 log per helper, se 0.04). It matches a
  reach-versus-dose trade-off, but every non-helper entry was rebound too, so the mechanism is not isolated.
- Per build 0.73–1.03 (20/24 below 0.90); per cell 0.65–1.25 (one cell at 1.25). No single build or cell drives it.
- About 94% of the interval width is seed noise. Resolving a true 0.85 against the 0.90 bar would need r ≥ 14
  (6–7 h more queue) and would still fail if the true ratio is above about 0.86.

Against the explanations in question.md: reach is supported where literal coverage was absent; dose is supported
where it was present (losses at 2–3 helpers); "non-helper rebinding cancels the gain" is not supported pooled;
the remaining 2.5× gap to R-gate is not explained by missing bindings (R-bind supplies all 24 in 23/24 builds), so
helper types, weights, dilution or the half-library draw rule remain candidates.

Decision: park 61, because uniform rebinding answered the decision it was built for only partly. It helps:
harm is excluded and a saving of at least about 7% is shown. Whether it clears the pre-set 10% bar is unresolved.
More seeds on the same contrast (r ≥ 14, 6–7 h) would only move a label near 0.85–0.90. The stratum pattern points
to a different design that keeps literal dose and adds reach. That design is strategy's call, because root 10 has
no slot left. The digest gains this belief, scoped to development cells.
