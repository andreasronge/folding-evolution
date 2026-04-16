# Pre-registration: §v2.16 — Regime-shift benchmark on chem-tape (central theory prediction)

**Status:** DEFERRED · 2026-04-16 · pending DEAP infrastructure + headline-stakes sign-off

> **Deferred 2026-04-16.** Scoping investigation confirmed:
>
> - DEAP is **not installed** (`pyproject.toml` dependencies: numpy, matplotlib, mlx, pyyaml only).
> - **No existing DEAP tree-GP runner** exists in the codebase. Building one is a ~150-200 LoC module with primitive-set matching, fitness-function matching, task-alternation wiring, and per-generation logging.
> - This prereg commits to a **headline-narrowing** outcome under FAIL
>   (the project's current "folding adapts, direct encoding can't" result
>   would become folding-specific). User acknowledgement of that stake is
>   required before commit.
>
> The draft prereg body below reflects the full design. Before promotion
> from DEFERRED to QUEUED, the user must:
>
> 1. Authorize the DEAP infrastructure build (~2-3h engineering + test + review).
> 2. Acknowledge the headline-narrowing stake under FAIL outcome.
> 3. Confirm the Option B task-pair choice (§v2.3 `sum_gt_{5,10}_slot`).

## Question (one sentence)

Does chem-tape (BP_TOPK, then Arm A) recover faster than a matched DEAP tree-GP baseline after task-regime shifts (alternation every N generations), as theory.md's central prediction (§The Central Prediction) requires for the folding/chem-tape vs direct-encoding headline to generalize beyond the folding track?

## Hypothesis

theory.md's central prediction — based on Altenberg's constructional selection framework — is that representations exposing a **body-invariant route** (chem-tape's demonstrated mechanism, per `findings.md#op-slot-indirection` and `#constant-slot-indirection`) should recover from task-regime shifts faster than representations that must re-discover compositional structure per regime (direct tree GP).

This prediction has been tested on the **folding** track (the project's current headline result, per CLAUDE.md "Key Findings" #2) but has **never been tested on chem-tape**. The v2 suite is entirely fixed-task or narrow alternation within a single pair-type. A clean regime-shift result on chem-tape would:

1. **Generalize the folding headline to a second representation.** Strong positive paper-level result.
2. **Narrow the paper claim if null.** Folding's regime-shift advantage does not automatically extend to chem-tape — the claim becomes "folding-specific."
3. **Differentiate the two decoder arms.** If BP_TOPK beats DEAP but Arm A doesn't, the effect is specifically about the body-invariant-route mechanism (which BP_TOPK enables and Arm A does not at 6-token bodies — per `findings.md#constant-slot-indirection` decoder-arm caveat).

## Setup

> **USER REVIEW NEEDED (design decision 5):** task pair choice.
>
> future-experiments.md §4a offers two task-pair candidates:
>
> **Option A — F_AND / F_OR (the paper's "compositional depth" pair).** Theoretically principled, but F_AND is already known to be proxy-trapped (`findings.md#proxy-basin-attractor`, 0/20 at all tested configurations). A regime-shift over F_AND and F_OR would confound the regime-shift effect with the proxy-basin effect — chem-tape might "lose" not because it can't shift regimes but because it can't solve F_AND at all.
>
> **Option B — §v2.3 `sum_gt_5_slot` / `sum_gt_10_slot` (the body-invariant pair).** Clean: both tasks are known solvable (80/80 BOTH under task-alternation at period=300). This directly tests whether shorter-period alternation (e.g., period=10) still preserves the body-invariant-route mechanism, and whether tree-GP recovers as fast. Less glamorous (not AND/OR) but mechanism-valid.
>
> **Option C — A decorrelated-sampler F_AND / F_OR pair (§v2.4-proxy-2 design).** Removes the proxy-basin confound by using the dual-decorrelated sampler where AND-composition IS solvable. Needs pre-sweep verification that F_OR under the same decorr sampler is ALSO solvable at some reasonable rate. Technically clean but higher setup cost.
>
> **Default below assumes Option B (§v2.3 pair, period=10).** Rationale: the primary research question is mechanism transfer between representations on a task family that chem-tape _can_ solve. Adding the F_AND proxy confound to the regime-shift axis muddies the test of theory.md's prediction. A clean B result (chem-tape wins on the pair where it's known to work) is the strongest evidence for the theoretical claim; adding the harder F_AND/F_OR variant is a follow-up, not the primary.
>
> Please confirm or override.

> **USER REVIEW NEEDED (design decision 6):** DEAP tree-GP baseline.
>
> future-experiments.md references "matched DEAP tree-GP baseline." Two sub-decisions:
>
> **6a. Does the DEAP tree-GP baseline for alternation on the §v2.3 task pair already exist in the codebase?** Recent commits show `psb2-sanity-probe.md` plan for a DEAP comparison but I couldn't find a committed alternation sweep. If it doesn't exist, this prereg must include a ~1-2h infrastructure investment to wire up DEAP on these tasks.
>
> **6b. Which DEAP configuration?** Proposal: DEAP GP with primitive set including `INT_ADD`, `INT_GT`, `SUM_LIST`, `MAX_LIST`, `IF_ELSE` (matching the semantic ops available in v2_probe). Tree depth cap matched to chem-tape tape_length=32 approximate expressivity. Population size matched to chem-tape pop=1024. Generations matched to chem-tape gens. Fitness function identical.
>
> **Default below assumes 6a = infrastructure does not exist (budget ~2h for wiring) and 6b = DEAP config as proposed above.** Please confirm or override; if 6a is wrong, reduce the setup cost estimate.

- **Sweep files:** `experiments/chem_tape/sweeps/v2/v2_16_regime_<arm>.yaml` for arm ∈ {bp_topk, arm_a, deap_treegp}
- **Arms / conditions:** 3 arms (chem-tape BP_TOPK, chem-tape Arm A, DEAP tree-GP)
- **Task schedule:** alternate `sum_gt_5_slot` / `sum_gt_10_slot` every **period = 10** generations for total gens = 200 (20 regime shifts)

  > Secondary periods {5, 20} as follow-up if primary gives clean signal — do NOT run up-front; the cost is 3× and period=10 is the pre-registered primary.

- **Seeds:** 0-19 per arm
- **Fixed params:** chem-tape pop=1024, tape_length=32, v2_probe alphabet; DEAP pop=1024 with matched primitive set
- **Est. compute:** ~2-3h at 10 workers (3 arms × 20 seeds × 200 gens). DEAP wiring: +1-2h one-time.

**Principle 20 audit:** label functions unchanged (§v2.3 pair). Input distribution and sampler unchanged. The **alternation period** changes (300 → 10) but this is a selection-schedule knob, not a training-distribution knob. Principle 20 does **not** apply to selection-schedule changes, but note that a very-short period could interact with class balance per-window (within any 10-generation window, only one task is active, so the effective per-window label balance is the per-task balance). Per-window class balance is auto-balanced by the sum-gt tasks at their specified thresholds, but log per-task balance as a diagnostic.

## Baseline measurement (required)

- **Baseline quantity:** mean fitness over the full 200-generation run for each arm; recovery speed = mean generations to recover to within 10% of pre-shift fitness after each of the 20 regime shifts.
- **Reference anchors:**
  - §v2.3 BP_TOPK at period=300: 20/20 BOTH at gen=1500. Period=10 is the new regime; reference is this sweep itself.
  - §v2.11 Arm A at period=300: 20/20 BOTH (same pair). Reference is this sweep itself.
  - DEAP on §v2.3: **no committed baseline**. This sweep is the DEAP baseline.
- **Measurement:** all three arms in this sweep.

## Internal-control check (required)

- **Tightest internal contrast:** the three-arm comparison on the same task, same seeds, same regime schedule. That IS the internal control — three representations under identical task pressure.
- **Are you running it here?** Yes.
- **Additional within-chem-tape control:** the BP_TOPK vs Arm A comparison isolates the body-invariant-route mechanism (BP_TOPK has it on 4-token bodies per §v2.11; Arm A has it on 4-token bodies per §v2.11 but not on 6-token bodies per §v2.6 Pair 1 follow-ups). On the §v2.3 4-token body, both should preserve the mechanism — the question is whether the mechanism helps under regime-shift.

## Pre-registered outcomes (required — at least three)

Let `R_BP`, `R_A`, `R_DEAP` = mean recovery speed (generations-to-within-10%-of-pre-shift) averaged over the 20 shifts per arm.
Let `F_BP`, `F_A`, `F_DEAP` = mean terminal fitness over last 20 generations per arm.

| outcome | criterion | interpretation |
|---------|-----------|----------------|
| **PASS — chem-tape wins, both arms** | `R_BP ≤ R_DEAP − 3` AND `R_A ≤ R_DEAP − 3` AND `min(F_BP, F_A) ≥ F_DEAP − 0.05` | **The headline result.** Chem-tape's body-invariant-route mechanism recovers faster than direct tree-GP on this pair, both decoder arms. Generalizes the folding-track headline. |
| **PASS — BP_TOPK wins, Arm A doesn't** | `R_BP ≤ R_DEAP − 3` AND `R_A > R_DEAP − 1` | The mechanism works for BP_TOPK but not Arm A — consistent with the decoder-arm caveat in findings. Narrower positive. |
| **PARTIAL — chem-tape mean higher but recovery similar** | `F_BP > F_DEAP + 0.05` AND `|R_BP − R_DEAP| ≤ 2` | Chem-tape produces higher-fitness solutions per-window but doesn't **adapt faster**. Suggests higher-quality routines, not faster adaptation — narrows the theoretical claim. |
| **INCONCLUSIVE** | `|R_BP − R_DEAP| ≤ 2` AND `|F_BP − F_DEAP| ≤ 0.05` | No distinguishable difference on this pair/period. Try larger period (20) or harder task; this pair may be too easy. |
| **FAIL — DEAP wins** | `R_DEAP < R_BP − 2` OR `F_DEAP > F_BP + 0.05` | Direct tree-GP recovers faster. **Narrows the folding headline**: the folding-track adaptation advantage does not extend to chem-tape. Paper claim must narrow to "folding-specific." |

**Threshold justification:** 3-generation recovery-speed gap is the minimum detectable difference at n=20 with 20 shifts per run (effective n = 20 × 20 = 400 shift-observations). Terminal-fitness gap of 0.05 is conventional; observations in §v2.3 showed train/holdout gap of 0.0156 so 0.05 is comfortably above noise.

## Degenerate-success guard (required)

- **Too-fast recovery (R < 1):** if R_BP ≈ 0, chem-tape is retaining a single body across shifts (slot-indirection absorbs the variation — `findings.md#constant-slot-indirection` IS this mechanism) without actually "recovering." This is **a real positive for the mechanism, not a degenerate result** — but the narrative frame changes: chem-tape doesn't "recover faster," it avoids needing to recover. Classification: still PASS, with the narrative adjusted.
- **Never-solves on DEAP:** if DEAP's mean fitness stays near-random, it's not solving the task family at all. This is possible on the §v2.3 pair (the task is chem-tape-tuned). Test this up front with a fixed-task DEAP sanity run at period=∞ (single task, no alternation) — if DEAP can't solve even the fixed task, the regime-shift comparison is uninformative.
- **Task-window contamination:** if period=10 is too short for DEAP's tree-GP to produce offspring before the regime shifts, DEAP's null is an artifact of periodicity, not adaptation capacity. Report as a separate diagnostic.
- **Detection:** DEAP sanity run at period=∞ pre-sweep; monitor per-window fitness trajectories for all three arms; decode chem-tape winners for body-invariant-route confirmation.

## Statistical test (if comparing conditions)

- **Primary:** per-shift recovery-speed distribution compared across arms via paired Wilcoxon (seeds paired across arms on matched seeds; shifts as repeated measures per seed).
- **Secondary:** terminal-fitness comparison via paired Wilcoxon across arms.
- **Significance threshold:** α = 0.05, two-sided. Multiple comparison: three arm pairs (BP_TOPK vs DEAP, Arm A vs DEAP, BP_TOPK vs Arm A) — apply Bonferroni (α_corrected = 0.017) for the claim-level significance.

## Diagnostics to log (beyond fitness)

- Per-seed × per-arm full fitness trajectory (every generation)
- Per-shift recovery-speed distribution per arm
- Body-invariant-route confirmation on chem-tape winners (decode_winner.py check; which task was the winner evolved on at final gen)
- DEAP population size, mean tree depth, mean program length per generation
- Per-window class balance (should be constant per task, but verify)
- Pre-sweep DEAP fixed-task sanity result

## Scope tag (required for any summary-level claim)

**If PASS — headline result:** `across-representation · n=20 per arm · at pop=1024 gens=200 period=10 v2_probe · on §v2.3 sum_gt_{5,10}_slot pair · chem-tape recovers faster than DEAP tree-GP under task-regime shift (both decoder arms / BP_TOPK only)`

## Decision rule

- **PASS — both arms →** major headline. Promote to findings.md as a cross-representation claim ("Chem-tape's body-invariant-route mechanism produces adaptation advantage over direct tree-GP on regime-shifted tasks"). Triggers a paper-level narrative update: folding-track headline now generalizes to chem-tape.
- **PASS — BP_TOPK only →** positive but narrower. Document decoder-arm dependence (consistent with existing findings). Promote to findings.md with decoder-arm scope tag.
- **PARTIAL — higher mean, similar recovery →** narrow theoretical claim: chem-tape solves better per-window but doesn't adapt faster. Queue a longer-period / harder-task follow-up.
- **INCONCLUSIVE →** the §v2.3 pair is too easy for regime-shift to produce differential signal. Queue the same experiment on a harder pair (possibly Option C, decorr F_AND/F_OR, once §v2.4-proxy-4 resolves discoverability vs maintainability).
- **FAIL — DEAP wins →** narrow paper headline. Folding-track adaptation advantage does NOT generalize to chem-tape on this task family. Update CLAUDE.md "Key Findings" and methodology.md. This is a serious narrowing; triggers promote-finding review and likely a supersession-style rewrite of current framing.

---

*Audit trail.* Five outcome rows including PARTIAL and INCONCLUSIVE (principle 2). Anchors: §v2.3 (BP_TOPK 20/20), §v2.11 (Arm A 20/20) at period=300; no DEAP baseline exists yet (this sweep establishes it). Internal control is the three-arm comparison on shared seeds (principle 1). Degenerate-success candidates include too-fast recovery via slot-indirection absorbing variation (principle 4). Principle 20 noted but not directly triggered. Decision rule commits to findings.md, CLAUDE.md, and paper-headline edits per outcome (principle 19) — the highest-stakes commitment of this prereg batch.

**USER REVIEW CHECKLIST** (before commit):
- [ ] Approve Option B (§v2.3 pair) vs Option A (F_AND/F_OR) vs Option C (decorr F_AND/F_OR)
- [ ] Confirm DEAP tree-GP infrastructure status (6a: exists vs needs building; if building, add ~2h budget)
- [ ] Approve period = 10 primary; {5, 20} as contingent follow-ups
- [ ] Approve 3-generation recovery-speed gap threshold
- [ ] Confirm commit-hash gating
- [ ] Acknowledge: a FAIL outcome narrows the project's current headline — this is a high-stakes prereg
