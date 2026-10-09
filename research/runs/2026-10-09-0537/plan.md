---
estimated_minutes: 140
---
# Implementation plan, fixed before execution

Implement the approved R30/R100 experiment by extending the 0306 positional harness. Queue time is expected to be 90–180 minutes including preparation; timeout ceilings are preparation 1,800 s and scoring 12,000 s (230 minutes total). Measure setup and recoded search throughput before admitting the full queue; the 80-minute estimate assumes the inherited 11.7 worker-s/search and may be optimistic. If the fixed design cannot fit these limits, record measured infeasibility and stop without changing its roster or maps.

## Conditions and seeds

Use the sixteen frozen Q tables and all 2,048 historical (corpus, cell, seed) triples from 0306, paired with the 1548 C rows. Run exactly 4,096 new searches: R30 and R100, sixteen corpora, sixteen then-addition cells, eight search seeds per cell. Keep the original case draws, RNG streams, population 256, evaluation cap 524,288 and offspring operators. For each corpus/dose, construct two realizations with RNG SeedSequence([537, corpus, dose, k]); dose is integer 30 or 100, k is 0 or 1. Sorted search-seed indices 0–3 use k=0 and 4–7 use k=1, frozen before scoring. Position zero is unchanged. At each body position/context select exactly 7,200 of the 24,000 alleles for R30 and permute their entries uniformly; R100 permutes all entries. No realization selection by performance.

Map the original Q generation-zero alleles through the inverse context-dependent permutation using Q's decoded previous tokens. This preserves every paired initial tape exactly and preserves the independent uniform allele prior. Hash the actual lookup and permutation arrays. Exact per-row counts imply exact uniform-prior probability for every complete tape.

## Gates, measurements and smoke

Require exhaustive row-count preservation; all 4,096 initial-population token hashes equal Q; sixteen identity-Q and sixteen unchanged-C historical searches replay bit-exactly. Smoke-test map inversion, row counts, crossover/mutation stream preservation and small-scale search, then measure complete capped recoded searches and setup at ten workers. Include setup/memory costs and scheduling tail in runtime admission. Preparation records source/code/backend hashes; scoring refuses mismatched or non-admitted preparation.

Audit change-count and changed-span histograms for single-site resampling and the complete offspring operator on fixed uniform tapes (seed 202610090537, n=4,096 per corpus) and 1246 C solver tapes. Solver tapes are conditionally uniformly encoded: choose an allele uniformly from the preimage of each emitted token conditional on its preceding token and position. Report direct/downstream edits and tail probability P(changes>=4), including whether the uniform-tape footprint match transports to solver tapes. This is descriptive, not a gate to tune the frozen dose.

Primary effect G = exp(mean_corpus mean_cell,seed(log cost_Q - log cost_R30)), with failures costed at twice cap and a 95% t interval on 15 df. Secondary H = exp(mean(log cost_R30 - log cost_C)); approaches C requires H upper bound <=1.50. Report corresponding R100 gain interval, solves, one-cap and both-solved sensitivity, cells and realization spread. Gap share is log(G)/mean(log cost_Q - log cost_C) on the identical roster, not causal mediation. Record interval-based resolution price when unresolved; visualize effects and audit histograms.

## Interpretation fixed in advance

- G lower bound >=1.20: useful gain from this recoding at fixed uniform-prior supply. If H upper bound <=1.50, prioritize acquisition of variation coupling; otherwise retain coupling and fragments as candidates.
- G upper bound <=1.20: no useful R30 gain. Only say no useful gain at either dose if R100's upper bound also <=1.20. This bounds these recodings, not all wider mutation and not the necessity of C's conditional rows.
- G crossing 1.20: unresolved usefulness, return to strategy with resolution price. H crossing or exceeding the 1.50 bound leaves approach-to-C unsupported/unresolved as appropriate.
- R100 beating R30 while both lose to Q does not establish a useful lever. A useful R100 gain suggests dose dependence but remains secondary/descriptive.
- Poor transport of C-matched footprint to solver tapes limits interpretation of a null concerning width, while still testing this fixed representation.

The intervention changes edit correlations and potentially crossover along with width; matching mean/tail footprint does not match a transition kernel. It tests a frozen representation/variation change, cannot partition C's original advantage, and supports neither transfer nor acquisition on this development bank.

## Critique disposition

Notes 1–5 are incorporated above (measured throughput including setup; array hashes and fixed realization assignment; conditional-uniform solver encoding and full operator audit; explicit G/H direction; unresolved and negative outcome limits). Note 6's mutation-specific prior work is acknowledged: Byrne et al., *An Analysis of the Behaviour of Mutation in Grammatical Evolution* (2010), https://ncra.ucd.ie/papers/60210014.pdf, separates structural and nodal mutation effects; this test adds the exact distribution-preserving intervention against saved Q/C benchmarks. Notes 7–9 concern digest/question wording; researcher authorization restricts writes to this task folder, so those edits are deferred to the steward and no belief files are changed. No code_review.md or driver_feedback.md was present at planning time.

## Source audit corrections before recoded execution

The frozen Q tables all have range 24,000 (four_reducer_maps.R), rather than the proposal's 23,000. Implement the specified fraction f=0.30 as exactly 7,200 entries; full recoding uses 24,000. This corrects the count typo while retaining the frozen doses, probability distributions and search streams. Corpus seed indices are the fixed interleaved order BE1=0, PA1=1, ..., PA8=15.

The 1246 source contains 1,024 C searches, 936 solves, and zero saved C solver fields. Its 1,808 saved tapes are G4 collection solvers used to fit C. Do not substitute these in the C audit. Recover the 936 existing C solvers by replaying precisely those historical solved rows with return_solver=True, checking all non-clock/non-solver fields bit-exactly and checking D1331 solutions. This adds no scientific seeds, solver acquisition, fitting or target tuning. Their logged 3,057.13 worker-seconds project to 305.71 s on ten workers before tail/setup; preparation must include measured recovery and still finish within 1,800 s. If recovery cannot replay or this preparation cannot fit, stop and write infeasible.md. The first incomplete smoke exposed the allele-count mismatch before recoded execution; corrected smoke repeats in a fresh output folder.

## Committed-code smoke and queue admission

Code: `fe196c1d66381a25f9862ff1bfd8df75a9e2e571`. The committed preparation is in [preparation-committed/preparation.json](preparation-committed/preparation.json); the one-corpus small search smoke is in [smoke-final/smoke.json](smoke-final/smoke.json). All 48 relevant tests passed (41 existing harness tests and seven new recoding tests).

The committed preparation passed all exact count/bijection checks for 64 maps; all 4,096 initial-population token hashes; 936 historical C-solver recoveries with independent D1331 checks; and sixteen identity-recoded Q plus sixteen unchanged C historical searches. Preparation took 514.44 s, including 304.79 s for C recovery and 74.73 s of setup/map/audit work. Thirty-two searches per recoded arm (both realizations, every corpus) measured R30 at 12.22 worker-s/search and R100 at 16.77, including cold setup. Capped prices were 25.46 and 24.12 worker-s/search respectively. No arm/realization was selected using these observations.

Expected scoring with the 15% safety factor, finite-batch utilization, setup and reporting is 7,636.00 s; all-capped scoring including tail/setup/reporting is 10,375.39 s. Both pass the fixed 11,760 s admission ceiling inside the 12,000 s scoring timeout. Expected queue wall time including preparation is about 136 minutes; estimated_minutes is rounded to 140. The queue repeats preparation from the reviewed implementation rather than reusing smoke artifacts. Its two sequential timeouts total 13,800 s (230 minutes), below the eight-hour limit. The full scoring run was not launched during implementation.

Earlier scratch smoke folders are retained as implementation history: the first exposed the allele-count typo; the next exposed an unsigned-token decrement bug in conditional encoding, fixed before the passing smoke. An intermediate preparation was interrupted to rerun against committed code with the identity-recoding hook; only preparation-committed is the final admission evidence. These are implementation checks, not efficacy outcomes.
