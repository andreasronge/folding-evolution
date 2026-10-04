## Validation

- runs found: 210; duplicate (arm, L, seed) keys: 0
- seed-mixed L=64: 30/30 seeds (complete)
- seed-mixed L=128: 30/30 seeds (complete)
- seed-shared L=32: 30/30 seeds (complete)
- seed-shared L=64: 30/30 seeds (complete)
- seed-shared L=128: 30/30 seeds (complete)
- seed-dup L=64: 30/30 seeds (complete)
- seed-dup L=128: 30/30 seeds (complete)
- entry mapbias_s29_seed_mixed: status done, exit 0, commit 7141ecf, dirty True, wall 1030.38 s
- entry mapbias_s29_seed_shared: status done, exit 0, commit 7141ecf, dirty True, wall 1319.445 s
- entry mapbias_s29_seed_dup: status done, exit 0, commit 7141ecf, dirty True, wall 1024.001 s

## Readouts

### Readout 1: seed-mixed (shared share among fully exact individuals)

| L | seeds | final shared share: mean (min–max) | > 90% shared | > 90% duplicated | in between | no fully exact at end | final fully exact (mean) |
|---|---|---|---|---|---|---|---|
| 64 | 30 | 1.00 (0.95–1.00) | 30/30 | 0/30 | 0/30 | 0/30 | 0.35 |
| 128 | 30 | 1.00 (0.97–1.00) | 30/30 | 0/30 | 0/30 | 0/30 | 0.38 |

### Readout 2: seed-shared (does the shared form persist?)

| L | seeds | final fully exact (mean, min) | seeds with fully exact at every log point | final among fully exact: shared / partly / duplicated (means) | seeds ending < 50% shared |
|---|---|---|---|---|---|
| 32 | 30 | 0.34, 0.26 | 30/30 | 1.00 / 0.00 / 0.00 | 0/30 |
| 64 | 30 | 0.37, 0.31 | 30/30 | 1.00 / 0.00 / 0.00 | 0/30 |
| 128 | 30 | 0.36, 0.32 | 30/30 | 1.00 / 0.00 / 0.00 | 0/30 |

### Readout 3: seed-dup (does sharing arise from a duplicated start?)

| L | seeds | seeds with any shared individual (any log point) | max shared share | seeds with any partly shared | final fully exact (mean) | no fully exact at end | final partly / duplicated share (mean over seeds with fully exact) |
|---|---|---|---|---|---|---|---|
| 64 | 30 | 1/30 | 0.01 | 30/30 | 0.33 | 1/30 | 1.00 / 0.00 (n=29) |
| 128 | 30 | 3/30 | 0.01 | 30/30 | 0.34 | 1/30 | 0.99 / 0.01 (n=29) |

### Readout 4: run census (population means, generation 0 → final; reading from tags 0–2)

| arm | L | runs | read | unread | helpers (read, not an output run) | with a helper |
|---|---|---|---|---|---|---|
| seed-mixed | 64 | 3.50 → 7.25 | 3.50 → 3.64 | 0.00 → 3.61 | 0.50 → 0.90 | 0.50 → 0.89 |
| seed-mixed | 128 | 3.50 → 10.84 | 3.50 → 3.73 | 0.00 → 7.11 | 0.50 → 0.93 | 0.50 → 0.91 |
| seed-shared | 32 | 4.00 → 4.36 | 4.00 → 3.47 | 0.00 → 0.89 | 1.00 → 0.84 | 1.00 → 0.84 |
| seed-shared | 64 | 4.00 → 7.31 | 4.00 → 3.65 | 0.00 → 3.66 | 1.00 → 0.90 | 1.00 → 0.89 |
| seed-shared | 128 | 4.00 → 10.90 | 4.00 → 3.72 | 0.00 → 7.17 | 1.00 → 0.93 | 1.00 → 0.91 |
| seed-dup | 64 | 3.00 → 5.14 | 3.00 → 2.71 | 0.00 → 2.42 | 0.00 → 0.00 | 0.00 → 0.00 |
| seed-dup | 128 | 3.00 → 7.84 | 3.00 → 2.78 | 0.00 → 5.07 | 0.00 → 0.01 | 0.00 → 0.01 |

Fully exact individuals whose tag-1 or tag-2 output run feeds another output (other_output_helper; counted inside the three forms above), final generation, mean share:

- seed-mixed L=64: 0.004
- seed-mixed L=128: 0.000
- seed-shared L=32: 0.000
- seed-shared L=64: 0.000
- seed-shared L=128: 0.000
- seed-dup L=64: 0.015
- seed-dup L=128: 0.000

### Final populations: form tallies and decoded genomes

Tally = forms of all fully exact individuals in the final population (elites excluded); elites = forms of the elite slots.

**seed-mixed, L=64**

- seed 0: 349/1022 fully exact, tally {'shared': 349}, elites ['shared', 'shared']. Sampled: **shared**; consumers 3:2,1:1,3:0,2:1,1:0,0:3,7:0  
  `[3] C0 INPUT SUM C5 C5 ADD GT | [1] RECV0 RECV3 ADD C1 GT | [3] C0 INPUT SUM C5 C5 ADD NOP12 | [2] RECV0 RECV3 ADD THR GT | [1] CHARS NOP13 RECV0 RECV3 ADD ADD C1 C2 | [0] ADD INPUT NOP13 RMAX C5 GT | [7] RMAX RECV0 RECV3 ADD RMAX NOP12 C2 NOP13 INPUT SUM C5 C5 ADD`
- seed 1: 360/1022 fully exact, tally {'shared': 360}, elites ['duplicated', 'shared']. Sampled: **shared**; consumers 3:2,0:3,2:1,1:1,0:0,2:0,39:0  
  `[3] INPUT SUM C5 C5 ADD GT | [0] INPUT RMAX C5 GT | [2] RECV0 RECV3 ADD NOP13 C0 GT | [1] THR RECV0 RECV3 ADD C1 GT | [0] INPUT RMAX C5 GT | [2] RECV0 RECV3 ADD NOP13 C0 GT | [39] NOP NOP NOP NOP NOP NOP NOP NOP ADD NOP NOP NOP NOP NOP NOP SWAP`
- seed 2: 334/1022 fully exact, tally {'shared': 334}, elites ['duplicated', 'shared']. Sampled: **shared**; consumers 0:3,2:1,1:1,3:2,32:0,1:0,0:0  
  `[0] INPUT RMAX C5 GT | [2] DUP RADD RECV0 NOP12 RECV3 ADD SUM GT | [1] NOP RECV0 RECV3 ADD C1 GT NOP13 | [3] DUP GT GT INPUT SUM C5 DUP ADD GT | [32] RECV3 IF_GT ANY MAP_EQ_E | [1] NOP RECV0 RECV3 ADD C1 GT NOP13 | [0] INPUT RMAX C5 GT`
- seed 3: 344/1022 fully exact, tally {'shared': 343, 'partly': 1}, elites ['duplicated', 'shared']. Sampled: **shared**; consumers 0:3,59:0,3:2,14:0,1:1,2:1,1:0,19:0,63:0,18:0  
  `[0] INPUT RADD NOP RECV20 INPUT RMAX C5 GT RADD INPUT RMAX NOP12 C5 GT | [59]  | [3] C5 INPUT SUM C5 DUP ADD GT | [14]  | [1] RECV0 RECV3 ADD C1 GT | [2] THR RECV0 RECV3 ADD SWAP GT | [1] RECV0 RECV3 ADD C1 | [19] RMAX ADD GT | [63] RMAX GT INPUT INPUT SUM CHARS C5 C5 ADD SUM | [18] SUM RMAX`
- seed 4: 367/1022 fully exact, tally {'shared': 367}, elites ['shared', 'shared']. Sampled: **shared**; consumers 3:2,0:3,1:1,1:0,0:0,2:1,3:0,48:0,14:0  
  `[3] INPUT SUM C5 NOP C5 ADD GT NOP13 | [0] INPUT RMAX C5 GT | [1] RECV0 RECV3 ADD C1 GT | [1] NOP RECV3 ADD C1 | [0] INPUT RMAX C5 GT | [2] NOP RECV0 RECV3 ADD RECV16 GT | [3] NOP13 SUM C5 C5 ADD GT NOP12 | [48] SUM C5 C5 ADD GT NOP NOP IF_GT CHARS NOP NOP NOP DUP | [14] RMAX NOP MAP_EQ_E`

**seed-mixed, L=128**

- seed 0: 372/1022 fully exact, tally {'shared': 372}, elites ['shared', 'shared']. Sampled: **shared**; consumers 0:3,1:1,3:2,2:1,3:0,57:0,56:0,1:0,3:0,2:0,51:0,2:0,3:0,1:0  
  `[0] C0 INPUT RMAX C5 GT DUP | [1] RECV0 RECV3 ADD NOP C1 GT | [3] GT INPUT SUM C5 DUP ADD GT | [2] RECV0 RECV3 ADD SUM GT | [3] INPUT SUM C5 C5 ADD GT | [57] INPUT DUP RECV14 NOP13 | [56] SWAP INPUT SUM NOP13 C5 THR C5 RMAX GT | [1] RECV0 RECV3 ADD C1 GT | [3] INPUT SUM C5 C5 ADD GT | [2] RECV0 RECV3 ADD ANY GT | [51] MAP_EQ_E RECV11 CHARS INPUT GT | [2] GT RECV0 RECV3 ADD SUM GT | [3] C5 DUP ADD GT | [1] RECV0 RECV3 ADD NOP GT NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP RECV33`
- seed 1: 407/1022 fully exact, tally {'shared': 404, 'partly': 2, 'duplicated': 1}, elites ['duplicated', 'shared']. Sampled: **shared**; consumers 2:1,3:2,0:3,1:1,2:0,13:0,50:0,7:0,0:0,39:0  
  `[2] RECV0 RECV3 ADD ANY GT | [3] RADD C5 INPUT SUM C5 C5 ADD GT | [0] SWAP INPUT RMAX C5 GT | [1] RECV0 RECV3 ADD C1 NOP GT | [2] SUM RECV0 NOP13 RECV3 ADD GT THR | [13] SWAP GT | [50] RMAX C5 CHARS | [7] NOP12 DUP INPUT CHARS C5 ADD GT | [0] IF_GT SWAP INPUT RMAX C5 GT NOP NOP NOP NOP NOP RMAX NOP C2 | [39] NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP SUM NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP13`
- seed 2: 410/1022 fully exact, tally {'shared': 406, 'duplicated': 1, 'partly': 3}, elites ['duplicated', 'shared']. Sampled: **shared**; consumers 2:1,1:1,0:3,3:2,57:0,57:0,29:0,43:0,50:0  
  `[2] RECV0 RECV3 ADD ANY GT | [1] SWAP RECV0 RECV3 ADD C1 GT | [0] NOP12 NOP SUM INPUT RMAX C5 GT | [3] INPUT SUM C5 DUP ADD GT | [57]  | [57] RMAX INPUT C2 MAP_EQ_E GT | [29] RECV5 C1 INPUT C2 RECV30 RMAX SUM NOP13 ANY RECV3 ADD GT C2 C5 THR INPUT RMAX C5 | [43] RECV54 RECV21 RMAX C1 GT C1 NOP12 RMAX | [50] NOP CHARS THR C5 GT NOP NOP NOP NOP NOP NOP C5 NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP THR NOP12 NOP NOP NOP13 NOP NOP NOP NOP NOP RECV47 C1 NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP13 ANY NOP NOP NOP INPUT`
- seed 3: 385/1022 fully exact, tally {'shared': 382, 'duplicated': 3}, elites ['duplicated', 'shared']. Sampled: **shared**; consumers 2:1,1:1,3:2,1:0,0:3,46:0  
  `[2] RECV0 RECV3 ADD C0 NOP13 GT | [1] RECV0 RECV3 ADD C1 GT | [3] C1 C5 INPUT SUM C5 DUP ADD GT | [1] RECV24 NOP RECV0 RECV3 ADD C1 GT | [0] NOP13 INPUT RMAX C5 NOP GT | [46] DUP GT C1 ADD GT ANY SUM RECV0 RECV3 NOP GT ANY THR NOP NOP NOP C2 C0 RMAX NOP RADD NOP IF_GT NOP C1 NOP NOP NOP NOP13 NOP THR NOP NOP C0 SWAP NOP NOP NOP NOP ADD NOP NOP NOP NOP NOP DUP NOP NOP NOP NOP NOP MAP_EQ_E NOP INPUT NOP NOP NOP NOP NOP NOP NOP NOP NOP13 NOP C1 NOP NOP NOP NOP GT NOP NOP NOP NOP MAP_EQ_E NOP NOP NOP12 GT NOP NOP NOP NOP RECV21`
- seed 4: 364/1022 fully exact, tally {'shared': 364}, elites ['shared', 'shared']. Sampled: **shared**; consumers 2:1,3:2,0:3,1:1,45:0,24:0  
  `[2] CHARS C5 CHARS RECV0 RECV3 ADD C0 GT | [3] INPUT SUM C5 C5 ADD GT | [0] THR INPUT RMAX C5 GT | [1] MAP_EQ_E IF_GT NOP12 RECV0 RECV3 ADD DUP C1 GT | [45] RMAX NOP NOP NOP NOP NOP NOP NOP NOP NOP RMAX SUM NOP DUP NOP NOP C0 NOP NOP IF_GT NOP SWAP NOP NOP NOP NOP NOP12 CHARS NOP C0 DUP IF_GT NOP NOP12 SWAP NOP NOP NOP NOP13 RECV50 NOP MAP_EQ_E | [24] DUP NOP C1 NOP ANY DUP NOP NOP NOP NOP NOP NOP GT NOP THR RECV6 NOP IF_GT MAP_EQ_E NOP NOP NOP NOP NOP NOP NOP NOP INPUT NOP NOP RADD NOP NOP NOP NOP NOP NOP DUP NOP NOP C2`

**seed-shared, L=32**

- seed 0: 347/1022 fully exact, tally {'shared': 347}, elites ['shared', 'shared']. Sampled: **shared**; consumers 3:2,1:1,0:3,2:1,2:0  
  `[3] INPUT SUM C5 C5 ADD GT | [1] RECV0 RECV3 ADD C1 GT | [0] ADD INPUT RMAX C5 GT NOP12 | [2] RECV0 RECV3 ADD ANY GT | [2] RECV0 RECV3 ADD NOP12 GT`
- seed 1: 347/1022 fully exact, tally {'shared': 347}, elites ['shared', 'shared']. Sampled: **shared**; consumers 13:0,0:3,1:1,3:2,2:1  
  `[13] RECV0 RECV3 ADD RADD ADD | [0] INPUT RMAX C5 GT | [1] RECV0 RECV3 ADD C1 GT | [3] INPUT RADD C5 C5 ADD GT | [2] RECV0 RECV3 ADD ANY GT`
- seed 2: 349/1022 fully exact, tally {'shared': 349}, elites ['shared', 'shared']. Sampled: **shared**; consumers 0:3,1:1,2:1,3:2,3:0  
  `[0] INPUT RMAX C5 GT | [1] RECV0 RECV3 ADD C1 GT | [2] RECV0 RECV3 ADD C0 GT | [3] INPUT SUM C5 DUP ADD GT | [3] INPUT SUM C5 C5 ADD GT`
- seed 3: 320/1022 fully exact, tally {'shared': 320}, elites ['shared', 'shared']. Sampled: **shared**; consumers 1:1,2:1,0:3,3:2  
  `[1] RECV0 RECV3 ADD C1 GT | [2] RECV0 RECV3 ADD C0 GT | [0] NOP13 INPUT RMAX C5 GT | [3] INPUT RADD C5 DUP ADD GT`
- seed 4: 354/1022 fully exact, tally {'shared': 354}, elites ['shared', 'shared']. Sampled: **shared**; consumers 1:1,3:2,0:3,2:1  
  `[1] RECV0 RECV3 ADD C1 GT | [3] INPUT SUM C5 C5 ADD GT | [0] INPUT RMAX C5 GT | [2] RECV0 RECV3 ADD C0 GT`

**seed-shared, L=64**

- seed 0: 351/1022 fully exact, tally {'shared': 351}, elites ['shared', 'shared']. Sampled: **shared**; consumers 0:3,3:2,18:0,3:0,1:1,2:1,49:0,48:0  
  `[0] INPUT RMAX C5 GT | [3] INPUT SUM C5 DUP ADD GT | [18] RECV15 RECV3 ADD C1 GT ADD CHARS RMAX C5 GT | [3] INPUT SUM C5 DUP ADD GT | [1] RECV0 RECV3 ADD C1 GT | [2] RADD IF_GT RECV0 RECV3 NOP ADD RECV57 GT | [49] INPUT SUM MAP_EQ_E C5 ADD C5 | [48] RECV0 CHARS RECV3 CHARS C1 GT NOP RECV57`
- seed 1: 367/1022 fully exact, tally {'shared': 367}, elites ['shared', 'shared']. Sampled: **shared**; consumers 3:2,1:1,2:1,3:0,18:0,20:0,0:3,2:0  
  `[3] INPUT SUM C5 C5 ADD GT | [1] NOP12 RECV0 RECV3 NOP12 ADD C1 GT | [2] RECV0 RECV3 ADD SUM GT | [3] INPUT SUM C5 DUP ADD GT | [18] RECV23 RECV3 ADD C1 GT | [20] RADD RECV0 ANY INPUT SUM GT C5 DUP GT | [0] INPUT RMAX C5 GT | [2] RECV0 RECV3 ADD SUM GT`
- seed 2: 388/1022 fully exact, tally {'shared': 388}, elites ['shared', 'shared']. Sampled: **shared**; consumers 1:1,2:1,0:3,3:2,51:0  
  `[1] RECV0 RECV3 ADD C1 GT | [2] RECV0 RECV3 ADD DUP RMAX GT | [0] ADD INPUT RMAX C5 GT | [3] INPUT SUM C5 C5 ADD GT | [51] NOP NOP NOP NOP NOP NOP NOP NOP SWAP SWAP NOP NOP NOP RADD NOP MAP_EQ_E NOP NOP SWAP NOP C2 SUM NOP NOP NOP12 NOP NOP CHARS RECV40 NOP NOP C5 NOP NOP IF_GT C1`
- seed 3: 352/1022 fully exact, tally {'shared': 352}, elites ['shared', 'shared']. Sampled: **shared**; consumers 2:1,1:1,3:2,0:3,58:0,57:0,1:0,2:0,1:0,45:0,2:0  
  `[2] RECV0 RECV3 ADD ANY GT | [1] RECV0 RECV3 ADD C1 GT | [3] INPUT SUM C5 DUP ADD GT | [0] IF_GT INPUT NOP13 RMAX C5 GT | [58] RECV0 RECV3 ADD C1 GT SWAP INPUT RMAX C5 | [57]  | [1] NOP RECV0 RECV3 ADD C1 GT | [2] RECV0 RECV3 ADD C0 GT | [1] RECV33 RECV3 ADD C1 GT | [45] GT | [2] RECV0 RECV3 NOP13 C0 GT`
- seed 4: 370/1022 fully exact, tally {'shared': 370}, elites ['shared', 'shared']. Sampled: **shared**; consumers 3:2,1:1,0:3,2:1,0:0,3:0,1:0  
  `[3] INPUT SUM C5 C5 ADD GT | [1] SUM RMAX RECV0 RECV3 ADD C1 GT | [0] INPUT RMAX C5 GT DUP | [2] RECV5 RECV0 RECV3 ADD C0 GT | [0] INPUT RMAX C5 GT | [3] INPUT SUM C5 C5 ADD GT | [1] CHARS RECV0 RECV3 ADD C1 GT`

**seed-shared, L=128**

- seed 0: 373/1022 fully exact, tally {'shared': 373}, elites ['shared', 'shared']. Sampled: **shared**; consumers 2:1,3:2,1:1,56:0,3:0,3:0,0:3,2:0,3:0,40:0,46:0,59:0  
  `[2] RECV0 RECV3 ADD RMAX GT | [3] INPUT SUM C5 C5 ADD GT | [1] RECV0 RECV3 ADD C1 GT | [56] ADD ADD NOP12 GT MAP_EQ_E CHARS | [3] SWAP C2 RADD INPUT SUM C5 DUP ADD GT | [3] INPUT SUM C5 RECV20 ADD GT | [0] ADD SUM INPUT RMAX C5 GT | [2] RECV0 RECV3 ADD C0 NOP12 GT | [3] IF_GT INPUT SUM C5 C5 ADD GT | [40] NOP RECV0 NOP RECV3 ADD ANY GT | [46] ANY SUM SWAP C5 C5 ADD MAP_EQ_E SWAP NOP13 RADD INPUT C2 RECV22 RECV0 RADD IF_GT GT NOP12 NOP NOP NOP NOP NOP NOP NOP DUP NOP NOP NOP SWAP NOP NOP INPUT | [59] NOP NOP NOP NOP NOP SWAP NOP NOP NOP NOP NOP NOP SWAP NOP RMAX C1`
- seed 1: 370/1022 fully exact, tally {'shared': 370}, elites ['shared', 'partly']. Sampled: **shared**; consumers 0:3,57:0,3:2,1:1,3:0,61:0,2:1,0:0,23:0  
  `[0] NOP12 INPUT RMAX C5 GT | [57] GT NOP13 | [3] INPUT SUM C5 C5 ADD GT | [1] SUM RECV45 RECV20 C0 NOP RECV57 RECV34 RECV0 RECV3 ADD C1 GT | [3] INPUT SUM C5 C5 ADD GT | [61] C2 NOP13 C0 RADD C2 C2 C1 | [2] RECV0 RECV3 ADD C0 GT | [0] ADD DUP INPUT RMAX C5 GT | [23] NOP NOP NOP NOP NOP NOP DUP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP12 NOP NOP ANY`
- seed 2: 407/1022 fully exact, tally {'shared': 407}, elites ['shared', 'shared']. Sampled: **shared**; consumers 1:1,2:1,0:3,2:0,3:2,1:0  
  `[1] CHARS RECV0 RECV3 ADD C1 NOP12 GT | [2] RECV0 RECV3 ADD C0 GT NOP13 | [0] INPUT RMAX C5 GT | [2] RECV0 RECV3 ADD C0 GT NOP13 | [3] INPUT SUM C5 C5 ADD GT | [1] RECV0 RECV3 ADD C1 GT NOP NOP NOP NOP NOP MAP_EQ_E NOP NOP SUM NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP INPUT NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP ANY NOP NOP ADD NOP NOP NOP ANY`
- seed 3: 353/1022 fully exact, tally {'shared': 352, 'partly': 1}, elites ['shared', 'shared']. Sampled: **shared**; consumers 2:1,3:2,0:3,57:0,0:0,1:1,3:0,62:0,62:0,3:0,58:0,45:0,59:0  
  `[2] IF_GT RECV0 RECV3 ADD NOP NOP SUM GT | [3] INPUT RADD C5 C5 ADD GT | [0] INPUT RMAX C5 GT | [57] NOP SUM MAP_EQ_E ADD RADD SWAP C0 GT | [0] INPUT RMAX C5 GT | [1] RECV0 NOP13 RECV3 ADD C1 GT | [3] INPUT RADD C0 C5 ADD GT | [62] ANY NOP C1 NOP12 CHARS ADD NOP13 | [62] RECV40 INPUT | [3] INPUT RADD C5 C5 ADD GT | [58] ADD INPUT | [45]  | [59] IF_GT RECV0 RECV3 ADD NOP NOP SUM GT NOP NOP NOP RADD NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP DUP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP12`
- seed 4: 382/1022 fully exact, tally {'shared': 382}, elites ['shared', 'shared']. Sampled: **shared**; consumers 3:2,2:1,1:1,60:0,4:0,62:0,55:0,0:3,32:0,1:0,28:0,0:0,55:0,32:0,1:0  
  `[3] INPUT SUM C5 C5 NOP ADD GT | [2] GT INPUT C0 RECV0 NOP RECV3 ADD RECV52 GT | [1] THR RMAX RECV0 RECV3 ADD ADD C1 GT | [60] INPUT RECV0 NOP RECV3 ADD GT RECV0 THR GT | [4] C1 CHARS IF_GT ANY | [62] INPUT C0 C5 GT | [55] INPUT SWAP RMAX RECV0 RECV3 ADD C0 GT SWAP | [0] RECV15 INPUT RMAX C5 GT | [32] INPUT RMAX GT | [1] C1 CHARS RECV0 RECV3 ADD C1 GT | [28] THR ANY NOP RADD C5 C5 ADD GT | [0] INPUT RMAX C5 GT | [55] C0 CHARS SWAP | [32] IF_GT GT THR C0 DUP | [1] RECV0 RECV3 ADD C1 GT NOP NOP NOP NOP NOP NOP RADD NOP C0`

**seed-dup, L=64**

- seed 0: 322/1022 fully exact, tally {'partly': 321, 'duplicated': 1}, elites ['duplicated', 'partly']. Sampled: **partly**; consumers 0:3,2:1,1:1,0:0,0:0,2:0  
  `[0] RMAX RECV25 C5 C2 INPUT RMAX C5 GT | [2] ANY RECV63 RECV0 INPUT RADD C5 C5 ADD GT ADD RMAX GT | [1] NOP RECV0 INPUT RADD C5 C5 ADD GT ADD C1 GT | [0] INPUT RMAX C5 GT | [0] INPUT RMAX C5 GT | [2] ANY RECV63 RECV0 INPUT RADD C5 C5 ADD GT ANY ADD RMAX GT`
- seed 1: 367/1022 fully exact, tally {'partly': 367}, elites ['duplicated', 'partly']. Sampled: **partly**; consumers 2:1,1:1,14:0,0:3,49:0,24:0  
  `[2] ANY RECV0 INPUT RADD C5 C5 ADD GT ADD SUM GT | [1] NOP RECV0 INPUT SUM C5 C5 ADD GT ADD C1 GT | [14] NOP12 NOP CHARS NOP IF_GT NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP GT RMAX | [0] MAP_EQ_E INPUT RMAX C5 GT | [49]  | [24] RMAX C5 GT`
- seed 2: 340/1022 fully exact, tally {'partly': 340}, elites ['duplicated', 'partly']. Sampled: **partly**; consumers 2:1,0:3,1:1,2:0,0:0,0:0  
  `[2] RMAX RECV0 INPUT SUM C5 C5 ADD GT ADD SWAP GT | [0] INPUT RMAX C5 GT | [1] RECV0 INPUT SUM C5 C5 ADD GT ADD C1 GT | [2] RECV34 RECV0 C1 SUM C5 C5 IF_GT GT ADD SWAP GT DUP | [0] IF_GT INPUT RMAX C5 GT | [0] INPUT NOP C1 C1 C5 GT`
- seed 3: 343/1022 fully exact, tally {'partly': 338, 'duplicated': 5}, elites ['duplicated', 'partly']. Sampled: **partly**; consumers 0:3,2:1,1:1,2:0  
  `[0] CHARS NOP13 RMAX C0 INPUT RMAX C5 GT | [2] RECV0 INPUT SUM C5 C5 ADD GT ADD SUM GT | [1] RECV0 INPUT SUM C5 C5 ADD GT ADD C1 GT | [2] RECV0 INPUT SUM C5 C5 ADD GT ADD C0 GT NOP NOP NOP NOP NOP NOP NOP12 NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP C2`
- seed 4: 345/1022 fully exact, tally {'partly': 343, 'duplicated': 2}, elites ['duplicated', 'partly']. Sampled: **partly**; consumers 1:1,38:0,2:1,0:2,0:0  
  `[1] ANY RECV0 INPUT RADD C5 DUP ADD GT ADD C1 GT | [38]  | [2] INPUT RMAX C5 GT INPUT SUM C5 C5 ADD GT ADD C0 GT | [0] MAP_EQ_E INPUT RMAX C5 GT | [0] INPUT RMAX C5 GT NOP RMAX NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP C5`

**seed-dup, L=128**

- seed 0: 340/1022 fully exact, tally {'partly': 340}, elites ['duplicated', 'partly']. Sampled: **partly**; consumers 60:0,1:1,51:0,2:1,0:3,2:0,2:0,0:0,0:0,42:0,31:0,0:0  
  `[60] RMAX C2 C0 | [1] NOP RECV0 INPUT SUM C5 C5 ADD GT ADD C1 GT | [51] RECV0 C1 SUM SWAP C0 C0 ADD GT GT RADD IF_GT RMAX RECV29 | [2] NOP13 RECV0 INPUT RADD C5 C5 ADD GT ADD RADD GT | [0] CHARS ANY C1 INPUT RMAX C5 GT NOP13 | [2] NOP13 RECV0 INPUT RADD C5 ADD NOP12 GT ADD RADD GT | [2] RECV0 INPUT RADD C5 C5 ADD GT ADD NOP12 RADD GT | [0] INPUT RMAX C5 GT | [0] INPUT RMAX C5 RADD | [42] C2 GT DUP C1 | [31] C5 C1 | [0] C1 INPUT C5 C5 DUP NOP NOP C2 NOP THR NOP12 NOP NOP NOP NOP NOP12 GT NOP NOP NOP NOP NOP13 RECV32 NOP NOP NOP RECV60 NOP DUP`
- seed 1: 363/1022 fully exact, tally {'partly': 361, 'duplicated': 2}, elites ['duplicated', 'partly']. Sampled: **partly**; consumers 14:0,0:3,1:1,2:1,30:0,1:0,29:0,0:0,53:0,47:0  
  `[14] NOP13 RADD MAP_EQ_E SWAP ANY SUM C5 CHARS ADD IF_GT C2 C2 GT RADD | [0] INPUT RMAX C5 GT | [1] RECV0 INPUT RADD C5 C5 ADD GT ADD C1 GT | [2] RECV0 INPUT RADD C5 C5 ADD GT ADD ANY GT | [30]  | [1] RECV28 INPUT RADD C5 C5 ADD GT ADD C1 GT | [29] C0 RECV29 RECV56 INPUT RADD C0 C5 ADD DUP ADD GT | [0] DUP SWAP INPUT RMAX GT | [53] NOP13 INPUT RMAX C5 GT NOP NOP NOP NOP NOP NOP12 DUP NOP NOP NOP NOP NOP NOP IF_GT NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP ADD NOP ADD GT NOP13 MAP_EQ_E | [47] GT NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP RMAX`
- seed 2: 384/1022 fully exact, tally {'partly': 384}, elites ['duplicated', 'partly']. Sampled: **partly**; consumers 0:3,1:1,5:0,2:1,18:0,1:0,2:0,1:0,18:0  
  `[0] MAP_EQ_E RMAX GT DUP MAP_EQ_E INPUT RMAX C5 GT | [1] RECV0 INPUT SUM C5 C5 ADD GT ADD C1 GT | [5] GT C2 MAP_EQ_E RADD | [2] INPUT RECV0 INPUT SUM C5 C5 ADD GT ADD RECV29 GT | [18] ANY GT INPUT SUM C1 RADD INPUT CHARS SUM SUM ADD C2 RECV56 CHARS ANY SWAP DUP C0 C2 SUM MAP_EQ_E RMAX IF_GT C5 THR GT | [1] RECV0 INPUT SUM NOP12 C5 C5 CHARS ADD GT ADD C1 NOP GT | [2] RECV0 INPUT SUM C5 C5 ADD GT ADD NOP12 RMAX GT | [1] RECV0 RADD NOP12 C5 C5 ADD GT ADD C1 RECV44 GT | [18] C5 NOP13 DUP C5 INPUT THR NOP12 SWAP RMAX ADD NOP12 RECV36 ANY ADD INPUT THR RMAX MAP_EQ_E INPUT DUP`
- seed 3: 341/1022 fully exact, tally {'partly': 339, 'duplicated': 2}, elites ['duplicated', 'partly']. Sampled: **partly**; consumers 1:1,0:2,0:0,20:0,1:0,53:0,44:0,2:1,0:0,20:0  
  `[1] RECV36 C2 RECV0 INPUT RADD C5 DUP ADD GT ADD C1 GT | [0] INPUT RMAX C5 GT | [0] NOP INPUT DUP RMAX C5 GT | [20] THR MAP_EQ_E RECV0 INPUT SUM C5 C2 RADD C5 C5 GT ADD RECV61 GT | [1] NOP DUP RECV31 INPUT RADD C5 DUP ADD GT ADD C1 GT | [53] INPUT RMAX NOP13 GT NOP NOP NOP SUM NOP NOP NOP NOP GT NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP C2 NOP NOP NOP NOP RMAX NOP NOP SUM NOP C2 | [44] C0 ANY GT | [2] INPUT RMAX C5 GT INPUT SUM C5 C5 ADD GT ADD C0 GT | [0] INPUT RMAX C5 GT | [20] `
- seed 4: 362/1022 fully exact, tally {'partly': 362}, elites ['duplicated', 'partly']. Sampled: **partly**; consumers 1:1,32:0,2:1,0:3,28:0,7:0  
  `[1] RADD RECV0 INPUT SUM C5 C5 ADD GT NOP12 ADD C1 GT | [32] RECV0 INPUT SUM C5 C5 ADD RMAX ADD C1 GT | [2] RECV0 INPUT SUM C5 DUP ADD GT ADD RADD GT | [0] INPUT RMAX C5 C0 INPUT RMAX ADD C5 GT | [28] C5 C1 C5 C5 DUP NOP13 C2 RECV59 SWAP C1 GT | [7] NOP INPUT SWAP NOP NOP NOP NOP IF_GT NOP NOP NOP NOP NOP INPUT NOP NOP NOP INPUT NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP C0 NOP INPUT MAP_EQ_E NOP NOP NOP NOP NOP NOP NOP12 NOP DUP NOP NOP NOP SWAP NOP NOP NOP NOP C1 NOP NOP NOP NOP NOP NOP NOP NOP NOP NOP13 RMAX`

