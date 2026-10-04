# Review of map-bias §30 (nineteenth)

**Verdict:** every number in the §30 tables matches the raw outputs, and the headline (a rare shared form is lost with crossover at 0.7) stands. Three readings are too strong: "crossover is the obstacle" for a new genome, the mechanism candidate, and the size-knob sentence. One run that lost the solution is counted as a form outcome.

**What I ran** (nothing written to the repo):
- **Recompute:** all table cells from the 1080 `result.json` files.
- **Final populations:** all 1020 arm A/B populations re-classified by knockout, elites kept separate.
- **Crossover enumeration:** the real v2 operator on each pair of forms, 20,000 children per pairing, split by branch (L=64).
- **Evolution probes:** 27 runs of 150 generations at L=64 (3 seeds per cell) and 10 random-start runs of 600 generations. Pointers, not results.

## Findings

1. **Must fix — "crossover is the obstacle" for a newly discovered genome.**
   - Sentence: "For a newly discovered shared genome, crossover is the obstacle."
   - A new genome starts as one copy; the smallest start tested is 32 copies.
   - With crossover off, 32 copies still lose to partly shared in 22/30 and 23/30 runs (L 64/128). If copies are independent, that is about 1% establishment per copy against partly shared and about 3% against duplicated.
   - The frozen elite (finding 4) agrees: with crossover off, seed 4 from 1/10 against partly shared kept an immortal shared elite for 300 generations and ended with 1 shared individual of about 425 exact ones, at both L=64 and L=128.
   - Replace with: "For a rare shared form (32–103 copies), crossover at 0.7 is a sufficient obstacle. Crossover off does not make establishment likely from a single copy: 32 copies lose to partly shared in 22–23 of 30 runs at 64 and 128 cells, roughly 1% per copy."

2. **Must fix — the mechanism candidate is not the main drain.**
   - Sentence: "Homologous body swaps putting `RECV3` consumers into hosts without a tag-3 run is the obvious candidate, but it was not isolated."
   - Enumeration at L=64, shared × competitor (duplicated and partly shared give near-identical numbers):

     | pairing | branch | shared | converted (exact, not shared) | dead |
     |---|---|---|---|---|
     | shared = parent A | homologous | 0.25 | 0.75 | 0.00 |
     | shared = parent A | cut | 0.20 | 0.40 | 0.40 |
     | shared = parent B | homologous | 0.00 | 0.25 | 0.75 |
     | shared = parent B | cut | 0.15 | 0.35 | 0.50 |

   - The larger loss is conversion: a shared recipient takes a self-contained consumer body and stays exact. The `RECV3`-without-helper case is the lethal half, when shared is the donor.
   - One round of crossover at 0.7 cuts a rare shared share by about 35% (1/32 → 0.019, 1/10 → 0.065), which fits extinction by generation 5–12.
   - I tried the repair (a taken body brings the donor's runs it reads). In the model 1/32 → 0.022 instead of 0.019; in evolution from 1/10 it won 0/6 runs.
   - Replace with: "Both branches remove it. As the recipient, a shared genome takes self-contained consumer bodies and its children stay exact but stop being shared (75% of homologous children). As the donor, its `RECV3` consumers land in hosts without a tag-3 run and the children die. A probe that repaired only the second case did not rescue a rare shared form (0/6)."
   - In **Next**, drop "lets a consumer travel with its helper" as the change worth trying, and drop the "cheaper first step"; the table above is that step.

3. **Must fix — one arm A run lost the solution and is counted as "lost".**
   - Arm A, 1/4, crossover 0.7, L=128, seed 9: the census has under 20 fully exact individuals at 47 log points from generation 70. It ends with 1 in the sample and 3 of 1022 in the population; training-perfect is 0.39.
   - It is the same seed and shortcut as §29 (sum > 15). The "lost" verdict rests on one individual.
   - Table cell "12 / 15" should read "12 / 14 (1 lost the solution)".
   - Replace "No run in arms A or B ended without a fully exact individual" with: "No run in arms A or B ended with zero fully exact individuals in the sample, but seed 9 (arm A, 1/4, crossover 0.7, L=128) lost the solution from generation 70 and is not counted as a form outcome."
   - Arm C, L=128, seed 9 has the same problem: no fully exact individual at 32 log points (last at 990), with a return at generation 1000. "0/30 lost" hides it.

4. **Should fix — the "in between" seeds with crossover on are the frozen elite.**
   - Slot 0 holds its generation-0 genome at generation 300 in 1020/1020 runs. It is shared in about 1/k of seeds.
   - Of the 17 in-between seeds in crossover-on cells, 16 are that elite plus 0–6 of its children in the sample. Only arm B, 1/2, L=64, seed 17 (0.88) is a real mix.
   - Counting non-elites in the whole population at ≤ 1/10 with crossover on: 290 of 300 runs have no shared individual, and 10 have 1–2 among 300–390 exact ones (9 of those have a shared elite).
   - This strengthens the result: in seeds 4, 9, 16 and 27 an immortal shared parent fed children in for 300 generations and never established.
   - With crossover off, seeds with a shared elite win about as often as the rest (for example 5 of 8 against 19 of 30).
   - Replace "Few seeds end in between" with: "Few seeds end in between, and with crossover on all but one of those are the seeded elite in slot 0, which never changes, plus a few of its children."

5. **Should fix — "hits 0 at a median of generation 5–12".**
   - This is the first census with no shared individual among 70–110 sampled exact ones, and generation 5 is the first log point.
   - In 3–9 runs per cell a shared individual shows up again later (up to generation 295); those are the elite of finding 4.
   - Replace with: "It drops below what the census can see (none among 70–110 sampled exact individuals) at a median of generation 5–12; 5 is the first log point."

6. **Should fix — arm C "5–8 times more slowly".**
   - The medians 390 and 640 cover only the 23 and 22 runs that converted. Over all 30 seeds the median is about 545 (L=64) and 715 (L=128), so 7–9 times, and a lower bound.
   - The random latent tags are one fixed draw per length. The L=128 draw happens to put tags 0, 1 and 2 on body cells; the L=64 draw has none. So 390 vs 640 cannot be read as a length effect.
   - Replace with: "about 7–9 times more slowly at least (all-seed median near generation 545 and 715, against 80; 7–8 runs had not converted by generation 1000). The latent tags are a single draw per length."

7. **Should fix — "a pure B helper still practically never appears" is confounded.**
   - Arm C ran with crossover at 0.7, which by this section's own result removes a rare shared form within generations. A census of 256 every 10 generations cannot see short-lived single individuals.
   - Add: "Arm C cannot separate 'never discovered' from 'discovered and removed by crossover'."

8. **Should fix — the size-knob sentence contradicts the results above it.**
   - Sentence: "The size knob matters only against partly shared, and only with a large start share."
   - With crossover off, 32 cells also does better from small shares: 15 vs 8 and 7 from 1/32, and 24 vs 19 and 16 from 1/10.
   - Arm A has no 32-cell arm, so "only against partly shared" was not tested.
   - Replace with: "Against partly shared, 32 cells helps: 29/30 vs 13–16/30 from 1/2 with crossover on, and a weaker trend from 1/32 and 1/10 with crossover off. It does not rescue a rare shared form with crossover on. Against duplicated, 32 cells could not be tested."

9. **Should fix — the title and first bullet read as anti-sharing; the probe says majority rule.**
   - Reciprocal probe (shared at 3/4 or 9/10, crossover 0.7, L=64): shared reached ≥ 99% in 9/9 runs against either competitor. The rare partly shared or duplicated form was the one eliminated.
   - Arm B from 1/2 is a coin flip (16/30, 13/30), which fits two stable states.
   - Add to the first bullet of "What this shows": "A 3-seed probe suggests the barrier is symmetric: with crossover on, whichever of two incompatible forms holds the majority removes the other."

10. **Note — arm A is shared vs duplicated only for the first tens of generations.** The zero-latent duplicated form turns partly shared on its own (§29, median generation 80). Lost runs with crossover off end 100% partly shared, 0% duplicated.

11. **Note — the label does not hide a surviving helper.** A hybrid with one `RECV3` consumer is labelled partly shared, but in lost runs only 0–3% of genomes still have any read helper run.

12. **Note — census vs full tallies.** Across all 1020 populations the largest gap in shared share is 0.05. Two cells differ at the 90% line: arm B, 1/2, crossover 0, L=32 is 29 wins by full tally, not 28. Arm B, 1/32, crossover 0, L=32 stays 15, with one seed swapped.

13. **Note — report script.**
    - `summarise` gives a form verdict on any `n_fully_exact > 0`; require at least 20 (finding 3).
    - The "first hits 0" column includes runs that later won (2 of 13 at arm A, 1/32, crossover 0, L=64).
    - Final outcomes are better taken from `final_population.npz` without slots 0–1.

14. **Note — checked and sound.** 1080/1080 runs, 36/36 cells, no duplicate keys, exact start counts, 294/300, every won/lost cell, arm C counts and the three shared sightings (one individual each).

`experiments/output/2026-10-03/s30/fable_review.md` exists and is empty; I left it alone.

## Next: one programme, about 8 hours of the 10

Random starts do solve the task: in my probe 2 of 5 runs with crossover 0.7 had a fully exact population by generation 600, both partly shared, against 0 of 5 with crossover off. So stage 4 is worth most of the budget. Crossover appears to help discovery while blocking rare incompatible forms, and stage 4 can show that directly.

| order | arm | cells | runs | wall (10 workers) |
|---|---|---|---|---|
| 0 | pilot: 2 seeds per cell for D, E, F; 1 seed per cell for G | – | ~100 | ~20 min |
| 1 | D: crossover dose | rate 0.1, 0.3, 0.5 × start 1/32, 1/10 × (dup L=64, partly L=64, partly L=32) | 540 | ~45 min |
| 2 | E: reciprocal | shared at 3/4, 9/10, 31/32 × (dup L=64, partly L=64, partly L=128), crossover 0.7 | 270 | ~22 min |
| 3 | G: stage 4, random starts | L 32, 64, 128 × crossover 0.7, 0.3, 0; 50 seeds; 3000 generations; `log_every: 20` | 450 | 4–6.3 h |
| 4 | F: few copies, crossover off | 1 and 8 shared copies × (dup, partly), L=64, 100 seeds | 400 | ~33 min |

- **Settings:** D, E and F run 300 generations with `log_every: 5`, 30 seeds unless listed, otherwise as §30. G has no seed tapes; `track_shared` and `dump_final_population` stay on.
- **Launch:** D, E and G need no `src/` change and can go now as one queue. F needs the change below, so run it as a second queue once tested.
- **Trim rule:** if the G pilot median is over 500 s per run, drop crossover 0.3 at L 32 and 128 (350 runs).

**Readouts and what each outcome means:**
- **D:** wins per cell next to §30's 0 and 0.7 columns.
  - Probe from 1/10: against duplicated 5/6 wins at 0.1–0.3; against partly shared 1/6.
  - If that holds, the barrier is graded against duplicated, but any crossover blocks the contest that matters.
- **E:** seeds where shared stays above 90%.
  - If the rare competitor is always removed (probe 9/9), rewrite the §30 claim as majority rule.
  - If rare partly shared invades, crossover is specifically against sharing, and §29's retention only held because partly shared cannot arise from shared by mutation.
- **G:** per cell:
  - seeds with a fully exact individual ever and at the end, and the generation of the first one;
  - the form at first appearance and at the end (non-elite tally);
  - any shared individual at any log point;
  - seeds that lose the solution.

  Outcomes:
  - All partly shared, no shared, at every crossover rate: discovery of a B helper is the obstacle on this task, and establishment is moot.
  - Shared present at the first solve and kept: a founder effect; the barrier only matters when another form gets there first.
  - Crossover off solves far less often: the trade-off (crossover finds solutions but removes rare forms) is the finding.
- **F:** wins out of 100.
  - Independence predicts about 3 and 1 wins from one copy (dup, partly) and about 22 and 7 from eight.
  - A match confirms finding 1's 1–3% per copy; many more wins would mean copies help each other.

**Code change for F (default unchanged):** a `seed_counts` option, about 12 lines.
- `config.py`: add `seed_counts: str = ""`, drop it from the hash dict when empty (as `seed_split`), and reject it without arm TAG or together with `seed_split`.
- `evolve.build_initial_population`, before the existing loop:
  ```python
  if cfg.seed_counts:
      counts = [int(c) for c in cfg.seed_counts.split(",")]
      if len(counts) != len(seeds) or sum(counts) != n_seed or min(counts) < 0:
          raise ValueError("seed_counts needs one count per seed tape, summing to the seeded count")
      pop = [seeds[k].copy() for k, c in enumerate(counts) for _ in range(c)]
  ```
  The existing loop becomes the `else` branch. Neither path draws random numbers before the shuffle, so current runs replay exactly.
- Test: `seed_counts="1,1023"` gives exactly one shared genome, and an empty value leaves the config hash and the initial population unchanged.

**Report script for the new arms:** take final outcomes from the non-elite final population, require at least 20 fully exact individuals for a form verdict, and list elite forms separately.
