---
decision: continue
node: questions/01-map-bias/08-evolve-bias
next: runs/2026-10-05-1700/proposal.md
---
# Decision — 2026-10-05-1558

**Continue [08](../../questions/01-map-bias/08-evolve-bias/question.md).** The sampling test
returned the pre-registered verdict **A** in both families. A fitted `op_weights` vector raised
held-out P(exact) 4.9× (sum>2) and 8.9× (max>2) over uniform, and 4.8× and 6.7× over the other
family's fit. All adjusted lower bounds were above 3. Mismatched fits gave the holdouts nothing
(1.0×, 1.3×), so C is out for these holdouts. D is out at this fit strength.

The meaning is narrower than "family structure". The reviewer's post-hoc product of four op
folds (INPUT, GT, aggregator, threshold constant) reproduces all 30 rates within 1.5×. The
aggregator-swap pools swap the family. The fits also suppressed the unseen constant (CONST_2
0.37×), which cost about 2.7× of holdout gain. So the transferable content is one op's weight.
The M side rests on one fit trajectory. There was one seed and one holdout per family.

**Why continue rather than park.** The plan pre-registered A → test evolution on the holdouts.
That separates A from B (supply vs success), the question's main open contrast. Item 12
predicts B, so the outcome is genuinely uncertain. 08 has 2 experiments left and the root has 3.
The fitted vectors already exist (`result.json`, key `vectors`), and `evolve.py` already applies
`op_probs` to initial genomes and to mutation. The test is cheap.

**Why the hand-set arm.** Given the product-model reading, a win for the fitted vector would
not by itself show that fitting found anything beyond "raise the family's aggregator". A
hand-set vector (INPUT, GT and the aggregator at the fit's folds, everything else uniform)
separates the two and turns the post-hoc model into a pre-registered prediction (sampling
≈ 13× and 25× on the holdouts).

**Not chosen.** A second M fit trajectory or a harder fit (does CONST_2 suppression reach D?)
would refine the sampling result but change no decision. `next: strategy` is premature while 08
has a pre-registered next step.

**Parked questions.** None reopens. [02](../../questions/01-map-bias/02-fixed-target-sampling/question.md)
still needs the owner's wish (the coming evolution-vs-sampling comparison bears on its theme,
but does not meet its condition). [07](../../questions/01-map-bias/07-shared-arrival/question.md)
has no B-helper copy or replay. [04](../../questions/01-map-bias/04-random-start-discovery/question.md)
depends on 07.

**Tree changes.** 08 log entry and summary updated. C and D are marked out for these holdouts,
and A' (one-op transfer) is added as a narrowing of A. The stop rule now covers the evolution
outcome, and a reopen condition is in place for when 08 is parked. Root 01 summary updated.
The digest gains one bullet on fitted-bias transfer and an updated 08 entry.
