# Execution

Code: commit `1773d11e97ccbc710a1ead0d969c926102cb0860` on `research/2026-10-11-0024`. Queue runner exit: 0.

Rerun: check out that commit (`git worktree add <dir> 1773d11e97ccbc710a1ead0d969c926102cb0860`), run the `worktree_setup` commands from research/config.toml in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from it. Seeds are fixed, so the runs repeat.

| id | status | wall s | output (repo-relative) |
|---|---|---|---|
| 2026-10-11-0024-prepare | done | 186.01 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-0024-prepare |
| 2026-10-11-0024-dg | done | 1625.849 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-0024-dg |
| 2026-10-11-0024-ts | done | 376.63 | /Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-0024-ts |
