---
status: open
tags: [map-bias, evolve-the-bias, task-family, compositional-transfer, decoder, fresh-start]
budget: {experiments: 10, used: 0}
---
# Can an adapted decoder help fresh populations solve unseen operation combinations beyond a token-frequency bias?

Current summary: **learned token weights on G transfer about 2× to the withheld compositions
and to branch-else; allowing learned contextual moves added no resolved training gain on top (≤ 1.11×),
their holdout increment is unresolved, and the one off-family hint that they shift speed toward
branch shapes did not replicate in a second set of learning runs from the same starts. On the
four-reducer bank, with a narrower split (one BE, two PA holdouts), the same token learner
improves G4 about 2–3× on both families' withheld cells, and which family it was trained on
made no detectable difference there: matched over mismatched 1.02× [0.84, 1.25] (BE) and 0.96×
[0.79, 1.15] (PA). The 95% upper bounds are 1.2485× on BE (roughly 1.3× in leave-one-map-out
checks) and 1.15× on PA; a 1.1× family preference is not excluded. On those three cells the
frozen maps' gain comes from both their starting programs and their use during search, which
overlap heavily: each conditional increment is about 1.3–1.4×, against a 2.29× diagonal; on the
ten training cells the same holds (1.28×, 1.33×), and the start weighs relatively more on BE
cells than on PA cells (C −0.45 log2 [−0.68, −0.22]; family not separated from shape or
difficulty)** (10 of 10 slots used, budget spent; strategy 1400 raised the budget from 5 to 7,
strategy 1723 to 9, strategy 2331 to 10).
Run 2026-10-07-0315 ([17](17-decoder-initialization-variation/question.md), commit `5dae3a6`,
row 1): the same frozen 2×2 on the ten training cells (4 BE, 6 PA), 200 fresh seeds, 122 000
searches, 4.3 h, all validation passed. Ongoing-decoder increment given M's start 1.28× [1.22,
1.34]; start increment given ongoing M 1.33× [1.26, 1.40]; diagonal 2.44× [2.23, 2.66];
interaction −0.52 log2 [−0.62, −0.42]. S = log2(MG/GM) negative on all four BE cells (each
resolved), −0.05 to +0.54 on the PA cells (none resolved negative); C = −0.45 [−0.68, −0.22]
(Welch over cells), 20/20 maps agree in direction. S tracks MM difficulty across cells (r 0.77,
post hoc), so family, shape and difficulty tail are not separated on these screened cells.
Run 2026-10-06-2331 ([17](17-decoder-initialization-variation/question.md), commit `8f42f38`,
row 3): the 20 frozen 1723 maps (M) and G4 (G) crossed as starting-program source × search
decoder, with generation-0 token tapes held identical by re-encoding; 400 fresh seeds, three
2229 cells. Ongoing-decoder increment given M's start 1.39× [1.31, 1.47]; start increment given
ongoing M 1.30× [1.24, 1.36]; diagonal 2.29× [2.05, 2.54]; interaction −0.34 log2 [−0.40,
−0.29] (sub-additive in 20/20 maps). Start-heavy on the BE cell (ongoing increment 1.11× [1.04,
1.19]), ongoing-heavy on the PA cells; one BE cell, descriptive.
Run 2026-10-06-2229 ([16](16-crossed-family-adaptation/question.md), commit `33fcee2`, row 4):
the 20 frozen stage-1 maps and G4 on the three holdouts, 400 shared fresh seeds each. Gains over
G4 resolved in all six arm × cell estimates (1.97×–2.93×, lowest lower bound 1.63×); holdout
gains remain substantial (BE's point gain slightly lower than on training, PA's higher; these
cross-block comparisons do not establish equality or absence of overfitting). Pre-stated within-map interaction 0.98× [0.83, 1.15].
The BE bound holds by 0.0015 and is not robust to dropping single maps (upper bound then
1.25–1.30).
Run 2026-10-06-1723 (16, stage 1, commit `db96645`, row 4):
10 independent G4-based token-multiplier trajectories per family (BE trains on 4 cells, PA on 6).
Own-family gain over G4 on fresh training searches: BE 2.18× [1.98, 2.40], PA 2.27× [1.95, 2.65].
Off-family training cells: 2.07× [1.94, 2.21] and 1.93× [1.61, 2.30]. Matched over mismatched
in-sample: 1.13× [0.93, 1.37] on BE cells and 1.10× [0.93, 1.29] on PA cells, both unresolved;
a post hoc within-map interaction 1.24× [1.09, 1.41]. Learning cost 10–14 min per trajectory.
Run 2026-10-06-1603 ([15](15-four-reducer-family-bank/question.md), commit `92ba7c5`, row 1):
adding FIRST to SUM/MAX/MIN leaves 13 of 36 ten-token cells on D1331 (BE 5, PA 8). BE has no
holdout pair whose roles are covered by training, on any of three domains; PA splits. On all 13
cells G4 solved 45–50/50 with medians 8.7k–28.7k. A hand-set BE grammar and a hand-set PA
grammar showed a crossed family preference: matched over swapped 1.68× [1.39, 2.05] on BE,
1.32× [1.12, 1.57] on PA. Context strengthens it relative to the tied-marginal controls (paired
contrasts 1.51×, 1.46×, lower bounds 1.09, 1.16); the marginal contrasts alone are unresolved
(BE [0.90, 1.36], PA [0.76, 1.10]). Only the BE grammar had a resolved own-family gain over G4;
for the PA grammar no gain was resolved (0.87× [0.75, 1.04], admitting gains up to about 4%). This is a positive witness for a decoder class, not learned
evidence. The symmetric matched/mismatched test cannot run on this bank under the frozen
rules.
Run 2026-10-06-0811 ([13](13-post-addition-map-learning/question.md), commit `0709104`, row 4):
from the six saved M maps, 12 matched pairs × 35 generations compared R (token steps plus
whole-row contextual residuals) with M+ (token steps only). R / M+ on fresh training 1.00×
[0.90, 1.11] (a gain above 1.11× excluded); on the two holdouts 1.16× [0.91, 1.48] and 1.06×
[0.83, 1.31], unresolved because the between-start spread is about twice the planned one.
Continued token learning still helped (M+ / M 1.45× on training). Frozen M was faster than G
on the two branch-else cells (2.23× [1.66, 3.06]), with a point estimate similar to the PA
holdouts (2.25×, 2.06×; lower bounds 1.81, 1.60; separate estimates, not an equivalence test),
and unresolved on linear cells, so its benefit is not confined to PA on the cells scored; a PA
preference is not ruled out. An unregistered six-map pattern, R faster than M+ on branch-else
(1.33× [1.05, 1.66], 5/6 starts) and slower on linear (0.65× [0.44, 0.88]), was the only hint of
learned context tied to the training shape; run 1425 (below) did not replicate it. Operator acceptance was near 25% for every
operator; these counts do not establish how well selection ranks individual steps.

Run 2026-10-06-1425 ([14](14-saved-map-shape-shift/question.md), commit `b397f72`, row 3;
approved twice before as runs 1400 and 1419, both blocked by a merge conflict): 55 saved maps on
the eight frozen off-family cells, 200 fresh seeds each. On the six unscored "b" continuations
R / M+ was 0.94× [0.77, 1.16] on branch-else and 1.29× [0.88, 1.91] on linear; the shift was
0.73× [0.57, 0.94], opposite to "a" in 6/6 starts. The "a" maps repeat their pattern on the
fresh seeds (shift 1.86× [1.41, 2.44]); a consistently positive learner-level shift was not
demonstrated (two continuations of six shared starts disagree in sign). On "b", a G-context
token-only map matched to R's pooled emitted token frequencies was not resolved from R; R's
advantage is bounded to about 1.17× (BE) and 1.12× (shift). Both learners, in both
letters, were faster than their M start on BE (lower bounds 1.05–1.10×). Six shared M starts
only.

Run 2026-10-06-0132 ([13](13-post-addition-map-learning/question.md), commit `02cf76f`): on the
one-family post-addition split (six training, two withheld cells on D1331), 23 learned token
multipliers on G's rows (M, 6 trajectories × 25 generations) sped fresh search 2.2× over frozen G
on training and 2.0× / 1.7× on the two holdouts (95% lower bounds 1.47, 1.26; 6/6 trajectories).
The full contextual learner (C, 552 weights, three-coordinate mutations) drifted modestly but
showed no resolved training gain (0.92× [0.78, 1.09]). A frequency-only learner (T) beat its
context-free start 1.7–2.1× but stayed 1.8–2.4× slower than G. Family specificity and mechanism
are unmeasured; the bank was screened, so this is fresh-seed transfer on a screened bank, not an
untouched benchmark.

Earlier: two feasibility studies. Run 2026-10-05-2247 ([11](11-composition-bank/question.md)):
the 3×3 reducer/combiner bank failed its split and headroom requirements (no eligible split at
524 288 evaluations — Sm-SEL 27/50 under uniform, SM-SEL an exact alias — and all four structural
splits failed the 4 096-evaluation headroom rule under the hand-set previous-token grammar G,
held-out medians 768–4 096). Run 2026-10-06-0001 ([12](12-generic-grammar-headroom/question.md))
failed the two-family requirement but kept a usable one-family post-addition split: ten-token
cells leave room above G (post-addition and branch-else medians 8 192–41 728), yet none of six
same-primitive shapes gave two families with ≥ 4 non-aliased cells each. Across both banks G beats
its own context-free marginals (G-marg) 2.6–19.5× (KM median, 2247) and 1.5–6.0× (paired capped
time, 0001; 15/16 intervals exclude 1). Root 01 earlier showed useful transfer of fitted token
frequencies between constant thresholds, with a hand-set scaffold performing comparably. See the
[plan](../../plans/compositional-map-transfer.md),
[family addendum](../../plans/compositional-family-headroom.md),
[one-family plan](../../plans/post-addition-map-adaptation.md) and
[opening strategy](../../runs/2026-10-05-2039/strategy.md).

Competing explanations:
- A: Experience across training tasks selects reusable assembly preferences. The adapted
  decoder improves held-out search beyond a fitted independent-token map and simple fixed
  assembly controls, with an advantage tied to the training family.
- B: More useful tokens or generic well-formed programs explain the gain. An independent
  token bias or task-agnostic assembly rule performs comparably.
- C: The decoder specializes to training programs. Training improves but transfer fails
  when programs are reset or operation combinations are withheld.
- D: Held-out solvers become more frequent, but that distributional gain does not improve
  evolutionary search at the tested budget, or decoder changes damage useful local moves.
- E: The proposed tasks or adaptation loop are not tractable at the measured budget.
  This is a feasibility result about this design, not a negative answer to A.

Sub-questions: [11-composition-bank](11-composition-bank/question.md) (closed: this bank
fails on tractability at 524k and on the 4 096 headroom rule against G; run 2026-10-05-2247),
[12-generic-grammar-headroom](12-generic-grammar-headroom/question.md) (closed: ten-token
branch cells leave headroom above G, but no same-primitive family pair survives the alias
screen; run 2026-10-06-0001).
[13-post-addition-map-learning](13-post-addition-map-learning/question.md) (closed, 2 of 2
slots: G-based token multipliers transfer about 2× to the withheld pair and to branch-else;
contextual row moves on top add no resolved training gain (R / M+ 1.00× [0.90, 1.11]), holdout
increment unresolved; runs
2026-10-06-0132 and 2026-10-06-0811).
[14-saved-map-shape-shift](14-saved-map-shape-shift/question.md) (closed, 1 of 1 slot, run
2026-10-06-1425, row 3: 0811's branch-versus-linear shift of R over M+ did not replicate on
the "b" continuations (shift 0.73× [0.57, 0.94]); on those maps a frequency-matched token-only
control was not resolved from R, shift 1.02× [0.92, 1.12]).
[15-four-reducer-family-bank](15-four-reducer-family-bank/question.md) (closed, 1 of 1 slot, run
2026-10-06-1603, row 1: with FIRST added, branch-else has no role-covered holdout pair on three
domains; PA splits; G4 tractable with headroom on all 13 cells; hand-set family grammars give a
crossed preference that context strengthens over the marginal controls, descriptive only; a
conservative learner-pilot projection excluded stage C, whose runtime was not measured there).
[16-crossed-family-adaptation](16-crossed-family-adaptation/question.md) (closed, 2 of 3
slots, runs 2026-10-06-1723 and 2026-10-06-2229: crossed BE/PA token-multiplier learning on the
1603 bank with one BE and two PA holdouts; both families learn about 2.2× on training, mostly
generically; on the holdouts every arm beats G4 2–3× and the matched-family advantage is 1.02×
(BE) and 0.96× (PA), 95% upper bounds 1.2485× and 1.15×, a 1.1× preference not excluded).
[17-decoder-initialization-variation](17-decoder-initialization-variation/question.md)
(closed, 2 of 2 slots, runs 2026-10-06-2331 row 3 and 2026-10-07-0315 row 1: both the learned
starting programs and the learned decoder during search help, about 1.3× given the other on the
withheld and the training cells, strongly sub-additive; on the training cells the start weighs
relatively more on BE than on PA cells, C −0.45 log2 [−0.68, −0.22], not separated from shape or
difficulty).

Related: [core question](../../../README.md#core-question),
[01-map-bias](../01-map-bias/question.md),
[08-evolve-bias](../01-map-bias/08-evolve-bias/question.md),
[09-generic-bias-speedup](../01-map-bias/09-generic-bias-speedup/question.md),
[run 0811 decision](../../runs/2026-10-06-0811/decision.md),
[run 1603 decision](../../runs/2026-10-06-1603/decision.md),
[run 1723 decision](../../runs/2026-10-06-1723/decision.md),
[run 0315 decision](../../runs/2026-10-07-0315/decision.md),
[digest](../../digest.md), [chem-tape findings](../../../docs/chem-tape/findings.md).

Review after the feasibility experiment and after the four allocated experiments. A
failed task candidate should prompt a bounded redesign, not an automatic stop of the
program. An unresolved transfer effect should be sized against measured runtime before
deciding whether another allocation could settle it.

Reopen if parked: a tractable task suite supplies the missing compositional contrast, a
decoder with demonstrably better training/search feasibility becomes available, or new
evidence defeats the specific generic-bias or overfitting explanation that caused parking.
