---
estimated_minutes: 78
---

Implement the approved four-reducer feasibility study, with the proposal's frozen arms,
roster, screen, split and search budgets. This is implementation of an approved design;
no new pre-registration or findings promotion is requested. Expected queue wall time is
60–78 minutes without C, about 150 minutes with C. One 14,400-second queue timeout;
12,600-second internal deadline. Read-only inspection preceded this plan; no experiment
or smoke test has run.

Conditions and seeds

- Add FIRST as token 23 in `v2_rmin_first`, preserving `v2_rmin`. Empty/wrong-type
  reducer inputs return zero. Exhaustive semantic/Python validation through depth 4,
  100,000 random length-32 Python/Rust comparisons (seed 1603001), all 36 padded
  canonicals checked in Rust. Screen D625/D1331/D2401 through stored depth 8 and
  output-only depth 9, exact typed-state dedup; drop >=80% aliases and exact duplicates.
- Select only D1331. BE has 12 and PA 24 cells. Apply the original role-covered
  lexicographic holdout-pair rule separately to each family; no cross-label split.
- U, F4, G4, G4-marg, G4-BE, G4-PA, G4-BE-marg, G4-PA-marg;
  24,000 alleles, 24 tokens, 25 rows, all weights as proposal. P=256, length=32,
  cap=524,288, 64-case lexicase, exact verification over all 1,331 cases.
- B: 50 paired seeds per retained cell/arm, seed IDs 1603100–1603149, balanced
  blocks of ten. Every arm on a cell receives the same seed. Independent bootstrap
  seed 1603002, 2,000 draws of seed indices within each fixed cell, carrying all arms.
- C only if both splits, frozen headroom (each F4/G4/G4-marg median >=4,096 on
  at least three of four holdouts), G4 training tractability (>=35/50 solves and
  observed KM median <=65,536), and measured complete cost pass. Two trajectories
  per family, seeds 1603200–1603203, G4 initialization, (4+12), 25 generations,
  24 fresh training searches per candidate, inner cap 65,536. Fresh final scoring
  seed IDs 1603300–1603349 on training and 1603400–1603499 on holdouts, paired
  across G4 and four learned maps.

Measurements and infrastructure

Extend/reuse the existing composition screen/search and token-learning harnesses.
The new staged runner will emit validation.json, screen/domain bank JSON (including
near-alias witnesses and role-coverage obstacles), calibration.jsonl, checkpoint_b1.json,
summary.json, a readable report and calibration plots under RUN_DIR. Records identify
cell, family, arm, seed, cap, solved/evaluation time and elapsed seconds; these are
produced directly. Grouping is explicitly cell × arm and family × contrast. KM medians
and seed-bootstrap intervals are produced from event/censor records; an unobserved
median is reported as `> cap`, never substituted with cap. Solve curves are at
4,096/32,768/131,072/524,288, with mean seconds including censored runs. Family
speed ratios use capped log2 times and the proposal's geometric mean over fixed cells.
Report G4/U, F4/U, G4/G4-marg, matched/G4, grammar and marginal matched/swapped
contrasts and family censoring. Plots show solve curves and contrast intervals.

First balanced block logs all solves, seconds including capped runs and projected B/C
cost. C projection counts 4 × (4 initialization + 25 × 16) × 24 inner searches
(38,784), plus five-map final scoring (4,250 searches if 9 train/4 holdout cells).
Use measured G4 seconds at the inner cap and a 2× slower-candidate allowance, plus
measured final-scoring cost and worker overhead, before admitting C. Whole blocks
only; deadline-induced missing blocks always produce unresolved, not a negative result.
C parent-ranking diagnostic compares the four selected parents' original scores to
scores on the next generation's shared fresh 24 training seeds, *within* generation.
Use average ranks; undefined if fewer than three candidates or fewer than two distinct
scores in either vector. Report individual generation correlations and their median;
do not correlate all generations pooled. Learning is a cost/signal pilot only.

Outcome interpretation (proposal Table A, first matching row)

U: failed/incomplete validation or screen, fewer than 50 seeds anywhere, or incomplete
started C scoring => unresolved; report finished work and re-plan missing parts.
1: either family lacks a split => reject only this bank under this split rule; report
obstacles, alias witnesses, full B calibration and descriptive intervals. The predicted
BE failure does not make this approved screen/calibration infeasible and is not grounds
to stop before B. Learned specificity/capacity remain unanswered. Strategy may weigh
training-only BE or its single role-covered holdout; neither runs here.
2: splits pass, headroom fails => fails the frozen 4,096-evaluation headroom rule;
no claim that improvement is impossible.
3: splits/headroom pass but tractability/cost fails => skip C, report measured cap/cost
needed; strategy decides next.
4: C completes and at least one trajectory per family has fresh-training gain CI lower
bound >1 => provisional go to slot 7 subject to strategy review.
5: C completes and a family has no resolved training gain => learning not demonstrated
at this budget; specificity/capacity remain unresolved.

Independent descriptive Table B, separately per family and marginal pair:
W if matched/swapped speed-ratio lower bound >1 (large if estimate >=1.5);
else C if either arm >25% capped; else B if upper bound <1.25; else X unresolved.
W in one family means matched-prior advantage on that family's tested cells; opposite
matched advantages in both establish crossed preference. W in contextual grammars but
not marginals alone does not attribute the advantage to context. Report both intervals
and the directly seed-paired difference of log contrasts / ratio of ratios. Any context
attribution requires that direct contrast's lower bound >1. These diagnostics gate nothing.
All intervals are descriptive feasibility/pilot readouts, with no confirmatory p-value
or promoted mechanism claim. A perfect/fast calibration would indicate a ceiling and
be evaluated by the frozen headroom rule; cap saturation is censoring, not incapacity.

Critique disposition

Notes 1–4 are incorporated above: explicit full C cost including initialization/scoring,
slower-map allowance, limited pilot scope, paired context-minus-marginal contrast,
crossed-preference wording, narrow headroom language, KM bounds and within-generation
ranking. Notes 5–8 concern historical belief files; the researcher is prohibited from
editing those files and will leave them to the steward. No code_review.md or
 driver_feedback.md was present at planning time.

Smoke and handoff

Rebuild Rust in the worktree venv, run relevant engine/screen/decoder tests, a reduced
end-to-end runner smoke, and timed FIRST calibration searches including hard cells.
If those demonstrate the approved design cannot run (validation irreparable, targets
unreachable, or measured cost far outside budget), write infeasible.md with measured
numbers, commit and stop. Otherwise write the full one-entry queue and commit code
plus task artifacts; do not execute the full queue as researcher.

Implementation details fixed before the full queue

- Tied marginals use the exact expected emitted-token proportions over all 32
  positions under iid uniform alleles, including the start row. Stable largest
  remainder assigns the 24,000 alleles (error <=1/24,000 per token). This implements
  the frozen tied-marginal controls without Monte Carlo error; empirical smoke
  checks confirm their emitted frequencies. Tables and SHA256 hashes are saved in
  maps.json before screening or search. The new modules are four_reducer_bank.py,
  four_reducer_maps.py, four_reducer_run.py and four_reducer_report.py.
- The 0132 final-parent selection uses 20 fresh seeds per training cell on each
  of four parents. C's complete projection includes these additional searches
  (1,440 if nine training cells), initialization (384 searches), 38,400 generation
  searches, and 4,250 final-scoring searches. Inner cost is the worst cell's measured
  G4 mean to 65,536, including capped runs; final cost uses the worst cell's measured
  full-cap mean. Both receive 2× slowdown allowance plus 25% worker overhead.
- Learning seed namespace: trajectory seed ×10,000 + generation ×100 + draw index;
  24 draws per candidate, cyclically distributed over its training cells, with the
  cycle rotated by generation. All candidates within a generation share assignments.
  Final parent selection uses trajectory seed ×10,000 +5,000+[0,19]. These namespaces
  are disjoint from B and fresh final scoring. No holdout score selects a map.
- First-block projected overrun permanently excludes C for cost; B continues in
  balanced blocks until the deadline. A final projection is also required to admit C.
  U precedence includes missing/duplicate calibration seed IDs and incomplete C.
