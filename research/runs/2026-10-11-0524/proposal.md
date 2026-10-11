---
node: questions/10-compositional-map-transfer/47-tree-donor-arrangement
title: Label-rearranged tree libraries versus intact libraries on gate-sum's unmatched splits
bank: x4-gate-sum-v1 (development bank since 0348; 0150 libraries unchanged)
---
**Question.** Per [strategy 0524](strategy.md) and its [plan](../../plans/tree-donor-arrangement.md):
on gate-sum splits B and C, which no learned predicate covers, the frozen 0150 libraries cut restarted tree GP
to about 0.35× of R-tree ([46](../../questions/10-compositional-map-transfer/46-tree-library-fresh-composition/question.md)).
Do donors that keep each library's shapes, sizes and size-conditioned primitive counts, but with permuted labels,
keep that gain? Competing explanations: [47](../../questions/10-compositional-map-transfer/47-tree-donor-arrangement/question.md).

**One fact changes the reading (read-only probe, [log](../../questions/10-compositional-map-transfer/47-tree-donor-arrangement/log.md)).**
Counting distinct-input pair sums by split, the intact libraries hold 48 for A, 1 for B and 6 for C. A
permutation of the kind the audit used gives about 17, 17 and 15. So intact B/C gains do not come from the
right predicate pairs, and the control *adds* them while removing the learned arrangement. On B/C, retention
means arrangement is unneeded; a resolved loss means intact libraries carry something beyond pair identity. Split A is the **positive control**: there, rearrangement removes known-useful information (the predicate
is kept in about 1/3 of permutations). If R-perm does not lose clearly on A, the control is too weak to read.

**Closest known technique.** The libraries are run-transferable libraries
([Keijzer, Ryan & Cattolico 2004](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/bibs/3103/31030531.htm)),
here externally fitted and frozen, with no inheritance. The control is related to
headless-chicken tests of whether subtree *content* matters
([Angeline 1997](https://gpbib.pmacs.upenn.edu/gp-html/angeline_1997_tcbbe.html)). Here shape and
primitive counts stay fixed. Retention would point toward a distribution-type target like
[PIPE](https://gpbib.pmacs.upenn.edu/gp-html/Salustowicz_97ecml.html), not implemented here. A **mechanism
test of a known method**.

**Arms (all 18 cells).** Search, verifier, cap, restarts and library-draw rule exactly as 0348 (`1f02bb7`).
- **R-tree:** ordinary restarted tree GP.
- **R-lib:** the 24 intact 0150 libraries.
- **R-perm:** each library rearranged by the plan's construction. Labels are permuted within (entry node count,
  compiled length, node arity, node width) pools. Duplicates, unchanged entries and accidental originals are kept.
  There are **3 realizations per build**, from a seed rule frozen before scoring, with no selection.

**Unit and size.** One job is (build, cell, repeat). There are **6 repeats**: realization = repeat mod 3. The
three arms share each job's eight new attempt seeds, which must be disjoint from history. Jobs: 24 × 18 × 6 =
2,592 per arm, 7,776 in total. Primary: 12 B/C cells, **1,728 jobs per arm**. Intervals are paired block
bootstraps over the 24 builds, with realizations nested.

**Feasibility.** Audit: 142–155 of 181 entries changed, invariants held. On 0348's B/C rows,
means were R-tree 68,647, R-lib 24,070 and R-size 57,282 evaluations; worker seconds per job were 6.41, 2.12 and
5.22. R-lib half-versus-half (576 jobs each): [0.83, 1.26]. At 1,728 jobs
the expected half-width is about ±12–15%, so the 1.25 margin can resolve. Worker time ≤ about 37,000 s
(R-perm priced as R-tree); at 0348's measured 10× parallelism, **about 1 h wall**.
- **Stage gate:** R-perm on the 4 development cells, inside prepare. If projected scoring exceeds 100 min, drop
  to 4 repeats (2 realizations × 2), as pre-stated.
- **Validation before scoring:** tree parse; compiler, interpreter and Rust agreement on every rearranged entry;
  exact count, skeleton and width invariants; a determinism replay of saved 0348 R-lib jobs.
- **Timeouts:** prepare 40 min + scoring 120 min (≤ 3 h).

**Full cost.** About 4.5 h: preparation ≤ 120 min, queue about 1 h, review/analysis/decision about 1.5 h.

**Primary comparison.** Mean capped evaluations, **R-perm ÷ R-lib on B/C** (12 cells, equal weight), with a 95%
interval. Margin 1.25: a 25% cost increase, about a fifth of the intact log-gain over R-tree.
- **Arrangement unnecessary at this resolution:** upper bound < 1.25, and R-perm ÷ R-tree upper < 0.80, and
  the solve-fraction difference (R-perm − R-lib) has lower bound > −0.03. A resolved R-perm < R-lib is
  reported as a gain from redistributed pairs.
- **Arrangement carries worthwhile information:** lower bound > 1.10 and point estimate ≥ 1.25.
- **Otherwise unresolved:** report the precision price; this is not evidence of retention.
- **Validity guards:** R-lib ÷ R-tree on B/C must have upper < 0.60 (replication). The positive control on A is
  reported as R-perm ÷ R-lib. If A's lower bound is ≤ 1.5, retention is read as "control too weak", not as a
  mechanism.

Descriptive: per split; the 4 B/C cells whose then-branch pair is a learned pair versus the other 8;
per-realization cost against target pairs supplied; insertions and rejections; worker seconds;
acquisition-plus-search curves (0150 acquisition charged to both library arms).

**Expectation.** About 65%: retention on B/C, with R-perm ÷ R-lib between 0.8 and 1.1, and A losing
2–5×. **Surprises:** a resolved B/C loss despite better pair supply; or no loss on A.

**Next action.** Retention: return to strategy to price a simpler statistical acquisition (shape plus
size-conditioned label counts). Intact advantage: return to strategy with joint expressions as the target for
a different-source or unfamiliar-content test. Unresolved or failed A control: report the price, return to
strategy. No follow-up is funded automatically.
