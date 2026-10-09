---
estimated_minutes: 90
---
Implement the approved frozen positional replacement test; queue wall-clock estimate is
84–92 minutes, conditional on new-arm throughput. No target searches run before this plan.
Preparation allowance is 30 minutes and full scoring timeout is 3 hours; no top-up.

Conditions and seeds: use the 16 pinned 1246 C tables (BE1–8, PA1–8), 1548 row F's
16 then-addition cells and the exact eight paired seed/case draws per corpus/cell.
Run 2,048 Q and 2,048 P searches, population 256, 32 alleles, cap 524,288,
64 training cases sampled without replacement and unchanged exact D1331 verification,
selection, mutation and crossover. Reuse authenticated 1548 C/T/G4 and 0125 K rows.
Q retains G4 conditional rows, reweighted separately at each position; P draws each
position independently. Both project C under the uniform latent prior, before selection.
Use normalize with floor 250 inside Q fitting, propagate actual quantized Q marginals,
keep C's exact start row at Q position zero, and freeze support handling, fitting and
hashes before scoring. No target-performance tuning.

Validation: publish table hashes, maximum per-token discrepancy and total variation
at every position for both Q and P, and their worst discrepancies. Require max token
error <= 0.001; additionally require per-position TV <= 0.005 (distributed discrepancy
must remain below half a percentage point). Validate positional lookup against a simple
reference decoder with changing tables at every position, support, deterministic decoding
and analytic uniform-allele marginals. Replay 32 legacy C/T rows bit-exactly, excluding
only clock fields; replay 16 historical K rows using 32 identical positional copies of K.
Any failed design gate leads to infeasible.md and stop, not a different intervention.

Small-scale preparation: time Q and P across all 16 corpora and both collection families
(32 searches), retaining full-cap rows and decoder/worker/wall timing. Historical solve
counts were C 1,771/2,048, T 1,547/2,048, K 1,484/2,048. Q/P hit rates and throughput
are unknown. Price lookup construction/overhead, measured per-evaluation capped tails,
4,096-search completion and a 15% safety allowance plus reporting reserve. Admit only
if preparation fits 30 minutes and the conservative complete scoring estimate fits the
3-hour timeout. Queue entry uses the admitted immutable preparation and current code /
binary hashes. Preparation results are validation/timing, not an efficacy decision.

Measurements: capped cost (unsolved = 2*cap), solves, per-cell and BE/PA summaries,
training fitness/diversity curves; corpus-weighted C/Q primary, C/P, Q/K and Q/P;
1*cap and both-solved sensitivities (with occupancy). Report log(C/Q)/log(C/K)
as descriptive arithmetic, never a causal fraction. Use fixed-seed uniform tapes to
measure tokens changed per mutation and crossover for C/T/K/Q/P, without tuning fits.
Unit is corpus (n=16); primary is exp(mean_corpus(mean_cell_seed(log cost_Q-log cost_C)))
with 95% t interval, 15 df. Exactly the fixed roster must finish for a decision.

Interpretation (critique corrections): C/Q lower bound >=1.20 means **this G4-based
positional replacement is insufficient**; upper bound <=1.20 means sufficient within
the stated 20% bound; otherwise unresolved. Always inspect C/P against those same bands.
If Q fails but P succeeds, independent positional supply remains viable. If Q succeeds
and P fails, supplied grammar remains useful. If both fail, these two frozen replacements
failed under these operators, favouring investigation of dependencies without ruling out
all positional learners. Both succeeding supports positional targets, not their learnability.
Discordant or broad controls remain explicit unresolved results. A C advantage cannot
separate solver supply from changed variation neighbourhoods, or establish fragments.
Then-addition is a development bank; no transfer or acquisition claim is authorized.

The projected x1.14 half-width assumes K-like corpus spread, not measured Q precision.
If unresolved, price further independent corpora conditional on observed spread; the
proposal's ~30 corpora is a precision estimate, not a guarantee near the boundary.
Return to strategy after results or a measured obstruction. Do not execute the full queue
in this implementation turn.

Critique points 1–5 are incorporated above. Points 6–7 concern digest/question wording
outside this role's write scope; defer those corrections to the steward and do not edit
research/digest.md or questions. No code_review.md or driver_feedback.md was present.
