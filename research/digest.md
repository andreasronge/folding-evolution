# Digest: what we currently believe, and why

As of 2026-10-08, after run 2026-10-07-2243 (root 23, stopped at its cost gate, no result). Latest
result: run 2026-10-07-2156, commit `36c665d`. Core question since the 2026-09-25 reframe: *how
does the genotype→program map bias what evolution finds and keeps ("arrival of the frequent"),
and can that bias be adapted to a task family?* Run-by-run history, superseded numbers and the
former long-form sections are in the questions' `log.md` files.

Sources: [notebook](../docs/map-bias/notebook.md) (§1–§32; reviews in
[docs/map-bias/reviews/](../docs/map-bias/reviews/)) and [findings](../docs/map-bias/findings.md)
(items 1–17, owner-promoted). §NN means a notebook section. Exploratory hobby work, mostly 30–50
seeds per cell; pre-registration is noted where it applies. Ratios are speed (> 1 = first arm faster) with 95%
intervals unless stated.

## 01 Map bias (root open, budget spent)

[01](questions/01-map-bias/question.md). Chem-tape and TAG alphabets, threshold and fixed-target tasks.

**Measuring the bias.**
- **Random-genotype frequency predicts which tasks are easy, not which hard ones get solved.**
  Evolution routinely finds behaviours rarer than 1 in 50M random tapes; on the chem-tape alphabet
  chem decoder and direct encoding have almost the same bias. ([item 1](../docs/map-bias/findings.md), §1)
- **Folding's advantage over direct encoding on fixed targets looks like sampling**: where the maps
  differ, folding makes exact solvers 1.3–30× more common and solves more often. On those tasks
  evolution was mostly a worse sampler than random search (one exception); not general: on TAG
  threshold tasks with lexicase every arm solved 9–40× sooner than computed (not run) random
  search. ([item 17](../docs/map-bias/findings.md), §27–§28; [02](questions/01-map-bias/02-fixed-target-sampling/question.md), parked; steering untested)
- **The frequency knob changes how often a part is made, not what is reachable**: weighting one op
  switches between equivalent routes without changing solve rates; very high weights hurt by
  dilution. ([item 12](../docs/map-bias/findings.md), §16, §19)

**Fitting the bias to a threshold family** (sum/max > k, TAG, lexicase, crossover v2, L 64, P 1024).
- **In sampling, a fitted `op_weights` vector transfers to a held-out member**: 4.9× (sum>2) and
  8.9× (max>2) more exact solvers than uniform; the other family's fit gives 1.0× / 1.3×; the
  transferable part is mainly the aggregator weight. One seed, one fit; the post-hoc product model
  that explained it **failed out of sample** (hand-set vector 5.45× / 11.07×, predicted 17× / 22×).
  Fairly sure of the numbers, narrow in meaning. ([08](questions/01-map-bias/08-evolve-bias/question.md), [run 1558](runs/2026-10-05-1558/analysis.md))
- **In evolution the fitted bias is about 4× faster than uniform** (4.33× / 3.58×, lower bounds
  2.6×, 1.9×), and a hand-set INPUT/GT/aggregator scaffold matches it (0.93×, 1.08×). Family
  specificity is unresolved: matched beats the other family's fit only 1.66× / 1.80× (not resolved
  against a 2× bar, 100 pairs). Sampling lift does not predict evolution speed (pass-through
  0.35–3.2). Median speed, one evolution setup. ([08](questions/01-map-bias/08-evolve-bias/question.md), [run 1705](runs/2026-10-05-1705/analysis.md))
- **The other family's vector gives a real generic speed-up; on max>2 it is the INPUT/GT raise.**
  Pre-registered, 250 pairs: 2.73× (sum>2) and 2.02× (max>2) over uniform (lower bounds 2.12,
  1.45). INPUT/GT alone matches the full vector on max>2 (0.90× [0.71, 1.08]); on sum>2 both parts
  beat uniform and neither is resolved against the full vector. Its flat sampling rate was a
  cancellation (INPUT/GT raises solvers 3.2× / 3.9×, the rest cuts them to 0.23× / 0.35×).
  Initialization and mutation are coupled, so no mechanism is named; sum>2 open.
  ([09](questions/01-map-bias/09-generic-bias-speedup/question.md), [run 1814](runs/2026-10-05-1814/analysis.md))
- **On sum>2 the exact max>2 shortcut is used as a last step but is not needed** (pilot only,
  50 seeds): it is the solver's parent in 55/60 exposed runs; barring it delays 49/55 pairs but
  100/100 still solve. Its share of the rest-of-vector gain is unknown (R's gain 1.30, 0.71–2.32).
  Not a null on the stepping stone. ([09](questions/01-map-bias/09-generic-bias-speedup/question.md), [run 1957](runs/2026-10-05-1957/analysis.md))

**Building blocks (chem-tape, tagged runs).** Lexicase, not a new primitive, supplies blocks;
arrangement is then the bottleneck. Tagged transplants are safe (0 crashes in 940); crossover
merges blocks when the join is cheap, but a one-op-join stack does as well, so the advantage is the
join's cost, not modularity. XOR/valley thread closed: joins are built by small edits, no valley
found. ([items 4–16](../docs/map-bias/findings.md), §3–§26)

**Shared helpers (line stopped 2026-10-05).** Three outputs on tags 0/1/2 sharing parts A and B;
hand-built shared, partly shared and duplicated forms; crossover v2, lexicase, P 1024. Fairly sure
for these layouts at L 64; nothing beyond them.
- **Retention is easy; establishment from rare is blocked by mixing between lineages.** A shared
  form at majority persists, and the majority form wins (270/270). From 1/32–1/10 with a selected
  mate it was lost in 294/300 runs; with self as mate it won 183/240 contests against 34/240
  (selected mate) and 75/120 (crossover off). (§29–§31, [06](questions/01-map-bias/06-self-mate-establishment/question.md))
- **Crossover is also what solves, but discovery needs no lineage mixing**: 48–50/50 random-start
  runs solve with crossover, 0–4/50 without; self-mating solves 68–80% by generation 3000, about
  3× slower than a selected mate. A helper already in the host does not rescue a rare shared form.
  (§31 G, §32 J–K; [04](questions/01-map-bias/04-random-start-discovery/question.md) parked, [05](questions/01-map-bias/05-latent-helper/question.md) closed)
- **Solutions arrive mostly partly shared or duplicated and the first established form is kept**
  (121/129). Shared endings are rare (about 4–8 in 100–450 runs, B-helper type). Shared never loses
  to duplicated as such: losers end partly shared. Shortcuts are structural: about a third of each
  final population fits training without being exact; 9/35 runs still end so at 256 cases. (§31 G, §32 L)
- **Why shared endings are rare is unresolved.** Exact shared children do arrive (about 2 per run),
  but all A-only/other; single copies drift out (0/100 established, ≤ 3.6%); no B-helper in 30M
  children (≤ 1.2e-7). 100 insertions cannot tell drift from a disadvantage.
  ([07](questions/01-map-bias/07-shared-arrival/question.md), parked; [03](questions/01-map-bias/03-rare-shared-establishment/question.md) closed)

Status: 03, 05, 06 closed; 02, 04, 07, 08, 09 parked with reopen conditions in their question files.

## 10 Compositional map transfer (root open, 15 of 15 used)

[10](questions/10-compositional-map-transfer/question.md): can a decoder adapted across related
tasks help fresh populations solve unseen operation combinations beyond a token-frequency bias?
Stack tape `v2_rmin(_first)`, length-4 lists, P 256, lexicase on 64 cases with an exact check over
the domain (D1331 from 0001 on), 524k cap. G / G4 are hand-set previous-token grammars; U uniform;
"-marg" the same token marginals without context. All sub-questions 11–22 closed. Every bank is
screened and inspected, so all transfer claims are development-bank claims.

**Banks.**
- **No bank yet supports a symmetric two-family test.** The 3×3 reducer/combiner bank has no
  eligible split at 524k and every split fails the 4 096-evaluation headroom rule under G
  ([11](questions/10-compositional-map-transfer/11-composition-bank/question.md)); none of six
  same-primitive assembly shapes gives two families with enough distinct cells, 0/45 rows, from
  alias identities ([12](questions/10-compositional-map-transfer/12-generic-grammar-headroom/question.md));
  the four-reducer (FIRST) bank has no role-covered branch-else (BE) holdout pair, though
  post-addition (PA) splits ([15](questions/10-compositional-map-transfer/15-four-reducer-family-bank/question.md)).
  Scope: these shapes, domains and frozen rules. Root 10 therefore ran a one-family PA split (G) and
  then a narrower BE/PA split on the four-reducer bank (BE holds out 1 cell, PA 2; G4).
- **Ten-token branch cells leave room above the hand-set grammars** (G medians 2–10× above 4 096; G4
  medians 8.7k–28.7k on all 13 retained cells). (12, 15)

**Hand-set context and supply.**
- **Contextual grammars beat their own token marginals on three banks**: G/G-marg 2.6–4.5× (ADD/DADD
  cells) and about 10–20× (SEL), all intervals above 1; 1.5–6.0× (15/16 resolved) on the second
  bank; G4/G4-marg 4.4× [3.4, 5.6] (BE), 3.3× [2.7, 4.0] (PA). Not a mechanism: G also emits far more
  exact solvers and changes more tokens per mutation. (11, 12, 15)
- **Supply overstates speed here too**: a fixed token bias raises exact-solver sampling 11–82× but
  speed only 1.9–3.5×; G raises supply 120–1 650× for 8.6–31×. ([11](questions/10-compositional-map-transfer/11-composition-bank/question.md))
- **A fixed decoder can express a family preference**: two hand-set family grammars give matched
  over swapped 1.68× [1.39, 2.05] (BE) and 1.32× [1.12, 1.57] (PA), strengthened by context over the
  marginal controls (1.51×, 1.46×); against G4 the BE grammar helps BE (1.36×) and the PA grammar
  shows no resolved PA gain (0.87× [0.75, 1.04]). Expressivity only, not what a learner finds. (15)

**Token learning by outer-loop selection** (multipliers on the hand-set rows; 4+12 loop).
- **Learned token weights transfer about 2–2.5× to withheld cells, on both setups.** On G (PA only):
  2.23× [1.82, 2.75] on training, 2.25× [1.81, 2.81] and 2.06× [1.60, 2.63] on the two withheld cells
  (200 seeds), 2.23× [1.66, 3.06] on branch-else, unresolved on linear (1.08× [0.72, 1.57]); about a
  quarter of the training log-gain is lost on holdouts (descriptive). The learned change is mostly
  INPUT up, DUP down, IF_GT up. Starting from G-marg instead, token learning gains 1.7–2.1× but
  stays at 0.41–0.57× of G. ([13](questions/10-compositional-map-transfer/13-post-addition-map-learning/question.md))
  On G4: 2.18× / 2.27× on own-family training cells, about 2.0× on the BE withheld cell and 2.5–2.6× on
  the two PA withheld cells (all six resolved). ([16](questions/10-compositional-map-transfer/16-crossed-family-adaptation/question.md))
- **That gain is mostly generic; no family advantage was resolved on withheld cells.** Cross-family
  training gains 2.07× and 1.93×; all 20 maps make the same big moves. Matched over mismatched on
  withheld cells 1.02× [0.84, 1.25] (BE) and 0.96× [0.79, 1.15] (PA); the BE bound rises to about
  1.3× leave-one-map-out; a 1.1× preference is not excluded (detecting it needs about 64–75
  trajectories per family). An in-sample interaction of 1.24× [1.09, 1.41] hints at some family
  information on trained cells. Not separated: better prior for this family versus repair of G4's
  weak spots. (16)
- **The frozen maps help through both the starting programs and the decoder used during search,
  sub-additively.** Given the other, ongoing decoder 1.39× / 1.28× and start 1.30× / 1.33×
  (withheld / training), diagonal 2.29× / 2.44×, interaction −0.34 / −0.52 log2 (20/20 maps).
  Not direct seeding (12 of 79 200 searches solved at generation 0). On training cells the start
  weighs relatively more on BE than PA (−0.45 log2 [−0.68, −0.22]), but family is not separated
  from shape or difficulty. Which population properties carry the start gain is unresolved.
  ([17](questions/10-compositional-map-transfer/17-decoder-initialization-variation/question.md))

**Context learned by outer-loop selection: no resolved gain from four procedures.**
- **Full 552-weight learner from G**: 0.92× [0.78, 1.09] on training (gain > 1.09× excluded at that
  budget); its three-cell steps were far below score noise, a plausible but unisolated cause. (13)
- **Row residuals on top of learned M versus continued token learning**: training 1.00× [0.90, 1.11];
  withheld PA 1.16× [0.91, 1.48] and 1.06× [0.83, 1.31], unresolved (about 20 starts would resolve
  1.16×). (13) Their off-family branch-over-linear shift is a property of individual learning runs:
  1.86× [1.41, 2.44] on the "a" maps, reversed 0.73× [0.57, 0.94] on the "b" maps; on "b" a token-only
  map matched to R's emitted frequencies was not resolved from R (BE 1.04× [0.91, 1.17]). Selection
  on PA leaves off-family speed free to wander about 0.5 log2.
  ([14](questions/10-compositional-map-transfer/14-saved-map-shape-shift/question.md))
- **Rank-one context steps mixed into token continuation**: in a loop where token continuation
  learned (96 searches per candidate; T/S 1.14× [1.09, 1.20] and 1.12× [1.03, 1.22] on two fresh
  blocks), C/T 0.967× [0.871, 1.073]: a mean gain above about 1.07× is excluded for this loop and
  these token-tuned starts; small gains or losses up to 13% are not. The earlier 24-search loop
  (C/T 0.955×) did not resolve token learning, so it was not a fair test. Which change made token
  learning work (evidence per candidate, depth, total effort) is not isolated. Context learned
  jointly from G4, or added without displacing token steps, is untested.
  ([18](questions/10-compositional-map-transfer/18-compact-context-learning/question.md),
  [19](questions/10-compositional-map-transfer/19-selection-calibrated-continuation/question.md))

**Context fitted directly to solvers (external fitting, not selection).**
- **A previous-token table fitted to exact G4 solver tapes beats a token-only fit to the same tapes,
  and the gain transfers.** C/T 1.365× [1.288, 1.446] on training (31/32 corpora), 1.293× [1.213,
  1.378] on the withheld cells. Matching C's pooled emitted frequencies does not reproduce it (C/K
  1.65×), though that control is itself slower than T. No matched-family advantage on withheld cells
  (BE 1.02× [0.91, 1.15]; one PA cell favoured the mismatched fit, 0.75× [0.63, 0.89]). Tapes carry
  about 0.45 bits per transition of order information; a corpus pays for itself in about 120–590
  searches. One bank, split and shrinkage (α 50); which structure carries it is unknown.
  ([20](questions/10-compositional-map-transfer/20-solver-corpus-context/question.md))
- **One feedback refit, to solvers found under the fitted table, speeds search further.** C2/C
  1.404× [1.347, 1.464] on training (32/32 lineages), 1.289× [1.204, 1.381] withheld; a fresh one-shot
  G4 refit C' is not resolved from C (0.997× [0.940, 1.058]), so the gain is the collection
  procedure (yield, diversity and tape content bundled). The refit sharpens the decoder (row entropy
  3.91 → 3.80 bits, order information 0.41 → 0.48); not shown causal. Whether a second step helps
  or harms is untested. ([21](questions/10-compositional-map-transfer/21-iterated-solver-corpus/question.md))
- **On training cells that step raised context's advantage over a token-only fit; on withheld cells
  this is unresolved.** I = (C2/T2)/(C1/T1) 1.169× [1.093, 1.250] (BE 1.34× [1.19, 1.50], PA 1.02×
  [0.95, 1.09]; partly in slow seeds, median variant 1.089× [1.008, 1.177]); the token-only fit also
  gained (T2/T1 1.20× training, 1.19× withheld); C2/T2 still 1.58× / 1.37×. Withheld I 1.087× [0.984,
  1.200]: neither equality nor absence; about 46 new lineages would resolve it at the observed effect.
  Same seeds as 1924, not an independent replication.
  ([22](questions/10-compositional-map-transfer/22-feedback-context-increment/question.md))

**Overall.** Useful, transferable assembly information beyond token frequency exists in this
system's own solvers and can be fitted externally; the selection-based learners tried did not
reach it. Learned token biases transfer about 2× but show no resolved family specificity.
Not shown: that evolution reaches fitted context; what structure carries it; transfer to a fresh
bank.

## 23 Heritable variation bias (root open, budget 2, 0 used)

[23](questions/23-heritable-variation-bias/question.md): can a token-frequency vector inherited
with each program learn a useful bias through program selection alone, and help fresh populations
once frozen? **No belief yet.** The first design (run 2026-10-07-2243, commit `25f929e`) was built
and validated but stopped at an over-strict pre-run cost gate (mean-based pricing ≈ 1–2.3 h).
Stage-0 observations (one acquisition run per family × arm) are logged, not evidence; they flag two
design problems: early-stopped episodes give the arm that solves less about 3× more generations
(so more drift), and the max family is rarely solved under this exposure (6–7/48 episodes).
([log](questions/23-heritable-variation-bias/log.md), [decision](runs/2026-10-07-2243/decision.md);
returned to the strategist)

## Older context

Earlier tracks are background, not the current line. The original folding track (3-bond
ceiling broken via Pareto scaffold preservation, regime-shift result):
[docs/folding/findings.md](../docs/folding/findings.md). The chem-tape track before the
reframe: [docs/chem-tape/findings.md](../docs/chem-tape/findings.md) and
[experiments.md](../docs/chem-tape/experiments.md). The CA track:
[docs/ca/experiments.md](../docs/ca/experiments.md). Also
[docs/coevolution.md](../docs/coevolution.md), [docs/theory.md](../docs/theory.md)
(Altenberg's constructional selection) and
[docs/python-rewrite-results.md](../docs/python-rewrite-results.md). Process lessons:
[docs/methodology.md](../docs/methodology.md) (the line now runs in light hobby mode).
