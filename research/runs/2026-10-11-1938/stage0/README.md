# Stage-0 read-only probe (steward, 1938)

Off-harness, about 3 min of compute in total, in a `git archive` export of `research/main` at `3a18ef5`
with its own venv and Rust build (`worktree_setup` from `research/config.toml`; `_folding_rust` and
`folding_evolution` import from the export). Unchanged `tree_gp_search.search`, restart loop as in
`order_run.execute` (≤ 8 × 65,536, P 256, mix 0.5), unchanged `order_library.build(cap=None)` (R-all) with
signed-gate helper vectors passed only as `diagnostic_vectors`. Labels in numpy:
`p(a,b) = Xa>0 ? Xb : 0`, `n(a,b) = Xa>0 ? 0 : Xb`; IF_GT prefix is `(11, else, then, cond)`, so
`p = (11,5,b,a)`, `n = (11,b,5,a)`. Not a bank: no manifest, alias screen or old-bank check.
Run from the export root with `PYTHONPATH=. .venv/bin/python probe/<script>`
(`sg.py src 2`, `census.py`, `libs.py`, `dst.py <cells> 3`, `dst2.py <cells> 3`).
Seeds: sources 19380000–19384717 and 19480000–19484717; destinations 19390000–19393027.
The experiment must use a different namespace.

| Observation | Value |
|---|---|
| 24 helper trees | interpreter = VM = numpy labels; 4 nodes, 6 tokens |
| Sources, 2 builds × 48 cells × 2 jobs | 192/192 solved, all first attempt; median 1.8 k, mean 2.1 k evaluations; ~200 k evaluations and ~10 worker-s per build |
| Source solver form | ADD-rooted 146/192, IF_GT-rooted 46/192; **own helper's output in 71/192 (37%)**, at 3–9 nodes in 44/192 (23%; 25 of the 71 at the minimal 4 nodes) |
| R-all libraries | 37 entries each (3–9 nodes, 1–3 inputs); signed-gate helpers **11/24 and 6/24** |
| Needed-helper coverage per destination | both helpers 3/24 and 2/24; at least one 19/24 and 10/24 |
| Destinations p01+n23, p12+n30, p23+n01, p31+n02 × 3 repeats (12 jobs per arm) | R-tree 12/12 first attempt, mean 5.2 k (median 4.2 k); R-gate (24 helpers) 1.5 k; new R-all builds 0/1 2.8 k, 2.7 k; transported 1228 R-all (`semantic_all`, builds 0/1) 3.3 k, 4.6 k |
| Worker seconds per destination job | 0.1–0.3 |

Reading: unlike rectifiers ([54](../../../questions/10-compositional-map-transfer/54-rectified-sum-acquisition/log.md),
own-helper 8.9%, 0/96 recurrent-and-emittable), evolved signed-gate sources often build their helper at
an emittable size, and R-all keeps a quarter to a half of them. Destinations are easy for every arm
(question 50's ≥ 90% first-attempt condition is met), but no library raised cost on these cells.
Small n, four seen cells; observations, not beliefs. The four destinations are seen and must be in the
development roster.
