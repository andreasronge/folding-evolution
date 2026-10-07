---
next: proposal
---
# Decision: run 2026-10-06-2331 (question 17, slot 1)

**Continue [17](../../questions/10-compositional-map-transfer/17-decoder-initialization-variation/question.md)
with its second slot**, the last slot of root 10. Proposal:
[runs/2026-10-07-0315/proposal.md](../2026-10-07-0315/proposal.md).

**Result.** Row 3 ("both conditional increments positive"), clean: every validation gate
passed, 400/400 seeds complete, GG solved 94.5–99.5% per cell, the diagonal reproduced (2.29×
[2.05, 2.54]). With identical starting tapes, searching under the learned map instead of G4
saves 1.39× [1.31, 1.47]; with the search decoder held at the learned map, starting from its
programs instead of G4's saves 1.30× [1.24, 1.36]. Both are robust to the cap. The two overlap
heavily: either alone, starting from G4, gives 60–68% of the diagonal in log units, interaction
−0.34 log2 [−0.40, −0.29], negative in 20/20 maps. The pre-registered prediction favoured row 1
(start adds < 1.19× once M is used during search, 45%); that was wrong.

**Why continue rather than return to strategy.** The plan's decision rule allows slot 2 for
rows 1–4, and the strategist allocated slot 10 for exactly this. The run also produced one new,
unexplained pattern that changes how the pooled result should be read: the larger component
flips with the cell (start-heavy on the BE cell, ongoing-heavy on both PA cells). It rests on a
single BE cell. The ten training cells (4 BE, 6 PA) are the only cells that can test whether the
balance tracks family without new screening, and the same runner, maps and validation apply.
The next proposal therefore pre-registers the family difference in log2(T_MG/T_GM) across
cells as a co-primary readout, alongside replication of the pooled increments. A mutation versus
crossover split was considered and deferred: it subdivides "ongoing" further, while the family
question determines whether the pooled 2331 statement is a property of the maps or an average
over tasks that behave differently.

**After slot 2**, 17 closes and root 10's budget is spent, so the program returns to strategy
whatever the outcome.

**Tree changes.**
- 17: log entry, summary and explanations updated (I and O not supported as sole carriers; B
  fits with strong sub-additivity; R only partly). Budget 2, 1 used. Status open.
- Root 10: summary, sub-question entry and log updated; 9 of 10 slots used.
- Digest: new section "Starting programs versus ongoing decoder"; header and open-question list
  updated.
- Digest check (critique notes 6–8) fixed in the digest, root 10's question.md and 16's
  question.md: "did not carry" → interaction unresolved, 0.98× [0.83, 1.15], a modest preference
  possible; "match or exceed" → BE's point gain slightly lower and PA's higher than training,
  not evidence of equality or absence of overfitting; "bounded below about 1.25×" → 95% upper
  bounds 1.2485× (BE, about 1.3× leave-one-map-out) and 1.15× (PA); "no preference appeared" →
  "no preference was resolved". The append-only logs of root 10 and 16 get correction notes
  instead of edits.
- Parked questions re-checked: 02, 04, 07, 08 and 09. None of their reopen conditions is met.
  09(b) asks for a heritable-bias design that needs to know whether supply alone is what evolution
  uses; this result says the start and ongoing components both matter here, but no such
  design is pending.
