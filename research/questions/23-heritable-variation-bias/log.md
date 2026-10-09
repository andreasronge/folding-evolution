# Log: inherited token-generation frequencies

## 2026-10-08 — run 2026-10-07-2243: inherited vs ancestry-broken acquisition (slot 1), stopped at the cost gate

**Experiment.** [Proposal](../../runs/2026-10-07-2243/proposal.md),
[critique](../../runs/2026-10-07-2243/critique.md) (approve_with_notes),
[plan](../../runs/2026-10-07-2243/plan.md). Each individual carries θ ∈ [−3, 3]^22,
p = 0.9·softmax(θ) + 0.1/22, inherited from the recipient with N(0, 0.03²) per component;
48 episodes alternating sum/max thresholds 1 and 5, tapes redrawn from each individual's p at
every reset, an episode ends at the first exact solve or 128 generations. Broken control:
one uniform permutation of θ rows per generation before selection. Planned: 16 acquisition
runs per family × arm, mean final p frozen and scored on 16 shared seeds per training target
against uniform, the hand-set scaffold and the 1558 fit.

**Result: no experiment ran.** The modifier path was built (commit `25f929e`), 151 tests pass,
all four target labels and exact checks validate, σ = 0 identical-row replay reproduces the
legacy search on 20 seeds. Stage 0 timed one acquisition run per family × arm and 80 frozen
searches. The plan's conservative admission rule (2× the slower arm, 2× the *worst* observed
search for every scoring batch) priced the fixed roster at 569 min against a 210 min ceiling;
the max1 uniform tail (one search, 170.6 s, mostly shortcut verification) drives that number.
Mean-based pricing with 2× margin gives about 136 min
([infeasible.md](../../runs/2026-10-07-2243/infeasible.md)). The gate was too strict for
this harness; cost itself is not the obstacle.

**Stage-0 observations (n = 1 acquisition run per family × arm, 4 paired seeds per target;
descriptive only, not evidence for any explanation).**

| Family / arm | Episodes solved / 48 | Generations | Frozen geo-mean evals, target 1 / 5 (cap 262 144) |
|---|---:|---:|---|
| sum inherited | 47 | 1 679 | 25.6k / 36.0k |
| sum broken | 17 | 5 053 | 163k / 168k (1 of 8 censored) |
| max inherited | 7 | 5 624 | all 8 censored |
| max broken | 6 | 5 793 | all 8 censored |
| uniform (same seeds) | — | — | sum 41.6k / 46.0k; max 86k / 231k |
| hand scaffold | — | — | sum 4.5k / 7.3k; max 12.3k / 29.2k |
| 1558 fit | — | — | sum 7.8k / 6.4k; max 19.9k / 21.0k |

- The sum inherited vector raised INPUT to 0.36 (uniform 0.045), GT to 0.064; SUM and
  REDUCE_ADD stayed near or below uniform; SEP_A rose to 0.12. Partial scaffold recovery at
  best; on these 8 searches it sits between uniform and the scaffold (about 1.3–1.6× faster
  than uniform, about 5× slower than the scaffold).
- Both broken vectors drifted onto unhelpful tokens (sum: SLOT_13 0.22, IF_GT 0.16, INPUT
  0.010; max: MAP_EQ_E 0.26, ANY 0.20) and the sum one was about 4× slower than uniform.
- The max inherited vector *lost* INPUT (0.006) and raised SEP_A, SLOT_12, THRESHOLD_SLOT;
  under this exposure max episodes are rarely solved and both learned max vectors are worse
  than uniform.

**What this means for the design (not for the hypotheses).** Two problems surfaced that the
approved primary contrast would not separate:
1. *Exposure confound.* Early-stopped episodes give the arm that solves less more generations,
   hence more neutral drift (√5 000 × 0.03 ≈ 2.1 log units per component, against the
   proposal's assumed ≈ 1). Broken ÷ inherited would then mix "linkage helps" with "the
   control drifted further from uniform". The plan already requires inherited < uniform for
   useful acquisition; uniform should be the primary reference, with equal generation counts
   across arms.
2. *Max family under-exposed.* 6–7/48 episodes solved; a frozen comparison where both arms
   are fully censored is uninformative (unresolved by the plan's own rule).

Decision: keep 23 open, budget unchanged (2, none used: no execution), and return to the
strategist (`next: strategy`) because the opening strategy and this question's allocation
ask for review after a build/cost failure, and the stage-0 observations argue for revising
the primary contrast and exposure rule, not just the cost gate; a priced revised slot 1 is in
[decision 2243](../../runs/2026-10-07-2243/decision.md).

## 2026-10-08 — digest condensing (run 2026-10-07-2243): former digest text moved here

The digest was rewritten as current beliefs only (word limit). This is the root-23 open-question line, moved verbatim as it stood before the rewrite; no belief changed. Relative links below are relative to `research/`, not to this folder.

- [23-heritable-variation-bias](questions/23-heritable-variation-bias/question.md) (open,
  root, budget 2, 0 used): can a token-frequency vector inherited with each program learn a
  useful bias through program selection alone, and help fresh populations once frozen?
  Untested: the first design (run 2026-10-07-2243) was built and validated but stopped at an
  over-strict pre-run cost gate; its stage-0 timing runs are logged as observations only.


## 2026-10-08 — run 2026-10-08-0843: equal-exposure acquisition, uniform primary (slot 1, corrected), stopped at the cost gate

**Experiment.** [Strategy](../../runs/2026-10-08-0843/strategy.md),
[proposal](../../runs/2026-10-08-0843/proposal.md),
[critique](../../runs/2026-10-08-0843/critique.md) (approve_with_notes),
[plan](../../runs/2026-10-08-0843/plan.md). Same modifier law as 2243, but every episode runs
exactly 128 generations in both arms (first solve recorded, verification skipped afterwards,
selection continues). Planned: 20 acquisitions per family × arm (80), each frozen vector scored
on 16 shared seeds per training target; uniform, scaffold and 1558 fit on 64 seeds per target.
Primary R_u = uniform ÷ inherited, per family.

**Result: no experiment ran.** Implementation `c01f16d` (on branch `research/2026-10-08-0843`,
not yet on `research/main`): 111 tests pass, smoke passes in all four cells, analysis updated
for the 20-run roster, uniform primary, separate family verdicts and S = inherited/scaffold.
The pre-stated admission rule (timeout sum = 2 × mean-based estimate + 15 min, ceiling 3 h)
gave 11 397 s for the full roster and 10 868 s for the approved 32-reference-seed fallback,
**68 s over** 10 800 s. Mean-based expected queue: 87 / 83 min. The overrun came from max
acquisitions: 396–433 s each against an anticipated 260 s, of which 236–276 s is verification
(211k–247k fresh verifications before the first witness in some episodes). Stop rule followed
([infeasible.md](../../runs/2026-10-08-0843/infeasible.md), [projection](../../runs/2026-10-08-0843/cost/projection.json)).

**Timing observations (one acquisition per family × arm, separate streams, excluded from
inference; no frozen scoring).** All four ran exactly 6 144 generations / 6 192 censuses.
First exact solves / 48 episodes: sum inherited 35, sum broken 25, max inherited 26, max broken
19. Under 2243's early-stop rule max solved 7/48 and 6/48 and sum inherited 47/48; the rules
and seeds differ and n = 1, so this neither shows nor rules out that fixed-duration exposure
relieves the max under-exposure problem, or that post-solve maintenance slows later sum solves.
Mean lineage depth 5 995–6 132 of 6 144.

**Correction to the 2243 entry above (critique 0843 note 9).** "Cost itself is not the
obstacle" was too categorical. 2243 established a plausible mean-based price from four
acquisitions and 80 searches, not a validated full-roster runtime; the revised acquisition law
then proved 1.5–1.7× dearer on max than assumed.

Decision: keep 23 open, budget unchanged (2, none used), and propose the same approved design
with the descriptive reference seeds removed (16 shared contrast seeds only; contrasts never
used the extra seeds), because that changes no comparison or decision rule, prices at about
10 600 s against the 10 800 s ceiling, and the strategist reviews immediately after the result
anyway; a second strategist pass for a 68 s overrun would add an agent cycle without a decision
to make ([decision 0843](../../runs/2026-10-08-0843/decision.md)).

## 2026-10-08 — run 2026-10-08-0918: equal-exposure acquisition ran; one acquisition cut by a hidden per-job deadline, no frozen scoring

**Experiment.** [Proposal](../../runs/2026-10-08-0918/proposal.md) (the approved 0843 design,
reference seeds cut to the 16 shared contrast seeds), [critique](../../runs/2026-10-08-0918/critique.md)
(approve_with_notes), [plan](../../runs/2026-10-08-0918/plan.md),
[preparation](../../runs/2026-10-08-0918/preparation.md) (exact timeout sum 10 603 s, 197 s under
the ceiling; 127 tests), [code review](../../runs/2026-10-08-0918/code_review.md) (pass),
[execution](../../runs/2026-10-08-0918/execution.md), [analysis](../../runs/2026-10-08-0918/analysis.md).
Code `511711c` (merges `c01f16d`). Queue: acquisition (80 runs) → sum scoring → max scoring → analysis.

**Result: no primary measurement.** The acquisition stage ran all 80 acquisitions in 3 742 s
(timeout 5 824 s). 79 completed. Max / inherited / replicate 14 was cut at episode 31 of 48 by a
1 200 s per-job default deadline in `acquire()` (`job.get("seconds", 1200)`, error
"acquisition timing deadline; not censoring"; 1 035 s of it in the exact verifier). Neither the
proposal ("acquisition is never cut") nor the plan listed this deadline. The code review named
it as a minor note and judged it unlikely to bind. The completeness check then refused the
roster, as the plan required, and the three later entries failed their marker gate in 0.01 s.
Zero frozen searches ran, so R_u, L and S do not exist. `score()` has the same kind of hidden
default (600 s per search).

**Runtime observations.** At 10 workers, per-run times were 1.3–1.9× the single 0843 timing
runs: means 295 / 331 s (sum inherited / broken) and 609 / 560 s (max), max-cell maxima 1 065
and 1 081 s among complete runs. Reproduction took ≈ 205 s per run in every cell, against
126–139 s at 4 workers (contention, plus un-pinned Rayon threads). Max runs spend ≈ 60% of their
time in the verifier. The stage timeout would have held (summed worker time 36 501 s ≈ 3 650 s on
10 workers). The max-scoring timeout (3 162 s) was priced on old-law vectors and is now
likely too short: these vectors solve during acquisition, so their frozen searches will call
the verifier.

**Acquisition observations (descriptive, not evidence for any explanation; 20 runs per cell,
19 for max inherited).**

| Cell | Solves / 48, mean (sd) | Paired inherited − broken, 95% bootstrap |
|---|---|---|
| sum inherited / broken | 30.6 (11.0) / 31.1 (10.1) | −0.6 [−7.5, +6.0], 20 pairs |
| max inherited / broken | 22.8 (8.3) / 18.9 (8.5) | +4.1 [−1.3, +9.5], 19 pairs |

- Within-acquisition solving shows no resolved arm difference in either family; between-run SD
  (≈ 10 of 48) is large. This is search under a changing distribution on the acquisition's own
  populations, not the frozen fresh-start measure.
- Solve rate fell over the 48 episodes in all four cells (sum 0.79–0.81 → 0.55–0.60 per
  12-episode block; max 0.47–0.59 → 0.35–0.39).
- Both arms moved equally far from uniform: L1 distance of the population-mean distribution
  rose from ≈ 0.12 after episode 1 to ≈ 0.9 by episode 30 and plateaued (final 0.90–0.93; max
  possible ≈ 1.9). The broken arm has no linkage, so this movement is what the σ = 0.03
  walk over 6 144 generations (≈ 2.3 log units) produces without any lineage selection. The 2243
  entry above already flagged this drift scale. Whether the drift explains the falling
  solve rate is not separable from episode order here.
- Post hoc, weak: mean pairwise correlation of final vectors across replicates 0.09 (both
  inherited cells) vs 0.05 / 0.02 (broken); replicate-mean inherited vectors of the two
  families correlate 0.73 across tokens, broken 0.09. At most a small shared component riding
  on large neutral drift; says nothing about usefulness.

**Reading.** Nothing about A–E is decided. The observations make two things more likely in a
completed run: frozen vectors that are mostly drift, so R_u near or below 1 in both arms (a
Bounded verdict for this σ and schedule), and linkage hard to identify. That is a prediction
to test, not a result.

**Process lesson.** A default deadline written for stage-0 timing reached the main stage, and a
review note judged it "unlikely to bind" from a margin over one 4-worker run. Plans should list every
per-job time limit. A limit in a main stage should equal the stage timeout or be absent, because
the stage timeout already bounds cost and a per-job cut turns a slow run into missing data.

Decision: keep 23 open, and return to the strategist (`next: strategy`), because this is the
third build/cost stop on this design and the question's allocation sends any further stop to
strategy. The run counts as one of the two allocated experiments (it executed), leaving one.
I recommend a recovery run rather than a redesign: 79 of 80 acquisitions are valid and
reproducible under fixed seeds. Remove the per-job deadlines, pin Rayon threads, reprice max
scoring from the verifier costs seen here, and split the queue if needed. That yields the primary
contrast for about 1.5–2 h of queue. Reasons and price are in
[decision 0918](../../runs/2026-10-08-0918/decision.md).

## 2026-10-08 — run 2026-10-08-1046: recovery of 0918, frozen scoring ran — Bounded in both families; inherited vectors no better than uniform

**Experiment.** [Strategy](../../runs/2026-10-08-1046/strategy.md),
[proposal](../../runs/2026-10-08-1046/proposal.md), [critique](../../runs/2026-10-08-1046/critique.md)
(approve_with_notes), [plan](../../runs/2026-10-08-1046/plan.md),
[code review](../../runs/2026-10-08-1046/code_review.md) (pass),
[execution](../../runs/2026-10-08-1046/execution.md), [analysis](../../runs/2026-10-08-1046/analysis.md).
Code `a804f4f`. The approved 0918 design, unchanged; only operational fixes (per-job deadlines
removed, Rayon pinned to 1 thread). The 79 valid 0918 acquisitions were reused (SHA-256 checked);
max/inherited/14 was rerun from its original seed. Replay gates: two complete control replays
(sum/inherited/0, max/broken/0) and the 30 completed episodes of the cut run matched 0918
exactly; no fallback. This completes one comparison; it is not a replication. Queue 75 min
(acquisition 893 s, sum scoring 983 s, max scoring 2 585 s) against 3.25 h of timeouts.

**Result (pre-registered primary).** 80 acquisitions × 2 training targets × 16 shared seeds,
plus uniform, hand scaffold and 1558 fit on the same 16 seeds per target: 2 752 frozen
searches, none missing. Endpoint: geometric mean evaluations to first exact solve over both
targets, censored at 262 144; crossed bootstrap over acquisitions and seeds. Reference vectors
are single rows (seed noise only).

| Family | R_u = uniform ÷ inherited | Verdict | L = broken ÷ inherited | broken ÷ uniform | S = inherited ÷ scaffold |
|---|---|---|---|---|---|
| sum | 0.33 [0.21, 0.53] | Bounded | 1.00 [0.69, 1.41] | 3.00 [1.93, 4.68] | 11.9 [7.0, 20.4] |
| max | 0.73 [0.50, 1.06] | Bounded | 1.58 [1.04, 2.36] | 2.17 [1.53, 3.04] | 5.75 [3.66, 8.95] |

- **Sum:** the inherited vectors make search 1.9–4.8× costlier than uniform (resolved worse).
- **Max:** an inherited gain over uniform above 1.06× is excluded; a loss up to about 2× is not.
  Per target, max1 favours uniform (U/I 0.53) and max5 is tied (1.00), where uniform itself solved
  only 8/16.
- **Linkage:** on max, persistent ancestry gave cheaper vectors than shuffled ancestry; the
  broken control is worse than uniform, not better, so this is not an artefact of a control
  that beats uniform. On sum, L is unresolved (0.69–1.41). Where linkage mattered it made the
  vectors less costly, not better than uniform.
- **Scaffold:** a greater-than-twofold disadvantage against the hand scaffold is established in
  both families (S lower bounds 7.0 and 3.7); the 1558 fit is 6.8–13× cheaper than inherited.
- Between-acquisition SD of log cost 0.50–0.65. Runs cheaper than uniform: sum 1/20 inherited,
  1/20 broken; max 5/20 inherited, 2/20 broken. Cheaper than the scaffold: 0/80.
  Break-even is undefined (negative saving per search).

**Post hoc observations (not beliefs).**
- Acquisition solves and frozen solves correlate 0.59–0.85 across the 20 runs of a cell; the
  shared program seed confounds this, so it does not show that acquisition success could select
  vectors.
- Final vectors are concentrated (mean max token probability 0.22 vs 0.045 uniform) on tokens
  that differ between runs. Replicate-mean inherited vectors correlate 0.04 (sum) and 0.18 (max)
  with the 1558 fit. On sum the aggregator token fell below uniform (0.023 vs 0.045; scaffold
  0.089). The max inherited mean carries more GT than broken (0.087 vs 0.039).
- The 0918 prediction (R_u at or below 1 in both families) held. That the vectors are "mostly
  drift" is consistent with this, but drift versus selection was not isolated: broken ancestry
  removes persistent association, it is not a mutation-only control.

**Correction to the 0918 entry above (critique 1046 notes 6–7).** "Both arms moved equally far
from uniform" should read: both arms reached similar observed mean distances from uniform
(L1 0.90–0.93); similar distance does not imply equal direction or utility. "This movement is
what the σ = 0.03 walk … produces without any lineage selection" should read: the movement is
consistent with substantial drift; its contribution relative to selection was not isolated.
"At most a small shared component riding on large neutral drift" should read: weak
cross-replicate correlations suggest a possible shared component; its size, cause and
usefulness remain unmeasured.

**Reading against the explanations.** A (selection accumulates a useful frozen bias) is not
supported for this procedure: Acquired is excluded in both families. C (generic supply or
scaffold recovery) is not supported: no gain over uniform, far below the scaffold. B fits sum
(no resolved linkage effect, no useful increment); on max linkage had a resolved effect but no
useful one. D is not separable here (resident-program benefit was not measured). E (too little
selectable signal at this σ and schedule) remains open as a redesign hypothesis; nothing in
this run measures it.

Decision: park 23, because the pre-registered comparison is answered for this procedure
(Bounded in both families, with inherited vectors no better than uniform and more than twofold
behind the scaffold), the question's two experiments are used, and a further run of the same
procedure would not change a decision; a redesign (lower σ, different exposure or inheritance
rule) has no measured selectable signal to justify a slot ahead of root 10's reserve plan. The
decision goes to the strategist (`next: strategy`), as the strategy and plan require for every
outcome ([decision 1046](../../runs/2026-10-08-1046/decision.md)).

## 2026-10-08 — wording correction (steward, run 1246 digest check)

Correction to the 1046 entry above, from the [1246 critique's digest check](../../runs/2026-10-08-1246/critique.md)
(notes 7–9); the numbers are unchanged. "Inherited vectors no better than uniform" (heading and
decision) is stronger than the evidence: on max U/I 0.73 [0.50, 1.06] excludes the registered
1.5× gain and any gain above 1.06×, but permits a small benefit; on sum inherited is resolved
worse. Read it as "no useful gain established (useful = the registered 1.5× threshold)".
"Max5 is tied (1.00)" means the observed capped geometric costs were nearly equal (148,914 vs
148,634, uniform solving 8/16); equality is not established. Linkage on sum (B/I 1.00 [0.69,
1.41]) is unresolved, not absent. question.md and the digest now use this wording.

## 2026-10-08 — digest condensing (run 2026-10-08-1831): wording moved here

The digest was compressed under its word limit; no belief changed. These root-23 passages were
cut or shortened there and are kept here verbatim. Relative links are relative to `research/`.

- "(σ = 0.03 per component, 48 episodes × 128 generations)"; "The hand scaffold is 11.9× [7.0,
  20.4] and 5.75× [3.66, 8.95] cheaper than the inherited vectors. Fairly sure for this procedure;
  it bounds this σ, schedule and inheritance rule, not self-adaptation, and says nothing about
  transfer."
- "Broken ÷ inherited 1.58× [1.04, 2.36] on max (broken itself 2.17× costlier than uniform)";
  "Whether the vectors' movement is mostly drift was not isolated (no mutation-only control). Post
  hoc observations are in the [log](questions/23-heritable-variation-bias/log.md)."

## 2026-10-09 — digest condensing (run 2026-10-09-0843): wording moved here

The digest was compressed under its word limit; no belief changed. This root-23 passage was
shortened there and is kept here verbatim: "Drift versus selection in the vectors' movement was not
isolated (no mutation-only control)."

## 2026-10-09 — digest condensing (run 2026-10-09-1743): former digest text moved here

The digest was rewritten under its word limit (3035 → about 2920 words); no belief changed. This
is the section as it stood before the rewrite, verbatim. Relative links are relative to
`research/`. Wording only was shortened ("than the inherited vectors"; "was not isolated").

```
## 23 Heritable variation bias (root parked, budget 2, 2 used)

[23](questions/23-heritable-variation-bias/question.md): can a token-frequency vector inherited
with each program learn a useful bias through program selection alone, and help fresh populations
once frozen? TAG threshold tasks (sum/max > 1, 5), development bank `tag-threshold-v1`.

- **Under the one procedure tested, inherited frequencies gave fresh populations no useful bias
  (the registered 1.5× gain over uniform) on their training targets.** Pre-registered, 20
  acquisitions per family × arm (σ = 0.03, 48 episodes × 128 generations), each frozen vector scored
  on 16 shared seeds per target. Uniform ÷ inherited cost: sum 0.33× [0.21, 0.53] (inherited
  resolved worse), max 0.73× [0.50, 1.06] (a gain above 1.06× excluded, a loss up to about 2× not).
  The hand scaffold is 11.9× and 5.75× cheaper than the inherited vectors. Fairly sure for this σ,
  schedule and inheritance rule; not a verdict on self-adaptation, silent on transfer.
  ([run 1046](runs/2026-10-08-1046/analysis.md))
- **Persistent ancestry made the max vectors less costly than shuffled ancestry; no gain over uniform
  was established.** Broken ÷ inherited 1.58× [1.04, 2.36] on max; unresolved on sum, 1.00× [0.69,
  1.41]. Drift versus selection was not isolated (no mutation-only control).
  ([log](questions/23-heritable-variation-bias/log.md))
```
