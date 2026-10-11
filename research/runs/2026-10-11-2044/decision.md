---
next: strategy
---
# Decision — 2026-10-11-2044 signed-chain depth probe

**Keep [59](../../questions/10-compositional-map-transfer/59-signed-chain-depth/question.md) open. Return to
strategy; no proposal written.** Strategy 2044 funded one probe, and both the strategy and the proposal said it
would return to strategy afterwards. The probe's slot (root 10, 49/49) is used. A confirmation needs its own
allocation.

**What the probe found** (six development cells, 288 paired jobs per arm, commit `8a621df`; observations only):
- **The chain bank is a hard tier, but not capped.** R-tree solved 30% of jobs on the first attempt and capped 5.6%.
  Its mean cost was 159 k evaluations, about 20× the easy family. The supplied prior solved every job.
- **The saved libraries gave a small saving that is not resolved.** R-all/R-tree was **0.79 [0.60, 1.03]**. It was
  below 1 in 6/6 cells but only 14/24 builds. A 40% saving is excluded. Both "any saving" and the 0.80 bar are
  unresolved.
- **The supplied helpers keep large headroom.** R-gate/R-tree was 0.30 [0.23, 0.38], and R-gate/R-all 0.38.
  Linking alone did not limit search on these cells.
- **By point estimate, R-all saved nothing when a library held none of the three needed helpers.** The stratum
  ratios were 1.02 → 0.37 from 0 to 3 helpers. This is confounded, and the top stratum has only 16 units.
- **All three of the plan's recommendation flags were met:** hard, not ceilinged, precise and affordable.

No digest belief changes, because a probe gives observations only. The digest records 59 under "not shown" as
probe-only, with its saving unresolved.

**Steward's recommendation to strategy.** If root 10 continues, fund **one protected confirmation of 59**, sized
on the doubled-variance forecast and using a primary rule the forecast can resolve:
- **Design:** the 18 frozen protected cells × 24 saved builds × **r = 4**, with R-tree, R-all and R-gate. That is
  5,184 jobs in total, about 76 min central and 152 min with doubled tails, under 207 min of summed timeouts.
  Total cost is about 4–5 h with agent time. It reuses this run's code, bank, method and seed rules, so no new
  build work is needed.
- **Primary:** pooled capped mean evaluations, R-all/R-tree, with a two-way bootstrap.
  - **"Saving" if the upper bound is < 1.0.**
  - Report the 0.80 materiality bar as secondary. Near the observed 0.79 it is expected to stay unresolved: at
    r = 2, unresolved for true effects of about 0.63–1.01.
- **Why this is worth it:** it answers strategy 2044's question on never-searched cells. Either outcome changes
  the digest:
  - **Resolved saving:** frozen acquisition still pays on harder assembly, though about 2.6× behind the supplied
    helpers.
  - **Unresolved:** this marks a limit on deeper reuse of the recipe.
- **What it will not answer:** why the gap to R-gate persists. The coverage gradient points at acquisition
  keeping only about a third of the helpers (8.6/24). That is the more interesting next mechanism. It needs new
  acquisition or extractor work, which strategy 2044 declined for this block. I would not fund it before the
  confirmation.

If strategy judges a likely "small saving, about 20%" result not worth 4–5 h, park 59. Its reopen condition
already names this confirmation.

**Tree changes.**
- **59:** log entry with the probe's results and decision. Its summary was rewritten and its reopen condition
  made concrete. Status stays open.
- **Root 10:** the summary gains the 59 probe sentence. The budget history records strategy 2044's 48 → 49, and
  59 is added to the sub-question list. A root log entry was added.
- **Digest:** header, budget and sub-question status updated. The "not shown" list now cites 59 (probe only).
- **Critique 2044 digest-check notes 5–8 fixed:**
  - Note 5: "All completed banks are now development banks; 58's was fresh and frozen before its first protected
    scoring."
  - Note 6: "showed no saving" → "gave no resolved saving (a 20% saving excluded, harm unresolved)". Fixed in the
    digest, the root 10 summary and the 58 summary. The 58 log has a correction entry; log lines are append-only.
  - Note 7: 58's explanation (e) now says the protected result met the rule with a similar point estimate.
    Representativeness is not established.
  - Note 8: 50's log has a correction entry. In 49 the native TS library also harmed native TS search, and the
    1938 order-library harm is unresolved. "A library-on-failure gate would buy little" is untested.
- **Parked questions re-checked; none reopened:**
  - 50: no default mixed deployment is funded, and no harm was seen on the chain cells.
  - 54: no rectifier source redesign.
  - 23 and 55: no token-specific signal and no content-choice decision.
  - 01 subtree: unchanged.
  - 58 stays closed: its "hard tier" reopen item is now pursued in 59.
