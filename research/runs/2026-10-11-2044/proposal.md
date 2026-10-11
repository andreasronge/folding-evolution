---
node: questions/10-compositional-map-transfer/59-signed-chain-depth
title: Signed-chain depth probe — saved 1938 R-all libraries vs R-tree and R-gate on three linked conditionals
bank: x4-signed-chain-v1 (new; development roster only, protected roster frozen untouched)
kind: probe
---
**Question** ([strategy 2044](strategy.md), [plan](../../plans/signed-gate-composition-depth.md), new
sub-question [59](../../questions/10-compositional-map-transfer/59-signed-chain-depth/question.md)). Do the 24
frozen 1938 signed-gate libraries lower search cost where assembly is hard, and does the supplied helper
repertoire show headroom they miss? Destinations `p(a,b)+n(b,c)+p(c,d)`, all 24 index permutations, `v2_x4`,
D625. Follows the strategy as written; this probe only prices a confirmation.

**Stage 0 already ran** (off-harness, ~1 min, 1938 export of `3a18ef5`;
[notes and scripts](stage0/README.md)). The shape is hard but not capped:
- 4 cells × 3 repeats: R-tree 12/12 solved, **6/12 on the first attempt**, up to 7 of 8 attempts, mean **138 k**
  evaluations (1938: 7.8 k, 97.7% first attempt). R-gate 31 k. Two stage-0 R-all builds 100 k, 101 k.
- Saved 1938 libraries hold all three needed helpers in **3.3%** of build × cell, none in 25%: R-all supplies
  helpers partially, R-gate fully.
- Worker-s per job: mean 8.3 (R-tree), ~6 (R-all), 2.1 (R-gate); max 22. ~7.6 effective workers.
- These 4 cells (the 4 lowest label SHA-256s in the audit) are seen and join the development roster.

**Closest known technique.** Run Transferable Libraries
([Keijzer, Ryan & Cattolico 2004](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf)):
bias acquired by external fitting in earlier runs, carried frozen into new ones; no inheritance. Known in this
tree; this is a **boundary test**: does that bias still pay when the target needs three linked pieces and
restarts are common? No new learner, source or extractor.

**Bank and freeze** (as the plan): label/interpreter/VM checks incl. zero conditions; ≤ 9-token alias screen;
≥ 80% old-bank and pairwise exclusions, recorded without replacement. Development roster = the 4 seen cells
plus the lowest-hash survivors to six; all other survivors protected and frozen with the method before any
search; stop if fewer than 8 protected. Fresh seed namespace excluding 1938's and stage 0's
(20440000–20443027). Protected cells unused for smoke tests or timing.

**Arms** (unchanged engine at `9da9c2c`: ≤ 8 × 65,536, P 256, mix 0.5, half library donors):
R-tree; R-all = the 24 saved 1938 `semantic` libraries, hash-checked; R-gate = 24 helpers uniform.
Unit: build × development cell × repeat, seeds shared across arms; 24 × 6 × 2 = 288 units per arm, 864 jobs.

**Descriptive outputs** (no outcome table): solves, capped jobs, first-attempt rate, attempts distribution,
mean/median/p95 evaluations and worker-s per arm, cell and build; R-all/R-tree and R-gate/R-tree with two-way
bootstrap intervals (description only); needed-helper coverage (0–3) per build × cell and R-all cost by
coverage stratum (confounded; never used to select builds or cells); cost `A + N·S` using 1938's ~216 k
acquisition (stage 0 suggests repayment within ~10 searches, against 66 in 1938).

**Pricing the confirmation** (the probe's purpose). From probe variance components, simulate the 95% interval
of R-all/R-tree on the protected roster for 18 cells × 24 builds × r ∈ {1, 2, 4} repeats, and its queue time at
measured throughput plus a 2× tail scenario. Stage-0 scenario: r = 2 is 2,592 jobs ≈ 14 k worker-s ≈ 31 min.
Recommend a confirmation to strategy only if all hold:
1. **Hard**: R-tree first-attempt rate ≤ 85% on development cells.
2. **Not ceilinged**: R-gate solves ≥ 95% and R-tree capped jobs ≤ 25%.
3. **Decisive and affordable**: some r gives an expected interval with upper/lower ≤ 1.6 (1938: 1.53) within
   4 h summed timeouts.

No gate on the R-all point estimate: a protected result that R-all does not help where R-gate does limits
deeper reuse and is as decision-relevant as a saving. The confirmation's primary would be pre-registered then
(pooled capped mean evaluations R-all/R-tree; upper < 0.80 saving, lower ≥ 0.80 excluded).

**Feasibility and cost.** Probe jobs ≈ 864 × 5.5 worker-s ≈ 4.8 k worker-s ≈ 11 min wall; a fully capped job
≈ 30 worker-s, so even 10% capping adds < 2 min. Queue timeouts: prepare/verify 15 min + probe 40 min =
**55 min** (≤ 60). Agent time: critique 0.5 h, preparation ≤ 2 h (adapter from `signed_gate_bank.py`, runner
from the 1938 scorer; extractor untouched), code review 0.5 h, analysis and decision 1 h. **Total ≈ 3.5–4 h**,
inside the 3–4 h expected / 5 h ceiling; the 5–7 h confirmation still fits the ~17 h left.

**Expectation.** R-tree first attempt 40–70%, mean 100–200 k; R-gate 0.15–0.35× of R-tree; R-all 0.6–0.9×,
interval wide. All three criteria met.

**Surprises.** R-all ≥ 1 (partial acquired content does not help linked assembly); R-all close to R-gate
despite 3% full coverage; R-tree mostly first-attempt on the other two cells (stage 0 unrepresentative);
R-gate capping often (linking, not supply, limits search).

**Next.** Return to strategy with the price and recommendation; no confirmation, second shape or extractor
change is automatic.
