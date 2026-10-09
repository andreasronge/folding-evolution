# Learn reusable executable fragments from training solvers

Candidate plan for [root 10](../questions/10-compositional-map-transfer/question.md),
written by [strategy 0125](../runs/2026-10-09-0125/strategy.md). **First stage allocated by
[strategy 0826](../runs/2026-10-09-0826/strategy.md); reuse stage requires review.**
This is a bounded direction, not an experiment registration or a commitment to a full
library-learning engine. The current allocation and qualifications appear below.

**Question.** Does treating learned program fragments as units of variation improve
fresh search beyond the existing fitted previous-token decoder and matched primitive
supply? A fragment changes which coordinated edits are easy to make. The current table
changes next-token probabilities but supplies no explicit reusable unit.

Literature searched for this review: [Ellis et al., DreamCoder (2020 preprint)](https://arxiv.org/abs/2006.08381)
learns symbolic abstractions and a search guide. The repository analogue proposed here
is much narrower: a small, externally extracted library of literal stack fragments,
without neural guidance, parameterized functions or recursive library growth. It would
test learned variation units, not inherited map evolution. The paper motivates the
mechanism; it supplies no evidence of a benefit in this harness.

**What to build first.** Reuse the independent exact-solver training corpora from 1246,
D1331 and the unchanged primitive executor. Extract short recurring contiguous fragments
from training solvers only, with a deterministic bounded length/library-size rule and
equal weighting of source tasks. Freeze the extractor before evaluation. A first scope
is fragments of three to six primitive tokens with a well-defined stack effect; exclude
complete training solutions and reject fragments whose apparent reuse is only inert
padding. Establish stack effects and actual contribution using executor traces or a
validated dependency replay, including underflow, wrong-type and conditional behavior.
Do not equate token frequency with executable reuse or use canonical target programs
to supply the library. If a small trustworthy extractor cannot be built in one prepare
cycle, report that obstacle before expanding the project.

Use fragments as bounded, same-length block replacements in decoded offspring, retaining
the primitive tape length and executor. A fragment need not become a new Rust opcode.
`composition_search.Decoder.encode` already provides conditional-uniform inverse encoding;
check it before using it to represent edited tapes. Re-encoding changes latent variation,
so every compared block-replacement arm must use the same path and randomization law.
Keep the established C search as a separate practical benchmark; do not attribute a
difference from legacy C entirely to fragments if that path differs.

**Controls and first answer.** Compare intact learned blocks with blocks assembled from
their matched per-position token distributions at the same span lengths, replacement
rate and primitive work. This removes cross-position dependence while retaining the
operator's gross edit size and token supply. Keep unmodified fitted C as the strong
benchmark. A shuffled block is not automatically a fair control: its invalid-stack rate
may explain the entire difference. Report that diagnostic and narrow the inference if
validity changes. A gain over this control alone cannot show superiority to learned C.

Freeze libraries per independent source corpus, discard solver programs and initialize
fresh populations. Start with training-cell calibration and a substantive comparison
if affordable; no library or rate is chosen using evaluation-bank performance. Retain
the source-corpus unit of uncertainty. Count extraction and source acquisition as well
as search evaluations, executed primitive work and wall time. Root 01's cheap-join result
is the warning: shorter assembly or larger edits can explain an advantage without a
special modularity mechanism.

**Staging and full cost.** Planning allowance: **5–7 h** for extraction, semantics,
operator validation, measured timing and a decision-sized training comparison, then
**6–9 h** for a separately reviewed reuse test: **11–16 h total**, including agents and
contingency. These are unmeasured allowances, not forecasts from C's throughput. Each
stage needs its own measured price and at most four queue hours; a feasibility-only
probe must instead stay under 60 minutes of timeouts. The first stage must price the
complete second stage, rather than only show that fragments can be extracted.

Existing comparison-gate holdouts and then-addition can test reuse on development data.
A claim of fresh-bank transfer needs a separately frozen bank and method and an added
semantic/build price; it is outside this allowance. Root 10 already serves the narrow
question, so a new root is not required merely to try a different representation.

**Answers and reconsideration.** A useful gain beyond matched supply and legacy C would
justify a new representation at this scope; survival on excluded compositions would
support reuse. Improvement only over damaged or weaker controls would not. Tight small
effects limit this extractor/operator; broad intervals need a resolution price.
Reconsider this candidate at the next strategy review when the K result and a bounded
training-corpus inspection can justify the full cost. C beating K would strengthen the
case for structure beyond pooled frequency, but would neither prove this candidate nor
be a necessary condition for it. No automatic abstraction build follows a positive K test.

**Allocation and update, 2026-10-09 0826.** K and the positional replacements Q/P have
now failed to reproduce C on then-addition. Random recoding of Q to C's mutation width
made it slower at exactly unchanged random-program supply
([0537](../runs/2026-10-09-0537/analysis.md)). These results remove specific simpler
replacements; they do not establish executable fragments as C's mechanism or predict
that this library will help. The new question is whether explicitly learned, coherent
variation units add useful search power beyond C itself.

Allocate **one experiment**, root 10 budget **22 → 23**, through the next strategy
review. The steward should open a sub-question for this representation test, retaining
the earlier questions as completed references. Expect **5–7 h total** for extraction,
validation, measured pricing, training comparison and agent review, with at most **4 h
summed queue timeouts** and the **120 min prepare limit**. The separate reuse stage
remains an unallocated **6–9 h**, making **11–16 h** for the complete candidate. Reprice
both stages before admission using the actual deadline, 2026-10-10T08:12:10. The
remaining approximately 24 h is time for a complete answer, not a reason to enlarge it.

Use the existing 1246 training corpora and frozen C tables. Source inspection in this
review confirms that `Decoder.encode` and the ordinary offspring path are available
on `research/main`; it does not establish the cost of the fragment path. The extractor,
dependency checks and block operator remain new work. Preserve independent corpora and
both source families; no library, fragment length, insertion rate or corpus is selected
by then-addition or comparison-gate holdout performance. Repeated substrings alone are
not evidence of active reusable computation. Require the bounded semantic check in the
original plan, and retain source-task provenance and empty-library outcomes.

Keep two questions distinct. Intact blocks versus their position-matched block control
asks whether their joint content helps under the new operator. Intact blocks versus
unchanged C asks whether the new procedure is worth using. **A win over a damaged block
control alone does not earn the reuse stage.** Recent random-recoding losses make this
particularly important. Report underflow/wrong-type/default use, contribution to output,
and realized token-change footprints: equal replacement spans do not guarantee equal
numbers of changed tokens. The executor has closed semantics, so these are differences
in effective computation, not necessarily invalid programs or crashes.

Use the same re-encoding law in all block arms. A difference from legacy C can include
the new operator and latent refresh; do not call it an isolated effect of fragments.
If separating that implementation effect becomes necessary, price a matched-path
control before adding it. Do not turn the first study into a general operator matrix.
No new opcode, function-call engine, recursive abstraction learner or fresh task bank
is part of this allocation. All current evaluation banks are development data.

Exit to strategy with a decision-relevant training comparison, interpretable controls,
and a measured price for frozen-library reuse; or return earlier with a specific
semantic, build or complete-cost obstruction. A useful increment over C, supported by
the block-content comparison, would justify considering reuse on excluded compositions.
A tightly small increment or harm ends this extractor/operator's expansion. A broad
interval requires a resolution price, not a negative verdict. If only a probe is
possible, keep its queue timeouts within 60 minutes and reprice confirmation **and**
reuse before requesting more allocation. No automatic length/rate sweep follows.
