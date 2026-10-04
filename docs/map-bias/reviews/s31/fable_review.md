# Review of map-bias §31 (twentieth)

**Verdict:** every number in the §31 tables matches the raw outputs, and arms D, E and F stand with small wording changes. Four stage-4 readings do not hold as written: "genuine pure helpers", "no route from rare to common", "crossover is needed" and the L 32 sentence.

**What I ran** (nothing written to the repo; scratch scripts in `/tmp/s31rev`):
- All 1660 runs re-tallied from `s31_runs.json` and cross-checked against each run's final census.
- Stage-4 table, transitions and "lost" counts recomputed from `shared_stats`.
- Every fully exact non-elite genome in the 129 stage-4 verdict populations re-classified by knockout. For each helper I recorded what it computes and which outputs read it.
- Census trajectories read for the five "gained sharing" runs.

## Findings

1. **Must fix — "Decoded, these are genuine pure helpers."** Five of the 13 shared verdicts share only A; eight have a helper that is a function of the sum.

   | helper content | runs (L / crossover / seed) |
   |---|---|
   | B-type (function of the sum), 8 runs | 64/0.3: 20, 23, 27, 46; 128/0.3: 27, 36, 45; 128/0.7: 15 |
   | A recomputed in a helper, 2 runs | 128/0.7: 1 (read by outputs 0 and 2), 3 (read by 1 and 2) |
   | relay of output A (`… RECV0 IF_GT`), 3 runs | 128/0.3: 48; 128/0: 1, 45 |

   - Both crossover-off "shared" verdicts are relays of A, so no B helper ended a run without crossover.
   - Two runs (64/0.3 seed 46, 128/0.3 seed 27) have A read as a helper plus a B-type helper, which is the full hand-built form.
   - B-type verdicts by rate at L 64 and 128: 1 of 48 at 0.7, 7 of 56 at 0.3 (Fisher p = 0.07), 0 of 6 at 0.
   - Replace the two "Decoded…" bullets with: "Decoded, 8 of the 13 have a helper computing B or a function of the sum, read by both consumers (4 at L 64 / 0.3, 3 at L 128 / 0.3, 1 at L 128 / 0.7). The other 5 share only A through a non-output run: 3 relay output A, 2 recompute A in a helper. Neither crossover-off verdict is a B helper."
   - Replace "A pure helper arises from random starts in a few percent of runs" with: "A B helper ends the run in 8 of 450 runs (8 of 129 verdicts)."

2. **Must fix — "What it lacks is a route from rare to common while crossover is on."** Two stage-4 runs show such a route inside an established exact population.
   - L 128, 0.3, seed 27: exact partly shared population from generation 720. A B-type shared form is at 1–8% from 2020 to 2100, 82% at 2200 and 100% from 2400.
   - L 128, 0.7, seed 1: exact duplicated population from 520. The A-helper form is at 8% at 1000 and 97% at 1420, after dipping back to 8% at 1360.
   - §30 arm C is the same thing: partly shared arose and took over duplicated populations in 45 of 60 runs at 0.7.
   - The other three "gained sharing" runs (64/0.3 seed 46, 128/0.3 seed 48, 128/0.7 seed 15) are not contests between exact forms. The shared form was the first exact form to establish in a training-perfect shortcut population.
   - Replace with: "The hand-built shared form has no route from rare to common against the hand-built competitors once crossover is 0.3 or more (D). A variant that arises inside a population can spread with crossover on: 2 of about 120 established exact populations changed to a form with a shared helper (one B-type at 0.3, one A-type at 0.7). D measures a contest between two unrelated layouts, not the fate of a new mutant."

3. **Must fix — "Crossover is needed to find solutions at all" and "pull in opposite directions".** The counts are right; the mechanism is not shown.
   - Crossover v2 also rearranges runs (the cut branch deletes and duplicates run segments). No arm separates mixing between lineages from that rearrangement.
   - "Ever fully exact" is a single sampled individual in 59 of the 201 runs, and under 5 in 94.
   - At population level, for L 64/0.7, 64/0.3, 128/0.7, 128/0.3: training-solved at the end (≥ 10% training-perfect) in 49, 48, 50, 49 of 50; exact population at the end in 28, 30, 20, 26. Without crossover: 2 and 4 of 50, all exact.
   - Replace the heading with: "Without crossover, random starts almost never solve (mutation 0.015, 3000 generations)."
   - Replace the first "What this shows" bullet with: "Runs with crossover v2 solve the training cases in 48–50 of 50 runs at L 64 and 128; runs without it in 2–4. The same crossover removes a rare hand-built form. Not shown: whether discovery needs mixing between lineages or only v2's run-level rearrangement."

4. **Must fix — the L 32 sentence is wrong twice.**
   - The partly shared form (27 cells) also fits at 32 (§29).
   - Evolution found duplicated solutions in 31 cells: 6 of the 19 verdicts at L 32 are duplicated. They use `IF_GT` where the hand-built tails use `ADD C1 GT`.
   - Replace "The hand-built forms make sharing the only fit at 32, but evolution at 32 mostly fails to solve at all" with: "At 32 only the hand-built duplicated form is excluded, and evolution found duplicated solutions in 31 cells (6 of 19 verdicts). So 32 cells does not force sharing."

5. **Should fix — founder effect.** The "first form" rests on one individual in 59 runs.
   - Using the first census with ≥ 20 exact and > 90% one form, 121 of 129 keep their form. The changes are 4 duplicated → partly, 1 duplicated → shared, 2 partly → shared, 1 mixed → partly.
   - For shared outcomes: 10 of 13 were shared at the first established population.
   - Two of 12 shared-first populations later lost the solution (for example L 64, 0.3, seed 36).
   - Replace with: "The form of the first established exact population (≥ 20 of 256) is kept in 121 of 129 runs. Of the 13 shared endings, 10 were shared from the start."

6. **Should fix — Shortcuts bullet.** Of the 72 runs that had an exact individual but end below 20, only 8 ever had 20 in a sample. Add: "The other 64 are training-perfect shortcut populations that throw off occasional exact individuals. 92 of 196 training-solved runs at L 64 and 128 with crossover end that way."

7. **Should fix — "Copies act independently."** Observed 4, 0, 23, 10 against predicted 3, 1, 22, 7. Zero of 100 has a 95% upper bound near 3.6%. Replace with: "Single-copy results are consistent with independent copies (about 3% per copy against duplicated, about 1% against partly shared)."

8. **Should fix — "Majority rule holds."** E tested shared at ≥ 3/4 with crossover 0.7 only, and the rule is not symmetric at 1/4. Shared from 1/4 beat duplicated in 6 and 12 of 30 runs (§30); duplicated or partly shared from 1/4 won 0 of 90. Add: "The tipping point is below 1/2 for shared against duplicated and near 1/2 against partly shared."

9. **Should fix — "0.1 already cuts wins by about half."** From 1/10 it is 19 → 11 and 24 → 9; from 1/32 it is 8 → 2 and 15 → 1. Replace with: "crossover 0.1 cuts wins by half or more from 1/10 and by three quarters or more from 1/32."

10. **Note — evolved shared forms are not smaller.** Cells in runs that any output depends on, median per population: shared 32–42, partly 28–34 at the run-median level (32 at L 64), duplicated 31–41. A tie-break toward fewer cells would favour compact partly shared genomes, so drop that candidate from **Next**.

11. **Note — "partly" is looser in stage 4.** In partly-verdict populations, 31% of exact individuals have A read by only one consumer (4.9% in §29).

12. **Note — D's in-between runs are the frozen elite again.** All 15 are seeds 4, 9, 16 or 27 with a shared slot-0 elite; 13 have 1–8 shared individuals. Two are real mixes (partly, L 32, 0.1, 1/10, seeds 16 and 27: 102 and 83 shared).

13. **Note — report script.**
    - Take the first form from the first census with ≥ 20 exact.
    - Record helper content (function of max only → A-type).
    - The run census's `helpers` counts structurally read runs: about 0.85 per genome in every crossover-on population, while knockout finds a single-reader helper in under 2% of exact genomes.

14. **Note — checked and sound.**
    - 1660/1660 runs, no duplicates, none short; wall time 7.4 h.
    - Every D, E, F and G cell and the §30 endpoints; 270/270; lost 1/1/3/3; 82/30/8; 9 of 129; 51 + 14 + 7.
    - Census against full tally: largest gap 0.06; one run differs at the 90% line (partly, L 32, 0.1, 1/10 is 9 by tally, 8 by census).
    - `seed_counts` is correct and draws no random numbers before the shuffle.
    - The commit message of `3587de6` repeats finding 1's claim and cannot be changed; the notebook should carry the correction.

## Next: one programme, about 6.5 hours of the 10

The open question that decides the rest is finding 3: if rearrangement without mixing finds solutions, the trade-off disappears. Launch at 23:00 unless you want it by day.

| order | arm | cells | runs | wall (10 workers) |
|---|---|---|---|---|
| 0 | pilot: 1 seed per cell for J and L, 2 for K | – | ~25 | ~25 min |
| 1 | J: who is the mate? Random starts, 3000 generations, 50 seeds | L 64: self at 0.3, self at 0.7, random at 0.3; L 128: self at 0.3 | 200 | ~2.7 h |
| 2 | K: latent helper, seeded, 300 generations, L 64 | shared from 1/32 and 1/10 against "partly + unread B run", crossover 0.1 / 0.3 / 0.7, 30 seeds; one shared copy at 0 and 0.3, 100 seeds; competitor alone, 30 seeds | 410 | ~35 min |
| 3 | L: 256 training cases, random starts, L 64, crossover 0.3, 50 seeds | 1 | 50 | 1–2 h (unmeasured) |
| 4 | optional: G at L 64 / 0.3, seeds 50–99 | 1 | 50 | ~40 min |

**Readouts and what each outcome means:**
- **J**, against G's 0.3 and 0 cells on the same seeds: training-solved at the end, exact verdicts, form at the first established population, helper content.
  - Self-mate solves about as often as 0.3 (48 of 50): discovery needs rearrangement, not mixing. The trade-off is not forced, and establishment can then be studied without the majority barrier.
  - Self fails and random mate succeeds: foreign material is enough; selection of the mate is not.
  - Both fail: mixing between selected lineages is what finds solutions, and the trade-off is real.
- **K**: wins as in D, plus the share of genomes whose tag-3 run still computes B.
  - Shared wins from 1/10 at 0.3–0.7: the barrier is the missing helper in the host, and "helper first, readers later" is a route.
  - Shared still loses: conversion on the recipient side is enough, and the barrier belongs to mixing two forms.
  - The competitor-alone cell shows how fast an unread helper decays; without it a loss cannot be read.
- **L**: exact verdicts of 50, against 30 with 64 cases.
  - 45 or more: shortcuts are a training-sample effect, and later stage-4 work should use 256 cases.
  - Otherwise shortcuts are structural on this task.
- **Trim rule:** if the L pilot is over 1100 s per run, cut L to 30 seeds.

**Code change for J (default unchanged), about 10 lines:**
- `config.py`: add `crossover_mate: str = "selected"`; drop it from the hash dict at the default; accept `"selected"`, `"self"`, `"random"`; reject non-default values outside arm TAG.
- `evolve.py`, in both reproduction loops where `crossover(population[i], population[j], cfg, rng)` is called: use `population[i]` as the mate for `"self"` and `random_genotype(cfg, rng)` for `"random"`. Keep the second selection draw so the default stream is untouched.
- Test: the default gives an identical hash and final population on one §31 config; `"self"` children contain only the parent's runs.

**K needs no `src/` change.** Build the competitor in the sweep generator with `tagged.build` (tag order 0, 3, 1, 2; 34 cells), not in `sh.FORMS`, so stages 1–3 and their tests are untouched.
