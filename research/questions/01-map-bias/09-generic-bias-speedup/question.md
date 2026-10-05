---
status: parked
tags: [map-bias, op-weights, evolution-speed, supply-vs-success, generic-bias, shortcuts, chem-tape]
budget: {experiments: 2, used: 0}
---
# Why does an op-frequency vector with no sampling lift speed evolution 2–3×?

Current summary (2026-10-05, after run 1957; parked again): **The speed-up is real, and on
max>2 raising INPUT and GT is enough; on sum>2 the split is unresolved, and the max>2 shortcut
is used but not needed.** Run 1957 reopened 09 under (c) to test the shortcut directly (veto
exact max>2 from reproduction, U/R × ordinary/veto, sets where max>2 is always
training-perfect). Its pilot-based power gate failed on one criterion (0.48/0.53 < 0.80), so
only the 50-seed pilot exists and no registered label applies. At pilot strength: when exact
max>2 appears it is the solver's immediate parent in 55/60 runs; vetoing it delays the solve
(49/55 exposed pairs slower) but never stops it (100/100), because near-max programs take over.
Whether this explains R's advantage over uniform is unknown (pilot I 1.38, 0.82–2.00; R's gain
on these sets 1.30, 0.71–2.32).

Earlier (run 1814): on fresh seeds (250
pairs) the other family's fitted vector X again reaches an exact solve sooner than uniform:
2.73× (sum>2) and 2.02× (max>2), lower bounds 2.12 and 1.45. Splitting X into IG (X's INPUT
and GT, rest uniform) and R (INPUT/GT at 1/22, rest in X's proportions): on max>2 IG carries
(IG÷X 0.90, 0.71–1.08) and R falls short with no gain over uniform; on sum>2 both beat
uniform (2.11×, 1.61×) and neither is resolved against X's 1.5× margin (IG÷X 1.29,
0.92–1.63; R÷X 1.69, 1.39–2.20). The tasks disagree, so the frozen rule parked 09.

The premise has narrowed. X's "no sampling lift" is a cancellation: IG alone raises the
exact-solver rate 3.2× / 3.9×, R alone lowers it to 0.23× / 0.35×. So the carrying part on
max>2 is a supply-raising intervention (pass-through 0.57, speed-up smaller than lift). What
is left of "speed-up without supply" is R on sum>2: 1.61× faster with a quarter of uniform's
exact solvers. There R and X (both raise REDUCE_MAX) meet about 10× more training-perfect
inexact candidates than U and IG (median 637 and 627 vs 58 and 67 per run), which fits G3; 1957
tested it only at pilot strength. Initialization and mutation stay coupled, so none of this names a mechanism.
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
  training set did not separate arms (49 seeds in the small group) (1814). Run 1957's veto
  stopped at its pilot: the exact phenotype is the usual last step in both U and R and blocking
  it delays exposed runs, but near-max programs replace it; its share of R's advantage is
  unmeasured. Neither supported nor excluded as the explanation.*

Tested in run 2026-10-05-1814 (which *intervention* suffices, not which mechanism) and run
2026-10-05-1957 (shortcut veto; pilot-only stop, no registered result). See log.

Related: [08-evolve-bias](../08-evolve-bias/question.md) (parent finding),
[01-map-bias](../question.md),
[run 2026-10-05-1705 analysis](../../../runs/2026-10-05-1705/analysis.md) (data
`experiments/output/2026-10-05/2026-10-05-1705-evolve-bias/`, commit `9abc25c`),
[run 2026-10-05-1814 analysis](../../../runs/2026-10-05-1814/analysis.md) (component test;
data `experiments/output/2026-10-05/2026-10-05-1814-evolve-bias-components/`, commit
`31d4408`, code `experiments/chem_tape/evolve_bias_components.py`),
[run 2026-10-05-1957 analysis](../../../runs/2026-10-05-1957/analysis.md) (shortcut veto,
pilot only; data `experiments/output/2026-10-05/2026-10-05-1957-shortcut-veto/`, commit
`2a002a8`, code `experiments/chem_tape/evolve_shortcut_veto.py`),
[run 2026-10-05-1558](../../../runs/2026-10-05-1558/analysis.md) (fitted vectors, prune arm),
[findings item 12](../../../../docs/map-bias/findings.md), [notebook §16, §19, §28](../../../../docs/map-bias/notebook.md),
[02-fixed-target-sampling](../02-fixed-target-sampling/question.md),
`experiments/chem_tape/evolve_bias.py`

Stop rule: two experiments, both spent (runs 1814, 1957). 1814's frozen rule parked 09 on
task disagreement. 1957 was the one direct test of the stepping stone that the strategy allowed,
with a commitment to stop this threshold line whatever the result; it ended at the pilot gate.
No precision extension, veto-definition sweep or IG-vs-X refinement follows under this budget.

Reopen if: (a) a new task family or alphabet shows an evolution speed-up with no or negative
sampling lift (the R-on-sum>2 pattern) on more than one task; (b) a heritable-bias design
needs to know whether INPUT/GT supply alone is what evolution uses, and the strategist judges
a separately pre-registered sum>2 resolution (IG vs X at ≥ 650 pairs) worth a slot; or (c)
the owner funds a rerun of 1957's veto design with a fixed size (n ≈ 1600, ~2.5 h, fits one
queue) or a model-based power gate instead of one resampled from 50 pilot rows. Condition (c)
as first written (any direct test of the stepping stone) has been used.
