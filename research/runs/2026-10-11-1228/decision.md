---
next: strategy
---
# Decision — 2026-10-11-1228 uncapped semantic library (R-all) on order development cells

**Close [53](../../questions/10-compositional-map-transfer/53-order-library-cap-release/question.md) (answered at
its scope) and [52](../../questions/10-compositional-map-transfer/52-order-helper-acquisition/question.md); no
proposal; return to strategy.**

**Result.** Removing the 16-entry cap from the behaviour-keyed extractor turned the same acquired corpora from a
cost into a large saving on the six order development cells of `x4-order-v1`. The primary result, the ratio of
pooled capped arithmetic mean evaluations bootstrapped over 24 independent builds, was **R-all / R-tree 0.40
[0.32, 0.50]**. That lands in the pre-registered "useful acquisition" branch (upper < 0.80; the end-recipe branch
needed lower > 0.67). Capped R-S cost 1.23× [1.07, 1.41] of R-tree on the same corpora, and R-all / R-S was 0.33
[0.27, 0.39]. The effect held in 24/24 builds and all six cells (0.35–0.47), with no solve loss (576/576). It
repays its acquisition against R-tree after about 5 searches. The supplied 12-helper order prior is still 7.3×
[5.5, 9.8] cheaper than R-all, so R-all recovers about half the log gap and no repayment against that prior is
claimed. This was my named surprise: I had guessed 0.8–1.0×.

**What it means, and what it does not.** On this bank, the recurrence-only recipe *can* acquire useful content
that the alphabet lacks (min/max built from GT/IF_GT), once ranking stops shutting out 2-cell classes. Earlier library gains were on sum-based content, and on B/C
a hand-written sum prior did better; here the sum prior harmed (1129 probe) and the acquired library helped. Descriptively, a
needed helper is in the R-all pool in 126/144 cell × build pairs (capped 14/144), cost falls with coverage (0.77 →
0.45 → 0.23 of R-tree), and 382/576 R-all solvers contain a needed-helper entry. Helper causality is not isolated:
entry count, sizes, content and the trivia share of draws changed together, and the no-helper stratum also beat
capped R-S. Scope: six development cells of a bank already used by 1129, method chosen after seeing that bank. It
is not a transfer claim.

**Why close, and why no proposal.** 53's pre-stated question is answered. The plan routes this outcome to
strategy with a separately priced protected-stage case. Root 10 is at 44/44, and strategy 1228 asked to review
after this result. A next step exists that deserves an experiment, but which one is a value choice the strategist
reserved ("a development win does not automatically authorize it"). I therefore give the priced options here
instead of a proposal. The run has used 14/40 experiments, with about 25 h until the 2026-10-12 14:19 deadline.

| Option | What it settles | Cost (agent + queue) |
|---|---|---|
| **A. Protected cells of `x4-order-v1`** (the plan's stage) | Saved R-all builds on the 24 never-searched cells (4 disjoint-pair, 20 overlapping) vs R-tree and R-order. No new acquisition. Roughly 3.5 k jobs, about 45 min queue at measured rates. | ~4–5 h (strategy priced 6–8 h). |
| **B. Fresh content-family bank, R-all frozen now** | Is R-all a recipe, or a fix tuned to this bank? A new helper family built from existing primitives (e.g. median-of-three or clamp), with bank, method and rule frozen before any search. Compare R-all, R-tree, a supplied-helper prior and capped R-S. This is the README's transfer standard. | ~8–12 h incl. bank design and screen; stage 0 to measure source solvability. |
| C. R-all back on gate-sum (B/C and native TS) | Does uncapping keep the earlier gains, does it beat the hand sum prior on B/C (51's reopen condition), and how much harm does it do on easy native TS (50's question)? | ~4–6 h, if the saved 0833 source solvers can be re-extracted. |
| D. Helper-ablated R-all from saved libraries | Whether helpers or less trivia carry the saving. Mechanism only. | ~2–3 h. |

**My recommendation: B.** A is cheap, but it adds little information. The same 12 helpers serve all 30
destinations, all six development cells already sit at 0.35–0.47, and the method was devised after the bank was
seen, so a protected win would still only be held-out cells of a development bank (critique note 4). B tests the
claim that matters for root 10: that a frozen automatic recipe acquires useful *new* content on a family it was
not tuned on. Run C before B only if the strategist wants R-all as the default recipe across families, because C
answers deployment (harm on easy targets) rather than acquisition. D can wait until a decision depends on it.

**Tree changes.** 53 closed with a reopen condition (ingredient or cap-size decision). 52 closed (literal recipe:
no acquisition, probe; behaviour keying without the cap: acquisition and saving, 53). Critique 1228's digest-check
notes 6–9 are fixed in 52's summary and log and in 50's and 51's logs, plus a note in the root log; the digest did
not carry those wordings. The root-10 summary and budget line are updated. Digest: one new belief bullet (53, at
development scope), the as-of line, budget and status line, and the Overall paragraph (former text kept in the
root log). The digest is about 3,000 words. Parked questions re-checked:
- 50: the order cells are not easy targets, and default deployment is unfunded, so its condition is not met. A
  cross-reference was logged. Option C would test it.
- 45 (iii): needs a fresh bank frozen with the method. Not met; option B would meet it for R-all.
- 51: no learned library is proposed for B/C. Not met.
- Root 23: R-all is external fitting, not an inherited signal. Not met.
- Root-01 sub-questions: nothing relevant.

None reopened.
