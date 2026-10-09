---
next: strategy
---
# Decision: run 2026-10-09-0843 — keep question 32 open, return to strategy

**Result.** On C's unchanged search over the comparison-gate training cells (16 corpora × 4 cells
× 32 paired seeds, complete roster, all checks passed, commit `e347793`), one-step block edits
with intact learned fragments (F) beat C 1.57× [1.42, 1.75], the library-marginal control B 1.60×
[1.45, 1.77] and the C-chain block control W 1.23× [1.12, 1.36]. Pre-registered rule 1 fired:
`earns_review_of_reuse`. W alone beat C 1.28× [1.17, 1.39]; B/C 0.98× [0.93, 1.04]. My guess
(F/C 1.0–1.15) was wrong.

**Decision: continue question 32 through strategy (`next: strategy`), no proposal written.**
Because:
1. The approved rule 1 routes to a strategy review of reuse, and strategy 0826 asked to come back
   after the training result. Nothing follows automatically.
2. Root 10 has used all 23 slots; any next experiment needs an allocation.
3. The result raises a second question that competes with reuse. A library-free block edit
   sampled from C's own chain beats C's point mutation by 1.28×. That gain matters for the
   acquisition half of the core question, because it needs no library. The strategist should
   weigh it against reuse.

Question 32 stays open: training cells are answered, but excluded compositions are the real
test, because the leave-one-out libraries are mostly shared 3-token syntax. The digest gains two
beliefs, scoped to training cells of a development bank. No parked question's reopen
condition is met. Root 23 needs a changed inheritance rule with a measured selectable signal,
and root 01's 02/04/07/08/09 conditions concern helper and threshold lines that this run does
not touch. The 0843 critique's Digest check listed no problems.

**What I would propose next, for the strategist to weigh** (planning prices from plan.md and
the measured rates; holdouts may be harder than training):

| Candidate | What it decides | Price |
|---|---|---|
| **A. Reuse stage (recommended first).** Whole-corpus frozen libraries; F, W, C on the 8 protected comparison-gate holdouts and the 16 then-addition cells; same operator, rate and seeds law; primary F/C and F/W. | Whether learned fragments help beyond C *and* beyond chain blocks on compositions the library never saw, including a new shape. A win would make fragments a candidate acquisition target; a collapse to F≈W would say the gain is block editing, not content. | F + C 3 072 searches each ≈ 71 queue min; W adds ≈ 35 min; ≈ 4.5 h with agents. Size seeds from the observed corpus SD (0.17–0.19 at 32 seeds/cell). |
| B. Why block edits beat C's point mutation. Add a point-mutation arm with suffix repair (C's resample, but repair the next allele so the decoded suffix is kept) beside W and C on training cells. | Separates suffix preservation from chain-sampled content in W/C. | ≈ 1 slot, about 3–4 h; reuses this harness. |
| C. Evolutionary acquisition of fragments (e.g. fragments harvested from the population during the run). | The acquisition gap the strategy names. | Unpriced; needs a design and a build stage. |

I recommend A first because the scope limit (shared syntax, training cells) is the largest
uncertainty in the new belief, the stage is already priced and validated, and its F/W contrast
also partly bears on B. Carry W as a standing comparator in any follow-up: it is a cheap,
library-free 1.28× over C.

Autonomous run 2026-10-08-0812: 10/40 experiments, deadline 2026-10-10T08:12, about 21 h left.
