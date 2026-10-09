# Can a cheap acquired bias improve its own next source batch?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
allocated by [strategy 2033](../runs/2026-10-09-2033/strategy.md). This is a direction
and complete-cost envelope; the steward supplies the proposal, fixed size and decision
rule. It is not an experiment registration.

**Question and reason.** Does using the four-attempt C4+F4 procedure to collect the
next small batch teach a better complete decoder/library than spending the same
attempt allocation under G4? Does its improvement repay the additional acquisition
relative to keeping C4+F4? This tests adaptive versus static acquisition, rather than
locating an adequate corpus size by a sweep.

There is a specific positive precedent: [21](../questions/10-compositional-map-transfer/21-iterated-solver-corpus/question.md)
found that exact-source feedback beat a fresh G4 refit on withheld compositions
1.33× [1.26, 1.40]. However, it started with a large, successful corpus on an easier
bank. [35](../questions/10-compositional-map-transfer/35-small-source-acquisition/question.md)
now supplies cheap but weaker seeds and a measured acquisition/performance trade-off.
Small collections may amplify useful syntax or lock in accidental omissions. Neither
the large-corpus result nor partial-program feedback answers that boundary question.

The closest technique is [Salustowicz and Schmidhuber, *Probabilistic incremental
program evolution* (1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/), which updates a
program-generating distribution using search results. Here the update is a batched
external fit to exact solvers, followed by frozen reuse across compositions. It is
neither per-individual inheritance nor selection among decoder genotypes.

**Reuse and bounded build.** Inspect the reviewed code on `research/main`, especially
`small_source_run.py`, `small_source_report.py`, `solver_corpus_fit.py`,
`fragment_library.py`, `fragment_operator.py` and `composition_search.py` (35's code
`652fde5`). The small-source runner already saves exact solvers from block-operator
searches and builds both components. Use `solver_feedback_run.py` as orchestration
reference, not as a bank definition: it uses the older split. These runners are absent
from the current `main` checkout; do not recreate the search engine.

Keep comparison-gate-v1's four training cells per family, D1331 length-three inputs,
G4, the alphabet, 32-token tapes, P256, the search cap, exact verifier, fitter and
fragment extractor unchanged. Use 35's saved source manifests and rebuilt C4+F4 seeds,
including empty cells and small libraries. Preserve both families and the four
preassigned source blocks per corpus; do not select the successful cheap acquisitions.
The 64 builds are nested within sixteen corpus units for continuity with the previous
analysis, not 64 independent task-family replications.

A concrete single update to price is **four initial plus four further attempts per
training cell**. Both procedures share the same first four G4 attempts. In the
adaptive procedure, collect the further four under that build's frozen C4+F4, including
its existing block operator and fallback. In the static procedure, collect them under
G4. Each attempt starts a new program population; no solved tape is seeded into it.
This intervention changes the whole collection policy, including its operator. It
does not isolate the decoder from the library or yield from content.

Pool each procedure's first and second batches, then rebuild its final C and F with
the unchanged equal-cell normalization, shrinkage, activity/recurrence rules and
fallbacks. In particular, normalize to the same fitting mass as before: more tapes must
not silently weaken the prior. Pooling and fitting rules must match across procedures.
Do not substitute the last batch alone after looking at outcomes. No third update,
source-size sweep, collection-until-success rule or new fragment selector is included.

Static continuation may reuse disjoint saved G4 attempts, selected by schedule order
before performance inspection, with their original acquisition cost charged. Verify
that continuation attempts do not overlap any seed batch being treated as independent;
choose a deterministic assignment across all four blocks. If that cannot be validated,
collect fresh static controls and include them in the price. Hash attempt keys, source
tables/libraries and final fits. Preserve exact-solver checks and legacy replay. Keep
new collection seeds separate from all evaluation and timing seeds. An empty second
batch remains an outcome, never grounds to refill or drop an acquisition.

**First experiment and answer.** Evaluate both completed procedures on the complete
then-addition roster, using fresh program populations and paired evaluation cases/seeds.
Keep the retained C4+F4 and full C+F results as practical references, plus the existing
G4 reference where appropriate. Historical rows require provenance and exact replay;
otherwise price rescoring. Shared latent seeds across different decoders need not
produce identical initial programs. These are development sources and development
targets; no fresh-bank transfer claim is available.

The primary comparison is adaptive versus static acquisition at equal allocated
attempts and caps. The steward should choose a useful effect and fixed size that can
distinguish a substantial gain from an increment too small to warrant feedback. Preserve
corpus uncertainty, source-block variation, both families, solve counts and cap
sensitivity. More scoring seeds cannot replace acquisition replication. Do not decide
from an unpaired smoke average against a historical geometric mean, which misled 35's
forecast. Timing calibration is not evidence that feedback works.

Also report arithmetic acquisition-plus-search costs, A + N*S, for adaptive, static,
retained-small and full procedures. Charge the common first batch once per deployed
procedure, all failed attempts, the intermediate fit/library used for collection and
the final rebuild. Equal attempts are equal allocation, not equal realized cost or
solver count. Report evaluations and measured wall/worker time separately; do not
import 35's weak two-row timing calibration as a precise economic comparison. Display
the reuse ranges where each procedure is preferable rather than inventing an owner's
deployment horizon. Capped effort is not uncapped expected time to solve.

A worthwhile adaptive/static advantage, useful beyond retaining the seed and supported
by the cost curves, would establish that the cheap bias can improve its own acquisition
procedure on these excluded compositions. This matters even if it does not recover
the full corpus's speed. Equal improvement in both enlarged procedures supports buying
more data without a demonstrated feedback benefit. Tight small effects or harm end
this sparse feedback policy. Wide intervals remain unresolved and require a resolution
price. No outcome identifies family specificity, semantic modules, or endogenous map
evolution. Without token and chain controls, do not partition the gain between context,
frequencies and fragments.

**Complete cost and exit.** One experiment through the next strategy review; expected
**6–9 hours total**, including up to two hours preparation, roughly 2–4 hours collection
and scoring, and 2–3 hours proposal/review/analysis/contingency. These are planning
allowances, not quotas. Summed queue timeouts at most **5 hours**,
reduced as needed to finish analysis before **2026-10-10T08:12:10**. Preparation remains
capped at 120 minutes.

The concrete price anchor is 35: 8,192 two-arm searches took 104 minutes, plus 131 seconds
of queued preparation. A similarly balanced scoring scenario costs that order of time,
with 1,024 additional adaptive collection searches (64 builds × four cells × four
attempts), and another 1,024 if static sources must be rerun. The old sparse arm's mean
7.4 worker-seconds per evaluation search is only an anchor: new training collection,
feedback fits, failed sources and verifier tails need measurement at intended concurrency.
The scenario does not prescribe an adequate sample size. Price the complete decision,
including references, before admission; the historical pipeline already supplies the
interfaces, but this review has run no new efficacy or timing experiment.

Return to strategy after this one result or an earlier measured build, validity,
precision or full-cost obstacle. A separate feasibility-only cycle is not the intended
deliverable; a probe fallback must obey the 60-minute timeout limit and still justify
confirmation within the remaining window. No automatic third round or fresh bank is
funded. If the complete comparison cannot fit or cannot distinguish a decision-relevant
effect, return the slot for a stop/value review rather than running merely because a
small queue is feasible.
