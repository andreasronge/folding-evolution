---
status: parked
tags: [map-bias, evolve-the-bias, task-family, transfer, op-weights, arrival-of-the-frequent, chem-tape, evolution-speed]
budget: {experiments: 3, used: 0}
---
# Can the map's bias be fitted to a family of tasks, and does that help evolution on unseen members?

Current summary (2026-10-05, after runs 1705 and 1814; parked): **Yes against uniform,
barely against the other family.** A fitted `op_weights` vector speeds evolution on its held-out threshold about 4×
over uniform (sum>2 4.33×, max>2 3.58× in median evaluations to an exact solve; lower bounds
2.6× and 1.9×), so B is out for these tasks. A hand-set scaffold (INPUT, GT and the family
aggregator raised, constants uniform) does as well as the fit (0.93×, 1.08×). Matched beats
the *other* family's fit by only 1.66× / 1.80×, unresolved against the 2× bar. And the
mismatched vector, which adds no exact solvers on these holdouts, is itself 3.3× / 1.9×
faster than uniform (unregistered): most of the gain is generic, and sampling lift does not
predict evolution speed-up. Pre-registered outcome: **Partial** → strategy, last slot unspent.
The generic speed-up was split off as
[09-generic-bias-speedup](../09-generic-bias-speedup/question.md). Run 1814 replicated it on
fresh seeds (2.73× / 2.02×) and found that on max>2 raising INPUT and GT alone (rest thinned
evenly) reproduces it; on sum>2 the split is unresolved. The mismatched vector's flat
sampling rate turned out to be INPUT/GT's 3–4× lift cancelled by the rest of the vector's
3–4× loss. 09 parked on task disagreement, so 08's unfinished part (family specificity)
parks with its 1705 result.

Earlier steps: feasibility (run 1510, reviewer probes) showed only thresholds equal to an
alphabet constant (1, 2, 5) are sampleable on TAG at ~1e-6, so the family is "sum/max > c"
with c ∈ {1, 2, 5}. Sampling (run 1558, one seed) read A: the matched fit raised held-out
P(exact) 4.9× / 8.9× over uniform and 4.8× / 6.7× over the mismatched fit, via INPUT, GT
and the aggregator weight; the fits suppressed CONST_2 (0.37×). Run 1705 measured the
hand-set scaffold's sampling lift at 5.45× / 11.07×, against the four-op product model's 17×
/ 22×: the model, fitted post hoc in 1558, failed out of sample.

Competing explanations:
- A (fit and transfer): a family-fitted bias speeds evolution on held-out members beyond
  uniform and beyond a mismatched family's bias. *Half met (run 1705): beyond uniform yes,
  beyond mismatched 1.7–1.8×, unresolved.*
- B (supply, not success): held-out P(exact) rises but evolution does not speed up (item 12's
  prediction). *Out for sum>2 / max>2 on median speed (run 1705).*
- C (generic): matched and mismatched biases help about equally because both carry the same
  generic content (raised INPUT/GT, suppressed junk ops). *Out for sampling (1558), but
  carries most of the evolution gain (run 1705, unregistered; replicated in 1814). On max>2
  the generic part is the INPUT/GT raise; on sum>2 unresolved (09).*
- D (no transfer): *out at this fit strength (1558).*
- A' (one-op scaffold suffices): a hand-set INPUT/GT/aggregator vector does as well as the
  fit. *Holds at cell level in both families (run 1705), though not awarded as an outcome
  because A was not established.*

Related: [01-map-bias](../question.md), [README core question](../../../../README.md),
[09-generic-bias-speedup](../09-generic-bias-speedup/question.md) (parked; component test,
[run 2026-10-05-1814](../../../runs/2026-10-05-1814/analysis.md)),
[findings items 1, 12, 17](../../../../docs/map-bias/findings.md),
[notebook §1, §11, §15–§19, §28](../../../../docs/map-bias/notebook.md),
[02-fixed-target-sampling](../02-fixed-target-sampling/question.md) (fixed-target map bias,
parked; run 1705 saw evolution beat computed random search 9–40×, unlike §28),
`experiments/chem_tape/arrival_frequent.py` (random-tape sampler),
`ChemTapeConfig.op_weights` / `op_probs` in `src/folding_evolution/chem_tape/config.py`,
[run 2026-10-05-1510](../../../runs/2026-10-05-1510/code_review.md) (blocked: infeasible task
set; code `experiments/chem_tape/family_bias.py` at commit `3803bca`),
[run 2026-10-05-1558](../../../runs/2026-10-05-1558/analysis.md) (sampling verdict A; fitted
vectors in `experiments/output/2026-10-05/2026-10-05-1558-family-bias/result.json`, key
`vectors`; commit `cd69bce`),
[run 2026-10-05-1705](../../../runs/2026-10-05-1705/analysis.md) (evolution, Partial; code
`experiments/chem_tape/evolve_bias.py` at commit `9abc25c`; data
`experiments/output/2026-10-05/2026-10-05-1705-evolve-bias/`),
`src/folding_evolution/chem_tape/evolve.py` (uses `op_probs` for initial genomes and mutation)

Stop rule: parked 2026-10-05 after run 1814, as 1814's proposal fixed ("if 09 parks, park
the unfinished part of 08 with its 1705 result"). The answered part stands: a family-fitted
bias speeds evolution about 4× over uniform on the held-out member, a hand-set scaffold does
as well, and most of the gain is generic. The open part, family specificity (1.66× / 1.80×,
unresolved against 2×), keeps its last slot unspent: more seeds can at best show "real but
small". A heritable-bias follow-up goes through the strategist only.

Reopen if (once parked or closed): a richer alphabet makes non-constant thresholds sampleable
(a family with more than a constant's difference between members), 09 reopens and shows
which part of the generic speed-up a heritable bias would need to carry, or a decoder-rule
version of part 2
gets its own plan and owner go-ahead.
