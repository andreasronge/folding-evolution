# Decision: run 2026-10-08-1246

**Close [24](../../questions/10-compositional-map-transfer/24-comparison-gate-bank/question.md);
open [25](../../questions/10-compositional-map-transfer/25-comparison-gate-transfer/question.md)
and propose its frozen stage 2 ([run 1534 proposal](../2026-10-08-1534/proposal.md)).**

Why:
- 24 is answered. The comparison-gate bank gives a role-covered split with 4 training and 4
  protected holdouts per family. G4 still has headroom (68% solved at 524k). On the training cells,
  corpus context beat token fitting 3.11× [2.78, 3.48] over 16 corpora, with collection yield
  58.9%. The pre-stated rule (lower bound > 1 and yield ≥ 40%) routes to stage 2 with a wide margin
  ([analysis](analysis.md)). The run was complete and clean: 5 376 searches, 0 holdout searches,
  and the stage-2 roster frozen.
- The result is a training-cell fitting result, not transfer. The question the program cares
  about is whether the advantage survives new compositions, and the eight frozen holdouts are the
  cheapest test of that anywhere in the tree. The tables, seeds and endpoint already exist, and
  1246's report prices the scoring at about 66 min of queue at training difficulty (3 h timeout).
  Changing the design now would forfeit the freeze, so the proposal runs it unchanged.
- Root 10 has used 16 of 16 slots. Strategy 1246 also asked for a review before transfer is
  funded. The proposal therefore goes to the strategist for allocation. I recommend one slot,
  because no other open line has a comparably cheap test of a consequential belief.
- No new decision is needed for the run-wide scope: the autonomous run has about 40 h left and has
  used 3 of 40 experiments.

Other upkeep this cycle:
- I applied the critic's digest-check notes 7–9 (root 23 wording). "No useful gain established"
  is now tied to the registered 1.5× threshold. Linkage on sum is unresolved, not absent. "Max5
  tied" means nearly equal observed costs, not established equality. These changes are in root
  23's question.md, the digest, and a correction entry appended to its log.
- I re-checked the parked questions (01/02, 04, 07, 08, 09; root 23). None of their reopen
  conditions is met by this run: it adds evidence only about root 10's externally fitted context.
