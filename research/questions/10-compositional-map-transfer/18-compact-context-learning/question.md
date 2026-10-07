---
status: closed
tags: [compositional-transfer, decoder, contextual-learning, rank-one, selection-noise, token-multipliers, fresh-start]
budget: {experiments: 2, used: 0}
---
# Can selection learn a compact context change that speeds fresh training search beyond equally funded token tuning?

Current summary: **closed at its tested scope after run 2026-10-07-1137 (question 19, row 6),
which met this question's reopen condition. In a loop where token-only continuation from the
saved 1723 maps demonstrably learned (96 searches per candidate, 9 600 searches per arm; T/S
1.143× [1.089, 1.200] on one fresh block, 1.122× [1.031, 1.222] on another), adding rank-one
context steps under equal search funding gave no resolved increment: C/T 0.967× [0.871, 1.073],
so a mean gain above about 1.07× is excluded for this representation, these starts and this
loop; a small gain or loss is not.** C gave up half its token steps to context steps, and its
token component was slower in the point estimate (C0/T 0.932× [0.860, 1.010], unresolved, not pre-stated), so A
below is not shown, and B (steps too small to select) and C (gains small or cancelled by the
token learning given up) are not separated. Context learned jointly from G4
(D) and context added on top of a full token budget remain untested.

Earlier, run 2026-10-07-0821 (row 3): at 24 searches per child and 4 040 searches per arm, C/T
0.955× [0.833, 1.095], but token continuation did not resolve learning either (T/S 1.03× [0.90,
1.16]; C/S 0.98× [0.90, 1.07]), so that null could not tell ineffective context from a loop with
no resolved progress. Single context steps do have repeatable effects (stage A: true
step-effect variance 0.047 [0.027, 0.065] log2², comparable to the token steps' 0.028
[0.005, 0.051]), and ranking 24
mutants by 48 searches picks ones better than the average mutant on new seeds. The selected
picks' difference from their parent was unresolved (−0.017 [−0.085, +0.041] log2); the average
step was harmful. In the loop, parents turned over 1.4 times per generation with no resolved net movement
in either arm. The per-search learning rate allowed by T/S's upper bound (≈ 5.4 × 10⁻⁵ log2) still
includes 0811's token continuation rate (≈ 4.0 × 10⁻⁵, other bank), so a 3× longer run might
move; the reviewer's alternative reading, that per-child noise (0.33 log2) swamps step effects
(sd 0.17–0.22), is an interpretation, not a measured contrast. Descriptively, PA's learned
residuals look slightly harmful (C/C0 0.91× [0.85, 0.98] on 8 PA pairs; pooled 0.96× [0.90,
1.02]; removing the residual also shifts emitted token frequencies). Final residuals had small
absolute cosine alignment with the hand-set BE − PA direction (≤ 0.105; ≤ 0.045 in run 1137).

Before run 0821 (steward probe on 1723's logs): a 24-search candidate score has noise sd ≈ 0.34
log2; token steps' true-effect variance was 0.075–0.086 early in learning and 0.025–0.037 later;
a rank-one residual can represent 55% / 64% of the BE / PA hand-set context relative to G4 and
93% of their BE − PA contrast. Earlier contextual procedures: 0132 (0.92× [0.78, 1.09]) and
0811 (R/M+ 1.00× [0.90, 1.11]) also found no resolved gain beyond token learning.

Competing explanations:
- A: Compact context changes have selectable effects, and selection accumulates them into a
  fresh-training gain beyond equally funded token tuning.
- B: Single compact context steps have too little effect on search cost to be selected at an
  affordable scoring effort (a selection-signal limit, not absence of useful context).
- C: Context steps are selectable but their gains are small or are cancelled by the token
  learning the contextual arm gives up under equal funding.
- D: Useful context exists only jointly with token learning from G4, or in directions that a
  rank-one residual with random starting row factors cannot reach. A null here would not
  test this explanation.
- E (added after 0821): the 2 + 6 loop at 24 searches per child makes no measurable progress from
  these token-tuned starts for any operator, so a C/T contrast at this budget cannot separate A
  from B or C. Consistent with T/S and C/S both unresolved and flat in-loop slopes (each arm's
  drift bounded to about ±1.15× over the run); not isolated.

Status by explanation (0821): A not shown (C/T upper 1.095); B only partly addressed: initial b-steps
have repeatable effects and can be ranked against other mutants at 48 searches, but the selected
quarter was not shown to beat its parent, and later steps were not calibrated; C and E not separated; D untested.
Status after 1137: E no longer limits the test: a loop at 96 searches per candidate does make
token progress (T/S resolved > 1 on two seed blocks), so C/T is informative there (0821's
24-search loop was not re-tested; T96/T24 1.114× [0.987, 1.257] is unresolved); A not shown (C/T upper 1.073); B and C not separated (observed survival into the
parent set: context steps 0.22–0.23, token steps 0.23–0.25; C's token component slower in the point estimate, C0/T 0.932× [0.860, 1.010], unresolved);
D untested.

Scope: the ten 1723 training cells (4 BE, 6 PA) of the frozen 1603 bank, D1331,
`v2_rmin_first`, G4, saved 1723 token maps as starting points. The three withheld cells are
not touched in this question's first experiment.

Related: [root 10](../question.md), [concept plan](../../../plans/learnable-context.md),
[strategy 0803](../../../runs/2026-10-07-0803/strategy.md),
[13 post-addition learning (0811 R vs M+)](../13-post-addition-map-learning/question.md),
[15 hand-set family grammars](../15-four-reducer-family-bank/question.md),
[16 crossed token learning](../16-crossed-family-adaptation/question.md),
[run 1723 analysis](../../../runs/2026-10-06-1723/analysis.md),
[run 0821 analysis](../../../runs/2026-10-07-0821/analysis.md),
[run 0821 decision](../../../runs/2026-10-07-0821/decision.md),
[19 selection-calibrated continuation](../19-selection-calibrated-continuation/question.md),
[run 1137 analysis](../../../runs/2026-10-07-1137/analysis.md).

Reopen if: a context design that does not take steps away from token learning (context
added on top of a full token budget, or after token learning flattens) or one learned jointly
from G4 is funded; or a different compact context representation shows a measured selectable
signal. Size any follow-up with 1137's C/T pair sd (interval half-width about 0.15 log2 at
8 + 8 starts) and note that per-start gains are not measurable at 50 fresh seeds.
