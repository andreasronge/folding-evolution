---
node: questions/23-heritable-variation-bias
title: Recover 0918 — complete the one cut acquisition, then frozen scoring (inherited vs uniform/broken/scaffold)
bank: tag-threshold-v1   # sum/max > 1, 5 on length-4 lists over 0..9; threshold 2 untouched (development bank)
---
**What this is.** I am following [strategy 1046](strategy.md). This run completes the approved
[0918 comparison](../2026-10-08-0918/proposal.md) ([plan](../2026-10-08-0918/plan.md)). That run
stopped because one of 80 acquisitions, max/inherited/14, hit a hidden 1 200 s per-job deadline
([decision 0918](../2026-10-08-0918/decision.md)). Design and decision rule are
unchanged. This finishes one comparison, not a replication, and uses root 23's last slot.

**Closest technique.** Per-individual self-adaptation: strategy parameters travel with their
carriers and are selected only through them
([Stephens et al. 1998](https://pubmed.ncbi.nlm.nih.gov/9847423/)). New here: a frozen fresh-start
test of an inherited token distribution. The mechanism is already in this tree; no new search.

**Recovery changes (operational only).**
1. Remove the per-job defaults in `acquire()` (1 200 s) and `score()` (600 s), or set them to the
   stage timeout. Pin `RAYON_NUM_THREADS=1`. List every time limit in plan.md.
2. Add a selective acquisition path:
   - Rerun max/inherited/14 from its original seed.
   - As a determinism check, replay two complete runs fixed in advance: sum/inherited/0 and
     max/broken/0.
   - Write a new acquisition directory: the 79 original rows (SHA-256, source path) plus the new row.
3. **Replay gates; there is no scoring unless all pass.**
   - Each replayed complete run matches its 0918 row exactly: `probs`, `theta`, and every
     episode's solved/first_gen/evaluations_to_exact.
   - Replicate 14 matches the cut row's 30 completed episodes.
   - On failure, fall back to a full deterministic replay of all 80 acquisitions (≈ 3 750 s
     at 10 workers, measured in 0918).
4. Before admission, time about 80 searches with this run's vectors on scoring indices ≥ 2000,
   never 0–15. Price by roster-weighted means plus the observed tail rate.

**Feasibility, measured** (steward probe, 3 min, [rows](probe_timing.json), [script](probe_timing.py)).
Code `511711c` in its own worktree build, 10 workers, pinned Rayon, 28 searches with
predetermined 0918 vectors on indices 1000–1001.
- **Max:** mean **12.3 s**. One search in 20 spent 145 s in the verifier; the other 19 averaged
  5.1 s. The tail rate drives the price.
- **Sum:** mean **6.0 s**.
- **Disclosure.** The probe showed solve outcomes for 5 max vectors on 4 disjoint searches each.
  That is far too few to estimate an effect, and the design was frozen before the probe. These
  rows are excluded from inference.

**Price** (1 376 searches per family):

| Entry | Expected | Timeout |
|---|---:|---:|
| A: completion + 2 replays, 3 workers | 15–25 min | 3 600 s |
| B: sum scoring | ≈ 14 min | 2 400 s |
| C: max scoring | ≈ 28 min at a 1/20 tail; ≈ 62 min at 3/20 | 5 400 s |
| D: analysis | < 5 min | 300 s |
| **Total** | **≈ 1.1 h (pessimistic 1.8 h)** | **3.25 h** (cap 5 h) |

- If preparation timing puts max scoring above 75 min, run C as its own queue after B. Do not
  shrink the roster.
- **Agent time:** preparation ≤ 120 min, plus about 1.5 h of review and analysis.
- **Full cost:** about 4.5–5 h, under the 7 h ceiling.

**Primary comparison** (unchanged; per family, never pooled): **R_u = uniform ÷ inherited** cost.
- **Cost:** geometric-mean evaluations to the first exact solve over both training targets.
  Censored searches count at the cap of 262 144. Solve counts are reported.
- **Interval:** 95% crossed bootstrap over the 20 acquisitions and shared indices 0–15.

| Outcome | Rule |
|---|---|
| **Acquired** | lower bound > 1 and point ≥ 1.5× (takes precedence) |
| **Bounded** | upper bound < 1.5× |
| **Unresolved** | otherwise |

**Interpretation controls** (as in 0918):
L = broken ÷ inherited (beside broken ÷ uniform, so a degraded control is visible);
S = inherited ÷ scaffold; break-even in the same units.

**Expectation** (slightly revised after the probe):
- **Sum:** acquired 35%, unresolved 35%, bounded 30%. The equal drift in 0918 argues against a
  large gain.
- **Max:** acquired 45%, unresolved 30%, bounded 25%.
- **Most likely:** a modest gain over uniform in one family, with the scaffold clearly better.
- **Surprises:** inherited within 2× of the scaffold, or broken ≈ inherited with both beating
  uniform. The latter would point to generic supply, not persistent inheritance.

**Next action.** Every outcome goes straight to the strategist.
- **Acquired, L lower bound > 1 and S lower bound < 2:** price threshold-2 transfer as a candidate.
- **Acquired, but linkage unresolved or the scaffold clearly better:** record the acquisition
  and end expansion of this procedure.
- **Bounded in both families:** park 23 with a bound on this σ and schedule, not on self-adaptation.
- **Unresolved:** report the SD and the extension price.
- **Gate failure with the full replay over budget:** stop with the revised cost.

**Scope.** One modifier law, σ = 0.03, 48 × 128 generations (maintenance included), development
bank, training targets, fixed token meanings.
