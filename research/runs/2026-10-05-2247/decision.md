---
next: strategy
---
# Decision: run 2026-10-05-2247 (11-composition-bank)

**Close 11; open 12; no proposal — return to strategy.**

The run is complete and clean (commit `0995d33`, 2 400 searches, 2·10⁸ samples per arm, no
failures) and fired the pre-stated **row 2**: at 524 288 evaluations no transversal is
eligible, because SM-SEL is an exact alias and Sm-SEL is solved in only 27/50 uniform runs
(95% 39–68%). The structural headroom table, required whichever row fired, shows that **row 3
would fire too**: all four structurally possible splits lack headroom, every time because the
hand-set grammar G solves two holdouts in under 4 096 evaluations. Since each split holds out
one ADD and one DADD cell, and G's medians there are 768–2 304, no split of this bank can have
headroom against G at any cap. So the bank's binding problem is not tractability (a larger cap
might fix Sm-SEL) but that a generic previous-token grammar already spells out the syntax of
every cell.

Why close 11 rather than continue or park: the question "is there a tractable bank with room
for a learned decoder?" is answered for this bank — no — and the answer does not hinge on a
borderline count. Re-running with a larger cap would answer only the tractability half and
leave the headroom block in place. Its slot is spent.

Why not propose the next experiment myself: both firing rows prescribe a return to strategy,
and the root-10 plan says the same for a failed bank. The next design depends on a
program-level choice the steward should not make alone: what root 10's "simple fixed
task-agnostic assembly bias" control is. G was written knowing this bank and matches its
syntax; a learned previous-token decoder could at best learn similar rows. The options
(recorded in [12](../../questions/10-compositional-map-transfer/12-generic-grammar-headroom/question.md)):
1. **Deeper tier, same G**: three-reducer or nested cells, longer programs; also repair the
   SEL column. Risk: G still covers the syntax and wins only by length.
2. **Bank-blind control**: fix a weaker grammar (e.g. type-valid continuations) before
   choosing tasks; 11's stage A and U/F data are reusable. Risk: an easy control to beat.
3. **Different family structure**: families whose canonical programs need different bigrams,
   so a family-specific decoder has something a generic one cannot.
4. **Park root 10**: if no bank on this alphabet escapes a generic previous-token grammar,
   learned transfer on this decoder form has little room, which is itself worth stating.

Root 10 has 3 of 4 slots left; 12 holds 1.

Beliefs changed (digest, new section "Composition bank"): this bank has no usable split;
G leaves no headroom; G beats its own marginals 2.6–19.5× in median search speed (paired
intervals all above 1, supply and variation not separated); F gives 1.9–3.5×; search gains
are roughly a tenth of supply gains or less. Scope: one bank, one harness, 50–150 paired seeds
per cell × arm.

Parked questions re-checked: 09's reopen (a) needs a speed-up with no or negative sampling
lift; every biased arm here raised supply 11–1 650×, so not met. 08's decoder-rule condition is
root 10 itself, already running. 02, 04, 07 are untouched by this result. None reopens.

Digest check (critique.md notes 5–6): no problems listed; nothing to fix.
