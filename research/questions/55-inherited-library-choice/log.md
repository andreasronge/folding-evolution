- 2026-10-11 (steward, 1427): opened by [strategy 1427](../../runs/2026-10-11-1427/strategy.md); probe proposed
  ([proposal](../../runs/2026-10-11-1427/proposal.md)), critic approve_with_notes
  ([critique](../../runs/2026-10-11-1427/critique.md): size-matched null is not an exact robustness control;
  thresholds advisory; aggregate-law readout), [plan](../../runs/2026-10-11-1427/plan.md) took notes 1–4, code
  review pass ([review](../../runs/2026-10-11-1427/code_review.md)).

- 2026-10-11 (steward, 1427): **probe run** (commit `f8f4246`; queue 480 s + 533 s of 3,300 s;
  [analysis](../../runs/2026-10-11-1427/analysis.md), [execution](../../runs/2026-10-11-1427/execution.md)).
  `x4-order-v1` development cells only, 24 saved 1228 R-all libraries, P 256, lexicase, crossover 0.5; a per-program
  bit (recipient-inherited, no bit mutation, f₀ = 0.25) switches mutation donors to R-all. Arms L linked, S bits
  shuffled before each selection, Z linked bits with size-matched random donors, N neutral. Grids complete
  (336/336 trajectories, 1,440/1,440 readout jobs), no protected cells scored, no bookkeeping alarm. Observations:
  - **Absorption is fast.** Every trajectory ended fixed or lost; 328/336 by the end of episode 0, median absorbing
    generation 12 (L) to 18 (S), latest 136. Episodes 2–12 measured nothing about the bit.
  - **Fixation:** L 46/96 (0.48), S 27/96 (0.28), Z 29/96 (0.30), N 16/48 (0.33). Library-level bootstrap:
    L − S **0.20 [0.04, 0.35]**, L − Z **0.18 [0.05, 0.30]**; S, Z and N all compatible with the neutral 0.25.
    Per build L > S in 14/24, tie 4, L < S 6.
  - **Per-generation selection differential** (selected-parent minus census carrier share, pre-solve polymorphic
    generations): L +0.016 [0.009, 0.023] (library bootstrap; relative carrier advantage ≈ 4%), S, Z, N within
    ±0.005 of zero. L's rise sits in the pre-solve phase of episodes that go on to solve.
  - **Revert confound present and matched:** pre-solve library-draw rejection L 0.39, S 0.40, Z 0.42 against
    ordinary 0.30–0.32; Z still fixed at the neutral rate, so extra clones alone did not raise the bit here (Z
    content is not neutral, so content versus robustness is not fully separated).
  - **Frozen readout** (capped mean evaluations, library bootstrap): initial / R-all 1.33 [1.03, 1.72];
    **L-final / initial 0.91 [0.71, 1.20], unresolved**; L-final / R-all 1.21 [0.98, 1.46]; L-final / S-final 0.70
    [0.57, 0.82], which the convex dose curve (cost by probability 0: 74 k, 0.125: 45 k, 0.25: 37 k, 0.5: 32 k)
    explains as S losing the bit in more builds, not as separate usefulness evidence. Ceiling if every L trajectory
    fixed: about 0.73× of initial.
  - Steward read-only checks on the saved rows (descriptive, no interval): (i) in episode 0, where selection
    acted, L and S solved equally often within 64 generations (55/96 each; discordant pairs 20 vs 20); Z 34/96,
    N 15/48. Linkage moved the bit without a visible within-run solve gain. (ii) Deploying one evolved population's
    law (0 or 0.5, at L's fixation rate 0.48) would cost about 0.48 × 32 k + 0.52 × 74 k ≈ 54 k on the pooled dose
    curve, about 1.2× the initial mixture: under drift-dominated absorption, selection turns the starting mixture
    into a lottery that the convex dose curve punishes.
  Against the explanations (observations only): A gets its selection half (L above S and Z, about 4% relative
  carrier advantage) but not its usefulness half; B in its strong form (no carrier advantage) is not supported, but in its weak form (an advantage
  too small to fix the bit reliably against drift) it fits; C (drift) dominates the outcome: the bit is decided in about 15 generations and fixed in only half the L runs;
  D and E are both live: the readout cannot separate them, and the dose curve leaves little headroom above
  f₀ = 0.25 (headroom against R-all was present at the point, interval to 1.03). All three advisory thresholds
  held; the usefulness inspection the plan required is unresolved.

  Decision: park 55 because the probe answered what this procedure can answer cheaply: program selection gave the
  R-all carriers a small, resolved advantage over shuffled and size-matched controls (observation), but drift
  absorbed the bit within about 15 generations, so the extracted law's usefulness over the starting mixture is
  unresolved with a ceiling of about 0.73×, it is not better than fixed R-all, and a single population's law is a
  lottery that the dose curve makes worse in expectation. Confirming the allele movement alone would not change a
  decision (strategy 1427: "more inherited allele movement alone is not a useful answer"), and the 1-experiment
  budget is spent. A usefulness test needs a redesigned instrument (polymorphism kept by bit mutation or weaker
  drift, a starting frequency where the dose curve is steep), which strategy 1427 said is not automatically
  funded. Back to the strategist, as the proposal stated.

- 2026-10-11 (steward, 1530): wording correction after [critique 1530](../../runs/2026-10-11-1530/critique.md)
  (digest check, notes 6–9); the 1427 entry above is left as written, read it with these corrections. No numbers
  in the analysis change.
  - "328/336 by the end of episode 0" is wrong: analysis §2.1 and `exposure.jsonl` give **290/336** absorbed in
    episode 0 (L 88, S 80, Z 82, N 40), 45 in episode 1, one later. "Episodes 2–12 measured nothing" should read
    "episodes after the second measured almost nothing about the bit".
  - "Z still fixed at the neutral rate, so extra clones alone did not raise the bit here" overstates: Z 0.302
    [0.208, 0.406] is compatible with neutrality and with an increase. Read: no Z fixation excess was resolved; the
    controls do not fully separate content from robustness.
  - The dose curve does not "explain" L-final / S-final: it pools different build compositions, so it is
    consistent with a mixture/absorption account but does not identify the within-build counterfactual. The
    ≈ 1.2× single-population cost is an unvalidated pooled-curve projection, without an interval.
  - "Not better than fixed R-all" in the decision line: read "no improvement over fixed R-all was established"
    (1.21 [0.98, 1.46], point worse). The 55/96 vs 55/96 solve counts are equal observations, not equal rates.
  - "Drift decided every trajectory" / "C (drift) dominates the outcome": absorption is measured; attributing every
    outcome to drift is not, given the resolved linked selection differential. The question summary now says
    "every trajectory absorbed rapidly".
  The parking decision is unchanged: its reasons (allele movement alone does not change a decision; budget spent;
  usefulness needs a redesigned instrument) do not depend on these wordings.


- 2026-10-11 (steward, digest compression 1628): wording only, no belief changed. The digest's root-55 section
  now ends "One probe; observations only, in its [log](…). No beliefs yet." Former text:

  ```
  of an already useful donor law (R-all on the order cells), and does the result help fresh search? One
  probe so far; its observations are in the [log](questions/55-inherited-library-choice/log.md), not here.
  No beliefs yet.
  ```

- 2026-10-11 (steward, 1736): **reopened** by [strategy 1736](../../runs/2026-10-11-1736/strategy.md) (budget 1 → 2),
  meeting the reopen condition's first branch (bit mutation keeps the modifier polymorphic; low starting dose). Proposed
  the plan's single design: f₀ = 1/16, child bit redrawn from Bernoulli(1/16) with probability 1/32, arms L/S/N × 24
  libraries × 6, each population's own law deployed alone at q = 0.5·final f against q₀ = 1/32 and R-all
  ([proposal](../../runs/2026-10-11-1736/proposal.md)). Primary: L-final/q₀, useful if upper bound < 0.90, no worthwhile
  saving if lower bound > 0.80. Steward forecast, recorded before any data ([forecast_model.py](../../runs/2026-10-11-1736/forecast_model.py);
  1427's s ≈ 0.036, ~100 distinct parents, fitted pooled dose curve): L-final/q₀ ≈ 0.95, a 20% saving needs s ≈ 0.1.
  This is a model, not evidence.

- 2026-10-11 (steward, 1736): **experiment run** (commit `3a18ef5`; critic approve_with_notes, notes 1–5 taken in the
  [plan](../../runs/2026-10-11-1736/plan.md); [code review](../../runs/2026-10-11-1736/code_review.md) pass; queue
  615 s + 3,676 s of 9,000 s; [analysis](../../runs/2026-10-11-1736/analysis.md),
  [execution](../../runs/2026-10-11-1736/execution.md)). Six `x4-order-v1` development cells, 24 saved 1228 R-all
  libraries, P 256, lexicase, crossover 0.5. Bit f₀ = 1/16; each nonelite child's inherited bit redrawn from
  Bernoulli(1/16) with probability 1/32; twelve 64-generation episodes, programs reset, bits persist. Arms L linked,
  S shuffled before selection, N neutral (ordinary donors in both states), 24 libraries × 6 populations each. Each of
  the 432 populations deployed alone at q = 0.5 · final f, 6 cells × 2 fresh seeds × 8 restarts of 65,536
  evaluations, against q₀ = 1/32 and R-all (q = 0.5) on the same seed blocks. Grids complete (432/432 trajectories,
  8,640/8,640 readout jobs, 18 capped failures charged 524,288), seed and hash audits clean, protected cells unscored.
  - **Bit dynamics.** Mean final f: L 0.290 [0.230, 0.351], S 0.052 [0.035, 0.073], N 0.062 [0.038, 0.091];
    L − N 0.228 [0.158, 0.297], L − S 0.237 [0.172, 0.304]; L above both in 24/24 libraries. No absorption: L
    polymorphic in 94,661/110,592 generations. L is bimodal: 46/144 populations ended above 0.5, 55/144 at or below
    1/16. Pre-solve selection differential at 0 < f ≤ 0.25: L +0.0017 [+0.0011, +0.0022] per generation, N −0.0008;
    above f = 0.25 L's differential is about +0.016, ten times larger. Most of L's rise came in episode 1, then held
    near 0.3 with mutation pulling back. Mutation bookkeeping matched 1/512 and 15/512.
  - **Primary, L-final / q₀ 0.805 [0.704, 0.913]** (capped mean evaluations, nested paired bootstrap, 8,192 draws).
    Upper bound not < 0.90 and lower bound not > 0.80 → pre-set row 4, **unresolved** against the 10% bar. The
    interval excludes 1. Controls: L-final / N-final 0.746 [0.642, 0.860], L-final / S-final 0.699 [0.609, 0.797].
    L-final / R-all 1.71 [1.45, 2.01]; headroom q₀ / R-all 2.12 [1.83, 2.50] (≥ 1.25, so informative). Worker
    seconds give the same ratios. L cheaper than q₀ in 20/24 libraries, 94/144 populations and 6/6 cells by point.
    Library-only bootstrap (not the registered unit) [0.737, 0.876]. Dropping the 18 capped jobs: 0.811.
  - **The saving is a dose.** Each endpoint's cost is predicted within 6% by the 1427 dose curve at its own q
    (L 0.95, S 1.06, N 0.99 observed/predicted). L endpoints with f ≥ 0.25 (62) cost 0.53× q₀ on the same seeds;
    those with f < 1/8 (68) cost 1.04×. N and S cost more than q₀ despite mean q ≈ 1/32 because 35 N and 32 S
    endpoints sit at q = 0 on a convex curve.
  - **Economics** (reported): acquisition 214 k + exposure 197 k evaluations per population; the exposure saves 12 k
    per fresh search against q₀, repaying after about 16 searches; hand-set R-all needs no exposure and is 1.71×
    cheaper per search.
  - **Forecast miss** (steward, recorded before data): predicted L-final / q₀ ≈ 0.95, L mean f ≈ 0.13. Wrong by
    0.15 and 2×. The single-s model missed positive frequency dependence: selection is nearly flat while the bit is
    rare and much stronger once common, so populations that escape the low-f band run away and the rest stay at the
    mutation floor.
  Against the explanations (scope as above): A — supported at this scope: linked carriers rise above shuffled and
  neutral controls and the deployed law is cheaper than its start, but the pre-set 10% usefulness bar is unresolved.
  B — not supported in its strong form; the weak per-generation advantage while rare fits its weak form. C — drift
  does not explain L: L − N and L − S are resolved and N/S stay at the mutation floor. D — not supported for this
  readout: the frozen frequency helps fresh search through the dose curve. E — headroom was present (2.12×); the
  exposure was strong enough to move the bit in 43% of populations. New observation (hypothesis, not tested): the
  weak low-frequency selection with crossover 0.5 resembles root 01's finding that mixing between lineages blocks
  rare forms from establishing ([06](../01-map-bias/06-self-mate-establishment/question.md)).

  Decision: park 55 because the redesigned instrument answered what a dose-only selector can answer. Selection
  under recurrent mutation raised a useful supplied law's carrier above both controls (resolved), and one
  population's frozen law beat its starting law with an interval that excludes 1 but not the pre-set 10% bar. The
  dose analysis shows the law carries nothing beyond its frequency, so the remaining primary uncertainty (does the
  saving exceed 10%?) would not change any program decision: either way the evolved law is 1.7× costlier than
  setting q = 0.5 by hand, its exposure repays only after about 16 searches, and nothing about content learning or
  transfer follows. Resolving it is priced (about 432 more trajectories + 8,640 readout jobs, ~70 min queue, ~4 h
  complete, and the analysis's resampling suggests even that only just reaches an upper bound of 0.90); I do not
  recommend buying it. Not closed: the pre-set rule did not resolve, and the result is one mutation rate, one
  population size, one crossover rate and one supplied library. Budget 2/2 used; back to strategy, as strategy 1736
  and the proposal stated. No parked question's reopen condition is met (23's requires a selectable signal in
  token-frequency learning; this one is a supplied structured law with 2.1× headroom).


- 2026-10-11 (steward, digest compression 1736, second pass): wording only, no belief changed. The digest's root-55
  bullets lost these details (all stand; see the run 1736 entry above and [analysis](../../runs/2026-10-11-1736/analysis.md)):
  "child bit redrawn from Bernoulli(1/16)" (now "mutation rate 1/32 toward 1/16"); the bimodality counts "46/144
  above 0.5, 55/144 at or below 1/16"; and the upper bounds "0.86, 0.80" of L-final over the neutral and shuffled
  endpoints. Former text (links relative to `research/`):

  ```
  - **With recurrent bit mutation, linked selection raised the R-all carrier bit above both controls.**
    f₀ 1/16, child bit redrawn from Bernoulli(1/16) at rate 1/32, twelve 64-generation episodes: mean final
    f 0.29 [0.23, 0.35] linked, 0.06 neutral bit, 0.05 shuffled (L − N 0.23 [0.16, 0.30]; 24/24 libraries).
    Bimodal (46/144 above 0.5, 55/144 at or below 1/16): selection is weak while the bit is rare and
    about ten times stronger above f = 0.25.
  - **One population's frozen law made fresh search cheaper than its starting law, but by an amount the
    pre-set 10% bar does not resolve, and only through its dose.** Deployed alone at q = f/2 it cost 0.805×
    [0.704, 0.913] of q₀ (evaluations), and 0.75× and 0.70× of neutral and shuffled endpoints (upper bounds 0.86, 0.80). Every
    endpoint costs within 6% of the dose curve at its own q. Hand-set R-all is 1.71× [1.45, 2.01] cheaper and
    needs no exposure. One mutation rate, population size and supplied library; no content learning or transfer.
  ```
- 2026-10-11 (steward, 1938): wording corrections from [critique 1938](../../runs/2026-10-11-1938/critique.md)
  notes 7 and 10 (1736 entries above and the summary; the data are unchanged):
  - "every endpoint costs within 6% of the dose curve at its own q" claims more than was checked. 1736 §4 compared
    arm averages: the three arm-average costs (L/S/N) were within about 6% (0.95/1.06/0.99) of predictions
    averaged over their endpoint doses. Endpoint-wise accuracy was not tested.
  - 0.805 [0.704, 0.913] is the average over separate-population deployments, not a guarantee for one population:
    94/144 L endpoints were cheaper than their paired start.
  - "selection is about ten times stronger above f = 0.25" / "missed positive frequency dependence": the observed
    pre-solve selection differential was about ten times larger in the high-frequency stratum. That suggests
    frequency-dependent dynamics but is not an intervention on frequency or a tenfold normalized selection
    coefficient (absolute change also depends on f(1−f), program state and history).
  Summary in question.md and the digest corrected accordingly.

## 2026-10-12 — digest compression (steward task 2026-10-11-2353): wording moved here

The digest was 3037 words; it was rewritten to about 2,940. No belief changed. Two secondary observations from
[run 1736](../../runs/2026-10-11-1736/analysis.md) left the digest and stand as recorded above:

- Linked-selection bullet, after "Bimodal": "the observed pre-solve selection differential was about ten times
  larger above f = 0.25 (suggests frequency-dependent dynamics; not an intervention on frequency)."
- Frozen-law bullet: "94/144 endpoints beat their paired start".

## 2026-10-12 — reopened for content choice; steward headroom probe (task 2026-10-12-0250)

Reopened by [strategy 0250](../../runs/2026-10-12-0250/strategy.md). Before proposing, the steward ran a
≤ 10-min fixed-law probe with the unchanged engine (research/main `465f2fa`; [script and rows](../../runs/2026-10-12-0250/headroom-probe/)):
24 paired builds (1228 `semantic_all` b ↔ 1938 `semantic` b) × 6 development cells × 1 seed per family, all laws at
library probability 0.5; M = within-library-normalized 50/50 mixture. Capped mean evaluations (worker-s/job):

| family | O (order lib) | G (gate lib) | M (mix) | O/M | G/M |
|---|---|---|---|---|---|
| order (6 dev cells) | 27.9k (2.1) | 100.2k (7.4) | 36.0k (2.7) | 0.78 [0.51, 1.18] | 2.78 [1.85, 4.29] |
| gate (6 dev cells) | 7.9k (0.57) | 3.5k (0.22) | 5.1k (0.35) | 1.56 [1.01, 2.29] | 0.69 [0.47, 1.05] |

Observations only (one seed per unit; bootstrap over builds, cells within builds). Each library is much cheaper
on its own family; gate donors on order cells cost more than no library at all (1736's q = 0 was 74k on other
seeds). The mixture leaves roughly 20–30% headroom to the matched pure library in both directions. 142/144
G-on-order jobs solved. Probe seeds use the domain `steward-probe-2026-10-12-0250`.

## 2026-10-12 — experiment 0250: inherited content choice (order vs signed-gate library)

Experiment ([proposal](../../runs/2026-10-12-0250/proposal.md), [plan](../../runs/2026-10-12-0250/plan.md),
[analysis](../../runs/2026-10-12-0250/analysis.md); commit `4ed0469`). The bit chose which saved library supplied
donors (state 0: 1228 R-all order library, state 1: 1938 R-all signed-gate library, paired by build index), each on
half of mutations; redraw 1/32 toward Bernoulli(1/2), f₀ = 1/2. Exposure on six development cells of
`x4-order-v1` or `x4-signed-gate-v1`: twelve 64-generation episodes, P 256, lexicase, crossover 0.5. Arms L (linked),
S (shuffled), N (neutral, both states 50/50). 24 builds × 8 populations × 3 arms × 2 families = 1,152 trajectories;
36,288 readout jobs, each population's law deployed alone (gate share f/2). Data complete, all audits passed, 19/36,288
readouts capped (order only), no protected cell scored.

Result:
- **Primary R (geometric mean over families of L-matched / M) 0.991 [0.926, 1.060]** (capped mean evaluations, nested
  paired bootstrap). Order L-matched/M 0.982 [0.882, 1.093]; gate 0.999 [0.928, 1.075]. Pre-set rule: upper not
  < 0.90, lower > 0.80 → **"20% pooled saving excluded"**, which the proposal said ends the candidate. Neither family
  met its directional conjunction (gate L-matched/L-swapped 0.929 [0.856, 1.005]; order 0.953 [0.846, 1.081]).
- **Headroom was present:** own pure library / M 0.725 [0.594, 0.876] on order, 0.778 [0.679, 0.887] on gate. So this
  is a negative for this selector and exposure rule, not saturation.
- **Bit dynamics.** Mean final f (gate share): order L 0.377 [0.341, 0.413] vs S 0.485, N 0.486 (L − S −0.108
  [−0.163, −0.056], 22/24 builds); gate L 0.516 [0.472, 0.560] vs S 0.484, N 0.475 (L − S +0.032 [−0.029, +0.095],
  unresolved). Selection moved the bit toward the matched library, resolved only on order, and by far less than I
  predicted (0.15–0.3 on order).
- **Why so little (descriptive decomposition of this run's traces):** selection on the bit acted almost only before
  each episode's first solve (order −0.0064 per generation, gate +0.0037; about ten times weaker afterwards), while
  the redraw pulls f toward 0.5 at (0.5 − f)/32 every generation. On order, f fell to about 0.24 at first solve and
  relaxed to about 0.38–0.43 by episode end; the readout froze the relaxed value.
- **The endpoint law carries nothing visible beyond its frequency.** On a dose curve built from S, N and L-swapped
  endpoints, L-matched's endpoints predict 0.90 of M on order (observed 0.98; 0.96 without capped rows) and 1.01 on
  gate (observed 1.00). L-matched/S 0.94 [0.83, 1.06] and /N 0.97 [0.86, 1.10] on order; 0.97 and 0.98 on gate, all
  containing 1.
- Economics (reported): exposure saves ~740 evaluations per fresh order search (~260 searches to repay), ~6 on gate.
  The pure matched library (no exposure) stays cheapest on each family.
- Forecast miss (mine, recorded before data): R ≈ 0.85–0.9 and order f 0.15–0.3. I priced the endpoint as if selection
  acted throughout exposure; with f₀ and the redraw target both at 1/2, the mutation pull opposes selection at full
  strength, unlike 1736 (redraw toward 1/16, selection pushing up).

Against the explanations (scope: twelve development cells, two supplied libraries, this exposure rule):
A — not supported for content choice: linked carriers moved the right way on order, but the frozen mixture was no
cheaper than the start (pooled savings above about 7% excluded; smaller ones not) and not resolved cheaper than S or
N. B — consistent: the useful library helped carriers only during the short pre-solve phase. C — drift does not
explain the order shift (L − S resolved); on gate the shift is unresolved. D — partly: the readout froze a
maintenance-phase balance, not the pre-solve selected frequency. E — headroom present; the exposure rule was too weak
to hold a useful frequency (the pre-solve minimum 0.24 sits where other populations' endpoints cost 0.73–0.83 of M —
a projection, not measured for frozen pre-solve laws).

Decision: park 55 because the pre-registered content-choice test answered its question at this scope: program-linked
inheritance moved the choice toward the suited library on one family but left no frozen saving (R 0.99
[0.93, 1.06], 20% excluded, headroom 22–28% present). The strategy and proposal both said this outcome ends the
candidate and returns to strategy; budget 3/3 is spent. Not closed: savings under 10% are not excluded, and a
different exposure rule (freeze at first solve, or a redraw not aimed at the start) could behave differently — that
is a new design, not a top-up, and the observation behind it is a projection. No parked question's reopen condition
is met (23 needs a selectable token-frequency signal; 50 needs default mixed deployment).

- 2026-10-12 (steward, 0250, digest wording): to make room for the content-choice bullet, the digest's 1736 bullet
  lost "L − N 0.23 [0.16, 0.30]; 24/24 libraries", "0.75× and 0.70× of neutral and shuffled endpoints", "needs no
  exposure" and "one mutation rate, population size and supplied library". All stand as recorded above; no belief
  changed.

## 2026-10-12 — digest compression (steward task 2026-10-12-0250): wording moved here

The digest was 3030 words; it was rewritten to about 2,970. No belief changed. The content-choice bullet lost the
endpoint levels behind the difference, which stand as recorded above ([run 0250](../../runs/2026-10-12-0250/analysis.md)).
Former text: "Final gate share on order 0.377 vs 0.485 shuffled (L − S −0.11 [−0.16, −0.06]); on gate +0.03 [−0.03,
+0.10], unresolved." Now: "Final gate share, linked minus shuffled: order −0.11 [−0.16, −0.06]; gate +0.03 [−0.03,
+0.10], unresolved."
