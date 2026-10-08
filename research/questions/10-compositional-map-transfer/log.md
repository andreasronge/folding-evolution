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

## 2026-10-06: runs 2026-10-06-1723 (16), crossed BE/PA token learning, stage 1 — ran; row 4

Strategy 1723 raised root 10 to 9 slots, opened [16](16-crossed-family-adaptation/question.md)
and authorized the narrower split (BE holds out `S?m:(M+F)`, PA holds out `(F?S:M)+m` and
`(S?M:m)+F`). Slot 7: 10 independent G4-based token-multiplier trajectories per family, 0132's
learner unchanged, fresh training scores on all ten training cells, no holdout searched (commit
`db96645`, 4.28 h, complete). Own-family gain over G4: BE 2.18× [1.98, 2.40], PA 2.27× [1.95,
2.65]. Off-family training cells 2.07× [1.94, 2.21] and 1.93× [1.61, 2.30]. Matched over
mismatched in-sample: 1.13× [0.93, 1.37] (BE cells), 1.10× [0.93, 1.29] (PA cells), both X; post
hoc within-map interaction 1.24× [1.09, 1.41]. Size rule: n = 10 per family suffices
([analysis](../../runs/2026-10-06-1723/analysis.md)).

Decision: continue with stage 2 in 16 (slot 8: holdout evaluation of the 20 frozen maps plus G4),
because row 4 routes there, the size rule needs no more trajectories, and only the withheld cells
can separate generic from family-dependent transfer. Slot 9 stays unspent for strategy after the
crossed result. Corrections to the 1603 entry above (critique 1723 notes 5–7): "The PA grammar
does not beat G4 on PA" should read "no PA improvement over G4 was resolved (0.87× [0.75, 1.04],
admitting gains up to about 4%)"; "sits in context rather than marginals" should read "context
strengthens the crossed preference relative to the tied-marginal controls; the marginal contrasts
alone are unresolved"; and "so stage C could not have run in this queue" should read "the frozen
2× allowance excluded stage C; actual learner runtime was not measured there" (run 1723 has now
measured it: 10–14 min per trajectory).

## 2026-10-06: run 2026-10-06-2229 (16), frozen crossed maps on the three holdouts, stage 2 — ran; row 4

Slot 8. The 20 frozen stage-1 maps and G4 on BE `S?m:(M+F)`, PA `(F?S:M)+m` and PA `(S?M:m)+F`,
400 shared fresh seeds each, 524k cap, no learning (commit `33fcee2`, 35 min, complete, G4 gate
passed). Gains over G4: all six arm × cell estimates resolved, 1.97×–2.93×. Matched over
mismatched: BE 1.02× [0.835, 1.2485], PA 0.96× [0.79, 1.15], both bounded below 1.25×, neither
resolved; interaction 0.98× [0.83, 1.15]. The BE bound is at the margin (leave-one-map-out
upper bounds 1.25–1.30) ([analysis](../../runs/2026-10-06-2229/analysis.md)).

Decision: close 16 and return to strategy, because the crossed question is answered at this
design's resolution (generic transfer about 2–3×, a matched-family advantage above about 1.25×
excluded on these three cells, a 1.1× one not), and a detection-sized rerun (about 64–75
trajectories per family, 14–30 h) would most likely only tighten a bound around 1. Root 10 has
one slot left; whether it buys a mechanism arm (union-trained or scrambled-family maps),
learned context, or a wrap-up is the strategist's call.

## 2026-10-07: run 2026-10-06-2331 (17), starting programs × ongoing decoder on the frozen maps — ran; row 3

Slot 9 (strategy 2331 raised the budget 9 → 10 and opened [17](17-decoder-initialization-variation/question.md)
with two slots). The 20 frozen 1723 maps (M) and G4 (G) on the three 2229 cells, 400 fresh seeds,
four arms (GG, MM, MG, GM) with generation-0 token tapes held identical between paired arms by
conditional-uniform re-encoding (commit `8f42f38`, 3.0 h, complete, every validation check
passed). Ongoing-decoder increment given M's start 1.39× [1.31, 1.47]; start increment given
ongoing M 1.30× [1.24, 1.36]; diagonal 2.29× [2.05, 2.54]; interaction −0.34 log2 [−0.40,
−0.29], negative in 20/20 maps. The larger component is the start on the BE cell and the ongoing
decoder on both PA cells (descriptive, one BE cell)
([analysis](../../runs/2026-10-06-2331/analysis.md)).

Decision: spend slot 10 on 17's slot 2 (the same frozen 2×2 on the ten training cells, testing
whether the start/ongoing balance tracks cell family), because the result is bounded (row 3) as
the strategy required, and the new per-cell pattern can only be tested with more cells; after it,
root 10's budget is spent and the program returns to strategy. Wording corrections to the 2229
entry above (critique 2331 notes 7–8; no numbers change): "both bounded below 1.25×" and "a
matched-family advantage above about 1.25× excluded" should read "95% upper bounds 1.2485× (BE,
roughly 1.3× leave-one-map-out) and 1.15× (PA)"; these are upper confidence bounds on the
advantage.

## 2026-10-07: run 2026-10-07-0315 (17), starting programs × ongoing decoder on the ten training cells — ran; row 1

Slot 10 of 10. The same frozen 2×2 as 2331 (20 frozen 1723 maps, G4; arms GG, MM, MG, GM with
generation-0 tapes held identical by re-encoding) on the 4 BE and 6 PA training cells, 200 fresh
seeds, 122 000 searches (commit `5dae3a6`, 4.27 h, complete, every validation check passed).
Ongoing-decoder increment given M's start 1.28× [1.22, 1.34]; start increment given ongoing M
1.33× [1.26, 1.40]; diagonal 2.44× [2.23, 2.66]; interaction −0.52 log2 [−0.62, −0.42].
Family balance C = mean S(BE) − mean S(PA) = −0.45 log2, Welch 95% [−0.68, −0.22]: the start
weighs relatively more on BE cells, the ongoing decoder on PA cells; both components resolved
positive within each family. S correlates with MM difficulty across cells (r 0.77, post hoc)
([analysis](../../runs/2026-10-07-0315/analysis.md)).

Decision: close 17 (answered at this design's resolution; see its log) and return the program to
strategy, because root 10's ten slots are spent. Root 10 stays open for the strategist: its
primary question (A versus B: does an adapted decoder help beyond a token-frequency bias, with an
advantage tied to the training family?) has a generic-transfer answer (about 2–3×) with no
resolved family advantage on the withheld cells, and a mechanism answer (both channels,
overlapping, task-dependent balance); learned context gave no resolved gain. Whether to close,
park or fund more is the strategist's call.

- 2026-10-07 (0803): strategy 0803 raised the budget 10 → 12 and asked whether selection can
  learn compact context beyond token tuning. Opened [18](18-compact-context-learning/question.md)
  (2 slots). Decision: propose run 0803, a calibration gate on rank-one context steps followed by
  16 paired context-versus-token continuations from saved 1723 maps, because the plan asks for
  training feasibility before any transfer test, and pairing within saved token-tuned starts
  measures "beyond token tuning" more cheaply than learning from G4 again.

- 2026-10-07 (0821): critic sent 0803 back (`revise`): a variance-only gate could stop useful
  learning and misdiagnose a selection-signal limit. Decision: propose run 0821, the same paired
  continuation with stage A kept as calibration and effort choice only (no stop), because the
  C-versus-T contrast is the direct test and low step variance does not bound selected gains.

- 2026-10-07 (0821): slot 11 of 12. Run 2026-10-07-0821 ([18](18-compact-context-learning/question.md),
  commit `f61aec4`, complete, 2.64 h, all validation passed, no holdout touched): 16 paired
  continuations (8 BE, 8 PA) from saved 1723 maps on the ten training cells, token-only T versus
  token-or-rank-one-context C, 4 040 searches per arm. C/T 0.955× [0.833, 1.095]; T/S 1.03×
  [0.90, 1.16]; C/S 0.98× [0.90, 1.07]; in-loop slopes flat in both arms. Row 3
  ([analysis](../../runs/2026-10-07-0821/analysis.md)).
  Decision: park 18 and return root 10 to strategy with one slot left, because the pre-registered
  row 3 says the null does not tell ineffective context from a loop with no resolved progress for
  either operator; making the token arm learn first needs a different, ~5–6 h loop, and whether
  that beats the other uses of the last slot (or closing the root) is the strategist's call.

- 2026-10-07 (1137): strategy 1137 raised the budget 12 → 13 and directed one bounded attempt to
  make token continuation from the saved maps learn before another context comparison. Opened
  [19-selection-calibrated-continuation](19-selection-calibrated-continuation/question.md)
  (2 slots); 18 stays parked until 19 meets its reopen condition. Proposal: run 2026-10-07-1137.

- 2026-10-07 (1137): slot 12 of 13. Run 2026-10-07-1137 ([19](19-selection-calibrated-continuation/question.md),
  commit `86ef669`, complete, 4.63 h, all validation passed, no holdout touched): from the 16
  saved 1723 maps, token-only continuation at 96 searches per candidate (9 600 searches per
  trajectory) learned: T/S 1.143× [1.089, 1.200] on 0821's fresh seeds, 1.122× [1.031, 1.222] on
  new seeds. In the same loop, mixing in rank-one context steps gave C/T 0.967× [0.871, 1.073].
  Row 6 ([analysis](../../runs/2026-10-07-1137/analysis.md)).
  Decision: close 19 and close 18 at its tested scope, and return root 10 to the strategist with
  one slot left, because the pre-registered context test has now run with a working token
  control and excludes a mean gain above about 1.07×; the remaining context designs (joint
  learning from G4; context that does not displace token steps) are different experiments that
  would need about 4–6 h of queue against about 5 h left before the 22:25 deadline, so whether
  to spend the last slot or close the root is a program-level call.

- 2026-10-07 (1707): strategy 1707 gave root 10's thirteenth slot to fitting decoder context
  directly from training-solver corpora (external fitting, not map evolution; no budget raised).
  Opened [20-solver-corpus-context](20-solver-corpus-context/question.md) (1 slot). Decision:
  propose run 2026-10-07-1707 (16 independent G4 solver corpora per family; contextual fit versus
  token-only fit and an emitted-marginal control on fresh training seeds, then all frozen fits on
  the three holdouts), because a steward probe showed corpora cost about a minute per family and
  the token fit alone already beats G4 about 2.5–3×, so the C-versus-T contrast can be sized to
  ±8% within about 1.3 h of queue.

- 2026-10-07 (1924): strategy 1924 raised the budget 13 → 14 for one feedback step. Opened
  [21-iterated-solver-corpus](21-iterated-solver-corpus/question.md) (1 slot); 20 stays closed.
  Decision: propose run 2026-10-07-1924. Each of the 32 saved 1707 tables C collects new training
  solvers and is refitted with the same frozen rule (C2). C2 is compared with C and with a one-shot
  refit to a fresh G4 corpus (C'), on training and then withheld cells. A steward probe found
  near-full yield under C, about 140 worker-s per lineage, and C2 ahead of C in 4/4 lineages. The
  comparison fits in about 75–85 min of queue.

- 2026-10-07 (1924): slot 14 of 14. Run 2026-10-07-1924 ([21](21-iterated-solver-corpus/question.md),
  commit `5565d54`, complete, 73 min, all validation passed): refitting each of the 32 saved 1707
  tables C to exact training solvers found under it (C2) gave C2/C 1.404× [1.347, 1.464] on
  training (32/32 lineages) and 1.289× [1.204, 1.381] on the withheld cells; against a fresh
  one-shot G4 refit C', C2/C' 1.408× and 1.330× (lower bounds 1.34, 1.26); C'/C 0.997× [0.940,
  1.058] and 0.969× [0.908, 1.035]. Row 1 with transfer on both holdout contrasts
  ([analysis](../../runs/2026-10-07-1924/analysis.md)). Applied critic 1924's digest-check fixes to
  this file and to 20 (unresolved T versus 1723 maps, overfitting not isolated, B not established
  for the selection learners nor excluded in its generic form).
  Decision: close 21 and return root 10 to the strategist (`next: strategy`), because the
  pre-stated rule is met with margin, root 10 has used 14 of 14 slots, and the open follow-ups
  (a second step, a token-only T2 refit from the same corpora to locate the increment, active-token
  fitting, a broader holdout bank) each need a new allocation.

## 2026-10-08 — digest condensing (run 2026-10-07-2243): former digest text moved here

The digest was rewritten as current beliefs only (word limit). This is the digest's run-by-run preamble and the root-10 open-question lines, moved verbatim as it stood before the rewrite; no belief changed. Relative links below are relative to `research/`, not to this folder.

As of 2026-10-08 (run 2026-10-07-2243 opened root 23 and stopped at its cost gate with no result; before it run 2026-10-07-2156, commit `36c665d`: token-only fits T1 and T2 scored on the exact seeds of the saved C1 and C2, completing the four-arm feedback crossing on training and withheld cells; its first attempt, run 2026-10-07-2129, stopped at preparation on the autonomous deadline with no result; before it run 2026-10-07-1924, commit `5565d54`: one feedback refit of the solver-corpus tables from solvers found under them, against the parent and a fresh one-shot refit, training and withheld cells; before it run 2026-10-07-1707, commit `627336d`: previous-token and token-only tables fitted directly to exact G4 solver tapes, training and withheld cells; before it run 2026-10-07-1137, commit `86ef669`: the same token-only versus rank-one-context continuation from the saved token maps, at 96 searches per candidate, training cells only; before it run 2026-10-07-0821, commit `f61aec4`: the same comparison at 24 searches per child; before that run 2026-10-07-0315, commit `5dae3a6`: the same starting-program × search-decoder crossing on the ten training cells; before that run 2026-10-06-2331, commit `8f42f38`: the frozen maps' starting programs crossed with the decoder used during search, on the three withheld cells; before that run 2026-10-06-2229, commit `33fcee2`: the frozen crossed BE/PA token maps scored on the three withheld cells, stage 2; before that run 2026-10-06-1723, `db96645`, crossed BE/PA token learning on the four-reducer bank, stage 1, training cells only; before that run 2026-10-06-1603, `92ba7c5`, the four-reducer FIRST bank feasibility study; before that run 2026-10-06-1425, `b397f72`, the saved-map shape-shift check, after runs 1400 and 1419 with the same design were blocked by a merge conflict; before it run 2026-10-06-0811, `0709104`, contextual moves versus continued token learning from the learned post-addition maps; before 0811 run 2026-10-06-0132, `02cf76f`, root 10's first decoder-learning study; run 2026-10-06-0001, `a65ded0`, and run 2026-10-05-2247, `0995d33`; runs 2026-10-05-1510, 2026-10-05-2039 and 2026-10-05-2242 were blocked before running). This covers the **map-bias line**, the current
core question since the 2026-09-25 reframe: *how does the genotype→program map bias what
evolution finds and keeps ("arrival of the frequent")?* Until 2026-10-05 the line studied
whether the chemistry can discover, preserve and reuse a **shared helper** (one functional part
read by several outputs); that line has stopped. The README's part 2, fitting the map's bias
to a task family ([08](questions/01-map-bias/08-evolve-bias/question.md),
[09](questions/01-map-bias/09-generic-bias-speedup/question.md)), gave a bounded answer and is
parked too; root 01's budget is spent (last slot: run 1957, stopped at its pilot). The strategist
opened root [10-compositional-map-transfer](questions/10-compositional-map-transfer/question.md)
to test part 2 on held-out operation combinations with an adaptable decoder. The first bank
failed its split/headroom requirements; the second failed the two-family requirement but kept a
usable one-family post-addition split (see "Composition bank" and "Assembly-family screen"
below). On that split, learned token multipliers on the hand-set grammar G transferred to the
two withheld compositions (about 2×) and to the related branch-else cells; allowing learned
contextual moves on top gave no resolved training gain (≤ 1.11×) and an unresolved holdout
increment, and their one off-family hint did not replicate (see "Decoder learning on
post-addition", "Contextual moves on top of M" and "Saved-map shape shift"). The four-reducer
bank meant to supply a second family fails the split rule for branch-else (see "Four-reducer
bank"). On that bank, with a narrower split authorized by strategy, the token learner improves
the four-reducer grammar G4 about 2.2× on both families' training cells and 2–3× on the three
withheld cells; which family the maps were trained on made no detectable difference on the
withheld cells (matched over mismatched 1.02× and 0.96×; 95% upper bounds 1.2485× on BE, rising to
about 1.3× in leave-one-map-out checks, and 1.15× on PA; a 1.1× preference is not excluded)
(see "Crossed family learning"). On those three cells and on the ten training cells, the maps' gain
comes both from the programs the search starts with and from using the map during search, each
about 1.3× given the other, and the two gains are strongly sub-additive; on the training cells
the start weighs relatively more on branch-else cells than on plus-arg cells (see "Starting
programs versus ongoing decoder"). A third contextual procedure (rank-one context steps mixed
into token continuation from the saved maps) first ran in a loop where token continuation did
not resolve learning (0821). With 4× more search evidence per candidate, token-only continuation
did learn (about 1.12–1.14× on two fresh seed blocks), and in that loop context under equal
search funding added no resolved increment (C/T 0.967× [0.871, 1.073]) (see "Compact context
continuation" and "Selection-calibrated continuation"). A different signal did work: a
previous-token table fitted directly to the token tapes of exact G4 solvers beat a token-only
fit to the same tapes about 1.37× on training cells and 1.29× on the withheld cells, over 32
independent corpora, with no resolved family advantage (see "Solver-corpus context fit"). One
feedback step added further search speed: refitting each table to exact solvers found under it
beat its parent about 1.40× on training and 1.29× on the withheld cells, while a fresh one-shot
refit was not resolved from the parent (see "Solver-corpus feedback refit"). On the training
cells that step also raised the fitted context's advantage over a token-only fit to the same
corpora, by about 1.17× and mostly on BE, while the token-only fit itself improved about 1.20×;
on the withheld cells that interaction is unresolved (see "Feedback context increment"). Root 10
has used all 15 of its slots.

## Open questions

- [10-compositional-map-transfer](questions/10-compositional-map-transfer/question.md) (open,
  root, budget 15, 15 used): can a decoder adapted across related tasks help fresh populations
  solve unseen operation combinations beyond a token-frequency bias? Two feasibility studies
  (one bank failed split/headroom, one failed the two-family requirement but kept a PA split),
  then two learning studies: learned token multipliers on G transfer about 2× to the withheld
  pair and to branch-else; contextual row moves on top add no resolved training gain (≤ 1.11×),
  holdout increment unresolved, and their off-family branch shift did not replicate (14). The
  four-reducer bank failed the symmetric split (15); on a narrower split, crossed token learning
  improves both families about 2.2× on training and 2–3× on the withheld cells, with no resolved
  family advantage there (95% upper bounds 1.25× BE, 1.15× PA; 16, closed). The frozen maps' gain comes from both starting
  programs and ongoing decoder use, about 1.3× each given the other and sub-additive, on the
  withheld and the training cells; the balance differs between BE and PA training cells (17,
  closed). Rank-one context steps mixed into token continuation: no resolved training increment,
  first in a loop where token continuation did not resolve learning (18), then in one where it
  did, C/T 0.967× [0.871, 1.073] (19; 18 and 19 closed). A previous-token table fitted to exact
  solver tapes beat a token-only fit to the same tapes 1.37× on training and 1.29× on the
  withheld cells, no resolved family advantage (20, closed). Refitting those tables to solvers
  found under them gave a further 1.40× on training and 1.29× on the withheld cells, attributable
  to the collection procedure (21, closed). On training cells that feedback step raised C's
  advantage over a token-only fit, I 1.17× [1.09, 1.25], mostly in BE, while the token-only fit
  also improved 1.20×; on the withheld cells I is unresolved, 1.09× [0.98, 1.20] (22, closed).
  15 of 15 slots used.
  - [11-composition-bank](questions/10-compositional-map-transfer/11-composition-bank/question.md)
    (closed, run 2026-10-05-2247): this 3×3 bank has no eligible split at 524k (Sm-SEL 27/50
    under U), and all four splits fail the 4 096 headroom rule under the hand-set grammar G.
  - [12-generic-grammar-headroom](questions/10-compositional-map-transfer/12-generic-grammar-headroom/question.md)
    (closed, run 2026-10-06-0001): ten-token branch cells leave 2–10× headroom above G, but none
    of six same-primitive assembly shapes yields an eligible two-family pair (alias identities).
  - [13-post-addition-map-learning](questions/10-compositional-map-transfer/13-post-addition-map-learning/question.md)
    (closed, runs 2026-10-06-0132 and 2026-10-06-0811): G-based token multipliers transfer to the
    withheld PA pair (2.25×, 2.06× on 200 seeds); the 552-weight learner showed no resolved
    training gain (0.92× [0.78, 1.09]); row residuals on top of M vs continued token steps:
    training 1.00× [0.90, 1.11], holdouts 1.16× and 1.06×, unresolved.
  - [14-saved-map-shape-shift](questions/10-compositional-map-transfer/14-saved-map-shape-shift/question.md)
    (closed, run 2026-10-06-1425, row 3): 0811's branch-versus-linear shift of R over M+ did not
    replicate on the "b" continuations (shift 0.73× [0.57, 0.94], opposite sign); the "a" maps
    keep it on fresh seeds, so it is run-specific; on "b" a frequency-matched token-only map
    was not resolved from R (shift 1.02× [0.92, 1.12]).
  - [15-four-reducer-family-bank](questions/10-compositional-map-transfer/15-four-reducer-family-bank/question.md)
    (closed, run 2026-10-06-1603, row 1): with FIRST added, branch-else has no role-covered
    holdout pair on three domains; PA splits; G4 has headroom on all 13 cells; hand-set family
    grammars show a crossed preference that context strengthens over the marginal controls
    (descriptive).
  - [16-crossed-family-adaptation](questions/10-compositional-map-transfer/16-crossed-family-adaptation/question.md)
    (closed, runs 2026-10-06-1723 and 2026-10-06-2229, row 4 both): BE- and PA-trained token maps
    beat G4 about 2.2× on training cells and 2–3× on the three withheld cells; matched over
    mismatched on the withheld cells 1.02× (BE) and 0.96× (PA), 95% upper bounds 1.2485× (about
    1.3× leave-one-map-out) and 1.15×, a
    1.1× preference not excluded.
  - [17-decoder-initialization-variation](questions/10-compositional-map-transfer/17-decoder-initialization-variation/question.md)
    (closed, 2 of 2 slots, runs 2026-10-06-2331 row 3 and 2026-10-07-0315 row 1): with starting
    tapes held identical, the learned decoder during search adds 1.39× [1.31, 1.47] (withheld
    cells) and 1.28× [1.22, 1.34] (training cells); with the search decoder held at M, learned
    starting programs add 1.30× [1.24, 1.36] and 1.33× [1.26, 1.40]; sub-additive in both. On
    the training cells the start weighs relatively more on BE than PA cells (−0.45 log2 [−0.68,
    −0.22]); not separated from shape or difficulty.
  - [18-compact-context-learning](questions/10-compositional-map-transfer/18-compact-context-learning/question.md)
    (closed at tested scope, 1 of 2 slots, run 2026-10-07-0821 row 3, then via 19): rank-one
    context steps mixed into token continuation from the saved maps add no resolved training
    increment; in the loop where token continuation learned, C/T 0.967× [0.871, 1.073]. Context
    learned jointly from G4, or added without displacing token steps, untested.
  - [19-selection-calibrated-continuation](questions/10-compositional-map-transfer/19-selection-calibrated-continuation/question.md)
    (closed, 1 of 2 slots, run 2026-10-07-1137 row 6): at 96 searches per candidate token
    continuation from the saved maps learned, T/S 1.143× [1.089, 1.200] and 1.122× [1.031, 1.222]
    on two fresh blocks; the cause is not isolated from the changed depth and total effort.
  - [20-solver-corpus-context](questions/10-compositional-map-transfer/20-solver-corpus-context/question.md)
    (closed, 1 of 1 slot, run 2026-10-07-1707 row 1): over 32 independent solver corpora, the
    fitted previous-token table beats the token-only fit C/T 1.365× [1.288, 1.446] (training) and
    1.293× [1.213, 1.378] (withheld); no matched-family advantage was resolved on the three
    withheld cells, and one PA cell favoured the mismatched fit; external fitting, not
    evolutionary discovery.
  - [21-iterated-solver-corpus](questions/10-compositional-map-transfer/21-iterated-solver-corpus/question.md)
    (closed, 1 of 1 slot, run 2026-10-07-1924 row 1): refitting each C to exact solvers found
    under it (C2) gives C2/C 1.404× [1.347, 1.464] (training) and 1.289× [1.204, 1.381] (withheld);
    a fresh one-shot G4 refit C' is not resolved from C (0.997× [0.940, 1.058]) and C2/C' is
    1.41× / 1.33×. One step, external fitting; yield, diversity and tape content not separated.
  - [22-feedback-context-increment](questions/10-compositional-map-transfer/22-feedback-context-increment/question.md)
    (closed, 1 of 1 slot, run 2026-10-07-2156, training row 1, holdout row 4; first attempt 2129
    stopped at preparation): I = (C2/T2)/(C1/T1) 1.169× [1.093, 1.250] on training (BE 1.34×
    [1.19, 1.50], PA 1.02× [0.95, 1.09]); T2/T1 1.20×; withheld I 1.087× [0.984, 1.200],
    unresolved. Reopen on a funded seed or lineage extension (price both).

