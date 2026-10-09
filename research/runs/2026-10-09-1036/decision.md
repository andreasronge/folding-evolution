---
next: strategy
---
# Decision: run 2026-10-09-1036 — close question 32, return to strategy

**Result.** Frozen whole-corpus fragment libraries (F), C-chain blocks (W) and plain C were run on
C's unchanged search (commit `348f9e2`). The roster was complete: 15 360 rows. All prepare and
handoff checks passed: libraries equal to 0843, edit audits, bit-exact C replays, 0 padded-fragment
solvers and 96 smoke replays.

On then-addition-v1 (primary; 16 corpora × 16 cells × 16 seeds):
- F/W **1.195× [1.111, 1.286]**, 14/16 corpora favour F; both-solved pairs 1.15× [1.09, 1.22].
- F/C **1.466× [1.380, 1.558]**, 16/16 corpora.
- W/C 1.227× [1.148, 1.311].

On the 8 protected comparison-gate holdouts (reference): F/W 1.27×, F/C 1.75×, W/C 1.38×.

Pre-registered rule 2 fired: `repertoire_earns_acquisition_review`. I guessed F/W 1.05–1.15, F/C
about 1.4 and W/C about 1.25. F/C and W/C were right; F/W came in slightly higher. F/C's change
from training is 0.93× [0.83, 1.05], unresolved. By contrast, C/T lost a third across the same
shape change. ([analysis](analysis.md))

**Decision: close 32 and return to strategy (`next: strategy`); no proposal written.** Because:
1. **The question is answered at its tested scope.** Do learned fragments speed fresh search
   beyond C? Yes on training cells, on protected holdouts and on one excluded shape, against both
   C and a library-free control. More precision on the same banks would not change a decision.
2. **Rule 2 routes to strategy.** It asks for a review of *acquiring* a repertoire. That is a
   different question with no design or price yet, and strategy 1036 asked to come back after
   this result.
3. **No slots are left.** Root 10 has used 24 of 24; 32 has used 2 of 2.

The limits stay attached. Both banks are development banks, and the libraries are shared syntax
that then-addition needs by construction. On this shape there was no supply control. The F/W
lower bound clears the worthwhile 1.10× by only 1%, and not in the both-solved or BE-only
sensitivities. So a true increment above 1.10× is not established. Nothing was acquired.

**Tree changes.**
- [32](../../questions/10-compositional-map-transfer/32-learned-fragment-operator/question.md):
  closed. Its summary and log were updated, and it has a new reopen condition.
- Root 10: budget line, sub-question entry and log updated.
- Digest: added "Frozen whole-corpus libraries keep that advantage on the excluded compositions
  tested". The W bullet now carries the across-shape numbers, and "Overall" was updated.
- Older 27–31 bullets were condensed to stay under the word limit. Their full wording is kept
  verbatim in root 10's log.

**Digest check (critique 1036, notes 6–8): all fixed.**
- Note 6: "all intervals above 1" now applies to bank 11 only, with "15/16 cell contrasts resolved"
  for bank 12.
- Note 7: in 32, "Marginal blocks do not" is now "no resolved gain; gains above about 4.4%
  excluded".
- Note 8: in 32, "F is no better than C" is now "F/C is unresolved on this cell, 0.99× [0.70,
  1.41]; F is worse than W in the descriptive comparison".

**Parked questions.** No reopen condition is met.
- Root 23 needs a changed inheritance rule with a measured selectable signal. An externally fitted
  library is not one.
- Root 01's 02/04/07/08/09 concern the helper and threshold lines, which this run does not touch.

**For the strategist to weigh.** These are my ranking, not priced designs. The run has used 11 of
40 experiments, and the deadline is 2026-10-10 08:12, about 18 h away.

1. **Can a useful library come from a cheaper source? (acquisition cost)** The repayment arithmetic
   shows the gap. F saves about 0.5 worker-s per then-addition search over W. Extraction costs
   4 s, but the solver corpus cost 48 039 worker-s, about 96 000 searches of saving. Two cheap
   source sets already exist:
   - 27/28's pre-solve parent tapes;
   - a handful of solvers per cell.

   Scoring F built from them against W on training cells and then-addition would show whether a
   repertoire can be had without exact solvers. That is the step toward acquisition rule 2 asks
   for. A within-run harvest from the population's own elites (ARL-style,
   [Rosca 1995](https://cdn.aaai.org/Symposia/Fall/1995/FS-95-01/FS95-01-011.pdf)) would be the
   endogenous version, but it needs new engine work. Knockout activity on non-solvers needs a
   definition, so a stage-0 probe should come first.
2. **Why W beats C (mechanism, cheaper).** One arm could make C's point mutation keep the decoded
   suffix; another could give W blocks uniform content. Together they would split suffix-preserving
   locality from chain content, on training cells, in about 75 queue min. This matters because
   W/C is 1.2–1.4× on every bank, and W needs no library. Across then-addition cells, F/W and W/C
   correlate −0.67 (post hoc), so fragments and chain blocks may partly substitute for each other.
3. **Lower value now.** Two other options rank below these: a B (supply) arm on then-addition,
   which adds precision and mechanism on the same banks, and F on a bank fresh to the method,
   which needs a new bank and is the costliest.

If none of these is judged worth a slot before the deadline, ending the autonomous run here is
reasonable. The fragment line has a clean, scoped result to stop on.
