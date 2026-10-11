---
next: strategy
---
# Decision: close 46, return to strategy

**Close [46](../../questions/10-compositional-map-transfer/46-tree-library-fresh-composition/question.md).** The run
was complete and valid ([analysis](analysis.md), code review pass, commit `1f02bb7`). All 5,184 scoring rows are
present, the three arms share each job's eight attempt seeds, and the seeds are disjoint from history. The 24
libraries and size controls were re-derived from 0150's saved source rows and are hash-equal to the originals.
The bank and split were frozen before any protected search, and the reviewer re-verified all 5,175 solvers as
exact on D625. The result lands on the plan's **transfers** branch by a wide margin:

- mean evaluations R-lib ÷ R-tree **0.250 [0.217, 0.289]** (69,442 → 17,346; about 4× cheaper);
- reliability guard passes: solve difference +0.0012 [0.000, +0.0029] (1,728/1,728 vs 1,726/1,728);
- R-lib ÷ size-matched random donors **0.291 [0.231, 0.372]**; R-size ÷ R-tree 0.860 [0.716, 1.011], unresolved;
- worker seconds 0.234 [0.201, 0.273]; with the 0150 acquisition charged, a library repays after about
  **55 [49, 62]** gate-sum searches.

R-lib was cheaper in 18/18 cells and 24/24 builds.

**The important qualification: most of the pooled gain is predicate-matched.** On the split whose predicate the
libraries learned on DG, the ratio is **0.055 [0.042, 0.071]** (≈ 18×). On that split about half the solvers
contain the library predicate verbatim. On the two splits no learned predicate covers, the ratios are **0.363
[0.299, 0.434]** and **0.338 [0.287, 0.400]** (≈ 3×), and large entries almost never survive verbatim there. Both
of the plan's readings therefore apply: the parts transfer across composition in every split, and the large
number comes mostly from reusing one familiar predicate.

**How sure I am.** I am confident of the direction and rough size on this bank, and the gain is resolved in
every split. Three limits remain:
1. **The shape was assembled from the libraries' own parts.** Three pair sums plus one of the three possible
   predicates. Two development cells were probed before the freeze. This shows reuse across composition, not
   transfer to unfamiliar content.
2. **The carrier of the ≈ 3× floor is unknown.** Pair sums, the small entries, or an input/`ADD` frequency shift
   that the size control does not match could each produce it. The size control's own small effect (0.86) is
   unresolved.
3. **Repayment is bank-relative.** The 55 searches follow from R-tree costing 69k per job here.

The gate-sum protected cells are now spent, so this is a development bank from here on.

**Why `next: strategy` and no proposal.** Strategy 0348 funded exactly this experiment and required a return to
review after its result. It also said a useful transfer "earns a new choice among mechanism, acquisition on
different sources and broader tasks", and that choice is the strategist's. Root 10 is at 38/38. I re-checked the
reopen conditions for root 23 and the parked root-01 questions (02, 04, 07, 08, 09). None is met: this result
comes from external extraction plus frozen insertion. It is not a heritable or frequency bias, and it is not a
threshold-family result.

**For the strategist.** I would rank the candidates this way:
- **Ingredient test on the unlearned splits first (about 2–3 h; no new source searches).** Use `x4-gate-sum-v1`'s
  B/C splits, which are now development data, and/or DG. Arms against R-tree: {pair sums only}; {predicate only};
  and random donors matched to the libraries' input/`ADD` token frequency as well as size. The ≈ 3× floor is the
  part of the gain that does not rely on matching a learned predicate. Knowing whether it is content or token
  supply decides what a cheaper acquisition, or a learned donor distribution (PIPE-like), would need to carry.
  This is a mechanism test of a known method (Keijzer et al. 2004; O'Neill et al. 2017).
- **Boundary shape with unfamiliar content (about 5–8 h).** A fresh bank whose solution needs subtrees the DG
  libraries lack, for example a different operator inside the predicate, with the method frozen. This finds the
  limit of transfer. A failure there would be informative, not a setback.
- **Not worth buying now:** precision on gate-sum, insertion-rate or cap tuning, another familiar-parts shape,
  more DG acquisitions.

Root 23's inheritance question is untouched by this result. A successful *external* library is not evidence
that inherited acquisition has a selectable signal.

**Digest check (critique 0348, notes 6–8) applied.**
- Note 6: the digest now reads "no matched-family advantage resolved on the tested withheld cells".
- Note 7: the marginal-block heading now reads "showed no resolved gain on training cells". The text adds "gains
  above about 4% excluded there; B untested on the transfer shape".
- Note 8: 45's summary now says few final solvers contain larger entries verbatim under the literal matcher, and
  that transformed reuse and causal pathways are unmeasured. A correction note is appended to 45's log.
