# Make continuation learn before interpreting another context comparison

Concept-plan addendum for [root 10](../questions/10-compositional-map-transfer/question.md),
selected by [strategy 1137](../runs/2026-10-07-1137/strategy.md). This is a research direction,
not an experiment registration. The steward chooses the design and fixes its outcome rules.
This addendum replaces the next-step guidance in [learnable-context](learnable-context.md)
where the new evidence bears on scoring and starting maps.

**Question.** Can a more reliable selection score produce fresh-search improvement from the
saved token maps, and, in a loop that demonstrably improves them, do compact context steps
add to equally funded token tuning?

[0821](../runs/2026-10-07-0821/analysis.md) found repeatable single-step effects but selected
mutants only reached parent level. Neither continuation resolved improvement. Its effort
rule predicted accumulated gains that did not appear. Do not reuse that rule, positive
step-effect variance, or selected-versus-average-mutant performance as evidence that a
loop will climb. Noise and insufficient depth remain competing explanations; this plan
seeks a usable procedure, not a causal diagnosis of their relative importance.

**What to build.** Reuse the reviewed 0821 runner, saved 1723 maps, rank-one representation,
G4, D1331 and ten training cells. Keep inner search and the task split fixed. Change the
outer scoring procedure in one bounded way: give candidate/parent comparisons substantially
more independent search evidence, initially considering about four times the 24-search
effort. Use shared seeds within comparisons and fresh blocks across selection steps.
Paired seeds already existed in 0821; they are not the new intervention. Count rescoring,
selection of the final map and evaluation in the cost. Report actual inner evaluations as
well as search counts, since early termination makes searches unequal in cost.

At variance 2.65 log2², 96 independent searches would give roughly 0.17 log2 score noise,
against about 0.33 at 24. This is a sizing approximation, not a demonstrated learning rate.
Check it against actual paired scores. Avoid a sweep of representations, mutation scales,
objectives and depths. Increasing precision while making the trajectory four times shorter
could simply exchange one limitation for another; measure the full learning budget.

**First experiment.** Use a training-only calibration followed, where affordable, by a
substantive continuation in the same queue. Judge selected candidates against their own
parents on independent seeds, and judge the completed token continuation against its saved
start on fresh searches. A token arm improving from G4 would not establish improvement from
these already-tuned starts. Include both training families and retain all preselected starts;
do not admit only the parents on which the probe succeeded.

The token-only check supplies the positive control for a conditional contextual comparison.
Freeze any procedure chosen using calibration before independent confirmation. Do not pool
calibration trajectories selected for success into the main evidence. If a context stage is
admitted in the same queue, both main arms must use the same procedure and comparable total
effort; the main token arm must independently show progress as well. A tiny pilot's failed
significance test is an unresolved feasibility result, not proof that learning is impossible.
Choose the gate and fixed confirmation size so plausible improvement could actually pass.

Use 0821's observed 0.38 log2 pair spread when sizing C/T: 16 balanced pairs gave a roughly
0.20 log2 half-width. More search seeds cannot replace independent starting-map replication.
The same saved starts permit a conditional comparison of procedures, not a new sample of
task families. No canonical programs or hand-set family-grammar directions enter learning.

**Time and conditional second experiment.** There are about eleven hours left at this
strategy review. Target at most six queue hours for the first experiment, including its
calibration and final scoring, and preserve about three hours for implementation, review,
analysis and contingency. Recalculate at proposal time and before admitting a stage; the
eight-hour per-queue ceiling is not the available wall time. The old throughput of roughly
1,200 searches/minute is a planning reference, not a guarantee for altered scoring.

If token continuation learns but the first queue cannot fit a meaningful C/T comparison,
the added slot can settle that comparison. If a contextual training increment is already
established, it can instead test frozen-map transfer beyond token controls on the three
existing withheld cells. Include frequency-matched controls if attributing the increment
to context rather than changed marginals. These are reused screened targets, not pristine
holdouts. Do not tune against them. A full second learning study is not promised within
this deadline; reserve it only if measured runtime and precision fit after analysis.

**Answers and exit.** Improved T/S followed by improved C/T would establish useful additional
adaptation for this procedure; family-specific transfer still requires matched/mismatched
evaluation. Improved T/S with a tight small C/T bound limits contextual continuation here.
No resolved T/S progress limits this attempted procedure and leaves context unresolved.
Broad C/T bounds after a working token control justify a sized continuation only if it fits
and would change the decision. Return to strategy after the result. Do not automatically
extend this into another optimizer sweep or interpret a failed gate as ending the program.
