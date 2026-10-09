# Can useful fragment bias be extracted before a complete solution?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
allocated by [strategy 1350](../runs/2026-10-09-1350/strategy.md). The steward supplies
the proposal, sample size and decision rule. This is not an experiment registration.

The [fragment reuse result](../runs/2026-10-09-1036/analysis.md) establishes a useful
externally supplied repertoire on development banks. It does not tell us whether the
repertoire requires completed assemblies. The [partial-program study](../runs/2026-10-08-1831/analysis.md)
already saved independently collected programs from before their source searches' first
exact solve. Their full-tape context fit is useful but weak. Short active windows might
retain useful pieces without retaining those tapes' unfinished surroundings. They might
instead preserve the wrong computations. That distinction changes whether early population
material is a credible source for a later acquisition procedure.

**First question.** With the search decoder held fixed, can a library extracted from
pre-solve programs improve fresh search on excluded compositions beyond blocks drawn
from the decoder's own chain? Compare it with the existing solver-fragment library to
measure how much useful repertoire this early source recovers. This first stage isolates
the source opportunity; it does not yet establish a system acquired without exact solvers.

**What to reuse and build.** On `research/main`, reuse `fragment_library.py`,
`fragment_operator.py`, `fragment_reuse_run.py` and the reviewed search path (1036 code
`348f9e2`). The current `main` checkout lacks these runners. Keep D1331 length-three
inputs, the alphabet, C tables, 32-token tapes, search operators and fragment insertion
law. Use the sixteen 1831 collections, both BE and PA, in
`experiments/output/2026-10-08/2026-10-08-1831-partial-program-context/search.jsonl`.
The archive is present (about 54 MB); its rows include corpus, source seed, checkpoint,
tape, exactness and first-solve provenance. This is an interface check, not a measurement
of partial-fragment yield or search efficacy.

Adapt the extractor's source interface explicitly. It currently requires `solved` and
`solver`, verifies exactness and skips unsolved rows; do not disguise partial tapes as
solvers. Select only the S parent archive before the first exact-solve generation. Do
not select sources by whether they later solved, by evaluation-bank performance, or by
the archive's full-domain accuracy. Revalidate the old temporal and non-exactness checks.
Preserve early-stopped, empty and failed source attempts in the resource manifest.

Bound extraction before any evaluation: use a deterministic, performance-blind subsample
per source/checkpoint, balance source tasks, and count recurrence across distinct source
searches rather than treating many descendants of one population as independent evidence.
For example, one archived S tape per source at each of the three existing checkpoints is
a small candidate to price. Fix the subsample and duplicate treatment before scoring;
no library-size, length, collection-horizon or checkpoint sweep is needed.

Retain the existing 3–6-token windows, bounded library size, recurrence across source
cells and NOP-knockout activity assay. On a partial program, a knockout changing its
output establishes activity, **not usefulness or improved fitness**. The old assay can
be generalized without inventing a target-aware fragment reward. Validate Python/Rust
agreement and report stack/default behavior as before. Freeze ranking, activity inputs,
normalization and empty-library behavior. If a library is empty, keep that replicate
with a declared fallback (such as its matched chain operator), never collect until it
becomes attractive. Report how often the fallback was used. Do not supply canonical
programs or complete training solutions to the new library.

**First experiment.** Use the complete then-addition-v1 roster as an excluded-composition
development test. Keep all sixteen collection replicates, pairing each partial collection
with a preassigned same-family C table; matching IDs is bookkeeping, not shared ancestry.
Pair fresh search seeds and initial tapes across procedures. The comparison is between
partial-source fragments, their matched C-chain block control W, and the old exact-solver
fragment procedure as a reference. A different library length distribution requires its
own matched W law: do not assume the old W rows match it. The exact-source reference may
use its original operator law, but then it is a comparison of complete procedures, not
an isolated causal effect of source completeness.

The main decision is usefulness beyond W, with a prespecified worthwhile increment,
corpus-level 95% interval, fixed size and explicit unresolved outcome. Preserve both
families and individual cell results. Historical F/W spread can inform a price, but new
partial-source variance must be allowed for. Do not choose favorable partial libraries or
targets from a small timing look. Include the unchanged C benchmark if affordable; it is
secondary to the paired W comparison and the exact-fragment reference. Reuse old rows
only with recoverable pairing and replay; otherwise price fresh reference searches.

This is external extraction from selected programs, not per-individual map inheritance
or selection among decoder genotypes. Without a new marginal-block control, any advantage
compares source/operator procedures, not joint content isolated from token supply. All
targets are development data. Do not describe active literal windows as self-contained
functions, or their reuse as semantic modularity.

**Full cost and staging.** Allocate one root-10 experiment now, **5–7 hours total**,
including up to two hours preparation, about two hours scoring, reviews, analysis and
contingency; **at most four hours summed queue timeouts**, preparation at most 120 minutes.
The 1036 three-arm reuse queue took 152 minutes for 15,360 searches. A scenario retaining
16 corpora × 16 then-addition cells × 16 seeds × 3 arms is 12,288 searches, roughly
two hours at that rate. This is a price anchor, not a prescribed adequate sample size or
a measured rate for the new libraries. Extraction and a slower partial-fragment arm must
be timed at intended concurrency. Prefer validation and a substantive comparison in one
cycle. A probe-only fallback is descriptive, at most 60 minutes of queue timeouts, and
must still price confirmation and the conditional stage below.

1831's saved timing records total **5,058 worker-seconds / 521 collection wall-seconds**
for the sixteen partial collections, versus 48,039 worker-seconds for the old exact
corpora. Those are different collection procedures, not matched tape counts. Reusing
the files saves execution now but does not erase acquisition cost in a from-scratch
calculation. Charge all failed/empty attempts, verification, extraction and fitting.

**Conditional second stage, not allocated.** If early fragments are useful, test the
complete early-data route: use each collection's own partial context fit and library,
discard all source programs, and score fresh searches against that same partial fit
with chain blocks, plus an exact-corpus procedure and G4 as practical references.
This removes the expensive exact C scaffold used in stage one. Start with one frozen
partial fit, not additional feedback rounds. Price **6–9 further hours**, including
agents and slower partial-decoder searches; the complete candidate is therefore
**11–16 hours**, within the supplied 18-hour window only if measured costs cooperate.
The second stage needs strategy review and a new allocation; do not spend the reserve
automatically. Reprice it during first-stage preparation and against the actual deadline.

Report arithmetic mean savings and acquisition costs in consistent units. For F versus
W on the same exact C, its corpus is a shared cost, not an incremental charge against
F alone. A complete cheap-pipeline claim must compare each procedure's own acquisition
plus subsequent search cost. Give the break-even search count only where savings are
positive; use a cost curve rather than silently assuming unlimited future tasks.

**Answers and exit.** A useful partial-fragment/W advantage establishes that completed
solutions are unnecessary as the *fragment source*, conditional on C. Its remaining gap
to exact-source fragments determines how attractive the complete early-data route is.
A tight small or harmful effect ends expansion of this source/extractor at this scope;
it does not reject all pre-solve learning. A broad interval needs a resolution price,
not a negative label or an automatic top-up. Return to strategy after the result, or on
a measured build, validity or complete-cost obstruction. No online archive, extra rounds,
fresh bank or callable-function engine is authorized by this allocation.

The relevant precedent is [Rosca, *Towards Automatic Discovery of Building Blocks in
Genetic Programming* (1995)](https://cdn.aaai.org/Symposia/Fall/1995/FS-95-01/FS95-01-011.pdf):
ARL uses search traces and activation to discover subroutines. This plan tests an earlier,
narrower prerequisite with frozen literal windows; it does not implement ARL's adaptive
function representation. [Keijzer, Ryan and Cattolico, *Run Transferable Libraries*
(2004)](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf)
provides the cross-run library precedent, not evidence for our proposed source rule.
