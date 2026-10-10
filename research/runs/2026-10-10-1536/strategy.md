---
next: proposal
---

Continue with **one protected transfer test of cheap acquisition on the
independent-input double-gate family**, question 40 under root 10. The
[steward's suggestion](steward_proposal.md) earns this allocation because its
answer changes the demonstrated scope of the acquisition recipe. The probe's
successful implementation alone would not justify it.

`uv run python scripts/research.py status` reports autonomous run
**2026-10-10-1419**, **1/40 experiments used**, deadline
**2026-10-12T14:19:15 Europe/Stockholm**; about 47 hours remain at this review.
The review covers the [core question](../../../README.md#core-question),
[digest](../../digest.md), three roots and their child questions/reopening
conditions, [plans and owner note](../../plans/), and recent decisions and
[briefs](../../briefs/2026-10-10-2026-10-10-0311.md).

**What the program has learned.**

- **Supply, discovery and persistence are different properties of a map.**
  Random-genome frequency predicts easy tasks better than hard evolutionary
  discoveries. Cheap joins explained the tested composition advantage;
  lineage mixing blocked rare shared forms, while self-mating relieved that
  barrier. Natural arrival and single-copy establishment remain unresolved.
  These results explain particular search dynamics, without establishing
  acquired family bias ([root 01](../../questions/01-map-bias/question.md)).
- **Useful bias survives discarding the programs that taught it.** Outer
  selection learned token weights giving roughly 2× transfer, with both
  initialization and ongoing decoding contributing. The tested contextual
  selection procedures added no resolved benefit. External solver fitting
  did: context versus token fitting was **2.12× [1.86, 2.41]** on then-addition
  when fresh. Pooled/positional frequency replacements did not reproduce it;
  random recoding to match mutation width hurt. Conditional content and
  structured variation remain unseparated ([digest](../../digest.md)).
- **Short learned blocks add value, and acquisition can be cheap.** Fragments
  added **1.47×** over fitted context and **1.20×** over its chain blocks on
  then-addition; this does not establish semantic modules. A8—four source
  attempts per cell, fit, four adaptive attempts, refit—retained useful
  performance on fresh two-sum-v1 at about a tenth of full acquisition cost.
  Rebuilding from complementary sources again gave **2.50× [2.17, 2.85]**
  over G4, repaying acquisition after about **35 searches in evaluations**.
  This is one alternative roster within the original two source families;
  equivalence to historical builds and general wall-time savings are unshown
  ([37 decision](../2026-10-09-2303/decision.md),
  [38 analysis](../2026-10-10-0145/analysis.md)).
- **Inherited usefulness is still missing.** The tested inherited-frequency
  rule made frozen search worse than uniform on sum; on max a gain above
  1.06× was excluded. Persistent ancestry helped relative to shuffled
  ancestry on max without establishing useful acquisition. This limits one
  rule and exposure schedule, not self-adaptation
  ([root 23](../../questions/23-heritable-variation-bias/question.md)).

The newest evidence is **a probe observation, not a confirmed transfer result**.
[0311](../2026-10-10-0311/analysis.md) produced a validated 4-source/4-development/
8-protected split on `v2_x4`, D625. G4 found only 22/128 first-batch solvers;
the median 2.5/16 missed the stated discovery reference. Four intermediate
*fragment libraries* were empty, but their context fits still existed; all
eight final builds completed. On development cells A8 solved 55/64 versus
G4's 7/64. The 12.2× capped-cost ratio falls to 7.3× at the alternative penalty.
This supports paying for independent confirmation, while leaving source
fragility, baseline quality and effect magnitude open. The protected cells
have never been searched.

**Which roots matter now.** Root **10** comes first: whether the unchanged
recipe can acquire useful bias for different assembly requirements determines
how far the practical answer to the core question extends. Root **23** remains
the most important mechanistic gap: adaptation through descendants would
answer something external fitting cannot. The new probe supplies no inherited
signal and does not meet its reopening condition. Root **01** remains useful
background, but further helper, shortcut or fixed-target refinements would not
change the present acquisition choice. Its budget stays unchanged. No new
root is needed; both new-root allowances remain unused.

**The current line against different mechanisms.** Literature searched for
this review places A8 near [Salustowicz and Schmidhuber, *Probabilistic
incremental program evolution* (1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/):
search outcomes update a program-generating distribution. A8 uses external
batched fitting and frozen reuse, with different context and fragment rules.
Its case today is the existing transfer evidence plus a strong, independently
testable development observation.

The owner's alternative is **per-individual self-adaptation**: variation
parameters receive indirect selection through their descendants, without a
corpus fitter. [Stephens et al., *Self-adaptation in evolving systems*
(1998)](https://pubmed.ncbi.nlm.nih.gov/9847423/) demonstrates this principle for
encoded mutation/crossover probabilities in model landscapes, including a
changing environment. A concrete repository candidate is preserving linked
program/map lineages across related goal changes rather than resetting their
programs between episodes. My inference is that this could change the credit
available to modifiers; the paper does not establish transferable token bias
here. It ranks below confirmation because the existing inherited result is
negative and no revised rule yet has a measured selectable signal. The
[inheritance plans](../../plans/heritable-bias-equal-exposure.md) remain the
starting point, not authorization for another unchanged run. Reconsider a
bounded changed-rule study when its signal and full acquisition-plus-frozen-
evaluation cost justify displacing other work.

A second candidate is **parameterized callable abstractions**. [Ellis et al.,
*DreamCoder: Bootstrapping Inductive Program Synthesis with Wake-Sleep Library
Learning* (PLDI 2021)](https://www.neurosymbolic.org/papers/EllisWNSMHCST21.pdf)
learns abstractions and a search policy. Unlike literal window insertion,
argument binding could reuse computation across changed inputs. That is a
plausible representation hypothesis, not an explanation of our results.
The pilot currently shows literal fits coping with the new family; it offers
no identified binding failure that would justify the extractor, call semantics
and validation work now. Reconsider if protected results expose such a limit.
If that becomes the leading candidate, write its staged plan before proposing
it; lack of a plan is not a reason to end the program.

**What the steward should ask next.** *Does the unchanged A8 recipe, rebuilt
independently from this family's sources, give fresh populations a worthwhile
advantage on its eight protected compositions?* A positive extends external
acquisition beyond the earlier output-addition families. A bounded small
effect or failure limits this recipe's portability. Either changes what we
can claim and which acquisition/representation question deserves investment.
Use the existing [independent-input plan](../../plans/independent-input-family-acquisition.md)
and question 40; this strategy is not the experiment registration.

The steward's **24 fresh builds**, rather than the pilot price scenario's
53–64 builds, are reasonable for the **1.5× usefulness decision**. Its estimated
interval half-width factor of 1.43 would put an effect near 2.2× above that
margin at the expected precision; this is a planning calculation, not a power
guarantee. There is no need to buy a 1.25 half-width merely to estimate the
large pilot ratio precisely. Preserve build uncertainty and shared-baseline
uncertainty; do not substitute pilot builds or tune against protected scores.

Keep solve fractions, cap sensitivity and acquisition cost alongside the
primary ratio. Three protected cells have a predicate pairing absent from
sources; report these separately from the other five without making a
three-cell subgroup the general conclusion. G4 is a fixed supplied prior,
not a demonstrated competitive baseline for every alphabet. Thus a success
is usefulness relative to G4 at this cap, not universal search superiority.
The proposed old-artifact arm O costs only about six additional queue minutes
at measured rates and is acceptable as descriptive context. Its token-id
reinterpretation prevents treating O/A8 as a clean family-specificity test.
Neither contrast isolates predicate placement, token supply, context,
fragments or inheritance. No control matrix is needed for this first answer.

Charge failures and all acquisition once per deployed build. Repayment must
use arithmetic acquisition-plus-search costs, not the geometric speed ratio;
wall-time claims require comparable measurements under load. Do not reuse
0145's defective two-replay calibration.

**Allocation and exit.** Raise only root 10's frontmatter
`budget.experiments` **31 → 32**, granting **one experiment through the next
strategy review**. Roots 01 and 23 are unchanged. Expected complete time is
**4.5–5 hours**, including preparation, review, approximately one hour of
measured-rate queue work, analysis and contingency; allow the proposed
**two hours summed queue timeouts**, preparation at most 120 minutes. Reprice
if the protected runner requires materially more work. About 42 hours should
remain afterward; the other **38 available experiment slots are unallocated**.

Exit to strategy after the protected comparison with its uncertainty,
per-cell reliability and acquisition economics, or earlier on a validity,
build or complete-cost obstacle. Useful transfer earns consideration of a
same-alphabet crossed-family test or PSB2, not automatic funding. A broad
interval needs a resolution price; a small or harmful effect needs an
evidence-based choice among acquisition and representation alternatives.
None automatically ends the run. Stop only if no complete candidate then
justifies its remaining cost within the deadline.

**Owner note disposition.** The sole
[owner-heritable-map.md](../../plans/owner-heritable-map.md) is unchanged since
[strategy 0311](../2026-10-10-0311/strategy.md): SHA-256
`439bf7393e478eecebe519357bbcb314b90720df3de73fd0f482a0e715e7bba8`.
There are no new or changed unanswered owner notes. Its directions remain:

| Direction | Disposition, reason, and reconsideration |
|---|---|
| Inherited op frequencies | **Pursued** at root 23's tested scope; further work **deferred** because frozen usefulness failed. Reconsider a changed rule with measured selectable signal, a bank where learned frequencies beat the hand scaffold, or a necessary frequency-only inheritance control. |
| Capture and synonyms | **Deferred**: the owner's useful-inheritance prerequisite remains unmet. Reconsider after that evidence and a concrete reassignment limitation; engine validation stays a separate stage. |
| Population-level maps | **Pursued** for outer-selected token maps; further contextual selection **deferred**. Reconsider a changed representation or ranking signal with a credible complete learning-and-transfer price. External A8 fitting does not answer this direction. |
| Free table mutation; ambiguous intermediates | **Declined for this block**. Reconsider only as a necessary contrast or to resolve a specific gap in a justified reassignment study, following the owner's order. |

**What to stop.** Stop automatic source-size sweeps, additional feedback rounds,
full-pipeline parity top-ups, unchanged pre-solve extraction, finer suffix or
random-recoding studies, and blind contextual optimizer retries. Do not raise
source attempts to hide this probe's sparse discovery. Leave S8′ scoring and
the PA deficit aside unless they change an acquisition decision; S8′ alone
would not isolate its cause. Keep helper and CA expansion parked. Defer PSB2
until this bounded transfer answer informs which recipe deserves the larger
benchmark/interface investment. Available time and the 40-experiment cap are
not reasons to fill a queue.
