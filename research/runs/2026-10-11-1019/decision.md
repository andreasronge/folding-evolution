---
next: strategy
---
# Decision: run 2026-10-11-1019 (question 51, slot 42 of root 10)

**Close [51](../../questions/10-compositional-map-transfer/51-source-free-donor-prior/question.md) and
return to strategy.** I am not writing a proposal for 1129.

**Why close.** The registered rule had three predicates. All three held with room to spare:
- R-hand ÷ R-TS **0.852 [0.762, 0.958]**, against a required upper bound < 1.25.
- R-hand ÷ R-tree 0.318 [0.291, 0.349], against < 0.80.
- Solve difference +0.003 [+0.001, +0.005], against > −0.03.

The interval excludes 1 in the prior's favour, and a learned advantage above 1.25 is excluded (lower bound
0.76). Data checks, seed pairing, TS-library reconstruction and code review were clean. The R-TS arm replicated
0833 on fresh seeds (0.373 vs 0.382 of R-tree), so the comparator was healthy. The question was whether a fixed,
supplied sum prior keeps the B/C saving. For this bank the answer is yes, and it does slightly better. More
seeds would only narrow a contrast whose decision is already made.

**What this changes.**
- *The comparator moves.* On B/C a learned or generated library now has to beat this alphabet-built prior,
  not R-tree. With acquisition charged, TS libraries never repay against it within 200 searches
  (cumulative 1.23 [1.10, 1.37] at 200).
- *The B/C case for acquisition is gone on this bank.* A short way of putting it is "small ADD sums help
  gate-sum search". That is a fair reading at substitution level. It is not an ingredient result: pair
  coverage, constants 2/5, entry count and the missing ANY/GT entries changed together.
- *What is left for learning.* The B/C result does not cover split A. There, 0524 showed that the learned
  `GT(ADD,ADD)` arrangement carried a 5× extra gain. That predicate is exactly what a 3-node sum prior cannot
  supply. Tape-context evidence (questions 20–38) is also untouched.
- *A hint, not a finding.* The heterogeneity is consistent with "coverage of the gate's pairs matters": the
  prior's gain sits on split (03|12), where TS libraries rarely hold X0+X3, and TS wins on the one cell whose
  sums TS concentrates on. This is post-hoc over 12 cells. It stays in the log, not the digest.

**Digest check (critique 1019, notes 6–7) applied.** "No comparison predicate" now names the exact absent
structure: seven-node `GT(ADD,ADD)`, 0/24 TS libraries; the libraries do hold 13 smaller GT-rooted entries.
This is fixed in the digest and the root summary/49 entry. A correction note is appended to 49's log; its
earlier entries are left unchanged, because the log is append-only. The note restates "unrelated to library
size (Spearman −0.14)" as an observed correlation over 24 builds, with the size effect unresolved.

**Parked questions re-checked.** [50](../../questions/10-compositional-map-transfer/50-library-easy-target-harm/question.md)
stays parked: no mixed-difficulty deployment is funded. One note for whoever reopens it: the hand prior is
also a mix-0.5 donor law, so it may share the easy-target harm. Nothing here bears on the parked questions in
roots 01 and 23. 45's reopen item (i) has been used: 51 was opened from it and has now answered it at the
substitution level.

**Why strategy, not a proposal.** Root 10's 42-slot allocation is spent. Strategy 1019 told us to return
after this result, and its "what to stop" list rules out hand-prior variants and an ingredient matrix. The
next purchase is a different block, which is the strategist's choice. About 27 h remain in the run
(deadline 2026-10-12T14:19), and 12 of 40 experiments have been used.

**What I would put to the strategist** (input, not a proposal):
1. *Unfamiliar-content boundary, now with the prior as an arm.* This is the most informative option. On a
   fresh bank, frozen together with the method, test whether a freshly acquired library beats both R-tree and
   a prior built by the same rule from the new alphabet. The bank's content should not be "sums of inputs":
   for example, needed subterms built from other binary ops, or a nested predicate that a 3-node prior cannot
   express. That is the first test that could show learning doing something a supplied prior cannot. It also
   removes the development-bank caveat that hangs over 45–51.
2. *Statistical generator (PIPE-like): defer further.* On B/C, its target benefit is already captured by a
   prior that costs nothing. It needs a destination where the prior fails before it has anything to learn.
3. *Return to root 23 (inheritance).* This is still the long-run mechanism the core question cares about.
   Nothing in this result gives it a new selection signal, so it needs the strategist's redesign, not a slot.
4. *Stopping the library line is also defensible.* On the banks we have, the practical answer is now "tree
   GP plus a supplied sum prior". Option 1 is only worth buying if the strategist expects the new content to
   defeat the prior.
