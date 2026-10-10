---
next: proposal
---

Continue with **a same-alphabet test of useful family preference**, under root 10.
The next question is whether independently acquired biases favour their own
family's excluded compositions over the other family's, or whether one acquired
bias helps both equally well. This now matters more than improving the cheap
recipe's speed on another closely related target.

This review covers the [core question](../../../README.md#core-question),
[digest](../../digest.md), question tree and reopening conditions, plans, owner
note, and recent decisions and briefs through [1536](../2026-10-10-1536/decision.md).
`uv run python scripts/research.py status` reports run **2026-10-10-1419**, **2/40
experiments used**, ending **2026-10-12T14:19:15 Europe/Stockholm**, with about
**45 hours left** at handoff. There is time for a complete, consequential comparison.

**What the program has learned.**

- **Program supply does not fully predict evolutionary discovery or persistence.**
  Root 01 separated easy-task sampling bias from hard-task search, and cheap joins
  from a special modularity advantage. Lineage mixing blocks establishment of rare
  shared forms; self-mating removes that barrier. Natural arrival and single-copy
  establishment remain unresolved. These are useful distinctions, but further
  refinements would not change today's acquisition choice
  ([root 01](../../questions/01-map-bias/question.md)).
- **Learned bias can remain useful after its source programs are discarded.**
  Outer-selected token weights transferred roughly 2×. The tested contextual
  selection procedures added no resolved benefit. External solver fitting did:
  context beat the restricted token fit **2.12× [1.86, 2.41]** on then-addition
  when fresh. Pooled and positional frequency replacements did not reproduce it;
  random recoding to match mutation width hurt. Conditional content and structured
  variation remain unseparated ([digest](../../digest.md)).
- **Literal fragments and cheap feedback are useful acquisition components.**
  Fragments added **1.47×** over fitted context on then-addition, without establishing
  semantic modules. A8—four source attempts per cell, fit context and fragments,
  four adaptive attempts, refit—retained useful performance on fresh two-sum-v1 at
  about a tenth of full acquisition cost. Rebuilding from a complementary roster
  gave **2.50× [2.17, 2.85]** over G4. These are external fits, not inherited maps
  ([37](../2026-10-09-2303/decision.md), [38](../2026-10-10-0145/decision.md)).
- **The recipe now works within a substantially different family.** On the
  independent-input double-predicate bank, 24 fresh builds solved **317/384**
  protected searches versus G4's **63/384**. The capped-cost advantage was
  **10.1× [7.6, 13.1]**, falling to **6.4× [5.0, 8.0]** at the one-cap failure
  charge. This confirms usefulness relative to a weak supplied prior on eight
  cells, including three with a predicate pairing absent from sources. It is
  within-bank confirmation, not fresh-bank generality or uncapped solve-time
  acceleration. The old-family control reinterpreted token meanings, so its
  inferiority cannot establish family specificity
  ([1536 analysis](../2026-10-10-1536/analysis.md)).
- **Useful inherited acquisition is still unshown.** Root 23's one rule produced
  worse frozen search than uniform on sum; on max, a gain above 1.06× was excluded.
  Persistent ancestry helped against shuffled ancestry on max without making the
  result useful. That bounds this procedure, not self-adaptation
  ([root 23](../../questions/23-heritable-variation-bias/question.md)).

The practical answer is therefore stronger than the evolutionary answer: search
can teach a reusable external decoder/library, but neither useful per-individual
inheritance nor a reliable preference for the training family has been established.
Older folding and CA results do not close either gap.

**Which roots matter now.** Root **10** is first: distinguish family-dependent
acquisition from a broadly useful correction to a poor prior. Earlier specificity
tests were unresolved near 1.0–1.1× between closely related output families; the
new setting offers a larger structural contrast without another alphabet change.
Root **23** is the larger long-term mechanistic gap, but no new evidence meets its
reopening conditions. Root **01** stays unfunded: its parked helper, shortcut and
fixed-target questions do not decide which transferable bias to acquire. No new
root is needed; both new-root allowances remain available.

**Current line against different mechanisms.** I searched the literature for this
review. [Salustowicz and Schmidhuber, *Probabilistic incremental program evolution*
(1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/) updates a program-generating
distribution using successful search. A8 belongs to that external-learning
tradition, with different fitting, fragment and frozen-reuse rules. Its next test
is a boundary/mechanism comparison, not a claim to invent distribution learning.

The owner's mechanistically different candidate is **self-adaptation through
descendants**. [Stephens et al., *Self-adaptation in evolving systems*
(1998)](https://pubmed.ncbi.nlm.nih.gov/9847423/) studies encoded mutation and
crossover probabilities receiving indirect selection in model landscapes. A
concrete changed-rule candidate would preserve linked program/modifier lineages
across goal changes, instead of resetting programs between episodes. My inference
is that this could change the credit available to modifiers; the paper does not
show transferable token bias here. Its greater conceptual payoff is outweighed
today by the negative frozen-usefulness result and lack of a measured signal for
the revised rule. The old [equal-exposure plan](../../plans/heritable-bias-equal-exposure.md)
priced a first cycle at 5–7 hours; revised acquisition plus informative frozen
evaluation and transfer would need repricing, provisionally at least a comparable
first cycle plus a further evaluation cycle. Do not buy another unchanged run.

**Parameterized callable abstractions** are another distinct candidate.
[Ellis et al., *DreamCoder* (PLDI 2021)](https://people.csail.mit.edu/asolar/papers/EllisWNSMHCST21.pdf)
learns abstractions and a search policy. Argument binding could reuse computations
where literal windows fail; that is a hypothesis for this repository. It requires
new extraction/call semantics and validation, whereas the latest literal procedure
has no demonstrated binding failure. Defer that build until a concrete such limit
or a cheaper complete comparison makes it preferable.

Among nearer alternatives, component attribution using saved A8 builds is cheaper
but would mainly choose which pieces to carry. A stronger uninformed baseline
would improve the practical speed claim but would not answer family dependence.
Another fresh-bank success would extend coverage without resolving that ambiguity.
The crossed comparison directly pits two acquired biases against each other, so
its main conclusion need not rest on G4's weakness. It still cannot establish
superiority to a competitive general-purpose synthesis baseline.

**What the steward should ask next.** *Does unchanged cheap acquisition learn a
useful preference for double-sum predicates versus two-sum outputs, when both
families use the same executor, inputs and primitive inventory?* A positive would
justify keeping family-specific acquisitions. Tight small contrasts, with useful
search in both families, would favour a shared bias as the next acquisition
target. One bias winning everywhere would favour that bias; harming the other
family alone would show specialization without useful improvement in both.

I wrote [the same-alphabet plan](../../plans/same-alphabet-family-preference.md).
Use `(A+B)>(C+D) ? E:F` versus `A>B ? C+D:E+F` over X0–X3. Both canonicals have
six readout occurrences, two additions, one comparison and one conditional. This
improves on the suggested one-addition output contrast by matching gross operation
counts. The output family's semantic eligibility and search rates are **unmeasured**.
Matching canonical counts does not match evolved token supply or isolate assembly
order: output ranges and other task properties still differ.

Reuse all 24 frozen double-predicate acquisitions if provenance and unchanged
method checks pass; acquire the output family's biases with the same recipe.
Prefer the eight still-unscored double-predicate cells plus a performance-blind
output split. The plan assigns bounded validation and development calibration
before any evaluation of those targets. The steward should open the next numbered
child of root 10 (currently **41**); it supplies the proposal and decision rule,
not a reopening of the already answered question 40.

**Allocation and exit.** Raise only root 10's `budget.experiments` **32 → 33**:
**one substantive experiment through the next strategy review**. Expected complete
time is **6–9 hours**, including bank/build work, calibration, roughly 2–3 hours
of acquisition/scoring, reviews, analysis and contingency. Preparation remains
at most 120 minutes; allow at most **4 hours summed queue timeouts**. These are
provisional prices, anchored by 1536's measured 31.7-minute preparation/acquisition
and 31.5-minute scoring entries, not measured output-family rates. Reprice the
complete comparison before admission. The other **37 available run slots remain
unallocated**; roots 01 and 23 are unchanged.

The run has used **one probe and one full experiment**. Its standalone probe
allowance is exhausted (`research.py probe_allowed`: one plus one per four full
experiments). Therefore do not propose the steward's separate bank probe or
relabel a feasibility-only study as full. Propose the substantive crossed question
with bounded prerequisite checks and a stop on failed admission. A short semantic
check during proposal preparation can expose an obstruction before execution.
Do not run filler experiments to unlock another probe.

Exit to strategy after the crossed result, with directional uncertainty, absolute
usefulness and acquisition economics, or earlier on a semantic, validity, build
or full-cost obstruction. A broad interval earns a resolution price, not an
automatic top-up. If the candidate fails, compare the saved-artifact component
question and revised inheritance/representation candidates at their complete
prices. Stop only if none justifies its cost within the remaining deadline.

**Owner note disposition.** The sole [owner-heritable-map.md](../../plans/owner-heritable-map.md)
is unchanged since [strategy 1536](../2026-10-10-1536/strategy.md): SHA-256
`439bf7393e478eecebe519357bbcb314b90720df3de73fd0f482a0e715e7bba8`.
There are **no new or changed unanswered owner notes**. Its dispositions remain:

| Direction | Disposition, reason, and when to reconsider |
|---|---|
| Inherited op frequencies | **Pursued** at root 23's tested scope; continuation **deferred** because frozen usefulness failed. Reconsider a changed rule with measured selectable signal, a bank where learned frequencies beat the hand scaffold, or a necessary frequency-only inheritance control. |
| Capture and synonyms | **Deferred**: useful inherited learning, the owner's prerequisite, is still missing. Reconsider after it and a concrete reassignment limitation; validate engine changes separately. |
| Population-level maps | **Pursued** for outer-selected token maps; further contextual selection **deferred**. Reconsider a changed representation or ranking signal with an informative complete learning/transfer price. A8's external fitting does not satisfy this direction. |
| Free table mutation; ambiguous intermediates | **Declined for this block**. Reconsider only as a necessary contrast or specific gap in a justified reassignment study, following the owner's ordering. |

**What to stop.** Stop precision top-ups of A8 versus full F, source-size and
extra-feedback sweeps, more G4-only confirmations of the same family, unchanged
pre-solve fragment extraction, finer suffix/recoding studies, and blind contextual
optimizer retries. Leave the unscored S8′ arm and PA deficit alone unless they
change an acquisition decision. Keep helper and CA expansion parked. Defer PSB2
until this comparison tells us whether the benchmark should receive a shared
acquisition or task-family acquisitions. A positive here earns that planning
decision, not an automatic benchmark queue.
