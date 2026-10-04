## Validation

- runs: 895 (200 §31 reference); duplicate run keys: 0; stopped early: 0
- entry mapbias_s32_latent_rare: status done, exit 0, commit 805a641, dirty True, wall 808.559 s
- entry mapbias_s32_latent_copy: status done, exit 0, commit 805a641, dirty True, wall 851.842 s
- entry mapbias_s32_latent_alone: status done, exit 0, commit 805a641, dirty True, wall 137.445 s
- entry mapbias_s32_mate: status done, exit 0, commit 805a641, dirty True, wall 11250.542 s
- entry mapbias_s32_cases256: status timeout, exit 143, commit 805a641, dirty True, wall 9000.116 s
- entry mapbias_s32_stage4_more: status done, exit 0, commit 805a641, dirty True, wall 4465.123 s

## Readouts

### Arm K: shared vs partly shared plus an unread B run (L 64, 300 generations)

| start | crossover | seeds | won (> 90% shared) | shared gone | in between | lost the solution | slot-0 elite shared: won / all | genomes with the B run intact (mean, non-elite) |
|---|---|---|---|---|---|---|---|---|
| 1/32 | 0.1 | 30 | 4 | 26 | 0 | 0 | 0 / 0 | 0.03 |
| 1/32 | 0.3 | 30 | 0 | 30 | 0 | 0 | 0 / 0 | 0.00 |
| 1/32 | 0.7 | 30 | 0 | 30 | 0 | 0 | 0 / 0 | 0.01 |
| 1/10 | 0.1 | 30 | 15 | 14 | 1 | 0 | 2 / 4 | 0.09 |
| 1/10 | 0.3 | 30 | 2 | 26 | 2 | 0 | 0 / 4 | 0.02 |
| 1/10 | 0.7 | 30 | 0 | 27 | 3 | 0 | 0 / 4 | 0.00 |
| 1 copy | 0.0 | 100 | 2 | 98 | 0 | 0 | 0 / 0 | 0.01 |
| 1 copy | 0.3 | 100 | 0 | 99 | 1 | 0 | 0 / 0 | 0.01 |
| alone | 0.3 | 30 | 0 | 30 | 0 | 0 | 0 / 0 | 0.00 |

"alone": the competitor only; there is no shared form, so the won/gone columns do not apply (they read 0 / all). Its last column is the decay of an unread B run.

### Random starts: §32 arms J, L, G2 and §31 arm G reference (3000 generations)

| arm | L | crossover | mate | cases | seeds | training-solved at end | exact population at end (≥ 20) | first established form: shared / partly / dup | final verdict: shared / partly / dup / mixed | shared verdicts: B-type / A-type / other | median s per run |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G (§31) | 128 | 0.3 | selected | 64 | 50 (0–49) | 49 | 26 | 3 / 19 / 7 | 4 / 16 / 6 / 0 | 3 / 1 / 0 | 574 |
| G (§31) | 64 | 0.0 | selected | 64 | 50 (0–49) | 2 | 2 | 0 / 2 / 0 | 0 / 2 / 0 / 0 | 0 / 0 / 0 | 400 |
| G (§31) | 64 | 0.3 | selected | 64 | 50 (0–49) | 48 | 30 | 4 / 22 / 5 | 4 / 21 / 5 / 0 | 4 / 0 / 0 | 437 |
| G (§31) | 64 | 0.7 | selected | 64 | 50 (0–49) | 49 | 28 | 0 / 21 / 8 | 0 / 21 / 7 / 0 | 0 / 0 / 0 | 491 |
| G2 | 64 | 0.3 | selected | 64 | 50 (50–99) | 49 | 27 | 0 / 23 / 7 | 0 / 22 / 5 / 0 | 0 / 0 / 0 | 768 |
| J | 128 | 0.3 | self | 64 | 50 (0–49) | 39 | 21 | 3 / 19 / 2 | 2 / 18 / 1 / 0 | 1 / 1 / 0 | 615 |
| J | 64 | 0.3 | random | 64 | 50 (0–49) | 2 | 2 | 1 / 1 / 0 | 1 / 1 / 0 / 0 | 1 / 0 / 0 | 465 |
| J | 64 | 0.3 | self | 64 | 50 (0–49) | 34 | 17 | 2 / 15 / 1 | 2 / 15 / 0 / 0 | 2 / 0 / 0 | 491 |
| J | 64 | 0.7 | self | 64 | 50 (0–49) | 40 | 22 | 0 / 20 / 4 | 0 / 19 / 3 / 0 | 0 / 0 / 0 | 566 |
| L | 64 | 0.3 | selected | 256 | 35 (0–34) | 35 | 26 | 4 / 21 / 3 | 3 / 21 / 2 / 0 | 1 / 1 / 1 | 3029 |

