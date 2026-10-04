# Implementation and smoke validation

Implemented `experiments/chem_tape/shared_arrival.py`; full run is queued, not
executed by the researcher. `queue.yaml` contains one entry, running this
worktree's venv with this worktree as cwd, with all outputs under `$RUN_DIR`.
No Rust changes or rebuild required.

The engine's reproduction function is reused without changing its RNG draws.
Its optional parent rows now identify the actual self-crossover parent, rather
than the unused selected mate; fresh random mates have parent index -1. Config
validation continues to prohibit engine-wide track_lineage for non-selected
mates; the new harness requests per-generation parent rows directly and tracks
its own bounded descendant flags. Original source seeds generate training cases;
continuation seeds affect only reproduction. Elite parentage and descendants
are included; verdicts exclude elite slots and require 20 exact individuals.

Stage 1 saves every offspring's parent row and classifications in compressed
per-source batches. Byte and semantic caches reject training failures before
exactness and knockout classification. Arrival JSONL preserves each occurrence,
including identical layouts; sampling is by occurrence, weighted by source
exposure/draws. Source-specific rates and contributions, mixture exclusions,
lineage survival, descendant shared share, total shared share, helper types,
interval-censored first absence, and source-aligned products are explicit.
Exact-shared absence can reverse through surviving non-shared descendants;
loss of all descendants is absorbing. Controls continue for the same horizon.

The optional five-source replay checks every history column, saved shared and
run census records, and the full final population before accepting a midpoint.
Midpoint census is bounded by the remaining side-check budget. Failure or
incomplete checking restricts scope to final populations. CI overlap does not
prove temporal equivalence. Missing historical exposure also prevents a whole
cohort exposure point estimate.

## Validation

- `RAYON_NUM_THREADS=1 .venv/bin/python -m pytest tests/test_shared_arrival.py tests/test_s32_mate.py tests/test_shared_helper.py -q`: 38 passed.
- Ruff checks on the harness, tests and engine passed.
- Two-source, 32-generation throughput pilot: 65,408 children, 31,864 from partly
  parents, 0 new shared arrivals, 12.19 seconds with two workers. This is smoke
  evidence only, not the experiment's rate estimate.
- Final two-source smoke: 8,176 children, 3,986 from partly parents, 0 new shared
  arrivals; all expected files generated, stage 2 correctly skipped.
- Fixtures exercise insert/control continuations and positive lineage census;
  no hand-built or foreign-genome controls are queued as research evidence.
- Full input validation: exactly seeds 0–49; 16 terminal target sources retained.
  Seed 23 has an unmeasured historical duration; the 15 known-duration sources
  contribute 21,257,600 historical offspring. See plan.md's dated amendment.

Smoke artifacts are in `/tmp/shared-arrival-2135/` and intentionally outside
full-run outputs. Queue metadata and manifest record the execution commit;
the smoke manifests record dirty implementation state and full_run_evidence=false.

Additional ancestry/regression check:
`tests/test_chem_tape_mapbias_step1_3.py`: 11 passed (49 targeted tests total).
Queue parsed successfully with `scripts/queue_lib.py:load_queue`; output plot
rendered and inspected, including explicit skipped-continuation panels.
