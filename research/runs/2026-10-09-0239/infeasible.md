---
reason: runtime_admission_gate
next: strategy
---
The implemented design passes the intervention and replay checks, but fails the
pre-stated conservative runtime admission gate. Stop before the full queue; no queue.yaml
is issued and no full-roster efficacy result exists. This is a narrow budget obstruction,
not evidence that the projections are unreachable or that the full run would time out.

Measured at ten workers on this worktree; raw outputs and arguments are in
[smoke/config.json](smoke/config.json), [smoke/preparation.json](smoke/preparation.json),
[smoke/validation.json](smoke/validation.json), [smoke/timing.json](smoke/timing.json),
[smoke/search.jsonl](smoke/search.jsonl) and [smoke/stderr.log](smoke/stderr.log).
Preparation completed its measurements in **196.74 s (3.28 min)**, then exited nonzero
because admission was false. The deliberate refusal is recorded in validation.json.

Passed checks:

- All 16 source corpora and Q/P projections validated. Q start rows equal C exactly.
- Worst Q per-token marginal error: **0.0000384510**; worst positional total variation:
  **0.0001593589**. P: **0.0000273016**, **0.0001608541**, respectively.
  Limits were 0.001 per token and 0.005 total variation. Every quantized row retains
  at least 250 counts/token, with allele range 24,000.
- Actual positional lookups validated exhaustively across positions/contexts/alleles
  and against a scalar reference on changing-table tapes. Fitting/checking took **49.61 s**.
- **32/32 C/T** historical rows replayed bit-exactly, as did **16/16 K** historical rows
  through 32 positional copies of K. Only clock fields were excluded; repeated-K hashes
  are canonical legacy map hashes. Source and projected table hashes are published.
- Ten targeted tests passed (63.45 s), including complete-roster inference and joint
  control interpretation; compilation and diff whitespace checks passed. Rust unchanged.

Fixed timing sample: one Q and one P search for each of the 16 corpora, rotating across
all 16 target cells, at scientific cap 524,288 / population 256. These are preparation
measurements, not independent estimates of a corpus-weighted efficacy effect.

| Measurement | Q | P |
|---|---:|---:|
| Exact solves / fixed timing searches | 9/16 | 6/16 |
| Mean worker seconds/search | 13.9107 | 17.3116 |
| Mean decode seconds/search | 0.1381 | 0.0727 |
| Mean lookup construction seconds | 0.2248 | 0.0087 |
| Lookup bytes | 19,200,000 | 768,000 |
| Capped timing searches | 7 | 10 |
| Mean worker seconds among capped rows | 24.1065 | 21.2075 |
| Pooled evaluation-rate projection at cap, seconds/search | 23.9027 | 20.9563 |
| 2,048-search average-cost projection at ten workers, minutes | 47.48 | 59.09 |

Pricing uses the larger of pooled evaluation-rate capped cost and measured capped-row
mean for each arm, with one capped scheduling tail. For the exact 4,096-search workload:

- Average-worker-cost projection: **6,394.31 s = 106.57 min**.
- Observed finite-batch wall projection: **7,659.63 s = 127.66 min** (includes idle tails).
- All-capped projection with scheduling tail: **9,304.43 s = 155.07 min**.
- Conservative admission price: `1.15 * max(6394.31, 7659.63, 9304.43)
  + 49.61 fitting/check seconds + 120 reporting seconds`
  = **10,869.70 s = 181.16 min**.
- Approved scoring timeout: **10,800 s = 180 min**. Shortfall: **69.70 s (1.16 min)**.

Thus the 30-minute preparation gate passes and the three-hour scoring admission gate
fails. Observed average/batch forecasts also exceed the proposal's 84–92-minute expected
queue time. They are small-sample forecasts, not a guaranteed whole-roster runtime.
No tolerance, fitting rule, hit-rate assumption, safety factor, sample or arm was changed
in response to these measurements. No top-up, timeout enlargement or performance tuning
was attempted after the failed gate.

What would work instead: the steward can re-propose the **same fixed roster and method
with a 3 h 15 min (11,700 s) scoring timeout**, preserving the admission rule and safety
factor. This gives 830.30 s (13.84 min) beyond the measured conservative price;
30 min preparation + 195 min scoring is **3 h 45 min**, still below strategy's four-hour
summed timeout ceiling. Review the acquisition decision's value against the revised
107–128-minute expected runtime first. A different runtime gate or optimized implementation
would need a new approved plan and preparation; they were not substituted here.

Return to the steward/strategy with the conditional Q/P interpretation from plan.md intact.
The saved small timing sample does not authorize a C/Q or C/P sufficiency verdict.
