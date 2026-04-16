# Pre-registration: §v2.15 — Systematic decoder-ablation grid (doubles as Part 1 Phase 0 diagnostic gate)

**Status:** QUEUED · target commit `TBD` · 2026-04-16

## Question (one sentence)

Does any parameterization of the BP_TOPK decoder's {K, bond_protection, min_run_length} knobs lift §v2.6 Pair 1 (6-token mixed-type body, 4/20 BOTH at reference config) measurably toward the §v2.3 ceiling, **without losing §v2.3's 20/20 BOTH** — establishing whether the chemistry-knob search space has useful structure before committing to the Part 1 meta-learning ES machinery?

## Hypothesis

The Part 1 program (meta-learning the developmental system) costs substantial machinery. Its leverage depends on a prior that is currently untested: **"there exist decoder configurations the current pointwise reference does not sit on, where hard bodies become discoverable while easy bodies remain solved."** Three disjoint outcomes:

1. **Leverage exists.** At least one grid cell produces `Pair1_BOTH ≥ 12/20` while `v2.3_BOTH ≥ 18/20`. The chemistry search space has useful structure; Part 1 ES machinery is worth building.
2. **No joint cell.** Every Pair 1-lifting cell collapses §v2.3. The chemistry knobs trade ceiling against floor; Part 1 would need to search simultaneously over decoder _and_ alphabet/body, enlarging scope.
3. **Uniform null.** No cell lifts Pair 1 above §v2.14c preserve-4× reference (8/20 BOTH). Chemistry knobs lack the leverage to move hard-body discovery; Part 1 meta-learning should redirect toward executor-rule / body-topology interventions rather than bonding parameters.

The future-experiments.md Phase 0 framing explicitly assigns this experiment the role of a gate on Part 1.

## Setup

**Design decision (resolved 2026-04-16):** narrow 2×3 grid over **two existing config knobs** (K, bond_protection_ratio). Option A-style 3×3×3 was rejected because `min_run_length` is **not in the current `ChemTapeConfig`** — adding it is a separate Rust+Python engineering task and deserves its own prereg. The 2×3 grid is still gate-adequate: if no cell with (K, bp) alone lifts Pair 1 while preserving §v2.3, the chemistry-knob direction is limited and Part 1 ES should expand scope before committing to bonding-parameter meta-learning.

**Grid (final):**
- `K` ∈ {3, 5}  (v2 default = 3; §v2.13 already ran K=5 independently — we run here fresh for matched-commit comparison)
- `bond_protection_ratio` ∈ {0.0, 0.5, 1.0}  (0.0 = strict protection, 0.5 = current default, 1.0 = no protection / uniform mutation)

6 cells total. All 6 run fresh (even cells matching existing committed results) to avoid cross-commit baseline drift.

- **Sweep files:** one YAML per task (2 total). Grid expands within each YAML via {K, bond_protection_ratio, seed}.
  - `experiments/chem_tape/sweeps/v2/v2_15_grid_v2_3.yaml`
  - `experiments/chem_tape/sweeps/v2/v2_15_grid_pair1.yaml`
- **Seeds:** 0-19 (disjoint from the §v2.3 seed expansion blocks 20-79, which use the reference cell)
- **Fixed params:** pop=1024, gens=1500, v2_probe alphabet, tape_length=32, executor rule = **preserve** (current project default)
- **Est. compute:** ~4-5h wall at 10 workers (6 cells × 2 tasks × 20 seeds = 240 runs)
- **Related experiments:** §v2.3 (pinned anchor K=3 bp=0.5 = 20/20), §v2.6 Pair 1 (pinned anchor = 4/20), §v2.13 K=5 (independent prior)

**Future grid extension (flagged for separate prereg):** `min_run_length` and `tape_length` axes would add additional decoder surface. `min_run_length` needs a new config field + executor wiring. These are out of scope for §v2.15 and queued as future engineering.

**Principle 20 audit:** label functions, input distribution, and sampler unchanged from §v2.3 and §v2.6 Pair 1. Only decoder parameters change. Principle 20 **not triggered**.

## Baseline measurement (required)

- **Baseline quantity:** reference-cell BOTH-solve rate per task.
- **Values (measured, pinned):**
  - §v2.3 reference: 20/20 BOTH (commit `e3d7e8a` plus seed expansion `c2d38ec` etc.) — **ceiling**.
  - §v2.6 Pair 1 reference: 4/20 BOTH (commit `0230662` / `344e4de`) — **floor**.
  - §v2.13 k=5 on these tasks: existing independent grid cell, serves as a sanity anchor.
- **Measurement of new cells:** this sweep measures them directly.

## Internal-control check (required)

- **Tightest internal contrast:** reference cell vs each grid cell, on both tasks, on the same seeds. The grid IS the internal control.
- **Are you running it here?** Yes.
- **External validity note:** the grid is within-decoder-family (BP_TOPK parameter space). Does not test cross-decoder (Arm A) or cross-alphabet variation — those are separate axes already covered by §v2.11/§v2.12/§v2.13.

## Pre-registered outcomes (required — at least three)

Per-cell classification (evaluated jointly on §v2.3 alt and Pair 1 alt):

| cell outcome | §v2.3 BOTH criterion | Pair 1 BOTH criterion | interpretation |
|---|---|---|---|
| **JOINT-LIFT** | ≥ 18/20 | ≥ 12/20 | Cell lifts Pair 1 without losing §v2.3. **Part 1 gate PASSES** at this cell. |
| **LIFT-AT-COST** | < 18/20 | ≥ 12/20 | Cell lifts Pair 1 but collapses §v2.3. Knobs trade ceiling for floor. Part 1 gate partial. |
| **CEILING-STABLE-NULL** | ≥ 18/20 | ≤ 8/20 | Cell preserves §v2.3 but does nothing for Pair 1. Knobs useless at this direction. |
| **GLOBAL-COLLAPSE** | < 18/20 | ≤ 8/20 | Cell is strictly worse than reference on both. Knob direction harmful. |
| **INTERMEDIATE** | any | Pair 1 ∈ [9, 11] | Borderline; expand to larger n for confirmation. |

Aggregated grid-level outcomes (across all 6 cells):

| grid outcome | criterion | Part 1 implication |
|---|---|---|
| **PASS — leverage found** | At least one cell is JOINT-LIFT | Chemistry-knob space has useful structure. Part 1 ES machinery over these knobs is worth building. Locate the optimum via Part B (expand JOINT-LIFT cells to full 3×3×3 if Option B was used). |
| **PARTIAL — tradeoff-only** | ≥ 1 LIFT-AT-COST cell, 0 JOINT-LIFT | Chemistry knobs trade §v2.3 ceiling for Pair 1 floor. Part 1 ES is premature; needs a richer search space (multi-task meta-objective, or decoder + body joint search). |
| **NULL — uniform no-lift** | All cells CEILING-STABLE-NULL or GLOBAL-COLLAPSE (no cell lifts Pair 1 ≥ 12/20) | Chemistry knobs lack leverage on this axis. Redirect Part 1 toward executor-rule / body-topology / extraction-layer interventions. |
| **CATASTROPHIC** | All cells GLOBAL-COLLAPSE | Something is wrong with the sweep — investigate before interpreting. |

**Threshold justification:** Pair 1 ≥ 12/20 matches the "scales-bar" convention from §v2.6 (per `Plans/prereg_v2_6.md`). §v2.3 ≥ 18/20 is the existing 20/20 ceiling minus ±2 noise.

## Degenerate-success guard (required)

- **K=5 artifact:** §v2.13 already ran k=5 on these tasks; this grid's k=5 cell should reproduce within ±2 (cross-commit sanity). Large divergence is a code-drift flag.
- **bond_protection=1.0 artifact:** at bp=1.0, no bonds are ever broken by mutation in BP_TOPK semantics. This may collapse the search to a single initial-bonding configuration (diversity collapse). Detect via generation-0 vs final population-entropy ratio; a collapsed ratio is diagnostic.
- **min_run_length=2 artifact:** forcing longer runs may mechanically lift Pair 1 (whose canonical body is 6 tokens) while ceiling-clipping §v2.3 (whose canonical body is 4 tokens and thus can't satisfy min_run=2). This is **a real effect, not a degenerate one** — but we should NOT read it as "chemistry knobs have leverage" if it's just "min_run=2 filters for bodies ≥ 6 tokens." Attractor inspection distinguishes.
- **Too-clean (JOINT-LIFT at every cell):** would indicate a baseline-drift issue or a misconfiguration in the reference cell. Cross-check against committed §v2.3 / §v2.6 Pair 1 results.
- **Detection:** `decode_winner.py` on all 16 × 20 = 320 winners; tabulate canonical-body-family rates per cell; report population-entropy trajectory per cell.

## Statistical test (if comparing conditions)

- **Primary:** descriptive per-cell counts vs reference.
- **Per-cell:** paired McNemar against reference on shared seeds for cells flagged as JOINT-LIFT or LIFT-AT-COST candidates (suggestive).
- **Significance threshold:** α = 0.05, two-sided; acknowledge multiple-testing load across 8 cells — require at least two LIFT categorizations for a finding claim (single hits with marginal p may be noise).

## Diagnostics to log (beyond fitness)

- Per-cell × per-seed BOTH-solve + best-fitness (both tasks)
- Attractor-category classification per cell per task (via `decode_winner.py`)
- Canonical-body-family rate per cell
- Generation-0 vs final population-entropy (diversity-collapse diagnostic)
- Mean program length per cell (min_run_length sanity)
- Seed overlap with §v2.3 and §v2.6 Pair 1 reference solvers per cell

## Scope tag (required for any summary-level claim)

**If PASS — leverage found:** `within-decoder-family · n=20 · at BP_TOPK v2_probe with grid {K ∈ {3,5}, bond_protection_ratio ∈ {0.0, 0.5, 1.0}} · on §v2.3 alt + §v2.6 Pair 1 alt · chemistry-knob space has leverage on 6-token body discovery without collapsing 4-token body ceiling`

**If NULL:** no claim enters findings.md. Chronicle as "Part 1 gate closed at the (K, bond_protection) axes; chemistry-knob leverage is bounded within the tested range."

## Decision rule

- **PASS — leverage found →** expand the JOINT-LIFT cell(s) from 2×2×2 to full 3×3×3 (Part B, separate prereg) to locate optimum. Draft Part 1 Phase 1 (ES + soft bonds, `5+1`) prereg with this grid's JOINT-LIFT cell as starting point.
- **PARTIAL — tradeoff-only →** document the cell-level tradeoff; do NOT draft Part 1 Phase 1 yet. Queue a multi-task meta-objective design pass.
- **NULL →** chronicle the null; redirect Part 1 roadmap toward executor-rule interventions (§v2.14 arc continuation) and body-topology interventions (alphabet extension). ES machinery over chemistry knobs is explicitly deprioritized.
- **CATASTROPHIC →** investigate infrastructure before any Part 1 work.

---

*Audit trail.* Joint per-cell and grid-level outcomes, each ≥ 3 rows (principle 2). §v2.3 and §v2.6 Pair 1 anchors from committed results (principle 6). Internal control is the grid against reference on shared seeds (principle 1). Degenerate-success candidates include min_run_length mechanical artifact and diversity collapse (principle 4). Principle 20 not triggered. Decision rule commits to Part 1 roadmap contingent on grid outcome (principle 19) — which is the load-bearing commitment this experiment is designed to make.

*Resolved design decisions: 2×3 grid over (K, bond_protection_ratio) using existing config knobs; min_run_length/tape_length deferred to separate prereg; JOINT-LIFT thresholds §v2.3 ≥ 18/20 AND Pair 1 ≥ 12/20; commit-hash gated.*
