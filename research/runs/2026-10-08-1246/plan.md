---
estimated_minutes: 146
---

Implement [proposal](proposal.md) on `research/2026-10-08-1246`; task artifacts stay
in this main-checkout run folder. No full experiment or protected-target search is
performed during preparation. This is implementation of an approved experiment,
not a new preregistration or a findings update.

Conditions and freeze

- Enumerate the 2 × 240 role assignments, collapse commutative/behavioural aliases
  using the lexicographically first id, exclude constant gates, cross-family
  behaviours and old-bank behaviours, then rerun the frozen exhaustive ≤9-token
  screen on D1331 (reject agreement ≥80%). Validate all canonicals against Python
  and Rust, with a saved length-three D1331 input manifest and stable hashes.
  This does not certify 13-token minimality. Record inactive-branch checks.
- Use precisely the four training cells per family listed in the proposal. The
  twelve previously probed behaviours remain development-only, including aliases.
  For each family and repeated reducer S/M/m/F choose the unprobed, retained,
  training-role-covered representative minimizing sha256(id + "1246"). Save the
  candidate lists, split, token totals and hashes before any search. Remaining
  eligible behaviours stay unsearched.
- Reuse production `composition_search.search`, unchanged G4 and `solver_corpus_fit`:
  first D1331-exact solver's entire 32-token tape; each cell's empirical transitions
  rescaled to 1600; T has 24 bounded multipliers on G4; C has alpha=50 shrinkage;
  K fitted and diagnosed but not scored. No canonical or witness enters a search
  job, initialization or fit. K convergence does not gate C/T or exclude corpora.
- Full roster: 8 independent corpora per family, 48 G4 collection searches per
  own cell (3072); C/T each 16 paired fresh seeds per own cell (2048); G4 32
  additional fresh seeds per training cell (256). Cap=524288, population=256,
  tape length=32, 64 randomly chosen fitness cases; exact solve requires D1331.
- Replace 1707's 24/48 per-cell yield gate: no minimum beyond one exact tape per
  cell is needed to fit. An empty cell stops execution with an acquisition
  obstacle; never substitute another cell, reuse a canonical, or drop that corpus.
  Report solves, attempts and distinct tapes per cell/corpus. The continuation
  gate is pooled collection yield ≥40% across the analysed balanced corpus prefix;
  also report per-family yield. The 1600 weights are normalization, not independent
  observation counts. Yield is an acquisition-cost gate, not a mechanism test.

Seeds and timeout blocks

- Full seed base 202610081246, smoke base 202710081246. Reuse the injective 1707
  rule: base + phase*1000000 + (family==PA)*100000 + corpus_index*2000
  + cell_index*200 + seed_index. Phases: 0 collection, 1 training C/T,
  2 future holdout C/T, 3 training G4, 5 future holdout G4. Fresh cases and
  variation are paired between C and T only. Check all seed blocks for collisions.
- Smoke: one corpus per family, 8 collection seeds per own training cell, 2
  fresh paired seeds per own cell and 2 G4 fresh seeds per cell, at the scientific
  cap (112 searches). This development-only smoke times collection, independent
  verification, fitting, both fitted arms and reporting; it is not an efficacy
  decision. A stochastic low smoke yield is reported, not a full-run yield verdict.
- Execute G4 training first, then fixed pair blocks (BE1, PA1), …, (BE8, PA8).
  Each pair collects and fits both corpora, persists hashes, and completes its
  paired C/T scoring before the next pair starts. Save every completed search.
  On timeout, analyse only the largest fully completed initial sequence of these
  pair blocks, never whichever jobs finished fastest. At least the first six
  pairs (12 corpora) are required for the primary interval; fewer means incomplete
  execution. Exclude the trailing incomplete pair and report its costs/yields
  separately. A non-timeout validation or empty-cell failure is an execution
  obstacle, not an allowed fallback efficacy result. No optional statistical
  stopping. Reserve reporting time inside the 10800-second queue timeout.
- Freeze the complete stage-2 roster/seeds/rules now: every one of the 16 corpus
  C/T tables × all eight holdouts × 16 seeds; G4 32 per holdout (4352 searches).
  Save fitted T/C/K hashes as corpora are acquired and a complete freeze when all
  sixteen exist. Stage 2 remains unallocated; no holdout search command is enabled.
  Keep the narrower C-versus-T transfer claim; do not add K scoring to stage 2.

Measurements and interpretation

- Primary corpus score is mean(log(cost_T) − log(cost_C)) over its four cells ×
  16 paired seeds; unsolved cost is 2×cap. C/T = exp(mean corpus score), with a
  two-sided 95% t interval over the 16 independent corpora (or declared 12/14
  completed prefix). Equal BE/PA counts give equal family weights. Also report
  1×cap sensitivity and each family separately. Training effects only; positive
  C/T compares fitting procedures and does not isolate order from changed emitted
  token frequencies. K emitted-frequency diagnostics remain descriptive.
- Routing precedence: if lower bound >1 and pooled yield ≥40%, recommend strategy
  consider stage 2. This wins the overlap with upper bound <1.10. If lower >1
  but yield <40%, report resolved relative gain with acquisition obstacle and
  return to strategy without recommending transfer. Otherwise upper bound <1.10
  bounds the gain below 10% and makes stage 2 unattractive for C/T; it does not
  establish no advantage. Remaining intervals are unresolved; report additional
  balanced corpora needed for a 1.10× precision target and to detect the observed
  effect, with their measured acquisition/scoring price. Do not enlarge this queue.
- Report C/G4 and T/G4 capped geometric costs and solve rates, per family and cell,
  using the independently seeded proposed G4 rows. If C only beats a damaged T
  and neither improves on G4, the result is a relative fit advantage without
  useful adaptation; flag that limitation for strategy rather than silently
  changing the approved primary rule. Summarize acquisition evaluations, distinct
  tapes, fitting/verification/search wall and worker time, costs to repay fitting,
  task spread, training fitness/diversity curves and continuation runtime.
- If C/T resolves upward, the old-bank fit benefit replicates on these new training
  compositions; protected transfer remains open. A tightly bounded small effect
  limits this procedure on this bank. Wide intervals distinguish neither a
  shape-specific old-bank gain nor reusable corpus information. Low yield points
  to acquisition difficulty. Uniformly easy searches would reveal ceiling/headroom
  limitations, not independent confirmation of the token-order mechanism.
- With 1707's within-family corpus SDs 0.27/0.16 log2 and similar family means,
  approximate pooled SD is 0.222 log2. At n=16 the 95% half-width is 0.118 log2
  (multiplicative 1.085); n=12 gives 0.141 (1.103). Twice those SDs gives 0.237
  (1.178) and 0.282 (1.216). Family mean separation can widen the pooled interval;
  these are planning scenarios, not guaranteed precision on the harder bank.

Critique dispositions

Notes 1–6 are implemented above: new yield policy and distinct-tape diagnostics,
protected deterministic split, frozen one-shot procedure, signed endpoint and
precedence/precision, fixed balanced timeout prefix, and restricted mechanism
scope with G4 headroom. Note 3 needs no new literature work for this replication.
Notes 7–9 concern existing digest/question/log claims outside the researcher's
write scope; defer those text corrections to the steward. This run neither edits
nor endorses those claims. No code_review.md or driver_feedback.md is present.

Feasibility stop

Before queueing, require semantic counts/split to match the probe and measured
collection/fitted-arm throughput consistent with completion within the approved
three-hour envelope (including overhead). If this approved design cannot run,
write measured `infeasible.md`, commit implementation, and stop for steward review.
Do not change targets, cap, fitting law, holdouts or sample sizes to rescue it.


Preparation measurements (after the pre-run plan above)

The semantic build reproduced 37 BE / 56 PA survivors, with 480 × 1331
canonical checks in each executor. It took 111.5 s total, including 109.0 s
screening and 2.28 s canonical validation; peak screen RSS was about 5.17 GiB
as reported in [screen_timing.json](smoke/bank/screen_timing.json).
The vendored bank SHA-256 is
`df3476d0823cff5eaed57fccf19f01e6a2699442be3139b5f05cb56e5f7aa15d`.
The exact frozen holdout ids/candidates are in [bank.json](smoke/bank/bank.json).

The initial development smoke completed all 112 searches in 190.4 s, including
45 independent solver verifications, all 16 C/T pairing checks, both fits and
reporting. Collection solved 45/64 (BE 20/32, PA 25/32), with no empty cell and
45 distinct tapes. Mean worker seconds/search including verification: collection
12.37, fresh G4 17.35, C 7.16, T 14.43. Fits averaged 0.157 s/corpus and reporting
took 1.48 s. This is throughput/yield evidence only, not an efficacy result.

Using the small blocks' measured effective utilization (7.78 collection workers,
6.70 scoring workers) projects 8627 s / 144 min for the approved full stage,
including fitting. Larger full blocks should amortize their final worker tails
better, but that is not needed for the three-hour ceiling. Set estimated_minutes
conservatively to 145, retain exactly the approved 5376-search roster and 10800 s
timeout; do not enlarge or redesign the experiment. Stage 2 extrapolates to about
121 min at the same difficulty/utilization, without timing any protected task;
strategy must reprice that continuation after full training results.

A forced internal-deadline run terminated its workers and produced explicit
incomplete execution (zero complete pairs, no efficacy eligibility, no holdout
searches). The full queue validates. Focused scientific tests check protected
split/seed rosters, low-yield fitting and empty-cell refusal, endpoint direction,
decision precedence, balanced prefix handling and cap sensitivity; 22 tests pass.
A second complete smoke on the finished implementation will be recorded in
[smoke.md](smoke.md), with its provenance and deterministic replay check.

Final smoke completed in 191.3 s with the same scientific observations and a
145.7-minute full-stage projection; estimated_minutes is rounded to 146. All
112 scientific search rows replay exactly, and all final source/binary and
schedule hashes verify. See [smoke.md](smoke.md) for the preparation record.
