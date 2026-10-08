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

- 2026-10-07 (2129, wording correction from the 2156 critique's digest check): in the 2129 entry
  above, read "no T1/T2 search of the primary roster ran" as "only the fixed 160-row T2 timing
  block (seed 0 of the primary training roster) was evaluated; the rest of the roster was not
  launched and no four-arm interaction was computed", and "fits in well under an hour" as
  "projects to about 22–53 minutes under the stated holdout-cost assumptions; full-roster
  throughput and T2 holdout cost were unmeasured". (Run 2156 then took 26.4 min.)

- 2026-10-07 (2156, [analysis](../../../runs/2026-10-07-2156/analysis.md), code commit `36c665d`,
  root 10 slot 15 of 15): T1 (1707 token-only fit) and T2 (token-only fit to the 1924 feedback
  corpus) scored on the exact 1924 seeds and training indices where C1 and C2 had been scored;
  32 lineages, 5 120 training and 3 072 holdout searches per arm. All checks passed (128 table
  hashes, 16 384 saved C rows, 64/64 replays, no duplicates); queue 26.4 min of 75, holdout
  admitted by the timing gate. Unsolved 0.3–1.5% in every arm, charged 2 × cap.
  Training (primary): I = (C2/T2)/(C1/T1) = 1.169× [1.093, 1.250], 25/32 lineages above 1, no
  single lineage carries it (leave-one-out lower bounds 1.08–1.11). T2/T1 1.201× [1.150, 1.255],
  so the token-only fit also improved. By family: BE I 1.337× [1.19, 1.50], PA I 1.021× [0.953,
  1.094] (PA T2/T1 1.24× against C2/C1 1.27×). Lower bound stays above 1 under 1× and 4× cap and
  dropping unsolved seeds; the non-registered median-over-seeds variant gives 1.089× [1.008,
  1.177], so part of the mean effect sits in the slow tail. Seed noise accounts for nearly all the
  between-lineage spread in training. Holdout: I = 1.087× [0.984, 1.200] (21/32 above 1), T2/T1
  1.186× [1.107, 1.271], C2/T2 1.365× [1.287, 1.447]; between-lineage variance exceeds seed noise
  about 1.6×; about 46 balanced lineages would put the lower bound above 1 at the observed effect
  (roughly twice that for good power), and no practical n bounds it within ±10%.
  Outcome: training row 1 (feedback raised the advantage of this additionally fitted context
  procedure over this restricted token fit; both fits improved); holdout row 4 (transfer of the
  interaction unresolved — not equality, not absence). Explanation A (contextual increment) is
  supported on training cells, concentrated in BE; B (corpus improves any fit equally) is not
  excluded for PA, whose interval sits inside ±10%; C (I < 1) is excluded on training.
  Decision: close 22 because its pre-registered primary contrast is answered (row 1) and the
  remaining unknown, transfer of the interaction to the withheld cells, needs new lineages
  (about 50–90, with fresh C1/C2 corpora, roughly 1.5–3 h) rather than a rerun of this design;
  root 10 has no slot left, so whether that replication beats the root's other gaps is the
  strategist's call (next: strategy).

## 2026-10-08 — correction (steward, from critique 2243 note 6)

The decision above said the withheld interaction "needs new lineages … rather than a rerun".
That is too strong. 2156's holdout variance is 0.159/0.164 log2² with estimated seed
contributions 0.098/0.103; the remainder (~0.06 per family) gives an approximate
infinite-seed 95% half-width of about 0.09 log2 at 32 lineages, below log2(1.087) ≈ 0.12.
A plug-in projection only, but seed-only resolution is not excluded. Reopen condition and
digest now say: both lineage and seed uncertainty matter; price both extensions before
choosing. Decision unchanged: 22 stays closed because its primary contrast was answered.

## 2026-10-08 — digest condensing (run 2026-10-07-2243): former digest text moved here

The digest was rewritten as current beliefs only (word limit). This is section "Feedback context increment", moved verbatim as it stood before the rewrite; no belief changed. Relative links below are relative to `research/`, not to this folder.

## Feedback context increment (root 10, run 2026-10-07-2156)

One run, commit `36c665d`, complete data (16 384 new T searches, 26 min; 128 table hashes, the
16 384 saved C1/C2 rows and 64/64 replays validated; no duplicates; holdout admitted by a
timing-only gate). T1 = 1707's token-only fit, T2 = the token-only fit to the 1924 feedback
corpus (saved in 1924, never scored); both scored on the exact seeds and training indices where
1924 scored C1 (= 1707's C) and C2. 32 lineages, 5 120 training and 3 072 withheld searches per
arm; unsolved 0.3–1.5% per arm, charged 2 × cap. Interaction I = (C2/T2)/(C1/T1); I > 1 means
feedback raised the contextual fit's advantage. Training families weighted equally (15 df);
withheld cells over 32 lineages (31 df). Pre-registered rows; reviewed analysis. Fairly sure of
the training numbers; this extends 1924's seeds, it is not an independent replication.
([22](questions/10-compositional-map-transfer/22-feedback-context-increment/question.md),
[analysis](runs/2026-10-07-2156/analysis.md))

- **On training cells, feedback raised the fitted context's advantage over the token-only fit
  (BE-carried, partly tail-driven).** I = 1.169× [1.093, 1.250]; 25/32 lineages above 1; no
  single lineage carries it (leave-one-out lower bounds 1.08–1.11); stable under 1× or 4× cap
  and dropping unsolved seeds (lowest 1.131× [1.059, 1.209]). BE 1.337× [1.19, 1.50]; PA 1.021×
  [0.953, 1.094], unresolved and inside ±10%. A median-over-seeds variant (not pre-registered)
  gives 1.089× [1.008, 1.177], so part of the mean effect sits in slow or unsolved seeds.
- **The token-only fit also gained from feedback.** T2/T1 1.201× [1.150, 1.255] on training,
  1.186× [1.107, 1.271] on the withheld cells. Of C2's 1.40× over C1 on training, the token-only
  fit matched about 1.20× and the interaction is the remaining 1.17×. In PA the two gains were
  similar (T2/T1 1.24×, C2/C1 1.27×). The context fit still wins after feedback: C2/T2 1.580×
  [1.520, 1.641] training, 1.365× [1.287, 1.447] withheld.
- **On the withheld cells the interaction is unresolved.** I = 1.087× [0.984, 1.200], 21/32
  lineages above 1. This is neither equality nor absence. Both acquisition-lineage and scoring-seed
  uncertainty matter (between-lineage variance about 1.6× the seed noise); a plug-in projection
  in [critique 2243](runs/2026-10-07-2243/critique.md) does not exclude seed-only resolution,
  and about 46 new balanced lineages would put the lower bound above 1 at the observed effect
  (about twice that for good power). Price seed and lineage extensions before choosing.
- **C1/T1 reproduced on 1924's seeds.** 1.352× [1.274, 1.434] against 1707's independent-seed
  1.365×.
- **Not shown:** what the extra contextual advantage is made of (yield, diversity, tape content
  and the fitting rule stay bundled in "feedback"); why it is BE-specific in this sample (one BE
  withheld cell, family not separated from shape or difficulty); anything about token maps in
  general (T is 24 global multipliers over G4's fixed context, fitted by likelihood); a second
  feedback step.

