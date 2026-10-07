# Preparation validation

The approved design is implementable. The full experiment has not been run.
The queue has one four-hour entry, with a 3.8-hour internal deadline, adaptive
pair admission and the approved fixed search budgets. All critique notes are
addressed in plan.md and the implementation; no design changes were needed.

Validation command:

```sh
.venv/bin/python -m pytest -q tests/test_rank_one_learning.py tests/test_map_learning.py tests/test_crossed_learning.py
```

**26 passed in 23.05 seconds.** Ruff check and format checks passed on the
three new modules and the new tests. After the final timing comparison was aligned to Stage A’s operator/family grain, the ten new tests passed again in 10.32 seconds and the smoke below was repeated. Both Python and Rust imports were verified to resolve inside this worktree. Tests cover all twenty frozen map
reconstructions, sparse operators, unchanged context redraw, clipping and
post-clipping column means, signed covariance/nonnegative Gamma plug-in,
paired bootstrap reselection, both 4,040-search budgets, independent mutant
seeds, shared T/C streams, fresh pairing/completeness, prospective-pair/G4
reserves, slower-B projection updates, equal family weights, cost signs,
twice-cap censoring, and outcome precedence. The final report rejects missing,
duplicate and non-training rows and incomplete trajectory records.

Final smoke command:

```sh
RUN_DIR=experiments/output/2026-10-07/2026-10-07-0821-smoke-final .venv/bin/python -m experiments.chem_tape.rank_one_run --smoke --workers 10 --deadline-seconds 900
```

Completed in **33.76 seconds**: 1,344 calibration, 768 continuation, 96 final
selection and 100 fresh searches. Both families completed; both arms and token,
b and a operators were exercised. All twenty inherited maps reconstructed
exactly, and fresh validation passed with exactly 100 expected observations.
The smoke report correctly returns U because its budgets/caps and pair count
are diagnostic. The learning figure was visually inspected. Smoke seeds use a
separate +10,000,000 namespace and never influence full-run effort choice.

Fixed isolated throughput probe:

```sh
RUN_DIR=experiments/output/2026-10-07/2026-10-07-0821-probe .venv/bin/python -m experiments.chem_tape.rank_one_run --probe --workers 10 --deadline-seconds 900
```

576 searches on predetermined token and b mutants from BE9/10 and PA9/10:
384 at cap 65,536 and 192 at cap 524,288, in separate batches. This measures
feasibility only; Stage A is still responsible for full-run effort selection.

| Operator/family | 65k solves | 65k mean seconds/search | 524k solves | 524k mean seconds/search |
|---|---:|---:|---:|---:|
| Context BE | 91/96 | 0.428 | 48/48 | 0.772 |
| Token BE | 84/96 | 0.572 | 48/48 | 0.402 |
| Context PA | 90/96 | 0.539 | 48/48 | 0.860 |
| Token PA | 89/96 | 0.584 | 46/48 | 1.082 |

The 65k batch took 21.61 seconds, the fresh-cap batch 23.41 seconds. Slowest
65k group after batch overhead was 0.588 seconds/search: about 30 minutes for
A and 133 minutes for sixteen continuation pairs, under the assumption that
later maps have similar cost. The proposal's fresh projection scales to about
0.91 seconds/search; the directly measured fresh group means were 0.40–1.08.
These are modest samples, not a guarantee that sixteen pairs fit. Six pairs
per family remain plausible inside the deadline; actual A/B timings determine
admission, with fresh scoring reserved for the prospective pair as well.

An initial 144-search mixed-cap probe took 18.65 seconds. It gave an inflated
effective overhead factor of 2.08 because process startup and a small batch's
long unsolved tail left workers idle. Increasing this *timing probe* and
separating caps measured occupied-batch throughput without changing the
approved study. Both probe records are archived for transparency. The isolated
probe was run after the test process finished. An initial smoke caught a mean
effect implementation issue (partial-A diagnostic entered mu); it was fixed
and the final smoke/tests above passed against the corrected estimator.

Seed definitions in the existing 0132, 0811, 1603, 1723, 2229, 2331 and 0315
harnesses were inspected; the new 1,821,000,000–1,827,000,000 namespaces and
their smoke/probe offsets do not intersect their search blocks. Tests also
check that all 29,184 full calibration search seeds are mutually disjoint and
that continuation/final streams share only the intended T/C pairings.

Compact evidence is in [preparation/](preparation/): smoke configuration,
status, validation and report, a figure, isolated/initial probe measurements,
compressed raw smoke/probe rows, and file hashes. Raw working outputs remain
in the ignored worktree experiments/output directory. No finding, question,
digest or brief was changed, and no holdout score was loaded.
