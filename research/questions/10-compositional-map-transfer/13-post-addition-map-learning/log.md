# Log

## 2026-10-06: opened (run 2026-10-06-0132)

Opened under root 10 on strategy 0132's direction (one-family transfer on the post-addition
split from run 0001). Steward probes on the six training cells, 65 536 cap, 20 seeds per cell
(`a65ded0`, unreviewed): G 13.75 / 13.94 mean log2 cost on two seed sets (SE 0.14); hand-set PA
grammar 14.10; U 16.57; G with all log-weights + N(0, 0.5) 14.12–14.86; one row + N(0, 0.7)
−0.26 to +0.54 versus G (SE ≈ 0.17, paired correlation 0.16–0.49). Inner-run cost 0.65–1.2 s
at 10 workers. ([results](../../../runs/2026-10-06-0132/steward_probes/results.md))

Decision: propose a gated outer-loop adaptation study with three learners (contextual, G-based
token multipliers, token-only), six independent trajectories each, evaluated on fresh training
seeds and both holdouts ([proposal](../../../runs/2026-10-06-0132/proposal.md)), because the
probes show the training signal is measurable but small against noise, and only real
trajectories can tell learning from no learning.

## 2026-10-06: run 2026-10-06-0132, result

Experiment: three outer-loop learners from fixed starts — C (all 552 contextual log-weights,
from G), M (23 global token multipliers on G's rows, from G), T (23 tied weights, from G-marg) —
6 matched trajectories each, (4 + 12) with re-scored parents, 3-coordinate N(0, 0.5) mutations,
25 generations on the six training cells at the 65k cap; every final map then scored on the same
fresh seeds (6 training cells × 50, 2 holdouts × 100, cap 524 288)
([proposal](../../../runs/2026-10-06-0132/proposal.md), [plan](../../../runs/2026-10-06-0132/plan.md)).

Result: outcome **row 1** on complete data (commit `02cf76f`, 197 528 searches, all 18
trajectories; [analysis](../../../runs/2026-10-06-0132/analysis.md)). Ratios are speed (> 1 =
faster), 95% two-level bootstrap, 524k cap:
- C / G: training 0.92 [0.78, 1.09] (no practical gain; 65k: 0.94 [0.81, 1.09]); holdouts 1.16
  [0.86, 1.54] and 0.80 [0.60, 1.07]. Learning curves flat in all six; L1 drift from G 1.1–1.5;
  C-marg / G-marg 1.01–1.10. C stayed at G plus noise.
- M / G: training 2.23 [1.82, 2.75]; holdouts (S?M:S)+M 2.01 [1.47, 2.81], (S?M:S)+m 1.71
  [1.26, 2.32]; all 6 trajectories faster on all three sets; curves still falling at gen 25.
  M's holdout cost sits 0.38 log2 above its training cost (G +0.12): about a third of the
  training gain does not reach the holdouts.
- T / G-marg 1.69–2.12× faster on all sets, but T / G 0.41–0.57.
- What M and T learned, consistent across trajectories: INPUT up (M ×3.4, 6/6), DUP down
  (M ×0.5, 6/6; T 6/6), IF_GT up (M 6/6), reducers up.
- Stage 0: G repeatability 13.86 vs 13.81 (gate 0.6). The gate dropped stage-3 sampling
  (projection 427 min vs 420); the run took 346 min. No sampled solver rates for learned maps.

Decision: keep 13 open (1 of 2 slots left) and return to strategy (`next: strategy`), because
row 1 and strategy 0132 both send the first adaptive result there before slots 2–3 are spent.
The run answers the procedure question, not A1: three-coordinate steps in 552 dimensions never
lifted C above the score noise (sd ≈ 1.6 log2 per run), so contextual learning is untested
rather than rejected. The restricted learner M gives the root its first held-out gain from a
learned decoder change (1.7–2.0× over frozen G, lower bounds 1.26/1.47); whether that gain is
specific to the PA family or a generic improvement of G on this alphabet is unmeasured.

## 2026-10-06: proposal for the last slot (run 2026-10-06-0811)

Steward probes (unreviewed; [results](../../../runs/2026-10-06-0811/steward_probes/results.md)):
re-reading 0132's generations, C's three-cell children had true-effect sd 0.00–0.09 log2 against
M's 0.25–0.28 (noise sd ≈ 0.4 per 24-run candidate), still 0.25 at generations 18–25. At the six
saved M maps, one-step children (60 per operator, 24 paired training searches each, 65k cap):
M token step 0.32, whole-row step N(0, 0.5) 0.18, N(0, 1.0) 0.34 (mostly harmful on average).
23 training searches/s at 10 workers.

Decision: propose R (M's multipliers plus row residuals, half token steps and half row steps)
against M+ (continued token steps) from the same M starts, 12 matched pairs × 35 generations,
with an R-without-residuals ablation and a frozen-M off-family check on the 8 non-PA cells
([proposal](../../../runs/2026-10-06-0811/proposal.md)), because row steps are now measured to be
visible to selection where C's were not, and strategy 0811 asks for the contrast against
continued token learning rather than frozen M.

## 2026-10-06: run 2026-10-06-0811, result

Experiment: from each of 0132's six saved M maps, two matched continuations per arm (12 pairs,
24 trajectories, 35 generations, same (4 + 12) outer loop and shared per-pair seeds). M+ continues
M's 3-multiplier token steps. R adds 24 × 23 row residuals (start 0): half its children take the
M+ step, half perturb one whole row by N(0, σ), σ ∈ {0.5, 1.0}. R_abl is each final R with its
residuals removed. Every map scored on shared fresh seeds (training 6 × 50, holdouts 2 × 200,
524k cap); frozen G and M1–M6 also on the eight non-PA cells of 0001 (2 branch-else, 6 linear);
the "a" continuations of M+ and R on the same cells; 10⁸-genotype sampling for 18 maps
([proposal](../../../runs/2026-10-06-0811/proposal.md), [plan](../../../runs/2026-10-06-0811/plan.md)).
The code review removed the stage-0 row-spread gate before the run (it failed in about half of
resamples of the pilot); only the harness check could stop the study.

Result: outcome **row 4, unresolved**, on complete data (commit `0709104`, 376 796 searches,
12/12 pairs, 4 h 50 min; [analysis](../../../runs/2026-10-06-0811/analysis.md)). Speed ratios
(> 1 = first map faster), 95% two-level bootstrap over six start clusters and shared seeds:
- R / M+: training 1.00 [0.90, 1.11] (no practical gain; a gain above 1.11× is excluded);
  holdouts (S?M:S)+M 1.16 [0.91, 1.48] and (S?M:S)+m 1.06 [0.83, 1.31], both unresolved. R faster
  in 6, 8 and 9 of 12 pairs. Between-start sd of the contrast 0.16 log2 on training, 0.45 / 0.41
  on holdouts, about twice the proposal's assumption; one trajectory (R4a) is slow everywhere.
- R / R_abl: training 1.15 [0.97, 1.41] unresolved; holdouts 1.10 [0.97, 1.25] (bounded below
  1.25) and 1.17 [0.88, 1.53] unresolved.
- M+ / M: training 1.45 [1.26, 1.69]; holdouts 1.21 [0.95, 1.54] and 1.43 [1.14, 1.78]. R / M
  1.41–1.51, all faster. Both arms gained the same 0.54 log2 on training.
- Frozen M / G on 200 fresh holdout seeds: 2.25 [1.81, 2.81] and 2.06 [1.60, 2.63] (training
  2.08 [1.72, 2.49]), replicating 0132; both lower bounds now clear 1.5.
- Off-family, frozen M / G: branch-else 2.23 [1.66, 3.06]; linear 1.08 [0.72, 1.57] (G near the
  population floor there). Learned "a" maps, not pre-registered, six maps: R / M+ on branch-else
  1.33 [1.05, 1.66], on linear 0.65 [0.44, 0.88] (slower in 6/6); M+ / M on linear 1.52 [1.09, 2.14].
- Sampling (descriptive): R raised PA-training solver supply about 2× over M+ in 5 of 6 starts
  and lowered linear D1 supply in 5 of 6; the PA supply rise did not give a resolved PA search gain.
- Outer loop: every operator's children entered the next parent set at the chance rate
  (23.7–25.8% against 25%). Selection on 24 searches per candidate does not tell row moves from
  token moves; both arms improved by slow cumulative bias. Stage-0 calibration put both
  operators' true-effect sd at 0.00 (R upper 0.11), an unstable estimate that gated nothing.
- Descriptive shrinkage of the gain over M on the holdouts: M+ lost 48% / 5%, R 8% / none.

Correction to the 0132 entry (critique 0811, digest check): C "stayed at G plus noise" should
read "C drifted modestly (L1 1.1–1.5) but showed no resolved training improvement; a gain above
1.09× is excluded at this budget". E1 for C means no resolved improvement, not zero movement.
"About a third" of M's training gain lost on the holdouts is about a quarter pooled (≈ 22%; 14%
and 33% per holdout). Learned directions agreed for INPUT up and DUP down (M and T) and IF_GT up
(6/6 M maps); reducer changes had exceptions and T otherwise scattered.

Decision: close 13 (budget spent) because its question is answered for the learner that moved
and the remaining contrast cannot be settled cheaply. Selecting on six PA tasks gives a decoder
that speeds the withheld pair about 2× over G (now with lower bounds 1.81 / 1.60 on 200 seeds).
Allowing contextual row moves added no training gain over continued token learning (bounded below
1.11×), and the holdout increment is unresolved (points 1.06–1.16). At the observed spread,
bounding a true null below 1.25 needs about 9 independent starts and resolving a true 1.16× needs
about 20, so a new M-map screen first; more seeds or continuations would not help. The
unregistered off-family pattern (R better on branch-else, worse on linear, PA supply up) is the
part worth a pre-registered test; it goes to the strategist with root 10's last slot.

## 2026-10-06: correction to the 0811 entries (critique 1400, digest check)

No new experiment. Language corrections only; numbers unchanged.
- "Selection on 24 searches per candidate does not tell row moves from token moves; both arms
  improved by slow cumulative bias" should read: operator acceptance fractions were near 25%
  (23.7–25.8%); equal average acceptance across classes can coexist with selection of better
  children within each class, so these counts do not establish how well selection ranks
  individual steps. Slow cumulative improvement is a proposed explanation, not an isolated mechanism.
- "Allowing contextual row moves added no training gain" should read "no resolved training gain,
  R / M+ 1.00× [0.90, 1.11]"; small positive effects are allowed.
- R / R_abl "resolved nowhere" means no resolved advantage on the three PA sets (1.15× [0.97, 1.41],
  1.10× [0.97, 1.25], 1.17× [0.88, 1.53]), not proof that residuals contribute nothing.
- "M and M+ carry every resolved gain" should read: token-only adaptation has demonstrated gains;
  an additional contribution from learned residuals has not been established in the planned PA
  comparisons.

Decision: none (no experiment); 13 stays closed because the corrections narrow wording, not results.

- 2026-10-06 (correction, from the 1419 critique's digest check): the off-family line in
  question.md said "M's change is not specific to post-addition among the IF_GT shapes scored".
  Separate PA and branch-else estimates show transfer to branch-else, not the absence of a PA
  preference. Now reads: "M's benefit is not confined to post-addition on the tested cells; a PA
  preference remains unmeasured." No data changed.

## 2026-10-08 — digest condensing (run 2026-10-07-2243): former digest text moved here

The digest was rewritten as current beliefs only (word limit). This is sections "Decoder learning on post-addition" and "Contextual moves on top of M", moved verbatim as it stood before the rewrite; no belief changed. Relative links below are relative to `research/`, not to this folder.

## Decoder learning on post-addition (root 10, run 2026-10-06-0132)

One run, commit `02cf76f`, complete data (18 trajectories, 197 528 searches). Same tape, harness
and frozen maps as 0001. Six post-addition training cells, two withheld `(S?M:S)+M`,
`(S?M:S)+m` (then/else pair never seen in training) on D1331. Three learners, 6 matched
trajectories each: (4 + 12) with re-scored parents, three-coordinate N(0, 0.5) mutations,
25 generations, selection on 24 fresh 65k-cap training searches per candidate. Final maps
scored on shared fresh seeds (training 6 × 50, holdouts 2 × 100, cap 524 288). Speed ratios
with 95% two-level bootstrap. Reviewed analysis; fairly sure of the numbers, narrow in scope:
one screened family, starts at G, one optimizer and budget.
([13](questions/10-compositional-map-transfer/13-post-addition-map-learning/question.md),
[run analysis](runs/2026-10-06-0132/analysis.md))

- **Learned token multipliers on G's template speed the withheld compositions about 2×** (1.7–2.25× across two seed sets). M (23
  global multipliers applied to every row of G) vs frozen G: fresh training 2.23× [1.82, 2.75];
  holdouts 2.01× [1.47, 2.81] and 1.71× [1.26, 2.32]; all 6 trajectories faster on every set.
  On 0132's 100 holdout seeds a ≥ 1.5× gain was not established (lower bounds 1.47, 1.26);
  re-scored on 200 new seeds in run 0811 the same maps give 2.25× [1.81, 2.81] and 2.06×
  [1.60, 2.63]. About a quarter of the training log-gain is lost on the holdouts on average
  (≈ 22% pooled; 14% and 33% per holdout; descriptive). The context is G's, supplied by hand;
  what was learned is token weighting: INPUT up (×3.4) and DUP down (×0.5) in all six M maps and
  in T, IF_GT up in all six M maps, reducer changes with exceptions. Curves were still declining
  at generation 25; 35 more generations of the same steps gave another 1.45× on training (run
  0811). Branch-else results are in the next section.
- **The full contextual learner showed no resolved gain with three-coordinate steps.** C (all 552
  log-weights, from G): fresh training 0.92× [0.78, 1.09] vs G, so a gain above 1.09× is excluded
  at this budget; flat curves; it drifted modestly (L1 1.1–1.5 vs M's 11–14). Its context-free
  marginals show no resolved improvement over G's (C-marg/G-marg 1.01–1.10; training interval
  [0.92, 1.23], holdouts [0.79, 1.30] and [0.79, 1.52], which admit appreciable gains).
  Holdouts split: 1.16× [0.86, 1.54] and 0.80× [0.60, 1.07]. Each child changes three table cells by about e^±0.5, far below the per-run score sd (≈ 1.6 log2, 24 runs
  per candidate). The operator is a plausible explanation, not an isolated cause; the result does
  not show that contextual preferences cannot be learned or would not transfer.
- **Frequency-only learning helps a context-free start but does not reach G.** T (23 tied weights,
  from G-marg): 1.69–2.12× faster than G-marg on all sets, still 0.41–0.57× of G's speed. It
  agrees with M on DUP down and INPUT up. G/G-marg on these seeds 3.0–4.8×, replicating 0001.
- **Token-weight learning found maps 2.2× faster than G on fresh training searches,** contrary to
  the steward's pre-run expectation (random whole-table perturbations and a hand-set PA grammar
  had not beaten G). This shows accessible improvement, not the shape of G's neighbourhood.

## Contextual moves on top of M (root 10, run 2026-10-06-0811)

One run, commit `0709104`, complete data (12/12 matched pairs, 376 796 searches, 4 h 50 min).
Same harness and split as 0132. From each of the six saved M maps, two continuations per arm,
35 generations, same outer loop and shared seeds within a pair: M+ (M's token steps) vs R
(M's multipliers plus 24 × 23 row residuals; half token steps, half whole-row N(0, 0.5 or 1.0)
steps). Shared fresh test seeds (training 6 × 50, holdouts 2 × 200, 524k cap); bootstrap over
six start clusters and seeds. Reviewed analysis; fairly sure of the numbers, narrow in scope:
one screened family, one outer loop and operator, starts at M.
([13](questions/10-compositional-map-transfer/13-post-addition-map-learning/question.md),
[run analysis](runs/2026-10-06-0811/analysis.md))

- **Allowing contextual row moves gave no resolved training gain over continued token
  learning.** R / M+ on fresh training 1.00× [0.90, 1.11]: a gain above 1.11× is excluded. Both
  arms gained the same 0.54 log2 over their starts (R / M 1.46×, M+ / M 1.45×).
- **On the withheld pair the increment is unresolved (points 1.06–1.16×).** R / M+ 1.16× [0.91, 1.48]
  and 1.06× [0.83, 1.31]; R faster in 8 and 9 of 12 pairs. The between-start spread (0.41–0.45
  log2) is about twice the planned one; bounding a true null below 1.25× needs about 7–9
  independent starts, resolving a true 1.16× about 20. The residual ablation (R / R_abl
  1.15× [0.97, 1.41], 1.10× [0.97, 1.25], 1.17× [0.88, 1.53] on the three PA sets) has no
  resolved speed advantage anywhere; appreciable gains remain possible, so no gain is
  attributed to the residuals, which is not the same as showing they contribute nothing.
- **Operator acceptance was near the chance rate.** Children of every operator (token,
  row σ 0.5, row σ 1.0) entered the next parent set at 23.7–25.8% against 25%. Equal average
  acceptance across operator classes can coexist with selection of better children within each
  class, so these counts do not establish how well selection ranks individual steps. Slow
  cumulative improvement is a proposed explanation, not an isolated mechanism.
- **M's learned change also speeds the branch-else cells, so its benefit is not confined to
  post-addition.** Frozen M / G on the two branch-else cells 2.23× [1.66, 3.06], a point
  estimate similar to the PA holdout gains (2.25×, 2.06×; separate estimates, not an
  equivalence test, so a PA preference is not ruled out); on the six linear cells 1.08×
  [0.72, 1.57], unresolved with G near the population floor. Branch-else is a related shape,
  not an independently trained family.
- **Unregistered hint (not replicated in run 1425): in the six "a" maps, allowing row moves
  shifted speed toward branch shapes and away from linear ones.** Six "a" maps: R / M+
  1.33× [1.05, 1.66] on branch-else (faster in 5/6) and 0.65× [0.44, 0.88] on linear (slower in 6/6), while M+
  alone got 1.52× faster than M on linear. R doubled PA-training solver supply over M+ in 5 of
  6 starts and lowered linear supply in 5 of 6, without a resolved PA search gain. Post hoc, six
  maps, no attribution to residuals: a pattern to test, not a finding. The pre-registered check
  on the "b" continuations (run 1425, next section) found the opposite shift.

