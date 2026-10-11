# Implementation and feasibility smoke

Implementation commit: `60ab766` on `research/2026-10-11-1228`. Worktree clean;
no `research/` files were included in the commit.

`order_cap_run.py` is the new prepare/score entry point. It reuses the 1129
engine, execution, exact-solver/restart validation and multiprocessing writer.
The only existing implementation changed is `order_library.build`: default
`cap=16` preserves R-S; `cap=None` emits the same ranked eligible pool in full.
The 1129 driver stays unchanged. A frozen copy of its bank and method freeze
lives in `experiments/chem_tape/data/order_cap_1228/`; bank digest is
`2fc0d88c67ae651cbf3b927ecdedcebdd60220e30307ed4f9aa2bb428803d74a`.
All old source hashes except the intended extractor change must match the
pilot. Rust binary identity across worktree installations is recorded in the
new freeze rather than required to match the pilot binary; every Rust source
hash must match. No Rust source was changed or rebuild needed.

Preparation logs source rows as they finish, retains failed sources, validates
the complete fixed source schedule, builds both libraries from each same
corpus, checks the exact first-16 prefix and all-eligible count, and verifies
every emitted representative occurs as a proper subtree in its own corpus.
Scoring reconstructs all libraries and checks method, bank, schedule, seed and
artifact hashes before any destination jobs. Workers receive only IDs and
labels; helper/canonical/role annotations cannot seed search. Analysis requires
the full paired grid and charges failures 524,288. Helper census is used only
for descriptive coverage after extraction. Both extraction passes and
preparation validation are included in reported worker acquisition cost;
replay-validation timing is separate. The report implements the plan's
decision precedence and 8,192 paired whole-build pooled-mean bootstraps.

Final smoke artifacts are [prepare](smoke/prepare-verified/preparation.json),
[libraries](smoke/prepare-verified/libraries.json),
[report](smoke/score-verified/report.json) and
[dynamics](smoke/score-verified/dynamics.png). They were produced from the
uncommitted implementation whose exact source and binary hashes are saved in
`method_freeze.json`; its reported git hash is the parent commit. Full queue
execution will record the implementation commit on a clean branch.

| Measurement | Final smoke |
|---|---:|
| Independent acquisitions | 1 |
| Source solves/jobs | 48/48 |
| Acquisition evaluations | 368,640 |
| Acquisition worker seconds | 21.389 |
| Source batch wall seconds | 6.244 |
| Entire preparation wall seconds | 7.202 |
| R-S/R-all library classes | 16/25 |
| Exact prefix and provenance validation | passed |
| Destination jobs | 48 (12 per arm) |
| Solves R-tree/R-order/R-S/R-all | 12/12, 12/12, 12/12, 12/12 |
| Destination batch wall seconds | 17.491 |
| Mean worker-s R-tree/R-order/R-S/R-all | 3.787 / 0.209 / 5.170 / 0.999 |
| Maximum destination job worker seconds | 16.824 |
| Protected searches | 0 |

The source build was approximately 1.83× the pilot mean evaluations and
1.88× its worker time; extrapolating even that smoke rate to 24 acquisitions
costs about 513 worker-seconds, comfortably inside the 20-minute preparation
timeout. Destination smoke rates are below the proposal's conservative
pricing. A single build is not a rate guarantee or an investment decision;
retain the 90-minute score timeout, fixed n and conservative expected 40-minute
queue estimate. No approved-design infeasibility was found.

During implementation, a test detected helper annotations in worker envelopes;
the new driver strips them before dispatch. The first score attempt correctly
refused provenance admission because an in-memory tuple grammar was compared
directly with JSON-reloaded lists. The check now uses canonical digests, and
the final preparation/score passed. Earlier `prepare`, `prepare-final`,
`prepare-reviewed` and failed `score-reviewed` folders are retained as scratch
smoke history, not full-run results. No experiment settings changed in response
to smoke outcomes.

Validation: 42 focused tests passed across `test_order_probe`, `test_order_cap`,
`test_tree_library`, `test_tree_gp` and `test_tree_hand`. The added tests cover
cap identity/all-eligible emission, census independence, source-only and empty
libraries, protected rejection, historical/full/smoke seed separation,
pooled-mean whole-build inference, incomplete/failure-cap rejection, threshold
precedence and preparation reload/tampering/failure refusal. Ruff and
`git diff --check` pass. Dynamics plot was rendered and inspected.

`queue.yaml` parses through `scripts.queue_lib.load_queue`; both commands pass
`bash -n`. Entries use this worktree's `.venv`, write all experiment outputs
under `$RUN_DIR`, and sum to 6,600 seconds (110 minutes). Internal deadlines
leave 30 seconds for shutdown. Full execution has not been started by the
researcher; the driver runs it after review. All critique notes are addressed
or explicitly deferred in [plan.md](plan.md).
