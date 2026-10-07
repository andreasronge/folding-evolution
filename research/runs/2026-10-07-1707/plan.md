---
estimated_minutes: 100
---

Implement the approved external solver-corpus fit without changing the search, bank, split,
alpha, corpus replication, or evaluation counts. Queue timeout is 8,100 s (2.25 h), with a
7,920 s internal deadline and 120 s reporting reserve, ten processes and one Rayon thread
per process. Initial expected queue wall-clock was 70–85 min including replay validation; the smoke
updates the conservative expectation to about 90–100 min (details in smoke.md).

Before collection, replay the first 20 sorted GG seeds of 0315 on the first BE and first PA
training cells against the frozen saved rows. Require identity of all saved scientific fields,
excluding seconds, decode_seconds, budget_seconds, phase and bookkeeping identifiers. Return
solver tapes only when requested; verify every saved tape independently on all 1,331 inputs.
All tables must pass Decoder, shape (25,24), range 24,000 and minimum count 250. Verify the
frozen bank and saved 1723 map hashes and reject holdouts from collection/training job payloads.

Full collection: 16 independent corpora/family, 48 G4 searches per own training cell, cap
524,288, P=256, length 32. Fit only first exact solver full tapes. Equalize each cell's
transition-count total to 1,600, including previous-token start 24. T is bounded L-BFGS-B
weighted likelihood from zero; C uses alpha 50 against G4; K uses exactly 400 fixed-point
steps of size 0.7 to match quantized C's uniform-latent, position-pooled 32-token marginal.
Log optimizer status, yields by corpus/cell, all tables and hashes, K max errors and fit times.
K is valid iff max error <=0.001. Required validation failure, any collection cell below
24/48, more than four invalid K fits/family, or incomplete stage 1 stops comparison claims.
K mismatch alone is an allowed exclusion, not required scientific/table validation failure.

Seed allocation (all integers, disjoint from the steward probe): base 2,026,100,717.
A phase adds phase*1,000,000; a family adds family_index*100,000 (BE=0, PA=1);
a corpus adds corpus_index*2,000; a cell adds cell_index*200; then seed_index.
Collection phase 0; training phase 1; holdout phase 2; G4 training reference phase 3;
1723 descriptive maps phase 4 (map index in corpus position); G4 holdout phase 5.
Smoke uses separate base 2,126,100,717; the 48/cell feasibility probe uses base 2,226,100,717.
Cell stride 200 accommodates the 128-seed G4 holdout block without overlaps; corpus stride
2,000 accommodates six training cells. The initial diagnostic used strides 100/1,000
(which were disjoint at its reduced evaluation counts); confirmation uses the corrected rule.
Within a corpus/cell, T/C/K share seeds; blocks across corpora, cells, families and phases
are disjoint. The identical replay seeds are exclusively validation, excluded from estimates.

Stage 1: T/C/K each receive 32 fresh seeds per own-family cell per corpus (15,360 searches
when K validates); G4 gets 96/cell (960); the twenty frozen 1723 maps get 16/own cell (1,600).
Stage 2: all corpora's frozen fits get 32/each of three holdouts (9,216 when K validates),
G4 gets 128/holdout (384). Admission requires complete stage 1 and remaining work time
strictly greater than 1.5 times projection. Update projection using actual stage-1 costs
and throughput, with the three holdouts' saved G4 timings as a conservative difficulty
factor; no holdout searches occur earlier. Record projection and skip reason. It is a time
gate only, independent of the result. An unfinished holdout stage is descriptive partial
coverage, never a complete transfer estimate.

Primary measurement is mean log2 evaluations, unsolved charged 2*cap; also report 1*cap
sensitivity. Within corpus: equal-weight cells; within pooled contrast: equal-weight family
means. Pooled SE=0.5*sqrt(SE_BE^2+SE_PA^2), t_15 (use the smaller valid family df for a
K-valid subset); report delta and speed=2^(-delta) with 95% CI, per-family contrasts and
observed corpus spreads. Preserve all-corpus C/T as the procedure estimate. Attribution
requires C/T and C/K on the identical K-valid subset; scope it to that subset if exclusions
occur. Unresolved C/K does not establish C equals K.

Outcome rules before observations: row 0 is the feasibility rule above; row 1 requires
all-corpus C/T lower>1 and K-valid C/T and C/K lower>1 (scope to K-valid subset); row 2 is
all-corpus C/T lower>1 without that attribution; row 3 is C/T lower<=1 and upper<1.10;
row 4 is lower<=1 and upper>=1.10. Rows 1–2 support procedure improvement, with row 1
separating gain from pooled emitted frequencies. Row 3 bounds this full-tape estimator,
smoothing and corpus, not assembly information in general; row 4 leaves it unresolved and
requires a reported sample-size estimate from observed spread. These fits are external
fitting, not evolutionary discovery, and do not isolate mutation/crossover mechanisms.

Holdout C/T and C/K use per-corpus equal means across three cells and t over 32 corpora
(or validated subset). In rows 1–2, lower>1 means transfer; lower<=1 and upper<1.10 excludes
a >10% gain; otherwise unresolved. Else holdouts are descriptive. Matched/mismatched C per
holdout uses Welch over 16 vs 16 corpora. Useful family adaptation also needs matched C
improvement over G4, not just mismatch slowing. BE transfer covers one task.

Always report C/G4, T/G4, T versus own-family 1723 maps (unpaired procedure comparison),
solve rates, per-cell collection yields, exclusions and arithmetic work. Charge collection
failures and fitting in break-even: actual collection evaluations divided by arithmetic
mean capped-evaluation savings over G4, and collection+fit worker seconds divided by mean
seconds savings. No finite break-even for nonpositive savings. Relative C/T benefit alone
is insufficient to call a fit practically useful if it damages G4. Plots show search costs,
fitness/diversity curves and corpus contrast variability; bond counts do not apply to this
token-decoder experiment.

Implementation validation: small deterministic tests of tape-return compatibility, exact
transition weighting and marginal fit, seed roster/counts, deadline admission and interval
rules. Smoke the full 48/cell collection for one corpus/family, then a small evaluation;
check timings/yields and all tape/table validations before queue construction. A separate
small end-to-end smoke exercises reporting and holdout admission using reduced counts,
clearly labeled smoke_only and never used as evidence. If measured design infeasibility
arises, stop and write infeasible.md; do not change approved parameters.

Critique 1–5 are addressed above. Critique 6–7 concern prior digest/question claims, which
the researcher is prohibited from editing. Their stronger assertions are not used here;
carry those corrections to the steward: C0/T=0.932 [0.860,1.010] and selected-mutant versus
parent delta=-0.017 [-0.085,+0.041] have unresolved direction. No equality, plateau or causal
allocation finding is assumed.
