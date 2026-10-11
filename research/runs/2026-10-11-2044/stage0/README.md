# Stage-0 read-only probe (steward, 2044)

Off-harness, about 1 min of compute, in the 1938 stage-0 export (`/tmp/sg1938`, `git archive` of
`research/main` at `3a18ef5`, own venv and Rust build). Scripts here are copied from `/tmp/sg1938/probe/`
and import the 1938 [`sg.py`](../../2026-10-11-1938/stage0/sg.py) (unchanged `tree_gp_search.search`,
restart loop ≤ 8 × 65,536, P 256, mix 0.5). Not a bank: no manifest, alias screen, VM check of the chain
labels, or old-bank check.

- `chain.py p30+n01+p12,p30+n02+p21,p13+n30+p02,p01+n12+p23 3`: destinations
  `p(a,b)+n(b,c)+p(c,d)` (numpy labels), 4 cells × 3 repeats; arms R-tree, R-gate (24 helpers),
  and the two **1938 stage-0** R-all builds (`lib0.pkl`, `lib1.pkl`; not the saved 1938 libraries).
  The 4 cells are the 4 lowest label SHA-256s in the [planning audit](../gate-composition-planning-audit.json).
  Seeds 20440000–20443027 (base `20440000 + cell*1000 + repeat*10`, 8 per unit).
- `cov.py semantic`: needed-helper coverage of the **24 saved 1938 R-all libraries** over all 24 chain cells.

| Arm (12 jobs) | Solved | First attempt | Attempts used | Mean evals | Median | Mean / max worker-s |
|---|---|---|---|---|---|---|
| R-tree | 12/12 | 6/12 | 1,2,1,1,6,1,6,1,3,3,1,7 | 138 k | 82 k | 8.3 / 22.1 |
| R-gate | 12/12 | 9/12 | max 3 | 31 k | 9.5 k | 2.1 / 8.3 |
| R-all build 0 | 12/12 | 5/12 | max 5 | 100 k | 103 k | 6.4 / 19.5 |
| R-all build 1 | 12/12 | 7/12 | max 6 | 101 k | 35 k | 5.9 / 19.3 |

Per-cell R-tree means: 41 k, 134 k, 175 k, 203 k. Wall 36 s for 48 jobs (~7.6 effective workers).
For comparison, 1938 protected R-tree: mean 7.8 k, 97.7% first attempt.

Saved 1938 libraries (`cov.py`): 37.4 entries, 8.6/24 helpers on average; of the three helpers a chain cell
needs, a build × cell has 0: 25%, 1: 48%, 2: 24%, all 3: 3.3%.

The four cells are now seen and must be in the development roster. Small n; observations, not beliefs.
