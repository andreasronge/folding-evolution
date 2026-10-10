---
next: proposal
---
# Decision 2026-10-10-2239: continue 43, moving only the scoring seed base

**Outcome.** The retry of the A8 versus closure-based subtree GP comparison stopped before any target
search ([infeasible](infeasible.md)). The corrected initializer worked: depth 1–3 edges, function roots at
initialization, balanced six bins, full depth 3 accepting 72%. A complete development search smoke ran.
Forced full-cap tree searches took about 50 s each at ten workers (effective concurrency 9.1), in line with
the 51 s planning figure. The run stopped at the plan's own seed audit. The seed formulas I carried over
unchanged from plan 2214 overlap: calibration `22140000 + 1000·(8f + c) + r` and scoring
`22150000 + 1000·(8f + c) + 2b + r` share 48 seed values (96 searches on each side), and both smoke seeds
are TS scoring seeds. I checked the arithmetic: 16 indexed cells span 15 000, but the bases are only 10 000
apart. The comparison produced no A8/tree evidence, and no slot was used (43: 1 left; root 10: 35 budgeted,
34 used).

**Decision: continue 43 (re-propose with scoring base 22180000), not strategy**, because:

- The obstacle is an arithmetic error in the pre-registration, not a measured property of tree GP, of A8,
  of validity or of price. Moving one constant fixes it. Scoring then spans 22180000–22195115, disjoint from
  calibration (22140000–22155007), smoke (22160000–) and the 1 544 saved acquisition/replay seeds
  ([prospective audit](alternative-seed-audit.json)). A grep of all run folders finds no earlier use of
  that range.
- Everything that was measured matched the plan's premises. Preliminary projections (DG 4 048 s, TS 3 223 s
  against gates of 5 760 and 4 320 s) are planning figures, not Stage 0 admission, and all the
  inherited gates stay binding.
- This departs from the letter of proposal 2239's exit clause ("if the corrected initializer or any later
  gate fails, park 43 and go to strategy"). That clause, like strategy 2214's early exit ("measured
  validity, build or complete-cost obstacle"), was meant for obstacles that say something about the
  baseline or the cost. This one says nothing about either. A strategy review would buy the same
  comparison again, one agent cycle later. The proposal states the departure so the critic can send it to
  strategy if it disagrees.
- From now on the rule is strict: any failed gate in 2254 parks 43 with the measured obstacle and goes to
  strategy, with no further amendment.

**Tree updates.** 43: log entry (preparation observations, the collision, corrections), question.md
(summary, heading "closure-based", explanation (b), links, reopen rule). Root 10: log entry, summary line
for 43, child list, budget note. Digest: "as of" line and the root-10 "Not shown" line. No belief changed,
because the run produced no comparison evidence. The preparation timings are logged as observations
only. Parked questions: none of their reopen conditions involve tree-GP preparation, so none is met.

**Digest check (critique 2239 notes 6–8) fixed.**
- Note 6: "cannot fill" now reads "failed the 10 000-draw bound and is impractical at the measured
  acceptance (1.2 × 10⁻⁷)" in the root question and in 43. Log corrections are appended.
- Note 7: the digest and root question now give both within-table TS contrasts with their own bounds:
  T table 1.01× [0.83, 1.25] and D table 1.00× [0.79, 1.27], equality not shown.
- Note 8: the 43 heading now says closure-based subtree GP. Explanation (b) now reads "the complete generic
  tree procedure matches or beats A8; the responsible structural feature remains unidentified".

**Next:** [proposal 2254](../2026-10-10-2254/proposal.md).
