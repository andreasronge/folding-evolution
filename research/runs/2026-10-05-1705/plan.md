# Pre-registration: 2026-10-05-1705 — evolution of frozen family bias

**Status:** IMPLEMENTING; frozen before any smoke, pilot, sampling or evolutionary data, 2026-10-05. The owner-approved proposal is proposal.md. This task-folder plan uses the required prereg template headings; the user's task-folder destination and commit instruction supersede the skill's default Plans/ destination and commit question.

## Question (one sentence)
Does the frozen fitted op-frequency bias reduce median candidate evaluations to an exact solution on held-out sum>2 and max>2, relative to uniform and the other family's fit?

## Hypothesis
A: fitted supply enrichment passes through to a ≥2× median evolutionary speed gain, perhaps with low pass-through; A' is plausible because the manual scaffold restores CONST_2 to uniform. B: sampling supply changes without a worthwhile median-speed gain. Neither A nor A' identifies an improved search mechanism. Prior: proposal's A (2–4× speed), about 30% B. Related: ../2026-10-05-1558/analysis.md and map-bias §28.

## Setup
- **Sweep file:** queue.yaml; harness experiments/chem_tape/evolve_bias.py; frozen input experiments/chem_tape/evolve_bias_vectors.json. Copy of this plan is committed in the worktree research/runs/2026-10-05-1705/.
- **Arms / conditions:** sum2 and max2 × uniform, matched, mismatched, hand. Matched uses sum/max respectively; mismatched uses max/sum. Five unique 22-probability vectors below. Hand holds INPUT (1), GT (8), SUM (5) and REDUCE_ADD (11), or REDUCE_MAX (18), at matched probabilities; CONST_0/1/2/5 (2/3/15/16) are exactly 1/22. Every other probability shares the remaining mass equally. No fit, refit or vector selection here.
- **Seeds:** master 202610051705. Training/evolution replicate seed is master+100000+replicate (look 1 indices 0–49, look 2 50–99), shared across arms within each family, with independent training and evolution substreams. Pilot master+10000+index 0–9 shared across sizes/arms; smoke master+20000+index; sampling uses named SHA256-derived streams. None use 1558 seed streams. Bootstrap master+300000+family/comparison/look offsets; 100000 paired seed resamples per comparison.
- **Fixed params:** TAG alphabet 22 ops, 64 tags, L=64; max combine; preserve semantics, slots 12/13 NOP and threshold binding 0. Lexicase, crossover v2, crossover rate **0.7**, mate policy **selected** (both parents independently lexicase selected, self-selection possible), mutation 0.015 on each op and each tag, tags resampled uniformly; elite_count=2, panmictic, no duplication, fast_rng=True. All arms explicitly supply 22 op probabilities to initialization and op mutation. Changes in this probability vector alter initial supply, mutational supply, effective no-op mutation probability, and program/run architecture together; no isolated causal-op or mechanism claim.
- **Training sampler:** uniform draws with replacement within each label, 32 negative + 32 positive cases, shuffled per replicate/family; duplicates allowed (sum2 has only 15 negative domain inputs, so 32 unique negatives are impossible). Same cases for every arm/size at the paired seed. Full verification is all 10000 length-4 lists over [0,9]. This explicitly adapts the 1558 label-balanced sampler; no mbs four-stratum sampler or task-bound constant.
- **Est. compute:** one queue entry ≤28800 s total, four worker processes with Rayon=1 each. Pilot and sampling run inside the reviewed queue; only smoke timing in researcher turn. Internal deadline 27900 s leaves 900 s for analyses/output. Pilot is runtime/censoring calibration, not power evidence.
- **Pilot:** two population sizes 256 and 1024, uniform and hand, 10 disjoint seeds per task/size/arm (80 runs). Maximum candidate cap 4194304 including gen 0. Candidate caps considered 262144, 1048576, 4194304, from the same long trajectories. For each size choose the smallest cap with ≥8/10 uniform exact solves. Of sizes passing choose the one with latest hand KM median in candidate evaluations at its cap; unestimable hand median ranks latest, ties choose smaller size. If none passes, choose largest size whose measured cap-time fits the remaining budget for all 400 look-1 runs, and the largest listed affordable cap (potentially more censoring). If no listed cap fits, record runtime-infeasible and finish with unresolved routing; do not silently reduce N or cap. Pilot deadline 9000 s; interrupted pilot is not a valid calibration and routes unresolved. A process deadline abort is infrastructure missingness, never endpoint censoring.
- **Sample size/budget:** initially 50 seeds in each of eight cells. After pilot and sampling, before any confirmatory run, freeze selected size/cap per task and affordability in design.json. Estimate cap runtimes by the maximum measured pilot seconds per batch-processed training candidate (including implementation overhead; separate from the event-position endpoint) (per task/size) × cap; inflate 1.5×; reserve 900 s analysis. Sum estimated process seconds / 4 for 400 or 800 runs (using balanced worker schedules), plus longest-job allowance. If 800 fit, allow two looks; otherwise look 1 only, explicitly **large-effect screen**. If even 400 do not fit, stop runtime-infeasible. Once frozen, no budget-based endpoint or estimator switching. Unexpected deadline exhaustion is explicitly incomplete.
- **Sampling check:** 125000000 independent genomes for each hand vector, batches of 100000, same 1558 draw/screen/full Rust pipeline semantics. Descriptive only; no gate on sampling lift. Use 1558 transfer/look1 counts for uniform/sum/max (each 125M, sum2 173/852/176, max2 69/92/612). Export actual counts, rates, exact-binomial 95% intervals. Source SHA256: 792c4c0e0c982452e79db87b2acd9442d884f9b9b6ea35b9ba6af1c4ccc28615; source commit in frozen JSON. Product-model lift predictions use the actual hand vectors, ~17× / ~22×, not fitted constants.

### Frozen vectors
**uniform** (op ids 0–21):
```json
[0.045454545454545456, 0.045454545454545456, 0.045454545454545456, 0.045454545454545456, 0.045454545454545456, 0.045454545454545456, 0.045454545454545456, 0.045454545454545456, 0.045454545454545456, 0.045454545454545456, 0.045454545454545456, 0.045454545454545456, 0.045454545454545456, 0.045454545454545456, 0.045454545454545456, 0.045454545454545456, 0.045454545454545456, 0.045454545454545456, 0.045454545454545456, 0.045454545454545456, 0.045454545454545456, 0.045454545454545456]
```

**sum** (op ids 0–21):
```json
[0.03915026377197807, 0.12997486558237975, 0.02167181812543057, 0.05212621476271949, 0.027904374339493325, 0.08924745070289453, 0.02516837213615126, 0.05161211134368733, 0.1470277886559739, 0.02416885039155886, 0.03079440240523236, 0.07860878371606148, 0.03379298401359292, 0.026323484977979615, 0.0173961783160833, 0.01681685590942878, 0.07830929397700831, 0.020302557366706175, 0.020440627297962755, 0.006883286038467351, 0.0519545656152771, 0.010324870553932764]
```

**max** (op ids 0–21):
```json
[0.0393773975627665, 0.11800448951454848, 0.02072733484111011, 0.054857510798725, 0.014615065715744389, 0.01713904572578992, 0.024619945974200034, 0.033034577073963324, 0.13490493868427017, 0.03243564040045219, 0.04482445828061793, 0.018155389054489497, 0.04788301477193389, 0.041047216391779495, 0.01469639861016689, 0.016589104357988882, 0.07360621174101957, 0.025636214526606527, 0.12927685060208766, 0.024740527265089275, 0.0510534357288278, 0.022775232377822505]
```

**hand_sum** (op ids 0–21):
```json
[0.026665923537464893, 0.12997486558237975, 0.045454545454545456, 0.045454545454545456, 0.026665923537464893, 0.08924745070289453, 0.026665923537464893, 0.026665923537464893, 0.1470277886559739, 0.026665923537464893, 0.026665923537464893, 0.07860878371606148, 0.026665923537464893, 0.026665923537464893, 0.026665923537464893, 0.045454545454545456, 0.045454545454545456, 0.026665923537464893, 0.026665923537464893, 0.026665923537464893, 0.026665923537464893, 0.026665923537464893]
```

**hand_max** (op ids 0–21):
```json
[0.02906636929206079, 0.11800448951454848, 0.045454545454545456, 0.045454545454545456, 0.02906636929206079, 0.02906636929206079, 0.02906636929206079, 0.02906636929206079, 0.13490493868427017, 0.02906636929206079, 0.02906636929206079, 0.02906636929206079, 0.02906636929206079, 0.02906636929206079, 0.02906636929206079, 0.045454545454545456, 0.045454545454545456, 0.02906636929206079, 0.12927685060208766, 0.02906636929206079, 0.02906636929206079, 0.02906636929206079]
```

## Baseline measurement (required)
- **Baseline quantity:** uniform-arm KM median evaluations to exact solve in this evolutionary setup, measured concurrently; uniform solve rate at shared task cap is secondary.
- **Measurement:** individual runs log event/time/cap and solver genome; KM includes gen 0, duplicates and reevaluated elites. Gen g candidate i is evaluation g*P+i+1. Batch computation after that position is implementation overhead, excluded from the endpoint; exact-validation inputs are also overhead. Stop after first full-domain exact solver. Every distinct training-perfect genome is validated on all 10000 inputs (cached by full genome bytes, no hash-only key); no sample-only confirmation. No training-fitness early exit.
- **Value (if known):** to be measured in full run. Historical sampling rates are used only for the descriptive random-search baseline.

## Internal-control check (required)
- **Tightest internal contrast:** same-task paired seed, matched vs mismatched fit, alongside matched vs uniform; hand vs matched asks whether simple manual scaffold enrichment does as well.
- **Are you running it here?** Yes, all three comparisons in each family; no new family or heritable bias.

## Pre-registered outcomes (required — at least three)
Per comparison use oriented ratio slow/reference ÷ tested arm: uniform/matched, mismatched/matched, matched/hand. F = lower bound>1 AND point≥2; E = whole interval strictly inside (0.5,2); R = upper bound<1 AND point≤0.5; U = everything else (including unestimable medians/bounds). R is a resolved reverse effect, prevents wasteful second looks; it never supports A/B. These predicates are mutually exclusive. Routing metrics use CI treatment (25b option b), not unguarded means.

Family status grid (M=uniform/matched, S=mismatched/matched):
| M \ S | F | E | R | U |
|---|---|---|---|---|
| F | family-specific gain | generic/partial gain | partial/reversal | unresolved specificity |
| E | median equivalence vs uniform | median equivalence vs uniform | median equivalence + reversal | median equivalence, specificity unresolved |
| R | reverse vs uniform | reverse vs uniform | reverse both | reverse, specificity unresolved |
| U | unresolved baseline contrast | unresolved baseline contrast | unresolved baseline contrast | unresolved |

Cross-product of sum and max family states: both family-specific gain → A; both M=E → B; any U in a contrast needed for A/B → unresolved unless an already-resolved one-family gain/reversal establishes a partial result; every other cell → Partial (including resolved reversals). For A, hand/fit F or E in both families adds A'; any hand/fit R or U leaves A without A' and the narrower cell-level result visible. Hand comparison is independent: each of F/E/R/U is retained for each family regardless of A/B routing. Descriptive axes (solve rate/tails/sampling/pass-through) do not change routing; all cross-products of high/low/unestimable diagnostics with every routing row are reported with that same row, not suppressed.

| outcome | quantitative criterion | interpretation / next |
|---|---|---|
| **PASS — clean (A)** | both families M=F and S=F | useful fitted transfer on these holdouts; close 08, heritable follow-up to strategist |
| **PASS — partial** | only one family gains, generic gain, or resolved reverse effects | report cell-specific direction, send to strategy with last slot unspent |
| **FAIL — B** | both M=E | no worthwhile *median-speed* gain here despite supply lift; park frequency-only 08; report differing tails/cap solve rates |
| **INCONCLUSIVE** | remaining unresolved required contrasts, unestimable medians/bounds, infeasible/incomplete execution, or screen lacking a large effect | next: strategy; do not park frequencies as ineffective |

## Degenerate-success guard (required)
Too-clean outcomes include gen-0/first-position solves, all arms at ceiling, training-perfect shortcuts, constant-output programs and verification aliasing. Detect using a conjunction of (i) candidate-level event position (handles time-resolution ceiling), (ii) full-domain check of every unique training-perfect candidate (handles shortcuts/constants), (iii) parity/planted-solver and nonexact-shortcut tests (handles executor mismatch), (iv) logged train cases, vector checksums, solver genomes and full-byte verification cache (handles leakage/collision). Early or all-100% solves alone are not evidence of mechanism. Advisory per-seed inspection after row matching: verify saved solvers independently, inspect aggregate/GT/constant content and run census, and inspect time-zero solves and nonexact training-perfect counts. No additional p-value gate.

## Statistical test (if comparing conditions)
- **Test:** fixed now **KM median ratio with paired seed bootstrap percentile CI**, no log-normal AFT, no extrapolation. 100000 paired resamples, seed and look fixed. Undefined median is +infinity; quantiles use order-statistic (`inverted_cdf`) bounds, preserving unestimable draws. Both arm medians and both ratio interval bounds must be finite; otherwise U. At least 99% of bootstrap paired ratios must have both medians finite (reliability guard), otherwise U. No dropping censored/unestimable resamples.
- **Classification:** confirmatory; six comparisons per sweep, two looks = 12 potential decisions in the **2026-10-05-1705 held-out median-speed family**.
- **Significance threshold:** two-sided alpha=0.05/(6*2)=0.004166666666666667 (99.5833% CI). No recycling unused alpha. Bootstrap finite-sample coverage is approximate, not an exact FWER guarantee; do not use the proposal's SE≈0.14 as a power guarantee (critic's exponential median SE≈0.20 at n=100 is accepted).
- **Stopping:** compute all six at look 1; freeze each non-U verdict, point, interval, N and look forever. Look 2, if affordable, adds indices 50–99 only to the union of cells participating in U comparisons; shared-cell additions never rewrite stopped comparisons. A task/arm may have 100 seeds while a frozen contrast remains a 50-seed contrast. Never skip paired seeds; missing runs mark incomplete and cannot resolve a contrast.

## Diagnostics to log (beyond fitness)
All these metrics are **pending an infra extension** in evolve_bias.py before full run (~one implementation turn):
- run_one → runs/{phase}/{task}/{arm}/{seed}.json: candidate event/time/cap, generation/position, training indices/hash/config, elapsed seconds, verification counts, nonexact shortcut count, exact solver bytes, sparse history of best/mean training fitness, unique genotypes, run census. histories stop at event.
- summarize_cells grouping explicitly by (phase,task,arm,look/replicate set) → result.json cells: KM medians, event counts, cap solve rates and histories; compare → frozen comparison rows and bootstrap bounds. Missingness stays explicit.
- sample_hand → sampling.json: exact successes/N/rate/binomial CI per task/hand. frozen historical counts in vectors JSON.
- plot_results → diagnostics.png: eight KM CDF curves with full random-search curves 1-(1-p)^N and propagated p-CI band (all N, use log1p/expm1); per-arm median speed over random search and pass-through (uniform/arm median speed divided by p_arm/p_uniform) in result.json, unestimable as null. Fitness/diversity/run-count plot histories separately.
- sampler_audit → sampler_audit.json produced before pilot/sweep: class balance=32/64, both labels present, constant predictor accuracy, max>2 proxy for sum2 and sum>2 proxy for max2 on representative training seed and domain. Nondegeneracy requires both classes, logged actual accuracies; proxy perfection is possible on a small sample and does not authorize early stop. Implementation smoke exercises the audit before any sweep.

## Scope tag (required for any summary-level claim)
If promoted later: two constant-only holdouts sum>2 / max>2, L64 TAG, one frozen fitted vector per family (M one trajectory), lexicase/crossover-v2 at 0.7 selected mates and mutation 0.015, at pilot-selected shared family size/cap, n=50 or100 per cell. Median equivalence does not mean identical tails or general irrelevance of frequencies. Hand-set win establishes only a sufficient manual INPUT/GT/aggregator scaffold; no single-op attribution.

## Decision rule
A/A' → close practical question 08, strategist handles heritable follow-up. B → park frequency-only 08 with median scope. Partial → strategy with final slot unspent. Unresolved/incomplete/screen without large effect → strategy, no null claim. Sampling/product-model/pass-through diagnostics refine interpretation after routing only. No edits to questions/digest/briefs in researcher phase.

## Critique disposition and fidelity
All critique points accepted: estimator selected before pilot; unestimable KM data remain unresolved; stopped contrasts frozen despite shared-cell growth; crossover/mating fully specified; precision assumptions caveated; tail/cap differences remain visible; positive effects may be entirely supply-driven. No code_review.md or driver_feedback.md was present on entry. No full run is launched in this turn; the queue includes pilot, hand sampling, both affordable looks and analyses, with runtime feasibility decided before confirmatory data.

Pre-data correction: checked against alphabet.py, CONST_2 is id 15 (id 4 is CHARS). Corrected the hand-vector constant ids to 2/3/15/16 before any execution.
