# Learn reusable executable fragments from training solvers

Candidate plan for [root 10](../questions/10-compositional-map-transfer/question.md),
written by [strategy 0125](../runs/2026-10-09-0125/strategy.md). **Not allocated yet.**
This supplies a bounded alternative for the next review; it is not an experiment
registration or a commitment to a full library-learning engine.

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
