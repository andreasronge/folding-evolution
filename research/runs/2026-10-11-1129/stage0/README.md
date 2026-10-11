# Stage-0 read-only probe (steward, 1129)

Off-harness, about 1 min of compute in a temporary worktree of `research/main` at `e29219b`
(`tree_gp_search.search`, `tree_library.extract` unchanged). Single attempts, cap 65,536, P 256, mix 0.5,
D625 labels computed in numpy (helpers `lo(a,b) = Xa>Xb ? Xb : Xa`, `hi` likewise). Not a bank: no
manifest, alias screen or old-bank overlap check. Run `uv run python probe_order.py`, `probe2.py`,
`probe3.py` from a worktree root. Seeds: sources 7000–7799, destinations 9000–9005.

| Observation | Value |
|---|---|
| Sources (all 24, `probe3`) | 71/72 solved, ~3 k evaluations typical, solver median 15 nodes |
| R-tree on 3 destinations × 6 seeds | 10/18 solved at 65,536; capped mean 34.4 k |
| R-order (12 helpers, half the donors) | 18/18 solved; mean 1.4 k (768–3,840) — near the 3-generation floor |
| Unchanged extractor, 4 builds | helper entries 1 / 0 / 0 / 0; capped mean 23.2 k (13/18), 51.7 k (5/18), 50.4 k (5/18), 55.6 k (4/18) |
| Build with the helper | only the 4-cell roster chosen so each helper occurs twice (lo01 extracted) |
| Helper census (71 solvers) | 41 contain a subtree computing their own helper on D625; of 44 such subtrees only 11 are the 6-node form, 19 are ≤ 9 nodes, the rest 10–22 nodes |

The three destinations used here (lo01+hi23, lo01+hi12, lo02+hi13) are seen and must go into the
development roster.
