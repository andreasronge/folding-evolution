---
next: proposal
---
# Decision: run 2026-10-05-2039 (11-composition-bank)

**Continue 11.** The cycle produced no data: the driver stopped at `prepare` because merging
`main` (research-loop v2) into `research/main` conflicts on one file,
`research/runs/2026-10-05-1957/code_review.md` (add/add; checked with `git merge-tree`). No
plan, code, queue or `execution.md` exists, so 11's single slot and root 10's four are unspent.

Nothing about the question changed. The feasibility study is still the step root 10 depends
on (strategy: establish a non-aliased, tractable held-out target and measure adaptation cost
before building decoder evolution), and no other open question beats it: root 01's children
are parked with unmet reopen conditions (re-checked: 02, 04, 07, 08, 09 — no new evidence).

The next proposal ([run 2026-10-05-2242](../2026-10-05-2242/proposal.md)) is the same study
with the critic's six notes folded in: a throughput calibration stage 0, an executable split
rule for 7–8-cell banks with per-length alias screens, pooled top-up counts, censored-median
handling, decoder validation against direct `v2_rmin`, a frozen G and G-marg measurement, and
total (not per-queue) experiment-2 cost.

**Owner action needed:** resolve the conflict in `research/runs/2026-10-05-1957/code_review.md`
when merging `main` into `research/main`; otherwise the next cycle blocks at the same step.
Digest: header and open-questions list updated (root 10 added); no belief changed.
