Checks are done (numbers recomputed from the 210 `result.json` files, final populations re-classified, plus a small in-memory probe); here is the review.

# Review of map-bias §29 (eighteenth)

**Verdict:** the stage 1–3 numbers are mostly right, but the headline reading ("retention is not the problem, discovery is") is too broad, and the suggested mechanism (crossover asymmetry) points the wrong way. In a small probe, the shared form wins from 50% but is wiped out within 10 generations from 10% when crossover is on.

**What I ran:**
- **Recompute:** all stage 3 table values from the raw outputs, and the stage 2 table against `preserve.md`. Both match except where listed below.
- **One-generation model:** the real operators applied to a clonal shared/duplicated mix, 20,000 children per cell, children classified by knockout.
- **Probe:** 18 runs of 100 generations at L=64/128, 3 seeds per cell, about 30 s wall, nothing written to the repo. Treat it as a pointer, not a result.

| start share of shared | crossover | L | outcome (3 seeds each) |
|---|---|---|---|
| 50% | 0.7 | 64 | shared ≥ 93% by gen 20; partly 19–34% at gen 10 |
| 50% | 0 | 64 | shared ≥ 93% by gen 20 |
| 10% | 0 | 64 | shared ≥ 99% by gen 60 |
| 10% | 0.7 | 64 | shared at 0 by gen 15 and never back; population turns partly |
| 10% | 0.7 | 128 | shared at 0 by gen 10 and never back; population turns partly |
| 1/32 | 0.7 | 64 | shared at 0 by gen 5 and never back |

## Findings

1. **Must fix — the "which reading applies" conclusion is overstated.**
   - Sentences: "So sharing needs no size pressure here. Of the plan's three readings, the third applies: retention is not the problem, discovery is." The briefing's "Which reading applies" paragraph says the same.
   - Stage 3 only tested retention from 100% and from 50%. The probe shows the shared form is lost from 10% and from 1/32 with crossover v2 at 0.7 (9/9 runs), and wins from 10% with crossover off (3/3).
   - A newly discovered shared genome starts rare, so this is the case that matters for stage 4.
   - Change to: "Retention from a majority or an equal share is not the obstacle. Establishment from a small share was not tested here; a 3-seed probe suggests crossover removes a rare shared form."

2. **Must fix — the crossover-asymmetry explanation is contradicted.**
   - Sentences: "Not shown: why the shared form wins. Stage 2 points to a crossover asymmetry (… 0.80 vs 0.38) and to a smaller mutation target per consumer" and the stage 2 bullet "Shared as parent A: 0.80 of children fully exact."
   - The 0.80 counts exact children, not shared children. With shared as parent A and duplicated as parent B, the exact children split roughly a third each shared / partly / duplicated (818 / 1161 / 867 with crossover only, L=64).
   - In the one-generation model at 50/50, crossover lowers the shared share to 0.44 (L=64) and 0.46 (L=128). Mutation alone raises it: per-capita 0.271 vs 0.230.
   - With crossover off the shared form still takes over as fast (probe, 3/3). The supported candidate is mutation load: 24 critical cells vs 33.
   - Change to: "Crossover between the forms mostly converts shared genomes into partly shared and duplicated ones; the candidate cause of the takeover is the smaller mutation target, which a mutation-only probe supports (3 seeds)."

3. **Must fix — two seed-dup runs lost the fully exact solution, and §29 does not say so.**
   - Seed 9 at L=64 has 0 fully exact in the census from generation 960; at L=128 from generation 280 with brief returns (17 of 51 log points). The final populations hold 4 and 1 fully exact individuals of 1022.
   - The population moved to a training-perfect tag-1 body `INPUT SUM C5 C5 ADD C5 ADD GT` (sum > 15). It is wrong on 1,940 of 10,000 lists but right on that seed's 64 training cases, and shorter than the exact body.
   - `s29_report.py` readout 3 has no "no fully exact at end" column, and `np.nanmean` drops these runs silently.
   - Add to the seed-dup bullets: "In 2/60 runs (seed 9, both lengths) the population lost the fully exact solution to a shorter training-perfect tag-1 body (sum > 15)." Add a "no fully exact at end: 1/30" entry to both seed-dup table rows.
   - It is the same force as the shared takeover: selection among training-perfect genomes is neutral, so the genome with fewer critical cells wins, exact or not.

4. **Must fix — "wins … at 64 and 128 cells as well as 32".**
   - Sentence: "against an equal mix of duplicated solutions it wins outright and fast, at 64 and 128 cells as well as 32." Seed-mixed was not run at 32 because the duplicated form does not fit.
   - Change to: "it wins outright and fast at 64 and 128 cells; at 32 only persistence was tested."
   - Same fix in the briefing: "the shared form holds and wins at all lengths".

5. **Should fix — "Sharing of A arises in 60/60 runs" is helped by how the forms were built.**
   - `_cells` gives every non-RECV body cell tag 0, and mutation changes op and tag independently. So any op → RECV mutation in the seeded genomes reads tag 0, which is A.
   - One point mutation (the `GT` of the A copy → RECV) turns a duplicated consumer into an exact partly shared one. With random latent tags, as in evolved or random genomes, that route is about 64 times rarer.
   - I did not test this. Add: "The hand-built forms carry tag 0 on all non-RECV cells, which makes RECV0 the default result of an op mutation; the 60/60 and the median of generation 80 may not hold with random latent tags."

6. **Should fix — generation-0 census range.**
   - "46–52% shared (seed-mixed)" is the pilot's range. Across the 60 runs it is 45–55% (0.449–0.547).

7. **Should fix — "95% … at generation 20, ≥ 95% from then on".**
   - The seed means at generation 20 are 0.96 (L=64) and 0.94 (L=128); the per-seed minimum is 0.81 and 0.82. About 4–5% are partly shared at that point.
   - Change to: "mean 96% (64) and 94% (128) at generation 20, lowest seed 81%; the mean stays ≥ 94% from then on." Same in the briefing.
   - The probe shows a partly shared bump of 19–34% around generation 10 that a 20-generation census cannot see.

8. **Should fix — run time.**
   - "140–160 s per run" should be "88–196 s per run, median 139 s".

9. **Should fix — elites.**
   - "Elites (slots 0–1) keep the seeded genome frozen" is not quite right. Elites are the first two of an unstable `argsort` over tied training fitness.
   - The report shows slot 1 holding a partly shared genome in seed-dup and a shared one in seed-mixed. Say "slot 0 kept a seeded genome in the inspected runs".

10. **Note — "partly" with one reader.**
    - In all 60 seed-dup final populations, 998 of 20,454 partly shared individuals (4.9%) have a tag-0 consumer count of 2. The existing bullet could carry the number.

11. **Note — the 4 "shared" sightings in seed-dup.**
    - Each is one individual at one log point (generations 760, 260, 660, 800), never at the end; no final population has one.
    - The label only needs some non-output run with count ≥ 2, so these may be relays of A rather than a B helper. "At most 1% of a sample" should read "one individual among the 84–105 fully exact ones".

12. **Note — seed-shared is not exactly 100% throughout.**
    - The lowest logged value is 0.987 (L=64) and 0.988 (L=128); the final value is 1.00 in all 90 runs. "Never replaced" stands.

13. **Note — the fully exact share and the mutation-load argument.**
    - About a third is fully exact at every length, although stage 2 mutant survival runs from 0.42 (32) to 0.12 (128). The populations have evidently become more robust than the hand-built forms (decoded genomes end in a junk run that absorbs the padding).
    - The bullet "That fits a mutation-and-crossover load" should add that the equal share across lengths is not what the stage 2 numbers predict.

14. **Note — measures and code I checked and found sound.**
    - **Knockout:** it blanks the body and keeps the run, so a shadowed copy cannot stand in. That is the right choice here.
    - **Wide lexicase:** the word-by-word comparison is correct. The all-pass row always wins, so parents are drawn only from training-perfect individuals; I did not read the code that picks within the winning group.
    - **Census:** own generator, caching by semantic key is safe for the form label, and the 500-list prefilter is conservative.
    - **Stage 2 table:** all 77 cells match `preserve.md` to rounding.
    - **Completeness:** 210/210 runs, no duplicate keys, 1000 generations each.

`experiments/output/2026-10-02/s29_night/fable_review.md` exists but is empty; I left it alone, as instructed.

## What to do next

**Primary: establishment from a small share (one night, about 1.5 hours of the window).** No `src/` change is needed: `seed_split` takes a list, so 1 shared + 9 duplicated hex entries give exactly 10%.

| arm | competitor | start share of shared | crossover rate | L | generations |
|---|---|---|---|---|---|
| A | duplicated | 1/32, 1/10, 1/4, 1/2 | 0.7 and 0 | 64, 128 | 300 |
| B | partly shared | 1/32, 1/10, 1/2 | 0.7 and 0 | 32, 64, 128 | 300 |
| C | seed-dup with random latent tags (finding 5) | – | 0.7 | 64, 128 | 1000 |

- **Settings:** 30 seeds, `log_every: 5`, otherwise as §29.
- **Budget:** A is 480 runs, B is 540, C is 60. At about 40 s per 300-generation run (probe: 12 s per 100 generations) and 140 s for C, that is roughly 80 minutes on 10 workers. Pilot 2 seeds per arm first.
- **Readouts:**
  - Per cell, seeds ending > 90% shared and seeds where shared is gone.
  - The lowest start share from which shared wins, with and without crossover.
  - The generation at which shared reaches 0.
  - For C, the seeds that turn partly shared and when.
- **Why B matters:** duplicated populations turn partly shared anyway, so shared vs partly (24 vs 27 cells) is the contest a new B helper would actually face.
- **Reading it:** if shared cannot establish from ≤ 10% with crossover on but can with it off, crossover is the establishment barrier. Stage 4 then needs a crossover-off arm, and the chemistry change to consider is making consumer bodies travel with their helper.

**Alternative 1: stage 4 as planned, with one added arm.** Random starts at 32/64/128, 50 seeds, 3000 generations, crossover 0.7 and 0. That is 300 runs, a few hours if random-start runs cost about the same per generation as these; pilot first. It can follow the primary in the same queue, but its result is hard to read until the primary says whether a rare shared form can survive.

**Alternative 2: mutation-rate dose-response.** Seed-mixed at 50/50, crossover off, mutation 0.005 / 0.015 / 0.03, L=64, 30 seeds, 300 generations (90 runs, about 6 minutes). If the takeover speed scales with the rate, the mutation-load explanation in finding 2 is confirmed directly.
