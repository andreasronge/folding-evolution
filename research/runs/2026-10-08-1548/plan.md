---
estimated_minutes: 135
---

Implement the approved proposal, with no refit and no target search during preparation.
This is implementation of an approved design, not a new preregistration or a
findings update. Task artifacts stay here; code/data are committed on the worktree
branch without research/ files.

Conditions and freeze

- Retain deterministic enumeration of all 240 then-addition A>B?C+D:E programs
  on D1331 (all length-three lists over integers -5..5). Check every canonical
  in Python and Rust. Deduplicate nonconstant-gate behaviours by smallest ID,
  exhaustively screen all executable tapes through nine tokens using FirstMachine,
  reject agreement >=80%, then require <80% agreement against every v1 behaviour
  (the whole distinct nonconstant v1 roster, not just training/holdouts). Exclude
  exact 1603-bank aliases. Record IDs, aliases, exclusion reasons, agreement and
  witnesses. Expect counts 240 -> 162 -> 86 -> 37 -> 16 before old-bank exclusion;
  any disagreement stops preparation for review. Old-bank exclusion may reduce
  the final roster transparently; never replace a cell based on performance.
- Pin the bank file SHA and source corpora.json/freeze.json SHA; validate all
  C/T tables against 1246 freeze hashes. Preserve its complete D roster and seeds,
  and require 16 non-smoke fitted corpora (BE1/PA1 through BE8/PA8). Freeze both
  target schedules, method, seeds, source/training scores, bank and table hashes
  before any target-row execution. No fitting or canonical tape enters a search.
- Row F: all retained fresh cells, C/T 8 paired seeds per cell per corpus,
  G4 16 independent seeds/cell. At 16 cells this is 4352 searches. Row D:
  unchanged 1246 frozen 4352-search roster on the eight v1 holdouts (C/T 16
  paired seeds/cell/corpus and G4 32/cell). Both use cap 524288, P256, tape32,
  unchanged search parameters, exact D1331 solve check and fresh populations.

Seeds, smoke and queue

- F base 202610081548; phase 6 C/T and phase 7 G4, using the existing injective
  base+phase*1000000+(family==PA)*100000+corpus_index*10000+cell_index*200+seed_index
  rule (the 16-cell roster requires a 10000 rather than 2000 corpus stride). D uses the exact saved 1246 holdout roster. Check collisions within and
  across both rows and against all source searches. C/T alone share seeds.
- Smoke uses only the eight v1 TRAINING cells, frozen BE1/PA1 tables, two paired
  C/T seeds per own-family cell and two G4 seeds per training cell: 48 searches
  at full cap. Smoke base 202710081548, phases 6/7. No fresh or holdout timing,
  G4 screening or performance-based bank selection. Reuse search batching and
  worker validation, verify deterministic replay on a small training subset,
  and exercise forced deadline/error checkpoint paths without target searches.
- Full queue: F timeout 14400 s, D timeout 12600 s, total 7.5 h. Ten workers,
  reserve 120 s for reporting plus 120 s before the outer timeout. Expected
  135 minutes is historical 2.2 h plus reporting, not a worst-case guarantee.
  Reprice training smoke if measured rates invalidate the approved assumptions;
  do not time protected targets to improve the projection.
- G4 first, then whole fixed corpus pairs BE1/PA1 through BE8/PA8. Save each
  search and checkpoint each block. Analyse only the largest fully completed
  initial balanced prefix; >=6 complete pairs needed, otherwise incomplete.
  Never accept a partial pair or fallback efficacy result after any error.
  Report complete pair/corpus counts, trailing observations and stop reason.

Measurements and outcome meaning

- Primary F exp(mean_corpus(mean_cell_seed(log(cost_T)-log(cost_C)))) with
  unsolved cost 2*cap and a two-sided 95% t interval across balanced corpora.
  First apply completeness/error eligibility; then flag severe shared censoring:
  if both arms solve <25%, this is a capped endpoint, not search speed or evidence
  of useful uncapped transfer. Always report per-arm/per-cell solve counts;
  above 25% does not make censoring harmless.
- Ordered numerical rule: LB>1 means resolved relative C/T gain on the frozen
  selected new-shape bank (if UB<1.10 also, resolved but below 10%). Otherwise
  UB<1.10 means gain bounded below 10% at this cap, consistent with shape
  specificity, without identifying its cause. Otherwise unresolved; report
  additional balanced corpora for precision/detecting the observed gain, priced
  at historical 423 s acquisition per corpus plus measured scoring.
- D is secondary within-shape generalization on a development bank. D positive
  with F bounded is a boundary on then-addition's selected tie-heavy F>m/M>F
  behaviours; branch placement, gate selection and behaviour distribution are
  not separated. D and F positive support reuse of corpus information at this
  method/bank scope. Wide F intervals, incomplete prefixes or severe shared
  censoring leave the central useful-transfer question unresolved.
- Report intervals only for per-cell C/T and leave-one-cell-out range, F source
  family BE-minus-PA, D matched-versus-mismatched family and own-family holdout
  minus training shrinkage (same corpus), F minus training shrinkage, 1*cap
  sensitivity and descriptive unpaired C/G4 and T/G4. Preserve source training
  rows so comparisons match family/corpus and sample units. If C beats T but
  both lose to G4, this establishes relative fit superiority without useful
  adaptation against G4. K stays unscored; C/T does not isolate token order.
- Persist search.jsonl including evaluations/solves/case indices/hashes/curves,
  config/bank/schedules/freeze/validation/progress/timing/result JSON, report.md
  and diagnostics.png. Corpus intervals condition on this selected bank, not
  arbitrary shapes. Runtime/checkpoint correctness is checked before queueing.

Critique dispositions

1–3: retain source procedure, honest timeout scenarios, balanced prefixes and
reporting reserve; implement/retain complete semantic audit and freeze. A semantic
mismatch stops for review. 4: use restricted boundary language and censoring
precedence above. 5: restore D matched/mismatched and own-family shrinkage;
F source-family contrast has no matched training shape; G4 and censoring qualify
interpretation. 6: approved known-procedure transfer test needs no new literature
search. 7: digest observations are outside the researcher write scope, deferred
to steward, without endorsing unchanged claims. No code_review.md or
driver_feedback.md was present at preparation start.

Feasibility stop

If bank semantics or frozen artifacts disagree, or training smoke shows the
approved runtime/design cannot work, write infeasible.md with measured numbers
and a concrete alternative, commit the implementation and end without a queue.

Preparation measurements (after the pre-run plan)

The complete semantic build reproduced {'raw': 240, 'nonconstant': 162, 'distinct': 86, 'nine_token_survivors': 37, 'fresh_before_old_exclusion': 16, 'final': 16} in 108.5 s,
with all 240 × 1331 canonical cases agreeing in Python and Rust. The final bank
SHA-256 is `26be2d562275ff908b9874667b80ac88795984fb74c2ce3d8dc2738f726e5748`.
The probe-order reducer counts reproduce S3/M5/m4/F4. Two equivalence
groups span repeated-reducer inventories, so lexicographic canonical IDs instead
give S3/M4/m3/F6; all 16 behaviour hashes are unchanged. Both conventions and
alias reducer sets are retained, rather than treating representation as new cells.

Both rows contain exactly 4352 searches; D equals the saved 1246 holdout
roster byte-for-byte at the row level. Both rosters and the 48-search training
smoke use collision-checked blocks disjoint from all source searches. All
source file hashes and 48 C/T/K table hashes validate, without fitting.

The first smoke completed 48 training searches in 87.3 s including reporting.
Mean worker seconds/search were C 4.46, T 7.70, G4 15.76; 16 C/T case pairing
checks passed. This is throughput evidence only, with no target efficacy result.
Projected per-row training-difficulty time is about 51 min at historical 9.57
effective workers, or 93 min using this tiny batch's tail-limited 5.24 workers.
Retain the historical expected queue estimate of 135 min and approved 7.5 h
timeouts: fresh difficulty remains unknown and completion is not guaranteed.
No fresh/holdout search was timed.

Thirteen focused tests pass, covering semantic audit, source/table provenance,
seed collisions, unchanged D, payload protection, corpus endpoint direction,
missing/duplicate rows, complete balanced prefixes, no error fallback, matched
family shrinkage, cap sensitivity, decision precedence and shared censoring.
A forced deadline produces an explicit incomplete checkpoint; an injected
validation error exits 1 with validation failed and no efficacy eligibility.
Queue format validates with two entries and exactly 27000 timeout seconds.
Final smoke on the committed implementation and deterministic replay are recorded
in [smoke.md](smoke.md). No protected target searches ran during preparation.

Final committed smoke completed in 88.8 s, reproducing
all 48 scientific search rows exactly. Source/binary/freeze hashes validate;
[smoke.md](smoke.md) records preparation against commit `45b2bdb2cbe5dee7ef04c3b5ebc10c54ce3e233a`.
