---
estimated_minutes: 55
---
Implement the approved assembly-family screen and calibration, without running the full
queue in this researcher turn. Initial queue estimate was 90–110 minutes. The bounded D1331 smoke supports about
40–55 minutes (details in smoke.md), bounded by a
130-minute internal deadline (including a reporting reserve) and a 150-minute queue timeout.

Frozen conditions: v2_rmin, threshold slot 0, all 18 executable tokens, complete typed-stack
semantic deduplication through depth 8, depth 9 evaluated output-only. Serial domains D625
(length 4, -2..2), D1331 (length 3, -5..5), D2401 (length 4, -3..3). Roster: GA has 18
cells (unordered distinct condition reducers, ordered distinct branches); BT and BE each
have 27 (condition S/M/m, unordered distinct sum operands, any third reducer); PA has 54
(condition S/M/m, ordered distinct branches, any summand); D1 and D2 each have 18
(combinations with replacement of the two undoubled/sum reducers, any remaining reducer).
These 162 canonical ten-token programs and their roles, labels, primitive counts and
hashes are written before the screen. Exact duplicate labels reject *all* members, across
all six shapes, following 2247. No post-screen choice of duplicate representatives.
A cell retains only if canonical Rust execution agrees exactly, every <=9-token program
agrees on strictly less than 80%, and it has no duplicate. Identity, near-alias and duplicate
reasons are separate; insufficient role coverage is a pair/split failure, not an alias.

Pair selection is independent of search: >=4 retained cells in each shape, compatible
canonical token multisets between shapes, and a two-cell holdout covering only reducer-role
pairs also present in training. Choose maximum total cells, then smaller domain, then shape
names; holdouts are lexicographically first valid pairs. Report actual primitive totals
and token-multiset overlap for training and holdouts, not a claim of perfect frequency
balance. With no eligible pair, B uses all retained cells on the domain with most PA cells,
smaller domain breaking ties. The alias screen is validated against raw Rust enumeration
through depth 4, including the output-only last level; expanded domains also get independent
canonical/random full-stack checks. Stored shorter states need not be revisited: semantic
identity preserves every future continuation, and shorter witnesses suffice.

Controls U/F/G/G-marg are the exact frozen 2247 tables, vendored with expected hashes;
no marginal refitting or tuning of these controls. Search reuses the existing allele decoder
and fresh-population lexicase engine, parametrised by inputs, with P=256, 32 alleles, 64
fixed lexicase cases, cap=524288. Seeds 260601000+i (i=0..49) are shared across cells and arms;
F top-ups use 260602000+i (i=0..99) only if the first 50 solve 30..39. Diagnostic C reuses B seeds 260601000+i for paired G/matched comparisons;
it starts fresh program populations under each grammar. Sampling uses disjoint seeds 260604000+arm*10000+chunk; bootstraps 260605000.
Smoke uses disjoint seeds starting 260609000. Never seed populations with canonical solutions.
Search outputs preserve exact full-domain checks, shortcuts, elapsed time including capped
runs, budget-specific times, fitness and diversity curves, training indices and table hashes.

Critic notes 1–5: Time B's first balanced block of ten seeds on the *actual retained roster*
and domain, not just D625. Record block wall throughput and project remaining B, all
requested F top-ups, conditional C, and reporting time; sampling is secondary and cut first.
Continue baseline B before top-ups and C, using complete balanced ten-seed blocks. Any missing
required block/top-up/C leaves calibration unresolved. Serial stage A processes release memory
between domains. Smoke benchmarks expanded-domain cells (including linear) at full cap;
severe runtime/memory mismatch stops implementation with infeasible.md rather than a redesign.
Sampling targets 100000000 genotypes per base arm in bounded chunks, records actual completed
denominators, exact hits and Clopper–Pearson intervals; zero hits also receive a one-sided
95% upper bound 1-0.05**(1/n). Sampling incompleteness alone does not invalidate B/C.

Freeze all six diagnostic grammar tables *before* screening. Every modified row starts at
500 per token (11500 total), with remaining 11500 allocated equally to named destinations:
GA/BT/BE: after ADD -> INPUT (12000 total), after IF_GT -> DUP (12000);
PA: after IF_GT -> INPUT and ADD (6250 each), after ADD -> DUP (12000);
D1: after each reducer -> DUP, after ADD -> INPUT;
D2: after each reducer -> INPUT, after ADD -> DUP.
BT versus BE intentionally has identical tables: the proposed rows cannot distinguish that
pair; still run/report the contrast if selected, with no claim about the whole decoder class.
Unchanged rows are frozen G. Marginals follow 2247: 312500 decoded genotypes, seeded by shape,
then independent 312500 validation genotypes and the same tolerance. Hash/save all tables.
C runs both selected tables and their tied marginals on every cell, 50 seeds each; also
report matched/swapped contrast with context removed, descriptively.

Measurements: each cell/arm gets solve fraction, Kaplan–Meier median and 95% bootstrap interval
(common administrative censoring; fewer than half solves means >cap), mean censored-inclusive
seconds, shortcuts, and sampling rates/bounds. Ratios G/U, F/U, G/G-marg are paired capped-time
ratios per cell for descriptive use, explicitly not uncensored KM ratios. Shape decisions use
geometric means of cellwise paired KM median ratios. Bootstrap seed blocks are resampled jointly
across all cells/arms (2000 replicates). Any nonfinite median in a point estimate or bootstrap
replicate makes that shape's KM contrast unresolved; record fraction of undefined replicates,
and capped-time sensitivity alongside it, never turn inf/inf into 1.

Outcome interpretations (first applicable): incomplete A/B/required top-up/C => U for the
calibration, but retain a separate completed semantic verdict. With complete A and no pair,
row 1 means only the enumerated 162 candidates on these three domains fail the stated alias,
duplicate or split rules. It does not require an alphabet change or exclude other length-10
families. A surviving pair with censoring or an interval spanning 1 is U for the affected
contrast (candidate for precision top-up, not equality). Row 2 means these diagnostic grammars
did not establish the >=1.5 contrast in both shapes; an upper bound below 1 is observed
inferiority, not decoder-class impossibility. Row 3 requires improvement over G established
(lower bound >1) in *both* shapes and fewer than two of four holdouts fail the unchanged 4096 headroom rule;
an interval spanning 1 remains U, while established lack of the operational advantage is row 3.
Row 4 is no B with >=50% G solves on every training cell, or cheapest eligible G-start scenario
>16 wall hours; row 5 passes both shape contrasts, holdout headroom and <=16h projection.
Comparable contextual and tied-marginal contrasts support a frequency explanation, not transfer.
No adaptation or transfer is measured in this cycle.

Stage D: without a pair, split-specific cost is undefined; report per-cell U/G cost and solve
curves at B=32768/65536/131072. Otherwise for each shape and start U/G pool within-cell variances
of log2(min(T,B)); k=max(2,ceil(4*SD_B**2/n_train)) targets SE <=0.5 log2 units for the equally
weighted training objective assuming independent inner runs. 6 contextual + 6 token-only
trajectories per shape, population 16, 30 generations (initial population plus 30 offspring
populations: 31 evaluations). Reuse trajectories for both transfer directions. Project 24
maps + 24 tied marginals + 4 controls on 4 holdouts x 50 seeds, plus 24 marginal estimates
(and validation). Include capped-search scenarios and arithmetic. Starting-decoder costs are
scenarios: adaptation can change runtime. Any later >8h study needs separately reviewed queues.

Critic notes 6–7 concern existing digest/question claims. This researcher role may write only
this run folder in research/, so those edits are deferred to the steward; the new reporting
uses the qualified operational threshold and does not claim an optimisation ceiling.
