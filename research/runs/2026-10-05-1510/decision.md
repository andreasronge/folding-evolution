---
decision: continue
node: questions/01-map-bias/08-evolve-bias
next: runs/2026-10-05-1558/proposal.md
---
# Decision: continue 08 with an amended task set

The run never executed. The code passed review on correctness (Rust TAG sampler, exactness
checks, adjusted intervals, verdict table; commit `3803bca`, branch `research/2026-10-05-1510`).
It was blocked because the frozen task set cannot pass its own calibration gate. The reviewer's
uniform probes (95M tapes) found 0 hits for sum>10, sum>15, max>7 and every Σ holdout except
sum>7 (1 hit). Running the queue would have spent one of 08's three experiments to print that
table. No budget was used.

**Continue, not park.** Nothing about the question has been tested, the design survived three
critiques, and the code is ready. Only the task set and two pool sizes need to change. On the
TAG alphabet, thresholds equal to a built-in constant (1, 2, 5) are hit about once per 1M
tapes. So the next run fits on >1 and >5 and holds out >2 in both families, and enlarges the
fit's per-iteration pool so the fit can iterate (review note 1). It should take about an hour.
One-ADD thresholds (max>3, sum>7, …) are scored on the same pools, but only descriptively.

**Why not raise the calibration cap instead.** 3–5G uniform tapes would make only the one-ADD
thresholds eligible (~1e-8). Decisive transfer pools at that rate would need several G tapes
per arm, more than the 8 h queue limit. sum>10 and above might still be out of reach.

**Prior.** In the reviewer's descriptive emulation, mismatched fits also raised P(exact)
(≈ 3–5×), so C (generic gain) is the likeliest reading. If the run reads C or D cleanly, the
stop rule parks the frequency-only version of part 2.

**Parked questions.** None reopens. 02 still needs the owner's wish to settle fixed-target
bias. 07 has no testable B-helper copy and no instrumented replay. 04 depends on 07.

**Process lesson.** Probe uniform hit rates before freezing a sampling task set. The proposal
now asks for this.
