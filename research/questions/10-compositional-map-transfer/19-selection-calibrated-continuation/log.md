# Log — 19 selection-calibrated continuation

- 2026-10-07 (1137): opened from strategy 1137 (root 10 budget 12 → 13; this question gets
  slots 12 and 13). Steward probe on 0821's `search.jsonl` (read-only): learn searches 0.471 s
  per worker (65k cap), fresh 0.867 s (524k cap); shared-seed child-minus-parent per-search
  difference variance 3.95 log2² (single-candidate 2.54, seed correlation ≈ 0.22) → noise sd
  0.41 at 24 searches, 0.20 at 96; true between-start sd of fresh S cost ≈ 0.04 log2 (BE) and
  ≈ 0.25 (PA). Proposal: run 2026-10-07-1137 (T at 96 searches per candidate from the 0821
  starts, scored on 0821's fresh seeds; a C arm at the same loop only if T passes a pre-stated
  gate, scored on a new fresh block that also confirms T/S).

- 2026-10-07 (1137): run 2026-10-07-1137 (commit `86ef669`, complete, 4.63 h of a 5.75 h
  timeout, 335 700 searches, all validation passed, 4 000/4 000 S rows bit-identical to 0821,
  no holdout touched; slot 12 of root 10, 1 of 2 here). 16 saved 1723 starts (8 BE, 8 PA), 2 + 6
  loop, 96 searches per candidate, 12 generations, 9 600 searches per trajectory. Stage 1 (T,
  token only), scored on 0821's fresh block F1: **T/S 1.143× [1.089, 1.200]**, 16/16 starts
  improved (gate ≥ 1.10 passed; start-and-seed bootstrap 82% ≥ 1.10). T_mid/S 1.081× [1.017,
  1.149], T/T_mid 1.058× [0.990, 1.130] (no resolved flattening); T96/T24 1.114× [0.987, 1.257]
  (procedure comparison, unresolved); in-loop slope −0.013 [−0.021, −0.005] log2/generation,
  14/16 negative. Stage 2 (C, token or rank-one context step, ½ each, same in-loop seeds), all 16
  admitted, scored on new block F2: **T/S(F2) 1.122× [1.031, 1.222]**; **C/T 0.967× [0.871,
  1.073]** (BE 1.04× [0.86, 1.25], PA 0.90× [0.79, 1.03], descriptive); C/S 1.084× [0.993, 1.184];
  C/C0 1.037× [0.972, 1.107]; C0/T 0.932× [0.860, 1.010] (not pre-stated: C made half as many
  token proposals as T). Per-start T/S on F1 and F2 correlate only 0.15 (implied true
  between-start sd ≈ 0.07 log2), so only pooled means are informative; winner's curse at
  acceptance −0.14 to −0.16 log2. Residuals had small absolute cosine with the hand-set
  BE − PA direction (≤ 0.045). Outcome row 6 (gate passed, T/S(F2) lower > 1, C/T upper < 1.15);
  sensitivity variants keep it (T/S(F2) lower 1.031–1.047, C/T upper 1.010–1.076), though the
  F2 lower bound sits close to row 5. ([analysis](../../../runs/2026-10-07-1137/analysis.md))
  Decision: close 19 (1 of 2 slots used) and close 18 at its tested scope, because the question
  is answered: with 96 searches per candidate, token continuation from these saved maps does
  learn (about 1.12–1.14× on two seed blocks), and in that loop rank-one context under equal
  search funding added no resolved increment, with a gain above about 1.07× excluded. The
  remaining alternatives (context added on top of a full token budget, context learned jointly
  from G4, more depth) are different experiments that do not fit cleanly in root 10's last slot
  before the 22:25 deadline, so root 10 goes back to the strategist.
