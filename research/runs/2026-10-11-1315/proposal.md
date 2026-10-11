---
node: questions/10-compositional-map-transfer/54-rectified-sum-acquisition
title: Rectified-sum probe — verify the stage-0 obstruction and measure headroom for frozen R-all
bank: x4-rectified-sum-v1 (new; development roster only, protected roster frozen untouched)
kind: probe
---
**Question.** Per [strategy 1315](strategy.md) and the [plan](../../plans/rectified-sum-acquisition.md): can the
frozen uncapped semantic recipe (R-all, [53](../../questions/10-compositional-map-transfer/53-order-library-cap-release/question.md))
acquire rectifier helpers `pos/neg(a,b)` from sources `pos/neg(a,b)+Xc` and save search on `pos(a,b)+neg(c,d)`?

**Stage 0 already ran and changes the probe's job** (off-harness, ~9 min, research build of `60ab766`;
[notes and scripts](stage0/README.md)):
- Sources are easy: 96/96 solved on the first attempt, median 2.0 k evaluations, about 140 k per build.
- But evolution solves them **without the helper**. 84/96 solvers are IF_GT-rooted, 80/96 contain `a+b+c`
  (the `max(a+b+c, c)` route), and only 11/96 contain their own helper. R-all pooled **0 and 1** of 12 helpers.
- Destinations are hard for every arm (4 cells × 4 repeats): R-tree 4/16 solved (capped mean 419 k); supplied
  R-rect 11/16 (287 k); R-all 7/16 and 4/16; transported order R-all 0/16.
- Caveat: my first run used the main venv, whose VM returns zeros for `v2_x4`, so everything "failed", including
  the order control. Caught, but these are unreviewed numbers: 2 builds, 16 jobs per arm.

So the plan's exit ("return earlier on a semantic obstruction") very likely applies. Stage 0 points to two
obstructions: (a) **no acquisition opportunity**, because the sources admit a helper-free solution; and (b)
**little headroom**, because even supplied helpers leave destinations cap-bound. **Why not go straight to
strategy:** stopping ends root 10's fresh-family portability line. It should rest on reviewed, reproducible
numbers rather than an off-harness probe that already produced one artefact.

**Closest known technique.** Run Transferable Libraries ([Keijzer, Ryan & Cattolico 2004](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf)):
subtrees from earlier runs are frozen as a library for new runs. Semantic keying follows libraries indexed by
output vectors ([Pawlak, Wieloch & Krawiec 2015](https://gpbib.cs.ucl.ac.uk/gp-html/Pawlak_2014_ieeeEC.html)).
External fitting, no inheritance; both cited earlier in this tree, mechanism unchanged.
This is a **boundary test**: does recurrence-based acquisition fail when source solutions need not factor through
the reusable part?

**Bank.** Follow the plan: a manifest of 24 sources and 30 destinations; interpreter/Python/VM agreement checked
under the research build, with an import check that the VM is the worktree's; the ≤ 9-token alias screen; and the
80% old-bank exclusion. The development roster is the 4 seen stage-0 cells (2 overlapping, 2 disjoint) plus the 2
lowest-SHA-256 admitted overlapping cells. The rest are protected, frozen with the method and never searched. If
fewer than 8 protected cells survive, report that and stop.

**Arms** (unchanged engine, restarts ≤ 8 × 65,536, P 256, mix 0.5, half donors):
1. R-tree.
2. R-rect: the 12 helpers, uniform.
3. R-all: **8 new acquisitions**, each 24 sources × 2 R-tree jobs, failures charged, `order_library.build(cap=None)` unchanged.
4. R-order-all: the saved 1228 R-all libraries of builds 0–7, transported unchanged.

Unit: build × cell × repeat, 8 × 6 × 2 = 96 per arm. Seeds are shared across arms per unit, from a new audited
namespace. 384 scoring jobs.

**Reported** (descriptive): source cost; solver census (own helper, `a+b+c`, root op); helpers and ranks per
R-all build; needed-helper coverage per cell × build. Per arm: solves, first-attempt rate, capped arithmetic and
geometric means, worker seconds; ratios to R-tree with a build bootstrap.

**Recommendation rule (pre-stated).** Price a decision-sized protected confirmation only if **all** hold:
(1) a needed helper is in the R-all pool in ≥ 24/48 cell × build pairs; (2) R-rect solves ≥ 90% and R-rect/R-tree
≤ 0.5 (headroom); (3) R-all/R-tree ≤ 0.67. Otherwise return to strategy, recommend ending this candidate, and name
the failed condition: (a) acquisition, if (1) fails and the own-helper census is < 25%; (b) headroom, if (2) fails;
or both. If R-all/R-tree ≤ 0.67 *without* helpers, flag it as a lead for 53's mechanism, not a reason to continue.

**Feasibility.** Sources take seconds (0.07 worker-s per job). Destination jobs cost 22–38 worker-s;
all 384 at the cap is ≈ 14.6 k worker-s, about 22 min wall on 11 workers. Timeouts: prepare 15 min + score 40 min = **55 min** (≤ 60). R-tree first-attempt solves are about
2/16, far below question 50's 90% trigger.

**Full cost.** Researcher 1–1.5 h (adapt `order_cap_run.py`/`order_bank.py` to the new labels and add a
reporting-only rectifier census; extraction untouched). Review 0.5 h, queue ≤ 1 h, analysis and decision 1 h:
**about 3–4 h**, within the allocated 4–6 h. This uses root 10's slot 45 and the run's third probe (allowance four).

**Expectation.** The own-helper census is about 10%; R-all holds a needed helper in ≤ 10/48 pairs; R-all/R-tree is
0.8–1.1; R-rect solves 65–80% with R-rect/R-tree about 0.6–0.8; R-order-all is worse than R-tree. Outcome: both
obstructions. **Surprises:** helpers recurring regularly once there are 8 builds; R-rect near the floor (stage 0
would then be noise); or R-all clearly helping without helpers.

**Next.** Return to strategy whatever the outcome. No source redesign, cap or size increase, or new family
inside this allocation; those are strategy's call.
