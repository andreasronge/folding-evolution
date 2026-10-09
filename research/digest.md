# Digest: what we currently believe, and why

As of 2026-10-09, after run 2026-10-09-0537 (commit `fe196c1`). Core question since the
2026-09-25 reframe: *how does the genotype→program map bias what evolution finds and keeps
("arrival of the frequent"), and can that bias be adapted to a task family?* Run-by-run history,
superseded numbers and fuller wording are in the questions' `log.md` files.

Sources: [notebook](../docs/map-bias/notebook.md) (§1–§32; reviews in
[docs/map-bias/reviews/](../docs/map-bias/reviews/)) and [findings](../docs/map-bias/findings.md)
(items 1–17, owner-promoted). §NN means a notebook section. Exploratory hobby work, mostly 30–50
seeds per cell; pre-registration is noted where it applies. Ratios are speed (> 1 = first arm
faster) with 95% intervals unless stated.

## 01 Map bias (root open, budget spent)

[01](questions/01-map-bias/question.md). Chem-tape and TAG alphabets, threshold and fixed-target
tasks. 03, 05, 06 closed; 02, 04, 07, 08, 09 parked with reopen conditions in their question files.

**Measuring the bias.**
- **Random-genotype frequency predicts which tasks are easy, not which hard ones get solved.**
  Evolution routinely finds behaviours rarer than 1 in 50M random tapes; on the chem-tape alphabet
  chem decoder and direct encoding have almost the same bias. ([item 1](../docs/map-bias/findings.md), §1)
- **Folding's advantage over direct encoding on fixed targets looks like sampling**: where the maps
  differ, folding makes exact solvers 1.3–30× more common and solves more often, and evolution was
  mostly a worse sampler than random search (one exception). Not general: on TAG threshold tasks
  with lexicase every arm solved 9–40× sooner than computed (not run) random search. Steering
  untested. ([item 17](../docs/map-bias/findings.md), §27–§28; [02](questions/01-map-bias/02-fixed-target-sampling/question.md), parked)
- **The frequency knob changes how often a part is made, not what is reachable**: weighting one op
  switches between equivalent routes without changing solve rates; very high weights hurt by
  dilution. ([item 12](../docs/map-bias/findings.md), §16, §19)

**Fitting the bias to a threshold family** (sum/max > k, TAG, lexicase, crossover v2, L 64, P 1024).
- **In sampling, a fitted `op_weights` vector transfers to a held-out member**: 4.9× (sum>2) and
  8.9× (max>2) more exact solvers than uniform, against 1.0× / 1.3× for the other family's fit;
  mainly the aggregator weight. One seed, one fit; the post-hoc product model that explained it
  failed out of sample. Numbers solid, meaning narrow. ([08](questions/01-map-bias/08-evolve-bias/question.md), [run 1558](runs/2026-10-05-1558/analysis.md))
- **In evolution the fitted bias is about 4× faster than uniform** (4.33× / 3.58×, lower bounds
  2.6×, 1.9×); a hand-set INPUT/GT/aggregator scaffold is within the registered 0.5–2× margin of it
  (0.93×, 1.08×; a broad margin, not equality). Family specificity unresolved: matched over the
  other family's fit 1.66× / 1.80× (not resolved against a 2× bar). Sampling lift does not predict
  speed (pass-through 0.35–3.2). Median speed, one setup. ([08](questions/01-map-bias/08-evolve-bias/question.md), [run 1705](runs/2026-10-05-1705/analysis.md))
- **The other family's vector gives a real generic speed-up; on max>2 INPUT/GT alone reproduces it
  within the tested margin.** Pre-registered, 250 pairs: 2.73× (sum>2), 2.02× (max>2) over uniform
  (lower bounds 2.12, 1.45). INPUT/GT alone versus the full vector on max>2: 0.90× [0.71, 1.08]
  (registered 1.5× margin); on sum>2 neither part is resolved against the full vector. Its flat
  sampling rate was a cancellation (INPUT/GT raises solvers 3.2× / 3.9×, the rest cuts them to
  0.23× / 0.35×). Initialization and mutation are coupled, so no mechanism is named.
  ([09](questions/01-map-bias/09-generic-bias-speedup/question.md), [run 1814](runs/2026-10-05-1814/analysis.md))
- **On sum>2 the exact max>2 shortcut is used as a last step but is not needed** (pilot, 50 seeds):
  the solver's parent in 55/60 exposed runs; barring it delays 49/55 pairs but 100/100 still solve.
  Its share of the gain is unknown (rest-of-vector gain 1.30, 0.71–2.32); not a null on the
  stepping stone. ([09](questions/01-map-bias/09-generic-bias-speedup/question.md), [run 1957](runs/2026-10-05-1957/analysis.md))

**Building blocks (chem-tape, tagged runs).** Lexicase, not a new primitive, supplies blocks;
arrangement is then the bottleneck. Tagged transplants are safe (0 crashes in 940); crossover
merges blocks when the join is cheap, but a one-op-join stack does as well, so the advantage is the
join's cost, not modularity. XOR/valley thread closed: joins are built by small edits, no valley found.
([items 4–16](../docs/map-bias/findings.md), §3–§26)

**Shared helpers** (line stopped 2026-10-05; three outputs on tags 0/1/2 sharing parts A and B;
crossover v2, lexicase, P 1024, L 64). Fairly sure for these layouts; nothing beyond them.
- **Retention is easy; establishment from rare is blocked by mixing between lineages.** A majority
  shared form persists, and the majority form wins (270/270). From 1/32–1/10 with a selected mate
  it was lost in 294/300 runs; with self as mate it won 183/240 contests (selected mate 34/240,
  crossover off 75/120). (§29–§31, [06](questions/01-map-bias/06-self-mate-establishment/question.md))
- **Crossover is also what solves, but discovery needs no lineage mixing**: random starts solve
  48–50/50 with crossover, 0–4/50 without; self-mating solves 68–80% by generation 3000, about 3×
  slower than a selected mate. A helper already in the host does not rescue a rare shared form.
  (§31 G, §32 J–K; [04](questions/01-map-bias/04-random-start-discovery/question.md) parked, [05](questions/01-map-bias/05-latent-helper/question.md) closed)
- **Solutions arrive mostly partly shared or duplicated, and the first established form is kept**
  (121/129). Shared endings are rare (about 4–8 in 100–450 runs, B-helper type); shared never loses
  to duplicated as such (losers end partly shared). Shortcuts are structural: about a third of each
  final population fits training without being exact (9/35 runs still so at 256 cases). (§31 G, §32 L)
- **Why shared endings are rare is unresolved.** Exact shared children arrive (about 2 per run, all
  A-only/other); single copies drift out (0/100 established, ≤ 3.6%); no B-helper in 30M children
  (≤ 1.2e-7). 100 insertions cannot tell drift from a disadvantage.
  ([07](questions/01-map-bias/07-shared-arrival/question.md), parked; [03](questions/01-map-bias/03-rare-shared-establishment/question.md) closed)

## 10 Compositional map transfer (root open, 22 of 22 used)

[10](questions/10-compositional-map-transfer/question.md): can a decoder adapted across related
tasks help fresh populations solve unseen operation combinations beyond a token-frequency bias?
Stack tape `v2_rmin(_first)`, length-4 lists, P 256, lexicase on 64 cases with an exact check over
the domain (D1331 from 0001 on), 524k cap. G / G4 are hand-set previous-token grammars;
"-marg" the same token marginals without context. Sub-questions 11–31 closed. Banks before
then-addition-v1 (26) were screened and inspected, so their transfer claims are development-bank
claims; then-addition-v1 was the first fresh bank, frozen with the method before scoring, and is
now a development bank too.

**Banks.**
- **The sign-gated banks could not support a symmetric two-family test** (these shapes, domains
  and frozen rules; [11](questions/10-compositional-map-transfer/11-composition-bank/question.md),
  [12](questions/10-compositional-map-transfer/12-generic-grammar-headroom/question.md),
  [15](questions/10-compositional-map-transfer/15-four-reducer-family-bank/question.md)); hence a
  one-family post-addition (PA) split (G), then a branch-else (BE)/PA split on the four-reducer
  bank (BE 1 holdout cell, PA 2; G4).
- **A comparison-gated bank gives a protected multi-holdout split with headroom.** BE
  `A>B ? C : D+E`, PA `(A>B ? C : D)+E`, 13 tokens: 37 BE and 56 PA behaviours after the exact
  ≤ 9-token screen (not a 13-token minimality certificate); a frozen, performance-blind split gives
  4 training and 4 holdouts per family with matched token totals; G4 solves 68% of training-cell
  searches at 524k. ([24](questions/10-compositional-map-transfer/24-comparison-gate-bank/question.md), [run 1246](runs/2026-10-08-1246/analysis.md))
- **Ten-token branch cells leave room above the hand-set grammars** (G medians 2–10× above 4 096;
  G4 medians 8.7k–28.7k on all 13 retained cells). (12, 15)

**Hand-set context and supply.**
- **Contextual grammars beat their own token marginals on three banks**: G/G-marg 2.6–4.5× (ADD/DADD)
  and about 10–20× (SEL), all intervals above 1; 1.5–6.0× (15/16 resolved) on the second bank;
  G4/G4-marg 4.4× [3.4, 5.6] (BE), 3.3× [2.7, 4.0] (PA). Not a mechanism: G also emits far more
  exact solvers and changes more tokens per mutation. (11, 12, 15)
- **Supply overstates speed**: a fixed token bias raises exact-solver sampling 11–82× but speed only
  1.9–3.5×; G raises supply 120–1 650× for 8.6–31×. ([11](questions/10-compositional-map-transfer/11-composition-bank/question.md))
- **A fixed decoder can express a family preference**: two hand-set family grammars give matched
  over swapped 1.68× [1.39, 2.05] (BE) and 1.32× [1.12, 1.57] (PA), strengthened by context over
  marginal controls (1.51×, 1.46×); against G4 the BE grammar helps BE (1.36×), the PA grammar shows
  no resolved PA gain (0.87× [0.75, 1.04]). Expressivity only, not what a learner finds. (15)

**Token learning by outer-loop selection** (multipliers on the hand-set rows; 4+12 loop).
- **Learned token weights transfer about 2–2.5× to withheld cells, on both setups.** On G (PA only,
  200 seeds): 2.23× [1.82, 2.75] on training, 2.06–2.25× (lower bounds ≥ 1.60) on the two withheld
  cells, unresolved on linear (1.08× [0.72, 1.57]); mostly INPUT up, DUP down, IF_GT up. From
  G-marg it gains 1.7–2.1× but stays at 0.41–0.57× of G.
  ([13](questions/10-compositional-map-transfer/13-post-addition-map-learning/question.md)) On G4:
  about 2.2× on own training cells, 2.0× (BE) and 2.5–2.6× (PA) on withheld cells, all resolved.
  ([16](questions/10-compositional-map-transfer/16-crossed-family-adaptation/question.md))
- **That gain is mostly generic; no family advantage was resolved on withheld cells.** Cross-family
  training gains 2.07× and 1.93×; all 20 maps make the same big moves. Matched over mismatched on
  withheld cells 1.02× [0.84, 1.25] (BE), 0.96× [0.79, 1.15] (PA); a 1.1× preference is not
  excluded. An in-sample interaction of 1.24× [1.09, 1.41] hints at family information on trained
  cells; a better family prior is not separated from repair of G4's weak spots. (16)
- **The frozen maps help through both the starting programs and the decoder used during search,
  sub-additively.** Given the other, ongoing decoder 1.39× / 1.28× and start 1.30× / 1.33×
  (withheld / training), diagonal 2.29× / 2.44×, interaction −0.34 / −0.52 log2 (20/20 maps). Not
  direct seeding (12 of 79 200 searches solved at generation 0). The start weighs more on BE
  training cells (−0.45 log2 [−0.68, −0.22]; family not separated from shape or difficulty).
  ([17](questions/10-compositional-map-transfer/17-decoder-initialization-variation/question.md))

**Context learned by outer-loop selection: no resolved gain from four procedures.**
- **Full 552-weight learner from G**: 0.92× [0.78, 1.09] on training; steps far below score noise
  are a plausible, unisolated cause. (13)
- **Row residuals on learned M versus continued token learning**: training 1.00× [0.90, 1.11];
  withheld PA 1.16× and 1.06×, unresolved, and not replicated across learning runs. (13, [14](questions/10-compositional-map-transfer/14-saved-map-shape-shift/question.md))
- **Rank-one context steps mixed into token continuation**: where token continuation itself
  learned (1.14×, 1.12×, resolved), C/T 0.967× [0.871, 1.073]: a gain above about 1.07× excluded for
  this loop and these token-tuned starts. Context learned jointly from G4 is untested.
  ([18](questions/10-compositional-map-transfer/18-compact-context-learning/question.md),
  [19](questions/10-compositional-map-transfer/19-selection-calibrated-continuation/question.md))

**Context fitted directly to solvers (external fitting, not selection).**
- **A previous-token table fitted to exact G4 solver tapes beats a token-only fit to the same tapes,
  and the gain transfers.** C/T 1.365× [1.288, 1.446] on training (31/32 corpora), 1.293× [1.213,
  1.378] withheld. Matching C's pooled emitted frequencies does not reproduce it (C/K 1.65×, though
  K is slower than T). No matched-family advantage resolved on the three withheld cells (BE 1.02×
  [0.91, 1.15], specificity not refuted; one PA cell favoured the mismatched fit, 0.75×). Tapes
  carry about 0.45 bits per transition of order information; a corpus pays for itself in about
  120–590 searches. One bank, split and shrinkage (α 50); which structure carries it is unknown.
  ([20](questions/10-compositional-map-transfer/20-solver-corpus-context/question.md))
- **One feedback refit, to solvers found under the fitted table, speeds search further.** C2/C
  1.404× [1.347, 1.464] on training (32/32 lineages), 1.289× [1.204, 1.381] withheld; a fresh
  one-shot G4 refit is not resolved from C (0.997× [0.940, 1.058]), so the gain is the collection
  procedure (yield, diversity and tape content bundled). The refit sharpens the decoder (lower row
  entropy), not shown causal; a second step is untested.
  ([21](questions/10-compositional-map-transfer/21-iterated-solver-corpus/question.md))
- **On training cells that step raised context's advantage over a token-only fit; on withheld cells
  this is unresolved.** I = (C2/T2)/(C1/T1) 1.169× [1.093, 1.250] (BE 1.34×, PA 1.02× [0.95, 1.09];
  median variant 1.089× [1.008, 1.177]); the token-only fit also gained about 1.2×. Withheld I
  1.087× [0.984, 1.200]. Same seeds as 1924, not an independent replication.
  ([22](questions/10-compositional-map-transfer/22-feedback-context-increment/question.md))
- **The one-shot context advantage replicates on the comparison-gate bank's training cells, larger.**
  16 new G4 corpora (yield 58.9%): C/T 3.11× [2.78, 3.48] (BE 2.86×, PA 3.37×; 2.82× at 1 × cap),
  16/16 corpora; a broad shift, not only fewer capped T runs. Why it exceeds the old bank's 1.37× is
  not identified. ([24](questions/10-compositional-map-transfer/24-comparison-gate-bank/question.md), [run 1246](runs/2026-10-08-1246/analysis.md))
- **Those frozen tables keep most of the advantage on protected holdouts and on one fresh bank of a
  new shape, shrunk from training.** No refit. Comparison-gate-v1's eight protected holdouts
  (development bank): C/T 2.60× [2.31, 2.92], 8/8 resolved. Fresh `then-addition-v1`
  (`A>B ? C+D : E`, 16 cells chosen by a semantic screen alone, pinned before any search): 2.12×
  [1.86, 2.41], 16/16 corpora, 14/16 cells resolved; 1.74× on pairs both arms solved. Shrinkage
  from training is resolved across shape, 0.68× [0.57, 0.81], not within shape, 0.88× [0.72, 1.07].
  Family matching on the holdouts unresolved, 1.10× [0.89, 1.35]; on the fresh bank C/T is larger
  for BE-fitted corpora (ratio of C/T ratios 1.38× [1.13, 1.68]; secondary). Scope: one fresh bank,
  designed after v1 was seen, all cells on two tie-heavy gates; the interval conditions on these 16
  cells; why the gain shrinks is not identified.
  ([25](questions/10-compositional-map-transfer/25-comparison-gate-transfer/question.md),
  [26](questions/10-compositional-map-transfer/26-then-addition-fresh-bank/question.md), [run 1548](runs/2026-10-08-1548/analysis.md))
- **On then-addition, frozen maps matched to C's pooled or per-position emitted frequencies do not
  reproduce C's advantage.** Same seeds and case draws, 16 corpora; every corpus and cell above 1.2
  for each: K (G4 × 24 multipliers, C's pooled marginals) C/K 2.48× [2.17, 2.83], and K is slower
  than the token fit (K/T 0.86× [0.77, 0.96]), as on the old bank (1.65×, 0.83×); Q (G4 matched to
  C's marginal at each of 32 positions) C/Q 2.41× [2.11, 2.75], not resolved from K (Q/K 1.03×
  [0.93, 1.13]); P (independent positional draws, no context) C/P 5.47× [4.79, 6.25], solving 50.5%
  against C's 86.5%. Both-solved pairs still about 1.9× for K and Q. Scope: external projections
  under the uniform latent prior, one operator set; C's mutation changes about 3 tokens against 1.7
  (K, Q) and 0.9 (P); a learned positional map is untested.
  ([29](questions/10-compositional-map-transfer/29-frequency-matched-transfer/question.md),
  [30](questions/10-compositional-map-transfer/30-position-matched-replacement/question.md),
  [run 0125](runs/2026-10-09-0125/analysis.md), [run 0306](runs/2026-10-09-0306/analysis.md))
- **Recoding Q to C's mutation width, with Q's random-program distribution held exactly fixed, made
  search slower.** Context-dependent allele permutations within each row (token counts per row
  exact, starting tapes identical to Q's) raised tokens changed per resample from 1.7 to 3.0 (C
  2.95). R30/Q 0.86× [0.80, 0.91] (14/16 corpora below 1; both realizations and families);
  full-row permutation R100/Q 0.41× [0.39, 0.43]; C/R30 2.82× [2.49, 3.19]. So random, undirected
  width does not carry C's advantage. Scope: two random recodings, one development bank; width is
  not isolated from changed allele–token correlations; structured coupling and C's content are not
  separated. ([31](questions/10-compositional-map-transfer/31-distribution-preserving-recoding/question.md),
  [run 0537](runs/2026-10-09-0537/analysis.md))

**Context fitted to non-solving programs (external fitting, before any exact solve).**
- **Tapes from G4 searches that had not yet solved teach a context fit that beats a token fit to the
  same tapes, and G4, on the comparison-gate training cells, mostly by more runs solving within the
  cap.** 16 corpora of parent tapes (searches stopped at first solve or 65k evaluations): C_S/T_S
  1.28× [1.12, 1.45] (13/16 corpora; both-solved 1.05× [0.88, 1.24]; BE 1.42× [1.17, 1.72], PA
  1.15× [0.96, 1.38] unresolved); a worthwhile 1.20× is plausible, not established. C_S/G4 1.62×
  [1.37, 1.90], again 1.62× [1.41, 1.86] on fresh seeds (2116). Selected parents not resolved from
  uniform population samples (C_S/C_P 1.04× [0.92, 1.16]). The exact-solver fit stays 3.7× faster
  (C_S/C_exact 0.27× [0.24, 0.30]) for about 7.9× more source evaluations. Scope: own training cells of a development bank, one collection
  horizon, K unscored.
  ([27](questions/10-compositional-map-transfer/27-partial-program-context/question.md), [run 1831](runs/2026-10-08-1831/analysis.md))
- **Collecting further under that partial fit beat collecting the same allocation under G4, by a
  small margin resolved only on BE.** 16 lineages, 96 sources per cell per arm: two rounds under the
  updated fit (F) against one fit to G4-collected tapes (O), F/O 1.18× [1.01, 1.37]; a worthwhile
  1.15× is neither established nor excluded. BE 1.42× [1.17, 1.72], PA 0.98× [0.83, 1.16]
  unresolved (PA collection diagnostics improved too; their causal role is unresolved). More G4
  tapes gave no resolved gain (0.99× [0.89, 1.10]); F over keeping the first fit unresolved (1.16×
  [0.99, 1.36]). Context feedback beat token feedback 1.46× [1.23, 1.75]; F stays far below the
  exact-solver fit (0.31×). Scope: 27's training cells, three rounds, equal source allocation;
  yield and tape content bundled.
  ([28](questions/10-compositional-map-transfer/28-partial-program-feedback/question.md), [run 2116](runs/2026-10-08-2116/analysis.md))

**Overall.** Assembly information beyond a token-only fit exists in this system's own solvers and
can be fitted externally; it transfers to withheld compositions and to one fresh bank of a new shape
at about 2× (a third smaller than on training). On then-addition, under these operators, the tested
frozen pooled and positional frequency projections do not reproduce C's advantage, and neither does
Q randomly recoded to C's mutation width. A much weaker version is fittable before any exact solve
(training cells only). The selection-based procedures tested have not established a reproducible
contextual search advantage over token controls; learned token biases transfer about 2× with no
resolved family specificity. Not shown: that evolution reaches fitted context; whether C's
conditional content or structured coupling carries it; transfer beyond one fresh shape.

## 23 Heritable variation bias (root parked, budget 2, 2 used)

[23](questions/23-heritable-variation-bias/question.md): can a token-frequency vector inherited
with each program learn a useful bias through program selection alone, and help fresh populations
once frozen? TAG threshold tasks (sum/max > 1, 5), development bank `tag-threshold-v1`.

- **Under the one procedure tested, inherited frequencies gave fresh populations no useful bias
  (the registered 1.5× gain over uniform) on their training targets.** Pre-registered, 20
  acquisitions per family × arm (σ = 0.03, 48 episodes × 128 generations), each frozen vector scored
  on 16 shared seeds per target. Uniform ÷ inherited cost: sum 0.33× [0.21, 0.53] (inherited
  resolved worse), max 0.73× [0.50, 1.06] (a gain above 1.06× excluded, a loss up to about 2× not).
  The hand scaffold is 11.9× and 5.75× cheaper than the inherited vectors. Fairly sure for this σ,
  schedule and inheritance rule; not a verdict on self-adaptation, silent on transfer.
  ([run 1046](runs/2026-10-08-1046/analysis.md))
- **Persistent ancestry made the max vectors less costly than shuffled ancestry; no gain over uniform
  was established.** Broken ÷ inherited 1.58× [1.04, 2.36] on max; unresolved on sum, 1.00× [0.69,
  1.41]. Drift versus selection in the vectors' movement was not isolated (no mutation-only
  control). ([log](questions/23-heritable-variation-bias/log.md))

## Older context

Background, not the current line: the original folding track (3-bond ceiling broken via Pareto
scaffold preservation; regime shift) in [docs/folding/findings.md](../docs/folding/findings.md);
pre-reframe chem-tape in [findings](../docs/chem-tape/findings.md) and
[experiments](../docs/chem-tape/experiments.md); CA in [docs/ca/experiments.md](../docs/ca/experiments.md);
[coevolution](../docs/coevolution.md), [theory](../docs/theory.md) (Altenberg),
[python-rewrite-results](../docs/python-rewrite-results.md). Process lessons:
[docs/methodology.md](../docs/methodology.md) (the line now runs in light hobby mode).
