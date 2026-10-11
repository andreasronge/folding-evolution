# Digest: what we currently believe, and why

As of 2026-10-11, after run 2026-10-11-1228 (uncapped semantic library on order-helper cells; commit
`60ab766`).
Core question since the 2026-09-25 reframe: *how does the genotype→program map bias what evolution
finds and keeps ("arrival of the frequent"), and can that bias be adapted to a task family?*
History, superseded numbers and secondary contrasts are in the questions' `log.md` files.

Sources: [notebook](../docs/map-bias/notebook.md) (§1–§32; [reviews](../docs/map-bias/reviews/))
and owner-promoted [findings](../docs/map-bias/findings.md) (items 1–17). Exploratory hobby work,
mostly 30–50 seeds per cell. Ratios are speed (> 1 = first arm faster) with 95% intervals unless
stated.

## 01 Map bias (root open, budget spent)

[01](questions/01-map-bias/question.md). Chem-tape and TAG alphabets, threshold and fixed-target
tasks. 03, 05, 06 closed; 02, 04, 07, 08, 09 parked.

**Measuring the bias.**
- **Random-genotype frequency predicts which tasks are easy, not which hard ones get solved.**
  Evolution routinely finds behaviours rarer than 1 in 50M random tapes; on chem-tape, chem decoder
  and direct encoding have almost the same bias. ([item 1](../docs/map-bias/findings.md), §1)
- **Folding's fixed-target advantage over direct encoding looks like sampling**: where the maps
  differ, folding makes exact solvers 1.3–30× more common and solves more often; evolution was
  mostly a worse sampler than random search. Not general: on TAG threshold tasks with lexicase
  every arm solved 9–40× sooner than computed random search. Steering untested.
  ([item 17](../docs/map-bias/findings.md), §27–§28; [02](questions/01-map-bias/02-fixed-target-sampling/question.md))
- **The frequency knob changes how often a part is made, not what is reachable**: weighting one op
  switches between equivalent routes without changing solve rates; very high weights dilute.
  ([item 12](../docs/map-bias/findings.md), §16, §19)

**Fitting the bias to a threshold family** (sum/max > k, TAG, lexicase, crossover v2, L 64, P 1024;
one setup, median speed; [08](questions/01-map-bias/08-evolve-bias/question.md), [09](questions/01-map-bias/09-generic-bias-speedup/question.md)).
- **A fitted `op_weights` vector transfers to a held-out member, about 4× faster than uniform in
  evolution.** Sampling: 4.9× (sum>2), 8.9× (max>2) more exact solvers than uniform (other family's fit
  1.0× / 1.3×), mainly via the aggregator weight (one seed, one fit; [run 1558](runs/2026-10-05-1558/analysis.md)).
  Evolution: 4.33× / 3.58× (lower bounds 2.6×, 1.9×); a hand-set INPUT/GT/aggregator scaffold is
  within the registered 0.5–2× margin of it (not equality); family specificity unresolved (1.66× /
  1.80× over the other family's fit, against 2×); sampling lift does not predict speed ([run 1705](runs/2026-10-05-1705/analysis.md)).
- **Most of that gain is generic; on max>2 INPUT/GT alone reproduces it within the tested margin.**
  Pre-registered, 250 pairs: the other family's vector 2.73× (sum>2), 2.02× (max>2) over uniform
  (lower bounds 2.12, 1.45); INPUT/GT versus the full vector on max>2 0.90× [0.71, 1.08] (1.5× margin);
  sum>2 unresolved. Initialization and mutation coupled; no mechanism named ([run 1814](runs/2026-10-05-1814/analysis.md)).
  On sum>2 the exact max>2 shortcut is used as a last step but not needed (pilot: barred, 100/100
  still solve; its share of the gain unknown; [run 1957](runs/2026-10-05-1957/analysis.md)).

**Building blocks (chem-tape, tagged runs).** Lexicase, not a new primitive, supplies blocks;
arrangement is then the bottleneck. Tagged transplants are safe (0 crashes in 940); crossover
merges blocks when the join is cheap, but a one-op-join stack does as well, so the advantage is the
join's cost, not modularity. No valley found: joins are built by small edits (thread closed).
([items 4–16](../docs/map-bias/findings.md), §3–§26)

**Shared helpers** (three outputs on tags 0/1/2 sharing parts A and B; crossover v2, lexicase, P 1024,
L 64). Fairly sure for these layouts; nothing beyond them.
- **Retention is easy; establishment from rare is blocked by mixing between lineages.** A majority
  shared form persists and wins (270/270). From 1/32–1/10 it was lost in 294/300 runs with a
  selected mate; with self as mate it won 183/240 contests (selected mate 34/240).
  (§29–§31, [06](questions/01-map-bias/06-self-mate-establishment/question.md))
- **Crossover is also what solves, but discovery needs no lineage mixing**: random starts solve
  48–50/50 with crossover, 0–4/50 without; self-mating solves 68–80%, about 3× slower than a
  selected mate. A helper already in the host does not rescue a rare shared form.
  (§31 G, §32 J–K; [04](questions/01-map-bias/04-random-start-discovery/question.md), [05](questions/01-map-bias/05-latent-helper/question.md))
- **Solutions arrive mostly partly shared or duplicated, and the first established form is kept**
  (121/129). Shared endings are rare (about 4–8 in 100–450 runs) but never lose to duplicated as
  such. About a third of each final population fits training without being exact. (§31 G, §32 L)
- **Why shared endings are rare is unresolved.** Exact shared children arrive (about 2 per run);
  single copies drift out (0/100, ≤ 3.6%); no B-helper in 30M children (≤ 1.2e-7). 100 insertions
  cannot tell drift from a disadvantage.
  ([07](questions/01-map-bias/07-shared-arrival/question.md), [03](questions/01-map-bias/03-rare-shared-establishment/question.md))

## 10 Compositional map transfer (root open, budget 44, 44 used)

[10](questions/10-compositional-map-transfer/question.md): can a decoder adapted across related
tasks help fresh populations solve unseen operation combinations beyond a token-frequency bias?
Stack tape `v2_rmin(_first)`, D1331 (length-3 lists over −5..5), P 256, lexicase on 64 cases with
an exact domain check, 524k cap. G / G4: hand-set previous-token grammars (post-addition split;
four-reducer bank); "-marg": same token marginals without context. Sub-questions 11–49 and 51–53 closed; 50 parked.
All banks are development banks; unless stated, fits are external and frozen before scoring.

**Banks.** Sign-gated banks could not support a symmetric two-family test; the four-reducer bank
has headroom above the hand-set grammars ([11](questions/10-compositional-map-transfer/11-composition-bank/question.md),
[12](questions/10-compositional-map-transfer/12-generic-grammar-headroom/question.md),
[15](questions/10-compositional-map-transfer/15-four-reducer-family-bank/question.md)). The
comparison-gate bank gives a protected multi-holdout split with headroom: branch-else (BE)
`A>B ? C : D+E`, post-addition (PA) `(A>B ? C : D)+E`, 13 tokens, performance-blind 4 training and 4 holdouts per family; G4 solves 68% of training searches. ([24](questions/10-compositional-map-transfer/24-comparison-gate-bank/question.md), [run 1246](runs/2026-10-08-1246/analysis.md))

**Hand-set grammars** (11, 12, 15).
- **Contextual grammars beat their own token marginals on all three banks**: G/G-marg 1.5–20× (11,
  12); G4/G4-marg 4.4× [3.4, 5.6] BE, 3.3× [2.7, 4.0] PA (15). Not a mechanism: G also emits far more
  exact solvers (11–82×, for 1.9–3.5× speed) and changes more tokens per mutation (11).
- **A fixed decoder can express a family preference**: matched over swapped grammars 1.68× [1.39,
  2.05] BE, 1.32× [1.12, 1.57] PA; only BE resolved a gain over G4. Expressivity only. (15)

**Learned by outer-loop selection** (4+12 loop).
- **Learned token weights transfer about 2–2.5× to withheld cells, mostly generically.** G (PA):
  2.06–2.25× on two withheld cells (lower bounds ≥ 1.60), unresolved on linear (1.08× [0.72, 1.57])
  ([13](questions/10-compositional-map-transfer/13-post-addition-map-learning/question.md)). G4: 2.0×
  BE, 2.5–2.6× PA withheld; matched over mismatched withheld 1.02× [0.84, 1.25] BE, 0.96× [0.79,
  1.15] PA (a 1.1× preference not excluded)
  ([16](questions/10-compositional-map-transfer/16-crossed-family-adaptation/question.md)).
- **The frozen maps help through both the starting programs and the search decoder,
  sub-additively**: given the other, decoder 1.39× / 1.28× and start 1.30× / 1.33× (withheld /
  training), both 2.29× / 2.44×; not direct seeding. ([17](questions/10-compositional-map-transfer/17-decoder-initialization-variation/question.md))
- **Learned context: no resolved gain from four procedures.** Full learner from G 0.92× [0.78, 1.09]
  (13); row residuals 1.00× [0.90, 1.11] ([14](questions/10-compositional-map-transfer/14-saved-map-shape-shift/question.md));
  rank-one steps 0.967× [0.871, 1.073], above about 1.07× excluded for this loop and these
  token-tuned starts ([18](questions/10-compositional-map-transfer/18-compact-context-learning/question.md),
  [19](questions/10-compositional-map-transfer/19-selection-calibrated-continuation/question.md)).
  Context learned jointly from G4 untested.

**Context fitted directly to solvers.**
- **A previous-token table (C) fitted to exact G4 solver tapes beats a token-only fit (T) to the
  same tapes, and the gain transfers.** Four-reducer bank: C/T 1.365× [1.288, 1.446] training,
  1.293× [1.213, 1.378] withheld; matching C's pooled frequencies does not reproduce it (C/K
  1.65×); no matched-family advantage resolved on withheld cells (BE 1.02× [0.91, 1.15]). One
  bank; carrying structure unknown.
  ([20](questions/10-compositional-map-transfer/20-solver-corpus-context/question.md))
- **One feedback refit, to solvers found under C, speeds search further**: C2/C 1.404× [1.347,
  1.464] training, 1.289× [1.204, 1.381] withheld; a fresh one-shot G4 refit is not resolved from C
  (0.997×), so the gain is the collection procedure (yield, diversity, content bundled).
  ([21](questions/10-compositional-map-transfer/21-iterated-solver-corpus/question.md),
  [22](questions/10-compositional-map-transfer/22-feedback-context-increment/question.md))
- **On the comparison-gate bank C/T is larger, and frozen tables keep most of it on protected
  holdouts and one fresh shape.** Training 3.11× [2.78, 3.48] (why above 1.37× unidentified); holdouts 2.60× [2.31, 2.92];
  then-addition-v1 (`A>B ? C+D : E`, cells pinned before any search) 2.12× [1.86, 2.41]; shrinkage
  resolved across shape (0.68× [0.57, 0.81]), not within; cause unidentified. Holdout family matching unresolved
  (1.10× [0.89, 1.35]). One fresh bank, designed after v1 was seen; two tie-heavy gates.
  ([25](questions/10-compositional-map-transfer/25-comparison-gate-transfer/question.md),
  [26](questions/10-compositional-map-transfer/26-then-addition-fresh-bank/question.md), [run 1548](runs/2026-10-08-1548/analysis.md))
- **On then-addition, frequency projections of C and random recoding to its mutation width do not
  reproduce its advantage**: C/K 2.48× [2.17, 2.83] (pooled marginals matched); C/Q 2.41× [2.11,
  2.75] (matched at each of 32 positions); Q recoded to C's width 0.86× [0.80, 0.91]. Conditional
  content versus structured coupling not separated.
  ([29](questions/10-compositional-map-transfer/29-frequency-matched-transfer/question.md),
  [30](questions/10-compositional-map-transfer/30-position-matched-replacement/question.md),
  [31](questions/10-compositional-map-transfer/31-distribution-preserving-recoding/question.md))
- **Context fitted to non-solving programs helps less.** On comparison-gate training cells it beat a
  token fit to the same tapes 1.28× [1.12, 1.45] and G4 1.62× [1.37, 1.90]; the exact-solver fit is
  3.7× faster for about 7.9× more source evaluations. Two feedback rounds beat equal G4 collection
  1.18× [1.01, 1.37], resolved only on BE. Own training cells, one horizon.
  ([27](questions/10-compositional-map-transfer/27-partial-program-context/question.md),
  [28](questions/10-compositional-map-transfer/28-partial-program-feedback/question.md))

**Fragment block edits.** C's search unchanged; each non-elite child (p 0.2) gets one 3–6-token
block, decoded suffix kept. F: 32 knockout-active windows recurring in training solvers; B: their
per-position marginals; W: blocks sampled from C's own chain.
- **F speeds search beyond C and keeps that on the excluded compositions tested.** F/C 1.57× [1.42,
  1.75] training (leave-one-cell-out), 1.47× [1.38, 1.56] then-addition, 1.75× [1.57, 1.95]
  holdouts; change from training unresolved (0.93× [0.83, 1.05]). F/W 1.20–1.27× (lower bounds
  ≥ 1.11; above 1.10× not established). The libraries are the banks' shared 3–5-token syntax, which
  then-addition needs: reuse across one shape change, not modularity or acquisition; changed token
  supply not excluded.
  ([32](questions/10-compositional-map-transfer/32-learned-fragment-operator/question.md), [runs 0843](runs/2026-10-09-0843/analysis.md), [1036](runs/2026-10-09-1036/analysis.md))
- **Library-free chain blocks (W) also beat C, without needing suffix repair; marginal blocks (B)
  showed no resolved gain on training cells.** W/C 1.23–1.38× on training, then-addition and holdouts
  (lower bounds ≥ 1.15); B/C 0.98× [0.93, 1.04] (above about 4% excluded), so edit size alone does
  not explain F or W there. W/R on then-addition 0.954× [0.903, 1.007] (a repair gain above 0.7%
  excluded, a cost up to about 10% not). W's length law and token supply not isolated. (32,
  [34](questions/10-compositional-map-transfer/34-chain-block-suffix-preservation/question.md), [run 1606](runs/2026-10-09-1606/analysis.md))
- **The same extractor on pre-solve parents (E) gave no worthwhile gain over chain blocks on
  then-addition**: E/W_E 0.981× [0.911, 1.057] (above about 1.06× excluded); E/F 0.843× [0.795, 0.892].
  One source selection, one extractor.
  ([33](questions/10-compositional-map-transfer/33-pre-solve-fragment-source/question.md), [run 1350](runs/2026-10-09-1350/analysis.md))

**Cheap acquisition (C+F rebuilt from few sources; failures charged).**
- **Four sources per cell lose about a third of full speed; four more collected under that bias (A8)
  leave it unresolved from full speed at about a tenth of the acquisition.** Then-addition: (C4+F4)/F
  0.679× [0.614, 0.752]; F/A8 1.03× [0.95, 1.12] (an A8 slowdown above about 5% excluded); A8 beat
  four more collected under G4 1.13× [1.04, 1.22]. One source size, one update; yield, content,
  decoder and library bundled.
  ([35](questions/10-compositional-map-transfer/35-small-source-acquisition/question.md),
  [36](questions/10-compositional-map-transfer/36-sparse-source-feedback/question.md), [runs 1743](runs/2026-10-09-1743/analysis.md), [2033](runs/2026-10-09-2033/analysis.md))
- **A8 helped on a fresh output shape and replicated from complementary sources.** `two-sum-v1`
  (`A>B ? C+D : E+F`): G4/A8 2.73× [2.36, 3.17]; rebuilt from the former holdouts 2.50× [2.17, 2.85],
  unresolved from the original. One shape with familiar `+` joins.
  ([37](questions/10-compositional-map-transfer/37-cheap-bias-fresh-transfer/question.md),
  [38](questions/10-compositional-map-transfer/38-cheap-bias-source-replication/question.md), [runs 2303](runs/2026-10-09-2303/analysis.md), [0145](runs/2026-10-10-0145/analysis.md))
- **With addition inside the predicate, fresh A8 builds were about 6–10× cheaper than the weak G4
  prior on never-searched cells.** DG `(Xa+Xb)>(Xc+Xd) ? Xe:Xf` (alphabet `v2_x4`, D625; 24 builds),
  eight protected cells: cost(G4)/cost(A8″) 10.1× [7.6, 13.1] at 2 × cap, 6.4× [5.0, 8.0] at 1 × cap.
  Capped cost, weak prior, one bank; context, fragments and supply bundled.
  ([39](questions/10-compositional-map-transfer/39-independent-input-family-bank/question.md), [40](questions/10-compositional-map-transfer/40-independent-input-protected-transfer/question.md), [run 1536](runs/2026-10-10-1536/analysis.md))
- **DG-acquired builds were about 3× cheaper on unseen DG cells than branch-sum-acquired builds;
  the reverse is unresolved.** TS `Xa>Xb ? Xc+Xd : Xe+Xf`: TS-built ÷ DG-built cost on DG cells 2.98×
  [2.07, 4.33]; on TS cells 1.29× [0.94, 1.78] the other way. Join content versus harder sources not
  separated; one family pair, capped cost. ([41](questions/10-compositional-map-transfer/41-same-alphabet-family-preference/question.md), [run 1717](runs/2026-10-10-1717/analysis.md))
- **Both components carry that DG advantage.** On DG cells without libraries the DG table is 3.26×
  [2.43, 4.30] cheaper than the TS table; on the TS table the DG library beats no library 3.05×
  [2.32, 4.07] and the TS library 1.95× [1.43, 2.66] (unresolved against 1.5×) but stays 1.55×
  [1.15, 2.09] behind the native pair. No library shown to need its own table; no library difference
  resolved on TS cells (equality not shown). One family pair; content versus size not separated;
  which component is larger is a point estimate. ([42](questions/10-compositional-map-transfer/42-family-bias-component-transfer/question.md), [run 2001](runs/2026-10-10-2001/analysis.md))

**Against tree GP** (closure-based subtree GP, restarted, `v2_x4`; donor libraries and priors supply
half the mutation donors; development banks unless stated).
- **Under a common restart schedule, tree GP with no learned prior needs about a fifth fewer DG
  evaluations than A8; A8 stays cheaper in worker seconds.** One tree configuration, up to 8 × 65,536
  evaluations: R-tree/R-A8 0.79× [0.68, 0.92]; solved 765 vs 754 of 768 (noninferior within 3 points;
  equal reliability not established); worker seconds 1.39× [1.20, 1.60]. A8's full-cap reliability
  lead was mainly the schedule.
  ([43](questions/10-compositional-map-transfer/43-acquired-bias-vs-tree-gp/question.md), [44](questions/10-compositional-map-transfer/44-restarted-tree-vs-a8/question.md), [run 0024](runs/2026-10-11-0024/analysis.md))
- **A frozen library of recurring source subtrees cut DG evaluations about 2.6×, beyond size-matched
  random donors.** 24 libraries of 3–9-node subtrees recurring in ≥ 2 source cells (pair sums
  `ADD(Xi,Xj)` plus, in 20/24, one `GT(ADD,ADD)` predicate): R-lib/R-tree 0.39× [0.33, 0.46],
  R-lib/R-size 0.41× [0.33, 0.53]; no solve loss observed. One extractor and rate.
  ([45](questions/10-compositional-map-transfer/45-tree-subtree-library/question.md), [run 0150](runs/2026-10-11-0150/analysis.md))
- **The same libraries cut evaluations about 4× on one fresh shape, far more where the learned
  predicate fits.** `x4-gate-sum-v1` (`(Xa+Xb)>(Xc+Xd) ? Xe+Xf : Xg`, 18 cells frozen before any
  search): R-lib/R-tree 0.25× [0.22, 0.29], R-lib/R-size 0.29× [0.23, 0.37]; predicate-matched split
  A 0.055× [0.042, 0.071], B/C 0.36×, 0.34×. Reuse of the libraries' own parts across composition,
  not unfamiliar content.
  ([46](questions/10-compositional-map-transfer/46-tree-library-fresh-composition/question.md), [run 0348](runs/2026-10-11-0348/analysis.md))
- **On B/C, label-rearranged libraries kept that gain at the registered resolution; A's extra gain
  needs the learned arrangement.** Labels permuted within size/arity/width pools: R-perm/R-lib B/C
  1.03× [0.85, 1.23] (an intact advantage up to about 20% not excluded), A 5.1× [3.7, 7.1]. The
  permutation removed nearly all learned predicates and tripled B/C pair supply.
  ([47](questions/10-compositional-map-transfer/47-tree-donor-arrangement/question.md), [run 0524](runs/2026-10-11-0524/analysis.md))
- **Uniform labels on the same shapes lost most of the B/C gain.** R-unif/R-perm 2.07× [1.68, 2.61];
  R-unif/R-tree 0.755× [0.645, 0.884] (about 40% of the saving kept), worse in 23/24 builds. Against
  size-matched random donors unresolved (R-size/R-unif 1.10× [0.86, 1.37]), so the shape contribution
  is unresolved (up to about 30% not excluded). Label content changed together; one uniform law.
  ([48](questions/10-compositional-map-transfer/48-tree-donor-label-supply/question.md), [run 0652](runs/2026-10-11-0652/analysis.md))
- **Rebuilt from branch-sum (TS) sources, the same recipe also cut B/C evaluations about 2.6×, for
  about a twelfth of DG's acquisition.** 24 TS builds: R-TS/R-tree 0.38× [0.34, 0.43], R-TS/R-sizeTS
  0.41× [0.34, 0.48], no solve loss; repays after about 6 searches (DG about 64); TS versus DG
  libraries 1.03× [0.86, 1.22], unresolved. No TS library holds `GT(ADD,ADD)` (0/24; DG 21/24), so it
  seems unnecessary for this saving (cross-cohort observation). One extractor, one TS cohort.
  ([49](questions/10-compositional-map-transfer/49-tree-library-source-portability/question.md), [run 0833](runs/2026-10-11-0833/analysis.md))
- **On near-solved native TS targets, both libraries raised cost.** R-TS/R-tree 1.78× [1.58, 2.00],
  R-DG/R-tree 1.33× [1.12, 1.57], all jobs solved; R-tree solves 99% first time. One roster, mix 0.5;
  whether gating the library removes this is untested ([50](questions/10-compositional-map-transfer/50-library-easy-target-harm/question.md)).
- **A fixed sum-donor prior with no acquisition was cheaper than the TS libraries on B/C.** All
  `ADD(input,input)` and `ADD(input,const)` forms: R-hand/R-TS 0.85× [0.76, 0.96], R-hand/R-tree 0.32×
  [0.29, 0.35]; donor arms solved all 1,728 jobs, R-tree 1,723; TS acquisition never repaid against
  it within 200 searches (19/24 builds favour the prior). Substitution, not isolation: coverage,
  constants, size and ANY/GT content changed together; prior written after seeing these results.
  ([51](questions/10-compositional-map-transfer/51-source-free-donor-prior/question.md), [run 1019](runs/2026-10-11-1019/analysis.md))
- **On order-helper cells, an uncapped behaviour-keyed library cut evaluations about 2.5×; under the
  16-entry cap the same corpora cost more than no library.** `x4-order-v1` (`lo(a,b)+hi(c,d)` from
  GT/IF_GT), six development cells, 24 acquisitions keeping every output class recurring in ≥ 2
  source cells (25–37 entries): R-all/R-tree 0.40× [0.32, 0.50], 24/24 builds, all jobs solved;
  capped R-S/R-tree 1.23× [1.07, 1.41]; repays after about 5 searches. A supplied order prior is 7.3×
  [5.5, 9.8] cheaper. Size, content and trivia share changed together; helpers' causal share,
  protected cells and fresh banks untested.
  ([53](questions/10-compositional-map-transfer/53-order-library-cap-release/question.md), [run 1228](runs/2026-10-11-1228/analysis.md))

**Overall.** Solver-fitted context and fragment blocks transfer beyond token frequency to withheld
compositions and one fresh shape; outer-loop selection learns token biases but no resolved context
gain. Restarted tree GP needs fewer DG evaluations than A8; learned subtree libraries cut its cost
2.6× on DG and 4× on fresh gate-sum, a fixed sum prior 3.1× on development gate-sum B/C, and an
uncapped library of acquired order helpers 2.5× on development order cells (a supplied order prior
far more); libraries harmed near-solved targets. Not shown: that evolution reaches fitted context or fragments; what
carries C's, the library's or the prior's advantage; why DG components are better; A8 on a fresh
family bank or against tuned tree GP; acquired order content beyond development cells; an
easy-target policy; transfer beyond three fresh shapes.

## 23 Heritable variation bias (root parked, budget 2, 2 used)

[23](questions/23-heritable-variation-bias/question.md): can a token-frequency vector inherited
with each program learn a useful bias through program selection alone, and help fresh populations
once frozen? TAG threshold tasks (sum/max > 1, 5), development bank `tag-threshold-v1`.

- **Under the one procedure tested, inherited frequencies gave fresh populations no useful bias
  (the registered 1.5× gain over uniform) on their training targets.** Pre-registered. Uniform ÷ inherited cost: sum 0.33×
  [0.21, 0.53] (inherited resolved worse), max 0.73× [0.50, 1.06] (a gain above 1.06× excluded, a
  loss up to 2× not); the hand scaffold is 11.9× and 5.75× cheaper. Fairly sure for this σ, schedule
  and inheritance rule; not a verdict on self-adaptation, silent on transfer.
  ([run 1046](runs/2026-10-08-1046/analysis.md))
- **Persistent ancestry made the max vectors less costly than shuffled ancestry; no gain over
  uniform was established.** Broken ÷ inherited 1.58× [1.04, 2.36] on max; unresolved on sum, 1.00×
  [0.69, 1.41]. Drift versus selection not isolated (no mutation-only control).
  ([log](questions/23-heritable-variation-bias/log.md))

## Older context

Background, not the current line: original folding track ([findings](../docs/folding/findings.md));
pre-reframe chem-tape [findings](../docs/chem-tape/findings.md), [experiments](../docs/chem-tape/experiments.md);
[CA](../docs/ca/experiments.md); [coevolution](../docs/coevolution.md); [theory](../docs/theory.md)
(Altenberg); [python-rewrite-results](../docs/python-rewrite-results.md). Process:
[methodology](../docs/methodology.md) (light hobby mode).
