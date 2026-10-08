# Log: 25-comparison-gate-transfer

- 2026-10-08 (steward, after run 1246): opened for the frozen stage 2 of the comparison-gated
  transfer plan, because 24's pre-stated rule routed to it (training C/T lower bound 2.78 > 1,
  yield 58.9% ≥ 40%). Root 10 has used 16 of 16 slots, so the proposal (run 1534) needs an
  allocation from the strategist. Decision: propose the frozen roster unchanged (16 corpora ×
  C/T × 8 holdouts × 16 seeds, G4 32 per holdout), because changing it after seeing training
  results would forfeit the freeze.

- 2026-10-08 (run 1548 row D, charged to 26; [analysis](../../../runs/2026-10-08-1548/analysis.md)): the frozen roster ran unchanged (4 352 searches, identical row for row to 1246's `schedule.json`, 52 min). C/T 2.60× [2.31, 2.92] on the eight protected holdouts, 16/16 corpora, 121/128 corpus × holdouts, all 8 holdouts LB > 1; solves C 93.9%, T 84.8%, G4 76.6%. Matched over mismatched family 1.10× [0.89, 1.35], unresolved; own-family holdout over training 0.88× [0.72, 1.07], unresolved. Development bank: within-shape generalization, not fresh-bank transfer. Decision: close 25 as answered (A supported, B ruled out on these holdouts, F not resolved), because its frozen test ran in full and the 1534 critique's fresh-bank requirement was met by row F of the same run.
