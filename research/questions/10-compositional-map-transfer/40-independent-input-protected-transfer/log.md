# Log: 40 independent-input protected transfer

2026-10-10 (steward, run 2026-10-10-0311): opened after 39's stage-1 pilot (G4/A8 12.2× [6.7, 20.7] on
four development cells; G4 7/64, A8 55/64, O 22/64 solved; between-build log-SD 0.79). Stage 2 design
suggested to strategy as [proposal](../../../runs/2026-10-10-1536/proposal.md) (the driver may rename it
`steward_proposal.md`): 24 fresh A8 builds, 8 protected cells, 48 shared seeds per cell for G4 and A8,
O descriptive, primary G4/A8 against a 1.5× margin.

Decision: open and send to strategy because root 10 has no budget left and strategy 0311 asked for a
review after stage 1; the design is priced from measured stage-1 rates.

2026-10-10 (steward, run 2026-10-10-1536): **stage 2 ran** (slot 32; strategy 1536 raised root 10's budget
31 → 32 for this test). Commit `7244fa1`, code review pass, critic approve_with_notes;
[analysis](../../../runs/2026-10-10-1536/analysis.md), [execution](../../../runs/2026-10-10-1536/execution.md).
24 fresh A8″ builds (768 source searches) and 896 scoring searches on the 8 protected cells, which
had never been searched before; method, builds, seeds and roster hash-frozen before the first protected
search. Data complete: no missing, duplicated or substituted rows; no build replaced; no error rows.

- **Primary** (geometric capped cost, failures at 2 × cap; build-resampled bootstrap with a shared G4
  seed draw): cost(G4)/cost(A8″) **10.08× [7.60, 13.15]**; at 1 × cap 6.37× [5.02, 8.03]. Lower bound
  above the pre-set 1.5× under both charges, so the label is not penalty-sensitive; the magnitude is,
  because 321/384 G4 searches hit the cap. A capped-cost ratio against a weak supplied prior, not a
  time-to-solution ratio.
- **Solved** (descriptive Wilson; searches sharing a build are not independent): G4 63/384 (16% [13, 20]),
  A8″ 317/384 (83% [78, 86]), O 58/128 (45% [37, 54]). Same-seed pairs: A8″ cheaper 307, G4 cheaper 23,
  both capped 54. A8″ cheaper in all 8 cells (per-cell 6.3–20.6×).
- **Unseen predicate pairing** {02|13} (3 cells, descriptive): G4/A8″ 6.76× [4.94, 9.24] against 12.81×
  [8.99, 17.76] on the 5 seen-pairing cells; A8″ solved 115/144 there. The three smallest per-cell ratios
  are these cells; G4 also solves them slightly more often, so part of the gap is the baseline.
- **Builds.** First-batch yield 64/384 (17%), median 2/16 per build (discovery-obstacle reading again,
  non-gating); 8/24 builds had an empty intermediate library and ran their adaptive batch on context
  alone; 6 ended with 1–2 source cells unsolved. Every build beat pooled G4 by > 1.5× at 2 × cap (range
  1.9–33.6×, median 11.3); at 1 × cap 23/24 did and build 16 sat at 1.5. Build log-cost SD 0.62 (pilot 0.79).
  Empty-intermediate builds costlier on average (119 k vs 64 k geometric), Spearman of yield vs cost
  −0.44, with three low-yield builds at the pooled level: descriptive, not a causal yield relation.
- **O** (8 reinterpreted old-family A8′ builds, descriptive): G4/O 2.34× [1.64, 3.48], O/A8″ 4.30×
  [2.68, 6.61]. Token reinterpretation prevents a family-specificity reading.
- **Economics** (arithmetic evaluations, failures at cap): acquisition 12.5 M per build; saving 313 k per
  search; repays G4 after about 40 protected searches (per build 26–144). No wall-time claim.

Against expectations: every stated expectation met (R 4–10×, at the top; A8″ solving most; G4 < 20%;
unseen cells helped but less; O between). The named surprise (unseen-pairing cells no better than G4)
did not occur. Development pilot 12.2× [6.7, 20.7] on 4 cells; this run is slightly smaller and consistent.

Scope: one family, alphabet `v2_x4`, D625; the 8 protected cells of development bank `x4-double-gate-v1`
(a within-bank confirmation, not fresh-bank transfer); relative to the fixed G4 prior at the 524k cap;
context, fragments and token supply bundled; alphabet, domain and predicate placement changed together
relative to the output-addition banks; external fitting, not inheritance.

Decision: close 40 because the pre-set rule fired with a wide margin (lower bound 7.6× at 2 × cap, 5.0× at
1 × cap, against 1.5×), so the question is answered at this scope: the unchanged A8 recipe, rebuilt
independently from this family's sparse sources, gives fresh search a large capped-cost advantage over G4
on its protected cells. More builds or seeds would not change that label; what remains open (family
specificity, what the artifacts carry, a stronger baseline, a fresh bank) needs a different experiment.
Strategy 1536 asked for a return to strategy after this comparison, so `next: strategy`.
([decision](../../../runs/2026-10-10-1536/decision.md))
