---
next: strategy
---
# Decision: run 2026-10-07-0315 (question 17, slot 2)

**Close [17](../../questions/10-compositional-map-transfer/17-decoder-initialization-variation/question.md)
and return the program to strategy.** No proposal is written: both roots have spent their budgets
(root 10 now 10 of 10, root 01 6 of 6), and no sub-question is open.

**Result.** Row 1, clean: 122 000 searches complete, every validation gate passed (786 historical
rows bit-identical, generation-0 tapes paired on all 80 000 MG/GM rows), GG solved 91–100% per
cell. On the ten training cells:
- Ongoing decoder given M's start (P1) 1.28× [1.22, 1.34]; start given ongoing M (P2) 1.33×
  [1.26, 1.40]; diagonal 2.44× [2.23, 2.66]; interaction −0.52 log2 [−0.62, −0.42]. The pooled
  2331 pattern (both help, sub-additive) replicates on a different set of cells.
- Family balance C = mean S(BE) − mean S(PA) = −0.45 log2, Welch 95% [−0.68, −0.22] over 4 vs 6
  cells. All four BE cells have S resolved below 0; no PA cell is resolved below 0. Leave-one-cell-
  out and both cap sensitivities keep label B; 20/20 maps agree in direction.
- The difference is relative: both components are resolved positive within each family.
- Post hoc: S correlates with MM difficulty across cells (r 0.77). At matched difficulty the
  families still separate, but four and six screened cells cannot separate family from
  composition shape or difficulty tail.

**Why close.** Both slots are spent, and the question is answered at this design's resolution.
The learned map works through both channels on all 13 cells tested, about 1.3× each given the
other, with heavy overlap. On the training bank the balance between the two differs by cell
group. What remains is *why*: which property of the starting population carries the gain, how
mutation, crossover and inherited alleles divide the ongoing effect, and whether family, shape or
difficulty drives the balance. Answering that needs new cells or a finer intervention, not
another run of this design. Each of those is a new question with its own budget, and that budget
can only come from the strategist.

**Why strategy rather than a new sub-question.** Root 10 has no slots left. Its primary question
(A versus B in its question.md) now has a generic-transfer answer: about 2–3× on withheld cells,
with no resolved family advantage (95% upper bounds 1.25× BE, 1.15× PA). It also has a mechanism
answer from 17, and learned context showed no resolved gain. Whether that warrants a further
mechanism slot, a wrap-up into `docs/map-bias/findings.md`, or a new root is a program-level
call. Candidates the strategist may weigh, none of which I am proposing:
(a) a census of generation-0 partial programs under M versus G, a cheap read-only analysis of
existing tapes that might name what the start supplies;
(b) mutation-only versus crossover-only search under M, to split "ongoing";
(c) cells that vary shape and difficulty independently, to test whether the balance follows
family. (c) needs new screening, because branch-else had no role-covered holdout pair on this
bank (15).

**Tree changes.**
- 17: closed (2 of 2). Log entry added. Summary, competing explanations, Related and Reopen if
  updated. Critique 0315 digest-check notes 5–6 are fixed: "the start effect is about useful
  partial programs, not seeded solvers" now reads "direct solver seeding is unlikely to explain
  the gain; which properties carry it is unresolved". A wording-correction note is appended to
  the log rather than editing the 2331 entry.
- Root 10: summary, 17's entry, Related and log updated. 10 of 10 slots used. Status left open
  for the strategist.
- Digest: header and opening paragraph updated. The "Starting programs versus ongoing decoder"
  section now covers both runs. Note 5 is fixed: the sentence "part of what the start supplies
  is what the decoder supplies" became "sub-additive on capped log cost, consistent with but not
  establishing a shared supply". Note 6 is fixed: the heading "not about seeded solvers" became
  "direct solver seeding is unlikely to explain the start gain". The open-question list is
  updated, and 16's "no detected family advantage" now gives its upper bounds.
- Parked questions re-checked: 02, 04, 07, 08 and 09. None of their reopen conditions is met.
  - 08's "decoder-rule version of part 2 with its own plan" is root 10 itself. It was already
    accounted for when root 10 opened.
  - 09(b) asks for a heritable-bias design that needs the INPUT/GT supply answer. None is
    pending. This result bears on supply versus dynamics only for the frozen G4-based maps.
