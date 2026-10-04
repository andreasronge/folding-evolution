---
node: questions/01-map-bias/07-shared-arrival
title: Shared arrival — offspring census plus single-copy self-mate contest
---

**Why this now.** Run 2026-10-04-1839 closed 06. Under self-mating, a seeded shared form at 3–10%
is kept and usually wins (183/240), so the establishment barrier is mixing between lineages. But
random-start runs under self-mate still end shared only 2/50, 0/50 and 2/50 times (§32 J). Two
explanations are left:
- **Arrival:** variation rarely produces exact shared children.
- **Fixation:** shared children are produced, but a single new copy rarely fixes.

The 06 proposal said I would close the line with "rare because it rarely arrives", but that claim
was never measured. The critic flagged that 32–103 seeded copies are not one new mutant. The 06
analysis adds side evidence for biased arrival: every lost shared-vs-duplicated contest ends
*partly shared*, a form nobody seeded.

**Why this beats the other open questions.** This is the last piece needed to state the
shared-helper result honestly. It measures the root's "arrival of the frequent" directly at the
level of program forms. It mostly reuses existing data, and the line stops after it whatever it
shows (written into 07).

**What would run.**
1. **Offspring census (no evolution).**
   - Parents: every non-elite individual in the final populations of §32 J self-mate L 64 /
     crossover 0.3 (50 runs) and §31 G L 64 / crossover 0.3, selected mate (50 runs). Also the
     three hand-built forms, as a reference.
   - For each parent, make K offspring with the engine's own offspring path: self-crossover v2
     at 0.3, then mutation at μ 0.015.
   - Classify each child: exact shared / partly / duplicated, or not exact. Pre-filter on the 64
     training cases and run the full exactness check only on children that pass.
   - Report the per-offspring rate of each child form, split by parent form: exact shared,
     partly, duplicated, and non-exact. Repeat with mutation only.
   - Target is about 10M children (K ≈ 100). The researcher sizes K so the census takes about an
     hour or less. If a rate is 0, report its upper bound.
2. **Single-copy contest under self-mate.**
   - Same as §31 F (`s31_few_copies.yaml`): 1 shared copy vs 1023 duplicated, and vs 1023
     partly shared.
   - L 64, crossover 0.3, `crossover_mate: self`, 300 generations, seeds 0–99.
   - 200 runs, about 16 minutes on 10 workers (06 ran at about 49 s per run).
   - Compare with crossover off (§31 F: about 3% vs duplicated, about 1% vs partly).
3. **Readout.** Expected shared establishments per run ≈ rate of exact shared children from an
   established population × 1022 offspring per generation × generations after the first
   solution (from §32 J histories) × single-copy fixation (from step 2). Compare with the
   observed 2 of 100 L 64 self-mate runs in §32 J (0.3 and 0.7).

**What each outcome would mean.**
- **A, arrival.** Exact shared children from partly or duplicated parents are rare enough that
  the product is about the observed 0.02 per run (within a factor of a few). Partly children from duplicated parents are
  far more common. Then I close 07 and the shared-helper line: "shared helpers are kept once
  common, without mixing; they are rare because variation from the forms evolution reaches first
  seldom produces them". This would be the line's contribution to the root's explanation A.
- **B, fixation.** Shared children arrive many times per run, but single self-mate copies fix
  far less often than about 1–3%, for example 0/100. Then a new copy is the bottleneck, not
  arrival. I would park the line with that, noting that seeded and newborn copies behave
  differently.
- **C, neither fits.** The predicted number is far from the observed number in either direction.
  The one-step census then misses multi-step paths through non-exact parents. I would park the
  line with the path question as its reopen condition.

**Limits stated up front.**
- Final populations are established populations. They give the arrival rate *into* a population
  that is already solved, not at first discovery, because mid-run snapshots do not exist.
- The task is the same as before (one task, L 64).

**Alternatives considered.**
- **Root part 2, letting the map's bias evolve across a task family.** This is the bigger
  untested half of the core question and the natural next direction. It needs a plan file first.
  I suggest the owner commission one so it is ready when 07 ends.
- **02's rarity ladder.** The reopen condition is not met: the line is ending, not stalling, and
  no owner wish is recorded. The owner can choose it instead of part 2 after 07.
- **Fresh-seed replicate of 06.** This would check whether self-mate really beats crossover off
  (27 vs 19). The result is unclear and would not change a decision.
- **04's duplication-only companion.** It explains how self-mating discovers. It does not decide
  anything.

**Tree edits made with this proposal.**
- Closed 06.
- Opened 07 (budget 2, with a stop rule).
- Updated 04's summary, the root question and log, and the digest.
