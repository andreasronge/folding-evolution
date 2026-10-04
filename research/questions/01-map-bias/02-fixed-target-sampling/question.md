---
status: parked
tags: [map-bias, folding-vs-direct, random-search, sampling, fixed-target, rarity-ladder]
budget: {experiments: 3, used: 0}
---
# Does folding's map bias help evolution beyond making solvers more common?

Current summary: Folding and direct encoding differ in bias (rank correlation 0.19–0.30), and
folding solves more often wherever they differ, consistent with its 1.3–30× higher P(exact)
(§27). On these fixed-target tasks evolution is mostly a worse sampler than random search with
the same budget; it beat sampling only on direct count∘rest(employees), where solvers are rare
but the plateau is not deceptive (§28). The two maps were never compared at matched
P(exact) × evaluations, so "folding helps evolution beyond sampling" is not shown either way.

Competing explanations:
- A: Folding's advantage is purely a sampling advantage (solvers are more frequent on arrival).
- B: Folding also changes mutational access (neighbourhoods), which would show as a better
  ratio to sampling at matched P(exact) × evaluations.
- C: The (μ+λ) truncation loop freezes on one behaviour, so these runs cannot tell A from B
  (steering untestable in this harness).

Related: [01-map-bias](../question.md),
[findings item 17](../../../../docs/map-bias/findings.md) (incl. "Night 2" and "Open"),
[notebook §27–§28](../../../../docs/map-bias/notebook.md),
[Plans/map-bias-pivot.md](../../../../Plans/map-bias-pivot.md),
[Plans/map-bias-pivot-night2.md](../../../../Plans/map-bias-pivot-night2.md),
[experiments/map_bias/](../../../../experiments/map_bias/)

Reopen if: the shared-helper line (03–05) stalls and the owner wants fixed-target map bias
settled; run the rarity ladder from findings "Open" (count(restᵈ(X)), d = 1–3, both maps,
offspring-first ties, plus random search; needs ~200M Phase A samples for direct at d = 3).
If fold's ratio to sampling stays below 1 where direct's is above 1, drop fixed-target map
bias and re-test the regime-shift claim against direct encoding and random restarts.
