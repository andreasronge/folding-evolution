---
status: parked
tags: [map-bias, op-weights, evolution-speed, supply-vs-success, generic-bias, shortcuts, chem-tape]
budget: {experiments: 2, used: 0}
---
# Why does an op-frequency vector with no sampling lift speed evolution 2–3×?

Current summary (2026-10-05, after run 1814; parked): **The speed-up is real, and on max>2
raising INPUT and GT is enough; on sum>2 the split is unresolved.** On fresh seeds (250
pairs) the other family's fitted vector X again reaches an exact solve sooner than uniform:
2.73× (sum>2) and 2.02× (max>2), lower bounds 2.12 and 1.45. Splitting X into IG (X's INPUT
and GT, rest uniform) and R (INPUT/GT at 1/22, rest in X's proportions): on max>2 IG carries
(IG÷X 0.90, 0.71–1.08) and R falls short with no gain over uniform; on sum>2 both beat
uniform (2.11×, 1.61×) and neither is resolved against X's 1.5× margin (IG÷X 1.29,
0.92–1.63; R÷X 1.69, 1.39–2.20). The tasks disagree, so the frozen rule parks 09.

The premise has narrowed. X's "no sampling lift" is a cancellation: IG alone raises the
exact-solver rate 3.2× / 3.9×, R alone lowers it to 0.23× / 0.35×. So the carrying part on
max>2 is a supply-raising intervention (pass-through 0.57, speed-up smaller than lift). What
is left of "speed-up without supply" is R on sum>2: 1.61× faster with a quarter of uniform's
exact solvers. There R and X (both raise REDUCE_MAX) meet about 10× more training-perfect
inexact candidates than U and IG (median 637 and 627 vs 58 and 67 per run), which fits G3 but
was not tested. Initialization and mutation stay coupled, so none of this names a mechanism.
Run 1705 first showed the effect (3.3× / 1.9×, 50 pairs, unregistered).

Competing explanations:
- G1 (shared scaffold supply): both fits raise INPUT (2.6–2.9×) and GT (3.0–3.2×). Partial
  structures every threshold task needs (read the list, compare) then arrive more often,
  though full solvers do not; selection builds on them. *As an intervention: holds on max>2
  (IG ≈ X), unresolved on sum>2 (IG÷X 1.29). Note IG also raises full solvers 3–4× (1814).*
- G2 (junk suppression): both fits push many task-irrelevant ops down. Fewer mutations land
  on or insert useless ops, so more variation is spent on relevant positions. 1558's prune
  arm (floors NOP-like ops only) did nothing for *sampling*; it was never run in evolution.
  *R (X's rest of the vector) shows no gain on max>2 and is resolved slower than X on sum>2,
  though 1.61× faster than uniform there (1814). R is not pure junk suppression.*
- G3 (shortcut stepping stone): on sum>2 the max-fit vector supplies max>2, which is
  training-perfect on 76 of the 100 sum>2 training sets; exact sum>2 may be a short step from
  it. Mismatched runs met shortcuts most often. Cannot explain the max>2 side (sum>2 is
  training-perfect on 0 of 100 max>2 training sets). *The only candidate left for R's sum>2
  gain; R and X meet ~10× more shortcuts there, but splitting seeds by whether max>2 fits the
  training set did not separate arms (49 seeds in the small group). Untested (1814).*

Tested in run 2026-10-05-1814 (see log). The test separated which *intervention* suffices,
not which mechanism; that was its registered scope.

Related: [08-evolve-bias](../08-evolve-bias/question.md) (parent finding),
[01-map-bias](../question.md),
[run 2026-10-05-1705 analysis](../../../runs/2026-10-05-1705/analysis.md) (data
`experiments/output/2026-10-05/2026-10-05-1705-evolve-bias/`, commit `9abc25c`),
[run 2026-10-05-1814 analysis](../../../runs/2026-10-05-1814/analysis.md) (component test;
data `experiments/output/2026-10-05/2026-10-05-1814-evolve-bias-components/`, commit
`31d4408`, code `experiments/chem_tape/evolve_bias_components.py`),
[run 2026-10-05-1558](../../../runs/2026-10-05-1558/analysis.md) (fitted vectors, prune arm),
[findings item 12](../../../../docs/map-bias/findings.md), [notebook §16, §19, §28](../../../../docs/map-bias/notebook.md),
[02-fixed-target-sampling](../02-fixed-target-sampling/question.md),
`experiments/chem_tape/evolve_bias.py`

Stop rule: one experiment, spent (run 1814). The frozen rule closes 09 only if the same
component carries in both tasks; the tasks disagreed, so 09 is parked. No follow-up run to
firm up the sum>2 reading under this question's budget.

Reopen if: (a) a new task family or alphabet shows an evolution speed-up with no or negative
sampling lift (the R-on-sum>2 pattern) on more than one task; (b) a heritable-bias design
needs to know whether INPUT/GT supply alone is what evolution uses, and the strategist judges
a separately pre-registered sum>2 resolution (IG vs X at ≥ 650 pairs) worth a slot; or (c)
someone proposes a direct test of the max>2 stepping stone on sum>2 (e.g. R with REDUCE_MAX
reset to 1/22, or training sets on which max>2 is not training-perfect, sized to separate
1.5× from 1×).
