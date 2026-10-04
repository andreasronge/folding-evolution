---
status: closed
tags: [shared-helper, establishment, crossover, crossover-dose, majority-rule, tagged-runs]
budget: {experiments: 3, used: 0}
---
# Can a rare hand-built shared form establish against partly shared or duplicated forms, and how does crossover rate set the barrier?

Current summary: No, not once crossover v2 is at 0.3 or more. From 1/32 or 1/10 with
crossover 0.7 the shared form is lost in 294/300 runs (§30); the barrier is graded against
duplicated (from 1/10: 29, 30, 24, 3, 0 of 30 wins at crossover 0, 0.1, 0.3, 0.5, 0.7) and
steep against partly shared (0.3 stops it) (§31 D). Whichever form holds the majority wins
(270/270 at ≥ 3/4 shared, §31 E); without crossover each copy establishes independently at
about 3% vs duplicated and 1% vs partly shared (§30, §31 F).

Competing explanations:
- A: Crossover converts or kills the rare form from both sides: as recipient it takes
  self-contained bodies (children stay exact, stop being shared), as donor its RECV consumers
  land in hosts with no helper run (Fable's enumeration, §30). Supported.
- B: The shared form is intrinsically less fit (more fragile). Not supported: with crossover
  off it often wins, and from a majority it always wins.
- C: The barrier is the missing helper in the host, not crossover as such. Open; tested in
  [05-latent-helper](../05-latent-helper/question.md).

Related: [01-map-bias](../question.md),
[04-random-start-discovery](../04-random-start-discovery/question.md) (the same crossover is
what solves), [05-latent-helper](../05-latent-helper/question.md),
[notebook §29–§31](../../../../docs/map-bias/notebook.md),
[Plans/establishment-s30.md](../../../../Plans/establishment-s30.md),
[Plans/s31-dose-reciprocal-stage4.md](../../../../Plans/s31-dose-reciprocal-stage4.md),
report `experiments/output/2026-10-03/s31/report/s31_report.md` (not in this checkout)

Note: closed for the hand-built contest only. §31 points out that D measures a contest
between two unrelated layouts, not the fate of a new mutant arising inside a population;
that case belongs to 04. A crossover schedule (on early, off later) is untested.
