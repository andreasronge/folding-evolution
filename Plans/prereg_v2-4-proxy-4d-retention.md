# Pre-registration: §v2.4-proxy-4d — direct edit-distance-2 retention measurement across the three seeded cells

**Status:** QUEUED · target commit `TBD` (will be recorded post-infra-extension) · 2026-04-17

## Relationship to prior work (not a supersession)

§v2.4-proxy-4b (commit `f10b066`, chronicle `cac7537`) and §v2.4-proxy-4c
(chronicle `cd98520`) pre-registered the **edit-distance-2 retention rate
`R_2`** as the full-population retention metric. At chronicle time, `sweep.py`
produced only per-generation aggregate stats, so the reported retention was an
**exact-match upper bound** `R_exact ≤ (pop − unique_genotypes) / pop`
inferred from `history.npz`. The bound landed below the PARTIAL floor
(0.036 / 0.04) — a low-value bound is conclusive for the prereg's direction,
*but the prereg's committed metric remained unmeasured*. Methodology
principle 25 (measurement-infrastructure gate) was violated at prereg time
on those three sweeps; §v2.4-proxy-4d is the infrastructure fix that
discharges the commitment.

This prereg does **not** supersede §v2.4-proxy-4b/4c. It closes the
measurement gap they left open. If `R_2` is consistent with the exact-match
bound, the prior interpretations stand. If `R_2` is large (a near-canonical
edit-distance-2 shell exists), the prior interpretations need revision —
which is why this experiment is worth running despite the strong
aggregate-stats prior.

## Question (one sentence)

Across the three §v2.4-proxy-4b/4c seeded cells (BP_TOPK preserve, Arm A,
consume) at `seed_fraction=0.01` on `sum_gt_10_AND_max_gt_5` natural
sampler, what is the directly-measured edit-distance-2 retention rate
`R_2` in the final population at gen 1500, and does it satisfy the
original preregs' PASS/PARTIAL/FAIL criteria or remain below floor?

## Hypothesis

Strong prior for `R_2 < 0.05` in all three cells (erosion reading):
`final_mean_fitness = 0.845` at gen 1500 is inconsistent with a large
edit-distance-2 shell around canonical (whose fitness is ≥ ~0.95 for
edit-distance-1 mutants that don't break the active program, and 1.0 for
exact canonical). A population mean that low can only coexist with a
retention shell if the shell is a small fraction of the population.

**Three non-overlapping readings:**
1. **Erosion confirmed.** `R_2 < 0.05` in all three cells. The
   exact-match upper bound was tight; direct measurement just closes the
   gap. Prior §v2.4-proxy-4b/4c interpretations stand; mechanism
   narrowing of `proxy-basin-attractor` (broad F/R dissociation) is
   reinforced by a direct measurement.
2. **Near-canonical shell exists.** `R_2 ≥ 0.3` in ≥1 cell despite mean
   fitness 0.845. Would indicate a bimodal population with a tight shell
   of edit-distance-1–2 near-canonical bodies plus a larger erosion
   tail. Would narrow the F/R-dissociation claim: the dissociation is
   specifically between exact-match retention and best-of-run F, not
   between shell-level retention and F. Mechanism reading pivots toward
   "canonical is locally stable but its 1-bit-mutation neighbours look
   like canonical to a permissive classifier."
3. **Partial shell.** `R_2 ∈ [0.05, 0.3)` in ≥1 cell. Original PARTIAL
   row is satisfied for that cell. Modest shell exists; interpret
   descriptively.

## Setup

- **Infrastructure changes (see principle 25 block below):**
    - Add `dump_final_population: bool = False` to `ChemTapeConfig`. Included
      in hash when `True`, excluded at default (preserves existing cached
      hashes). Per [feedback_pyo3_optional_defaults](MEMORY) pattern —
      additive, backwards-compatible.
    - Extend `EvolutionResult` with `final_population: np.ndarray | None`
      and `final_population_fitness: np.ndarray | None`, populated only
      when the flag is set (shape `(pop_size, tape_length)` / `(pop_size,)`).
    - Extend `run.py::execute` to serialize `final_population.npz`
      (populations + fitnesses, uint8 + float32) into the run directory
      when present.
    - Write `experiments/chem_tape/analyze_retention.py` — post-processor
      that reads `final_population.npz` across a sweep directory, computes
      `R_k` for `k ∈ {0 (exact), 1, 2, 3}` against the canonical 12-token
      body, and emits per-seed × per-arm CSV + summary JSON.
- **Sweep files:** reuse with a new name to get fresh hashes:
    - `v2_4_proxy4d_bp_topk_preserve.yaml` (same as 4b + `dump_final_population: true`)
    - `v2_4_proxy4d_arm_a.yaml` (same as 4c Arm A + flag)
    - `v2_4_proxy4d_consume.yaml` (same as 4c consume + flag)
- **Arms / conditions:** per sweep, 3 seed_fraction arms {0.0, 0.001, 0.01}
  × 20 seeds = 60 configs. Only the `seed_fraction=0.01` arm enters the
  confirmatory R_2 test (the other two arms are baseline sanity checks
  for drift replication vs §v2.4-proxy-4b/4c).
- **Task:** `sum_gt_10_AND_max_gt_5` (fixed, natural sampler — identical to
  4b/4c).
- **Seeds:** 0–19 (same as 4b/4c).
- **Fixed params:** pop=1024, gens=1500, v2_probe alphabet, tape_length=32,
  `disable_early_termination: true`, canonical seed tape hex
  `0201121008010510100708110000000000000000000000000000000000000000`.
- **Est. compute:** ~15–25 min wall per sweep at 10 workers (same as 4b/4c);
  total ~45–60 min. Engineering: ~45–60 min prior to compute.
- **Related experiments:** §v2.4-proxy-4b (R_exact ≤ 0.036 bound), §v2.4-proxy-4c
  (Arm A + consume, R_exact ≤ ~0.04).

**Principle 20 audit:** label function, sampler, and input distribution
identical to §v2.4-proxy-4b/4c. No sampler change.

**Principle 23 declaration:** all three sweeps run as one batch after the
infra extension is merged. Each sweep is a measurement-only replication
of its predecessor — no mechanism knob changes.

## Baseline measurement (required)

- **Baseline quantity 1 (drift check):** F_AND and final_mean_fitness at
  `seed_fraction=0.0` per sweep — must match §v2.4/§v2.12/§v2.14b
  (0/20 solve) and §v2.4-proxy-4b/4c baseline arms.
- **Baseline quantity 2 (cross-sweep comparability):** final_mean_fitness
  and unique_genotypes at `seed_fraction=0.01` per sweep — must fall
  within ±0.02 / ±5% of the §v2.4-proxy-4b/4c values for the same cell.
  If either baseline drifts, the R_2 measurement is not comparable and
  the result must be re-scoped to the new commit's regime.
- **Anchor values (from prior chronicles):**
    - BP_TOPK preserve 4b: final_mean=0.845, unique=987/1024, F_2=20/20.
    - Arm A 4c: final_mean≈0.84, F_2=20/20 (exact digits in chronicle
      `cd98520`).
    - Consume 4c: final_mean≈0.84, F_2=20/20 (exact digits in chronicle
      `cd98520`).

## Internal-control check (required)

- **Tightest internal contrast:** R_2 across the three cells at fixed
  seed_fraction=0.01 — same task, same seeds, same canonical body, only
  decoder/executor varies. If R_2 is consistent across cells, the retention
  profile is a property of the canonical body × task pressure; if it
  differs, the dissociation has decoder/executor structure. This is the
  same internal contrast §v2.4-proxy-4c ran on F, now extended to R_2.
- **Are you running it here?** Yes, as the primary comparison.

## Pre-registered outcomes (required — grid across R_2 bins × 3 cells)

Per methodology 2b: the outcome table is a grid over the one measured
axis (R_2) × three cells. F is observed-frozen at 20/20 per cell; this
experiment does not re-measure F. We therefore enumerate outcomes over
the R_2 axis per cell, with a cross-cell summary row.

Let `R_2^{bp}`, `R_2^{armA}`, `R_2^{consume}` be the directly-measured
edit-distance-2 retention at `seed_fraction=0.01`, final generation.

| outcome (cross-cell pattern) | criterion | interpretation |
|---|---|---|
| **CONFIRM — erosion across all cells** | all three R_2 < 0.05 | Original §v2.4-proxy-4b/4c bound-based reading is directly validated. `proxy-basin-attractor` narrowing stands unchanged. No findings.md edit required beyond appending this direct-measurement anchor. |
| **NARROW — shell in ≥1 cell** | any R_2 ≥ 0.3 | A near-canonical edit-distance-2 shell exists in at least one cell. The F/R-dissociation claim must be narrowed: the dissociation is between **exact-match** retention and F, not between **shell-level** retention and F. Findings.md narrowing row edits required. |
| **PARTIAL — leaky shell in ≥1 cell** | any R_2 ∈ [0.05, 0.3) and no R_2 ≥ 0.3 | Modest shell in ≥1 cell. Original PARTIAL row of §v2.4-proxy-4b is satisfied for that cell. Report descriptively; cross-cell pattern determines follow-up. |
| **DIFFERENTIAL — cells diverge** | not all cells in the same bin above | At least two cells land in different R_2 bins (e.g., BP_TOPK < 0.05, Arm A ≥ 0.3). The retention regime depends on decoder/executor. Requires a cell-specific narrowing in findings.md. |
| **SWAMPED — drift check fails** | seed_fraction=0.0 solves > 2/20 in any sweep OR final_mean drifts > ±0.02 from 4b/4c anchor in any cell | Commit-level drift invalidates comparability. Re-run vs §v2.4-proxy-4b/4c at matching commit or isolate the drift source before interpreting R_2. |

**Threshold justification:** the `R_2 ≥ 0.3` bar matches §v2.4-proxy-4b's
original PASS-discoverability criterion (direct port). The `R_2 < 0.05`
bar matches the original FAIL-maintainability floor (direct port). The
PARTIAL bin `[0.05, 0.3)` matches the original PARTIAL-leaky row. Thresholds
are baseline-relative in that they preserve the original preregs' grid.

## Degenerate-success guard (required)

- **Classifier-permissiveness artifact (`R_2 → 1.0`):** if the edit-distance-2
  classifier admits bodies that are not canonical-equivalent (e.g., common
  NOP-tail variants whose active program differs from canonical but
  happens to sit within edit-distance 2 on the full 32-token tape),
  R_2 can read high without retention being real. **Detection:**
    - Define edit distance over the **active 12-token prefix only** after
      stripping trailing NOPs. Report `R_2_active_only` as the primary
      metric; include `R_2_full_tape` as a secondary sanity cross-check.
    - For any cell with R_2 ≥ 0.3, decode 10 random shell members and
      confirm they extract to the canonical program token-for-token
      under the `extract_bp_topk_program` function (for BP_TOPK) or the
      permeable-all view (for Arm A / consume).
    - If the shell is not canonical-equivalent under decode, reclassify
      the cell as ERODED with a classifier caveat.
- **Zero-retention artifact (`R_2 = 0` exactly):** could indicate (a)
  genuine erosion, (b) integer-overflow / indexing bug, or (c) the
  canonical body itself is missing from the final population even though
  the best-of-run is canonical. **Detection:** cross-check that `R_0` (exact
  match) equals the count of best-of-run canonical exact matches reported
  in result.json; if `R_0 = 0` but best-of-run-canonical count > 0, there
  is a bug in population-dump collection.
- **Seed_fraction=0.0 sanity:** all three sweeps' Arm-0 runs should show
  `R_2 < 0.005` (essentially zero, since canonical was never seeded). If
  `R_2 > 0.02` at Arm 0, the classifier admits false positives and must
  be tightened before interpreting Arm-2 results.
- **All degenerate-success checks must run before the chronicle is
  written**, not after.

## Statistical test (if comparing conditions)

- **Primary:** descriptive per-cell R_2 + 95% bootstrap CI over seeds.
  No p-value gate on R_2 directly — this is a closure measurement of an
  already-pre-registered metric. The confirmatory p-values already exist
  on the F axis (from §v2.4-proxy-4b/4c's McNemar tests).
- **Classification (principle 22):** **exploratory** — effect-size only.
  This prereg does not add a new confirmatory test to the proxy-basin
  family. It discharges a measurement obligation against existing
  confirmatory tests.
- **Current family size (proxy-basin family):** 3 (per `Plans/fwer_audit_2026-04-17.md`:
  §v2.4-proxy-4b + §v2.4-proxy-4c Arm A + §v2.4-proxy-4c consume). Corrected
  α = 0.05/3 ≈ 0.017. §v2.4-proxy-4d does not change this.
- **Justification for "no new p-value gate":** the prior confirmatory
  McNemar tests gated "does seeding canonical change F?" All three
  passed (20/20 vs 0/20). R_2 is the descriptive retention metric those
  preregs committed to measuring but could only bound. Closure
  measurement of a pre-committed descriptive metric does not require
  a new p-value.

## Diagnostics to log (beyond fitness)

- Final-generation full population (pop_size × tape_length, uint8) and
  per-individual fitness (pop_size, float32) — the raw data.
- `R_k` for `k ∈ {0, 1, 2, 3}` per seed per arm (edit distance over the
  active 12-token prefix). `R_0` is a hard cross-check against
  `unique_genotypes` from `history.npz`.
- `R_2_full_tape` as a secondary sanity metric (expected ≥ `R_2_active_only`;
  if lower, there is a definitional inconsistency).
- Distribution of edit-distance-to-canonical across the final population
  (histogram 0..32) per seed per arm. Picks up bimodality directly.
- Fraction of final-pop individuals with fitness ≥ 0.999 (near-canonical
  fitness) per seed per arm — `R_fit` as an orthogonal retention proxy.
- Per-seed × per-arm best-of-run canonical-exact-match rate (cross-check
  the "best slot is pinned at canonical" claim from the 4b/4c revision).
- Cross-sweep seed overlap on R_2 ≥ 0.3 (if any) — which seeds, if any,
  retain the shell under which decoder/executor.

## Scope tag (required for any summary-level claim)

**If CONFIRM (erosion):** `cross-decoder / cross-executor · n=20 per cell ·
at pop=1024 gens=1500 v2_probe disable_early_termination=true · on
sum_gt_10_AND_max_gt_5 natural sampler · direct edit-distance-2 retention
measured below PARTIAL floor · F/R dissociation validated by direct
measurement, not only by an exact-match upper bound`

**If NARROW:** `cross-decoder / cross-executor · n=20 per cell · at <regime
above> · shell exists in <which cells> · F/R dissociation restricted to
exact-match retention vs best-of-run — shell-level retention does couple
with F`

## Decision rule

- **CONFIRM erosion →** append a measurement-closure row to §v2.4-proxy-4b
  and §v2.4-proxy-4c chronicle entries (not supersession — annotation).
  Update `findings.md#proxy-basin-attractor` narrowing row to cite the
  direct measurement instead of the bound. Clear Task #20 (retention
  analysis) from the morning briefing. Natural next experiment:
  non-tournament-selection probe (the remaining single-knob question).
- **NARROW (shell in ≥1 cell) →** enter supersession mode on the
  F/R-dissociation narrowing in findings.md; narrow the claim to
  "exact-match retention dissociates from F; shell-level retention
  partially couples." Pre-register a follow-up to characterise the
  shell (composition, stability under further mutation). Hold the
  non-tournament-selection probe until the shell's mechanism is
  understood.
- **PARTIAL leaky →** descriptive-only chronicle update. No findings.md
  edit unless the cross-cell pattern is mechanism-revealing. Note in
  morning briefing.
- **DIFFERENTIAL →** cell-specific narrowing in findings.md. Queue an
  inspection experiment to characterise why the divergent cell differs.
- **SWAMPED →** isolate drift, re-run at matching commit. Do not update
  findings.md.

---

*Audit trail (principle gates):*

- **Outcome grid (principle 2, 2b):** five rows, grid over the measured
  R_2 axis across three cells. CONFIRM / NARROW / PARTIAL bins cover the
  R_2 range; DIFFERENTIAL handles cell-divergence; SWAMPED handles commit
  drift. No cell of the (R_2 bin × cell identity) grid is blank — all
  land in one of the five rows.
- **Baseline-relative thresholds (principle 6):** thresholds are direct
  ports of §v2.4-proxy-4b's original grid, preserving the prereg-level
  bins the original measurement could only bound.
- **Internal control (principle 1):** three-cell R_2 comparison at fixed
  seed_fraction=0.01 is the tightest internal contrast available.
- **Degenerate-success (principle 4):** classifier-permissiveness,
  zero-retention bug, Arm-0 classifier-false-positive — all enumerated
  before running.
- **Principle 20 (sampler audit):** not triggered. Task, sampler, label
  function unchanged from §v2.4-proxy-4b/4c.
- **Principle 22 (FWER):** classified exploratory; does not grow the
  proxy-basin family. Justification given above.
- **Principle 25 (measurement-infrastructure gate):** all metrics named:
    - `R_2_active_only` (primary), `R_2_full_tape`, `R_k` for k ∈ {0,1,3}:
      **state (iii) pending** — the `dump_final_population` extension
      + `analyze_retention.py` post-processor. Effort ~45–60 min. Committed
      to completing before the sweep runs; prereg is committed to
      `Plans/prereg_v2-4-proxy-4d-retention.md` at the same commit as
      the infra extension or earlier.
    - `final_mean_fitness`, `unique_genotypes`, `F_AND`: **state (i)
      produced directly** by existing `history.npz` / `result.json`
      pipeline.
    - `R_fit` (fraction with fitness ≥ 0.999): **state (i) produced
      directly** from `final_population_fitness.npz` after infra
      extension lands.
- **Decision rule (principle 19):** commits the five outcomes to
  specific downstream actions including findings.md edits, follow-up
  preregs, and the non-tournament-selection gating question.
