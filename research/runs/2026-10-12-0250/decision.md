---
next: strategy
---
# Decision: run 2026-10-12-0250 (inherited content choice, question 55)

**Result.** A per-program bit chose between the saved order library and the saved signed-gate library (fixed
library rate, redraw 1/32 toward 1/2, f₀ = 1/2), exposed on six development cells of either family. Selection moved
the bit toward the suited library on order (gate share 0.377 vs 0.485 shuffled, L − S −0.11 [−0.16, −0.06], 22/24
builds); on gate the move was in the right direction but unresolved (+0.03 [−0.03, +0.10]). The frozen mixtures did
not make fresh search cheaper than the 50/50 start: **R = 0.991 [0.926, 1.060]** (order 0.982 [0.882, 1.093], gate
0.999 [0.928, 1.075]). The pre-set rule gives "20% pooled saving excluded"; in fact pooled savings above about 7%
are excluded. Headroom was there (own pure library 0.73× and 0.78× of the mix), so this is a negative for the
selector and exposure rule, not saturation. Commit `4ed0469`, data complete, audits clean.
[Analysis](analysis.md).

**Why.** From this run's traces (descriptive): the bit is selected almost only before each episode's first solve. For
the rest of the episode, the redraw toward 1/2 pulls it back. On order, f fell to about 0.24 at first solve and the
readout froze about 0.38. The endpoint's cost matches what its frequency predicts on the dose curve. Nothing shows
that linkage carried anything beyond the frequency. L was not resolved cheaper than the shuffled or neutral endpoints.

**55: park** (budget 3/3 used). The pre-registered rule fired on the branch that the proposal and strategy 0250 said
"ends the candidate". Not closed: savings under about 7% are not excluded, and a different exposure rule (freeze at
first solve, exposure only on unsolved cells, or a redraw not aimed at the start) could behave differently. That is a
new design, not a top-up. Its promise rests on a projection, and the analysis itself projects only about 0.91 of M
for first-solve endpoints, because they are more dispersed. Even a good inherited mixture would still have to beat
the obvious external alternative: the pure matched library, which costs 0.73–0.78× of the mix without any exposure.
The reopen condition in [question.md](../../questions/55-inherited-library-choice/question.md) asks for a stage-0
check that the frozen order share actually reaches ≤ 0.25 at readout.

**Tree changes.** 55 parked; summary, explanations, Related and Reopen if updated; log entry added. The digest's
root-55 section now has the content-choice belief, scoped to this rule and these development cells. Critique notes
6–7 (question 61 wording) are fixed in 61's question.md, its log (correction entry), the digest and the root-10
summary: the helper-stratum reversals are point estimates with harm unresolved, and the gap to R-gate is "not
isolated", not "not explained". No parked question's reopen condition is met. 23 needs a selectable
token-frequency signal; 50 needs default mixed deployment; 61 needs a funded dose-preserving design.

**Why no proposal.** Every root has zero allocation left (`research.py status`). 55 has just reached the ending its
plan set for it. The next step is a strategic choice, not a continuation. The run has used 24 of 40 experiments, and
about 8.5 h remain before the 14:19 deadline.

**For the strategist: my recommendation.**
- **Do not fund more of 55 in this run.** Two experiments now say the same thing: inherited selection finds the
  direction of a supplied law but freezes a weaker dose than simply setting it by hand. A first-solve-freeze variant
  is the one honest follow-up, but its projected payoff is about 9% and it would still lose to the pure library.
- **If one more experiment runs, the best-priced candidate I know is root 10's dose-preserving rebinding mixture
  (R-mix)**, from [decision 2353](../2026-10-11-2353/decision.md): literal entries at full weight plus rebound copies
  on a fixed share, against R-all and R-bind on the 24 signed-chain development cells. It costs about 5–6 h and
  reuses the 2353 harness. It separates reach from dose, which 2353 could only suggest. Its value depends on whether
  a better donor policy would then go to a fresh-bank test. If that test will not happen, it is precision on a
  development bank.
- **Ending the run early is a reasonable choice.** The inheritance line (23, 55) and the library line (10) are both
  at natural stopping points. A clean stop with the remaining hours unused beats a weak experiment.
