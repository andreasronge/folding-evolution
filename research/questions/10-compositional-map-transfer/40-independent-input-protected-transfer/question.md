---
status: open
tags: [compositional-transfer, new-family, fresh-transfer, acquisition-cost, external-fitting, independent-inputs]
budget: {experiments: 1, used: 0}
---
# Does the unchanged A8 recipe, rebuilt on the independent-input double-gate family, help fresh search on its protected cells?

Current summary: **open, awaiting allocation (stage 2 suggested to strategy).** Every useful A8
result so far came from branch-else/post-addition sources with output-addition targets. On the
independent-input bank ([39](../39-independent-input-family-bank/question.md)), a pilot of eight
builds was far cheaper than G4 on four development cells (G4/A8 12.2× [6.7, 20.7], penalty-inflated;
A8 solved 55/64 against G4's 7/64). That is a probe observation on development cells. This question
asks whether independently rebuilt A8 artifacts, frozen with the method, beat contemporaneous G4 by a
worthwhile margin (pre-set 1.5×) on the eight protected cells, three of which use a predicate pairing
({02|13}) that no source cell has.

Competing explanations for a gain:
- (a) the recipe learns the new double-sum assembly from its own sources (context plus fragments);
- (b) generic push/ADD/GT syntax shared with older families carries it: eight reinterpreted
  old-family builds (O) scored as a descriptive arm;
- (c) supply only (readout and ADD frequency): not separated here; earlier frequency replacements
  did not reproduce C on the old banks, but that is not tested on this family.

Competing explanations for no gain: sparse first-batch discovery (median 2.5/16 per build in the
pilot) leaves some builds with thin fits; or the protected cells, especially the unseen pairing,
need assembly the sources do not teach.

Scope: one family, alphabet `v2_x4`, D625, 8 protected cells of bank `x4-double-gate-v1` (frozen by
SHA before any search, never scored); external fitting, not inheritance; decoder, library, yield and
content bundled.

Opened 2026-10-10 (steward, run 2026-10-10-0311) after [39](../39-independent-input-family-bank/question.md)'s
pilot; follows the [plan](../../../plans/independent-input-family-acquisition.md)'s second stage, which
needs its own allocation. Budget 1, counted against root 10 (31 of 31 used at opening).

Related: [39](../39-independent-input-family-bank/question.md), [38](../38-cheap-bias-source-replication/question.md),
[37](../37-cheap-bias-fresh-transfer/question.md), [run 0311 analysis](../../../runs/2026-10-10-0311/analysis.md),
[run 0311 decision](../../../runs/2026-10-10-0311/decision.md), [log](log.md).

Reopen if: (not closed). If strategy declines the allocation, park with reopen condition: a decision
comes to depend on whether external acquisition extends beyond output-addition families.
