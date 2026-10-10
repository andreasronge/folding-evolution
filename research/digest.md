# Digest: what we currently believe, and why

As of 2026-10-10, after run 2026-10-10-1536 (commit `7244fa1`). Core question since the
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
  mainly the aggregator weight. One seed, one fit: numbers solid, meaning narrow.
  ([08](questions/01-map-bias/08-evolve-bias/question.md), [run 1558](runs/2026-10-05-1558/analysis.md))
- **In evolution the fitted bias is about 4× faster than uniform** (4.33× / 3.58×, lower bounds
  2.6×, 1.9×); a hand-set INPUT/GT/aggregator scaffold is within the registered 0.5–2× margin of it
  (not equality). Family specificity unresolved (1.66× / 1.80× over the other family's fit, against
  a 2× bar); sampling lift does not predict speed. Median speed, one setup.
  ([08](questions/01-map-bias/08-evolve-bias/question.md), [run 1705](runs/2026-10-05-1705/analysis.md))
- **The other family's vector gives a real generic speed-up; on max>2 INPUT/GT alone reproduces it
  within the tested margin.** Pre-registered, 250 pairs: 2.73× (sum>2), 2.02× (max>2) over uniform
  (lower bounds 2.12, 1.45); INPUT/GT versus the full vector on max>2 0.90× [0.71, 1.08] (1.5×
  margin); on sum>2 neither part is resolved. Initialization and mutation are coupled, so no
  mechanism is named.
  ([09](questions/01-map-bias/09-generic-bias-speedup/question.md), [run 1814](runs/2026-10-05-1814/analysis.md))
- **On sum>2 the exact max>2 shortcut is used as a last step but is not needed** (pilot, 50 seeds):
  the solver's parent in 55/60 exposed runs; barring it delays 49/55 pairs but 100/100 still solve;
  its share of the gain is unknown (1.30, 0.71–2.32).
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

## 10 Compositional map transfer (root open, 32 of 32 used)

[10](questions/10-compositional-map-transfer/question.md): can a decoder adapted across related
tasks help fresh populations solve unseen operation combinations beyond a token-frequency bias?
Stack tape `v2_rmin(_first)`, D1331 (length-3 lists over −5..5; only 11's first bank used length-4
lists), P 256, lexicase on 64 cases with an exact domain check, 524k cap. G / G4: hand-set
previous-token grammars (post-addition split; four-reducer bank); "-marg": the same token
marginals without context. Sub-questions 11–40 closed. Every bank, including then-addition-v1 (26),
two-sum-v1 (37) and x4-double-gate-v1 (39–40), is now a development bank.

**Banks.** Sign-gated banks could not support a symmetric two-family test (these shapes and rules;
[11](questions/10-compositional-map-transfer/11-composition-bank/question.md),
[12](questions/10-compositional-map-transfer/12-generic-grammar-headroom/question.md),
[15](questions/10-compositional-map-transfer/15-four-reducer-family-bank/question.md)); the
four-reducer bank's ten-token branch cells leave headroom above the hand-set grammars.
**The comparison-gate bank gives a protected multi-holdout split with headroom**: branch-else
(BE) `A>B ? C : D+E`, post-addition (PA) `(A>B ? C : D)+E`, 13 tokens, 37 BE and 56 PA behaviours
after an exact ≤ 9-token screen (no 13-token minimality certificate); frozen, performance-blind
4 training and 4 holdouts per family; G4 solves 68% of training-cell searches.
([24](questions/10-compositional-map-transfer/24-comparison-gate-bank/question.md), [run 1246](runs/2026-10-08-1246/analysis.md))

**Hand-set context and supply.**
- **Contextual grammars beat their own token marginals on all three banks**: G/G-marg 2.6–20× (11)
  and 1.5–6.0× (12, 15/16 cells resolved); G4/G4-marg 4.4× [3.4, 5.6] BE, 3.3× [2.7, 4.0] PA (15).
  Not a mechanism: G also emits far more exact solvers and changes more tokens per mutation.
- **Supply overstates speed**: a token bias raises exact-solver sampling 11–82× but speed only
  1.9–3.5× (11).
- **A fixed decoder can express a family preference**: matched over swapped family grammars
  1.68× [1.39, 2.05] (BE), 1.32× [1.12, 1.57] (PA); against G4 only the BE grammar resolved a gain
  for its family. Expressivity only. (15)

**Token learning by outer-loop selection** (multipliers on the hand-set rows; 4+12 loop).
- **Learned token weights transfer about 2–2.5× to withheld cells, on both setups.** G (PA, 200
  seeds): 2.23× [1.82, 2.75] training, 2.06–2.25× (lower bounds ≥ 1.60) on two withheld cells,
  unresolved on linear (1.08× [0.72, 1.57])
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
  training cells (confounded with shape and difficulty).
  ([17](questions/10-compositional-map-transfer/17-decoder-initialization-variation/question.md))

**Context learned by outer-loop selection: no resolved gain from four procedures.** On training:
full 552-weight learner from G 0.92× [0.78, 1.09] (13); row residuals versus continued token
learning 1.00× [0.90, 1.11], withheld unresolved and not replicated
(13, [14](questions/10-compositional-map-transfer/14-saved-map-shape-shift/question.md)); rank-one
context steps in token continuation C/T 0.967× [0.871, 1.073], a gain above about 1.07× excluded
for this loop and these token-tuned starts
([18](questions/10-compositional-map-transfer/18-compact-context-learning/question.md),
[19](questions/10-compositional-map-transfer/19-selection-calibrated-continuation/question.md)).
Context learned jointly from G4 is untested.

**Context fitted directly to solvers (external fitting, not selection).**
- **A previous-token table (C) fitted to exact G4 solver tapes beats a token-only fit (T) to the
  same tapes, and the gain transfers.** Four-reducer bank: C/T 1.365× [1.288, 1.446] training
  (31/32 corpora), 1.293× [1.213, 1.378] withheld; matching C's pooled frequencies does not
  reproduce it (C/K 1.65×). No matched-family advantage resolved on withheld cells (BE 1.02× [0.91,
  1.15]; specificity not refuted). One bank, split and shrinkage; the carrying structure is unknown.
  ([20](questions/10-compositional-map-transfer/20-solver-corpus-context/question.md))
- **One feedback refit, to solvers found under C, speeds search further.** C2/C 1.404× [1.347,
  1.464] training (32/32 lineages), 1.289× [1.204, 1.381] withheld; a fresh one-shot G4 refit is
  not resolved from C (0.997×), so the gain is the collection procedure (yield, diversity and tape
  content bundled). It raised C/T on training (1.17× [1.09, 1.25]; withheld unresolved). A second
  step is untested.
  ([21](questions/10-compositional-map-transfer/21-iterated-solver-corpus/question.md),
  [22](questions/10-compositional-map-transfer/22-feedback-context-increment/question.md))
- **On the comparison-gate bank C/T is larger (training 3.11× [2.78, 3.48], 16/16 corpora; why it
  exceeds 1.37× is unidentified), and frozen tables keep most of it on protected holdouts and one
  fresh shape, shrunk from training.** No refit. Holdouts 2.60× [2.31, 2.92], 8/8 resolved;
  then-addition-v1 (`A>B ? C+D : E`, 16 cells pinned before any search) 2.12× [1.86, 2.41], 14/16
  cells resolved. Shrinkage resolved across shape (0.68× [0.57, 0.81]), not within (0.88× [0.72,
  1.07]); cause unidentified. Family matching on holdouts unresolved (1.10× [0.89, 1.35]). Scope:
  one fresh bank designed after v1 was seen, two tie-heavy gates, these 16 cells.
  ([24](questions/10-compositional-map-transfer/24-comparison-gate-bank/question.md),
  [25](questions/10-compositional-map-transfer/25-comparison-gate-transfer/question.md),
  [26](questions/10-compositional-map-transfer/26-then-addition-fresh-bank/question.md), [run 1548](runs/2026-10-08-1548/analysis.md))
- **On then-addition, frozen frequency projections of C do not reproduce its advantage, nor does
  random recoding to C's mutation width.** C/K 2.48× [2.17, 2.83] (K: G4 multipliers matched to
  C's pooled marginals); C/Q 2.41× [2.11, 2.75] (Q: matched at each of 32 positions). Recoding Q's
  rows at a fixed random-program distribution to C's width slowed search:
  R30/Q 0.86× [0.80, 0.91]. Scope: one operator set, two recodings; C's
  conditional content and structured coupling not separated; a learned positional map untested.
  ([29](questions/10-compositional-map-transfer/29-frequency-matched-transfer/question.md),
  [30](questions/10-compositional-map-transfer/30-position-matched-replacement/question.md),
  [31](questions/10-compositional-map-transfer/31-distribution-preserving-recoding/question.md))

**Learned fragments as block edits (external fitting; development banks).** C's search unchanged;
each non-elite child (p 0.2) gets one 3–6-token block, decoded suffix kept. F: a library of 32
knockout-active windows recurring in the training solvers; controls B (the library's per-position
marginals) and W (blocks sampled from C's own chain), same length and start laws.
- **F speeds search beyond C on the comparison-gate training cells.** Leave-one-cell-out, 16
  corpora: F/C 1.57× [1.42, 1.75] (16/16), F/B 1.60× [1.45, 1.77], F/W 1.23× [1.12, 1.36].
  ([32](questions/10-compositional-map-transfer/32-learned-fragment-operator/question.md), [run 0843](runs/2026-10-09-0843/analysis.md))
- **Frozen whole-corpus libraries keep that advantage on the excluded compositions tested.**
  Then-addition F/C 1.47× [1.38, 1.56] (16/16), F/W 1.20× [1.11, 1.29]; holdouts F/C 1.75× [1.57,
  1.95], F/W 1.27× [1.17, 1.38]. F/C's change from training is unresolved (0.93× [0.83, 1.05]),
  whereas C/T lost a third across the same shape. F/W above a worthwhile 1.10× is not established
  (5/16 cells resolved). Scope: the libraries are the banks' shared 3–5-token syntax, which
  then-addition needs by construction: reuse of one external fit across one shape change, not
  modularity, fresh-bank transfer or acquisition; changed token supply not excluded.
  (32, [run 1036](runs/2026-10-09-1036/analysis.md))
- **Library-free chain blocks (W) also beat C; marginal blocks (B) showed no resolved gain.** W/C
  1.28× [1.17, 1.39] training, 1.23× [1.15, 1.31] then-addition, 1.38× [1.23, 1.56] holdouts; B/C
  0.98× [0.93, 1.04] on training (a gain above 1.04× excluded, a small loss not) at ~2.8 tokens
  changed per edit, so edit size alone does not explain F's or W's gain. (32)
- **W's suffix repair is not needed for its gain on then-addition at this resolution.** The same
  blocks without repair (R), paired: W/R 0.954× [0.903, 1.007] (a repair gain above 0.7% excluded,
  a cost up to about 10% not); R/C 1.286× [1.208, 1.370]. Not isolated from W's length law or
  token supply; full C only.
  ([34](questions/10-compositional-map-transfer/34-chain-block-suffix-preservation/question.md), [run 1606](runs/2026-10-09-1606/analysis.md))
- **The same extractor applied to pre-solve parents (E) gave no worthwhile gain over chain blocks
  on then-addition.** E/W_E 0.981× [0.911, 1.057] (W_E: chain blocks with E's length law; a gain
  above about 1.06× excluded, a small gain or loss not); E/F 0.843× [0.795, 0.892], 0/16 corpora.
  E lacks F's `gt` comparison joins (descriptive; untested as F's carrier). Scope: one source
  selection and extractor, C still fitted from exact solvers.
  ([33](questions/10-compositional-map-transfer/33-pre-solve-fragment-source/question.md), [run 1350](runs/2026-10-09-1350/analysis.md))

**Cheap acquisition (C+F rebuilt from few sources; failures charged).**
- **Four source attempts per cell (C4+F4) lose about a third of the full pipeline's speed on
  then-addition; four more attempts collected under that cheap bias (A8) leave it unresolved from
  full speed.** (C4+F4)/F 0.679× [0.614, 0.752] (16/16). Four more attempts under C4+F4 (A8)
  rather than G4 (S8), then refit: S8/A8 1.13× [1.04, 1.22] (unresolved against 1.10); full F/A8
  1.03× [0.95, 1.12] (an A8 slowdown above about 5% excluded, a gain of about 10% not). A8's
  acquisition is about a tenth of full F's; its estimated total cost is below S8's at every
  reported horizon, resolved through 1 024 searches. Scope: development sources and bank, one
  source size, one update; yield, content, decoder and library bundled.
  ([35](questions/10-compositional-map-transfer/35-small-source-acquisition/question.md),
  [36](questions/10-compositional-map-transfer/36-sparse-source-feedback/question.md),
  [run 1743](runs/2026-10-09-1743/analysis.md), [run 2033](runs/2026-10-09-2033/analysis.md))
- **On one fresh bank frozen A8 was not materially slower than the frozen full pipeline, and every
  fitted arm stayed useful.** `two-sum-v1` (`A>B ? C+D : E+F`, 16 cells pinned before any search,
  4 seeds per cell; G4 solved 20%, 63% on then-addition): cost(A8)/cost(full F) 0.945× [0.819,
  1.092] (a 1.20× loss excluded; a 9% loss or an 18% gain not); G4/A8 2.73× [2.36, 3.17], G4/full
  F 2.58× [2.28, 2.90]; S8/A8 1.17× [1.04, 1.33]. With acquisition charged, A8's estimated total
  cost is below S8's and full F's at every reported horizon through 4 096 searches; it repays G4
  after about 47 searches in evaluations. Scope: one output shape with familiar `+` joins;
  existing acquisitions; addition in the predicate untested.
  ([37](questions/10-compositional-map-transfer/37-cheap-bias-fresh-transfer/question.md), [run 2303](runs/2026-10-09-2303/analysis.md))
- **The unchanged A8 recipe, rebuilt from a different source roster, again gave a clearly useful
  frozen bias; whether it matches the original builds is unresolved.** Sixteen fresh builds from
  the four former holdout cells per family, on `two-sum-v1`: cost(G4)/cost(A8′) 2.50× [2.17, 2.85]
  (pre-set margin 1.5×; BE 3.14×, PA 1.99× [1.66, 2.32]). Against the historical A8
  builds on identical keys, cost 1.09× [0.90, 1.32] (PA weaker, cause unplaced: the static arm went
  unscored). Acquisition 4.5 M evaluations, repaying G4 after about 35 searches in evaluations.
  Scope: one alternative roster in the same two families; development data on both sides.
  ([38](questions/10-compositional-map-transfer/38-cheap-bias-source-replication/question.md), [run 0145](runs/2026-10-10-0145/analysis.md))
- **On one family with addition inside the predicate, fresh A8 builds were about 6–10× cheaper than
  the weak G4 prior on its eight protected cells.** `(Xa+Xb)>(Xc+Xd) ? Xe:Xf` over four independent
  readouts (alphabet `v2_x4`, D625); 24 builds from four sparse sources (first batch 64/384 solved).
  cost(G4)/cost(A8″) 10.1× [7.6, 13.1] with failures at 2 × cap, 6.4× [5.0, 8.0] at 1 × cap (margin
  1.5×); solved 317/384 against 63/384; every build above 1.5× at 2 × cap; three cells with a predicate
  pairing no source has 6.8× [4.9, 9.2] (descriptive). Reinterpreted old-family builds were clearly
  weaker (O/A8″ 4.3× [2.7, 6.6]; token reinterpretation, so not a specificity test). Scope: capped-cost
  ratio (321/384 G4 capped); within-bank protected cells, not a fresh bank; alphabet, domain and
  predicate placement changed together; context, fragments and supply bundled.
  ([39](questions/10-compositional-map-transfer/39-independent-input-family-bank/question.md),
  [40](questions/10-compositional-map-transfer/40-independent-input-protected-transfer/question.md), [run 1536](runs/2026-10-10-1536/analysis.md))

**Context fitted to non-solving programs (external fitting, before any exact solve).** On the
comparison-gate training cells, a context fit to tapes from G4 searches that had not yet solved beat
a token fit to the same tapes 1.28× [1.12, 1.45] and G4 1.62× [1.37, 1.90], mostly by more runs
solving within the cap; the exact-solver fit stays 3.7× faster for about 7.9× more source
evaluations. Two further collection rounds under the updated fit beat equal G4 collection 1.18×
[1.01, 1.37], resolved only on BE. Scope: own training cells, one horizon.
([27](questions/10-compositional-map-transfer/27-partial-program-context/question.md),
[28](questions/10-compositional-map-transfer/28-partial-program-feedback/question.md))

**Overall.** Solver-fitted context beyond token frequency transfers about 2× to withheld
compositions and one fresh shape; tested projections and recodings do not reproduce it. Fragment
block edits add about 1.5× over C. The cheap A8 recipe (a tenth of the acquisition) is unresolved
from full speed, about 2.5× faster than G4 when rebuilt from another roster, and 6–10× cheaper in
capped cost than G4 on protected cells of one predicate-addition family. Selection has not established a contextual gain;
learned token biases transfer about 2× without resolved family specificity. Not shown: that
evolution reaches fitted context or fragments; what in C or A8 carries the advantage; whether A8
builds are family-specific; A8 on a fresh bank of a new family, against a strong baseline, or from
arbitrary sources; transfer beyond two fresh output shapes.

## 23 Heritable variation bias (root parked, budget 2, 2 used)

[23](questions/23-heritable-variation-bias/question.md): can a token-frequency vector inherited
with each program learn a useful bias through program selection alone, and help fresh populations
once frozen? TAG threshold tasks (sum/max > 1, 5), development bank `tag-threshold-v1`.

- **Under the one procedure tested, inherited frequencies gave fresh populations no useful bias
  (the registered 1.5× gain over uniform) on their training targets.** Pre-registered, 20
  acquisitions per family × arm (σ = 0.03), each frozen vector scored on 16 seeds per target.
  Uniform ÷ inherited cost: sum 0.33× [0.21, 0.53] (inherited resolved worse), max 0.73× [0.50,
  1.06] (a gain above 1.06× excluded, a loss up to about 2× not). The hand scaffold is 11.9× and
  5.75× cheaper. Fairly sure for this σ, schedule and inheritance rule; not a verdict on
  self-adaptation, silent on transfer. ([run 1046](runs/2026-10-08-1046/analysis.md))
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
