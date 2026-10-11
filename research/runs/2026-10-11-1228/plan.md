---
estimated_minutes: 40
---

# Approved cap-release experiment

Implement the approved [proposal](proposal.md), retaining the 1129 tree engine,
source effort, semantic key, recurrence, representative, ranking, sizes, donor
mix and restart policy. R-all removes only the semantic top-16 truncation;
R-S and R-all share each newly acquired corpus. Keep constants and comparators.
Reload and hash-check the saved 1129 bank; never re-screen or search its 24
protected destinations. Freeze a repository copy for reproducible preparation.

Full conditions: 24 independent builds, each 24 source cells × 2 R-tree
searches (1,152 source jobs). Score R-tree, R-order, R-S and R-all on the same
6 development cells × 24 builds × 4 repeats (576 paired units, 2,304 jobs).
Each job has 8 fixed-seed attempts of 65,536 evaluations, population 256,
crossover 0.5, maximum 32 compiled tokens. Failures cost 524,288 evaluations;
failed sources and empty libraries stay in the experiment. No complete-case
acquisition selection, reduced pools, early stopping or automatic top-up.

Seeds: SHA256 of task namespace `2026-10-11-1228`, phase, cell, build,
repeat and attempt; arms share destination attempt seeds. Smoke uses separate
phase namespaces, one complete acquisition and two repeats per development
cell. Audit full/smoke/source/score uniqueness and disjointness from 1129 and
the existing historical schedule artifacts. Bootstrap uses fixed seed
202610111228 and 8,192 whole-build resamples.

Before the full queue, test provenance, cap-prefix identity, all-eligible
emission, recurrence/size boundaries, failed and empty corpus behavior,
protected-cell rejection, schedules and paired pooled-mean inference. Then
smoke-test one 48-job acquisition and 48 destination jobs at unchanged search
caps. Reconstruct libraries from their own corpus before scoring. Helper
census and needed-helper labels are reporting-only; test that altering them
cannot alter extraction or donor construction. Preserve the old capped path.

Measurements: capped arithmetic mean evaluations and paired whole-build
95% percentile bootstrap of the ratio of pooled means (equal cell/repeat
weights). Report R-all/R-tree primary, R-all/R-S secondary, geometric ratios,
solves, worker seconds, acquisition/extraction/validation costs, break-even
search counts against R-tree, and the recovered R-tree→R-order log gap.
Report donor draws, accepted insertions and rejections, library sizes, and
cost splits by destination-needed helper coverage 0/1/2 descriptively.
Do not claim repayment against R-order when it is cheaper.

## Outcomes and critique disposition

Resolve critique note 2 by precedence: first, **lower 95% bound > 0.67 → end
this recurrence-only recipe on these development order cells**. This excludes
the worthwhile one-third saving, even if the upper bound is below 0.80;
report evidence for a smaller saving separately. Otherwise, **upper bound
< 0.80 → useful acquisition; return to strategy with a separately priced
protected-stage case**, assessed alongside the stronger R-order reference.
Otherwise **unresolved → price resolution and return to strategy**, without
calling uncertainty equality. Strict boundary inequalities are retained.
Thus [0.70, 0.78] ends the recipe, and an interval spanning both thresholds is
unresolved. This routing is fixed before any smoke or scoring outcomes.

A large gain supports the explanation that cap crowding obstructed useful
acquisition and that the expanded repertoire pays for dilution under this
procedure. Harm or an excluded worthwhile saving favors insufficient useful
bias after dilution/acceptance costs. Uncertainty leaves both explanations
open. R-all/R-S isolates cap removal, not helper causality: donor sizes,
contents and sampling probabilities change together. Coverage strata do not
resolve that confounding. Fresh acquisitions test repeatability, not a fresh
bank. Conclusions concern externally fitted subtree reuse on these six
development cells, not inherited adaptation, general transfer, or superiority
to the supplied R-order prior (critique notes 3–5).

Feasibility baseline (critique note 1): 384/384 pilot sources solved; mean
201,536 evaluations and 11.36 worker-seconds/build. Destinations: R-tree
96/96, R-order 96/96, R-S 93/96 solved, with 5.44/0.37/7.63 mean worker-s/job.
R-sum's 10.56 s prices R-all provisionally, giving 25 min scoring on ten
workers; all R-all jobs at ~38 s gives ~51 min. Expect ~40 min total including
prepare/verification; hard queue timeouts are prepare 1,200 s and score
5,400 s (110 min total), with internal deadlines 30 s earlier. Preserve
partial rows on resource failure and refuse analysis/admission without the
complete grid. If smoke finds unreachable targets, a failed validity gate or
rates/runtime far from these assumptions, write infeasible.md and stop for
the steward instead of changing the design.

Critique notes 6–9 concern existing digest/question/log claims. The researcher
role forbids edits outside this task folder in research/, so defer their
suggested wording to the steward; none will be copied into new conclusions.
Specifically, unresolved benefit is not absence; helpers assigned to two
targets may occur incidentally elsewhere; observed availability is partial;
content mismatch is plausible rather than isolated causally. No new literature
or claim promotion is part of this implementation task.
