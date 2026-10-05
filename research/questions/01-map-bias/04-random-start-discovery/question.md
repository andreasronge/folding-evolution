---
status: parked
tags: [shared-helper, stage-4, random-start, crossover, crossover-mate, first-form-persistence, shortcuts, training-cases]
budget: {experiments: 3, used: 0}
---
# From random starts, does discovery need mixing between lineages, and which form arrives and persists?

Current summary: From random starts, crossover v2 is what solves (48–50 of 50 runs solve the
training cases at L 64/128; 0–4 of 50 reach a fully exact individual without it), and the form
of the first established exact population is kept in 121 of 129 runs (§31 G). Solutions arrive
mostly partly shared or duplicated; a B helper ends the run in 8 of 450 runs, and about half of
training-solved runs end as shortcut populations that fit 64 cases without being exact. §32
J: discovery does not need mixing between lineages. Crossing a parent with itself solves
34–40 of 50 runs by generation 3000, but about three times more slowly than a selected mate
(median gen 2120 vs 730); a random mate solves 2 of 50, like crossover off. L: 256 cases do not
remove shortcuts (9 of 35 still end as shortcuts, all failing only the OR output), so they are
structural, not a 64-case artefact. G2: shared verdicts are 4 in 100 at L 64/0.3. Establishment
under self-mating was tested in [06](../06-self-mate-establishment/question.md): a seeded
shared form is kept at about the crossover-off rate, so the discovery–establishment trade-off
is not forced. Open here only: Fable's duplication-only companion and the 0.3 vs 0.7 parity.

Competing explanations:
- A: Discovery needs mixing between selected lineages, so the trade-off with establishment
  (03) is real.
- B: Discovery needs only v2's run-level rearrangement (cut branch deletes and duplicates run
  segments); self-mate crossover would solve about as often and the trade-off is not forced.
- C: Foreign material is enough: random-mate succeeds where self-mate fails.
- (shortcuts) D: shortcut populations are a 64-case training-sample effect (≥ 45 of 50 exact
  verdicts at 256 cases) vs E: they are structural.

Related: [01-map-bias](../question.md),
[03-rare-shared-establishment](../03-rare-shared-establishment/question.md),
[05-latent-helper](../05-latent-helper/question.md),
[06-self-mate-establishment](../06-self-mate-establishment/question.md),
[07-shared-arrival](../07-shared-arrival/question.md),
[notebook §31 G](../../../../docs/map-bias/notebook.md),
[Plans/s32-mate-latent-cases.md](../../../../Plans/s32-mate-latent-cases.md) (arms J, L, G2
and Fable's readings), sweeps `experiments/chem_tape/sweeps/mapbias/s32_mate.yaml`,
`s32_cases256.yaml`, `s32_stage4_more.yaml`, report script `experiments/chem_tape/s32_report.py`

Not yet shown (§31): why 0.3 and 0.7 discover equally well while 0.1–0.3 already blocks
establishment; the 20-generation census can miss a brief earlier "first form".

Reopen if: 07 reopens and needs random-start dynamics (e.g. where B-helper children first
arrive), or the shared-helper line resumes; then run Fable's duplication-only companion
(crossover 0, `run_duplication_rate`) first, as it is the cheapest open item.
