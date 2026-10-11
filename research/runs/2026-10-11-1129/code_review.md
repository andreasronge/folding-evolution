---
verdict: pass
---

# Code review — 2026-10-11-1129 order-helper acquisition probe

Reviewed `c4fa27d..db30b15` (order_bank.py, order_library.py, order_run.py, test_order_probe.py), proposal.md,
critique.md, plan.md, queue.yaml and the smoke artifacts. Ran the three test files named in smoke.md:
27 passed (15 + 12).

## Blocking issues

None.

## What was checked

- **Arm wiring.** `envelopes` maps R-tree → no library, R-order → the 12 frozen helpers, R-sum → the 1019
  `hand_prior` entries with their multiplicities, R-L/R-S → `libraries[build]['literal'|'semantic']`. Protected
  cells are refused; source-phase search is R-tree on the 24 `S:` cells only. Helper orientation matches
  stage 0 (`lo=(11,a,b,10,a,b)` is min, `hi=(11,b,a,10,a,b)` is max under `interpret`).
- **Seeds.** Score seeds depend on (cell, build, repeat, attempt) only, so the five arms are paired on
  identical seed schedules; `seed_audit` enforces exactly one job per arm per seed, source/score/smoke phase
  disjointness, and exclusion of the stage-0 seeds (7000–7799, 9000–9005) and saved historical schedules.
  The 63-bit SHA scheme is the one 1019 used.
- **R-S extractor matches plan.md.** Proper input-containing subtrees of any size, one count per solver per
  exact D625 vector, interpreter/VM agreement on every pooled form, observed-only representative by
  (nodes, canonical, prefix), recurrence ≥ 2 distinct cells, 3–9-node filter before the 16 cap, both
  `pooling_rank` and `uncapped_rank` recorded. R-L calls `tree_library.extract` unchanged.
- **Routing rule.** `summarize` implements the pre-stated rule (destination-needed helper included in ≥ 6/8
  builds and ≥ 50% of the positive geometric log gap, undefined when R-order shows no gap). It only labels
  a recommendation; nothing in the queue acts on it.
- **Stop rules that decide whether the main stage runs.** Bank admission (all 24 sources, ≥ 8 protected with
  ≥ 2 disjoint) is deterministic and passed in smoke with 54/54 cells retained, so it cannot stop the run for
  a stochastic reason. Internal deadlines (1170 s / 1770 s) fail the phase rather than shrink it; the
  conservative projection (all 192 learned jobs fully capped at the slowest observed rate, 90% utilisation,
  +50%) is 1577 s against 1770 s, and the realistic projection is 231 s. Sum of queue timeouts is 3000 s,
  within the 60-min probe limit.
- **Queue plumbing.** `run_queue.py` computes the date directory once per launch, so
  `$RUN_DIR/../2026-10-11-1129-prepare` resolves even if the queue crosses midnight. `load_prepared` re-derives
  freeze, schedules, audit and both libraries and compares digests, so a stale or edited prepare folder fails
  loudly.
- **Critique.** Notes 1–4 are addressed in plan.md and in code (explicit 8-attempt source budget, sustained
  throughput measured in throughput.json, executable R-S rule with filter-before-cap, geometric gap with
  undefined case, separate interpretations for size limit / crowding / unresolved). Notes 5–6 are digest
  wording outside the task folder; plan.md says why they are deferred to the steward. Acceptable.

## Minor notes (not blocking; for the analysis and the steward)

1. **Admission relaxes the existing screen's near-alias rule.** `order_bank.build` overwrites `retained` to
   exclude only exact ≤ 9-token aliases, whereas `screen_domain` (and the independent-input bank that used it)
   also excludes `domain_near_alias` at ≥ 80%. In the smoke bank all 12 `S:hi..+Xc` sources are flagged
   `domain_near_alias` (525/625 = 84%); under the old rule half the sources would have been excluded and the
   plan's "all 24 sources survive" check would have failed. The choice is recorded in `bank.admission`, is
   consistent with the proposal's wording, and no destination is flagged (max 375/625), so scoring is
   unaffected. smoke.md does not mention the 12 flags; the analysis should report them, and any later protected
   proposal should state which rule it freezes.
2. **Semantic pooling admits semantically constant classes.** "Contains an input" is syntactic, so e.g.
   `GT(X0, 5)` (always 0 on D625) pools every constant-0 subtree that mentions an input. In smoke this class
   ranked first in R-S (9 cells, 10 solvers) and took a cap slot. Faithful to the frozen recipe, and the
   diagnostics expose it, but when the analysis routes to explanation (c) "cap crowding" it should say what
   outranked the helpers (constants, small sums, comparators) rather than assume small sums.
3. **R-L helper diagnostics re-implement `extract`'s ranking** (`literal_ranked`) instead of reading the
   returned `literal_entries`. The logic matches today (same filters, counts, tie-breaks; smoke agrees), but a
   one-line cross-check that `included` ⇔ canonical present in `lib['literal']` would make the R-L column of
   `helper_build_counts` self-verifying.
4. **Smoke already hints at the likely outcome.** All 12 helpers had uncapped semantic ranks 18–30 and
   literal ranks beyond the cap in the single smoke build, i.e. explanation (c). One build is not evidence;
   just a reminder that the full run's descriptive routing should be reported as such and not promoted.
5. `methods()` hashes `order_*.py` twice (once via `method_hashes()`'s glob). Harmless.
