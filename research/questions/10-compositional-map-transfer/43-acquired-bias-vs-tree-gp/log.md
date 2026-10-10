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
