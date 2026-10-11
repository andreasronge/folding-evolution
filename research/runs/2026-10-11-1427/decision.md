---
next: strategy
---
# Decision — 2026-10-11-1427 inherited library-choice probe

**Park [55](../../questions/55-inherited-library-choice/question.md); no proposal; return to strategy.**
Root 55's one-probe budget is spent. Strategy 1427 asked for a review after this probe, and the
proposal said so too. Every other open question also has no budget left (`research.py status`: roots 10
and 55 at 0 left, 01 spent, 23 parked).

**What the probe showed (observations; six order development cells, 24 saved R-all libraries, protected
cells unsearched; commit `f8f4246`).**
- A recipient-inherited bit that switches mutation donors to R-all (f₀ = 0.25, no bit mutation) fixed in
  **46/96** linked runs. The controls fixed in 27/96 (shuffled), 29/96 (size-matched random donors) and
  16/48 (neutral). L − S **0.20 [0.04, 0.35]**, L − Z **0.18 [0.05, 0.30]**, library bootstrap. The
  controls are all compatible with the neutral 0.25.
- The cause is a small per-generation advantage among selected parents (+0.016 [0.009, 0.023], about 4%
  relative). It appears only in L and only before the first solve. The revert/clone confound was present
  and matched across L, S and Z.
- Drift decided everything. Every run ended fixed or lost, 328/336 within the first episode, with a median
  of 12–18 generations. 11 of the 12 planned episodes measured nothing about the bit.
- Usefulness is unresolved. The frozen mean law against the starting mixture was **0.91 [0.71, 1.20]**,
  against fixed R-all 1.21 [0.98, 1.46]. The dose curve is convex: 74 k evaluations at probability 0,
  45 k at 0.125, 32 k at 0.5. So even universal fixation would only reach about 0.73× of the starting
  mixture.
- Steward checks on the saved rows (descriptive): in the episode where selection acted, linked and
  shuffled populations solved equally often (55/96 each). One population's own law is 0 or 0.5. At L's
  fixation rate that lottery would cost about 1.2× the starting mixture on the pooled dose curve.

**Why park, not continue or close.** The probe answered the cheap part: carriers of a useful law can be
favoured by program selection alone, but too weakly against drift to yield a resolved fresh-search
gain. A confirmation of the plan's design would mostly re-measure allele movement, which strategy 1427
ruled insufficient. Its usefulness readout is capped near 0.73× and is already beaten by simply fixing
R-all. A usefulness test needs a new instrument, and the strategy said that is not funded automatically.
It would need either polymorphism kept by bit mutation or weaker drift, or a starting point where the
dose curve has headroom. Not closed, because nothing here shows inherited choice cannot be useful. One
population size, one crossover rate, one library law and no bit mutation were tested. The reopen
condition in 55 names the redesign and the cheap confirmation that a later inheritance study could reuse.

**For the strategist.** This adds to root 23's result. Under program selection in these populations
(P 256, lexicase, crossover 0.5), an inherited variation modifier is decided within about 15 generations.
That happens even when the modifier is a known useful law and carriers gain a resolved advantage. Any
future heritable-map work (the owner's note) must first beat that time scale. My recommendation:
- Do not continue 55 in this design.
- Of the candidates strategy 1427 deferred, protected scoring of R-all on `x4-order-v1` (4–5 h) is the
  one I would fund next. The 0.40× order saving is the program's clearest development-scope acquisition
  success, and it has never been tested on unsearched cells.
- If that does not justify its cost against the remaining ~22 h, write `next: stop`.

**Housekeeping.** Critique digest-check notes 5–6 are fixed. The 54 and root-10 summaries now say "no
resolved saving (a saving above about 4% excluded)". A correction entry in 54's log narrows the
"could not change the decision" wording; the 1315 entry stays as written. Digest: header updated, and a
root-55 stub added with no beliefs, because probe results stay in the log. No parked question's reopen
condition is met: 23 needs a changed frequency-learning procedure, and strategy 1427 states that a binary
selector does not establish learned frequencies. 50 and 54 are unaffected.
