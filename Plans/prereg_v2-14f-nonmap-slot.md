# Pre-registration: §v2.14f — Non-MAP slot binding (distinguishes type-chain vs MAP-family for consume effect)

**Status:** DEFERRED · 2026-04-16 · pending alphabet-extension decision

> **Deferred 2026-04-16.** The clean test of "MAP-family-specific vs
> type-chain-driven" requires a non-MAP op (e.g., `FILTER_EQ_R`) at slot_12.
> Scoping investigation confirmed `FILTER_EQ` is **not** registered in the
> `v2_probe` alphabet (alphabet.py line 55-73; alphabet is locked at 22 ids
> per architecture-v2.md). Candidate REDUCE-based substitutions would
> simultaneously change op-family, type-chain, and body topology — a
> confounded design that cannot cleanly distinguish the two readings.
>
> Options for the user's call:
>
> 1. **Add `v2_probe_filter` alphabet extension** adding `FILTER_EQ_R` at id
>    24 (pattern established by `v2_split` at ids 22-23). ~50-100 LoC +
>    tests + executor dispatch + task wiring. Dedicated engineering prereg.
> 2. **Accept the confounded REDUCE-based design**, with scope tags that
>    explicitly note the type-chain+family-simultaneously-changed confound.
>    Cheaper but weaker science.
> 3. **Defer the question** pending a more motivating downstream finding
>    (e.g., if §v2.14g narrows scope further, the MAP-family vs type-chain
>    question may not remain load-bearing).
>
> The draft prereg body below assumes option (1) if the user authorizes it.

## Question (one sentence)

Does the safe-pop consume solve-rate lift replicate when slot_12 binds a **non-MAP** op (breaking MAP-family-specificity), or is the effect specific to the MAP_EQ_* op family?

## Hypothesis

§v2.14e replicated the consume lift (P=4/20 → C=8/20) on a second MAP-family op (MAP_EQ_E vs MAP_EQ_R in §v2.14). Identical solver sets across the two slot bindings are consistent with both (a) type-chain-driven (str→charlist→intlist→int) and (b) MAP-family-specific readings. This experiment substitutes a non-MAP op that **preserves the str-domain input processing but breaks the MAP-family signature**, so the two readings make distinguishable predictions:

- **Type-chain-driven:** the lift replicates on any op producing the same str→…→int chain, regardless of family.
- **MAP-family-specific:** the lift attenuates or vanishes under non-MAP ops with different internal semantics.

> **USER REVIEW NEEDED (design decision 1):** which non-MAP op at slot_12?
>
> Candidate A — `FILTER_EQ_R` (or equivalent): str→filtered-str→… keeps the string-domain intermediate stage, cleanly isolates "MAP-family" as the only dimension changed. Same semantic output distribution as MAP_EQ_R (char-presence predicate); minimal baseline-difficulty shift expected.
>
> Candidate B — `REDUCE_MAX` or `REDUCE_SUM` on the charlist: charlist→int directly, skips the intlist intermediate. Changes the **type chain** as well as the op-family, so a null result is confounded (did the chain change break the effect, or the family change?). Explicitly worse as a clean disambiguator but is the only currently-available non-MAP op in v2_probe — **if FILTER_EQ is not implemented, REDUCE_SUM on charlist is the fallback and the experiment becomes a weaker test**.
>
> Default below assumes Candidate A (FILTER_EQ_R). If the op is not in the v2_probe alphabet, please either (a) add it (one line in the alphabet def + task wiring) or (b) approve the fallback to Candidate B with the confound noted in scope.

**Requires new task definitions:** `any_char_count_R_filtereq_gt_1_slot` and `any_char_count_R_filtereq_gt_3_slot` — identical semantic labels to §v2.14 R-count tasks but the canonical solver must route through FILTER_EQ at slot_12 instead of MAP_EQ_R. The target label function (count of R) is unchanged so difficulty comparability is preserved at the label level; only the canonical body structure changes.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_14f_nonmap_preserve.yaml`, `v2_14f_nonmap_consume.yaml`
- **Arms / conditions:** 2 executor rules (preserve, consume) × non-MAP slot binding = 2 sweeps
- **Tasks:** `{any_char_count_R_filtereq_gt_1_slot, any_char_count_R_filtereq_gt_3_slot}` alternation, period 300 (matches §v2.14)
- **Seeds:** 0-19
- **Fixed params:** pop=1024, gens=1500, BP_TOPK(k=3, bp=0.5), v2_probe alphabet, tape_length=32
- **Est. compute:** ~30 min (2 sweeps × ~15 min at 10 workers)
- **Related experiments:** §v2.14 R-count (P=4/20, C=8/20 under MAP_EQ_R), §v2.14e E-count (P=4/20, C=8/20 under MAP_EQ_E)

**Principle 20 audit:** label function identical to §v2.14 R-count (count of R ≥ threshold). Input distribution (length-16 strings over 53-char alphabet) unchanged. Sampler unchanged. Principle 20 **not triggered** — this is an op-family change, not a distribution change.

## Baseline measurement (required)

- **Baseline quantity:** BOTH-solve rate under preserve on the non-MAP pair. This is a NEW body topology — no prior baseline exists.
- **Measurement:** the preserve arm of THIS experiment is the baseline.
- **Expected value (calibration):** near 4/20 if FILTER_EQ produces a comparable search landscape to MAP_EQ. But FILTER_EQ may be easier (single-predicate body is shorter) or harder (different dependency order), and the preserve-arm result is the binding reference.

## Internal-control check (required)

- **Tightest internal contrast:** preserve vs consume on the SAME non-MAP pair, SAME seeds, SAME commit. The ablation IS the internal control.
- **Are you running it here?** Yes.
- **Cross-experiment anchor:** solver-set overlap with §v2.14 / §v2.14e (same label function, different required body) tests whether the effect is driven by the specific seeds' search trajectories vs the body topology.

## Pre-registered outcomes (required — at least three)

Let `P_NM` = preserve-arm non-MAP BOTH, `C_NM` = consume-arm non-MAP BOTH.

| outcome | quantitative criterion | interpretation |
|---------|------------------------|----------------|
| **PASS — replicates** | `C_NM ≥ P_NM + 4` AND `P_NM ∈ [1, 8]` (not swamped either direction) | Consume effect replicates outside the MAP family. The finding broadens from "MAP-family slot bindings" to "type-chain-driven, family-neutral." |
| **PASS — partial** | `C_NM ∈ [P_NM+1, P_NM+3]` AND `P_NM ∈ [1, 8]` | Directional lift present but smaller than §v2.14/§v2.14e. Op-family interacts with the effect; type-chain is part of the mechanism but not the whole story. |
| **SWAMPED** | `P_NM ≥ 18/20` OR `C_NM ≥ 18/20` with `P_NM` also high | Non-MAP body is easier; no mechanism signal. Log and move on. |
| **FAIL — no lift** | `|C_NM − P_NM| ≤ 1` AND `P_NM ∈ [1, 10]` | Consume does not help on the non-MAP body. The consume effect is MAP-family-specific at this budget. Narrows findings.md scope from "MAP-family slot bindings" to "MAP-family _necessary_." |
| **FAIL — consume worse** | `C_NM ≤ P_NM − 2` | Consume damages the non-MAP body. Unexpected; inspect. |

**Threshold justification:** +4 for PASS matches the §v2.14/§v2.14e effect size. The [1, 8] baseline window ensures we have room to measure ±4 without floor/ceiling effects. Swamp cutoff at 18/20 matches the §v2.6 prereg convention.

## Degenerate-success guard (required)

- **Swamp candidate:** if FILTER_EQ yields a shorter canonical body (e.g., 4-token vs 6-token), P_NM could hit 18+/20 and the experiment becomes uninformative. Diagnose via attractor-category inspection on the preserve arm.
- **Too-clean (C_NM = 20/20):** attractor-inspect for a trivial program exploiting the new op's semantics (e.g., FILTER_EQ followed by LEN).
- **Seed-overlap confound:** if the consume solver set is identical across §v2.14 (MAP_EQ_R) and §v2.14f (FILTER_EQ_R), the effect may be seed-determined rather than op-driven. The §v2.14e prereg already flagged this caveat; §v2.14f extends the comparison to a non-MAP op, which stresses the shared-RNG reading harder.
- **Detection:** run `decode_winner.py` on all 40 winners (both arms, all seeds); tabulate attractor categories and canonical-body-family counts per arm. Print the per-seed solve matrix overlap with §v2.14 consume solvers.

## Statistical test (if comparing conditions)

- **Test:** paired McNemar on seeds 0-19 (preserve vs consume on non-MAP pair).
- **Significance threshold:** α = 0.05, two-sided (underpowered at n=20; report raw counts as primary).
- **Secondary:** descriptive seed-overlap with §v2.14 and §v2.14e consume solvers.

## Diagnostics to log (beyond fitness)

- Per-seed BOTH-solve + best-fitness under both rules
- Winner-genotype attractor-category classification (both arms)
- Per-seed solve-matrix overlap with §v2.14 and §v2.14e consume solvers
- Holdout gap
- Whether non-MAP canonical body converges in winners (structural check, not just label score)

## Scope tag (required for any summary-level claim)

**If PASS:** `within-family-broadened · n=20 · at BP_TOPK(k=3,bp=0.5) v2_probe · on {MAP_EQ_R, MAP_EQ_E, FILTER_EQ_R} slot bindings · 6-token string-count body · executor-rule ablation replication across op-families`

**If FAIL:** existing findings.md scope tag narrows — `MAP-family slot bindings` stays, and the non-MAP failure adds a concrete boundary in "Scope boundaries."

## Decision rule

- **PASS — replicates →** broaden findings.md `safe-pop-consume-effect` from "two MAP-family slot bindings" to "across op-families on the 6-token string-count body." This is a substantial scope broadening; triggers a promote-finding pass.
- **PASS — partial →** note the attenuated effect on non-MAP; keep the two-MAP-binding scope as the clean claim, add the non-MAP partial as supporting-but-weaker evidence.
- **FAIL — no lift →** narrow findings.md scope from "two MAP-family slot bindings" to "MAP-family slot bindings (necessary, possibly via op-internal semantics beyond the type chain)." Queue a mechanism probe for why the MAP-internal semantics matter.
- **FAIL — consume worse →** investigate winners; do not change findings.md until understood.
- **SWAMPED →** non-MAP body is too easy; uninformative. Do not update findings. Consider higher-threshold non-MAP pair (e.g., filter_eq_gt_5_slot) as follow-up.

---

*Audit trail.* Five outcome rows plus SWAMPED (principle 2). Baseline is this sweep's preserve arm (principle 6). Internal control is the preserve/consume ablation on shared seeds (principle 1). Degenerate-success candidates enumerated including seed-overlap confound (principle 4). Principle 20 not triggered — label function unchanged. Decision rule commits to exact findings.md edits per outcome (principle 19).

**USER REVIEW CHECKLIST** (before commit):
- [ ] Approve the op choice (FILTER_EQ_R vs REDUCE_* vs something else)
- [ ] Confirm the task definition can be added (`any_char_count_R_filtereq_gt_*_slot`) or name a better wiring
- [ ] Approve the ±4 effect-size threshold (matches §v2.14e convention)
- [ ] Confirm commit-hash gating (prereg must land before sweep runs)
