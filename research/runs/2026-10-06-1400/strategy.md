---
next: proposal
---

Continue [root 10](../../questions/10-compositional-map-transfer/question.md).
**Next question: does the apparent shift toward branch tasks repeat in the unused
continuations, and does that shift depend on the learned contextual residuals?** Spend
one bounded experiment on this interpretation check, then move toward an actual
matched/mismatched family comparison. Neither answer to the check finishes the root.

**What we have learned.** The [core question](../../../README.md#core-question) asks both
how a map biases discovery and whether experience can adapt that bias to a task family.
The [digest](../../digest.md), question tree, [current ledger](../../briefs/2026-10-05-2225-ledger.md)
and [latest brief](../../briefs/2026-10-06-2026-10-06-0811.md) support four conclusions:

- Supply, search and preservation are distinct. Folding's fixed-target advantage was
  consistent with greater solver supply; evolution often lost to random sampling there.
  TAG lexicase instead beat its sampling-derived random-search baseline. Large supply
  gains on the composition banks translated into much smaller search gains. None is a
  general ranking of encodings or an identified supply-versus-neighbourhood mechanism.
- The building-block line established useful mechanisms: cheap joins explain the
  modular-assembly advantage; selected-mate crossover destroys rare shared forms,
  whereas self-mating permits discovery and seeded establishment. Natural B-helper
  arrival and single-copy success remain unresolved. More precision there would not
  answer whether the map learns task-family information.
- Learned bias transfers in the tested settings. Root 01's threshold fits sped search
  about fourfold over uniform, but hand-set biases did comparably and other-family fits
  also helped. Root 10 now has transfer to withheld operation combinations: learned
  token multipliers on G give 2.25× [1.81, 2.81] and 2.06× [1.60, 2.63] on new search
  seeds. Only the decoder transfers; program populations restart. This is meaningful
  progress beyond constant substitution, on one screened family with a supplied grammar.
- Learned context remains unresolved. In [0811](../2026-10-06-0811/analysis.md), allowing
  row residuals versus continuing token learning gave training 1.00× [0.90, 1.11] and
  holdouts 1.16× [0.91, 1.48] / 1.06× [0.83, 1.31]. Continued token learning itself helped.
  The frozen token maps helped branch-else about as much as post-addition. The six-map,
  post-hoc branch/linear trade-off is a lead, not evidence of family-specific learning.

Older tracks do not supply the missing comparison. The folding
[revised account](../../../docs/folding/findings.md#8-the-complexity-ceiling-revised)
ties transfer to preserved scaffolds, reachable structures and scoring geometry; the
README's earlier broad adaptation language should not drive this decision. Chem-tape
[slot transfer](../../../docs/chem-tape/findings.md) reused a body. The
[CA plan](../../../Plans/ca-developmental-revival.md) asks worthwhile damage and I/O
robustness questions, but not yet decoder-only transfer across task families. Coevolution's
[role conflict and constant-output lessons](../../../docs/coevolution.md) argue for
keeping the current map-learning question isolated from simultaneous task evolution.

**Which roots matter now, and alternatives.** Root 10 is first: it has a working learner,
positive transfer and a concrete uncertainty about what was learned. Root 01 remains
important for explaining supply and variation, but its parked questions do not currently
block a transfer experiment. The latest evidence meets none of their reopen conditions;
in particular, increased PA supply without increased speed is not 09's low-supply speed-up.

| Direction | What it could change | Decision |
|---|---|---|
| Test the saved-map branch/linear shift and residual dependency | Determines whether the only new contextual lead survives another continuation and whether residuals contribute to it. Reuses completed learning. | Next, one bounded check. |
| Build two families with the same primitive inventory | Enables the missing matched/mismatched learning comparison; distinguishes family adaptation from broadly useful syntax or token retuning. | Next substantive direction; concrete [plan](../../plans/four-reducer-family-transfer.md) written now. |
| Improve the outer selection objective | Could reveal contextual learning hidden by noisy candidate ranking. Both learners still improved, so acceptance near 25% alone is not proof that selection failed. | Calibrate fresh-training ranking reproducibility before funding another full optimizer comparison. |
| Resolve the existing 1.16× PA increment | Tightens a small effect without supplying family specificity. Roughly 20 independent starts are needed at the measured spread. | Defer; extra seeds or continuations from the same starts are insufficient. |
| Separate supply from variation, or resume CA/helper work | Important mechanisms, but less direct progress on the present family-learning gap. | Keep deferred, not rejected. |

**Direction for the steward.** Use a new child with available allocation; 13 is closed
and exhausted. Take the question above into a proposal, using the saved maps rather than
retraining. The "b" continuations have not been evaluated on these off-family cells, but
share the six M starts with the exploratory "a" maps. They provide a conditional
replication, not six new independent starting maps. Keep inference clustered by start,
freeze the task contrast before scoring, and retain every start.

Compare the branch and linear changes, including R's own residual ablation. Removing
residuals tests dependency in co-adapted maps; it also changes emitted token frequencies.
An empirically marginal-matched control, if affordable, would strengthen interpretation,
but beating it alone would not show newly learned context because G already has context.
Do not label an ablation result as proof of assembly learning beyond token frequencies.
Account for the unequal baseline difficulty and absence of IF_GT in linear tasks. A loss
on linear tasks alone is not a useful branch gain. No expanding search for favourable
off-family cells belongs in this confirmatory comparison.

The [steward's estimate](../2026-10-06-0811/decision.md) is about 1–2 hours without new
learning; verify that cost and size the comparison from the observed start variation.
If six starts cannot distinguish the proposed outcome, narrow the question to these
saved maps or return a measured redesign rather than buy thousands of inner seeds.
Fresh-task family specificity remains open whether the pattern repeats, disappears or
stays unresolved. A positive dependency check motivates carrying contextual adaptation
into the two-family study; a negative lowers its priority relative to the successful
token learner. An unresolved result is not permission for an indefinite precision loop.

**Allocation.** `uv run python scripts/research.py status` confirms 4/40 experiments used,
root 10 left=1, root 01 left=0. About 32 hours remain. Raise only root 10's frontmatter
`budget.experiments` from **5 to 7**, one **+2** step:

1. Existing fifth slot: settle the saved-map shape-shift/dependency question to the
   precision the six starts permit.
2. Added sixth slot: settle whether the planned four-reducer bank supplies two usable
   families, headroom and affordable inner search. A semantic failure is a useful answer
   about this candidate, not a reason to repeat the previous screen unchanged.
3. Added seventh slot: if feasibility supports it, test whether equally funded adaptation
   to each family improves its own withheld combinations more than the other family's
   adaptation. Otherwise return to strategy with the measured obstacle before spending it.

Return to strategy after the next result and after feasibility. These are allocations,
not approval of future designs. Keep each queue within eight hours and reserve time for
analysis and review; the experiment count is not the binding resource. A larger independent
learning replication can receive a later named allocation if its measured cost fits.
Leave root 01 unchanged and preserve the remaining root opening: this work still belongs
under root 10. The other 33 run slots remain unallocated after these three planned uses.

**What to stop.** Stop repeated G-versus-marginals demonstrations, uniform zero-hit
sampling, sparse three-cell contextual mutations and same-start PA precision extensions.
Keep threshold-veto refinements and shared-helper censuses parked. Do not treat noisy
single-step acceptance as a universal optimization diagnosis, related branch shapes as
an independently trained family, or a failed bank as a failed core hypothesis. Do not
weaken fixed controls or relax failed alias rules to manufacture headroom. Continue the
program: both the saved-map check and the planned two-family feasibility probe deserve
their cost; spending the fifth slot is not an automatic stopping point.
