---
status: closed
tags: [shared-helper, establishment, crossover, crossover-mate, self-mate, tagged-runs]
budget: {experiments: 2, used: 0}
---
# Can a rare shared form establish when every crossover is with the parent itself?

Current summary: Yes. With self as the mate, crossover v2 at 0.3 or 0.7 does not remove a
rare shared form: it wins 183/240 seeded contests against 34/240 with a selected mate in the
same cells and seeds, and at least as often as with crossover off in every cell (run
[2026-10-04-1839](../../../runs/2026-10-04-1839/analysis.md), commit f2e4048). Shared share
does not fall early, and no self-crossover child changes form. So the establishment barrier
is mixing between lineages (A), and discovery (§32 J) and seeded establishment can coexist
under self-mating. Soft spot: at 0.7 against partly shared, 5 runs reached ≥ 95% shared and
then fell back. Limits: hand-built layouts, 32 or 103 copies, L 64, one task; nothing about
arrival or single copies.

Competing explanations:
- A: The barrier is mixing between lineages (hybrids). **Supported.** Under self-mating, shared wins about
  as often as with crossover off (§30/§31 D crossover-0 column), so discovery and
  establishment can coexist under one operator.
- B: v2's run-level rearrangement itself (segment deletion/duplication) hurts the shared form
  more than its competitors, because one deleted helper run breaks several outputs. Under
  self-mating shared still loses, and the hybrid account is incomplete. Not supported (census: 20% vs 19% broken, no form change).
- C: In between: self-mating removes most of the barrier against duplicated but not against
  partly shared (the steeper contest in §31 D). Not supported (all four partly cells rescued).

Related: [01-map-bias](../question.md),
[03-rare-shared-establishment](../03-rare-shared-establishment/question.md) (the selected-mate
contest this repeats), [04-random-start-discovery](../04-random-start-discovery/question.md)
(self-mate discovery, §32 J), [05-latent-helper](../05-latent-helper/question.md),
[notebook §31 D, §32 "Next"](../../../../docs/map-bias/notebook.md),
[07-shared-arrival](../07-shared-arrival/question.md) (the follow-up),
sweeps `experiments/chem_tape/sweeps/mapbias/s31_dose.yaml` (contest setup) and
`self_mate_establishment.yaml`, script `experiments/chem_tape/self_mate_establishment.py`

Note: the "yes" makes arrival the likely limit but does not show it: self-mated random starts
ended shared in only 2/50, 0/50 and 2/50 runs (§32 J), no more than with a selected mate, and
32–103 seeded copies are not one new mutant (critic). Tested in 07.

Reopen if: a fresh-seed replicate shows self-mate establishment clearly below crossover off,
or the late reversals at crossover 0.7 against partly shared (5 of 30 runs from 1/10)
recur at other rates or lengths, which would mean "kept once common" fails under self-mate.
