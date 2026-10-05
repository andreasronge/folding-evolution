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

## Run 2026-10-05-1957: does R's sum>2 gain use the exact max>2 shortcut? (reopened under (c))

Reopened under condition (c) on the [strategy](../../../runs/2026-10-05-1945/strategy.md)'s
direction, for root 01's last experiment. Experiment: [proposal](../../../runs/2026-10-05-1957/proposal.md)
(revision of 1945, approved by the critic), [plan](../../../runs/2026-10-05-1957/plan.md), code
`experiments/chem_tape/evolve_shortcut_veto.py` plus an `eligible` mask in `chem_tape/evolve.py`
at commit `2a002a8` (branch `research/2026-10-05-1957`; code review passed on the second pass
after a runtime-gate fix). 1814's harness on sum>2 only, with training sets on which max>2 is
training-perfect by construction (A). Four cells: U / R × ordinary / veto, where *veto* bars any
program equal to max>2 on all 10,000 lists from reproduction (parents, clones, elites). Stage 1:
50-seed pilot. Stage 2 (600 or 800 seeds) only if pilot-based power reached 0.80 for all of
(a) interaction I, (b) R's veto penalty P_R, (c) "P_R upper < 1.25 when P_R = 1".
Data `experiments/output/2026-10-05/2026-10-05-1957-shortcut-veto/`, 223 s wall.

Result: **pilot-only stop; no registered contrast, no outcome label**
([analysis](../../../runs/2026-10-05-1957/analysis.md)). Power (a) and (b) were 300/300 at both
sizes; (c) was 0.48 (n=600) and 0.53 (n=800), so stage 2 did not run, as frozen. Pilot complete
and clean: 200/200 runs solved, 0 censored, 200/200 solvers re-verified exact, 100/100 identity
checks, veto never leaked.

Pilot only (n=50, exploratory, outside the registered family):

| Median ratio (98.75% CI) | Pilot |
|---|---|
| C1 = U-ord ÷ R-ord (R's gain on A) | 1.30 (0.71–2.32) |
| P_R = R-veto ÷ R-ord | 1.46 (0.99–2.08) |
| P_U = U-veto ÷ U-ord | 1.06 (1.00–1.46) |
| I = P_R ÷ P_U | 1.38 (0.82–2.00) |

- The exact max>2 phenotype is the usual last step: in ordinary runs where it appears (U 25/50,
  R 35/50), the first exact solver has an exact-max>2 parent in 55/60, and the solve follows
  within a median 1–2 generations. It appears late (median generation 21 U, 13 R).
- Vetoing it delays exposed runs in both arms (veto slower in 49 of 55 untied exposed pairs;
  median delay first-max>2 → solve 1 → 4 generations in U, 2 → 10 in R) but never prevents the
  solve (100/100). Near-max inexact programs take over (their share rises 2.4× in U, 3.3× in R;
  sampled ones agree with max>2 on ~99% of the domain).
- R meets the shortcut more often and earlier than U, as in 1814. Whether it costs R more than U
  (I) and whether R's gain even holds on A (C1) are unresolved at n=50.
- The reviewer finds the (c) power estimate fragile: it comes from resampling 50 pilot rows, and
  under resampling of the pilot itself it ranged 0.05–1.00 at n=800 (11/16 ≥ 0.80). Runtime did
  not force the stop; n≈1600 would have fitted the queue. So the honest reading is "the
  registered gate was not met", not "no affordable design can decide".

Against the explanations: G3 is neither supported nor excluded as an explanation of R's
advantage. At pilot strength, exact max>2 is *used* as a stepping stone in both arms and blocking
it costs a few generations, but it is not *needed*: a family of near-max programs serves as the
same route. G1 and G2 are untouched.

Decision: park 09 again, because the proposal and strategy committed to stopping this threshold
line after one valid run whatever the result, and a pilot-only stop under the frozen gate is that
result (the plan names it a feasibility outcome, not evidence against G3); 09's and root 01's
budgets are now spent. Running stage 2 after seeing the pilot would be a second look. Reopen
condition (c) is used up; I do not add a new one from this line beyond an owner-funded rerun.
Fairly sure of the pilot's descriptive pattern (direction is clear in 49/55 exposed pairs);
nothing is known at registered strength about R's advantage.
