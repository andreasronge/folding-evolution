---
status: open
tags: [shared-helper, latent-helper, establishment, crossover, helper-first, tagged-runs]
budget: {experiments: 3, used: 0}
---
# Does a helper run already present in the host let a rare shared form establish under crossover?

Current summary: §30 found that crossover removes a rare shared form from both sides; one
branch is that its RECV consumers land in hosts without a tag-3 (B) run. §32 arm K tests a
"helper first, readers later" route: shared from 1/32 and 1/10 (and single copies) against
"partly shared plus an unread B run" (34 cells), crossover 0 / 0.1 / 0.3 / 0.7, L 64, plus a
competitor-alone arm measuring how fast the unread B run decays. Built at `805a641`; results
not yet recorded.

Competing explanations:
- A: The barrier is the missing helper: with a B run already in the host, shared wins from
  1/10 at crossover 0.3–0.7, and "helper first" is a route.
- B: Recipient-side conversion alone is enough: shared still loses, because as recipient it
  takes self-contained consumer bodies and stops being shared (75% of homologous children in
  Fable's §30 enumeration).
- C: The unread B run decays before it can matter (unread runs are purged under crossover);
  the competitor-alone arm checks this.

Related: [01-map-bias](../question.md),
[03-rare-shared-establishment](../03-rare-shared-establishment/question.md) (the barrier this
probes), [04-random-start-discovery](../04-random-start-discovery/question.md),
[notebook §30](../../../../docs/map-bias/notebook.md) ("Both crossover branches remove the
shared form"; a probe repairing only the donor case rescued 0/6),
[findings Setup "Tagged crossover loses runs"](../../../../docs/map-bias/findings.md),
[Plans/s32-mate-latent-cases.md](../../../../Plans/s32-mate-latent-cases.md), sweeps
`experiments/chem_tape/sweeps/mapbias/s32_latent_rare.yaml`, `s32_latent_copy.yaml`,
`s32_latent_alone.yaml`
