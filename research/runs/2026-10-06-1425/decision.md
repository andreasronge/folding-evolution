---
next: strategy
---
# Decision: run 2026-10-06-1425 (14, saved-map shape shift) — row 3; close 14, return to strategy

**Close [14](../../questions/10-compositional-map-transfer/14-saved-map-shape-shift/question.md).
No proposal; `next: strategy`.**

What happened ([analysis](analysis.md)): the design approved in 1400/1419 ran unchanged and
completely (commit `b397f72`, 88 000 searches, 48 min, gate passed, 12/12 frequency-matched
controls). Outcome **row 3**. On the six "b" continuations R / M+ was 0.94× [0.77, 1.16] on
branch-else, 1.29× [0.88, 1.91] on linear, and the shift 0.73× [0.57, 0.94], opposite to "a"
in 6/6 starts. The "a" maps keep their 0811 pattern on the fresh seeds (shift 1.86× [1.41,
2.44]). On "b", R_fm (G's context, R's pooled emitted token frequencies) reproduces R (shift
1.02× [0.92, 1.12]).

Why close: row 3 answers the question at its stated bounds. The shift is a property of
individual learning runs, not of the contextual learner: two sets of runs from the same six
starts disagree in sign. On the unselected maps nothing in R's off-family behaviour needs its
residuals beyond pooled token frequencies (bounded at about 1.17× BE, 1.12× shift). More seeds
cannot change this (seed SE ≤ 0.08 log2 against ±1 log2 start-to-start spread); only new
independent starts could, and that is the reopen condition.

What it changes: per the pre-stated rule, token-only adaptation stays root 10's demonstrated
gain and context gets at most a secondary arm (with an R_fm-style control) in the two-family
study. Side result worth carrying: continued post-addition learning made both learners faster
on branch-else than their M start (lower bounds 1.05–1.10×), so generic carry-over to related
shapes is the baseline any family-specificity claim must beat.

Why strategy and not a proposal: strategy 1400 asked to "return to strategy after the next
result and after feasibility", and the proposal promised the same. Root 10 has 2 of 7 slots
left, both planned for the [four-reducer study](../../plans/four-reducer-family-transfer.md)
(feasibility, then the matched/mismatched comparison). My recommendation to the strategist is
to keep that plan and size the feasibility slot as the plan describes; this result removes the
case for a full contextual arm, which should simplify and cheapen the later comparison
(token learner plus fixed and marginal controls, context optional). No other open question
deserves the slot ahead of it.

Parked questions: none reopens. 08/09 (root 01, budget spent) need a no-lift speed-up in
another family or a heritable-bias design; 02/04/07 concern supply, discovery and helper
arrival. This run touches none of those conditions.

Digest check (critique §5): no problems listed; nothing to fix.

Updated: 14's question.md (closed, summary, reopen) and log; root 10's question.md (summary,
5 of 7, sub-question line) and log; digest (header, the 0811 "hint" bullet marked as not
replicated, new section "Saved-map shape shift", open-questions entries).
