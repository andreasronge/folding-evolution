---
node: questions/10-compositional-map-transfer/12-generic-grammar-headroom
title: Assembly-family bank — exhaustive 9-token alias screen over a frozen design space, 10-token search calibration, gated family-grammar diagnostic (root 10, experiment 2 of 5)
---
## Why this now

The [strategy](strategy.md) sends root 10 through 12 with the
[assembly-family plan](../../plans/compositional-family-headroom.md): two families, same
primitives, addition in different structural positions, then measure headroom against the
frozen G and whether a family grammar can use the contrast. I follow it, but **read-only probes
I ran this cycle show that the plan's candidate pair fails the alias screen**. So this
proposal widens the screen to a small frozen design space. It also runs the search
calibration that any 10-token redesign needs, and gates the family-grammar diagnostic on a
pair surviving. The most likely outcome is row 1 (no pair survives). If so, the strategist
gets the specific semantic obstacle plus measured 10-token search costs, as the plan asks
("record whether semantics, tractability, headroom, context capacity or outer-loop cost
failed"). It does not get a third unmeasured redesign.

## Probes (this cycle; `research/main` @ `0995d33` built in /tmp; one run each; unreviewed)

The exhaustive screen reused `composition_bank.SemanticMachine` (all 18 executable tokens, no
syntactic pruning, exact typed-state dedup). I extended it one level as "output-only" (depth 8
stored, depth 9 children evaluated, not stored). The ≥ 80% rule is 2247's: a cell fails if
some shorter program agrees with it on ≥ 80% of inputs.

| Probe | Result |
|---|---|
| Screen cost, 625 inputs | depth 7: 1.6M states, 2 s, 0.7 GB; depth 8: 12.2M states, 19 s, 5.3 GB; depth 9 (output-only): 92 s, 7.3 GB. Same ±5% on 1 331 and 2 401 inputs. |
| **Gate** `(A+B)>0 ? C : D` (18 cells, 10 tokens) | All 18 fail at ≤ 7 tokens: 80–90% agreement with the old bank's `S>0 ? C : D`, because sign(A+B) ≈ sign(S). Same on the two wider domains. |
| **Branch-then** `S>0 ? (X+Y) : Z` (9 cells) | 625: 0/9 survive ≤ 9 tokens. 6 exact aliases come from identities: with Z ∈ {X,Y}, `Z + (S>0 ? X : 0)` uses the executor's zero default; with S as a branch value, DUP reuses the condition. The rest are 0.84–0.94 near-aliases (`M ≈ 2` given S>0, a constant substitution). On 1 331 inputs still 0/9: 0.82–0.88 via `(X+Y)>0 ? (X+Y) : Z`. |
| **Branch-else** `S>0 ? Z : (X+Y)` (9 cells) | 2/9 survive on every domain probed (`S?m:(S+M)`, `S?M:(S+m)`). |
| **Post** `(S>0 ? X : Y) + Z` (18 cells) | 625: 4/18 survive (best 0.67–0.74). 1 331 and 2 401 inputs: 8/18 (the 8 with X ≠ S). |
| Linear, DUP position `2(X+Y)+Z` vs `2X+Y+Z` (18 + 18) | 3 + 3 survive (distinct reducers only; 0.59). |
| Search, 12 ten-token cells (post + branch, 625 inputs; P 256, cap 524 288, 6–8 seeds per cell × arm, 528 runs) | G median 7–34k on every cell (all above 4 096). U: 11/12 cells solved in ≥ 4/6, `S?M:(S+m)` 1/8. F: 11/12 cells ≥ 5/6, `S?M:(S+m)` 2/8. G-marg ≥ 5/6 everywhere. Mean 4.0 s per run including capped runs (10 workers, 12 cores). Capped U runs take 9–14 s. |

What follows from the probes: (i) with ADD and IF_GT over {S, M, m} there are exactly four
tree shapes. Gate and branch-then are dead from identities and sign correlation, not from the
domain, so the plan's pair cannot be rescued by a wider input range. (ii) Post-addition is the
one rich shape. (iii) Ten-token cells do leave room against G: its medians are 2–8× the 4 096
line. 10-token search is tractable under F/G-marg but uneven under U. Measured with 6–8 seeds,
so these are estimates, not results.

## What would be run

**Stage A — exhaustive alias screen over a frozen design space (≈ 10 min, 8 GB).**
The researcher builds the depth-8 + output-only-depth-9 extension of the existing screen and
tests it against brute force to depth 4, as in 2247. It also parametrises the domain.
- Domains: D625 (length 4, {-2..2}), D1331 (length 3, {-5..5}), D2401 (length 4, {-3..3}).
- Candidate families, all with conditions S, M and m, written out with canonical programs:
  the four ADD/IF_GT shapes (gate, branch-then, branch-else, post) and the two DUP-position
  linear shapes.
- A cell is **retained** on a domain if (a) its canonical program, NOP-padded to 32, reproduces
  it exactly on the Rust executor, (b) no program of ≤ 9 tokens agrees on ≥ 80% of inputs, and
  (c) no other candidate has the same label vector.
- Both cutoffs are 2247's and are frozen now.

**Pair rule (frozen).** An eligible pair is two shapes whose canonical programs have the same
token multiset, on the same domain. Each shape needs ≥ 4 retained cells, and each must have a
holdout pair: 2 retained cells such that every reducer-in-role in them also occurs in ≥ 1 of
the remaining retained cells of that shape. Among eligible pairs, the most total retained cells
wins; ties go to the smaller domain, then the lower shape names.
Holdouts within a shape are the lexicographically first valid pair of cell ids. They are fixed
before any search and are outcome-blind.

**Stage B — 10-token search calibration (always runs; ≈ 35–60 min on 8 workers).**
- Cells: every cell retained on the stage-B domain. That is the selected pair's domain, or
  else the domain with the most retained post cells, ties to the smaller domain (probe: D1331, 10 post/branch-else cells plus any linear survivors, so 10–16 cells).
- Arms: U, F, G and G-marg, the frozen 2247 tables. Hashes are checked; nothing is retuned.
- Runs: 50 paired seeds per cell × arm, P 256, cap 524 288, lexicase on 64 cases with the exact
  check on the full domain. Same paired-seed scheme as 2247, on fresh seeds.
- Top-up: 100 more seeds wherever F is 30–39/50.
- Sampling: 10⁸ decoded genotypes per arm. Cells with no hits get a 95% upper bound. Sampling
  is cut first if the deadline is near.
- Size: 10–16 cells × 4 × 50 ≈ 2 000–3 200 runs × ~4 s (probe mean) ≈ 2.2–3.6 CPU-h. Capped U runs on the
  hard cells may double this.

**Stage C — family-grammar diagnostic (only if a pair is eligible; ≈ 30 min).**
- Two hand-set grammars, fixed now from the family rules. Each is G with only the rows after
  ADD and after IF_GT replaced; the 500 floor and R = 23 000 are kept.
  - The family whose ADD feeds a later operand: ADD row → INPUT 12 000; IF_GT row → DUP 12 000
    (terminal-safe).
  - The family whose IF_GT feeds a later operand: IF_GT row → INPUT 6 000 + ADD 6 000 (both
    routes); ADD row → DUP 12 000.
  - For a linear pair, the same rule applies to the rows after reducers and after ADD (DUP
    after the reducer vs after ADD).
- Arms: each grammar and its measured tied marginals (the 2247 G-marg procedure), on every cell
  of both shapes, 50 paired seeds. One grammar is matched to a cell's shape, the other swapped.
- These are diagnostic priors, not learned maps. They test whether the previous-token decoder
  class can carry this family contrast at all.

**Stage D — projected cost of the transfer experiment (computed, not run).**
- Reference design: 6 contextual and 6 token-only adaptation trajectories per training shape
  (24 in total). Matched and mismatched transfer reuse the same trajectories.
- Outer loop: population 16, 30 generations. Inner searches use k seeds per training cell at
  budget B ∈ {32k, 65k, 131k}.
- k = max(2, ⌈(2·SD_B)² / n_train⌉), where SD_B is the pooled within-cell SD of
  log₂ min(T, B) under the start decoder.
- Transfer test: every learned map + its tied marginals + U, F, G and G-marg, on 4 holdouts ×
  50 fresh seeds.
- Reported for two start decoders, U and G, from measured seconds per run at each B (censored
  runs included), in CPU-hours and in wall-hours on 8 workers.
- Probe-based guess: G-start ≈ 3–4 h wall, U-start ≈ 25 h wall.

**Queue:** one entry, timeout 2 h 30 min, internal deadline 2 h 10 min. Stages A → B → C, with
balanced seed blocks of 10 so a deadline leaves usable partial data.

## Outcome rules (first match decides)

| # | Condition | Meaning / next step |
|---|---|---|
| U | Stage A incomplete on any domain, or stage B < 50 seeds on any cell × arm, or stage C (when triggered) incomplete | Unresolved; re-plan the missing part. |
| 1 | No eligible pair on any domain (stage A) | **Semantic failure of same-primitive assembly families on v2_rmin over {S, M, m}** at canonical length ≤ 10. Close 12 and return to strategy with: the retained-cell table per shape × domain, the alias witnesses, and stage B's 10-token headroom/tractability/cost. A fix needs an alphabet change, such as a fourth weakly correlated reducer or a comparison that is not sign-aligned with S. That is a program-level choice. *Probes predict this row.* |
| 2 | Eligible pair, but the contrast is not usable. Usable means: in **both** shapes, the geometric mean over the shape's cells of the paired median ratio swapped/matched is ≥ 1.5, with a 95% paired-bootstrap lower bound > 1. | Context-capacity failure: a previous-token decoder cannot exploit this contrast. Return to strategy. |
| 3 | Usable contrast, but no room above G. Either matched does not beat G (geometric-mean G/matched lower bound ≤ 1 in both shapes), or F, G or G-marg has median < 4 096 on ≥ 2 of the 4 holdouts. | The best family-adapted rows add nothing over the frozen G here. Return to strategy. |
| 4 | Rows 2–3 pass, but the projected transfer study is > 16 h wall at G-start, or no B gives G ≥ 50% solves on every training cell | Feasible but costly. Return to strategy with the staged cost. |
| 5 | Rows 2–3 pass and the projection is ≤ 16 h | **Go:** freeze the pair, split, grammars and controls. The next proposal is the adaptation-and-transfer study on fresh seeds. |

Every row reports, per cell × arm: solves, Kaplan–Meier median with a 95% bootstrap interval
(> 524 288 if under 50%), mean seconds per run including censored runs, shortcuts, and the
sampling rate or its bound. It also reports the G/U, F/U and G/G-marg paired ratios. Rows 1–4
are limits of this design on this alphabet, not a negative answer to root 10.

## Alternatives considered

- **Run the plan's gate/branch pair as written.** Rejected. The probe shows all 18 gate cells
  and all 9 branch-then cells alias at ≤ 9 tokens on three domains, so the run would end at
  stage A while measuring less than this design.
- **Return to strategy now, without a run.** This is the honest alternative and the probes
  nearly justify it. But the strategist would get unreviewed one-seed numbers. It also would
  not get measured 10-token search costs (the plan's stated unknown: "deeper-task and
  outer-loop costs are still unknown"), nor a complete screen of the six shapes. Those are the
  inputs any alphabet-level redesign needs. If the critic judges the probe sufficient, I accept
  sending this straight to strategy.
- **Relax the 80% rule to keep branch-then.** Rejected: the failing near-aliases are constant
  substitutions (`M ≈ 2` given S>0) and sign correlations. Moving the cutoff after seeing data
  is what the strategy forbids.
- **Add a fourth reducer now.** It needs Rust and executor changes, and the semantics are
  unprobed. That is the strategist's call, informed by row 1's table.
- **Root 01 parked questions** (02, 04, 07, 08, 09): none meets its reopen condition (re-checked
  against the digest). The strategy keeps them parked.

**Budget:** root 10 has 5 experiments, 1 used (run 2247), so 4 left. This uses 12's single
slot. Probe scripts are in `/tmp/rmprobe/probe/` (not committed; numbers above are from them).
