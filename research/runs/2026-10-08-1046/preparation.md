# Preparation admission

Implemented and committed as `a804f4f26d4d4874d22abf14a6af64be02e8bf6b` on `research/2026-10-08-1046`. Worktree is clean. No research/ files are in this commit; all task artifacts are in this main-checkout run folder. The full experiment has not run during preparation.

The original source is `/Users/andreas/developer/folding-evolution/experiments/output/2026-10-08/2026-10-08-0918-acquisition`, clean commit `511711c35cfaada094184ea6c4fa616503b01ee4`. Source manifest, recorded code hashes, all 80 row identities, per-row scientific config, effective program seeds and modifier streams validate. The only incomplete source is max/inherited/14, with 30 complete episodes and one partial episode. No Rust sources changed from the approved commit; this worktree's Rust extension is available.

Implementation adds `recover` and `recovery-timing` modes. Recovery preserves acquisition phase `main` and original seeds; no recovery-specific scientific seed stream exists. It reruns the fixed two complete controls and cut run at three workers, compares theta/probs exactly and all completed episode endpoints (plus training/census/verification bookkeeping), omits runtime from equality, then copies 79 unchanged source files with source paths and SHA-256 hashes and writes the completed cut row. Replays stay separately preserved under selective/. A failed replay invokes the complete 80-acquisition fallback at ten workers, using the remainder of the same 9000-second recovery envelope. It refuses fallback if the modeled complete replay cannot fit that remainder. Incomplete output cannot publish ACQUISITIONS_COMPLETE or enable scoring.

Removed hidden 1200/600-second acquisition/scoring defaults. Explicit deadlines remain for preparation and recovery, all documented in plan.md. Frozen inference scoring has only the queue's stage deadlines, no per-job cutoff. Every queue command pins RAYON_NUM_THREADS=1. The existing scientific law and bootstrap are unchanged; analysis continuation wording now correctly names a development-bank threshold-2 extension.

## Measured repricing

The fixed preparation roster was written in plan.md before any searches: five acquisition vectors per family/arm, both targets, indices 2000–2001 (80 searches), plus all three references on both targets/families at index 2002 (12 searches). All 92 searches completed in **279.824 s**. No index 0–15 or threshold 2 was exposed. These are clustered feasibility observations only: sum inherited/broken solved 15/20 and 18/20, max inherited/broken 10/20 and 9/20. No effect estimate, inference verdict, precision assertion or vector selection uses them. The earlier small probe's sum 2/4 versus 2/4 and max 10/12 versus 1/8 likewise remain feasibility-only and excluded.

Pricing uses 320 searches per learned arm/target cell and 16 per reference/target cell, ten workers, and a 0.9 × observed slowest-search final-worker allowance. See [timing/projection.json](timing/projection.json), [timing/timing.json](timing/timing.json), [timing/timing_roster.json](timing/timing_roster.json), and [cost.json](cost.json).

| Stage | Expected seconds | Timeout seconds |
|---|---:|---:|
| Selective recovery | 1920.6 modeled | 3600 within A |
| Full fallback, if required | 5450.6 modeled additional | remainder of A's 9000 |
| Sum scoring | 779.4 measured roster projection | 2400 |
| Max scoring | 4066.8 measured roster projection | 5400 |
| Analysis | reserve 300 | 300 |
| Preparation timing | 279.8 measured | reserve 900 |

Max has **5/40 learned searches** with verifier time >=60 s (all-row rate 5/46). Their 822.251 measured verifier seconds project to 26312.0 verifier worker seconds in the full roster. Slowest max search took 260.126 s. All tails and completed cap censors remain in the cost data. Learned arm means are 39.566/19.885 seconds for max and 4.159/6.365 seconds for sum; equal roster weighting matters. References are priced separately. The sum allowance includes a 34.323-second fit-reference search and a 43.750-second learned search. The max point estimate is **67.8 minutes**, below the fixed 75-minute split trigger, so C stays in the main queue. Small clustered timing and one observation per reference/target provide no completion guarantee; max has about 22 minutes of timeout headroom above this point price.

The earlier 3741.851-second acquisition stage was incomplete, not a complete replay measurement. The cut's 1200.344 seconds extrapolated linearly from 30/48 completed episodes gives 1920.550 seconds; original measured worker times plus a final-worker allowance give 5450.640 seconds for a complete replay. These estimates are conservative extrapolations with no claim of validated throughput. An unused selective allowance can fund fallback; if an especially slow failed attempt leaves less than 5450.6 seconds, recovery stops for replanning rather than renewing the allowance.

Normal full queue estimate is **117.779 minutes**, fallback branch **208.623 minutes**, plus 4.664 minutes preparation timing. Queue timeout sum is **17100 s**, plus the 900-second preparation allowance = **18000 s / 5 h**, including every branch. Agent preparation was about 15 minutes (started 11:03:56 local); reserving 90 minutes downstream review/analysis gives normal expected full cost about 3.8 h and fallback about 5.3 h. Even conservatively charging the entire five-hour timeout envelope plus 30 minutes preparation plus 90 minutes downstream work fits the seven-hour ceiling. Splitting or retrying cannot reset these allowances. Queue sizing remains 80 acquisitions and 2752 inference searches.

Timing ran during implementation and its manifest honestly records a dirty worktree and source hashes. Later changes added fallback-budget reporting/tests, tail accounting and corrected scope wording; acquisition/evaluation/seed laws used for timing did not change. The final clean smoke is anchored to the final implementation commit. An initial source-validation attempt exposed a validator mistake (raw seed versus effective config seed); it was corrected before any preparation search ran. Failed attempts did not yield omitted timing searches.

## Validation

- **134 targeted tests passed**: inherited-bias mechanism, endpoints, ordering, sigma-zero replay, complete/partial rosters, staged analysis/plots, TAG/evolution and bias regressions; exact replay versus runtime variation; selective provenance; full replay fallback; refusal when fallback exceeds the remaining budget; explicit-only job deadlines; balanced timing roster and tail-preserving weighting.
- Small four-cell smoke at P=32, two episodes and three reproduction generations/episode passes: six reproductions, eight censuses and 256 population evaluations per acquisition. Final rerun is [smoke-clean/manifest.json](smoke-clean/manifest.json), clean final commit, with [smoke-clean/smoke.json](smoke-clean/smoke.json).
- Ruff and git diff whitespace checks pass.
- queue.yaml parses through scripts.queue_lib.load_queue: four unique correctly prefixed IDs, pinned Rayon, RUN_DIR outputs, validated shell syntax, 17100-second timeout sum. No full acquisition or inference scoring has been launched.

## Critique disposition

1. Timing roster was fixed before observations; arm/target and reference costs are weighted correctly, every tail/failure retained. Timing solve observations are feasibility only, not acquisition rates or effect estimates.
2. Master/phase/config/extraction remain unchanged; runtime is excluded from exact replay equality; source hashes and both provenance layers are kept. Complete-roster gates and explicit-only deadlines prevent missingness-as-censoring. Both selective and full-fallback branches are priced cumulatively, including preparation timing and agent/review reserves; unused selective budget may fund fallback without increasing the envelope.
3. This remains a self-adaptation mechanism test of frozen token distributions after discarding carriers. No claim of a new self-adaptation principle or contextual decoder is added; no modifier tuning is authorized.
4. Preserve the capped-cost endpoint, solve counts, between-acquisition log-cost SD and review-time extension price. Both learned arms fully censored leave linkage unidentified; broad R_u intervals remain unresolved. Similar benefits do not identify inheritance or task-generic supply. S lower<2 is only absence of an established twofold disadvantage; upper<2 supports within-twofold.
5. Training targets are development-bank evidence. Threshold 2 is an extension on that bank, not a fresh transfer bank; continuation wording is corrected in code.
6–7. **For the steward:** question/digest/log corrections are outside this role's authorized write scope. Replace “drift equally far” with “Both arms reached similar observed mean distances from uniform (L1 0.90–0.93).” Replace mutation-only/neutral-drift causal attribution with “The movement is consistent with substantial drift; its contribution relative to selection was not isolated.” Weak cross-replicate correlations suggest a possible shared component; its size, cause and usefulness remain unmeasured. No question, digest, log or brief was edited here.
