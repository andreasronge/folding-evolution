# Log: 03-rare-shared-establishment

## Seeded 2026-10-04 from prior work

- §29 (commits 9848d08, 7141ecf; write-up 441be87, review 26688f4): hand-built shared / partly shared / duplicated forms, variation alone, seeded retention → shared form persists from 100% and takes over from 50% at L 64/128; Fable's 3-seed probe: from 10% or 1/32 with crossover 0.7 it is gone within 15 generations (9/9), from 10% with crossover off it won (3/3). [notebook §29](../../../../docs/map-bias/notebook.md)
Decision: measure establishment from a small share (§30) because a newly found shared genome starts rare, so "discovery is the obstacle" was premature.
- §30 (commit d49f4ec; write-up a623cb3, review a6a9f66): arms A (vs duplicated), B (vs partly shared), 1/32 to 1/2 shared, crossover 0.7 or 0, 300 generations; arm C seed-dup with random latent tags → with crossover on, a rare shared form is lost in 294/300 runs and wins none; with crossover off it often wins (vs duplicated from 1/10: 29/30 and 26/30); partly shared is the stronger competitor; both crossover branches remove the shared form; arm C converts to partly shared 7–9× more slowly than §29. [notebook §30](../../../../docs/map-bias/notebook.md)
Decision: run dose (D), reciprocal (E), few copies (F) and stage 4 (G) (Fable's programme, Plans/s31-dose-reciprocal-stage4.md) because §30 tested only crossover 0 and 0.7 and only seeded starts.
- §31 D/E/F (commit 8844b6c; write-ups 3587de6, 4d44db3, d8e8725): crossover dose 0.1/0.3/0.5; shared at 3/4 to 31/32; 1 and 8 copies with crossover off, 100 seeds → barrier graded vs duplicated, steep vs partly shared (0.3 stops it at both lengths); majority rule 270/270, not symmetric at 1/4; single-copy wins match independent copies (~3% vs duplicated, ~1% vs partly). [notebook §31](../../../../docs/map-bias/notebook.md)
Decision: treat the hand-built establishment question as answered and ask instead whether a helper already in the host changes it (K, §32) and whether discovery needs lineage mixing (J, §32), per Fable's twentieth review.

Status at seeding: closed (hand-built contest). Follow-ups live in 04 and 05.
