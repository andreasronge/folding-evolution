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

## 2026-10-06: strategy 0811, contextual continuation (13, last slot)

Strategy 0811 asked for 13's last slot to compare learning contextual changes on top of the
saved M maps against continuing token-only learning for the same budget, plus a frozen-M
off-family check. Proposal: R (row residuals) vs M+ (token steps), 12 matched pairs × 35
generations ([proposal](../../runs/2026-10-06-0811/proposal.md)); critic approve_with_notes.

## 2026-10-06: run 2026-10-06-0811, result (13)

Result: outcome row 4, unresolved, on complete data (commit `0709104`, 12/12 pairs). R / M+:
training 1.00× [0.90, 1.11]; holdouts 1.16× [0.91, 1.48] and 1.06× [0.83, 1.31]. M+ / M 1.45×
on training. Frozen M / G: holdouts 2.25× [1.81, 2.81] and 2.06× [1.60, 2.63] on 200 new seeds;
branch-else 2.23× [1.66, 3.06]; linear 1.08× [0.72, 1.57]. Unregistered: R / M+ 1.33× on
branch-else, 0.65× on linear (six maps). Operators accepted at the chance rate. Details in
[13's log](13-post-addition-map-learning/log.md).

Decision: close 13 and return to strategy with root 10's last slot (4 of 5 used), because 13's
question is answered for the learner that moved, the R / M+ holdout increment would need about
20 independent starts to resolve at the observed spread, and strategy 0811 reserved the last
slot's use (replication, second family or mechanism) for the strategist. The root's answer so
far: a learned decoder change transfers about 2× to withheld compositions and to the related
branch-else shape, but every resolved gain is token-weight retuning of a hand-supplied context;
learned context beyond that is bounded below 1.11× on training and unresolved on the holdouts.

## 2026-10-06: correction to the 0811 decision (critique 1400, digest check)

"Every resolved gain is token-weight retuning of a hand-supplied context" overstates attribution.
It should read: token-only adaptation has demonstrated gains; an additional contribution from
learned residuals has not been established in the planned PA comparisons (R / M+ training 1.00×
[0.90, 1.11], holdouts unresolved; R / R_abl unresolved; an exploratory branch-else R / M+ 1.33×
[1.05, 1.66] on six maps). "M was as much faster on branch-else as on PA" means similar point
estimates (about 2.2×), not an equivalence result.

## 2026-10-06: strategy 1400 and run 2026-10-06-1400 (14), blocked before running

Strategy 1400 raised root 10's budget from 5 to 7: one slot for the saved-map shape-shift check
(new sub-question [14](14-saved-map-shape-shift/question.md)), then a four-reducer two-family
feasibility study, then (if feasible) a matched/mismatched family comparison. Proposal: score the
"b" continuations (with "a", G and M1–M6 as references) on the eight frozen off-family cells, with
R_abl and a frequency-matched token-only control R_fm, 88 000 searches, ≈ 1 h at 10 workers
([proposal](../../runs/2026-10-06-1400/proposal.md)); critic approve_with_notes, auto-approved.

Result: none. The driver stopped at prepare because merging main into research/main conflicts
(add/add on `research/runs/2026-10-06-0811/code_review.md`: main holds the second-pass `pass`
review, research/main the first-pass `fail` review). No code was written and no slot was used.

Decision: keep 14 open and re-propose the same check as run 1419 with the critic's notes folded
in, because nothing was learned, the design was approved, and the conflict is a one-file
bookkeeping fix (keep main's second-pass review), not a design problem. Root 10 stays at 4 of 7.

## 2026-10-06: run 2026-10-06-1419 (14), blocked again before running

Same check as 1400 with that critic's notes applied; critic approve_with_notes, auto-approved.
Result: none. The driver again stopped at prepare on the same add/add conflict
(`research/runs/2026-10-06-0811/code_review.md`). The steward committed main's second-pass
review onto research/main (`e37c4a7`, plumbing only, no working tree touched); main now merges
into research/main cleanly (`git merge-tree`).

Decision: re-propose 14's check as run 1425 with the 1419 critic's two interpretation notes
applied, because the design has been approved twice, no belief changed, and the only blocker is
gone. Root 10 stays at 4 of 7; the slot after 14 still goes to the four-reducer feasibility study.

## 2026-10-06: run 2026-10-06-1425 (14), saved-map shape shift — ran; row 3

The 1400/1419 design ran unchanged (commit `b397f72`, 88 000 searches, 48 min, complete; gate
passed). On the six "b" continuations R / M+: BE 0.94× [0.77, 1.16], LIN 1.29× [0.88, 1.91],
shift 0.73× [0.57, 0.94] (below 1 in 6/6 starts). The "a" maps repeat 0811 on 200 fresh seeds
(shift 1.86× [1.41, 2.44]). "b"-only R / R_fm shift 1.02× [0.92, 1.12]; the pooled D-a (1.23×
[1.11, 1.36]) is carried by the selected "a" maps. Both learners faster than M on BE in both
letters ([analysis](../../runs/2026-10-06-1425/analysis.md)).

Decision: close 14, because row 3 answers it: the branch/linear shift differs in sign between two
learning runs from the same starts, so it is not a reproducible property of the contextual
learner, and on the unselected maps R's pooled token frequencies on G's context reproduce it.
Context gets at most a secondary arm in the two-family study; the token learner is the primary
one. Root 10 is at 5 of 7. Return to strategy before the four-reducer feasibility slot, as
strategy 1400 asked.

## 2026-10-06: runs 2026-10-06-1536 / 1603 (15), four-reducer FIRST bank — ran; row 1

Strategy 1536 gave slot 6 to the four-reducer feasibility study and opened
[15](15-four-reducer-family-bank/question.md). The 1536 proposal was sent back because it read a
missing hand-set grammar contrast as decoder incapacity. The revision (1603) made that contrast a
descriptive positive witness, and the critic approved it with notes. The run (commit `92ba7c5`,
43.7 min, complete) reproduced the probe's screen exactly. On D1331, 13 of 36 cells survive
(BE 5, PA 8). **BE has no role-covered holdout pair on any of the three domains.** PA splits
(2 holdouts, 6 training). G4 solves 45–50/50 on every cell, with medians 8.7k–28.7k, above the
4 096 line. Hand-set family grammars show a crossed preference: matched over swapped is 1.68×
[1.39, 2.05] on BE and 1.32× [1.12, 1.57] on PA. That preference sits in context rather than
marginals (paired contrasts 1.51× [1.09, 2.09], 1.46× [1.16, 1.82]). The PA grammar does not
beat G4 on PA (0.87× [0.75, 1.04]). A 4-trajectory token-learner pilot on this bank projects to
2.4–4.7 h, so stage C could not have run in this queue
([analysis](../../runs/2026-10-06-1603/analysis.md)).

Decision: close 15 and return to strategy, because the frozen split rule rejects this candidate.
Root 10 now has 6 of 7 slots used. Its last slot (the matched/mismatched comparison) has no
symmetric bank to run on. Only strategy can approve an asymmetric design, a new candidate, or a
reallocation. Correction to the 1425 entry above (critique 1603 note 7): "reproduce it" should
read "was not resolved from it" (R's advantage bounded to about 1.17× on BE, 1.12× on the shift).
