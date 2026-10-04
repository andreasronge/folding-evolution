---
node: questions/01-map-bias/08-evolve-bias
title: Family-fitted op frequencies — does a map bias fitted on some tasks help evolution on held-out ones?
---

**Why this now.** The shared-helper line stopped with run 2026-10-04-2135 (07 and 04 parked;
see [decision](../2026-10-04-2135/decision.md)). The root question has two parts, and part 2
("let the map's bias evolve across related tasks and check whether it transfers") has never
been run. Two earlier briefs suggested a plan file for it; none exists, so this proposal is
the smallest first step. It answers one thing before anyone builds a self-adapting map: **is
there anything for map evolution to find?** That is, does a map bias fitted to a task family
help evolution on members it was not fitted on, and is the help specific to the family?

The knob is `op_weights`: the draw distribution over ops for random genomes and mutations
(`ChemTapeConfig.op_probs`). It is the frequency part of the map, the same as letting codon
redundancy in the token→op table change. It already exists, is hash-neutral at default, and
was validated in §15–§19. Decoder rules are not a parameter yet; this proposal does not touch them.

**Prior expectation (stated so the result can surprise us).** Findings item 12 says frequency
changes when a part arrives, not what is reachable. §1 says evolution solves anything with
P(exact) ≳ 5e-5 and is erratic below 1e-6. So I expect fitted weights to raise held-out
P(exact) a lot, and solve rate only where the held-out task sits in the 1e-6 to 5e-5 band.

**What would run.** One queue entry, two stages, TAG arm, L 64, on **one alphabet shared by
both families**. A weight vector is over op ids, so an id must mean the same op in every task.
Several string tasks bind slot 12 to a task-specific op (e.g. `MAP_EQ_R`). If no existing
alphabet runs both families with the same op meanings, replace S with a second intlist
sub-family that uses different ops (e.g. sum-threshold slot tasks against max/AND/OR tasks),
and say so in the plan.
- **Families** (existing tasks; the researcher may swap members to get the P(exact) band
  right, before seeing any stage-2 data):
  - *Intlist family I.* Fit on `mbs_max_gt_5`, `mbs_sum_gt_10`, `mbs_and`; hold out `mbs_or`
    and `mbs_xor`.
  - *String family S.* Fit on `count_r`, `has_upper`, `any_char_is_R`; hold out
    `any_char_is_E` and `any_char_count_gt_1_slot`.
- **Stage 1: fit the weights by random sampling only, no evolution in the loop.**
  - A simple ES or cross-entropy loop over log-weights, scored by mean log P(training-perfect)
    over the fitting tasks on random L 64 tapes drawn with those weights (Rust batch path).
  - Use a smoother score (e.g. P(balanced accuracy ≥ 0.9)) if P(perfect) is too rare to rank
    candidates.
  - Clamp every weight to ≥ 0.05× uniform, so no op becomes unreachable.
  - Three fits: I-fit, S-fit, and a both-fit on I ∪ S fitting tasks (the generic-dilution
    control).
  - Then estimate held-out P(perfect) and P(exact) for uniform and each fit on all four
    held-out tasks, ~50M tapes per cell (§1 ran 61 × 50M in ~2 h on 10 cores).
  - Cap 1.5 h. Report the fitted vectors: which ops moved, and by how much.
- **Stage 2: evolution on the intlist held-out tasks.**
  - 4 arms (uniform / I-fit / S-fit / both-fit) × `mbs_or`, `mbs_xor` × 30 seeds = 240 runs.
  - Pop 1024, lexicase, crossover v2 with the standard selected mate, 1500 generations, seeds
    shared across arms.
  - Readouts: exact solve rate on holdout inputs, and generations to first training-perfect
    and first exact (survival curves).
  - Runs took 88–196 s each in comparable §24 queues, so about 1 h on 10 workers.
  - The string held-out tasks get stage 1 only. If the intlist side shows anything, a
    symmetric stage 2 is a cheap follow-up.
- **Total:** about 2.5 h; one overnight queue.

**What each outcome would mean.**
- **A, fit and transfer.** I-fit beats uniform *and* both-fit on held-out P(exact), and on
  solve rate or time to solve (Fisher / log-rank, n = 30 per arm). S-fit is at or below
  uniform. The map's frequency bias can usefully fit a family. Next: make the weights
  heritable inside evolution under varying family members (the real part-2 test).
- **B, supply, not success.** Held-out P(exact) rises under I-fit, but solve rate and time do
  not move beyond seed noise. This is item 12 at family level. Park the frequency-only version
  of part 2; a decoder-rule version needs its own plan file.
- **C, generic dilution.** I-fit ≈ both-fit > uniform. The gain is "remove useless ops", not a
  family fit. Park, same as B.
- **D, no transfer.** Fitted weights raise P on the fitting tasks only. Park.
- **Sanity check.** If S-fit does not hurt the intlist tasks, the knob is too weak at these
  bounds to say anything; report as inconclusive rather than B.

**Alternatives considered.**
- **02's rarity ladder** (count(restᵈ(X)), fold vs direct). Its reopen condition is half met
  (the shared-helper line has stopped), but it needs an owner wish to settle fixed-target bias.
  It is also part 1 again, and needs ~200M Phase A samples. Offered to the owner as the swap if
  part 2 is not wanted now.
- **B-helper single-copy insertions (reopen 07).** It is the sharpest hypothesis left in the
  shared-helper line, but no natural B-helper child exists to insert, and resolving p near 1%
  needs ≥ 300 insertions. It goes against the stop rule both owner and critic kept. It is in
  07's reopen condition instead.
- **Heritable weights straight away** (each genome carries its own op distribution). That is
  the real part-2 experiment, but if B/C/D hold there is nothing for it to find, and it costs a
  new engine feature. It comes after A, not before.
- **Evolution inside the fitting loop** (score weights by solve rate, not P). It is closer to
  "evolve the map", but costs about 100× more and confounds fit with seed noise at n = 30.

**Budget.** 08 is new with budget 3; the root has 4 left. This is one experiment. 08's stop
rule: if this reads B, C or D cleanly, the frequency-only version of part 2 is parked.
