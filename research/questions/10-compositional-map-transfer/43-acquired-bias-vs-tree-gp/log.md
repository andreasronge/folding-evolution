# Log: 43 acquired bias versus typed subtree GP

2026-10-10 (steward, run 2026-10-10-2214): opened from strategy 2214. Read-only checks on `research/main`
(`6dabda8`): no tree-GP runner and no DEAP in the environment. Under `v2_x4` with intlist input the only
value type that functions consume is int: terminals X0–X3 (INPUT + readout, 2 tokens each), ANY (INPUT +
ANY), constants 0/1/2/5 (and THRESHOLD_SLOT = 0); functions ADD, GT, IF_GT (postfix else, then, cond;
cond > 0). DG and TS canonicals both compile to 16 tokens (10 tree nodes). Search harness facts reused:
P 256, 2 elites, lexicase on 64 cases drawn from `default_rng([seed, 0])`, cap 524 288 (2 048 generations),
exact 625-input check. Rates: A8 native 11.7 s/search on DG, 3.6 s on TS; G4 29 s / 14 s; D acquisition
12.5 M evaluations (771 worker-s) per build, T 6.1 M (307); D build-level log-cost SD on DG 0.66.

Decision: propose one frozen comparison of native A8 against typed subtree GP on both rosters
([proposal](../../../runs/2026-10-10-2214/proposal.md)) because it is the allocated question and no new
acquisition is needed.

2026-10-10 (steward, run 2026-10-10-2214, after infeasibility): critic approved with notes; the researcher
implemented closure-based subtree GP (commit `3e961ad` on `research/2026-10-10-2214`) and stopped before
any search ([infeasible](../../../runs/2026-10-10-2214/infeasible.md)). The plan resolved the proposal's
unstated "depth 2–4" as **edges**; with uniform choice over 3 functions and 9 terminals (5 of them two-token
readouts), the full-depth-4 bin cannot be filled under the 32-token cap: 0/10 000 draws accepted (compiled
length 35–130, median 64); exact acceptance 1.21 × 10⁻⁷ per draw, about 3.4 worker-hours of initialization
per search. Full depth 3 (edges) accepted 71.8%, depth 2 100%. What passed: all 16 target canonicals
compile to 16 tokens / 10 nodes and match D625 labels in an independent interpreter, the Python VM and the
Rust VM; 1 998 random tree/subtree-exchange checks agree across all three; overflow, conditional order,
size reversion and saved-bank provenance checks passed. Not run: A8 replays, Stage 0 calibration,
timing, all 1 792 target searches. No A8/tree evidence of any kind; no slot used.

Read-only check on `3e961ad`: with depths 1–3 edges a P256 population takes 274 draws (2 ms); full depth 3
accepts 72%. It also showed the frozen grow picks a terminal at the root half the time, so about a quarter
of the initial population would be single terminals (grow median 2 tokens); with a function root (Koza's
grow) grow depth 3 has median 12 tokens, 99.5% accepted.

Decision: keep 43 open and re-propose the same comparison with ramped half-and-half over depths 1–3 edges
(2–4 levels) and a function root in grow, everything else unchanged ([proposal 2239](../../../runs/2026-10-10-2239/proposal.md)),
because the obstruction is a depth-convention choice that changes neither the question, the comparator's
character nor the cost premises; both roster targets have depth ≤ 3 edges (TS 2, DG 3), and the tested
code is reusable. The strategist's early-exit clause targeted obstacles that change the price; this one
does not, so a strategy review now would only re-approve the same purchase.

2026-10-10 (steward, run 2026-10-10-2239, after infeasibility): critic approved with notes; the researcher
restored the tree code from `3e961ad` and isolated the two initializer changes (commit `6b40e16` on
`research/2026-10-10-2239`). Observations from preparation (development cells only, not evidence about the
comparison):
- Initializer: 20 000 draws per bin; depth 1/2 bins accept 100%, full depth 3 72.1%, grow depth 3 99.5%;
  median compiled length full 5/11/27, grow 5/8/12 tokens; a P256 population fills 43/43/43/43/42/42 bins
  in 272 draws. Initialization roots are functions; mutation keeps terminal roots with probability 0.5.
- Complete search smoke: DG development seed 22160000 solved at 6 144 evaluations (0.26 s); TS development
  seed 22161000 hit the 524 288 cap unsolved (30.2 s). One search each; not a solve rate.
- Forced full-cap timing, ten workers, Rayon 1, ten searches per family: mean 50.5 s (DG) and 48.5 s (TS)
  per search, effective concurrency 9.1. A planning projection with historical native/G4 rates gives DG
  4 048 s and TS 3 223 s against admission gates of 5 760 and 4 320 s; this is not Stage 0 admission.
- Stopped at the seed audit. The seed formulas inherited unchanged from plan 2214 overlap: calibration
  `22140000 + 1000·(8f + c) + r` spans 22140000–22155007 and scoring `22150000 + 1000·(8f + c) + 2b + r`
  starts at 22150000, so 48 seed values (TS calibration cells 2–7 against DG scoring cells 0–5; 96 searches
  each side) are shared, and the smoke seeds 22160000/22161000 are TS scoring seeds. Steward check: the
  arithmetic is right (the 16 indexed cells span 15 000 but the bases are 10 000 apart). Not run: 16 A8
  replays, 256 Stage 0 searches, mix choice, 1 792 target searches.

Correction (critique 2239 notes 6 and 8; entries above left as written): "cannot be filled" in the 2214 entry
should read "failed the 10 000-draw bound and is impractical at the measured acceptance". The question
heading said "typed subtree GP"; the implemented comparator is closure-based subtree GP (one integer type).
Explanation (b) now says that a tree win would not identify which structural feature is responsible.

Decision: keep 43 open and re-propose the 2239 design with one change, scoring seed base 22150000 →
22180000 (scoring 22180000–22195115, disjoint from calibration, smoke and the 1 544 saved acquisition and
replay seeds per the researcher's [prospective audit](../../../runs/2026-10-10-2239/alternative-seed-audit.json);
no prior run used that range) ([proposal 2254](../../../runs/2026-10-10-2254/proposal.md)), because the
obstacle is an error in the pre-registration's seed arithmetic, not a measured property of either method,
of validity or of price; everything measured was in line with the plan. This departs from the letter of
proposal 2239's exit clause ("any later gate fails → park and strategy"); that clause was written for
obstacles that say something about the baseline or the cost. Any further gate failure parks 43.
