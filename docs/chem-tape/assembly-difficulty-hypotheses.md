# Assembly-Difficulty Hypotheses (scratch note, unvalidated)

**Status:** UNVALIDATED HYPOTHESES · scratch note, not a findings-level claim · 2026-04-15

**Scope.** This note enumerates candidate axes for predicting how hard a canonical body is to evolve under chem-tape's BP_TOPK decoder. It is a **pre-registration framework**, not a deployed metric. None of the axes below are empirically calibrated — the project currently has n=3 body shapes with informative data (§v2.3, §v2.6 Pair 1, §v2.6 Pair 2/3 with the latter two swamped and therefore uninformative for body-structure difficulty). Methodology §8 applies: n=3 is hypothesis-generation, not predictor-fitting.

**What this note is *not*:**

- **Not** a scoring function. Do not compute a scalar "assembly difficulty score" for any body on the basis of this note and use it downstream. Hand-weighted sums over these axes at n=3 trivially reproduce the ranking they were built to predict (methodology §4 — degenerate-success guard applies to metrics, not only experimental outcomes).
- **Not** a finding. Nothing here enters `findings.md` until at least two of the axes below have independent regression coefficients from ≥2 controlled experiments with varied bodies.
- **Not** a validated predictor. Treat every axis as "plausibly load-bearing, not yet tested."

---

## Motivation

§v2.6 showed Pair 1 (6-token `INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT`, string domain) fails at 4/20 BOTH while §v2.3 (4-token `INPUT SUM THRESHOLD_SLOT GT`, integer domain) succeeds at 80/80. The §v2.6 baseline-completion chronicle (commit `dbca965`) narrows the `constant-slot-indirection` finding from `across-family` to `one pair` and leaves an open mechanism question: **is Pair 1 harder because of body length, input domain, assembly-transition cliff, or something else?**

§v2.7 (prereg at [`Plans/prereg_pair1-transitions.md`](../../Plans/prereg_pair1-transitions.md)) measures partial→canonical transition rates directly on existing trajectory data. The queued §v2.6-pair1 follow-ups (scale-8x, scale-A, tape24) test budget, decoder, and tape-length axes. Once those land, the observed dependence of solve rate on body-structure features can be regressed against candidate axes below.

This note organises the candidate axes so that future preregs can test **one axis at a time**, holding the others constant.

---

## Candidate axes (hypotheses, not metrics)

Each axis below has: (a) what it measures, (b) how to make it objective (avoid 0/1/2 hand-coded rungs), (c) the controlled experiment that would calibrate it.

### L — required-token count in the canonical body

- **Measures:** structural length of the required-token set in the canonical BP_TOPK-extracted program.
- **Objective version:** `|canonical_token_set|`. Computed purely from the body definition, zero judgment.
- **Already observed:** Pair 1 = 6; §v2.3 = 4. Confounded with input-domain in current data.
- **Disambiguating experiment:** §v2.8 — a 6-token integer body OR a 4-token string body, holding input-domain constant while varying L, or vice versa. Regression coefficient on L can be estimated from §v2.8 + existing §v2.3/§v2.6 data.
- **Expected strength:** probably a weak predictor on its own. Length matters only because it carries more of the axes below.

### O — strict order-constraint count in the canonical dependency DAG

- **Measures:** number of must-precede edges in the canonical-body DAG (e.g., `INPUT < SUM`, `SUM < THRESHOLD_SLOT`, `THRESHOLD_SLOT < GT`).
- **Objective version:** extract the dependency DAG from the BP_TOPK execution semantics of the canonical body. Count directed edges. No judgment.
- **Already observed:** Pair 1 ≈ 5 edges; §v2.3 ≈ 3 edges. Correlated with L but not identical (a 6-token body with a loose DAG could have fewer edges than a 4-token strict chain).
- **Disambiguating experiment:** construct two bodies with matched L but different O (e.g., L=5 strict chain vs L=5 with a commutative pair). Run §v2.9-style test.
- **Expected strength:** likely a stronger predictor than L alone. Strict order is what makes partial-token assemblies mechanically invalid.

### D — depth from root to first task-informative node

- **Measures:** how many canonical tokens must be correctly assembled before the body emits a scalar with non-trivial fitness correlation to the target label.
- **Objective version (the hard part — do NOT hand-count):** for each canonical prefix of length 1..L, evaluate the prefix-program's fitness on the task training set. `D = smallest k such that mean-fitness-of-prefix-k ≥ (random_baseline + α)` for some pre-registered α (say 0.1 above 0.5). Requires a per-prefix evaluation sweep, not a judgment call.
- **Already observed:** not yet computed. §v2.7's milestone-trajectory data does *not* directly give D because §v2.7 reports milestones, not prefix-fitness. D would need a separate cheap analysis script on the same history.csv data.
- **Disambiguating experiment:** pre-register §v2.10 to compute per-prefix fitness for each of the current canonical bodies (§v2.3, Pair 1/2/3). One-time cost, reusable across future bodies.
- **Expected strength:** probably the load-bearing axis. "Partial body with zero gradient signal" is precisely what traps evolution.

### I — count of invalid partial prefixes

- **Measures:** number of prefix programs (prefixes of the canonical token sequence) that execute to zero or near-zero fitness on the training set.
- **Objective version:** same prefix-evaluation sweep as D. `I = |{k : mean-fitness-of-prefix-k ≤ random_baseline + α}|`. Pre-registered α.
- **Already observed:** not yet computed. **Crucially, this is what §v2.7's M_near and M_partial are measuring empirically** via mutation neighborhoods — hand-coding I before §v2.7 lands would prejudge the experiment.
- **Disambiguating experiment:** wait for §v2.7 to land; I can be read off the milestone-transition data plus per-prefix evaluation.
- **Expected strength:** very likely the strongest single predictor if the "assembly cliff" hypothesis lands under §v2.7.

### R — run fragility

- **Measures:** does the canonical body tolerate fragmentation (tokens surviving across non-contiguous runs in BP_TOPK) or does fragmentation destroy semantics?
- **Objective version (open problem):** does not have a clean objective definition yet. Candidate: simulate every way to split the canonical token set across K runs and measure fitness degradation. Expensive and schema-dependent.
- **Already observed:** not measured. Current proposals in the literature (the user's note above) use 0/1/2 hand rungs — not objective, operator-dependent.
- **Disambiguating experiment:** defer. Not worth formalising until the simpler axes (L, O, D, I) have been calibrated.
- **Expected strength:** unknown; depends on how often BP_TOPK actually fragments canonical candidates. Could be trivially zero if BP_TOPK almost always keeps canonical bodies intact, or could be a dominant factor.

### S — stack fragility under order perturbation

- **Measures:** how fitness changes under permutation of the canonical token sequence (holding the token set constant, varying order).
- **Objective version:** sample random permutations of the canonical token set, evaluate each, report fitness-under-permutation distribution. `S = 1 − (mean-fitness-of-random-permutation / mean-fitness-of-canonical)`.
- **Already observed:** not measured.
- **Disambiguating experiment:** a single cheap post-hoc analysis on each canonical body (≤1000 permutations at ~10 ms each = ~10 s per body).
- **Expected strength:** likely important but largely predicted by O (strict order constraints). Running S-measurement per body would tell us whether S adds anything beyond O.

---

## The DAG formalisation (cleaner than a weighted score)

Rather than collapse these into a scalar `BADS = aL + bO + cD + dI + eR + fS`, publish a tuple per body:

```
canonical_body_profile(body):
    L        = |canonical_token_set|
    O        = |must-precede edges in canonical DAG|
    D        = smallest k with prefix-k-fitness ≥ baseline + α
    I        = #k with prefix-k-fitness ≤ baseline + α
    R        = deferred (measurement not formalised)
    S        = 1 − (mean permutation fitness / canonical fitness)
```

Report all five (or six) components separately. Let downstream correlation tests decide which predict BOTH solve rate / first-hit-gen / ADI / `M_near` / partial→canonical transition rate.

**Why a tuple beats a scalar:**

- No weight-fitting at n=3 — we'd overfit trivially.
- Each component is independently testable with a designed experiment.
- The correlation structure (which axis dominates which outcome) becomes a finding itself rather than being hidden inside a weighted sum.
- Failures of prediction are diagnosable: if the tuple matches but the BOTH rate doesn't, the hypothesis that "assembly difficulty predicts BOTH rate" is itself falsifiable.

---

## Cross-references

- **Prereg §v2.7** — [`Plans/prereg_pair1-transitions.md`](../../Plans/prereg_pair1-transitions.md). Will give empirical `M_near`, `M_partial`, and decomposed `R` (partial→canonical and near→canonical) for Pair 1 vs §v2.3. These are the first data points for the `I` axis above.
- **§v2.6 baseline-completion chronicle** — [`experiments-v2.md §v2.6`](experiments-v2.md). The narrowing that motivates this note.
- **Queued Pair-1 follow-ups** (separate preregs, axes indicated):
  - `§v2.6-pair1-scale-8x` — budget axis. Tests whether Pair 1's failure resolves at 8× compute; complementary to all BADS axes (if yes, the "difficulty" is budget-bound, not structural).
  - `§v2.6-pair1-scale-A` — decoder axis. Tests whether the difficulty is BP_TOPK-specific (R and S in particular may be decoder-dependent).
  - `§v2.6-pair1-tape24` — tape-length axis. Shorter tape may change how partial assemblies execute.
- **§v2.8** (not yet pre-registered) — body-length vs input-domain disambiguation. Will give first regression coefficient on L independent of input-domain.

## Downstream commitment

When enough axes have landed independent calibration (≥2 regressions from controlled experiments with ≥10 bodies total), this note can be retired in favour of a findings-ledger entry with scope tag, commit hashes, and validated predictors. Until then, **do not cite axis values as evidence, do not build a composite score, do not compare bodies on "BADS"**. Cite specific measured values (e.g., `M_near_P1 = 0.03`) tied to specific experiments only.

## Review history

- 2026-04-15 — created as a scratch note during §v2.7 prereg finalisation, after discussing a proposed BADS (Body Assembly Difficulty Score) composite metric. The composite form was deferred to post-§v2.8; this decomposition-into-axes form is the hypothesis-generation version kept around for future prereg design.
