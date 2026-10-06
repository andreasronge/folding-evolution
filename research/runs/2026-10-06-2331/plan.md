---
estimated_minutes: 198
---

# Pre-registration: decoder initialization × ongoing use

**Status:** implementation pending, 2026-10-06. This plan implements the approved
[proposal](proposal.md); its grid, budgets and gates are unchanged. The final task
commit is the execution target. No full experiment is run by the researcher.

## Question (one sentence)

How much of the frozen 1723 maps' search gain on the three reused 2229 cells is
retained by learned starting programs and by continued use of the learned decoder?

## Hypothesis

The ongoing decoder may suffice conditional on initialization, but both components
may contribute; the approved prediction is rows 1/3/5/4/2 at 45/30/12/8/5%.
Probe arm means inform this prediction and are not untouched evidence.

## Setup

- Four arms: GG and MM use original uniform alleles; MG preserves MM's complete
  token tapes and searches under G; GM preserves GG's complete tapes and searches
  under M. GG is run once per seed/cell and shared across all 20 maps.
- All ten BE and ten PA frozen 1723 maps, equal family weight and equal map weight
  within family; no selection or merging. Preserve artifact hashes and provenance.
- Cells: BE `S?m:(M+F)`, PA `(F?S:M)+m`, PA `(S?M:m)+F`.
- Main seeds 2331000–2331399 (400), shared across arms/maps/cells. Probe seeds
  9000000–9000024 and historical seeds are excluded from inference.
- G4, D1331, v2_rmin_first, length 32, population 256, lexicase, crossover .7,
  mutation .03, cap 524288, exact full-domain verification remain unchanged.
- Initialization alone changes: conditional-uniform inverse encoding uses
  default_rng([seed, 3]); cases, initialization, variation and selection retain
  their original streams. All positions, including inactive tokens, are encoded.
- Main count 73200 searches. Additional MMr self-reencoding check: all maps/cells
  on the first 100 main seeds (6000 searches). Historical reproduction: 21 tables
  × three cells × seeds 2229002–2229011 = 630 searches.
- Ten workers with single-threaded scoring. Estimated queue 132 minutes, 198 with
  1.5× slack; queue timeout 18000 s and internal deadline 16200 s including gates.
  Seed-major scheduling completes every arm/map/cell of a seed before starting
  the next seed. Analysis uses complete blocks, minimum 200 main seeds.

## Baseline measurement (required)

GG is the concurrent baseline and MM the learned diagonal. Cost T is evaluations
to first exact solve, or 524288 if unsolved. Reproduce GG cell solve fractions
≥85% and diagonal D = log2(T_GG/T_MM) with lower 95% bound > log2(1.25).
These guards come from the approved proposal and prior 2229 baseline, not an
inferred population ceiling. No sampler or target function changes.

## Internal-control check (required)

MG/MM starts from identical complete ordered token populations; GM/MM holds the
ongoing decoder fixed. These are primary P1=log2(T_MG/T_MM) and
P2=log2(T_GM/T_MM). Also always report I_G=log2(T_GG/T_MG),
O_G=log2(T_GG/T_GM), D, interaction P1−O_G, and descriptive I_G/D, O_G/D.

## Pre-registered outcomes (required — at least three)

Use first matching row. Labels: N if upper 95% bound < δ=.25 log2; P if
lower >0 and upper ≥δ; X otherwise. N can be negative; flag upper <0 as
antagonism. P is resolved positive, not proof of a ≥1.19× increment.

| Row | Criterion | Conditional interpretation |
| --- | --- | --- |
| U | Any validation fails; <200 complete seeds; any GG cell solve fraction <.85; or D lower bound ≤log2(1.25) | Intervention/reproduction/coverage problem; mechanism uninterpretable. |
| 1 | P2=N, P1=P | Ongoing M suffices at this margin; learned start adds <1.19× **given ongoing M**. A substantial start effect under G remains possible. |
| 2 | P1=N, P2=P | Learned start suffices at this margin; ongoing M adds <1.19× **given learned start**. This is not an exclusively initial-supply mechanism. |
| 3 | P1=P, P2=P | Both conditional increments are positive; use interaction and secondary effects to describe combination. |
| 4 | P1=N, P2=N | Components are conditionally redundant at the margin; if a mixed arm resolves below MM, report antagonism explicitly. |
| 5 | Any X (remaining five cells of the N/P/X cross-product) | Attribution unresolved, including intervals spanning zero and δ. |

Per-cell, per-family and secondary effects cannot override the row; they are
descriptive effect sizes. Routing uses CI bounds with ≥200 complete main blocks,
20 retained maps and the fixed resampling protocol below, not point means.

## Degenerate-success guard (required)

Wrong encoding or lost inactive tokens: exact round trips plus paired population
hashes. Accidental changes to search/RNG: historical substantive-row reproduction.
Distorted conditional allele draws: positive-width and interval-bound assertions,
the conditional-law argument below and a marginal chi-square diagnostic.
False apparent parity: report all interval widths and never equate non-rejection
with equivalence. Ceiling/failed solve effects: report cap counts and solve
fractions, and require the diagonal gain guard. Hash checks do not alone establish
the initialization law; the law check does not alone establish search reproduction.

Validation before the main grid:

1. Decode uniform source alleles, then G→M and M→G for all 20 maps, 10000 tapes
   per direction/pair; require exact equality and interval bounds at every position.
2. G, BE1, PA1 self-encoding, 1000000 alleles each, 240 equal-width bins:
   chi-square failure p<.05/3. Source tapes are decoded from uniform alleles.
   This is only a marginal diagnostic. Conditional law: each tape's probability
   is the product of destination interval widths/24000; drawing uniformly within
   every corresponding interval cancels these widths, recovering the independent
   uniform allele law when source=destination. Positive widths are mandatory.
3. Source=destination with original alleles: compare evaluations, solved and curve
   exactly with historical 2229 search.jsonl (630 rows). Runtime metadata excluded.
4. Every row logs SHA256 of generation-0 full ordered token tapes. For each seed,
   map and cell, MG=MM and GM=GG; mismatch stops before another seed.
5. MMr/MM 99% crossed-bootstrap interval must contain log2 ratio 0. Exclusion
   fails validation and stops before main expansion beyond the first 100 seeds.
   Report estimate and width; containing zero is not equivalence.

## Statistical test (if comparing conditions)

Search inference is exploratory, effect-size/interval based lab-notebook routing,
not paper-level confirmatory p-value claims. No new confirmatory family is opened.
Three chi-square engineering diagnostics form a separate initialization-validation
family, Bonferroni .05/3; this gates implementation validity, not a mechanism claim.
MMr/MM uses the approved 99% interval validity gate; containing zero proves no
equivalence. No tests of per-cell/family descriptive contrasts are added.

Primary uncertainty: 20000 crossed bootstrap replicates, fixed seed 2331400.
Resample ten maps with replacement independently within BE and PA; independently
resample whole seed blocks, using the same sampled seed indices across every arm,
map and cell. Average paired log2 costs over seeds, cells equally, and families
equally. This retains shared GG and common-seed covariance for every contrast.
Use percentile 95% intervals (99% for law check). Report original map-level t
intervals as sensitivity: for GG-based contrasts, the proposal's additive GG-seed
variance correction is explicitly a sensitivity approximation, not primary.
Recompute uncertainty using actual complete n; 200-seed fallback does not inherit
the 400-seed precision estimate. Mixed-contrast spread is measured, not assumed
equal to historical diagonal spread. Report bootstrap configuration and n.

## Diagnostics to log (beyond fitness)

Pending infrastructure extension, to be completed and checked before queueing:
composition_search emits initial token SHA256 and initialization parameters;
new run harness emits arm/map/family/cell/seed, evaluations, solved, curve, runtime
and all source artifact hashes. New analysis groups the full arm×map×cell×seed
grid, computes all contrasts and widths, per-cell/family summaries, solve fractions,
shares, t sensitivity and outcome row, and plots contrast intervals and solve/cost
diagnostics. All outputs under RUN_DIR. No requested measurement is a proxy.
Implementation/smoke evidence and gate decisions are saved in this task folder.

## Scope tag (required for any summary-level claim)

20 frozen maps, three screened/reused cells, supplied G4 context, D1331, this
population/operator/budget regime. Ongoing decoder use bundles inherited latent
alleles, mutation, crossover and continued selected program supply; it does not
isolate neighbourhood quality beyond sampling. Starting programs include partial
programs. No claim of learned context, family specificity, or untouched transfer.

## Decision rule

Rows 1–4: steward may propose slot 2 on the ten training cells, sized from measured
spread/cost. U or 5: return to strategy before slot 2. If implementation smoke
finds the approved design infeasible, write measured infeasible.md, commit and stop
without a full queue or redesign.

Critique notes 1–5 are addressed above. Preserve any discoverable steward probe
source/raw timing provenance; do not invent missing probe artifacts. Notes 6–8
concern digest/question corrections, outside the researcher's authorized task
folder, and are deferred to the steward; no belief files are edited here.
