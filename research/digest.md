# Digest: what we currently believe, and why

As of 2026-10-09, after run 2026-10-09-2033 (commit `e12edbf`). Core question since the
2026-09-25 reframe: *how does the genotype→program map bias what evolution finds and keeps
("arrival of the frequent"), and can that bias be adapted to a task family?* History and
superseded numbers are in the questions' `log.md` files.

Sources: [notebook](../docs/map-bias/notebook.md) (§1–§32; [reviews](../docs/map-bias/reviews/))
and owner-promoted [findings](../docs/map-bias/findings.md) (items 1–17). Exploratory hobby work,
mostly 30–50 seeds per cell; pre-registration noted where it applies. Ratios are speed (> 1 = first
arm faster) with 95% intervals unless stated.

## 01 Map bias (root open, budget spent)

[01](questions/01-map-bias/question.md). Chem-tape and TAG alphabets, threshold and fixed-target
tasks. 03, 05, 06 closed; 02, 04, 07, 08, 09 parked (reopen conditions in their question files).

**Measuring the bias.**
- **Random-genotype frequency predicts which tasks are easy, not which hard ones get solved.**
  Evolution routinely finds behaviours rarer than 1 in 50M random tapes; on chem-tape, chem decoder
  and direct encoding have almost the same bias. ([item 1](../docs/map-bias/findings.md), §1)
- **Folding's fixed-target advantage over direct encoding looks like sampling**: where the maps
  differ, folding makes exact solvers 1.3–30× more common and solves more often; evolution was
  mostly a worse sampler than random search (one exception). Not general: on TAG threshold tasks
  with lexicase every arm solved 9–40× sooner than computed random search. Steering untested.
  ([item 17](../docs/map-bias/findings.md), §27–§28; [02](questions/01-map-bias/02-fixed-target-sampling/question.md), parked)
- **The frequency knob changes how often a part is made, not what is reachable**: weighting one op
  switches between equivalent routes without changing solve rates; very high weights dilute.
  ([item 12](../docs/map-bias/findings.md), §16, §19)

**Fitting the bias to a threshold family** (sum/max > k, TAG, lexicase, crossover v2, L 64, P 1024).
- **In sampling, a fitted `op_weights` vector transfers to a held-out member**: 4.9× (sum>2) and
  8.9× (max>2) more exact solvers than uniform, against 1.0× / 1.3× for the other family's fit;
  mainly the aggregator weight. One seed, one fit; a post-hoc product model failed out of sample.
  Numbers solid, meaning narrow.
  ([08](questions/01-map-bias/08-evolve-bias/question.md), [run 1558](runs/2026-10-05-1558/analysis.md))
- **In evolution the fitted bias is about 4× faster than uniform** (4.33× / 3.58×, lower bounds
  2.6×, 1.9×); a hand-set INPUT/GT/aggregator scaffold is within the registered 0.5–2× margin of it
  (0.93×, 1.08×; not equality). Family specificity unresolved (1.66× / 1.80× over the other
  family's fit, against a 2× bar). Sampling lift does not predict speed. Median speed, one setup.
  ([08](questions/01-map-bias/08-evolve-bias/question.md), [run 1705](runs/2026-10-05-1705/analysis.md))
- **The other family's vector gives a real generic speed-up; on max>2 INPUT/GT alone reproduces it
  within the tested margin.** Pre-registered, 250 pairs: 2.73× (sum>2), 2.02× (max>2) over uniform
  (lower bounds 2.12, 1.45); INPUT/GT alone versus the full vector on max>2 0.90× [0.71, 1.08]
  (registered 1.5× margin); on sum>2 neither part is resolved. Initialization and mutation are
  coupled, so no mechanism is named.
  ([09](questions/01-map-bias/09-generic-bias-speedup/question.md), [run 1814](runs/2026-10-05-1814/analysis.md))
- **On sum>2 the exact max>2 shortcut is used as a last step but is not needed** (pilot, 50 seeds):
  the solver's parent in 55/60 exposed runs; barring it delays 49/55 pairs but 100/100 still solve.
  Its share of the gain is unknown (1.30, 0.71–2.32).
  ([09](questions/01-map-bias/09-generic-bias-speedup/question.md), [run 1957](runs/2026-10-05-1957/analysis.md))

**Building blocks (chem-tape, tagged runs).** Lexicase, not a new primitive, supplies blocks;
arrangement is then the bottleneck. Tagged transplants are safe (0 crashes in 940); crossover
merges blocks when the join is cheap, but a one-op-join stack does as well, so the advantage is the
join's cost, not modularity. No valley found: joins are built by small edits (thread closed).
([items 4–16](../docs/map-bias/findings.md), §3–§26)

**Shared helpers** (three outputs on tags 0/1/2 sharing parts A and B; crossover v2, lexicase,
P 1024, L 64). Fairly sure for these layouts; nothing beyond them.
- **Retention is easy; establishment from rare is blocked by mixing between lineages.** A majority
  shared form persists and wins (270/270). From 1/32–1/10 with a selected mate it was lost in
  294/300 runs; with self as mate it won 183/240 contests (selected mate 34/240, crossover off
  75/120). (§29–§31, [06](questions/01-map-bias/06-self-mate-establishment/question.md))
- **Crossover is also what solves, but discovery needs no lineage mixing**: random starts solve
  48–50/50 with crossover, 0–4/50 without; self-mating solves 68–80% by generation 3000, about 3×
  slower than a selected mate. A helper already in the host does not rescue a rare shared form.
  (§31 G, §32 J–K; [04](questions/01-map-bias/04-random-start-discovery/question.md) parked, [05](questions/01-map-bias/05-latent-helper/question.md) closed)
- **Solutions arrive mostly partly shared or duplicated, and the first established form is kept**
  (121/129). Shared endings are rare (about 4–8 in 100–450 runs); shared never loses to duplicated
  as such. Shortcuts are structural: about a third of each final population fits training without
  being exact (9/35 runs still so at 256 cases). (§31 G, §32 L)
- **Why shared endings are rare is unresolved.** Exact shared children arrive (about 2 per run, all
  A-only/other); single copies drift out (0/100 established, ≤ 3.6%); no B-helper in 30M children
  (≤ 1.2e-7). 100 insertions cannot tell drift from a disadvantage.
  ([07](questions/01-map-bias/07-shared-arrival/question.md), parked; [03](questions/01-map-bias/03-rare-shared-establishment/question.md) closed)

## 10 Compositional map transfer (root open, 28 of 28 used)

[10](questions/10-compositional-map-transfer/question.md): can a decoder adapted across related
tasks help fresh populations solve unseen operation combinations beyond a token-frequency bias?
Stack tape `v2_rmin(_first)`, length-4 lists, P 256, lexicase on 64 cases with an exact domain
check, 524k cap. G / G4: hand-set previous-token grammars for the post-addition split and the
four-reducer bank; "-marg": the same token marginals without context. Sub-questions 11–36
closed. Every bank, including then-addition-v1 (fresh when first scored in 26), is now a
development bank.

**Banks.** Sign-gated banks could not support a symmetric two-family test (these shapes and rules;
[11](questions/10-compositional-map-transfer/11-composition-bank/question.md),
[12](questions/10-compositional-map-transfer/12-generic-grammar-headroom/question.md),
[15](questions/10-compositional-map-transfer/15-four-reducer-family-bank/question.md)); the
four-reducer bank's ten-token branch cells leave headroom above the hand-set grammars.
**The comparison-gate bank gives a protected multi-holdout split with headroom**: branch-else
(BE) `A>B ? C : D+E`, post-addition (PA) `(A>B ? C : D)+E`, 13 tokens, 37 BE and 56 PA behaviours
after an exact ≤ 9-token screen (no 13-token minimality certificate); frozen, performance-blind
4 training and 4 holdouts per family; G4 solves 68% of training-cell searches at 524k.
([24](questions/10-compositional-map-transfer/24-comparison-gate-bank/question.md), [run 1246](runs/2026-10-08-1246/analysis.md))

**Hand-set context and supply.**
- **Contextual grammars beat their own token marginals on all three banks**: G/G-marg 2.6–20× (11)
  and 1.5–6.0× (12, 15/16 cells resolved), G4/G4-marg 4.4× [3.4, 5.6] BE, 3.3× [2.7, 4.0] PA (15).
  Not a mechanism: G also emits far more exact solvers and changes more tokens per mutation.
- **Supply overstates speed**: a token bias raises exact-solver sampling 11–82× but speed only
  1.9–3.5× (11).
- **A fixed decoder can express a family preference**: matched over swapped family grammars
  1.68× [1.39, 2.05] (BE), 1.32× [1.12, 1.57] (PA); against G4 only the BE grammar resolved a gain
  for its family. Expressivity only. (15)

**Token learning by outer-loop selection** (multipliers on the hand-set rows; 4+12 loop).
- **Learned token weights transfer about 2–2.5× to withheld cells, on both setups.** G (PA, 200
  seeds): 2.23× [1.82, 2.75] training, 2.06–2.25× (lower bounds ≥ 1.60) on two withheld cells,
  unresolved on linear (1.08× [0.72, 1.57]); mostly INPUT up, DUP down, IF_GT up
  ([13](questions/10-compositional-map-transfer/13-post-addition-map-learning/question.md)). G4:
  about 2.2× on own training cells, 2.0× (BE) and 2.5–2.6× (PA) withheld, all resolved
  ([16](questions/10-compositional-map-transfer/16-crossed-family-adaptation/question.md)).
- **That gain is mostly generic; no family advantage was resolved on withheld cells.** Cross-family
  training gains 2.07× and 1.93×; all 20 maps make the same big moves. Matched over mismatched
  withheld 1.02× [0.84, 1.25] (BE), 0.96× [0.79, 1.15] (PA); a 1.1× preference is not excluded. An
  in-sample interaction (1.24× [1.09, 1.41]) hints at family information on trained cells, not
  separated from repair of G4's weak spots. (16)
- **The frozen maps help through both the starting programs and the search decoder,
  sub-additively.** Given the other, decoder 1.39× / 1.28× and start 1.30× / 1.33× (withheld /
  training), both 2.29× / 2.44× (20/20 maps); not direct seeding. The start weighs more on BE
  training cells (not separated from shape or difficulty).
  ([17](questions/10-compositional-map-transfer/17-decoder-initialization-variation/question.md))

**Context learned by outer-loop selection: no resolved gain from four procedures.** Full
552-weight learner from G 0.92× [0.78, 1.09] on training (13); row residuals versus continued token
learning 1.00× [0.90, 1.11] on training, withheld unresolved and not replicated (13,
[14](questions/10-compositional-map-transfer/14-saved-map-shape-shift/question.md)); rank-one
context steps in token continuation C/T 0.967× [0.871, 1.073], a gain above about 1.07× excluded
for this loop and these token-tuned starts
([18](questions/10-compositional-map-transfer/18-compact-context-learning/question.md),
[19](questions/10-compositional-map-transfer/19-selection-calibrated-continuation/question.md)).
Context learned jointly from G4 is untested.

**Context fitted directly to solvers (external fitting, not selection).**
- **A previous-token table (C) fitted to exact G4 solver tapes beats a token-only fit (T) to the
  same tapes, and the gain transfers.** Four-reducer bank: C/T 1.365× [1.288, 1.446] training
  (31/32 corpora), 1.293× [1.213, 1.378] withheld. Matching C's pooled emitted frequencies does not
  reproduce it (C/K 1.65×). No matched-family advantage resolved on withheld cells (BE 1.02× [0.91,
  1.15]; specificity not refuted). One bank, split and shrinkage; the carrying structure is unknown.
  ([20](questions/10-compositional-map-transfer/20-solver-corpus-context/question.md))
- **One feedback refit, to solvers found under C, speeds search further.** C2/C 1.404× [1.347,
  1.464] training (32/32 lineages), 1.289× [1.204, 1.381] withheld; a fresh one-shot G4 refit is
  not resolved from C (0.997× [0.940, 1.058]), so the gain is the collection procedure (yield,
  diversity and tape content bundled). It raised context's advantage over a token-only fit on
  training (1.169× [1.093, 1.250], mostly BE; withheld unresolved, 1.087× [0.984, 1.200]). A second
  step is untested.
  ([21](questions/10-compositional-map-transfer/21-iterated-solver-corpus/question.md),
  [22](questions/10-compositional-map-transfer/22-feedback-context-increment/question.md))
- **On the comparison-gate bank C/T is larger on training cells (3.11× [2.78, 3.48], 16/16
  corpora; why it exceeds 1.37× is unidentified), and frozen tables keep most of it on protected
  holdouts and one fresh shape, shrunk from training.** No refit. Holdouts 2.60× [2.31, 2.92], 8/8
  resolved; `then-addition-v1` (`A>B ? C+D : E`, 16 cells pinned before any search) 2.12× [1.86,
  2.41], 16/16 corpora, 14/16 cells resolved. Shrinkage resolved across shape (0.68× [0.57, 0.81]),
  not within (0.88× [0.72, 1.07]); cause unidentified. Family matching on holdouts unresolved
  (1.10× [0.89, 1.35]); on then-addition C/T is larger for BE-fitted corpora (1.38× [1.13, 1.68];
  secondary). Scope: one fresh bank, designed after v1 was seen, two tie-heavy gates; the interval
  conditions on these 16 cells.
  ([24](questions/10-compositional-map-transfer/24-comparison-gate-bank/question.md),
  [25](questions/10-compositional-map-transfer/25-comparison-gate-transfer/question.md),
  [26](questions/10-compositional-map-transfer/26-then-addition-fresh-bank/question.md), [run 1548](runs/2026-10-08-1548/analysis.md))
- **On then-addition, frozen frequency projections of C do not reproduce its advantage, nor does
  random recoding to C's mutation width.** C/K 2.48× [2.17, 2.83] (K: G4 token multipliers matched
  to C's pooled marginals; K/T 0.86× [0.77, 0.96]); C/Q 2.41× [2.11, 2.75] (Q: matched at each of
  32 positions; Q/K 1.03× [0.93, 1.13]); C/P 5.47× (independent positional draws). Recoding Q's
  rows at a fixed random-program distribution to C's width (tokens changed per resample 1.7 → 3.0;
  C 2.95) slowed search: R30/Q 0.86× [0.80, 0.91], full-row 0.41×. Scope: one operator set, two
  recodings; C's conditional content and structured coupling not separated; a learned positional
  map untested.
  ([29](questions/10-compositional-map-transfer/29-frequency-matched-transfer/question.md),
  [30](questions/10-compositional-map-transfer/30-position-matched-replacement/question.md),
  [31](questions/10-compositional-map-transfer/31-distribution-preserving-recoding/question.md))

**Learned fragments as block edits (external fitting; development banks).** C's search unchanged;
each non-elite child (p 0.2) gets one 3–6-token block, decoded suffix kept. F: a library of 32
knockout-active windows recurring in the training solvers; controls B (the library's per-position
marginals) and W (blocks sampled from C's own chain), same length and start laws.
- **F speeds search beyond C on the comparison-gate training cells.** Leave-one-cell-out, 16
  corpora: F/C 1.57× [1.42, 1.75] (16/16 corpora), F/B 1.60× [1.45,
  1.77], F/W 1.23× [1.12, 1.36].
  ([32](questions/10-compositional-map-transfer/32-learned-fragment-operator/question.md), [run 0843](runs/2026-10-09-0843/analysis.md))
- **Frozen whole-corpus libraries keep that advantage on the excluded compositions tested.**
  Then-addition F/C 1.47× [1.38, 1.56] (16/16 corpora), F/W 1.20× [1.11, 1.29] (14/16); holdouts
  F/C 1.75× [1.57, 1.95], F/W 1.27× [1.17, 1.38]. F/C's change from training is unresolved (0.93×
  [0.83, 1.05]), whereas C/T lost a third across the same shape. F/W above a worthwhile 1.10× is
  not established; uneven across cells (5/16 resolved). Scope: the libraries are the banks' shared
  3–5-token syntax, which then-addition needs by construction: reuse of one external fit across one
  shape change, not modularity, fresh-bank transfer or acquisition; changed token supply not
  excluded. (32, [run 1036](runs/2026-10-09-1036/analysis.md))
- **Library-free chain blocks (W) also beat C; marginal blocks (B) showed no resolved gain.** W/C
  1.28× [1.17, 1.39] training, 1.23× [1.15, 1.31] then-addition, 1.38× [1.23, 1.56] holdouts; B/C
  0.98× [0.93, 1.04] on training (a gain above 1.04× excluded, a small loss not) at ~2.8 tokens
  changed per edit, so edit size alone does not explain F's or W's gain. (32)
- **W's suffix repair is not needed for its gain on then-addition at this resolution.** R: the same
  chain blocks without the repair, paired with 1036: W/R 0.954× [0.903, 1.007] (a repair gain above
  0.7% excluded, a cost up to about 10% not; 1.10× excluded under each sensitivity and family
  split); R/C 1.286× [1.208, 1.370], 16/16 corpora. The ripple is local: 64% of edits change the
  suffix, by about 3 tokens when they do. Not isolated from W's length law or token supply. Scope:
  full C only, development bank.
  ([34](questions/10-compositional-map-transfer/34-chain-block-suffix-preservation/question.md), [run 1606](runs/2026-10-09-1606/analysis.md))
- **The same extractor applied to pre-solve parents (E) gave no worthwhile gain over chain blocks
  on then-addition.** E: libraries from 1831's parents archived before their search first solved;
  W_E: chain blocks with E's length law. E/W_E 0.981× [0.911, 1.057] (a gain above about 1.06×
  excluded, a small gain or loss not); E/F 0.843× [0.795, 0.892], 0/16 corpora. E lacks F's `gt`
  comparison joins (descriptive; untested as F's carrier). Scope: one source selection and
  extractor, C still fitted from exact solvers.
  ([33](questions/10-compositional-map-transfer/33-pre-solve-fragment-source/question.md), [run 1350](runs/2026-10-09-1350/analysis.md))
- **Rebuilding decoder and library from four source attempts per cell (C4, F4) loses about a third
  of the full pipeline's speed on then-addition.** Four capped G4 attempts per training cell
  (8% of the source evaluations, failures charged): (C4+F4)/F 0.679×
  [0.614, 0.752], 16/16 corpora; the pre-set 0.833 tolerance excluded pooled and per family (not in
  every source block); (C4+F4)/C 0.996× [0.919, 1.080]; F4/W4 1.12× [1.03, 1.22] (unresolved
  against 1.10). Counting acquisition, cheaper than full F up to about 1 500 [1 250, 2 000] fresh
  searches. One source size; single builds vary (0.21–1.34); decoder and library losses not
  separated.
  ([35](questions/10-compositional-map-transfer/35-small-source-acquisition/question.md), [run 1743](runs/2026-10-09-1743/analysis.md))
- **Four more attempts per cell collected under that cheap bias (A8) beat four more G4 attempts
  (S8), and the rebuilt pipeline is not resolved from the full one; whether the gain reaches a
  worthwhile 1.10× is unresolved.** Both pool eight attempts and refit. Cost ratios: S8/A8 1.13×
  [1.04, 1.22] (14/16 corpora; same under the cap sensitivities); full F/A8 1.03× [0.95, 1.12] (an
  A8 slowdown above about 5% excluded); full F/S8 0.92× [0.84, 1.00]. A8's batch solved 92.5% (G4
  58%) at 0.30× the evaluations; no lock-in. With acquisition (A8 6.5 M, S8 10.2 M, full F 61 M
  evaluations), A8 beats S8 at every horizon, resolved to 1 024 searches. Scope: one
  external-fitting update, development sources and bank; yield, content, decoder and library
  bundled.
  ([36](questions/10-compositional-map-transfer/36-sparse-source-feedback/question.md), [run 2033](runs/2026-10-09-2033/analysis.md))

**Context fitted to non-solving programs (external fitting, before any exact solve).**
- **Tapes from G4 searches that had not yet solved teach a context fit (C_S) that beats a token fit
  to the same tapes, and G4, on the comparison-gate training cells, mostly by more runs solving
  within the cap.** Parent tapes stopped at first solve or 65k evaluations: C_S/T_S 1.28× [1.12,
  1.45] (both-solved 1.05× [0.88, 1.24]; PA unresolved); C_S/G4 1.62× [1.37, 1.90], again 1.62× on
  fresh seeds. Selected parents not resolved from uniform population samples (1.04× [0.92, 1.16]).
  The exact-solver fit stays 3.7× faster for about 7.9× more source evaluations. Scope: own
  training cells, one collection horizon. ([27](questions/10-compositional-map-transfer/27-partial-program-context/question.md), [run 1831](runs/2026-10-08-1831/analysis.md))
- **Collecting further under that partial fit beat collecting the same allocation under G4, by a
  small margin resolved only on BE.** Two rounds under the updated fit against one fit to
  G4-collected tapes, 96 sources per cell per arm: 1.18× [1.01, 1.37] (BE 1.42×, PA 0.98× [0.83,
  1.16]); over keeping the first fit unresolved (1.16× [0.99, 1.36]); far below the exact-solver
  fit (0.31×). Scope: 27's training cells, three rounds; yield and tape content
  bundled. ([28](questions/10-compositional-map-transfer/28-partial-program-feedback/question.md), [run 2116](runs/2026-10-08-2116/analysis.md))

**Overall.** Solver-fitted context beyond token frequency transfers about 2× to withheld
compositions and one fresh shape; tested projections and recodings do not reproduce it. Fragment
block edits add about 1.5× over C (about 1.2× beyond C's own chain blocks). From four source
attempts per cell instead of 48 the pipeline is a third slower; one adaptive batch of four more
leaves it unresolved from full speed (a slowdown above 5% excluded) at a tenth of the acquisition.
Selection has not established a contextual gain; learned token biases transfer about 2× without
resolved family specificity. Not shown: that evolution reaches fitted context or fragments; what in
C carries its advantage; the cheap adaptive pipeline on a fresh bank; transfer beyond one shape.

## 23 Heritable variation bias (root parked, budget 2, 2 used)

[23](questions/23-heritable-variation-bias/question.md): can a token-frequency vector inherited
with each program learn a useful bias through program selection alone, and help fresh populations
once frozen? TAG threshold tasks (sum/max > 1, 5), development bank `tag-threshold-v1`.

- **Under the one procedure tested, inherited frequencies gave fresh populations no useful bias
  (the registered 1.5× gain over uniform) on their training targets.** Pre-registered, 20
  acquisitions per family × arm (σ = 0.03), each frozen vector scored on 16 seeds per
  target. Uniform ÷ inherited cost: sum 0.33× [0.21, 0.53] (inherited
  resolved worse), max 0.73× [0.50, 1.06] (a gain above 1.06× excluded, a loss up to about 2× not).
  The hand scaffold is 11.9× and 5.75× cheaper. Fairly sure for this σ, schedule and inheritance
  rule; not a verdict on self-adaptation, silent on transfer. ([run 1046](runs/2026-10-08-1046/analysis.md))
- **Persistent ancestry made the max vectors less costly than shuffled ancestry; no gain over
  uniform was established.** Broken ÷ inherited 1.58× [1.04, 2.36] on max; unresolved on sum,
  1.00× [0.69, 1.41]. Drift versus selection not isolated (no mutation-only control).
  ([log](questions/23-heritable-variation-bias/log.md))

## Older context

Background, not the current line: the original folding track (3-bond ceiling broken via Pareto
scaffold preservation; regime shift) in [docs/folding/findings.md](../docs/folding/findings.md);
pre-reframe chem-tape [findings](../docs/chem-tape/findings.md) and
[experiments](../docs/chem-tape/experiments.md); [CA](../docs/ca/experiments.md);
[coevolution](../docs/coevolution.md), [theory](../docs/theory.md) (Altenberg),
[python-rewrite-results](../docs/python-rewrite-results.md). Process:
[docs/methodology.md](../docs/methodology.md) (now light hobby mode).
