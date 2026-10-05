The approved design is feasible at the measured scale. These are implementation probes,
not the 50-seed experiment or a transfer result. The full queue has not been launched.

- D1331, all 162 frozen cells, all executable prefixes through depth 9: 95.06 seconds;
  peak RSS 4686 MiB (4.58 GiB). Stored depth 8 has 12,284,368 states; output-only depth 9
  reaches 11,629 distinct output vectors. Canonicals and every best alias witness were
  verified against the production Rust executor on all 1,331 inputs.
- Retained counts on this domain: GA 0, BT 0, BE 2, PA 8, D1 3, D2 3. This probe does not
  substitute for the queued exhaustive three-domain screen or its frozen selection rule.
- Actual retained roster: 16 cells × 4 controls × 2 fresh paired seeds = 128 searches,
  P 256, full cap 524,288. Eight-worker block wall time 46.75 s; mean run time including
  capped runs 2.636 s. Nine runs were censored. U solved 28/32 (mean 4.662 s), F 30/32
  (2.346 s), G 32/32 (0.461 s), G-marg 29/32 (3.076 s). Two seeds do not establish rates
  for any individual cell; the queue recalibrates with ten balanced seeds on its selected
  roster before proceeding.
- Sampling, 100,000 genotypes per control on the retained D1331 roster: U 168,351/s,
  F 148,995/s, G 140,420/s, G-marg 141,483/s, with exact full-domain confirmation.
  Actual hits/denominators and seeds are in smoke_metrics.json. These throughput estimates
  are secondary; no precision claim is made for rare exact hits.
- End-to-end shallow-screen smoke on all three domains completed 48 full-cap searches
  across the six shapes in 60.33 s (62.69 s including setup and small sampling).
- An 8-second deadline smoke stopped during the first screen at 5.03 s, released its
  worker, wrote all required queue artifacts, and recorded incomplete/unresolved semantics.

On the measured retained roster, 50-seed B projects to about 19.5 minutes from block wall
throughput. Three serial screens project to about five minutes; a worst-case F top-up on
all 16 cells adds about nine minutes at the pooled rate. Sampling all four controls with
four simultaneous chunk jobs projects to about twelve minutes, with unused time available
for uncertainty/overhead and conditional C. The working estimate is 40–55 minutes, within
the approved 130-minute internal deadline and 150-minute timeout. Conditional C and actual
F requests are projected again from the first full balanced block; sampling is cut first.
There is no measured runtime, memory or target-execution obstacle requiring infeasible.md.

Validation: 23 focused tests passed, including raw Rust enumeration through depth 4 versus
the output-only screen, independent complete typed-stack checks on all three domains,
canonical execution, frozen-control hashes, shape/split selection, censoring and joint paired
bootstrap handling, both-shape outcome requirements, cost arithmetic, expanded-domain search,
and the existing composition tests. Ruff and git diff whitespace checks passed. Queue parsing
passed; one entry has timeout 9000 s, below the eight-hour aggregate cap. No Rust code changed.

Reproduce the feasibility probe from the worktree (about 2–3 minutes):

```sh
PYTHONPATH="$PWD" RUN_DIR="$PWD/experiments/output/assembly-feasibility-recheck" RAYON_NUM_THREADS=1 .venv/bin/python research/runs/2026-10-06-0001/smoke_benchmark.py
```

The committed smoke script recreates the serial D1331 screen, actual retained-roster
searches and throughput measurement. Raw implementation-probe outputs remain in
`experiments/output/assembly-feasibility/`, `assembly-smoke/` and `assembly-deadline-smoke/`;
smoke_metrics.json records the relevant numbers and raw SHA-256 hashes. The queue writes
fresh outputs under its own RUN_DIR and uses fresh full-run seeds.
