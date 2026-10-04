# Log: 04-random-start-discovery

## Seeded 2026-10-04 from prior work

- §31 G (commit 8844b6c; write-ups 3587de6, 4d44db3, d8e8725): stage 4, random starts, L 32/64/128 × crossover 0.7/0.3/0, 50 seeds, 3000 generations → with crossover, fully exact reached in 41–43/50 (L 64/128) and 11–15/50 (L 32); without, 0/2/4 of 50; first established form kept in 121 of 129 runs; shared is the final verdict in 13 of 450 runs, of which 8 have a B-type helper (often "B shared, A duplicated"); 2 established populations changed to a helper form from inside; 92 of 196 training-solved runs end as shortcut populations; 32 cells does not force sharing; evolved shared forms are not smaller. [notebook §31](../../../../docs/map-bias/notebook.md)
Decision: correct the first-form persistence count (4d44db3) and the "genuine pure helpers" claim in 3587de6's message (d8e8725: 8 of 13 shared verdicts are B-type, 5 share only A) because Fable's twentieth review decoded the genomes.
Decision: run J (crossover mate), L (256 training cases) and G2 (seeds 50–99 of L 64/0.3) because §31 could not separate lineage mixing from v2's run-level rearrangement, and shortcuts might be a training-sample effect (Plans/s32-mate-latent-cases.md).
- §32 J/L/G2 (commit 805a641): `crossover_mate` option (selected / self / random, hash-neutral at default); 200 + 50 + 50 runs queued in `experiments/chem_tape/sweeps/mapbias/queue_s32.yaml` → results not yet recorded in the notebook or present in this checkout (2026-10-04). [Plans/s32-mate-latent-cases.md](../../../../Plans/s32-mate-latent-cases.md)
