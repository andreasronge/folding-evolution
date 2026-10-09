---
node: questions/10-compositional-map-transfer/32-learned-fragment-operator
title: Learned executable fragments as block edits on top of C (training cells)
bank: comparison-gate-v1
---
**Question and mechanism.** Following [strategy 0826](strategy.md) and the
[fragment plan](../../plans/learned-executable-fragments.md): does inserting short
executable fragments, learned from the same G4 solver corpora C was fitted to, make fresh
search faster than C itself, and does their joint content matter rather than block editing
as such? A previous-token table cannot propose a multi-token computation as one edit; a
fragment insertion can.

**Closest known technique.** Run-transferable libraries ([Keijzer, Ryan & Cattolico,
GECCO 2004](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/bibs/3103/31030531.htm);
[Ryan et al., GPTP 2004](https://gpbib.cs.ucl.ac.uk/gp-html/ryan_2004_GPTP.html)) carry
modules learned in some runs into later runs. ARL ([Rosca & Ballard](https://gpbib.cs.ucl.ac.uk/gp-html/rosca_1995_tadbb.html))
finds subroutines within a run. [DreamCoder](https://arxiv.org/abs/2006.08381) learns
abstractions with a neural guide. Here the library adapts by **external fitting**. New:
literal stack-tape blocks as same-length overwrites under a learned context decoder (no new
opcodes), tested against a strong learned benchmark (C), with controls separating joint
content from block-edit volume. A mechanism test of a known idea.

**Library (frozen before scoring).** For each of the 16 1246 corpora (8 BE, 8 PA), take G4
exact solvers and mark tokens knockout-active (NOP substitution changes output on a fixed
96-input sample). Candidates are contiguous tape windows of length 3–6 in which every token
is active and which recur in ≥ 2 source cells. **Leave one cell out:** the library used when
scoring cell c comes only from the corpus's other 3 cells. This removes memorized pieces of
c's own solutions; C keeps its in-sample fit, so this is conservative for F. Rank by source
cells, then cell-weighted count, then length; keep 32. Exclude fragments that solve a bank
cell when NOP-padded. Report each fragment's stack effect (depth change, underflow) and any
short library. [Probe](steward_probe/fragment_probe.py): median 20/32 active tokens per
solver; 255–386 recurring all-active windows per corpus. Leave-one-out counts are unmeasured;
prepare reports them.

**Arms.** All arms use C's table and the unchanged search
([composition_search](../2026-10-09-0537/execution.md)): P 256, lexicase, 524k cap. Block arms
add one operator. After crossover and mutation, each non-elite child, with fixed probability
**r = 0.2** (a priori: about +20% edit volume), gets one block at a uniform start; the
window and next position are re-encoded conditional-uniformly under C, keeping downstream
tokens. Operator draws use a separate RNG stream, so everything else is paired across arms.
- **C**: no operator.
- **F**: intact library fragment, drawn uniformly.
- **B**: same span; each token drawn from the library's per-position distribution for that
  length (joint content removed, supply and span kept).
- **W**: same span, block sampled from C's own conditional chain (controls block editing and
  the re-encoding path).

Experimental unit: the corpus (n = 16). Each corpus is scored on its own family's 4 training
cells × **32 fresh seeds**, giving 2 048 searches per arm and 8 192 in total.

**Feasibility and cost.** C on these cells: 5.47 CPU-s per search, 91% solved (1246). At an
assumed 1.2× operator overhead, about 55k CPU-s, ~95 min on 10 workers. Prepare ≤ 30 min
(extraction, semantic checks, bit-exact replay of sampled 1246 C rows with the operator off,
timed smoke of all arms setting an all-capped bound); score ≤ 3 h timeout. With ~2.5 h of
agents, about 5.5–6.5 h total, inside the 5–7 h allowance.

**Primary comparison and decision rule.** Speed F/C = exp(mean over corpora of mean log
cost_C − log cost_F); unsolved runs cost 2 × cap; 95% t interval over 16 corpora.
- **Earns review of the reuse stage**: F/C ≥ 1.15 with lower bound > 1.0, **and** F/B and F/W
  both > 1 with lower bounds > 1. A win only over B or W does not count.
- **Ends this extractor/operator**: F/C upper bound < 1.10, or F/C resolved > 1 while F/W is
  not (block editing explains it, as in root 01's cheap-join result).
- **Otherwise unresolved**: report the corpus count needed and the price.

Descriptive: 1 × cap and both-solved sensitivities; BE/PA; realized tokens changed per
insertion per arm; underflow/default use in offspring; share of solvers containing a library
fragment (F against C's base rate); time per evaluation. Prepare also prices **reuse**
(whole-corpus libraries, F and C, comparison-gate holdouts plus then-addition; my estimate
2–2.5 h queue).

**Expectation.** F beats B (B writes incoherent stack code); F against W and C is uncertain:
C already places `INPUT FIRST GT IF_GT`-like runs cheaply, and root 01 found joins, not
modules, were the bottleneck. Guess: F/C 1.0–1.2×. Surprising: F/C ≥ 1.3× with F/W resolved
(C misses multi-token structure), or F/C < 0.9× (solver fragments disrupt more than help).

**Next action.** Earned: return to strategy with the measured reuse price (development
banks only). Ended: close 32, return to strategy. Unresolved: price resolution. No rate or
length sweep, no second library round.
