---
next: proposal
---

Use at most the last experiment under [01-map-bias](../../questions/01-map-bias/question.md)
to ask: **Does access to the max>2 shortcut causally help evolution reach exact sum>2,
explaining why the residual fitted bias speeds evolution despite making exact solvers
rarer?** Ask the steward for a direct test under [09's reopen condition
(c)](../../questions/01-map-bias/09-generic-bias-speedup/question.md). Do not open a new root.

**What the program has learned.** The [core question](../../../README.md#core-question)
requires both a distribution of programs and an account of what search does with that
distribution. Random-genotype frequency predicts easy tasks; folding's fixed-target
advantage is consistent with more frequent exact solvers. It does not establish a search
advantage beyond sampling. Tagged chem-tape supplies the complementary evidence: selection
preserves useful parts, cheap joins enable assembly, and mating changes which forms
establish. These are separate contributions, not a general developmental-encoding win.
See [map-bias findings](../../../docs/map-bias/findings.md).

The shared-helper line separated establishment of a seeded minority from retention and
natural arrival. Self-mating removes the seeded establishment barrier, but naturally
arising A-only/other shared copies disappeared, and the B-helper form seen in successful
endings never appeared in the relevant census. Arrival versus fixation remains unresolved
for that form. The line stopped at a useful boundary; further generic shared-child counts
would not answer it. See [06](../2026-10-04-1839/analysis.md) and
[07](../2026-10-04-2135/analysis.md).

Part 2 has a bounded positive. Externally fitted token frequencies transferred to a held-out
threshold in sampling and made median evolutionary solving about four times faster than
uniform. A hand-set INPUT/GT/aggregator scaffold performed comparably. Family-specific
speed gains over the other family's fit were only 1.66–1.80× and unresolved against the
chosen 2× bar. This is constant-substitution transfer with a fixed decoder, one fitted
vector per family, and initialization and mutation changed together. It does not establish
heritable map adaptation, richer family learning, or savings after fitting cost.
See [1558](../2026-10-05-1558/analysis.md) and [1705](../2026-10-05-1705/analysis.md).

The [latest run](../2026-10-05-1814/analysis.md) reproduced the other-family speed-up at
2.73×/2.02× on fresh seeds. On max>2, raising INPUT/GT while thinning everything else
reproduces it within the registered margin. That intervention also raises exact-solver
supply; the full vector's nearly unchanged sampling rate hid opposing component effects.
This does **not** prove supply mediates its speed-up. The sharper residual is sum>2:
the rest-of-vector arm R is 1.61× faster than uniform while sampling only 0.23× as many
exact solvers. The sampling comparison is descriptive and uses historical uniform counts.
R's frequent training-perfect shortcuts suggest a route, but their abundance and proximity
in time to exact solves do not establish ancestry or causation.

Older tracks reinforce this distinction. Folding's scaffold-transfer result ultimately
narrowed to reachable structures, preserved inventory and compatible partial-credit
scoring. Chem-tape slot transfer depends on shared bodies; its proxy-basin work shows that
frequent approximations can trap search. CA spatial and temporal specialization improved
parity, but those results do not establish developmental repair or family-adapted bias.
See [folding's revised assessment](../../../docs/folding/findings.md#8-the-complexity-ceiling-revised),
[chem-tape findings](../../../docs/chem-tape/findings.md),
[CA experiments](../../../docs/ca/experiments.md), and the
[CA revival plan](../../../Plans/ca-developmental-revival.md).

**Which questions matter now.** There is only one existing root, 01. Its highest-value
remaining issue is whether bias toward an inexact intermediate can help search even while
bias toward complete solutions worsens. That connects measuring bias to choosing what a
future adaptive map should optimize. A causal positive would justify considering access
to useful intermediates alongside exact-solver frequency; a negative would remove this
specific justification for doing so. Either answer remains local to this task and harness.

Question 08 remains the longer-term destination, but evolving the already sufficient
INPUT/GT scaffold would add little evidence of family learning. A new root should first
have a transfer question that goes beyond manual scaffold tuning. Fixed-target folding
versus direct (02) remains secondary: TAG lexicase beating computed random search does not
resolve it across different tasks and selection regimes. Its owner-request condition is
still unmet. CA robustness is a coherent separate project, but less direct for the current
core question than the residual in 09.

**What the steward should do next.** Propose one bounded causal test of the max>2 route
behind R's sum>2 gain. This is a new mechanism question explicitly allowed by 09(c), not
a rerun to classify IG or R against the old 1.5× margin. Leave arms and sample sizes to
proposal and critique. The crucial design requirement is interpretability: changing
REDUCE_MAX probability also redistributes other probability mass; changing training cases
also changes selection. Either intervention needs a comparison that separates the proposed
route from those accompanying changes. More shortcut counts alone cannot do that.

Explain in the proposal what would support the route, what would rule out a practically
meaningful contribution, and what would remain ambiguous. If an affordable design cannot
make that distinction, return `next: stop` rather than spend the slot on another
association. After one valid experiment, report the bounded answer and stop this threshold
line even if the result is unresolved; no precision extension or replacement explanation
sweep follows automatically.

**What to stop.** Keep 08's specificity estimate parked. Do not run the ≥650-pair
component-label refinement, restart shared-helper censuses or crossover refinements,
or resume 02 without its recorded condition. Defer heritable-bias machinery and decoder
evolution until there is a stronger transfer target and a concrete plan; do not create
a root merely to replenish this line's budget. `research.py status` confirms one
experiment remains at root 01 and effectively at 09. This strategy changes no existing
questions, digest, briefs, budgets or promoted findings; the steward handles any reopening.
