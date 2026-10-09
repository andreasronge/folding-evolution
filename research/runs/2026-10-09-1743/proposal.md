---
node: questions/10-compositional-map-transfer/35-small-source-acquisition
title: Four-attempt sources for the complete C+F pipeline on then-addition
bank: then-addition-v1
---
Follows [strategy 1743](strategy.md) and its [plan](../../plans/small-corpus-complete-pipeline.md),
with one change (below). New sub-question [35](../../questions/10-compositional-map-transfer/35-small-source-acquisition/question.md), budget 1; root 10 at 27.

**Question.** Can C4+F4, rebuilt only from four capped G4 source attempts per training cell
(failures charged), match the full-corpus C+F pipeline (48 attempts) on then-addition? Sources
would cost about 8% of the search time. Does F4 still beat C4's own chain blocks (W4)?

**Closest known technique.** The map adapts by **external fitting** to earlier solvers.
Distribution transfer from source problems:
[Ardeh, Mei & Zhang 2020](https://gpbib.cs.ucl.ac.uk/gp-html/Ardeh_2020_CEC.html).
Probabilistic grammar learning in GP:
[Wong, Wong & Leung 2016](https://gpbib.cs.ucl.ac.uk/gp-html/conf_tpnc_WongWL16.html).
Run-transferable libraries: [Keijzer et al. 2004](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf).
Joint library and policy learning: [DreamCoder](https://people.csail.mit.edu/asolar/papers/EllisWNSMHCST21.pdf).
Adds: a priced boundary test of how few solvers decoder and library need.

**Probe (done, 2 min, not efficacy; [script](steward_probe/small_source_probe.py), [output](steward_probe/small_source_probe.json)).**
Refitting from all 48 attempts reproduced the 16 full C hashes. The first four attempts gave
150/256 solvers, with 4 empty cells (G4 fallback). F4 holds 4–28 fragments, none empty, and C4 is
sharper than C. On 64 unpaired then-addition searches per arm:

| arm | solved | geometric cost | worker-s per search |
|---|---|---|---|
| C4 | 51/64 | 112k | 7.9 |
| C4+F4 | 61/64 | 42k | 3.8 |
| 1036 C | — | 67k | — |
| 1036 F | — | 46k | — |

Retention is plausible; the library may rescue a weaker decoder.

**Change from the plan: four disjoint source blocks.** Block b (0–3) is attempts 4b+1…4b+4 of each
1246 schedule's 48 per cell. That gives 64 equal-allocation acquisitions. Seed s of 1036's 16 seeds
per (corpus, cell) uses block s mod 4, so the scoring cost is unchanged. Each corpus averages four
acquisitions, not one draw of source luck. Block 0 is the audited prefix; blocks 1–3 are
uninspected.

**Build.** Reuse research/main's fitter, extractor, operator and runner (1036 path, suffix kept).
- **C4:** the unchanged estimator. An empty cell takes G4's expected length-32 transitions.
- **F4:** may hold fewer than 32 fragments. If empty, F4 and W4 both use uniform 3–6 chain blocks.
- **W4:** draws from C4 with F4's length, start and rate laws.

Prepare checks:
- attempt keys, source hashes and exact solvers;
- the legacy estimator reproduces full C, and an all-empty source recovers G4;
- the edit audit;
- 16 F and 16 W rows from 1036, plus 2 G4 rows from 1548, replay bit-exactly (if the F or W rows
  fail, stop).

**Arms and unit.**
- **New arms:** C4+F4 and C4+W4 on 1036's then-addition roster (16 corpora × 16 cells × 16 seeds;
  4,096 each, 8,192 in total). They share initial programs and case draws.
- **Paired references from 1036:** full F, W and C. Same cases, but different initial programs
  (intended).
- **Unpaired reference:** G4, from 1548.
- **Unit:** corpus, n = 16.

**Feasibility and cost.** Using the probe's rates and W4 ≈ 6.8 worker-s:
4,096 × 10.6 / 9.94 ≈ **73 min**, or 85 min with a 15% margin.
- **Admission:** if smoke × 1.15 > 150 min, use 12 seeds; if that still does not fit, write
  `infeasible.md`.
- **Queue timeouts:** 30 + 180 min = **3.5 h**.
- **Agents:** about 3 h (preparation ≤ 2 h).
- **Total:** 5–6.5 h of the 14.3 h left.
- **Acquisition prices:** source worker-s per corpus, 3,002 for the full corpus against 240 for
  block 0, plus verification, fit and extraction.

**Primary comparison.** Retention ρ = F/(C4+F4). It is exp(mean over corpora of the paired log cost
difference), with unsolved runs counted as 2 × cap, and a 95% t interval on 15 df. The tolerated
loss is **0.833** (20% more search cost). That equals F's increment over W (1.20×), so a larger loss
gives back a whole learned component.
1. **Retained:** lower bound > 0.833. Cheap acquisition becomes actionable.
2. **Tight loss:** upper bound < 0.833. Ends this four-attempt policy.
3. **Unresolved:** otherwise. Price the resolution.

Expected half-width ×1.08–1.15 (1036's F/W SD plus acquisition variance).

**Secondary, no rule.**
- (C4+F4)/(C4+W4), read against 1.10. If W4 retains and F4 adds less than 1.10, that favours
  acquiring C alone.
- (C4+W4)/W and (C4+F4)/G4.
- Per block and per cell, BE/PA, 1 × cap, both-solved, fallbacks, and F4's sizes and `gt` joins.
- **Cost curves A + N·S** for G4, the full pipeline and the cheap one, with break-even N and
  corpus-bootstrap intervals. There is no break-even when the savings are not positive.

**Expectation.** ρ ≈ 0.95 [0.85, 1.06] (rule 1 or 3), and F4/W4 ≥ 1.2. Surprises: ρ resolved
above 1 (full corpus over-sharpens) or ρ < 0.7.

**Scope.** Reused development sources and tasks; not fresh-bank transfer or map evolution.

**Next action.** Every rule returns to strategy.
