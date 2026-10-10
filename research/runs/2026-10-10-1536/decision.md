---
next: strategy
---
# Decision — run 2026-10-10-1536 (question 40)

**Close [40](../../questions/10-compositional-map-transfer/40-independent-input-protected-transfer/question.md)
and return to strategy.** No proposal is written: root 10 has used 32 of 32 slots, no open question
remains under it, and [strategy 1536](strategy.md) asked for a review after this comparison.

**Result.** Code review passed; critic approve_with_notes (notes 1–5 handled in plan and code). Data
complete: 768 source and 896 scoring rows, none missing, duplicated or substituted; no build replaced;
protected cells never searched before this run; everything hash-frozen before the first protected search.
- *Primary:* cost(G4)/cost(A8″) **10.08× [7.60, 13.15]** (failures at 2 × cap), **6.37× [5.02, 8.03]**
  at 1 × cap. The lower bound clears the pre-set 1.5× under both charges → label **useful protected-cell
  replication on x4-double-gate-v1, relative to G4 at this cap**, not penalty-sensitive. Magnitude is
  censoring-inflated: 321/384 G4 searches capped.
- *Solved:* A8″ 317/384, G4 63/384, O 58/128. A8″ cheaper in all 8 cells; all 24 builds above 1.5× at
  2 × cap (23/24 at 1 × cap, build 16 at 1.5).
- *Descriptive:* unseen-pairing cells 6.8× [4.9, 9.2] vs seen 12.8× [9.0, 17.8]; O/A8″ 4.3× [2.7, 6.6];
  sparse discovery again (first batch 64/384; 8/24 empty intermediate libraries) degraded some builds but
  defeated none; repayment about 40 searches per build in evaluations.
([analysis](analysis.md))

**Why close.** The pre-set rule fired by a wide margin; more builds or seeds cannot change the label.
What remains open is a different question each: family specificity, what the artifacts carry, a stronger
baseline, a fresh bank.

**What changed in belief.** The digest gains one belief (now confirmed, not a probe): on one family with
addition inside the predicate, independently rebuilt A8 artifacts were 6–10× cheaper in capped cost than
G4 on its protected cells. This extends the recipe's demonstrated scope beyond output-addition families,
at within-bank, single-family, weak-baseline scope. The unseen-pairing result says the gain is not limited
to the exact predicate pairings sources contain (three cells, descriptive).

**What it does not settle.** Family specificity (O's token reinterpretation confounds O/A8″); context vs
fragments vs supply; predicate placement alone (alphabet and domain changed too); fresh-bank transfer;
a competitive baseline; inheritance.

**Suggestion for strategy (not a proposal).** The core question asks whether bias can be adapted *to a
task family*; every specificity test so far was unresolved near 1.0–1.1× (16, 20, 25), always between two
closely related output-addition families. This family gives A8 effects four times larger than the old
banks, and the O arm hints at something family- or alphabet-specific but cannot separate the two. The most
belief-changing next step is a **same-alphabet crossed-family test on `v2_x4`**: a second family with
addition in the output (e.g. `Xa>Xb ? Xc : Xd+Xe`), A8 built on each family's sources, both scored on
both families' protected cells, primary matched/mismatched cost ratio. It needs a stage-0 probe first:
the output-addition family on `v2_x4` is unscreened (≥ 12 separated cells, distinct from the double-gate
cells, G4 headroom). Rough price from 0311/1536 rates: probe about 1.5 h total; the crossed stage about
twice 1536's queue (~2 h, likely split) plus agent time, 5–7 h. Cheaper but less new: component attribution
(C-only vs C+F vs a token fit) with the 24 frozen builds on the eight spare, still unscored cells of this
bank. Root 23 stays below these: no changed inheritance rule has a measured selectable signal.

**Parked questions re-checked.** None met: root 23 (needs a selectable inherited signal; this was
external fitting), root 01's parked children 02/04/07/08/09 (no relevant new evidence), 39 (the protected
comparison did not need a different split), 38 (no decision depends on the PA deficit).

**Tree edits this cycle.**
- 40: log entry; closed; tag `fresh-transfer` → `protected-replication` (critique note 7); summary, scope,
  Related, Reopen if.
- 39: question.md censoring sentence corrected (critique note 6); correction appended to its log.
- Root 10: summary sentence (the probe line replaced by the confirmed result), slot line 32/32, sub-question
  entry, Related, log entry, and a condensing entry holding the digest text moved out.
- Digest: header, root 10 header (32 of 32), sub-question line, new cheap-acquisition bullet, Overall/Not
  shown; the 27/28 bullets condensed to one paragraph (old text in root 10's log) to stay near 3000 words.
