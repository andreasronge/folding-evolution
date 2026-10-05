---
next: proposal
---

Continue with new root [10-compositional-map-transfer](../../questions/10-compositional-map-transfer/question.md):
**Can a decoder adapted across related tasks help fresh populations solve unseen operation
combinations beyond a token-frequency bias?** Start by establishing a tractable transfer
target and measuring adaptation cost. The [new plan](../../plans/compositional-map-transfer.md)
makes that direction actionable. The prior strategy's lack of a demonstrated target is a
reason for this feasibility experiment, not for ending a fresh 40-experiment, roughly
48-hour run.

**What the program has learned.** The [core question](../../../README.md#core-question)
has two parts: measure which behaviours a map supplies, then ask whether experience can
adapt that bias to a task family. Part 1 has substantial evidence. Random-genotype
frequency predicts easy tasks, and folding's fixed-target advantage is consistent with
making solvers more common. It does not establish a search advantage beyond sampling.
The fixed-target search harness mostly lost to equal-budget sampling; recent TAG lexicase
threshold searches beat a random-search baseline computed from sampling rates. Different
tasks and search regimes prevent treating that contrast as a general map comparison.
See [digest](../../digest.md) and [map-bias findings](../../../docs/map-bias/findings.md).

Supply is only one influence on evolutionary outcomes. Cheap joins explain the tagged
assembly advantage over the original stack baseline. Selected-mate crossover prevents
rare seeded shared forms from establishing; self-mating removes that barrier while still
allowing discovery. But natural single-copy establishment remains unresolved for the
B-helper form: the census found A-only/other shared children, not that form. Further
generic shared-child counts would refine the wrong population of events.
See [06 analysis](../2026-10-04-1839/analysis.md) and
[07 analysis](../2026-10-04-2135/analysis.md).

Part 2 has a bounded positive: externally fitted token frequencies transferred to a
held-out constant and sped median evolutionary solving about fourfold over uniform.
A hand-set INPUT/GT/aggregator scaffold performed comparably. The matched/mismatched
speed difference, 1.66–1.80×, remained unresolved against the chosen 2× bar. One fitted
vector per family and constant-only holdouts leave learned compositional structure,
heritable map adaptation and net savings after fitting cost untested.
See [1558](../2026-10-05-1558/analysis.md) and [1705](../2026-10-05-1705/analysis.md).

The [1814 component test](../2026-10-05-1814/analysis.md) replicated the generic speed-up.
On max>2, raising INPUT/GT sufficed and also raised exact-solver supply; the full vector's
nearly unchanged supply concealed cancellation. On sum>2, the residual vector still
sped solving despite lower supply. The [1957 pilot](../2026-10-05-1957/analysis.md) showed
that exact max>2 often supplied the last step, but vetoing it only delayed solves as
near-max alternatives appeared. Its contribution to the residual vector's advantage is
unknown. The main stage never ran; the unstable pilot power gate supplies neither a
mechanism null nor evidence that a decisive run is unaffordable.

Older tracks constrain the next design. Folding's scaffold transfer narrowed to preserved
inventory, reachable structures and compatible scoring, rather than general adaptation
speed. Chem-tape slot transfer required shared bodies; its breadth and plasticity checks
did not establish general family learning. CA spatial/temporal specialization improved
parity, but repair and family-adapted bias were not measured. The Elixir coevolution
designs exposed role conflict and constant-output collapse; they do not supply a tested
adaptive decoder. These motivate fresh-program transfer, expressive task checks and
simple controls, rather than restarting all tracks. Sources:
[folding assessment](../../../docs/folding/findings.md#8-the-complexity-ceiling-revised),
[chem-tape findings](../../../docs/chem-tape/findings.md),
[CA experiments](../../../docs/ca/experiments.md), [coevolution](../../../docs/coevolution.md).

**Which root questions matter now, and why.** Before this strategy the tree had only
root 01, with six experiments spent and every child closed or parked. Its unanswered
part-2 question matters more than further threshold precision. Root 10 now gives that
question a distinct test: new operation combinations, adaptation of a decoder, and fresh
programs after transfer. It does not reopen 08 under another name merely to tighten the
old intervals. Root 01 remains the evidence base for supply, search and establishment;
its narrow residual mechanisms are secondary until a new result needs them.

| Candidate direction | What it could change | Priority now |
|---|---|---|
| Compositional map transfer | Whether task experience teaches reusable map structure beyond token supply and generic syntax | First. A feasibility probe can establish the target and compute needed; failure would identify a concrete design bottleneck. |
| Resolve 09's sum>2 veto interaction | Whether one replaceable shortcut explains one residual speed advantage | Lower. A larger run may be affordable, but either outcome leaves richer transfer untested. No dependency of the new plan requires it. |
| Fixed-target rarity ladder, 02 | Whether folding helps search beyond its sampling advantage in that harness | Useful part-1 work, but it leaves part 2 untouched and retains its recorded owner-request reopen condition. |
| CA damage and I/O probes | Whether evolved parity rules exhibit repair or geometric robustness | A credible inexpensive alternative, with an [existing plan](../../../Plans/ca-developmental-revival.md), but a less direct test of bias learned across task families. Keep available for a later strategic comparison. |

**What the steward should do next.** Propose under root 10: **Is there a tractable set of
held-out operation combinations on which a learned decoder could demonstrate more than
constant substitution or a fixed token scaffold?** This is the immediate uncertainty to
resolve before investing in decoder evolution. The plan supplies a concrete candidate
bank, implementation route and controls. Measure discovery and runtime; do not insist
on abundant random exact hits if evolutionary discovery is feasible. No new primitives
or task-specific slot bindings should silently encode the withheld compositions.
Use the existing research branch's engines where possible. Leave sample sizes and the
experiment's non-overlapping outcome rules to proposal and critique.

**Allocation.** `research.py status` showed 0/40 experiments used in this autonomous run
and zero remaining under root 01. Leave root 01's budget and every existing question
unchanged. Open root 10 with four experiments, each with a purpose:

1. Settle target expressibility, meaningful holdouts and search/adaptation feasibility.
2. Test adapted-map transfer against frequency, fixed assembly and mismatched-training
   explanations, using independent adaptation trajectories.
3. Resolve or replicate the transfer result with new map starts and reserved compositions.
4. Settle the leading explanation that would change the next decision; release this slot
   if the root is already answered.

These are allocations, not four mandatory runs or a declaration that four must suffice.
Return for strategy after feasibility if the implementation or task bank needs a major
change, and after these slots otherwise. Later increases can be made in 1–4 experiment
steps with a named unresolved decision. Keep 36 run slots unallocated and one of the two
new-root openings available; the deadline and measured queue costs matter more than
filling the 40-slot cap. Each queue must fit the eight-hour review limit.

**What to stop.** End the constant-threshold refinement line as committed in
[1945's strategy](../2026-10-05-1945/strategy.md) and
[1957's decision](../2026-10-05-1957/decision.md). Do not launch the roughly 1600-seed veto
rerun, IG-versus-X precision extension, or veto-definition sweep without a new scientific
dependency. Keep shared-helper censuses and crossover refinements parked until their
specific reopen conditions are met. Defer CA retraining, expanded plasticity and a
coevolution port. Stop using finite no-hit counts as reachability verdicts or a pilot gate
failure as a negative mechanism result. Continue the program through root 10; the present
evidence leaves a worthwhile feasibility experiment, not a reason to wait for the owner.
