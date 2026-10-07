---
next: proposal
---

Continue [root 10](../../questions/10-compositional-map-transfer/question.md), returning to
its unresolved question: **can selection learn useful decoder context beyond token tuning?**
First establish whether coherent contextual changes can be selected reliably at affordable
cost. The [new concept plan](../../plans/learnable-context.md) gives the steward a route;
the next proposal should settle training feasibility, not promise a full family-transfer
result before its cost and precision are measured.

**What the program has learned.** Against the [core question](../../../README.md#core-question),
the [digest](../../digest.md), full question tree and
[run ledger](../../briefs/2026-10-05-2225-ledger.md) support four conclusions:

- Map bias matters, but exact-solver frequency alone does not predict evolutionary speed.
  Folding's fixed-target advantage was consistent with increased solver supply; evolution
  often lost to random sampling there. TAG lexicase behaved differently. Cheap joins and
  selected-mate versus self-mate crossover also changed discovery and establishment.
  Those results concern particular maps and operators, not a universal developmental
  advantage. Natural B-helper arrival and single-copy establishment remain unresolved.
- Map adaptation transfers. Threshold fits improved held-out search about 4× over uniform,
  with a hand-set scaffold performing comparably. Root 10's token multipliers on a supplied
  contextual grammar improve search on withheld operation combinations about 2–3×. Only
  decoder parameters transfer; program populations restart. This is outer-loop map
  adaptation, not simultaneous map/program coevolution.
- Family specificity and newly learned context remain open. In the
  [crossed transfer test](../2026-10-06-2229/analysis.md), matched over mismatched training
  gave 1.02× on BE and 0.96× on PA; intervals permit a modest preference. The fragile BE
  upper bound is roughly 1.3× under sensitivity checks. Two contextual procedures did not
  establish a fresh-training increment beyond token tuning, and the off-family shift
  [failed to replicate across continuations](../2026-10-06-1425/analysis.md). Conversely,
  hand-set context strengthens a crossed preference on the four-reducer bank. That is a
  capacity witness, not evidence that selection learns it.
- The generic gain has two experimentally separated contributions. With starting programs
  preserved, ongoing M adds 1.39× on the three transfer targets and 1.28× on the ten training
  cells; learned initialization adds 1.30× and 1.33× given ongoing M. The
  [latest result](../2026-10-07-0315/analysis.md) replicates their sub-additivity. BE training
  cells are relatively more start-dependent than PA cells (difference −0.45 log2,
  95% [−0.68, −0.22]), but shape and difficulty remain confounded. Sub-additivity does not
  identify a shared resource; ongoing use still bundles mutation, crossover and continuing
  program supply. Direct solver seeding is unlikely to account for the start effect.

**Which roots matter now.** Root 10 remains first: its original beyond-token question
is unanswered, it has tractable tasks and a working token learner, and a positive contextual
result would change the central interpretation of what evolved. Root 01 remains the
conceptual foundation for distinguishing arrival from search dynamics, but its parked
threshold and helper experiments are lower priority. Keep its budget unchanged. No third
root is needed: the remaining permission to open one is capacity, not an obligation.
Historical folding and CA work supplies motivation, but another developmental robustness
study would need a direct connection to adaptive map bias to displace this question.

| Candidate direction | What it would change | Priority now |
|---|---|---|
| Compact contextual learning with measured selection reliability | Tests whether an accessible context change adds useful information beyond the successful token learner. A positive opens the missing family-transfer test; a bounded negative limits a materially different procedure. | First. The existing task bank avoids another feasibility screen, and the hand-set context witness makes a probe worthwhile. |
| Split ongoing use into mutation/crossover, or census starting partial programs | Could explain the replicated generic gain. A census alone is descriptive; operator removal changes the search regime and needs careful controls. | Defer. We already know both start and ongoing use matter. Another subdivision is less decisive for whether family structure can be learned. |
| New cells separating shape and difficulty | Tests whether the BE/PA mechanism balance generalizes and fixes the shortage of BE holdouts. | Worth future screening, but lower priority than testing learning on the tractable bank. A third bank is not needed to establish training feasibility. |
| More token trajectories, union/scrambled training, or a 1.1× specificity test | Tightens generic-versus-family dependence within the current representation. | Defer. Detecting 1.1× needs about 64–75 trajectories per family and 14–30 h of learning before scoring, without adding BE tasks. Union training alone still would not separate a general reducer prior from G4 repair. |

**Next for the steward.** Open a new child under root 10 (next available number: 18).
Ask whether a compact context-changing learner, with measured scoring reliability, improves
fresh training search beyond an equally funded token learner on the existing BE and PA
training sets. This is a new procedure, not a rerun of 0811. Its rationale is coherent
context moves plus a measured selection signal: 1723's 24-search parent rankings were
unstable, while larger final-selection scores better predicted fresh gains. That does not
prove noise caused the earlier contextual results. Use the plan to make the question
testable; retain an unresolved outcome and keep all holdout scores out of procedure selection.

**Allocation.** `research.py status` confirms **10/40 experiments used**, both roots with
zero left, and a deadline of **2026-10-07 22:25** (about fourteen hours remain). Raise only
root 10's frontmatter `experiments` **10 → 12**, one **+2** step:

1. Slot 11 settles whether the compact learner has an affordable, repeatable selection
   signal and a fresh-training increment beyond token tuning. Combine calibration and
   substantive learning where possible; target at most four queue hours.
2. Slot 12 tests whether a successful procedure transfers beyond token tuning and whether
   that transfer depends on training family, adding independent trajectories as needed.
   If training remains usefully resolvable instead, spend it on that resolution before
   touching transfer. Target at most five further queue hours; return to strategy if
   neither continuation can change a decision at the measured cost.

Reserve roughly five hours for agent work and contingency; recalculate at proposal time.
Every queue stays ≤8 h. The remaining thirty autonomous slots are an upper bound, not
thirty feasible cycles before the deadline. No existing question status, log, digest or
brief is changed here; the steward updates the tree and now-stale budget prose.

**What to stop.** End the initialization-by-decoder crossing series after its two answered
slots. Do not repeat G-versus-marginals demonstrations, saved-map branch/linear checks,
unmodified high-dimensional contextual runs, or token-learning precision extensions aimed
only at a 1.1× preference. Keep threshold-veto refinements and helper censuses parked. Avoid
automatic alphabet/domain expansion and promotion of these working results into findings
as part of this strategy task. Continue the autonomous run: contextual learning deserves a
bounded feasibility probe, so the conditions for `next: stop` are not met.
