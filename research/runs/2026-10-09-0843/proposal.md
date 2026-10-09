---
node: questions/10-compositional-map-transfer/32-learned-fragment-operator
title: Learned executable fragments as block edits on top of C (training cells), revised
bank: comparison-gate-v1
---
**Revision of [0826](../2026-10-09-0826/proposal.md)** answering its [critique](../2026-10-09-0826/critique.md).
Unresolved controls now mean "unresolved", with a price; added admission rule, edge cases and
precision scenario. Strategy: [0826](../2026-10-09-0826/strategy.md).

**Question and mechanism.** Do short executable fragments, learned from the G4 solver corpora C
was fitted to, speed fresh search beyond C when inserted as one-step block edits? Does their
joint content matter beyond block editing? A previous-token table cannot propose a multi-token
computation in one edit.

**Closest known technique.** Run-transferable libraries ([Keijzer, Ryan & Cattolico 2004](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf));
ARL ([Rosca & Ballard 1995](https://cdn.aaai.org/Symposia/Fall/1995/FS-95-01/FS95-01-011.pdf));
[DreamCoder](https://arxiv.org/abs/2006.08381). The library adapts by **external fitting**.
New: a controlled stack-tape mechanism test against a strong fitted decoder; not evolutionary
acquisition.

**Library (frozen).** Knockout-active (NOP, 96 inputs) contiguous 3–6-token windows from 1246's
G4 solvers that recur in ≥ 2 source cells. Leave one cell out: scoring cell c draws only on the
corpus's other 3 cells. Rank by source cells, then count, then length, then lexicographic order,
and keep 32. Drop fragments that solve any of the corpus's 4 cells when NOP-padded. Libraries
under 32 are used as is. A library under 8 stops prepare as a feasibility result, with the
roster kept.

**Measured** ([probe](steward_probe/loo_probe.py)): 138–307 leave-one-out windows (median 208).
No top-32 fragment solves a cell. The top 32 are ~75% 3-token (mean span ≈ 3.3). Report each
fragment's stack effect, underflow, wrong-type/default use and provenance. Knockout activity
shows contribution in the source program only.

**Arms.** C's table and the [search](../2026-10-09-0537/execution.md) are unchanged (P 256,
lexicase, 524k cap). Each non-elite child gets one block with probability r = 0.2. That is a
child fraction; realized tokens changed are reported. F/B/W share the length law (the library's
lengths) and a uniform start in [0, 32−L]. The window and the next position are re-encoded under
C, and the decoded suffix is kept.
- **C**: no operator. **F**: an intact fragment, drawn uniformly.
- **B**: the library's per-position token distribution for length L.
- **W**: C's own chain, given the preceding token.

A separate operator RNG keeps the other draws (not parents after divergence). Prepare asserts, on 10k edits per arm, that tokens outside the window (including the tape end)
are unchanged. It also replays 1246 C rows bit-exactly with the operator off.

Unit: corpus (n = 16, 8 BE/8 PA) × 4 training cells × **32 seeds**, or 2 048 searches per arm.
**Why 32:** random pseudo-arm splits of 1246's C rows give a null corpus SD of 0.27 at 16 seeds
(95% half-width ×1.155) and 0.19 at 32 (×1.107). At 16 seeds, a 1.15× gain would be unresolvable.

**Feasibility and admission.** C solves 91% of these searches, at 5.47 s per search (capped: 28.9 s).
With C-like solving and 1.2× overhead, the queue is ~90 min on 10 workers. If every block run
capped, it would take ~6 h. The smoke runs 4 arms × 4 cells × 8 non-scoring seeds, with
diagnostics. Projected queue = Σ 2 048 × measured s × 1.15 / 10. Use the largest of {32, 24, 16}
seeds that fits in ≤ 3.5 h, the same for all arms. If none fits, report the smoke to strategy.
Plan.md lists expected solves per arm. Cost: prepare ≤ 45 min, queue ≤ 3.5 h, agents ~2.5 h.
Total ≈ 5.5–7 h.

**Primary comparison.** X/Y = exp(mean over corpora of log cost_Y − log cost_X). Unsolved runs
cost 2 × cap; 95% t interval, 15 df. Rules are applied in order:
1. **Earns review of reuse**: F/C ≥ 1.15 with lower bound > 1, and F/B and F/W lower bounds > 1.
2. **Ends this extractor/operator**: F/C upper bound < 1.10, a practical judgment.
3. **Block editing suffices**: F/C lower bound > 1 and F/W upper bound < 1.10. End the library.
   Report W/C to strategy as a cheaper candidate; nothing follows automatically.
4. **Joint content unresolved**: F/C lower bound > 1, and F/W or F/B spans 1.0–1.10. This is not
   evidence for either explanation. Price the run needed for a ×1.07 half-width; reuse is not earned.
5. **Otherwise unresolved**: same pricing.

Descriptive: 1 × cap, both-solved, BE/PA, W/C, B/C, tokens changed, offspring underflow/default
use, library share in solvers, time per evaluation. Prepare also prices the reuse stage: whole-corpus libraries, F and C, holdouts plus
then-addition (~2–2.5 h queue).

**Scope.** A three-way win supports this procedure beyond these controls, not modularity or an
explanation of C; development banks only.

**Expectation.** F beats B. F against W and C is doubtful: the blocks are mostly 3-token blocks
that C may already produce cheaply (root 01: joins, not modules). Guess: F/C 1.0–1.15, so rule 2
or 3. Surprising: F/C ≥ 1.3 with F/W resolved, or F/C < 0.9.

**Next action.** Rule 1 leads to strategy with the reuse price. Rules 2/3 close 32. Rules 4/5:
strategy with the price. No sweeps.
