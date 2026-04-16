# Pre-registration: §v2.14

**Status:** QUEUED · target commit `TBD` · 2026-04-16

## Question (one sentence)

Does the executor's safe-pop rule (preserve-on-type-mismatch vs consume-on-type-mismatch) measurably affect evolutionary outcomes on body assembly tasks of different typed-chain lengths?

## Hypothesis

The current "preserve" rule (`executor.py:39-56`) leaves wrong-typed values on the stack when an op encounters a type mismatch, creating persistent type barriers. On the 6-token typed dependency chain (`INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT`, which crosses str → charlist → intlist → int types), these barriers may suppress assembly: intermediate wrong-typed values block downstream ops from reaching useful values below them on the stack. The alternative "consume" rule always pops regardless of type, simplifying the stack more aggressively.

On the 4-token body (`INPUT SUM THRESHOLD_SLOT GT`, all-int chain after INPUT pushes intlist), type mismatches are rare in near-canonical programs, so the rule should be neutral. On the 6-token body (mixed str/charlist/intlist/int chain), the rule may matter.

**Directional prediction is genuinely uncertain.** Kuyucu et al. (2011, see `docs/theory.md` §6) found that their "stricter" decision rule (conjunctive gene activation) outperformed the "more permissive" one (voter). Consume is the stricter analog. But the systems are different enough that the prediction could go either way. This is an exploratory ablation informed by the Kuyucu methodology (systematic micro-ablation of decoder rules across multiple task families), not a confirmation experiment.

**Motivation:** Codex independent review identified a concrete "stack jam" mechanism on the 6-token chain — wrong-typed junk persisting on the stack forces downstream typed ops to see defaults instead of reaching useful values. This is the kind of thing that can punish long-body assembly while barely mattering on short bodies.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2_14_safe_pop.yaml`
- **Arms / conditions:** 2 executor rules × 2 task pairs = 4 sweeps
  - **preserve** (current default): `safe_pop` returns type default without popping on mismatch
  - **consume** (ablation): `safe_pop` always pops top-of-stack, returns type default if mismatched
- **Task pairs:**
  - **Easy pair** (§v2.3's pair): `{sum_gt_5_slot, sum_gt_10_slot}` alternation, period 300
  - **Hard pair** (§v2.6 Pair 1): `{any_char_count_gt_1_slot, any_char_count_gt_3_slot}` alternation, period 300
- **Seeds:** 0-19 (same range as prior experiments, enabling seed-level comparison)
- **Fixed params:** pop=1024, gens=1500, BP_TOPK(k=3, bp=0.5), v2_probe alphabet, mutation_rate=0.03, crossover_rate=0.7
- **Est. compute:** ~60 min at 4-worker M1 parallelism (4 sweeps × ~15 min each)
- **Related experiments:** §v2.3 (easy pair baseline, 80/80 BOTH), §v2.6 Pair 1 (hard pair baseline, 4/20 BOTH), §v2.6-pair1 follow-ups (decoder/compute/tape ablations)

**Implementation:** one-line change in `src/folding_evolution/chem_tape/executor.py:safe_pop`. The current rule at lines 52-54 returns the type default WITHOUT popping when the stack top has the wrong type. The consume variant changes this to pop unconditionally and return the type default if mismatched. Both arms run fresh on all seeds at the same commit — no reuse of prior sweep data.

**No sampler changes.** Same tasks, same input distributions, same label functions as §v2.3 and §v2.6 Pair 1. Principle 20 gate is not triggered.

## Baseline measurement (required)

- **Baseline quantity:** BOTH-solve rate under `preserve` rule on each pair, measured in THIS experiment
- **Measurement:** the preserve arm runs simultaneously with the consume arm at the same commit, same seeds. This is the controlled baseline.
- **Value (calibration from prior data, not the threshold source):**
  - Easy pair: ~20/20 BOTH (§v2.3 established 80/80 across 4 blocks at commit `e3d7e8a`)
  - Hard pair: ~4/20 BOTH (§v2.6 Pair 1 at commit `0230662`)
- **Threshold source:** the measured preserve-arm values from THIS sweep, not imported numbers.

## Internal-control check (required)

- **Tightest internal contrast:** preserve vs consume on the SAME task pair, SAME seeds, SAME commit. The ablation IS the internal control — one executor rule change, everything else identical.
- **Are you running it here?** Yes. This is the experiment.

## Pre-registered outcomes (required — at least three)

All thresholds are relative to the measured preserve-arm values from this sweep (principle 6). Let `P_easy` = preserve-arm BOTH on easy pair, `C_easy` = consume-arm BOTH on easy pair, `P_hard` = preserve-arm BOTH on hard pair, `C_hard` = consume-arm BOTH on hard pair.

| outcome | quantitative criterion | interpretation |
|---------|------------------------|----------------|
| **PASS — consume helps hard pair** | `C_hard > P_hard + 3` AND `C_easy ≥ P_easy − 2` | Safe-pop rule is a real lever on 6-token mixed-type assembly. Preserve rule's type barriers suppress compositional assembly on mixed-type chains. Does NOT hurt easy pair. Promote to mechanism-ablation finding. |
| **PARTIAL — helps hard, hurts easy** | `C_hard > P_hard + 3` AND `C_easy < P_easy − 2` | Safe-pop rule reshapes the landscape in a body-length-dependent way. Consume helps assembly but disrupts slot-indirection on shorter bodies. Characterize the tradeoff; inspect easy-pair regressions. |
| **PARTIAL — unexpected direction** | `C_easy > P_easy` (meaningful only if `P_easy < 20`) AND `|C_hard − P_hard| ≤ 3` | Consume helps where not predicted. Inspect easy-pair winner genotypes. |
| **INCONCLUSIVE** | `|C_hard − P_hard| ≤ 3` AND `|C_easy − P_easy| ≤ 2` | Safe-pop rule is not a detectable lever at n=20 on these pairs. Executor semantics don't shape the search landscape enough to matter at this budget. Close the ablation axis. |
| **FAIL — consume worse** | `C_hard < P_hard − 3` OR (`C_easy < P_easy − 2` AND `C_hard ≤ P_hard`) | Preserve rule is actively beneficial. Type barriers are a feature, not a bug — they create useful stack structure that aids evolution. |

**Threshold justification (principle 6):** The ±3 threshold on the hard pair corresponds to the seed-substitution noise band observed in §v2.6 follow-ups: tape-length-24 moved from 4/20 to 6/20 but with **zero** seed overlap (pure seed substitution, not a mechanism lift). A delta of +4 or more exceeds this noise band. The ±2 threshold on the easy pair is tighter because the easy pair is near-ceiling (expected ~20/20) and any regression would be notable.

## Degenerate-success guard (required)

- **Too-clean result would be:** consume 20/20 on both pairs
  - **Candidate degenerate mechanism:** if consume makes most programs produce output 0 (by emptying the stack aggressively), constant-0 programs could dominate — but a solve requires ≥0.999 fitness, not ~0.50, so constant-output degeneracy cannot produce 20/20. A genuine 20/20 on the hard pair would be surprising.
  - **How to detect:** winner-genotype inspection on all 20 hard-pair consume seeds. Check for: (a) canonical 6-token body, (b) degenerate constant-output programs, (c) novel program architectures enabled by consume.
- **Near-threshold on hard pair (principle 21):** if `C_hard` is 3-7/20 (within ±3 of expected `P_hard` ~4/20), run attractor-category classification on all 20 consume-hard winners. Report seed-overlap with preserve-hard solvers. The tape-24 precedent (§v2.6-pair1-tape24) showed +2 BOTH but zero seed overlap — must check for the same substitution effect here.
- **Preserve-arm replication check:** if `P_easy < 18/20`, something has changed since §v2.3. Flag as a replication failure and investigate code drift before interpreting the consume comparison. If `P_hard` deviates by more than ±3 from the expected ~4/20, similarly flag.

## Statistical test (if comparing conditions)

- **Test:** paired McNemar on seeds {0..19} per pair (preserve vs consume on matched seeds). Secondary: Fisher exact test on the 2×2 table of (solved/not-solved) × (preserve/consume) per seed.
- **Significance threshold:** α = 0.05, two-sided
- **Power note:** at n=20 and expected effect sizes, McNemar is likely underpowered. The primary analysis is descriptive: solve counts, seed-overlap analysis (which specific seeds solved under each rule), and winner-genotype classification. Statistical tests are secondary and will be reported but not decision-driving.

## Diagnostics to log (beyond fitness)

- Per-seed BOTH-solve status under each rule (the seed-overlap table)
- Per-seed best-fitness under each rule (distributional comparison)
- Winner-genotype decoded programs for ALL hard-pair seeds under BOTH rules (for attractor-category classification per principle 21)
- Holdout gap on both pairs under both rules (guards against overfitting)
- Per-seed flip-transition cost (fitness delta at each task switch) under both rules
- Stack-depth statistics from execution traces on a representative sample of evolved programs under each rule (diagnostic for the "stack jam" hypothesis — does consume produce shallower stacks at convergence?)

## Scope tag (required for any summary-level claim)

**If this experiment passes, the claim enters findings.md scoped as:**
`within-family / n=20 / at BP_TOPK(k=3,bp=0.5) v2_probe / on {sum-body 4-token, string-count-body 6-token} pairs / executor-rule ablation / exploratory`

## Decision rule

- **PASS-clean →** Promote "safe-pop consume rule lifts mixed-type assembly" to findings.md with scope tag. Queue §v2.14b: consume rule on §v2.4 proxy-basin tasks to test whether consume also affects proxy-basin trapping (different mechanism axis, worth checking).
- **PARTIAL (helps hard, hurts easy) →** Characterize the tradeoff with winner-genotype inspection on both pairs. Consider a hybrid rule (consume for non-int pops, preserve for int pops) as a follow-up design. Do NOT change the project default without understanding the tradeoff.
- **PARTIAL (unexpected direction) →** Inspect easy-pair winners under consume. Look for novel program architectures. Queue a replication on the hard pair at 4× compute to check if the null on hard is budget-limited.
- **INCONCLUSIVE →** Close the safe-pop ablation axis. Proceed to chemistry-parameter diagnostic grid sweep on the hard pair (Option B from the Kuyucu/meta-learner prioritization analysis) as the next experiment.
- **FAIL →** Document as a negative finding: the preserve rule is load-bearing for chem-tape evolution at this budget. Proceed to chemistry-parameter diagnostic grid sweep.
