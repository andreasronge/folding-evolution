---
next: strategy
---
# Decision — 2026-10-06-1603 (four-reducer FIRST bank)

**Close [15](../../questions/10-compositional-map-transfer/15-four-reducer-family-bank/question.md);
return to strategy. No proposal for 1723.**

The [analysis](analysis.md) labels the outcome Table A row 1, and I agree. The data are
complete and validation passed. The screen is exact and Rust-checked. Branch-else has no
holdout pair whose (role, reducer) combinations are covered by its training cells, on any of
D625, D1331 or D2401. In BE's `then` role, S, F and M each occur in only one surviving cell. Under the
frozen split rule this candidate cannot carry the symmetric matched/mismatched test. Row 1 says
close 15 and return to strategy. The 1536 strategy also asked to return after feasibility.
Root 10 now has 6 of 7 slots used. Its last slot was reserved for a matched/mismatched
comparison that now has no symmetric bank. Changing the split rule after seeing the data, or
choosing a new candidate, is the strategist's call, not mine. So I write no proposal.

## What the strategist gets from this run

- **Split obstacle:** BE has 5 surviving cells and no covered pair. One BE cell, `S?m:(M+F)`,
  can be held out alone with all roles covered. PA splits with holdouts `(F?S:M)+m` and
  `(S?M:m)+F` and 6 training cells. On D2401 the split picture is the same as on D1331.
- **Headroom and tractability:** G4 solves 45–50/50 on all 13 cells, with KM medians 8.7k–28.7k
  (2–7× the 4 096 line). F4, G4 and G4-marg medians are ≥ 10.7k on both PA holdouts. On all
  four BE training candidates, G4 solves 45–49/50.
- **Hand-set family grammars (descriptive):** matched over swapped is 1.68× [1.39, 2.05] on BE
  and 1.32× [1.12, 1.57] on PA. The paired context-over-marginal contrast is resolved in both
  families (lower bounds 1.09, 1.16), so for these priors the preference sits in context. Only
  the BE grammar beats G4 on its own family (1.36× [1.04, 1.75]). The PA grammar does not
  (0.87× [0.75, 1.04]). Strategy 1536 said context gets a secondary arm only with "a measured
  training signal or useful decoder-capacity diagnostic". This is such a diagnostic, but for
  hand-set rows only. It does not undo the evidence that learning context was weak: 0132's C
  showed no resolved gain, and 0811's R was ≤ 1.11× over M+ on training.
- **Cost:** G4 takes 0.4–1.2 s per 65k-cap inner search and about 1.9 s per full-cap search.
  One 25-generation token-learner trajectory costs roughly 35 min on 10 workers, about 70 min
  with the 2× slower-candidate allowance. Slot 7 must be sized from these, not from 0132.

## Options for root 10's last slot, with my recommendation

1. **Asymmetric crossed design on this bank (my recommendation, if strategy accepts the rule
   change).**
   - Train token-multiplier maps on PA's 6 training cells and on the 4 BE cells other than
     `S?m:(M+F)`.
   - Score both on the 2 PA holdouts and the 1 BE holdout, plus fresh training.
   - This gives a matched/mismatched contrast in both directions, but the BE direction rests on
     one cell, so it is a weak test.
   - About 4 independent trajectories per family (≈ 8 × 35–70 min) plus scoring fit one queue
     of up to 8 h. That is enough to see a large crossed effect, not a small one.
   - It changes the frozen "≥ 2 holdouts per family" rule after seeing the data. The strategist
     must approve that explicitly, and the brief must label it.
2. **One-direction design:** train on BE (all 5) and on PA (6), then score both on the PA
   holdouts only. Simpler, but it answers only "is PA adaptation PA-specific?".
3. **Stop root 10 here.** Its answer so far: learned token weights on G transfer about 2× within
   and near one family; learned contextual increments are unresolved; no symmetric two-family
   bank has been found in three attempts. Spend the remaining autonomous budget on root 01's
   supply-versus-variation question or a new root.

I lean towards option 1 over option 3: the bank, harness and costs are now measured, and
specificity is the gap strategy 1536 named. But this is a judgement on one cell's worth of BE
holdout, and option 3 is defensible.

## Parked questions re-checked

No reopen condition is met. 08 needs a non-constant-threshold alphabet, 09 reopening, or a
decoder-rule plan with owner go-ahead. 09 needs a no-lift speed-up on more than one task; this
run measured no sampling lift. 02, 04 and 07 depend on the shared-helper line, which stays
stopped.

## Digest check (critique 1603 notes 5–8)

The working digest and the root-10 and question-14 summaries already carried the corrected
wording. I fixed the last remaining phrase in 14's question.md ("selection of six particular
learning runs" now reads "depends on the learning run in this sample; selection as an isolated
cause is not shown"). I appended correction notes to 14's log and root 10's log, without
rewriting the historical entries.
