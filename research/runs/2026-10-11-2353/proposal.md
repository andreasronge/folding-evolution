---
node: questions/10-compositional-map-transfer/61-input-rebound-library-reuse
title: Consistent input rebinding of the saved signed-gate libraries on the signed-chain cells
bank: x4-signed-chain-v1 (all 24 cells, now development; saved 1938 R-all libraries unchanged, plus their rebound copies)
---
**Question.** The saved signed-gate libraries cut signed-chain cost to 0.778× [0.696, 0.870] of R-tree. The
supplied repertoire is 3× cheaper still. The saving tracks how many needed helpers a library holds *with the right
inputs* (0.98 → 0.42 for 0–3). Is literal binding the limit? **R-bind** replaces every entry with its 24
consistent X0–X3 permutations, without deduplication. A draw is the original entry draw followed by a uniform
permutation. The symmetry is supplied, not learned ([strategy](strategy.md), [plan](../../plans/input-rebound-library-reuse.md)).

**Why it is clean.** The 24 cells `p(a,b)+n(b,c)+p(c,d)` are exactly the 24 permutations of (a,b,c,d). Library
σ(L) on cell c behaves like L on σ⁻¹(c). Pooled over the roster, R-all therefore already averages each library
over all bindings, and R-bind puts that mixture into every search. Content and roster-averaged helper mass stay
fixed. The test asks whether spreading mass across bindings (reach) beats concentrating it on the bindings the
sources built (dose).

**Closest known technique.** Run-transferable libraries
([Keijzer, Ryan & Cattolico 2004](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf)).
[Murphy, Ryan & Howard 2007](https://gpbib.cs.ucl.ac.uk/gp-html/Murphy_2007_FBIT.html) expanded templates into
function families that differ in argument count and order, then pruned the redundancy. Parameterised ADFs:
[Koza 1993](https://doi.org/10.1016/B978-0-08-094832-4.50024-6). Here the map adapts by external fitting, frozen
before use. This test adds expanded donors that keep their learned weights, and prices them against the literal
library and a supplied prior on a hard tier. It is a mechanism test, not transfer.

**Arms.** The frozen `83c7c5b` engine, with [2150](../2026-10-11-2150/proposal.md)'s settings: P 256, mix 0.5,
half-library donors, 8 × 65,536 cap, exact D625 check.
- R-all and R-bind: 24 builds × 24 cells × **r = 6**, sharing seed tuples.
- R-tree and R-gate do not depend on the build: r = 1, paired with repeat 1, as references.
- Seeds are fresh from 20480000 and audited. Smoke rows are timing-only and excluded.

**Feasibility (measured).**
- 2150 worker-seconds per job: R-tree 11.56, R-all 8.80, R-gate 3.18, on 7.98 workers.
- 8,064 jobs take about **144 min** at R-all's speed, or 164 min at R-tree's. Summed timeouts are ≤ 230 min.
- If R-bind's smoke cost exceeds 1.3× R-all's, use r = 5.
- Precision: a pseudo-contrast from 2150's R-all rows (builds shifted, so build effects are independent) gave a log
  half-width of 0.112 at 18 cells and r = 4. Seed noise dominates (repeat-splitting gave the same at r = 2), so I
  expect about **0.08–0.09** here.

**Full cost.**
- Preparation ≤ 2 h: constructor, provenance, renaming ≡ column-permutation check through the production VM,
  identity replay, smoke.
- Queue about 2.5 h; analysis about 1.5 h.
- **5.5–6.5 h** in all, inside the 8 h ceiling and before 14:19.

**Primary (fixed before scoring).** R-bind/R-all, as the ratio of pooled capped mean evaluations over 24 cells.
The 95% interval comes from a two-way build × cell bootstrap, with repeats averaged within units and arms paired.
- **Material gain:** upper bound < 0.90.
- **Small, none or harm:** lower bound > 0.85, which ends uniform rebinding. It is labelled harm if the lower
  bound is > 1.00.
- **Unresolved** otherwise, which is not evidence of equality.

Forecast at half-width 0.09: a true ratio of 0.75 resolves material with probability about 0.97, and 0.80 about
0.7. A true 0.90 is unresolved about 75% of the time. A true 1.00 ends the line with probability about 0.93.

**Secondaries (labels).**
- R-bind/R-tree and R-gate/R-bind.
- Worker seconds, solves, caps and tails.
- Donor insertions and rejections.
- Needed-helper draw probability per arm.
- R-bind/R-all by R-all's needed-helper stratum (descriptive).
- `A + N·S` at N = 10 and 100, with A = 216 k evaluations per build for both library arms.

**Validity (reported first).**
- R-tree first-attempt rate ≤ 85% and capped share ≤ 25%.
- R-gate solves ≥ 95%.
- R-all/R-tree within [0.6, 1.0]; otherwise flag R-all as atypical.

**Expectations.** There are about 13,800 donors per job, 23% of them helpers. That still leaves about 100 draws per
needed binding, so I expect reach to beat dose:
- R-bind/R-all of **0.70–0.90**;
- the gain concentrated where R-all held no needed helper, with a small loss possible where it held two or three;
- R-gate still ≥ 1.5× cheaper, because only 8.6 helper types exist on average and build 5 has no negative gates.

**Surprises.**
- R-bind reaching R-gate.
- Resolved harm, meaning dose matters.
- A stratum-0 loss, meaning rebinding the non-helper entries hurts.

**Next.** Return to strategy. A material gain points to a fresh-bank test or an argument representation. Small or
none points to acquiring the never-built helper types. This opens sub-question 61, using strategy 2353's one slot.
