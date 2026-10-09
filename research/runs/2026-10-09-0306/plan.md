---
estimated_minutes: 130
---
Continue the approved rerun of 0239 on existing commit `0faced8` (integration
`4f1d432` from `37c78c1`) and address the blocking code review. The scoring
timeout remains 11,700 seconds and default scoring deadline remains 11,580
seconds. Preserve the scientific implementation and all measurements; change
the admission predicate as explicitly requested by code_review.md. Expected
queue wall-clock is about 110–135 minutes, including preparation; preparation timeout is 1,800 seconds, scoring
timeout 11,700 seconds, summed 225 minutes (below the four-hour ceiling).
This revised plan is written before any new experiment or test execution.
Do not execute the full queue in this implementation turn.

Conditions and seeds: retain all 16 pinned 1246 C tables (BE1–8, PA1–8),
1548 row F's 16 then-addition cells and the exact eight paired seed/case draws
per corpus/cell. Run 2,048 Q and 2,048 P searches, population 256, 32 alleles,
cap 524,288, 64 training cases without replacement and the unchanged D1331
exact check, selection, mutation and crossover. Authenticate and reuse 1548
C/T/G4 and 0125 K. Q retains G4's conditional rows with per-position
multipliers; P draws independently from C's positional marginals. Fit only
uniform-prior marginals, using the inherited quantized normalization floor
250, actual quantized propagation, exact C start row for Q and frozen support,
fits and hashes. No target-performance tuning or roster expansion.

Validation and smoke: rerun inherited targeted tests and the complete
preparation at ten workers. Publish source/projected hashes, every position's
maximum token error and TV for Q/P; require token error <= 0.001 and TV <=
0.005, and Q start rows equal C exactly. Preserve exhaustive lookup/scalar
decoder checks, support checks, 32 bit-exact C/T replays and 16 bit-exact K
replays through 32 positional copies (only clock fields excluded). Time one
Q and one P search for each corpus, rotating across the 16 cells, at the
scientific cap: 32 preparation searches excluded from the scoring roster and
efficacy analysis. Log lookup construction, decode/worker/batch times and
capped tails. Preserve the published conservative price: 1.15 times the maximum
of average,
finite-batch and all-capped projections (with scheduling tail), plus fitting/check
time and 120 seconds reporting. This remains a diagnostic, not the admission
predicate. Per the blocking review, admission requires all three conditions:

- preparation elapsed <= 1,800 seconds;
- expected = 1.15 * max(average, finite-batch) + fitting/check time + 120 < 11,700;
- bound = all-capped (including scheduling tail) + fitting/check time + 120 < 11,700.

The 15% multiplier remains on expected runtime; the zero-solve all-capped
projection supplies a separate hard refusal bound without an additional 15%.
This explicitly changes the original admission predicate to avoid stopping the
cycle for timing noise in the small deterministic sample, as the review requires.
Record both admission prices and the exact rule in preparation.json, alongside
the unchanged conservative price and every existing measurement. Test observed
smoke-like load drift, strict timeout boundaries, and independent failure of each
of the three conditions. A failed design/admission gate means infeasible.md and
stop. Queue preparation repeats the gates and pricing with the final code/binary.

Prior timing observations: 0239 preparation solved Q 9/16 and P 6/16, using
rotating cells and unpaired with C. Historical full-roster solves were C
1,771/2,048, T 1,547/2,048 and K 1,484/2,048. The tiny timing sample supplies
neither an expected full-roster solve count nor evidence that either control
is insufficient. Previous expected scoring was 107–128 minutes and the
conservative price 181.16 minutes; this rerun preserves the experiment slot,
roster and published conservative price. The reviewed admission predicate above
changes how that measured price is used; fresh measurements determine admission.

Measurements: primary capped search cost (unsolved = 2*cap), solves,
per-cell and BE/PA summaries, fitness/diversity traces, C/Q, C/P, Q/K and Q/P;
1*cap and both-solved sensitivities with occupancy; descriptive arithmetic
log(C/Q)/log(C/K); and tokens changed per mutation/crossover for C/T/K/Q/P
on fixed-seed uniform tapes. Corpus is the unit (n=16). C/Q is
exp(mean_corpus(mean_cell_seed(log cost_Q - log cost_C))), with a 95% t
interval on 15 df. Only a complete fixed roster permits a decision.

Interpretation: C/Q lower bound >= 1.20 rejects this G4-based positional
replacement; upper bound <= 1.20 means sufficient within 20%; otherwise
unresolved. Always read C/P against the same bands. Q failing with P
succeeding leaves independent positional supply viable. Q succeeding with
P failing supports supplied grammar. Both failing rejects these two frozen
replacements under these operators and favours dependency-carrying targets,
without rejecting all positional learners or proving necessity of C's rows.
Both succeeding supports positional targets. Success establishes neither
learnability nor causality. Matching uniform-prior marginals does not match
selected populations or variation neighbourhoods, so C's advantage cannot
separate solver supply from effects on variation. Broad/discordant controls
remain explicit uncertainty. The inherited x1.14 precision forecast assumes
K-like corpus spread, not measured Q precision. If unresolved, report the
interval and price of resolution, with no top-up. Development-bank mechanism
scope only; transfer would require a fresh bank frozen with its method.
After full-run analysis, return to strategy.

Critique notes 1–4 are incorporated above. Completing both arms preserves the
approved mechanism question at the revised measured price; no new literature
or technique is claimed. Notes 5–6 concern question/digest wording outside
this researcher's write scope: defer to the steward, with the narrower joint
Q/P interpretation retained here. The current code_review.md requires the
admission correction above; also update config.task to this cycle and the inherited data README's current timeout/deadline
instructions while retaining frozen data paths and deterministic validation seeds.
No driver_feedback.md is present. approval.md approves with the critique notes.
Existing smoke/ records belong to commit 0faced8; write new smoke evidence to
smoke-review/ so those measured observations remain unchanged. Tests and the
full preparation will run before the final queue is updated. No full queue run.
