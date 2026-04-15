# Pre-registration: §v2.6'-Pair2 — `sum_gt_{18,24}_slot_r12` redesigned at Fmin-intermediate thresholds

**Status:** QUEUED · target commit `75ab827` · 2026-04-15

Derived from `findings.md#constant-slot-indirection` Open external-validity
question (i): *"does a redesigned §v2.6' with Fmin-intermediate thresholds
on Pair 2 / Pair 3 bodies support the mechanism?"* and from
[`docs/chem-tape/experiments-v2.md §v2.6 Caveats`](../docs/chem-tape/experiments-v2.md#v26):
*"does Pair 2 redesigned at thresholds {e.g., 18, 24} over [0,12] —
pushed onto the ascending shoulder of the sum-CDF — pass the scales bar?"*

This is the experiment §v2.6 was supposed to run and didn't. §v2.6 Pair 2
landed swamp (Fmin = 20/20 at thresholds {7, 13} over [0,12]) and was
mechanism-untested. The original prereg's threshold choice pre-accepted
that swamp. This redesign moves thresholds onto the CDF shoulder where
mechanism lift can actually be measured.

## Question (one sentence)

On the §v2.6 Pair 2 body shape (`INPUT SUM THRESHOLD_SLOT GT` over [0,12])
at thresholds chosen to keep `Fmin` intermediate (target ∈ [4, 17]), does
constant-slot indirection extend the §v2.3 mechanism to a second body
variant — establishing two-pair breadth for `findings.md#constant-slot-indirection`?

## Hypothesis

§v2.3's 80/80 BOTH on `sum_gt_{5,10}_slot` over [0,9] at the same body
shape (just narrower range) is the closest comparand. The body
(`INPUT SUM THRESHOLD_SLOT GT`) is byte-identical; only input range and
threshold values differ. Three plausible outcomes:

1. **Mechanism extends to second body variant.** BOTH ≥ scales-bar at
   matched compute. The §v2.3 mechanism reading scales to a second body
   in the same family with shifted input range. `findings.md#constant-slot-indirection`
   broadens from "one pair" to "two pairs in the integer-sum family."

2. **Mechanism is pair-specific (`sum_gt_{5,10}_slot` only).** BOTH
   ≤ 5/20 at matched compute. §v2.3's 80/80 was pair-specific even
   within the same body shape. The narrowest-possible reading of
   `findings.md#constant-slot-indirection` stands.

3. **Partial extension.** BOTH ∈ [6, scales-bar). Mechanism extends in
   weakened form on this variant. Some axis of difference between
   `sum_gt_{5,10}` over [0,9] and `sum_gt_{?,?}` over [0,12] partially
   matters.

The closeness of body shape (byte-identical canonical body; only range
and thresholds vary) weights the prior toward (1). A FAIL would be the
most surprising and informative outcome.

## Setup

This experiment runs in **two phases with a HARD GATE between them**:
Phase A picks the threshold pair via sampler audit + 5-seed scout.
Phase B is the main alternation + 20-seed fixed-baseline sweep, **and
runs ONLY IF Phase A produces a qualifying candidate AND that
candidate's measured Fmin lands in the intermediate range**. (Codex
[P1] finding addressed: earlier draft said "if no candidate qualifies,
Phase B runs on C2 by default and is interpreted via Phase A scout
reject row" — that is exactly the §v2.6 mistake repeated. Hard gate
replaces it.) If Phase A fails, Phase B does NOT run; queue entry
skips and a re-prereg with wider threshold candidates is required.

### Candidate threshold pairs (Phase A picks one)

For length-4 intlists over [0,12] (range hi_exclusive=13), sum mean=24,
std ≈ 6.93 by normal approximation. Candidate pairs targeting Fmin
in the [4, 17] range:

| candidate | t1 | t2 | label task 1 | label task 2 | a-priori P(label) |
|---|---|---|---|---|---|
| **C1** | 18 | 24 | `sum > 18` | `sum > 24` | ~0.81 / ~0.50 |
| **C2** | 22 | 28 | `sum > 22` | `sum > 28` | ~0.62 / ~0.28 |
| **C3** | 24 | 30 | `sum > 24` | `sum > 30` | ~0.50 / ~0.19 |

The §v2.6 swamp (Fmin = 20/20 at thresholds {7, 13}) was at labels
`sum > 7` (P≈0.99) and `sum > 13` (P≈0.94) — both at near-ceiling.
These candidates push thresholds onto the CDF shoulder where Fmin
should be measurable.

### Phase A — sampler audit + scout

For each candidate {C1, C2, C3}:

1. **Task builder reuse:** the existing `_make_sum_gt_slot_range_task(t,
   hi_exclusive=13, name=...)` factory in `tasks.py` already supports
   arbitrary thresholds. Add registry entries for new thresholds (e.g.,
   `sum_gt_18_slot_r12`, `sum_gt_22_slot_r12`, etc.). No new factory
   code needed.
2. **Sampler audit on seeds {0, 1, 2}** for each task (codex [P1]
   addressed: extended from seed-0 only; multi-seed required by
   principle 20):
   - (i) class balance per seed. **Required: 0.40 ≤ ratio ≤ 0.60 on
     every audited seed.**
   - (ii) primary proxy accuracies per seed (codex [P1] addressed:
     `any cell > 11` was named in the degenerate-success guard but
     missing from the audit list; added):
     `constant-1`, `constant-0`, `sum > 5`, `sum > 10`, `sum > 15`,
     `sum > 20`, `sum > 25`, `sum > 30`, `max > 5`, `max > 7`,
     `max > 9`, `max > 11`, `any cell > 9`, `any cell > 11`.
     **Required: max proxy accuracy < 0.90 on every audited seed.**
   - (iii) label viability: positive count ≥ 5 per seed.
3. **5-seed scout sweep** per task (BP_TOPK(k=3, bp=0.5), pop=1024,
   gens=1500). Compute pair Fmin_scout.
4. **Selection rule (HARD GATE — codex [P1] addressed):**
   - If at least one candidate passes ALL audit checks (i)+(ii)+(iii)
     across seeds {0, 1, 2} **AND** has scout `Fmin_scout ∈ [1, 4]`:
     select the qualifying candidate with the highest Fmin_scout.
     Phase B runs on the selected pair.
   - **Otherwise: HALT.** Phase B does NOT run. Queue entry marked
     "halted at Phase A; re-prereg required with wider candidate
     thresholds." Three nearby candidates {C1, C2, C3} bias toward
     ceiling; if all three fail, a §v2.6''-Pair2 prereg with wider
     candidates (e.g., {(28, 32), (15, 22)}) is needed.

### Phase B — main alternation + fixed-baseline sweep

- **Sweep files:**
  - `experiments/chem_tape/sweeps/v2/v2_6p_pair2_alt.yaml` — alternation
    on the selected pair (parameterized by Phase A's pick).
  - `experiments/chem_tape/sweeps/v2/v2_6p_pair2_fixed.yaml` —
    fixed-task baselines on each task of the selected pair.
- **Tasks:** the selected pair (e.g., `sum_gt_18_slot_r12`,
  `sum_gt_24_slot_r12`).
- **Alphabet:** `v2_probe`.
- **Fixed params (matched verbatim to §v2.6 Pair 2 prereg):** `arm: BP_TOPK`,
  `topk: 3`, `bond_protection_ratio: 0.5`, `tape_length=32`, `n_examples=64`,
  `holdout_size=256`, `pop_size=1024`, `generations=1500`, `tournament_size=3`,
  `elite_count=2`, `mutation_rate=0.03`, `crossover_rate=0.7`,
  `task_alternating_period=300`.
- **Seeds:** `0..19` (n=20).
- **Est. compute:**
  - Phase A: ~12 min (6 scout sweeps × 5 seeds × ~2.5 min/run wall
    at 8 workers).
  - Phase B: ~15 min alternation + ~30 min fixed baselines.
  - Total: ~60 min at 10 workers.

## Baseline measurement (required)

- **Baseline quantity:**
  - §v2.3 (`sum_gt_{5,10}_slot` over [0,9]): F_5 = 20/20, F_10 = 19/20,
    BOTH = 80/80.
  - §v2.6 Pair 2 original (`sum_gt_{7,13}_slot_r12` over [0,12]): F_7 =
    20/20, F_13 = 20/20, BOTH = 20/20 (swamp).
- **Per-pair alternation threshold (principle 6):** `scales_bar =
  max(Fmin_B − 3, 12)`, matching §v2.3 / §v2.6 / §v2.8 formula.
  `Fmin_B` is the Phase B 20-seed fixed-baseline Fmin.

## Internal-control check (required)

- **Tightest internal contrast:** §v2.3's `sum_gt_{5,10}_slot` over [0,9].
  Body shape is byte-identical (`INPUT SUM THRESHOLD_SLOT GT`); only
  input range and thresholds vary. **No body shape variation;** this is
  the cleanest within-family pair-replication test possible.
- **Are you running it here?** Yes. Phase B IS the within-family
  same-body-shape replication test (per principle 1).

## Sampler-design audit (principle 20)

**TRIGGERED.** New range and new thresholds change the training
distribution. Required pre-sweep measurements (Phase A above):

- (i) class balance per task on seed=0 training. **Required: 0.40 ≤
  ratio ≤ 0.60.**
- (ii) max proxy accuracy across the candidate proxy set per task on
  seed=0 training. **Required: < 0.90.**
- (iii) label viability per task: positive count ≥ 5.

Phase A reports these per candidate. Failure on the selected candidate
triggers the "Phase A scout reject" outcome row.

**Methodology note (principle 20 reinforcement):** §v2.6's original
Pair 2 prereg pre-accepted swamp (Fmin = 20/20) at the threshold-table
level without measuring proxy accuracies. This redesign explicitly
discharges the sampler-audit gate the original missed.

## Pre-registered outcomes (required — at least three)

Definitions:
- `BOTH_6p = ` Phase B alternation BOTH-solve at fitness ≥ 0.999.
- `Fmin_B = min(F_task1_B, F_task2_B)` from Phase B fixed-baseline sweep.
- `scales_bar = max(Fmin_B − 3, 12)`.

| outcome | criterion | interpretation |
|---|---|---|
| **scales (mechanism extends to second body variant)** | `Fmin_B ∈ [4, 17]` AND `BOTH_6p ≥ scales_bar` AND mechanism inspection confirms slot-indirection | §v2.3's mechanism extends to a second body variant in the integer-sum family. `findings.md#constant-slot-indirection` broadens scope tag from "one pair / one body shape" to "two pairs / one body shape (range-variant)." First clean two-pair breadth result. Mechanism-rename check (principle 16): name should NOT narrow further; the broadening is on number of pairs, not on the operating regime. |
| **partial (mechanism extends in weakened form)** | `Fmin_B ∈ [4, 17]` AND `BOTH_6p ∈ [6, scales_bar)` | Mechanism extends but with reduced efficiency. Some axis of difference between [0,9] and [0,12] partially affects mechanism reach. Add a "range-dependence within the integer-sum family" line to `findings.md#constant-slot-indirection` Scope boundaries. |
| **does-not-scale (mechanism does not extend to this range)** | `Fmin_B ∈ [4, 17]` AND `BOTH_6p ≤ 5/20` | The mechanism does not extend to the §v2.3 body shape under [0,12] range at the selected thresholds. **Multiple competing readings remain (codex [P1] addressed: earlier draft jumped straight to "pair-specific rename"; that's premature):** (1) range-dependence — [0,12] differs from [0,9] in ways that affect mechanism; (2) sampler/proxy contamination not caught by audit; (3) decoder-arm sensitivity (§v2.11 / §v2.13 axes); (4) genuinely pair-specific. Principle 16 requires *narrowing when warranted*, not jumping to the narrowest available story. **Decision rule under does-not-scale:** queue inspection-deeper diagnostic (decoded-winner classification per Gate 4) and follow-up §v2.6'-Pair2-cross-decoder before any rename pass. NO findings supersession in this pass; instead add an Open external-validity question naming the four competing readings. |
| **swamped (Phase A miss)** | `Fmin_B ≥ 18/20` | Phase A scout under-estimated task difficulty; selected pair is at ceiling. `BOTH_6p = 20/20` is mechanism-untested. **No findings change.** Re-design with higher thresholds and re-prereg as §v2.6''-Pair2. |
| **baseline-fails (Phase A over-shot)** | `Fmin_B ≤ 3/20` | Phase A scout under-estimated task difficulty in the other direction; both individual tasks fail. Alternation result uninterpretable. **No findings change.** Re-design with lower thresholds. |

## Degenerate-success guard (required)

- **Too-clean candidates:**
  - `BOTH_6p = 20/20` AND `Fmin_B ∈ [10, 17]` — clean two-pair result;
    the strongest single positive of the night for the constant-slot-indirection
    finding. Inspection mandatory.
  - `BOTH_6p = 20/20` AND `Fmin_B ≥ 19/20` — swamp signature, pre-accepted.
- **Candidate degenerate mechanisms:**
  1. **Range-limit trick** (per §v2.6 prereg degenerate-success #3):
     evolution exploits a predicate like `any cell > 11` that correlates
     with sum-gt-threshold under [0,12] without actually using
     THRESHOLD_SLOT. This was checked and ruled out on §v2.6 original
     Pair 2; verify it doesn't reappear at higher thresholds.
  2. **Per-task constant-construction shortcut** (parallel per-task
     bodies): under BP_TOPK, two non-interfering programs on the same
     tape could solve both tasks. Ruled out on §v2.6 original Pair 2's
     winners (THRESHOLD_SLOT present in 18/20 and 16/20 of fixed-task
     winners). Verify it doesn't reappear here.
  3. **Single-predicate proxy attractor** (per §v2.4): one of the
     candidate proxies in the audit list scores ≥ 0.85 and dominates
     the search. Phase A's audit is the gate against this.
- **Classifier-tooling deferral note (codex [P1] finding addressed via
  explicit deferral):** the current `decode_winner.py:76` admits the
  extracted program is a "permeable-all view" superset, NOT actual
  BP_TOPK extraction; `classify_proxy:103` only emits coarse tags. The
  fine-grained classification below (canonical-contiguous vs canonical-
  with-scatter vs alt-assembly vs per-task-shortcut) is NOT cleanly
  distinguishable with current tooling; manual per-winner inspection
  is required for ambiguous cases. Implementing a richer classifier is
  a separate infrastructure item (§v2.X-classifier-extension, not yet
  pre-registered). Estimated manual-classification time: ~30-45 min for
  ≤ 60 winners (20 alt + 20 task1 fixed + 20 task2 fixed).
- **How to detect (inspection commitment with current tooling):**
  1. For all Phase B BOTH-solvers AND all 40 fixed-baseline winners:
     run `decode_winner.py v2_6p_pair2 --all`.
  2. Apply available coarse-tag classification:
     `uses_THRESHOLD_SLOT`, `proxy_max_gt_C`, `proxy_sum_gt_C`,
     `range_check_any_cell_gt_C` (NEW — codex [P1] addressed: the
     range-limit-trick guard requires `any cell > c` checks for c up
     to 11; verify classifier emits this tag, otherwise add it as a
     pre-Phase-B classifier extension), `unclassified`.
  3. **Manual per-winner inspection** for any winner tagged
     `unclassified` OR for any BOTH-solver where THRESHOLD_SLOT is
     present but its causal role is unclear from coarse tags.
     Categorise manually into: canonical-slot-causal, per-task-
     shortcut, proxy-attractor, range-limit-trick, unclassified.
  4. **Strict deduction rule (codex [P2] addressed: replace soft "softens
     accordingly" with hard arithmetic):** the "slot-indirection support
     count" used for outcome interpretation =
     `BOTH_6p − (per-task-shortcut + proxy-attractor + range-limit-trick + unclassified)`.
     If this support count drops the outcome below the row threshold,
     the outcome downgrades by exactly one row (scales → partial →
     does-not-scale). No discretionary "softening."
  5. Compute the actual single-predicate proxy accuracy on **all 20
     Phase B seeds' training data** (not just seeds 0..2). If proxy
     accuracy varies seed-to-seed beyond the audit-window mean ± 0.05,
     the audit's multi-seed numbers were not representative; flag as a
     methodology lesson and note in the chronicle.

## Statistical test

**Codex [P1] finding addressed: redefine McNemar comparator as
seedwise binary, not aggregate-vs-aggregate.**

- **Phase B alternation BOTH vs fixed-task conjunction:** paired McNemar
  on shared seeds 0..19. Per-seed binary outcomes:
  - `alt_BOTH_seed_s = 1` iff alternation seed s solves both tasks ≥ 0.999.
  - `fixed_AND_seed_s = 1` iff fixed-task seed s solves task1 ≥ 0.999 AND
    seed s solves task2 ≥ 0.999 (per-seed conjunction; the seedwise
    version of "BOTH vs Fmin").
  - McNemar on (b, c). Two-sided exact binomial. One-sided α=0.05 for
    "alternation < fixed_AND" direction.
- **Cross-experiment comparison:**
  - vs §v2.3 (`sum_gt_{5,10}_slot` over [0,9]): two-proportion z on
    BOTH (independent seeds across experiments). Descriptive/secondary
    only — tasks differ in input range and thresholds, so the
    comparison is suggestive rather than definitive.
  - vs §v2.6 Pair 2 original (`sum_gt_{7,13}_slot_r12`): descriptive
    only (different threshold pair, same body shape, swamped).

## Diagnostics to log (beyond fitness)

- Phase A: per-task class balance, max proxy accuracy and identity, scout
  F_scout (5 seeds).
- Phase B alternation: BOTH_6p, F_task1_B, F_task2_B, Fmin_B, scales_bar.
- Per-seed best-of-run final fitness on each task.
- Mean and max train−holdout gap (overfit audit).
- Mean and max post-flip fitness drop on alternation; full distribution.
- Decoded body identity per BOTH-solver and per non-solver winner.
- Solved-seed identity per Phase B condition.
- Per-seed empirical proxy accuracies on Phase B seeds 0..19 (not just
  seed=0; methodology cross-check).

## Scope tag (required for any summary-level claim)

**If Phase B lands "scales", `findings.md#constant-slot-indirection`
broadens to:**

`within-family · n=20 on shared seeds 0..19 per pair · at pop=1024 gens=1500
BP_TOPK(k=3, bp=0.5) v2_probe alphabet · on body INPUT SUM THRESHOLD_SLOT GT
across two range-variant pairs: (sum_gt_{5,10}_slot over [0,9])
and (sum_gt_{t1,t2}_slot_r12 over [0,12]) where (t1,t2) was selected
in Phase A`

Explicitly **NOT** claiming on PASS:
- Generalisation to body shapes other than `INPUT SUM THRESHOLD_SLOT GT`
  (Pair 1's CHARS chain and Pair 3's REDUCE_MAX still untested at
  Fmin-intermediate).
- Generalisation to operations beyond integer arithmetic.
- Decoder-arm independence (§v2.11 / §v2.13 separately).
- "Across-family" extension — this is two pairs in the *same* body
  family at different ranges. The proper across-family test still
  requires a redesigned Pair 3 (REDUCE_MAX body) at Fmin-intermediate.

## Decision rule

- **scales →** trigger findings.md broadening pass on
  `findings.md#constant-slot-indirection`. Headline scope tag updates
  from "one pair" to "two pairs (same body shape, range-variant)."
  Add this experiment + §v2.3 as joint Supporting experiments. Leaves
  open the across-family question (Pair 3 redesign).
- **partial →** add "range-dependence" line to Scope boundaries.
  No headline change. Queue follow-up `§v2.6'-Pair2-scale` (4× compute)
  IF user values further data on this axis.
- **does-not-scale →** the most surprising outcome. Trigger mechanism
  rename check (principle 16): the §v2.3 mechanism may need to be
  renamed something more pair-specific. Flag for codex review and
  paper-scope discussion before commiting any rename.
- **swamped →** Phase-A-miss; re-design with higher thresholds. Run
  `§v2.6''-Pair2` with new candidates. No findings change.
- **baseline-fails →** Phase-A-over-shoot; re-design with lower
  thresholds. No findings change.

---

*Audit trail.* Five pre-registered Phase B outcome rows including partial,
swamp, and baseline-fails (principle 2). Phase B thresholds anchored to
Phase B's own measured Fmin (principle 6). Tightest within-family contrast
is byte-identical body shape against §v2.3 (principle 1). Sampler-design
audit triggered with all three required pre-sweep measurements (principle 20)
— this is the gate the original §v2.6 Pair 2 prereg missed. Degenerate-success
candidates enumerated with strict inspection commitment including
range-limit-trick guard (principle 4 + 21). Decision rule includes
broadening trigger (scales), narrowing/rename trigger (does-not-scale),
and re-prereg triggers for Phase A design failures (principle 13 + 19).
Cross-experiment comparison method differentiated for each baseline
(McNemar on matched seeds vs two-proportion z on independent seeds vs
descriptive-only) (principle 7).
