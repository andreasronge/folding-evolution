# Arc: proxy-basin-attractor

**Central question (one sentence):** under what conditions does greedy evolution on intlist AND-composition tasks with a high-accuracy single-predicate proxy converge to the proxy alone rather than the full compositional body — and once the canonical compositional body is available (via seeding), does the population retain it or erode?

**Current state (one sentence):** the basin is active as a greedy-convergence claim across three decoder × executor cells on `sum_gt_10_AND_max_gt_5`; seeded-init reaches 20/20 best-of-run solve with active-view erosion (`R₂_active ≤ 0.0053` per cell, commit `a8a1e6d`), while the BP_TOPK decoded-view retention remains measurement-gated and the R_fit cross-cell differential flags a candidate decoder-specific mechanism narrowing.

**Live next question:** decode-consistent retention measurement on the dumped `final_population.npz` — does `R₂_decoded` under BP_TOPK look like Arm A's (erosion to proxy) or like canonical-through-filtering (decoded-view retention via top-K recovery)? Resolves the candidate rename flagged by §v2.4-proxy-4d.

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

## Open questions (priority-ordered)

| # | question | resolver | compute |
|---|---|---|---|
| 1 | Does BP_TOPK-decoded retention `R₂_decoded` look like erosion (Arm A pattern) or like filter-through-canonical (canonical preserved via top-K decode)? | follow-up on `final_population.npz` using the now-implemented `extract_decoded()` path in `analyze_retention.py` | **zero-compute** |
| 2 | Is the F/R dissociation tournament-selection-specific? | not-yet-scoped; fresh prereg under ranking or Pareto selection on the same three cells | fresh |
| 3 | Does the F/R dissociation generalise to other proxy-basin-attractor tasks (decorr samplers, split-halves)? | not-yet-scoped | fresh |
| 4 | Whether the basin exists for OR/XOR/larger-k compositions. | not-yet-scoped | fresh |
| 5 | Whether a sampler that eliminates ALL single-predicates above ~0.80 frees AND-composition. | not-yet-scoped; may require a different input domain. | fresh |

## Closed questions (most recent first)

| question | resolved by | resolution |
|---|---|---|
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
- **`pure discoverability-limited`** — superseded by `best-of-run canonical retention with active-view erosion under mutation pressure` at commit `cac7537` (2026-04-17, §v2.4-proxy-4b). Refined by §v2.4-proxy-4c broadening across three decoder × executor cells; further refined by §v2.4-proxy-4d direct active-view measurement (commit `a8a1e6d`). Decoder-specific re-narrowing named as candidate awaiting open-question #1.

---

## Promotion criteria (when to consolidate to findings.md)

- **Positive consolidation** — top-line claim is already ACTIVE in findings.md at this mechanism-reading scope; further narrowing lands as findings-revision commits (not arc promotions). Promotion complete.
- **Decoder-specific re-narrowing** (contingent) — if the decode-consistent follow-up shows `R₂_decoded` patterns diverge between Arm A and BP_TOPK cells, the arc re-narrows in findings.md: mechanism name updates to reflect decoder-specific tail structure; scope tag updates; new review-history entry cites the decode-consistent chronicle's commit.
- **Abandonment** — not applicable at this stage; arc has active open questions and ongoing experimental support.
