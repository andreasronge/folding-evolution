---
next: strategy
---
# Decision: run 2026-10-09-0125

**Close [29](../../questions/10-compositional-map-transfer/29-frequency-matched-transfer/question.md),
answered at its scope. Write no proposal: [strategy 0125](strategy.md) allocated this one
comparison and asked to return to strategy afterwards with the fragment plan's price. Root 10 has
now used all 20 slots, so any further root-10 experiment needs an allocation anyway.**

Why:
- The run was complete and clean. There were 2 048/2 048 K searches in 42 min (projection 72 min).
  All 48 table hashes and the bank SHA passed, the 32 C/T replays were bit-exact on the current
  build, and the 16 timing rows replayed identically. Pairing with C and T was exact in all 2 048
  triples.
- The pre-stated rule applied cleanly. **C/K 2.48× [2.17, 2.83]**, and the lower bound is far above
  1.20. The verdict is "this G4-based pooled-frequency replacement is insufficient within 20% on these
  cells". It is robust to 1 × cap (2.25×) and to both-solved pairs (1.92×), and holds in every
  corpus and every cell.
- K is even slower than the token-only fit to the same tapes: K/T 0.86× [0.77, 0.96]. This
  replicates question 20 (0.83×) on a second bank. C's pooled marginals are a worse target than
  the ML token fit, so C's frequency shift looks like a by-product of its context rows rather than
  useful in itself. That reading is an interpretation and was not tested.
- Nothing in the result calls for a top-up or replication. Whether C − K comes from context
  dependencies or from positional frequency is a different question and needs a different control.

**Belief changes** (digest updated): the fresh-bank bullet no longer says "K unscored". A new bullet
gives C/K 2.48× [2.17, 2.83] and K/T 0.86× [0.77, 0.96]. Its scope: G4's context kept, pooled (not
positional) marginals matched, and then-addition now counts as a development bank. The root-10
"Overall" now says that pooled frequency on G4 does not carry the advantage on either bank. It
still leaves context versus position unseparated.

**Critic digest-check notes 5–8 fixed.** Root 10's question.md and 28's question.md were reworded:
- "added nothing" became "no improvement resolved; gains above about 10% excluded".
- "all of it on BE" and "PA null" became "gain resolved on BE; PA unresolved".
- The yield claim now says the collection diagnostics are descriptive.
- "A tenth of the gap" is now marked as point-estimate arithmetic, with F/R unresolved.

Both logs are append-only, so they got correction entries rather than edits. The digest
already used qualified wording; I narrowed its "nothing measurable" to "no resolved gain".

**Parked questions re-checked.** These are 01/02, 04, 07, 08, 09 and root 23. None of their
reopen conditions is met. The result bears on root 23 only indirectly: it does not supply the
changed rule or the selectable signal that root 23 requires.

**For the strategist.** Here are the options as I see them; the strategist decides.
1. **Position-matched K** (cheap, about 4 h, same frozen corpora and 1548 row F seeds). This would
   be G4 × a 32 × 24 position-by-token multiplier table matched to C's per-position marginals. It
   separates "context" from "where tokens sit". The answer changes the target for any inherited or
   selected learner. A non-contextual positional map is a much simpler thing to evolve than
   previous-token rows, and it is the natural next step after the owner's inherited-frequency idea.
   I would rank it first. It is the cheapest test that could redirect root 23 or the owner's
   heritable-map note. Its closest precedent is position-specific EDA / PBIL-style
   probability vectors, which makes it a boundary test, not a new technique.
2. **[Learned executable fragments](../../plans/learned-executable-fragments.md)** (11–16 h,
   unallocated). C/K does not show that fragments would help. It only sets a target of about
   2.5× over a frequency map on these cells.
3. **Stop root 10's external-fitting line.** The program's open gap is how evolution acquires the
   contextual target. Neither option above answers that directly. If the strategist judges that
   no acquisition design is ready, `next: stop` is defensible: 7 of 40 experiments are used and the
   deadline is 2026-10-10 08:12.
