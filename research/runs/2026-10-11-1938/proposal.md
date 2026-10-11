---
node: questions/10-compositional-map-transfer/58-signed-gate-acquisition
title: Signed-gate acquisition — frozen R-all on a fresh conditional-value bank, against R-tree, transported order libraries and a supplied gate prior
bank: x4-signed-gate-v1 (new; development roster plus 18 protected cells frozen with the method before any protected search)
---
**Question** ([strategy 1938](strategy.md), [plan](../../plans/signed-gate-content-acquisition.md)). Can the unchanged
uncapped semantic recipe (R-all, [53](../../questions/10-compositional-map-transfer/53-order-library-cap-release/question.md))
acquire useful bias from sources `p/n(a,b)+(Xc+Xc)` and cut search cost on never-searched destinations
`p(a,b)+n(c,d)`? Here `p(a,b) = Xa>0 ? Xb : 0` and `n` is its complement. Does new acquisition add anything beyond
the order libraries we already own?

**Stage 0 already ran** (off-harness, ~3 min compute, research build of `3a18ef5`; [notes and scripts](stage0/README.md)).
The rectifier probe died at the source; this family does not.
- The helper trees match across interpreter, VM and labels.
- Sources: 192/192 solved on the first attempt, ~200 k evaluations per 96-job build.
- Solvers often build their own helper: **37%** do, **23%** at an emittable 3–9 nodes (rectifier: 8.9%, 2.3%).
  Two R-all builds kept **11/24 and 6/24** helpers.
- Four destinations × 3 repeats, mean evaluations: R-tree 5.2 k (12/12 first attempt), R-gate 1.5 k,
  new R-all 2.8 k / 2.7 k, transported 1228 R-all 3.3 k / 4.6 k.
- These four cells are now seen and join the development roster.

**Question 50's condition is met** (R-tree first-attempt solving ~100%). No library raised cost on the probed cells.
I add no gate; the primary rule detects harm. Because destinations solve in about 20 generations, the result covers
easy compositions only.

**Closest known technique.** Run Transferable Libraries ([Keijzer, Ryan & Cattolico 2004](https://pure.ul.ie/en/publications/run-transferable-libraries-learning-functional-bias-in-problem-do/)):
bias learned in earlier runs is carried into new ones, by external fitting with no inheritance. The mechanism is
already in this tree. This is a **replication/boundary test**: does the frozen extractor carry over to a second
content family, with bank and split frozen together with the method?

**Bank and freeze**, as the plan specifies:
- Interpreter/VM agreement checks, including zero/negative conditions and IF_GT operand order.
- The ≤ 9-token alias screen and ≥ 80% old-bank exclusion; all surviving sources are used.
- Development roster: the 4 seen cells plus the 2 survivors with the lowest SHA-256 of their labels. The rest are
  protected, frozen before any protected search (smoke runs included).
- If fewer than 8 protected cells survive, stop and return to strategy.
- Seeds come from a fresh namespace that excludes stage 0's.

**Arms.** All use the unchanged engine: ≤ 8 × 65,536 restarts, P 256, mix 0.5, half library donors.
1. **R-tree**: no library.
2. **R-all**: 24 new builds, each from every source × 2 R-tree jobs, through `order_library.build(cap=None)`.
   Failures and empty libraries are charged.
3. **R-order**: the 24 saved 1228 R-all libraries (`semantic_all`), unchanged.
4. **R-gate**: the 24 helpers, drawn uniformly.

Unit: build × cell × repeat, with seeds shared across arms; R-order build *b* uses 1228 library *b*.
- Protected roster: 24 × 18 × 4 = 1,728 units per arm, 6,912 jobs.
- Development roster: 24 × 6 × 2 units per arm, 1,152 jobs. Descriptive only; it selects nothing.

**Primary comparison.** R-all / R-tree, pooled capped arithmetic mean evaluations on the protected cells. The 95%
interval comes from a two-way bootstrap over builds and cells. Material saving means **at least a fifth** fewer
evaluations.
- **Upper bound < 0.80**: the recipe extends to this second content family.
- **Lower bound ≥ 0.80**: a saving that large is excluded, which limits the recipe on this pair; a lower bound > 1
  means harm.
- **Otherwise**: unresolved.

**Secondary results** (reported, no rule):
- R-all / R-order: below 1 means acquisition adds beyond owned content; about 1 means the saving is generic.
- R-all / R-gate.
- Solves and worker seconds.
- Per-build helper census and needed-helper coverage.
- Cost `A + N·S`, with R-order shown both as owned and as newly acquired. Stage 0 gives A ≈ 200 k against a saving
  of ~2.5 k per search, so repayment takes about 80 searches.

**Feasibility and cost.**
- Job times: source jobs ~0.05 worker-s, destination jobs 0.1–0.3 worker-s.
- Wall time: 2,304 acquisition jobs plus 8,064 scoring jobs take ~10 min on 11 workers. If 10% of jobs capped,
  that would add ~35 min.
- Queue timeouts: 30 + 20 + 60 = **110 min**.
- Agent time: critique 0.5 h, preparation ≤ 2 h (bank module from `rectified_bank.py`, runner from
  `order_cap_run.py`/`order_protected_run.py`, extraction untouched), review 0.5 h, analysis and decision 1 h.
- **Total about 5–6 h**, inside the 8–11 h envelope and the 18 h left.

**Expectation.**
- R-all / R-tree 0.5–0.65.
- R-gate ~0.3.
- R-order 0.65–0.9, so R-all / R-order ~0.75–0.9, possibly unresolved.

**Surprises:**
- R-all ≥ 0.8, meaning the probe cells were unrepresentative.
- R-order matching R-all, meaning the saving is generic.
- Any library harm.

**Next.** Return to strategy whatever the outcome. There is no automatic extra bank, helper ablation, harder tier
or extractor change.
