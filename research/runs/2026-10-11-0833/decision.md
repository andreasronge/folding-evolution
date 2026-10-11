---
next: strategy
---
# Decision: run 2026-10-11-0833 (question 49, slot 41 of root 10)

**Close [49](../../questions/10-compositional-map-transfer/49-tree-library-source-portability/question.md) and
return to strategy.** I am not writing a proposal for 1019.

**Why close.** The primary landed far inside its pre-set portable branch. The unchanged 0150 extractor was
rebuilt from the four branch-sum (TS) source cells. On gate-sum B/C those libraries cut mean evaluations to
**0.382× [0.335, 0.433]** of restarted tree GP. The rule was upper < 0.80, and the solve guard passed: +0.003
[+0.001, +0.005], 1,728 vs 1,723 of 1,728. The saving holds in 24/24 builds and 12/12 cells, and it is not a
donor-size effect (R-TS ÷ R-sizeTS 0.406× [0.344, 0.482]). Validation, seed audits and code review were clean.
The question asked whether the recipe works from another source family on this destination. For these
development rosters, the answer is yes. More builds would only tighten the TS-versus-DG contrast (1.03× [0.86,
1.22]). Resolving it would take roughly 800 more builds, and it would not change the next choice.

**What is new beyond the yes.**
- *Acquisition is much cheaper from TS.* It costs 0.245 M evaluations per library against DG's 2.88 M, and
  repays after about 6 B/C searches instead of about 64. This makes the economics case far stronger than
  0150/0348 suggested, on this destination.
- *The libraries harm near-solved targets.* On the native TS roster, where plain R-tree solves 99% of jobs
  first time, TS libraries cost **1.78× [1.58, 2.00]** and DG libraries 1.33× [1.12, 1.57]. Explanation (c)
  ("native-only reuse") is contradicted. Mix 0.5 is a cost when there is nothing to buy. I opened this as
  parked [50](../../questions/10-compositional-map-transfer/50-library-easy-target-harm/question.md). Strategy
  0833 asked to stop rate sweeps, and the question is about deployment, not acquisition.
- *Content (observational, across two cohorts).* TS libraries hold no comparison predicate, and they always
  contain the split-matched pair sums that 18/24 DG libraries lack. Yet both cohorts give about the same B/C
  saving. Their common content is small `ADD(input, input|const)` donors. This fits 48's label-law reading,
  but what is sufficient is not identified.

**Why not propose.** Root 10's allocation is spent (41/41), and roots 01 and 23 have no budget. Strategy 0833
said to return after this result: "useful performance with credible economics earns a choice between a
new-content boundary and simpler statistical acquisition."

**Recommendation to the strategist.** Before choosing between those two, I would buy the cheap control that
this result now makes the main threat. *Does a hand-set, source-free donor set do as well as the learned ones?*
For example, all distinct `ADD(Xi,Xj)` plus `ADD(Xi,c)` at the learned libraries' size, with no acquisition.
TS and DG libraries differ in content yet save about the same on B/C, so a generic ADD-sum prior on this
alphabet may be enough. If it is, "the library learns a useful adapted bias" reduces to "small ADD sums help
gate-sum search", and neither a generator nor a new-content boundary is the right next purchase.
- Price: no acquisition and saved 0833 libraries, so about 1–1.5 h of queue (B/C 12 cells × 24 × 6 for
  R-tree, R-TS and R-hand, using the 0652/0833 worker rates) plus one agent cycle. It is cheaper than either
  strategy option.
- Decision rule I would suggest: R-hand ÷ R-TS upper < 1.25 means a generic prior suffices at this
  resolution. Lower > 1.25 means the learned content adds a worthwhile amount, and the generator or boundary
  choice follows.
- Optional: one library-on-failure arm on native TS, which would also answer 50 cheaply. Skip it if it
  enlarges the design.
- Otherwise, I would rank the **unfamiliar-content boundary (5–8 h)** above the **statistical generator
  (10–14 h)**. TS acquisition is now cheap, so a generator's main selling point, cheaper acquisition, has
  weakened.

**Parked and closed questions.** None reopens automatically.
- 48's condition is met only if a generator is chosen. In that case, run its single-component replacements
  first.
- 45's reopen item (i), "hand-set {pair sums}", is exactly the control recommended above. If the strategist
  funds it, it belongs under a new sub-question citing 45(i), not as more DG seeds.
- 41/42's TS-direction conditions are not met.
- Root 23 has no new selectable signal, and nothing here touches root 01.

**Digest check.** Critique notes 6–8 are applied.
- The pre-solve-extractor bullet regains "on then-addition" and "one source selection". The repair sentence
  regains "on then-addition".
- 48's "perform like random size-matched donors" and "skeletons alone do not carry the gain" now read "cost
  difference unresolved; descriptive reuse similar" and "preserving shapes with this uniform label law did
  not retain the full learned-label saving; the shape contribution remains unresolved".
- These changes are in 48's question, the root summary and sub-question entry, and the digest. 48's log has a
  dated correction appended rather than an edit.

**Analysis wording narrowed.** analysis.md §3 says "learned content, not donor size, carries the gain". The
supported claim is narrower: the learned libraries beat this size-matched random control. The analysis's
"the DG comparison skeleton is not needed" is a cross-cohort observation, not a controlled contrast. The
question, log and digest use the narrower forms.
