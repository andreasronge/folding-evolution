# Do frozen fragments help on excluded compositions?

Continuation of [learned executable fragments](learned-executable-fragments.md),
allocated by [strategy 1036](../runs/2026-10-09-1036/strategy.md). This is a direction
and implementation plan; the steward supplies the proposal, size and decision rule.

**Question.** Does carrying the learned library improve fresh search on excluded
compositions beyond both C and its library-free chain-block operator W? The
[training result](../runs/2026-10-09-0843/analysis.md) gives F/C 1.57× and F/W 1.23×,
but mostly short shared syntax and one cell where F loses to W. Reuse can decide
whether a separate library deserves acquisition work. It cannot by itself distinguish
generic syntax from reusable computational abstractions.

**Reuse the completed implementation.** Start from reviewed commit `e347793`, the
0843 extractor/operator and its saved whole-corpus libraries in the preparation
artifacts. Retain the 16 source corpora, their frozen C tables, the primitive executor,
D1331 length-three inputs, and the fixed library size, length, ranking and activity
rules. Recover actual hashes and interfaces from artifacts/code. All source material
remains the original four training cells per family. No new collection, library
ranking, rate tuning or filtering against evaluation-task solutions is needed.

Validate whole-corpus library provenance and deterministic reconstruction under the
old rule. Whole-corpus libraries use four source cells rather than the training
experiment's three-cell leave-one-out libraries. Record that change: a difference
from the training effect is not a clean estimate of attenuation with task distance.
Knockout activity is contribution in the source program, not a certificate that a
window is a self-contained computation at arbitrary insertion stacks.

**First and only allocated experiment.** Freeze the method and complete evaluation
roster before scoring: the eight comparison-gate holdouts and the sixteen then-addition
cells, all excluded from source collection. They are development banks already used
in program decisions, not fresh banks. Start every search afresh; transfer only C and
the appropriate frozen library. Retain F, W and unchanged C on paired seeds and initial
programs. W must share F's span/start/rate and re-encoding law for each library; no
target-specific adjustment. Validate operator-off replay, suffix preservation and
equal initial tapes using the existing audits.

Make the incremental library value F/W the main scientific comparison, with F/C
retained as the practical benchmark. Prefer then-addition as the primary scope because
it changes expression shape; the comparison-gate holdouts give the within-shape
reference. Fix that choice before evaluation and report the two banks separately.
Preserve independent source-corpus uncertainty, both source families and individual
cell results. Do not let a pooled average hide a collapse across shape. The steward
chooses one worthwhile increment and a fixed size that can change the library decision.
Eight seeds per corpus/cell is a cost scenario, not a prescribed adequate sample size.

B need not be repeated to decide whether carrying a library beats W. Without B here,
do not claim that the transfer increment isolates dependencies from changed token
supply. Even with B, F/W would compare block-generating procedures, not prove semantic
modularity. Report realized edits, solve rates, capped-cost sensitivity and wall time.
Reuse old C rows only if exact pairing and replay are recovered; otherwise price new C.

**Cost.** The completed training queue scored 8,192 searches in 74 minutes. The
steward's continuation scenario is 3,072 searches per arm: F+C about 71 minutes,
W another 35, plus about 10 minutes preparation/reporting and 2.5 hours agent work,
roughly **4.5 hours total**. These extrapolate training rates; harder excluded cells,
whole-library behavior and adequate precision remain to be priced. Allocate **5–7
hours total**, including preparation, review, analysis and contingency, with **at most
4 hours summed queue timeouts** and **120 minutes preparation**. Measure the full
roster's cost before admission; preserve a balanced complete roster if redesign is
necessary. No performance-based task pruning or optional seed top-up.

Source collection is sunk for this comparison, but an acquisition recommendation must
report it. Separate the incremental library extraction/validation cost from C's shared
corpus cost. Estimate repayment from arithmetic mean evaluation or wall-time savings,
in consistent units, rather than dividing costs by a geometric speed ratio. No positive
saving means no demonstrated break-even.

**Exit.** Return to strategy after this result, or earlier on a measured validity,
build or complete-cost obstruction. A useful F/W increment with useful F/C performance
across shape supports investing in acquisition of this repertoire; it does not show
acquisition or family specificity. Within-shape benefit alone limits the repertoire's
reuse. A tight small F/W bound favors the simpler W procedure if W/C is useful. A broad
F/W interval remains unresolved and needs a resolution price; it is not evidence that
block mechanics explain the gain. Harm ends this extractor/operator's expansion at
that scope. No outcome automatically funds another library, fresh bank, optimizer or
mechanism-control cycle.

The closest precedent is [Keijzer, Ryan and Cattolico, *Run Transferable Libraries —
Learning Functional Bias in Problem Domains* (2004)](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf).
This experiment tests literal block insertion alongside a fitted decoder, rather than
their callable-function library mechanism. It is external extraction and frozen reuse,
not per-individual map inheritance.
