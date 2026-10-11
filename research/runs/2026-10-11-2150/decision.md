---
next: strategy
---
# Decision — 2026-10-11-2150 protected signed-chain reuse confirmation

**Close [60](../../questions/10-compositional-map-transfer/60-signed-chain-protected-reuse/question.md) and
[59](../../questions/10-compositional-map-transfer/59-signed-chain-depth/question.md) as answered. Return to
strategy; no proposal written.** Strategy 2150 funded this one slot (root 10, now 50/50). It named no automatic
follow-up and asked for a return to strategy after the result. The candidate I would weigh next changes the
acquisition recipe. Strategy kept that outside this block, so the call belongs to the strategist.

**What the confirmation found** (18 never-searched protected cells × 24 saved 1938 builds × 4 repeats, 1,728
paired jobs per arm, commit `83c7c5b`; complete grid; pre-stated rule):
- **Validity passed.** R-tree solved 27.0% of jobs on the first attempt and capped 6.8%, so this is the hard tier
  and it is not cap-dominated. R-gate solved 1,728/1,728.
- **Saving resolved: R-all/R-tree 0.778× [0.696, 0.870]** (pooled capped mean evaluations, two-way bootstrap).
  - Worker seconds were 0.761× [0.680, 0.848].
  - The ratio was below 1 in 18/18 cells and 20/24 builds.
  - The point estimate reproduces the development probe's 0.79 on fresh cells, with a narrower interval than
    forecast.
- **The 0.80 bar is unresolved.** A saving between 13% and 30% fits the data. A ">20%" saving is neither shown
  nor excluded.
- **Acquisition repays fast:** after **5.4 [3.8, 9.7] searches**, against about 66 on the easy 1938 cells. The
  libraries save 39.6 k [22.2 k, 57.1 k] evaluations per search. At 10 searches, acquiring and reusing is cheaper
  than searching from scratch, though only just at the interval's edge.
- **The supplied helpers stay far ahead.** R-gate/R-tree was 0.263× [0.233, 0.296] and R-gate/R-all 0.338× [0.298,
  0.383]. The acquired libraries close only a small part of that gap.
- **The saving tracks needed-helper coverage** (descriptive and confounded). R-all/R-tree was 0.98, 0.78, 0.59 and
  0.42 with 0, 1, 2 and 3 of a cell's three helpers present (456, 792, 436 and 44 jobs). About 72% of build × cell
  pairs hold at most one needed helper.

**Why close rather than continue.** 60's question is answered for this bank. The decision rule resolved and all
three validity checks passed. A larger run could tighten the 0.80 label. It would not change any decision,
because repayment within about 10 searches already settles the economic question. 59's question ("do the libraries
help where assembly is hard?") is answered by 60 for this bank: yes, modestly. The two remaining open points are
attribution (helpers versus other content) and why acquisition keeps so few helpers. Both are about the acquisition
step, not this deployment test.

**Steward's recommendation to strategy.** The data now point at one lever: acquisition coverage. With none of a
cell's needed helpers the libraries save nothing on this tier. With all three they come close to R-gate.
- **What is already known.** Strategy 2150 asked for a saved-corpus audit before funding any representation change.
  1938's helper census covers part of it ([analysis](../2026-10-11-1938/analysis.md)). Of 576 helper × build slots,
  206 were kept, 151 were built but not recurrent, 121 were built but inadmissible, and 98 were never built by any
  solver.
- **What that implies.** About three quarters of the missing helpers (272/370) were built by source solvers and then
  lost in extraction. So coverage looks limited by the extractor more than by source discovery. The census does not
  separate literal-binding loss from plain non-recurrence, and the meaning of "inadmissible" needs checking.
- **Candidate.** Re-extract from the saved 1938 corpora under a changed admission or recurrence rule, with no new
  source search. Measure helper coverage first, then deploy on the signed-chain cells against R-all, R-tree and
  R-gate. This is a mechanism test on what are now development cells; a transfer claim would need a fresh bank.
  It is cheap to build relative to the deferred abstraction engine (12–18 h), roughly 3–5 h in all. It asks
  whether the recipe, not just its frozen output, can close part of the 3× gap to supplied helpers.
- **Alternatives.** Strategy 2150 deferred inherited choice between libraries (55, about 8–12 h). The helper
  ablation it declined becomes worth running only if the extraction change does not move coverage.
- **If strategy judges the library line at diminishing returns,** root 10 can stop here with a clear statement:
  frozen acquired libraries help on held-out cells across three content families and one hard tier, but stay 2–7×
  behind supplied priors.

The ledger shows 17 full experiments and 5 probes. The probe allowance (one plus one per four full) is used, so the
candidate would need to be a full experiment.

**Tree changes.**
- **60:** closed. Summary written with the contrast, interval and scope; log entry added; reopen condition
  updated (the protected cells are now development data).
- **59:** closed as answered by 60. Summary rewritten; log has a correction entry and a closing entry.
- **Root 10:** summary sentence for 60 added. Budget history records strategy 2150's 49 → 50. The sub-question
  list marks 59 and 60 closed. A root log entry was added.
- **Digest:** header and root 10 budget/status updated. There is one new belief bullet (protected chain saving,
  with interval, repayment and scope). The "Overall" line moves hard targets from "not shown" to shown for this bank.
  The "not shown" list keeps hard targets on a fresh bank.
- **Critique 2150 digest-check notes 6–9 fixed:**
  - Note 6: "hard but uncapped" / "without a ceiling" became "hard tier with 5.6% R-tree capping, below the pre-set
    25% cap-dominance flag". Fixed in root 10 and 59; 59's log has a correction entry.
  - Note 7: "a 40% saving is excluded" was dropped from root 10. In 59 it now reads "descriptive lower cost-ratio
    bound about 0.60".
  - Note 8: "linking alone did not limit search" became "the supplied repertoire substantially reduced cost …;
    residual assembly cost and helper causality remain unresolved".
  - Note 9: the forecast wording in 59 became "a meaningful but uncertain chance of resolving any saving".
- **Parked questions re-checked; none reopened:**
  - 50: no default mixed-difficulty deployment is funded.
  - 54: no rectifier source redesign or changed acquisition method has been proposed for its bank. If strategy
    funds the re-extraction candidate, 54's saved rows could serve as a contrast where sources seldom build the
    helper.
  - 55 and 23: no content-choice design or token-specific signal.
  - The 01 subtree: unchanged.
