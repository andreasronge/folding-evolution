---
estimated_minutes: 125
---

Implement the approved complementary-source replication without changing search,
decoder fitting, extraction, or edit laws. This is implementation of an already
approved experiment, not a new research-rigor registration or findings promotion.

Conditions and seeds
--------------------
Use the complete frozen comparison-gate `split.holdouts`: four BE and four PA
cells, recovered by a validated explicit loader. Keep the legacy training loader
unchanged. Sixteen independent acquisitions, indexed by the interleaved CORPORA
list (BE1, PA1, ..., BE8, PA8), learn only their own family's four cells.
Each gets 16 first-batch G4 attempts, 16 adaptive attempts under its own C4+F4,
and 16 static G4 continuation attempts. Pool first+adaptive for A8′ and
first+static for S8′. Failures and empty-cell/library fallbacks remain included.
The 768 collection attempts comprise 512 G4 and 256 adaptive searches.

Collection base 206610100145: seed = base + phase*1,000,000 +
build_index*10,000 + cell_index*100 + attempt_index, phase 0 first G4,
1 static G4, 2 adaptive. Smoke uses an additional 10,000,000 offset and only
BE1 and PA1; smoke artifacts cannot admit scoring. Check all source seeds
against the retained 1246/2033 collections. Never reuse historical source tapes
in a new build; those tapes are used solely for replay validation.

Confirmation uses 2303's unchanged formula: 206610092303 +
build_index*10,000 + target_index*100 + seed_ordinal (0..3). All sixteen
two-sum-v1 targets and all sixteen builds remain, giving 1,024 searches per
arm. Each new build has one artifact used for all four seeds. Historical delta
matches new build j, target c, ordinal s to historical corpus j, target c,
block s, ordinal s and the identical seed; the four historical block artifacts
are explicitly mapped in a saved pairing manifest. Pairing controls target
randomness, not source ancestry or equal per-build reliability.

Use 32 separate timing searches: BE1, PA1, BE2, PA2 × four frozen timing cells
× A8′/S8′, one seed each, with separate timing seed base. Fixed D1331, 64
training cases from rng([seed,0]), population 256, cap 524,288, exact verification,
F rate .2, suffix preserved, and all ordinary search laws remain unchanged.
Reuse 2303's 256 G4 rows, pinned by SHA and exact key roster; replay a sample
including both end cells. Historical A8 rows are contextual comparisons only.

Measurements and uncertainty
----------------------------
Save every collection/search row, intermediate and final tables/libraries,
source yields, empty cells, library size, attempts/provenance, fit/extraction/
verification time and all unsuccessful search costs. Save schedules before
collection, implementation/bank/build hashes, admission, and complete handoff
validation. Produce results JSON, per-family/per-cell summaries, solve counts,
between-build spread and plots from complete confirmation only.

Primary u = geometric capped-penalized G4/A8′ cost (failures = 2×cap).
Reuse 2303's cell-stratified G4 seed bootstrap, one shared baseline draw per
replicate, and resample builds within BE/PA (8 each), 8,192 fixed bootstrap
draws. The uncertainty units are 16 individual acquisitions, not 64 historical
blocks or target rows. Illustrative precision: single-build log SD .35 gives
SE .35/sqrt(16)=.0875; with shared G4 log SE .06, combined SE .106 and 95%
half-width factor exp(1.96*.106)=1.23. At spread .50 and G4 SE .08 it is
1.34. These are scenarios, not measured variances; the old .27 was a contrast
SD and cannot be used as the new build SD. At true u=1.8 the wider scenario
can remain unresolved; no efficacy-based sample enlargement.

Report delta = A8′/historical A8 on identical target keys, averaging paired
log differences per build, with a t interval on 15 df; call it a historical
roster comparison. Report sigma′ = S8′/A8′ (contextual 1.17), per-family/cell
effects, source and target solve counts, and sensitivity with failures=1×cap.
Compute A+N*S using arithmetic actual capped evaluations and worker-seconds,
charge first batch once per deployed arm and both adaptive fits, extraction,
and verification. Bootstrap prices jointly with build search costs and the
shared G4 baseline; report break-even distributions including never-repay
draws. The 1.5 geometric usefulness margin does not guarantee repayment in
100 searches. All metrics above need emitted report paths before queuing.

Admission, feasibility and stopping
----------------------------------
Historical source G4: 196/256 solves, 12.03 worker-s/attempt; expected ~392
G4 solvers here. Adaptive ~237/256 is an assumption from 2033's 92.5%, not a
measurement on the new roster. Historical target counts: A8 521/1,024,
S8 482/1,024, G4 51/256. Collection ~7.4k worker-s and full scoring ~64 min
at prior throughput justify the 90-minute expectation.

Before full queue: exact old-default decoder/library replay of one 2033 build,
source-membership and full-solver exclusion tests, fallback/edit audit,
small-scale collection and fitting on two builds with disjoint smoke seeds.
Measure full-cap collection at intended ten-worker concurrency. Stop with
infeasible.md if target validity, recipe gates, rates/runtime or deadline make
the approved design untenable; do not redesign or create an efficacy pilot.

Queue prepare (2,400s) then score (7,200s), total 160 minutes <8h cap and
proposal's 3h ceiling. Prepare collects/fits all 16 acquisitions and runs the
32 timing searches; first candidate fitting projection×1.15 plus handoff replay
and reporting reserve before 2026-10-10T07:12:10+02:00 is (a) both arms at
4 seeds, then (b) A8′ alone at 4 seeds; otherwise stop with a cost obstacle.
Include elapsed collection/fitting/validation/replay in actual-deadline checks.
Score rechecks hashes and scientific timing replay, refuses smoke/incomplete
handoffs, and observes the actual finish deadline. No solve-rate admission.

Interpretation fixed before runs
-------------------------------
* LB(u)>1.5: useful replication on this complementary development roster;
  carry the recipe toward a later genuinely new family, not a general claim.
* UB(u)<1.5: misses the chosen usefulness bar. Delta, rather than this threshold
  alone, supplies direct evidence of historical deterioration. Preserve the
  verified original artifact set; return to strategy for source checking.
* Interval spanning 1.5: unresolved; report the resolution price in builds,
  without automatic top-up. A timing stop provides no confirmation evidence.
* Poor A8′ with useful S8′ implicates the adaptive policy at this scope; both
  poor implicate this recipe/source combination. Neither separates yield from
  content or decoder from library. Dropping S8′ forfeits this diagnostic and
  never reduces the 16 primary builds.
* Broad delta/sigma intervals establish neither equality nor source dependence;
  near-one pooled delta does not show equal reliability of every build.

Scope: externally fitted bundled decoder/library; two existing source families,
one complementary roster, development targets, no inherited-evolution,
new-family, fresh-bank, semantic-module or family-specificity claim.
Critique notes 1–6 are implemented above. Notes 7–8 request digest/question-log
corrections outside the researcher's write scope; leave them for the steward,
and avoid those overstatements in all new outputs.

Implementation/smoke checkpoint (after the plan above was written): the full-cap
two-build smoke completed 96 collection attempts, four final artifacts and 16
reserved-cell target searches in 153.7 seconds. Mean worker-seconds were 10.60
first G4, 10.39 static G4 and 1.80 adaptive. The small target sample projected
109.7 minutes for both arms including 15% margin (114.6 with replay/report
reserve), at 7.10 effective workers. This still fits the approved 120-minute
score timeout; update expected queue wall-clock to 125 minutes including full
prepare. Smoke admission is disabled. The full prepare stage must use its own
32-search timing batch and actual-deadline admission; this checkpoint cannot
select an arm or supply confirmation artifacts.
