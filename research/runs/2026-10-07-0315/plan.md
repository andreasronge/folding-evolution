---
estimated_minutes: 400
---

# Approved training-bank initialization intervention

Written before executing experiment code. Implements [proposal.md](proposal.md), with
[critique.md](critique.md)'s interpretation and routing notes. No full run is launched
by the researcher. This is implementation of the approved design, not a new prereg.

## Conditions and seeds

Retain all 20 frozen 1723 maps (BE1–10, PA1–10), verified source hashes, G4,
D1331, v2_rmin_first, tapes 32, population 256, lexicase, crossover .7,
mutation .03, cap 524288, 64 training cases, exact verification on 1331 inputs.
Use the four BE and six PA training cells listed in the proposal/1723 config,
without selecting maps or cells based on smoke outcomes. Four arms: GG shared
once per cell/seed; MM; MG preserves MM's complete generation-0 token tapes
while searching under G; GM preserves GG's tapes while searching under M.
Conditional-uniform inverse encoding at generation zero uses [seed,3]; all
other RNG streams and the search engine stay unchanged. Drop MMr and its law
check; the previous non-rejection did not prove equivalence.

Full seeds 3150000–3150199, shared by all conditions: 122000 searches. Dispatch
at most two consecutive seed blocks together. Retain only whole checked blocks,
in seed order, so a deadline leaves a balanced prefix. Minimum 120 complete
seeds. Smoke uses 3150900–3150901 at cap 8192; feasibility uses those same two
excluded seeds at full cap across all maps/cells/arms, to measure mixed-arm
costs, cap rates and two-block efficiency. Smoke/probe data never enter inference.

Before the grid: G↔M round trips, 10000 tapes per direction for each of 20 maps;
420 bit-exact substantive fresh-score reproductions from 1723 (all 21 tables,
ten cells, seeds 1723300–1723301); 366 substantive-row reproductions from 2331
(all four arms, three cells, seeds 2331000–2331001). Verify reference identity,
counts, and hashes. Runtime metadata excluded from exact comparisons. Every
main block checks MG=MM and GM=GG ordered full-token hashes, training indices,
source/destination tables and row coverage. Any validation failure stops grid
execution. Reduced smoke may use one historical seed; full validation remains
queued. No marginal-law or MMr diagnostic is added.

## Budget and feasibility

Conservative expectation: 6.4 hours search plus approximately 10 minutes for
validation and 6 minutes reporting = about 400 minutes. The proposed 5.3-hour
estimate assumes an unmeasured dispatch improvement; it is not the budget basis.
Internal deadline 25200 seconds includes validation and a 360-second reporting
reserve; queue timeout 27000 seconds (7.5 hours, below 8-hour cap). Measure first
complete two-block batch without selecting cells/maps. Report CPU cost, wall time,
effective workers, per-arm/cell cap rates and projected 120/200-seed runtime.
If measurements show the design cannot reach its minimum within the approved
budget, write infeasible.md and stop for steward replanning. Small-n cap rates
are diagnostics, not a replacement for the full-run coverage gate.

## Measurements and inference

T is evaluations to first exact solve or cap if unsolved. Reuse search.jsonl's
arm/map/family/cell/seed, evaluations, solved, curve, seconds and initialization
hashes. Save config/source provenance, validation.json, reproduction.jsonl,
search.jsonl, timing.json, result.json, summary.md and plots under RUN_DIR.
Runner/report extensions will supply the new family aggregation and sensitivities.

P1=log2(T_MG/T_MM), P2=log2(T_GM/T_MM), D=log2(T_GG/T_MM),
I_G=log2(T_GG/T_MG), O_G=log2(T_GG/T_GM), interaction=P1−O_G.
Pooled weighting: equal cells within cell family, equal BE/PA cell-family
weights, equal maps within map family, equal map-family weights. Crossed
bootstrap: 20000 replicates, fixed seed 2331400 (reuse 2331 protocol); maps
resampled within BE/PA, shared whole-seed indices across arms/maps/cells.
Labels N if upper<.25 log2; otherwise P if lower>0 (upper≥.25); X otherwise.
N bounds a conditional increment below the practical threshold, not absence.
Flag upper<0 as antagonism.

Per-cell S_c=mean over maps/seeds log2(T_MG/T_GM)=P1−P2.
C=mean of four BE S_c minus mean of six PA S_c, Welch 95% t interval over cells.
Report BE/PA means, every S_c, Welch df and within-family spread s_w
(pooled within-family sample SD). For deterministic family routing use precedence
B (upper<0), then E (interval strictly inside −.25,+.25), then R (lower>0),
then X. Also report direction and margin containment separately; B/E and R/E
may overlap as properties even though the routed label is unique.

Sensitivity: recompute contrasts/C/outcome after winsorizing T at 65536 and
after dropping triplets where any of GG/MM/MG/GM reaches the cap (the 2331
analysis definition). Preserve within-family equal map weighting, averaging
available seeds within each map/cell, and
shared bootstrap draws; explicitly report missingness/occupancy. Report changed
labels and never substitute sensitivity rows for planned routing. Per-cell,
map-family × cell-family (in-sample/off-family), solve fractions, cap counts,
and optional 13-cell view are descriptive only. The prior three-cell result is
linked rather than pooled inferentially because seeds differ.

These are exploratory effect-size/interval notebook decisions, not new
confirmatory p-value claims. Welch summarizes four vs six screened cells and
these frozen maps, not randomly sampled families or independent map learning.

## Outcomes: first match

| Row | Condition | Meaning for competing explanations |
| --- | --- | --- |
| U | validation fails; <120 complete seeds; any GG cell solves <75%; D lower≤log2(1.25) | Intervention/coverage problem; no mechanism attribution. |
| 1 | P1=P, P2=P, C=B | Both conditional components help; BE is relatively more start-dependent than PA on this bank. No sign flip is established by C alone. |
| 2 | P1=P, P2=P, C=E | Both help; training-bank family difference bounded within ±.25. Does not identify the prior BE cell as cell-specific. |
| 3 | P1=P, P2=P, C=R | Both help; relative balance reversed on this training bank. Does not establish that the prior withheld BE cell was atypical. |
| 4 | P1=P, P2=P, C=X | Both help; family dependence unresolved; report spread and interval widths. |
| 5 | one of P1/P2=N, other=P | One conditional increment is below the practical threshold while the other resolves positive; 2331's pooled pattern does not carry over at this margin. |
| 6 | otherwise | Attribution unresolved, or conditionally redundant at the margin if both N; flag antagonism. |

Per-cell/map-family/descriptive views cannot change the row. Every row closes
question 17 and returns the program to strategy, as approved; the researcher
does not edit belief or question files. Critique notes 1–4 are addressed here.
Notes 5–6 concern steward-owned digest/question language; defer those edits to
the steward, and preserve their qualifications in this experiment's summaries.

Scope: ten reused screened training cells, twenty frozen maps, supplied G4
context, one domain/operator/budget regime. In-sample/off-family composition
is visible. Ongoing use bundles mutation, crossover, inherited latent alleles
and continued program supply. Negative interaction measures sub-additivity on
capped log cost, not a shared causal resource. Initial populations' useful
properties remain unidentified; rare seeded solvers do not select a mechanism.
