---
estimated_minutes: 150
---

Implement the approved two-sum-v1 boundary test, using the unchanged D1331
(length-three lists over -5..5), primitives, cap 524288, population 256,
lexicase, crossover .7, mutation .03, two untouched elites, fragment rate .2
and suffix-preserving F operator. This implements the existing approved
proposal; it neither opens a new preregistration nor promotes findings.

Before any search, enumerate all six-role assignments containing all four
reducers, with each sum lexically ordered in the canonical reducer spelling
F,M,S,m. IDs are `TB:A>B?C+D:E+F`, representatives the lexically smallest ID
within each full-domain label hash. Reject constant gates; validate every
canonical (including excluded assignments) on every D1331 input in Python
and Rust. Apply the existing complete <=9-token screen, unchanged. Compare
with all 220 comparison-gate plus 86 then-addition behaviours, including
excluded cells. Reject agreement >=80%. Sort by SHA256("two-sum-v1:"+id),
greedily take 16 confirmation cells, at most four per unordered gate pair,
with mutual agreement <80%; continue to four timing cells, requiring the
same separation from all previously selected cells and the same gate quota.
Stop if any semantic gate fails; do not try another shape or domain.
Minimality through 16 tokens is unproved; the screen excludes only <=9-token
aliases and near-aliases, leaving 10-15-token shortcuts possible.

Freeze saved final 2033 A8/S8 (64 builds each), full 1036 C+F (16 builds),
G4, historical acquisition prices, backend/code hashes, bank and all seed
rosters together before stage 0. Validate artifact hashes, decoded fragment
edits, and sampled historical scientific replay before timing. No fitting
or new acquisition on the two-sum bank. Canonicals/screen witnesses never
enter the search envelopes.

Stage 0 uses 10 processes with RAYON_NUM_THREADS=1 (also scoring settings).
On each of the four timing cells run A8/S8/full_F under BE1 and PA1,
all four blocks, one seed each: 96 fitted searches. Run G4 four seeds per
cell: 16 searches. These 112 keys are diagnostic only. Seed base
206610092303: timing = base+1000000+corpus_index*10000+cell_index*100+block;
G4 timing = base+2000000+cell_index*100+ordinal. Confirmation fitted seeds
= base+corpus_index*10000+cell_index*100+ordinal (block=ordinal%4);
G4 confirmation = base+3000000+cell_index*100+ordinal. Arms share fitted
keys and 64 training cases, blocks retain equal weight. No timing keys
are confirmation keys. Freeze all 8-seed, 4-seed and S8-omitted schedules.

Use measured per-arm total search plus external verification seconds and
effective throughput at scoring concurrency to project each option
separately, always including the unchanged 256-search G4 roster. In order:
8 seeds (6400 total), 4 seeds (3328), 4 seeds without S8 (2304). Select the
first with projection *1.15 <=150 minutes. Preserve all 16 corpus units
and four blocks. Also require prepare/replay/report reserves, <=3h score
and <=45min prepare timeouts, and completion by 2026-10-10T07:12:10 local,
reserving the last hour before the actual 08:12:10 deadline for analysis.
Stop/report infeasibility if even the minimum option fails; forecasts of
solve rates/precision are scenarios and never admission evidence.

Primary ratio rho=cost(A8)/cost(full_F) uses paired log capped evaluation
cost (unsolved=2cap), equal cells/seeds then equal blocks within corpus,
16 corpus units, two-sided 95% t interval with 15 df. Report worker seconds
separately. Usefulness G4/A8 propagates G4 seed uncertainty independently
within every fixed target cell, sharing each G4 resample across all corpus
comparisons; resample fitted corpus units within BE/PA. All intervals
condition on the fixed selected targets. Full_F solve fraction must be
>=25% (512 solves at eight seeds, 256 at four) for retention. Report sigma
S8/A8 if included, full_F/G4, per-cell, per-source-family, solve rates,
1cap sensitivity, diagnostics and acquisition+N*arithmetic-search curves
at N=0,1,4,16,64,256,1024,4096 in evaluations and worker-seconds.

Interpretation fixed before running:
- rho UB<1.20, G4/A8 LB>1, full_F solve guard met: useful retention on
  this fresh target roster, carry A8 forward for strategy consideration.
- rho LB>1.20: material relative loss. Selecting full acquisition additionally
  requires full_F usefulness against G4 and acquisition curves at a stated
  horizon; relative loss alone cannot justify deployment.
- rho LB>1 and UB>=1.20: resolved loss with unresolved materiality.
- rho UB<1.20 but usefulness fails: bounded retention and failed usefulness
  are separate findings. Mostly timing-out fitted arms cannot count as success.
- Intervals spanning retention and material loss: acquisition choice unresolved;
  report the independent-corpus resolution price, no automatic top-up.
- Resolved sigma<1 suggests adaptive specialization, without identifying its
  cause. This single familiar-join output shape cannot establish general
  transfer, inherited adaptation, or addition-in-predicate transfer.
Return to strategy under every outcome. No post-score target filtering.

Critique disposition: notes 1-5 are implemented above; note 6 adds Keijzer,
Ryan and Cattolico (2004), Run Transferable Libraries, as the closer literal
reuse precedent alongside PIPE/DreamCoder. The contribution is the cost/
transfer boundary of this procedure. Notes 7-10 identify upstream notebook
wording; this role is prohibited from editing questions/digest/briefs, so
leave those corrections to the steward. This plan retains their narrower
one-sided bound, estimated horizon cost, observed recovery and D1331 scope.

Implementation verification: semantic bank build first; small capped searches
and historical replay next; full timing belongs to queued preparation. If
smoke measurements show the approved gates cannot pass, record measured
numbers in infeasible.md, commit and stop instead of queuing scoring.

Implementation and smoke evidence (no confirmation scoring)

- `smoke-bank/canonical_validation.json`: all 444 canonical assignments x
  1,331 inputs agreed in Python and Rust (zero mismatches). The full screen
  took 108.7 s; 333 nonconstant assignments, 289 distinct behaviours, 76
  eligible. `smoke-bank/bank.json` records the frozen 16+4 split. Committed
  bank byte SHA256 is
  `d2fc77e957f71ad71e8d7f9e720f8fb24824510e9670d025cd8271d3113ea451`.
- `smoke-final/smoke.json`: all 50 historical scientific replays passed,
  along with 10,000 suffix edits and 2,048 empty-fallback edits. The small
  search roster ran 28 diagnostic searches at cap 8,192 across both source
  families/all blocks, plus 10 full-cap searches on another timing cell.
  Full-cap mean worker seconds (including external verification): A8 9.81,
  S8 21.12, full F 16.02, G4 20.10. These small timing observations support
  continuing to stage 0; they do not set admission, estimate confirmation
  efficacy, or alter the selected bank. Smoke cannot produce an admitted
  preparation. The full 112-search timing roster remains in queued prepare.
- Current historical replay calibration is measured for each cheap arm,
  full F and G4. Worker acquisition curves convert historical G4 source
  seconds with current G4 replay; adaptive continuation and cheap overheads
  with the matching 2033 arm replay, and full-fit overheads with full-F
  replay. This is approximate calibration, not new acquisition timing.
  All historical acquisition evaluations remain charged exactly.
- `two_sum_run.py` wraps the existing sparse-feedback executor in a separate
  bank adapter, preserving the historical harness. All three full schedules,
  timing/replay rosters, method/backend hashes and accounting are frozen
  before timing. Scoring rejects smoke/changed handoffs and scientifically
  replays all 112 timing rows before any confirmation search.
- `pytest -q tests/test_two_sum.py tests/test_sparse_feedback.py
  tests/test_small_source.py tests/test_fragment_operator.py`: 29 passed.
  Tests cover the deterministic split, unchanged G4 sampling under every
  fallback, balanced blocks, all admission paths/deadline failure, shared
  baseline uncertainty, known ratio direction, the timeout success guard,
  full report/plots, historical price accounting and invalid handoffs.
  Ruff checks pass. Queue parsed with `scripts.queue_lib.load_queue`:
  two sequential entries, IDs prefixed as required, summed timeouts 13,500 s.
- The independent-corpus resolution price reports additional scoring cost,
  an explicitly labelled lower bound on repeated acquisition cost (policies
  share source attempts), and a three-hour agent-time scenario. No top-up
  is authorized by this estimate.

The original outcome rules and critique dispositions above remain unchanged.

Final verification is anchored to commit `74196a82db1a2b5b2cfacb812d6bd0e906a78e99` in
`smoke-committed/`: all 50 historical replays, 28 small-cap searches,
10 full-cap timing searches, 10,000 suffix edits and 2,048 fallback edits
passed again on the clean committed implementation. Full-cap means were
A8 9.98, S8 21.26, full F 16.04,
G4 20.15 worker-seconds. These remain diagnostics; queued stage 0
sets admission. No research/ files are included in the task-branch commit.
