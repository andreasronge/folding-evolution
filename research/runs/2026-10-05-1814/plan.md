# Pre-registration: 2026-10-05-1814 — INPUT/GT versus residual vector

**Status:** QUEUED, frozen before any experiment execution, 2026-10-05. Implementation and final n will be committed before the full run. This task-folder plan follows the research-rigor prereg template; the user's destination and explicit commit authorization override the skill's default Plans/ path and commit question. An identical copy will be committed in this worktree's research/runs/2026-10-05-1814/.

## Question (one sentence)
Does raising INPUT/GT mass or changing the conditional distribution of the remaining operations suffice to reproduce the other-family vector's median evolutionary speed-up within 1.5× on both sum>2 and max>2?

## Hypothesis
IG scaffold enrichment or R residual reshaping may suffice; both, neither, partial improvement, nonreplication, and task disagreement remain possible. The interventions distinguish sufficiency of vector components, not scaffold supply versus junk suppression versus shortcut ancestry. Related: proposal.md, critique.md, ../2026-10-05-1705/analysis.md, ../2026-10-05-1759/strategy.md.

## Setup
- **Sweep file:** queue.yaml; new bounded harness experiments/chem_tape/evolve_bias_components.py, reusing evolve_bias.py's engine, full-domain verification, and survival routines from 1705 at 9abc25c. No pilot or parameter tuning on new outcomes.
- **Arms / conditions:** tasks sum2/max2 × U/IG/R/X. X is frozen max/sum fit respectively in evolve_bias_vectors.json. U=1/22 each. IG copies X's p_INPUT (id1) and p_GT (id8), distributing remaining mass equally over 20 ops. R keeps these two at 1/22 and distributes 20/22 proportional to X's other probabilities. X is unchanged. Record all 8 vectors and source SHA256; verify their construction before running.
- **Seeds:** new master 202610051814; named SHA256/SeedSequence streams exactly as 1705 but with this master. Main replicate labels master+100000+i, i=0..n-1; shared training and evolution seeds across all four arms within a task. Smoke labels master+20000+i, no reuse in main; sampling named sampling/components/{task}/{arm}, training screen master+40000. Bootstrap master+300000+100*task_index+contrast_index. Old master 202610051705 is never used for new data.
- **Fixed params:** TAG 22 ops, 64 tags, L64, P1024, candidate cap262144 including gen0, lexicase, crossover v2 at0.7 with selected mate, mutation0.015 on ops/tags, elite2, panmictic, fast_rng=True, numpy backend with Rust training/full-domain prediction. Preserve safe-pop, combine max, slots12/13 inert, threshold0. Initialization and mutation both use the arm vector; initial supply, mutation supply, effective no-op probability and architecture change together. No single-op or mechanism attribution.
- **Training:** unchanged 32 negative+32 positive uniform within-label draws with replacement, shuffled, 64 cases. Same seed/task cases in every arm. Full domain is all10000 length4 lists over0..9. Training perfection never stops evolution unless exhaustive target agreement is100%.
- **Final n:** initially250 paired seeds per cell (2000 runs), one look. Before new outcomes, simulate on saved 1705 main/mismatched times only, with 200 independent synthetic experiments/task/n. Draw two independent size-n samples with replacement from that task's empirical X distribution, then pair by synthetic replicate index for our frozen paired bootstrap (100000 resamples, 99.5% CI). Record P(upper<1.5) for exact matching and P(2.25*lower>1.5) for a 2.25× slower arm; administrative censoring of the scaled arm at262144 is retained. Both checks use the same outer samples but separate scaled comparisons if censoring changes them. If either probability at250 is<0.80 on either task, try300 then350; choose the first passing n, or350 if none passes, explicitly retaining the precision limitation. Log Monte Carlo uncertainty; this is per-comparison precision, not joint verdict power. No margin change, added look, or new-data calibration.
- **Sampling:**125000000 tapes each for sum2/IG,sum2/R,max2/IG,max2/R, screened on balanced cases and exhaustively validated with the existing Rust sampler. U/X rates use the frozen historical125M counts from the vector artifact (U173/69, X176/92); mark their historical provenance. Descriptive exact-binomial95% intervals and sampling lift; intervals including1 do not prove equal rates.
- **Est. compute:** approximately1.5h at250, four workers with Rayon1; one overnight queue entry timeout10800s (3h), internal deadline9900s with900s output reserve. Increasing n to350 stays within this timeout. Unexpected missingness/deadline is incomplete, never endpoint censoring. No full run in this researcher turn.

## Baseline measurement (required)
- **Baseline quantity:** contemporaneous U and X KM medians in candidate evaluations, per task.
- **Measurement:** event at generation*g P+position+1; repeated elites/duplicates and gen0 count. Candidates beyond the earliest verified solver in a computed batch are processing overhead only. All unsolved complete runs are right-censored at262144. Full-domain validation is overhead, not candidate evaluations.
- **Value (if known):** measured in this run; 1705's3.3×/1.9× gains motivate replication but are not baseline nulls.

## Internal-control check (required)
- **Tightest internal contrast:** fresh paired U/X replication, then U/IG,U/R,IG/X,R/X in each task; four arms form a2×2 design.
- **Are you running it here?** Yes; no new task family or mechanism experiment.

## Pre-registered outcomes (required — at least three)
Each task first needs a reliable U/X lower bound>1. If it fails, both components are labelled 'not applicable: X not replicated', with all comparisons reported. Otherwise each component has independent gates: vsX within=upper<1.5, short=lower>1.5, open=otherwise; vsU faster=lower>1, not resolved=otherwise. Unreliable/undefined intervals are open/not resolved. Strict boundaries mean equality is unresolved.

| vsX / vsU | faster | not resolved |
|---|---|---|
| within | carries | unresolved (within; improvement not resolved) |
| short | falls short, but faster than U | falls short; improvement not resolved |
| open | unresolved (faster; sufficiency open) | unresolved on both gates |

Full task grid below uses C=carries,S=falls short,O=unresolved; this covers every IG×R combination. Descriptive high/low/undefined sampling and shortcut axes never alter any cell.

| IG / R | C | S | O |
|---|---|---|---|
| C | either intervention meets1.5× | IG sufficient; R falls short | IG sufficient; R unresolved |
| S | R sufficient; IG falls short | neither within1.5× | neither sufficiency resolved positively; IG short |
| O | R sufficient; IG unresolved | neither sufficiency resolved positively; R short | component sufficiency unresolved |

| outcome | quantitative criterion | interpretation / next |
|---|---|---|
| PASS — IG or R | X replicated in both; same nonempty set of carrying arms in both | close09 on that intervention's sufficiency only; retain each other arm's label; strategy next |
| PASS — either | X replicated in both; both arms carry in both | close09: either intervention meets1.5×; no additivity claim; strategy next |
| PARTIAL — task disagreement | any differing carrying set or one-task answer | report task-local labels, park09, strategy next |
| INCONCLUSIVE — replicated | X replicated; no carrying arm in one/both tasks | park09, even if both short; if both short say neither alone is within1.5×, retain vsU gates; no follow-up to strengthen reading |
| INCONCLUSIVE — nonreplication | X replication gate fails in one/both | 'not replicated at n=final n'; never '1705 was noise'; park09, strategy next |
| INCONCLUSIVE — infrastructure | any missing/incomplete runs or invalid pairing | do not issue scientific closure; fail queue without COMPLETE |

Identical verdict means identical carrying intervention(s) in both tasks; differing noncarrying-arm S/O labels stay visible but do not change a common positive sufficiency verdict, as proposal's 'other status stays open' clause requires. On max2, carries means within1.5×, not most of the gain. If09 closes, later steward may close08 with its scoped1705 result; otherwise park its unfinished part. Researcher does not edit question states.

## Degenerate-success guard (required)
Too-clean candidates: training-perfect max-as-sum/sum-as-max proxies, constant outputs, inert INPUT/GT on the tape, gen0 ceiling, reused seeds/vectors, executor disagreement. Joint engineering guards: exhaustive validation (handles shortcuts/constants); saved training indices and stream/vector hashes (handles leakage); exact candidate position and censoring (handles ceiling); independent Python/Rust parity on planted, cyclic and representative genomes (handles executor mismatch); output dependency decoding versus mere tape presence (handles inert ops). No diagnostic upgrades a statistical label. Decoding is a conservative structural data-dependency slice, not proof that an op was necessary; multiple same-tag max branches and IF_GT branches may contribute. State that qualification explicitly.

## Statistical test (if comparing conditions)
- **Test:** ratio of KM medians, paired seed-percentile bootstrap,100000 resamples; order-statistic inverted_cdf bounds. Administrative censored times become infinity for median estimation; undefined bootstrap ratios contribute an envelope[0,infinity], never dropped. Both median estimates and bounds must be finite,≥99% of paired bootstrap medians finite; otherwise gates unresolved. n≥250 with one fixed look; bootstrap coverage and FWER are approximate.
- **Classification:** confirmatory,2026-10-05-1814 component-sufficiency median-speed family. Exactly5 contrasts/task×2tasks=10 tests, no repeated looks. Two-sided alpha0.05/10=0.005 (99.5% CI). No statistical tests on diagnostics or precision simulations.
- **Routing-critical clauses:** CI treatment (25b option b), finite-fraction reliability guard above. Labels route sufficiency only; mechanism interpretation is advisory after matching. No clause both routes and identifies mechanism.

## Diagnostics to log (beyond fitness)
Infrastructure states before implementation:
- **Produced directly:** evolve_bias.py run_one candidate event/time/cap/position, exhaustive verification, solver bytes, config and train indices; km_curve/bootstrap_medians survival; binomial exact sampling interval.
- **Pending extension, complete before full run (~one implementation turn):** run_one optional component diagnostics emits per-generation best training accuracy and first generations≥0.75/1.0,≤20 distinct nonexact training-perfect genomes with first-seen gen and agreement on both full-domain tasks. Save only candidates encountered before the stopping position, in population order; continue evolution on shortcuts.
- **Pending extension:** component summarize grouping explicitly(task,arm,complete replicate set) → result.json cells with medians, capped solve rate, sampling lift/provenance, random median, evolutionary speed and pass-through. Frozen comparison records grouped(task,numerator,denominator) → comparisons.json/result.json with ten CIs and per-task exclusive labels. log(U/C)/log(U/X) in every estimable cell and multiplicative interaction(m_IG*m_R)/(m_U*m_X), descriptive only.
- **Pending extension:** decoder emits decoded.json for all1705 main solver genomes and new solvers/retained shortcuts, output-connected runs and output-value data dependencies versus tape INPUT/GT presence. Structural dependencies overapproximate necessity, not mechanism evidence; no ancestry claim. Include prior source file hashes. Full-domain other-family agreement is produced directly by exhaustive predictions.
- **Pending extension:** diagnostics.png survival/random-search and training trajectories, structure.png genotype diversity/run census, report.md complete numeric tables, design.json parameters/seeds/n, sampler_audit.json representative unchanged sampler balance/proxy accuracies. Sampling design is unchanged; existing sampler audit retained as verification, not new sampler tuning.

## Scope tag (required for any summary-level claim)
Two constant-only holdouts sum>2/max>2; frozen other-family vectors; TAG L64/P1024/lexicase/selected crossover-v2 .7/mutation .015; cap262144; final n250–350 paired seeds; initialization and mutation coupled; intervention sufficiency within1.5× only. No isolated op, search mechanism, additive or full-log-gain claim.

## Decision rule
Every outcome returns to strategy; only shared replicated positive sufficiency closes09. Otherwise park09 with task labels and partial effects; no additional study to rescue an unresolved reading. Descriptive sampling, interaction, log-gain share and shortcut decoding do not gate labels. Full run is queued for review, not executed here.

## Critique disposition and fidelity
All critique points retained: exclusive labels, lower>1.5 evidence for short, unresolved≠no improvement, no non-additivity inference, same two-task closure scope, no mechanism inference, historical sampling intervals≠equivalence, final n chosen using old data only, per-comparison precision caveat and maximum350. approval.md contains no additional owner conditions. No code_review.md or driver_feedback.md exists on entry.

## Frozen old-data precision check (before any new outcomes)

Final n=250 per cell; precision pass=True. 200 synthetic experiments/task,100000 paired bootstrap draws each,alpha=.005. Source:650 archived main rows from1705; only mismatched/X rows used for calibration. The source snapshot and each original-file hash are committed in evolve_bias_components_prior.json; no full-run dependency on mutable external files. Results in precision.json and frozen evolve_bias_components_design.json.

sum2: P(upper<1.5)=0.845, P(scaled lower>1.5)=0.815, median exact-match upper=1.347575363404039. Monte Carlo95% intervals: within[0.787,0.892], short[0.754,0.866].

max2: P(upper<1.5)=0.88, P(scaled lower>1.5)=0.9, median exact-match upper=1.3624761982179796. Monte Carlo95% intervals: within[0.827,0.922], short[0.850,0.938].

Both probabilities met80% on each task; no n increase. The results do not guarantee sufficient precision for intermediate effects or the joint two-task verdict. No new sampling or evolution has yet run.

## Implementation and smoke verification (engineering only)

All pending extensions above are now **produced directly**, with the decoder's explicitly qualified conservative structural slice. evolve_bias.py accepts an optional master/alpha and opt-in component diagnostics; its original defaults, selection, reproduction, candidate accounting and stopping behavior are retained. evolve_bias_components.py provides the four-arm construction, fixed single look, grouped tables, exclusive labels, descriptive sampling/interaction/log-gain share, decoding and output orchestration. No Rust source changed, so no rebuild was required. The frozen prior snapshot removes any full-run dependence on the mutable1705 output directory. Old and new saved solvers are exhaustively re-verified while decoding; a wrong saved solver/shortcut classification fails execution.

Clean implementation commit8d1e56f produced the first smoke at experiments/output/2026-10-05/2026-10-05-1814-smoke/ (ignored raw data). Engineering smoke used P64,cap16384,one disjoint smoke seed in each of8 cells,4 workers,and10000 tapes for each of4 component vectors. All8 runs completed; individual process seconds ranged0.403–2.921. It wrote1971 per-generation accuracy records,40 retained nonexact shortcuts,and683 decode records (including all642 archived1705 solvers,one smoke solver,and40 shortcuts). No label or n was changed after this smoke; it does not estimate a scientific effect or calibrate the full runtime. Trajectories stopped at events/cap; capped runs remained censored. All requested queue artifacts were produced.

Representative unchanged-sampler audit: sum2 and max2 each have32/64 positives,constant accuracy0.5,and both labels. Other-task proxy training accuracies are1.0 and0.625 respectively,with full-domain agreement0.9934 for both. Thus training perfection is a shortcut risk, explicitly handled by exhaustive validation and continued evolution.

Verification:89 tests passed across existing survival, tagged executor, op-weight and sampling tests plus24 new component tests. The tests cover all six gate combinations and strict1/1.5 boundaries, fresh paired seeds, vector reconstruction and coupled config, censoring/reliability, shortcut distinctness/order/20-limit, per-generation logging without endpoint changes, output-dependency versus tape presence, fixed one-look full orchestration, precision n escalation on toy old data,and infrastructure missingness without COMPLETE. Ruff format/lint and git whitespace checks passed. Import checks resolve both Python package and Rust extension inside this worktree. All700 possible fresh main evolutionary seeds (n≤350) were explicitly disjoint from200 unique archived main evolutionary seeds; named SeedSequence entropy also uses the distinct master.

Queue validation passed:one id2026-10-05-1814-evolve-bias-components,timeout10800s,total3h,internal9900s with900s analysis reserve,all command/output paths using the worktree and RUN_DIR. Shell syntax and expect_outputs were checked against the smoke. Canonical plan/queue/precision artifacts match their committed worktree copies. The full250-pair study and125M-per-vector sampling are left to the reviewed overnight queue.

Plot QA: inspected diagnostics.png and structure.png. Added explicit arm legends and increased single-trajectory opacity while retaining low opacity for250 trajectories; a second smoke will check these final presentation changes and reproducibility. This does not change experimental parameters or endpoints.

Final smoke from clean commit091d9f1 wrote experiments/output/2026-10-05/2026-10-05-1814-smoke-final/. It exactly reproduced all8 endpoints, event positions, solver genomes, training cases, per-generation histories,40 retained shortcut records, sampling counts, numeric cell/comparison tables and decoded genomes from the first smoke (wall timings and record order excluded). git_dirty=false. Final diagnostic/structure plots were visually inspected. Extended seed checking also confirmed all700 possible new main engine seeds are unique and disjoint from all222 archived1705 pilot/main/smoke engine seeds. Final changes after that smoke are documentation only. The reviewed full queue remains unexecuted.
