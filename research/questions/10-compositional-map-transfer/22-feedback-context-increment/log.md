# Log

- 2026-10-07 (strategy 2129): opened under root 10 with 1 slot (root 14 → 15). Proposal
  [2129](../../../runs/2026-10-07-2129/proposal.md): evaluate T1 and T2 on the exact 1924
  phase-11/12 seeds where C1 and C2 were already evaluated, giving a four-arm crossing on shared
  seeds.

- 2026-10-07 (2129): slot not used; stopped at preparation as infeasible
  ([infeasible](../../../runs/2026-10-07-2129/infeasible.md), code commit `ec742da` on branch
  `research/2026-10-07-2129`). Critic approved with notes (precision quote was a heuristic, not a
  bound; "mostly contextual" dropped; roster is 16 BE × 4 + 16 PA × 6 cells). The researcher
  implemented the four-arm crossing and a preflight; no T1/T2 search of the primary roster ran
  and no interaction was computed. Preflight: all 128 table hashes and the 16 384 saved C1/C2 row
  keys, seeds and training indices validated; 64/64 C1/C2 replays matched exactly; a fixed T2
  timing block (seed 0 on every own training cell of all 32 lineages, 160 searches) solved
  160/160 at 0.665 worker-s per search on BE and 0.343 on PA (C2 averaged 0.453 over both
  families in 1924). The block reached only 4.33 effective workers (long tail in a
  small block; 1924 reached about 9.7), so the gate projected 29.5 min for the training stage,
  36.9 min with its 1.25 allowance, against 26.5 min left before the 22:20:38 work cutoff set by
  the autonomous deadline. Row 0: no claim about explanations A–C.
  Decision: continue 22 with the same design in a fresh work window (proposal
  [2156](../../../runs/2026-10-07-2156/proposal.md)), because the failure was the calendar, not
  the design: the tables, seeds, replay and code are validated, T2 is fast and solvable, and at
  either measured throughput (4.3 or 9.7 workers) the full training and holdout roster fits in
  well under an hour once the autonomous deadline no longer caps it.
