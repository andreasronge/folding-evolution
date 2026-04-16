# Pre-registration: §v2.4-proxy-4b — seeded-init maintainability probe (full horizon)

**Status:** QUEUED · target commit `TBD` · 2026-04-16

## Supersession note

§v2.4-proxy-4 (commit `9455d04`) was **design-flawed** — early-termination at
`fitness.max() >= 1.0 and not alternating` killed the seeded arms at gen 1
before mutation + tournament selection could drift the canonical body. The
result reported gen-0 dominance, not multi-generation maintainability.
§v2.4-proxy-4b adds a `disable_early_termination` config flag and reruns
the same three arms, letting the GA run the full 1500 gens so retention
rate `R_i` at final generation becomes measurable.

Per methodology principle 13, §v2.4-proxy-4 is not deleted — it remains in
the chronicle for the reasoning trail, annotated as SUPERSEDED.

## Question (one sentence)

When the §v2.4 AND task's canonical 12-token body is injected into the initial
population at fractions {0, 0.001, 0.01} and the GA runs the full 1500 gens
**without early-termination**, is the canonical body **retained** (discoverability-
limited) or **displaced** by the single-predicate proxy basin (maintainability-
limited)?

## Hypothesis

Same three hypotheses as §v2.4-proxy-4 — but now actually measurable because
the GA won't short-circuit at gen 1:

1. **Discoverability-limited (PASS).** Seeded canonical bodies retained at
   final gen 1500; selection favors them over the proxy. Retention rate `R`
   stays high across mutation pressure. Meta-learning should attack
   exploration / diverse initialization.
2. **Maintainability-limited (FAIL).** Seeded bodies get displaced; final
   population drifts to the proxy basin despite 10 or more seeded copies
   at gen 0. Meta-learning must attack selection pressure.
3. **Both (PARTIAL).** Partial retention — some seeds retain, others drift.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_4_proxy4b_seeded.yaml`
- **Arms / conditions:** 3 arms via `seed_fraction` axis: {0.0, 0.001, 0.01}
- **Tasks:** `sum_gt_10_AND_max_gt_5` (fixed, natural sampler — matches §v2.4 baseline)
- **Seeds:** 0-19 (same as §v2.4-proxy-4 for cross-sweep comparability)
- **Fixed params:** pop=1024, gens=1500, BP_TOPK(k=3, bp=0.5), v2_probe, tape_length=32, preserve, **`disable_early_termination: true`**
- **Seed tape (fixed):** canonical 12-token CONST_0-first AND body + 20 NOPs. Hex: `0201121008010510100708110000000000000000000000000000000000000000`. Identical to §v2.4-proxy-4.
- **Est. compute:** ~45 min at 10 workers (60 configs × full 1500 gens at ~5-7 min per run for pop=1024)
- **Related experiments:** §v2.4-proxy-4 (superseded by this), §v2.4 baseline (0/20)

**Principle 20 audit:** label function, input distribution, and sampler unchanged. The ONE config difference from §v2.4-proxy-4 is `disable_early_termination: true`. Principle 20 not triggered.

**Principle 23 audit:** Arm 0 still serves as the drift-check vs §v2.4 baseline (0/20). Arms 1/2 now actually exercise the GA over full 1500 gens — the prereg deliverables that §v2.4-proxy-4 silently skipped (final-population retention rate, per-gen entropy trajectory, lineage-tree-distance sample) become measurable.

## Baseline measurement (required)

- **Baseline quantity:** F_AND under seed_fraction=0.0 (Arm 0). Must reproduce §v2.4 = 0/20 at full 1500 gens (which is what §v2.4-proxy-4's Arm 0 already did: 0/20, mean best 0.921, matching §v2.4 exactly).
- **Anchor:** §v2.4 baseline F_AND = 0/20 (commit `e3d7e8a`).

## Internal-control check (required)

- **Tightest internal contrast:** Arm 0 vs Arm 1 vs Arm 2 on same task, same seeds, same commit. Same as §v2.4-proxy-4.
- **Are you running it here?** Yes.

## Pre-registered outcomes (required — at least three)

Let `F_i` = F_AND under seed_fraction `i` at full 1500 gens.
Let `R_i` = final-generation retention rate (fraction of final pop whose extracted program matches canonical body within edit-distance ≤ 2).

| outcome | criterion | interpretation |
|---------|-----------|----------------|
| **PASS — discoverability-limited** | `F_1 ≥ 15/20` AND `F_2 ≥ 18/20` AND `R_2 ≥ 0.3` | Seeded canonical body is retained; best-of-run stays at canonical. §v2.4 is a pure discoverability failure. Meta-learning targets exploration. |
| **PARTIAL — leaky** | `F_1 ∈ [3, 14]` OR (`F_2 ∈ [10, 17]` AND `R_2 ∈ [0.05, 0.3]`) | Canonical bodies partially retained; proxy competes. Both mechanisms matter. |
| **FAIL — maintainability-limited** | `F_2 ≤ 2/20` AND `R_2 < 0.05` | Seeded bodies displaced. Basin is selection-level. Meta-learning targets selection pressure. |
| **ARM-0 DRIFT** | `F_0 > 2/20` | Seed_fraction=0.0 arm deviates from §v2.4 baseline. Investigate before interpreting. |

**Retention rate `R` measurement:** `decode_winner.py` on each final-population individual (or a sampled subset if full-pop decode is too expensive); count fraction whose extracted program matches the canonical body's token set (unordered) and length (12 ± 2 active tokens).

**Threshold justification:** `R_2 ≥ 0.3` (30% of final pop retains canonical) is a weaker bar than §v2.4-proxy-4's 0.5 — calibrated down because 1500 gens of mutation pressure on 10 seeded individuals out of 1024 (0.01 fraction) can reasonably dilute retention even under positive selection. The 0.05 FAIL floor is the "essentially gone" threshold.

## Degenerate-success guard (required)

- **Trivial retention at Arm 2 (`R_2 ≈ 1.0`):** would mean seeded bodies dominate the entire final population despite mutation. Possible if the canonical body has zero mutation-viable neighbors (every mutation hurts fitness), making it a strong attractor rather than a leaky one. Report the pattern; interpret as PASS with a strong-attractor sub-reading.
- **F_2 = 20/20 with R_2 low:** possible if the best-of-run is a mutated descendant of the canonical body that still solves but isn't recognized by the retention-rate classifier (edit-distance > 2). Inspect winners directly — a descendant solver is still a PASS, just with imperfect retention metric.
- **Detection:** `decode_winner.py` on all 60 best-of-run winners + final-pop sample; per-arm attractor classification; gen-0 / mid / final population entropy trajectory.

## Statistical test (if comparing conditions)

- **Primary:** descriptive solve-rate and retention-rate per arm.
- **Paired McNemar:** Arm 0 vs Arm 1 and Arm 0 vs Arm 2 on F_AND, shared seeds.
- **Classification (principle 22):** **confirmatory** — gates the mechanism-reading claim that would narrow findings.md's `proxy-basin-attractor`.
- **Family:** "proxy-basin family" — together with §v2.4-proxy, §v2.4-proxy-2, §v2.4-proxy-3, §v2.12. Running an FWER audit at promotion time; this prereg adds 1 confirmatory test to that family.
- **Significance threshold:** α = 0.05 two-sided raw; family-wise α TBD at promotion time.

## Diagnostics to log (beyond fitness)

- Per-seed × per-arm F_AND + best-of-run fitness + holdout gap
- Retention rate per arm (final-pop canonical-body match within edit-distance ≤ 2)
- Population-entropy trajectory per arm (gen 0, 100, 500, 1000, 1500)
- Winner-genotype attractor-category classification per arm
- Per-run wall time (drift check; should be ~5-7× longer than §v2.4-proxy-4 due to full 1500 gens)
- Solver seed overlap with §v2.4-proxy-4 Arms 1/2 (should be ≥ 18/20 overlap if maintainability holds)

## Scope tag

**PASS (discoverability-limited):** `within-family · n=20 per arm · at pop=1024 gens=1500 BP_TOPK(k=3,bp=0.5) v2_probe disable_early_termination=true · on sum_gt_10_AND_max_gt_5 natural sampler · seeded canonical body retained under full-horizon mutation+selection pressure`

## Decision rule

- **PASS — discoverability-limited →** `/research-rigor promote-finding` to narrow `findings.md#proxy-basin-attractor` scope boundary: "canonical AND body, when seeded, is maintained at population level under BP_TOPK preserve — the basin prevents *discovery*, not *retention*." Directs Part 1 meta-learning toward exploration operators.
- **PARTIAL — leaky →** promote the joint reading. Queue mutation-robustness follow-up with per-gen lineage logging.
- **FAIL — maintainability-limited →** promote the selection-level reading. Part 1 meta-learning targets selection / multi-objective approaches. This is the least-expected outcome given gen-0 dominance; would be a strong finding.
- **ARM-0 DRIFT →** investigate; do not update findings.md.

---

*Audit trail.* Four outcome rows (principle 2). §v2.4 baseline anchor (principle 6). Internal control is the seed-fraction ablation at full horizon (principle 1). Degenerate-success includes trivial retention + edit-distance-classifier-miss (principle 4). Principle 20 not triggered. Principle 22 classified as confirmatory, family "proxy-basin." Principle 23 explicit: the §v2.4-proxy-4 prereg's silently-skipped deliverables (full-horizon maintainability, retention rate, entropy trajectory) are the deliverables this sweep actually executes. Decision rule commits to specific findings.md edits per outcome (principle 19).

**Supersession of §v2.4-proxy-4:** upon completion of this sweep, add a supersession block to the §v2.4-proxy-4 chronicle (when it's eventually logged) noting that §v2.4-proxy-4b measured what §v2.4-proxy-4 intended to measure. The §v2.4-proxy-4 result (gen-0 dominance signature) is preserved as observation; the interpretation (discoverability-vs-maintainability) moves to §v2.4-proxy-4b.
