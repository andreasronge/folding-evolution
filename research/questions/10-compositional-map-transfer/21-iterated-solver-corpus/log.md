# Log — 21 iterated solver corpus

- 2026-10-07 (1924): opened from strategy 1924 (root 10 raised 13 → 14; this is slot 14).
  Steward probe in a scratch worktree of `research/main` (`627336d`; read-only;
  [script](../../../runs/2026-10-07-1924/steward_probe.py)): for 1707 lineages BE1, BE2, PA1 and PA2,
  48 collection searches per own training cell under the saved C (seeds 19 240 000+), refitted
  with the frozen 1707 `fit` (C2), then C2 against C on 16 fresh seeds per cell (19 340 000+,
  shared). Yield under C was 47/48–48/48 per cell (BE 190/192 twice, PA 288/288 twice). 190–288
  distinct tapes. Collection took 120–158 worker-s per lineage, 12–32 s wall. Mean body-row entropy
  was G4 4.19, C 3.91, C2 3.78–3.81 bits. C2 − C was −0.34 (se 0.29), −0.83 (0.27), −0.29 (0.27)
  and −0.43 (0.21) log2. Proposal: run 2026-10-07-1924.

- 2026-10-07 (1924): slot 14 of 14 (root 10's only slot for 21). Run 2026-10-07-1924
  ([analysis](../../../runs/2026-10-07-1924/analysis.md), commit `5565d54`, complete, 72.9 min,
  39 976 searches, all validation passed, 1707 replay bit-identical, stage D admitted at full size
  by timing alone). Each of the 32 saved 1707 tables C collected 48 searches per own training cell
  (7 623/7 680 solved, worst cell 44/48) and was refitted with the frozen rule (C2); a fresh G4
  corpus (7 378/7 680) gave the one-shot control C'. Training, 32 shared seeds per cell: C2/C
  **1.404× [1.347, 1.464]** (32/32 lineages; BE 1.56×, PA 1.27×), C2/C' 1.408× [1.342, 1.478]
  (32/32), C'/C 0.997× [0.940, 1.058]. Withheld cells: C2/C **1.289× [1.204, 1.381]** (28/32),
  C2/C' 1.330× [1.263, 1.401] (31/32), C'/C 0.969× [0.908, 1.035]. C2 is sharper than C in every
  lineage (body-row entropy 3.91 → 3.80 bits, previous-token MI 0.41 → 0.48); C' matches C on
  both. Collection under C cost 0.63 worker-s per search against 2.17 under G4 and gave slightly
  more distinct tapes. One PA training cell, `(S?M:F)+m`, showed no gain on its own (0.98×,
  descriptive). Row 1, holdout transfer on both contrasts (source-attributed useful feedback by
  the plan's definition).
  Decision: close 21 as answered at this scope and return root 10 to the strategist (`next:
  strategy`), because the pre-stated row 1 and both holdout contrasts are met with margin over 32
  independent lineages, the fresh-control replication C'/C is within about ±6%, and the
  remaining unknowns (a second step, which part of the procedure — yield, diversity or what C
  finds — carries the gain, mechanism) are different experiments that need a new allocation;
  root 10 has used 14 of 14 slots.

- 2026-10-07 (2129, wording correction from the 2129 critique's digest check): in the 1924 entry
  above, read "C' matches C on both" as "C' has similar mean entropy and mutual information to C
  (3.905 against 3.907 bits; 0.409 against 0.407; no equivalence test)", and "showed no gain on its
  own (0.98×, descriptive)" as "no gain was resolved (0.98× [0.84, 1.13], descriptive)". The
  speed gain is attributed to the collection procedure; whether it is contextual is question
  [22](../22-feedback-context-increment/question.md). No reopen: 22 is the allocation for the T2
  comparison named in this question's reopen condition.
  Decision: keep 21 closed because its answered scope is unchanged; only the wording was too strong.
