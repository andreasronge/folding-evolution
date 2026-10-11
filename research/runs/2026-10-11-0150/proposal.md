---
node: questions/10-compositional-map-transfer/45-tree-subtree-library
title: Frozen source-subtree library as mutation donors in restarted tree GP (DG)
bank: x4-double-gate-v1 (8 spare cells; 4 source cells for new tree-source searches), development data
---
**Question.** Following [strategy 0150](strategy.md): can a small library of subtrees, learned from new
tree-GP solutions on the 4 DG source cells, make fresh restarted tree GP (R-tree, the
[0024](../2026-10-11-0024/analysis.md) comparator: 90,392 mean evaluations, 765/768 exact) cheaper on the 8 DG
target cells, beyond valid random donors of the same size? Competing explanations (content / donor size /
nothing) in [45](../../questions/10-compositional-map-transfer/45-tree-subtree-library/question.md).

**Closest known technique.** Transfer of subtrees between GP runs: SubTree/FullTree transfer
([Dinh, Chu & Nguyen 2015](https://gpbib.cs.ucl.ac.uk/gp-html/Dinh_2015_CEC.html)), source chromosomes reused
as mutation subtrees ([Thuong et al. 2023](https://gpbib.cs.ucl.ac.uk/gp-html/thuong_2023_ICTA.html)), common
subtrees across related problems ([O'Neill et al. 2017](https://gpbib.cs.ucl.ac.uk/gp-html/oneill_2017_CEC.html)),
run-transferable libraries ([Keijzer, Ryan & Cattolico 2004](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf)).
External fitting, frozen; no inheritance. This is a **replication/boundary test of a known method**: what it adds
is a restarted, already-strong baseline, a valid size-matched donor control, exact (D625) program synthesis,
and acquisition charged in the same units.

**Acquisition (learning unit = one library, 24 independent).** Per library: 8 R-tree jobs on each of the 4
DG source cells (unchanged 0024 search and restart policy, ≤ 8 × 65,536), new seeds. From every exact solver
tree take proper subtrees (root excluded) with 3–9 nodes containing an input; count recurrence by source cell
(once per solver; ADD children sorted only for counting); keep those in ≥ 2 cells; rank by cells, solvers,
size, prefix; cap 16; insert the most common literal form. Failures and empty libraries stay in the cohort.
Source trees are discarded after extraction; no target tree or 0024 solver is used.

**Arms (scoring).** 24 libraries × 8 target cells × 8 repeats = **1,536 jobs per arm**, all arms sharing
attempt seeds, same initializer, mix 0.5, selection, 32-token cap, restart policy.
- **R-tree**: unchanged.
- **R-lib**: each mutation donor comes, with probability 0.5, uniformly from the library (else the ordinary
  depth-3 random donor; empty library → always ordinary). Inserted fully expanded; oversize reverts as now.
  About 25% of children get a library donor.
- **R-size**: same, with a frozen random library per acquisition: each entry rejection-sampled from the
  ordinary donor generator to the learned entry's node count and compiled length.

**Feasibility (measured).** Probe on the 2254 calibration source solvers (feasibility only;
[log](../../questions/10-compositional-map-transfer/45-tree-subtree-library/log.md)): 4 solvers per cell give
3–10 entries (median ≈ 6), mostly pair sums `ADD(Xi,Xj)` plus 1–3 `GT(ADD,ADD)` predicates in 91% of draws;
8 per cell should be richer. 0024 R-tree: per-job CV 1.15, 8.9 worker-s per job, 98 µs per evaluation, seed
pairing correlation 0.05. At 1,536 jobs per arm the ratio's 95% half-width is about ±9–10% (more if libraries
are heterogeneous).

**Cost.** Queue: sources 768 jobs ≈ 6.8k worker-s; scoring 4,608 jobs ≈ 41k worker-s; ≈ 80 min at 10
workers. Timeouts: prepare + acquire 45 min, scoring 150 min with a stage-0 timing gate (3.25 h ≤ 4 h).
Preparation ≤ 120 min: a donor hook in `tree_gp_search.search` whose off-path replays 8 saved 0024 R-tree jobs
bit-identically; interpreter/VM agreement on all library entries; seed audit against all earlier runs. Agent
time ≈ 4–5 h; total ≈ 6–8 h.

**Primary comparison.** Mean evaluations (cells equal weight, failures at 524,288) R-lib ÷ R-tree, 95% block
bootstrap over the 24 acquisitions. Decision rule, with solve-fraction difference R-lib − R-tree lower bound
> −0.03 required for a gain:
- **Useful**: upper < 0.90 and R-lib ÷ R-size upper < 1 → return to strategy recommending the fresh-bank stage.
- **Size, not content**: R-lib ÷ R-tree upper < 0.90, R-lib ÷ R-size unresolved → no fresh-bank stage for
  this extractor.
- **End**: lower > 0.85 (a saving above 15% excluded) → end this extractor's expansion.
- Otherwise unresolved → report the resolution price.

Also reported: worker seconds; acquisition-plus-search curves in both units (acquisition ≈ 32 × 90k ≈ 2.9M
evaluations and ≈ 285 worker-s per library); per-cell ratios, split into the 5 targets whose pair split
occurs in source predicates and the 3 that do not (`X1+X3 / X0+X2`); insertion, oversize-rejection and
fallback counts; training-perfect-not-exact share (0024: 9.6%).

**Expectation.** A modest gain, R-lib ÷ R-tree ≈ 0.8–0.95, concentrated in the 5 covered cells, with R-size
near R-tree, because ordinary depth-3 donors already make `ADD(Xi,Xj)` often but rarely make the whole
predicate. Surprising: a gain above 1.3×, which would mean ordinary tree search misses composable blocks;
R-size as good as R-lib; or a gain on the 3 uncovered cells.

**Next action.** Researcher implements in a worktree on `research/main` (from `1773d11`); DG only, no TS.
Return to strategy after the result.
