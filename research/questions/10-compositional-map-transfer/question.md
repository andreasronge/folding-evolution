---
status: open
tags: [map-bias, evolve-the-bias, task-family, compositional-transfer, decoder, fresh-start]
budget: {experiments: 45, used: 0}
---
# Can an adapted decoder help fresh populations solve unseen operation combinations beyond a token-frequency bias?

Current summary: **learned token weights on G transfer about 2× to the withheld compositions
and to branch-else; allowing learned contextual moves added no resolved training gain on top (≤ 1.11×),
their holdout increment is unresolved, and the one off-family hint that they shift speed toward
branch shapes did not replicate in a second set of learning runs from the same starts. On the
four-reducer bank, with a narrower split (one BE, two PA holdouts), the same token learner
improves G4 about 2–3× on both families' withheld cells, and which family it was trained on
made no detectable difference there: matched over mismatched 1.02× [0.84, 1.25] (BE) and 0.96×
[0.79, 1.15] (PA). The 95% upper bounds are 1.2485× on BE (roughly 1.3× in leave-one-map-out
checks) and 1.15× on PA; a 1.1× family preference is not excluded. On those three cells the
frozen maps' gain comes from both their starting programs and their use during search, which
overlap heavily: each conditional increment is about 1.3–1.4×, against a 2.29× diagonal; on the
ten training cells the same holds (1.28×, 1.33×), and the start weighs relatively more on BE
cells than on PA cells (C −0.45 log2 [−0.68, −0.22]; family not separated from shape or
difficulty). A third contextual procedure, rank-one context steps mixed into token
continuation from the saved maps, was first run in a loop where token continuation did not
resolve learning (0821); in a loop with 4× more search evidence per candidate, token-only
continuation did learn (T/S 1.14× [1.09, 1.20] and 1.12× [1.03, 1.22] on two fresh seed blocks)
and context under equal search funding still added no resolved increment (C/T 0.967× [0.871,
1.073]; a mean gain above about 1.07× excluded for this loop and these starts, a small gain or
loss not). Context learned jointly from G4, or added without displacing token steps, is untested.
A different signal did work: a previous-token table fitted directly to exact G4 solver tapes
(external fitting, not selection) beat a token-only fit to the same tapes 1.37× [1.29, 1.45] on
training cells and 1.29× [1.21, 1.38] on the three withheld cells, over 32 independent corpora,
with no resolved family advantage. One feedback step then helped further: refitting each table to exact solvers
found under it (C2) beat its parent 1.40× [1.35, 1.46] on training and 1.29× [1.20, 1.38] on the
withheld cells, and beat a fresh one-shot G4 refit by similar margins, while that fresh refit was
not resolved from the parent (C'/C 0.997× [0.940, 1.058]). So useful, transferable assembly
information beyond token frequency exists in this system's own solvers; one round of fitting to
solvers found under the fitted decoder adds further search speed. On the training cells that
step also raised the fitted context's advantage over a token-only fit to the same corpora
(I 1.17× [1.09, 1.25], mostly BE; the token-only fit improved 1.20× too); on the withheld cells
that interaction is unresolved (1.09× [0.98, 1.20]) (22). The selection-based learners tried so
far did not reach it. On a new comparison-gated bank (13-token compositions, 4 training and 4
protected holdouts per family), the same one-shot fit replicated on training cells with a larger
effect: C/T 3.11× [2.78, 3.48] over 16 fresh corpora, 16/16 corpora favouring C (24). The same
frozen tables kept most of that advantage on the eight protected holdouts of that (development)
bank, 2.60× [2.31, 2.92] (25), and on a fresh bank of a new shape, then-addition `A>B ? C+D : E`
(16 semantically selected cells on two gates), 2.12× [1.86, 2.41], a resolved shrinkage from
training of 0.68× [0.57, 0.81] (26). On that bank a G4 token map matched to C's pooled emitted
frequencies (K) does not reproduce the gain: C/K 2.48× [2.17, 2.83], all 16 corpora and cells,
and K is slower than the token-only fit (K/T 0.86× [0.77, 0.96]) (29). Matching C's per-position
frequencies does not reproduce it either: on G4's grammar (Q) C/Q 2.41× [2.11, 2.75], not resolved
from K (Q/K 1.03× [0.93, 1.13]), and as independent positional draws (P) C/P 5.47× [4.79, 6.25]
(30). Widening Q's mutation to C's size by random context-dependent allele recoding, with Q's
random-program distribution and starting tapes held exactly fixed, made search slower, not faster:
R30 cost 1.17× [1.09, 1.25] Q's, and a full-row recoding 2.4× (31). So undirected width does not
carry the gap. Whether C's conditional content or its structured coupling does, and why the gain
shrinks across shape, are not identified. Exact solvers are not the only usable
data: a context fit to tapes from G4 searches that had not yet solved beat a token fit to the same
tapes 1.28× [1.12, 1.45] and G4 1.62× [1.37, 1.90] on the training cells, mostly by solving within
the cap more often, with no resolved parent-selection enrichment; the exact-solver fit stays far
faster (0.27× [0.24, 0.30]) at about 7.9× more source evaluations (27). Collecting two further
rounds of such tapes under the updated context fit beat spending the same source allocation
under G4 and fitting once, 1.18× [1.01, 1.37], gain resolved on BE (1.42× [1.17, 1.72]), PA
unresolved (0.98× [0.83, 1.16]); with more G4 tapes alone no improvement was resolved (0.99× [0.89,
1.10]; gains above about 10% excluded at this scope), and the gain over keeping the first fit is
unresolved (1.16× [0.99, 1.36]) (28). A different kind of unit also helps on the training cells: inserting intact 3–6-token fragments, extracted from other cells' training solvers, as one-step block edits on top of C's unchanged search made it 1.57× [1.42, 1.75] cheaper than C, 1.60× cheaper than blocks from the library's per-position marginals and 1.23× [1.12, 1.36] cheaper than blocks sampled from C's own chain; that library-free chain block alone beat C 1.28× [1.17, 1.39], cause not isolated (32). Frozen whole-corpus libraries kept the advantage on excluded compositions: on then-addition F/C 1.47× [1.38, 1.56], F/W 1.20× [1.11, 1.29], W/C 1.23× [1.15, 1.31], and on the comparison-gate holdouts F/C 1.75×, F/W 1.27×; F/C's change from training (0.93× [0.83, 1.05]) is unresolved, where C/T lost a third across the same shape (development banks; the libraries are shared syntax; externally fitted, nothing acquired) (32). The same extractor applied to parents archived before their source search first solved gave no worthwhile gain over C-chain blocks with its length law on then-addition, E/W_E 0.981× [0.911, 1.057] (a gain above about 1.06× excluded at this scope), and was resolved slower than the exact-solver library, E/F 0.843× [0.795, 0.892]; one source selection and one extractor, C still fitted from exact solvers (33). The C-chain block operator's boundary repair, which keeps the decoded suffix, is not needed at this resolution: without it (R) the same blocks were not resolved slower on then-addition, W/R 0.954× [0.903, 1.007] (a repair gain above 0.7% and the worthwhile 1.10× excluded, a repair cost up to about 10% not), and still beat C 1.29× [1.21, 1.37]; under these block edits the suffix ripple is local, about 3 tokens when it occurs, and the repair's effect under other decoders is unmeasured (34). Rebuilding both decoder and library from four capped G4 attempts per training cell (8% of the source evaluations, failures charged) did not retain the full pipeline's search performance on then-addition: cost(full F)/cost(C4+F4) 0.679× [0.614, 0.752], excluding the pre-set 20% tolerance pooled, in both families and under the cap sensitivities (blocks 0 and 1 do not exclude it separately); C4+F4 was not resolved from full C alone (0.996× [0.919, 1.080] in cost) and its fragments still beat its own chain blocks 1.12× [1.03, 1.22] (unresolved against 1.10). In arithmetic acquisition-plus-search evaluations it is the cheaper deployment only up to about 1 500 fresh searches (development sources and bank; one source size) (35). Collecting four more attempts per training cell under that cheap bias (A8) instead of under G4 (S8), then refitting, showed no observed lock-in on that update: S8/A8 1.126× [1.039, 1.220] in cost, resolved above 1 but unresolved against the worthwhile 1.10×, at 0.30× the second batch's evaluations; A8 was not resolved from the full 48-attempt pipeline (cost(full F)/cost(A8) 1.031× [0.951, 1.117], a slowdown above about 5% excluded) and has lower estimated total evaluation cost than S8 at every reported horizon, resolved through 1 024 searches (one external-fitting update; development sources and bank; decoder, library, yield and content bundled) (36). On a fresh bank frozen before any search (`two-sum-v1`, `A>B ? C+D : E+F`, 16 cells), the frozen A8 was not materially slower than frozen full F, cost(A8)/cost(full F) 0.945× [0.819, 1.092] (a 1.20× loss excluded, sign unresolved), all fitted arms beat G4 about 2.3–2.7× (G4/A8 2.73× [2.36, 3.17]), S8/A8 was again 1.173× [1.036, 1.327], and with acquisition charged A8's estimated total cost was below S8's and full F's at every reported horizon through 4 096 searches, repaying G4 after about 47 searches in evaluations (one fresh output-composition shape on D1331; existing acquisitions, not new sources) (37). Rebuilt from fresh searches on the complementary source roster (the four former holdout cells per family), the unchanged A8 recipe again beat G4 on two-sum-v1, cost(G4)/cost(A8′) 2.50× [2.17, 2.85] (pre-set margin 1.5×; BE 3.14×, PA 1.99× [1.66, 2.32]; 16 single builds), and was not resolved from the historical A8 builds on identical keys, 1.09× [0.90, 1.32] in cost (a 10% gain or a 32% loss not excluded; three PA builds about 2× costlier, cause unplaced because the static S8′ arm went unscored); acquisition 4.5 M evaluations, repaying G4 after about 35 searches (one alternative roster in the same families; development data on both sides) (38)**. On a new family with addition inside the predicate and four independent readouts (`(Xa+Xb)>(Xc+Xd) ? Xe:Xf`, alphabet `v2_x4`, D625), a probe found a valid protected split and sparse first-batch source discovery (22/128) (39); then 24 fresh A8″ builds from its four source cells were far cheaper than G4 on the eight protected cells, never searched before: cost(G4)/cost(A8″) 10.1× [7.6, 13.1] with failures at 2 × cap, 6.4× [5.0, 8.0] at 1 × cap (pre-set margin 1.5×), A8″ solving 317/384 against G4's 63/384, every build above 1.5× at 2 × cap, the three cells with a predicate pairing absent from sources 6.8× [4.9, 9.2] (descriptive), and eight reinterpreted old-family builds clearly weaker than fresh ones (O/A8″ 4.3× [2.7, 6.6]); a capped-cost ratio against a weak supplied prior (321/384 G4 capped), within one development bank, context, fragments and supply bundled (40). Crossing that family (DG) with a branch-sum family on the same alphabet (TS, `Xa>Xb ? Xc+Xd : Xe+Xf`), 24 builds per family, 8 never-searched cells per family: on DG cells the DG-built cohort beat the TS-built one, cost(T)/cost(D) 2.98× [2.07, 4.33] at 2 × cap (2.40× [1.76, 3.30] at 1 × cap, 8/8 cells); on TS cells the direction is unresolved, cost(D)/cost(T) 1.29× [0.94, 1.78], on a roster near ceiling for both cohorts (95–97% solved); the interaction 1.96× [1.58, 2.44] clears the 1.5× margin at 2 × cap only; all cohorts beat G4 on both rosters (≥ 2.75×); family content and the much harder DG sources (G4 first batch 17% vs 63%) not separated (41). Crossing the saved tables and libraries of those builds (24 donor pairs, fresh seeds) showed both components carry the DG advantage: without libraries the DG-built table was 3.26× [2.43, 4.30] cheaper on DG cells than the TS-built table, a point gap similar to the fresh native gap (3.03×); the DG library also sped the TS-built table, 3.05× [2.32, 4.07] over no library and 1.95× [1.43, 2.66] over its own library (unresolved against the pre-set 1.5×), leaving the hybrid 1.55× [1.15, 2.09] behind the native DG pair; no dependence of a library on its native table was shown, and on TS cells no library difference was resolved in either within-table comparison (T table 1.01× [0.83, 1.25], D table 1.00× [0.79, 1.27]; upper cost-ratio bounds 1.25 and 1.27, equality not shown) (development data, frozen external fits, one family pair) (42). Against family-blind closure-based subtree GP (no learned prior; crossover mix selected on source/development cells and frozen before target scoring) on the same rosters, frozen native A8 showed no ≥ 1.5× geometric search-cost advantage on DG under failures charged at 2 × cap, while keeping positive arithmetic savings: cost(tree)/cost(A8) 0.961× [0.683, 1.352] at 2 × cap (an A8 advantage of 1.5× excluded, a tree advantage up to about 1.46× not; 1 × cap 0.785× [0.583, 1.055], unresolved); A8 solved more (314/384 vs 202/384) while tree GP was much faster when it solved, so A8 still saves arithmetic evaluations and repays its acquisition after about 146 [99, 269] DG searches per build; on TS tree GP was about 5.7× cheaper (0.175× [0.142, 0.217], descriptive); on DG both beat G4 about 10×, on TS A8 about 7.2× and tree GP about 40.8× (geometric costs) (development rosters, evaluations as the unit, one tree configuration whose DG failures crowded its 32-token cap; two earlier attempts stopped before scoring) (43). Restarting both procedures with the same schedule (up to 8 attempts of 65,536 evaluations, same 524,288 total) removed A8's remaining DG evaluation advantage: mean evaluations R-tree ÷ R-A8 0.792× [0.682, 0.915] (paired 24-build bootstrap, 768 jobs per arm), solved 765/768 vs 754/768 (difference +0.014 [0.000, 0.034], noninferiority within 3 points, equality not shown); restarts also lifted A8 itself from 83.6% to 98.2% solved and cut its cost 0.727× [0.647, 0.814], so 43's A8 reliability lead was mainly a full-cap schedule effect. In worker seconds the direction reverses (tree ÷ A8 1.388× [1.196, 1.604]; tree costs 1.75× more per evaluation), so A8 repays its historical acquisition after about 312 [211, 579] searches per build in seconds and never in evaluations; on TS restarted tree was 0.181× [0.159, 0.202] in evaluations (descriptive); part of tree's restart gain may be training-case redraw, not separated (development rosters, one cutoff, saved builds) (44). Inside restarted tree GP, a frozen library of recurring subtrees extracted from new tree-GP solvers on the four DG source cells (24 independent acquisitions; mostly pair sums `ADD(Xi,Xj)` plus, in 20/24, one `GT(ADD,ADD)` comparison predicate), used as half of the mutation donors, cut mean evaluations on the eight DG target cells to 0.390× [0.332, 0.463] of R-tree's and 0.414× [0.332, 0.533] of size- and length-matched random donors, with no reliability loss (1,536/1,536 vs 1,524/1,536 solved); lower in 24/24 acquisitions and all 8 cells, including cells whose pair split no learned predicate contains (0.35–0.53×); repaying its acquisition after about 54 [45, 65] searches; the carrying ingredient (comparison skeleton, pair sums, or an input/`ADD` token-frequency shift the size control does not match) is unidentified (development bank, one extractor, ~11% realised insertion) (45). The same 24 frozen libraries transferred as a search-cost saving to a fresh bank frozen before any protected search (`x4-gate-sum-v1`, `(Xa+Xb)>(Xc+Xd) ? Xe+Xf : Xg`, 18 protected cells): R-lib ÷ R-tree 0.250× [0.217, 0.289], R-lib ÷ R-size 0.291× [0.231, 0.372], 1,728/1,728 vs 1,726/1,728 solved, lower in 18/18 cells and 24/24 builds, repaying acquisition after about 55 [49, 62] searches; the relative gain is much larger on the split whose predicate the libraries learned (0.055×) than on the two splits no learned predicate covers (about 0.34–0.36×) (one shape assembled from the libraries' own parts; two development cells probed before the freeze) (46). Rearranging each library's labels within (entry size, compiled length, node arity, token width) pools, which keeps shapes and size-conditioned primitive counts but removed the learned predicate almost entirely and tripled the supply of pair sums those two splits need, kept the gain on them: R-perm ÷ R-lib 1.031× [0.854, 1.225] (retention margin 1.25; an intact advantage up to about 20% not excluded), R-perm ÷ R-tree 0.360× [0.299, 0.429], 1,728/1,728 solved in both donor arms; on the learned predicate's split it raised cost 5.14× [3.68, 7.14], removing most of that split's extra gain. So that split's extra gain needs the learned arrangement; the unmatched-split gain does not at this resolution, though its carrier is still unidentified (retention could be a cancellation of lost arrangement and added pairs) (development bank, one cohort, one construction) (47). With shapes held fixed, drawing labels uniformly within compatible classes lost most of that B/C gain: R-unif ÷ R-perm 2.07× [1.68, 2.61], R-unif ÷ R-tree 0.755× [0.645, 0.884] (about 40% of the saving kept), not resolved from random size-matched donors (R-size ÷ R-unif 1.095× [0.864, 1.367]); preserving shapes with this uniform label law did not retain the full learned-label saving, and the shape contribution remains unresolved (one uniform law; ADD share, ANY share, constants and dependencies changed together) (48). The unchanged extractor rebuilt from the four branch-sum (TS) source cells instead of DG (24 new builds, 0.245 M evaluations each, about 12× cheaper than DG) cut B/C evaluations to 0.382× [0.335, 0.433] of R-tree and 0.406× [0.344, 0.482] of its size-matched random donors, no solve loss, 24/24 builds and 12/12 cells, repaying after about 6 searches; TS ÷ DG libraries 1.03× [0.86, 1.22] (unresolved); none of the 24 TS libraries holds the seven-node `GT(ADD,ADD)` predicate (DG 21/24; they do hold 13 smaller GT-rooted entries), so neither that predicate nor split-matched pairs seem necessary for this saving (cross-cohort observation). On the near-solved native TS targets both libraries raised cost (TS-built 1.78× [1.58, 2.00], DG-built 1.33× [1.12, 1.57] of R-tree) (development rosters; one extractor, mix and schedule) (49). A fixed, source-free prior of all `ADD(input,input)` and `ADD(input,const)` forms (written from the alphabet after seeing these results, no acquisition) was cheaper than the 24 TS libraries on B/C: R-hand ÷ R-TS 0.852× [0.762, 0.958], R-hand ÷ R-tree 0.318× [0.291, 0.349], all jobs solved in both donor arms; TS acquisition never repaid against it within 200 searches. Substitution, not ingredient isolation: pair coverage, constants, size and ANY/GT content changed together (development bank) (51). A probe on a new content family, pairwise order helpers `lo/hi(a,b)` (observations only, six development cells, protected roster never searched), found the unchanged literal extractor acquired no helper in 0/8 builds and cost 1.55× [1.09, 2.17] of R-tree; a behaviour-keyed variant held a helper in 3/8 builds and was unresolved from R-tree (1.00× [0.68, 1.46]); a supplied 12-helper prior was about 20× cheaper than R-tree; evolution builds the helpers (63% of source solvers) but in varied or bloated literal forms, and keyed helpers lost to the 16-entry cap under cells-first ranking (52). Removing that cap (R-all: every behaviour class recurring in ≥ 2 source cells, 25–37 entries; 24 new acquisitions, pre-registered) turned the same corpora into a large saving on the six development cells: R-all ÷ R-tree 0.40× [0.32, 0.50] in capped arithmetic mean evaluations (24/24 builds, 6/6 cells), R-all ÷ capped R-S 0.33× [0.27, 0.39], capped R-S ÷ R-tree 1.23× [1.07, 1.41]; repaying after about 5 searches; a needed helper in the pool in 126/144 cell × build pairs (capped 14/144); the supplied order prior still 7.3× [5.5, 9.8] cheaper; helper causality not isolated (size, content and trivia share changed together); protected cells unsearched, same development bank (53). A probe of that frozen R-all recipe on rectified pair sums `pos(a,b)+neg(c,d)` (observations only, six development cells, protected roster never searched) found sources solved mostly through the three-input sum, no rectifier helper in any of 8 libraries (needed-helper coverage 0/48) and no resolved saving, R-all ÷ R-tree 1.03× [0.96, 1.10] (a saving above about 4% excluded at this descriptive resolution, a smaller one not); a supplied 12-helper prior gave 0.57× [0.50, 0.64] (54, parked).
(45-slot budget, 45 used; strategy 1315 raised the budget from 44 to 45 and assigned slot 45 to the [54](54-rectified-sum-acquisition/question.md) probe; strategy 1228 raised the budget from 43 to 44 and assigned slot 44 to [53](53-order-library-cap-release/question.md); strategy 1129 raised the budget from 42 to 43 and assigned slot 43 to the [52](52-order-helper-acquisition/question.md) probe; strategy 1019 raised the budget from 41 to 42 and assigned slot 42 to [51](51-source-free-donor-prior/question.md); strategy 0833 raised the budget from 40 to 41 and assigned slot 41 to [49](49-tree-library-source-portability/question.md); strategy 0652 raised the budget from 39 to 40 and assigned slot 40 to [48](48-tree-donor-label-supply/question.md); strategy 0524 raised the budget from 38 to 39 and assigned slot 39 to [47](47-tree-donor-arrangement/question.md); strategy 0348 raised the budget from 37 to 38 and assigned slot 38 to [46](46-tree-library-fresh-composition/question.md); strategy 0150 raised the budget from 36 to 37 and assigned slot 37 to [45](45-tree-subtree-library/question.md); strategy 0024 raised the budget from 35 to 36 and assigned slot 36 to [44](44-restarted-tree-vs-a8/question.md); strategy 2214 raised the budget from 34 to 35 and assigned slot 35 to [43](43-acquired-bias-vs-tree-gp/question.md), whose first two attempts (2214, 2239) stopped before scoring and whose third (2254) used the slot; strategy 2001 raised the budget from 33 to 34 and assigned slot 34 to [42](42-family-bias-component-transfer/question.md); strategy 1717 raised the budget from 32 to 33 and assigned slot 33 to [41](41-same-alphabet-family-preference/question.md); strategy 1536 raised the budget from 31 to 32 and assigned slot 32 to [40](40-independent-input-protected-transfer/question.md); strategy 0311 raised the budget from 30 to 31 and assigned slot 31 to [39](39-independent-input-family-bank/question.md); strategy 0145 raised the budget from 29 to 30 and assigned slot 30 to [38](38-cheap-bias-source-replication/question.md); strategy 2303 raised the budget from 28 to 29 and assigned slot 29 to [37](37-cheap-bias-fresh-transfer/question.md); strategy 2033 raised the budget from 27 to 28 and assigned slot 28 to [36](36-sparse-source-feedback/question.md); strategy 1743 raised the budget from 26 to 27 and assigned slot 27 to [35](35-small-source-acquisition/question.md); strategy 1606 raised the budget from 25 to 26 and assigned slot 26 to [34](34-chain-block-suffix-preservation/question.md); strategy 1350 raised the budget from 24 to 25 and assigned slot 25 to [33](33-pre-solve-fragment-source/question.md); strategy 1036 raised the budget from 23 to 24 and assigned slot 24 to [32](32-learned-fragment-operator/question.md)'s reuse stage; strategy 0826 raised the budget from 22 to 23 and assigned slot 23 to [32](32-learned-fragment-operator/question.md); strategy 0537 raised the budget from 21 to 22 and assigned slot 22 to [31](31-distribution-preserving-recoding/question.md); strategy 0239 raised the budget from 20 to 21 and assigned slot 21 to [30](30-position-matched-replacement/question.md); strategy 0125 assigned slot 20 to [29](29-frequency-matched-transfer/question.md); strategy 2116 assigned slot 19 to [28](28-partial-program-feedback/question.md); strategy 1831 assigned slot 18 to [27](27-partial-program-context/question.md); allocation 1534 raised the budget from 16 to 20 for a four-slot block, first
slot run 1548; strategy 1246 raised the budget from 15 to 16, for 24; strategy 2129 raised the budget from 14 to 15, for 22; strategy 1924 raised the budget from 13 to 14; strategy 1400 raised the budget from 5 to 7, strategy 1723 to 9, strategy
2331 to 10, strategy 0803 to 12, strategy 1137 to 13; sub-questions [18](18-compact-context-learning/question.md)
and [19](19-selection-calibrated-continuation/question.md) closed;
[20](20-solver-corpus-context/question.md) closed after run 1707,
[21](21-iterated-solver-corpus/question.md) after run 1924;
[22](22-feedback-context-increment/question.md) closed after run 2156; its first attempt,
run 2129, stopped at preparation).
Run 2026-10-09-0537 ([31](31-distribution-preserving-recoding/question.md), commit `fe196c1`): the
16 Q tables recoded by context-dependent allele permutations within each body row (R30: 30% of
entries, R100: all), row counts exact so the uniform-prior tape distribution is Q's; generation 0
inverse-mapped to Q's token tapes; 4 096 searches on Q's triples, 100 min, gates all passed (the
queue's `failed` mark is a plotting import after results were written). Tokens per allele resample
C 2.95, Q 1.71, R30 3.00, R100 7.71. cost_Q/cost_R30 0.855 [0.801, 0.914] (14/16 corpora < 1),
cost_Q/cost_R100 0.409 [0.386, 0.434], cost_R30/cost_C 2.82× [2.49, 3.19]. Solves C 86.5%, Q 73.9%,
R30 73.7%, R100 52.4%.
Run 2026-10-09-0306 ([30](30-position-matched-replacement/question.md), commit `2bab2c2`; first
attempt 0239 stopped at its runtime admission gate): frozen Q (G4 × per-position multipliers matched
to C's marginal at all 32 positions, C's start row) and P (independent draws from C's positional
marginals) from the 16 1246 C tables, on 1548 row F with C/T/K's paired seeds; 4 096 searches,
96 min, complete, replays bit-exact. C/Q 2.41× [2.11, 2.75] (1 × cap 2.21×, both-solved 1.95×;
16/16 corpora and cells above 1.20); C/P 5.47× [4.79, 6.25]; Q/K 1.03× [0.93, 1.13]; Q/P 2.27×;
T/Q 1.14× [1.04, 1.24]. Solves C 86.5%, T 75.5%, Q 73.9%, K 72.5%, P 50.5%. Tokens changed per
allele resample C 2.97, Q/K/T 1.73, P 0.92.
Run 2026-10-09-0125 ([29](29-frequency-matched-transfer/question.md), commit `8e62831`): the
16 frozen 1246 K tables (G4 × 24 multipliers matched to C's pooled emitted marginals) on 1548 row
F's 16 then-addition cells with C/T's paired seeds and case draws; 2 048 searches, 42 min,
complete, 32/32 C/T replays bit-exact. C/K 2.48× [2.17, 2.83] (1 × cap 2.25×, both-solved 1.92×;
BE-fitted 2.77×, PA-fitted 2.21×); K/T 0.86× [0.77, 0.96]; K/G4 1.57× (unpaired). Solves C 86.5%,
T 75.5%, K 72.5%, G4 63.3%.
Run 2026-10-08-2116 ([28](28-partial-program-feedback/question.md), commit `393a4dc`): 16
lineages (one 1831 corpus each, round 1 replayed bit-exactly), 96 sources per own training cell
per acquisition arm; F collects rounds 2–3 under C1/C2 and freezes C3, TF the same with token
fits, O collects under G4 and fits once; R = C1; G4 and C_exact references; 6 144 paired scoring
searches, 200 min, complete. F/O 1.18× [1.01, 1.37] (1 × cap 1.16×; both-solved 1.09× [0.95,
1.26]; BE 1.42× [1.17, 1.72], PA 0.98× [0.83, 1.16]); F/R 1.16× [0.99, 1.36]; O/R 0.99× [0.89,
1.10]; F/TF 1.46× [1.23, 1.75]; F/C_exact 0.31× [0.25, 0.38]; R/G4 1.62× [1.41, 1.86] (replicates
1831). Solves C_exact 92%, F 74%, R 73%, O 72%, TF 66%, G4 62%. F used 7.4% fewer source
evaluations than O.
Run 2026-10-08-1831 ([27](27-partial-program-context/question.md), commit `998a9fe`): 16
partial corpora (8 BE, 8 PA), 32 G4 sources per own training cell stopped at first solve or 65 536
evals, 8 parent (S) + 8 uniform (P) tapes per unsolved checkpoint (64/128/256 generations), 89 536
tapes all verified non-exact; five arms (C_S, T_S, C_P, 1246's C_exact, G4) × 16 paired seeds × 4
cells; 5 120 searches, 120 min, complete. C_S/T_S 1.28× [1.12, 1.45] (1 × cap 1.22×, both-solved
1.05× [0.88, 1.24]; BE 1.42×, PA 1.15× [0.96, 1.38]); C_S/G4 1.62× [1.37, 1.90]; T_S/G4 1.27×;
C_S/C_P 1.04× [0.92, 1.16]; C_S/C_exact 0.27× [0.24, 0.30]. Solves C_exact 90%, C_S 73%, C_P 73%,
T_S 66%, G4 61%.
Run 2026-10-08-1548 ([26](26-then-addition-fresh-bank/question.md), commit `45b2bdb`, rows F
and D): the 32 frozen 1246 tables, no refit, on (F) the fresh then-addition bank (16 cells × 8
paired seeds per corpus, 4 352 searches, 70 min) and (D) 1246's unchanged holdout roster (4 352
searches, 52 min); complete, no errors. F: C/T 2.12× [1.86, 2.41], 1 × cap 1.96×, both-solved
1.74×; 16/16 corpora, 14/16 cells resolved; solves C 86.5%, T 75.5%, G4 63.3%; shrinkage from
training 0.68× [0.57, 0.81]; (C/T)_BE over (C/T)_PA 1.38× [1.13, 1.68]. D: C/T 2.60× [2.31,
2.92], 8/8 holdouts resolved; own-family holdout/training 0.88× [0.72, 1.07]; matched over
mismatched 1.10× [0.89, 1.35].
Run 2026-10-07-2156 ([22](22-feedback-context-increment/question.md), commit `36c665d`,
training row 1, holdout row 4): token-only fits T1 (to 1707 corpora) and T2 (to 1924 feedback
corpora) scored on the exact 1924 seeds of C1 and C2; 32 lineages, 5 120 training and 3 072
holdout searches per arm, 26 min, all validation and 64/64 replays passed. Training: interaction
I = (C2/T2)/(C1/T1) 1.169× [1.093, 1.250] (BE 1.34× [1.19, 1.50], PA 1.02× [0.95, 1.09]); T2/T1
1.201× [1.150, 1.255]; C2/T2 1.580×; C1/T1 on these seeds 1.352× (1707: 1.365×); median-over-seeds
variant 1.09× [1.008, 1.18]. Holdouts: I 1.087× [0.984, 1.200]; T2/T1 1.186× [1.107, 1.271];
C2/T2 1.365× [1.287, 1.447].
Run 2026-10-07-1924 ([21](21-iterated-solver-corpus/question.md), commit `5565d54`, row 1): each
of the 32 saved 1707 tables C collected 48 searches per own training cell under itself (7 623/7 680
solved) and was refitted with the frozen 1707 rule (C2); a fresh G4 corpus gave the one-shot
control C' (7 378/7 680); 32 shared fresh seeds per cell and arm; 39 976 searches, 73 min, all
validation passed. Training: C2/C 1.404× [1.347, 1.464] (32/32 lineages), C2/C' 1.408× [1.342,
1.478], C'/C 0.997× [0.940, 1.058]. Holdouts: C2/C 1.289× [1.204, 1.381], C2/C' 1.330× [1.263,
1.401], C'/C 0.969× [0.908, 1.035]. C2's rows are sharper than C's in every lineage. Yield,
tape diversity and tape content of the C-collected corpora are not separated.
Run 2026-10-07-1707 ([20](20-solver-corpus-context/question.md), commit `627336d`, row 1): 16
corpora per family, each from 48 G4 collection searches per own training cell (7 408/7 680
solved), fitted to T (24 token multipliers on G4, maximum likelihood), C (transition counts
shrunk toward G4, α 50) and K (G4 × multipliers matched to C's pooled emitted marginal); 32 fresh
seeds per cell and arm; 35 240 searches, 81 min, all validation passed. Training: C/T 1.365×
[1.288, 1.446], C/K 1.654× [1.568, 1.744], K/T 0.825× [0.776, 0.878]; T/G4 2.42×, C/G4 3.31×
(unpaired); T versus the 1723 maps unresolved. Holdouts: C/T 1.293× [1.213, 1.378], C/G4 2.75×;
matched over mismatched C 1.02× [0.91, 1.15] (BE), 0.75× [0.63, 0.89] and 0.99× [0.89, 1.10] (PA).
Run 2026-10-07-1137 ([19](19-selection-calibrated-continuation/question.md), commit `86ef669`,
row 6): the same 16 saved 1723 starts, 2 + 6 loop at 96 searches per candidate, 12 generations,
9 600 searches per trajectory; 335 700 searches, 4.63 h, all validation passed (0821's S rows
reproduced bit-identically), no holdout touched. T/S 1.143× [1.089, 1.200] on 0821's fresh seeds
(16/16 starts), 1.122× [1.031, 1.222] on new seeds; C/T 0.967× [0.871, 1.073]; C/S 1.084× [0.993,
1.184]; C0/T 0.932× [0.860, 1.010] (C made half as many token proposals as T). Per-start gains
are not measurable at 50 seeds (F1/F2 correlation 0.15); only pooled means are informative.
Run 2026-10-07-0821 ([18](18-compact-context-learning/question.md), commit `f61aec4`, row 3):
16 pairs (8 BE, 8 PA) from saved 1723 maps on the ten training cells, token-only (T) versus
token-or-rank-one-context (C) continuation, 4 040 searches per arm, 2 + 6 loop at 24 searches
per child; 174 964 searches, 2.64 h, all validation passed, no holdout touched. C/T 0.955×
[0.833, 1.095] (pair sd 0.38 log2); T/S 1.03× [0.90, 1.16]; C/S 0.98× [0.90, 1.07]; flat in-loop
slopes in both arms. Stage A: single context steps have repeatable effects (σ²_T 0.047 [0.027,
0.065]); the best quarter of 24 mutants beat the average mutant on new seeds, but their
difference from the parent was unresolved (−0.017 [−0.085, +0.041] log2).
Run 2026-10-07-0315 ([17](17-decoder-initialization-variation/question.md), commit `5dae3a6`,
row 1): the same frozen 2×2 on the ten training cells (4 BE, 6 PA), 200 fresh seeds, 122 000
searches, 4.3 h, all validation passed. Ongoing-decoder increment given M's start 1.28× [1.22,
1.34]; start increment given ongoing M 1.33× [1.26, 1.40]; diagonal 2.44× [2.23, 2.66];
interaction −0.52 log2 [−0.62, −0.42]. S = log2(MG/GM) negative on all four BE cells (each
resolved), −0.05 to +0.54 on the PA cells (none resolved negative); C = −0.45 [−0.68, −0.22]
(Welch over cells), 20/20 maps agree in direction. S tracks MM difficulty across cells (r 0.77,
post hoc), so family, shape and difficulty tail are not separated on these screened cells.
Run 2026-10-06-2331 ([17](17-decoder-initialization-variation/question.md), commit `8f42f38`,
row 3): the 20 frozen 1723 maps (M) and G4 (G) crossed as starting-program source × search
decoder, with generation-0 token tapes held identical by re-encoding; 400 fresh seeds, three
2229 cells. Ongoing-decoder increment given M's start 1.39× [1.31, 1.47]; start increment given
ongoing M 1.30× [1.24, 1.36]; diagonal 2.29× [2.05, 2.54]; interaction −0.34 log2 [−0.40,
−0.29] (sub-additive in 20/20 maps). Start-heavy on the BE cell (ongoing increment 1.11× [1.04,
1.19]), ongoing-heavy on the PA cells; one BE cell, descriptive.
Run 2026-10-06-2229 ([16](16-crossed-family-adaptation/question.md), commit `33fcee2`, row 4):
the 20 frozen stage-1 maps and G4 on the three holdouts, 400 shared fresh seeds each. Gains over
G4 resolved in all six arm × cell estimates (1.97×–2.93×, lowest lower bound 1.63×); holdout
gains remain substantial (BE's point gain slightly lower than on training, PA's higher; these
cross-block comparisons do not establish equality or absence of overfitting). Pre-stated within-map interaction 0.98× [0.83, 1.15].
The BE bound holds by 0.0015 and is not robust to dropping single maps (upper bound then
1.25–1.30).
Run 2026-10-06-1723 (16, stage 1, commit `db96645`, row 4):
10 independent G4-based token-multiplier trajectories per family (BE trains on 4 cells, PA on 6).
Own-family gain over G4 on fresh training searches: BE 2.18× [1.98, 2.40], PA 2.27× [1.95, 2.65].
Off-family training cells: 2.07× [1.94, 2.21] and 1.93× [1.61, 2.30]. Matched over mismatched
in-sample: 1.13× [0.93, 1.37] on BE cells and 1.10× [0.93, 1.29] on PA cells, both unresolved;
a post hoc within-map interaction 1.24× [1.09, 1.41]. Learning cost 10–14 min per trajectory.
Run 2026-10-06-1603 ([15](15-four-reducer-family-bank/question.md), commit `92ba7c5`, row 1):
adding FIRST to SUM/MAX/MIN leaves 13 of 36 ten-token cells on D1331 (BE 5, PA 8). BE has no
holdout pair whose roles are covered by training, on any of three domains; PA splits. On all 13
cells G4 solved 45–50/50 with medians 8.7k–28.7k. A hand-set BE grammar and a hand-set PA
grammar showed a crossed family preference: matched over swapped 1.68× [1.39, 2.05] on BE,
1.32× [1.12, 1.57] on PA. Context strengthens it relative to the tied-marginal controls (paired
contrasts 1.51×, 1.46×, lower bounds 1.09, 1.16); the marginal contrasts alone are unresolved
(BE [0.90, 1.36], PA [0.76, 1.10]). Only the BE grammar had a resolved own-family gain over G4;
for the PA grammar no gain was resolved (0.87× [0.75, 1.04], admitting gains up to about 4%). This is a positive witness for a decoder class, not learned
evidence. The symmetric matched/mismatched test cannot run on this bank under the frozen
rules.
Run 2026-10-06-0811 ([13](13-post-addition-map-learning/question.md), commit `0709104`, row 4):
from the six saved M maps, 12 matched pairs × 35 generations compared R (token steps plus
whole-row contextual residuals) with M+ (token steps only). R / M+ on fresh training 1.00×
[0.90, 1.11] (a gain above 1.11× excluded); on the two holdouts 1.16× [0.91, 1.48] and 1.06×
[0.83, 1.31], unresolved because the between-start spread is about twice the planned one.
Continued token learning still helped (M+ / M 1.45× on training). Frozen M was faster than G
on the two branch-else cells (2.23× [1.66, 3.06]), with a point estimate similar to the PA
holdouts (2.25×, 2.06×; lower bounds 1.81, 1.60; separate estimates, not an equivalence test),
and unresolved on linear cells, so its benefit is not confined to PA on the cells scored; a PA
preference is not ruled out. An unregistered six-map pattern, R faster than M+ on branch-else
(1.33× [1.05, 1.66], 5/6 starts) and slower on linear (0.65× [0.44, 0.88]), was the only hint of
learned context tied to the training shape; run 1425 (below) did not replicate it. Operator acceptance was near 25% for every
operator; these counts do not establish how well selection ranks individual steps.

Run 2026-10-06-1425 ([14](14-saved-map-shape-shift/question.md), commit `b397f72`, row 3;
approved twice before as runs 1400 and 1419, both blocked by a merge conflict): 55 saved maps on
the eight frozen off-family cells, 200 fresh seeds each. On the six unscored "b" continuations
R / M+ was 0.94× [0.77, 1.16] on branch-else and 1.29× [0.88, 1.91] on linear; the shift was
0.73× [0.57, 0.94], opposite to "a" in 6/6 starts. The "a" maps repeat their pattern on the
fresh seeds (shift 1.86× [1.41, 2.44]); a consistently positive learner-level shift was not
demonstrated (two continuations of six shared starts disagree in sign). On "b", a G-context
token-only map matched to R's pooled emitted token frequencies was not resolved from R; R's
advantage is bounded to about 1.17× (BE) and 1.12× (shift). Both learners, in both
letters, were faster than their M start on BE (lower bounds 1.05–1.10×). Six shared M starts
only.

Run 2026-10-06-0132 ([13](13-post-addition-map-learning/question.md), commit `02cf76f`): on the
one-family post-addition split (six training, two withheld cells on D1331), 23 learned token
multipliers on G's rows (M, 6 trajectories × 25 generations) sped fresh search 2.2× over frozen G
on training and 2.0× / 1.7× on the two holdouts (95% lower bounds 1.47, 1.26; 6/6 trajectories).
The full contextual learner (C, 552 weights, three-coordinate mutations) drifted modestly but
showed no resolved training gain (0.92× [0.78, 1.09]). A frequency-only learner (T) beat its
context-free start 1.7–2.1× but stayed 1.8–2.4× slower than G. Family specificity and mechanism
are unmeasured; the bank was screened, so this is fresh-seed transfer on a screened bank, not an
untouched benchmark.

Earlier: two feasibility studies. Run 2026-10-05-2247 ([11](11-composition-bank/question.md)):
the 3×3 reducer/combiner bank failed its split and headroom requirements (no eligible split at
524 288 evaluations — Sm-SEL 27/50 under uniform, SM-SEL an exact alias — and all four structural
splits failed the 4 096-evaluation headroom rule under the hand-set previous-token grammar G,
held-out medians 768–4 096). Run 2026-10-06-0001 ([12](12-generic-grammar-headroom/question.md))
failed the two-family requirement but kept a usable one-family post-addition split: ten-token
cells leave room above G (post-addition and branch-else medians 8 192–41 728), yet none of six
same-primitive shapes gave two families with ≥ 4 non-aliased cells each. Across both banks G beats
its own context-free marginals (G-marg) 2.6–19.5× (KM median, 2247) and 1.5–6.0× (paired capped
time, 0001; 15/16 intervals exclude 1). Root 01 earlier showed useful transfer of fitted token
frequencies between constant thresholds, with a hand-set scaffold performing comparably. See the
[plan](../../plans/compositional-map-transfer.md),
[family addendum](../../plans/compositional-family-headroom.md),
[one-family plan](../../plans/post-addition-map-adaptation.md) and
[opening strategy](../../runs/2026-10-05-2039/strategy.md).

Competing explanations:
- A: Experience across training tasks selects reusable assembly preferences. The adapted
  decoder improves held-out search beyond a fitted independent-token map and simple fixed
  assembly controls, with an advantage tied to the training family.
- B: More useful tokens or generic well-formed programs explain the gain. An independent
  token bias or task-agnostic assembly rule performs comparably.
- C: The decoder specializes to training programs. Training improves but transfer fails
  when programs are reset or operation combinations are withheld.
- D: Held-out solvers become more frequent, but that distributional gain does not improve
  evolutionary search at the tested budget, or decoder changes damage useful local moves.
- E: The proposed tasks or adaptation loop are not tractable at the measured budget.
  This is a feasibility result about this design, not a negative answer to A.

Where they stand after runs 1707, 1924, 2156, 1548, 0125, 0306, 0537 (1831 and 2116 bear on acquisition, not transfer): A's first half (held-out gain beyond a fitted independent-token
map) is supported for an externally fitted previous-token table, now also on a fresh bank of a new
shape (2.12×, 26), not yet for any adapted-by-selection decoder; its second half (advantage tied to the training family) is not supported:
no matched-family gain was resolved on the three withheld cells, one PA cell resolved the other way, and
the token maps' family contrast is bounded (16); on the comparison-gate holdouts family matching
is 1.10× [0.89, 1.35], unresolved (25). For externally fitted A8 builds it is now supported in one direction on one alphabet: DG-built builds beat TS-built ones about 3× on DG cells, while the TS direction is unresolved on a near-ceiling roster (41). B remains compatible with every selection-based
learner tried (token gain about 2×, no contextual increment resolved). For the fitted tables, the
tested token-only fit and G4 do not reproduce C's gain, C2 adds a further 1.29× on the withheld
cells, and on training cells a token-only refit to the feedback corpus recovers only part of
C2's increment (I 1.17×, BE-carried; withheld cells unresolved); a broader generic or task-agnostic assembly explanation has not been tested and remains
possible. C is not supported (withheld gains 2–3× for
token maps, plus 1.29× for C and a further 1.29× for C2; the extent of overfitting was not
isolated; cross-shape shrinkage of C/T from training is resolved, 0.68×, but 2.1× remains). D is not supported at this budget. E applied to two banks and
was resolved by the four-reducer bank. Run 1831 (27) bears on how A's fitted decoder could be
acquired rather than on transfer: a C-over-T advantage (1.28×, training cells) is already
available from searches that have not yet solved, at about 1/8 of the exact corpora's source
evaluations, though it is much weaker than the exact-solver fit. Run 2116 (28) shows that
collecting further under the updated partial fit beats collecting further under G4 by a small
margin (1.18× [1.01, 1.37]; resolved on BE, PA unresolved); at the point estimates it closes about a tenth of the log
gap to the exact-solver fit, while improvement over retaining the first fit remains unresolved
(F/R 1.16× [0.99, 1.36]). Run 0125 (29) narrows B for the fitted tables on then-addition, now a development bank: a G4
map matched to C's pooled emitted frequencies is 2.48× slower than C and slower than T, so pooled
frequency on G4's template does not reproduce C's gain there. Run 0306 (30) narrows it further:
per-position frequency on G4's template (C/Q 2.41×) or alone (C/P 5.47×) does not reproduce it
either. These are two frozen external projections under one operator set; a positional learner is
not excluded. Run 0537 (31) tested the neighbourhood explanation with one intervention: Q recoded
to C's mutation width at an exactly fixed random-program distribution was 1.17× [1.09, 1.25] slower
than Q, and stronger recoding was slower still. So random, undirected width does not explain C's
gain. Structured coupling of the kind C's rows create is not excluded. Run 1606 (34) tested containment inside the
C-chain block operator: removing the boundary repair resolved no slowdown (W/R 0.954× [0.903, 1.007]; a repair
gain above 0.7% excluded), so the block operator's gain over C does not need the kept suffix at this
resolution; coordinated chain
proposals help without it (R/C 1.29×), though they are not isolated from the operator's length law.

Sub-questions: [11-composition-bank](11-composition-bank/question.md) (closed: this bank
fails on tractability at 524k and on the 4 096 headroom rule against G; run 2026-10-05-2247),
[12-generic-grammar-headroom](12-generic-grammar-headroom/question.md) (closed: ten-token
branch cells leave headroom above G, but no same-primitive family pair survives the alias
screen; run 2026-10-06-0001).
[13-post-addition-map-learning](13-post-addition-map-learning/question.md) (closed, 2 of 2
slots: G-based token multipliers transfer about 2× to the withheld pair and to branch-else;
contextual row moves on top add no resolved training gain (R / M+ 1.00× [0.90, 1.11]), holdout
increment unresolved; runs
2026-10-06-0132 and 2026-10-06-0811).
[14-saved-map-shape-shift](14-saved-map-shape-shift/question.md) (closed, 1 of 1 slot, run
2026-10-06-1425, row 3: 0811's branch-versus-linear shift of R over M+ did not replicate on
the "b" continuations (shift 0.73× [0.57, 0.94]); on those maps a frequency-matched token-only
control was not resolved from R, shift 1.02× [0.92, 1.12]).
[15-four-reducer-family-bank](15-four-reducer-family-bank/question.md) (closed, 1 of 1 slot, run
2026-10-06-1603, row 1: with FIRST added, branch-else has no role-covered holdout pair on three
domains; PA splits; G4 tractable with headroom on all 13 cells; hand-set family grammars give a
crossed preference that context strengthens over the marginal controls, descriptive only; a
conservative learner-pilot projection excluded stage C, whose runtime was not measured there).
[16-crossed-family-adaptation](16-crossed-family-adaptation/question.md) (closed, 2 of 3
slots, runs 2026-10-06-1723 and 2026-10-06-2229: crossed BE/PA token-multiplier learning on the
1603 bank with one BE and two PA holdouts; both families learn about 2.2× on training, mostly
generically; on the holdouts every arm beats G4 2–3× and the matched-family advantage is 1.02×
(BE) and 0.96× (PA), 95% upper bounds 1.2485× and 1.15×, a 1.1× preference not excluded).
[17-decoder-initialization-variation](17-decoder-initialization-variation/question.md)
(closed, 2 of 2 slots, runs 2026-10-06-2331 row 3 and 2026-10-07-0315 row 1: both the learned
starting programs and the learned decoder during search help, about 1.3× given the other on the
withheld and the training cells, strongly sub-additive; on the training cells the start weighs
relatively more on BE than on PA cells, C −0.45 log2 [−0.68, −0.22], not separated from shape or
difficulty).
[18-compact-context-learning](18-compact-context-learning/question.md) (closed at tested
scope, 1 of 2 slots, runs 2026-10-07-0821 row 3 and, via 19, 2026-10-07-1137 row 6: rank-one
context steps mixed into token continuation from saved maps add no resolved training increment
in a loop where token continuation learns, C/T 0.967× [0.871, 1.073]; joint learning from G4 and
non-displacing context untested).
[19-selection-calibrated-continuation](19-selection-calibrated-continuation/question.md) (closed,
1 of 2 slots, run 2026-10-07-1137 row 6: 96 searches per candidate make token continuation from
the saved maps learn, T/S 1.143× [1.089, 1.200] and 1.122× [1.031, 1.222] on two fresh blocks;
cause not isolated from the changed depth and total effort).
[20-solver-corpus-context](20-solver-corpus-context/question.md) (closed, 1 of 1 slot, run
2026-10-07-1707 row 1: a previous-token table fitted to exact solver tapes beats a token-only fit
to the same tapes 1.37× on training and 1.29× on the withheld cells, 32 corpora, no
resolved family advantage; external fitting, not evolutionary discovery).
[21-iterated-solver-corpus](21-iterated-solver-corpus/question.md) (closed, 1 of 1 slot, run
2026-10-07-1924 row 1: refitting each C to exact solvers found under it gives C2/C 1.40× [1.35,
1.46] on training and 1.29× [1.20, 1.38] on the withheld cells, and C2/C' 1.41× and 1.33× against
a fresh one-shot G4 refit; attributable to the collection procedure, whose yield, diversity and
content are not separated; one step only).
[22-feedback-context-increment](22-feedback-context-increment/question.md) (closed, 1 of 1
slot, run 2026-10-07-2156: on training cells feedback raised the fitted context's advantage over
the token-only fit, I 1.17× [1.09, 1.25], carried by BE (PA 1.02× [0.95, 1.09]); the token-only
fit also improved 1.20×; on the withheld cells I 1.09× [0.98, 1.20], unresolved).
[24-comparison-gate-bank](24-comparison-gate-bank/question.md) (closed, 1 of 1 slot, run
2026-10-08-1246: comparison-gated BE/PA bank, 37/56 behaviours retained, frozen 4 + 4 split per
family; on the training cells C/T 3.11× [2.78, 3.48], 16 corpora, collection yield 58.9%; both
fits beat G4 descriptively, C 5.8×, T 1.9×; training cells only, emitted frequencies uncontrolled).
[25-comparison-gate-transfer](25-comparison-gate-transfer/question.md) (closed, answered by run
2026-10-08-1548 row D: C/T 2.60× [2.31, 2.92] on the eight protected holdouts of development bank
comparison-gate-v1; family matching 1.10× [0.89, 1.35], unresolved).
[26-then-addition-fresh-bank](26-then-addition-fresh-bank/question.md) (closed, 1 of 1 slot, run
2026-10-08-1548 row F: on the fresh then-addition bank C/T 2.12× [1.86, 2.41], 16 corpora,
shrinkage from training 0.68× [0.57, 0.81]; one selected bank, two gates, K unscored).
[27-partial-program-context](27-partial-program-context/question.md) (closed, 1 of 1 slot, run
2026-10-08-1831: context fitted to tapes from not-yet-solved G4 searches beats a token fit to the
same tapes 1.28× [1.12, 1.45] and G4 1.62× [1.37, 1.90] on the training cells; mostly a
within-cap reliability gain, BE-carried; no resolved parent enrichment; exact-solver C 3.7× faster).
[28-partial-program-feedback](28-partial-program-feedback/question.md) (closed, 1 of 1 slot, run
2026-10-08-2116: two feedback rounds of partial-tape collection under the updated context fit
beat equal-allocation one-shot G4 collection, F/O 1.18× [1.01, 1.37], BE 1.42×, PA 0.98× [0.83,
1.16], gain resolved on BE, PA unresolved; no improvement resolved from more G4 data, O/R 0.99×
[0.89, 1.10]; F/R unresolved; training cells only).
[29-frequency-matched-transfer](29-frequency-matched-transfer/question.md) (closed, 1 of 1 slot,
run 2026-10-09-0125: on then-addition C beats a G4 map matched to its pooled emitted frequencies,
C/K 2.48× [2.17, 2.83], 16/16 corpora; K/T 0.86× [0.77, 0.96]; context versus positional
frequency not separated; development bank by now).
[30-position-matched-replacement](30-position-matched-replacement/question.md) (closed, 1 of 1
slot, run 2026-10-09-0306 after 0239 stopped at admission: frozen per-position projections of C
on then-addition do not reproduce it, C/Q 2.41× [2.11, 2.75], C/P 5.47× [4.79, 6.25]; Q/K 1.03×
[0.93, 1.13]; development bank).
[31-distribution-preserving-recoding](31-distribution-preserving-recoding/question.md) (closed,
1 of 1 slot, run 2026-10-09-0537: Q recoded by random context-dependent allele permutations to C's
mutation width, at Q's exact random-program distribution, is slower than Q, cost_Q/cost_R30 0.855
[0.801, 0.914]; full-row recoding 0.409; no useful gain at either dose; development bank).
[32-learned-fragment-operator](32-learned-fragment-operator/question.md) (closed, 2 of 2
slots, run 2026-10-09-0843: learned fragment block edits beat C on training cells, F/C 1.57× [1.42,
1.75], F/W 1.23× [1.12, 1.36], F/B 1.60×; W/C 1.28× [1.17, 1.39]; run 2026-10-09-1036: frozen
whole-corpus libraries on then-addition F/C 1.47× [1.38, 1.56], F/W 1.20× [1.11, 1.29], W/C 1.23×
[1.15, 1.31], holdouts F/C 1.75×, F/W 1.27×; development banks; acquisition untested).
[33-pre-solve-fragment-source](33-pre-solve-fragment-source/question.md) (closed, 1 of 1 slot,
run 2026-10-09-1350: the 0843 extractor on pre-solve parents from 1831 gives full libraries without
`gt` joins; on then-addition E/W_E 0.981× [0.911, 1.057], rule 3, no worthwhile increment; E/F
0.843× [0.795, 0.892], E/W 1.007×; development bank, C fitted from exact solvers).
[34-chain-block-suffix-preservation](34-chain-block-suffix-preservation/question.md) (closed, 1 of 1
slot, run 2026-10-09-1606: C-chain blocks without the boundary repair (R) on then-addition, W/R 0.954×
[0.903, 1.007], rule 3, repair not needed at this resolution; R/C 1.286× [1.208, 1.370]; ripple ~3
tokens when it occurs; development bank, C fitted from exact solvers).
[35-small-source-acquisition](35-small-source-acquisition/question.md) (closed, 1 of 1 slot,
run 2026-10-09-1743: C4+F4 from four G4 attempts per training cell, cost(full F)/cost(C4+F4)
0.679× [0.614, 0.752], 0.833 retention excluded pooled and per family, blocks 0 and 1 unresolved
separately; cheaper than full F up to about 1 500 searches; development bank).
[36-sparse-source-feedback](36-sparse-source-feedback/question.md) (closed, 1 of 1 slot,
run 2026-10-09-2033: one adaptive batch under C4+F4 versus four more G4 attempts, S8/A8 1.126×
[1.039, 1.220], unresolved against 1.10; full F/A8 1.031× [0.951, 1.117]; A8 cheaper at every
horizon; development bank).
[37-cheap-bias-fresh-transfer](37-cheap-bias-fresh-transfer/question.md) (closed, 1 of 1 slot,
run 2026-10-09-2303: frozen A8/S8/full F/G4 on fresh `two-sum-v1`; cost(A8)/cost(full F) 0.945×
[0.819, 1.092], 1.20× loss excluded, sign unresolved; G4/A8 2.73× [2.36, 3.17]; S8/A8 1.173×
[1.036, 1.327]; one fresh shape, D1331).
[38-cheap-bias-source-replication](38-cheap-bias-source-replication/question.md) (closed, 1 of 1
slot, run 2026-10-10-0145: A8 rebuilt 16 times from the complementary source roster; on two-sum-v1
cost(G4)/cost(A8′) 2.50× [2.17, 2.85], useful replication against 1.5×; δ = A8′/historical A8 1.09×
[0.90, 1.32], unresolved; PA weaker; S8′ built, unscored; development data).
[39-independent-input-family-bank](39-independent-input-family-bank/question.md) (closed, 1 of 1
slot, run 2026-10-10-0311, probe: bank `x4-double-gate-v1` on alphabet `v2_x4`/D625 gives 24
separated double-sum-predicate cells and a frozen 4/4/8 split; first-batch G4 discovery sparse
(22/128); pilot on 4 development cells G4/A8 12.2× [6.7, 20.7], penalty-inflated, O/A8 6.7×;
observations only, protected cells unscored).
[40-independent-input-protected-transfer](40-independent-input-protected-transfer/question.md)
(closed, 1 of 1 slot, run 2026-10-10-1536: 24 fresh A8″ builds on 39's eight protected cells,
cost(G4)/cost(A8″) 10.1× [7.6, 13.1] (1 × cap 6.4× [5.0, 8.0]) against a 1.5× margin; A8″ 317/384 solved,
G4 63/384; unseen-pairing cells 6.8×; O/A8″ 4.3×; within-bank confirmation, weak G4 baseline).
[41-same-alphabet-family-preference](41-same-alphabet-family-preference/question.md) (closed, 1 of 1
slot, run 2026-10-10-1717: DG-built vs TS-built A8 cohorts on `v2_x4`, 8 never-searched cells per family;
cost(T)/cost(D) on DG 2.98× [2.07, 4.33], cost(D)/cost(T) on TS 1.29× [0.94, 1.78] unresolved (TS roster near
ceiling); interaction 1.96× [1.58, 2.44] at 2 × cap, 1.75× [1.45, 2.12] at 1 × cap; reciprocity not established;
all arms beat G4; content vs source difficulty not separated).
[42-family-bias-component-transfer](42-family-bias-component-transfer/question.md) (closed, 1 of 1 slot,
run 2026-10-10-2001: saved 1717 tables × libraries crossed in 24 donor pairs; on DG cells bare tables
T/∅ ÷ D/∅ 3.26× [2.43, 4.30], a point gap similar to the fresh native gap 3.03×; D library on the T table 3.05× over none,
1.95× [1.43, 2.66] over the T library (primary, unresolved against 1.5×); hybrid 1.55× [1.15, 2.09] behind D/D;
no native-pair dependence shown; no TS library difference resolved in either table, 1.01× [0.83, 1.25] and 1.00× [0.79, 1.27]).
[43-acquired-bias-vs-tree-gp](43-acquired-bias-vs-tree-gp/question.md) (closed, 1 of 1 slot, run
2026-10-10-2254 after two attempts stopped before scoring: frozen A8 against frozen closure-based subtree GP;
DG cost(tree)/cost(A8) 0.961× [0.683, 1.352] at 2 × cap (inside the 1.5× margin; 1 × cap 0.785× [0.583, 1.055]
unresolved); A8 solved 314/384, tree 202/384; A8 repays after about 146 DG searches per build in arithmetic
evaluations; TS 0.175× [0.142, 0.217] descriptive, tree cheaper).
[44-restarted-tree-vs-a8](44-restarted-tree-vs-a8/question.md) (closed, 1 of 1 slot, run 2026-10-11-0024: both
procedures restarted at 65,536 evaluations, up to 8 attempts; DG mean evaluations R-tree ÷ R-A8 0.792× [0.682,
0.915], solved 765/768 vs 754/768 (+0.014 [0.000, 0.034]); worker seconds 1.388× [1.196, 1.604] the other way;
restarted A8 ÷ full-cap A8 0.727×; TS 0.181× descriptive).
[45-tree-subtree-library](45-tree-subtree-library/question.md) (closed, slot 37, run 2026-10-11-0150: frozen
subtree library from new tree-source solvers as mutation donors in restarted tree GP; DG mean evaluations
R-lib ÷ R-tree 0.390× [0.332, 0.463], R-lib ÷ size-matched donors 0.414× [0.332, 0.533]; 1,536/1,536 solved;
repays after about 54 searches; carrying ingredient unidentified).
[46-tree-library-fresh-composition](46-tree-library-fresh-composition/question.md) (closed, slot 38, run
2026-10-11-0348: the 24 frozen 0150 libraries on 18 protected cells of fresh `x4-gate-sum-v1`; R-lib ÷ R-tree
0.250× [0.217, 0.289], ÷ R-size 0.291× [0.231, 0.372]; 1,728/1,728 solved; per split 0.055× (learned predicate's
split), 0.363×, 0.338×; repays after about 55 searches; carrier of the unlearned-split gain unidentified).
[47-tree-donor-arrangement](47-tree-donor-arrangement/question.md) (closed, slot 39, run 2026-10-11-0524: the 24
0150 libraries with labels permuted within size/arity/width pools (3 realizations per build) against intact
libraries on `x4-gate-sum-v1`; B/C R-perm ÷ R-lib 1.031× [0.854, 1.225] (retention margin 1.25), ÷ R-tree 0.360×;
split A 5.14× [3.68, 7.14]; arrangement needed for the predicate split's extra gain, not for the B/C gain at this
resolution; carrier unidentified).
[48-tree-donor-label-supply](48-tree-donor-label-supply/question.md) (closed, slot 40, run 2026-10-11-0652: the
same 0150 skeletons, widths, sizes and multiplicities with labels drawn uniformly within compatible classes;
B/C R-unif ÷ R-perm 2.07× [1.68, 2.61] (registered loss), ÷ R-tree 0.755× [0.645, 0.884], ÷ R-size unresolved
(R-size ÷ R-unif 1.095× [0.864, 1.367]); preserving shapes with this uniform label law did not retain the full
learned-label saving, and the shape contribution remains unresolved (up to about 30% not excluded); which label
component matters is unidentified).
[49-tree-library-source-portability](49-tree-library-source-portability/question.md) (closed, slot 41, run
2026-10-11-0833: the unchanged extractor rebuilt from the four TS source cells; B/C R-TS ÷ R-tree 0.382× [0.335,
0.433] (portable branch, upper < 0.80), ÷ R-sizeTS 0.406× [0.344, 0.482], ÷ R-DG 1.03× [0.86, 1.22] unresolved;
1,728/1,728 solved; repays after about 6 searches; no seven-node `GT(ADD,ADD)` predicate in any of the 24 TS libraries; native TS harmed,
R-TS ÷ R-tree 1.78× [1.58, 2.00]).
[50-library-easy-target-harm](50-library-easy-target-harm/question.md) (parked at opening, no budget: can a
library-use policy, e.g. library only after a failed first attempt, remove 49's native-TS harm while keeping
the B/C saving?).
[51-source-free-donor-prior](51-source-free-donor-prior/question.md) (closed, slot 42, run
2026-10-11-1019: a fixed 192-entry prior of all ordered `ADD(Xi,Xj)` and `ADD(Xi,c)`/`ADD(c,Xi)` forms, no
acquisition, against the 24 saved 0833 TS libraries on B/C; R-hand ÷ R-TS 0.852× [0.762, 0.958] (retained
branch, upper < 1.25), ÷ R-tree 0.318× [0.291, 0.349]; 1,728/1,728 solved in both donor arms; TS acquisition
never repays against it within 200 searches; which ingredient carries it is not isolated).
[52-order-helper-acquisition](52-order-helper-acquisition/question.md) (parked, slot 43, probe, run
2026-10-11-1129: can the subtree recipe acquire pairwise min/max helpers on a new bank `x4-order-v1`? Observations
on six development cells: literal extractor 0/8 builds with a helper, 1.55× [1.09, 2.17] of R-tree; behaviour-keyed
3/8, 1.00× [0.68, 1.46]; supplied order prior 0.048×; limit located as literal keying, then cap crowding, then
emission size; whether an included helper speeds search unresolved).
[53-order-library-cap-release](53-order-library-cap-release/question.md) (open, slot 44, strategy 1228: does
removing R-S's 16-entry cap, keeping every eligible recurrent semantic class, make acquisition useful on the
order development cells?).

Related: [core question](../../../README.md#core-question),
[01-map-bias](../01-map-bias/question.md),
[08-evolve-bias](../01-map-bias/08-evolve-bias/question.md),
[09-generic-bias-speedup](../01-map-bias/09-generic-bias-speedup/question.md),
[run 0811 decision](../../runs/2026-10-06-0811/decision.md),
[run 1603 decision](../../runs/2026-10-06-1603/decision.md),
[run 1723 decision](../../runs/2026-10-06-1723/decision.md),
[run 0315 decision](../../runs/2026-10-07-0315/decision.md),
[run 0821 decision](../../runs/2026-10-07-0821/decision.md),
[run 1137 decision](../../runs/2026-10-07-1137/decision.md),
[run 1707 decision](../../runs/2026-10-07-1707/decision.md),
[run 1924 decision](../../runs/2026-10-07-1924/decision.md),
[run 2156 decision](../../runs/2026-10-07-2156/decision.md),
[run 1246 decision](../../runs/2026-10-08-1246/decision.md),
[run 1548 decision](../../runs/2026-10-08-1548/decision.md),
[run 1831 decision](../../runs/2026-10-08-1831/decision.md),
[run 2116 decision](../../runs/2026-10-08-2116/decision.md),
[run 0125 decision](../../runs/2026-10-09-0125/decision.md),
[run 0239 decision](../../runs/2026-10-09-0239/decision.md),
[run 0306 decision](../../runs/2026-10-09-0306/decision.md),
[run 0537 decision](../../runs/2026-10-09-0537/decision.md),
[run 0843 decision](../../runs/2026-10-09-0843/decision.md),
[run 1036 decision](../../runs/2026-10-09-1036/decision.md),
[run 1350 decision](../../runs/2026-10-09-1350/decision.md),
[run 1606 decision](../../runs/2026-10-09-1606/decision.md),
[run 1743 decision](../../runs/2026-10-09-1743/decision.md),
[run 2033 decision](../../runs/2026-10-09-2033/decision.md),
[run 2303 decision](../../runs/2026-10-09-2303/decision.md),
[run 0145 decision](../../runs/2026-10-10-0145/decision.md),
[run 0311 decision](../../runs/2026-10-10-0311/decision.md),
[run 1536 decision](../../runs/2026-10-10-1536/decision.md),
[run 1717 decision](../../runs/2026-10-10-1717/decision.md),
[run 2001 decision](../../runs/2026-10-10-2001/decision.md),
[run 2254 decision](../../runs/2026-10-10-2254/decision.md),
[run 0024 decision](../../runs/2026-10-11-0024/decision.md),
[run 0150 decision](../../runs/2026-10-11-0150/decision.md),
[run 0348 decision](../../runs/2026-10-11-0348/decision.md),
[run 0524 decision](../../runs/2026-10-11-0524/decision.md),
[run 0652 decision](../../runs/2026-10-11-0652/decision.md),
[run 0833 decision](../../runs/2026-10-11-0833/decision.md),
[run 1019 decision](../../runs/2026-10-11-1019/decision.md),
[digest](../../digest.md), [chem-tape findings](../../../docs/chem-tape/findings.md).

Review after the feasibility experiment and after the four allocated experiments. A
failed task candidate should prompt a bounded redesign, not an automatic stop of the
program. An unresolved transfer effect should be sized against measured runtime before
deciding whether another allocation could settle it.

Reopen if parked: a tractable task suite supplies the missing compositional contrast, a
decoder with demonstrably better training/search feasibility becomes available, or new
evidence defeats the specific generic-bias or overfitting explanation that caused parking.
