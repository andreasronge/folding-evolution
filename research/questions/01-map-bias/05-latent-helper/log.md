# Log: 05-latent-helper

## Seeded 2026-10-04 from prior work

- §30 (commit d49f4ec; write-up a623cb3): Fable's enumeration of crossover v2 at L 64 → a shared recipient takes self-contained bodies (75% of homologous children stay exact but stop being shared); a shared donor's RECV3 consumers land in hosts without a tag-3 run and die; a probe repairing only the donor case did not rescue a rare shared form (0/6). [notebook §30](../../../../docs/map-bias/notebook.md)
- §31 (commit d8e8725, Fable's twentieth review): proposed arm K, shared vs "partly shared plus an unread B run".
Decision: build and launch K with J and L right away, after at most two Codex reviews, because the owner asked for §32 to be built and launched immediately (Plans/s32-mate-latent-cases.md).
- §32 K (commit 805a641): 180 rare-start runs (crossover 0.1/0.3/0.7), 200 single-copy runs (crossover 0 and 0.3, 100 seeds), 30 competitor-alone runs → results not yet recorded in the notebook or present in this checkout (2026-10-04). [Plans/s32-mate-latent-cases.md](../../../../Plans/s32-mate-latent-cases.md)
- §32 K results (write-up dd684f9, Fable's twenty-first review 298c1de): shared wins 4/0/0 of 30 from 1/32 and 15/2/0 of 30 from 1/10 at crossover 0.1/0.3/0.7 (without the B run: 2/0/0 and 11/0/0); single copies 2 of 100 at crossover 0 (vs 0). One crossover with shared as mate: 21% broken / 54% partly / 25% shared children with the B run, 63/30/7 without. Shared share halves within 5 generations at 0.3 while the B run is still intact in ~30% of hosts. [notebook §32](../../../../docs/map-bias/notebook.md)
Decision (recorded at seeding, steward to confirm): close. A helper already in the host does not let a rare shared form establish at crossover ≥ 0.3; the barrier is recipient-side conversion to partly shared (B), not a missing or decayed helper.

## 2026-10-04, steward

Decision: confirm close because §32 K showed no detectable gain at any crossover rate and the
contest is lost while the B run is still present (recipient-side conversion, B).
