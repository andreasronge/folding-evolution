---
next: strategy
---
# Decision: run 2026-10-10-2001 (table × library crossing, question 42)

**Close [42](../../questions/10-compositional-map-transfer/42-family-bias-component-transfer/question.md)
and return to strategy. No proposal written.**

**What happened.** Commit `6dabda8`, code review pass, 4 608 searches complete, all validity checks passed
(16 native replays bit-exact, shared-table initial populations identical, bare arms zero block events).
On 8 DG cells (failures at 2 × cap, 24 donor pairs):

| Contrast | Ratio | 95% |
|---|---:|---:|
| Fresh native gap T/T ÷ D/D | 3.03× | [2.28, 3.97] |
| Bare tables T/∅ ÷ D/∅ | 3.26× | [2.43, 4.30] |
| D library on T table vs none, T/∅ ÷ T/D | 3.05× | [2.32, 4.07] |
| **Primary R = T/T ÷ T/D** (vs 1.5× margin) | **1.95×** | **[1.43, 2.66]** — unresolved |
| Hybrid gap T/D ÷ D/D | 1.55× | [1.15, 2.09] |
| D library identity D/T ÷ D/D | 1.35× | [1.10, 1.68] |
| TS retention T/D ÷ T/T | 1.01× | [0.83, 1.25] |

Labels unchanged at 1 × cap. The primary missed its margin by 0.07 on the lower bound. The direction is
one-sided (22/24 pairs, 8/8 cells, lower bound ≥ 1.40 under every estimator tried), but by the pre-stated
rule it is unresolved, not established.

**Why close.** The question was which component a later learner must acquire. The answer is both: the
bare DG table alone shows a gap as large as the native one, and the DG library speeds a foreign table about
3× over no library, needs no native table, and costs nothing on TS. Which component is "larger" depends on
the order of swaps (library first 1.95× then table 1.55×; table first 2.24× then library 1.35×), so
I do not claim either dominates. Resolving R against 1.5× (about 5 more donor pairs with two new
acquisitions each, ≈ 35 min queue, only if R is really near 1.95) would sharpen one replacement number,
not change the choice. The proposal and strategy both pre-committed to a strategy exit in every case.
Root 10's 34 slots are used.

**What the strategist should weigh.**
- The component answer turns the next mechanism question into *why* the DG components are better:
  content, library size, or learning on harder sources (G4 first batch 17% vs 63%). The table carries
  the effect without libraries, so a test of the table part could vary sources without fragments.
- A weak new observation: on TS cells the bare T table beat the bare D table 1.43× [1.01, 2.00] at
  2 × cap only (1 × cap crosses 1). Libraries hid it in 1717. It is not a belief yet. It only weakly
  touches 41's reopen clause, so 41 stays closed.
- Everything here is development data with frozen external fits on one family pair. The program's
  open practical gaps (fresh bank, stronger baseline, PSB2) and root 23's inheritance gap are unchanged.

**Tree changes.** 42 closed with a Reopen-if condition. The 41 and root-10 question files and logs have
critique notes 8–9 wording corrections ("reciprocity not established"; "unresolved", not "no power").
Digest: new 42 bullet, 41 bullet shortened, 37/38 bullet corrected per notes 6–7, root-10 Overall updated;
former text moved to root 10's log. No parked question's reopen condition is met (checked 02, 04, 07, 08,
09 and root 23).
