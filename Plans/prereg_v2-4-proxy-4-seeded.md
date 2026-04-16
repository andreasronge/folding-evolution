# Pre-registration: §v2.4-proxy-4 — Seeded-initialization probe on §v2.4 AND (discoverability vs maintainability)

**Status:** QUEUED · target commit `TBD` · 2026-04-16

## Question (one sentence)

Is the §v2.4 AND task (F_AND = 0/20 at every configuration tested) un-solved because the canonical 12-token AND body is **undiscoverable from realistic random starts**, or because it is **actively displaced by the single-predicate proxy basin under selection**?

## Hypothesis

The `proxy-basin-attractor` finding says evolution reliably converges to high-accuracy single-predicates (`max > 5`, `sum > 10`). What it does not establish is whether the canonical 12-token AND body, if present in the initial population, would be **retained** by selection or **displaced** in favor of the simpler proxy.

Three disjoint hypotheses, distinguished by seeded-population retention:

1. **Discoverability-limited.** Seeded canonical bodies are retained; selection favors them over the proxy. §v2.4's 0/20 is a search/exploration failure — the mechanism can find the body if given a head-start but can't reach it cold. Part 1 meta-learning should attack exploration (e.g., novelty search, diverse initialization).
2. **Maintainability-limited.** Seeded canonical bodies get **displaced** under mutation/selection drift toward the simpler proxy. The basin is a selection-pressure phenomenon, not a search problem. Part 1 meta-learning should attack selection (multi-objective, Pareto).
3. **Both.** Partial retention, partial displacement — both mechanisms contribute.

The §v2.4 sanity check (commit `f806d04`, experiments-v2.md line 306) already established the canonical 12-token body produces 64/64 train and 256/256 holdout correct labels: semantically valid, scores 1.000. The question is purely about evolutionary dynamics.

## Design constraint (important)

**Bonded-tape construction is not supported in the current Rust executor** (scoping investigation, 2026-04-16). Bonding is computed post-execution in the Python layer; there is no API for seeding a tape with a pre-formed bonded run. This prereg therefore uses **unbonded seeded tapes only**: the canonical 12 tokens are placed at positions 0..11 of the tape, and positions 12..31 are filled with NOPs (id 0, inactive). Under BP_TOPK's bonding logic, the canonical 12 active tokens form the single bonded run (all remaining cells are inactive), so the extracted program at gen 0 is exactly the canonical body for every seeded individual.

This narrows the test slightly: we are measuring whether a **canonical body present and extractable at gen 0** is retained under mutation/selection — which is the maintainability question, conditioned on the surface-structural starting point being canonical. Pure-search-landscape maintainability (bodies present in non-canonical bonded form) is not tested here.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_4_proxy4_seeded.yaml`
- **Arms / conditions:** 3 arms via `seed_fraction` axis:
  - Arm 0: `seed_fraction = 0.0` (drift check; should reproduce §v2.4 = 0/20)
  - Arm 1: `seed_fraction = 0.001` (~1 canonical body in pop=1024)
  - Arm 2: `seed_fraction = 0.01` (~10 canonical bodies in pop=1024)
- **Tasks:** `sum_gt_10_AND_max_gt_5` — single fixed task (no alternation), natural sampler (matches §v2.4 baseline)
- **Seeds:** 0-19
- **Fixed params:** pop=1024, gens=1500, BP_TOPK(k=3, bp=0.5), v2_probe alphabet, tape_length=32, executor rule = preserve
- **Seed tape (fixed, pre-committed):** 12-token CONST_0-first canonical AND body = `CONST_0 INPUT REDUCE_MAX CONST_5 GT INPUT SUM CONST_5 CONST_5 ADD GT IF_GT`. Hex: `020112100801051010070811`. Padded with 20 NOPs → final hex: `0201121008010510100708110000000000000000000000000000000000000000` (32 bytes).
- **Est. compute:** ~45 min at 10 workers (3 arms × 20 seeds × 1500 gens)
- **Related experiments:** §v2.4 baseline (F_AND = 0/20 at pop=1024), §v2.4-proxy-2 (dual-decorr still 0/20), §v2.12 Arm A (0/20), §v2.14b consume (0/20 on natural sampler)

**Principle 20 audit:** input distribution and sampler unchanged from §v2.4 natural. Label function unchanged. Initial population content changed from uniform-random to uniform-random ∪ k canonical bodies. This is an initialization perturbation, not a sampler change — principle 20 does not directly apply. **Noted side-effect:** a seeded individual that perfectly labels all training examples during early generations can distort population-entropy metrics; tracked in diagnostics.

## Baseline measurement (required)

- **Baseline quantity:** F_AND under seed_fraction=0.0 (Arm 0 of this sweep). Must reproduce §v2.4 = 0/20.
- **Anchor:** §v2.4 baseline F_AND = 0/20 (commit `e3d7e8a`).
- **Drift check:** if Arm 0 F_AND > 2/20, flag cross-commit drift before interpreting Arms 1-2.

## Internal-control check (required)

- **Tightest internal contrast:** Arm 0 vs Arm 1 vs Arm 2 on the same task, same seeds, same commit. The seed-fraction gradient IS the internal control.
- **Are you running it here?** Yes.
- **Not included (optional follow-up):** a "noise-control" arm with seed-fraction non-canonical (e.g., random 12-token bodies that are not the canonical). Deferred to avoid scope creep; reasonable because the structural ablation (seed_fraction=0) already controls for "did anything change merely by having more gen-0 diversity."

## Pre-registered outcomes (required — at least three)

Let `F_0`, `F_1`, `F_2` = F_AND (solve ≥ 0.999) under seed_fractions 0.0, 0.001, 0.01.
Let `R_i` = **retention rate** at final generation under Arm i, measured as the fraction of the final population whose extracted program matches the canonical body within edit-distance ≤ 2 (allows for small mutations that don't disrupt semantic function).

| outcome | criterion | interpretation |
|---------|-----------|----------------|
| **PASS — discoverability-limited** | `F_1 ≥ 15/20` AND `F_2 ≥ 18/20` AND `R_2 ≥ 0.5` | Seeded canonical bodies survive and dominate. §v2.4's 0/20 is a pure **search/discoverability** failure — the mechanism retains the body when given the head-start. Meta-learning should target exploration/diversity at gen 0. |
| **PARTIAL — leaky maintainability** | `F_1 ∈ [3, 14]` OR (`F_2 ∈ [10, 17]` AND `R_2 ∈ [0.1, 0.5]`) | Canonical bodies partially retained but actively competed against by the proxy. Both discoverability and maintainability contribute. Meta-learning must target both. |
| **FAIL — maintainability-limited** | `F_2 ≤ 2/20` AND `R_2 < 0.1` | Seeded bodies get **displaced** by the proxy despite head-start. The basin is a selection-level attractor. Meta-learning must attack selection pressure (multi-objective, Pareto). |
| **ARM-0 DRIFT** | `F_0 > 2/20` | Seed_fraction=0.0 arm produces > §v2.4 baseline; the sweep is not a clean §v2.4 replication. Investigate before interpreting Arms 1-2. |

**Threshold justification.** 15/20 for `F_1` at 0.001: one injected body × high mutation resistance × selection-driven fixation should give >75% solve rate if the body is maintained. 18/20 for `F_2` at 0.01 is a hard handle on high retention. PARTIAL range captures fractional retention. FAIL matches §v2.4 baseline (≤2/20) plus low retention.

## Degenerate-success guard (required)

- **Trivial gen-0 fitness dominance.** A single injected canonical body has fitness 1.000 at gen 0; under tournament selection it rapidly fixates. This is **the expected PASS signature, not a degenerate artifact** — but we must confirm domination holds at **final generation** (via retention rate `R`), not just early.
- **False retention via copy-paste.** If all retained canonical bodies are exact copies of the seed (zero lineage-distance), mutation rate may be too low or selection too elite. Check lineage tree-distance on a sample of retained individuals; pure-copy retention is suspicious.
- **Proxy displacement inside retained lineage.** A seeded canonical body could drift toward the proxy at the token level (e.g., `max > 5` sub-program emerges from mutations within the canonical body's footprint) while still being classified as "canonical within edit-distance 2." Audit retained bodies' extracted program structure via `decode_winner.py`.
- **Too-clean (`F_2 = 20/20` with `R_2 ≈ 1.0`).** Would mean seeded bodies are invincible at seed_fraction=0.01. Report but do not over-interpret; meta-learning implications still valid.
- **Detection commitments:** `decode_winner.py` on all 60 best-of-run winners; gen-0 / mid / final population entropy; 3-seed sample of lineage tree-distance on retained canonical bodies.

## Statistical test (if comparing conditions)

- **Primary:** descriptive solve-rate counts per arm + retention rate per arm.
- **Paired McNemar:** Arm 0 vs Arm 1 and Arm 0 vs Arm 2 on shared seeds for F_AND.
- **Significance threshold:** α = 0.05, two-sided.
- **Retention rate:** report per-arm with 95% Wilson CI; compare qualitatively (low power at n=20 runs per arm).

## Diagnostics to log (beyond fitness)

- Per-seed × per-arm F_AND + best-of-run fitness + holdout gap
- Retention rate per arm (final-population canonical-body match ≤ edit-distance 2)
- Population-entropy trajectory per arm (gen 0, every 100 gens, final)
- Winner-genotype attractor-category classification per arm
- Lineage tree-distance sample on retained canonical bodies (3 samples per arm) — mutation/copy check
- Seed overlap with §v2.4 baseline non-solvers (Arm 0 should be ≥ 18/20 overlap)

## Scope tag (required for any summary-level claim)

**PASS — discoverability-limited:** `within-family · n=20 per arm · at pop=1024 gens=1500 BP_TOPK(k=3,bp=0.5) v2_probe · on sum_gt_10_AND_max_gt_5 natural sampler · seeded canonical body retained — §v2.4 is a discoverability failure`

**PARTIAL — leaky maintainability:** `within-family · n=20 per arm · at pop=1024 gens=1500 BP_TOPK(k=3,bp=0.5) v2_probe · on sum_gt_10_AND_max_gt_5 natural sampler · seeded canonical body partially retained — both discoverability and maintainability contribute`

**FAIL — maintainability-limited:** `within-family · n=20 per arm · at pop=1024 gens=1500 BP_TOPK(k=3,bp=0.5) v2_probe · on sum_gt_10_AND_max_gt_5 natural sampler · seeded canonical body actively displaced by proxy — §v2.4 is a selection-level attractor`

## Decision rule

- **PASS — discoverability-limited →** update `findings.md#proxy-basin-attractor` "Scope boundaries" with the discoverability-specific reading. Queue Part 1 meta-learning Phase 1 design toward exploration/diversity operators (Novelty Search, Quality-Diversity, diverse initialization).
- **PARTIAL — leaky →** update `findings.md#proxy-basin-attractor` with the joint reading. Queue mutation-robustness follow-up at finer lineage resolution.
- **FAIL — maintainability-limited →** update `findings.md#proxy-basin-attractor` with the selection-level reading. Queue Part 1 design toward selection interventions (multi-objective / Pareto / fitness-sharing).
- **ARM-0 DRIFT →** investigate; do not update findings.md.

---

*Audit trail.* Four outcome rows (principle 2). §v2.4 baseline as anchor (principle 6). Internal control is the seed-fraction ablation on shared seeds (principle 1). Degenerate-success candidates include trivial gen-0 dominance, false retention, and proxy drift inside retained lineage (principle 4). Principle 20 reviewed (not triggered — initialization perturbation, not sampler change). Decision rule commits to exact findings.md edits AND specific Part 1 direction per outcome (principle 19) — this is the load-bearing commitment this experiment makes.
