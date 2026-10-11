---
node: questions/10-compositional-map-transfer/56-order-library-protected-cells
title: Frozen R-all order libraries on the 24 protected order cells
bank: x4-order-v1 (protected roster, first search; saved 1228 R-all libraries unchanged)
---
**Question and mechanism.** This follows [strategy 1530](strategy.md) and the
[plan](../../plans/order-library-protected-reuse.md). On the six development cells, R-all cost **0.40
[0.32, 0.50]** of R-tree ([1228](../2026-10-11-1228/analysis.md)). That method was revised after this bank
had been seen. Does the frozen saving hold on the 24 never-searched `split.protected` cells (`lo(a,b)+hi(c,d)`;
4 disjoint-pair, 20 overlapping-pair)? I reuse all 24 saved 1228 libraries, rebuilt from their own corpora and
checked against the recorded contents. Nothing is collected, refitted or ranked again. The bank is reloaded and
checked against hash `2fc0d88c…d74a`, with no re-screen.

**Closest known technique.** Run Transferable Libraries ([Keijzer, Ryan & Cattolico 2004](https://pure.ul.ie/en/publications/run-transferable-libraries-learning-functional-bias-in-problem-do/))
carry acquired functions into later GP runs. The follow-up [Undirected Training of RTLs (EuroGP 2005)](https://gpbib.cs.ucl.ac.uk/gp-html/eurogp_KeijzerRMC05.html)
trains libraries without the target problem. Here the map adapts by **external fitting**: recurrent semantic
classes from source solvers become frozen, fully expanded mutation donors. There are no callable abstractions and
no inheritance. **A boundary/replication test of a known technique.** It adds whether a saving chosen with six
cells in view holds on the excluded combinations. It is not a fresh-bank test: the same twelve helpers serve both
rosters.

**Arms, unit, seeds.** Three arms: R-tree, R-all and R-order (the supplied 12-helper prior). The tree engine,
D625 verification, initializer, half-library donor mix and 8 × 65,536 restart attempts stay as at `60ab766`.
Design: 24 builds × 24 protected cells × 2 repeats gives **1,152 seed-paired units and 3,456 jobs**. Every unit
draws its own R-tree run; no baseline is shared across builds. Scoring seeds come from a namespace disjoint from
1129, 1228 and 1427. The method, roster and seeds are frozen in `method_freeze.json` before any protected job
runs. Smoke and timing runs use development cells only. Jobs run repeat-major, so repeat 0 completes for every
build × cell first. The new wrapper keeps `order_cap_run.py`/`order_run.py` replayable.

**Feasibility (measured at 1228).** Mean worker seconds per job were R-tree 5.31 (p99 31), R-all 2.14, R-order
0.27, so about 7.7 per unit. 1228 ran 8.1 k worker-s in 836 s, about 9.7 effective workers. Expected load is
≈ 8.9 k worker-s, about **15 min**, and about 45 min if protected cells cost 3× development. Timeouts: prepare
25 min (rebuild, verify, freeze, development smoke) and score 90 min, **115 min total**. If the score step times
out, the pre-stated fallback analyses only the completed repeat 0. Precision was priced from the 1228 rows
(bootstrap over builds). Intervals were ×/÷1.48 for 6 cells × 1 repeat, 1.29 for × 2 and 1.27 for × 4: build
variance dominates. With 48 pairs per build I expect about **×/÷1.25 or better** for the primary, and about ×/÷1.4–1.5
for the 4-cell disjoint stratum (descriptive only).

**Full cost.** Researcher ≤ 2 h, code review 0.5 h, queue 0.3–1 h, analysis and decision 1.5 h: about **4.5–5 h**,
within the 6 h ceiling and well before the 2026-10-12 14:19 deadline.

**Primary comparison and decision rule.** The primary measure is the ratio **R-all / R-tree** of pooled capped
arithmetic mean evaluations over all 24 cells (equal units per cell; failures charged 524,288). The 95% interval
is a bootstrap over the 24 builds with seed pairs kept. Cells are fixed because they are the whole protected roster.
A worthwhile saving is **0.67×**, as in 1228.
- **Useful on held-out cells:** upper < 0.80, *and* R-all has at most 12 (1%) more unsolved units than R-tree.
  R-all is then kept as a scoped reference on this family; return to strategy.
- **End expansion on this family:** lower > 0.67. That excludes a worthwhile saving (or shows harm).
- **Otherwise unresolved:** price the resolution and return to strategy. This is not equality and not an automatic
  top-up.

Reported outside the rule:
- Per-cell and per-stratum ratios (disjoint versus overlapping), and solves by arm.
- Geometric ratios and worker-second ratios.
- R-all / R-order, and the share of the R-tree → R-order log gap that R-all recovers.
- Break-even searches against R-tree, in evaluations and in worker seconds. Each build is charged its historical
  acquisition, failures included: **214 k evaluations and 13.1 worker-s per build** (1228 `acquisition.jsonl`).
- Needed-helper coverage of each protected cell × build pair, computed from the libraries before scoring. It is
  descriptive and never used to select libraries.

If R-order remains cheaper, no repayment against it is claimed.

**Expectation.** The sources cover all twelve helpers symmetrically, and the six development cells sat at
0.35–0.47. I expect R-all/R-tree of about **0.40–0.55** (useful branch), with R-order still 5–8× cheaper.
Development disjoint cells were easiest for R-tree (~51 k versus 74–103 k evaluations). Surprises: an upper bound
≥ 0.80, meaning the development roster was favourable, or any stratum where R-all costs more than R-tree.

**Next action.** The researcher builds the wrapper and the prepare/score entries. Then return to strategy, whatever
the outcome. A positive result funds nothing further automatically.
