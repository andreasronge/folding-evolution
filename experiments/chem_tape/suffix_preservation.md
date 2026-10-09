# Chain-block boundary preservation (1606)

Approved design: `research/runs/2026-10-09-1606/proposal.md` in the main checkout.
Run `python -m experiments.chem_tape.suffix_preservation_run --prepare --workers 10`
with a fresh `RUN_DIR` and `RAYON_NUM_THREADS=1`. Scoring requires
`--preparation <prepare-output>/preparation.json`; `--validate-preparation`
checks the complete handoff and repeats the 32 timing searches without efficacy
scoring. The task queue fixes deadlines and output locations.

R uses the same `BlockOperator` as W, including the empirical library-derived
length distribution, uniform legal starts, C-chain token proposals, ordinary
variation, separate `[search_seed,4]` RNG, conditional uniform allele encoding,
and exclusion of the two elites. At the next allele only, R selects the token
that the original allele decodes to under the new final block token, and
refreshes within that token's interval. W selects the original decoded token
instead. R leaves the later alleles untouched; their decoded tokens may change.
R counts changes by decoding the resulting child, including the entire suffix.
Historical W's change counts are inside-block counts, with zero suffix changes.

Preparation SHA-checks the saved 1036 full roster, byte-pinned historical
results/configuration/freezes/libraries/laws, and the existing exact C source.
It verifies full roster metadata and replays one primary W/C search per corpus
(scientific payload, solver, curves and operator statistics; timing excluded).
If any scientific replay differs, the entire historical reference is dropped:
new W/R paired primary seeds are used, with no holdouts or paired C. The fixed
32-search timing smoke covers every primary cell and all corpora at 10 workers.
The full paired mode scores 4,096 primary plus 1,024 holdout R searches; fallback
scores 8,192 primary W/R searches. Admission estimates measured concurrency,
uses 15% margin, conservatively costs holdouts at primary mean, reserves handoff
replay/reporting time, and never changes sample size in response to outcomes.

The 10,000-edit audit deliberately includes tape ends, neutral blocks and
unchanged final block tokens. Its histogram includes those controls and should
not be read as a natural proposal distribution. Scored R diagnostics report the
natural distribution. Same-input W/R invariants do not imply identical block
contents after their search trajectories diverge.

Only complete rosters produce a report. W/R > 1 favors repair; unsolved cost is
2×cap, equal-weight corpus mean paired log costs, 95% t interval (15 df). Ordered
rules and descriptive sensitivities are in `suffix_preservation_report.py`.
An unresolved result retains incumbent repair and prices a conditional ×1.05
resolution study without authorizing it. Used banks support a boundary-policy
mechanism study; no transfer, acquisition, modularity or sole-cause conclusion.
