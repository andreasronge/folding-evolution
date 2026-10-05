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
on 5/10/15 and 2/5/7) was infeasible and never ran. The next run uses the constant
thresholds: fit on >1 and >5, hold out >2, in both families. A descriptive emulation hinted
that mismatched fits raise P(exact) too (≈ 3–5×), so C is a live prior.

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
  just remove useless ops. No family-specific fit.
- D (no transfer): the fit raises P(exact) on training members only.

Related: [01-map-bias](../question.md), [README core question](../../../../README.md),
[findings items 1, 12, 17](../../../../docs/map-bias/findings.md),
[notebook §1, §11, §15–§19](../../../../docs/map-bias/notebook.md),
[02-fixed-target-sampling](../02-fixed-target-sampling/question.md) (fixed-target map bias,
parked), `experiments/chem_tape/arrival_frequent.py` (random-tape sampler),
`ChemTapeConfig.op_weights` / `op_probs` in `src/folding_evolution/chem_tape/config.py`,
[run 2026-10-05-1510](../../../runs/2026-10-05-1510/code_review.md) (blocked: infeasible task
set; code `experiments/chem_tape/family_bias.py` at commit `3803bca`, branch
`research/2026-10-05-1510`)

Stop rule: if the first experiment reads B, C or D cleanly, park the frequency-only version of
part 2 and say so in the digest; a decoder-rule version needs its own plan file and owner go-ahead.
