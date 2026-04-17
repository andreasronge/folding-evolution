# Arc: proxy-basin-attractor

**Central question (one sentence):** under what conditions does greedy evolution on intlist AND-composition tasks with a high-accuracy single-predicate proxy converge to the proxy alone rather than the full compositional body — and once the canonical compositional body is available (via seeding), does the population retain it or erode?

**Current state (one sentence):** the basin is active as a greedy-convergence claim under uniform-random init; under seeded-init the F/R dissociation is now decoder-specific per the decode-consistent follow-up (commit `cca2323`, 2026-04-17 evening) — under BP_TOPK both `R₂_active` and `R₂_decoded` ≈ 0.002 alongside `R_fit ≈ 0.72` (wide solver neutral network with canonical off-center; majority-solver cloud is structurally distinct from canonical), while under Arm A `R₂_active` ≈ 0.005 alongside `R_fit ≈ 0.004` (classical proxy-basin with canonical elite-preserved only).

**Live next question:** is the decoder-specific F/R dissociation tournament-selection-specific? All three 4b/4c/4d cells share `tournament_size=3, elite_count=2`; a ranking or Pareto selection probe would test whether either decoder-specific mechanism dissolves under lighter selection pressure. Not-yet-scoped; fresh compute required.

**Related findings.md entry:** [findings.md#proxy-basin-attractor](../findings.md#proxy-basin-attractor) — `ACTIVE`, narrowed at mechanism layer.

## Chronology

| date | §id | commit | what it added / changed |
|---|---|---|---|
| 2026-04-14 | [§v2.4](../experiments-v2.md#v24) | `e3d7e8a` | Baseline: `sum_gt_10_AND_max_gt_5` F_AND = 0/20 at pre-reg compute; fitness clusters 0.85–0.97. |
| 2026-04-14 | [§v2.4 compute-scaling](../experiments-v2.md#v24) | `94da867` | 4× compute (pop=2048, gens=3000) still 0/20 — attractor robust to budget scaling. |
| 2026-04-14 | [§v2.4 inspection](../experiments-v2.md#v24) | `cd01d6e` | Winner-inspection: 14/20 baseline seeds converge to exact `max > 5` predicate. Refinement-bottleneck framing falsified. |
| 2026-04-15 | [§v2.4-alt](../experiments-v2.md#v24-alt) | `0230662` | threshold=5 task solves at 17/20 with compositional body — "compositional depth doesn't scale" falsified; basin blocks only when proxy is high-accuracy. |
| 2026-04-15 | [§v2.4-proxy](../experiments-v2.md#v24-proxy) | `0230662` | Under decorrelation (P(max>5\|+)=1.0, P(max>5\|−)=0.5), evolution shifts from `max>5` to `sum>10`. Basin is predicate-agnostic. Name broadened to `single-predicate proxy basin attractor` (methodology §16b). |
| 2026-04-16 | [§v2.12](../experiments-v2.md#v212-arm-a-direct-gp-on-v24-proxy-basin-tasks-2026-04-16) | `1cfe7d5` | Arm A direct GP traps in same basin (0/20 natural, 1/20 decorr) — decoder-general on this task family. |
| 2026-04-16 | [§v2.4-proxy-2](../experiments-v2.md#v24-proxy-2-simultaneous-dual-proxy-decorrelation-on-and-composition-2026-04-16) | `92b3325` | Dual-decorrelation confirms proxy cascade — evolution shifts to third-tier proxies (sum>15, any_cell>7). |
| 2026-04-17 | [§v2.4-proxy-4b](../experiments-v2.md#v24-proxy-4b-seeded-initialization-maintainability-probe--full-horizon-2026-04-16) | `f10b066` | Seeded-init probe: 20/20 best-of-run solve + `R_exact ≤ 0.036`. F/R dissociation → best-of-run retention ≠ full-population retention. Mechanism narrowed from pure-discoverability-limited. |
| 2026-04-17 | [§v2.4-proxy-4c](../experiments-v2.md#v24-proxy-4c-cross-decoder--cross-executor-replication-of-fr-dissociation-2026-04-17) | `9135345` | F/R dissociation replicates under Arm A preserve and BP_TOPK consume. Tournament selection is the common ingredient. Scope broadened across three decoder × executor cells. |
| 2026-04-17 | [§v2.4-proxy-4d](../experiments-v2.md#v24-proxy-4d-active-view-edit-distance-2-retention-measurement-across-the-three-v24-proxy-4b4c-seeded-cells-2026-04-17) | `a8a1e6d` | Direct active-view `R₂_active ≤ 0.0053` per cell (principle-25 gap closed on active view). Incidental R_fit cross-cell differential (BP_TOPK ~0.72 vs Arm A ~0.004) flagged; decoder-specific re-narrowing named as candidate; decode-consistent follow-up queued. |
| 2026-04-17 evening | [§v2.4-proxy-4d decode-consistent follow-up](../experiments-v2.md#v24-proxy-4d-active-view-edit-distance-2-retention-measurement-across-the-three-v24-proxy-4b4c-seeded-cells-2026-04-17) | `cca2323` | BP_TOPK decoded-view R₂ directly measured via `engine.compute_topk_runnable_mask` on dumped `final_population.npz`. `R₂_decoded` tracks `R₂_active` within ~0.001 in every cell (BP_TOPK preserve 0.0024 vs 0.0025; consume 0.0025 vs 0.0025). Resolves candidate rename: BP_TOPK's 72% `R_fit` majority is the "alternative solver cloud" reading, not "decoded-view retention through filtering." Decoder-specific mechanism split confirmed. |

## Open questions (priority-ordered)

| # | question | resolver | compute |
|---|---|---|---|
| 1 | Is the decoder-specific F/R dissociation tournament-selection-specific? All three 4b/4c/4d cells share `tournament_size=3, elite_count=2`; ranking / Pareto / (µ,λ) selection is untested. | not-yet-scoped; fresh prereg under ranking or Pareto selection, ideally on both decoder arms so the two mechanisms (BP_TOPK solver-network vs Arm A proxy-basin) are tested separately | fresh |
| 2 | Under BP_TOPK, does the wide solver neutral network compress toward canonical under higher `bond_protection_ratio`, or remain stable across the neutral network? | Tier-1 prereg candidate: `bp_ratio ∈ {0.5, 0.7, 0.9}` on BP_TOPK preserve seeded cell, measure (R₂_decoded, R_fit, F) as 3-axis outcome grid per §26 | fresh |
| 3 | Under Arm A, does plasticity (runtime adaptation of operator thresholds, rank-1 in `docs/chem-tape/runtime-plasticity-direction.md`) widen the effective solver plateau? | runtime-plasticity prereg scoped to Arm A; ~1-2 hrs engineering then sweep | fresh |
| 4 | Does the F/R dissociation generalise to other proxy-basin-attractor tasks (decorr samplers, split-halves)? | not-yet-scoped | fresh |
| 5 | Whether the basin exists for OR/XOR/larger-k compositions. | not-yet-scoped | fresh |
| 6 | Whether a sampler that eliminates ALL single-predicates above ~0.80 frees AND-composition. | not-yet-scoped; may require a different input domain. | fresh |

## Closed questions (most recent first)

| question | resolved by | resolution |
|---|---|---|
| Does BP_TOPK-decoded retention `R₂_decoded` look like erosion (Arm A pattern) or like filter-through-canonical (canonical preserved via top-K decode)? | [§v2.4-proxy-4d decode-consistent follow-up](../experiments-v2.md#v24-proxy-4d-active-view-edit-distance-2-retention-measurement-across-the-three-v24-proxy-4b4c-seeded-cells-2026-04-17) commit `cca2323` | Erosion pattern — `R₂_decoded ≈ R₂_active ≈ 0.002` under BP_TOPK preserve and consume. The 72% R_fit majority is an **alternative solver cloud** (decoded programs are structurally distinct from canonical), not decoded-view canonical recovered through top-K filtering. Decoder-specific mechanism split confirmed. |
| Is the basin decoder-specific to BP_TOPK? | [§v2.12](../experiments-v2.md#v212-arm-a-direct-gp-on-v24-proxy-basin-tasks-2026-04-16) | No — Arm A traps in the same basin categories. Decoder-general on this task family. |
| Does decorrelating the top-1 proxy free the search? | [§v2.4-proxy](../experiments-v2.md#v24-proxy) | No — evolution shifts to the next-best predicate. Cascade confirmed. |
| Do third-tier proxies take over under dual-decorrelation? | [§v2.4-proxy-2](../experiments-v2.md#v24-proxy-2-simultaneous-dual-proxy-decorrelation-on-and-composition-2026-04-16) | Yes — proxy cascade. |
| Is a permeable-all active-view canonical shell hiding behind the §v2.4-proxy-4b/4c exact-match upper bound? | [§v2.4-proxy-4d](../experiments-v2.md#v24-proxy-4d-active-view-edit-distance-2-retention-measurement-across-the-three-v24-proxy-4b4c-seeded-cells-2026-04-17) | No — directly measured `R₂_active ≤ 0.0053` per cell. |

## Known failure modes / abandoned branches

- **"Refinement bottleneck under 4× compute" framing** — falsified by §v2.4 direct genotype inspection (commit `cd01d6e`). Do not revive this framing without fresh evidence that the basin is compute-limited; it is not.
- **"Compositional depth doesn't scale" framing** — falsified by §v2.4-alt's 17/20 on threshold=5 with the same compositional body. Basin is proxy-driven, not depth-driven.
- **"Pure discoverability-limited (selection would hold canonical if search could reach it)"** — narrowed by §v2.4-proxy-4b's F/R dissociation; selection does preserve canonical at best-of-run but does not propagate through the active-view population. Do not assume discoverability-only without the retention qualifier.

## Superseded readings (preserved per methodology §13)

- **`refinement bottleneck under 4× compute`** — superseded by `max > 5 proxy attractor` at commit `cd01d6e` (2026-04-14). Why: direct genotype inspection showed an exact-predicate attractor, not a refinement failure.
- **`max > 5 proxy attractor`** — superseded by `single-predicate proxy basin attractor` at commit `320fc6b` (2026-04-15, §16b broadening). Why: decorrelation shifted the attractor to `sum > 10` — the basin is predicate-agnostic.
- **`BP_TOPK-specific basin trap`** — superseded by `decoder-general on this task family` at commit `1cfe7d5` (2026-04-16). Why: §v2.12 showed Arm A traps identically.
- **`pure discoverability-limited`** — superseded by `best-of-run canonical retention with active-view erosion under mutation pressure` at commit `cac7537` (2026-04-17, §v2.4-proxy-4b). Refined by §v2.4-proxy-4c broadening across three decoder × executor cells; further refined by §v2.4-proxy-4d direct active-view measurement (commit `a8a1e6d`).
- **`best-of-run canonical retention with active-view erosion under mutation pressure (decoder-general / across three cells, common ingredient tournament selection)`** — superseded by a **decoder-specific mechanism split** at commit `cca2323` (2026-04-17 evening, §v2.4-proxy-4d decode-consistent follow-up). Why: R₂_decoded tracks R₂_active within ~0.001 in every cell, but R_fit cross-cell differential (BP_TOPK ~0.72 vs Arm A ~0.004) combined with the decoded-view evidence shows two distinct population-layer mechanisms under the same F/R dissociation header. Current per-decoder names:
  - **BP_TOPK (preserve + consume):** `canonical off-center in a wide solver neutral network; decoded programs across the majority-solver cloud are structurally distinct from canonical (R_fit ≈ 0.72, R₂_decoded ≈ 0.002)`.
  - **Arm A:** `classical proxy-basin population dynamics; canonical elite-preserved only, non-elite slots saturate in the proxy basin (R_fit ≈ 0.004, mean fitness ≈ 0.84)`.
  The common-ingredient "tournament selection" observation carries forward to both but is no longer a sufficient mechanism description — the decoder arm is itself load-bearing.

---

## Promotion criteria (when to consolidate to findings.md)

- **Positive consolidation** — top-line claim is already ACTIVE in findings.md at this mechanism-reading scope; further narrowing lands as findings-revision commits (not arc promotions). Promotion complete.
- **Decoder-specific re-narrowing** (contingent) — if the decode-consistent follow-up shows `R₂_decoded` patterns diverge between Arm A and BP_TOPK cells, the arc re-narrows in findings.md: mechanism name updates to reflect decoder-specific tail structure; scope tag updates; new review-history entry cites the decode-consistent chronicle's commit.
- **Abandonment** — not applicable at this stage; arc has active open questions and ongoing experimental support.
