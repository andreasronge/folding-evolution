---
next: proposal
---
# Decision 2026-10-10-2214: continue 43 with a corrected initializer

**Outcome.** The approved comparison (frozen native A8 versus family-blind subtree GP on the DG and TS
development rosters) stopped before any search ([infeasible](infeasible.md)). The plan read the
proposal's unstated "depth 2–4" as edges. Uniform choice over 3 functions and 9 terminals (5 of them
two-token readouts) cannot fill a full-depth-4 tree within 32 compiled tokens: 0/10 000 draws accepted,
exact acceptance 1.2 × 10⁻⁷ per draw, about 3.4 worker-hours of initialization per search. The tree
representation itself passed validation (16 canonicals and 1 998 random trees agree across an
independent interpreter, Python VM and Rust VM; overflow, conditional order, size reversion and provenance
checks). No A8 or tree search ran, so there is no evidence about the question and no budget slot was used
(43: 1 left; root 10: 35 budgeted, 34 used).

**Decision: continue 43 (re-propose), not strategy**, because:

- The obstacle is a depth convention, not a validity, precision or cost obstacle in the comparison. Both
  roster targets are inside depth 3 edges (TS 2, DG 3), so depth 1–3 edges (2–4 levels, the
  DEAP/Koza-style range) covers the target sizes without bias toward them.
- A read-only check on commit `3e961ad` today: with depth 1–3 edges, a P256 population takes 274 draws
  (2 ms); full depth 3 accepts 72%, all other bins ≥ 99.5%.
- The same check showed a second weakness of the frozen initializer: grow chose a terminal at the root
  with probability 0.5, so about a quarter of the initial population would be single terminals (grow
  median 2 tokens). Koza's grow draws the root from the function set. The retry adopts that (grow depth
  3 median 12 tokens, 99.5% accepted). This addresses critic 2214 note 5's concern about a weak baseline
  before any target is seen; mutation subtrees stay as frozen.
- Strategy 2214 asked for an early exit on obstacles that change the price. This one does not: the code
  exists, the timing and admission gates are unchanged and still to be met, and a strategy review would
  re-approve the same purchase.
- If the corrected initializer fails a gate, or Stage 0 shows a broken search path, 43 parks with the
  measured obstacle and the loop returns to strategy. No third design attempt.

**Tree updates.** 43 log and question (status line, links, reopen rule); root 10 log, question summary
and budget line; digest "as of" line and root-10 heading. No belief changed: the infeasible run produced
no A8/tree evidence. Parked questions: no reopen condition is met by a result with no searches.

**Digest check (critique 2214 notes 6–9) fixed.** Digest, root question and 42 now say "no TS library
difference resolved (1.01× [0.83, 1.25]; a loss above 1.25× excluded, equality not shown)" instead of
"interchangeable / free on TS". In 42, "sub-additively" and "as large as" became point-estimate language.
Correction entries were appended to the 42 and root logs, covering the "within 1.01×" scope (actual span
about 1.09×) and "must acquire both / no native-table dependence" (should read: both merit retaining in
this procedure; the D library's usefulness is not restricted to its native table). Earlier log entries
are left as written, since logs are append-only.

**Next:** [proposal 2239](../2026-10-10-2239/proposal.md).
