# Pre-registration: §v2.4-proxy-5b — `mutation_rate` sweep on BP_TOPK preserve + Arm A seeded cells (kinetic-vs-structural mechanism probe)

**Status:** QUEUED · target commit `TBD` · 2026-04-17 evening

## Supersession / upstream context

§v2.4-proxy-4d decode-consistent follow-up (commit `cca2323`) confirmed two decoder-specific mechanisms under the F/R dissociation header:

- **BP_TOPK (preserve + consume):** canonical off-center in a wide solver neutral network (R_fit ≈ 0.72; R₂_decoded ≈ 0.002 — structurally distinct decoded solvers).
- **Arm A:** classical proxy-basin population dynamics (R_fit ≈ 0.004; canonical elite-preserved only, non-elite sinks to proxy).

Both mechanisms were measured at `mutation_rate=0.03` (the project default). This prereg probes whether the two mechanisms are **kinetic** (erosion rate scales with mutation pressure; retention lifts at lower rates) or **structural** (rate-insensitive because decoder / selection geometry dominates the population distribution regardless of mutation kinetics). Different readings suggest different downstream directions: kinetic → robustness-to-mutation operators (lower mutation, repair operators); structural → representation-layer or selection-layer interventions.

## Question (one sentence)

Under `seed_fraction=0.01` on `sum_gt_10_AND_max_gt_5` natural sampler, does the decoder-specific F/R dissociation measured at `mutation_rate=0.03` scale with mutation rate — lifting `R₂_decoded` and/or `R_fit` at lower rates (kinetic mechanism), or holding rate-insensitive across `mutation_rate ∈ {0.005, 0.015, 0.03}` (structural mechanism) — and does the scaling differ between BP_TOPK preserve and Arm A?

## Hypothesis

Two competing readings per decoder arm × a cross-arm differential hypothesis:

1. **Kinetic under both arms.** Mutation pressure continuously drives canonical's neighbours off plateau; lower rates slow the drift proportionally. **Prediction:** R₂_decoded lifts monotonically as rate decreases in both arms (Arm A may lift more dramatically because its proxy-basin is selection-driven and mutation-enabled; BP_TOPK lifts more modestly because lateral drift across the neutral network is slower but the network is still structurally wide).

2. **Structural under both arms.** The decoder arm's geometry dominates — BP_TOPK's many-to-one decode creates the solver network regardless of mutation rate; Arm A's proxy-basin selection dynamics saturate non-elite slots regardless of how fast mutation happens, because selection pressure is what does the filling. **Prediction:** R₂_decoded and R_fit rate-insensitive in both arms.

3. **Decoder-specific (kinetic under Arm A, structural under BP_TOPK).** Arm A's proxy-basin erosion is classical mutation-rate-scaled (slow mutation → slow erosion); BP_TOPK's neutral network is decoder-structural (unaffected by rate because the many-to-one mapping is rate-independent). **Prediction:** R₂_decoded under Arm A lifts to ≥ 0.05 at mutation_rate=0.005; R_fit and R₂_decoded under BP_TOPK stay near their bp=0.5 mutation_rate=0.03 baselines.

Reading (3) is the most theoretically informative — it would cement the decoder-specific mechanism split as orthogonal to mutation kinetics, narrowing the §v2.4-proxy-4d decoder-split by a mutation-rate axis.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_4_proxy5b_mutation_rate.yaml`
- **Arms / conditions:** `mutation_rate ∈ {0.005, 0.015, 0.03}` × `arm ∈ {BP_TOPK preserve, A}` × `seed_fraction ∈ {0.0, 0.01}`. 3 × 2 × 2 = 12 cells.
  - BP_TOPK cells use `topk=3, bond_protection_ratio=0.5` (matches §v2.4-proxy-4b/4c/4d baseline).
  - Arm A cells use default `topk=1` (ignored for arm='A' execution; relevant only for the informational decoded-view column).
- **Seeds:** 0..19 per cell (disjoint-comparable with 4b/4c/4d).
- **Fixed params:** `safe_pop_mode=preserve`, `pop_size=1024`, `generations=1500`, `tournament_size=3`, `elite_count=2`, `crossover_rate=0.7`, `tape_length=32`, `alphabet=v2_probe`, `disable_early_termination=true`, `dump_final_population=true`, `seed_tapes="0201121008010510100708110000000000000000000000000000000000000000"`, `n_examples=64`, `holdout_size=256`, `backend=mlx`. Only `mutation_rate`, `arm`, and `seed_fraction` vary.
- **Est. compute:** 12 cells × 20 seeds. BP_TOPK cells: ~15 min/run; Arm A cells: ~7 min/run (per §v2.4-proxy-4d wall). At 10 workers: 6 BP_TOPK cells × 15 min + 6 Arm A cells × 7 min ≈ 45-60 min wall.
- **Related experiments:** §v2.4-proxy-4b (mutation_rate=0.03 BP_TOPK preserve baseline, commit `f10b066`), §v2.4-proxy-4c Arm A (mutation_rate=0.03 Arm A baseline, commit `9135345`), §v2.4-proxy-4d decode-consistent follow-up (commit `cca2323` — the mutation_rate=0.03 R₂_decoded + R_fit baselines this prereg anchors against).

**Principle 20 audit:** label function, input distribution, and sampler unchanged from §v2.4-proxy-4b/4c/4d. Only `mutation_rate`, `arm`, `seed_fraction` vary. Principle 20 not triggered.

**Principle 23 audit:** `mutation_rate=0.03` cells (both arms, both sf values) must reproduce §v2.4-proxy-4d numbers at the same commit — the baseline comparability gate. If they do not reproduce within bootstrap CI, investigate before interpreting the lower-rate cells.

## Baseline measurement (required)

- **Baseline quantity at `mutation_rate=0.03` × `sf=0.01` (principle 6 anchor):**
  - BP_TOPK preserve: `R₂_decoded = 0.0024` 95% CI `[0.0019, 0.0030]`; `R_fit_999 = 0.723`; `R₂_active = 0.0025` 95% CI `[0.0020, 0.0031]`. (§v2.4-proxy-4d decode-consistent follow-up, commit `cca2323`.)
  - Arm A: `R₂_decoded = 0.0046` 95% CI `[0.0036, 0.0056]` (informational; topk=1); `R_fit_999 = 0.004`; `R₂_active = 0.0053` 95% CI `[0.0043, 0.0063]`. (Same commit.)
- **Metric definitions (per principle 27, cited verbatim from `experiments/chem_tape/analyze_retention.py` METRIC_DEFINITIONS):**
  - `R2_decoded`:
    > Fraction of final-population tapes whose BP_TOPK(k=topk) decoded view — the exact token sequence passed to the VM under arm=BP_TOPK, computed as the top-K longest non-separator runs concatenated in tape order via engine.compute_topk_runnable_mask — is within Levenshtein edit distance 2 of canonical's decoded view. For arm=A runs this view is informational (the VM executes the raw tape), not execution-semantic.
  - `R_fit_999`:
    > Fraction of final-population individuals whose training-task fitness is >= 0.999 (near-canonical fitness proxy, independent of structural distance from canonical).
  - `R2_active`:
    > Fraction of final-population tapes whose permeable-all active view (non-NOP, non-separator tokens in tape order) is within Levenshtein edit distance 2 of canonical's 12-token active program. This view is a SUPERSET of the BP_TOPK(k) decode; active-view and decoded-view distances can disagree in either direction (Levenshtein is not monotone under the top-K-longest-run subsequence restriction).
  - `bootstrap_ci_spec`:
    > Nonparametric bootstrap over per-seed values: 10 000 resamples with replacement via numpy.random.default_rng(seed=42); 95% CI is the [2.5%, 97.5%] empirical quantile of the resampled means.
- **Drift-check expectation at sf=0.0:** F=0/20 at all three mutation rates, both arms (no solving without seed).

## Internal-control check (required)

- **Tightest internal contrast per arm:** `mutation_rate=0.005` vs `mutation_rate=0.03` at the same `sf=0.01`, same seeds, same commit. Within-arm comparison directly tests the kinetic-vs-structural reading for each decoder.
- **Cross-arm contrast:** under matched mutation_rate, compare R₂_decoded lift (vs mutation_rate=0.03 baseline) between BP_TOPK and Arm A. If lifts diverge, reading (3) — decoder-specific kinetic profile — is supported.
- **Are you running it here?** Yes, all six seeded cells span the internal contrast.

## Pre-registered outcomes (required — §26-compliant outcome grid, decoder-stratified)

<!--
Per methodology §26: grid every measured axis. Measured axes per-seed:
  - R₂_decoded (primary mechanism axis; decoder-specific meaning)
  - R_fit_999 (co-primary; decoder-level)
  - F_AND (solve rate; sanity)
Three readings per arm as the mechanism claims. Outcome rows are per-arm
because the two mechanisms are independent; cross-arm divergence becomes
its own named outcome.

R₂_decoded coarse bins: {low < 0.05 | mid 0.05-0.3 | high ≥ 0.3}
R_fit coarse bins:      {low < 0.3 | mid 0.3-0.7 | high ≥ 0.7}
F_AND sanity:           {20/20 | 15-19/20 | <15/20 SWAMPED}
-->

Outcome cells compare `mutation_rate=0.005` (slowest) against `mutation_rate=0.03` (baseline) at `sf=0.01`, per arm. `mutation_rate=0.015` is the interpolation point testing monotonicity.

### Per-arm outcomes

| outcome | arm | R₂_decoded at mr=0.005 vs baseline | R_fit_999 at mr=0.005 vs baseline | F_AND | interpretation |
|---|---|---|---|---|---|
| **A-KINETIC** | Arm A | ≥ 0.05 at mr=0.005 (monotone lift vs mr=0.03's ≈ 0.005) | any shift from baseline ≈ 0.004 | 20/20 | Reading (1 Arm A): Arm A proxy-basin erosion IS kinetic — slower mutation slows the sink. Robustness-to-mutation operators are live candidates. If R_fit also lifts substantially (> 0.3), canonical's basin is mutation-competitive; if R_fit stays low, erosion slows but canonical is still non-basin. |
| **A-STRUCTURAL** | Arm A | < 0.05 across all three rates | R_fit ≤ 0.05 across all rates (no lift) | 20/20 | Reading (2 Arm A): Arm A proxy-basin is selection-dominant; mutation rate is not the lever. Variation-layer interventions (repair, lower mutation) are the wrong direction for Arm A. Points toward selection-layer (ranking / Pareto) as the next probe. |
| **BP-KINETIC** | BP_TOPK | ≥ 0.05 at mr=0.005 AND R_fit ≥ 0.7 held | R_fit held at baseline ≈ 0.72 | 20/20 | Reading (1 BP_TOPK): the solver neutral network is stable in width but lateral drift is rate-scaled. Lower rate lets canonical persist longer in the cloud. The cloud structure is not itself kinetic, but retention *within* the structure is. |
| **BP-STRUCTURAL** | BP_TOPK | < 0.05 across all three rates | R_fit held within 95% CI of 0.72 across all rates | 20/20 | Reading (2 BP_TOPK): the wide solver network is structurally determined by the decoder's many-to-one mapping. Mutation rate doesn't shift its center. Representation-layer interventions (evolvable chemistry / AutoMap) are the right direction for BP_TOPK. |
| **DIVERGE** | both | A-KINETIC + BP-STRUCTURAL | ≈ as above | 20/20 | Reading (3 — decoder-specific kinetic profile). The strongest theoretically-informative outcome: mutation kinetics matter for Arm A's proxy basin but not for BP_TOPK's solver neutral network. Cements the decoder-specific mechanism split with a mutation-rate orthogonality claim. |
| **CONVERGE** | both | A-STRUCTURAL + BP-STRUCTURAL | baseline-rate-insensitive in both | 20/20 | Both mechanisms are structural under mutation rate. Variation-layer direction is retired for both arms; selection-layer and representation-layer directions are what remains. |
| **BOTH-KINETIC** | both | A-KINETIC + BP-KINETIC | both lift at mr=0.005 | 20/20 | Both mechanisms are kinetic; decoder-specific mechanism split remains valid at the structural layer but both decoders' retention lifts proportionally with slower mutation. Variation-layer direction remains live for both arms. |
| **SWAMPED** | either | any | any | F_AND < 18/20 at mr=0.005 | `mutation_rate=0.005` is too low to sustain the GA — 1500 gens of near-zero mutation starves exploration. Result uninformative for the kinetic question in the affected arm(s). Degenerate-success guard below specifies the unique_genotypes / exploration-failure conditions. |
| **BASELINE-DRIFT** | either | `mr=0.03` cell does not reproduce §v2.4-proxy-4d numbers | — | — | Commit-level drift between the 4d commit (`a8a1e6d`) and this sweep's target commit. Investigate before interpreting any other cell; no claim update until resolved. |
| **INCONCLUSIVE** | either | any pattern not fitting above | any | any | Per principle 2b, update the outcome grid before interpreting. |

**Threshold justification:** 0.05 floor is the §v2.4-proxy-4b PARTIAL floor (cross-sweep comparability); 0.3 is the PASS threshold (unused here — we expect even KINETIC outcomes in the 0.05-0.3 mid band rather than PASS-clean). R_fit 0.3/0.7 bins bracket the baseline BP_TOPK value (0.72) and provide clear separation from the Arm A baseline (0.004). 1500 generations at mutation_rate=0.005 corresponds to an expected ~7.5 mutations/tape total (vs ~45 at 0.03); this range was chosen so the low-rate arm is still performing search (not frozen) but at 1/6 the baseline rate.

## Degenerate-success guard (required)

- **Mutation-rate-too-low artefact (SWAMPED row):** at `mutation_rate=0.005`, the population may fail to explore enough genotype-space to solve even when seeded. Detection conditions:
  1. `F_AND` at `mr=0.005 × sf=0.01` must be ≥ 18/20 per arm; drops signal exploration failure.
  2. `unique_genotypes` at `mr=0.005 × sf=0.01` must exceed 500/1024 in each arm (baseline ≈ 987-1010/1024; drop to below 500 signals population freezing).
  3. `R₀_decoded` at `mr=0.005 × sf=0.0` (drift check) must remain at 0.000; a spike would flag seeding-leakage or infrastructure bug.
- **Arm A decoded-view interpretation artefact:** Arm A decoded-view (topk=1) is informational only; the primary Arm A signal is `R_fit_999` for mechanism reading and `R₂_active` for population-layer erosion. Do not promote any Arm A claim resting solely on the decoded column.
- **Cross-cell mutation-rate non-monotonicity:** if `R₂_decoded` lifts at `mr=0.015` but falls back at `mr=0.005`, that is an unexpected non-monotone signature — interpretation is `INCONCLUSIVE`, not KINETIC, pending investigation (likely a second-order interaction with selection pressure at very low mutation).

## Statistical test

- **Primary:** per-cell bootstrap 95% CI on `R₂_decoded`, `R₂_active`, and `R_fit_999`. Per-arm comparison uses paired McNemar on `F_AND` across mutation_rate values on shared seeds, gating the SWAMPED row at raw α = 0.05.
- **Classification (principle 22):** **exploratory.** Does not gate a new findings.md claim; informs the decoder-specific mechanism split already ACTIVE in `findings.md#proxy-basin-attractor`.
- **Family:** n/a (exploratory). Proxy-basin FWER family size unchanged at 3; corrected α stays at 0.05/3 ≈ 0.017.

## Diagnostics to log (beyond fitness)

- Per-seed × per-cell `F_AND`, `best-of-run` fitness (expected 20/20 and 1.0 respectively at sf=0.01)
- Per-cell `R₂_decoded`, `R₂_active`, `R₂_raw`, `R_fit_999`, `unique_genotypes`, `final_generation_mean` (via `analyze_retention.py`)
- Edit-distance histogram `{0, 1, 2, 3, ≥4}` active-view per cell
- Per-cell bootstrap 95% CI on all three R₂ views + R_fit_999
- Per-seed best-of-run hex at sf=0.01 per arm — confirm byte-for-byte canonical across all 120 seeded runs; deviations flag degenerate-success guard
- **Paired-seed R₂_decoded lift magnitude by arm at mr=0.005 vs mr=0.03** — the cross-arm divergence metric that resolves reading (3) DIVERGE vs reading (1)/(2)

## Scope tag (required for any summary-level claim)

**If this experiment's result enters a findings.md narrowing:**
`within-family · n=20 per cell (12 cells) · at pop=1024 gens=1500 tournament_size=3 elite_count=2 crossover_rate=0.7 v2_probe disable_early_termination=true · on sum_gt_10_AND_max_gt_5 natural sampler · BP_TOPK(k=3, bp=0.5) preserve + Arm A direct GP · mutation_rate ∈ {0.005, 0.015, 0.03} · seeded canonical 12-token AND body at sf ∈ {0.0, 0.01}`.

Not expected to broaden the top-line `proxy-basin-attractor` claim — this probe narrows the mechanism reading along a mutation-rate axis within the already-tested decoder-specific framing.

## Decision rule

- **DIVERGE →** update the `findings.md#proxy-basin-attractor` decoder-specific mechanism split to add a mutation-rate orthogonality note: Arm A's proxy basin is kinetic; BP_TOPK's solver network is structural. Cement the split as mechanism-layer (not just measurement-artefact). Move "variation-layer operators for Arm A" to live candidate, and "representation-layer operators for BP_TOPK" to the natural next direction. Queue an n=20 replication block on independent seeds (20-39) before paper-level citation.
- **CONVERGE →** both mechanisms are structural; update arc doc to close Open Q "is the dissociation mutation-kinetic?" with CONVERGE reading. Retire the variation-layer direction for both arms; prioritise selection-layer (non-tournament) and representation-layer (evolvable chemistry) directions. Plasticity probe (§v2.5-plasticity-1a) remains valid because its mechanism is phenotype-layer adaptation, orthogonal to the genotype-mutation-rate dimension.
- **BOTH-KINETIC →** both mechanisms respond to mutation rate; variation-layer direction remains live. Narrow the kinetic reading per-arm (magnitudes differ) and write up. Queue bp sweep (§v2.4-proxy-5a) to test whether bp and mutation_rate substitute or complement.
- **A-KINETIC / A-STRUCTURAL (without cross-arm coherence)** → interpret the Arm A mechanism alone; do not update BP_TOPK scope. Plasticity probe (§v2.5-plasticity-1a) prereg is the natural follow-up for the Arm A-specific mechanism.
- **BP-KINETIC / BP-STRUCTURAL (without cross-arm coherence)** → interpret the BP_TOPK mechanism alone. The "solver-neutral-network" naming either gains a mutation-rate qualifier (KINETIC) or stays as-is (STRUCTURAL).
- **SWAMPED →** repeat at `mutation_rate=0.01` instead of 0.005 if SWAMPED was triggered only at the lowest rate; do not claim structural if the low-rate cell was uninterpretable.
- **BASELINE-DRIFT →** investigate immediately; no findings-layer update until the mr=0.03 baseline reproduces.
- **INCONCLUSIVE →** update the outcome grid per principle 2b, then re-interpret.

---

*Audit trail.* Ten outcome rows (principle 2 + 2b; per-arm DIVERGE/CONVERGE/BOTH-KINETIC are orthogonal cross-arm cases). §v2.4-proxy-4d decode-consistent follow-up numbers are the measured baseline at mutation_rate=0.03 per arm (principle 6). Internal control is the within-arm mutation-rate contrast on shared seeds (principle 1). Degenerate-success guard covers mutation-rate-too-low, decoded-view artefact for Arm A, non-monotonicity (principle 4). Principle 20 not triggered. Principle 22 classified as exploratory; does not grow the proxy-basin FWER family. Principle 23 gate preserved — mr=0.03 cells must reproduce §v2.4-proxy-4d baselines. Principle 25 satisfied — all reported metrics are produced by `experiments/chem_tape/analyze_retention.py` at the current commit. Principle 26 satisfied — R_fit_999 is a co-primary grid axis per arm, not diagnostic-only. Principle 27 satisfied — metric definitions cited verbatim from the module's `METRIC_DEFINITIONS` dict. Decision rule commits to specific arc-doc / findings-layer edits per outcome (principle 19).
