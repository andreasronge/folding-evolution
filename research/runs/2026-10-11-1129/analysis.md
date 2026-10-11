---
outcome: observations
---
# Analysis — 2026-10-11-1129 order-helper acquisition probe

Reviewer: independent analysis of the two queue entries at commit `db30b15`. Raw data:
[prepare](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1129-prepare)
(`bank.json`, `acquisition.jsonl`, `libraries.json`) and
[score](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1129-score)
(`score.jsonl`, `report.json`). Plot: [analysis.png](analysis.png) (my own; the runner's `probe.png` agrees).
This is a `kind: probe`: everything below is descriptive on the six development cells. Nothing here is protected
or transfer evidence.

## 1. Data completeness

Both queue entries finished with exit 0, no `failure.json`, and the queue runner exit was 0.

| Phase | Expected | Found | Notes |
|---|---|---|---|
| Bank | 24 sources + 30 destinations | 54/54 retained, admitted | 6 development, 24 protected (4 disjoint, 20 overlapping); `protected_searches = 0` in both phases |
| Acquisition | 8 builds × 24 cells × 2 jobs = 384 R-tree source jobs | 384 rows, 384/384 solved | first attempt solved 378/384 (98%); mean 4.2 k evaluations |
| Libraries | 8 × (literal, semantic) | 8 × 16 + 8 × 16 entries | all pass `verify_entries`; score phase re-derived them and matched hashes |
| Scoring | 6 cells × 5 arms × 8 builds × 2 repeats = 480 | 480 rows, 480 unique keys, 0 duplicates | all 96 (cell, build, repeat) groups carry identical seed schedules across the 5 arms |
| Unsolved jobs (charged 524,288) | — | R-tree 0, R-order 0, R-sum 3, R-L 2, R-S 3 (each of 96) | all unsolved rows used exactly 8 attempts |

`validate_rows` (restart accounting, seed-attempt match, exact solver recheck) ran in both phases.
`report.json`'s `preparation_hash` equals `preparation.json`'s. Timing: prepare 118 s wall (105 s is the
nine-token alias screen), score 332 s wall against a 1,770 s internal deadline. Total queue 7.5 min of the 50 min
approved.

Bank note (code review note 1): all 12 `S:hi..+Xc` sources carry `alias_kind = domain_near_alias` with a
best ≤ 9-token agreement of 525/625 (84%). The admission rule excludes only exact aliases, so they were kept.
No destination exceeds 370/625 (59%). The best agreement with any saved independent-input bank cell is
475/625 (76%), below the 80% exclusion. A later protected proposal has to say which near-alias rule it freezes.

## 2. Key numbers

### 2.1 Arms on the six development cells (96 jobs each, 8 × 65,536 cap, paired seeds)

| Arm | Solved | First-attempt solves | Geometric mean | Median | Capped mean | Worker s |
|---|---|---|---|---|---|---|
| R-tree | 96/96 | 54/96 (56%) | 38.7 k | 46.5 k | 75.7 k | 523 |
| R-sum (1019 constructor prior) | 93/96 | 30/96 (31%) | 82.2 k | 97.9 k | 155.5 k | 1,014 |
| R-order (12 supplied helpers) | 96/96 | 91/96 (95%) | 1.87 k | 1.5 k | 5.4 k | 36 |
| R-L (literal extractor) | 94/96 | 29/96 (30%) | 60.0 k | 76.0 k | 133.0 k | 884 |
| R-S (behaviour-keyed extractor) | 93/96 | 42/96 (44%) | 38.8 k | 69.0 k | 106.8 k | 733 |

Paired log-cost ratio against R-tree (96 pairs; 95% bootstrap CI over pairs, then over the 6 cells as clusters):

| Comparison | Ratio | Pair CI | Cell-cluster CI | Arm cheaper in |
|---|---|---|---|---|
| R-sum / R-tree | 2.12× | [1.54, 2.91] | [1.70, 2.55] | 30/96 |
| R-order / R-tree | 0.048× | [0.04, 0.06] | [0.04, 0.07] | 96/96 |
| R-L / R-tree | 1.55× | [1.09, 2.17] | [1.16, 2.13] | 38/96 |
| R-S / R-tree | 1.00× | [0.68, 1.46] | [0.63, 1.68] | 49/96 |
| R-S / R-L | 0.65× | [0.43, 0.97] | [0.53, 0.80] | 56/96 |

Log gap R-tree → R-order is 3.03 nats (20.7×), larger than stage 0's single-attempt estimate. Gap recovered
(geometric, as the plan defines it): R-S −0.001, R-L −0.14, R-sum −0.25. No learned arm recovers any of it.

Per cell (geometric mean of 16 jobs, k evaluations): R-tree 20–78 k, R-order 1.5–2.3 k, R-sum 55–134 k, R-L 38–71 k,
R-S 19–56 k. R-S is cheaper than R-tree on the three cells needing `lo23` or `hi13` (18.8 vs 32.5, 29.4 vs 40.7,
37.0 vs 78.1 k) and dearer on the other three; see §2.4 for why that is confounded with build.

### 2.2 Acquisition: which helpers entered a library

Recommendation rule inputs: a destination-needed helper (one of the 7 needed by the development cells) included
in ≥ 6/8 builds and ≥ 50% gap recovered.

| Arm | Builds with any helper entry | Builds with a destination-needed helper | Entries |
|---|---|---|---|
| R-L | 0/8 | 0/8 | — |
| R-S | 3/8 | 2/8 | build 1: `hi13`; build 2: `lo03`; build 4: `lo03`, `lo23`, `hi03` |

Neither arm meets the rule. `report.json` records the same (`helper_build_counts` R-L 0, R-S 2; recommendation
"return located or unresolved limit").

Fate of the 96 helper × build cases under R-S (right panel of the plot):

| Fate | Cases | Meaning |
|---|---|---|
| Not recurrent (< 2 source cells had any subtree with the helper's output) | 26 | nothing poolable |
| Recurrent, but smallest observed form > 9 nodes | 21 | emission-size limit |
| Recurrent, admissible 3–9-node form, uncapped rank 17–32 | 44 | lost to the 16-entry cap |
| Included (rank 14–16) | 5 | the three builds above |

So in 49/96 cases R-S had an admissible, recurrent helper class in hand and the cap dropped it in 44 of them.
Under R-L, the 6-node literal form recurred in 2 cells in only 5/96 cases (ranks 20–23), never inside the cap;
in the other cases the helper's literal forms were singletons (one cell each), because the same behaviour is
written in different 6–9-node syntaxes across solvers.

What fills the 16 slots: every R-S entry except the five helpers is a 3-node tree. Across builds the slots go to
the six pairwise sums `Xa+Xb` (3–8 source cells each), 7–10 `GT` comparators (3–5 cells), and a constant-0 class
(a `GT(Xa, k)`-type subtree that is always 0 on D625; 5–8 cells, ranked first in builds 4 and 6). R-L libraries
are the same kind of content plus 3-node forms equal to a single input or `X0+1`. The ranking is by distinct
source cells first; each helper occurs in exactly 2 source cells by bank construction (`lo(a,b)+Xc` for two
values of `c`), so a helper can only enter when fewer than 16 classes have ≥ 3 cells and it then wins the
2-cell tie on solver count (the five included entries all had 4/4 source solvers). This is explanation (c),
cap crowding, with the crowd being sums, comparators and a constant class rather than only sums.

### 2.3 Helper census of the 384 source solvers

| | Count |
|---|---|
| Solvers containing a subtree computing their own helper on D625 | 242/384 (63%) |
| … smallest such subtree is the 6-node form | 59 |
| … smallest such subtree ≤ 9 nodes (emittable) | 91 |
| … smallest such subtree 10–23 nodes | 151 |
| Solvers containing a non-own helper | 0 |
| Source solver size | median 14 nodes; 40/384 are the 8-node canonical |

Per helper, 13–26 of its 32 solvers contain it, and 3–12 contain an emittable form. Stage 0's 41/71 and 11/44
figures hold up at scale (63% and 59/242). Evolution builds the helper most of the time, but in bloated form in
62% of those solvers.

### 2.4 Does an included helper help? (6 job pairs; suggestive only)

| Cell, build | R-S cost | R-tree cost, same seeds |
|---|---|---|
| `lo02+hi13`, build 1 (`hi13` in library) | 2,816 · 2,816 | 8,192 · 73,472 |
| `lo23+hi02`, build 4 (`lo23`) | 68,096 · 2,560 | 16,384 · 18,176 |
| `lo23+hi12`, build 4 (`lo23`) | 2,304 · 22,016 | 135,168 · 218,880 |

Two of the four build-4 solvers on `lo23` cells contain the `lo23` donor verbatim. Build 4 is R-S's cheapest
build (geometric 12.9 k vs R-tree 24.3 k on the same seeds). Splitting the paired comparison by build:

| Builds | R-S / R-tree | R-S / R-L |
|---|---|---|
| No helper entry (0, 3, 5, 6, 7; 60 pairs) | 1.14× [0.69, 1.85] | 0.80× [0.45, 1.42] |
| Any helper entry (1, 2, 4; 36 pairs) | 0.81× [0.46, 1.38] | 0.46× [0.25, 0.82] |
| Needed helper (1, 4; 24 pairs) | 0.67× [0.33, 1.31] | 0.27× [0.13, 0.55] |

The R-S advantage over R-L is concentrated in the builds whose library holds a helper; without one, R-S is
no better than R-tree and not clearly better than R-L. These are post-hoc splits with 24–60 pairs and
overlapping intervals against R-tree. They are consistent with "a helper in the library is used" but do not
establish it.

### 2.5 Other observations

- **R-order is not at the floor but close.** Median 1,536 evaluations (6 generations at P 256; floor 768),
  first attempt 91/96. Its solvers are median 13 nodes (the canonical size) and contain both needed helper
  literals verbatim in 73/96, one in 23/96. Not a shortcut: the donors are the solution.
- **R-tree does build the 6-node form.** 47/96 R-tree destination solvers contain the canonical 6-node form of
  at least one needed helper (both in 3). The content is reachable; it is just not cheap.
- **A library of 3-node trivia costs search time.** R-L (1.55×, CI excludes 1) and R-sum (2.12×, CI excludes 1)
  are both dearer than no library at all, with half of mutation draws taken by donors. R-sum's six sum
  constructors (`Xa+Xb`) and R-L's sums and comparators are all things R-tree finds in one generation; the
  donor draws displace useful mutation. The 1019 sum prior, which cut cost 3.1× on development gate-sum cells,
  roughly doubles it on these order cells.
- **Sources are not where the cost is.** 384/384 source solves, mean 4.2 k; the acquisition budget was not a
  constraint.

## 3. What the data shows and does not show

Shows (development cells, descriptive):

1. The unchanged literal extractor acquires no order helper in 0/8 builds. Its literal 6-node form recurs across
   two cells in 5/96 helper × build cases and ranks 20–23 there. Explanation (b), literal keying, is confirmed as
   one of the limits: behaviour keying finds an admissible recurrent class in 49/96 cases where literal keying
   finds one in 5/96.
2. Behaviour keying alone does not get helpers into the library: 44 of those 49 cases are ranked 17–32 under the
   cells-first ranking with a 16 cap. The located limit for R-S is (c), crowding, by 3-node sums, comparators
   and a constant class that recur in 3–8 cells against the helpers' structural maximum of 2. A second limit,
   emission size (21/96 cases), sits behind it.
3. Neither learned arm recovers any of the 3.0-nat R-tree → R-order gap on average. R-L and R-sum are worse
   than R-tree with intervals excluding 1.
4. The supplied prior is a 20× ceiling here, larger than stage 0 suggested, and the helpers are present in
   63% of source solvers.

Does not show:

- That raising the cap, ranking by solver count, or restricting pooling to ≥ 4-node forms would recover the gap.
  The build-split in §2.4 is suggestive (0.67× on 24 pairs with a needed helper) but is post hoc and overlaps 1.
- Anything about protected cells or transfer. The protected roster was never searched.
- Mechanism separation between (b) and (c): R-S changes keying, pooled sizes and representative choice together,
  so R-S > R-L (0.65×) implicates the bundle. Within R-S, the diagnostics separate crowding from emission size
  cleanly, which is the useful part.
- Whether the near-alias flag on the 12 `S:hi` sources matters; nothing in the scoring depends on it, but a
  protected proposal has to decide the rule.

## Against the predictions

Read after the analysis above. The plan (and proposal) are a probe: a recommendation rule, not an outcome
table. Checked item by item:

| Plan statement | Data |
|---|---|
| Queue fits 20 + 30 min; expected wall 10–15 min | 118 s + 332 s = 7.5 min. Fits. |
| All 24 sources survive admission; ≥ 8 protected with ≥ 2 disjoint | 24/24 sources, 24 protected (4 disjoint). Met. The 12 `S:hi` near-alias flags are recorded in `bank.json` but not in the plan's screening summary. |
| 384 source jobs with charged failures | 384/384 solved; nothing to charge. |
| Price a protected proposal only if a learned arm holds a destination-needed helper in ≥ 6/8 builds and recovers ≥ 50% of the log gap | R-L 0/8 and −14%; R-S 2/8 and −0.1%. **Rule not met; route back to strategy with a located limit**, as the plan prescribes. |
| Proposal expectation: R-L holds helpers in ≤ 2/8 builds and is no better than R-tree | Held: 0/8, and R-L is 1.55× dearer (CI [1.09, 2.17]). |
| Proposal expectation: R-S recovers some helpers but loses others to cap crowding, landing between R-tree and R-order | Half held: 5 helper entries in 3 builds, 44 eligible cases lost to the cap. But R-S did **not** land between R-tree and R-order: 1.00× R-tree overall. |
| Plan interpretation keys: eligible recurrent helpers ranked below 16 → cap crowding; recurrent with no ≤ 9-node form → emission-size limit; low census → limited availability | Primary located limit is **cap crowding** (44/96 cases), with **emission size** second (21/96) and non-recurrence third (26/96). Census is high (242/384), so availability is not the limit. |
| R-S improving on R-L implicates the bundle, not keying alone | R-S / R-L = 0.65× [0.43, 0.97]; concentrated in builds with a helper entry (0.46× on 36 pairs) and absent without one (0.80× [0.45, 1.42]). Interpreted as the bundle plus content, per the plan. |
| "Acquired helpers with little search benefit" vs usefulness | The two builds with a needed helper show R-S at 0.67× R-tree on 24 pairs, interval overlapping 1. Usefulness is not demonstrated, not refuted. |
| Stage 0 suggests little headroom against R-order | R-order is 20× below R-tree here and near the floor (median 1,536 vs 768). Headroom against it was never in question for this probe and remains unmeasured. |
| Surprises listed in the proposal: R-L recovering helpers; R-S failing despite the census; R-order far from floor | None occurred. One unlisted observation: the 1019 sum prior **hurts** on order cells (2.12×, CI [1.54, 2.91]), and so does the literal library. Donor libraries of 3-node content are a cost, not neutral. |

Routing per the plan's own rule: return to strategy with the located limit. The limit for R-S is the 16-entry
cap under cells-first ranking, where each order helper is structurally capped at 2 source cells while 3-node
sums, comparators and a constant class reach 3–8. The limit for R-L is literal keying (5/96 recurrent cases
against R-S's 49/96). Whether relieving the cap or the ranking converts acquisition into search benefit is an
open question that this probe's §2.4 split motivates but does not answer; the steward should treat those
24-pair numbers as a pricing input only. No variant sweep was run, and none is implied by this analysis.
