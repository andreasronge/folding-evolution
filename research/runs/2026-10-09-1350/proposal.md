---
node: questions/10-compositional-map-transfer/33-pre-solve-fragment-source
title: Fragments from pre-solve programs versus C-chain blocks on then-addition
bank: then-addition-v1
---
Follows [strategy 1350](strategy.md) and its [plan](../../plans/pre-solve-fragment-acquisition.md).
New sub-question [33](../../questions/10-compositional-map-transfer/33-pre-solve-fragment-source/question.md), budget 1. Root 10 is at 25.

**Question.** Exact-solver fragments F beat C-chain blocks W on then-addition (F/W 1.20×
[1.11, 1.29], [1036](../2026-10-09-1036/analysis.md)). Can the same extractor, run on parents
archived *before* their search first solved (1831), give a library E that also beats W? If yes,
complete solutions are not needed as the fragment source, with C held fixed.

**Probe (done, read-only, 2 s; [script](steward_probe/partial_library_probe.py),
[output](steward_probe/partial_library_probe.json)).** I took one S tape per source search and
checkpoint, using the lowest archive slot (slots are random draws, so this ignores performance).
That gives 331–359 tapes per corpus, then the 0843 rule (all-active 3–6 windows, ≥ 2 cells, top 32). All 16 libraries reach **32/32**. Every
fragment recurs in all 4 source cells and in at least 11 distinct source searches.
**About 14/32 fragments are shared with F** (9–18). The rest differ in a
telling way. E has no comparison joins (`input first gt`, `first gt if_gt`, `add … gt if_gt` are
exact-only). Instead it has `input <reducer> if_gt` and reducer pairs. So the test also asks
whether F's increment rides on the shared reducer/add syntax (E ≈ F) or on gate joins (E ≈ W).
That is suggestive, not a clean dissection. Prepare re-derives these libraries.

**Closest known technique.** Mining repeated or frequently sampled substructures from GP
populations: [Langdon & Banzhaf, *Repeated Patterns in GP* (2005)](https://gpbib.cs.ucl.ac.uk/gp-html/langdon_2005_NC.html),
[Burlacu et al., *Building Blocks Identification Based on Subtree Sample Counts* (2015)](https://gpbib.cs.ucl.ac.uk/gp-html/Burlacu_2015_APCASE.html).
Library reuse across runs: [Keijzer, Ryan & Cattolico (2004)](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf).
Discovery during search: ARL ([Rosca 1995](https://cdn.aaai.org/Symposia/Fall/1995/FS-95-01/FS95-01-011.pdf)).
The map adapts by **external fitting**; nothing is inherited. What this adds: a causal test of
whether pre-solution material holds reusable fragments, against a same-law control. A boundary test of a known idea.

**Design.** Run 1036's harness unchanged (C tables from 1548, P 256, lexicase, 524k cap, p 0.2
non-elite block edits, decoded suffix kept). Corpus i pairs 1831 collection i with C table i;
the shared ID is only bookkeeping.
- **E:** fragment drawn uniformly from corpus i's pre-solve library (the frozen rule above).
- **W_E:** C-chain blocks with E's per-corpus length and start laws.
- **Reused from 1036:** F, W and C rows on the **same 1036 then-addition seeds**, so they share
  initial populations and case draws. Prepare replays 48 of those rows bit-exactly, one per arm
  per corpus, before scoring. If any replay fails, F/C become historical references only and
  the primary contrast stands.

Unit: corpus, n = 16 (8 BE, 8 PA). Roster: 16 cells × 16 seeds per corpus, 4 096 searches per
arm, 8 192 new searches. No holdouts. Prepare adapts the extractor's source interface
(no fake `solved` flags) and checks Python/Rust traces, a tape manifest, a 10k-edit audit, NOP-padded
hits on then-addition cells (reported, not filtered) and timing. An empty library falls back to W_E and is
reported (the probe saw none).

**Feasibility and cost.** In 1036 the then-addition worker-seconds per search were F 5.69,
W 6.20 and C 7.20, at CPU efficiency 9.94 on 10 workers. Projection: 8 192 × 6.2 / 9.94 ≈
**85 min**, or 98 min with a 15% margin. Admission: if smoke × 1.15 exceeds 135 min, use 12
seeds (the first 12 of 1036's) and re-check; if that still does not fit, write `infeasible.md`.
Queue timeouts: prepare 30 + score 150 = **3 h** (cap 4 h); about 1.8 h expected. Agents need
about 3 h. **Total about 5 h.** Acquisition cost: 1831 collection 5 058 worker-s (sunk, from
saved records) and about 2 s of extraction, both reported.

**Primary comparison.** E/W_E on then-addition. Effect: exp(mean over corpora of the paired
log-cost difference); unsolved runs count as 2 × cap; 95% t interval, 15 df. Expected
half-width about ×1.08 (1036's F/W gave ×1.076). Worthwhile increment: 1.10×.
1. **Harm:** upper bound < 1. This source ends.
2. **Useful early source:** lower bound > 1 and point ≥ 1.10. Earns a strategy review of the
   complete early-data stage (6–9 h, not allocated).
3. **No worthwhile increment:** upper bound < 1.10. Ends expansion of this source/extractor at
   this scope. It does not reject pre-solve learning in general.
4. **Unresolved:** otherwise. Price a ×1.05 half-width.

**Secondary, no rule.** E/F (recovery; a procedure comparison), E/C, W_E/W (length law),
both-solved and 1 × cap sensitivities, BE/PA, per cell, library windows in solvers.

**Expectation.** E/W_E between 1.0 and 1.10 (rule 3 or 4), E/F about 0.85–0.95. Missing gate
joins should cost most of F's increment. Two results would surprise me: E/W_E ≥ 1.2 (shared
syntax is enough), or E resolved below W_E.
Scope: external extraction, C still fitted from exact solvers; no inheritance.

**Next action.** Every rule returns to strategy: rule 2 prices stage two, rule 4 prices the
resolution, rules 1 and 3 end this source.
