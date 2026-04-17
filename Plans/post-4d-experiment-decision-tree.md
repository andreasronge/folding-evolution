# Post-§v2.4-proxy-4d experiment decision tree

**Status:** Planning doc. Not pre-registered. Drafted 2026-04-17 evening after §v2.4-proxy-4d decode-consistent follow-up (commit `cca2323`) confirmed the decoder-specific mechanism split under the F/R dissociation.

**Related docs:**
- [`docs/chem-tape/arcs/proxy-basin-attractor-arc.md`](../docs/chem-tape/arcs/proxy-basin-attractor-arc.md) — live arc summary; current open questions
- [`docs/chem-tape/findings.md#proxy-basin-attractor`](../docs/chem-tape/findings.md) — claim layer, decoder-specific scope applied at `cca2323`
- [`docs/chem-tape/runtime-plasticity-direction.md`](../docs/chem-tape/runtime-plasticity-direction.md) — plasticity direction note, scoped to Arm A post-4d
- [`docs/methodology.md`](../docs/methodology.md) — 26-principle ledger + §27; §26 (grid diagnostic axes) and §27 (metric definitions in code) gate every prereg below

## What §v2.4-proxy-4d locked in

Two mechanisms under one F/R-dissociation header, confirmed across 180 runs + decode-consistent follow-up:

| decoder | R_fit (≥0.999) at sf=0.01 | R₂_decoded at sf=0.01 | mechanism reading |
|---|---|---|---|
| BP_TOPK preserve | 0.723 | 0.0024 | canonical off-center in wide solver neutral network |
| BP_TOPK consume | 0.730 | 0.0025 | same (independent of preserve/consume executor semantics) |
| Arm A | 0.004 | 0.0046 (informational, topk=1) | classical proxy-basin population dynamics |

Tournament selection is common across all cells but is no longer a sufficient mechanism description — **the decoder arm is itself load-bearing**. This reshapes the Tier-1 / Tier-2 plan below.

## Tier 1 — drafted as preregs, ready to run after 4d

Three preregs + two sweep YAMLs landed at this commit. The plasticity probe is BLOCKED on engineering (see "Engineering gates" below).

| slug | prereg | sweep YAML(s) | cost | §26 grid axes | runs within Tier-1 regardless of outcome? |
|---|---|---|---|---|---|
| §v2.4-proxy-5a | [`prereg_v2-4-proxy-5a-bp-sweep.md`](prereg_v2-4-proxy-5a-bp-sweep.md) | `v2_4_proxy5a_bp_sweep.yaml` | zero-LoC (bp is an existing ChemTapeConfig field); ~30-45 min wall | `(R₂_decoded, R_fit, F_AND)` | yes |
| §v2.4-proxy-5b | [`prereg_v2-4-proxy-5b-mutation-rate.md`](prereg_v2-4-proxy-5b-mutation-rate.md) | `v2_4_proxy5b_mutation_rate_bp_topk.yaml` + `v2_4_proxy5b_mutation_rate_arm_a.yaml` | zero-LoC (mutation_rate is an existing field); ~45-60 min wall total | `(R₂_decoded, R_fit, F_AND)` stratified by arm | yes |
| §v2.5-plasticity-1a | [`prereg_v2-5-plasticity-1a.md`](prereg_v2-5-plasticity-1a.md) | BLOCKED (no YAML yet) | ~2-4 hr engineering + 15-30 min sweep | `(F_AND_test, Baldwin_slope, R_fit_plastic - R_fit_frozen, F_AND_train)` | yes — but after engineering lands |

### Engineering gates for Tier-1 plasticity probe (§25 + §27)

Per §27, the plasticity prereg cannot transition from QUEUED to RUNNING until these land:

1. Plastic-operator implementation (rank-1 operator-threshold plasticity in a new module or VM extension)
2. `ChemTapeConfig` fields: `plasticity_enabled`, `plasticity_budget`, `plasticity_mechanism`, `plasticity_train_fraction` (all hash-excluded at defaults per §11)
3. Task split support (75/25 train/test)
4. `METRIC_DEFINITIONS` entries: `F_AND_test`, `F_AND_train`, `R_fit_plastic_999`, `R_fit_frozen_999`, `Baldwin_gap`, `Baldwin_slope`
5. Analysis pipeline (new script or extension of `analyze_retention.py`)
6. Pytest round-trip (frozen-disabled equivalence) + smoke (plastic non-degenerate)

Estimated total engineering effort: 2-4 hours. The prereg explicitly commits to the RUNNING transition checklist so the principle-23 execution-fidelity gate at chronicle time is pre-defined.

## Tier 2 — engineering-contingent, gated on Tier-1 outcomes

Six candidate Tier-2 experiments, ordered by engineering cost. Each is **only worth prereg-ing under specific Tier-1 outcomes** — the right-column gates below are the condition that makes the experiment informative.

| rank | candidate | engineering cost | gate (which Tier-1 outcome triggers) |
|---|---|---|---|
| 1 | **Non-tournament selection probe** — replace `tournament_size=3` + `elite_count=2` with ranking, (µ,λ), or Pareto selection on the BP_TOPK preserve + Arm A seeded cells | ~50-100 LoC (new selection-operator path in `evolve.py` behind a `selection_mode` config field); ~30-60 min sweep | Runs regardless of 5a/5b outcomes — the arc's open Q #1 is independent of bp / mutation_rate. But its *interpretation* depends on 5b: if 5b shows A-KINETIC, ranking selection on Arm A tests whether selection pressure is doing the work not visible to mutation rate. If 5b shows BP-STRUCTURAL, ranking selection on BP_TOPK tests whether tournament specifically creates the neutral-network geometry or whether it is decoder-intrinsic. |
| 2 | **Repair operator** — mutation variant that re-canonicalizes malformed runs back to nearest valid run (protects against separator-creation mutations that fragment bonded regions) | ~50-100 LoC in the mutation operator path + new config field | Only worth prereg-ing if §v2.4-proxy-5a (bp sweep) returns FAIL — decoder-structural. If bp=0.9 already compresses the cloud (PASS), repair is redundant; if bp does nothing (FAIL), repair is a targeted fallback at the mutation-operator level. If §v2.4-proxy-5b (mutation_rate) returns CONVERGE (both arms structural), repair is also unlikely to help. |
| 3 | **Lexicase / multi-objective (fitness, canonical-Hamming)** — lexicase selection on a vector of `(fitness_per_example, -hamming_to_canonical)` pressures the population to retain canonical-adjacent genotypes alongside task performance | ~100-200 LoC (new selection algorithm; lexicase has specific tie-breaking semantics) | Only worth prereg-ing if both (a) non-tournament selection probe (Tier-2 rank 1) shows tournament specificity AND (b) §v2.4-proxy-5a shows decoder-structural under BP_TOPK. At that point the remaining hypothesis is "selection pressure needs to explicitly include canonical-similarity." Redundant under either PASS outcome of 5a or non-tournament-probe. |
| 4 | **QD archive / MAP-Elites on canonical-distance behaviour descriptor** — maintain an explicit archive of canonical-distant-but-fit individuals keyed by Hamming-to-canonical behaviour descriptor; decouples "solved" from "retained in active evolution" | ~200-300 LoC (new archive data structure + archive-informed selection) | Orthogonal to all Tier-1 outcomes — route-around rather than solve. Worth prereg-ing independently, NOT as a contingent follow-up. Natural next experiment after Tier-1 lands if the user wants to pursue QD in parallel with the variation-layer probes. Not recommended as an early commit because the two directions (fix the mechanism vs route around it) should stay epistemically distinct. |
| 5 | **Evolvable chemistry (Direction 4)** — meta-evolve the chem-tape decoder itself (bond threshold, top-K K, bond-protection ratio as co-evolvable parameters) via an outer-loop ES or CGP | ~500-1000 LoC (two-level architecture; see `docs/theory.md` §Meta-Learned Developmental Systems) | Strong gate: only worth prereg-ing if §v2.4-proxy-5a AND 5b BOTH show BP_TOPK structural (decoder creates the neutral network regardless of mutation rate or bond-protection). Under those outcomes, the mechanism is genuinely at the representation layer, and evolvable chemistry is the principled direction per Altenberg constructional selection. |
| 6 | **AutoMap denoising autoencoder** (explicitly excluded from current plan per user's earlier instruction — retained here for decision-tree completeness) | ~500+ LoC + GPU compute | Same gate as evolvable chemistry, but AutoMap is a larger research swing. Retained in the decision tree as a representation-layer option; excluded from near-term prereg queue per user direction. |

## Decision flow

Post Tier-1 (both 5a and 5b landed; plasticity may still be running or pending engineering), the decision tree looks like:

### If §v2.4-proxy-5a PASS (cliff-flattening confirmed under BP_TOPK)

- Variation-layer direction is live for BP_TOPK. Repair operator (Tier-2 rank 2) becomes the natural follow-up if bp=0.9 is close to its protection ceiling (e.g., PASS at bp=0.7 already lifts R₂_decoded; bp=0.9 doesn't add more).
- Non-tournament selection probe (Tier-2 rank 1) remains worth running — tests whether the mechanism is bp-plus-tournament or bp-alone.
- QD archive (Tier-2 rank 4) still orthogonal; not directly gated.
- Evolvable chemistry (Tier-2 rank 5) de-prioritised — the mechanism has a cheaper operator-level lever.

### If §v2.4-proxy-5a FAIL (decoder-structural under BP_TOPK)

- Variation-layer direction for BP_TOPK is retired.
- Non-tournament selection probe (Tier-2 rank 1) becomes the critical next test — is the neutral network decoder-intrinsic, or tournament-selection-coupled?
  - If ranking selection also shows wide solver cloud → decoder-intrinsic → evolvable chemistry (Tier-2 rank 5) is the principled next step.
  - If ranking selection shows narrower cloud → tournament-coupled → Tier-2 rank 3 lexicase becomes informative.
- QD archive remains orthogonal.

### If §v2.4-proxy-5b DIVERGE (A-KINETIC + BP-STRUCTURAL — the theoretically-informative case)

- Strongest outcome: decoder-specific mechanism split is cemented at the kinetic-orthogonality layer.
- For Arm A: §v2.5-plasticity-1a becomes the most load-bearing next probe (tests whether within-lifetime adaptation can do what genotype mutation cannot). Engineering prerequisites become priority-1.
- For BP_TOPK: evolvable chemistry (Tier-2 rank 5) becomes the most load-bearing next probe (representation-layer is the structural lever, not variation or selection). Consider prereg immediately with gating on non-tournament selection probe results.
- Ranking selection probe (Tier-2 rank 1) is valuable cross-confirmation on both arms.

### If §v2.4-proxy-5b CONVERGE (both arms structural)

- Variation-layer retired for both arms.
- Non-tournament selection probe (Tier-2 rank 1) is priority-1 — selection is the only remaining non-representation lever.
- Plasticity probe remains valid on Arm A (orthogonal axis).
- Evolvable chemistry becomes the strong long-term direction if non-tournament selection also shows insensitivity.

### If §v2.4-proxy-5b BOTH-KINETIC (both arms respond to mutation rate)

- Variation-layer direction is live for both arms — a simpler story than DIVERGE.
- §v2.4-proxy-5a bp sweep under Arm A (extended from current prereg which is BP_TOPK only) becomes informative even though bp is decoder-ignored per current code — would require adding bp-for-Arm-A support if the result motivates.
- Plasticity probe less urgent (the variation-layer lever already works).

## Cross-cutting: principle-26 compliance for all Tier-1 and Tier-2 preregs

Every prereg in this tree MUST grid all measured axes at coarse bins per §26. No axis labeled "diagnostic" that carries mechanism-level information may be demoted to effect-size-only without citing the reason. Specifically:

- **R_fit is now a mechanism-level axis**, not diagnostic — per the post-4d finding. Every prereg touching the proxy-basin-attractor arc must grid R_fit alongside R₂_decoded.
- **Hamming-to-canonical distributions** (used in Baldwin diagnostic) must be gridded at 3 bins minimum if measured per-seed, per §26.
- **Baldwin_slope sign + CI** is a grid axis for any plasticity-related prereg, not a diagnostic flag.

## Cross-cutting: principle-27 compliance for all Tier-1 and Tier-2 preregs

Every metric cited in an outcome-grid row MUST exist in a module-level `METRIC_DEFINITIONS` dict and be quoted verbatim in the prereg's "Metric definitions" block. New metrics for new mechanisms require the METRIC_DEFINITIONS addition as a prerequisite engineering step. This is the measurement-fidelity gate that closed the 4d description-vs-implementation drift.

## What NOT to do right now

- **Do not queue Tier-2 items as preregs before Tier-1 runs.** Their outcome grids depend on the mechanism readings 5a / 5b establish. Writing grids now either bakes in assumptions (principle 2b failure) or commits compute to experiments whose interpretation shifts.
- **Do not expand the arc doc's open-questions list** by copying Tier-2 items there. Tier-2 items are contingent; the arc doc lists currently-live experimental targets, not the full decision tree. The decision tree is the right place for the contingent items.
- **Do not commit the plasticity probe's sweep YAML** until engineering lands. Per §25, committing a sweep YAML that refers to config fields that do not exist at the commit is a measurement-infrastructure failure at prereg-authoring time.

## Timeline (rough)

| step | what | blocking? | estimate |
|---|---|---|---|
| 1 | Run §v2.4-proxy-5a + §v2.4-proxy-5b sweeps (append to queue.yaml) | unblocks ~all Tier-2 gates | 1.5-2 hr wall |
| 2 | Log-result chronicles for 5a + 5b (via research-rigor log-result mode; codex review mandatory per principle 22/27) | unblocks findings-revision | ~1-1.5 hr each |
| 3 | Update arc doc + findings.md + decision tree (this doc) per 5a/5b outcomes | unblocks Tier-2 selection | ~30-45 min |
| 4 | Plasticity probe engineering (Tier-1 §v2.5-plasticity-1a prerequisites) | gates plasticity RUNNING | 2-4 hr |
| 5 | Decide Tier-2 next step per decision flow above | — | interactive |

Total wall to Tier-2 decision: ~5-8 hrs of focused work after the sweeps finish.
