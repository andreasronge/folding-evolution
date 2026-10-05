---
next: proposal
---

Continue root [10](../../questions/10-compositional-map-transfer/question.md), through
[12](../../questions/10-compositional-map-transfer/12-generic-grammar-headroom/question.md).
The next question is: **Can two task families using the same primitives but different
assembly patterns provide tractable unseen compositions, with room beyond the existing
fixed grammar for a family-adapted decoder?** This tests the missing half of the
[core question](../../../README.md#core-question): whether experience can change the map
in a way that transfers after the programs are discarded. A failed first bank is a reason
to redesign it, not to end this run.

**What we have learned.** The [digest](../../digest.md) and question tree support three
distinctions: which behaviours a map supplies, what selection and variation can discover
and retain, and whether the map itself learns useful family information.

- Random-genotype frequencies explain easy tasks and are consistent with folding's
  fixed-target advantage. They do not generally predict evolutionary speed. Fixed-target
  search often lost to equal-budget sampling; TAG threshold search beat a random-search
  baseline calculated from sampling rates. Those different harnesses are not a controlled
  comparison of maps.
- Cheap joins, rather than modularity alone, explained the tagged assembly advantage.
  Selected-mate crossover blocked establishment of rare seeded shared forms; self-mating
  removed that barrier while permitting discovery. Natural single-copy B-helper
  establishment remains unmeasured: the arrival census sampled other shared forms.
  See [06](../2026-10-04-1839/analysis.md) and [07](../2026-10-04-2135/analysis.md).
- Externally fitted token frequencies transferred between constant thresholds and sped
  median solving roughly fourfold over uniform. A hand-set scaffold performed comparably;
  family specificity remained unresolved against the chosen twofold bar. The component
  test explained max>2's generic gain through INPUT/GT. On sum>2 a residual gain despite
  lower exact-solver supply remains unexplained. The shortcut-veto pilot showed use of a
  replaceable intermediate, not its contribution to that gain. See
  [1705](../2026-10-05-1705/analysis.md), [1814](../2026-10-05-1814/analysis.md) and
  [1957](../2026-10-05-1957/analysis.md).
- Root 10 has now established a stronger intervention: the fixed contextual grammar G
  beat its context-free token marginals by 2.6–19.5× in median search cost across eight
  cells. Supply and mutation structure changed together, so this is not a mechanism
  separation. **No map was learned and no compositional transfer was tested.** The
  [2247 analysis](../2026-10-05-2247/analysis.md) and
  [latest brief](../../briefs/2026-10-06-2026-10-05-2247.md) show two feasibility failures:
  Sm-SEL solved only 27/50 under uniform at 524k, and every structural split had ADD/DADD
  holdouts already solved by G in 768–2,304 evaluations. Raising the cap addresses only
  the first problem.

Older tracks reinforce the need to separate these questions. Folding's transfer finding
narrowed to preserved scaffold inventory interacting with representation and scoring;
chem-tape slot transfer depended on a shared body. CA specialization improved parity but
does not establish learned map bias. Coevolution exposed role conflict and constant-output
collapse. See the [folding assessment](../../../docs/folding/findings.md#8-the-complexity-ceiling-revised),
[chem-tape findings](../../../docs/chem-tape/findings.md),
[CA record](../../../docs/ca/experiments.md), and [coevolution lessons](../../../docs/coevolution.md).
The older auto-summary's stop recommendation is historical: the current strategy and
ledger record root 10's subsequent opening and completed experiment.

**Priorities and alternatives.** Root 10 matters most because transferable, learned
assembly preferences remain untested and the decoder intervention is demonstrably large.
Root 01 remains the evidence base for supply versus search, but none of its parked
questions has acquired a new dependency or met its specific reopen condition.

| Candidate | What it would settle | Decision now |
|---|---|---|
| Different assembly families, same primitives | Whether there is a feasible family-information contrast beyond shared token supply and generic syntax | First. Reuses the reviewed decoder/search machinery; a bounded probe can change the program's next step. |
| Simply deepen the original bank under G | Whether longer compositions restore practical headroom | Useful fallback within 12, but length alone does not supply a matched/mismatched family contrast. Prefer structurally different families first. |
| Replace G with a weaker bank-blind grammar on the old bank | Whether learning could recover syntax that G was given | A legitimate narrower learning question, but weakening the comparator after seeing it win would not answer the current beyond-fixed-assembly question. Do not use this as the rescue. |
| Root 01's shortcut veto or folding rarity ladder | A residual one-task mechanism, or search advantage beyond sampling | Lower priority: neither tests learned compositional transfer. Existing reopen conditions remain in force. |
| CA damage/I/O probes | Whether evolved dynamics repair or redeploy | Credible alternative with an [existing plan](../../../Plans/ca-developmental-revival.md), but less direct for family-adapted genotype-to-program bias. Defer. |

**Direction for the steward.** Propose the question above under 12, using the
[assembly-family plan](../../plans/compositional-family-headroom.md). Preserve G as a
frozen, bank-informed benchmark; do not claim it was bank-blind, and do not remove it
because it won. The new bank should contrast where operations are assembled, not merely
which reducer or constant is frequent. Feasibility must establish semantic distinctions,
fresh-search cost and useful headroom, then estimate the whole adaptation comparison.
Canonical bigram differences alone cannot establish that a previous-token decoder can
exploit the contrast. Sample sizes, queue stages and outcome rules belong in the proposal.

**Allocation.** Status shows 1/40 experiments used, root 01 left=0, root 10 left=3,
and 12 left=1; about 46 hours remain. Raise only root 10's frontmatter `experiments`
from **4 to 5**, one **+1 step**. That step should settle whether the redesigned bank
supports an affordable, informative adaptation test; it compensates for the first bank's
failure without consuming the original transfer follow-ups. Root 10 now has four left:

1. Revised family/headroom feasibility under 12, including adaptation cost.
2. Independently evolve decoders and test fresh-program transfer against token, fixed
   grammar, marginal-matched and mismatched-family explanations.
3. Replicate or resolve transfer using independent map trajectories and reserved compositions.
4. One follow-up on the explanation that would change our next decision, only if needed.

These are allocations, not required expenditures. Leave 35 of the run's remaining slots
unallocated, root 01 unchanged, and the final new-root opening unused. Review strategy
after another bank failure or the first transfer result. Each queue remains at most eight
hours; measure runtime rather than filling that limit or treating a noisy pilot as proof
that a larger study is unaffordable. The last study took 19 minutes, but deeper-task and
outer-loop costs are still unknown.

**What to stop.** Do not top up Sm-SEL alone, relabel the old bank feasible by changing its
headroom cutoff, or repeat G-versus-marginals merely to tighten an already clear effect.
Keep constant-threshold refinements, veto-definition sweeps and shared-helper censuses
parked. Defer CA retraining, plasticity expansion and a coevolution port. Stop escalating
task depth if it supplies only difficulty without a learnable family contrast; return to
strategy with the measured obstacle and a revised plan. This stops uninformative lines,
not the autonomous run: the assembly-family direction deserves a feasibility probe.
