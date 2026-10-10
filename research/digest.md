# Digest: what we currently believe, and why

As of 2026-10-10, after run 2026-10-10-2214 (stopped before scoring, no new beliefs; latest evidence from commit `6dabda8`). Core question since the
2026-09-25 reframe: *how does the genotype→program map bias what evolution finds and keeps
("arrival of the frequent"), and can that bias be adapted to a task family?* History, superseded
numbers and secondary contrasts are in the questions' `log.md` files.

Sources: [notebook](../docs/map-bias/notebook.md) (§1–§32; [reviews](../docs/map-bias/reviews/))
and owner-promoted [findings](../docs/map-bias/findings.md) (items 1–17). Exploratory hobby work,
mostly 30–50 seeds per cell. Ratios are speed (> 1 = first arm faster) with 95% intervals unless
stated.

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
  ([item 17](../docs/map-bias/findings.md), §27–§28; [02](questions/01-map-bias/02-fixed-target-sampling/question.md))
- **The frequency knob changes how often a part is made, not what is reachable**: weighting one op
  switches between equivalent routes without changing solve rates; very high weights dilute.
  ([item 12](../docs/map-bias/findings.md), §16, §19)

**Fitting the bias to a threshold family** (sum/max > k, TAG, lexicase, crossover v2, L 64, P 1024;
[08](questions/01-map-bias/08-evolve-bias/question.md), [09](questions/01-map-bias/09-generic-bias-speedup/question.md)).
- **In sampling, a fitted `op_weights` vector transfers to a held-out member**: 4.9× (sum>2), 8.9×
  (max>2) more exact solvers than uniform, against 1.0× / 1.3× for the other family's fit; mainly
  the aggregator weight. One seed, one fit: numbers solid, meaning narrow. ([run 1558](runs/2026-10-05-1558/analysis.md))
- **In evolution the fitted bias is about 4× faster than uniform** (4.33× / 3.58×, lower bounds
  2.6×, 1.9×); a hand-set INPUT/GT/aggregator scaffold is within the registered 0.5–2× margin of it
  (not equality). Family specificity unresolved (1.66× / 1.80× over the other family's fit, against
  2×); sampling lift does not predict speed. Median speed, one setup. ([run 1705](runs/2026-10-05-1705/analysis.md))
- **The other family's vector gives a real generic speed-up; on max>2 INPUT/GT alone reproduces it
  within the tested margin.** Pre-registered, 250 pairs: 2.73× (sum>2), 2.02× (max>2) over uniform (lower bounds
  2.12, 1.45); INPUT/GT versus the full vector on max>2 0.90× [0.71, 1.08] (1.5× margin); sum>2
  unresolved. Initialization and mutation are coupled; no mechanism named. ([run 1814](runs/2026-10-05-1814/analysis.md))
- **On sum>2 the exact max>2 shortcut is used as a last step but is not needed** (pilot, 50 seeds):
  the solver's parent in 55/60 exposed runs; barring it delays 49/55 pairs but 100/100 still solve;
  its share of the gain is unknown (1.30, 0.71–2.32). ([run 1957](runs/2026-10-05-1957/analysis.md))

**Building blocks (chem-tape, tagged runs).** Lexicase, not a new primitive, supplies blocks;
arrangement is then the bottleneck. Tagged transplants are safe (0 crashes in 940); crossover
merges blocks when the join is cheap, but a one-op-join stack does as well, so the advantage is the
join's cost, not modularity. No valley found: joins are built by small edits (thread closed).
([items 4–16](../docs/map-bias/findings.md), §3–§26)

**Shared helpers** (three outputs on tags 0/1/2 sharing parts A and B; crossover v2, lexicase, P 1024,
L 64). Fairly sure for these layouts; nothing beyond them.
- **Retention is easy; establishment from rare is blocked by mixing between lineages.** A majority
  shared form persists and wins (270/270). From 1/32–1/10 with a selected mate it was lost in
  294/300 runs; with self as mate it won 183/240 contests (selected mate 34/240, crossover off
  75/120). (§29–§31, [06](questions/01-map-bias/06-self-mate-establishment/question.md))
- **Crossover is also what solves, but discovery needs no lineage mixing**: random starts solve
  48–50/50 with crossover, 0–4/50 without; self-mating solves 68–80% by generation 3000, about 3×
  slower than a selected mate. A helper already in the host does not rescue a rare shared form.
  (§31 G, §32 J–K; [04](questions/01-map-bias/04-random-start-discovery/question.md), [05](questions/01-map-bias/05-latent-helper/question.md))
- **Solutions arrive mostly partly shared or duplicated, and the first established form is kept**
  (121/129). Shared endings are rare (about 4–8 in 100–450 runs); shared never loses to duplicated
  as such. Shortcuts are structural: about a third of each final population fits training without being exact (9/35 runs
  still so at 256 cases). (§31 G, §32 L)
- **Why shared endings are rare is unresolved.** Exact shared children arrive (about 2 per run, all
  A-only/other); single copies drift out (0/100 established, ≤ 3.6%); no B-helper in 30M children
  (≤ 1.2e-7). 100 insertions cannot tell drift from a disadvantage.
  ([07](questions/01-map-bias/07-shared-arrival/question.md), [03](questions/01-map-bias/03-rare-shared-establishment/question.md))

## 10 Compositional map transfer (root open, budget 35, 34 used)

[10](questions/10-compositional-map-transfer/question.md): can a decoder adapted across related
tasks help fresh populations solve unseen operation combinations beyond a token-frequency bias?
Stack tape `v2_rmin(_first)`, D1331 (length-3 lists over −5..5), P 256, lexicase on 64 cases with
an exact domain check, 524k cap. G / G4: hand-set previous-token grammars (post-addition split;
four-reducer bank); "-marg": the same token marginals without context. Sub-questions 11–42 closed.
Every bank so far is a development bank. Unless stated, results are external fits frozen before
scoring.

**Banks.** Sign-gated banks could not support a symmetric two-family test; the four-reducer bank
leaves headroom above the hand-set grammars ([11](questions/10-compositional-map-transfer/11-composition-bank/question.md),
[12](questions/10-compositional-map-transfer/12-generic-grammar-headroom/question.md),
[15](questions/10-compositional-map-transfer/15-four-reducer-family-bank/question.md)). **The
comparison-gate bank gives a protected multi-holdout split with headroom**: branch-else (BE)
`A>B ? C : D+E`, post-addition (PA) `(A>B ? C : D)+E`, 13 tokens, 37 BE / 56 PA behaviours after an
exact ≤ 9-token screen (no 13-token minimality certificate); performance-blind 4 training and 4
holdouts per family; G4 solves 68% of training searches. ([24](questions/10-compositional-map-transfer/24-comparison-gate-bank/question.md), [run 1246](runs/2026-10-08-1246/analysis.md))

**Hand-set grammars** (11, 12, 15).
- **Contextual grammars beat their own token marginals on all three banks**: G/G-marg 2.6–20× (11),
  1.5–6.0× (12, 15/16 cells resolved); G4/G4-marg 4.4× [3.4, 5.6] BE, 3.3× [2.7, 4.0] PA (15). Not
  a mechanism: G also emits far more exact solvers and changes more tokens per mutation.
- **Supply overstates speed**: a token bias raises exact-solver sampling 11–82× but speed only
  1.9–3.5× (11).
- **A fixed decoder can express a family preference**: matched over swapped grammars 1.68× [1.39,
  2.05] BE, 1.32× [1.12, 1.57] PA; against G4 only BE resolved a gain. Expressivity only. (15)

**Token learning by outer-loop selection** (multipliers on the hand-set rows; 4+12 loop).
- **Learned token weights transfer about 2–2.5× to withheld cells, on both setups.** G (PA, 200
  seeds): 2.23× [1.82, 2.75] training, 2.06–2.25× (lower bounds ≥ 1.60) on two withheld cells,
  unresolved on linear (1.08× [0.72, 1.57]) ([13](questions/10-compositional-map-transfer/13-post-addition-map-learning/question.md)).
  G4: about 2.2× training, 2.0× BE and 2.5–2.6× PA withheld, all resolved ([16](questions/10-compositional-map-transfer/16-crossed-family-adaptation/question.md)).
- **That gain is mostly generic; no family advantage resolved on withheld cells.** Cross-family
  training gains 2.07×, 1.93×; all 20 maps make the same big moves. Matched over mismatched withheld
  1.02× [0.84, 1.25] BE, 0.96× [0.79, 1.15] PA; a 1.1× preference not excluded. An in-sample
  interaction (1.24× [1.09, 1.41]) hints at family information on trained cells, not separated from
  repair of G4's weak spots. (16)
- **The frozen maps help through both the starting programs and the search decoder,
  sub-additively**: given the other, decoder 1.39× / 1.28× and start 1.30× / 1.33× (withheld /
  training), both 2.29× / 2.44× (20/20 maps); not direct seeding. ([17](questions/10-compositional-map-transfer/17-decoder-initialization-variation/question.md))

**Context learned by outer-loop selection: no resolved gain from four procedures.** Training: full
552-weight learner from G 0.92× [0.78, 1.09] (13); row residuals versus continued token learning
1.00× [0.90, 1.11], withheld unresolved and not replicated (13, [14](questions/10-compositional-map-transfer/14-saved-map-shape-shift/question.md));
rank-one context steps in token continuation 0.967× [0.871, 1.073], a gain above about 1.07×
excluded for this loop and these token-tuned starts ([18](questions/10-compositional-map-transfer/18-compact-context-learning/question.md),
[19](questions/10-compositional-map-transfer/19-selection-calibrated-continuation/question.md)).
Context learned jointly from G4 is untested.

**Context fitted directly to solvers.**
- **A previous-token table (C) fitted to exact G4 solver tapes beats a token-only fit (T) to the
  same tapes, and the gain transfers.** Four-reducer bank: C/T 1.365× [1.288, 1.446] training
  (31/32 corpora), 1.293× [1.213, 1.378] withheld; matching C's pooled frequencies does not
  reproduce it (C/K 1.65×). No matched-family advantage resolved on withheld cells (BE 1.02× [0.91,
  1.15]). One bank; the carrying structure is unknown. ([20](questions/10-compositional-map-transfer/20-solver-corpus-context/question.md))
- **One feedback refit, to solvers found under C, speeds search further**: C2/C 1.404× [1.347,
  1.464] training (32/32), 1.289× [1.204, 1.381] withheld. A fresh one-shot G4 refit is not resolved
  from C (0.997×), so the gain is the collection procedure (yield, diversity and content bundled). A
  second step is untested. ([21](questions/10-compositional-map-transfer/21-iterated-solver-corpus/question.md),
  [22](questions/10-compositional-map-transfer/22-feedback-context-increment/question.md))
- **On the comparison-gate bank C/T is larger, and frozen tables keep most of it on protected
  holdouts and one fresh shape.** Training 3.11× [2.78, 3.48] (16/16; why above 1.37× unidentified);
  holdouts 2.60× [2.31, 2.92], 8/8 resolved; then-addition-v1 (`A>B ? C+D : E`, 16 cells pinned
  before any search) 2.12× [1.86, 2.41], 14/16 resolved. Shrinkage resolved across shape (0.68×
  [0.57, 0.81]), not within (0.88× [0.72, 1.07]); cause unidentified. Family matching on holdouts
  unresolved (1.10× [0.89, 1.35]). Scope: one fresh bank designed after v1 was seen, two tie-heavy
  gates. ([25](questions/10-compositional-map-transfer/25-comparison-gate-transfer/question.md),
  [26](questions/10-compositional-map-transfer/26-then-addition-fresh-bank/question.md), [run 1548](runs/2026-10-08-1548/analysis.md))
- **On then-addition, frequency projections of C and random recoding to C's mutation width do not
  reproduce its advantage**: C/K 2.48× [2.17, 2.83] (K: pooled marginals matched); C/Q 2.41× [2.11,
  2.75] (Q: matched at each of 32 positions); recoding Q's rows to C's width slowed search, R30/Q
  0.86× [0.80, 0.91]. C's conditional content and structured coupling not separated; a learned
  positional map untested. ([29](questions/10-compositional-map-transfer/29-frequency-matched-transfer/question.md),
  [30](questions/10-compositional-map-transfer/30-position-matched-replacement/question.md),
  [31](questions/10-compositional-map-transfer/31-distribution-preserving-recoding/question.md))

**Fragment block edits.** C's search unchanged; each non-elite child (p 0.2) gets one 3–6-token
block, decoded suffix kept. F: a library of 32 knockout-active windows recurring in training
solvers; B: the library's per-position marginals; W: blocks sampled from C's own chain.
- **F speeds search beyond C on comparison-gate training cells and keeps that on the excluded
  compositions tested.** F/C 1.57× [1.42, 1.75] training (leave-one-cell-out, 16/16), 1.47× [1.38,
  1.56] then-addition, 1.75× [1.57, 1.95] holdouts; F/C's change from training unresolved (0.93×
  [0.83, 1.05]), whereas C/T lost a third across the same shape. F/W 1.20–1.27× (lower bounds ≥
  1.11), but above a worthwhile 1.10× not established. Scope: the libraries are the banks' shared
  3–5-token syntax, which then-addition needs by construction: reuse of one fit across one shape
  change, not modularity, fresh-bank transfer or acquisition; changed token supply not excluded.
  ([32](questions/10-compositional-map-transfer/32-learned-fragment-operator/question.md), [runs 0843](runs/2026-10-09-0843/analysis.md), [1036](runs/2026-10-09-1036/analysis.md))
- **Library-free chain blocks (W) also beat C, without needing suffix repair; marginal blocks (B)
  showed no resolved gain.** W/C 1.23–1.38× on training, then-addition and holdouts (lower bounds ≥
  1.15). B/C 0.98× [0.93, 1.04] at ~2.8 tokens per edit, so edit size alone does not explain F's or
  W's gain. Without repair (then-addition): W/R 0.954× [0.903, 1.007] (a repair gain above 0.7%
  excluded, a cost up to about 10% not). Not isolated from W's length law or token supply. (32,
  [34](questions/10-compositional-map-transfer/34-chain-block-suffix-preservation/question.md), [run 1606](runs/2026-10-09-1606/analysis.md))
- **The same extractor on pre-solve parents (E) gave no worthwhile gain over chain blocks on
  then-addition**: E/W_E 0.981× [0.911, 1.057] (a gain above about 1.06× excluded); E/F 0.843×
  [0.795, 0.892]. E lacks F's `gt` joins (descriptive). One source selection and extractor.
  ([33](questions/10-compositional-map-transfer/33-pre-solve-fragment-source/question.md), [run 1350](runs/2026-10-09-1350/analysis.md))

**Cheap acquisition (C+F rebuilt from few sources; failures charged).**
- **Four sources per cell (C4+F4) lose about a third of full-pipeline speed on then-addition; four
  more collected under that bias (A8) leave it unresolved from full speed.** (C4+F4)/F 0.679×
  [0.614, 0.752]; F/A8 1.03× [0.95, 1.12] (an A8 slowdown above about 5% excluded); S8/A8 1.13×
  [1.04, 1.22] (S8: four more under G4; unresolved against 1.10). A8's acquisition is about a tenth
  of full F's; its estimated total cost is below S8's at every reported horizon (resolved through
  1 024 searches). One source size, one update; yield, content, decoder and library bundled.
  ([35](questions/10-compositional-map-transfer/35-small-source-acquisition/question.md),
  [36](questions/10-compositional-map-transfer/36-sparse-source-feedback/question.md), [runs 1743](runs/2026-10-09-1743/analysis.md), [2033](runs/2026-10-09-2033/analysis.md))
- **A8 was useful on a fresh output shape, then replicated from complementary sources on that
  now-development bank.** `two-sum-v1` (`A>B ? C+D : E+F`, cells pinned before any search; G4
  solved 20%): G4/A8 2.73× [2.36, 3.17]; S8/A8 1.17× [1.04, 1.33]; cost(A8)/cost(full F) 0.945×
  [0.819, 1.092] (a 1.20× loss excluded). A8's total cost is below S8's and full F's at every
  reported horizon through 4 096 searches; it repays G4 after about 47. Rebuilt from the former
  holdout cells: G4/A8′ 2.50× [2.17, 2.85], unresolved from the original builds (1.09× [0.90, 1.32]).
  One shape with familiar `+` joins, two source families.
  ([37](questions/10-compositional-map-transfer/37-cheap-bias-fresh-transfer/question.md),
  [38](questions/10-compositional-map-transfer/38-cheap-bias-source-replication/question.md), [runs 2303](runs/2026-10-09-2303/analysis.md), [0145](runs/2026-10-10-0145/analysis.md))
- **With addition inside the predicate, fresh A8 builds were about 6–10× cheaper than the weak G4
  prior on never-searched cells.** DG `(Xa+Xb)>(Xc+Xd) ? Xe:Xf` (alphabet `v2_x4`, D625; 24 builds
  from four sparse sources). Eight protected cells: cost(G4)/cost(A8″) 10.1× [7.6, 13.1] at 2 × cap,
  6.4× [5.0, 8.0] at 1 × cap (margin 1.5×); solved 317/384 vs 63/384; 8 further cells 8.2× [6.0,
  11.1]. Capped cost against a weak prior; one bank; context, fragments and supply bundled.
  ([39](questions/10-compositional-map-transfer/39-independent-input-family-bank/question.md), [40](questions/10-compositional-map-transfer/40-independent-input-protected-transfer/question.md), [run 1536](runs/2026-10-10-1536/analysis.md))
- **On that alphabet, DG-acquired builds were about 3× cheaper on unseen DG cells than builds
  acquired on a branch-sum family; the reverse is unresolved.** TS `Xa>Xb ? Xc+Xd : Xe+Xf`, 24 builds
  and 8 never-searched cells per family. DG cells: TS-built ÷ DG-built cost 2.98× [2.07, 4.33] at
  2 × cap, 2.40× [1.76, 3.30] at 1 × cap, 8/8 cells. TS cells: 1.29× [0.94, 1.78] the other way
  (reciprocity not established). Every cohort beat G4 on both rosters (lowest 2.75×). Join content
  versus learning on much harder sources (G4 first batch 17% vs 63%) not separated. One family pair,
  capped cost. ([41](questions/10-compositional-map-transfer/41-same-alphabet-family-preference/question.md), [run 1717](runs/2026-10-10-1717/analysis.md))
- **Both components carry that DG advantage: the DG table alone shows it, and the DG library also
  speeds a TS-built table.** Saved builds crossed table × library (24 donor pairs, fresh seeds, 8 DG
  cells, 2 × cap): without libraries the DG table is 3.26× [2.43, 4.30] cheaper than the TS table
  (fresh native gap 3.03×); on the TS table the DG library beats no library 3.05× [2.32, 4.07] and
  the TS library 1.95× [1.43, 2.66] (unresolved against 1.5×); that hybrid stays 1.55× [1.15, 2.09]
  behind the native DG pair. No library was shown to need its own table (DG over TS library on the DG
  table 1.35× [1.10, 1.68]); on TS cells no library difference was resolved (1.01× [0.83, 1.25]: a
  loss above 1.25× excluded, equality not shown). One family pair; library content versus size not
  separated; point estimates only for which component is larger.
  ([42](questions/10-compositional-map-transfer/42-family-bias-component-transfer/question.md), [run 2001](runs/2026-10-10-2001/analysis.md))

**Context fitted to non-solving programs.** On comparison-gate training cells, a context fit to
tapes from G4 searches that had not yet solved beat a token fit to the same tapes 1.28× [1.12, 1.45]
and G4 1.62× [1.37, 1.90], mostly by more runs solving within the cap; the exact-solver fit stays
3.7× faster for about 7.9× more source evaluations. Two further rounds under the updated fit beat
equal G4 collection 1.18× [1.01, 1.37], resolved only on BE. Own training cells, one horizon.
([27](questions/10-compositional-map-transfer/27-partial-program-context/question.md),
[28](questions/10-compositional-map-transfer/28-partial-program-feedback/question.md))

**Overall.** Solver-fitted context beyond token frequency transfers about 2× to withheld
compositions and one fresh shape; fragment blocks add about 1.5× over it. Selection has not
established a contextual gain; learned token biases transfer about 2× without resolved family
specificity. A8 costs a tenth of full-F acquisition on the original sources, unresolved from full speed there; on one
predicate-addition family it is 6–10× cheaper than G4 and about 3× cheaper than branch-sum-acquired
builds (reverse unresolved), carried by both table and library. Not shown: that evolution reaches
fitted context or fragments; what carries C's advantage over token fits; why the DG components are
better (content, size or source difficulty); A8 on a fresh bank of a new family, against a strong
baseline (a subtree-GP comparison, 43, stopped before scoring), or from arbitrary sources; transfer beyond two fresh shapes.

## 23 Heritable variation bias (root parked, budget 2, 2 used)

[23](questions/23-heritable-variation-bias/question.md): can a token-frequency vector inherited
with each program learn a useful bias through program selection alone, and help fresh populations
once frozen? TAG threshold tasks (sum/max > 1, 5), development bank `tag-threshold-v1`.

- **Under the one procedure tested, inherited frequencies gave fresh populations no useful bias
  (the registered 1.5× gain over uniform) on their training targets.** Pre-registered, 20 acquisitions per family ×
  arm (σ = 0.03), each frozen vector scored on 16 seeds per target. Uniform ÷ inherited cost: sum
  0.33× [0.21, 0.53] (inherited resolved worse), max 0.73× [0.50, 1.06] (a gain above 1.06×
  excluded, a loss up to 2× not); the hand scaffold is 11.9× and 5.75× cheaper. Fairly sure for this
  σ, schedule and inheritance rule; not a verdict on self-adaptation, silent on transfer.
  ([run 1046](runs/2026-10-08-1046/analysis.md))
- **Persistent ancestry made the max vectors less costly than shuffled ancestry; no gain over
  uniform was established.** Broken ÷ inherited 1.58× [1.04, 2.36] on max; unresolved on sum, 1.00×
  [0.69, 1.41]. Drift versus selection not isolated (no mutation-only control).
  ([log](questions/23-heritable-variation-bias/log.md))

## Older context

Background, not the current line: original folding track ([findings](../docs/folding/findings.md):
3-bond ceiling broken via Pareto scaffold preservation; regime shift); pre-reframe chem-tape
[findings](../docs/chem-tape/findings.md), [experiments](../docs/chem-tape/experiments.md);
[CA](../docs/ca/experiments.md); [coevolution](../docs/coevolution.md); [theory](../docs/theory.md)
(Altenberg); [python-rewrite-results](../docs/python-rewrite-results.md). Process:
[methodology](../docs/methodology.md) (light hobby mode).
