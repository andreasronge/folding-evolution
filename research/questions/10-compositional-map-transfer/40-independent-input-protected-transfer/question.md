---
status: closed
tags: [compositional-transfer, new-family, protected-replication, acquisition-cost, external-fitting, independent-inputs]
budget: {experiments: 1, used: 0}
---
# Does the unchanged A8 recipe, rebuilt on the independent-input double-gate family, help fresh search on its protected cells?

Current summary: **closed (answered at this scope: useful protected-cell replication on
`x4-double-gate-v1`, relative to G4 at this cap).** Every earlier useful A8 result came from
branch-else/post-addition sources with output-addition targets. On the independent-input bank
([39](../39-independent-input-family-bank/question.md)), `(Xa+Xb)>(Xc+Xd) ? Xe:Xf` with addition inside
the predicate, 24 fresh A8″ builds from the four source cells were scored against the fixed G4 prior on
the eight protected cells, which had never been searched (run
[1536](../../../runs/2026-10-10-1536/analysis.md)): cost(G4)/cost(A8″) **10.1× [7.6, 13.1]** with failures
charged at 2 × cap, **6.4× [5.0, 8.0]** at 1 × cap, against a pre-set 1.5× margin. A8″ solved 317/384
searches, G4 63/384 (321 G4 searches capped), so the magnitude is a capped-cost ratio against a weak
baseline, not a time-to-solution ratio. Every build beat pooled G4 by more than 1.5× at 2 × cap, despite
sparse first-batch discovery (64/384) and eight builds with an empty intermediate library. On the three
cells whose predicate pairing {02|13} no source has, the advantage was smaller but large (6.8× [4.9, 9.2],
descriptive). Eight reinterpreted old-family builds (O) were in between (O/A8″ 4.3× [2.7, 6.6]). One build
repays its acquisition after about 40 searches in evaluations.

Competing explanations for the gain, none separated here:
- (a) the recipe learns the new double-sum assembly from its own sources (context plus fragments);
- (b) generic push/ADD/GT syntax shared with older families: O helps much less than fresh builds, which
  bounds this for those eight reinterpreted artifacts only (token reinterpretation confounds it);
- (c) supply only (readout and ADD frequency): untested on this family.

Scope: one family, alphabet `v2_x4`, D625, the 8 protected cells of development bank `x4-double-gate-v1`
(within-bank confirmation, not fresh-bank transfer or general portability); G4 is a supplied prior, not
a demonstrated competitive baseline here; decoder, library, yield and content bundled; alphabet, domain
and predicate placement changed together relative to the output-addition banks; external fitting, not
inheritance.

Opened 2026-10-10 (steward, run 2026-10-10-0311) after [39](../39-independent-input-family-bank/question.md)'s
pilot. Slot 32 of root 10 (strategy 1536 raised the budget 31 → 32). Closed 2026-10-10 after run 1536.

Related: [39](../39-independent-input-family-bank/question.md), [38](../38-cheap-bias-source-replication/question.md),
[37](../37-cheap-bias-fresh-transfer/question.md), [run 0311 analysis](../../../runs/2026-10-10-0311/analysis.md),
[run 1536 proposal](../../../runs/2026-10-10-1536/proposal.md),
[run 1536 analysis](../../../runs/2026-10-10-1536/analysis.md),
[run 1536 decision](../../../runs/2026-10-10-1536/decision.md),
[plan](../../../plans/independent-input-family-acquisition.md), [log](log.md).

Reopen if: a decision comes to depend on a quantity this design left open that its saved artifacts can
answer without new acquisition, e.g. A8″ against a stronger uninformed baseline on these cells, or
per-build attribution (context table alone against context plus library) using the 24 frozen builds.
Family specificity, fresh-bank transfer and inheritance belong in new questions.
