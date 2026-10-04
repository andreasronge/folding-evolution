# Review of map-bias §32 (twenty-first)

**Verdict:** every number in the §32 tables matches the raw outputs, and `crossover_mate: self` is free of mixing. Four readings need changing: the K mechanism, the "B run intact" column, the J "random mate" reading, and the L provenance and comparison.

I edited no files; `experiments/output/2026-10-04/s32/fable_review.md` is still the empty placeholder. Scratch scripts are in `/tmp/s32rev`.

**What I ran:**
- `s32_report.py` re-run on all 895 runs into `/tmp`: the tables are identical to the committed report.
- Tallies, Fisher tests, time to training-solved and L run timing recomputed from `result.json` and `s32_runs.json`.
- Two small simulations with the repo's own operators: decay of the unread B run under mutation alone, and one generation of crossover v2 between the hand-built forms.

## Findings

1. **Must fix — K: "an unread helper decays before it can be used."** The contest is lost while the helper is still there, so decay is not the cause.
   - Under mutation alone the unread B run is intact in 78% of genomes after 1 generation, 30% after 5 and 10% after 10 (my simulation, 20,000 genomes, `mutate_batch` at 0.015).
   - From 1/10, the shared share among exact genomes is already 0.053 at generation 5 with crossover 0.3 and 0.023 with 0.7 (start 0.099).
   - One crossover between the shared form and the competitor, shared as the mate:

     | competitor | broken | partly | shared |
     |---|---|---|---|
     | partly shared (§31 D) | 63% | 30% | 7% |
     | partly shared + B run (K) | 21% | 54% | 25% |

   - So the B run does repair the hybrids. They are then classed, and function, as partly shared, because a child with one recomputing reader has a single-reader helper.
   - Replace the last K bullet with: "So a helper already in the host does not let a rare shared form establish at crossover 0.3 or more. The B run repairs the hybrids (21% broken against 63% without it), but 54–61% of shared × competitor children are partly shared and 22–25% shared. The shared share halves within 5 generations at 0.3, while the B run is still intact in about 30% of hosts."

2. **Must fix — "B run intact at end" mixes read and unread helpers.** The 0.09 and 0.03 are the shared winners' own, read, B run.
   - In runs where shared is gone, the B run is intact in 0.4–0.5% of genomes in every cell (largest single run 2%).
   - In the 1/10, 0.1 cell: 0.18 in the 15 won runs, 0.004 in the 14 gone runs.
   - Replace "at the end it is intact in 0–9% of genomes, and in 0% when the competitor runs alone" with: "where shared is gone, the B run is intact in under 1% of genomes at the end, the same as when the competitor runs alone."
   - Replace "Unread helpers decay within a few hundred generations under mutation and crossover" with: "An unread 7-cell run has a half-life of about 3 generations under mutation alone (simulation; no intermediate census in the runs)."

3. **Must fix — L provenance: 25 runs finished before the timeout, not 35.**
   - `sweep_index.json` lists 25. The other 10 (seeds 15 and 26–34) were written between 14:04 and 15:09 UTC, after the kill at 13:51, by workers that outlived the killed sweep.
   - These runs are complete (3000 generations, 151 censuses) and deterministic, so I would keep them.
   - The orphans ran alongside G2, which is why G2's median is 768 s against 437 s in §31. Outcomes are unaffected.
   - L runs took 25–124 minutes (median 50), not 25–50.
   - Replace the provenance bullet with: "L timed out at its 2.5-hour cap with 25 runs done. The 10 runs in flight (seeds 15, 26–34) were not killed and finished up to 78 minutes later, alongside G2. L is PARTIAL: 35 of 50 seeds (0–34). Runs took 25–124 minutes."

4. **Should fix — J: "a random mate does nothing" and "foreign random material adds nothing".** The random arm does not isolate foreign material.
   - Two random genomes rarely share a tag, so nearly every random-mate crossover takes the cut branch: the parent's tail runs are replaced by random runs.
   - That arm never duplicates the parent's own runs. Self-mating does: of 20,000 self-crossovers of a 4-run genome, 60% are clones, 20% duplicate a segment and 20% delete one.
   - Replace the random-mate bullet with: "With a random genome as mate, 2 of 50 solve, as with crossover off. This arm replaces the parent's tail runs with random runs and never duplicates the parent's own, so it shows that deletion plus random runs does not help. It does not test foreign material alone."
   - Replace "A random mate is no substitute for selected mixing: it behaves like crossover off" with: "A random mate solves as rarely as crossover off (2 of 50 each)."

5. **Should fix — J: "rearrangement does most of the discovery" needs its horizon.** The counts are right, but self-mating is about three times slower and still solving at the end.
   - Median generation of training-solved at L 64 / 0.3: 730 with a selected mate, 2120 with self.
   - Solved by generation 2000: 44 against 24. Solved between 2000 and 3000: 4 against 10.
   - Self against selected is significant in all three cells (Fisher p = 0.0004, 0.008, 0.004); self against crossover off is 34 against 2.
   - The plan had no branch for this outcome: it is between "about as often" and "fails".
   - Replace the heading with: "J: rearrangement within a genome is enough for most runs to solve within 3000 generations (34–40 of 50, against 2 without crossover); a selected mate makes it about three times faster."
   - Replace "So mixing between selected lineages adds a further 9–14 training-solved runs per 50 on top of rearrangement" with: "With a selected mate, 9–14 more runs per 50 have solved by generation 3000. Self-mated runs are still solving at the end, so the gap depends on the horizon."
   - Replace "Most discovery comes from v2's rearrangement within a genome" with: "Rearrangement within a genome is enough for discovery in 68–80% of runs by generation 3000."

6. **Should fix — "The trade-off is weaker than §31 suggested."** This rests on an untested step, which the text admits one bullet later. Replace the heading with: "The discovery–establishment trade-off may not be forced: discovery does not need mixing, but establishment under self-mating was not tested."

7. **Should fix — L: "256 training cases reduce shortcuts" and "from 40% to 26%".** The reduction is not shown, and the 40% counts two unsolved runs as shortcuts.
   - On the same seeds (0–34), 64 cases give 23 exact populations of 35, against 26 with 256. Seed by seed: 7 gained, 4 lost.
   - Shortcut populations among training-solved runs: 18 of 48 (38%) with 64 cases on all 50 seeds, 11 of 34 (32%) on seeds 0–34, and 9 of 35 (26%) with 256.
   - The plan's 90% line is 32 of 35; 26 is clearly below it, so "not only a training-sample effect" stands.
   - Replace the heading with: "L: 256 training cases do not remove shortcuts (PARTIAL, 35 seeds)."
   - Replace the "partly a training-sample effect" bullet with: "Shortcut populations are not only a training-sample effect: 9 of 35 training-solved runs end as shortcuts with 256 cases, against 11 of 34 with 64 cases on the same seeds. A reduction is not shown (26 against 23 exact populations of 35)."

8. **Should fix — K: "barely helps".** No cell differs from its no-B reference: 15 against 11 of 30 (p = 0.43), 2 against 0 of 30 (p = 0.49), 4 against 2 of 30 (p = 0.67), 2 against 0 of 100 (p = 0.50). Replace the heading with: "K: a latent B helper gives no detectable gain to a rare shared form." All four differences do point the same way, which is worth a clause.

9. **Note — self-mating is clean.**
   - Both reproduction paths pass the parent itself as mate, and the child holds only the parent's runs.
   - The homologous branch with self copies the first run of a tag over later runs with the same tag (probability 1/2 each). Those later runs are unexpressed under leftmost-wins, so this is silent.
   - Rearrangement dose is matched: the cut branch fires in half of the crossovers in both arms once the population shares tags.

10. **Note — the timeout did not bias which seeds finished.** Seeds 0–34 are exactly the first 35 dispatched: 25 done plus all 10 in flight. Run time barely differs by outcome (mean 3204 s for exact endings, 3484 s for shortcut endings).

11. **Note — shortcuts sit in the OR output.**
    - All 9 L shortcut runs are inexact on output 2 only (0–2% of the census exact there; outputs 0 and 1 are normal). Holdout fitness is 0.997–1.0.
    - With 64 cases, 12 of the 18 shortcut runs at L 64 / 0.3 fail on output 2 only, 3 on output 1 only and 3 on both.

12. **Note — mate type does not change the shortcut share.** Exact populations among solved runs: 50–55% with self, 53–62% with a selected mate.

13. **Note — checked and sound.**
    - 695 new runs plus 200 reference, no duplicate keys, none short.
    - Every K, J, L and G2 cell; the "without the B run" column against §31 D, §30 and §31 F.
    - Census wins equal the full tally in every K cell.
    - All 9 K "in between" runs hold 1–2 shared genomes in about 400; 8 are a frozen shared slot-0 elite (seeds 4, 9, 16, 27), as in §31.
    - Fisher p = 0.25 for 26/35 against 30/50; 4 shared verdicts in 100, all B-type; 0 of 50 against 4 of 50 is p = 0.12.
    - The "other" shared verdict in L (seed 14) is a helper that is a function of neither the sum nor the max.

## Next

The most informative step is §31 D's contest under self-mating: shared from 1/32 and 1/10 against partly shared and duplicated, at `crossover_mate: self`, 0.3 and 0.7, 300 generations.
- If shared wins as often as with crossover off (19 of 30 from 1/10), discovery and establishment can coexist under one operator.
- If shared still loses, the barrier is not mixing, and finding 1's hybrid account is wrong.

A cheap companion is crossover 0 with `run_duplication_rate` on, from random starts. It would say whether duplication alone is the part of self-mating that finds solutions.
