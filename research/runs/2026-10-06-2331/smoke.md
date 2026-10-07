# Implementation and preparation checks

Implemented the approved initialization-only intervention in the existing
`composition_search.search` loop. `Decoder.encode` draws independently from each
positive conditional interval; a ninth job field selects the source table and
whether to re-encode. GG/MM retain original alleles. Later search generations,
case/variation/selection streams, operators and exact verifier are unchanged.
Every row includes the complete generation-zero token-tape hash, source hash and
re-encoding flag. Search payloads still contain only target ID and labels.

`initialization_run` verifies frozen artifacts and labels, round trips, the
marginal allele-law diagnostic and historical reproduction before main search.
It runs one complete seed across all three cells/maps/arms at a time. The first
100 seeds include MMr; its failed 99% check stops expansion before seed 101.
Deadline partial rows remain on disk and are excluded from analysis. The report
uses the specified crossed map-within-family / whole-seed bootstrap, conditional
outcomes, negative-effect flags, per-cell/family/map summaries and t sensitivity.

Checks completed before writing the full queue:

- 40 directed encoding pairs × 10000 complete 32-token tapes = 400000 round
  trips, all exact; conditional interval bounds asserted for every draw.
- 1000000 self-encoded alleles each for G4, BE1, PA1. Chi-square p values
  .83223, .66271, .68267; all above the pre-stated .05/3 failure threshold.
- All 630 historical 2229 rows (21 tables × three cells × ten seeds) match
  evaluations, solved, curve, table hash and identity fields exactly. No mismatch.
- Small smoke: 486 searches on excluded seeds 9000023–9000024, all 20 maps,
  cap 8192, two complete paired blocks. All initial token-hash pairings passed.
- The final targeted existing/new suite passed all 55 tests, including 17
  intervention tests. A failed law check prevents seed 101, and deadline partial
  seeds are excluded. Engine, encoding, whole-seed
  covariance, outcome grid, reporting serialization and corruption checks covered.
- Full-sized synthetic reporting benchmark: 79200 rows, 20000 bootstrap
  replicates, main plus law report in 1.24 s, peak RSS about 363 MB. This is only
  an infrastructure benchmark; it contains no empirical mechanism evidence.
- Ruff and diff whitespace checks pass. Queue format validates; one
  18000-second entry, below the eight-hour sum cap.
  Python package and Rust extension both load from this worktree's environment.
  No Rust code changed. Smoke figures rendered and visually inspected.

The first smoke exposed a NumPy boolean at JSON serialization after searches
completed. It was converted to a native bool and guarded by a regression test;
the corrected smoke completed. Probe bookkeeping fields were also corrected:
the initial preparation config's `seeds` field listed the future main seeds even
though `probe_seeds` and every raw row correctly contain excluded probe seeds;
the final runner logs actual probe seeds. The probe field `cpu_search_seconds`
was a sum of per-search monotonic wall time, not measured process CPU time;
the final runner names it `sum_search_seconds`. Original artifacts are retained
with these corrections documented in preparation/provenance.json.

## Full-cap runtime repeat

The original proposal's scratch probe source/raw output was not located in the
task folder or searched temporary files. Rather than invent its provenance,
`initialization_run --probe` repeats its fixed BE1/PA4/PA9, three-cell, 25-seed
design: exactly 900 searches, excluded seeds 9000000–9000024, cap 524288, ten
single-threaded workers. Script, config, raw compressed rows, counts and timing
provenance are committed under this task's `preparation/` folder in the worktree.
Source references are independently pinned in `data/initialization_2331/`.

| Map | GG mean s (solves/75) | MM | MG | GM |
| --- | --- | --- | --- | --- |
| BE1 | 3.301 (70/75) | .452 (75/75) | 1.021 (74/75) | .626 (75/75) |
| PA4 | 2.085 (70/75) | .335 (75/75) | 1.251 (73/75) | .535 (75/75) |
| PA9 | 2.057 (70/75) | 1.551 (73/75) | 1.435 (73/75) | 1.291 (73/75) |

Probe wall time 124.59 s; sum of per-search wall time 1195.53 s. Historical
validation overlapped the early BE1 probe, increasing those timings; the forecast
retains them conservatively. The shared GG per-cell solves are 23/25, 23/25 and
24/25. Arm/map solve fractions range 93.3–100%, consistent with the proposal.

Forecast includes 1200 GG, 72000 map-arm, 6000 MMr and 630 reproduction searches.
Medians/effect estimates were not used to change the design. The worker-time
forecast is 76250 s; at the proposal's ×8.7 throughput plus reporting this is
149 minutes, 222 minutes with 1.5× slack. Observed probe throughput instead gives
135 minutes. MMr runtime is proxied by MM; full-grid seed barriers/stragglers
are covered by slack and the approved deadline, not directly measured here.
This remains feasible within the approved 270-minute internal deadline and
300-minute queue timeout; no redesign or infeasible.md is warranted.

## Queued checks and scope

The full MMr/MM search-law check is explicitly deferred to the first 100 main
seeds in the queue. Engineering checks above do not waive any queued gate.
No main seed or mechanism inference was run during preparation. Main attribution
still needs ≥200 complete seeds, concurrent GG solve fractions ≥85% per cell,
and a reproduced diagonal gain with lower 95% bound >log2(1.25). A failed gate
returns U; wide primary intervals return row 5. Both return to strategy.

Smoke data were generated while the implementation was uncommitted; their config
hash names the preregistration parent, not the final implementation commit.
The substantive search/encoding path is preserved in the final task commit,
and the full queue logs that reviewed commit at execution. No preparation result
is promoted to a scientific finding.

Commands used (each with a fresh RUN_DIR, RAYON_NUM_THREADS=1 and
OPENBLAS_NUM_THREADS=1): `initialization_run --smoke --workers 10
--deadline-seconds 900`, `--validate-only --workers 10 --deadline-seconds 900`,
and `--probe --workers 10 --deadline-seconds 900`, through this worktree's
`.venv/bin/python -m experiments.chem_tape.initialization_run`.
