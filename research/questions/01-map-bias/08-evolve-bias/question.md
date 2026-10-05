---
status: open
tags: [map-bias, evolve-the-bias, task-family, transfer, op-weights, arrival-of-the-frequent, chem-tape]
budget: {experiments: 3, used: 0}
---
# Can the map's bias be fitted to a family of tasks, and does that help evolution on unseen members?

Current summary (2026-10-05): The README's second part ("evolve the bias") has never been
tested. What we know that bears on it: the chem-tape map is extremely biased (one constant
behaviour takes 66–88% of random tapes, §1); random-tape frequency predicts easy tasks but
evolution routinely finds behaviours rarer than 1 in 50M (§1, findings item 1); and op
frequency acts as a supply rate: it changes how often a part is made and when it arrives,
saturates above uniform, and hurts through dilution when very high, without changing what is
reachable (findings item 12, §15–§19). Varying goals (Kashtan & Alon) showed nothing beyond
noise in §11. The cheapest map-level knob that exists is `op_weights`, the draw distribution
over ops for random genomes and mutations; it is equivalent to letting codon redundancy in the
token→op table change. Decoder rules themselves are not yet a parameter.

Feasibility (2026-10-05, run 1510, reviewer probes, not run data): on the TAG alphabet,
threshold predicates on length-4 lists over [0,9] are reachable by uniform sampling at ~1e-6
only when the threshold is an alphabet constant (1, 2, 5); one ADD away (max>3, sum>7) is
~1e-8, and sum>10, sum>15, max>7 and the like had 0 hits in 95M. So the first design (fit
on 5/10/15 and 2/5/7) was infeasible and never ran.

Sampling result (2026-10-05, run 1558, one seed): **A at the sampling level.** Fitting on >1
and >5 and holding out >2, the matched fit raised held-out P(exact) 4.9× (sum>2) and 8.9×
(max>2) over uniform, and 4.8× / 6.7× over the other family's fit; all adjusted lower bounds
above 3. Mismatched fits did nothing for the holdouts (1.0×, 1.3×), so C is out for these
holdouts. What transferred is narrow: every rate is reproduced by the product of four op
weights (INPUT, GT, the aggregator, the threshold constant), and swapping aggregator mass
swaps the family. The fits also overfit their constants (CONST_2 down to 0.37×), which cost
the holdouts ~2.7× of gain. M rests on one fit trajectory. Evolution untested, so A vs B is
open; item 12 predicts B. Next: evolution on sum>2 and max>2 with uniform, matched, mismatched
and a hand-set aggregator vector.

Before letting the bias evolve inside evolution, the first test is whether there is anything
for it to find: does a frequency bias fitted on some members of a task family raise P(exact)
and evolution's success on held-out members, more than a bias fitted on another family?

Competing explanations:
- A (fit and transfer): a family-fitted bias raises held-out P(exact) and solve rate or speed
  beyond uniform and beyond a mismatched family's bias. The map's bias can usefully adapt to a
  family; next is making it heritable.
- B (supply, not success): held-out P(exact) rises, but evolution's solve rate does not move,
  as item 12 would predict. Frequency bias matters to sampling, not to what selection reaches;
  part 2 would then need structural map changes (decoder rules), not frequencies.
- C (generic dilution): matched and mismatched fitted biases help about equally, because both
  just remove useless ops. No family-specific fit. *Out for the sum>2/max>2 holdouts (run
  1558: mismatched 1.0–1.3×).*
- D (no transfer): the fit raises P(exact) on training members only. *Out at this fit
  strength (gain 4.9× / 8.9×), but CONST_2 suppression is a live route to it under a harder
  fit (run 1558).*
- A' (one-op transfer, a narrowing of A): the only family information a frequency fit carries
  is the aggregator's weight (plus INPUT, GT), so a hand-set aggregator vector does at least as
  well as the fitted one. Run 1558's product model and swap pools point here (post hoc).

Related: [01-map-bias](../question.md), [README core question](../../../../README.md),
[findings items 1, 12, 17](../../../../docs/map-bias/findings.md),
[notebook §1, §11, §15–§19](../../../../docs/map-bias/notebook.md),
[02-fixed-target-sampling](../02-fixed-target-sampling/question.md) (fixed-target map bias,
parked), `experiments/chem_tape/arrival_frequent.py` (random-tape sampler),
`ChemTapeConfig.op_weights` / `op_probs` in `src/folding_evolution/chem_tape/config.py`,
[run 2026-10-05-1510](../../../runs/2026-10-05-1510/code_review.md) (blocked: infeasible task
set; code `experiments/chem_tape/family_bias.py` at commit `3803bca`, branch
`research/2026-10-05-1510`),
[run 2026-10-05-1558](../../../runs/2026-10-05-1558/analysis.md) (sampling verdict A; fitted
vectors in `experiments/output/2026-10-05/2026-10-05-1558-family-bias/result.json`, key
`vectors`; code at commit `cd69bce`), `src/folding_evolution/chem_tape/evolve.py` (uses
`op_probs` for initial genomes and mutation)

Stop rule: if the first experiment reads B, C or D cleanly, park the frequency-only version of
part 2 and say so in the digest; a decoder-rule version needs its own plan file and owner go-ahead.
The sampling test read A, so the evolution test (A vs B) runs next. If evolution reads B,
park the frequency-only version of 08. If it reads A, close 08 as answered; if the hand-set
aggregator vector does as well as the fitted one (A'), say the answer is "yes, through one op
weight", and only open a heritable-bias sub-question if the strategist judges it worth more
than other open lines.

Reopen if (once parked): a richer alphabet makes non-constant thresholds sampleable, or a
decoder-rule version of part 2 gets its own plan and owner go-ahead.
