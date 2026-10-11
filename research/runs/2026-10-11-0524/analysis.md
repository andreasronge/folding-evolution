---
outcome: arrangement_unnecessary_at_this_resolution
---
# Analysis: label-rearranged tree libraries versus intact libraries (0524)

Reviewer analysis of [proposal.md](proposal.md) / [queue.yaml](queue.yaml), run at commit `7c0e5df`
([execution.md](execution.md)). Raw data: `experiments/output/2026-10-11/2026-10-11-0524-prepare/` and
`.../2026-10-11-0524-score/`. Every number below was recomputed from `search.jsonl` with
[analysis_recompute.py](analysis_recompute.py) (output [analysis_recompute.txt](analysis_recompute.txt)) and
[analysis_content.py](analysis_content.py) ([analysis_content.txt](analysis_content.txt)); the harness's
`result.json` / `report.md` agree to three decimals wherever both report the same quantity.

## 1. Data completeness

| Check | Result |
|---|---|
| Queue | both entries `done`, exit 0; prepare 67 s wall, score 2,737 s wall (timeout 7,200 s) |
| Stage gate (prepare) | admitted **6 repeats, 3 realizations**; projection 3,796 s against a 6,000 s limit (4-repeat fallback not used); 288/288 development R-perm jobs solved |
| Validation (prepare) | replay of 6 saved 0348 R-lib jobs: all deterministic fields identical; interpreter/compiler check 144 cells passed; construction audit 72/72 constructions passed invariants and Rust/interpreter/Python agreement on D625 (543 verified entries) |
| Rows in `search.jsonl` | **7,776** = 24 builds × 18 cells × 6 repeats × 3 arms; 7,776 unique (build, cell, repeat, arm) keys, no duplicates; 2,592 per arm |
| Seed pairing | all 2,592 (build, cell, repeat) triples have identical 8-seed lists across the three arms; 20,736 attempt seeds, all distinct; `realization == repeat mod 3` in every row |
| Caps | every row has cap 524,288 (8 × 65,536); no row exceeds it |
| Failures | **10 unsolved jobs, all R-tree**, all at the full cap after 8 attempts (5 in A, 3 in B, 2 in C); R-lib 0/2,592, R-perm 0/2,592 unsolved |
| Scorer admission | score phase re-derived the constructions from the frozen libraries and re-checked all preparation hashes (`tree_permutation_run.score`); `git_dirty: false` |

Nothing is missing, duplicated or silently substituted. The grid is exactly the approved 7,776-job design.

## 2. Key numbers (mean capped evaluations per job)

Intervals are 95% paired bootstraps resampling the 24 builds and, within each, the 3 constructions with both
repeats and the matching R-tree/R-lib rows (the registered unit; 8,192 draws). I also report a build-only
bootstrap and a per-build log-ratio t-interval as cross-checks; they agree.

### Primary and guards (B/C = 12 cells, 1,728 jobs per arm)

| Quantity | Point | 95% interval | Rule | Status |
|---|---|---|---|---|
| **Primary: R-perm / R-lib on B/C** | **1.031** | **[0.854, 1.225]** | upper < 1.25 for retention | passes, by 0.025 |
| Baseline guard: R-perm / R-tree on B/C | 0.360 | [0.299, 0.429] | upper < 0.80 | passes |
| Replication guard: R-lib / R-tree on B/C | 0.349 | [0.301, 0.410] | upper < 0.60 | passes (0348: 0.34–0.36) |
| Reliability: solve fraction R-perm − R-lib on B/C | 0.000 | [0.000, 0.000] | lower > −0.03 | passes (1,728/1,728 both) |
| Positive control: R-perm / R-lib on A (864 jobs per arm) | 5.14 | [3.68, 7.14] | lower > 1.5 | passes |

Harness decision label: `arrangement_unnecessary_at_this_resolution`. Cross-checks on the primary: build-only
bootstrap [0.897, 1.187]; per-build geometric mean 1.012, t-interval [0.878, 1.167]; R-perm below R-lib in
11/24 builds. The retention bound therefore does not hinge on the nested resampling, but the registered
interval's upper end (1.225) sits close to the 1.25 margin.

Arm means on B/C: R-tree 72,558 · R-lib 25,343 · R-perm 26,125 evaluations. On A: 70,288 · 4,445 · 22,858.

### By split and subgroup (R-perm / R-lib)

| Group | Cells | Jobs/arm | R-perm / R-lib | R-lib / R-tree | R-perm / R-tree | Solves tree / lib / perm |
|---|---|---|---|---|---|---|
| A (control) | 6 | 864 | 5.14 [3.68, 7.14] | 0.063 [0.047, 0.082] | 0.325 [0.251, 0.414] | 859 / 864 / 864 |
| B | 6 | 864 | 1.02 [0.78, 1.30] | 0.376 [0.314, 0.451] | 0.383 [0.291, 0.490] | 861 / 864 / 864 |
| C | 6 | 864 | 1.05 [0.82, 1.31] | 0.320 [0.265, 0.389] | 0.335 [0.263, 0.417] | 862 / 864 / 864 |
| B/C learned then-pair | 4 | 576 | 0.87 [0.63, 1.17] | 0.382 [0.297, 0.492] | 0.332 [0.266, 0.406] | 572 / 576 / 576 |
| B/C other then-pair | 8 | 1,152 | 1.13 [0.93, 1.36] | 0.332 [0.286, 0.387] | 0.376 [0.300, 0.469] | 1,151 / 1,152 / 1,152 |
| all 18 | 18 | 2,592 | 1.36 [1.17, 1.59] | 0.256 [0.222, 0.298] | 0.349 [0.298, 0.407] | 2,582 / 2,592 / 2,592 |

Per cell ([analysis_ratios.png](analysis_ratios.png), left): all six A cells have R-perm/R-lib between 3.5
and 7.2 with lower bounds above 2; the twelve B/C cells range 0.78–1.51 and every B/C interval includes 1.
Per realization on B/C (576 jobs per arm each): 1.08 [0.84, 1.33], 1.01 [0.80, 1.21], 1.01 [0.77, 1.32]; no
single construction carries the result.

### Distribution, attempts and worker time on B/C

| Arm | Median evals | p90 | First-attempt solves | Jobs > 65,536 evals | Worker s per job |
|---|---|---|---|---|---|
| R-tree | 59,648 | 199,680 | 871 / 1,728 (50%) | 49.6% | 6.84 |
| R-lib | 5,632 | 71,757 | 1,367 / 1,728 (79%) | 20.9% | 2.25 |
| R-perm | 4,864 | 73,293 | 1,385 / 1,728 (80%) | 19.8% | 2.34 |

R-perm's median and first-attempt rate are slightly better than R-lib's; its mean is slightly worse because
of the upper tail. The registered metric is the mean.

Totals: 7,776 jobs, 27,157 worker-seconds (R-tree 17,284 · R-lib 4,158 · R-perm 5,715), 2,721 s wall,
sustained concurrency 9.98. The proposal's price (≤ 37,000 worker-s, about 1 h wall) held.

## 3. What the constructions actually contained

From `construction_audit.json` (the harness's exact motif definitions; counts summed over the 24 libraries,
181 entries per realization, mean 7.5 entries per library):

| | Intact | Realization 0 | Realization 1 | Realization 2 |
|---|---|---|---|---|
| Entries changed (label-wise) | — | 82% mean (25–100% per library) | | |
| Distinct behaviours (D625) | 168 | 174 | 174 | 174 |
| `ADD(Xa,Xb)` occurrences by split A / B / C | 300 / 3 / 18 | 28 / 21 / 36 | 35 / 28 / 33 | 20 / 31 / 31 |
| `GT(ADD(X2,X3),ADD(X0,X1))` occurrences (the learned predicate, this orientation only) | 63 (in 20 builds) | 0 | 1 | 0 |
| Split-A predicates, either orientation | 63 | 1 | 6 | 0 |
| Accidental split-B / split-C predicates | 0 / 0 | 4 / 4 | 3 / 6 | 4 / 3 |

So the control removed the learned predicate almost completely (not "kept in about 1/3", as the proposal
estimated) and raised B/C pair supply from 21 to 57–62 occurrences while creating a handful of B/C-correct
predicates. The proposal's "48 / 1 / 6" came from a different counting rule in the read-only probe; the
ordering is the same.

**Did the search use the rearranged material?** Literal contiguous-subtree matches in final solvers
(denominator: solved jobs):

| Group, arm | Solver has the cell's own `GT(ADD,ADD)` | Contains a ≥ 5-node entry of its own donor set verbatim | Contains an intact ≥ 5-node 0150 entry verbatim |
|---|---|---|---|
| A, R-lib | 499 / 864 (58%) | 513 / 864 (59%) | 513 / 864 |
| A, R-perm | 214 / 864 (25%) | 201 / 864 (23%) | 91 / 864 |
| A, R-tree | 250 / 859 (29%) | — | 45 / 859 |
| B/C, R-lib | 432 / 1,728 (25%) | 34 / 1,728 (2%) | 34 / 1,728 |
| B/C, R-perm | 609 / 1,728 (35%) | 180 / 1,728 (10%) | 6 / 1,728 |
| B/C, R-tree | 488 / 1,723 (28%) | — | 0 / 1,723 |

Library-draw mechanics are the same in both donor arms on B/C (insertion per draw 0.475 vs 0.473, rejection
0.525 vs 0.527; on A the intact library inserts more, 0.64 vs 0.48). Training-perfect-but-not-exact
individuals are about 5% of evaluations in all three arms, as in 0348.

## 4. What the data shows

1. **The B/C gain survives label rearrangement at the registered resolution.** Rearranged libraries cost
   1.03× the intact ones on B/C, interval [0.85, 1.23], and still cut restarted tree GP to 0.36×. Both
   registered conditions for "arrangement unnecessary" hold, with no reliability loss observed (1,728/1,728
   in both donor arms).
2. **The positive control worked, strongly.** On split A, rearrangement raised cost 5.1× (interval
   [3.7, 7.1]); every A cell and every build agrees. The A-specific advantage of the intact libraries
   (0.063× R-tree) is almost entirely removed, and after rearrangement A behaves like B/C (R-perm/R-tree
   0.325 on A versus 0.360 on B/C).
3. **Replication.** R-lib/R-tree on B/C is 0.349 [0.301, 0.410], matching 0348's 0.363 / 0.338 per split on
   fresh seeds.
4. **The rearranged material was used.** R-perm solvers on B/C contain a ≥ 5-node donor entry verbatim
   five times as often as R-lib solvers (10% vs 2%) and contain the cell's correct predicate more often
   (35% vs 25%), without any corresponding change in mean cost.

## 5. What the data does not show

- **It does not identify the carrier.** Rearrangement removed the learned arrangement *and* changed pair
  identity, operator placement and behaviour (78% of entries change behaviour; B/C pair supply tripled).
  Retention is consistent with explanation (b) of question 47 (shapes, sizes and size-conditioned counts
  suffice), but equally with a cancellation between losing something useful and gaining B/C pairs. The
  learned-then-pair subgroup (0.87 [0.63, 1.17]) versus the other eight cells (1.13 [0.93, 1.36]) is the
  only hint of structure and is unresolved.
- **It does not show that the gain is token-only or that acquisition could be cheaper.** Only this
  specific shape/size/arity/width-conditioned construction was tested.
- **Explanation (c), "intact pairings misdirect on B/C", is not supported**: R-perm is not resolvably
  cheaper than R-lib (lower bound 0.85, point above 1), despite a better B/C pair supply and more use of
  its entries in solvers.
- **An intact advantage of up to about 20% on B/C is not excluded.** The upper bound passes the 1.25
  margin by 0.025; the harness's own price for pushing the *lower* bound above 1.10 is about 150 more
  acquisitions, so the question "is there a small intact advantage" is not worth another run of this kind.
- Development bank; split A's control concerns a split where the predicate is known to matter and does
  not establish selective destruction on B/C.

## 6. Economics (acquisition-inclusive, B/C)

Each library costs 2.88M evaluations [2.60M, 3.16M] to acquire (0150 source jobs, including failures).
Savings per B/C job: R-lib 47.2k [41.3k, 52.8k], R-perm 46.4k [40.2k, 52.5k]; repayment after about 61 and
62 B/C searches respectively. Construction time is negligible. Rearrangement neither adds nor removes
economic value on B/C; on A it removes most of it.

## Against the predictions

Read [plan.md](plan.md) after the sections above were written.

| Plan / proposal prediction | Observed |
|---|---|
| Replication guard: B/C R-lib/R-tree upper < 0.60 | 0.349 [0.301, 0.410]: **passes** |
| Reliability guard: B/C solve difference lower > −0.03 | 0.000 [0.000, 0.000], 1,728/1,728 in both donor arms: **passes** (finite-sample; not population equality) |
| Retention: R-perm/R-lib upper < 1.25 and R-perm/R-tree upper < 0.80 | 1.031 [0.854, **1.225**] and 0.360 [0.299, 0.429]: **both pass**, the first by 0.025 |
| Positive control: A R-perm/R-lib lower > 1.5 | 5.14 [3.68, 7.14]: **passes**, so retention is read as the plan's "replacement by this shape/count-conditioned procedure at this resolution", not as control too weak |
| Intact-information branch (lower > 1.10 and point ≥ 1.25) | lower 0.854, point 1.031: **not reached** |
| Resolved B/C cost decrease ("gain from the rearranged procedure") | upper bound 1.225 > 1: **not reached**; the harness's sub-label for this case was not triggered |
| Proposal's expectation (≈65%): B/C retention with R-perm/R-lib in 0.8–1.1, A losing 2–5× | B/C point 1.03 is inside 0.8–1.1; A lost 5.1×, at the top of the expected range |
| Proposal's surprises: resolved B/C loss despite better pair supply; no loss on A | neither occurred |
| Plan: six repeats expected about one hour at ten workers; fallback to four if projection > 100 min | gate projected 63 min, admitted six repeats; actual scoring 45 min wall at concurrency 9.98 |
| Plan: predicate survival "1, 5 and 0" for the forward-oriented A predicate | as the code review noted, those counts are the *reversed* orientation `GT(ADD(X0,X1),ADD(X2,X3))`, which the intact libraries never contain; the learned orientation `GT(ADD(X2,X3),ADD(X0,X1))` survived 0, 1 and 0 times. Either way the control removed the predicate almost entirely, making A a stronger control than the proposal's "about 1/3 kept" assumed |

The outcome matches the proposal's first label, "arrangement unnecessary at this resolution", under the plan's
restricted reading: this particular shape/size/arity/width-conditioned rearrangement keeps the B/C gain, and the
split-A gain is arrangement-specific. The data do not say what the retained gain is made of (section 5), and the
retention margin passed narrowly. Per the proposal's next action, this returns to strategy to price a simpler
statistical acquisition; nothing is funded automatically.
