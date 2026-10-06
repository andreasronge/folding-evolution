---
next: strategy
---
# Decision — 2026-10-06-2229 (16, frozen crossed maps on the three holdouts)

**Close [16](../../questions/10-compositional-map-transfer/16-crossed-family-adaptation/question.md);
no proposal; return to strategy.**

Outcome row 4 ([analysis](analysis.md)), complete data, commit `33fcee2`. The 20 frozen stage-1
token maps and G4 on the three withheld cells, 400 shared seeds each:

- Every arm beats G4 on every holdout, 1.97×–2.93×, all six lower bounds ≥ 1.63×. Holdout gains
  match or exceed the training gains.
- Matched over mismatched: BE 1.02× [0.835, 1.2485], PA 0.96× [0.79, 1.15]; interaction 0.98×
  [0.83, 1.15]. No matched advantage detected; one above about 1.25× excluded in both directions
  (on BE only just — dropping one of 14 maps lifts the bound to 1.25–1.30); a 1.1× preference
  is not excluded.

Why close rather than continue: 16 asked whether matched training beats mismatched training on
the withheld cells. At the design's resolution the answer is no detectable difference, with
generic transfer of 2–3×. Explanation B fits, C does not apply (mismatched arms improve G4), D
was out after stage 1; A is not supported but not excluded below about 1.25×. Detecting a true
1.1× would need about 64–75 trajectories per family (14–30 h of learning), and with both point
estimates within 0.06 log2 of zero that spend would most likely buy a tighter bound around 1,
not a detection. The BE direction also rests on one task, which more trajectories cannot fix.
16 keeps a reopen condition (more BE holdouts, a context-changing learner with a resolved gain,
or an owner-funded detection run).

Why strategy and not a proposal: strategy 1723 reserved root 10's last slot (9 of 9) for a
decision after this result, and the remaining candidates are new directions rather than a
continuation of 16 — a mechanism arm (union-trained or family-scrambled maps: is the generic gain
a better prior for the reducer family or a fix of G4's weak spots?), a learned-context learner on
this bank, or wrapping up root 10's part-2 answer. Choosing among them, or moving to root 01 (no
budget left), is the strategist's call.

Parked questions re-checked (02, 04, 07, 08, 09): no reopen condition is met. 08's
"decoder-rule version of part 2" is what root 10 already is; 2229 adds no new task family with a
no-lift speed-up (09a).

Digest-check notes 6–8 from critique.md are fixed in the digest, in 16's question.md, and as
corrections in 16's log ("small" → unresolved estimates; "2 tied" → within 0.02 log2 of zero;
"no map hurt the other family" → positive estimated gains averaged over the other family's
training cells, arm-level gains resolved).
