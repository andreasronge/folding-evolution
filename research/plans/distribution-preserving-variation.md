# Change variation while preserving the program distribution

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
allocated by [strategy 0537](../runs/2026-10-09-0537/strategy.md). This is a question and
implementation direction, not an experiment registration. The steward fixes the design,
sample size, practical effect and decision rule.

**Question.** Can a recoding of Q that preserves its entire random-program distribution,
but broadens the changes caused by variation, improve search enough to approach C?
Q is the frozen G4 grammar matched to C's emitted frequencies at every position.
[0306](../runs/2026-10-09-0306/analysis.md) found C/Q 2.41× [2.11, 2.75], with about
2.97 versus 1.73 tokens changed by one allele resample. That association does not show
that larger changes help. It makes a specific alternative to acquiring new transition
probabilities worth testing.

The intervention changes which alleles encode each token in each context. It does not
change token meanings, conditional probabilities, tape length, selection or the nominal
mutation/crossover rates. A success would connect the two parts of the core question:
the distribution of random programs would be an insufficient target for learning a
useful map, even when that distribution is matched exactly.

**What to build.** Reuse `composition_search.py`, `position_matched.py` and the reviewed
0306 runner on `research/main` (completed code `2bab2c2`), the 16 frozen Q/C tables,
D1331 length-three inputs, `v2_rmin_first` and the then-addition development bank.
The current `main` checkout does not contain those runners. Inspect and extend the
research implementation; no new executor or bank is needed.

For a lookup row L at position j and previous token r, define
`L_new[j,r,u] = L_Q[j,r, permutation[j,r,u]]`, where each permutation is a fixed
bijection of the existing integer allele range. A bounded candidate is independently
permuting a fraction of allele entries within each body row, leaving the position-zero
start lookup unchanged. Keep the permutation fixed throughout search. A shared
permutation across all contexts is only a relabeling and is not the intended intervention;
context-dependent permutations change how a changed previous token propagates downstream.

Every row retains exactly the same count of each token. Under independent uniform
alleles, the probability of any complete token tape is the product of these unchanged
conditional probabilities. Therefore the entire program distribution, including exact
solver frequency and positional marginals, is unchanged. Validate this algebraic invariant
with exact row-count checks after construction; a sparse sampling census is unnecessary.
This equality concerns the uniform prior, not the populations that selection visits.

Pair Q and its recoding with **identical initial token tapes**. Given the original Q
alleles and their decoded previous-token contexts, apply the inverse permutation to each
allele to represent the same tape under the new lookup. This is a bijection of genotype
space that preserves the uniform prior. Verify full-tape and initial-fitness equality.
Apply it at initialization only. Do not repeatedly re-encode populations or elites.
Preserve case/selection/variation streams; give construction randomness its own stream.
Hash the actual recoded lookup/permutations, not just the unchanged probability table.

Strategy checked lookup construction on BE1 and PA1 without scoring any task: at 2,048
uniform latent tapes, a single random-site resample changed about 1.77/1.73 tokens under
Q and 2.49/2.55 after independently permuting 20% of each body row. All row counts were
exactly preserved. These are descriptive implementation checks, not search evidence or
a calibrated replacement. Source: 0306 preparation's `projected_tables.json`; latent
seed 202610090537, permutation seed 537, positions 1–31 and previous tokens 0–23.
Construction and all eight checks at fractions 0, .05, .10, .20 took about one second;
this does not price evolutionary scoring.

**Calibration and first experiment.** Before efficacy scoring, use a bounded,
performance-blind calibration of the recoding fraction to put Q's mutation displacement
near C's. Preserve every corpus and both fitting families. Freeze the construction rule,
calibration tolerance and construction seeds; never select permutations by search cost.
Use predeclared independent construction realizations rather than one lucky common
permutation. Corpus remains the inference unit; multiple realizations are nested in it.

Measure the distribution of changed-token counts, positions and contiguous spans, not
only its mean. Check ordinary single-site resampling and the actual offspring operator
(Bernoulli mutations after crossover); the existing 2.97/1.73 diagnostic is not the
full operator. Audit on uniform tapes and available training-derived parents with a
specified encoding law. These audits describe transport to selected states, not exact
matching of every population's neighbourhood. Return for review if the intended
intervention cannot be obtained without a new optimization project.

The primary question is the within-corpus search-cost improvement of recoded Q over Q.
Keep C as the practical benchmark: beating Q alone does not reproduce C. Reuse legacy
Q/C rows only after exact replay, case and initial-token checks; price new reference
rows if pairing cannot be recovered. Retain all 16 source corpora and the frozen bank
roster where affordable. No new solver collection is needed. Fix a decision-sized
comparison before efficacy scoring, with a 95% interval, solve counts, per-cell results,
cap sensitivity and an unresolved outcome. Treat then-addition as development data.

**Interpretation and next choice.** Improvement over Q would demonstrate an effect of
the changed representation/variation at fixed random-program supply. Approaching C
within a useful bound would make variation coupling a credible, cheaper acquisition
target before building fragment libraries. Improvement that leaves a substantial C gap
establishes a contribution for this recoding, without partitioning C's original advantage.
A tightly small or harmful change limits this recoding and weakens this particular
replacement; it does not establish that C's probabilities are necessary. Wide intervals
require a resolution price. None of these outcomes shows evolutionary acquisition.

The intervention can affect crossover as well as mutation, and alters edit correlations
as well as size. Even a successful mean match does not isolate mutation width as the
cause. Preserve and report that scope instead of claiming an exact neighbourhood match.
The related literature is [Stephens, *Effect of Mutation and Recombination on the
Genotype-Phenotype Map* (GECCO 1999; 2000 preprint)](https://arxiv.org/abs/nlin/0006051),
which studies operator effects among equivalent genotypes. Our particular recoding and
its possible benefit are hypotheses, not results supplied by that paper.

**Full cost and exit.** One root-10 slot through the next review, **6–8 hours total**:
up to two hours preparation, roughly two to three hours scoring/diagnostics, and two
to three hours proposal, review, analysis and contingency. These are allowances pending
measured recoded-search throughput. Q's 2,048 searches averaged 11.7 worker-seconds in
0306; the combined Q/P queue took 96 minutes. Slower recoded searches and nested
construction replication must be included in the new price. Summed queue timeouts
at most four hours; preparation at most 120 minutes. Do not stack extra safety on an
already all-capped bound as in the superseded 0239 admission calculation.

Prefer calibration and a substantive comparison within one cycle. A feasibility-only
probe has the separate 60-minute timeout ceiling and returns to strategy without an
efficacy verdict. Exit after the result or a measured validity/build/cost obstruction.
No automatic recoding sweep, reverse ablation, new bank or fragment stage follows.
The next review compares a justified acquisition question with the existing
[fragment plan](learned-executable-fragments.md), whose complete 11–16-hour allowance
must still fit the actual remaining deadline.
