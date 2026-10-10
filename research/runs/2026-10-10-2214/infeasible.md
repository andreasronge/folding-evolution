---
status: infeasible
next: strategy
targets_scored: false
---

# Initialization gate failed; return to steward

Implementation commit: `3e961ad` on `research/2026-10-10-2214`. Only experiment
code and tests are committed; task files remain in the main checkout as required.

The approved ramped half-and-half initialization at depths 2–4 cannot be filled
practically under the 32-compiled-token bound **with the frozen convention of
depth measured in edges, uniform functions/terminals, and resampling the same
full/grow bin**. This is an initialization obstruction, not unreachable targets
or evidence about the relative merits of A8 and tree search. The proposal did
not specify whether depth counted edges or levels; plan.md resolved that before
execution. A different convention or size-aware initialization needs an explicit
re-plan; I have not silently changed it after the failed check.

## Measured obstruction

Reproducer: `RUN_DIR=<fresh output directory> RAYON_NUM_THREADS=1 .venv/bin/python
-m experiments.chem_tape.tree_gp_validate` in the task worktree. Fixed seed
22160000, P256. Raw measurements: [smoke/validation.json](smoke/validation.json),
initial check [smoke/initialization.json](smoke/initialization.json).
The clean committed implementation is reproduced in
[smoke-committed/validation.json](smoke-committed/validation.json); timing values
in the table below are the first measured validation, not averages across repeats.

The population initializer failed in its full depth-4 bin after 10000 draws,
in 0.346 seconds. Independent fixed-seed batches:

| Full depth (edges) | Accepted / draws | Rejection | Min / median / max compiled tokens | Batch seconds |
|---|---:|---:|---|---:|
| 2 | 10000 / 10000 | 0% | 7 / 11 / 22 | 0.062 |
| 3 | 7182 / 10000 | 28.18% | 16 / 27 / 52 | 0.147 |
| 4 | 0 / 10000 | 100% observed | 35 / 64 / 130 | 0.347 |

Zero observed accepts alone is not proof of zero probability. The exact
generating-function calculation from the frozen grammar gives depth-4 acceptance
probability **1.2056525693407918e-7**, or one accept per **8.29 million draws**
on average. This is checked against the analytic enumeration in the test suite.
Terminals have length1 with probability4/9 and length2 with probability5/9;
each full level applies `z*(2*P(z)^2+P(z)^3)/3`. Binary full depth4 already has
31 nodes, so only exceptional almost-all-constant trees fit. A 10000-draw bin
has only **0.1205%** probability of yielding even one acceptable tree.

At measured single-process throughput, an accepted depth-4 tree would take
about **288 seconds** in expectation. The balanced P256 population requires
**42** such full-depth-4 trees: about **3.36 worker-hours of initialization per
search**, before evaluation. This is an extrapolation from the exact acceptance
probability and measured sampling rate, not an executed unlimited retry. Even
tenfold sampling acceleration would leave initialization far outside the
proposal's ≤51-second failed-search assumption. Keeping bounded retries instead
leaves the initializer unable to populate its specified bins. Stage 0's timing
and validity prerequisites therefore cannot pass as frozen.

## What passed, and what did not run

- All **16** target canonicals compiled unchanged to **16 primitive tokens /
  10 tree nodes**, matching exact D625 labels in the independent recursive
  interpreter, Python VM and production Rust VM. Fixtures were never searched.
- **1998** generated-tree/subtree-exchange checks passed independent/Python/Rust
  semantics on ordinary and missing-readout inputs. Rust wrapping overflow was
  checked separately against the independent interpreter, including an explicit
  `INT64_MAX + 1` fixture. Python's arbitrary-width arithmetic is not used as
  the overflow oracle.
- Size rejection reverted to parent1 as specified. Conditional order, closure,
  malformed-prefix rejection, two-token readout cost and exact polynomial
  probability have three passing focused pytest tests; Ruff passed.
- Saved bank/cohort/source-membership and production-method provenance checks
  passed through the existing `load_saved()` audit.
- **Not run:** 16 native search replays, 256 calibration searches, search replay,
  sustained-concurrency full-cap timing, 1792 target searches, uncertainty and
  repayment reports. The initialization obstruction precedes these gates.
  The implemented search loop is reusable code but has not passed a complete
  search smoke because the approved initializer fails before generation zero.

## What would work instead (for steward approval)

Keep the grammar, token cap, comparisons and samples; explicitly use depths
**2–4 levels (1–3 edges)** for ramped half-and-half, or choose full depths **2–3
edges** with grow allowed through4. The measured full-depth-3 acceptance is
71.82%, and full-depth-2 acceptance100%; all roster targets already fit the cap.
Either alternative resolves the measured initialization obstruction, but changes
the frozen initialization and still needs the approved semantic/search replay,
calibration, precision and sustained-concurrency gates. A size-aware full-tree
sampler is another possible re-design, with its changed prior disclosed.

Increasing retries would be unaffordable and would produce an almost-constant
full-depth-4 bin; increasing the token cap would change the procedure comparison.
Neither is a justified silent repair. No mix was selected, no queue.yaml was
written, and no efficacy/acquisition claim is made. This follows the user-required
infeasibility stop rather than preparing a queue whose admission cannot pass.
