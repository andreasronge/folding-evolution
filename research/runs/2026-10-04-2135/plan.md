# Pre-registration: 2026-10-04-2135 shared arrival

**Status:** QUEUED · 2026-10-04 · implementation commit recorded by queue metadata.
This is the execution plan for the approved proposal; approval.md overrides proposal.md.
Written before implementation, tests, throughput pilots, or experimental draws.

## Question (one sentence)

Do exact shared children rarely arrive, or rarely establish from one copy, in
the §32 J self-mate / crossover 0.3 / L64 established non-shared populations?

## Hypothesis

Both explanations remain live. Frozen final populations can constrain arrival
at those endpoints; inference about the historical established phase requires
a faithful mid-phase check. First discovery is outside scope.

## Setup

- One full queue entry, two stages, saved §32 J self/0.3/L64 cohort (50 seeds).
- Source root: experiments/output/2026-10-04/mapbias_s32_mate in the main repository.
  Log the resolved path, config, seed, source hashes and source population for every draw.
- Reuse engine reproduction and training evaluation. Frozen generations include
  elite selection and lexicase from all individuals; census only the 1022 new
  offspring, not the two retained elites. TAG mutation 0.015 and self-crossover v2.
- Deterministic master seed 321350; census seeds derived from master plus source
  seed and phase; continuation seeds 321351000 + trial index, same in both arms.
  Smoke tests use separate seed 321359 and do not enter full-run estimates.
- Stage 1: round-robin frozen generations across all 50 populations; target
  30,000,000 partly-parent draws, floor 3,000,000, wall cap 7200 seconds.
  Always report achieved all-offspring and per-stratum denominators, including
  when the partly-parent target/floor cannot be reached. Cache clones/semantic
  keys, with training-case rejection before exactness. Do not silently enlarge.
- Optional cheap side check: replay five deterministic partly-ending sources to
  midpoint of established non-shared phase. Require logged best hex AND all
  comparable history/census values and final full population fidelity; reject
  replay on mismatch. Bound replay cost separately; if absent/unverified,
  explicitly restrict conclusions to final populations.
- Stage 2: 100 natural single-copy insertions plus matched no-insertion controls,
  500 generations, own source config, 10 workers. Source distribution is
  proportional to population's historical exposure times its measured arrival
  rate, with children sampled by occurrence frequency within source. No balancing
  by layout and no 1/5 cap (owner override). If fewer than five sources produce
  arrivals, use the available arrival-weighted mixture, report concentration,
  and do not generalize to missing populations. If the historical target has
  no arrivals, skip stage 2; descriptive arrivals elsewhere are not substitutes.
- Stop after 100 if at least five inserted lineages establish, or estimated
  arrivals per target run are at most about one. Extend to 300 only if fewer
  than five establish and estimated arrivals per run are at least about ten.
  Intermediate exposure stops at 100 and remains unresolved as appropriate.
- No natural arrivals: skip foreign-genome transfers entirely (owner override).

## Baseline measurement (required)

Historical target: one late replacement in sixteen runs first established as
non-shared, roughly 24M total offspring exposure. Recompute each source's
established non-shared duration from saved census using the historical minimum
20 exact non-elite individuals and 50% form criterion. Censor transition times
at logged observations; report the duration convention and bounds. The seventeen
exact-ending and all other source populations remain separately visible.
Use each target source's all-offspring rate r_k and exposure T_k: E_k=T_k*r_k;
E=sum(E_k)/16. Include every non-shared parent stratum, including shortcuts/other.
Never use the partly-parent conditional rate as an all-offspring rate.

## Internal-control check (required)

Same source population and seed, insertion versus no insertion. First continued
generation replaces one randomly chosen non-elite offspring with the newborn.
Track descendant flags through engine parent rows (both parents, elites included).
The slot RNG is separate so intervention does not shift reproduction randomness.
Controls estimate independent shared establishment; helper identity is not ancestry.

## Pre-registered outcomes (required — at least three)

The following grid is advisory mechanism discrimination, not a significance gate.
Use confidence bounds and source-specific inspection; uncertain bins are INCONCLUSIVE.
Natural-copy p refers to descendant exact-shared establishment at 500 generations.

| historical exposure E per run | p low (consistent with <=1/E for E>=10) | p intermediate (~0.01–0.10 or uncertain) | p substantial (bounds support >=0.10) | p unmeasured / persistent-submajority dominated |
|---|---|---|---|---|
| <=1 | partial: low arrival, additional establishment limit possible | partial: low arrival | arrival-limited late replacement, subject to replay scope | INCONCLUSIVE: low endpoint arrival only |
| 1–10 | both may limit; INCONCLUSIVE if bounds broad | both may limit; compare source-aligned product | partial: both factors; inspect per source | INCONCLUSIVE |
| >=10 | fixation-limited if natural lineages mostly extinct and bounds resolve | partial / INCONCLUSIVE | neither factor explains rarity alone; INCONCLUSIVE | INCONCLUSIVE |
| exposure bound too loose / unknown | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE |

Zero arrivals with bounds looser than ~1e-6, material mid/final disagreement,
concentrated arrivals without source coverage, or >10x inconsistency with the
single observed replacement without a visible cause prevent a broad explanation.
Low arrival alone does not exclude an additional establishment bottleneck.
Five establishments in 100 do not demonstrate p>=10%.

## Degenerate-success guard (required)

Exclude shared-parent clones from new arrivals; distinguish training shortcuts
from exact children; check census totals and parent-index alignment. Require at
least 20 exact non-elite individuals for establishment. Independent arrivals
must not masquerade as inserted-lineage successes: report descendant survival,
descendant exact-shared share, and total shared share separately, including elite
descendants. Report helper categories separately for descendant exact-shared copies.
Extinction observations every ten generations and at horizon include the full
population; loss times are interval-censored and can be right-censored.

## Statistical test (if comparing conditions)

Exploratory estimation only: zero confirmatory tests / no FWER claim gate.
Report per-source binomial confidence intervals, pooled descriptive intervals,
and source-aligned E_k*p_k consistency checks only when p_k is measured. Exact
binomial bounds describe frozen draws / sampled trial mixtures, not untested
populations; clustered population variation is reported separately. No product
of differently weighted pooled estimates. No training sampler change.

## Diagnostics to log (beyond fitness)

All metrics are **pending an infrastructure extension**, implemented and verified
before the full queue: new experiment harness with per-source/phase/parent-stratum
grouping, occurrence-preserving arrival archive, continuation lineage census,
source-specific report and plots. Existing engine evaluate_population and
_reproduce provide training results and parent rows; multi_output provides exact
classification and shared census. Files: manifest.json, census.json,
arrivals.jsonl, trials/*.json, summary.json, report.md, diagnostics.png and COMPLETE.
The report must include throughput, target/floor/cap status, rates and bounds,
duration/exposure weighting, source concentration, replay fidelity or omission,
helper forms, descendant/total trajectories, loss intervals and unresolved trials.

## Scope tag (required for any summary-level claim)

One multi-output task, TAG v2, L64, self-mate, crossover 0.3, mutation 0.015;
late replacement, endpoint populations unless mid-phase fidelity is verified.
Small source-specific trial counts (<20) are hypothesis-generating only.

## Decision rule

All resolved grid cells close the shared-helper line with both factors and scope
stated. All unresolved cells park it with reopen condition: instrumented
deterministic replay recording arrivals and fates in situ. No extra sweeps or
first-discovery claims. This implementation commits runnable infrastructure and
the queue, not findings or research-tree decisions.

## Pre-full-run source validation amendment (2026-10-04)

Small-scale infrastructure validation found that seed 23 (`93f5c0aef31a`) has
34 exact final non-elites but never 20 exact individuals in the saved sampled
census (maximum 12 of 256). Thus the approved 16-source terminal target contains
15 sources with observed historical establishment and one unmeasured duration.
Retain all 16; mark seed 23's duration unmeasured, with conservative range
0–3000 generations, and report the known-exposure contribution separately.
The historical first-form criterion is >90% of at least 20 exact **sampled**
individuals, not 50% and not a full non-elite historical measurement. New
continuation verdicts still use >=20 full exact non-elites and >=50% share.
These historical sampled durations are a labelled occupancy proxy. They do not
silently become full-population establishment times. The known-duration source
exposure is 21,257,600 offspring, rather than the proposal's approximate 24M.

Trial weighting uses occurrence frequency times exposure/draws for eligible
non-shared target endpoints with observed duration. An arrival from the source
with unknown duration has unknown historical mixture weight; preserve its
occurrences and report p as unmeasured rather than imputing a weight. The
sampled mixture's exclusions are explicit. Missing duration prevents a whole
cohort point estimate and a low-arrival stopping claim; a >=10 known-exposure
contribution can still justify the pre-approved extension to 300 pairs. If no
weightable natural arrivals exist, skip continuations and label establishment
unmeasured, even if descriptive or unknown-exposure sources produced arrivals.

The optional replay budget is 600 seconds total, separate from the 7200-second
main census cap, and the default cheap midpoint census is 32 frozen generations
per verified replay. Report midpoint uncertainty; fidelity verification by
itself does not prove temporal representativeness. Conclusions remain scoped to
measured endpoints/midpoints and historical extrapolation remains a proxy.
