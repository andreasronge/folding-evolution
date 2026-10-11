# Stage-0 read-only probe (steward, 1315)

Off-harness, about 9 min of compute, in an export of `research/main` at `60ab766` with its own venv and Rust
build (`worktree_setup` from `research/config.toml`). Unchanged `tree_gp_search.search`, restart loop as in
`order_run.execute` (≤ 8 × 65,536, P 256, mix 0.5), unchanged `order_library.build(cap=None)` (R-all). D625
labels computed in numpy: `pos(a,b) = (Xa+Xb)>0 ? Xa+Xb : 0`, `neg` the complement. Not a bank: no manifest,
alias screen or old-bank check. Run from the export root with `PYTHONPATH=. .venv/bin/python <script>`
(`check.py`, `src.py 2`, `dst.py pos01+neg02,pos13+neg23,pos01+neg23,pos12+neg03 4`, `why.py`).
Seeds: sources 70000–89999, destinations 90000–90399, checks 5000–5299.

**Harness artefact caught first.** Run with the main checkout's venv, the compiled VM returned all zeros for
`v2_x4`, so 0/96 sources "solved" and the order positive control failed too. With the research-branch build
the control solves (`lo01+X2` 4/4 at 1.5–3.8 k). The numbers below are from the correct build only.

| Observation | Value |
|---|---|
| Hand trees | 12 helpers verified by the interpreter (8 nodes, 12 tokens); hand source 15 tokens |
| Sources, 2 builds × 24 cells × 2 jobs | 96/96 solved, all first attempt; median 2.0 k, mean 2.9 k evaluations; ~140 k per build |
| Source solver form | 84/96 IF_GT-rooted; 80/96 contain the 3-input sum `a+b+c`; **11/96 contain their own helper** (sizes 8–18 nodes) |
| R-all libraries | 11 and 18 entries, almost all 3–5-node classes; rectifier helpers **0 and 1** (pos12) |
| Destinations, 4 cells × 4 repeats (16 jobs per arm) | R-tree 4/16, capped mean 419 k; R-rect (12 supplied helpers) 11/16, 287 k; R-all build 0 7/16, 391 k; build 1 4/16, 426 k; transported order R-all (1228 build 0) 0/16, 524 k |
| Worker seconds per destination job | 22–38 (capped jobs dominate) |

Reading: the sources are solved without the helper, mostly as `max(a+b+c, c)` built on the three-input sum,
so recurrence-based extraction has almost nothing rectifier-shaped to pool. The destinations (25 tokens
against a 32-token cap) are hard for every arm; even the supplied prior leaves 5/16 unsolved. Small n,
four seen cells; observations, not beliefs. The four destinations used here are seen and belong in any
development roster.
