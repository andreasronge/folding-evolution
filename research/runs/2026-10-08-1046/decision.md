---
next: strategy
---
# Decision: run 2026-10-08-1046 (root 23, last slot): recovery worked, frozen scoring Bounded in both families — park 23

**Park root 23 and return to the strategist.** No proposal is written. The pre-registered
comparison is answered for this procedure, both of 23's experiments are used, every root now has
zero budget left, and the strategy and plan send every outcome of this run to strategy.

## What happened

- Recovery ran as planned: 79 reused 0918 acquisitions (hashes checked), max/inherited/14 rerun
  from its original seed, two control replays and the cut run's 30 episodes matched 0918
  exactly, no fallback. All 80 acquisitions and 2 752 frozen searches complete. Queue 75 min
  against 3.25 h of timeouts; no hidden deadline fired.
- Primary R_u = uniform ÷ inherited: **sum 0.33 [0.21, 0.53], max 0.73 [0.50, 1.06]. Bounded in
  both families.** On sum the inherited vectors are resolved worse than uniform; on max a gain
  above 1.06× is excluded.
- L = broken ÷ inherited: max 1.58 [1.04, 2.36], sum 1.00 [0.69, 1.41]. The broken control is
  worse than uniform in both families, so a damaged control does not explain L.
- S = inherited ÷ scaffold: 11.9 [7.0, 20.4] and 5.75 [3.66, 8.95]; a greater-than-twofold
  disadvantage is established. Break-even is undefined (negative saving).

## Why park, not close or continue

- **Not close:** the root asks whether inheritance *can* learn a useful bias. One modifier law
  at one σ and schedule on training targets bounds that procedure, not the mechanism
  (explanation E stays open).
- **Not continue:** another run of this procedure would not change a decision. A redesign
  (lower σ, entropy limit, different exposure or inheritance rule) has no measured selectable
  signal behind it. The two hints are weak: a resolved linkage effect on max that still left
  the vectors no better than uniform, and a within-cell correlation of acquisition and frozen
  solves (0.59–0.85) confounded by the shared program seed. Selecting vectors by acquisition
  success would also be outer-loop selection, which root 10 already covers.
- The reopen condition in [question.md](../../questions/23-heritable-variation-bias/question.md)
  now asks for a measured selectable signal (e.g. a cheap probe whose frozen vectors beat
  uniform at a resolved bound, or a mutation-only control showing selection moves the vectors).

## Tree updates

- [Log](../../questions/23-heritable-variation-bias/log.md): new 1046 entry, including the
  critic's notes 6–7 as a correction to the 0918 entry ("equally far", drift attribution,
  "small shared component").
- [question.md](../../questions/23-heritable-variation-bias/question.md): status parked, summary
  rewritten with the primary result and scope, explanation status, Related, Reopen if.
- [Digest](../../digest.md): root 23 now holds two scoped beliefs (no useful frozen bias under
  this procedure; linkage made max vectors less costly, not useful). Post hoc observations stay
  in the log. The "drift equally far" wording is gone.
- Parked questions rechecked: none reopens. 09's condition (b) needed a heritable-bias design
  that must know whether INPUT/GT supply alone is used; 23 is parked, so no.

## For the strategist

All three roots are at zero budget (01: 0, 10: 0, 23: 0). Run 2026-10-08-0812 has used 2 of 40
experiments with roughly 40 h to its deadline. The strategy for this cycle named the
[root-10 reserve plan](../../plans/comparison-gated-transfer.md) (corpus context versus token
fitting on new compositions, multiple holdouts per family, frozen evaluation) as the next
candidate, with an unmeasured new-task throughput and a 12–18 h envelope. I recommend assessing
it next, starting with a throughput and bank-screening stage before any full allocation. I see no
23 redesign that beats it now. On the owner note: step 1 is complete with a negative,
scoped answer; capture/synonyms and population-level maps had preconditions (useful frozen
transfer, value beyond the scaffold) that this result does not meet.
