---
next: stop
---

Stop this autonomous run at **17/40 experiments**. Keep the remaining **23 slots
unallocated** and open no new root. The useful cheap-acquisition result is worth
carrying forward; another complete candidate does not earn its cost in the roughly
five hours left before **2026-10-10T08:12:10 Europe/Stockholm**. This is a value and
readiness decision, not a consequence of the exhausted root allocations.

The review follows the [core question](../../../README.md#core-question),
[digest](../../digest.md), question tree and reopening conditions,
[plans and owner note](../../plans/), latest decisions and
[recent ledger](../../briefs/2026-10-08-0812-ledger.md).
`uv run python scripts/research.py status` confirms the run count and deadline:
roots 01 and 10 have no allocation left, and 23 is parked with its two slots used.
No existing question, budget, digest or historical brief is changed here.

**What the program has learned.**

- **Program supply, discovery and persistence are different bottlenecks.** Random
  frequency predicts easy tasks better than hard evolutionary discoveries. Cheap
  joins explained the tested composition advantage. Mixing between lineages blocked
  rare seeded shared forms; self-mating relieved that barrier. Natural B-helper
  arrival and single-copy fate remain unresolved. The older folding/regime-shift
  and CA work supplies context, not evidence of learned transferable map bias
  ([root 01](../../questions/01-map-bias/question.md)).
- **Selection can learn useful token bias.** Outer-selected token maps transfer
  roughly 2× gains after programs are discarded; both initialization and ongoing
  decoder use contribute. Family specificity remains unresolved. The tested
  contextual selection procedures have not established an additional useful gain
  ([root 10](../../questions/10-compositional-map-transfer/question.md)).
- **External fitting finds useful structure that those learners did not.** Solver
  context beat token fitting about 2.12× on then-addition when fresh. Pooled and
  positional frequency projections failed to reproduce it; random mutation-width
  recoding hurt at fixed random-program supply. Literal fragments added about
  1.47× over C and 1.20× over C-chain blocks. Suffix preservation was unnecessary
  at the tested resolution. Partial-program fitting helped modestly, while the
  tested pre-solve fragment extractor added no worthwhile increment. These are
  bounded interventions, not a complete explanation of C or semantic modularity
  ([digest and linked studies](../../digest.md)).
- **The cheap recipe, not just the original artifacts, is now credible within
  these families.** Four initial attempts per cell followed by four under the
  resulting C4+F4 bias produces A8. Its original acquisition used about 6.5 M
  evaluations versus 61 M for full F. On fresh two-sum-v1, A8/full-F cost was
  **0.945 [0.819, 1.092]**: a 20% loss excluded, equality unproved. Rebuilding from
  complementary sources gave **G4/A8′ 2.50× [2.17, 2.85]**, clearing the 1.5×
  usefulness bar in both families. It repays acquisition after about 35 searches
  in evaluations on that target roster. These are capped costs; wall-time repayment
  is unsettled because the historical calibration was defective
  ([2303](../2026-10-09-2303/analysis.md), [0145](../2026-10-10-0145/analysis.md)).
- **Inherited bias remains the central missing mechanism.** Root 23's one
  frequency-inheritance procedure failed frozen usefulness: worse than uniform
  on sum, with a max gain above 1.06× excluded. Linkage helped relative to shuffled
  ancestry on max without making the acquired map useful. This limits one rule
  and schedule, not self-adaptation
  ([root 23](../../questions/23-heritable-variation-bias/question.md)).

Every scored bank is now development data. Acquisition still uses the same two
output-addition families; a complementary source roster is not a new family.
The latest PA deficit and A8′/historical-A8 uncertainty do not overturn useful
replication or select a different acquisition policy.

**Root priorities now.** Root **10** has the strongest actionable connection to
the core question: take the successful recipe to different assembly requirements,
then use an observed limit to choose richer acquisition or representation. Root
**23** has the highest long-term mechanism importance: useful bias inherited and
selected through descendants would answer something external fitting cannot.
Its measured-signal reopening condition is not met. Root **01** remains valuable
background, but no new helper evidence or decision requiring a finer supply/fate
estimate justifies reopening its parked children. Another root would reorganize
these gaps without resolving them.

**Current line against different mechanisms.** I searched the literature for this
review. [Salustowicz and Schmidhuber, *Probabilistic incremental program evolution*
(1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/) updates a program-generating
distribution from successful search. A8 belongs to this broad external-fitting
tradition, with different corpus, fragment and frozen-reuse rules.

The owner's alternative gives the variation parameters credit through descendant
success. [Stephens et al., *Self-adaptation in evolving systems*
(1998)](https://pubmed.ncbi.nlm.nih.gov/9847423/) studies genetically encoded
mutation/crossover probabilities without a direct fitness reward for those
parameters. That mechanism differs from estimating counts in solver tapes.
Our negative inherited-frequency result makes another unchanged modifier run poor
value; it does not license replacing inheritance by fitting and calling the gap closed.

A related biological candidate is persistent lineages under changing related goals.
[Kashtan and Alon, *Spontaneous evolution of modularity and network motifs*
(2005)](https://pmc.ncbi.nlm.nih.gov/articles/PMC1236541/) found modular organization
under modularly varying goals in their model networks. My inference is that
maintaining linked program/map lineages across switches could expose a different
selection opportunity than our repeated program resets. Their result does not
establish map inheritance, frozen-map transfer or a benefit in this executor.
A resident-program advantage alone would not answer our core question. This remains
a candidate for a changed exposure/credit study, rather than grounds for an immediate
mutation-scale or curriculum sweep.

**Why the next substantive question needs a new window.** The question for the
steward is: *can the unchanged cheap acquisition recipe learn a useful bias for
composite predicates and transfer to excluded members, once the source family no
longer places addition in the output?* A success extends the recipe's scope; a
well-resolved failure supplies a concrete boundary for acquisition or representation.

I tested the two smallest semantic alternatives before deferring this direction.
These were deterministic bank audits, not evolutionary experiments:

| Candidate | Semantic result |
|---|---|
| Single-sum predicate on D2401, retaining the existing executor | 120 active distinct behaviours; seven survive the ≤9-token/80% screen; at most six mutually separated, even before old-bank exclusions. |
| Two-sum predicate on D1331, retaining the existing executor | 272 active distinct behaviours; eight survive both the short-program screen and old-roster exclusion; at most four mutually separated. |

The [full audits](predicate_domain_audit.py),
[domain result](predicate-domain-audit.json),
[two-sum result](double-predicate-audit.json) and
[exhaustive subset check](semantic-split-audit.json) are retained here. Both screens
completed in about 111 seconds using exported `b6d1974` code and Python canonical/
witness validation. Neither supplies the planned four-source/four-holdout split.
This is not a proof that smaller studies or other banks are impossible; shrinking
the source recipe or weakening separation would change the question being funded.
Rust validation and search feasibility were not measured.

The promising direction now has a [concrete plan](../../plans/independent-input-family-acquisition.md):
use independent indexed scalar inputs to remove the reducer correlations, build and
validate the separate alphabet/bank, then acquire and freeze A8 on a protected split.
Its provisional full cost is **7–10 hours**, including both stages and agent work.
That is a planning judgment, not a measured runtime lower bound. Only its bank stage
plausibly fits now; that stage alone would not change which acquisition procedure
we carry forward. Stop because the complete question is not ready at an adequate
price, rather than because the direction lacked a plan.

| Other candidate | Full-cost/value judgment for this window |
|---|---|
| Score saved S8′ to place the PA deficit | About 35 queue minutes, roughly 1.5 hours total. Feasible, but neither source-roster usefulness nor the carried recipe depends on the answer. Defer until a source failure or policy choice needs it. |
| More A8/full-F or A8/S8 precision, another feedback round, bare-C8 or fragment ablations | Would mainly refine development-bank detail. No deployment horizon, component choice or observed failure makes that increment consequential now. |
| Joint contextual selection from G4 | Still mechanistically relevant. The calibrated continuation precedent alone took 4.63 queue hours, before build/review/analysis; a new learner plus informative frozen evaluation has no credible complete price here. Do not buy another under-sized pilot. |
| Changed inherited exposure or credit | Potentially more important than another external-fit increment, but no measured selectable signal or validated revised procedure currently favors it. Preserve root 23's reopening test; do not rerun the failed law merely because its harness is cheap. |

**Owner note disposition.** The only `owner-*.md` is
[owner-heritable-map.md](../../plans/owner-heritable-map.md). Its SHA-256 is still
`439bf7393e478eecebe519357bbcb314b90720df3de73fd0f482a0e715e7bba8`, matching
[strategy 0145](../2026-10-10-0145/strategy.md); no new or changed note is unanswered.
For the handoff:

- **Pursued at tested scope; further work deferred:** inherited frequencies.
  Reconsider a changed rule with a measured selection signal and informative frozen
  usefulness comparison, or a necessary frequency-only control for inherited decoding.
- **Deferred:** capture and synonyms. The owner's prerequisite of useful inherited
  learning remains unmet. Reconsider after that evidence and a specific reassignment
  limitation; price engine validation separately.
- **Deferred:** optional population-level maps. Token selection worked; contextual
  selection has not established its increment. Reconsider a changed representation/
  ranking signal with a complete learning and transfer price.
- **Declined for this run:** free table mutation and ambiguous intermediates.
  Reconsider only as necessary contrasts in a justified reassignment study, respecting
  the owner's ordering. External A8 feedback does not satisfy step 1.

**What to stop.** End the current output-family acquisition series at its supported
scope. Stop automatic feedback rounds, source-size sweeps, precision top-ups without
a decision, the unchanged pre-solve extractor, finer suffix/recoding tests and blind
contextual optimizer retries. Keep helper, CA and token-reassignment expansion parked.
Carry forward A8, its measured limits and the new bank plan; keep external fitting,
outer selection and per-individual inheritance distinct. No experiment or budget
increase is authorized by this stop decision.
