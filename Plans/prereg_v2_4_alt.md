# Pre-registration: §v2.4-alt — body-matched compositional pair

**Status:** QUEUED · target commit `80d5320` (chem-tape code clean; working tree
has unrelated untracked dirs) · 2026-04-15

Derived from the doc draft at [docs/chem-tape/experiments-v2.md §v2.4-alt](../docs/chem-tape/experiments-v2.md#section-v2-4-alt---body-matched-compositional-pair-disentangles-the-v2-4-confound).
This file stamps the commitment at a specific commit and closes two gates the
doc draft under-specified (degenerate-success candidates, scope tag).

## Question (one sentence)

Is §v2.4's 0/20 driven by (a) compositional depth through `IF_GT`, (b) the
`CONST_0`-at-start-of-run decode-position constraint specific to the AND body,
or (c) a proxy-predicate attractor specific to the `sum>10 AND max>5` label?

## Hypothesis

The `IF_GT`-plus-`CONST_0`-prefix compositional body, when held constant across
two tasks differing *only* in a `THRESHOLD_SLOT`-bound integer, should behave
like §v2.3 — i.e., the slot-constant indirection mechanism should absorb the
threshold variation and both tasks should solve at high rates. If they don't,
the compositional body itself (independent of any proxy or decode-position
constraint) is the blocker, and §v2.4's "does not scale on compositional
depth" reading holds.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_4_alt.yaml`
  (task-alternating on the two new tasks)
- **Fixed-baseline sweep:** `experiments/chem_tape/sweeps/v2/v2_4_alt_fixed_baselines.yaml`
- **Tasks (new — to be added to tasks.py):**
  - `compound_and_sum_gt_5_max_gt_5_slot` (threshold=5)
  - `compound_and_sum_gt_10_max_gt_5_slot` (threshold=10)
- **Canonical body template (identical across both tasks):**
  `CONST_0 INPUT REDUCE_MAX CONST_5 GT INPUT SUM THRESHOLD_SLOT GT IF_GT`
  Label: `1 iff (max(input) > 5) AND (sum(input) > threshold)`.
- **Alphabet:** `v2_probe`.
- **Fixed params:** pop=1024, gens=1500, n_examples=64, holdout=256, arm=BP_TOPK,
  topk=3, bond_protection_ratio=0.5, tape_length=32 — matched to §v2.4 pre-reg.
- **Seeds:** 0..19 (n=20). Task-alternating period=300.
- **Related experiments:** §v2.3 (body-invariant constant-indirection, 80/80),
  §v2.4 (compositional {AND,OR}, 0/20 at 1× and 4× compute), §v2.4-proxy
  (diagnostic follow-up).
- **Est. compute:** ~20 min at 4 workers (alternation sweep) + ~20 min
  (fixed baselines, 2 tasks × 20 seeds).

## Baseline measurement (required)

- **Baseline quantity:** `F_AND_{5,10}` — per-task fixed-task solve rate at
  matched compute.
- **Measurement:** the fixed-baseline sweep above, run first.
- **Prior reference points** (baseline-relative thresholds calibrate against
  these, per methodology §6):
  - §v2.3 passed at **20/20 BOTH** fixed-task baselines and **20/20 BOTH**
    alternation. That is the "scales" shape.
  - §v2.4 fixed F_AND = **0/20** (mean 0.92). That is the "doesn't scale" shape.
  - Alternation threshold is expressed relative to `Fmin = min(F_alt_5, F_alt_10)`
    with an absolute floor — **BOTH ≥ max(Fmin − 3, 12)** counts as "scales"
    (same formula §v2.4 used; principle 6-compliant).

## Internal-control check (required)

- **Tightest internal contrast:** this experiment *is* the internal control
  for §v2.4. The canonical bodies are **token-sequence-identical** across the
  two tasks — they differ only in the task-bound `threshold` integer. Analogous
  to §v2.3's design at one compositional level up.
- **Are you running it here?** yes.

## Pre-registered outcomes (required — at least three)

| outcome | quantitative criterion | interpretation |
|---|---|---|
| **PASS — clean** | BOTH fixed baselines ≥ 15/20 **AND** alternation BOTH ≥ max(Fmin − 3, 12) | Decode-position constraint is **not** the blocker; §v2.4's "does not scale on compositional depth" reading falls apart. The slot-indirection mechanism extends to compositional bodies when decode-position is held constant. Claim scope narrows §v2.4's failure to the specific `sum_gt_10 AND max_gt_5` label function / proxy. |
| **PASS — partial** | one baseline in [10, 14], the other ≥ 15, alternation BOTH ≥ Fmin − 5 | Mechanism partially extends but one threshold variant is harder. Task-specific threshold effect — report, don't over-interpret. |
| **INCONCLUSIVE** | mixed (one ≥ 15, one ≤ 3), OR both in [4, 14] | Task-specific effects matter; next experiment disambiguates. |
| **FAIL** | BOTH fixed baselines ≤ 3/20 | The `IF_GT`-plus-`CONST_0`-prefix compositional shape is genuinely hard regardless of the label function. §v2.4's "does not extend to compositional depth" reading generalises. The mechanism has a compositional-depth ceiling independent of proxy attractors. |

## Degenerate-success guard (required — closing a gap in the doc draft)

A too-clean PASS (e.g., 20/20 BOTH with near-zero holdout gap, mirroring §v2.3)
must trigger mechanism inspection, not a silent claim upgrade. Candidate
degenerate mechanisms:

1. **Canonical-body rediscovery via slot-indirection:** evolution converges to
   the canonical body template on both tasks; threshold-slot absorbs the
   task-distinguishing variation. This is **not** a degenerate success — it
   *is* the hypothesis. But distinguish from:
2. **Trivial-predicate collapse:** evolution finds a predicate that solves both
   tasks by ignoring the threshold entirely (e.g., fixed `max > 5` ignoring
   `sum` — trivially 0.50 under balanced training, so only a problem if
   training samples happen to correlate). Detect via: per-task winner-fitness
   distribution (should separate by threshold if slot binding is doing work),
   plus direct genotype decode comparing the best-of-run program across
   threshold=5 vs threshold=10 seeds (should be token-identical if slot
   indirection is the mechanism).
3. **AND-reduction artifact:** if `max > 5` alone is a strong proxy for
   `max>5 AND sum>threshold` under the [0,9] input distribution at either
   threshold, evolution might still converge to the §v2.4 proxy attractor.
   Detect via: check baseline fitness distribution — if 0.85–0.97 like §v2.4
   with 0/20 solves, same attractor is present.

**Inspection commitment:** on any outcome with ≥15/20 BOTH, run a
winner-architecture decode on all 20 seeds of both tasks before promoting the
claim. Log to the chronicle entry as part of the result.

## Statistical test (if comparing conditions)

- **Test:** paired McNemar on shared seeds (0..19) comparing alternation BOTH
  vs Fmin. One-sided α=0.05. Reported alongside raw solve counts.

## Diagnostics to log (beyond fitness)

- Per-task fixed-baseline solve counts and holdout gaps.
- Alternation flip-transition cost (matches §v2.3's 399/400 zero-cost metric).
- Winner-genotype decode on any seed with train ≥ 0.999 (per degenerate-success guard).
- Per-task best-of-run fitness distribution (to flag §v2.4-style attractors).

## Scope tag (required for any summary-level claim)

**If this experiment passes, the claim enters findings.md scoped as:**
`within-family / n=20 / at pop=1024 gens=1500 BP_TOPK(k=3,bp=0.5) / on
IF_GT-compositional body-matched pair (threshold ∈ {5,10})`

Explicitly **not** claiming: "scales to compositional depth in general,"
"cross-family compositional scaling," or "mechanism is universal across
compositional bodies." §v2.6 is the breadth check; this is a precision
narrowing of §v2.4, not a generalization.

## Decision rule

- **PASS-clean →** supersede §v2.4 verdict: rewrite the §v2.4 claim to
  "compositional-depth failure was specific to the `sum>10 AND max>5` label
  and proxy attractor, not to IF_GT+CONST_0-prefix bodies generally." Add a
  §v2.4 supersession block (methodology §13). Then run §v2.6 to breadth-check.
- **PASS-partial →** report both; narrow the §v2.4 claim modestly
  ("partially extends"); still run §v2.4-proxy to disambiguate the remaining
  failure mode.
- **INCONCLUSIVE →** run §v2.4-proxy next to see which of (b) decode-position
  vs (c) proxy-attractor is doing the work.
- **FAIL →** §v2.4's compositional-depth ceiling claim holds cleanly; §v2.4-alt
  result *replaces* the confounded "maybe decode-position" framing with
  "compositional body itself is the blocker." Do NOT run §v2.4-proxy (no
  longer informative).

---

*Audit trail.* This prereg was derived from the in-doc draft at
`docs/chem-tape/experiments-v2.md §v2.4-alt` (commit 80d5320). Gaps closed:
(a) explicit degenerate-success candidates and inspection commitment (Gate 3,
methodology §4), (b) baseline-relative phrasing of thresholds made explicit
(Gate 4, methodology §6), (c) scope tag committed (methodology §18). The
doc draft's three outcomes are preserved; one PASS-partial row was added
to cover asymmetric-threshold results.
