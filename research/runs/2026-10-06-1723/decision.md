---
next: proposal
---
# Decision: run 2026-10-06-1723 (16, crossed BE/PA token learning, stage 1)

**Continue 16 with stage 2: score the 20 frozen maps and G4 on the three holdouts. No new
trajectories.** The proposal is [runs/2026-10-06-2229/proposal.md](../2026-10-06-2229/proposal.md).

## Why

- **Row 4 routes to stage 2, and the size rule fixed before the run gives n = 10.** Both
  families learn: own-family gain over G4 is BE 2.18× [1.98, 2.40] and PA 2.27× [1.95, 2.65],
  20/20 maps above 1. Both in-sample crossed contrasts are X: 1.13× [0.93, 1.37] and 1.10×
  [0.93, 1.29]. s_off = 0.355 log2 (BE cells 0.447), so n = 10 already meets the 0.50 log2
  half-width target. The rule said not to add trajectories, so slot 8 goes to the holdout
  evaluation that the plan reserved for slot 9.
- **Only the withheld cells can tell the remaining explanations apart.** D (no learning) is out
  for this learner and budget. C (damage) does not apply on the training cells, because each
  family's maps speed the other family's cells by 1.9–2.1×. A (family-dependent transfer) and
  B (generic) both fit the training data. In-sample, a preference of about 1.1× could just be
  the maps fitting their own cells.
- **The holdout scoring is cheap and already designed.** It is 25 200 full-cap searches, about
  50 min. The maps are saved and hashed.
- **What stage 2 can resolve.** My read-only check of the stage-1 fresh rows: at 50 seeds about
  half of the per-cell between-map variance is seed noise. The seed-noise sd is 0.15–0.33 log2
  and the remaining between-map sd is 0–0.46. So 400 seeds per holdout buys real precision on
  the single BE cell, and more seeds beyond that buy little. At n = 10 the BE direction resolves
  only effects of about 1.3–1.4× or more, and the PA direction about 1.2×. The in-sample
  preference is about 1.1×, so the most likely outcome is an unresolved crossed contrast with
  clear generic transfer. The proposal says what that means before any holdout is scored, as
  the analysis asked.
- **Why not more trajectories instead.** Resolving a true 1.1× per direction needs about 35–40
  trajectories per family (≈ 11 h more learning). The frozen rule rejects that. It would also
  be a data-dependent rescue, which strategy 1723 rules out.

## Tree changes

- 16: log entry for the run, and the summary and explanations updated after stage 1. Reopen
  condition revised: its old trigger, a learner with gains on both training sets, is now met.
- Root 10: summary, sub-question list and log updated (7 of 9 slots used). The log entry also
  corrects the 1603 wording flagged in critique 1723's digest check (notes 5–7).
- 15: question.md reworded for the same notes; a correction line added to its log. It stays
  closed. The one-cell BE holdout it named in its reopen condition runs in 16 instead.
- Digest: new section "Crossed family learning". In "Four-reducer bank", the heading and text
  that read context as the location of the preference, the unresolved PA gain as absence, and a
  projected learner cost as a measurement are all fixed.
- Parked questions re-checked: 02, 04, 07, 08 and 09. None of their reopen conditions is met.
  This run measured search speed under learned token maps only. It added no sampling-lift data
  (09a), no new threshold family (08) and nothing on shared helpers (02, 04, 07).

## After stage 2

Return to strategy whatever the outcome, as the plan and strategy 1723 require before funding
context, a new bank or a mechanism study. Slot 9 stays unspent until then.
