---
status: open
tags: [map-bias, developmental-map, inheritance, context, varying-goals, fresh-start, transfer]
budget: {experiments: 4, used: 0}
---
# Can selection on an inherited contextual decoder under related changing goals improve search after resident programs are discarded?

Opened by [strategy 0533](../../runs/2026-10-12-0533/strategy.md) for autonomous
run 2026-10-12-2311, following the new [owner direction](../../plans/owner-next-direction.md).
The [concept plan](../../plans/inherited-contextual-development.md) supplies the
direction, implementation boundary, first studies and complete cost envelope;
the steward chooses experiments and their decision rules.

Summary: untested. External fitting establishes that chem-tape previous-token
context can contain transferable information. Root 23 tested inherited token
generation probabilities; root 55 tested access to externally acquired tree
libraries. Neither made an individual's developmental decoder itself mutable
and subject to selection through its current decoded program. This root asks
whether that direct selection route, with related goals changing over time,
can accumulate a reusable map rather than merely a coadapted tape/map pair.

Use the existing latent-allele chem-tape representation and primitive executor.
Keep primitive meanings fixed. Inherit a bounded contextual emission table with
the tape; local changes affect its decoding. Preserve programs during training
goal changes, but transfer only frozen map state to independently initialized
populations. Fresh goals must be excluded from training and method selection.
No solver-corpus fitting, library extraction or externally ranked map searches
constitutes the proposed learning mechanism.

Competing explanations:

- A: Direct selection on contextual development across related tasks accumulates
  useful regularities. Frozen maps improve fresh search on unseen combinations.
- B: Map and tape coadapt to particular residents; resident adaptation improves,
  but map-only fresh search does not.
- C: Any benefit is generic token supply, the supplied starting grammar, or
  drift under the mutation law, rather than newly selected contextual structure.
- D: Changing goals prevent specialization or encourage reusable organization;
  alternatively, the same useful map would arise under fixed goals. A varying
  schedule alone does not identify the effect of environmental variation.
- E: Map edits disrupt decoding, crossover breaks coadaptation, or selection
  freezes the map before it learns useful information. These limit the tested
  representation and procedure, not inherited developmental evolution generally.

Allocation: four experiments through the next strategy review, including at
most the currently available one probe. Expected complete block 20–28 hours,
ceiling 32 hours, subordinate to the autonomous deadline. Stages must be
individually reviewed and priced; allocation is not a requirement to run all
four. Exit on a complete map-only transfer answer, a bounded usefulness
failure, or an obstacle making the complete remaining answer poor value.

Related: [01 supply and linkage](../01-map-bias/question.md),
[10 externally adapted maps](../10-compositional-map-transfer/question.md),
[23 inherited frequencies](../23-heritable-variation-bias/question.md),
[55 inherited library choice](../55-inherited-library-choice/question.md),
[owner-heritable-map](../../plans/owner-heritable-map.md),
[core question](../../../README.md#core-question).

Reopen if: after parking, a changed representation or exposure rule addresses a
measured failure of this block and has an affordable complete map-only readout;
or independent evidence establishes useful inherited context in this executor.
More seeds, table movement, or a warm-start advantage alone are insufficient.
