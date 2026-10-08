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
