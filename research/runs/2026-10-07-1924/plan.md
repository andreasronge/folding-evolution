---
estimated_minutes: 80
---

Implement the approved 1924 proposal using the unchanged 1707 search, bank,
transition counter and fitter. This plan is written before experiments or smoke
checks. No Rust or search-engine changes are planned.

Conditions and fixed seeds

- Retain BE1–16 and PA1–16, without selecting parents by speed. Commit all saved
  C tables with SHA256 provenance and the 20 1707 GG replay rows. Before stage A,
  check every parent against its saved search-row table hash, replay all 20 rows
  identically except timings/metadata, and re-verify every saved solver tape on
  D1331. Verify new collection tapes independently on all 1,331 inputs too.
- A: 48 searches per own training cell under C (7,680). Fit C2 once from those
  tapes alone, rescaling each cell to 1,600 transitions and shrinking to G4 with
  alpha=50. Save T and K, but evaluate neither. Yield floor: 24/48 in each cell.
- B: C2 and C each receive the same 32 new seeds per own training cell (10,240).
  C: run both on all three withheld cells, 32 seeds each (6,144), whenever B
  completes. Fresh random populations; cap 524,288, population 256, length 32,
  64 training cases; unchanged engine and alphabet.
- D: collect 48 searches per own training cell under G4 and fit C-prime with
  exactly the same rule. Evaluate C-prime on B and C seeds. Admit either the
  complete 32-lineage roster, the fixed BE1–8/PA1–8 roster, or none. Collection
  has the same 24/48 yield floor. A control yield or validation failure aborts
  D, retaining valid primary results; all C-prime source attribution then
  remains unresolved. No replacement, shrinking roster, or speed-selected
  partial-lineage inference. Each control phase must finish the entire admitted
  roster before any inferential contrast from that phase is available.
- Use seed_for with its unchanged BASE: phase 10 for A, phase 11 for B,
  phase 12 for C, phase 13 for D collection. C-prime evaluations reuse phases
  11/12. Phases 14–16 remain reserved. These blocks are disjoint from 1707
  phases 0–5 and probe seeds 19,240,000+/19,340,000+. Smoke uses a separate
  base (+300,000,000), one parent per family, eight collection attempts per
  cell and two evaluation seeds; scientific cap retained, yield floor four.

Timing and admission

Use ten workers and RAYON_NUM_THREADS=1. Expected full queue is 75–80 min.
At planning time (19:48 Stockholm), about 157 min remain to the 22:25 owner
cutoff. Reserve 20 min after queue work for review/analysis. At actual submission,
log wall time and use the earlier of start+100 min and 22:05 Stockholm as the
work deadline, with queue timeout 6,660 seconds (1.85 h). Reporting gets the
remaining queue margin. Stage D admission requires remaining work time >1.25
its projection, testing full before half. Use historical G4 collection cost
2.08 worker-s/search and historical 1707 C evaluation worker-s/search, with
throughput measured over A–C. No fitness, yield or effect size gates admission.
Submission later than planned reduces the available work time automatically.

Measurements and interpretation

Log all parameters, seeds, case indices, table hashes, evaluations, solved flags,
worker/wall seconds, tapes, yields and distinct tapes under RUN_DIR. Report body
row entropy, previous-token mutual information and start-row top-token share for
C/C2/C-prime, and collection cost versus arithmetic C2-over-C savings and future
searches to break even. Parent evaluation expectations from 1707 are 5,077/5,120
training and 3,034/3,072 holdout solves (~99%); C2 rates are unknown and measured.
Small-scale smoke results only test implementation and feasibility.

Per lineage, average log2 cost within each cell then equally across cells;
unsolved cost = 2*cap. Training estimate equally weights BE and PA means, with
SE=0.5*sqrt(SE_BE^2+SE_PA^2), t df=15 (full) or 7 (half-control).
Holdouts average the three cells per lineage, t df=31 (full) or 15
(half-control). Both sides of C-prime contrasts use the same admitted roster.
Report ratios 2^(-delta) and 95% intervals, per-family C2/C descriptively,
C-prime/C replication contrasts, and observed precision / required independent
lineage n when unresolved. Partial controls retain raw descriptive data only.

Disjoint training outcome rows (in this order):
0: invalid A/B, any C yield below floor, validation failure, or incomplete B:
no comparison claim; measured infeasibility.
1: C2/C lower>1 and complete C2/C-prime lower>1: further training gain
attributable to this source-decoder procedure, including yield/diversity effects.
2: C2/C lower>1 otherwise: parent improvement; attribution unresolved.
4: C2/C upper<1: degradation at this one-step scope.
3: C2/C lower<=1<=upper<1.10: this refit's mean training increment is bounded
below 10%; no equality or general saturation claim.
5: otherwise unresolved; report independent-lineage sizing.

For each holdout contrast, lower>1 means transfer; upper<1 means harm;
lower<=1<=upper<1.10 bounds transfer below 10%; otherwise transfer is unresolved.
Missing/incomplete C also leaves transfer unresolved. Source-attributed useful
feedback requires row 1 plus BOTH holdout C2/C and C2/C-prime lower>1. A wide
holdout interval does not establish a training-only limit. A resolved C-prime/C
gain establishes fresh-control improvement, not that the parent was
unrepresentative. All outcomes return to strategy; no second refit is authorized.

Critique disposition

Notes 1–5 are implemented above: solve expectations, submission-based timing,
source-procedure scope, fixed complete fallback roster/df/failure handling,
conditional precision, and distinct harm/bounded/unresolved outcome language.
Notes 6–11 concern existing digest/question/analysis claims. The researcher role
forbids editing questions/, digest.md and briefs/, so those corrections are left
for the steward. This run will avoid the flagged equality, absence, mechanism,
generic-explanation, overfitting and first-token causal claims. No start-row
ablation or family-specificity test is added.

Implementation and smoke checks (after the plan above)

The committed replay contains 20 GG seeds for each of the two 1707 replay
cells, so validation runs all 40 rows rather than selecting 20 in total. All
scientific fields and returned solver tapes replayed identically; all 7,408
original collection tapes independently re-verified on D1331. The final
smoke completed all A–D phases in 85.6 seconds with ten workers: C collection
80/80 solves (80 distinct tapes), G4 collection 78/80 (78 distinct tapes),
minimum per-cell yields 8/8 and 7/8 respectively. Training C/C2/C-prime
solved 20/20 each; holdout C/C2/C-prime solved 12/12, 11/12, and 12/12.
All loaded/fitted tables validated. These are implementation/feasibility
checks only, with no scientific comparison claim. See prepare_checks.json
for output paths, hashes, timings, validation counters and test command.

Twelve scientific-invariant tests and Ruff checks passed. The queue loads
with scripts.queue_lib.load_queue, has one correctly prefixed ID, writes
under RUN_DIR, and its timeout sum is 6,660 seconds. The final preparation
is around 20:05 Stockholm: an 80-minute queue started soon after review
would end around 21:25; the 100-minute internal bound would end around
21:45. Actual submission time and the absolute 22:05 work cutoff are logged
and enforced in code, so review delays automatically reduce D admission.
No design infeasibility was found. No Rust changes or rebuild were needed.
