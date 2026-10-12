# Can learned abstractions improve reuse beyond input renaming?

Concept plan under [root 10](../questions/10-compositional-map-transfer/question.md),
written by [strategy 0533](../runs/2026-10-12-0533/strategy.md). **Deferred to a
new funded block; no experiment or root allocation in this run.** The steward
supplies the proposal, sizes and primary decision rule. This is not a
registration or permission to begin a queue.

The question is whether learning expressions with argument holes from evolved
source programs produces a useful search bias beyond literal libraries and
their supplied input permutations. Root 10 already shows that acquired content
helps. Its remaining 2–7× gap to supplied helpers, and rebinding's modest gain,
make the acquisition representation worth changing before another donor-rate
or recurrence sweep. This does not assume that all of that gap is missing
abstraction: donor probability, irrelevant content, source coverage and rejection
also differ.

The mechanistically different candidate is corpus-guided abstraction synthesis,
as in [Bowers et al., *Top-Down Synthesis for Library Learning* (POPL 2023)](https://arxiv.org/abs/2211.16605),
found in this review's literature search. Stitch synthesizes library functions
guided by corpus structure and evaluates library quality through compression.
Compression motivates a candidate; our endpoint is cheaper fresh search.
This would be external acquisition from evolution's programs, not an inherited
map, nor evidence that evolution invents its own abstractions.

**What to build.** Start from the saved independent order and signed-gate source
corpora and the reviewed `research/main` tree runner. The source trees and
ordinary expanded-donor interface already exist in `tree_gp_search.py`,
`tree_library.py` and `order_library.py`; they are absent from this `main`
checkout. Build a small adapter between prefix trees and a pinned abstraction
learner, plus deterministic expansion and provenance. Do not build a new VM.

Permit holes for argument expressions, including repeated occurrences of the
same argument. Input renaming alone is already R-bind. Fix the allowable arities,
fitting effort, corpus weighting, library selection and argument-generating law
using source/development information before confirmation. Prefer one bounded
candidate to a representation sweep. The argument law is supplied and must be
reported separately from the learned bodies. Do not use target formulas,
required-helper lists or destination outputs to select abstractions or bindings.

Expand every application into ordinary primitives before insertion and scoring.
Preserve the 32-token limit and charge full expanded size and execution cost;
macros must not receive free complexity. Validate round trips, repeated argument
identity, IF_GT operand order, negative inputs and zero, against the independent
interpreter and production VM. Retain the existing literal and rebound paths
for replay. A syntactic learner need not discover semantically equivalent forms
or shorten the oversized representatives in the saved census.

**First experiments.** First, a bounded development study fits independent
libraries from the saved corpora and tests whether their fully expanded donors
improve search over R-bind and R-all. Keep ordinary restarted tree GP and the
supplied helper prior visible. Corpus compression and helper coverage are
diagnostics, never sufficient success. Include failed/empty fits. Price the
complete fresh-bank continuation before spending a development experiment.

If the new representation earns continuation, freeze its acquisition and donor
rules with a new bank before any performance search on that bank. The useful
boundary is a familiar conditional computation with a compound argument, which
input permutations cannot directly supply. One candidate family is
`p(Xa+Xb, Xc) + n(Xd, Xa)`, where `p(u,v)=u>0?v:0` and
`n(u,v)=u>0?0:v`. This is a candidate for a deterministic semantic screen, not
an admitted bank or a predicted hard task. Check old-bank aliases, ordinary
primitive expressibility and meaningful development/protected coverage; reject
the candidate if it cannot support the question. Preserve protected targets
from timing and method choice. Keep source acquisitions separate from targets.

The eventual answer is a worthwhile reduction in capped arithmetic search cost
over the simpler reusable procedure, on the frozen fresh bank, with acquisition
and fitting charged. The steward fixes one primary effect and 95% interval,
retains acquisition-build uncertainty, and reports solve fractions, worker time
and repayment horizons. A win only over R-tree is insufficient if R-bind is as
cheap; a compression win without a search win ends this candidate. A useful
fresh-bank increment would justify further abstraction acquisition. It would
not establish inheritance or superiority to informed domain knowledge.

**Full cost and exit.** Planning estimate **12–18 h complete**: 3–5 h for adapter
implementation/validation and its review, 4–5 h for the development comparison
including queue and analysis, and 5–8 h for bank validation, frozen comparison
and final review. These are estimates, not measured Stitch or new-bank rates.
The existing hard-chain evaluations took about 1.5–2.3 queue hours in 2150/2353;
new argument donors could be slower. Each prepare remains within 120 minutes;
split work into reviewed stages if necessary. Do not shrink the final comparison
merely to fit the current nine-hour remainder.

At a future allocation review, replace these estimates with an interface audit,
sustained development timing and a decision-sized price. A decision-sized
one-stage implementation could change this ranking if its *whole* cost is
demonstrated. Otherwise reserve the complete block, with review between stages;
feasibility alone does not earn confirmation. Return on a build, precision,
semantic-admission or cost obstacle. No automatic source-forcing, helper-aware
ranking, inherited-library engine or PSB2 extension follows.
