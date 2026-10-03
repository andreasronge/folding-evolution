# §30: can a rare shared form establish? (map-bias)

Status: planned 2026-10-03 from Fable's eighteenth review of §29
(`experiments/output/2026-10-02/s29_night/fable_review.md`). Hobby notebook, not
pre-registered. The user asked for it to run as soon as Codex has reviewed it (at most two
reviews), not at night.

## Why

§29 showed that the shared form (A and a B helper read by RECV, 24 cells) persists from 100%
and takes over from 50% against the duplicated form (33 cells). A newly discovered shared
genome starts rare, though. Fable's 3-seed probe found a shared form at 10% or 1/32 wiped
out within 15 generations with crossover v2 at 0.7, and winning from 10% with crossover off.
Fable's model points to the smaller mutation target (24 vs 33 critical cells) as the cause of
the 50/50 takeover, with crossover working against sharing. Before stage 4 (random starts),
we need to know whether a rare shared form can establish at all, and whether crossover is
what stops it.

Separately, §29's seeds carried tag 0 on every non-RECV cell, so an op → RECV mutation read A.
That may have made seed-dup's 60/60 conversion to partly shared easy.

## Arms (30 seeds each, settings as §29 unless listed)

| arm | file | contest | start share of shared | crossover | L | generations | log_every | runs |
|---|---|---|---|---|---|---|---|---|
| A | `s30_est_dup.yaml` | shared vs duplicated | 1/32, 1/10, 1/4, 1/2 | 0.7, 0 | 64, 128 | 300 | 5 | 480 |
| B | `s30_est_partly.yaml` | shared vs partly shared | 1/32, 1/10, 1/2 | 0.7, 0 | 32, 64, 128 | 300 | 5 | 540 |
| C | `s30_dup_latent.yaml` | seed-dup, random latent tags | – | 0.7 | 64, 128 | 1000 | 10 | 60 |

- A start share of 1/k means k seed tapes in equal shares (`seed_split`), one shared: 32,
  103, 256 or 512 shared genomes out of 1024.
- Arm B matters because duplicated populations turn partly shared anyway. Shared vs partly
  (24 vs 27 cells) is the contest a new B helper would actually face.
- Arm C uses `shared_helper.form_genome(..., latent="random")`. Ops are the same as §29;
  non-RECV body cells carry fixed random tags.

## Readouts (`experiments/chem_tape/s30_report.py`)

Per cell (contest, start share, crossover, L), with actual denominators:
- seeds ending > 90% shared among fully exact individuals;
- seeds where shared is gone at the end, and the median generation it first reaches 0;
- seeds with no fully exact individual at the end, reported, never counted as a form;
- per (contest, crossover, L), the lowest start share from which shared wins (> 90% at the
  end) in a majority of seeds.

For arm C: seeds where partly shared exceeds 50% and the median generation; any shared
individual; lost solutions.

## Reading it

- **Shared cannot establish from ≤ 1/10 with crossover on, but can with it off:** crossover is
  the establishment barrier. Stage 4 needs a crossover-off arm. The chemistry change to
  consider is making consumers travel with their helper.
- **Shared establishes from small shares either way:** neither retention nor establishment is
  the obstacle, and stage 4 tests discovery as planned.
- **Shared loses to partly shared (arm B) even from 1/2:** the cheap output-as-helper form is
  the real competitor, and a pure helper needs more than a smaller mutation target.
- **Arm C rarely or slowly turns partly shared:** §29's 60/60 was helped by the latent tag-0
  cells, and §29's seed-dup bullet stays caveated.

## Process

Pilot 2 seeds per arm, `codex review` at most twice, commit and push, launch
`queue_s30.yaml` with 10 workers. Write-up as notebook §30 with the commit hash, marked
"Fable review pending".
