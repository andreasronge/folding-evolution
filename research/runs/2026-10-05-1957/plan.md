# Pre-registration: 2026-10-05-1957 shortcut reproduction veto

**Status:** QUEUED · target commit: implementation commit on `research/2026-10-05-1957` · 2026-10-05

This is the implementation of the approved [proposal](proposal.md), using the prereg template from `docs/_templates/prereg.md`. The user's task-folder-only instruction takes precedence over the skill's `Plans/` destination. No full experimental data are examined during implementation; smoke seeds are excluded. All critique points below are accepted.

## Question (one sentence)

Does permitting exact max>2 phenotypes to reproduce explain part of R's exact sum>2 median-speed advantage on shortcut-admitting training sets?

## Hypothesis

R's elevated REDUCE_MAX sampling may give it reproductive access to an exact max>2 intermediate that accelerates exact sum>2 discovery. Alternatives: generic shortcut benefit shared by U; a proxy trap; negligible net reproductive contribution; other/inexact routes. Prior evidence and the rejected broad-intervention design are linked in the proposal.

## Setup

- **Sweep file:** this folder's `queue.yaml`, one three-hour entry, internal budget 10,500 seconds (300 seconds shutdown margin), four processes and one Rayon thread per process.
- **Arms / conditions:** U-ord, U-veto, R-ord, R-veto; sum2 only. U and R come unchanged from `evolve_bias_components.vectors` and its frozen vector source. Ordinary/veto share training cases, initial population, evolution RNG and operators within each vector/seed.
- **Seeds:** main master 202610051957; separate pilot master 202610051958; separate smoke master 202610051959. Pilot replicate seeds pilot-master+10000+[0,49]; main main-master+100000+[0,n-1]; smoke smoke-master+20000+[0,1]. Training and evolution use named SHA256/SeedSequence substreams under the phase master, separate from 1814. Power RNG master+300000; final bootstrap master+400000.
- **Fixed params:** TAG L64, P1024, 64 balanced cases (32 per class, with replacement), lexicase, two elites, crossover v2 0.7 with selected mate, mutation 0.015, fast RNG, administrative cap 262144 candidate evaluations. Earliest exact solver position determines time, as in 1814; generation batches may evaluate beyond that position. Smoke P64/cap16384 only.
- **Training A:** negatives use the inherited sum2-negative pool; positives are restricted to max2-positive inputs. Thus balance=0.5, exact max2 train accuracy=1, constant predictor accuracy=0.5 and both labels exist. `sampler_audit.json` emits these measured numbers on representative pilot/main seeds before evolution. Exhaustive domain audit must show 66 differing inputs and 9919 admitted positives.
- **Veto:** exhaustive full-domain phenotype class (exact sum2 first, exact max2 second, other) cached by complete genome bytes. Every training-perfect candidate is classified, including candidates later than the first solver in its generation. Because A admits the shortcut, detection is exhaustive for exact max2. Both parent roles, clones and elites use an explicitly filtered eligible pool, with a single eligible individual permitted and elite count limited to eligible count. Offspring may newly mutate into max2 and are then blocked next generation. Fully vetoed, unsolved populations stop as completed administrative cap-censored failures and are counted separately.
- **Identity:** paired runs execute in the same worker, recording SHA256 of ordered genome bytes each generation (no runtime fields). Generation zero through and including the first exact-max2 exposure must match; if ordinary stops first with no exposure, the entire pair, endpoint and solver must match. A mismatch raises an error and prevents the COMPLETE sentinel. An ordinary run can stop earlier after exposure; only the pre-exposure prefix is required to match.
- **Est. compute:** 200 pilot runs, then exactly 2400 or 3200 main runs if powered and affordable; no extension. Full run is queued, not executed by the researcher.
- **Related experiments:** 1814 component study at 31d4408; 1945 critique and strategy, linked in the proposal.

## Baseline measurement (required)

- **Baseline quantity:** U-ord/R-ord ratio of KM median evaluations (C1), measured again on A; the historical 1.61 gain is motivation only.
- **Measurement:** main paired four-cell seed records; pilot excluded.
- **Value:** unknown until main run. Practical bound tau=1.25 is frozen relative to the earlier gain (approximately half of log 1.61), never tuned using pilot.

## Internal-control check (required)

The tightest contrasts are R-veto/R-ord and U-veto/U-ord with identical vectors, cases and variation. Only eligibility changes. Its process consequences include changed elite composition, parent/mate opportunity and offspring distribution; causal interpretation is net access to reproduction, including population/mating mediation, not necessarily an ancestral stepping stone.

## Pre-registered outcomes (required — at least three)

Four confirmatory ratios: C1=U-ord/R-ord, P_R=R-veto/R-ord, P_U=U-veto/U-ord, I=P_R/P_U. Gate: C1 reliable lower>1. Otherwise no route claim. Conditional on this gate, take the first matching row:

| outcome | quantitative criterion | interpretation |
|---|---|---|
| FAIL — exact shortcut trap | P_R reliable upper<1 | Removing exact max2 speeds R; exact phenotype is a net trap here. |
| FAIL — no practical contribution | P_R reliable upper<1.25 | Net cost of removing exact phenotype is below the practical threshold; append detectable-but-small if lower>1. |
| PASS — route supported | P_R reliable lower>1 AND I reliable lower>1 | Reproductive access helps R disproportionately, explaining part of its advantage; population mediation remains possible. |
| PARTIAL — generic/uncertain differential | P_R reliable lower>1, interaction not resolved>1 | Shortcut helps R; contribution to R's extra advantage is unestablished. |
| INCONCLUSIVE | all remaining combinations, including unreliable estimates | Bounded unresolved result. |

This ordered predicate table is exhaustive over the cross-product of C1 replication/nonreplication/unreliable, P_R trap/small/substantial/open/unreliable and interaction positive/other/unreliable; no blank combinations. P_U is incorporated in I but never independently gates a label. All diagnostics are effect-size-only with no outcome-table rows because exposure, immediate ancestry and approximate routes do not identify necessity. They refine scope after row matching, never change routing.

Pilot power/runtime infeasibility is a completed feasibility result with no confirmatory contrasts and `next: stop`, not evidence against G3. Infrastructure missingness/identity failure is incomplete, never cap-censored and never promoted to a scientific null.

## Degenerate-success guard (required)

A too-clean identical veto/ordinary result could mean no exposure, failed detector, failed veto or compensation. Detect separately via planted exact max2/sum2/other classification tests; eligibility and lineage assertions for both parents/elites, including all-fail eligible rows and one survivor; exhaustive sampler audit; generation digest identity check; exposure counts and exact-veto census. No-exposure identical pairs are expected and constrain only this exact phenotype. Apparent universal solves must still pass all 10000 inputs; constant programs cannot solve. These multiple checks cover detection, propagation and endpoint artifacts.

## Statistical test (if comparing conditions)

- **Test:** whole four-cell seed-record percentile bootstrap of common-cap KM medians (100000 draws, chunks). Every contrast uses the same sampled seed indices, especially I; ratios of medians, not medians of ratios.
- **Classification:** confirmatory; family `2026-10-05-1957 exact-shortcut reproductive-access`, exactly four tests, one final look, raw family alpha .05, corrected alpha=.0125 (98.75% two-sided intervals). Pilot simulation and all descriptive quantities are exploratory and excluded from these contrasts.
- **Reliability:** inherited safeguards: common administrative cap, complete paired records; nonestimable bootstrap medians contribute [0,infinity] envelopes rather than being dropped. A gate requires finite point/lower/upper and >=.99 finite resamples. Missing runs invalidate main comparisons rather than becoming failures.
- **Power procedure, frozen before pilot:** resample whole four-cell pilot records, preserving observed between-arm dependence and post-exposure variation. Create null P_R=P_U=1 and alternative P_R=1.6,P_U=1 distributions by multiplying only exposed veto event times by a common vector-specific factor, preserving censor flags (originally censored observations remain censored) and administratively censoring injected events beyond cap. Unexposed ordinary/veto pairs are untouched. For effect injection, exposure requires a shortcut in a generation strictly earlier than the solver generation (or earlier than the final capped generation), so reproduction could actually occur; a shortcut merely earlier in the terminal batch cannot acquire an effect. Literal first appearance before the solver position remains a separate descriptive count. Use deterministic monotone bisection on log scale [-12,12] to target each empirical marginal KM median within relative numerical tolerance 1e-6; if an effect cannot be attained, the design is infeasible, not silently injected into unexposed pairs. The same alternative provides specified powers (a) I lower>1 and (b) P_R lower>1; the null provides (c) P_R upper<1.25. Report achieved effects, exposure, censoring, paired log-time correlations and joint probability C1/P_R/I all lower>1 under the alternative. No optimistic correlation is supplied. Use 300 simulations and 2000 inner bootstrap draws at each n=600,800, fixed RNG streams; report binomial MC intervals. Select the first n with all three estimated marginal powers>=.80. Joint route power is descriptive per critique, not an added gate. Freeze design.json before main jobs.
- **Runtime gate:** require complete 50x4 pilot. Estimate main wall time as `1.5 * n * mean(pilot worker-seconds per four-cell seed) / workers`, plus one conservative worst-case cap run and 600 seconds analysis reserve. The mean includes the measured cost of all four cells, including capped and fully-vetoed runs; it uses actual elapsed run times rather than pricing every main run at cap. The single cap-run reserve is `max_cell(1.5 * max_pilot(seconds / processed_candidates) * CAP)`, added without dividing by workers to cover a slow final worker. Record the mean costs by cell, mean four-cell seed cost, padded main estimate, cap-run reserve and total in design.json. The total must fit time remaining under the three-hour internal deadline. If power-selected n cannot fit, stop; do not downsize or try a different n for runtime. Deadline-truncated jobs record complete=false/time=null; queue exits nonzero without COMPLETE.

## Diagnostics to log (beyond fitness)

Infrastructure extensions to be completed and tested before queue launch:

- **Produced directly:** `runs/<phase>/<seed>.json` holds four cell rows grouped by seed/vector/veto; training indices/hash, full config/probabilities, endpoint, first_training_100, first max2 generation/position and whether strictly before solve, every-generation exact-veto counts and peak fractions, fully-vetoed flag, ordered population digests, remaining training-perfect other counts, verifications and bounded example genome slices (at most 20 unique others per row; census itself uncapped).
- **Produced directly:** immediate solver parent diagnostic via engine `lineage` indices and previous-generation phenotype flags; null at generation zero, both parent flags/kind recorded otherwise. Does not claim absence of earlier ancestry when neither immediate parent is max2.
- **Produced directly:** `comparisons` and `cells` in result.json via the new whole-record grouping/bootstrap wrapper; KM solve curves, per-seed fitness/diversity and shortcut fractions in diagnostics.png. Histories stop at solve/cap, so trajectories are individual, not survivor-biased average curves.
- **Produced directly:** pilot.json/power.json/design.json; power and runtime gates are recorded even when no main stage runs. pilot.json never enters final statistics. Metadata contains source-vector SHA256, code commit/dirty state and all seeds.

Metric definitions will also be exposed as `METRIC_DEFINITIONS` in the implementation: evaluations to earliest exhaustive exact sum2 candidate; exhaustive exact max2 reproductive exclusion; other training-perfect census; immediate-parent flags; four median ratios. All grouping uses the explicit four-cell seed wrapper, not the narrower inherited component aggregator.

## Scope tag (required for any summary-level claim)

`within-family / sum>2 / frozen R vector / TAG L64 P1024 lexicase / shortcut-admitting balanced cases / n=600 or 800 / exact max>2 phenotype only`. Net median-speed bounds allow compensation and do not exclude inexact max-like routes. Exposure and immediate ancestry are reported without a necessity claim.

## Decision rule

Every scientific outcome ends this threshold line with no precision extension, veto sweep, B/R-minus-M follow-up or added look. Rows 1–3 support closing 09 at the later steward step; rows 4–5/nonreplication leave it parked. Pilot-only ends `next: stop`; infrastructure failure requires correction, not interpretation. Question/digest/brief files are not edited by the researcher.

## Implementation validation (to complete after smoke)

Completed before pilot/main execution:

- 83 targeted tests passed across `test_evolve_shortcut_veto.py`, the two inherited bias harness suites, selection-mode, fast-RNG and chem-tape smoke suites. Tests cover exhaustive planted sum2/max2/other classification, cache hits, solver priority, explicit eligibility for both parents and elites under all-fail rows and one survivor (both RNG paths), all-true RNG identity, fully-vetoed censoring, immediate-parent flags, pre-exposure identity, whole-record interaction resampling, nonestimable envelopes, strict ordered outcome gates, effect injection limited to exposed pairs, runtime refusal, feasible/infeasible/main-missingness orchestration, and cancellation of queued seeds on identity error. A planted mixed population exercises real post-exposure reproduction.
- The final random smoke used separate smoke master 202610051959, two seeds, P64/cap16384, four cells each, workers=2, internal limit=180s. All eight runs completed at cap; all four ordinary/veto pairs matched for all 256 generations and at their endpoints. These random smoke runs had no exact-max2 exposure and made no full-domain verifications; detector/veto coverage is therefore supplied by the planted tests, not claimed from these random trajectories.
- Raw smoke artifacts: worktree `experiments/output/2026-10-05-1957-smoke-final-v2/`; compact validation is [smoke_validation.json](smoke_validation.json). The original smoke at clean commit 8462ab3 is in `experiments/output/2026-10-05-1957-smoke/`. Final smoke ran at clean implementation commit 3fa0405, including the separate phase masters, queued-job cancellation and reproduction-opportunity power mask. Full-run outputs will log the final clean implementation commit.
- `ruff check` passed for the new harness/tests; `git diff --check` passed. Queue loaded with `scripts/queue_lib.load_queue`, has one required-prefix entry, worktree-relative command, and timeout sum exactly 10800 seconds. Every normal terminal stage (main completion or feasibility stop) emits the expected outputs; infrastructure failures have no COMPLETE and exit nonzero.
- Sampler audit emits both representative phase masters/seeds with balance=.5, proxy training accuracy=1, constant accuracy=.5, both labels, 66 domain disagreements and 9919 admitted positives. No pilot or main data were run during implementation. A synthetic 800-seed/2000-draw bootstrap took about .053s, validating that the reserved analysis budget is plausible; this was a toy infrastructure check, not power evidence.
- No Rust code changed; the existing venv Rust extension was used and no rebuild was required.

Pre-pilot refinements implement the approved proposal literally: separate pilot/main/smoke master streams, numerical effect-target tolerance 1e-6 (unattainable targets stop), pending-job cancellation on identity failure, and requiring an actual reproduction opportunity for pilot effect injection (terminal-batch shortcuts cannot affect an endpoint). No thresholds or outcome labels were tuned on empirical pilot/main data.


## Metric definitions (verbatim from implementation)

- `time`: Candidate evaluations to the earliest exact sum>2 program in population order, verified on all 10000 lists; unsolved complete runs are administratively censored at cap.
- `exact_max`: Number of individuals whose output equals max>2 on all 10000 lists, after checking exact sum>2 first.
- `other_perfect`: Number of training-perfect individuals that are neither exhaustive exact sum>2 nor exhaustive exact max>2, counting duplicate genomes.
- `solver_parents`: Exact-max>2 flags of the immediate previous-generation parents of the earliest solver, using engine lineage indices; null for generation-zero solvers.
- `C1`: U-ord KM median evaluations divided by R-ord KM median evaluations.
- `P_R`: R-veto KM median evaluations divided by R-ord KM median evaluations.
- `P_U`: U-veto KM median evaluations divided by U-ord KM median evaluations.
- `I`: P_R divided by P_U, calculated from four cell KM medians with whole-seed paired bootstrap resampling.

## Code-review amendment (2026-10-05, before rerun)

The blocking issue in [code_review.md](code_review.md) is accepted: multiplying the maximum short-run seconds/candidate by the cap for every main run made runtime refusal nearly inevitable, despite affordable measured smoke costs. The revised gate above implements the reviewer's actual-pilot-cost estimate with a 50% margin, one conservative cap-run reserve and the existing analysis reserve. This is the first code-review amendment; no pilot or main data have been examined. Conditions, seeds, effect injection, power thresholds, sample sizes, confirmatory contrasts and outcome labels are unchanged. The previous implementation validation remains historical; fresh runtime regression tests and a separate smoke will be recorded below before the queue is finalized.
