---
next: strategy
---
# Decision — run 2026-10-09-1743 (question 35, four-attempt sources for the complete C+F pipeline)

**Close [35](../../questions/10-compositional-map-transfer/35-small-source-acquisition/question.md);
no proposal; return to strategy.**

**Why.** The run is complete and valid (8 192 searches, all gates, 34 historical and 128 smoke
replays bit-exact; review pass; commit `652fde5`). Pre-set rule 2 fired: retention
ρ = cost(full F)/cost(C4+F4) 0.679× [0.614, 0.752], upper bound below the 0.833 tolerance under
1 × cap, both-solved (0.832, just), BE, PA and in each of the four source blocks. The question asked
whether four attempts per cell can teach the whole C+F procedure to that target; at this source
size, bank and procedure the answer is no. Strategy 1743 routed every outcome back to strategy,
and root 10's 27 slots are used. Another four-attempt experiment would not change a decision.

**What the result leaves for the strategist** (inputs, not proposals):

1. **The acquisition choice is now a horizon question, not a retention question.** Arithmetic
   acquisition-plus-search in evaluations: C4+F4 is cheaper than full F up to about 1 530
   [1 247, 2 016] fresh searches and costlier beyond; both repay against G4 within about 31. A
   deployment that will run fewer than about a thousand searches of this kind would prefer the
   cheap sources; the program's own banks are reused well past that.
2. **An intermediate source rule is the obvious next candidate, but only post hoc motivated.**
   Across the 64 individual acquisitions, retention was worse with empty source cells (mean 0.52
   vs 0.735; Spearman −0.35) and small libraries (0.36); full 32-fragment libraries still averaged
   0.77. A "collect until k solvers per cell" rule, or 8–16 attempts, would need its own complete
   price (sources plus ~2 h scoring) and a reason the break-even matters. Q35's reopen condition
   covers this.
3. **Decoder versus library loss is not separated.** C4+F4 is not resolved from full C alone
   (cost ratio 0.996 [0.919, 1.080]); C4+W4 is slower than full C (0.890 [0.837, 0.947]) but W4
   carries F4's length law. A bare-C4 arm would separate them; it changes no acquisition decision
   by itself.
4. **F4 still adds over its own chain blocks** (1.12× [1.03, 1.22], unresolved against 1.10), in
   every block; the library's increment did not collapse with the decoder.

**Parked and closed questions re-checked.** None reopens. Q32's reopen clause "F built from fewer
or cheaper source tapes" is the experiment Q35 ran as its own sub-question; 32 stays closed. Q33's
`gt`-join condition is not met: `gt` fragment count correlated with per-acquisition retention
(Spearman 0.25, steward recomputation from `per_acquisition.json`) less than library size did and
is confounded with it. Root 23's changed-rule/measured-signal condition and root 01's helper and
fixed-target conditions are untouched by this run.

**Digest check (critique notes 7–9) fixed.** Digest bullet on W/R now says the 0.7% bound is the
pooled primary's and the 1.10× gain is excluded under each sensitivity and family split; question 34
now says dropping the repair is supported under the tested full-C setup only, and that block-edit
ripple is local despite re-decoding, with ordinary point-mutation ripple unmeasured. Corrections
logged in 34's and root 10's logs.

**Changed beliefs (digest).** New bullet under root 10: four-attempt rebuild (C4+F4)/F 0.679×
[0.614, 0.752] in speed; not resolved from C alone; F4/W4 1.12× [1.03, 1.22]; cheaper only up to
about 1 500 searches. Scope: one source size, reused development sources (1246) and development
bank then-addition-v1, external fitting, average over four replicate builds per corpus (single
builds 0.21–1.34). Root 10's Overall and "not shown" updated accordingly.

**Expectation miss.** I expected ρ ≈ 0.95 [0.85, 1.06]; the result is in the named surprise
direction. My 64-search unpaired probe on block 0 (C4+F4 42k vs F 46k geometric) was misleading;
paired, C4+F4 67.5k vs F 45.9k. Lesson: an unpaired 64-search probe against historical arm
summaries cannot predict a paired ratio to ±20%.

Budget: root 10 27/27 used; autonomous run 14/40 experiments used (this one counted); deadline
2026-10-10T08:12.
