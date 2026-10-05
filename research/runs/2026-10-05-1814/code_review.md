---
verdict: pass
---
# Code review — 2026-10-05-1814 (INPUT/GT versus residual vector, 2×2)

Reviewed `462d8b2..31d4408` in the worktree, plus proposal.md, critique.md, plan.md,
queue.yaml and precision.json. The worktree is clean at `31d4408`, and its plan.md and
queue.yaml are identical to the task-folder copies.

## Blocking issues

None.

## What I checked

1. **Arm wiring.** I rebuilt all 8 vectors from `evolve_bias_vectors.json`. Ids 1 and 8 are
   INPUT and GT in the alphabet. X is the other family's fit (max-fit on sum2, sum-fit on
   max2), the same vector as 1705's `mismatched` arm. IG takes X's two values and spreads the
   rest evenly (0.0374 / 0.0361 per op). R keeps 1/22 on the two and scales X's other 20 to
   total 20/22. All sum to 1. `op_weights` feeds both initialization and mutation
   (`cfg.op_probs`), so the coupling is as stated.
2. **Seeds.** Main labels are `202610051814 + 100000 + i`. Training and evolution streams are
   named by task and seed, not arm, so all four arms in a task share the training set and
   evolution seed (the intended pairing), and the tasks get different streams. The 250
   evolution seeds per task are unique. The new master enters every stream, so nothing
   overlaps 1705. Bootstrap seeds are distinct for the 10 contrasts.
3. **Diagnostics do not move the endpoint.** I re-ran 24 archived 1705 main runs (old master,
   `uniform` and `mismatched`, both tasks, 6 seeds each) with `component_diagnostics=True`.
   All 24 reproduced the archived event time and solver genome exactly. These are runs whose
   outcomes were already known; I ran no new arm and no new seed.
4. **Statistics and labels.** `compare` draws the same resample indices for both arms, treats
   censored medians as an unbounded envelope and never drops them. `labels_for_task` and
   `closure` match the plan's tables: strict 1 and 1.5 boundaries, "carries" needs within and
   faster, "falls short" needs the lower bound above 1.5, X must replicate, and 09 closes only
   on the same non-empty carrying set in both tasks. Alpha is 0.005 across exactly 10
   contrasts, one look. The 24 new tests pass.
5. **Missing data.** A deadline in sampling or in any run sets `incomplete`, skips COMPLETE and
   exits 1. Comparisons with an incomplete cell return no estimate, so no label can form from
   partial data. No silent fallback found.
6. **Runtime.** The 24 full-size runs above took 34 CPU-seconds in total (max 4.7 s per run).
   2,000 runs are therefore well under an hour of CPU on 4 workers; with about 15 minutes of
   sampling the 9,000 s compute deadline and 3 h timeout have a wide margin. The queue command
   runs from the worktree root, where `.venv` exists.
7. **Critique.** It recommended approve. Its cautions (closure means only the bounded
   component question, "carries" on max2 is not most of the gain, sampling intervals including
   1 are not equal rates, n frozen on old data with a 350 maximum, power is per comparison)
   are each carried into the plan's disposition section and into the report text.

## Minor notes (not blocking)

- **Decoder has no memo.** `decode` recurses over every simple call path, so a genome with
  many same-tag runs full of RECVs would take very long (a hand-built 8-run × 7-RECV tape did
  not finish in 20 s). It runs after `result.json` and `comparisons.json` are written, so the
  numbers would survive, but report.md and COMPLETE would not. On 161 real shortcuts from the
  reproduced runs the worst case was 7 runs, 4 sharing a tag, 2 RECVs, and 0.1 ms per decode,
  so I judge the risk small. If the entry times out after `result.json` exists, analyse from
  `result.json` and treat it as a decoder failure, not missing data.
- **Sum2 precision passed narrowly.** The chance of resolving a 2.25× slower arm as "short"
  is 0.815 with a Monte Carlo interval of 0.754–0.866. It passes the frozen rule on the point
  estimate; the true value may be under 80%. An "unresolved" label on sum2 should be read with
  that in mind.
- **An arm slower than U can only come out "unresolved".** If IG or R solves under about half
  its seeds by the cap, its bootstrap medians are often infinite, the C÷X interval is
  unreliable, and "falls short" cannot be reached. This is conservative and pre-registered;
  the analysis should report solve rates beside such a label.
- **Saved shortcuts are the first 20 distinct per run**, so they over-represent early
  generations. In the reproduced runs, max2 runs saved none and several sum2 runs hit the
  limit. Shortcut summaries are descriptive only, and uneven across tasks.
- **U and X sampling rates are historical** (1558 counts, screened on a different training
  set). The screen is only a prefilter before exhaustive validation, so the counts are
  comparable; the report labels the provenance.
