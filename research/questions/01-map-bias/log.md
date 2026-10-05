# Log: 01-map-bias

## Seeded 2026-10-04 from prior work

Notebook: [docs/map-bias/notebook.md](../../../docs/map-bias/notebook.md); findings:
[docs/map-bias/findings.md](../../../docs/map-bias/findings.md). Items below are the
root-level history; child questions carry their own logs.

- §1–§2 (commit 67413dd): reframe to GP-map bias; 50M random tapes per decoder setup, AND neighbourhood probe → map bias predicts easy tasks, not hard ones; chem decoder ≈ direct encoding; AND proxy basin is a wide valley (findings items 1–2). [notebook §1–§2](../../../docs/map-bias/notebook.md)
Decision: reframe the core question to GP-map bias in two parts, measure the bias and evolve the bias (README "Core Question"), and run it as a light hobby notebook because the rigor apparatus had grown larger than the findings it supported (2026-09-25). Part 2 (evolve the bias) has not been started.
- §3–§14 (commit e05aa5f): MIN token, lexicase, v3 domains, tagged runs, OR race, varying goals, combine markers → lexicase supplies blocks; tagged runs make transplants safe; crossover merges blocks when the join is cheap, but the advantage is the join's cost (items 3–10). [notebook §3–§14](../../../docs/map-bias/notebook.md)
Decision: stop the first line at §14 because the open follow-on (a join built across a valley) was judged a separate project.
- §15–§16 (commit 7c9cc42, results 90867ad): op_weights frequency knob, XOR → frequency changes how often a part is made, not what is reachable (item 12). [notebook §15–§16](../../../docs/map-bias/notebook.md)
- §17–§26 (commits e3e3ff1 … 08b315e, closed at 3ee1230 and a419d40): valley crossing, XOR without a free join, population-level exactness, crossover v2 and v1c → joins are built by small edits; no valley found; crossover assembly changes XOR discovery (items 13–16). [notebook §17–§26](../../../docs/map-bias/notebook.md)
Decision: close the XOR/valley thread because the join question was answered and no valley was found (3ee1230).
Decision: skip valley-crossing Step 2 and pivot to folding vs direct map bias (2f681a3) because helper signals were weak and any effect would sit inside the range crossover assembly alone moves.
- §27–§28 (commits cd7d463, f483aaf + a86c49c): folding vs direct, nights 1–2 → see [02-fixed-target-sampling](02-fixed-target-sampling/log.md).
Decision: return to the building-block question (shared-helper reuse, Plans/shared-helper-reuse.md) because nights 1–2 answered "which map samples solvers more often", not whether the chemistry helps discover, preserve and reuse parts (826fb68).
- §29 (commits 9848d08, 7141ecf; write-up 441be87, review 26688f4): shared-helper stages 1–3, hand-built shared / partly shared / duplicated forms, seeded populations → shared form persists from 100% and takes over from 50% at L 64/128; from duplicated starts evolution shares A (cheap RECV0) but never factors out a B helper; seed-dup speed was likely helped by tag-0 latent cells. [notebook §29](../../../docs/map-bias/notebook.md)
Decision: test establishment from a small share next (§30) because a newly discovered shared genome starts rare and Fable's 3-seed probe showed it wiped out with crossover on.
- §30–§31 (commits d49f4ec, 8844b6c; write-ups a623cb3, 3587de6, 4d44db3, d8e8725): establishment, dose, reciprocal, few copies, stage 4 → see [03-rare-shared-establishment](03-rare-shared-establishment/log.md) and [04-random-start-discovery](04-random-start-discovery/log.md).
Decision: drop the planned tie-break toward fewer cells because evolved shared forms are not smaller (§31, Fable's twentieth review).
- §32 (commit 805a641): crossover mate (J), latent helper (K), 256 cases (L), more stage-4 seeds (G2) built and committed; results in notebook §32 (dd684f9, 298c1de) → see [04](04-random-start-discovery/log.md) and [05](05-latent-helper/log.md).
Decision: close 05 (latent helper does not help); keep 04 open on the self-mating establishment test.
- Run 2026-10-04-1839 (commit f2e4048): self-mate contest, 240 runs + self-crossover census → shared wins 183/240 vs 34/240 with a selected mate and 75/120 with crossover off; no early loss; no form change under self-crossover. See [06](06-self-mate-establishment/log.md).
Decision: close 06 (barrier is mixing between lineages) and open [07-shared-arrival](07-shared-arrival/question.md) as the last shared-helper experiment, because the line cannot be closed honestly on "shared is rare because it rarely arrives" until arrival and single-copy fixation are measured. After 07 the line is parked or closed and attention moves to part 2 (evolving the bias) or 02.
- Run 2026-10-04-2135 (commit f418c91): shared-arrival census (173.7M children from 50 §32 J self/0.3 final populations) + 100 natural single-copy insertions → exact shared children arrive about 2 per run in established partly populations, all A-only/other, 0 B-helper; 0 of 100 single copies established (≤ 3.6%), all lost within 30 generations. See [07](07-shared-arrival/log.md).
Decision: park 07 (both factors may limit; bounds too broad to call it arrival- or fixation-limited) and park 04, which ends the shared-helper line as 07's stop rule said. Open [08-evolve-bias](08-evolve-bias/question.md) for the README's part 2, because it is the root's only untested half and 02's reopen condition still needs an owner wish that is not recorded.
