---
status: open
tags: [map-bias, op-weights, evolution-speed, supply-vs-success, generic-bias, shortcuts, chem-tape]
budget: {experiments: 2, used: 0}
---
# Why does an op-frequency vector with no sampling lift speed evolution 2–3×?

Current summary (2026-10-05, opened after run 1705): In
[08](../08-evolve-bias/question.md)'s evolution test, the *mismatched* fitted vector (the
other family's fit) adds no exact solvers by sampling on the holdouts (sum>2 1.02×, max>2
1.33×, intervals include 1), yet it reached an exact solve 3.3× (sum>2) and 1.9× (max>2)
sooner than uniform (median evaluations, 50 paired seeds, 95% intervals 2.18–3.93 and
1.30–2.79; unregistered contrast). It accounts for most of the matched vector's ~4× speed-up.
Pass-through (evolution speed-up ÷ sampling lift) ranged 0.35–3.2 across arms, so exact-solver
supply does not predict evolution speed here. This bears on item 12 ("frequency changes
supply, not reachability") and on §28 ("evolution is mostly a worse sampler"): in 1705 every
arm beat computed random search 9–40×. Not yet tested; nothing here is shown.

Competing explanations:
- G1 (shared scaffold supply): both fits raise INPUT (2.6–2.9×) and GT (3.0–3.2×). Partial
  structures every threshold task needs (read the list, compare) then arrive more often,
  though full solvers do not; selection builds on them.
- G2 (junk suppression): both fits push many task-irrelevant ops down. Fewer mutations land
  on or insert useless ops, so more variation is spent on relevant positions. 1558's prune
  arm (floors NOP-like ops only) did nothing for *sampling*; it was never run in evolution.
- G3 (shortcut stepping stone): on sum>2 the max-fit vector supplies max>2, which is
  training-perfect on 76 of the 100 sum>2 training sets; exact sum>2 may be a short step from
  it. Mismatched runs met shortcuts most often. Cannot explain the max>2 side (sum>2 is
  training-perfect on 0 of 100 max>2 training sets).

A clean first test (sketch, for the strategist to weigh): same harness and seeds as 1705 on
sum>2 and max>2 with arms uniform, mismatched, **INPUT+GT only** (raised to the fit's
probabilities, everything else uniform) and **suppression only** (the mismatched vector with
INPUT and GT reset to 1/22, renormalised). G1 predicts INPUT+GT ≈ mismatched; G2 predicts
suppression-only ≈ mismatched; both partial → additive. Decoding the 1705 shortcut genomes
first (no new runs) would test G3 for free. 1705 took 20 min for 650 runs.

Related: [08-evolve-bias](../08-evolve-bias/question.md) (parent finding),
[01-map-bias](../question.md),
[run 2026-10-05-1705 analysis](../../../runs/2026-10-05-1705/analysis.md) (data
`experiments/output/2026-10-05/2026-10-05-1705-evolve-bias/`, commit `9abc25c`),
[run 2026-10-05-1558](../../../runs/2026-10-05-1558/analysis.md) (fitted vectors, prune arm),
[findings item 12](../../../../docs/map-bias/findings.md), [notebook §16, §19, §28](../../../../docs/map-bias/notebook.md),
[02-fixed-target-sampling](../02-fixed-target-sampling/question.md),
`experiments/chem_tape/evolve_bias.py`

Stop rule: one experiment. If one of G1/G2 carries most of the gain, record it, close 09 and
let 08 close with it. If neither does, or the effect does not replicate on fresh seeds, park.

Reopen if (once parked): a new task family or alphabet shows the same no-lift speed-up, or a
heritable-bias design needs to know which part of a bias evolution uses.
