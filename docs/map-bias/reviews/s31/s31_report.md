## Validation

- runs: 1660; duplicate run keys: 0; stopped early: 0
- seeds per cell: D ('duplicated', 64, 0.1, '1/10'): 30, D ('duplicated', 64, 0.1, '1/32'): 30, D ('duplicated', 64, 0.3, '1/10'): 30, D ('duplicated', 64, 0.3, '1/32'): 30, D ('duplicated', 64, 0.5, '1/10'): 30, D ('duplicated', 64, 0.5, '1/32'): 30, D ('partly', 32, 0.1, '1/10'): 30, D ('partly', 32, 0.1, '1/32'): 30, D ('partly', 32, 0.3, '1/10'): 30, D ('partly', 32, 0.3, '1/32'): 30, D ('partly', 32, 0.5, '1/10'): 30, D ('partly', 32, 0.5, '1/32'): 30, D ('partly', 64, 0.1, '1/10'): 30, D ('partly', 64, 0.1, '1/32'): 30, D ('partly', 64, 0.3, '1/10'): 30, D ('partly', 64, 0.3, '1/32'): 30, D ('partly', 64, 0.5, '1/10'): 30, D ('partly', 64, 0.5, '1/32'): 30, E ('duplicated', 64, 0.7, 768): 30, E ('duplicated', 64, 0.7, 922): 30, E ('duplicated', 64, 0.7, 992): 30, E ('partly', 128, 0.7, 768): 30, E ('partly', 128, 0.7, 922): 30, E ('partly', 128, 0.7, 992): 30, E ('partly', 64, 0.7, 768): 30, E ('partly', 64, 0.7, 922): 30, E ('partly', 64, 0.7, 992): 30, F ('duplicated', 64, 0.0, 1): 100, F ('duplicated', 64, 0.0, 8): 100, F ('partly', 64, 0.0, 1): 100, F ('partly', 64, 0.0, 8): 100, G (128, 0.0): 50, G (128, 0.3): 50, G (128, 0.7): 50, G (32, 0.0): 50, G (32, 0.3): 50, G (32, 0.7): 50, G (64, 0.0): 50, G (64, 0.3): 50, G (64, 0.7): 50
- entry mapbias_s31_dose: status done, exit 0, commit 8844b6c, dirty True, wall 2096.994 s
- entry mapbias_s31_reciprocal: status done, exit 0, commit 8844b6c, dirty True, wall 1566.853 s
- entry mapbias_s31_few_copies: status done, exit 0, commit 8844b6c, dirty True, wall 1500.635 s
- entry mapbias_s31_stage4: status done, exit 0, commit 8844b6c, dirty True, wall 21438.203 s

## Readouts

Verdicts need ≥ 20 fully exact non-elite individuals in the final population.

### Arm D: crossover dose (shared from 1/32 and 1/10)

| contest | L | crossover | shared at start | seeds | won (> 90% shared) | shared gone | in between | lost the solution (< 20 exact) | slot-0 elite shared: won / all | mean shared share (verdict runs) |
|---|---|---|---|---|---|---|---|---|---|---|
| duplicated | 64 | 0.1 | 1/32 | 30 | 16 | 14 | 0 | 0 | 0 / 0 | 0.53 |
| duplicated | 64 | 0.3 | 1/32 | 30 | 10 | 20 | 0 | 0 | 0 / 0 | 0.33 |
| duplicated | 64 | 0.5 | 1/32 | 30 | 1 | 29 | 0 | 0 | 0 / 0 | 0.03 |
| duplicated | 64 | 0.1 | 1/10 | 30 | 30 | 0 | 0 | 0 | 4 / 4 | 1.00 |
| duplicated | 64 | 0.3 | 1/10 | 30 | 24 | 6 | 0 | 0 | 3 / 4 | 0.80 |
| duplicated | 64 | 0.5 | 1/10 | 30 | 3 | 25 | 2 | 0 | 0 / 4 | 0.10 |
| partly | 64 | 0.1 | 1/32 | 30 | 2 | 28 | 0 | 0 | 0 / 0 | 0.07 |
| partly | 64 | 0.3 | 1/32 | 30 | 0 | 29 | 0 | 1 | 0 / 0 | 0.00 |
| partly | 64 | 0.5 | 1/32 | 30 | 0 | 30 | 0 | 0 | 0 / 0 | 0.00 |
| partly | 64 | 0.1 | 1/10 | 30 | 11 | 17 | 2 | 0 | 2 / 4 | 0.36 |
| partly | 64 | 0.3 | 1/10 | 30 | 0 | 29 | 1 | 0 | 0 / 4 | 0.00 |
| partly | 64 | 0.5 | 1/10 | 30 | 0 | 29 | 1 | 0 | 0 / 4 | 0.00 |
| partly | 32 | 0.1 | 1/32 | 30 | 1 | 29 | 0 | 0 | 0 / 0 | 0.03 |
| partly | 32 | 0.3 | 1/32 | 30 | 0 | 30 | 0 | 0 | 0 / 0 | 0.00 |
| partly | 32 | 0.5 | 1/32 | 30 | 0 | 30 | 0 | 0 | 0 / 0 | 0.00 |
| partly | 32 | 0.1 | 1/10 | 30 | 9 | 19 | 2 | 0 | 2 / 4 | 0.31 |
| partly | 32 | 0.3 | 1/10 | 30 | 0 | 26 | 4 | 0 | 0 / 4 | 0.00 |
| partly | 32 | 0.5 | 1/10 | 30 | 0 | 27 | 3 | 0 | 0 / 4 | 0.00 |

### §30 endpoints for arm D's cells (crossover 0 and 0.7), same criterion

| contest | L | crossover | shared at start | seeds | won (> 90% shared) | shared gone | in between | lost the solution (< 20 exact) | slot-0 elite shared: won / all | mean shared share (verdict runs) |
|---|---|---|---|---|---|---|---|---|---|---|
| duplicated | 64 | 0.0 | 1/32 | 30 | 19 | 11 | 0 | 0 | 0 / 0 | 0.63 |
| duplicated | 64 | 0.7 | 1/32 | 30 | 0 | 30 | 0 | 0 | 0 / 0 | 0.00 |
| duplicated | 64 | 0.0 | 1/10 | 30 | 29 | 1 | 0 | 0 | 4 / 4 | 0.96 |
| duplicated | 64 | 0.7 | 1/10 | 30 | 0 | 27 | 3 | 0 | 0 / 4 | 0.00 |
| partly | 64 | 0.0 | 1/32 | 30 | 8 | 22 | 0 | 0 | 0 / 0 | 0.27 |
| partly | 64 | 0.7 | 1/32 | 30 | 0 | 30 | 0 | 0 | 0 / 0 | 0.00 |
| partly | 64 | 0.0 | 1/10 | 30 | 19 | 10 | 1 | 0 | 3 / 4 | 0.63 |
| partly | 64 | 0.7 | 1/10 | 30 | 0 | 28 | 2 | 0 | 0 / 4 | 0.00 |
| partly | 32 | 0.0 | 1/32 | 30 | 15 | 13 | 2 | 0 | 0 / 0 | 0.53 |
| partly | 32 | 0.7 | 1/32 | 30 | 0 | 30 | 0 | 0 | 0 / 0 | 0.00 |
| partly | 32 | 0.0 | 1/10 | 30 | 24 | 5 | 1 | 0 | 4 / 4 | 0.80 |
| partly | 32 | 0.7 | 1/10 | 30 | 0 | 26 | 4 | 0 | 0 / 4 | 0.00 |

### Arm E: reciprocal (shared in the majority, crossover 0.7)

| contest | L | crossover | shared at start | seeds | won (> 90% shared) | shared gone | in between | lost the solution (< 20 exact) | slot-0 elite shared: won / all | mean shared share (verdict runs) |
|---|---|---|---|---|---|---|---|---|---|---|
| duplicated | 64 | 0.7 | 768 | 30 | 30 | 0 | 0 | 0 | 25 / 25 | 1.00 |
| duplicated | 64 | 0.7 | 922 | 30 | 30 | 0 | 0 | 0 | 30 / 30 | 1.00 |
| duplicated | 64 | 0.7 | 992 | 30 | 30 | 0 | 0 | 0 | 30 / 30 | 1.00 |
| partly | 64 | 0.7 | 768 | 30 | 30 | 0 | 0 | 0 | 25 / 25 | 1.00 |
| partly | 64 | 0.7 | 922 | 30 | 30 | 0 | 0 | 0 | 30 / 30 | 1.00 |
| partly | 64 | 0.7 | 992 | 30 | 30 | 0 | 0 | 0 | 30 / 30 | 1.00 |
| partly | 128 | 0.7 | 768 | 30 | 30 | 0 | 0 | 0 | 25 / 25 | 1.00 |
| partly | 128 | 0.7 | 922 | 30 | 30 | 0 | 0 | 0 | 30 / 30 | 1.00 |
| partly | 128 | 0.7 | 992 | 30 | 30 | 0 | 0 | 0 | 30 / 30 | 1.00 |

### Arm F: few shared copies, crossover off, L 64 (100 seeds)

| contest | L | crossover | shared at start | seeds | won (> 90% shared) | shared gone | in between | lost the solution (< 20 exact) | slot-0 elite shared: won / all | mean shared share (verdict runs) |
|---|---|---|---|---|---|---|---|---|---|---|
| duplicated | 64 | 0.0 | 1 | 100 | 4 | 96 | 0 | 0 | 0 / 0 | 0.04 |
| duplicated | 64 | 0.0 | 8 | 100 | 23 | 77 | 0 | 0 | 1 / 2 | 0.23 |
| partly | 64 | 0.0 | 1 | 100 | 0 | 100 | 0 | 0 | 0 / 0 | 0.00 |
| partly | 64 | 0.0 | 8 | 100 | 10 | 90 | 0 | 0 | 1 / 2 | 0.10 |

Independence prediction from §30 (32 copies lost in 11/30 vs duplicated, 22/30 vs partly; P(win from n) ≈ 1 − (lost fraction)^(n/32)): duplicated n=1: 3/100, duplicated n=8: 22/100, partly n=1: 1/100, partly n=8: 7/100

### Arm G: stage 4, random starts (3000 generations, 50 seeds)

| L | crossover | seeds | fully exact ever (census) | median first generation | form at first census with fully exact: shared / partly / duplicated / other | end (final population, non-elite fully exact): ≥ 20 / 1–19 / 0 | final verdict (≥ 20): shared / partly / duplicated / mixed | final training-perfect share (mean) | any shared individual (census) | lost (census once ≥ 20 of 256 fully exact, end < 20) | median s per run |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 32 | 0.7 | 50 | 11 | 1380 | 0 / 7 / 4 / 0 | 7 / 0 / 43 | 0 / 3 / 4 / 0 | 0.09 | 0 | 0 | 436 |
| 32 | 0.3 | 50 | 15 | 1740 | 0 / 12 / 3 / 0 | 12 / 0 / 38 | 0 / 10 / 2 / 0 | 0.14 | 0 | 0 | 403 |
| 32 | 0.0 | 50 | 0 | – | 0 / 0 / 0 / 0 | 0 / 0 / 50 | 0 / 0 / 0 / 0 | 0.01 | 0 | 0 | 292 |
| 64 | 0.7 | 50 | 43 | 720 | 2 / 30 / 11 / 0 | 28 / 2 / 20 | 0 / 21 / 7 / 0 | 0.30 | 2 | 1 | 491 |
| 64 | 0.3 | 50 | 41 | 740 | 4 / 28 / 9 / 0 | 30 / 5 / 15 | 4 / 21 / 5 / 0 | 0.34 | 7 | 1 | 437 |
| 64 | 0.0 | 50 | 2 | 2740 | 0 / 2 / 0 / 0 | 2 / 0 / 48 | 0 / 2 / 0 / 0 | 0.02 | 0 | 0 | 400 |
| 128 | 0.7 | 50 | 43 | 700 | 3 / 26 / 14 / 0 | 20 / 8 / 22 | 3 / 11 / 6 / 0 | 0.31 | 9 | 3 | 665 |
| 128 | 0.3 | 50 | 42 | 800 | 4 / 29 / 9 / 0 | 26 / 3 / 21 | 4 / 16 / 6 / 0 | 0.34 | 7 | 3 | 574 |
| 128 | 0.0 | 50 | 4 | 1660 | 2 / 2 / 0 / 0 | 4 / 0 / 46 | 2 / 2 / 0 / 0 | 0.03 | 2 | 0 | 506 |

