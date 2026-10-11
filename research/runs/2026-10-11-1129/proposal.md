---
node: questions/10-compositional-map-transfer/52-order-helper-acquisition
title: Order-helper acquisition probe — literal versus behaviour-keyed extraction against a supplied order prior
bank: x4-order-v1 (new; development roster only, protected roster frozen untouched)
kind: probe
---
**Question.** Following [strategy 1129](strategy.md) and its [plan](../../plans/order-helper-acquisition.md): can the
unchanged subtree recipe ([45](../../questions/10-compositional-map-transfer/45-tree-subtree-library/question.md))
acquire order helpers `lo(a,b)`, `hi(a,b)` (6-node GT/IF_GT trees) from sources `lo/hi(a,b)+Xc`, and is there a
worthwhile learned-versus-prior question on destinations `lo(a,b)+hi(c,d)`?

**Stage 0 already ran** (read-only, off-harness, about 1 min at `e29219b`; [notes and scripts](stage0/README.md)):
- Sources are easy: 71/72 solved, about 3 k evaluations.
- R-tree 10/18 on 3 destinations at one 65,536 attempt (capped mean 34 k). R-order (12 helpers, half the
  donors) 18/18, mean **1.4 k**, near the three-generation floor.
- The unchanged extractor held a helper in 1/4 pilot builds (only on a roster hand-picked so helpers repeat);
  helper-free builds solved fewer destinations than R-tree (4–5/18).
- 41/71 source solvers contain a subtree computing their own helper on D625, but only 11/44 such subtrees are the
  6-node form; most are 10–22 nodes, beyond the 9-node ceiling and unpoolable by literal canonical keys.

Consequences: **"learned beats R-order" cannot be shown here**: R-order is at the floor and costs no
acquisition. The planned conditional comparison is therefore only about automatic acquisition of new content
(how much of the R-tree→R-order gap is recovered), never practical advantage. The likely limit is
**keying, not absence**: evolution builds the helper, in varied forms. So I add one arm the plan did not list: a
behaviour-keyed extractor on the *same* source solvers. It knows nothing about min/max (so it respects the plan's rule against recognising them). Without it the probe
would re-measure stage 0; with it, it separates
explanations (a) nothing to extract, (b) literal keying, (c) crowding by small sums under the 16-entry cap.

**Closest techniques.** Run-transferable libraries ([Keijzer, Ryan & Cattolico 2004](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf)):
external extraction across runs. Libraries of subprograms indexed by their semantics (output vectors) in
semantic-backpropagation operators ([Pawlak, Wieloch & Krawiec 2015](https://gpbib.cs.ucl.ac.uk/gp-html/Pawlak_2014_ieeeEC.html)),
within runs; here keying only pools recurrence across source runs, and the frozen library serves as plain
mutation donors (external fitting, no inheritance).

**Bank.** As in the plan: manifest, interpreter/Python/VM agreement (ties, negatives), the ≤ 9-token alias
screen, and the 80% agreement exclusion against saved independent-input banks. Development roster: the three
stage-0 destinations (seen) plus the three lowest-SHA-256 overlapping-pair cells. Protected: all remaining eligible
cells, frozen with rule and methods, never searched. If fewer than 8 protected cells (or fewer than 2 disjoint) survive, report and stop.

**Arms.** These are scored on the 6 development cells under the unchanged restart schedule (≤ 8 × 65,536, P 256, mix 0.5,
32-token cap, half donors):
1. R-tree.
2. R-sum: the 1019 constructor, rebuilt from the alphabet.
3. R-order: the 12 helpers, uniform, orientation as in stage 0.
4. R-L: the unchanged literal extractor.
5. R-S: same proper subtrees (containing an input), keyed by D625 output vector at any size; recurrence ≥ 2
   source cells; unchanged ranking and 16-entry cap; emits the smallest literal seen, dropped unless 3–9 nodes.

Acquisition: **8 builds**, each with all 24 source cells × 2 R-tree jobs (48 jobs; performance-blind, every
helper in 4 jobs), failures charged. R-L and R-S share each build's solvers. Scoring: R-tree/R-sum/R-order
6 cells × 16 seeds; R-L/R-S 8 builds × 6 cells × 2 seeds; seeds shared across arms; 480 jobs.

**Reported (descriptive, no outcome table).** Per build: helper entries (which, size) and ranks lost to the cap.
Helper census of all 384 source solvers. Per arm: capped mean and geometric mean, solves, first-attempt
rate, worker seconds, between-build SD of log cost. Gap recovered = log(R-tree/R-x) ÷ log(R-tree/R-order).

**Recommendation rule (pre-stated).** Price a protected comparison only if R-S or R-L holds a destination-needed helper in ≥ 6/8 builds
*and* recovers ≥ 50% of the log gap on the development cells. Its question would be acquisition of new content
(R-x versus R-tree, gap recovered), with R-order as ceiling. Otherwise stop this candidate and log the
located limit: (b) if R-S succeeds where R-L fails; (c) if helpers rank below the cap; (a) if the census is low.

**Feasibility and cost.** Stage 0 timing: ~0.5 worker-s per source job, 0–5 s per destination attempt. About 400 source
plus 480 scoring jobs ≈ 1–2 worker-hours, about 10 min on 10 workers. Queue timeouts: prepare 20 min + score 30 min
= **50 min** (≤ 60). Preparation ≤ 120 min (reused checks, runners, 1019 prior;
new: manifest, R-order list, ~40-line keyed extractor). Analysis ~1 h. **Total ~4–5 h**, within
the allocated 4–6 h. R-tree's first-attempt rate (~55%) is below question 50's 90% trigger.

**Expectations.** R-L holds helpers in ≤ 2/8 builds and is no better than R-tree. R-S recovers some helpers but
loses others to cap crowding, landing between R-tree and R-order. Surprises: R-L recovering helpers regularly;
R-S failing despite the census (→ c); R-order far from floor.

**Next.** Return to strategy with the located limit or a priced protected comparison; no variant sweeps.
