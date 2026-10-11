---
next: strategy
---
# Decision — 2026-10-11-1129 order-helper acquisition probe

**Park [52](../../questions/10-compositional-map-transfer/52-order-helper-acquisition/question.md); no proposal;
return to strategy.**

**What the probe showed (observations; six development cells, protected roster untouched).** On a new content
family, pairwise min/max helpers built from GT/IF_GT, the unchanged literal subtree recipe acquired no helper in
0/8 builds and cost 1.55× [1.09, 2.17] of plain restarted tree GP (geometric cost, 96 paired jobs). A
behaviour-keyed extractor on the same source solvers held a helper in 3/8 builds (a destination-needed one in
2/8) and was unresolved from R-tree, 1.00× [0.68, 1.46]. The supplied 12-helper order prior was about 20× cheaper
than R-tree (0.048× [0.04, 0.06]); neither learned arm recovered any of that gap. The 1019 sum prior cost 2.12×
[1.54, 2.91] here.

The limit is located, not absent content: 63% of the 384 source solvers compute their own helper, but literal
keys pool it in only 5/96 helper × build cases (varied, often bloated syntax). Behaviour keys pool it in 49/96, and
44 of those fall outside the 16-entry cap, because the ranking counts distinct source cells first and each helper
can recur in at most 2 source cells, while 3-node sums, comparators and a constant class recur in 3–8. Emission size
(> 9 nodes) is the next limit (21/96). Whether an included helper speeds search is unresolved (post-hoc, 24
pairs: 0.67× [0.33, 1.31]).

**Why park and not continue.** The pre-stated rule (a helper in ≥ 6/8 builds and ≥ 50% of the gap) was missed
by both arms, and it routes to strategy with a located limit, not to a protected comparison. Root 10's 43-slot
budget is spent, and strategy 1129 asked to review the program after this result. Not closed: the probe is one
look at development cells, and the usefulness of an acquired helper is still open.

**Why no proposal.** The obvious follow-up changes the extractor: rank so that 2-cell classes are not shut
out, raise the cap, or drop semantically constant classes. That is the kind of extractor tuning on a
development bank that strategy 1129 put under its own review ("no variant sweeps"), and it needs new budget. I
would not propose it unasked. For the strategist, as I see it:

1. **One extractor-mechanism test** (about 4–6 h): R-S with crowding relieved, set in advance (e.g. all
   eligible recurrent classes up to a fixed size budget, or rank by solvers within cells), against R-tree and
   R-S on the six development cells, with one pre-stated rule on gap recovered. Only if it passes would the
   frozen protected roster be priced. It answers "acquired but useless" against "never acquired". Risk: a
   library large enough to hold the helpers also holds more 3-node trivia, which this probe showed costs
   1.5–2× by itself.
2. **Stop the literal-library line on root 10.** Two results now show its value depends on content
   that is cheap to supply (sum prior on B/C; order prior here). Strategy 1129's deferred
   parameterized-abstraction candidate (DreamCoder-like) gains a concrete motivation from the literal-keying
   limit seen here, but it remains a 12–18 h build.
3. **Whether default library use is safe at all** (50's question, widened): irrelevant donors at mix 0.5 cost
   1.5–2× even where R-tree solves only 56% first time. 50's reopen condition is not formally met (it names
   ≥ 90% first-attempt targets or funded default deployment), but the evidence is now broader. Logged in 50.

**Tree changes.** 52 parked with a concrete reopen condition. 50 and 51 have cross-reference log entries, and
their status is unchanged. Root 10 summary, sub-question list and budget line updated. Digest: as-of line, budget
and status line, critique 1129's digest-check notes 5–6 fixed, and a pointer to 52 in "Not shown". No belief
changed (probe observations stay out of the beliefs). Parked questions re-checked: 50 (condition not met), root
23 (no new inheritance signal) and root-01 sub-questions (nothing relevant). None reopened.
