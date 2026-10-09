---
estimated_minutes: 110
---

Implement the approved training-stage experiment, using the frozen 1246 source and unchanged C tables/search (population 256, length 32, 64 search cases, lexicase, crossover .7, mutation .03, two elites, evaluation cap 524288). This is implementation of an approved proposal, not a new preregistration, result promotion, or redesign. No efficacy runs before preparation admission; smoke seeds never enter the scored endpoint.

All 16 corpora (BE1–BE8, PA1–PA8) and their four training cells remain in the score roster. Arms C/F/B/W share fresh initialization, cases and base variation draws; F/B/W additionally use a separate operator stream seeded [search_seed, 4]. Each non-elite child receives a block with probability .2 after standard crossover and mutation. F draws uniformly from its leave-one-cell-out library; B and W sample the same empirical library length law. B draws independent position marginals conditional on length; W draws the C chain conditional on the preceding decoded token. Starts are uniform on 0..32-L. Conditional-uniform inverse encoding touches the window and, when present, its next allele only, retaining decoded suffix and tape end. This alters allele variation as well as coordinated token content; measured span does not imply equal realized edits.

Preparation: NOP knockout on 96 fixed inputs (default_rng(0), sampling without replacement) identifies active source positions. Extract all-active contiguous lengths 3–6 from G4 collection solvers, retaining occurrence/seed/start provenance and requiring recurrence in at least two source cells. For each scoring cell exclude that cell's source tapes; order by descending source-cell count, occurrence count, length, then ascending token tuple. Drop fragments that solve any of the corpus's four cells when NOP-padded, tested over the complete input domain; retain at most 32. Below 8 in any library is infeasible (save roster and measured count). Report standalone stack effects and source-context underflow/wrong-type/default usage, explicitly distinguishing standalone behavior from knockout contribution. Build whole-corpus libraries only for a continuation price, without scoring reuse.

Validate 10,000 edits per block arm (across all corpora/cells, forced boundary coverage including start/end) for decoded outside-window and terminal invariance, conditional allele intervals, untouched outside alleles except repair position, and elite exclusion. Replay one historical 1246 C training row per corpus through the operator-off search and compare substantive fields exactly, excluding runtime metadata and newly added diagnostic fields. Pair initial hashes/case indices and log source/bank/code/backend hashes.

Seeds: scoring uses seed_for(0, family, corpus_index, cell_index, seed_index, base=203610090843 (task timestamp + 1e9)), with index 0..s-1 and paired arms. Smoke uses phase 1 of the same rule, eight indices per cell. Its 128 searches cover four arms × four cells × eight seeds. Distribute each cell's eight smoke seeds across all eight corpora of each family (four seed indices/cell for BE, four for PA), rotating cells through the corpus roster so every corpus and both families are timed. This gives broad corpus coverage but is not a precise new-arm rate estimate. No smoke seed overlaps scoring or source seeds. Fixed historical pseudo-arm procedure uses seed 202610090844 and 512 replicates: within each corpus/cell resample its 16 historical C rows into two independent groups of size 16/24/32; calculate corpus SD and t half-widths. Also retain the steward's stated .27/.19 SD scenarios, interpolation .22 at 24, and distinguish them from between-corpus F-effect variance.

Historical C-like expectation: 936/1024 = .9141 solves; at 32 seeds, 1872 expected solves per arm out of 2048 (24: 1404/1536; 16: 936/1024). This is only a scenario for F/B/W, whose rates are unknown. Replace these with arm-specific smoke estimates, denominators, times with production diagnostics, and uncertainty warnings after smoke. Precision scenario: t(15) SD / sqrt(16) gives half-width factors about 1.155, 1.124, 1.107 at 16/24/32 seeds. A 1.15× effect would not exclude 1 at 16 under this scenario; fallback sizes can resolve larger gains but are less capable at the target.

Admission: project each candidate s in [32,24,16] by sum_arm(64*s*mean_worker_seconds_arm)*1.15/10; select largest fitting both proposal's 3.5-hour admission and the timeout ledger. Reserve 45 minutes for queued preparation and at most 195 minutes for scoring (total ≤240 minutes), including scoring/reporting reserve and a deterministic replay of the smoke roster before scoring. If no candidate fits, source/library validation fails, or preparation exceeds 45 minutes, stop with infeasible.md, measured numbers and a concrete alternative for strategy. Do not change arms, rates, corpora, cap, or library rule to rescue admission.

Measurements: search.jsonl emits complete solver tapes, evaluations/solves, fitness/diversity curves, time/evaluation, initial hashes, cases, block attempts/spans/actual token changes and sampled offspring default/underflow diagnostics. Library records give token names, stack effects and source provenance; reports count library windows present in full solvers (occurrence, not causal use). Report BE/PA separately, W/C and B/C, penalty=1*cap, and both-solved paired sensitivities. Incomplete rosters never yield an efficacy decision. Plot fitness/diversity curves, edit diagnostics and cost/solve summaries.

Primary X/Y is exp(mean_corpus(mean_cell_seed(log cost_Y - log cost_X))), equal corpus weights, unsolved cost=2*cap, 95% t intervals across 16 independent corpus contrasts (15 df). Apply approved rules in order: (1) F/C≥1.15 with lower bound>1 AND F/B and F/W lower bounds>1 earns strategy review of reuse; (2) F/C upper bound<1.10 ends this extractor/operator; (3) F/C lower bound>1 and F/W upper bound<1.10 ends the library as **no worthwhile fragment increment over W**; report W/C, and use “block editing suffices” only if W/C supports it; (4) resolved F/C gain with F/B or F/W spanning 1..1.10 is joint-content unresolved; (5) otherwise unresolved. Rules 4/5 price a ×1.07 half-width using observed corpus SD and measured search costs, as a variance scenario rather than guaranteed precision. No broad interval establishes equality. A three-way win supports this externally fitted literal-block procedure on development cells; it does not establish modularity, C's mechanism, evolutionary acquisition, or fresh-bank transfer.

Critique disposition: all notes 1–5 retained above. The existing pseudo-arm claim is not reproduced by loo_probe.py; preparation saves an explicit calculation and seed rather than presenting it as known new-arm precision. Rosca's 1995 AAAI paper is sole-authored; ARL attribution is Justinian P. Rosca. DreamCoder learns abstractions and a search guide, whereas this implementation tests literal extracted blocks. Note 6 requires no implementation or belief edits. Continuation price includes whole-corpus library build and validation time, F/C holdout+then-addition searches (16 corpora, 8+16 cells, provisional 8 seeds), queue wall-clock with margin, and ~2.5 hours agent/review/analysis work; no continuation is authorized by this queue.

Implementation note before scientific searches: the initial timestamp-only seed namespace collided with historical seeds. The validation caught this before replay/smoke; use the disjoint +1e9 namespace above. The first extraction yielded 32 fragments in every LOO library. The failed attempt and roster remain in smoke/prepare-v1. Edit audits now include uniform interior starts as well as explicit tape-start/end cases.

Final implementation smoke (smoke/prepare-final/preparation.json): preparation 108.02 s;
all 64 LOO libraries contain 32 fragments; 30,000 edit checks passed (10k/arm,
including ~2,690 start and ~2,669 end edits per arm); all 16 frozen C refit checks
and 16 historical scientific-payload replays passed. The 128-search smoke has
32 searches/arm across all 16 corpora, with identical paired initial hashes/cases
and exactly 254 non-elite children per non-terminal generation.

| arm | smoke solves | worker seconds/search | expected full solves (scenario) |
|---|---:|---:|---:|
| C | 29/32 | 6.263 | 1856/2048 |
| F | 31/32 | 5.792 | 1984/2048 |
| B | 29/32 | 6.031 | 1856/2048 |
| W | 28/32 | 7.290 | 1792/2048 |

Select 32 seeds: full scoring projects to 5976.40 s (99.61 min); smoke replay
93.38 s plus 240 s reporting/scheduling reserves bring it to 6309.78 s
(105.16 min), below the 195-minute scoring timeout. Expected queued preparation
plus scoring is ~107 minutes; frontmatter rounds to 110. The timeout ledger is
45 + 195 = 240 minutes, meeting strategy's four-hour ceiling. Timings include
production sparse diagnostics, both families, and two cell/seed samples per
corpus per arm; each arm's rate remains uncertain at n=32. Some search tails
(67–91 s) exceed the historical capped mean; the mean-runtime admission passes,
but a widespread tail/cap shift would hit the fixed deadline and yield no
efficacy decision rather than silently reducing the roster.

Saved precision reconstruction (seed 202610090844; 512 bootstrap pseudo-arm
replicates) gives median corpus SD .2545/.2080/.1793 and half-width factors
1.1452/1.1172/1.1003 at 16/24/32 seeds. These are historical-C noise scenarios,
not measured F-effect heterogeneity; preserve both this calculation and the
steward's stated .27/.19 scenario. Reuse price is 3072 searches each for F/C:
~71 queue minutes scoring, whole-library build/validation/reporting ~10 min,
and 2.5 agent hours (~3.85 h complete scenario). It extrapolates training rates;
excluded compositions can be harder. Larger-corpus resolution prices also
charge measured historical G4 source collection (~3002 worker-s/corpus), C fit
verification and library extraction, plus scoring/reporting and agent work.

Tests: 34 focused tests pass, including complete-roster report/plot generation
and rejection of incomplete data; ruff and git diff whitespace checks pass.
Queue parser validates both task-prefixed IDs, worktree commands, outputs under
RUN_DIR, and summed 14,400 s timeouts. Full efficacy is reserved for the queue.

Scoring handoff smoke passed: smoke/handoff-final/validation.json verifies all 128 scientific payloads (including solver and operator counters), with no efficacy searches. Final code commit `e347793549b0531f7acf167a5cc1768ae77ff127` matches every preparation code/backend hash; worktree is clean. Research task files are outside this worktree and were not committed on the research branch.
