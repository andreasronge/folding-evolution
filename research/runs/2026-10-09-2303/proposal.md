---
node: questions/10-compositional-map-transfer/37-cheap-bias-fresh-transfer
title: Frozen A8 versus full F, S8 and G4 on a fresh two-sum bank
bank: two-sum-v1
---
**Question.** The question comes from [strategy 2303](strategy.md) and its [plan](../../plans/cheap-bias-fresh-transfer.md).
On then-addition, cost(full F)/cost(A8) was 1.031× [0.951, 1.117]
([2033](../2026-10-09-2033/analysis.md)). That bank is development data. Does A8 keep this
parity on fresh targets, or did eight attempts, half collected under its own bias, buy a
narrower bias?

**Departure from the strategy (measured).** On `(A+B)>C ? D : E`, research/main's ≤9-token
screen keeps only **4 of 124** behaviours: 28 have exact short identities and 92 are
near-aliases. Of the preflight's 64 candidates, 60 fail. The mirror `A>(B+C)` adds only
near-duplicates (0.92–0.93 agreement). The plan forbids relaxing the screen or the domain
([probe](semantic-probe.json),
[log](../../questions/10-compositional-map-transfer/37-cheap-bias-fresh-transfer/log.md)).

I therefore propose **one** replacement, fixed before any search: **two-sum
`A>B ? C+D : E+F`**. It has 16 tokens, the same primitives and the same domain. **76** of its
289 distinct behaviours pass the screen and agree on under 80% of inputs with every
comparison-gate and then-addition behaviour. The boundary tested is a longer
composition, not addition in the predicate. If this bank fails its gates, the run
returns to strategy and no other shape is tried. The critic may prefer returning now instead.

**Closest technique.** Model-building GP whose fitted program distribution transfers to a
changed target ([PIPE](https://pubmed.ncbi.nlm.nih.gov/10021756/);
[Ardeh et al. 2020](https://gpbib.cs.ucl.ac.uk/gp-html/Ardeh_2020_CEC.html)), plus
[DreamCoder](https://arxiv.org/abs/2006.08381)-style library reuse.
The map adapts by **external fitting** and is then frozen. This is a **fresh-bank replication
and boundary test** of the acquisition choice.

**Bank, frozen with the method before any search.**
1. Take all-four-reducer assignments with canonical sum order and no constant gates.
   Validate canonical outputs in Python and Rust, then deduplicate.
2. Apply the existing screen. Exclude behaviours with ≥ 80% agreement to any of the 306
   old-roster behaviours.
3. Order the remainder by SHA-256 of `"two-sum-v1:"+id`. Pick greedily, at most 4 per gate
   pair, with pairwise agreement < 80%, until there are 16 **confirmation** cells.
4. The next 4 cells that pass the same agreement check are **timing-only**.

Dry run: 16 + 4. Minimality is unproved.

**Arms.** All are hash-checked; nothing is refit on the new targets.
- **A8** and **S8**: 2033's 64 builds each (16 corpora × 4 blocks).
- **Full F**: 1036's 16 C+F builds.
- **G4**: no fit.

Operator, cap and P are unchanged; historical acquisition costs are charged.

**Unit and roster.** The unit is the corpus (n = 16, 15 df). Each corpus runs 16 cells × 8
seeds, 2 per block. A8, S8 and full F each run 2 048 searches on shared keys and cases. G4
runs 16 seeds per cell (256 searches).

**Feasibility.** Measured worker-seconds per search on then-addition: A8 5.76, S8 6.0,
full F 4.54, G4 8.54. A capped search costs about 28.5 s, on about 9.6 workers. So the roster
takes about 62 min at then-addition difficulty, and plausibly 2–3× that on 16-token targets.

Stage 0 times all arms on the 4 timing cells (about 112 searches). The first rule that fits
applies:
- 8 seeds if the projection × 1.15 is ≤ 150 min;
- else 4 seeds;
- else 4 seeds without S8;
- else stop and report a cost obstacle.

The corpus log-SD was 0.15 in 2033. Assuming 0.20 here gives a half-width factor of about
1.11 (about 1.14 at 4 seeds), so a true ρ ≤ 1.05 should resolve against 1.20.

**Full cost.** Researcher ≤ 120 min (bank builder, bank interface in
`sparse_feedback_run.py`, replay gates). Queue timeouts are 45 min for
prepare/stage 0 plus 3 h for scoring, 3.75 h in total; about 1.2–2.5 h is expected. Critic,
review, analysis and decision take about 2 h. Total about 6–7 h, ending before 08:12.

**Primary comparison.** ρ = cost(A8)/cost(full F), where > 1 means A8 is slower. It uses
2033's estimator: log capped cost, unsolved = 2 × cap, blocks weighted equally, paired keys.
- **UB < 1.20**, A8 faster than G4 (lower bound > 1, G4 cell means fixed), and full F
  solving ≥ 25%: **A8 retains useful performance on a fresh bank.** Carry A8 forward.
- **LB > 1.20: material loss.** Full acquisition earns its cost beyond development data.
- **LB > 1, UB ≥ 1.20:** a resolved loss of unknown size.
- **Otherwise unresolved.** Report the resolution price.

**Reported, no rule.**
- σ = cost(S8)/cost(A8) against 2033's 1.126. A resolved σ < 1 would suggest adaptive
  specialisation.
- Full F/G4 and solve rates.
- Per-cell and per-family results.
- A + N·S in evaluations and in this bank's worker-seconds.

**Expectations.** G4 solves 35–50%, and A8 and full F 70–85%. ρ ≈ 1.0–1.1, so "retains" has
about a 60% chance. The fitted arms beat G4 2–3×, because the branch sums are library syntax.
**Surprises:** ρ > 1.2, σ < 1, or fitted arms no better than G4.

**Next action.** Build and pin `two-sum-v1`, stage 0, score, analyse, return to strategy.
