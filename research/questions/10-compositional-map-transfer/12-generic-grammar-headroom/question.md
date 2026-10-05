---
status: open
tags: [compositional-transfer, task-bank, feasibility, decoder, generic-grammar, headroom]
budget: {experiments: 1, used: 0}
---
# Is there a bank where a fixed generic grammar leaves room for a learned decoder?

Current summary: Opened 2026-10-06 from [11](../11-composition-bank/question.md), unmeasured.
In 11's reducer/combiner bank a hand-set previous-token grammar G (INPUT → reducer; int →
INPUT/ADD/DUP/IF_GT) solved every held-out cell in a median of 768–4 096 evaluations, so no
split had headroom; its rows describe the syntax of every canonical program in the bank. A
learned previous-token decoder of the same form could, at best, learn similar rows. Root 10
therefore needs either tasks whose solutions are not spelled out by a generic grammar, or a
fixed control that is generic without knowing the bank. Waiting on the strategist: this sets
what root 10's "simple fixed task-agnostic assembly bias" control is, which is a program-level
choice.

Candidate designs (not yet compared):
- **Deeper tier, same G.** Three-reducer or nested cells (e.g. `S+M+m`, `S>0 ? X+Y : Z`). G
  still covers their syntax; longer programs may push G past the 4 096 line by length alone,
  which would meet the headroom rule without making G less informed. Also must fix the thin
  SEL column (11: one SEL cell aliased, one at 27/50 under U at 524k).
- **Weaker, bank-blind control.** Define the fixed grammar before the bank, e.g. rows that only
  favour type-valid continuations of the previous token, and re-test 11's bank against it
  (stage A and U/F data reusable). Risk: a weak control makes "beyond a generic bias" easy to
  pass and less interesting.
- **Different family structure.** Cells whose canonical programs need bigrams that differ
  between families, so a family-specific decoder has something a generic one cannot have.

Competing explanations for a failure here:
- Any bank expressible on this alphabet with a short canonical program is covered by some
  generic previous-token grammar (then root 10 needs a richer decoder context or alphabet).
- Banks deep enough to escape G are not tractable under U at an affordable cap.

Related: [root 10](../question.md), [11](../11-composition-bank/question.md),
[run 2247 analysis](../../../runs/2026-10-05-2247/analysis.md),
[plan](../../../plans/compositional-map-transfer.md).

Reopen if parked: the strategist picks a control definition for root 10 and a candidate bank
whose held-out cells are ≥ 4 096 median evaluations under that control in a probe.
