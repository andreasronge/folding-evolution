# Log — 18 compact context learning

- 2026-10-07 (0803): opened from strategy 0803 (root 10 budget 10 → 12; this question gets
  slots 11 and 12). Steward probe on 1723's `search.jsonl` / `generations.jsonl` (read-only):
  per-search log2 cost sd 1.67 at the 65 536 cap, 0.66 s per search; child-minus-parent
  noise variance 0.14–0.25 for a 24-search difference (shared seeds barely help); token-step
  true-effect variance 0.075–0.086 (generations 1–5) and 0.025–0.037 (6–25); reliability
  0.10–0.29; mean step effect +0.02 to +0.09 log2 (slightly harmful). Rank-one capacity: 55% /
  64% of the BE / PA hand-set context and 93% of their contrast. Proposal: run 2026-10-07-0803
  (calibration gate, then 16 paired continuations from saved 1723 maps).

- 2026-10-07 (0821): 0803 returned `revise` by the critic. Blocking: the σ²_T gate could stop
  on low variance although small or uniform effects can still accumulate. Steward probe (read-only,
  1723 `search.jsonl`): at the 65 536 cap the token learner's searches solved 88% (BE) / 93% (PA),
  84–99.5% by cell; in-loop best-of-16 score fell only about 0.2 log2 over generations 15–25
  (selection-biased), so a ~3 800-search continuation may barely move token-only maps. Decision:
  propose run 0821 without a gate: stage A calibrates both operators (8 start × row-direction
  units, independent per-mutant seeds) and picks n ∈ {24, 48}; stage B runs 16 equal-budget
  pairs; outcome rows split "token arm still learned" from "neither arm moved", because only
  the first makes a C/T null informative about context.

- 2026-10-07 (0821): run 2026-10-07-0821 (commit `f61aec4`, complete, 2.64 h of a 3.8 h
  deadline, 174 964 searches, all validation passed, no holdout touched; slot 11 of root 10, 1 of
  2 here). Stage A: single b-steps from b = 0 have repeatable effects (σ²_T 0.047 [0.027, 0.065];
  token 0.028 [0.005, 0.051]); the lowest-quarter-by-Δ_A mutants beat the average mutant on
  independent seeds (context −0.116 [−0.182, −0.060] log2) but only reach parent level (Δ_B
  −0.017 [−0.085, +0.041]); mean step harmful (μ +0.06 context, +0.03 token). Effort rule chose
  n = 24 (20 generations; 17% of bootstrap replicates would have chosen 48). Stage B: 16 pairs
  (8 BE, 8 PA) from saved 1723 maps, 4 040 searches per arm. Fresh training (50 seeds per cell,
  524k cap): **C/T 0.955× [0.833, 1.095]** (pair sd 0.38 log2, planned 0.29; 7/16 pairs > 1);
  T/S 1.03× [0.90, 1.16]; C/S 0.98× [0.90, 1.07]; C/C0 0.96× [0.90, 1.02] (PA alone 0.91×
  [0.85, 0.98], descriptive); in-loop slopes ±0.003 log2/generation in both arms, intervals
  spanning 0. Parents were replaced 1.4 times per generation with no net movement; survival into
  the parent set was 0.22–0.27 for every operator. Learned residuals were unrelated to the
  hand-set BE − PA contrast (|cos| ≤ 0.105). Outcome row 3: C/T upper < 1.15 and T/S lower ≤ 1
  (C/S lower ≤ 1 too). Steward note: T/S's upper bound allows about 5.4 × 10⁻⁵ log2 per search,
  and 0811's token continuation gained about 4.0 × 10⁻⁵ per search (0.54 log2 over 13 440, other
  bank and start), so "too shallow" is not excluded by this run. Neither is the reviewer's
  reading that per-child noise (0.33 log2 at n = 24) swamps true step effects (sd 0.17–0.22).
  ([analysis](../../../runs/2026-10-07-0821/analysis.md))
  Decision: park 18 (1 of 2 slots used) and return root 10 to strategy, because row 3 was
  pre-registered as "no increment, and too little learning to tell ineffective context from
  insufficient depth or selection signal". A further run is only informative if the token arm
  can first be shown to learn from these saved maps (T/S resolved > 1), which needs a different
  loop (more searches per child or a much longer continuation, ~5–6 h). That is a choice between
  this and other uses of root 10's last slot, so it goes to the strategist.
