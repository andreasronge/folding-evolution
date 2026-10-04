# Decision: close 06, open 07 (last shared-helper experiment)

**Close [06-self-mate-establishment](../../questions/01-map-bias/06-self-mate-establishment/question.md).**
The question is answered: yes. With self as the mate, crossover v2 at 0.3 and 0.7 lets a rare
seeded shared form win 183/240 contests, against 34/240 with a selected mate on the same cells
and seeds and 75/120 with crossover off. All 8 cells met the plan's strong-rescue row, none near
its boundary. This is proposal outcome A: the establishment barrier is mixing between lineages.
The census rules out B, since self-crossover never changes form and breaks shared only about 1
point more often. C is ruled out because all four partly-shared cells were rescued. The
reviewer's re-derivation matched the readouts in 240/240 runs, and re-running the historical
reference configs gave byte-identical results, so I trust the comparison.

**Why not close the whole shared-helper line now, as the proposal said I would under A.**
The proposal planned to stop with "shared forms are kept once common, and are rare because they
rarely arrive". The run supports the first half only. The critic and the analysis both note that
32–103 seeded copies are not one new mutant, and that arrival was never measured. Writing that
sentence into the digest would record a claim we have not shown. Two things together give a
new reason to spend one more experiment:

- the claim is cheap to test directly, with an offspring census on existing final populations
  plus a §31 F-style single-copy contest under self-mate;
- the analysis found side evidence for biased arrival: every lost shared-vs-duplicated contest
  ends partly shared, a form nobody seeded.

The test also ties the line back to the root question, "arrival of the frequent", at the level
of program forms. So I opened
[07-shared-arrival](../../questions/01-map-bias/07-shared-arrival/question.md) with budget 2 and
a written stop rule: after 07 the shared-helper line is parked or closed, whatever 07 shows.

**Other nodes.**
- 04 stays open, low priority. Its trade-off question is now answered via 06.
- 03 and 05 stay closed.
- Parked 02 is not reopened. Its condition needs the shared-helper line to stall *and* the owner
  to want fixed-target map bias settled. The line is ending, not stalling, and the second part
  is not documented. Once 07 is done, the owner should choose between 02's rarity ladder and
  root part 2 (evolving the bias).

**Uncertainty carried forward.**
- Self 0.7 vs partly from 1/10 has 5 late reversals after ≥ 95% shared. This is the reopen
  condition for 06.
- "Self-mate beats crossover off" (27 vs 19 vs duplicated from 1/32) is unclear. It rests on
  seeds shared across arms.
- Everything here is one task, L 64, and hand-built layouts.
