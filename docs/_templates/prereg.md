# Pre-registration: {experiment-id}

<!--
Save as: Plans/prereg_<short-slug>.md
Copy/paste this whole template. Delete these comment blocks and every
{placeholder} you fill in. Do not remove the required-field headings —
they enforce the methodology. See docs/methodology.md before editing.
-->

**Status:** QUEUED · target commit `{short-sha}` · {YYYY-MM-DD}

## Question (one sentence)

{The single question this experiment answers. If you need two sentences, split into two experiments.}

## Hypothesis

{What you expect to see and why. Link to the prior experiment(s) or theory section that motivate the prediction.}

## Setup

- **Sweep file:** `experiments/<track>/sweeps/<name>.yaml`
- **Arms / conditions:** {list}
- **Seeds:** {range, disjoint from prior seed sets if this is a confirmation}
- **Fixed params:** {pop, gens, mutation, crossover, E, …}
- **Est. compute:** {minutes · workers}
- **Related experiments:** {§N cross-links}

## Baseline measurement (required)

<!--
Principle 6: thresholds are baseline-relative, not absolute. Before
writing the outcome table, state WHAT the baseline is and how you'll
measure it in THIS experimental setup — not imported from a prior
sweep with different conditions. If no baseline exists yet, make the
first part of this experiment a baseline run and threshold Part B
against the measured value.
-->

- **Baseline quantity:** {e.g., fixed-task solve rate `F_baseline`}
- **Measurement:** {how this sweep measures it, or which prior sweep established it}
- **Value (if known):** {X/N from commit `sha`, else "to be measured in Part A below"}

## Internal-control check (required)

<!--
Principle 1: internal controls before external validity. What is the
simplest within-family contrast that could falsify the claim without
adding alphabet/task expansion? If the hypothesis survives the most
tightly-matched internal contrast, external tests are worth the cost.
If it doesn't, you catch the overreach for free.
-->

- **Tightest internal contrast:** {the minimal pair that could falsify}
- **Are you running it here?** {yes / deferred to §X / not applicable because Y}

## Pre-registered outcomes (required — at least three)

<!--
Principle 2: enumerate 3-4 distinct outcome regimes with pre-committed
interpretations. "Partial" and "swamped" are the usually-overlooked
categories. Thresholds must reference the baseline above, not absolute
numbers from prior experiments.
-->

| outcome | quantitative criterion | interpretation |
|---------|------------------------|----------------|
| **PASS — clean** | {baseline-relative criterion} | {what this means for the mechanism claim} |
| **PASS — partial** | {weaker baseline-relative criterion} | {narrower positive reading} |
| **INCONCLUSIVE** | {what in-between pattern looks like} | {what follow-up would disambiguate} |
| **FAIL** | {falsification criterion} | {what gets retracted or narrowed} |
| **SWAMPED** (if applicable) | {e.g., baseline already at ceiling} | {no mechanism-attributable signal possible} |

## Degenerate-success guard (required)

<!--
Principle 4: ask "what's the mechanism?" explicitly when a result is
too clean. Real plasticity mechanisms rarely produce perfect signatures
(20/20, zero drop, perfect symmetry). Enumerate the cheap artifacts
BEFORE running, so the post-hoc rationalization pressure is lower.
-->

- **Too-clean result would be:** {e.g., 20/20 BOTH, zero flip cost}
- **Candidate degenerate mechanisms:** {e.g., slot-indirection absorbing variation, trivial-constant output, input-invariant program}
- **How to detect:** {e.g., §8a-style winner-architecture inspection, per-subgroup diagnostics}

## Statistical test (if comparing conditions)

<!--
Principle 7: paired McNemar on shared seeds. Fixed-null p-values
against historical means are overstatement. If conditions share seeds,
the pairing structure is the test.

Principle 22: classify every test as confirmatory (gates a claim,
enters a FWER family) or exploratory (effect-size only, no p-value
gate). Family-wise correction protects paper-level inference.
-->

- **Test:** {paired McNemar on seeds {0..19} / two-proportion z on disjoint seeds / none — mechanism inspection only}
- **Classification:** `confirmatory` or `exploratory` (principle 22)
- **Family (if confirmatory):** {e.g., "proxy-basin family", "constant-slot-indirection family"} — name the claim this test would gate
- **Current family size:** {n_confirmatory_in_family — run research-rigor mode:fwer-audit if uncertain}
- **Significance threshold:** {raw α = 0.05 one-/two-sided; corrected α_FWER = 0.05 / n_family}

## Diagnostics to log (beyond fitness)

<!--
Principle 10: aggregate metrics hide mechanism. Identify per-subgroup
diagnostics that would distinguish competing mechanism hypotheses.
-->

- {per-island trajectories / per-seed longest-run / holdout gap / K distribution / etc.}

## Scope tag (required for any summary-level claim)

<!--
Principle 18: every summary bullet gets a scope tag. "Within-family",
"n=20", "at K=3 r=0.5", "on sum-gt-10-adjacent tasks". Tags age well;
naked claims age badly.
-->

**If this experiment passes, the claim enters findings.md scoped as:**
`{within-family / across-family / n=20 / at <regime> / on <task-family>}`

## Decision rule

{What you will do next under each outcome. This is the commitment that prevents post-hoc rerouting. Principle 2 + 19.}

- **PASS-clean →** {next experiment or promotion to findings.md}
- **PASS-partial →** {narrowing experiment}
- **INCONCLUSIVE →** {budget scaling or inspection}
- **FAIL →** {retraction target + narrowing target}
