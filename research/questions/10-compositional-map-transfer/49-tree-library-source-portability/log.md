# Log: 49 tree-library source portability

- 2026-10-11 (steward, 0833): opened. Read-only content probe (feasibility only, not the method's data): the
  unchanged 0150 `extract` (`163f005`) applied to saved 0024 TS R-tree solvers (target cells, 8 jobs per cell,
  4-cell pseudo-rosters, 48 pseudo-builds) gives 2–11 entries (median 6); entries are distinct-input pair sums
  `ADD(Xi,Xj)`, single-input comparisons `GT(Xi,Xj)`, input-plus-constant sums and a few 5-node nests; no 7-node
  `GT(ADD,ADD)` predicate (TS gates compare single inputs). In the real TS source roster only X0+X2 and X1+X2
  occur in two cells' formulas; other pair sums enter only if solvers use them incidentally. An ad hoc R-tree run
  on the TS sources with the main checkout's Rust extension gave invalid VM outputs (canonical program 20% correct);
  discarded: the researcher must use the worktree's own build.

- 2026-10-11 (steward, 0833): **experiment** [run 0833](../../../runs/2026-10-11-0833/analysis.md), commit
  `28db964`. The unchanged 0150 policy was run on the four `TS.split.source` cells: 24 new builds, 8 R-tree jobs
  per source cell each (768 acquisition jobs, 768/768 solved, 0.245 M [0.218, 0.275] evaluations per library).
  Same extractor, frozen before collection. Arms on gate-sum B/C (12 cells × 24 builds × 6 repeats): R-tree,
  R-TS (new libraries), R-DG (saved 0150 libraries, reconstructed), R-sizeTS (size/length-matched random donors
  per TS library). Native TS (8 target cells × 24 × 4): R-tree, R-TS, R-DG, reported separately. Stage-0 timing
  gate admitted (projected 269 s / 5,733 s against 2,700 / 9,000 s). 9,216/9,216 rows, shared attempt seeds in
  every slot, scoring 53 min wall. All validation passed: VM agreement, source/target separation, 0150 replay,
  DG reconstruction, seed audit.
  **Result.** B/C mean capped evaluations: R-tree 71,036 · R-TS 27,124 · R-DG 26,281 · R-sizeTS 66,844.
  Primary **R-TS ÷ R-tree 0.382 [0.335, 0.433]** (paired 24-build block bootstrap). Solve difference +0.003
  [+0.001, +0.005] (1,728 vs 1,723 of 1,728). This meets the pre-set *portable* branch (upper < 0.80, guard
  > −0.03). R-TS ÷ R-sizeTS 0.406 [0.344, 0.482]. R-TS ÷ R-DG 1.032 [0.862, 1.224] (independent cohorts;
  unresolved, a difference of about 15–20% either way is not excluded). R-TS was below R-tree in 24/24 builds
  (0.19–0.68) and in all 12 cells (0.29–0.61, every cell's upper bound < 0.80). Charging failures at ½× or 2×
  the cap changes nothing (0.386 / 0.374). Worker seconds 0.362 [0.315, 0.414]. Repays acquisition after
  **5.6 [4.9, 6.4]** B/C searches in evaluations (DG libraries: 64 [54, 76]).
  Native TS (never pooled): R-tree 5,414 · R-TS 9,622 · R-DG 7,198 mean evaluations, all 768/768 solved.
  **R-TS ÷ R-tree 1.777 [1.578, 2.000]**, so any saving is excluded and libraries make this roster costlier.
  R-DG ÷ R-tree 1.329 [1.122, 1.574]. R-tree solves 98.7% of these jobs on the first attempt; the extra cost is
  in restarts and the tail (p90 22,016 vs 8,960). It is unrelated to library size (Spearman −0.14).
  Library audit (descriptive): 3–10 entries per library (median 6.5); 144/148 entries are 3-node. Mostly
  `ADD(Xi,Xj)` (60) and input+constant sums (55). The 7-node `GT(ADD,ADD)` predicate appears in 0/24 TS
  libraries (DG: 21/24). Every TS library contains at least one pair sum for each B/C split; 18/24 DG
  libraries contain none.
  Explanations: (a) supported for this source pair and destination. (b) not supported: R-TS is far below
  R-tree and R-sizeTS. (c) contradicted: native TS was harmed, B/C helped. Observational, from two cohorts
  rather than a controlled contrast: a library with no comparison predicate and no reliance on split-matched
  pairs gave a B/C saving similar to DG's, so neither seems necessary for it. Small `ADD(input, input|const)`
  donors are the common content, consistent with 48's label-law reading; this is a hypothesis, not a result.
  Not shown: what is sufficient; whether DG's predicate adds anything on B/C (R-TS ÷ R-DG unresolved); whether a
  lower mix or a library-on-failure gate removes the native harm; any fresh-bank transfer (all development
  rosters).

  Decision: close 49 and return to strategy (`next: strategy`) because the primary landed well inside its
  pre-set portable branch with the guard passing, (a) is answered for these rosters, root 10's 41-slot
  allocation is spent, and strategy 0833 reserved the next choice (unfamiliar-content boundary vs simpler
  statistical generator) for its own review. The native-TS harm is a new deployment question; I have recorded
  it as parked [50](../50-library-easy-target-harm/question.md) rather than continuing 49.

- 2026-10-11 (steward, 1019): wording correction from [critique 1019](../../../runs/2026-10-11-1019/critique.md)
  §Digest check. (1) "No comparison predicate" in the digest and root summary was too broad: the 24 TS
  libraries hold 13 smaller GT-rooted entries (input/input, input/constant); what is absent from all 24 is the
  seven-node `GT(ADD,ADD)` predicate. That is an exhaustive observation on these saved libraries, not evidence
  that TS acquisition cannot produce it. (2) "Unrelated to library size (Spearman −0.14)" above should read: the
  observed size–harm rank correlation was −0.14 across these 24 builds (sizes 3–10, no interval, no size
  intervention); a size effect is unresolved. Digest and root summary corrected; entries above left as written.
