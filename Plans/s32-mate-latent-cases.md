# §32: crossover mate, latent helper, 256 training cases (map-bias)

Status: planned 2026-10-04 from Fable's twentieth review of §31
(`experiments/output/2026-10-03/s31/fable_review.md`). Hobby notebook, not pre-registered.
The user asked for it to be built now and launched right after at most two Codex reviews.

## Why

§31: random starts almost never solve without crossover v2, and with it they solve the
training cases in 48–50 of 50 runs. The same crossover removes a rare hand-built shared form.
v2 does two things, though:
- it mixes lineages;
- it rearranges runs: the cut branch deletes and duplicates run segments.

Whether discovery needs the first decides whether the trade-off is real. Separately:
- Does a helper already present in the host let a rare shared form establish (helper first,
  readers later)?
- Are the training-perfect shortcut populations a 64-case training-sample effect?

## Arms (generator `experiments/chem_tape/s32_make_sweeps.py`)

| arm | file | what | runs |
|---|---|---|---|
| K | `s32_latent_rare.yaml` | shared from 1/32 and 1/10 vs partly shared plus an unread B run (34 cells), crossover 0.1 / 0.3 / 0.7, L 64, 300 generations, 30 seeds | 180 |
| K | `s32_latent_copy.yaml` | one shared copy, crossover 0 and 0.3, 100 seeds | 200 |
| K | `s32_latent_alone.yaml` | the competitor alone, crossover 0.3, 30 seeds (decay of the unread B run) | 30 |
| J | `s32_mate.yaml` | random starts, `crossover_mate` self at 0.3 and 0.7 and random at 0.3 (L 64), self at 0.3 (L 128); 3000 generations, 50 seeds | 200 |
| L | `s32_cases256.yaml` | random starts, 256 training cases, L 64, crossover 0.3, 3000 generations, 50 seeds | 50 |
| G2 | `s32_stage4_more.yaml` | §31 G's L 64 / 0.3 cell, seeds 50–99 | 50 |

- New option `crossover_mate` ("selected" default / "self" / "random"). It is hash-neutral
  at the default, and the second selection is always drawn, so earlier runs replay.
- Order: K, J, L, G2.
- Trim rule: if the L pilot is over 1100 s per run, cut L to 30 seeds.

## Readouts (`experiments/chem_tape/s32_report.py`)

- **K:** wins as in §31 D, plus the share of genomes whose tag-3 run is still B's body.
- **J, L, G2,** against §31 G's matching cells (same seeds):
  - training-solved at the end (≥ 10% training-perfect);
  - exact population at the end (≥ 20 non-elite fully exact);
  - form of the first established exact population;
  - final verdict;
  - helper content of shared verdicts (B-type / A-type).

## Reading it (Fable)

- **J:**
  - self-mate solves about as often as 0.3 → discovery needs rearrangement, not mixing, and
    the trade-off is not forced;
  - self fails, random succeeds → foreign material is enough;
  - both fail → mixing between selected lineages finds solutions, and the trade-off is real.
- **K:**
  - shared wins from 1/10 at 0.3–0.7 → the barrier is the missing helper, and "helper first"
    is a route;
  - shared still loses → recipient-side conversion is enough.
- **L:**
  - ≥ 45 exact verdicts of 50 → shortcuts are a training-sample effect;
  - otherwise they are structural.
