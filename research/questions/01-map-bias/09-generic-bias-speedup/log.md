# Log: 09-generic-bias-speedup

## Opened 2026-10-05 by the steward

Opened from run [2026-10-05-1705](../../../runs/2026-10-05-1705/analysis.md) (08's evolution
test): the mismatched fitted vector, with no sampling lift on the holdouts, sped evolution
3.3× / 1.9× over uniform, an unregistered contrast that carries most of the matched speed-up.
The program goes to strategy first (`next: strategy` in
[decision](../../../runs/2026-10-05-1705/decision.md)), so no experiment is proposed yet.

## Run 2026-10-05-1814: which part of the other family's vector carries the speed-up?

Experiment: [proposal](../../../runs/2026-10-05-1814/proposal.md) (revision of 1810, approved
by the critic), [plan](../../../runs/2026-10-05-1814/plan.md), code
`experiments/chem_tape/evolve_bias_components.py` at commit `31d4408` (branch
`research/2026-10-05-1814`). Same harness as 1705 (TAG, L 64, P1024, lexicase, crossover v2
0.7 selected mate, mutation 0.015, cap 262,144). Four arms per task, each task using the
other family's fit as X: U uniform; IG = X's INPUT and GT, other 20 ops uniform; R = INPUT
and GT at 1/22, other 20 ops in X's proportions; X. Fresh master seed, 250 paired seeds per
cell, one look, 2,000 runs; 10 contrasts at 99.5%; frozen exclusive labels (carries = within
1.5× of X and faster than U). Plus 125M sampled tapes per IG/R vector. 3,572 s wall, complete;
all 1,953 solvers re-verified exact; 47 runs censored at the cap.

Result: **task disagreement → park**, as pre-registered
([analysis](../../../runs/2026-10-05-1814/analysis.md)).

| Ratio of median evaluations (99.5% CI) | sum>2 | max>2 |
|---|---|---|
| U ÷ X (replication) | **2.73** (2.12–3.48) | **2.02** (1.45–2.46) |
| U ÷ IG | 2.11 (1.63–3.01) | 2.24 (1.65–2.79) |
| U ÷ R | 1.61 (1.23–2.01) | 0.93 (0.66–1.28) |
| IG ÷ X | 1.29 (0.92–1.63) | 0.90 (0.71–1.08) |
| R ÷ X | 1.69 (1.39–2.20) | 2.16 (1.57–2.78) |
| Labels | IG unresolved, R unresolved | **IG carries**, R falls short (no gain over U shown) |

- X's speed-up replicates on fresh seeds in both tasks (1705: 3.3× / 1.9× on 50 pairs).
- max>2: raising INPUT and GT (rest thinned evenly) reproduces X's speed-up; IG solved all
  250 seeds, X left 10 unsolved, R left 30 (U 5). The rest of the vector shows no gain.
- sum>2: both components beat uniform; IG÷X misses the 1.5 margin by 0.13 at the upper bound,
  R÷X misses "short" by 0.11 at the lower bound. Both sit between the two effect sizes the
  precision check covered.
- Descriptive, and the most useful number: **X's flat sampling rate is a cancellation.** IG
  alone raises the exact-solver rate 3.2× / 3.9× over uniform; R alone lowers it to 0.23× /
  0.35× (intervals exclude 1; U and X counts historical from 1558). The products (0.74, 1.36)
  are close to X's 1.02 / 1.33. So the carrying component on max>2 is not a no-lift
  intervention. The only clear speed-up without (indeed against) supply left is R on sum>2
  (1.61× faster with 0.23× the solvers), where R and X, both with REDUCE_MAX raised, meet
  ~10× more training-perfect shortcuts than U and IG. Splitting sum>2 seeds by whether max>2
  fits the training set does not separate the arms (49 seeds in the small group): G3 neither
  supported nor excluded.
- The arms differ in how soon a training-perfect program appears (median generation e.g.
  sum>2 U 38, IG 15, R 21, X 10); the exact solve follows within 0–2 generations everywhere.
- The decode cannot discriminate: INPUT and GT are on the output path in every saved solver
  and shortcut in every arm, uniform included.

Against the explanations: G1 (INPUT/GT scaffold supply) holds as an intervention on max>2 and
is unresolved but leaning on sum>2 (point 1.29, paired geometric mean 1.09). G2 (rest of the
vector) fails on max>2 and is partial, resolved slower than X, on sum>2. G3 is untested in
effect. None of this separates mechanisms: initialization and mutation stay coupled, IG
also thins every other op by 0.82×, and R also moves task-relevant ops.

Decision: park 09, because the frozen rule closes it only on the same carrying set in both
tasks and the tasks disagree (max>2 {IG}, sum>2 {}); the plan forbids a follow-up run to
strengthen the sum>2 reading, and 09's stop rule was one experiment. The question's premise
has also narrowed: the "no-lift" speed-up was mostly IG's lift and R's loss cancelling, so
what is left unexplained is R's sum>2 gain, a one-task effect that G3 fits but nothing here
tests. Fairly sure of the replication and of IG ≈ X on max>2; the sampling decomposition is
descriptive with small historical denominators; sum>2 component status is genuinely open.
