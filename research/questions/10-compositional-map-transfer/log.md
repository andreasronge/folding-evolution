# Log

## 2026-10-05: opened by strategy (run 2026-10-05-2039)

Opened with 4 experiments; first is feasibility in
[11-composition-bank](11-composition-bank/question.md).

## 2026-10-05: run 2026-10-05-2039, bank feasibility (blocked, not run)

Experiment: the 11 feasibility study ([proposal](../../runs/2026-10-05-2039/proposal.md)).
Result: none; the cycle stopped at `prepare` on a `main` → `research/main` merge conflict
(`research/runs/2026-10-05-1957/code_review.md`). No slot charged.

Decision: continue root 10 through 11, re-proposing the same feasibility study with the
critic's notes ([run 2026-10-05-2242](../../runs/2026-10-05-2242/proposal.md)), because no
evidence changed and the block was operational.

## 2026-10-05: run 2026-10-05-2242, bank feasibility, second attempt (blocked, not run)

Experiment: the 11 feasibility study again ([proposal](../../runs/2026-10-05-2242/proposal.md)).
Result: none; the same merge conflict stopped it at `prepare`. The steward resolved it on
`research/main` (merge `823bc27`, taking `main`'s second-pass review of run 1957). No slot charged.

Decision: continue root 10 through 11 ([run 2026-10-05-2247](../../runs/2026-10-05-2247/proposal.md)),
because no evidence changed and the operational block is gone.

## 2026-10-06: run 2026-10-06-0001, assembly-family probes and proposal (12)

Strategy 0001 raised root 10 to 5 experiments and sent it through 12 with the assembly-family
plan. Steward probes (unreviewed, one run each, `0995d33` in /tmp): an exhaustive ≤ 9-token alias
screen kills all gate cells (`(A+B)>0 ? C : D` ≈ `S>0 ? C : D`, 80–90%) and all branch-then cells
(exact identities via the zero default or DUP of the condition, plus sign-correlation near-aliases)
on 625, 1 331 and 2 401 inputs; post-addition `(S>0 ? X : Y) + Z` keeps 4/18 (625) to 8/18 (wider
domains); branch-else 2/9. Ten-token cells sit well above the 4 096 line under G (medians 7–34k).

Decision: propose a widened, frozen alias screen + 10-token search calibration + gated
family-grammar diagnostic ([proposal](../../runs/2026-10-06-0001/proposal.md)), because the
plan's pair fails semantics and the strategist needs measured 10-token costs for any redesign;
probes predict its row 1.

## 2026-10-06: run 2026-10-06-0001, result (12)

Result: outcome row 1 on complete data (commit `a65ded0`). 162 ten-token canonicals in six
shapes, three domains: gate and branch-then 0 retained everywhere, branch-else ≤ 2, post-addition
4–8, linear 3 + 3; 0 eligible pairs, insensitive to the alias cutoff over 0.70–0.85. On D1331's
16 retained cells (50 paired seeds): G medians 8 192–41 728 on the ten branch cells (2–10× the
4 096 line), F and G-marg above the line everywhere; G/U 8.4–11.3×, G/G-marg 1.5–6.0×. Details in
[12's log](12-generic-grammar-headroom/log.md).

Decision: close 12 and return to strategy because row 1 and strategy 0001 both send a second
bank failure there; root 10 has 3 of 5 slots left, and whether to use a one-family post-addition
split, another contrast or an alphabet change is a program-level choice.

## 2026-10-06: strategy 0132, one-family learning (13)

Strategy 0132 chose the one-family post-addition route
([plan](../../plans/post-addition-map-adaptation.md)) and asked for a new child. Opened
[13-post-addition-map-learning](13-post-addition-map-learning/question.md) (budget 2). Steward
probes (unreviewed): G is a repeatable training start (13.75 / 13.94 mean log2 cost at 65k),
random perturbations mostly hurt, a hand-set PA grammar does not beat G, inner runs 0.65–1.2 s.

Decision: propose three learners (contextual C, G × token multipliers M, token-only T) × 6
independent outer-loop trajectories, evaluated on fresh training seeds and both holdouts, with a
stage-0 runtime gate ([proposal](../../runs/2026-10-06-0132/proposal.md)), because this is the
first test of learned transfer the root has been unable to run and the probes show it fits in
one ≤ 8 h queue.

## 2026-10-06: run 2026-10-06-0132, result (13)

Result: outcome row 1 on complete data (commit `02cf76f`). Contextual learner C: no practical
training gain over G (0.92× [0.78, 1.09]), flat curves. G-based token multipliers M: 2.23× faster
than G on fresh training, 2.01× [1.47, 2.81] and 1.71× [1.26, 2.32] on the two withheld
compositions, 6/6 trajectories. Token-only T: 1.7–2.1× over G-marg, 0.41–0.57× of G. Details in
[13's log](13-post-addition-map-learning/log.md).

Decision: return to strategy with 2 of 5 root slots left, because row 1 and strategy 0132 both
send the first adaptive result there. The root now has a positive held-out result for a learned
token-weight change on a supplied contextual template, but not for learned context; the next
slot should go to whichever of (a) a contextual learner that can move, (b) a generic-vs-PA check
of M's change, or (c) a supply/mutation split the strategist judges most decisive.
