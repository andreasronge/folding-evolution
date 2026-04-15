# Pre-registration: §v2.8 — 6-token integer-domain body to disambiguate body-length from input-domain on Pair 1's failure

**Status:** QUEUED · target commit `75ab827` · 2026-04-15

Derived from `findings.md#constant-slot-indirection` Open external-validity
question: *"§v2.6 Pair 1 (6-token string-count body) failed at 4/20 at
matched compute, possibly resolvable at higher pop/gens but untested."*
Pair 1 confounds body-length (6 tokens), input-domain (string), and
chain-shape (`MAP_EQ_R` + `CHARS` adds string-domain-specific assembly).
This experiment isolates **body-length** by running a 6-token
integer-domain body that uses neither `CHARS` nor `MAP_EQ_R`.

## Question (one sentence)

At matched compute (pop=1024, gens=1500, BP_TOPK(k=3, bp=0.5)) on a
6-token integer-domain canonical body that uses `THRESHOLD_SLOT` for
constant-slot indirection, does evolution reliably solve the alternation
pair, or does the failure pattern observed on §v2.6 Pair 1 reproduce —
isolating body-length as the dominant axis?

## Hypothesis

Three plausible outcomes:

1. **Body-length is the load-bearing axis.** A 6-token integer-domain
   body fails at roughly the same rate Pair 1 did (BOTH ~4-8/20).
   Pair 1's failure was primarily about body length, not string-domain
   specifics. The §v2.3 / §v2.6 contrast is "4-token easy, 6-token hard"
   regardless of input domain.

2. **String-domain (and/or `CHARS` / `MAP_EQ_R` chain) was the load-bearing
   axis.** A 6-token integer-domain body solves at roughly §v2.3 rates
   (BOTH ≥ 15/20 conditional on Fmin). Pair 1's failure was primarily
   string-domain-specific or `CHARS`-chain-specific; body length per se
   was not the blocker.

3. **Body-length AND something else interact.** A 6-token integer-domain
   body lands intermediate (BOTH 6-14/20). Body length is partially
   responsible; some additional factor specific to Pair 1 contributes too.

The §v2.6-pair1 follow-up sweeps (decoder, tape, compute) found
component-discovery upstream of assembly under BP_TOPK(k=3) on Pair 1,
which is consistent with body-length being load-bearing — longer bodies
have more components to discover. This weights the prior toward (1),
but does not preempt the experiment.

## Setup

This experiment runs in **two phases with a HARD GATE between them**:
Phase A is a sampler-audit + scout sweep that selects the threshold pair.
Phase B is the main alternation sweep on the selected pair, **and runs
ONLY IF Phase A produces a qualifying candidate**. (Codex [P1] finding
addressed: earlier draft said "Phase B runs regardless"; this is exactly
the §v2.6 mistake — soft gating that lets bad samplers through with a
post-hoc "scout reject" interpretation row. The hard gate replaces that
discipline.) If Phase A rejects all candidates, Phase B does NOT run;
the queue entry skips and a re-prereg is required before any main sweep
on this body.

### Body design

**Canonical body (6 tokens):** `INPUT SUM CONST_2 ADD THRESHOLD_SLOT GT`

VM semantics (verified against executor.py): pushes input intlist, sums
to scalar `s`, pushes `2`, adds (`s+2`), pushes task-bound threshold `t`,
GT (`(s+2) > t`) — equivalent to `sum > t-2`.

Reasoning for this body specifically:
- 6 tokens (matches Pair 1's length).
- Integer domain (no `CHARS`, no `MAP_EQ_R`) — eliminates Pair 1's
  string-domain confound.
- Strict left-to-right dependency (any reordering breaks semantics) —
  matches Pair 1's strict chain assembly.
- `THRESHOLD_SLOT` is the only task-distinguishing token; both paired
  tasks share token-identical canonical bodies (matches §v2.3 pattern).
- The shorter 4-token alternative `INPUT SUM CONST_C GT` is **not
  cheaper** for the relevant thresholds: constructing arbitrary
  constants in v2_probe alphabet (which has CONST_0, CONST_1, CONST_2,
  CONST_5) requires ADD chains. For threshold pair (17, 22), the
  shortest non-slot alternatives are `INPUT SUM CONST_5 CONST_5 CONST_5
  ADD ADD GT` (8 tokens) and `INPUT SUM CONST_5 CONST_5 CONST_5 CONST_5
  ADD ADD ADD GT` (10 tokens). The 6-token slot body is the cheapest
  path under both threshold settings.

### Candidate threshold pairs (Phase A picks one)

| candidate | label task 1 | label task 2 | a-priori P(label) (length-4 [0,9]) |
|---|---|---|---|
| **C1: (15, 20)** | `sum > 13` | `sum > 18` | ~0.79 / ~0.50 |
| **C2: (17, 22)** | `sum > 15` | `sum > 20` | ~0.65 / ~0.35 |
| **C3: (20, 25)** | `sum > 18` | `sum > 23` | ~0.50 / ~0.18 |

Estimated P values from sum mean=18, std≈5.74 normal approximation;
actual values will be measured in Phase A.

### Phase A — sampler audit + scout (the gate)

For each candidate {C1, C2, C3}:

1. **Implement task builder** as `make_sum_plus2_gt_t_slot_task(t)` in
   `tasks.py`, registering as `sum_plus2_gt_<t>_slot` for t ∈
   {15, 17, 20, 22, 25}.
2. **Sampler audit on seeds {0, 1, 2}** for each task (no GP, just
   measurement on 64-sample training set per seed; codex [P2] finding
   addressed by extending from seed-0 to multi-seed):
   - (i) class balance: positives / total per seed. **Required: 0.40 ≤
     positive ratio ≤ 0.60 on every audited seed.**
   - (ii) primary proxy accuracies per seed: `constant-1`, `constant-0`,
     `sum > 5`, `sum > 10`, `sum > 15`, `sum > 20`, `sum > 25`,
     `max > 5`, `max > 7`, `max > 9`, `any cell > 5`, `any cell > 7`,
     `any cell > 9`. **Required: max proxy accuracy < 0.90 on every
     audited seed.** If any proxy ≥ 0.90 on any seed, candidate is
     rejected (proxy-basin trap risk).
   - (iii) label viability: positive count ≥ 5 in training per seed.
3. **5-seed scout sweep** (per task, BP_TOPK(k=3, bp=0.5),
   pop=1024, gens=1500) on each candidate's two tasks. Compute
   per-task `F_scout` and pair Fmin.
4. **Selection rule (HARD GATE):**
   - If at least one candidate passes ALL audit checks (i)+(ii)+(iii)
     across seeds {0, 1, 2} **AND** has scout `Fmin ∈ [1, 4]`: select
     the qualifying candidate with the highest Fmin (closer to §v2.3's
     reference shape). Phase B runs on the selected pair.
   - **Otherwise: HALT.** Phase B does NOT run. Mark this prereg's
     queue entry as "halted at Phase A; re-prereg required." Re-prereg
     §v2.8' with different body shape or threshold range, anchored to
     what the Phase A measurements showed.

### Phase B — main alternation sweep on selected pair

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_8_main.yaml`
  (parameterized; the queue entry sets `task_alternating_values`
  according to Phase A's selection).
- **Tasks:** the selected pair from Phase A.
- **Alphabet:** `v2_probe`.
- **Fixed params (matched verbatim to §v2.6 Pair 1 prereg):** `arm:
  BP_TOPK`, `topk: 3`, `bond_protection_ratio: 0.5`, `tape_length=32`,
  `n_examples=64`, `holdout_size=256`, `pop_size=1024`, `generations=1500`,
  `tournament_size=3`, `elite_count=2`, `mutation_rate=0.03`,
  `crossover_rate=0.7`, `task_alternating_period=300`.
- **Seeds:** `0..19` (n=20).
- **Companion fixed-task sweep:** also run, both Phase B tasks fixed,
  seeds 0..19. Required to compute final Fmin (the scout's 5-seed
  Fmin is a low-confidence estimate; the 20-seed measurement is the
  load-bearing baseline).
- **Est. compute:**
  - Phase A: ~2 min sampler audit (no GP) + ~10 min scout
    (6 fixed-task scouts × 5 seeds × ~5s/run with light wall, but
    actual GP time ~2 min/run = ~12 min actual).
  - Phase B: ~15 min alternation + ~30 min fixed baselines.
  - Total: ~60 min at 10 workers.

## Baseline measurement (required)

- **Baseline quantity:** §v2.3 (4-token integer body, 80/80 BOTH) and
  §v2.6 Pair 1 (6-token string-count body, 4/20 BOTH at matched compute).
- **Reference points:**
  - §v2.3 (commit `e3d7e8a`): F_5 = 20/20, F_10 = 19/20, BOTH = 80/80
    across 4 seed blocks.
  - §v2.6 Pair 1 (commit `0230662`): F_gt1 = 4/20, F_gt3 = 10/20,
    BOTH = 4/20.
- **Per-pair alternation threshold (principle 6):** scales-bar = max(Fmin_B − 3, 12),
  matching §v2.3 / §v2.6 formula. `Fmin_B` is the Phase B fixed-baseline
  Fmin (the 20-seed measurement, NOT the 5-seed scout estimate).

## Internal-control check (required)

- **Tightest internal contrast:** §v2.3's 4-token integer body
  (`INPUT SUM THRESHOLD_SLOT GT`) at the same alphabet, decoder, and
  compute. **Only body length and one operator (CONST_2 ADD) vary.**
  The §v2.6 Pair 1 body is **not** the tightest internal contrast
  because it varies on three axes simultaneously (length, input-domain,
  chain-shape). This experiment's contrast against §v2.3 isolates body
  length more cleanly than Pair 1 ever could.
- **Are you running it here?** Yes. The Phase B alternation IS the
  within-family body-length contrast.

## Sampler-design audit (principle 20)

**TRIGGERED.** New tasks introduce a new label-function distribution.
Required pre-sweep measurements (Phase A above):

- (i) class balance (positives / total) per task on seed=0 training.
  **Required: 0.40 ≤ ratio ≤ 0.60.**
- (ii) maximum single-predicate proxy accuracy across the candidate
  proxy set per task on seed=0 training. **Required: < 0.90.**
- (iii) label viability: positive count ≥ 5 per task on seed=0 training.

Phase A reports these three numbers per candidate. **Failure of any
required check on the selected candidate triggers the "Phase A scout
reject" outcome row in Phase B's interpretation table.**

## Pre-registered outcomes (required — at least three)

Phase B outcomes are evaluated **after Phase A picks the threshold pair
(or rejects all candidates).** Definitions:

- `BOTH_8 = ` Phase B alternation BOTH-solve at fitness ≥ 0.999.
- `Fmin_B = min(F_task1_B, F_task2_B)` from Phase B fixed-baseline sweep.
- `scales_bar = max(Fmin_B − 3, 12)`.

| outcome | criterion | interpretation |
|---|---|---|
| **scales (body-length is NOT the blocker)** | Phase A selected a pair AND `Fmin_B ∈ [4, 17]` AND `BOTH_8 ≥ scales_bar` | The §v2.3 mechanism extends to a 6-token integer-domain body. Pair 1's failure was primarily string-domain-specific or `CHARS`-chain-specific, NOT body-length-specific. `findings.md#constant-slot-indirection` scope **broadens** from "one pair (4-token integer)" to "one 4-token integer pair AND one 6-token integer pair." Pair 1's diagnosis sharpens to "string-domain or chain-specific assembly difficulty." |
| **partial (body-length is partly the blocker)** | Phase A selected a pair AND `Fmin_B ∈ [4, 17]` AND `BOTH_8 ∈ [6, scales_bar)` | Body length is partially responsible for the 6-token failure pattern. Pair 1's string-domain confound is also partly load-bearing; both contribute. The mechanism extends with reduced efficiency at 6 tokens. Add a "decoder × body-length × input-domain" caveat to `findings.md#constant-slot-indirection` Open external-validity questions. |
| **does-not-scale (body-length IS the blocker)** | Phase A selected a pair AND `Fmin_B ∈ [4, 17]` AND `BOTH_8 ≤ 5/20` | Body length is the dominant axis for the 6-token failure. A 6-token integer body with no string-domain confound still fails ≈ 4/20 like Pair 1. Pair 1's failure characterization narrows to "6-token bodies are intrinsically hard at this budget under BP_TOPK(k=3)." Decoder follow-up §v2.6-pair1 sweeps (Arm A, k=5, etc.) become the natural rescue axis for **all** 6-token bodies, not just Pair 1's. |
| **swamped (Fmin too high to measure)** | Phase A selected a pair AND `Fmin_B ≥ 18/20` | Selected candidate was easier than the scout suggested. BOTH = 20/20 alternation is consistent with two independently easy tasks; mechanism untested. Re-design with higher thresholds. **No findings change.** Acknowledge as a Phase-A-design failure (the scout missed swamp-shoulder). |
| **baseline-fails (Fmin too low to measure)** | Phase A selected a pair AND `Fmin_B ≤ 3/20` | Selected candidate is harder than the scout suggested. Both individual tasks fail at solo evaluation, so alternation BOTH cannot exceed Fmin. **No findings change**, but signals that 6-token bodies even in the integer domain are at the edge of the feasible region under this decoder × budget. |
| **Phase A scout reject (no candidate passed sampler audit)** | All three candidates failed at least one required sampler check OR scout Fmin landed at {0/5, 5/5} on all candidates | Pre-experiment design failure. Phase B does not run a meaningful alternation sweep (or runs but is uninterpretable). Re-design with different body shape or threshold candidates. **No findings change**, but flag as a methodology lesson: 6-token integer body design is harder than 4-token; threshold-CDF-shoulder targeting is non-trivial here. |

## Degenerate-success guard (required)

- **Too-clean candidates:**
  - `BOTH_8 = 20/20` AND `Fmin_B ≥ 19/20` — swamp signature; pre-accepted
    as swamped row above.
  - `BOTH_8 ≥ 18/20` AND `Fmin_B ∈ [10, 17]` — clean scaling on a
    6-token body; would be the strongest single positive result of the
    night. Inspection commitment: must verify slot-indirection is the
    mechanism (vs alt-assembly).
  - `Fmin_B = 0/20` and `BOTH_8 ≥ 5/20` — alternation lift without
    fixed-task viability. Mechanism-impossible on its face; would
    indicate task-builder bug.
- **Candidate degenerate mechanisms:**
  1. **Evolution finds a 4-token alternative `INPUT SUM CONST_C GT` that
     matches the label without slot-indirection.** Even though such an
     alternative requires a 5-7 token constant chain (> 6 tokens total),
     evolution might find it for one task and a different one for the
     other — defeating the body-invariant route framing.
  2. **Evolution finds a single-predicate proxy** (e.g., `sum > 10`
     scoring high on training) that the Phase A audit missed (e.g.,
     because the scout's seed=0 audit is not representative of seeds
     1..19). This would be a §v2.4-style proxy basin rather than a
     mechanism failure.
  3. **Alt-assembly via BP_TOPK permeability** (per §v2.4-alt seed 2,
     §v2.6-pair1-scale precedent): the canonical body's tokens appear
     scattered across the tape but extract to behaviorally-equivalent
     programs. PASS-on-mechanism if so, but inspection required.
- **Classifier-tooling deferral note (codex [P1] finding addressed via
  explicit deferral):** the current `decode_winner.py:76` admits the
  extracted program is a "permeable-all view" superset, NOT actual
  BP_TOPK extraction; `classify_proxy:103` only emits coarse tags
  (`uses_THRESHOLD_SLOT`, `sum_variant`, `max_gt_const`, etc.). The
  fine-grained categories below (canonical-contiguous vs
  canonical-with-scatter vs alt-assembly) are NOT cleanly distinguishable
  with the current tooling. Implementing a richer classifier that
  reconstructs actual BP_TOPK extraction + per-task body-comparison is a
  separate infrastructure item (§v2.X-classifier-extension, not yet
  pre-registered). Until it lands, the inspection below uses the
  available coarse tags + manual per-winner decode for ambiguous cases.
  Estimated manual-classification time: ~30-45 min for ≤ 60 winners.
  Recorded as deferred infrastructure cost.
- **How to detect (inspection commitment with current tooling):**
  1. For all Phase B BOTH-solvers AND all Phase B fixed-task winners:
     run `decode_winner.py v2_8_main --all` and `decode_winner.py
     v2_8_fixed --all`.
  2. Apply the available coarse-tag classification:
     `uses_THRESHOLD_SLOT`, `proxy_max_gt_C`, `proxy_sum_gt_C`,
     `if_gt_compositional`, `unclassified`. For each tag report
     X/N counts.
  3. **Manual per-winner inspection** for any winner tagged
     `unclassified` OR for any BOTH-solver where THRESHOLD_SLOT is
     present but its causal role is unclear from the coarse tags.
     Categorise into: canonical-slot-causal (slot value affects per-task
     output as designed), per-task-shortcut (two different bodies, slot
     irrelevant), proxy-attractor (cheap-program match), unclassified.
  4. **Strict deduction rule (codex [P1] finding addressed: per-task-
     shortcut isn't the only deduction; proxy-attractor and
     unclassified ALSO don't support slot-indirection):** the
     "slot-indirection support count" used for outcome interpretation =
     `BOTH_8 − (per-task-shortcut + proxy-attractor + unclassified)`.
     If this support count drops the outcome below the row threshold,
     downgrade the outcome accordingly.
  5. For all 40 fixed-baseline winners (20 per task): also classify and
     report the proxy-attractor count. If ≥ 5/20 winners on either task
     are proxy-attractor, this is a §v2.4-style trap and the mechanism
     reading is moot regardless of Phase B alternation outcome.

## Statistical test

**Codex [P1] finding addressed: redefine McNemar comparator as
seedwise binary, not aggregate-vs-aggregate.**

- **Phase B alternation BOTH vs fixed-task conjunction:** paired McNemar
  on shared seeds 0..19. Per-seed binary outcomes:
  - `alt_BOTH_seed_s = 1` iff alternation seed s solves both tasks ≥ 0.999.
  - `fixed_AND_seed_s = 1` iff fixed-task seed s solves task1 ≥ 0.999 AND
    fixed-task seed s solves task2 ≥ 0.999 (per-seed conjunction; this
    IS the seedwise comparator that "BOTH vs Fmin" was trying to express
    — Fmin is an aggregate, this is the seedwise version).
  - McNemar on disagreement counts (b, c) where b = seeds where
    fixed_AND=1 but alt_BOTH=0, c = seeds where alt_BOTH=1 but
    fixed_AND=0. Two-sided exact binomial. One-sided α=0.05 reported
    alongside for "alternation < fixed_AND" direction.
- **Cross-experiment comparison:** descriptive only.
  - vs §v2.3 (4-token integer): direction and rough magnitude.
  - vs §v2.6 Pair 1 (6-token string): direction and rough magnitude.
- **Phase A scout statistical test:** none. Scout is descriptive only;
  load-bearing measurement is Phase B's 20-seed Fmin.

## Diagnostics to log (beyond fitness)

- Phase A audit: per-task class balance, max proxy accuracy across the
  candidate proxy set, identity of the max proxy. Per-task scout
  F_scout (5 seeds).
- Phase B alternation: BOTH_8, F_task1_B, F_task2_B, Fmin_B, scales_bar.
- Per-seed best-of-run final fitness on each task.
- Mean and max train−holdout gap (overfit audit).
- Mean and max post-flip fitness drop on alternation; full distribution.
- Decoded body identity per BOTH-solver and per non-solver winner (per
  Gate 4 above).
- Solved-seed identity per Phase B condition (overlap diagnostic).
- COMP and ADI per Phase B condition (component-presence vs solve gap,
  per §v2.6-pair1-scale convention).

## Scope tag (required for any summary-level claim)

**If Phase B lands "scales" with the chosen threshold pair (t1, t2),
the claim broadens `findings.md#constant-slot-indirection` to:**

`within-family · n=20 on shared seeds 0..19 · at pop=1024 gens=1500
BP_TOPK(k=3, bp=0.5) v2_probe alphabet · on bodies {INPUT SUM
THRESHOLD_SLOT GT (4-token, [0,9]); INPUT SUM CONST_2 ADD THRESHOLD_SLOT
GT (6-token integer, thresholds {t1, t2})}`

Explicitly **NOT** claiming on PASS:
- Generalisation to all 6-token integer bodies (one body shape only).
- Generalisation to other 6-token bodies that include MAP / CHARS / chain
  ops (Pair 1 still untested except in its existing form).
- Decoder-arm independence (§v2.11 / §v2.13 are separate axes).
- Constant-slot-indirection extends to non-integer-arithmetic 6-token
  bodies.

## Decision rule

- **scales →** trigger findings.md broadening pass on
  `findings.md#constant-slot-indirection`. The headline scope tag changes
  from "one pair / one body shape" to "two pairs / two body shapes
  (4-token, 6-token both integer)." Pair 1's diagnosis sharpens to
  "string-domain or chain-specific" in `findings.md` Open external-validity
  questions.
- **partial →** add a "body-length × input-domain interaction" line to
  `findings.md#constant-slot-indirection` Scope boundaries. Do NOT broaden
  the headline. Queue follow-up `§v2.8-scale` (4× compute) IF the user
  decides this axis is worth more compute.
- **does-not-scale →** **NARROWED interpretation (codex [P1] finding
  addressed): one failed 6-token body cannot establish "6-token bodies
  are intrinsically hard."** It establishes that **this** body shape on
  this decoder × budget is hard. Update
  `findings.md#constant-slot-indirection` Open external-validity questions
  to add a row: "On the `INPUT SUM CONST_2 ADD THRESHOLD_SLOT GT` body
  at thresholds {t1, t2}, does-not-scale at matched compute under
  BP_TOPK(k=3, bp=0.5) — failure mode unresolved between body-length,
  body-shape-specific assembly, and decoder-arm sensitivity (need
  cross-decoder data on this body to disentangle)." Pair 1 follow-ups
  remain Pair-1-specific evidence; their generalisation to "all
  6-token bodies" is not warranted by §v2.8 alone.
- **swamped →** acknowledge Phase-A-design miss; re-design with higher
  thresholds and re-prereg as §v2.8'.
- **baseline-fails →** acknowledge feasibility edge; re-design with
  lower thresholds OR record as evidence for "6-token integer at the
  edge of feasibility under this decoder × budget" if all reasonable
  threshold ranges fail.
- **Phase A scout reject →** acknowledge body-design difficulty for
  6-token integer; methodology lesson recorded; re-design with
  alternative 6-token body candidates (e.g., aggregator-variant bodies).

---

*Audit trail.* Six pre-registered Phase B outcome rows including partial,
swamp, baseline-fail, and Phase-A-reject (principle 2). Phase B
thresholds anchored to Phase B's own measured Fmin (principle 6). Tightest
within-family contrast against §v2.3 explicitly named (principle 1).
Sampler-design audit triggered with three required pre-sweep measurements,
each with explicit pass criteria (principle 20). Degenerate-success
candidates enumerated per direction with strict inspection commitment
including "per-task-shortcut deducts from slot-indirection count"
discipline (principle 4 + 21). Decision rule includes broadening trigger
(scales), narrowing trigger (does-not-scale), and re-prereg triggers
(swamp / baseline-fails / Phase-A-reject) for all design-failure modes
(principle 13 + 19). Phase A's scout is explicitly descriptive; only
Phase B's 20-seed measurement is load-bearing (principle 8).
