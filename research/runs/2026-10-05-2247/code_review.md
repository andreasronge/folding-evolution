---
verdict: pass
---
# Code review (second pass): composition bank, decoder harness and headroom feasibility

Reviewed `25f199d..0995d33` (revision `4beb9e3..0995d33` in detail), proposal.md,
plan.md, queue.yaml and critique.md. The first pass failed on two gates; both
are now addressed and I found no new wiring bug. No blocking issues.

Reviewer checks used reviewer-only seeds (pilot 99000000–99000049, top-ups
99100000–99100099, disjoint from stage 0/B/C). Scratch files are in
`/tmp/rev2247`; nothing was written to the repo.

## Blocking issues

None.

## How the first-pass issues were resolved

1. **Tractability cap at 524 288 (was blocking).** The researcher took the
   offered alternative: the cap stays, plan.md justifies it (experiment 2's
   inner budgets stop at 131 072; a larger cap answers a different question),
   and `result.json` and `summary.md` now report headroom and F/G holdout
   medians for every structurally eligible transversal whatever row fires.
   Row 2's text now says "at 524288 evaluations; larger caps are untested".
   Checked on the pilot: the outcome is still row 2, and the summary shows all
   four structural transversals lacking headroom under G, which is the
   information the first pass said would be masked.
2. **Inner-budget gate without a borderline rule (was blocking).** Stage C now
   adds 100 U seeds for any potential training cell with 20–30/50 solves at
   any of 32k/65k/131k, pooled threshold 75/150, coalesced with the
   tractability top-up. `costs()` refuses a budget with a missing top-up and
   `decision()` then routes to unresolved. Tests cover 74/150 vs 75/150,
   the missing top-up, and coalescing (12 passed).

## Gate checks on the revised code

- **Stage C on the pilot, run for real.** The pilot triggers 6 requests
  (F headroom on SM-ADD and Sm-ADD, G headroom on Sm-SEL and Mm-SEL, U inner
  budget on Sm-DADD at 32k and Mm-SEL at 131k). The 600 top-up runs took
  95 s on 8 workers, against the 1 800 s ceiling. Over 200 resamples of the
  pilot seeds the request count is 5.8 on average and 8 at most, so the
  ceiling does not bind and an "unfinished top-up" outcome is not expected.
- **Outcome after pooling:** row 2, no further requests. Sm-SEL under U stays
  at 26/50 (in the 30–39 band in 28 of 200 resamples, as before).
- **Pooled values:** Sm-DADD U 82/150 at 32k; Mm-SEL U 77/150 at 131k (126/150
  at the cap); Mm-SEL G median 4 096 (interval 3 072–5 376); Sm-SEL G median
  5 120 (4 352–6 656). All four structural transversals lack headroom under G
  after top-up (two G holdout medians below 4 096 in each).
- **Queue.** One entry, 10 800 s, internal deadline 9 600 s with a 300 s
  reserve. Expected wall time is about 25 minutes; the time is spent on the
  approved sizes, not truncated by any gate.
- **Critique.** Notes 1–4 remain answered in plan.md; 5–6 need no change.

## Minor notes

- Mm-SEL under U at 131 072 is 77/150 pooled, two above the threshold. If the
  real run ever reaches rows 4a/4/5, the analysis should call the inner
  budget borderline and quote the interval; the pooled rule has no second
  band by design. On the pilot those rows are not reached.
- A U cell topped up only for an inner-budget reason is then also judged for
  tractability on the pooled 105/150 rather than its original 35/50. This is
  more data for the same rule and I consider it harmless, but the analysis
  should state which cells were pooled and why (`topup_plan.json` has it).
- The likely result is row 2 with every structural transversal lacking
  headroom under G. The analysis should report both and not read row 2 as
  "targets unreachable" (26/50 at 524k became 36/50 at 2M in the first-pass
  cap check).
- Sm-SEL under G moved from "median interval contains 4 096" at 50 seeds to
  5 120 (4 352–6 656) at 150. The headroom verdict did not change because the
  other two holdouts are well below 4 096.
- Remaining first-pass minor notes (stage 0 mean time overstates stage B,
  decoder validation compares two Rust paths, queue under 30 minutes) still
  apply and do not affect results.
