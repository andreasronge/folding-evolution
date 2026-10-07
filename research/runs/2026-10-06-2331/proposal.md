---
node: questions/10-compositional-map-transfer/17-decoder-initialization-variation
title: Learned starting programs versus learned ongoing decoder — 2×2 on the frozen 1723 maps
---
**Why this now.** This follows [strategy 2331](strategy.md) and its
[concept plan](../../plans/decoder-initialization-variation.md) as written. Root 10's
reliable result is that the 20 frozen token maps from 1723 (M) make fresh search 2–3× faster
than G4 (G) on the three 2229 cells. A map changes two things: which programs the search
starts from, and what mutation and crossover produce afterwards. Until now these have always
changed together. This experiment separates them on the saved maps, with no new learning. It
uses slot 9 of root 10 (budget 10, 8 used). I opened sub-question
[17](../../questions/10-compositional-map-transfer/17-decoder-initialization-variation/question.md)
with 2 slots. Slot 2 (the ten training cells) runs only if this one gives a bounded answer.

**Design.** The 2229 harness (`composition_search.search` on `research/main`) is unchanged
apart from initialization. G4, D1331, `v2_rmin_first`, 32-token tapes, pop 256, lexicase,
crossover 0.7, mutation 0.03, cap 524 288, and exact 1 331-input verification all stay as
they are. Four arms per map, cell and seed:

| Arm | Initial tapes | Decoder during search | Alleles at generation 0 |
|---|---|---|---|
| GG | G-decoded uniform alleles | G | original (2229 code path); one per seed and cell, shared by all maps |
| MM | M-decoded uniform alleles | M | original (2229 code path) |
| MG | the **same tapes as MM** | G | re-encoded under G |
| GM | the **same tapes as GG** | M | re-encoded under M |

Re-encoding is conditional-uniform. Each token is drawn uniformly in its allele interval in
the destination table's row for the previous token (start row for position 0). It is drawn
independently for every position and individual, from its own stream `default_rng([seed, 3])`,
separate from the case, initial, variation and selection streams. All 21 tables have allele
range 24 000, 24 tokens and minimum interval width 250 (checked), so every interval is
non-empty. Encoding happens once at generation 0. Later generations run the original code.
Inactive tokens are re-encoded too.

- **Cells:** the three 2229 cells (BE `S?m:(M+F)`, PA `(F?S:M)+m`, PA `(S?M:m)+F`). These are
  reused targets for a mechanism study, not untouched holdouts.
- **Maps:** all 20 (BE1–10, PA1–10), with equal weight and family labels kept. No map is
  selected, merged or dropped.
- **Seeds:** 400 fresh seeds per cell, 2331000–2331399, shared by every arm. Probe seeds
  9000000–9000024 and all 2229 seeds stay out of the analysis.
- **Count:** 3 × 400 × (1 + 20 × 3) = 73 200 searches.

**Validation (run in the same queue before the main grid; failure stops the run):**
1. Round trip: for G→M and M→G with all 20 maps, decode(encode(tapes)) equals the tapes
   exactly, on 10 000 random tapes per pair.
2. Law: re-encoding a table into itself gives uniform alleles. Use a chi-square test on 1e6
   alleles in 240 bins, for G and two maps chosen by fixed index (BE1, PA1).
3. Reproduction: the new code path with source = destination and original alleles must give
   rows bit-identical to 2229's `search.jsonl` (evaluations, solved, curve). This covers all
   21 arms × 3 cells on seeds 2229002–2229011, 630 searches.
4. Pairing: every row logs the hash of its generation-0 token tapes. The MG hash must equal MM's
   and the GM hash must equal GG's for every (map, cell, seed).
5. Search-level law check: an extra arm MMr (M re-encoded into M) for all maps and cells on the
   first 100 main seeds (6 000 searches). Compare it with MM using the same map-level analysis.
   The check fails if the 99% interval for MMr/MM excludes 1.

Order jobs seed-major, with all arms for a seed before the next seed. A deadline then leaves
a balanced set of complete seeds. Analysis uses the complete seeds and needs at least 200.

**Feasibility (measured).** A probe ran on 2026-10-06 in a scratch copy of the `research/main`
search function. It changed only initialization, and the identity path matched the original
search exactly. It covered maps BE1, PA4 and PA9 (PA9 is the weak map), the three cells and
25 seeds, 900 searches in total. Mean seconds per search (single-threaded per worker, 10
workers):

| Map | GG | MM | MG | GM | wall for 300 searches |
|---|---:|---:|---:|---:|---:|
| BE1 | 1.96 | 0.28 | 0.64 | 0.37 | 28 s |
| PA4 | 1.98 | 0.32 | 1.21 | 0.50 | 33 s |
| PA9 | 2.03 | 1.55 | 1.43 | 1.28 | 52 s |

All arms solved 93–100%. The round-trip assertion held on every probe search. Projection:
GG 1 200 × 2.0 s plus map arms 72 000 × 0.84 s, plus validation (about 6 600 searches), comes
to about 68 000 CPU-s. At the observed ×8.7 parallel speed-up that is **about 2.2 h**, or
3.3 h at 1.5× slack. Timeout 5 h, internal deadline 4.5 h. Inverse encoding is a vectorised
32-step loop over 256 tapes per search, which is negligible.

The probe's arm means were read for runtime only. They hint that GM is close to MM and that
MG lies between MM and GG. They came from 25 seeds on three maps and selected nothing. They
do inform the predictions below, which is why I state them.

**Analysis.** Cost T = evaluations to the first exact solve, or the cap if unsolved. For each
map and cell, average log2 cost ratios over the seeds. Average the three cells with equal
weight. The map (trajectory) is the unit: n = 20, with 95% t intervals. Ratios are 2^(mean).

Primary contrasts, all within a map and free of the shared GG:
- **P1, ongoing increment given learned start:** log2(T_MG / T_MM). The arms start from
  identical tapes.
- **P2, start increment given learned ongoing decoder:** log2(T_GM / T_MM). Both arms search
  under M.

Diagonal check: D = log2(T_GG / T_MM). Secondary contrasts, always reported:
- I_G = log2(T_GG / T_MG), the start effect under G.
- O_G = log2(T_GG / T_GM), the ongoing effect from the G start.
- The interaction, P1 − O_G.

Every map's GG-based contrast contains the same GG seed noise. For these, the interval adds
the variance of the GG seed mean to s²/20 rather than treating it as replicated across maps.
Also report each cell separately, BE maps and PA maps separately, the solve fractions, and
I_G/D and O_G/D as shares (descriptive).

Practical margin δ = 0.25 log2 (1.19×), about a fifth of the expected diagonal gain (~1.2
log2). Labels for P1 and P2:
- **N:** upper bound < δ.
- **P:** lower bound > 0 and upper bound ≥ δ.
- **X:** anything else.
A resolved negative contrast (upper bound < 0) counts as N and is flagged.

Precision: seed noise per map is about 2.3 log2/√1 200 ≈ 0.07 log2. Spread between maps on
the 2229 gains was 0.16 (BE maps) to 0.38 (PA maps, mostly PA9) log2. That projects
half-widths of 0.06–0.15 log2, so N is reachable when a point estimate is below about
0.10–0.19.

**Outcome rules (first match):**

| Row | Condition | Meaning |
|---|---|---|
| U | any validation check fails; < 200 complete seeds; G/G solves < 85% on a cell; or D's lower bound ≤ log2 1.25 | Intervention or reproduction problem. Resolve it before assigning a mechanism. No slot 2. |
| 1 | P2 = N, P1 = P | **The ongoing decoder carries the gain.** Starting from M's programs adds < 1.19× once M is used during search. Keeping M during search adds a resolved increment over M's start. |
| 2 | P1 = N, P2 = P | **The learned start carries the gain.** Keeping M during search adds < 1.19× over M's starting programs. The benefit is an initial-supply effect at this budget. |
| 3 | P1 = P, P2 = P | **Both contribute.** The interaction and shares say how the two combine. |
| 4 | P1 = N, P2 = N | **Redundant.** Either component alone gives nearly all of the diagonal gain, so the interaction is negative. |
| 5 | otherwise (any X) | **Unresolved** for that component. Report the measured spread. Return to strategy before using slot 2. |

The interaction and both secondary effects are reported in every row. Per-cell or per-family
differences are descriptive and cannot change the row.

**Prediction.** Row 1 at 45%, row 3 at 30%, row 5 at 12%, row 4 at 8%, row 2 at 5%. Searches
are short: median 4k–16k evaluations, 16–62 generations, and almost no solver appears at
generation 0. Even so, generation-0 supply may well matter. That is why row 3 is not
unlikely.

**What it cannot show.** An ongoing effect bundles mutation, crossover, inherited alleles and
continued program supply under selection. It is not evidence of a better neighbourhood beyond
sampling, and not a full supply-versus-topology decomposition. A start effect includes useful
partial programs, not only exact solvers. Nothing here bears on learned context or family
specificity. All of it is three screened cells with hand-supplied G4 context.

**Next by outcome.** Rows 1–4: slot 2 runs the same frozen 2×2 on the ten training cells, to
check whether the pattern holds across the screened bank and not only on three cells.
Projected cost is about 10/3 × 2.2 h ≈ 7 h at 400 seeds, or about 3.7 h at 200 seeds; I
would size it from this run's spread. If row 1 or 3 holds, a later question could split
mutation from crossover under M. Rows U and 5: back to strategy with costs and spreads.

**Alternatives considered.**
- *Switching tables on unchanged alleles:* this rewrites the starting population, so it
  confounds the test (plan).
- *Re-encoding active tokens only:* inactive tokens matter after crossover.
- *Running mutation and crossover as separate arms now:* the strategy says to keep them
  together in this first question.
- *A G-only or M-only pilot first:* the measured runtime makes a separate pilot cycle
  unnecessary, and the validation stage is gated in the same queue.
- *Contextual learning on the four-reducer bank:* the strategist's next alternative, not
  this cycle.
