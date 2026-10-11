---
next: strategy
---
# Decision: run 2026-10-11-0524 (question 47, slot 39 of root 10)

**Close [47](../../questions/10-compositional-map-transfer/47-tree-donor-arrangement/question.md) and return
to strategy.** No proposal is written for 0652.

**Why close.** The primary landed on its pre-set retention branch: on the two gate-sum splits no learned
predicate covers (B/C), label-rearranged libraries cost 1.031× [0.854, 1.225] of intact ones (margin 1.25),
still 0.360× [0.299, 0.429] of plain restarted tree GP, with 1,728/1,728 solved in both donor arms. The
intact gain replicated (0.349×), and the positive control worked strongly: on the learned predicate's split
A, rearrangement cost 5.14× [3.68, 7.14]. The question as asked is answered for this construction: shapes,
sizes and size-conditioned label counts retain the B/C gain at this resolution, while A's extra gain needs
the learned arrangement. A tighter run could only bound a small intact advantage (≤ 20%), which would not
change the next acquisition choice; the analysis prices pushing the lower bound above 1.10 at about 150 more
acquisitions.

**Why not propose.** Root 10's budget is spent (39/39), and strategy 0524 reserved the follow-up for its own
review: "useful retention makes a simpler statistical acquisition worth pricing … neither result
automatically funds a follow-up."

**What the strategist should weigh (my recommendation).** Before pricing a statistical acquisition, buy one
cheaper check: **does the B/C gain need anything learned at all?** R-perm kept learned shapes *and* learned
label counts; the old size control (R-size, random donors matched on size and compiled length but not on
inputs) did not reproduce the gain (0348: R-lib/R-size 0.29× overall). An arm with the libraries' shapes but
labels drawn uniformly within each width class (no learned counts), scored on B/C against R-lib and R-perm
with the same harness (`tree_permutation_run`, ~45 min of scoring, ~4 h full cost, no new acquisition),
separates "learned primitive counts" from "supply of small input-bearing expressions of the right shapes".
If uniform labels also retain the gain, the useful learned content on unmatched targets is shape/size only,
and a statistical learner has little to learn there; if they lose, label counts are the acquisition target.
The construction's confound (B/C pair supply tripled) should be tracked by the same content audit. The
alternative purchases from strategy 0524 still stand: different-source acquisition (portability, 7–10 h) and
an unfamiliar-content boundary (5–8 h). I rank the uniform-label check first because it is cheapest and
decides what any statistical acquisition must learn.

**Digest check.** Critique 0524 notes 6–8 applied: "mostly where/mostly predicate-matched" removed from the
digest heading, root summary and 46's summary (split A carries about 43% of pooled savings; the relative gain
is what is much larger); 46's "equals R-tree's" share and "no reliability loss" corrected by a log note and
summary edit.

**Parked questions re-checked.** None reopens. 29/30/31 concern the tape decoder's frequency projections and
need a proposed frequency-only or structured-recoding learner; none is proposed. Root 23 needs a changed
inheritance rule with measured selectable signal; this run supplies none. 09(b) needs a heritable-bias design
asking about INPUT/GT supply; none exists yet.

**Beliefs changed.** One new digest bullet under "Against tree GP" (47), the 46 heading narrowed, and the
Overall paragraph extended. Scope throughout: development bank `x4-gate-sum-v1`, one DG acquisition cohort,
one extractor, one construction.
