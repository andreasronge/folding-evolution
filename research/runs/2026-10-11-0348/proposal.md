---
node: questions/10-compositional-map-transfer/46-tree-library-fresh-composition
title: Frozen DG subtree libraries in restarted tree GP on a fresh gate-sum bank
bank: x4-gate-sum-v1 (new; built performance-blind, frozen with the method before protected search)
---
**Question.** Following [strategy 0348](strategy.md) and its [plan](../../plans/tree-library-fresh-composition.md):
do the 24 unchanged 0150 libraries (DG-acquired pair sums plus, in 20/24, one `GT(ADD,ADD)` predicate) make
restarted tree GP cheaper on a fresh shape, `(Xa+Xb)>(Xc+Xd) ? Xe+Xf : Xg`, after charging acquisition?
Competing explanations (reusable parts / DG-specific composition / donor size) in
[46](../../questions/10-compositional-map-transfer/46-tree-library-fresh-composition/question.md).

**Closest known technique.** Run-transferable libraries ([Keijzer, Ryan & Cattolico 2004](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf));
subtree transfer between GP problems ([Dinh, Chu & Nguyen 2015](https://gpbib.cs.ucl.ac.uk/gp-html/Dinh_2015_CEC.html);
[O'Neill et al. 2017](https://gpbib.cs.ucl.ac.uk/gp-html/oneill_2017_CEC.html)). External fitting, frozen; no
inheritance. A **transfer/boundary test of a known method**; it adds a protected fresh bank, a restarted strong
baseline, a size-matched donor control and acquisition charged in the same units. Mechanism already in the tree,
so no new literature search.

**Bank (frozen before protected search).** `v2_x4`, D625, 32-token cap. Candidates: the
[planning audit](semantic-planning-audit.json)'s 144 (A<B, C<D, pairs partition X0–X3, E<F, any G; exact DG/TS
aliases removed; pairwise agreement < 80%), in ascending label-hash order. Admission: no program of ≤ 9 tokens
computes the label on D625 (existing screen), canonical verified in interpreter, Python and Rust. Split rule,
performance-blind: **development** = the first four survivors (includes both probed cells; covers all three pair
splits); **protected** = the first six remaining survivors of each pair split, **18 cells**. Fewer than six
survivors in a split → return the obstruction to strategy. Record roster and exclusion reasons.

**Arms** (0150 code, unchanged search, initializer, mix 0.5, lexicase, donor rule, 8 × 65,536 restarts):
**R-tree**; **R-lib** (half of mutation donors uniformly from a library); **R-size** (0150's size- and
compiled-length-matched random donors, rebuilt from recorded seeds). Libraries reconstructed from 0150's
`acquisition.jsonl` under the original rule and hash-checked against `libraries.json`; all 24 used. Unit: one
acquisition (24 blocks); 24 × 18 cells × 4 repeats = **1,728 jobs per arm**, attempt seeds shared across arms,
audited against all historical and probe seeds (log).

**Feasibility (measured, [probe](probe/)).** On the two development cells, single attempts: R-tree solves 30/48
within 65,536 evaluations (DG: 0.47 per attempt), R-lib 46/48; 72–87 µs per evaluation; library donors entered
9–15% of children. Expected restarted cost ≈ 54k (R-tree) and ≈ 9k (R-lib) evaluations per job. 0150's 24-block
interval at 1,536 jobs was about ±17% in log ratio.

**Cost.** Scoring ≈ 1,728 × (4.4 + 4.4 + 0.8) s ≈ 17k worker-s ≈ 30 min at 10 workers. Queue timeouts: prepare
40 min (screen ≈ 2 min, verification, library reconstruction, seed audit, off-path replay of 8 saved 0150 jobs,
stage 0 = 24 builds × 4 development cells × 3 arms, gate: projected scoring ≤ 90 min) + scoring 90 min = **2.2 h**
(≤ 4 h). Implementation ≤ 2 h (bank module generalised from `branch_sum_bank.py`; target list and split from the
bank, no change to `tree_gp_search`). Agents ≈ 3 h. Total ≈ 5–6 h, inside the strategist's 5–8 h.

**Primary comparison.** Mean evaluations, cells equal weight, failures charged 524,288: R-lib ÷ R-tree, 95%
paired block bootstrap over the 24 acquisitions; guard: solve-fraction difference lower bound > −0.03.
- **Transfers**: upper < 0.90 with guard → this frozen, externally acquired bias helps on a new composition;
  return to strategy.
- **Small or none**: lower > 0.85 (a saving above 15% excluded), or harm (lower > 1) → end this route's expansion.
- Otherwise unresolved → report the resolution price.

Secondary, stated now: R-lib ÷ R-size (content beyond size if upper < 1); worker-second ratio; break-even
searches = 2.88 M acquisition evaluations ÷ (R-tree − R-lib mean), with interval, also in worker seconds; per cell
and per pair split ({X0+X1 | X2+X3}, the learned predicate's split, vs the other two); attempt-of-solve
distribution; insertion and oversize counts; shortcut share. DG's 0.39 is a different bank: comparisons with it are
descriptive.

**Disclosure.** The probe looked at R-lib vs R-tree on two cells before freezing. The method is 0150's, untuned
here; those cells are development-only; protected cells stay untouched by every arm until scoring.

**Expectation.** R-lib ÷ R-tree ≈ 0.15–0.35, every split gaining, because the target contains three pair sums
and the libraries are mostly pair sums; R-size ≈ R-tree as on DG. Surprising: ratio above 0.6, no gain on the two
splits without a learned predicate, or R-size close to R-lib (which would point to token supply over content).
Even the expected outcome is narrow: a shape assembled from the libraries' own parts, so it shows reuse across
composition, not unfamiliar content or modularity.

**Next action.** Researcher implements on `research/main` (from `d7ec100`) in a worktree; one queue (prepare,
score). Return to strategy after the result.
