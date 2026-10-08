# Inherited variation bias

Concept plan for [root 23](../questions/23-heritable-variation-bias/question.md), selected
by [strategy 2243](../runs/2026-10-07-2243/strategy.md), pursuing step 1 of the
[owner note](owner-heritable-map.md). This is not an experiment registration. The steward
chooses the primary comparison, fixed sizes and decision rules.

**Question.** Can program selection acquire a useful token-generation distribution when
that distribution is inherited with each individual? Does its benefit survive discarding
the programs, extend to an excluded family member, and improve on the existing hand-set
scaffold? This separates acquisition, frozen usefulness and practical improvement.
The map here is a variation/sampling law; token meanings and developmental decoding stay fixed.

The closest technique is self-adaptation of strategy parameters, as in
[Stephens et al. (1997)](https://arxiv.org/abs/adap-org/9708002) and
[Serpell and Smith (2010)](https://doi.org/10.1162/EVCO_a_00006).
Those studies motivate inherited variation parameters, not this task-family result.
Unlike the [PIPE](https://pubmed.ncbi.nlm.nih.gov/10021756/)-related corpus procedure in
root 10, no external likelihood fit updates the evolving vector. Unlike root 10's outer
learner, no candidate vector receives a fitness computed from multiple independent searches.
Only program performance determines reproduction within the evolving population.

**What to reuse and build.** Start with the reviewed TAG harness at commit `9abc25c`
(`experiments/chem_tape/evolve_bias.py`, vector artifact and `family_bias.py`) and its later
corrections on `research/main`. The current `main` checkout lacks parts of that runner.
Reuse its exact verifier, task cases and ordinary operators, not the latent-context
composition decoder. Existing Python reproduction calls `tagged.mutate_batch` with one
global `op_probs` vector; it records recipient/mate indices. A per-child probability row
and a parallel inherited-parameter array should allow the mechanism without a Rust
decoder rewrite. This is a code inspection, not a measured preparation/runtime guarantee.

Each individual carries its ordinary token tape and positive normalized op probabilities,
represented by bounded log weights with a support floor. Begin without family information
in those weights. Retain total mutation, insertion, deletion and crossover rates. Mutating
weights does not reinterpret any existing token. In reproduction copy the selected
recipient's weights, perturb them slightly, and use the resulting child weights for its
newly drawn ops. Crossover copies program material under the existing rule; inherit the
modifier from the designated recipient, rather than silently averaging parents. Copy
elite weights with elites. Fix that inheritance convention before outcomes; it is part
of this procedure, not a universal model of biological inheritance.

Validate per-row draws, support, normalization, parent/child bookkeeping and that modifier
changes alone leave a resident tape's execution unchanged. With modifier mutation disabled
and all rows identical, recover the existing fixed-weight operator law and baseline search.
Preserve a legacy path for exact replay where possible; changed RNG consumption must be
identified rather than disguised as identical seeds. Keep modifier randomness separate.
Use the existing Rust executor for batches. If implementation exceeds one 120-minute
prepare, return a measured build obstacle; do not expand into a general coevolution engine.

**Task exposure and controls.** Use the existing sum/max threshold development bank on
length-four lists over 0..9. Train separate populations on thresholds 1 and 5; exclude
threshold 2 from adaptation, calibration and map selection. Their differences are constant
substitutions, so this establishes only a small mechanism test. It does not reproduce
root 10's compositional claim or supply a fresh task bank. Recover exact task and vector
definitions from artifacts, and verify all proposed training targets on the 10,000-input
domain; the old holdout runner hardcodes threshold 2 in places and needs explicit generalization.

Use a fixed, balanced schedule of training episodes with fresh training cases. At episode
boundaries discard program tapes and restart them while retaining the population's modifier
vectors; keep the schedule identical across arms. This gives repeated discovery pressure
and prevents transferring a solved program between targets. It is an imposed laboratory
exposure rule, not evidence that natural evolution performs resets. Freeze episode effort
and final extraction before confirmation; stopping on the best-looking modifier checkpoint
would add external map selection. Record exact solves but distinguish them from the fitness
that actually drives selection.

Compare persistent inheritance with a control that breaks program–modifier ancestry while
retaining the same allowed distributions, mutation rule and task exposure. A concrete
candidate is to permute modifier vectors uniformly among individuals immediately before
parent selection each generation, including those eligible for elitism. The control's
marginal distributions will subsequently evolve differently; that is an effect of the
intervention, not a reason to match them after seeing outcomes. It tests the consequence
of persistent linkage, not selection versus drift in all possible senses.

Keep uniform and the frozen family-appropriate INPUT/GT/aggregator scaffolds from 1705
as fixed controls, with the same task schedule where acquisition cost is compared. They
are supplied priors, not evidence of learning. The saved external fits are useful reference
vectors if inexpensive to score. Do not use their values as initial learned weights or
reward proximity to them. Show vector trajectories descriptively; resemblance to a fit
does not prove useful adaptation.

**First experiment.** Validate the path and measure selection opportunity, throughput,
between-training-run variability and frozen-map performance on fresh *training-task*
searches. Choose one bounded modifier rule and exposure schedule using training-only
calibration, then freeze it for independent acquisition runs. Avoid a sweep of mutation
scales, curricula and crossover rates. Confirmatory units are independently adapted
populations, paired across procedures where appropriate, not individuals from one population.

For frozen evaluation, choose a deterministic extraction rule in advance, such as the
arithmetic mean of final population probabilities, then apply that one vector globally
in otherwise unchanged fresh searches. This intentionally asks about a transferable global
bias; it may miss advantages that require a heterogeneous population of modifiers. Save
individual vectors to preserve that distinction. Never transfer program tapes or choose
vectors using evaluation performance. Compare inherited versus ancestry-broken extraction,
uniform and scaffold. A within-training solve gain alone is not the endpoint.

Size one primary search-cost comparison with a 95% interval and an explicit worthwhile
increment; set the scaffold requirement before outcomes. Preserve failed searches in the
cost. Training map acquisition and later scoring both count. The old 1705 queue completed
in about 20 minutes, but it used fixed vectors and early exact stopping: it does not price
fixed-duration acquisition episodes, heterogeneous probabilities or the new controls.
Measure these before promising the full study.

**Conditional second experiment.** Freeze the procedure and score independently acquired
vectors from both families on sum>2 and max>2 with fresh populations and seeds. Include
matched/mismatched training and the fixed controls; retain training-run uncertainty.
No extra holdout seeds can replace independent acquisition runs. This is transfer within
the reused threshold bank, not a general family result. A full transfer comparison is
worthwhile only if the first result leaves a credible, affordable decision about inherited
usefulness and practical value. A broad first interval may instead justify a properly
sized training resolution; obtain strategy review if only feasibility ran or the procedure
needs changing.

**Allocation and answers.** Two experiments; target at most four queue hours each, with
about six additional hours for preparation, code review, analysis and contingency: a
10–14 h block inside the new 48 h run. These are spending ceilings pending measurement,
not forecasts from the old fixed-weight rate. If the first slot is only a `kind: probe`,
its total queue timeouts must be at most 60 minutes, fixed seeds and descriptive outputs;
return to strategy before confirmation. Do not consume the whole block proving that code runs.

A frozen advantage over the ancestry-broken control and uniform supports useful acquisition
through this inheritance procedure. A matched-over-mismatched transfer advantage addresses
family dependence separately. A gain over the scaffold is the reason to consider a richer
bank or the owner's next steps. Matching the scaffold is scientifically informative about
acquisition, but does not earn further machinery. Gains confined to resident tapes or
training targets limit transfer. Tight small-effect bounds limit the tested procedure;
broad bounds remain unresolved and require a priced decision-sized continuation, not an
automatic negative. Report total acquisition evaluations/time and the number of future
searches needed to repay them; where no measured saving exists, there is no break-even.

No token reassignment, synonyms, free table mutation, new alphabet, shortcut veto or
additional corpus-feedback round is included. Review before expanding this plan.
